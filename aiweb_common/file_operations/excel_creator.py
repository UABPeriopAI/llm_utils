import logging
import os
import tempfile

from fastapi import BackgroundTasks

import pandas as pd

from .file_handling import file_to_base64

logger = logging.getLogger(__name__)


class ExcelCreator:
    """
    Parent class that holds the common methods for creating Excel output
    from a pandas DataFrame.
    """

    def write_excel_output(self, tmpfile, df, input_search_terms, query_strings) -> None:
        """
        Write the results DataFrame to an Excel file, along with a summary
        sheet containing the input search terms and the PubMed query.
        """
        with pd.ExcelWriter(tmpfile, engine="xlsxwriter") as writer:
            workbook = writer.book
            df.to_excel(writer, sheet_name="Sheet1", index=False)
            sheet2_data = pd.DataFrame(
                {"Input Terms": [input_search_terms], "PubMed Query": [query_strings]}
            )
            sheet2_data.to_excel(writer, sheet_name="Sheet2", index=False)

            worksheet1 = writer.sheets["Sheet1"]
            worksheet2 = writer.sheets["Sheet2"]

            wrap_format = workbook.add_format({"text_wrap": True})

            # Auto-size columns based on the longest cell content.
            for idx, col in enumerate(df.columns):
                column_len = df[col].fillna("").astype(str).str.len().max()
                max_len = min(100, max(column_len, len(col)))
                worksheet1.set_column(idx, idx, max_len + 1, wrap_format)
            worksheet2.set_column(0, 0, len("Unique Keywords") + 1, wrap_format)

    def get_tempfile_excel(self, articles_df, research_question="", pubmed_query="") -> str:
        """
        Create a temporary .xlsx file from the articles DataFrame and
        return the temp file path.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmpfile:
            temp_file_path = tmpfile.name
        logger.debug("Writing Excel output to temporary file: %s", temp_file_path)
        self.write_excel_output(
            tmpfile=temp_file_path,
            df=articles_df,
            input_search_terms=research_question,
            query_strings=pubmed_query,
        )
        return temp_file_path


class FastAPIExcelCreator(ExcelCreator):
    """
    A specialized ExcelCreator for FastAPI usage.
    Inherits the common Excel-output functionality and adds a method
    to base64-encode the output for returning via FastAPI.
    """

    def __init__(self, background_tasks: BackgroundTasks):
        super().__init__()
        self.background_tasks = background_tasks

    def get_encoded_excel(self, articles_df, research_question="", pubmed_query="") -> str:
        """
        Create a temporary Excel file, base64-encode it for returning via
        FastAPI, and schedule the temp file for cleanup as a background task.
        """
        logger.debug("Creating temporary Excel file")
        temp_file_path = self.get_tempfile_excel(
            articles_df, research_question, pubmed_query
        )
        encoded_file = file_to_base64(temp_file_path)  # Convert file to base64
        logger.debug("File encoded")
        self.background_tasks.add_task(os.unlink, temp_file_path)
        return encoded_file
