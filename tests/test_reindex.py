import os
import sys
import pytest
from unittest.mock import MagicMock, patch, call

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_core.documents import Document


# ---------------------------------------------------------------
# RED PHASE: Tests for Reindexer (class doesn't exist yet)
# ---------------------------------------------------------------

def test_reindex_scans_both_source_folders():
    """
    Reindexer.run() must discover PDF files from BOTH
    source/ and source/private/ directories.
    """
    fake_files = [
        "source/trl_basics.pdf",
        "source/trl_advanced.pdf",
        "source/private/admin_trl_notes.pdf",
    ]

    with patch("reindex.glob.glob") as mock_glob, \
         patch("reindex.PDFParser") as MockParser, \
         patch("reindex.TextChunker") as MockChunker, \
         patch("reindex.VectorUploader") as MockUploader, \
         patch("reindex.PineconeManager"):

        mock_glob.return_value = fake_files
        MockParser.return_value.load.return_value = [
            Document(page_content="TRL content", metadata={"access": "public"})
        ]
        MockChunker.return_value.split.return_value = [
            Document(page_content="TRL chunk", metadata={"access": "public"})
        ]
        MockUploader.return_value.upload.return_value = None

        from reindex import Reindexer
        reindexer = Reindexer()
        reindexer.run()

        # Confirm glob was called to search for PDFs
        mock_glob.assert_called_once()
        # Confirm all 3 files were passed to PDFParser individually
        assert MockParser.return_value.load.call_count == 3


def test_reindex_processes_private_files_with_admin_tag():
    """
    Any PDF discovered under source/private/ must result in
    Document chunks tagged with access='private'.
    """
    private_doc = Document(
        page_content="Confidential admin TRL data",
        metadata={"access": "private", "source_file": "admin_trl_notes.pdf"}
    )
    private_chunk = Document(
        page_content="Confidential chunk",
        metadata={"access": "private", "source_file": "admin_trl_notes.pdf"}
    )

    with patch("reindex.glob.glob") as mock_glob, \
         patch("reindex.PDFParser") as MockParser, \
         patch("reindex.TextChunker") as MockChunker, \
         patch("reindex.VectorUploader") as MockUploader, \
         patch("reindex.PineconeManager"):

        mock_glob.return_value = ["source/private/admin_trl_notes.pdf"]
        MockParser.return_value.load.return_value = [private_doc]
        MockChunker.return_value.split.return_value = [private_chunk]

        from reindex import Reindexer
        reindexer = Reindexer()
        reindexer.run()

        # Confirm the upload was called with the private chunk
        uploaded_chunks = MockUploader.return_value.upload.call_args[0][0]
        for chunk in uploaded_chunks:
            assert chunk.metadata.get("access") == "private", \
                f"Private file must produce private chunks: {chunk.metadata}"


def test_reindex_calls_upload_for_all_files():
    """
    VectorUploader.upload() must be invoked once for each
    discovered PDF file during a reindex run.
    """
    fake_files = [
        "source/trl_basics.pdf",
        "source/trl_advanced.pdf",
        "source/private/admin_trl_notes.pdf",
    ]

    with patch("reindex.glob.glob") as mock_glob, \
         patch("reindex.PDFParser") as MockParser, \
         patch("reindex.TextChunker") as MockChunker, \
         patch("reindex.VectorUploader") as MockUploader, \
         patch("reindex.PineconeManager"):

        mock_glob.return_value = fake_files
        MockParser.return_value.load.return_value = [
            Document(page_content="chunk", metadata={"access": "public"})
        ]
        MockChunker.return_value.split.return_value = [
            Document(page_content="chunk", metadata={"access": "public"})
        ]

        from reindex import Reindexer
        reindexer = Reindexer()
        reindexer.run()

        # Upload must be called once per file (3 times total)
        assert MockUploader.return_value.upload.call_count == 3, \
            f"Expected 3 upload calls, got {MockUploader.return_value.upload.call_count}"
