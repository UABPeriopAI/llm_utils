"""
Document processor abstraction for PDF text extraction.

Provides a common interface (DocumentProcessor) with two implementations:
- AzureDocAIProcessor: uses Azure Document Intelligence (prebuilt-read model)
- DoclingProcessor: uses a self-hosted Docling server via HTTP API
"""

import io
import logging
from abc import ABC, abstractmethod

import requests

logger = logging.getLogger(__name__)


class DocumentProcessor(ABC):
    """Abstract base class for PDF text extraction backends."""

    @abstractmethod
    def extract_text(self, file_bytes: bytes) -> str:
        """Extract text from a PDF file.

        Args:
            file_bytes: Raw bytes of the PDF document.

        Returns:
            Plain text string extracted from the document.
        """
        ...


class AzureDocAIProcessor(DocumentProcessor):
    """Extract text from PDFs using Azure Document Intelligence."""

    def __init__(self, client):
        """
        Args:
            client: An Azure ``DocumentAnalysisClient`` instance.
        """
        self._client = client

    def extract_text(self, file_bytes: bytes) -> str:
        poller = self._client.begin_analyze_document(
            model_id="prebuilt-read", document=io.BytesIO(file_bytes)
        )
        result = poller.result()
        text = ""
        for page in result.pages:
            for line in page.lines:
                text += line.content + "\n"
        return text


class DoclingProcessor(DocumentProcessor):
    """Extract text from PDFs using a self-hosted Docling server."""

    def __init__(self, endpoint: str, api_key: str):
        """
        Args:
            endpoint: Base URL of the Docling service (e.g. ``http://docling:8080``).
            api_key: API key sent via the ``X-Api-Key`` header.
        """
        self._endpoint = endpoint.rstrip("/")
        self._api_key = api_key

    def extract_text(self, file_bytes: bytes) -> str:
        resp = requests.post(
            f"{self._endpoint}/v1/convert/file",
            files={"files": ("document.pdf", file_bytes, "application/pdf")},
            data={"to_formats": ["text"], "from_formats": ["pdf"]},
            headers={"accept": "application/json", "X-Api-Key": self._api_key},
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") != "success":
            errors = data.get("errors", [])
            raise RuntimeError(f"Docling conversion failed: {errors}")
        return data["document"]["text_content"] or ""
