# tests/test_tableone_creator.py
import pytest
from pathlib import Path
import tempfile
import os
import pandas as pd
from tableone import TableOne
from highres_common.create_table_one import TableOneCreator

def test_tableone_creation_and_output():
    # Create dummy data
    df = pd.DataFrame({
        "age": [25, 35, 45],
        "sex": ["M", "F", "F"],
        "group": ["A", "B", "A"]
    })

    vars_dict = {
        "columns": ["age", "sex"],
        "groupby": "group",
        "pval": True
    }

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp_input:
        df.to_csv(tmp_input.name, index=False)
        input_path = tmp_input.name

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_output:
        output_path = tmp_output.name

    creator = TableOneCreator(vars_dict, input_path=input_path, output_path=output_path)
    table = creator.create_table_one()

    # Check that the output file was created
    assert Path(output_path).exists(), "Output Excel file was not created"
    assert isinstance(table, TableOne), "Returned object is not a TableOne instance"

    # Clean up
    os.remove(input_path)
    os.remove(output_path)