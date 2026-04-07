from agents.qa_agent import answer_general_qa


def test_qa_agent_returns_thai_answer_when_rag_answer_is_available():
    response = answer_general_qa(
        query="TRL 4 คืออะไร",
        rag_answer="TRL 4 คือการตรวจสอบองค์ประกอบในห้องปฏิบัติการ",
    )

    assert response.mode == "qa"
    assert "TRL 4" in response.answer_text


def test_qa_agent_redirects_off_topic_questions_in_thai():
    response = answer_general_qa(
        query="ช่วยเขียนสูตรทำขนมให้หน่อย",
        rag_answer=None,
    )

    assert response.mode == "qa"
    assert "Technology Readiness Level" in response.answer_text
    assert "ขออภัย" in response.answer_text


def test_qa_agent_uses_retrieval_failure_fallback_when_rag_chain_breaks():
    response = answer_general_qa(
        query="TRL 4 คืออะไร",
        rag_answer=None,
        retrieval_status="retrieval_failed",
    )

    assert response.mode == "qa"
    assert response.source == "retrieval_failure_fallback"
    assert response.answer_text


def test_qa_agent_uses_empty_answer_fallback_when_retrieval_returns_no_answer():
    response = answer_general_qa(
        query="TRL 4 คืออะไร",
        rag_answer="   ",
        retrieval_status="empty_answer",
    )

    assert response.mode == "qa"
    assert response.source == "qa_fallback"
