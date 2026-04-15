from assessment.conversation import (
    AssessmentTurnResult,
    InMemoryAssessmentSessionStore,
    _build_additional_recommendation,
    run_assessment_turn,
)


def test_follow_up_question_comes_from_missing_evidence_and_avoids_repetition():
    store = InMemoryAssessmentSessionStore()
    state = store.create()
    state.asked_evidence_ids = ["trl_5_relevant_environment_test"]
    store.save(state)

    result = run_assessment_turn(
        "เรากำลังประเมินเทคโนโลยีนี้",
        session_id=state.session_id,
        store=store,
        candidate_level=5,
    )

    assert isinstance(result, AssessmentTurnResult)
    assert result.next_question
    assert "ประสิทธิภาพ" in result.next_question or "ความปลอดภัย" in result.next_question
    assert result.next_evidence_id == "trl_5_supporting_performance_data"


def test_multi_turn_assessment_asks_for_more_evidence_before_confirming_level():
    store = InMemoryAssessmentSessionStore()

    first_turn = run_assessment_turn(
        "ช่วยประเมิน TRL ให้หน่อย ตอนนี้มีผลทดสอบในสภาพแวดล้อมที่เกี่ยวข้องแล้ว",
        store=store,
        candidate_level=5,
    )

    assert first_turn.decision_status == "needs_more_evidence"
    assert first_turn.matched_level == 4
    assert first_turn.next_question

    second_turn = run_assessment_turn(
        "มีข้อมูลสมรรถนะและความปลอดภัยรองรับผลการทดสอบแล้ว",
        session_id=first_turn.session_id,
        store=store,
    )

    assert second_turn.decision_status == "completed"
    assert second_turn.matched_level == 5
    assert second_turn.next_question is None
    assert "TRL 5" in second_turn.answer_text


def test_multi_turn_assessment_downgrades_when_user_explicitly_denies_missing_evidence():
    store = InMemoryAssessmentSessionStore()

    first_turn = run_assessment_turn(
        "ช่วยประเมิน TRL ให้หน่อย ตอนนี้มีผลทดสอบในสภาพแวดล้อมที่เกี่ยวข้องแล้ว",
        store=store,
        candidate_level=5,
    )

    second_turn = run_assessment_turn(
        "ยังไม่มีข้อมูลสมรรถนะหรือความปลอดภัยรองรับผลการทดสอบ",
        session_id=first_turn.session_id,
        store=store,
    )

    assert second_turn.decision_status == "downgraded"
    assert second_turn.matched_level == 4
    assert second_turn.next_question is None
    assert "TRL 4" in second_turn.answer_text
    assert "คำแนะนำเพิ่มเติมหลังการประเมิน" in second_turn.answer_text
    assert "TRL 5" in second_turn.answer_text
    assert "มีข้อมูลสมรรถนะหรือความปลอดภัยที่รองรับผลการทดสอบ" in second_turn.answer_text


def test_assessment_may_ask_for_experiment_evidence_when_not_mentioned():
    result = run_assessment_turn(
        "โครงการนี้ศึกษาหลักการพื้นฐานและทบทวนงานวิจัยแล้ว มีสมมติฐานและแนวทางประยุกต์ใช้เบื้องต้น",
        candidate_level=3,
    )

    assert result.decision_status == "needs_more_evidence"
    assert result.matched_level == 2
    assert result.next_evidence_id in {"trl_3_proof_of_concept", "trl_3_analytical_results"}
    assert all(item["status"] == "unknown" for item in result.missing_evidence)


def test_assessment_downgrades_when_experiment_evidence_is_explicitly_missing():
    result = run_assessment_turn(
        "โครงการนี้ศึกษาหลักการพื้นฐานและทบทวนงานวิจัยแล้ว มีสมมติฐานและแนวทางประยุกต์ใช้เบื้องต้น แต่ยังไม่มีการทดลองใดๆ",
        candidate_level=3,
    )

    assert result.decision_status == "downgraded"
    assert result.matched_level == 2
    assert result.next_question is None
    assert any(item["status"] == "missing" for item in result.missing_evidence)


def test_target_early_stage_scenario_downgrades_to_trl_1_without_reasking_denied_evidence():
    result = run_assessment_turn(
        "โครงการนี้ยังอยู่ในขั้นศึกษาหลักการทางคณิตศาสตร์และทบทวนงานวิจัยที่เกี่ยวข้องเพื่อสนับสนุนสมมติฐาน "
        "โดยยังไม่มีการกำหนดแนวทางพัฒนาเทคโนโลยีหรือการทดลองใดๆ คุณว่างานของฉันอยู่ใน TRL level ไหน"
    )

    assert result.decision_status == "downgraded"
    assert result.matched_level == 1
    assert result.candidate_level == 2
    assert result.next_question is None
    assert any(
        item["id"] == "trl_2_application_defined" and item["status"] == "missing"
        for item in result.missing_evidence
    )


def test_target_early_stage_response_explains_level_blockers_and_next_step():
    result = run_assessment_turn(
        "โครงการนี้ยังอยู่ในขั้นศึกษาหลักการทางคณิตศาสตร์และทบทวนงานวิจัยที่เกี่ยวข้องเพื่อสนับสนุนสมมติฐาน "
        "โดยยังไม่มีการกำหนดแนวทางพัฒนาเทคโนโลยีหรือการทดลองใดๆ คุณว่างานของฉันอยู่ใน TRL level ไหน"
    )

    assert "TRL 1" in result.answer_text
    assert "หลักฐานที่รองรับ TRL 1" in result.answer_text
    assert "หลักการ" in result.answer_text
    assert "เอกสารวิจัย" in result.answer_text or "งานวิจัย" in result.answer_text
    assert "TRL 2" in result.answer_text
    assert "แนวทางพัฒนาเทคโนโลยี" in result.answer_text or "การประยุกต์ใช้" in result.answer_text
    assert "TRL 3" in result.answer_text
    assert "ยังไม่มีการทดลอง" in result.answer_text
    assert "ขยับไปสู่" in result.answer_text


def test_additional_recommendation_supports_other_levels_without_fixed_phrasing():
    recommendation = _build_additional_recommendation(
        matched_level=2,
        collected_evidence={
            "trl_1_basic_principles": True,
            "trl_1_documented_research": True,
            "trl_2_concept_formulated": True,
            "trl_2_application_defined": True,
        },
    )

    assert recommendation is not None
    assert "คำแนะนำเพิ่มเติมหลังการประเมิน" in recommendation
    assert "TRL 2" in recommendation
    assert "TRL 3" in recommendation
    assert "มีผลการพิสูจน์แนวคิดหรือผลทดลองเบื้องต้น" in recommendation
    assert "มีผลวิเคราะห์หรือบันทึกผลทดสอบที่ชี้ว่าคุณลักษณะสำคัญทำงานได้" in recommendation
