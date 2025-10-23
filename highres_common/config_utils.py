"configuration utils for highres_common"
import json
import os
import random
from typing import Optional, Type, Union
from urllib.request import urlopen
import yaml

import numpy as np


def load_config_from_url(url: Union[str, bytes], file_format: str = "json", encoding: str = "utf-8"
) -> dict:
    """
    It loads configuration data from a URL (json or yaml)

    Args:
      url: The URL to load config data from.
      file_format: format to load ("yaml" or "json"). Default "json"
      encoding: response decoding. Default "utf-8"

    Returns:
      A dictionary of the parsed data.
    """

    try:
        with urlopen(url) as response:
            data = response.read().decode(encoding)
        if file_format == "yaml":
            return yaml.safe_load(data)
        else:
            return json.loads(data)
    except Exception as e:
        raise RuntimeError(f"Failed to load JSON from URL '{url}': {e}") from e

def load_config(
        source: Union[str, bytes],
        file_format: str = "json",
        encoding: str = "utf-8"
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
    if file_format not in {"json", "yaml"}:
        raise ValueError(f"Unsupported config format: {format}")
    try:
        if file_format == "json":
            if isinstance(source, str) and source.startswith("http"):
                with urlopen(source) as response:
                    return json.load(response)
            elif os.path.isfile(source):
                with open(source, "r", encoding="utf-8") as fp:
                    return json.load(fp)
            else:
                return json.loads(source if isinstance(source, str) else source.decode(encoding))

        elif file_format == "yaml":
            if os.path.isfile(source):
                with open(source, "r", encoding="utf-8") as fp:
                    return yaml.safe_load(fp)
            else:
                return yaml.safe_load(source if isinstance(source, str) else source.decode(encoding))
        else:
            raise ValueError(f"Unsupported config format: {format}")
    except Exception as e:
        raise RuntimeError(f"Failed to load JSON: {e}") from e


def save_config(
        data: Union[dict, list],
        filepath: str,
        file_format: str = "jsn",
        encoding: str = "utf-8",
        cls: Optional[Type[json.JSONEncoder]] = None,
        sortkeys: bool = False,
        overwrite: bool = True
  ) -> None:
    """
    It saves a dictionary to a JSON or YAML in a specific location.

    Args:
      data: The dictionary orlist to serialize.
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
    if not overwrite and os.path.exists(filepath):
        raise RuntimeError(f"File already exists: {filepath}")
    try:
        if file_format == "json":
            with open(filepath, "w", encoding="utf-8") as fp:
                json.dump(data, indent=2, fp=fp, cls=cls, sort_keys=sortkeys)
        elif file_format == "yaml":
            with open(filepath, "w", encoding = encoding) as fp:
                yaml.safe_dump(data, fp, default_flow_style = False)
        else:
            raise ValueError(f"Unsupported config format: {file_format}")
    
    except Exception as e:
        raise RuntimeError(f"Failed to save dictionary to '{filepath}': {e}") from e


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
