import os
import sys
from unittest.mock import MagicMock, patch

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

from assessment.response_templates import get_response_message, get_response_title


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app  # noqa: E402
import jwt  # noqa: E402


client = TestClient(app)


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


def create_mock_token(payload: dict) -> str:
    merged_payload = {
        "iss": "trl-research",
        "aud": "trl-client",
        "exp": 2085343600,
        **payload,
    }
    return jwt.encode(merged_payload, TEST_PRIVATE_KEY, algorithm="RS256", headers={"kid": "v1", "typ": "JWT"})


def _auth_headers(payload: dict | None = None) -> dict[str, str]:
    token = create_mock_token(payload or {"role": "researcher", "sub": "user-001"})
    return {"Authorization": f"Bearer {token}"}


def test_cors_headers_whitelisted():
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
    response = client.post("/raggy/trl", json={"query": "What is TRL 4?"})
    assert response.status_code == 200
    assert response.json() == {
        "answer_markdown": f"## {get_response_title('qa')}\n\n{get_response_message('auth_error', mode='qa')}",
        "language": "th",
    }


def test_raggy_trl_endpoint_invalid_token():
    headers = {"Authorization": "Bearer fake.token.here"}
    response = client.post("/raggy/trl", headers=headers, json={"query": "What is TRL 4?"})
    assert response.status_code == 200
    assert response.json() == {
        "answer_markdown": f"## {get_response_title('qa')}\n\n{get_response_message('auth_error', mode='qa')}",
        "language": "th",
    }


def test_invalid_input_returns_polite_response():
    headers = _auth_headers()
    with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False):
        response = client.post("/raggy/trl", headers=headers, json={})

    assert response.status_code == 200
    assert response.json() == {
        "answer_markdown": f"## {get_response_title('qa')}\n\n{get_response_message('validation_error', mode='qa')}",
        "language": "th",
    }


def test_successful_request_persists_metadata_and_returns_request_id_header():
    headers = {
        **_auth_headers({"role": "researcher", "sub": "user-123"}),
        "X-Session-ID": "sess-123",
        "X-Request-ID": "req-123",
    }
    mock_store = MagicMock()

    with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False), \
         patch("main.get_retriever", return_value=MagicMock()), \
         patch("main.ChatOpenAI", return_value=MagicMock()), \
         patch("main.create_stuff_documents_chain", return_value=MagicMock()), \
         patch("main.create_retrieval_chain") as mock_chain_factory, \
         patch("main.get_metadata_store", return_value=mock_store):
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = {"answer": "RAG answer for TRL planning."}
        mock_chain_factory.return_value = mock_chain

        response = client.post("/raggy/trl", headers=headers, json={"query": "How should I plan TRL readiness?"})

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "req-123"
    saved_record = mock_store.save_record.call_args.args[0]
    assert saved_record["request_id"] == "req-123"
    assert saved_record["session_id"] == "sess-123"
    assert saved_record["user_id"] == "user-123"
    assert saved_record["workflow_mode"] == "qa"


def test_qa_uses_source_folder_before_retrieval_for_deterministic_comparison():
    headers = _auth_headers({"role": "researcher", "sub": "user-source-first-001"})
    query = "ช่วยเปรียบเทียบ TRL 5 กับ TRL 6 ว่าต่างกันตรงไหน"

    with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False), \
         patch("main.get_retriever", side_effect=AssertionError("retriever should not be used")), \
         patch("main.ChatOpenAI", side_effect=AssertionError("llm should not be used")), \
         patch("main.get_metadata_store", return_value=None):
        response = client.post("/raggy/trl", headers=headers, json={"query": query})

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "qa"
    assert data["language"] == "th"
    assert "TRL 5" in data["answer_markdown"]
    assert "TRL 6" in data["answer_markdown"]


def test_open_ended_qa_still_falls_back_to_rag_when_source_has_no_answer():
    headers = _auth_headers({"role": "researcher", "sub": "user-rag-fallback-001"})

    with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False), \
         patch("main.get_retriever", return_value=MagicMock()), \
         patch("main.ChatOpenAI", return_value=MagicMock()), \
         patch("main.create_stuff_documents_chain", return_value=MagicMock()), \
         patch("main.create_retrieval_chain") as mock_chain_factory, \
         patch("main.get_metadata_store", return_value=None):
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = {"answer": "RAG answer for broader TRL strategy."}
        mock_chain_factory.return_value = mock_chain

        response = client.post("/raggy/trl", headers=headers, json={"query": "How should our team plan TRL work this quarter?"})

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "qa"
    assert "RAG answer for broader TRL strategy." in data["answer_markdown"]


def test_assessment_response_contract_returns_session_and_next_question():
    headers = {
        **_auth_headers({"role": "researcher", "sub": "user-123"}),
        "X-Session-ID": "sess-assessment-001",
    }

    with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False), \
         patch("main.get_metadata_store", return_value=None):
        response = client.post(
            "/raggy/trl",
            headers=headers,
            json={"query": "ช่วยประเมิน TRL ให้หน่อย ตอนนี้มีผลทดสอบในสภาพแวดล้อมที่เกี่ยวข้องแล้ว"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "assessment"
    assert data["session_id"] == "sess-assessment-001"
    assert data["assessment_result"]["decision_status"] == "needs_more_evidence"
    assert data["missing_evidence"]
    assert data["next_question"]


def test_assessment_session_can_resume_and_complete_through_api_contract():
    headers = {
        **_auth_headers({"role": "researcher", "sub": "user-456"}),
        "X-Session-ID": "sess-assessment-002",
    }

    with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False), \
         patch("main.get_metadata_store", return_value=None):
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
    second_data = second_response.json()
    assert second_data["mode"] == "assessment"
    assert second_data["assessment_result"]["decision_status"] == "completed"
    assert second_data["assessment_result"]["matched_level"] == 5


def test_english_definition_qa_returns_english_language_contract():
    headers = _auth_headers({"role": "researcher", "sub": "user-en-qa-001"})

    with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False), \
         patch("main.get_retriever", side_effect=AssertionError("retriever should not be used")), \
         patch("main.ChatOpenAI", side_effect=AssertionError("llm should not be used")), \
         patch("main.get_metadata_store", return_value=None):
        response = client.post("/raggy/trl", headers=headers, json={"query": "What is TRL 4?"})

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "qa"
    assert data["language"] == "en"
    assert "## TRL Answer" in data["answer_markdown"]
    assert "laboratory environment" in data["answer_markdown"].lower()


def test_thai_query_can_override_response_language_to_english():
    headers = _auth_headers({"role": "researcher", "sub": "user-en-override-001"})

    with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False), \
         patch("main.get_retriever", side_effect=AssertionError("retriever should not be used")), \
         patch("main.ChatOpenAI", side_effect=AssertionError("llm should not be used")), \
         patch("main.get_metadata_store", return_value=None):
        response = client.post(
            "/raggy/trl",
            headers=headers,
            json={"query": "TRL 5 คืออะไร", "response_language": "en"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "en"
    assert "## TRL Answer" in data["answer_markdown"]
    assert "TRL 5" in data["answer_markdown"]


def test_english_assessment_request_returns_english_contract_and_routes_to_assessment():
    headers = {
        **_auth_headers({"role": "researcher", "sub": "user-en-assessment-001"}),
        "X-Session-ID": "sess-en-assessment-001",
    }

    with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False), \
         patch("main.get_metadata_store", return_value=None):
        response = client.post(
            "/raggy/trl",
            headers=headers,
            json={"query": "Please assess my project. We have tested the prototype in a relevant environment."},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "assessment"
    assert data["language"] == "en"
    assert "## TRL Assessment" in data["answer_markdown"]


def test_internal_metadata_session_endpoint_requires_admin_role():
    headers = _auth_headers({"role": "researcher", "sub": "user-123"})

    with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False):
        response = client.get("/internal/metadata/sessions/sess-123", headers=headers)

    assert response.status_code == 403


def test_internal_metadata_session_endpoint_returns_records_for_admin():
    headers = _auth_headers({"role": "admin", "sub": "admin-123"})
    mock_store = MagicMock()
    mock_store.get_records_by_session.return_value = [
        {
            "request_id": "req-123",
            "session_id": "sess-123",
            "user_id": "user-123",
            "role": "researcher",
            "timestamp": "2026-04-04T15:30:00+00:00",
            "response_status": "success",
            "route_path": "/raggy/trl",
            "model_name": "gpt-4o-mini",
        }
    ]

    with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False), \
         patch("main.get_metadata_store", return_value=mock_store):
        response = client.get("/internal/metadata/sessions/sess-123", headers=headers)

    assert response.status_code == 200
    assert response.json()["records"][0]["request_id"] == "req-123"


def test_internal_pinecone_connection_endpoint_returns_live_report_shape_for_admin():
    headers = _auth_headers({"role": "admin", "sub": "admin-123"})
    mock_manager = MagicMock()
    mock_manager.get_connection_report.return_value = {
        "index_name": "raggy-bot-trl-test",
        "host": "example-index-host",
        "dimension": 1536,
        "metric": "cosine",
        "ready": True,
        "state": "Ready",
        "total_vector_count": 42,
        "namespaces": {"default": 42},
    }

    with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False), \
         patch("main.PineconeManager", return_value=mock_manager):
        response = client.get("/internal/pinecone/connection", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["connected"] is True
    assert data["index_name"] == "raggy-bot-trl-test"
