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
