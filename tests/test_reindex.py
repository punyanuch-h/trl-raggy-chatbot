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

    with patch("reindex.discover_source_files") as mock_discover, \
         patch("reindex.SourceDocumentParser") as MockParser, \
         patch("reindex.TextChunker") as MockChunker, \
         patch("reindex.VectorUploader") as MockUploader, \
         patch("reindex.PineconeManager"):

        mock_discover.return_value = fake_files
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
        mock_discover.assert_called_once()
        # Confirm all 3 files were passed to the parser individually
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

    with patch("reindex.discover_source_files") as mock_discover, \
         patch("reindex.SourceDocumentParser") as MockParser, \
         patch("reindex.TextChunker") as MockChunker, \
         patch("reindex.VectorUploader") as MockUploader, \
         patch("reindex.PineconeManager"):

        mock_discover.return_value = ["source/private/admin_trl_notes.pdf"]
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

    with patch("reindex.discover_source_files") as mock_discover, \
         patch("reindex.SourceDocumentParser") as MockParser, \
         patch("reindex.TextChunker") as MockChunker, \
         patch("reindex.VectorUploader") as MockUploader, \
         patch("reindex.PineconeManager"):

        mock_discover.return_value = fake_files
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


def test_reindex_discovers_supported_pdf_and_txt_files():
    fake_files = [
        "source/trl_basics.pdf",
        "source/04_Technology Readiness Level-TRL.txt",
        "source/private/admin_trl_notes.pdf",
        "source/ignore.md",
    ]

    with patch("reindex.Path.rglob", return_value=fake_files):
        from reindex import discover_source_files

        discovered = discover_source_files()

    assert discovered == [
        "source/04_Technology Readiness Level-TRL.txt",
        "source/private/admin_trl_notes.pdf",
        "source/trl_basics.pdf",
    ]


def test_reindex_loads_txt_files_with_preserved_metadata():
    fake_doc = Document(page_content="TRL 4 definition", metadata={})

    with patch("reindex.Path.rglob", return_value=["source/example.txt"]), \
         patch("reindex.SourceDocumentParser") as MockParser, \
         patch("reindex.TextChunker") as MockChunker, \
         patch("reindex.VectorUploader") as MockUploader, \
         patch("reindex.PineconeManager"):
        MockParser.return_value.load.return_value = [fake_doc]
        MockChunker.return_value.split.return_value = [
            Document(page_content="TRL 4 definition", metadata={"access": "public", "source_file": "example.txt"})
        ]

        from reindex import Reindexer

        Reindexer().run()

        MockParser.return_value.load.assert_called_once_with("source/example.txt")
        uploaded_chunk = MockUploader.return_value.upload.call_args[0][0][0]
        assert uploaded_chunk.metadata["access"] == "public"
        assert uploaded_chunk.metadata["source_file"] == "example.txt"


def test_reindex_skips_unsupported_files_with_clear_log():
    with patch("reindex.Path.rglob", return_value=["source/notes.md"]), \
         patch("reindex.SourceDocumentParser") as MockParser, \
         patch("reindex.TextChunker") as MockChunker, \
         patch("reindex.VectorUploader") as MockUploader, \
         patch("reindex.PineconeManager"), \
         patch("builtins.print") as mock_print:
        from reindex import Reindexer

        Reindexer().run()

        MockParser.return_value.load.assert_not_called()
        MockChunker.return_value.split.assert_not_called()
        MockUploader.return_value.upload.assert_not_called()
        assert any("Skipping unsupported file" in str(call.args[0]) for call in mock_print.call_args_list)
