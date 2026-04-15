import sys
import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from assessment.response_templates import get_response_message

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from main import app
    import jwt
    client = TestClient(app)
except ImportError:
    app = None
    client = None
    jwt = None

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


def create_rs256_token(payload: dict, private_key: str, kid: str = "v1") -> str:
    return jwt.encode(payload, private_key, algorithm="RS256", headers={"kid": kid, "typ": "JWT"})


TEST_PRIVATE_KEY, TEST_PUBLIC_KEY = generate_rsa_keypair()


def create_mock_token(payload: dict) -> str:
    """Helper to generate RS256 tokens mapped to the test public key."""
    merged_payload = {
        "iss": "trl-research",
        "aud": "trl-client",
        "exp": 2085343600,
        **payload,
    }
    return create_rs256_token(merged_payload, private_key=TEST_PRIVATE_KEY, kid="v1")


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
    expected_answer = "## คำตอบ TRL\n\nขออภัย ไม่สามารถยืนยันสิทธิ์การเข้าใช้งานของคุณได้อย่างปลอดภัย กรุณาเข้าสู่ระบบอีกครั้ง"
    assert response.json() == {"answer_markdown": expected_answer}

def test_raggy_trl_endpoint_invalid_token():
    """Test that requests with an expired/fake token get polite text fallback."""
    assert client is not None, "API not implemented yet (RED PHASE)"
    
    headers = {"Authorization": "Bearer fake.token.here"}
    response = client.post("/raggy/trl", headers=headers, json={"query": "What is TRL 4?"})
    assert response.status_code == 200
    expected_answer = "## คำตอบ TRL\n\nขออภัย ไม่สามารถยืนยันสิทธิ์การเข้าใช้งานของคุณได้อย่างปลอดภัย กรุณาเข้าสู่ระบบอีกครั้ง"
    assert response.json() == {"answer_markdown": expected_answer}

def test_raggy_trl_valid_admin_token():
    """Test that a valid admin token effectively passes authorization and maps the role."""
    assert client is not None, "API not implemented yet (RED PHASE)"
    
    token = create_mock_token({"role": "admin"})
    headers = {"Authorization": f"Bearer {token}"}
    
    # Mocking dependencies by patching WHERE they are used
    with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False), \
         patch("main.get_retriever") as MockGetRetriever, \
         patch("main.ChatOpenAI") as MockChatOpenAI, \
         patch("main.create_retrieval_chain") as MockChainFactory, \
         patch("main.get_metadata_store", return_value=None):
        
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
        
        response = client.post("/raggy/trl", headers=headers, json={"query": "How should I plan TRL readiness?"})
        
        assert response.status_code == 200
        data = response.json()
        assert "answer_markdown" in data
        assert data["answer_markdown"].startswith("## คำตอบ TRL")
        assert "[Mock Admin Data Access]" in data["answer_markdown"]


def test_raggy_trl_accepts_backend_style_jwt_claims_with_audience():
    """Token from trl-backend may include aud/iss/iat/nbf/exp and custom identity fields."""
    assert client is not None, "API not implemented yet (RED PHASE)"

    token = create_mock_token(
        {
            "user_id": "backend-user-001",
            "user_email": "backend@example.com",
            "role": "admin",
            "client_id": "",
            "client_name": "",
            "is_temp": False,
            "iss": "trl-backend",
            "aud": "trl-frontend",
            "iat": 1775340000,
            "nbf": 1775340000,
            "exp": 2085343600,
        }
    )
    headers = {"Authorization": f"Bearer {token}"}
    mock_store = MagicMock()

    with patch.dict(
        os.environ,
        {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY, "JWT_AUDIENCE": "trl-frontend", "JWT_ISSUER": "trl-backend"},
        clear=False,
    ), \
         patch("main.get_retriever") as MockGetRetriever, \
         patch("main.ChatOpenAI") as MockChatOpenAI, \
         patch("main.create_stuff_documents_chain") as MockStuffChain, \
         patch("main.create_retrieval_chain") as MockChainFactory, \
         patch("main.get_metadata_store", return_value=mock_store):
        MockGetRetriever.return_value = MagicMock()
        MockChatOpenAI.return_value = MagicMock()
        MockStuffChain.return_value = MagicMock()

        mock_chain = MagicMock()
        mock_chain.invoke.return_value = {"answer": "Accepted backend token."}
        MockChainFactory.return_value = mock_chain

        response = client.post("/raggy/trl", headers=headers, json={"query": "What is TRL 4?"})

    assert response.status_code == 200
    saved_record = mock_store.save_record.call_args.args[0]
    assert saved_record["user_id"] == "backend-user-001"
    assert saved_record["role"] == "admin"


def test_raggy_trl_rejects_wrong_audience_when_configured():
    """If JWT_AUDIENCE is configured, aud must match."""
    assert client is not None, "API not implemented yet (RED PHASE)"

    token = create_mock_token(
        {
            "user_id": "backend-user-001",
            "role": "researcher",
            "aud": "wrong-frontend",
            "exp": 2085343600,
        }
    )
    headers = {"Authorization": f"Bearer {token}"}

    with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY, "JWT_AUDIENCE": "trl-frontend"}, clear=False):
        response = client.post("/raggy/trl", headers=headers, json={"query": "What is TRL 4?"})

    assert response.status_code == 200
    expected_answer = "## คำตอบ TRL\n\nขออภัย ไม่สามารถยืนยันสิทธิ์การเข้าใช้งานของคุณได้อย่างปลอดภัย กรุณาเข้าสู่ระบบอีกครั้ง"
    assert response.json() == {"answer_markdown": expected_answer}


def test_raggy_trl_accepts_rs256_backend_token_with_kid_specific_public_key():
    assert client is not None, "API not implemented yet (RED PHASE)"

    token = create_rs256_token(
        {
            "user_id": "backend-rs-user-001",
            "user_email": "backend@example.com",
            "role": "admin",
            "client_id": "",
            "client_name": "",
            "is_temp": False,
            "iss": "trl-backend",
            "aud": "trl-frontend",
            "iat": 1775340000,
            "nbf": 1775340000,
            "exp": 2085343600,
        },
        private_key=TEST_PRIVATE_KEY,
        kid="v1",
    )
    headers = {"Authorization": f"Bearer {token}"}
    mock_store = MagicMock()

    with patch.dict(
        os.environ,
        {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY, "JWT_AUDIENCE": "trl-frontend", "JWT_ISSUER": "trl-backend"},
        clear=False,
    ), \
         patch("main.get_retriever") as MockGetRetriever, \
         patch("main.ChatOpenAI") as MockChatOpenAI, \
         patch("main.create_stuff_documents_chain") as MockStuffChain, \
         patch("main.create_retrieval_chain") as MockChainFactory, \
         patch("main.get_metadata_store", return_value=mock_store):
        MockGetRetriever.return_value = MagicMock()
        MockChatOpenAI.return_value = MagicMock()
        MockStuffChain.return_value = MagicMock()

        mock_chain = MagicMock()
        mock_chain.invoke.return_value = {"answer": "Accepted RS256 backend token."}
        MockChainFactory.return_value = mock_chain

        response = client.post("/raggy/trl", headers=headers, json={"query": "What is TRL 4?"})

    assert response.status_code == 200
    saved_record = mock_store.save_record.call_args.args[0]
    assert saved_record["user_id"] == "backend-rs-user-001"
    assert saved_record["role"] == "admin"


def test_raggy_trl_rejects_rs256_token_when_public_key_is_missing():
    assert client is not None, "API not implemented yet (RED PHASE)"

    token = create_rs256_token(
        {"user_id": "backend-rs-user-001", "role": "researcher", "exp": 2085343600},
        private_key=TEST_PRIVATE_KEY,
        kid="v1",
    )
    headers = {"Authorization": f"Bearer {token}"}

    with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": "", "JWT_PUBLIC_KEY": ""}, clear=False):
        response = client.post("/raggy/trl", headers=headers, json={"query": "What is TRL 4?"})

    assert response.status_code == 200
    expected_answer = "## คำตอบ TRL\n\nขออภัย ไม่สามารถยืนยันสิทธิ์การเข้าใช้งานของคุณได้อย่างปลอดภัย กรุณาเข้าสู่ระบบอีกครั้ง"
    assert response.json() == {"answer_markdown": expected_answer}


def test_raggy_trl_accepts_base64_encoded_public_key_from_env():
    assert client is not None, "API not implemented yet (RED PHASE)"

    import base64

    token = create_rs256_token(
        {"user_id": "backend-rs-user-002", "role": "admin", "iss": "trl-backend", "aud": "trl-frontend", "exp": 2085343600},
        private_key=TEST_PRIVATE_KEY,
        kid="v1",
    )
    headers = {"Authorization": f"Bearer {token}"}
    mock_store = MagicMock()
    encoded_public_key = base64.b64encode(TEST_PUBLIC_KEY.encode("utf-8")).decode("utf-8")

    with patch.dict(
        os.environ,
        {"JWT_PUBLIC_KEY_V1": encoded_public_key, "JWT_AUDIENCE": "trl-frontend", "JWT_ISSUER": "trl-backend"},
        clear=False,
    ), \
         patch("main.get_retriever") as MockGetRetriever, \
         patch("main.ChatOpenAI") as MockChatOpenAI, \
         patch("main.create_stuff_documents_chain") as MockStuffChain, \
         patch("main.create_retrieval_chain") as MockChainFactory, \
         patch("main.get_metadata_store", return_value=mock_store):
        MockGetRetriever.return_value = MagicMock()
        MockChatOpenAI.return_value = MagicMock()
        MockStuffChain.return_value = MagicMock()

        mock_chain = MagicMock()
        mock_chain.invoke.return_value = {"answer": "Accepted base64 public key."}
        MockChainFactory.return_value = mock_chain

        response = client.post("/raggy/trl", headers=headers, json={"query": "What is TRL 4?"})

    assert response.status_code == 200
    saved_record = mock_store.save_record.call_args.args[0]
    assert saved_record["user_id"] == "backend-rs-user-002"


def test_raggy_trl_missing_role_downgrades_to_researcher():
    """Test that a valid token WITHOUT a role securely defaults to 'researcher'."""
    assert client is not None, "API not implemented yet (RED PHASE)"
    
    # Payload missing the 'role' key
    token = create_mock_token({"user_id": 12345}) 
    headers = {"Authorization": f"Bearer {token}"}
    
    # Mocking dependencies
    with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False), \
         patch("main.get_retriever") as MockGetRetriever, \
         patch("main.ChatOpenAI") as MockChatOpenAI, \
         patch("main.create_retrieval_chain") as MockChainFactory, \
         patch("main.get_metadata_store", return_value=None):
        
        MockGetRetriever.return_value = MagicMock()
        MockChatOpenAI.return_value = MagicMock()
        
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = {
            "answer": "[Mock Researcher Data Access] This is a mocked researcher response."
        }
        MockChainFactory.return_value = mock_chain
        
        response = client.post("/raggy/trl", headers=headers, json={"query": "How should I plan TRL readiness?"})
        
        assert response.status_code == 200
        data = response.json()
        assert "answer_markdown" in data
        assert "[Mock Researcher Data Access]" in data["answer_markdown"]


def test_invalid_input_returns_polite_response():
    """Test that invalid payloads return a polite 200 text string instead of 422 crash."""
    assert client is not None, "API not implemented yet"
    
    # Needs valid token to get past Auth gate to reach Validation gate
    token = create_mock_token({"role": "researcher"})
    headers = {"Authorization": f"Bearer {token}"}
    
    # Send empty json which fails the QueryRequest validation
    with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False):
        response = client.post("/raggy/trl", headers=headers, json={})
    assert response.status_code == 200
    expected_answer = "## คำตอบ TRL\n\nขออภัย ขณะนี้ระบบรองรับเฉพาะข้อความสำหรับคำถาม กรุณาพิมพ์คำถามที่ต้องการสอบถามแล้วผมจะช่วยต่อให้ครับ"
    assert response.json() == {"answer_markdown": expected_answer}


def test_successful_request_persists_safe_metadata_and_returns_request_id_header():
    token = create_mock_token({"role": "researcher", "sub": "user-123"})
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Session-ID": "sess-123",
        "X-Request-ID": "req-123",
    }
    mock_store = MagicMock()

    with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False), \
         patch("main.get_retriever") as MockGetRetriever, \
         patch("main.ChatOpenAI") as MockChatOpenAI, \
         patch("main.create_stuff_documents_chain") as MockStuffChain, \
         patch("main.create_retrieval_chain") as MockChainFactory, \
         patch("main.get_metadata_store", return_value=mock_store):
        MockGetRetriever.return_value = MagicMock()
        MockChatOpenAI.return_value = MagicMock()
        MockStuffChain.return_value = MagicMock()

        mock_chain = MagicMock()
        mock_chain.invoke.return_value = {"answer": "TRL 4 is validated in the lab."}
        MockChainFactory.return_value = mock_chain

        response = client.post("/raggy/trl", headers=headers, json={"query": "What is TRL 4?"})

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "req-123"
    saved_record = mock_store.save_record.call_args.args[0]
    assert saved_record["request_id"] == "req-123"
    assert saved_record["session_id"] == "sess-123"
    assert saved_record["user_id"] == "user-123"
    assert saved_record["role"] == "researcher"
    assert saved_record["response_status"] == "success"
    assert saved_record["route_path"] == "/raggy/trl"
    assert saved_record["model_name"] == "gpt-4o-mini"
    assert "query" not in saved_record
    assert "answer" not in saved_record
    assert "answer_markdown" not in saved_record


def test_metadata_write_failure_does_not_break_successful_response():
    token = create_mock_token({"role": "admin", "sub": "user-789"})
    headers = {"Authorization": f"Bearer {token}"}
    mock_store = MagicMock()
    mock_store.save_record.side_effect = RuntimeError("firestore unavailable")

    with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False), \
         patch("main.get_retriever") as MockGetRetriever, \
         patch("main.ChatOpenAI") as MockChatOpenAI, \
         patch("main.create_stuff_documents_chain") as MockStuffChain, \
         patch("main.create_retrieval_chain") as MockChainFactory, \
         patch("main.get_metadata_store", return_value=mock_store):
        MockGetRetriever.return_value = MagicMock()
        MockChatOpenAI.return_value = MagicMock()
        MockStuffChain.return_value = MagicMock()

        mock_chain = MagicMock()
        mock_chain.invoke.return_value = {"answer": "Admin answer content."}
        MockChainFactory.return_value = mock_chain

        response = client.post("/raggy/trl", headers=headers, json={"query": "What is TRL 4?"})

    assert response.status_code == 200
    assert "answer_markdown" in response.json()
    assert response.headers["x-request-id"]


def test_assessment_response_contract_returns_session_and_next_question():
    token = create_mock_token({"role": "researcher", "sub": "user-123"})
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Session-ID": "sess-assessment-001",
    }
    mock_store = MagicMock()

    with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False), \
         patch("main.get_metadata_store", return_value=mock_store):
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
    saved_record = mock_store.save_record.call_args.args[0]
    assert saved_record["workflow_mode"] == "assessment"
    assert saved_record["decision_status"] == "needs_more_evidence"


def test_assessment_session_can_resume_and_complete_through_api_contract():
    token = create_mock_token({"role": "researcher", "sub": "user-456"})
    headers = {
        "Authorization": f"Bearer {token}",
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
    assert second_data["session_id"] == "sess-assessment-002"
    assert second_data["assessment_result"]["decision_status"] == "completed"
    assert second_data["assessment_result"]["matched_level"] == 5
    assert second_data.get("next_question") is None


def test_target_early_stage_scenario_returns_assessment_result_through_api():
    token = create_mock_token({"role": "researcher", "sub": "user-target-scenario-001"})
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Session-ID": "sess-sprint13-target-api",
    }
    target_query = (
        "โครงการนี้ยังอยู่ในขั้นศึกษาหลักการทางคณิตศาสตร์และทบทวนงานวิจัยที่เกี่ยวข้องเพื่อสนับสนุนสมมติฐาน "
        "โดยยังไม่มีการกำหนดแนวทางพัฒนาเทคโนโลยีหรือการทดลองใดๆ คุณว่างานของฉันอยู่ใน TRL level ไหน"
    )

    with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False), \
         patch("main.get_metadata_store", return_value=None):
        response = client.post("/raggy/trl", headers=headers, json={"query": target_query})

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "assessment"
    assert data["session_id"] == "sess-sprint13-target-api"
    assert data["assessment_result"]["candidate_level"] == 2
    assert data["assessment_result"]["matched_level"] == 1
    assert data["assessment_result"]["decision_status"] == "downgraded"
    assert data["missing_evidence"]
    assert any(
        item["id"] == "trl_2_application_defined" and item["status"] == "missing"
        for item in data["missing_evidence"]
    )
    assert data.get("next_question") is None
    assert "TRL 1" in data["answer_markdown"]
    assert "หลักฐานที่รองรับ TRL 1" in data["answer_markdown"]
    assert "TRL 3" in data["answer_markdown"]
    assert "ยังไม่มีการทดลอง" in data["answer_markdown"]


def test_router_failure_falls_back_to_general_qa_without_crashing():
    token = create_mock_token({"role": "researcher", "sub": "user-router-001"})
    headers = {"Authorization": f"Bearer {token}"}

    with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False), \
         patch("main.route_trl_intent", side_effect=RuntimeError("router exploded")), \
         patch("main.get_retriever") as MockGetRetriever, \
         patch("main.ChatOpenAI") as MockChatOpenAI, \
         patch("main.create_stuff_documents_chain") as MockStuffChain, \
         patch("main.create_retrieval_chain") as MockChainFactory, \
         patch("main.get_metadata_store", return_value=None):
        MockGetRetriever.return_value = MagicMock()
        MockChatOpenAI.return_value = MagicMock()
        MockStuffChain.return_value = MagicMock()

        mock_chain = MagicMock()
        mock_chain.invoke.return_value = {"answer": "TRL 4 คือการทดสอบต้นแบบในห้องปฏิบัติการ"}
        MockChainFactory.return_value = mock_chain

        response = client.post("/raggy/trl", headers=headers, json={"query": "TRL 4 คืออะไร"})

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "qa"
    assert "TRL 4" in data["answer_markdown"]


def test_qa_orchestration_failure_returns_rag_answer_fallback():
    token = create_mock_token({"role": "researcher", "sub": "user-qa-fallback-001"})
    headers = {"Authorization": f"Bearer {token}"}

    with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False), \
         patch("main.get_retriever") as MockGetRetriever, \
         patch("main.ChatOpenAI") as MockChatOpenAI, \
         patch("main.create_stuff_documents_chain") as MockStuffChain, \
         patch("main.create_retrieval_chain") as MockChainFactory, \
         patch("main.orchestrate_query", side_effect=RuntimeError("qa orchestration exploded")), \
         patch("main.get_metadata_store", return_value=None):
        MockGetRetriever.return_value = MagicMock()
        MockChatOpenAI.return_value = MagicMock()
        MockStuffChain.return_value = MagicMock()

        mock_chain = MagicMock()
        mock_chain.invoke.return_value = {"answer": "TRL 3 คือการพิสูจน์แนวคิดเบื้องต้น"}
        MockChainFactory.return_value = mock_chain

        response = client.post("/raggy/trl", headers=headers, json={"query": "TRL 3 คืออะไร"})

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "qa"
    assert "TRL 3" in data["answer_markdown"]
    assert get_response_message("technical_error", mode="qa") not in data["answer_markdown"]


def test_qa_uses_source_folder_fallback_when_retrieval_fails_for_trl_definition():
    token = create_mock_token({"role": "researcher", "sub": "user-source-fallback-001"})
    headers = {"Authorization": f"Bearer {token}"}

    with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False), \
         patch("main.get_retriever") as MockGetRetriever, \
         patch("main.ChatOpenAI") as MockChatOpenAI, \
         patch("main.create_stuff_documents_chain") as MockStuffChain, \
         patch("main.create_retrieval_chain") as MockChainFactory, \
         patch("main.get_metadata_store", return_value=None):
        MockGetRetriever.return_value = MagicMock()
        MockChatOpenAI.return_value = MagicMock()
        MockStuffChain.return_value = MagicMock()
        MockChainFactory.side_effect = RuntimeError("pinecone unavailable")

        response = client.post("/raggy/trl", headers=headers, json={"query": "TRL 4 คืออะไร"})

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "qa"
    assert "TRL 4 คือ Component and/or Breadboard Validation in Laboratory Environment" in data["answer_markdown"]
    assert "ห้องปฏิบัติการ" in data["answer_markdown"]


def test_qa_uses_source_folder_before_retrieval_for_deterministic_comparison():
    token = create_mock_token({"role": "researcher", "sub": "user-source-first-001"})
    headers = {"Authorization": f"Bearer {token}"}
    query = "ช่วยเปรียบเทียบ TRL 5 กับ TRL 6 ว่าต่างกันตรงไหน"

    with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False), \
         patch("main.get_retriever", side_effect=AssertionError("retriever should not be used")), \
         patch("main.ChatOpenAI", side_effect=AssertionError("llm should not be used")), \
         patch("main.create_stuff_documents_chain", side_effect=AssertionError("rag should not be used")), \
         patch("main.create_retrieval_chain", side_effect=AssertionError("rag should not be used")), \
         patch("main.get_metadata_store", return_value=None):
        response = client.post("/raggy/trl", headers=headers, json={"query": query})

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "qa"
    assert "TRL 5" in data["answer_markdown"]
    assert "TRL 6" in data["answer_markdown"]
    assert "prototype" in data["answer_markdown"] or "ต้นแบบ" in data["answer_markdown"]
    assert "ข้อมูลจากเอกสารอ้างอิงยังไม่เพียงพอ" not in data["answer_markdown"]


def test_open_ended_qa_still_falls_back_to_rag_when_source_has_no_answer():
    token = create_mock_token({"role": "researcher", "sub": "user-rag-fallback-001"})
    headers = {"Authorization": f"Bearer {token}"}

    with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False), \
         patch("main.get_retriever") as MockGetRetriever, \
         patch("main.ChatOpenAI") as MockChatOpenAI, \
         patch("main.create_stuff_documents_chain") as MockStuffChain, \
         patch("main.create_retrieval_chain") as MockChainFactory, \
         patch("main.get_metadata_store", return_value=None):
        MockGetRetriever.return_value = MagicMock()
        MockChatOpenAI.return_value = MagicMock()
        MockStuffChain.return_value = MagicMock()
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = {"answer": "RAG answer for broader TRL strategy."}
        MockChainFactory.return_value = mock_chain

        response = client.post("/raggy/trl", headers=headers, json={"query": "How should our team plan TRL work this quarter?"})

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "qa"
    assert "RAG answer for broader TRL strategy." in data["answer_markdown"]
    MockGetRetriever.assert_called_once()
    MockChainFactory.assert_called_once()


def test_assessment_workflow_failure_returns_assessment_technical_fallback():
    token = create_mock_token({"role": "researcher", "sub": "user-assessment-fallback-001"})
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Session-ID": "sess-assessment-fallback-001",
    }

    with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False), \
         patch("main.run_assessment_turn", side_effect=RuntimeError("assessment exploded")), \
         patch("main.get_metadata_store", return_value=None):
        response = client.post(
            "/raggy/trl",
            headers=headers,
            json={"query": "ช่วยประเมิน TRL ให้หน่อย เรามีต้นแบบแล้ว"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "assessment"
    assert "ผลการประเมิน TRL" in data["answer_markdown"]
    assert get_response_message("technical_error", mode="assessment") in data["answer_markdown"]


def test_internal_metadata_session_endpoint_requires_admin_role():
    token = create_mock_token({"role": "researcher", "sub": "user-123"})
    headers = {"Authorization": f"Bearer {token}"}

    with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False):
        response = client.get("/internal/metadata/sessions/sess-123", headers=headers)

    assert response.status_code == 403


def test_internal_metadata_session_endpoint_returns_records_for_admin():
    token = create_mock_token({"role": "admin", "sub": "admin-123"})
    headers = {"Authorization": f"Bearer {token}"}
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


def test_internal_metadata_recent_endpoint_returns_recent_records_for_admin():
    token = create_mock_token({"role": "admin", "sub": "admin-123"})
    headers = {"Authorization": f"Bearer {token}"}
    mock_store = MagicMock()
    mock_store.list_recent_records.return_value = [
        {
            "request_id": "req-999",
            "session_id": None,
            "user_id": "user-777",
            "role": "admin",
            "timestamp": "2026-04-04T16:00:00+00:00",
            "response_status": "success",
            "route_path": "/raggy/trl",
            "model_name": "gpt-4o-mini",
        }
    ]

    with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False), \
         patch("main.get_metadata_store", return_value=mock_store):
        response = client.get("/internal/metadata/requests?limit=5", headers=headers)

    assert response.status_code == 200
    assert response.json()["records"][0]["request_id"] == "req-999"


def test_internal_pinecone_connection_endpoint_requires_admin_role():
    token = create_mock_token({"role": "researcher", "sub": "user-123"})
    headers = {"Authorization": f"Bearer {token}"}

    with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False):
        response = client.get("/internal/pinecone/connection", headers=headers)

    assert response.status_code == 403


def test_internal_pinecone_connection_endpoint_returns_live_report_shape_for_admin():
    token = create_mock_token({"role": "admin", "sub": "admin-123"})
    headers = {"Authorization": f"Bearer {token}"}
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
    assert data["total_vector_count"] == 42
    assert data["namespaces"] == {"default": 42}
