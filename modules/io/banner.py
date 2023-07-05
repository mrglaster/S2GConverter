import os

import modules.texture_processor.materials_reader

DEFAULT_BANNER_PATH = 'assets/banner.txt'


def get_banner_text() -> str:
    """Reads the banner data from the text file"""
    """Reads the banner from the text file"""
    if not os.path.exists(DEFAULT_BANNER_PATH):
        raise FileNotFoundError("Banner File was not Found! Path to the banner should be ../assets/banner.txt")
    with open(DEFAULT_BANNER_PATH, 'r', encoding='utf-8') as banner_file:
        return "".join(banner_file.readlines())


def print_banner():
    """Prints the banner"""
    print(get_banner_text())
