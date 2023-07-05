import os

from modules.io.banner import print_banner
from modules.texture_processor.pseudonormals_processor import generate_pseudo_normal_map
from modules.texture_processor.materials_reader import read_base_texture
from modules.texture_processor.materials_reader import  get_materials_list
def main():
    print_banner()
    print(get_materials_list(os.getcwd()))

if __name__ == '__main__':
    main()
