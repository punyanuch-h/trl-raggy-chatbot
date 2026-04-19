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


def test_router_uses_evidence_context_to_prefer_assessment():
    decision = route_trl_intent("ตอนนี้มีต้นแบบและผลทดสอบในห้องปฏิบัติการแล้ว ควรประเมินว่าอยู่ TRL ไหน")

    assert decision.intent == "trl_assessment"
    assert decision.needs_clarification is False


def test_router_keeps_definition_question_in_general_qa():
    decision = route_trl_intent("เกณฑ์ TRL 5 คืออะไร และต่างจาก TRL 6 อย่างไร")

    assert decision.intent == "general_qa"
    assert decision.needs_clarification is False


def test_router_keeps_trl_level_comparison_in_general_qa():
    decision = route_trl_intent("ช่วยอธิบายความต่างระหว่าง TRL 2 กับ TRL 3")

    assert decision.intent == "general_qa"
    assert decision.needs_clarification is False


def test_router_keeps_hypothetical_level_question_in_general_qa():
    decision = route_trl_intent("ถ้ายังมีแค่แนวคิดกับการทบทวนงานวิจัย ควรนับเป็น TRL อะไร")

    assert decision.intent == "general_qa"
    assert decision.needs_clarification is False


def test_router_keeps_evidence_requirement_question_in_general_qa():
    decision = route_trl_intent("TRL 8 ต้องมีหลักฐานอะไรบ้างก่อนบอกว่าพร้อมส่งมอบ")

    assert decision.intent == "general_qa"
    assert decision.needs_clarification is False


def test_router_keeps_generic_real_deployment_level_question_in_general_qa():
    decision = route_trl_intent(
        "ระบบที่ใช้งานจริงแล้วและมีรายงานติดตามผลหลังส่งมอบเกี่ยวข้องกับ TRL level ไหน"
    )

    assert decision.intent == "general_qa"
    assert decision.needs_clarification is False


def test_router_classifies_prototype_level_question_as_assessment():
    decision = route_trl_intent("โครงการนี้มีต้นแบบแล้ว อยู่ TRL ไหน")

    assert decision.intent == "trl_assessment"
    assert decision.needs_clarification is False


def test_router_classifies_missing_experiment_level_question_as_assessment():
    decision = route_trl_intent("ยังไม่มีการทดลองใดๆ งานฉันอยู่ TRL level ไหน")

    assert decision.intent == "trl_assessment"
    assert decision.needs_clarification is False


def test_router_classifies_project_level_question_without_trl_word_as_assessment():
    decision = route_trl_intent("โครงการนี้มีต้นแบบและผ่านการทดสอบเบื้องต้น ถือว่าอยู่ระดับไหน")

    assert decision.intent == "trl_assessment"
    assert decision.needs_clarification is False


def test_router_classifies_project_state_plus_trl_level_question_as_assessment():
    decision = route_trl_intent(
        "โครงการนี้ยังอยู่ในขั้นศึกษาหลักการทางคณิตศาสตร์และทบทวนงานวิจัยที่เกี่ยวข้องเพื่อสนับสนุนสมมติฐาน "
        "โดยยังไม่มีการกำหนดแนวทางพัฒนาเทคโนโลยีหรือการทดลองใดๆ คุณว่างานของฉันอยู่ใน TRL level ไหน"
    )

    assert decision.intent == "trl_assessment"
    assert decision.needs_clarification is False


def test_router_classifies_english_definition_question_as_general_qa():
    decision = route_trl_intent("What is TRL 4?")

    assert decision.intent == "general_qa"
    assert decision.needs_clarification is False


def test_router_classifies_english_comparison_question_as_general_qa():
    decision = route_trl_intent("Compare TRL 5 and TRL 6.")

    assert decision.intent == "general_qa"
    assert decision.needs_clarification is False


def test_router_classifies_english_assessment_request_as_assessment():
    decision = route_trl_intent("Please assess my project. We have tested the prototype in a relevant environment.")

    assert decision.intent == "trl_assessment"
    assert decision.needs_clarification is False


def test_router_handles_mixed_language_assessment_request_safely():
    decision = route_trl_intent("ช่วย assess project นี้หน่อย เรามี prototype tested in relevant environment แล้ว")

    assert decision.intent == "trl_assessment"
    assert decision.needs_clarification is False
