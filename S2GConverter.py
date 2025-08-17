import sys
import re
import glob
import math
import shutil
import argparse
import subprocess
import PIL.Image
import cv2
import colortrans
import os
import numpy as np
from PIL import Image, ImageStat, ImageEnhance

MAX_TRIANGLES_CONST = 500
TEXTURE_SIZE_CONST = 256
VMT_FIELDS_PATTERN = r'("([^"]+)"\s+"([^"]+)")'


def delta_brightness(source_texture: str, overlay_texture: str) -> float:
    return ImageStat.Stat(Image.open(overlay_texture).convert('L')).mean[0] - \
           ImageStat.Stat(Image.open(source_texture).convert('L')).mean[0]


def adjust_saturation(img: PIL.Image.Image, saturation_factor: float) -> PIL.Image.Image:
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(saturation_factor)
    return img


def change_brightness(image_path: str, value: int = 30) -> PIL.Image.Image:
    img = cv2.imread(image_path)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    v = cv2.add(v, value)
    v[v > 255] = 255
    v[v < 0] = 0
    final_hsv = cv2.merge((h, s, v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return img


def clear_pnm_processing_trash() -> None:
    for fname in ['combined.png', 'combined_result.png']:
        if os.path.exists(fname):
            os.remove(fname)
    for i in os.listdir():
        if 'grayscale' in i and os.path.isfile(i):
            os.remove(i)


def generate_pseudo_normal_map(source_texture: str, normal_map: str) -> None:
    try:
        img = Image.open(normal_map).convert('L')
        grayscale_name = normal_map[:len(normal_map) - 4] + "_grayscale.png"
        try:
            img.save(grayscale_name)
        except:
            pass
        background = cv2.imread(source_texture)
        overlay = cv2.imread(grayscale_name)

        if background.shape[:2] != overlay.shape[:2]:
            bh, bw = background.shape[:2]
            oh, ow = overlay.shape[:2]
            if bh * bw >= oh * ow:
                overlay = cv2.resize(overlay, (bw, bh), interpolation=cv2.INTER_LINEAR)
            else:
                background = cv2.resize(background, (ow, oh), interpolation=cv2.INTER_LINEAR)

        added_image = cv2.addWeighted(background, 0.92, overlay, 1, 0)
        cv2.imwrite('combined.png', added_image)
        value = delta_brightness(source_texture, 'combined.png')
        result = change_brightness('combined.png', -1 * value)
        cv2.imwrite('combined_result.png', result)
        img_pil = adjust_saturation(Image.open('combined_result.png'), 3)
        clear_pnm_processing_trash()
        reference = np.array(Image.open(source_texture).convert('RGB'))
        content = np.array(img_pil.convert('RGB'))
        result = Image.fromarray(colortrans.transfer_reinhard(content, reference))
        result.save(source_texture)
        print(f"Bump texture has been successfully generated for {source_texture}")
    except Exception as e:
        print(f"Error happened during bump texture generation for {source_texture}: {e}")



def read_base_and_bump_texture(vmt_file_path: str) -> tuple:
    base_texture = None
    bump_map = None
    with open(vmt_file_path, 'r') as file:
        file_content = file.read()
    matches = re.findall(VMT_FIELDS_PATTERN, file_content)
    for match in matches:
        key = match[1].lower()
        val = os.path.basename(match[2])
        if "basetexture" in key:
            base_texture = val
        elif "bumpmap" in key:
            bump_map = val
    if base_texture:
        return vmt_file_path[:-4], base_texture, bump_map
    raise ValueError(f"Bad VMT File: {vmt_file_path}")


def get_materials_list(model_folder_path: str) -> dict:
    result = {}
    for file in glob.glob(os.path.join(model_folder_path, "*.vmt")):
        k, base, bump = read_base_and_bump_texture(file)
        result[os.path.basename(k)] = (base, bump)
    return result


def run_executable(exe_name: str, args: list):
    exe_path = os.path.join(sys.path[0], 'utils', exe_name)
    subprocess.call([exe_path] + args)


def pathcheck(path_to_model: str) -> bool:
    folder = os.path.dirname(path_to_model)
    files = os.listdir(folder) if os.path.exists(folder) else []
    extensions = {'.vtx': False, '.vvd': False, '.vtf': False, '.vmt': False}

    for fname in files:
        for ext in extensions.keys():
            if ext in fname:
                extensions[ext] = True

    for k, v in extensions.items():
        print(f"{k.upper()} Detected: {v}")

    return all(extensions.values())


def next_pow_of_two(x: int) -> int:
    return int(2 ** math.ceil(math.log(x, 2)))


def convert_to_bmp_folder(path_to_vtf: str):
    utility_path = os.path.join(sys.path[0], 'utils', 'VTFCmd.exe')
    run_executable(utility_path, [
        "-folder", path_to_vtf + (os.sep if not str(path_to_vtf).endswith(os.sep) else ''),
        "-exportformat", "bmp",
        "-format", "A8"
    ])


def decompile_model(path_to_model: str):
    utility_path = os.path.join(sys.path[0], 'utils', 'cr.exe')
    run_executable(utility_path, [path_to_model])


def preprocess_textures(path_to_folder: str, materials: dict, generate_pnmaps: bool):
    if not os.path.exists(path_to_folder):
        return
    if generate_pnmaps:
        for mat_key, (base_tex, bump_tex) in materials.items():
            if bump_tex:
                base_path = os.path.join(path_to_folder, base_tex + ".bmp")
                bump_path = os.path.join(path_to_folder, bump_tex + ".bmp")
                if os.path.exists(base_path) and os.path.exists(bump_path):
                    print(f"Generating pseudo normal map for {base_tex} using {bump_tex}")
                    generate_pseudo_normal_map(base_path, bump_path)


def resize_textures(path_to_folder: str):
    if not os.path.exists(path_to_folder):
        return
    for fname in os.listdir(path_to_folder):
        if not fname.endswith(".bmp"):
            continue
        full_path = os.path.join(path_to_folder, fname)
        picture = Image.open(full_path)
        width, height = picture.size
        if width > TEXTURE_SIZE_CONST:
            width = int((width / next_pow_of_two(width)) * TEXTURE_SIZE_CONST)
        if height > TEXTURE_SIZE_CONST:
            height = int((height / next_pow_of_two(height)) * TEXTURE_SIZE_CONST)
        width = min(width, TEXTURE_SIZE_CONST)
        height = min(height, TEXTURE_SIZE_CONST)
        picture = picture.resize((width, height))
        picture = picture.quantize(colors=256, method=2)
        picture.save(full_path)


def fix_header(header: list[str]) -> list[str]:
    return [line.replace('    ', '').replace('  ', '') for line in header]


def get_smd_data(path_to_smd: str) -> list[str]:
    if not path_to_smd.endswith(".smd"):
        return []
    with open(path_to_smd) as f:
        return [line.rstrip('\n') for line in f]


def isnot_texturekey(value: str, materials: dict) -> bool:
    keys = materials.keys()
    return value not in keys and value.lower() not in keys and value.upper() not in keys


def read_smd_header(path_to_smd: str, materials: dict) -> list[str]:
    if not (path_to_smd.endswith(".smd") and os.path.exists(path_to_smd)):
        return []
    header = []
    if not materials:
        print("Error! Materials not found!")
        return []
    with open(path_to_smd) as f:
        for line in f:
            clean_line = line.rstrip('\n')
            if isnot_texturekey(clean_line, materials):
                header.append(clean_line)
            else:
                break
    return fix_header(header[:-1])


def split_smd_by_batches(smd_data: list[str], materials: dict) -> list[list[str]]:
    capability = []
    one_verticle_data = []
    for i, line in enumerate(smd_data):
        if i % 4 == 0 and i != 0:
            mat = one_verticle_data[0]
            mat_key = (mat if mat in materials else
                       mat.lower() if mat.lower() in materials else
                       mat.upper() if mat.upper() in materials else None)
            if mat_key:
                one_verticle_data[0] = materials[mat_key][0] + ".bmp"  # base texture only
            else:
                print("Material not found in material list! Problem material:", mat)
            capability.append(one_verticle_data)
            one_verticle_data = []
        if line != 'end':
            one_verticle_data.append(line)
    return capability


def polygons_per_part(polygons_amount: int) -> list[int]:
    if polygons_amount <= MAX_TRIANGLES_CONST:
        return [polygons_amount]
    data = []
    while polygons_amount > MAX_TRIANGLES_CONST:
        data.append(MAX_TRIANGLES_CONST)
        polygons_amount -= MAX_TRIANGLES_CONST
    data.append(polygons_amount)
    return data


def find_qc(path_to_model: str) -> str | None:
    folder = os.path.dirname(path_to_model)
    for fname in os.listdir(folder):
        if fname.endswith('.qc'):
            return os.path.join(folder, fname)
    return None


def find_anims_folder(path_to_model: str) -> str | None:
    folder = os.path.dirname(path_to_model)
    for fname in os.listdir(folder):
        if '_anims' in fname:
            return os.path.join(folder, fname)
    return None


def find_smd_reference(path_to_model: str) -> list[str]:
    folder = os.path.dirname(path_to_model)
    qc_file = find_qc(path_to_model)
    if not qc_file:
        return []
    smd_reference = []
    with open(qc_file, "r") as f:
        for line in f:
            parts = line.split(' ')
            for token in parts[1:]:
                if 'materials' in token or 'anims' in token or 'cd' in line:
                    break
                if 'smd' in token:
                    smd_reference.append(os.path.join(folder, token.replace('"', '').strip()))
    for ref in smd_reference:
        print("SMD Reference detected:", ref)
    return smd_reference


def convert_model(path_to_model: str, generate_pnmaps: bool):
    source_dir = sys.path[0]
    model_folder = os.path.dirname(path_to_model)

    materials = get_materials_list(model_folder)
    if not pathcheck(path_to_model):
        print("Missing required resources (.vtf, .vmt, .vtx, .vvd, .mdl)")
        return

    convert_to_bmp_folder(model_folder)
    decompile_model(path_to_model)

    preprocess_textures(model_folder, materials, generate_pnmaps)
    resize_textures(model_folder)

    model_name = os.path.basename(path_to_model).replace(' ', '')
    model_box_data = []
    qc_file_source = find_qc(path_to_model)
    if qc_file_source and os.path.exists(qc_file_source):
        with open(qc_file_source) as f:
            model_box_data = [line for line in f if "box" in line and "hboxset" not in line]

    anims_folder = find_anims_folder(path_to_model)
    animlist = []
    if anims_folder:
        os.chdir(anims_folder)
        for fname in os.listdir():
            anim_file = fname.replace(' ', '')
            if anim_file not in animlist:
                animlist.append(anim_file)
                print("Detected animation:", anim_file)
            try:
                os.rename(fname, anim_file)
            except:
                pass
            try:
                shutil.move(anim_file, model_folder)
            except:
                pass
        os.chdir(model_folder)

    smd_references = find_smd_reference(path_to_model)
    submodels_partnames = []
    submodels_counter = 0

    for smd_file in smd_references:
        if not os.path.exists(smd_file):
            continue
        header = read_smd_header(smd_file, materials)
        smd_data = get_smd_data(smd_file)
        if len(smd_data) <= len(header) + 1:
            print("WARNING! SMD data parsing error:", smd_file)
        verticle_data = split_smd_by_batches(smd_data[len(header) + 1:], materials)
        parts_amount = max(1, math.ceil(len(verticle_data) / MAX_TRIANGLES_CONST))
        ppt = polygons_per_part(len(verticle_data))
        local_partnames = []
        for part in range(parts_amount):
            print("Writing part:", part + 1)
            partfile = f"{smd_file[:-4]}_decompiled_part_nr_{part + 1}_submodel_{submodels_counter}.smd"
            local_partnames.append(partfile[:-4])
            with open(partfile, "w") as f:
                if 'triangles' not in header:
                    header.append('triangles')
                f.write('\n'.join(header) + '\n')
                for vtx in verticle_data[:ppt[part]]:
                    cleaned = [' '.join(line.split()[:9]) if idx > 0 else line for idx, line in enumerate(vtx)]
                    f.write('\n'.join(cleaned) + '\n')
                f.write('end\n')
            verticle_data = verticle_data[ppt[part]:]
            print(f"Part {part + 1} of submodel {submodels_counter} written successfully.")
        submodels_partnames.append(local_partnames)
        submodels_counter += 1

    qc_file = f"{path_to_model[:-4]}_goldsource.qc"
    with open(qc_file, "w") as f:
        f.write(f'$modelname "{model_name[:-4]}_goldsource.mdl"\n')
        f.write('$cd ".\\" \n$cdtexture ".\\" \n$scale 1.0\n')
        for box_line in model_box_data:
            f.write(box_line + '\n')
        anti_duble = set()
        bodypart_id = 0
        for group in submodels_partnames:
            for name in group:
                base = os.path.basename(name)
                if base not in anti_duble:
                    f.write(f'$body "studio{bodypart_id}" "{base}"\n')
                    anti_duble.add(base)
                    bodypart_id += 1
        for anim in animlist:
            f.write(f'$sequence {anim[:-4]} "{anim[:-4]}"\n')

    if os.path.exists(qc_file):
        shutil.copy(os.path.join(source_dir, 'utils', 'studiomdl.exe'), os.path.dirname(qc_file))
        run_executable(os.path.join(os.path.dirname(qc_file), "studiomdl.exe"), [qc_file])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True, help="Path to model you want to convert")
    parser.add_argument('--generate_pnmaps', action=argparse.BooleanOptionalAction, default=True,
                        help="Enable or disable pseudo normal map generation (default: True)")
    args = parser.parse_args(sys.argv[1:])
    input_data = format(args.input)
    assert os.path.exists(input_data), "Model does not exist"
    convert_model(input_data, args.generate_pnmaps)


if __name__ == '__main__':
    main()
