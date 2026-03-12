import os
import sys
import pytest
from unittest.mock import MagicMock, patch, call

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_core.documents import Document


# ---------------------------------------------------------------
# Helpers: Build mock chunks with correct metadata tags
# ---------------------------------------------------------------

def make_chunks(access: str, count: int = 3) -> list:
    return [
        Document(
            page_content=f"TRL content chunk {i}",
            metadata={"access": access, "source_file": "trl_guide.pdf"}
        )
        for i in range(count)
    ]


# ---------------------------------------------------------------
# RED PHASE: Tests for VectorUploader (class doesn't exist yet)
# ---------------------------------------------------------------

def test_public_chunks_do_not_have_admin_role_tag():
    """
    Chunks with access='public' must NOT receive the role='admin'
    metadata tag when uploaded to Pinecone.
    """
    with patch("vector_uploader.OpenAIEmbeddings") as MockEmbed:
        mock_embed_instance = MagicMock()
        mock_embed_instance.embed_documents.return_value = [[0.1] * 1536] * 3
        MockEmbed.return_value = mock_embed_instance

        mock_pinecone_mgr = MagicMock()
        mock_index = MagicMock()
        mock_pinecone_mgr.get_index.return_value = mock_index

        from vector_uploader import VectorUploader
        uploader = VectorUploader(pinecone_manager=mock_pinecone_mgr)
        uploader.upload(make_chunks(access="public"))

        # Inspect what was upserted
        upserted_vectors = mock_index.upsert.call_args[1]["vectors"]
        for vec in upserted_vectors:
            assert vec["metadata"].get("role") != "admin", \
                f"Public chunk should NOT have role='admin': {vec['metadata']}"


def test_private_chunks_have_admin_role_tag():
    """
    Chunks with access='private' must receive role='admin'
    metadata tag when uploaded to Pinecone to enforce RBAC filtering.
    """
    with patch("vector_uploader.OpenAIEmbeddings") as MockEmbed:
        mock_embed_instance = MagicMock()
        mock_embed_instance.embed_documents.return_value = [[0.2] * 1536] * 3
        MockEmbed.return_value = mock_embed_instance

        mock_pinecone_mgr = MagicMock()
        mock_index = MagicMock()
        mock_pinecone_mgr.get_index.return_value = mock_index

        from vector_uploader import VectorUploader
        uploader = VectorUploader(pinecone_manager=mock_pinecone_mgr)
        uploader.upload(make_chunks(access="private"))

        # Inspect what was upserted
        upserted_vectors = mock_index.upsert.call_args[1]["vectors"]
        for vec in upserted_vectors:
            assert vec["metadata"].get("role") == "admin", \
                f"Private chunk MUST have role='admin': {vec['metadata']}"


def test_upload_calls_upsert_exactly_once():
    """
    All chunks must be uploaded in a single batch upsert call
    rather than one call per chunk (performance requirement).
    """
    with patch("vector_uploader.OpenAIEmbeddings") as MockEmbed:
        mock_embed_instance = MagicMock()
        mock_embed_instance.embed_documents.return_value = [[0.3] * 1536] * 3
        MockEmbed.return_value = mock_embed_instance

        mock_pinecone_mgr = MagicMock()
        mock_index = MagicMock()
        mock_pinecone_mgr.get_index.return_value = mock_index

        from vector_uploader import VectorUploader
        uploader = VectorUploader(pinecone_manager=mock_pinecone_mgr)
        uploader.upload(make_chunks(access="public", count=3))

        # Upsert must be called exactly once (batch)
        mock_index.upsert.assert_called_once()
        # Confirm all 3 vectors were passed in the single call
        upserted_vectors = mock_index.upsert.call_args[1]["vectors"]
        assert len(upserted_vectors) == 3
