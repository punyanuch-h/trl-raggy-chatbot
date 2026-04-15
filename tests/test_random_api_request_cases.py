import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import main  # noqa: E402
from assessment.session_state import InMemoryAssessmentSessionStore  # noqa: E402
from main import app  # noqa: E402
import jwt  # noqa: E402


FIXTURE_PATH = Path(__file__).resolve().parents[1] / "examples" / "api_requests" / "trl_random_qa_assessment_cases.json"


def _load_fixture() -> dict:
    with FIXTURE_PATH.open("r", encoding="utf-8") as fixture_file:
        return json.load(fixture_file)


def _generate_rsa_keypair() -> tuple[str, str]:
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


TEST_PRIVATE_KEY, TEST_PUBLIC_KEY = _generate_rsa_keypair()
client = TestClient(app)


def _auth_headers(request_id: str) -> dict[str, str]:
    token = jwt.encode(
        {
            "iss": "trl-research",
            "aud": "trl-client",
            "exp": 2085343600,
            "sub": "random-case-user",
            "role": "researcher",
        },
        TEST_PRIVATE_KEY,
        algorithm="RS256",
        headers={"kid": "v1", "typ": "JWT"},
    )
    return {
        "Authorization": f"Bearer {token}",
        "X-Request-ID": request_id,
    }


def _case_ids(cases: list[dict]) -> list[str]:
    return [case["id"] for case in cases]


FIXTURE = _load_fixture()
QA_CASES = FIXTURE["qa_cases"]
COMPLETE_ASSESSMENT_CASES = [
    case for case in FIXTURE["assessment_cases"] if case["case_type"] == "complete_question"
]
SESSION_ASSESSMENT_CASES = [
    case for case in FIXTURE["assessment_cases"] if case["case_type"] == "session_followup"
]

KNOWN_FIXTURE_APP_MISMATCHES = {
}


@pytest.fixture(autouse=True)
def reset_assessment_sessions(monkeypatch):
    monkeypatch.setattr(main, "ASSESSMENT_SESSION_STORE", InMemoryAssessmentSessionStore())


@pytest.mark.parametrize("case", QA_CASES, ids=_case_ids(QA_CASES))
def test_random_qa_cases_from_fixture_return_qa_mode(case):
    if case["id"] in KNOWN_FIXTURE_APP_MISMATCHES:
        pytest.xfail(KNOWN_FIXTURE_APP_MISMATCHES[case["id"]])

    headers = _auth_headers(f"req-{case['id']}")

    with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False), \
         patch("main.get_retriever", return_value=MagicMock()), \
         patch("main.ChatOpenAI", return_value=MagicMock()), \
         patch("main.create_stuff_documents_chain", return_value=MagicMock()), \
         patch("main.create_retrieval_chain") as mock_chain_factory, \
         patch("main.get_metadata_store", return_value=None):
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = {"answer": "คำตอบ TRL สำหรับการทดสอบอัตโนมัติ"}
        mock_chain_factory.return_value = mock_chain

        response = client.post("/raggy/trl", headers=headers, json=case["request"])

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == case["expected_mode"]
    assert data["answer_markdown"]

    answer_markdown = data["answer_markdown"]
    for expected_text in case.get("expected_answer_contains", []):
        assert expected_text in answer_markdown
    for forbidden_text in case.get("forbidden_answer_contains", []):
        assert forbidden_text not in answer_markdown
    if case.get("expected_answer_contains_any"):
        assert any(expected_text in answer_markdown for expected_text in case["expected_answer_contains_any"])


@pytest.mark.parametrize(
    "case",
    COMPLETE_ASSESSMENT_CASES,
    ids=_case_ids(COMPLETE_ASSESSMENT_CASES),
)
def test_complete_assessment_cases_from_fixture_match_expected_level(case):
    headers = _auth_headers(f"req-{case['id']}")

    with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False), \
         patch("main.get_metadata_store", return_value=None):
        response = client.post("/raggy/trl", headers=headers, json=case["request"])

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == case["expected_mode"]
    assert data["assessment_result"]["matched_level"] == case["expected_matched_level"]
    assert data["assessment_result"]["decision_status"] == "completed"


@pytest.mark.parametrize(
    "case",
    SESSION_ASSESSMENT_CASES,
    ids=_case_ids(SESSION_ASSESSMENT_CASES),
)
def test_session_assessment_cases_from_fixture_complete_after_followups(case):
    if case["id"] in KNOWN_FIXTURE_APP_MISMATCHES:
        pytest.xfail(KNOWN_FIXTURE_APP_MISMATCHES[case["id"]])

    final_data = None

    for turn_index, turn in enumerate(case["turns"], start=1):
        headers = _auth_headers(f"req-{case['id']}-{turn_index}")

        with patch.dict(os.environ, {"JWT_PUBLIC_KEY_V1": TEST_PUBLIC_KEY}, clear=False), \
             patch("main.get_metadata_store", return_value=None):
            response = client.post("/raggy/trl", headers=headers, json=turn["request"])

        assert response.status_code == 200
        data = response.json()
        assert data["mode"] == case["expected_mode"]
        assert data["session_id"] == case["session_id"]
        assert data["assessment_result"]["decision_status"] == turn["expected_status"]
        final_data = data

    assert final_data is not None
    assert (
        final_data["assessment_result"]["matched_level"]
        == case["expected_matched_level_after_final_turn"]
    )
