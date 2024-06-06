import tempfile
import pandas as pd
import pypandoc
import streamlit as st
import pandas as pd
import tempfile
import pypandoc


class UploadManager:

    def read_file(self, file, extension):
        raise NotImplementedError
    
    def upload_file(self):
        raise NotImplementedError


# name for compataibility, will want StreamlitUploadManager eventually
class StreamlitUploadManager(UploadManager):
    def __init__(self, message: str, file_types: list):
        print("Initializing Upload Manager")
        self.message = message
        self.file_types = file_types
        
    def upload_file(self):
        self.uploaded_file = st.file_uploader(self.message, type=self.file_types)
        if self.uploaded_file is not None:
            return self.read_file(self.uploaded_file)
        else:
            st.write("Please upload a file to continue...")
            return None, None
    
    def read_file(self, file, extension):
        print("Extension - ", extension)
        if extension == ".xlsx":
            print("Opening Excel file")
            return pd.read_excel(file), extension
        elif extension == ".docx":
            print("Opening Word file")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmpfile:
                tmpfile.write(file.getvalue())
                return pypandoc.convert_file(tmpfile.name, "markdown"), extension
        return None, None

