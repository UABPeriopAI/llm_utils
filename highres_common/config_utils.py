"""
configuration utils for highres_common

Provides ConfigUtils: load/save configs (JSON/YAML) from URLs, files, or raw strings,
and a convenience method to set random seeds for reproducibility.
"""
import json
import logging
import os
from pathlib import Path
import random
from typing import Any, Optional, Type, Union
from urllib.request import urlopen

import yaml
import numpy as np

logger = logging.getLogger(__name__)


class ConfigUtils:
    """
    Utility class for loading, saving, and managing config files in JSON or YAML.

    Supports loading from URLs, file paths, or raw strings. Saves configs with
    optional sorting and custom JSON encoders.
    """

    def __init__(self, encoding: str = "utf-8", default_format: str = "json"):
        self.encoding = encoding
        self.default_format = default_format

    def load_config_from_url(self, url: Union[str, bytes], file_format: Optional[str] = None) -> dict:
        """
        Load configuration data from a URL (JSON or YAML).

        Args:
            url: The URL to load config data from.
            file_format: Format to load ("yaml" or "json"). Defaults to instance default.

        Returns:
            A dictionary of the parsed data.

        Raises:
            RuntimeError: If fetching or parsing fails.
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
            raise RuntimeError(f"Failed to load configuration from URL '{url}': {e}") from e

    def load_config(
        self,
        source: Union[str, bytes],
        file_format: Optional[str] = None,
    ) -> dict:
        """
        Load configuration from a path, URL, or raw string.

        Args:
            source: File path, URL, or raw config string/bytes.
            file_format: 'json' or 'yaml'. If None, uses the instance default.

        Returns:
            Parsed configuration as a dictionary.

        Raises:
            ValueError: If an unsupported format is requested.
            RuntimeError: If loading/parsing fails.
        """
        
        format_to_use = file_format or self.default_format
        if format_to_use not in {"json", "yaml"}:
            raise ValueError(f"Unsupported config format: {format_to_use}")

        try:
            # JSON handling
            if format_to_use == "json":
                if isinstance(source, str) and source.startswith("http"):
                    with urlopen(source) as response:
                        return json.load(response)
                elif os.path.isfile(source):
                    with open(source, "r", encoding=self.encoding) as fp:
                        return json.load(fp)
                else:
                    return json.loads(source if isinstance(source, str) else source.decode(self.encoding))

            # YAML handling
            elif format_to_use == "yaml":
                if os.path.isfile(source):
                    with open(source, "r", encoding=self.encoding) as fp:
                        return yaml.safe_load(fp)
                else:
                    return yaml.safe_load(source if isinstance(source, str) else source.decode(self.encoding))
            else:
                # Defensive, though earlier check prevents this path
                raise ValueError(f"Unsupported config format: {format_to_use}")
        except Exception as e:
            raise RuntimeError(f"Failed to load configuration: {e}") from e

    def save_config(
        self,
        data: Union[dict, list],
        filepath: str,
        file_format: Optional[str] = None,
        cls: Optional[Type[json.JSONEncoder]] = None,
        sortkeys: bool = False,
        overwrite: bool = True,
    ) -> None:
        """
        Save a dictionary or list to JSON or YAML.

        Args:
            data: The dictionary or list to serialize.
            filepath: The path to the file to save the data to.
            file_format: 'json' or 'yaml'. If None, uses the instance default.
            cls: Optional custom JSONEncoder subclass.
            sortkeys: If True, the keys of the dictionary are sorted before writing.
            overwrite: Whether to overwrite an existing file.

        Raises:
            RuntimeError: If saving fails due to I/O or serialization error.
        """
        format_to_use = file_format or self.default_format
        if format_to_use not in {"json", "yaml"}:
            raise ValueError(f"Unsupported config format: {format_to_use}")

        if not overwrite and os.path.exists(filepath):
            raise RuntimeError(f"File already exists: {filepath}")

        try:
            if format_to_use == "json":
                with open(filepath, "w", encoding=self.encoding) as fp:
                    # json.dump(obj, fp, ...) argument order: object first, file second
                    json.dump(data, fp, indent=2, cls=cls, sort_keys=sortkeys)
            elif format_to_use == "yaml":
                with open(filepath, "w", encoding=self.encoding) as fp:
                    yaml.safe_dump(data, fp, default_flow_style=False)
            else:
                raise ValueError(f"Unsupported config format: {format_to_use}")
        except Exception as e:
            raise RuntimeError(f"Failed to save configuration to '{filepath}': {e}") from e

    @staticmethod
    def set_seeds(seed: Union[int, float] = 42) -> int:
        """
        Set random seeds for deterministic behavior in tests/experiments.

        Args:
            seed: The seed for the random number generator. Defaults to 42.

        Returns:
            The integer seed value used.
        """
        random.seed(seed)
        np.random.seed(int(seed))
        return int(seed)
