from assessment.conversation import (
    AssessmentTurnResult,
    InMemoryAssessmentSessionStore,
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
