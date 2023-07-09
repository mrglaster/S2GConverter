# List of all requested for the model conversion
REQUIRED_FILES_EXTENSIONS = ['.mdl', '.vtf', '.vmt', '.vtx', '.vvd']


def check_required_files(path_to_model_folder: str) -> None:
    """Checks if the folder with the model contains all the necessary files"""
    files_in_folder = os.listdir(path_to_model_folder)
    missing_extensions = [extension for extension in extensions if
                          not any(file.endswith(extension) for file in files_in_folder)]
    for i in REQUIRED_FILES_EXTENSIONS:
        print(f"{i.upper()} FILES: {'FOUND' if i not in missing_extensions else 'NOT FOUND'}")
    if len(missing_extensions):
        raise ValueError(f"Files with following extensions weren't found: {REQUIRED_FILES_EXTENSIONS}")
