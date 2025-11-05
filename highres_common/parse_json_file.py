import csv
import itertools
import json
from pathlib import Path
from typing import Union
from sickbay import data

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

class JsonFileParser:
    """
    A class encapsulating utilities for reading, parsing and generating JSON files
    related to patient ID / MRN mappings.
    """

    def __init__(self, raw_dir: Union[str, Path] = None):
        self.raw_dir = Path(raw_dir) if raw_dir is not None else Path.cwd()

    def generate_map(self, patient_ids, mrnlist) -> None:
        """
        Create a mapping file that maps patient IDs to MRNs and saves it under the
        configured raw directory as 'mapping.txt'.
    
        This method is defensive: it accepts either a pandas DataFrame/Series-like
        object that supports .to_csv or a simple iterable of patient ids. It ensures
        the output directory exists and always writes a two-column CSV with header
        "patient_id,mrn".
    
        :param patient_ids: a pandas.DataFrame/Series or any iterable of patient ids
        :param mrnlist: a list of MRN strings
        """
        # Validate lengths
        try:
            pat_len = len(patient_ids)
        except TypeError:
            # if patient_ids is an iterator without len(), materialize it
            patient_ids = list(patient_ids)
            pat_len = len(patient_ids)
        mrn_len = len(mrnlist)
        if pat_len != mrn_len:
            raise ValueError("inputs must be same length")
    
        # Ensure output directory exists
        output_path = Path(self.raw_dir, "mapping.txt")
        output_path.parent.mkdir(parents=True, exist_ok=True)
    
        # If patient_ids looks like a pandas DataFrame/Series, try to attach mrns and use to_csv
        if hasattr(patient_ids, "to_csv"):
            # If it's a DataFrame-like object, add or replace 'mrns' column and write CSV without an index column
            try:
                patient_ids = patient_ids.copy()
                patient_ids["mrns"] = mrnlist
                patient_ids.to_csv(output_path, index=False)
                return
            except (TypeError, ValueError, AttributeError) as e:
                print(f"Warning: pandas export failed, falling back to manual writer. Reason: {e}")
    
        # Fallback: treat patient_ids as an iterable of ids and write a simple CSV
        with output_path.open("w", encoding="utf-8") as f:
            f.write("patient_id,mrn\n")
            for pid, mrn in zip(patient_ids, mrnlist):
                f.write(f"{pid},{mrn}\n")

    def read_json_file(self, file: Union[str, Path]):
        """
        Read and parse a JSON file and return its contents.

        :param file: path to JSON file
        :return: parsed JSON object (usually dict or list)
        """
        file = Path(file)
        with file.open(encoding="utf-8") as f:
            return json.load(f)

    def parse_json_file(self, input_json: dict):
        """
        Parse the provided JSON-like dict (expected format contains 'patients') and
        return patient_ids (from sickbay.data), start_times and stop_times lists.

        :param input_json: dictionary loaded from the JSON input
        :return: tuple(patient_ids_dataframe, start_times_list, stop_times_list)
        """
        mrnlist = [doc["mrn"].lstrip("0") for doc in input_json["patients"]]
        start_times = [doc["start_time"] for doc in input_json["patients"]]
        stop_times = [doc["stop_time"] for doc in input_json["patients"]]

        patient_ids = data.get_ids_from_mrns(mrnlist)
        # persist mapping file
        self.generate_map(patient_ids, mrnlist)
        return patient_ids, start_times, stop_times

    def generate_json_file(self, input_json: dict, output_json: Union[str, Path]):
        """
        Create a JSON file that contains patient IDs and their associated start/stop times.
        This will:
         - extract MRNs, start_times, stop_times from input_json
         - resolve patient IDs via sickbay.data.get_ids_from_mrns
         - generate the mapping file (mapping.txt)
         - remove the MRN column and drop rows with missing times
         - write the resulting DataFrame to the provided output_json path in 'table' orient

        :param input_json: dictionary loaded from the input JSON (expects 'patients')
        :param output_json: path to write the output json
        """
        mrnlist = [doc["mrn"].lstrip("0") for doc in input_json["patients"]]
        start_times = [doc["start_time"] for doc in input_json["patients"]]
        stop_times = [doc["end_time"] for doc in input_json["patients"]]

        patient_ids = data.get_ids_from_mrns(mrnlist)
        patient_ids["start_times"] = start_times
        patient_ids["stop_times"] = stop_times

        # generate and save mapping
        self.generate_map(patient_ids, mrnlist)

        # remove MRNs from the working dataframe
        patient_ids.drop(labels=["mrns"], axis=1, inplace=True)

        # drop rows where times are missing or empty strings
        rows_to_drop = patient_ids[patient_ids["start_times"] == ""].index
        patient_ids.drop(rows_to_drop, inplace=True)
        rows_to_drop = patient_ids[patient_ids["stop_times"] == ""].index
        patient_ids.drop(rows_to_drop, inplace=True)

        # write dataframe out to json file
        output_path = Path(output_json)
        patient_ids.to_json(output_path, orient="table", index=False)

# Backwards compatible module-level functions that delegate to JsonFileParser
_parser_singleton = JsonFileParser()

def generate_map(patient_ids, mrnlist):
    return _parser_singleton.generate_map(patient_ids, mrnlist)

def read_json_file(file):
    return _parser_singleton.read_json_file(file)

def parse_json_file(input):
    return _parser_singleton.parse_json_file(input)

def generate_json_file(input, output_json: Path):
    return _parser_singleton.generate_json_file(input, output_json)