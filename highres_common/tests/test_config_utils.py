import os
import tempfile
import json
import random
import numpy as np
import pytest

from highres_common.config_utils import (
    load_config,
    load_config_from_url,
    save_config,
    set_seeds
)

# --- Test set_seeds ---
def test_set_seeds_reproducibility():
    set_seeds(123)
    a = [random.random() for _ in range(3)]
    b = np.random.rand(3)

    set_seeds(123)
    a2 = [random.random() for _ in range(3)]
    b2 = np.random.rand(3)

    assert a == a2, "Python random not reproducible"
    assert np.allclose(b, b2), "NumPy random not reproducible"

# --- Test save_config and load_config roundtrip ---
@pytest.mark.parametrize("file_format", ["json", "yaml"])
def test_config_roundtrip(file_format):
    data = {"name": "Caitlin", "values": [1, 2, 3], "active": True}
    suffix = ".json" if file_format == "json" else ".yaml"

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        path = tmp.name

    save_config(data, filepath=path, file_format=file_format)
    loaded = load_config(path, file_format=file_format)
    assert loaded == data, f"{file_format.upper()} roundtrip failed"

    os.remove(path)

# --- Test load_config from raw string ---
def test_load_config_from_string_json():
    raw = '{"x": 1, "y": [2, 3]}'
    result = load_config(raw, file_format="json")
    assert result == {"x": 1, "y": [2, 3]}

def test_load_config_from_string_yaml():
    raw = "x: 1\ny:\n  - 2\n  - 3"
    result = load_config(raw, file_format="yaml")
    assert result == {"x": 1, "y": [2, 3]}

# --- Test load_config_from_url ---
@pytest.mark.parametrize("url,file_format", [
    ("https://raw.githubusercontent.com/vega/vega/master/docs/data/movies.json", "json"),
    ("https://raw.githubusercontent.com/OAI/OpenAPI-Specification/main/examples/v3.0/petstore-expanded.yaml", "yaml")
])
def test_load_config_from_url(url, file_format):
    result = load_config_from_url(url, file_format=file_format)
    assert isinstance(result, (dict, list)), f"{file_format.upper()} from URL did not return a dict or list"