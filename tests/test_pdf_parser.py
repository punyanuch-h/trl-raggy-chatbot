import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# Add root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_core.documents import Document


# ---------------------------------------------------------------
# RED PHASE: Tests for PDFParser (class doesn't exist yet)
# ---------------------------------------------------------------

def test_load_pdf_returns_text():
    """
    PDFParser must return a non-empty list of Document objects
    with populated page_content from the PDF.
    """
    with patch("pdf_parser.PyPDFLoader") as MockLoader:
        mock_instance = MagicMock()
        mock_instance.load.return_value = [
            Document(page_content="Technology Readiness Level 4 means...", metadata={})
        ]
        MockLoader.return_value = mock_instance

        from pdf_parser import PDFParser
        parser = PDFParser()
        docs = parser.load("source/trl_guide.pdf")

        assert len(docs) > 0
        assert docs[0].page_content != ""


def test_load_public_pdf_has_public_tag():
    """
    PDFs loaded from the standard source/ folder must be tagged 
    with metadata access='public'.
    """
    with patch("pdf_parser.PyPDFLoader") as MockLoader:
        mock_instance = MagicMock()
        mock_instance.load.return_value = [
            Document(page_content="TRL public document content.", metadata={})
        ]
        MockLoader.return_value = mock_instance

        from pdf_parser import PDFParser
        parser = PDFParser()
        docs = parser.load("source/trl_guide.pdf")

        for doc in docs:
            assert doc.metadata.get("access") == "public", \
                f"Expected 'public' tag but got: {doc.metadata.get('access')}"


def test_load_private_pdf_has_admin_tag():
    """
    PDFs loaded from source/private/ must be detected and tagged 
    with metadata access='private' to enforce RBAC privacy rules.
    """
    with patch("pdf_parser.PyPDFLoader") as MockLoader:
        mock_instance = MagicMock()
        mock_instance.load.return_value = [
            Document(page_content="Confidential admin-only TRL data.", metadata={})
        ]
        MockLoader.return_value = mock_instance

        from pdf_parser import PDFParser
        parser = PDFParser()
        # Simulating a file from a private subfolder (Windows or Unix paths)
        docs = parser.load("source/private/admin_trl_notes.pdf")

        for doc in docs:
            assert doc.metadata.get("access") == "private", \
                f"Expected 'private' tag but got: {doc.metadata.get('access')}"
