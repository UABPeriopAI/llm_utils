# Requirements
from pathlib import Path
from typing import Dict, Union
import logging
import pandas as pd
from tableone import TableOne

logger = logging.getLogger(__name__)

class TableOneCreator():
    def __init__(
            self,
            vars_dict: Dict,
            input_path: Union[str, Path],
            output_path: Union[str, Path] = None
    ):
        """Create a TableOne summary from a dataset
        
        Args:
            vars_dict: Dictionary of TableOne variable settings.
            input_path: Path to input csv file
            output_path: Optional path to save excel file
        """
        self.vars_dict=vars_dict
        self.input_path = Path(input_path)
        if output_path is None:
            raise ValueError("Output path must be specified for TableOne export.")
        self.output_path = Path(output_path)

    def create_table_one(self) -> TableOne:
        """
        Generate and save a TableOne Summary table
        
        Returns:
            TableOne object
        """

        df = pd.read_csv(self.input_path) # load data
        mytable = TableOne(data=df, **self.vars_dict) # create TableOne
        self.output_path.parent.mkdir(parents=True, exist_ok=True) # save to excel
        mytable.to_excel(self.output_path)
        logger.info(f"✅ Saved Tableone to {self.output_path}")
        return mytable
    