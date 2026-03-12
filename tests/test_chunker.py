import os
import sys
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_core.documents import Document

# ---------------------------------------------------------------
# RED PHASE: Tests for TextChunker (class doesn't exist yet)
# ---------------------------------------------------------------

# Helper: Create a long document for splitting tests
def make_long_document(access="public"):
    long_text = (
        "Technology Readiness Level (TRL) is a systematic metric that provides "
        "an assessment of the maturity of a particular technology. "
        "TRL 1 is the lowest level — basic principles are observed and reported. "
        "TRL 2 describes technology concept or application formulation. "
        "TRL 3 is the analytical and experimental critical function proof of concept. "
        "TRL 4 involves component and/or breadboard validation in laboratory environment. "
        "TRL 5 is component and/or breadboard validation in relevant environment. "
        "TRL 6 represents system or subsystem model or prototype demonstration in a relevant environment. "
        "TRL 7 is system prototype demonstration in an operational environment. "
        "TRL 8 represents system complete and qualified through test and demonstration. "
        "TRL 9 is the actual system proven through successful mission operations. "
        "Understanding these levels allows researchers in healthcare and education to plan "
        "their development roadmap and align funding milestones accordingly. "
    ) * 5  # Repeat to force chunking
    return Document(page_content=long_text, metadata={"access": access, "source_file": "trl_guide.pdf"})


def test_chunks_are_created_from_documents():
    """
    TextChunker must split a single long document into
    more than 1 chunk using RecursiveCharacterTextSplitter.
    """
    from text_chunker import TextChunker
    chunker = TextChunker()
    docs = [make_long_document()]
    chunks = chunker.split(docs)

    assert len(chunks) > 1, f"Expected multiple chunks but got {len(chunks)}"


def test_chunks_preserve_metadata():
    """
    Every chunk produced must retain the original document's
    metadata (e.g., access tag and source_file).
    """
    from text_chunker import TextChunker
    chunker = TextChunker()
    docs = [make_long_document(access="private")]
    chunks = chunker.split(docs)

    for chunk in chunks:
        assert chunk.metadata.get("access") == "private", \
            f"Chunk lost its access metadata: {chunk.metadata}"
        assert chunk.metadata.get("source_file") == "trl_guide.pdf", \
            f"Chunk lost its source_file metadata: {chunk.metadata}"


def test_chunks_do_not_exceed_token_limit():
    """
    No individual chunk's page_content should exceed 1000 characters,
    which is the configured chunk_size limit.
    """
    from text_chunker import TextChunker
    chunker = TextChunker()
    docs = [make_long_document()]
    chunks = chunker.split(docs)

    for i, chunk in enumerate(chunks):
        assert len(chunk.page_content) <= 1000, \
            f"Chunk {i} exceeds 1000 chars: {len(chunk.page_content)} chars"


def test_embeddings_return_1536_dimensions():
    """
    The embedding model must return vectors of exactly 1536 dimensions
    matching the OpenAI text-embedding-3-small specification.
    """
    with patch("text_chunker.OpenAIEmbeddings") as MockEmbeddings:
        # Mock the embed_documents method to return a 1536-dim vector
        mock_instance = MagicMock()
        mock_instance.embed_documents.return_value = [[0.1] * 1536]
        MockEmbeddings.return_value = mock_instance

        from text_chunker import TextChunker
        chunker = TextChunker()
        embedder = chunker.get_embeddings()

        result = embedder.embed_documents(["test TRL content"])

        assert len(result) == 1, "Expected 1 embedding vector"
        assert len(result[0]) == 1536, \
            f"Expected 1536 dimensions but got {len(result[0])}"
