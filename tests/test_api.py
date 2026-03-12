import sys
import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set test environment vars before importing app
os.environ["JWT_SECRET"] = "test_secret_key"

try:
    from main import app
    import jwt
    client = TestClient(app)
except ImportError:
    app = None
    client = None
    jwt = None

def create_mock_token(payload: dict) -> str:
    """Helper to generate symmetric PyJWT tokens mapped to the test secret"""
    return jwt.encode(payload, os.environ["JWT_SECRET"], algorithm="HS256")


def test_cors_headers_whitelisted():
    assert client is not None, "API not implemented yet (RED PHASE)"
    
    response = client.options(
        "/raggy/trl",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"

def test_raggy_trl_endpoint_requires_auth():
    """Test that requests missing Authorization header get polite text fallback (not 401)."""
    assert client is not None, "API not implemented yet (RED PHASE)"
    
    response = client.post("/raggy/trl", json={"query": "What is TRL 4?"})
    assert response.status_code == 200
    expected_answer = "I apologize, but I couldn't securely verify your access session. Could you please try logging in again?"
    assert response.json().get("answer") == expected_answer

def test_raggy_trl_endpoint_invalid_token():
    """Test that requests with an expired/fake token get polite text fallback."""
    assert client is not None, "API not implemented yet (RED PHASE)"
    
    headers = {"Authorization": "Bearer fake.token.here"}
    response = client.post("/raggy/trl", headers=headers, json={"query": "What is TRL 4?"})
    assert response.status_code == 200
    expected_answer = "I apologize, but I couldn't securely verify your access session. Could you please try logging in again?"
    assert response.json().get("answer") == expected_answer

def test_raggy_trl_valid_admin_token():
    """Test that a valid admin token effectively passes authorization and maps the role."""
    assert client is not None, "API not implemented yet (RED PHASE)"
    
    token = create_mock_token({"role": "admin"})
    headers = {"Authorization": f"Bearer {token}"}
    
    # Mocking dependencies by patching WHERE they are used
    with patch("main.get_retriever") as MockGetRetriever, \
         patch("main.ChatOpenAI") as MockChatOpenAI, \
         patch("main.create_retrieval_chain") as MockChainFactory:
        
        # 1. Mock Retriever
        mock_retriever = MagicMock()
        MockGetRetriever.return_value = mock_retriever
        
        # 2. Mock Chat Model
        mock_chat_model = MagicMock()
        MockChatOpenAI.return_value = mock_chat_model
        
        # 3. Mock Chain execution
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = {
            "answer": "[Mock Admin Data Access] This is a mocked admin response."
        }
        MockChainFactory.return_value = mock_chain
        
        response = client.post("/raggy/trl", headers=headers, json={"query": "What is TRL 4?"})
        
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "[Mock Admin Data Access]" in data.get("answer", "")

def test_raggy_trl_missing_role_downgrades_to_researcher():
    """Test that a valid token WITHOUT a role securely defaults to 'researcher'."""
    assert client is not None, "API not implemented yet (RED PHASE)"
    
    # Payload missing the 'role' key
    token = create_mock_token({"user_id": 12345}) 
    headers = {"Authorization": f"Bearer {token}"}
    
    # Mocking dependencies
    with patch("main.get_retriever") as MockGetRetriever, \
         patch("main.ChatOpenAI") as MockChatOpenAI, \
         patch("main.create_retrieval_chain") as MockChainFactory:
        
        MockGetRetriever.return_value = MagicMock()
        MockChatOpenAI.return_value = MagicMock()
        
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = {
            "answer": "[Mock Researcher Data Access] This is a mocked researcher response."
        }
        MockChainFactory.return_value = mock_chain
        
        response = client.post("/raggy/trl", headers=headers, json={"query": "What is TRL 4?"})
        
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "[Mock Researcher Data Access]" in data.get("answer", "")


def test_invalid_input_returns_polite_response():
    """Test that invalid payloads return a polite 200 text string instead of 422 crash."""
    assert client is not None, "API not implemented yet"
    
    # Needs valid token to get past Auth gate to reach Validation gate
    token = create_mock_token({"role": "researcher"})
    headers = {"Authorization": f"Bearer {token}"}
    
    # Send empty json which fails the QueryRequest validation
    response = client.post("/raggy/trl", headers=headers, json={})
    assert response.status_code == 200
    expected_answer = "I'm sorry, but I am currently only equipped to answer text-based questions. Please type out your question and I would be happy to help!"
    assert response.json().get("answer") == expected_answer
