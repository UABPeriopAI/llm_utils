# Requirements
from tableone import TableOne
import pandas as pd
from config import config
from config.config import logger
from pathlib import Path

class TableOneCreator():
    def __init__(self, vars_dict):
        self.vars_dict=vars_dict
    
    def create_table_one(self):
        #read
        df = pd.read_csv(config.PATIENT_DETAILS)

        mytable = TableOne(data=df, **self.vars_dict)

        mytable.to_excel(Path(config.RESULTS_DIR, "table1.xlsx"))
        logger.info("✅ Saved Tableone")