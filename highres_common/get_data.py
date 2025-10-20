from pathlib import Path
from datetime import datetime


def get_folders(filepath, extensions):
    all_folders = []
    location_of_interest = Path(filepath).absolute()
    for ext in extensions:
        all_folders.extend(location_of_interest.rglob(ext))
    return all_folders


def get_files(folders_to_search, extension):
    all_files = []
    for folder in folders_to_search:
        #print(folder)
        text_file_generators = folder.glob(extension)
        for text_file in text_file_generators:
            all_files.append(text_file)
    return all_files

def get_datetime_folder(date_str):
    dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    folder_name = dt.strftime('%Y-%m-%d_%H-%M-%S')
    return folder_name


def find_csv_folders(path):
    csv_folders = []
    for item in Path(path).iterdir():
        if item.is_file() and item.name.endswith('.csv'):
            csv_folders.append(str(Path(item.parent).resolve()))
        elif item.is_dir():
            csv_folders += find_csv_folders(str(item))
    csv_folders = list(set(csv_folders))  # remove duplicates
    return csv_folders