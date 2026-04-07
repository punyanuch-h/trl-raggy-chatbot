import os
import sys
from unittest.mock import MagicMock, patch

from langchain_core.documents import Document

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_load_txt_returns_document_with_public_metadata():
    with patch("source_document_parser.TextLoader") as MockLoader:
        mock_instance = MagicMock()
        mock_instance.load.return_value = [Document(page_content="TRL 4 content", metadata={})]
        MockLoader.return_value = mock_instance

        from source_document_parser import SourceDocumentParser

        docs = SourceDocumentParser().load("source/trl.txt")

    assert len(docs) == 1
    assert docs[0].metadata["access"] == "public"
    assert docs[0].metadata["source_file"] == "trl.txt"


def test_load_private_txt_returns_document_with_private_metadata():
    with patch("source_document_parser.TextLoader") as MockLoader:
        mock_instance = MagicMock()
        mock_instance.load.return_value = [Document(page_content="Private TRL note", metadata={})]
        MockLoader.return_value = mock_instance

        from source_document_parser import SourceDocumentParser

        docs = SourceDocumentParser().load("source/private/admin-note.txt")

    assert len(docs) == 1
    assert docs[0].metadata["access"] == "private"
    assert docs[0].metadata["source_file"] == "admin-note.txt"


def test_load_pdf_uses_pdf_loader_path():
    with patch("source_document_parser.PyPDFLoader") as MockLoader:
        mock_instance = MagicMock()
        mock_instance.load.return_value = [Document(page_content="PDF TRL content", metadata={})]
        MockLoader.return_value = mock_instance

        from source_document_parser import SourceDocumentParser

        docs = SourceDocumentParser().load("source/trl.pdf")

    assert len(docs) == 1
    MockLoader.assert_called_once_with("source/trl.pdf")
