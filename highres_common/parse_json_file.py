import json
from pathlib import Path

import numpy as np
from sickbay import data

from config import config


def generate_map(patient_ids, mrnlist):
    """
    It takes two lists of the same length, and creates a mapping file that can be used to map the
    patient IDs to the MRNs.

    The function takes two inputs:

    1. A list of patient IDs
    2. A list of MRNs

    The function then checks to make sure that the two lists are the same length. If they are not, it
    will throw an error.

    If they are the same length, it will create a mapping file in the raw data directory.

    The mapping file will be a csv file with two columns:

    1. Patient ID
    2. MRN

    The function will return nothing.

    :param patient_ids: a list of patient ids
    :param mrnlist: a list of MRNs
    """
    # Check to make sure they're the same length

    pat_len = len(patient_ids)
    mrn_len = len(mrnlist)
    if pat_len != mrn_len:
        raise ValueError("inputs must be same length")
    else:
        output_path = Path(config.RAW_DIR, "mapping.txt")
        # textfile = open(output_path, "w")
        patient_ids["mrns"] = mrnlist
        patient_ids.to_csv(output_path)


def read_json_file(file):
    """
    It opens a file, reads the file, and returns the file as a JSON object

    :param file: The file path to the JSON file
    :return: A list of dictionaries.
    """
    # print("JSON File", file)
    with open(file) as f:
        file_list_json = json.load(f)
        # print(file_list_json)
        return file_list_json


def parse_json_file(input):
    """
    It takes in a JSON file, parses it, and returns a list of patient IDs, start times, and stop times

    :param input: the json file that is passed in
    """
    mrnlist = [doc["mrn"].lstrip("0") for doc in input["patients"]]
    # print("mrn list - ", mrnlist)
    start_times = [doc["start_time"] for doc in input["patients"]]
    # print("start times - ", start_times)
    stop_times = [doc["stop_time"] for doc in input["patients"]]
    # print("stop times - ", stop_times)
    patient_ids = data.get_ids_from_mrns(mrnlist)
    print("IDS - ", patient_ids)

    generate_map(patient_ids, mrnlist)
    return patient_ids, start_times, stop_times

def generate_json_file(input, output_json:Path):
    
    mrnlist = [doc["mrn"].lstrip("0") for doc in input["patients"]]
    
    #print("mrn list - ", mrnlist)
    start_times = [doc["start_time"] for doc in input["patients"]]
    #print("start times - ", start_times)
    stop_times = [doc["end_time"] for doc in input["patients"]]
    #print("stop times - ", stop_times)
    patient_ids = data.get_ids_from_mrns(mrnlist)
    patient_ids["start_times"]=start_times
    patient_ids["stop_times"]=stop_times
      
    generate_map(patient_ids, mrnlist)
    
    #Map generated and saved, let's remove the mrn now.
    patient_ids.drop(labels=["mrns"], axis=1,inplace=True)
    
    #drop rows if there is a time missing
    rows_to_drop = patient_ids[patient_ids["start_times"]==''].index
    patient_ids.drop(rows_to_drop, inplace=True)
    rows_to_drop = patient_ids[patient_ids["stop_times"]==''].index
    patient_ids.drop(rows_to_drop, inplace=True)
           
    #write dataframe out to json file
    patient_ids.to_json(output_json, orient = 'table', index=False)