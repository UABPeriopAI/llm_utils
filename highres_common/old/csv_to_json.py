"""
Module Docstring
"""

__author__ = "Ryan Godwin, PhD"
__version__ = "0.0.1"
__license__ = "MIT"

import argparse
import csv
import json
from pathlib import Path
import itertools

def lower_first(iterator):
    return itertools.chain([next(iterator).lower()], iterator)

def csv_to_json(csvFilePath, jsonFilePath):
    jsonArray = []

    # read csv file
    with open(csvFilePath, encoding="utf-8-sig") as csvf:
        # load csv file data using csv library's dictionary reader
        csvReader = csv.DictReader(lower_first(csvf))

        # convert each csv row into python dict
        for row in csvReader:
            # add this python dict to json array
            jsonArray.append(row)
    
    # convert python jsonArray to JSON String and write to file
    with open(jsonFilePath, "w", encoding="utf-8-sig") as jsonf:
        jsonString = json.dumps(jsonArray, indent=4)
        jsonf.write(jsonString)


def main(args):

    csvFilePath = args.input_csv
    jsonFilePath = args.output_json
    csv_to_json(csvFilePath, jsonFilePath)


if __name__ == "__main__":
    """This is executed when run from the command line"""
    parser = argparse.ArgumentParser()

    # Required positional argument
    parser.add_argument(
        "-json",
        help="JSON output from CSV",
        required=False,
        action="store",
        dest="output_json",
        type=str,
        default=None,
    )

    parser.add_argument("-csv", help="Input CSV", required=True, action="store", dest="input_csv")

    # Specify output of "--version"
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__),
    )

    args = parser.parse_args()

    main(args)
