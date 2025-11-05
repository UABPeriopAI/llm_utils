import json
import tempfile
from pathlib import Path
import pytest
import pandas as pd
from highres_common.parse_json_file import CsvJsonConverter, JsonFileParser

def test_csv_to_json_conversion():
    converter = CsvJsonConverter()
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "test.csv"
        json_path = Path(tmpdir) / "test.json"

        # Write sample CSV
        csv_path.write_text("Name,Age\nAlice,30\nBob,25", encoding="utf-8")

        # Convert
        converter.convert(csv_path, json_path)

        # Validate JSON
        with json_path.open(encoding="utf-8") as f:
            data = json.load(f)
        assert data == [{"Name": "Alice", "Age": "30"}, {"Name": "Bob", "Age": "25"}]

def test_generate_map_with_dataframe():
    parser = JsonFileParser()
    with tempfile.TemporaryDirectory() as tmpdir:
        parser.raw_dir = Path(tmpdir)
        df = pd.DataFrame({"patient_id": ["A1", "B2", "C3"]})
        mrns = ["001", "002", "003"]

        parser.generate_map(df, mrns)

        output_path = Path(tmpdir) / "mapping.txt"
        assert output_path.exists()

        content = output_path.read_text()
        assert "patient_id,mrn" in content
        assert "A1,001" in content

def test_generate_map_with_iterables():
    parser = JsonFileParser()
    with tempfile.TemporaryDirectory() as tmpdir:
        parser.raw_dir = Path(tmpdir)
        patient_ids = ["X1", "Y2", "Z3"]
        mrns = ["101", "102", "103"]

        parser.generate_map(patient_ids, mrns)

        output_path = Path(tmpdir) / "mapping.txt"
        lines = output_path.read_text().splitlines()
        assert lines[0] == "patient_id,mrn"
        assert lines[1] == "X1,101"

def test_read_json_file():
    parser = JsonFileParser()
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = Path(tmpdir) / "sample.json"
        sample_data = {"foo": "bar"}
        json_path.write_text(json.dumps(sample_data), encoding="utf-8")

        result = parser.read_json_file(json_path)
        assert result == sample_data

def test_parse_json_file(monkeypatch):
    parser = JsonFileParser()

    # Mock sickbay.data.get_ids_from_mrns
    monkeypatch.setattr("your_module.data.get_ids_from_mrns", lambda mrns: pd.DataFrame({"patient_id": mrns}))

    input_json = {
        "patients": [
            {"mrn": "0001", "start_time": "2020-01-01", "stop_time": "2020-01-02"},
            {"mrn": "0002", "start_time": "2020-02-01", "stop_time": "2020-02-02"},
        ]
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        parser.raw_dir = Path(tmpdir)
        ids, starts, stops = parser.parse_json_file(input_json)

        assert list(ids["patient_id"]) == ["1", "2"]
        assert starts == ["2020-01-01", "2020-02-01"]
        assert stops == ["2020-01-02", "2020-02-02"]

def test_generate_json_file(monkeypatch):
    parser = JsonFileParser()

    monkeypatch.setattr("your_module.data.get_ids_from_mrns", lambda mrns: pd.DataFrame({"patient_id": mrns}))

    input_json = {
        "patients": [
            {"mrn": "0001", "start_time": "2020-01-01", "end_time": "2020-01-02"},
            {"mrn": "0002", "start_time": "2020-02-01", "end_time": "2020-02-02"},
        ]
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "output.json"
        parser.raw_dir = Path(tmpdir)

        parser.generate_json_file(input_json, output_path)

        assert output_path.exists()
        df = pd.read_json(output_path, orient="table")
        assert "start_times" in df.columns
        assert "stop_times" in df.columns
        