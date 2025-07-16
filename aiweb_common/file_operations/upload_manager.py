import base64
import os
import tempfile
from abc import abstractmethod
from io import BytesIO
from pathlib import Path
from typing import Any, Union

import pandas as pd
import pypandoc
import streamlit as st
from aiweb_common.file_operations.file_handling import ingest_docx_bytes
from docx import Document
from fastapi import BackgroundTasks, HTTPException


class UploadManager:
    @abstractmethod
    def read_file(self, file, extension):
        raise NotImplementedError

    @abstractmethod
    def upload_file(self):
        raise NotImplementedError

    def read_pdf(self, file, document_analysis_client):
        poller = document_analysis_client.begin_analyze_document(
            model_id="prebuilt-read", document=file
        )
        result = poller.result()
        text = ""
        for page in result.pages:
            for line in page.lines:
                text += line.content + "\n"
        return text


class StreamlitUploadManager(UploadManager):
    def __init__(
        self, uploaded_file, accept_multiple_files: bool = False, document_analysis_client=None
    ):
        # print("Initializing Upload Manager")
        self.uploaded_file = uploaded_file
        self.accept_multiple_files = accept_multiple_files
        self.document_analysis_client = document_analysis_client

    def process_upload(self):
        if self.uploaded_file is not None:
            if self.accept_multiple_files:
                data_list = []
                extension_list = []
                for item in self.uploaded_file:
                    extension = Path(item.name).suffix
                    data, extension = self.read_file(item, extension)
                    data_list.append(data)
                    extension_list.append(extension)
                return data_list, extension_list
            else:
                extension = Path(self.uploaded_file.name).suffix
                return self.read_file(self.uploaded_file, extension)
        else:
            st.write("Please upload a file to continue...")
            return None, None

    def read_file(self, file, extension):
        # print("Extension - ", extension)
        if extension == ".xlsx":
            return pd.read_excel(file), extension
        elif extension == ".docx":
            doc = Document(file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text, extension
        elif extension == ".csv":
            return pd.read_csv(file), extension
        elif extension == ".pdf":
            return self.read_pdf(file, self.document_analysis_client), extension
        else:
            return None, None


class FastAPIUploadManager(UploadManager):
    def __init__(self, background_tasks: BackgroundTasks, document_analysis_client=None):
        self.background_tasks = background_tasks
        self.document_analysis_client = document_analysis_client

    def process_file_bytes(self, file: bytes, extension: str) -> Union[pd.DataFrame, str]:
        print("Processing file with extension - ", extension)

        if extension == ".xlsx":
            print("Opening Excel file")
            return pd.read_excel(BytesIO(file))
        elif extension == ".csv":
            return pd.read_csv(BytesIO(file))
        elif extension == ".txt":
            print("Reading text file")
            return file.decode("utf-8")
        elif extension == ".docx":
            doc = Document(BytesIO(file))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        elif extension == ".pdf":
            return self.read_pdf(BytesIO(file), self.document_analysis_client)
        else:
            print("Converting file to Markdown")
            with tempfile.NamedTemporaryFile(delete=True, suffix=extension) as tmpfile:
                tmpfile.write(file)
                tmpfile.seek(0)
                return pypandoc.convert_file(tmpfile.name, "markdown")

    def read_and_validate_file(self, encoded_file: str, extension: str) -> Any:
        try:
            file_bytes = base64.b64decode(encoded_file)
            output = self.process_file_bytes(file_bytes, extension)
            if output is None:
                raise HTTPException(status_code=422, detail="Failed to process the file")
            return output
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) from e


class BytesToDocx(FastAPIUploadManager):
    def __init__(self, background_tasks, document_analysis_client=None):
        super().__init__(background_tasks, document_analysis_client)

    def process_file_bytes(self, file: bytes, extension=".docx") -> Document:
        if extension != ".docx":
            raise TypeError
        cv_in_docx_filepath, cv_in_docx = ingest_docx_bytes(file)
        self.background_tasks.add_task(os.unlink, cv_in_docx_filepath)
        return cv_in_docx
