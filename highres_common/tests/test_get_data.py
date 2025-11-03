from pathlib import Path
from datetime import datetime
import pytest
from highres_common.get_data import FileHelper  # Adjust import path as needed

def test_get_datetime_folder():
    date_str = "2025-11-03 09:00:00"
    expected = "2025-11-03_09-00-00"
    assert FileHelper.get_datetime_folder(date_str) == expected

def test_find_csv_folders(tmp_path):
    # Setup nested folders with CSV files
    folder_a = tmp_path / "a"
    folder_b = tmp_path / "a" / "b"
    folder_b.mkdir(parents=True)
    (folder_a / "file1.csv").write_text("data")
    (folder_b / "file2.csv").write_text("data")

    found = FileHelper.find_csv_folders(tmp_path)
    assert str(folder_a.resolve()) in found
    assert str(folder_b.resolve()) in found
    assert len(found) == 2

def test_get_folders(tmp_path):
    # Create dummy files
    (tmp_path / "file1.txt").write_text("text")
    (tmp_path / "file2.csv").write_text("csv")
    helper = FileHelper(tmp_path)
    folders = helper.get_folders(["*.txt", "*.csv"])
    assert any(f.name == "file1.txt" for f in folders)
    assert any(f.name == "file2.csv" for f in folders)

def test_get_files(tmp_path):
    # Create folders and files
    folder = tmp_path / "data"
    folder.mkdir()
    (folder / "log1.txt").write_text("log")
    (folder / "log2.txt").write_text("log")
    helper = FileHelper()
    files = helper.get_files([folder], "*.txt")
    assert len(files) == 2
    assert all(f.name.startswith("log") for f in files)