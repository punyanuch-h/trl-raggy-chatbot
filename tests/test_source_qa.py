from source_qa import answer_query_from_source


def test_source_qa_returns_authoritative_trl_definition_from_source_text():
    answer = answer_query_from_source("TRL 4 คืออะไร")

    assert answer is not None
    assert "TRL 4 คือ" in answer
    assert "ห้องปฏิบัติการ" in answer


def test_source_qa_ignores_non_definition_queries():
    assert answer_query_from_source("ช่วยประเมิน TRL ให้หน่อย ตอนนี้มีต้นแบบแล้ว") is None
