import os


def find_qc(path_to_model: str) -> str:
    """Returns path to the qc file"""
    parent_dir = os.path.dirname(path_to_model)
    files = [file for file in os.listdir(parent_dir) if file.endswith('.qc')]
    if files:
        return os.path.join(parent_dir, files[0])
    return None


def find_animations_folder(path_to_model: str) -> str:
    """Returns path to the animations folder"""
    parent_dir = os.path.dirname(path_to_model)
    folders = [folder for folder in os.listdir(parent_dir) if '_anims' in folder and os.path.isdir(os.path.join(parent_dir, folder))]
    if folders:
        return os.path.join(parent_dir, folders[0], '')
    return None
