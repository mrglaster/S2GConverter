import os
import sys
import argparse
import subprocess
import math
import shutil
from PIL import Image

MAX_TRIANGLES_CONST = 500
TEXTURE_SIZE_CONST = 256
materialist = {}

def pathcheck(path_to_model):
    resultVar = False
    contains_vtx = False
    contains_vvd = False
    contains_vtf = False
    contains_vmt = False
    if os.path.exists(path_to_model):
        a = os.listdir(os.path.dirname(path_to_model))
        for i in a:
            if '.vtx' in i:
                contains_vtx = True
            if '.vvd' in i:
                contains_vvd = True
            if '.vtf' in i:
                contains_vtf = True
            if '.vmt' in i:
                contains_vmt = True
            if contains_vvd and contains_vtx and contains_vtf and contains_vmt:
                resultVar = True
                break
    print("VTX Detected: "+str(contains_vtx))
    print("VTF Detected: " + str(contains_vtf))
    print("VMT Detected: " + str(contains_vmt))
    print("VVD Detected: " + str(contains_vvd))
    return resultVar


def next_pow_of_two(x):
    a=math.ceil(math.log(x, 2))
    return int(math.pow(2.0, a))

def convert_to_bmp_folder(path_to_vtf):
    args = "VTFCmd.exe -folder " + str(path_to_vtf)+"\\ " + '-exportformat "bmp" -format "A8"'
    subprocess.call(args)

def decompile_model(path_to_model):
    args = "cr.exe "+path_to_model
    print(path_to_model)
    subprocess.call(args)

def resize_textures(path_to_folder):
    if os.path.exists(path_to_folder):
        files = os.listdir(path_to_folder)
        for i in files:
            if i.endswith(".bmp"):
                picture = Image.open(path_to_folder+'\\'+i)
                width, height = picture.size
                if width>TEXTURE_SIZE_CONST:
                    width = int((width/next_pow_of_two(width))*TEXTURE_SIZE_CONST)
                if height>TEXTURE_SIZE_CONST:
                    height = int((height / next_pow_of_two(height)) * TEXTURE_SIZE_CONST)

                if height>TEXTURE_SIZE_CONST:
                    height = TEXTURE_SIZE_CONST
                if width>TEXTURE_SIZE_CONST:
                    width = TEXTURE_SIZE_CONST
                picture = picture.resize((width, height))
                picture = picture.quantize(colors=256, method=2)
                picture.save(path_to_folder+'\\'+i)


def read_smd_header(path_to_smd):
    header = []
    if path_to_smd.endswith(".smd"):
        with open(path_to_smd) as f:
            filedata = f.readlines()
            for i in filedata:
                if i[:len(i)-1] not in materialist:
                    header.append(i[:len(i)-1])
                else:
                    break
    return fix_header(header[0:len(header)-1])

def fix_header(header):
    for i in range(0, len(header)):
        header[i] = header[i].replace('    ', '')
        header[i] = header[i].replace('  ', '')
    return header

def get_smd_data(path_to_smd):
    truedata = []
    if path_to_smd.endswith(".smd"):
        with open(path_to_smd) as f:
            filedata = f.readlines()
            for i in filedata:
                truedata.append(i[:len(i)-1])
    return truedata

def count_of_polygons(path_to_smd):
    cntr = 0
    if path_to_smd.endswith(".smd"):
        with open(path_to_smd) as f:
            filedata = f.readlines()
            for i in filedata:
                if i[:len(i)-1].lower() in materialist.keys() or i[:len(i)-1].upper() in materialist.keys() or i[:len(i)-1] in materialist.keys() :
                    cntr += 1
    else:
        print("SMD reference reading error! File not found!")
    return cntr

def isnot_texturekey(value, list):
    if value not in list.keys() and value.lower() not in list.keys() and value.upper() not in list.keys():
        return True
    else:
        return False

def read_smd_header(path_to_smd):
    header = []
    if path_to_smd.endswith(".smd") and os.path.exists(path_to_smd):
        with open(path_to_smd) as f:
            filedata = f.readlines()
            if len(materialist)==0:
                print("Error! Materials not found! ")
                return
            for i in filedata:
                if isnot_texturekey(i[:len(i)-1], materialist):
                    header.append(i[:len(i)-1])
                else:
                    break
    return fix_header(header[0:len(header)-1])

def split_smd_by_batches(smd_data):
    print('='*100)
    capability = []
    one_verticle_data = []
    for i in range(0, len(smd_data)):
        if i%4==0 and i!=0:
            if one_verticle_data[0] in materialist.keys():
                one_verticle_data[0] = materialist[one_verticle_data[0]]+".bmp"
            elif one_verticle_data[0].lower() in materialist.keys():
                one_verticle_data[0] = materialist[one_verticle_data[0].lower()] + ".bmp"
            elif  one_verticle_data[0].upper() in materialist.keys():
                one_verticle_data[0] = materialist[one_verticle_data[0].upper()] + ".bmp"
            else:
                print("Something is realy wrong in materiallist! Are you sure you have all required files?")
                print("Problem material is: ", one_verticle_data[0])

            capability.append(one_verticle_data)
            one_verticle_data = []
        if smd_data[i]!='end':
            one_verticle_data.append(smd_data[i])
    return capability

def polygons_per_part(polygons_amount):
    data = []
    if polygons_amount<=MAX_TRIANGLES_CONST:
        data.append(polygons_amount)
        return data

    while polygons_amount>MAX_TRIANGLES_CONST:
        data.append(MAX_TRIANGLES_CONST)
        polygons_amount-=MAX_TRIANGLES_CONST
    data.append(polygons_amount)
    return data

def find_smd_reference(path_to_model):
    ttf = os.listdir(os.path.dirname(path_to_model) + '\\')
    smd_reference = []
    qc_file = ''
    for i in ttf:
        if i.endswith('.qc'):
            qc_file = os.path.dirname(path_to_model)+'\\'+i
            break
    f = open(qc_file, "r")
    qc_lines = f.readlines()
    for i in qc_lines:
        j = i.split(' ')
        for s in range(1, len(j)):
            if 'materials' in j[s] or 'anims' in j[s] or 'cd'in i:
                break
            if 'smd' in j[s]:
                j[s] = j[s].replace('\n','').replace('"','')
                smd_reference.append(os.path.dirname(path_to_model)+'\\'+j[s])
    for i in smd_reference:
        print("SMD Reference detected: ", i)
    return smd_reference

def get_materials(path_to_model):
    print("Analyzing .vmt files")
    files = os.listdir(os.path.dirname(path_to_model) + '\\')
    for i in files:
        if i.endswith('.vmt'):
            vmt_file = open(os.path.dirname(path_to_model) + '\\'+i, "r")
            lines = vmt_file.readlines()
            for j in lines:
                if 'basetexture' in j.lower():
                    texture_name = ''
                    btx = j.split(' ')
                    for p in range(1, len(btx)):
                        basetexture_line = ''
                        if 'basetexture' in btx[p-1] or 'basetexture' in btx[p-1].lower() or 'basetexture' in btx[p-1].upper():
                            basetexture_line = btx[p]
                            break
                    for k in range(len(basetexture_line)-1, 0, -1):
                        if basetexture_line[k]!='/' and basetexture_line[k]!='\\':
                            texture_name = basetexture_line[k]+texture_name
                        else:
                            break
                    texture_name=texture_name[:len(texture_name)-2]
                    materialist[i[:len(i)-4]] = texture_name
    for i in materialist.values():
        print("Detected material: ", i)

def find_qc(path_to_model):
    ttf = os.listdir(os.path.dirname(path_to_model) + '\\')
    for i in ttf:
        if '.qc' in i:
            return os.path.dirname(path_to_model) + '\\'+i
    return None

def find_animsfolder(path_to_model):
    ttf = os.listdir(os.path.dirname(path_to_model) + '\\')
    for i in ttf:
        if '_anims' in i:
            return os.path.dirname(path_to_model) + '\\'+i+'\\'
    return None





def convert_model(path_to_model):
    source_direction = os.getcwd()
    smd_direction = os.path.dirname(path_to_model) + '\\'

    get_materials(path_to_model)
    if pathcheck(path_to_model):
        convert_to_bmp_folder(os.path.dirname(path_to_model))
        decompile_model(path_to_model)
        resize_textures(os.path.dirname(path_to_model))
        model_name = os.path.basename(path_to_model).replace(' ', '')
        model_box_data = []

        #grabbing box data
        qc_file_source = find_qc(path_to_model)
        if os.path.exists(qc_file_source):
            qc_file_source_data = open(qc_file_source).readlines()
        for i in qc_file_source_data :
            if "box" in i and not 'hboxset' in i:
                model_box_data.append(i)

        #finding anims folder and moving animations to folder with model files
        anims_folder = find_animsfolder(path_to_model)
        animlist = []
        os.chdir(anims_folder)
        a = os.listdir()
        for p in a:
            anim_file = p.replace(' ', '')
            if anim_file not in animlist:
                animlist.append(anim_file)
                print("Detected animation: ", anim_file)
            try:
                os.rename(os.getcwd() + '\\' + p, os.getcwd() + '\\' + anim_file)
            except:
                pass
            try:
                shutil.move(os.getcwd() + '\\' + anim_file, smd_direction)
            except:
                pass
        os.chdir(smd_direction)

        smd_references = find_smd_reference(os.path.dirname(path_to_model) + '\\')
        submodels_partnames = []
        submodels_counter = 0
        start_triangle_section = 'triangles'

        for smd_file in smd_references:
            triangle_section_written = False
            if os.path.exists(smd_file):
                local_partnames = []
                header = read_smd_header(smd_file)
                if len(get_smd_data(smd_file)[len(header) + 1:]) > 0:
                    verticle_data = split_smd_by_batches(get_smd_data(smd_file)[len(header) + 1:])
                else:
                    print("WARNING! SMD data parsing error! It can cause some problems!")
                    print("Excepted: ", smd_file)
                    pass
                parts_amount = math.ceil(len(verticle_data) / MAX_TRIANGLES_CONST)
                if parts_amount==0:
                    parts_amount = 1
                ppt = polygons_per_part(len(verticle_data))
                for part in range(0, parts_amount):
                    print("Writing part: " + str(part + 1))
                    partfile = smd_file[:len(smd_file) - 4] + "_decompiled_part_nr_" + str(part + 1) + "_submodel_" + str(
                        submodels_counter) + ".smd"
                    local_partnames.append(partfile[:len(partfile) - 4])
                    f = open(partfile, "w")
                    if 'triangles' not in header:
                        header.append('triangles')
                    for header_line in header:
                        f.write(header_line)
                        f.write('\n')

                    for verticle in range(0, ppt[part]):
                        writing_data = verticle_data[verticle]
                        for s in range(0, len(writing_data)):
                            writing_data[s] = writing_data[s].replace('  ', '')
                            if s > 0:
                                fixed_data = writing_data[s].split(" ")
                                fixed_data = fixed_data[:9]
                                writing_data[s] = ' '.join(fixed_data)
                        for k in writing_data:
                            f.write(k)
                            f.write('\n')

                    f.write('end\n')
                    f.close()
                    verticle_data = verticle_data[ppt[part]:]
                    print("Part ", str(part + 1), " of sumbodel ", str(submodels_counter), " was successful written")
                    submodels_partnames.append(local_partnames)

        qc_file = path_to_model[:len(path_to_model) - 4] + "_goldsource.qc"
        f = open(qc_file, "w")
        f.write('$modelname "' + model_name[:len(model_name) - 4] + "_goldsource.mdl" + '"' + '\n')
        f.write('$cd ".\"' + '\n')
        f.write('$cdtexture ".\"' + '\n')
        f.write('$scale 1.0' + '\n')
        for i in model_box_data:
            f.write(i + '\n')
        bodypart_id = 0
        anti_duble = []
        for i in submodels_partnames:
            for j in i:
                if os.path.basename(j) not in anti_duble:
                    f.write('$body "studio' + str(bodypart_id) + '" "' + os.path.basename(j) + '"' + '\n')
                    anti_duble.append(os.path.basename(j))
                    bodypart_id += 1
        for i in animlist:
            f.write('$sequence ' + i[:len(i) - 4] + ' "' + i[:len(i) - 4] + '"' + '\n')
        f.write('\n')
        f.close()
        if os.path.exists(qc_file):
            shutil.copy(source_direction + '\\' + 'studiomdl.exe', os.getcwd())
            arguments = "studiomdl.exe " + qc_file
            subprocess.call(arguments)
    else:
        print("We didn't find all required resources. Are you sure you have .vtf(s), .vmt(s), .vtx, .vvd, .mdl ")

def fix_header(header):
    for i in range(0, len(header)):
        header[i] = header[i].replace('    ', '')
        header[i] = header[i].replace('  ', '')
    return header



def argsparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True, help="Path to model you want to convert")
    return parser



def main():
    parser = argsparser().parse_args(sys.argv[1:])
    input_data = format(parser.input)
    assert os.path.exists(input_data), "Model you want to convert doesn't exist"
    convert_model(input_data)

if __name__=='__main__':
    main()
