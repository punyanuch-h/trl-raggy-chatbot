from agents.intent_router import route_trl_intent


def test_router_classifies_general_qa_query_in_thai():
    decision = route_trl_intent("TRL 4 คืออะไร และต่างจาก TRL 5 อย่างไร")

    assert decision.intent == "general_qa"
    assert decision.needs_clarification is False


def test_router_classifies_assessment_query_in_thai():
    decision = route_trl_intent("ช่วยประเมินหน่อย เรามีต้นแบบและทดสอบในห้องปฏิบัติการแล้ว ตอนนี้น่าจะอยู่ TRL ไหน")

    assert decision.intent == "trl_assessment"
    assert decision.needs_clarification is False


def test_router_marks_ambiguous_query_for_clarification():
    decision = route_trl_intent("TRL ช่วยดูให้หน่อย")

    assert decision.intent == "general_qa"
    assert decision.needs_clarification is True
