"configuration utils for highres_common"
import csv
import itertools
import json
import os
from pathlib import Path
import random
from typing import Optional, Type, Union
from urllib.request import urlopen
import yaml

import numpy as np

class ConfigUtils:
    """
    Utility class for loading, saving, managing config files in JSON or YAML
    Load configs from url, file, or raw string
    Save configs with sorting and encoding
    """
    def __init__(self, encoding: str = "utf-8", default_format: str = "json"):
        self.encoding = encoding
        self.default_format = default_format

    def load_config_from_url(self, url: Union[str, bytes], file_format: Optional[str] = None) -> dict:
        """
        It loads configuration data from a URL (json or yaml)

        Args:
          url: The URL to load config data from.
          file_format: format to load ("yaml" or "json"). Default "json"
          encoding: response decoding. Default "utf-8"

        Returns:
          A dictionary of the parsed data.
        """

        format_to_use = file_format or self.default_format
        try:
            with urlopen(url) as response:
                data = response.read().decode(self.encoding)
            if format_to_use == "yaml":
                return yaml.safe_load(data)
            else:
                return json.loads(data)
        except Exception as e:
            raise RuntimeError(f"Failed to load JSON from URL '{url}': {e}") from e

    def load_config(
            self,
            source: Union[str, bytes],
            file_format: str = "json"
        ) -> dict:
        """
        Load configuration file from path, URL, or raw string.

        Args:
          source: File path, URL, or raw config string
          format: config format ("json", "yaml")
          encoding: encoding for text based formats

        Returns:
          parsed config as a dictionary

        Raises:
          RuntimeError: If loading fails or the config is invalid
        """

        format_to_use = file_format or self.default_format
        if format_to_use not in {"json", "yaml"}:
            raise ValueError(f"Unsupported config format: {format}")
        try:
            if format_to_use == "json":
                if isinstance(source, str) and source.startswith("http"):
                    with urlopen(source) as response:
                        return json.load(response)
                elif os.path.isfile(source):
                    with open(source, "r", encoding=self.encoding) as fp:
                        return json.load(fp)
                else:
                    return json.loads(source if isinstance(source, str) else source.decode(self.encoding))

            elif format_to_use == "yaml":
                if os.path.isfile(source):
                    with open(source, "r", encoding=self.encoding) as fp:
                        return yaml.safe_load(fp)
                else:
                    return yaml.safe_load(source if isinstance(source, str) else source.decode(self.encoding))
            else:
                raise ValueError(f"Unsupported config format: {format}")
        except Exception as e:
            raise RuntimeError(f"Failed to load JSON: {e}") from e


    def save_config(
            self,
            data: Union[dict, list],
            filepath: str,
            file_format: Optional[str] = None,
            cls: Optional[Type[json.JSONEncoder]] = None,
            sortkeys: bool = False,
            overwrite: bool = True
      ) -> None:
        """
        It saves a dictionary to a JSON or YAML in a specific location.

        Args:
          data: The dictionary or list to serialize.
          filepath: The path to the file to save the dictionary to.
          file_format: format to save ("json" or "yaml")
          cls: A custom JSONEncoder subclass. If specified, the object will use this encoder instead
            of the default.
          sortkeys: If True, the keys of the dictionary are sorted before writing. Defaults to False
          encoding: File encoding (default: "utf-8").
          overwrite: Whether to overwrite the existing file or not. (default: True)

        Raises:
          RuntimeError: If saving fails due to I/O or serialization error.
        """

        format_to_use = file_format or self.default_format
        if not overwrite and os.path.exists(filepath):
            raise RuntimeError(f"File already exists: {filepath}")
        try:
            if format_to_use == "json":
                with open(filepath, "w", encoding=self.encoding) as fp:
                    json.dump(data, indent=2, fp=fp, cls=cls, sort_keys=sortkeys)
            elif format_to_use == "yaml":
                with open(filepath, "w", encoding = self.encoding) as fp:
                    yaml.safe_dump(data, fp, default_flow_style = False)
            else:
                raise ValueError(f"Unsupported config format: {file_format}")
        except Exception as e:
            raise RuntimeError(f"Failed to save dictionary to '{filepath}': {e}") from e

    @staticmethod
    def set_seeds(seed: Union[int, float] = 42) -> int:
        """
        `set_seeds` sets the seed for reproducibility

        Args:
          seed: The seed for the random number generator. Defaults to 42
        
        Returns:
          Seed value used
        """

        # Set seeds
        random.seed(seed)
        np.random.seed(seed)
        return int(seed)

class CsvJsonConverter:
    def __init__(self, encoding: str = "utf-8", indent: int = 4):
        self.encoding = encoding
        self.indent = indent

    @staticmethod
    def _lower_first(iterator):
        first = next(iterator)
        first = first.lstrip('\ufeff').lower()
        return itertools.chain([first], iterator)

    def convert(self, csv_path: Union[str, Path], json_path: Union[str, Path]) -> None:
        csv_path = Path(csv_path)
        json_path = Path(json_path)
        json_array = []

        with csv_path.open(encoding=self.encoding) as csvf:
            reader = csv.DictReader(self._lower_first(csvf))
            for row in reader:
                json_array.append(row)

        with json_path.open("w", encoding=self.encoding) as jsonf:
            json.dump(json_array, jsonf, indent=self.indent)
