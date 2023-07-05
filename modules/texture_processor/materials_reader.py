import re
import os
import glob

VMT_FIELDS_PATTERN = r'"([^"]+)"\s*"([^"]+)"'


def read_base_texture(vmt_file_path: str) -> tuple:
    """Returns linked name of material and real name of one"""
    with open(vmt_file_path, 'r') as file:
        file_content = file.read()
    matches = re.findall(VMT_FIELDS_PATTERN, file_content)
    for match in matches:
        if "basetexture" in match[0].lower():
            return vmt_file_path[:-4], os.path.basename(match[1])
    raise ValueError(f"Bad VMT File: {vmt_file_path}")



def get_materials_list(model_folder_path: str) -> dict:
    """Returns list of materials as dictionary in following format key: vmt file value: name of texture file"""
    result = {}
    for file in glob.glob(model_folder_path + "/*.vmt"):
        k, v = read_base_texture(file)
        result[os.path.basename(k)] = v
    return result
