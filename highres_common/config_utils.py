import json
from urllib.request import urlopen

import numpy as np


def load_json_from_url(url):
    """
    It loads JSON data from a URL

    Args:
      url: The URL to load JSON data from.

    Returns:
      A dictionary of the JSON data.
    """
    data = json.loads(urlopen(url).read())
    return data


def load_dict(filepath):
    """
    Load a dictionary from a JSON's filepath.

    Args:
      filepath: The filepath to the JSON file.

    Returns:
      A dictionary.
    """

    with open(filepath, "r") as fp:
        d = json.load(fp)
    return d


def save_dict(d, filepath, cls=None, sortkeys=False):
    """
    It saves a dictionary to a specific location.

    Args:
      d: The dictionary to save.
      filepath: The path to the file to save the dictionary to.
      cls: A custom JSONEncoder subclass. If specified, the object will use this encoder instead of the
    default.
      sortkeys: If True, the keys of the dictionary are sorted before writing. Defaults to False
    """

    with open(filepath, "w") as fp:
        json.dump(d, indent=2, fp=fp, cls=cls, sort_keys=sortkeys)


def set_seeds(seed=42):
    """
    `set_seeds` sets the seed for reproducibility

    Args:
      seed: The seed for the random number generator. Defaults to 42
    """

    # Set seeds
    seed = np.random.seed(seed)
    return seed
