from assessment.session_state import AssessmentSessionState, InMemoryAssessmentSessionStore


def test_session_store_creates_and_resumes_assessment_state():
    store = InMemoryAssessmentSessionStore()

    created = store.create()
    created.collected_evidence["trl_4_lab_validation"] = True
    created.missing_evidence = [{"id": "trl_4_integrated_components", "description_th": "มีหลักฐานว่าองค์ประกอบหลักถูกประกอบและทำงานร่วมกันได้"}]
    created.candidate_level = 4
    created.last_asked_question = "มีหลักฐานว่าองค์ประกอบหลักถูกประกอบและทำงานร่วมกันได้หรือไม่?"
    store.save(created)

    resumed = store.get(created.session_id)

    assert resumed is not None
    assert resumed.session_id == created.session_id
    assert resumed.collected_evidence["trl_4_lab_validation"] is True
    assert resumed.candidate_level == 4
    assert resumed.last_asked_question


def test_session_state_serializes_required_fields_without_raw_conversation():
    state = AssessmentSessionState(session_id="sess-001")
    state.collected_evidence = {"trl_5_relevant_environment_test": True}
    state.missing_evidence = [{"id": "trl_5_supporting_performance_data", "description_th": "มีข้อมูลสมรรถนะหรือความปลอดภัยที่รองรับผลการทดสอบ"}]
    state.candidate_level = 5
    state.last_asked_question = "มีข้อมูลด้านประสิทธิภาพหรือความปลอดภัยที่รองรับผลการทดสอบระดับนี้อย่างไร?"

    payload = state.model_dump()

    assert payload["session_id"] == "sess-001"
    assert payload["collected_evidence"]["trl_5_relevant_environment_test"] is True
    assert payload["candidate_level"] == 5
    assert "last_user_message" not in payload
