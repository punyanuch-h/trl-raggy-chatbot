import os
import pytest
from unittest.mock import MagicMock, patch

# Set test environment vars before importing module
os.environ["PINECONE_API_KEY"] = "test-api-key"
os.environ["PINECONE_INDEX_NAME"] = "raggy-bot-trl-test"

# ---------------------------------------------------------------
# RED PHASE: Tests for PineconeManager (class doesn't exist yet)
# ---------------------------------------------------------------

def test_init_creates_index_when_not_exists():
    """
    If the target Pinecone index does NOT exist, the manager 
    must call create_index exactly once with 1536 dimensions.
    """
    with patch("pinecone_manager.Pinecone") as MockPinecone:
        mock_client = MagicMock()
        MockPinecone.return_value = mock_client
        
        # Simulate index not existing in the list
        mock_client.list_indexes.return_value.names.return_value = []
        
        from pinecone_manager import PineconeManager
        manager = PineconeManager()
        
        # Assert that index creation was called once with correct params
        mock_client.create_index.assert_called_once()
        call_kwargs = mock_client.create_index.call_args
        assert call_kwargs.kwargs.get("dimension") == 1536 or \
               (call_kwargs.args and 1536 in call_kwargs.args)


def test_init_skips_creation_when_index_exists():
    """
    If the target Pinecone index ALREADY exists, the manager 
    must NOT call create_index at all.
    """
    with patch("pinecone_manager.Pinecone") as MockPinecone:
        mock_client = MagicMock()
        MockPinecone.return_value = mock_client
        
        # Simulate index already existing in the cloud list
        mock_client.list_indexes.return_value.names.return_value = ["raggy-bot-trl-test"]
        
        from pinecone_manager import PineconeManager
        manager = PineconeManager()
        
        # Assert that index creation was NOT called since it exists
        mock_client.create_index.assert_not_called()


def test_connection_report_exposes_safe_index_stats():
    with patch("pinecone_manager.Pinecone") as MockPinecone:
        mock_client = MagicMock()
        mock_index = MagicMock()
        MockPinecone.return_value = mock_client
        mock_client.list_indexes.return_value.names.return_value = ["raggy-bot-trl-test"]
        mock_client.Index.return_value = mock_index

        mock_client.describe_index.return_value = {
            "dimension": 1536,
            "metric": "cosine",
            "host": "example-index-host",
            "status": {"ready": True, "state": "Ready"},
        }
        mock_index.describe_index_stats.return_value = {
            "total_vector_count": 42,
            "namespaces": {"": {"vector_count": 42}},
        }

        from pinecone_manager import PineconeManager
        manager = PineconeManager()

        report = manager.get_connection_report()

        assert report["index_name"] == "raggy-bot-trl-test"
        assert report["dimension"] == 1536
        assert report["metric"] == "cosine"
        assert report["host"] == "example-index-host"
        assert report["ready"] is True
        assert report["state"] == "Ready"
        assert report["total_vector_count"] == 42
        assert report["namespaces"] == {"default": 42}
