import pytest
import json
from highres_common.parse_json_file import CsvJsonConverter


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