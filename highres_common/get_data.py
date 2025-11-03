from pathlib import Path
from datetime import datetime


class FileHelper:
    def __init__(self, base_path=None):
        self.base_path = Path(base_path).absolute() if base_path else None

    def get_folders(self, extensions):
        if not self.base_path:
            raise ValueError("Base path not set")
        all_folders = []
        for ext in extensions:
            all_folders.extend(self.base_path.rglob(ext))
        return all_folders

    def get_files(self, folders_to_search, extension):
        all_files = []
        for folder in folders_to_search:
            text_file_generators = folder.glob(extension)
            for text_file in text_file_generators:
                all_files.append(text_file)
        return all_files

    @staticmethod
    def get_datetime_folder(date_str):
        dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        folder_name = dt.strftime('%Y-%m-%d_%H-%M-%S')
        return folder_name

    @staticmethod
    def find_csv_folders(path):
        path = Path(path)
        csv_folders = set()
        for item in path.iterdir():
            if item.is_file() and item.name.endswith('.csv'):
                csv_folders.add(str(item.parent.resolve()))
            elif item.is_dir():
                csv_folders.update(FileHelper.find_csv_folders(str(item)))
        return list(csv_folders)