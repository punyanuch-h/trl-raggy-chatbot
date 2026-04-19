from assessment.response_templates import get_response_message, get_response_title


def test_response_templates_are_thai_for_default_user_facing_fallbacks():
    assert "เข้าสู่ระบบ" in get_response_message("auth_error", mode="qa")
    assert "เฉพาะข้อความ" in get_response_message("validation_error", mode="qa")
    assert "ขัดข้อง" in get_response_message("technical_error", mode="qa")
    assert get_response_title("qa") == "คำตอบ TRL"


def test_response_templates_support_english_language_variant():
    assert "sign in again" in get_response_message("auth_error", mode="qa", language="en").lower()
    assert "technical problem" in get_response_message("technical_error", mode="qa", language="en").lower()
    assert get_response_title("assessment", language="en") == "TRL Assessment"


def test_response_templates_distinguish_qa_and_assessment_modes():
    qa = get_response_message("insufficient_evidence", mode="qa")
    assessment = get_response_message("insufficient_evidence", mode="assessment")

    assert qa != assessment
    assert "ข้อมูล" in qa
    assert "หลักฐาน" in assessment
