"""
Utilities for converting CSV to JSON and for parsing/generating patient mapping JSON files.

This module provides:
- CsvJsonConverter: convert CSV files to JSON arrays (handles BOM and lower-casing header).
- JsonFileParser: read/parse/generate JSON files used to map MRNs to patient IDs and produce a
  JSON file suitable for downstream Sickbay processing.

Edits applied to align style with aiweb_common:
- Added module docstring, explicit typing, defensive key access, and logging.
- Generate_json_file now accepts both "stop_time" and "end_time" keys defensively.
- Small resilience improvements when handling iterables vs pandas-like objects.
"""
from __future__ import annotations

import csv
import itertools
import json
import logging
from pathlib import Path
from typing import Any, List, Optional, Union

from sickbay import data

logger = logging.getLogger(__name__)


class CsvJsonConverter:
    """Convert a CSV file into a JSON array file.

    This handles potential UTF-8 BOM in the first header and lower-cases the first header field.
    """

    def __init__(self, encoding: str = "utf-8", indent: int = 4) -> None:
        self.encoding = encoding
        self.indent = indent

    @staticmethod
    def _lower_first(iterator):
        # Consume first line, strip BOM and lowercase first header entry, then chain back
        first = next(iterator)
        first = first.lstrip("\ufeff").lower()
        return itertools.chain([first], iterator)

    def convert(self, csv_path: Union[str, Path], json_path: Union[str, Path]) -> None:
        """Read a CSV and write JSON array to path."""
        csv_path = Path(csv_path)
        json_path = Path(json_path)
        json_array = []

        with csv_path.open(encoding=self.encoding) as csvf:
            reader = csv.DictReader(self._lower_first(csvf))
            for row in reader:
                json_array.append(row)

        json_path.parent.mkdir(parents=True, exist_ok=True)
        with json_path.open("w", encoding=self.encoding) as jsonf:
            json.dump(json_array, jsonf, indent=self.indent)


class JsonFileParser:
    """
    Utilities for reading, parsing and generating JSON files related to patient ID / MRN mappings.

    Typical input structure:
    {
      "patients": [
        {"mrn": "00123", "start_time": "...", "stop_time": "..."},
        ...
      ]
    }
    """

    def __init__(self, raw_dir: Optional[Union[str, Path]] = None) -> None:
        self.raw_dir = Path(raw_dir) if raw_dir is not None else Path.cwd()

    def generate_map(self, patient_ids: Any, mrnlist: List[str]) -> None:
        """
        Create a mapping file that maps patient IDs to MRNs and saves it under the configured raw directory as 'mapping.txt'.

        Accepts either a pandas-like object with .to_csv or an iterable of patient ids.
        """
        # Validate lengths defensively
        try:
            pat_len = len(patient_ids)
        except TypeError:
            patient_ids = list(patient_ids)
            pat_len = len(patient_ids)
        mrn_len = len(mrnlist)
        if pat_len != mrn_len:
            raise ValueError("inputs must be same length")

        output_path = Path(self.raw_dir, "mapping.txt")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Prefer pandas export when available
        if hasattr(patient_ids, "to_csv"):
            try:
                patient_ids = patient_ids.copy()
                patient_ids["mrns"] = mrnlist
                patient_ids.to_csv(output_path, index=False)
                return
            except Exception as e:  # fallback to manual write
                logger.warning("pandas export failed, falling back to manual writer. Reason: %s", e)

        # Fallback: write simple CSV
        with output_path.open("w", encoding="utf-8") as f:
            f.write("patient_id,mrn\n")
            for pid, mrn in zip(patient_ids, mrnlist):
                f.write(f"{pid},{mrn}\n")

    def read_json_file(self, file: Union[str, Path]) -> Any:
        """Read and parse a JSON file and return its contents."""
        file = Path(file)
        if not file.exists():
            raise FileNotFoundError(f"JSON file not found: {file}")
        with file.open(encoding="utf-8") as f:
            return json.load(f)

    def parse_json_file(self, input_json: dict) -> tuple:
        """
        Parse the provided JSON-like dict (expects 'patients') and return
        (patient_ids_dataframe, start_times_list, stop_times_list).

        The MRNs are normalized by stripping leading zeros before resolving patient IDs.
        """
        patients = input_json.get("patients", [])
        mrnlist = [doc.get("mrn", "").lstrip("0") for doc in patients]
        # Accept both "start_time" or "start"
        start_times = [doc.get("start_time", doc.get("start", "")) for doc in patients]
        # Accept both "stop_time" and "end_time"
        stop_times = [doc.get("stop_time", doc.get("end_time", "")) for doc in patients]

        patient_ids = data.get_ids_from_mrns(mrnlist)
        # persist mapping file
        self.generate_map(patient_ids, mrnlist)
        return patient_ids, start_times, stop_times

    def generate_json_file(self, input_json: dict, output_json: Union[str, Path]) -> None:
        """
        Create a JSON file that contains patient IDs and their associated start/stop times.

        - extracts MRNs, start_times, stop_times from input_json
        - resolves patient IDs via sickbay.data.get_ids_from_mrns
        - generates the mapping file (mapping.txt)
        - removes the MRN column and drops rows with missing times
        - writes the resulting DataFrame to the provided output_json path in 'table' orient
        """
        patients = input_json.get("patients", [])
        mrnlist = [doc.get("mrn", "").lstrip("0") for doc in patients]
        start_times = [doc.get("start_time", doc.get("start", "")) for doc in patients]
        stop_times = [doc.get("stop_time", doc.get("end_time", "")) for doc in patients]

        patient_ids = data.get_ids_from_mrns(mrnlist)
        # attach times
        try:
            patient_ids["start_times"] = start_times
            patient_ids["stop_times"] = stop_times
        except Exception as e:
            # If patient_ids is not a DataFrame-like object, log and raise
            logger.error("Expected patient_ids to be a DataFrame-like object: %s", e)
            raise

        # generate and save mapping
        self.generate_map(patient_ids, mrnlist)

        # remove MRNs column if present
        if "mrns" in patient_ids.columns:
            patient_ids.drop(labels=["mrns"], axis=1, inplace=True)

        # drop rows where times are empty strings or null-like
        if "start_times" in patient_ids.columns:
            rows_to_drop = patient_ids[patient_ids["start_times"] == ""].index
            patient_ids.drop(rows_to_drop, inplace=True)
        if "stop_times" in patient_ids.columns:
            rows_to_drop = patient_ids[patient_ids["stop_times"] == ""].index
            patient_ids.drop(rows_to_drop, inplace=True)

        # write dataframe out to json file
        output_path = Path(output_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        patient_ids.to_json(output_path, orient="table", index=False)


# Backwards compatible module-level functions that delegate to JsonFileParser
_parser_singleton = JsonFileParser()


def generate_map(patient_ids, mrnlist) -> None:
    return _parser_singleton.generate_map(patient_ids, mrnlist)


def read_json_file(file) -> Any:
    return _parser_singleton.read_json_file(file)


def parse_json_file(input) -> tuple:
    return _parser_singleton.parse_json_file(input)


def generate_json_file(input, output_json: Path) -> None:
    return _parser_singleton.generate_json_file(input, output_json)