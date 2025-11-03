import os
import tempfile
import json
import random
import numpy as np
import pytest

from highres_common.config_utils import ConfigUtils, CsvJsonConverter


# Create a reusable instance for tests
config_utils = ConfigUtils()

# --- Test set_seeds ---
def test_set_seeds_reproducibility():
    ConfigUtils.set_seeds(123)
    a = [random.random() for _ in range(3)]
    b = np.random.rand(3)

    ConfigUtils.set_seeds(123)
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

    config_utils.save_config(data, filepath=path, file_format=file_format)
    loaded = config_utils.load_config(path, file_format=file_format)
    assert loaded == data, f"{file_format.upper()} roundtrip failed"

    os.remove(path)

# --- Test load_config from raw string ---
def test_load_config_from_string_json():
    raw = '{"x": 1, "y": [2, 3]}'
    result = config_utils.load_config(raw, file_format="json")
    assert result == {"x": 1, "y": [2, 3]}

def test_load_config_from_string_yaml():
    raw = "x: 1\ny:\n  - 2\n  - 3"
    result = config_utils.load_config(raw, file_format="yaml")
    assert result == {"x": 1, "y": [2, 3]}

# --- Test load_config_from_url ---
@pytest.mark.parametrize("url,file_format", [
    ("https://raw.githubusercontent.com/vega/vega/master/docs/data/movies.json", "json"),
    #("https://raw.githubusercontent.com/OAI/OpenAPI-Specification/main/examples/v3.0/petstore-expanded.yaml", "yaml")
])

def test_load_config_from_url(url, file_format):
    result = config_utils.load_config_from_url(url, file_format=file_format)
    assert isinstance(result, (dict, list)), f"{file_format.upper()} from URL did not return a dict or list"

def test_csv_to_json_conversion(tmp_path):
    # Setup paths
    input_csv = tmp_path / "test.csv"
    output_json = tmp_path / "test.json"

    # Write sample CSV content
    input_csv.write_text("Name,Age\nAlice,30\nBob,25", encoding="utf-8-sig")

    # Convert
    converter = CsvJsonConverter()
    converter.convert(input_csv, output_json)

    # Validate output
    result = json.loads(output_json.read_text(encoding="utf-8-sig"))
    assert result == [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "25"}]
