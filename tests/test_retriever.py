import os
import sys
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_core.documents import Document

# ---------------------------------------------------------------
# RED PHASE: Tests for Role-Based Vector Retrieval
# ---------------------------------------------------------------

def test_researcher_retrieval_adds_metadata_filter():
    """
    If the user is a 'researcher', the retriever must inject a metadata 
    filter that explicitly excludes 'admin' role content.
    """
    with patch("rag_retriever.PineconeVectorStore") as MockStore, \
         patch("rag_retriever.OpenAIEmbeddings") as MockEmbed, \
         patch("rag_retriever.PineconeManager") as MockManager:

        # Mock OpenAI to prevent api_key error
        MockEmbed.return_value = MagicMock()
        MockManager.return_value = MagicMock()
        
        mock_vectorstore = MagicMock()
        MockStore.from_existing_index.return_value = mock_vectorstore
        
        # We need to mock the call to as_retriever()
        mock_retriever = MagicMock()
        mock_vectorstore.as_retriever.return_value = mock_retriever
        
        from rag_retriever import get_retriever
        
        # Test for researcher
        get_retriever(role="researcher")
        
        # Verify that as_retriever was called with the correct filter
        # The filter should exclude 'admin'
        mock_vectorstore.as_retriever.assert_called_once()
        args, kwargs = mock_vectorstore.as_retriever.call_args
        
        # The filter should be something like {"role": {"$ne": "admin"}} or similar
        # Based on Sprint 3 Plan: excluding { "role": {"$eq": "admin"} }
        expected_filter = {"role": {"$ne": "admin"}}
        assert kwargs["search_kwargs"]["filter"] == expected_filter

def test_admin_retrieval_has_no_filter():
    """
    If the user is an 'admin', the retriever should have no role-based 
    metadata filter, allowing access to all content.
    """
    with patch("rag_retriever.PineconeVectorStore") as MockStore, \
         patch("rag_retriever.OpenAIEmbeddings") as MockEmbed, \
         patch("rag_retriever.PineconeManager") as MockManager:

        # Mock OpenAI to prevent api_key error
        MockEmbed.return_value = MagicMock()
        MockManager.return_value = MagicMock()
        
        mock_vectorstore = MagicMock()
        MockStore.from_existing_index.return_value = mock_vectorstore
        mock_retriever = MagicMock()
        mock_vectorstore.as_retriever.return_value = mock_retriever
        
        from rag_retriever import get_retriever
        
        # Test for admin
        get_retriever(role="admin")
        
        mock_vectorstore.as_retriever.assert_called_once()
        args, kwargs = mock_vectorstore.as_retriever.call_args
        
        # Admin should not have the role exclusion filter
        assert "filter" not in kwargs["search_kwargs"] or \
               kwargs["search_kwargs"]["filter"].get("role") is None
