import os

DEFAULT_BANNER_PATH = 'assets/banner.txt'


def get_banner_line():
    """Reads the banner from the text file"""
    if not os.path.exists(DEFAULT_BANNER_PATH):
        raise FileNotFoundError("Banner File was not Found!")
    
