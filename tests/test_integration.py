import os
import sys
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient

# ---------------------------------------------------------------
# RED PHASE: Tests for LLM Integration (Ticket 3.3)
# ---------------------------------------------------------------

def test_raggy_trl_returns_real_ai_answer():
    """
    Test that the /raggy/trl endpoint successfully returns a 
    generative response from the RAG chain (mocked).
    """
    # Set environment variable for JWT
    os.environ["JWT_SECRET"] = "test_secret_key"
    
    with patch("main.get_retriever") as mock_get_retriever, \
         patch("main.ChatOpenAI") as mock_chat_llm, \
         patch("main.create_retrieval_chain") as mock_chain_factory, \
         patch("main.jwt") as mock_jwt:
        
        # 1. Mock JWT decoding to return an admin role
        mock_jwt.decode.return_value = {"role": "admin"}
        
        # 2. Mock the retriever and LLM
        mock_retriever = MagicMock()
        mock_get_retriever.return_value = mock_retriever
        
        # 3. Mock the final retrieval chain execution
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = {
            "answer": "TRL 4 is component validation in a laboratory environment.",
            "context": [MagicMock(page_content="Context chunk 1", metadata={"source_file": "trl.pdf"})]
        }
        mock_chain_factory.return_value = mock_chain
        
        # 4. Initialize Test Client after patches
        from main import app
        client = TestClient(app)
        
        # 5. Execute call
        headers = {"Authorization": "Bearer valid_token"}
        response = client.post("/raggy/trl", headers=headers, json={"query": "What is TRL 4?"})
        
        # 6. Assertions
        assert response.status_code == 200
        data = response.json()
        assert "answer_markdown" in data
        assert "TRL 4" in data["answer_markdown"]
        # Verify the chain was actually called
        mock_chain.invoke.assert_called_once()


def test_raggy_trl_passes_role_to_retriever():
    """
    Ensure the user role from the JWT is correctly passed to 
    the get_retriever function for RBAC enforcement.
    """
    os.environ["JWT_SECRET"] = "test_secret_key"
    
    with patch("main.get_retriever") as mock_get_retriever, \
         patch("main.ChatOpenAI"), \
         patch("main.create_retrieval_chain") as mock_chain_factory, \
         patch("main.jwt") as mock_jwt:
        
        # Mock researcher role
        mock_jwt.decode.return_value = {"role": "researcher"}
        mock_chain_factory.return_value = MagicMock()
        
        from main import app
        client = TestClient(app)
        
        headers = {"Authorization": "Bearer researcher_token"}
        client.post("/raggy/trl", headers=headers, json={"query": "TRL info"})
        
        # Assert get_retriever was called with researcher role
        mock_get_retriever.assert_called_with(role="researcher")
