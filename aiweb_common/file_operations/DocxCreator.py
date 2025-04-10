import os

from docx import Document
from fastapi import BackgroundTasks

from .file_handling import file_to_base64, markdown_to_docx_temporary_file


# TODO add comparable excel class
class DocxCreator:
    """ """

    def __init__(self, background_tasks: BackgroundTasks):
        self.background_tasks = background_tasks

    def convert_markdown_to_docx_bytes(
        self, generated_response, template_filepath=None
    ):
        """
        The `encode_generative_response` function converts a generated response to a base64 string after
        temporarily converting it to a DOCX file.

        Args:
          generated_response: It looks like the `encode_generative_response` method is encoding a generated
        response to a base64 string. The `generated_response` parameter seems to be the content of the
        response that needs to be encoded.

        Returns:
          The `encode_generative_response` method returns the `encoded_file`, which is a base64 string
        representation of a file generated from the `generated_response.content`.
        """
        print("converting markdown to temporary file")
        temp_file_path = markdown_to_docx_temporary_file(
            generated_response, template_location=template_filepath
        )
        encoded_file = file_to_base64(
            temp_file_path
        )  # Convert the file to a base64 string
        print("file encoded")
        self.background_tasks.add_task(os.unlink, temp_file_path)
        return encoded_file
