import os
import sys
from unittest.mock import MagicMock, patch

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


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


def test_raggy_trl_returns_real_ai_answer():
    with patch("main.get_retriever") as mock_get_retriever, \
         patch("main.ChatOpenAI") as mock_chat_llm, \
         patch("main.create_retrieval_chain") as mock_chain_factory:
        mock_retriever = MagicMock()
        mock_get_retriever.return_value = mock_retriever

        mock_chain = MagicMock()
        mock_chain.invoke.return_value = {
            "answer": "TRL 4 is component validation in a laboratory environment.",
            "context": [MagicMock(page_content="Context chunk 1", metadata={"source_file": "trl.pdf"})],
        }
        mock_chain_factory.return_value = mock_chain

        from main import app

        client = TestClient(app)
        token = create_rs256_token({"role": "admin", "exp": 2085343600})
        headers = {"Authorization": f"Bearer {token}"}
        with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False):
            response = client.post("/raggy/trl", headers=headers, json={"query": "What is TRL 4?"})

        assert response.status_code == 200
        data = response.json()
        assert "answer_markdown" in data
        assert "TRL 4" in data["answer_markdown"]
        mock_chain.invoke.assert_called_once()


def test_raggy_trl_passes_role_to_retriever():
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

        mock_get_retriever.assert_called_with(role="researcher")


def test_raggy_trl_assessment_flow_uses_rule_based_orchestrator():
    with patch("main.get_retriever") as mock_get_retriever, \
         patch("main.ChatOpenAI") as mock_chat_llm, \
         patch("main.create_retrieval_chain") as mock_chain_factory, \
         patch("main.get_metadata_store", return_value=None):
        mock_get_retriever.return_value = MagicMock()
        mock_chat_llm.return_value = MagicMock()
        mock_chain_factory.return_value = MagicMock()

        from main import app

        client = TestClient(app)
        token = create_rs256_token({"role": "admin", "exp": 2085343600})
        headers = {"Authorization": f"Bearer {token}"}
        with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False):
            response = client.post(
                "/raggy/trl",
                headers=headers,
                json={"query": "ช่วยประเมิน TRL ให้หน่อย เรามีต้นแบบและทดสอบในห้องปฏิบัติการแล้ว"},
            )

        assert response.status_code == 200
        data = response.json()
        assert "ผลการประเมิน TRL" in data["answer_markdown"]
        assert "TRL 4" in data["answer_markdown"]
        mock_chain_factory.return_value.invoke.assert_not_called()


def test_raggy_trl_general_qa_flow_still_uses_rag_chain():
    with patch("main.get_retriever") as mock_get_retriever, \
         patch("main.ChatOpenAI") as mock_chat_llm, \
         patch("main.create_retrieval_chain") as mock_chain_factory, \
         patch("main.get_metadata_store", return_value=None):
        mock_get_retriever.return_value = MagicMock()
        mock_chat_llm.return_value = MagicMock()

        mock_chain = MagicMock()
        mock_chain.invoke.return_value = {"answer": "TRL 2 คือการสร้างแนวคิดและการประยุกต์ใช้เทคโนโลยี"}
        mock_chain_factory.return_value = mock_chain

        from main import app

        client = TestClient(app)
        token = create_rs256_token({"role": "researcher", "exp": 2085343600})
        headers = {"Authorization": f"Bearer {token}"}
        with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False):
            response = client.post("/raggy/trl", headers=headers, json={"query": "TRL 2 คืออะไร"})

        assert response.status_code == 200
        assert "คำตอบ TRL" in response.json()["answer_markdown"]
        mock_chain.invoke.assert_called_once()


def test_raggy_trl_assessment_session_resume_skips_rag_on_follow_up_turn():
    with patch("main.get_retriever") as mock_get_retriever, \
         patch("main.ChatOpenAI") as mock_chat_llm, \
         patch("main.create_retrieval_chain") as mock_chain_factory, \
         patch("main.get_metadata_store", return_value=None):
        mock_get_retriever.return_value = MagicMock()
        mock_chat_llm.return_value = MagicMock()
        mock_chain_factory.return_value = MagicMock()

        from main import app

        client = TestClient(app)
        token = create_rs256_token({"role": "researcher", "exp": 2085343600})
        headers = {
            "Authorization": f"Bearer {token}",
            "X-Session-ID": "sess-integration-001",
        }
        with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False):
            first_response = client.post(
                "/raggy/trl",
                headers=headers,
                json={"query": "ช่วยประเมิน TRL ให้หน่อย ตอนนี้มีผลทดสอบในสภาพแวดล้อมที่เกี่ยวข้องแล้ว"},
            )
            second_response = client.post(
                "/raggy/trl",
                headers=headers,
                json={"query": "มีข้อมูลสมรรถนะและความปลอดภัยรองรับผลการทดสอบแล้ว"},
            )

        assert first_response.status_code == 200
        assert second_response.status_code == 200
        assert first_response.json()["mode"] == "assessment"
        assert second_response.json()["mode"] == "assessment"
        assert second_response.json()["assessment_result"]["matched_level"] == 5
        mock_chain_factory.return_value.invoke.assert_not_called()
