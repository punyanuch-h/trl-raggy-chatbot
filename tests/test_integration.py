import os
import sys
import pytest
from unittest.mock import MagicMock, patch
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient


def generate_rsa_keypair() -> tuple[str, str]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")
    return private_pem, public_pem


TEST_PRIVATE_KEY, TEST_PUBLIC_KEY = generate_rsa_keypair()


def create_rs256_token(payload: dict) -> str:
    merged_payload = {
        "iss": "trl-research",
        "aud": "trl-client",
        "exp": 2085343600,
        **payload,
    }
    return jwt.encode(merged_payload, TEST_PRIVATE_KEY, algorithm="RS256", headers={"kid": "v1", "typ": "JWT"})

# ---------------------------------------------------------------
# RED PHASE: Tests for LLM Integration (Ticket 3.3)
# ---------------------------------------------------------------

def test_raggy_trl_returns_real_ai_answer():
    """
    Test that the /raggy/trl endpoint successfully returns a 
    generative response from the RAG chain (mocked).
    """
    with patch("main.get_retriever") as mock_get_retriever, \
         patch("main.ChatOpenAI") as mock_chat_llm, \
         patch("main.create_retrieval_chain") as mock_chain_factory:
        
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
        token = create_rs256_token({"role": "admin", "exp": 2085343600})
        headers = {"Authorization": f"Bearer {token}"}
        with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False):
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
    with patch("main.get_retriever") as mock_get_retriever, \
         patch("main.ChatOpenAI"), \
         patch("main.create_retrieval_chain") as mock_chain_factory:
        mock_chain_factory.return_value = MagicMock()
        
        from main import app
        client = TestClient(app)
        
        token = create_rs256_token({"role": "researcher", "exp": 2085343600})
        headers = {"Authorization": f"Bearer {token}"}
        with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False):
            client.post("/raggy/trl", headers=headers, json={"query": "TRL info"})
        
        # Assert get_retriever was called with researcher role
        mock_get_retriever.assert_called_with(role="researcher")
