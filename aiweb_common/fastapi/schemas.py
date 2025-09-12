from enum import Enum

from pydantic import BaseModel, Field, field_validator

from aiweb_common.fastapi.validators import validate_xlsx_bytes


class UploadableFiles(str, Enum):
    """The class `UploadableFiles` is a subclass of `str` and `Enum` in Python."""

    DOCX = ".docx"
    XLSX = ".xlsx"


class DecodeRequest(BaseModel):
    encoded_data: str
    file_extension: str


class SearchRequest(BaseModel):
    """This class represents a search request in Python."""

    research_question: str


class MSWordResponse(BaseModel):
    """This class likely represents a response from a Microsoft Word document."""

    encoded_docx: str = Field(
        ..., description="Base64-encoded DOCX file. Decode to obtain the DOCX file."
    )


class BibTexResponse(BaseModel):
    """This class represents a response in BibTeX format."""

    encoded_docx: str = Field(
        ..., description="Base64-encoded BIB file. Decode to obtain the BIB file."
    )


class MSExcelResponse(BaseModel):
    """This class likely represents a response from an API that interacts with Microsoft Excel files."""

    encoded_xlsx: str = Field(
        ..., description="Base64-encoded XLSX file. Decode to obtain the XLSX file."
    )


class JSONResponse(BaseModel):
    """
    This class represents a response containing JSON data in a base64-encoded string.
    Decode this string to obtain the original JSON content.
    """

    encoded_json: str = Field(
        ..., description="Base64-encoded JSON data. Decode to obtain the JSON file."
    )


class XLSXinRequest(BaseModel):
    """This class likely represents a request object for handling XLSX file data in a Python application."""

    xlsx_encoded: str = Field(..., description="Base64-encoded XLSX file content.")

    @field_validator("xlsx_encoded")
    @classmethod
    def check_mime_type(cls, v, values, **kwargs):
        """
        The function `check_mime_type` validates XLSX file bytes.

        Args:
          cls: In the provided code snippet, the `cls` parameter is typically used to refer to the class
        itself within a class method. It is a common convention in Python to use `cls` as the first
        parameter in class methods to represent the class object.
          v: The `v` parameter in the `check_mime_type` function likely represents the value that needs
        to be validated or checked for its MIME type. It is passed as an argument to the function when
        it is called.
          values: The `values` parameter typically refers to a dictionary containing all the values
        being passed to the function or method. In this context, it is likely used to pass additional
        information or context to the `check_mime_type` function.

        Returns:
          The `check_mime_type` function is returning the result of calling the `validate_xlsx_bytes`
        function with the arguments `cls`, `v`, and `values`.
        """
        return validate_xlsx_bytes(cls, v, values)
