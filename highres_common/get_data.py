"""
Filesystem helpers used by highres_common.

Provides FileHelper for discovering folders/files by extension and formatting datetime-based folder names.
"""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

logger = logging.getLogger(__name__)


class FileHelper:
    """
    Small helper to locate folders and files and format datetime-based folder names.

    Args:
        base_path: Optional path used as the root for searches. If not provided, methods that
                   require a base_path will raise a ValueError.
    """

    def __init__(self, base_path: Optional[str | Path] = None) -> None:
        self.base_path = Path(base_path).absolute() if base_path else None

    def get_folders(self, extensions: Iterable[str]) -> List[Path]:
        """
        Search recursively under base_path for folders that match the provided glob patterns.

        Args:
            extensions: Iterable of glob patterns (e.g., ['*.csv', '*.txt']) applied via rglob.

        Returns:
            List[Path] of matching folders.

        Raises:
            ValueError: if base_path is not configured.
        """
        if not self.base_path:
            raise ValueError("Base path not set")
        all_folders: List[Path] = []
        for ext in extensions:
            all_folders.extend([p.parent for p in self.base_path.rglob(ext)])
        # deduplicate while preserving order
        seen = set()
        unique = []
        for p in all_folders:
            if p not in seen:
                seen.add(p)
                unique.append(p)
        return unique

    def get_files(self, folders_to_search: Iterable[Path], extension: str) -> List[Path]:
        """
        List files with the given extension inside the provided folders.

        Args:
            folders_to_search: Iterable of folder Paths to search.
            extension: Glob pattern for files inside each folder (e.g., '*.csv').

        Returns:
            List[Path] of matching files.
        """
        all_files: List[Path] = []
        for folder in folders_to_search:
            folder = Path(folder)
            if not folder.exists():
                logger.debug("Skipping non-existent folder: %s", folder)
                continue
            text_file_generators = folder.glob(extension)
            for text_file in text_file_generators:
                all_files.append(text_file)
        return all_files

    @staticmethod
    def get_datetime_folder(date_str: str) -> str:
        """
        Convert a datetime string 'YYYY-MM-DD HH:MM:SS' into a filesystem-safe folder name
        'YYYY-MM-DD_HH-MM-SS'.

        Args:
            date_str: Input date string in '%Y-%m-%d %H:%M:%S' format.

        Returns:
            Folder name string.
        """
        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        folder_name = dt.strftime("%Y-%m-%d_%H-%M-%S")
        return folder_name

    @staticmethod
    def find_csv_folders(path: str | Path) -> List[str]:
        """
        Recursively find folders that contain CSV files under the provided path.

        Args:
            path: Starting directory to search.

        Returns:
            List[str] of folder paths (resolved as strings) that contain at least one .csv file.
        """
        path = Path(path)
        csv_folders = set()
        for item in path.iterdir():
            try:
                if item.is_file() and item.name.endswith(".csv"):
                    csv_folders.add(str(item.parent.resolve()))
                elif item.is_dir():
                    csv_folders.update(FileHelper.find_csv_folders(str(item)))
            except PermissionError:
                logger.warning("Permission denied while scanning: %s", item)
        return list(csv_folders)