from agents.assessment_agent import interpret_assessment_input


def test_assessment_agent_extracts_structured_evidence_from_complete_statement():
    result = interpret_assessment_input(
        "เรามีต้นแบบระบบแล้วและได้ทดสอบในห้องปฏิบัติการว่าองค์ประกอบทำงานร่วมกันได้"
    )

    assert result.candidate_level_hint == 4
    assert result.evidence["trl_4_lab_validation"].status == "supported"
    assert result.evidence["trl_4_integrated_components"].status == "supported"
    assert result.final_level_proposed is None


def test_assessment_agent_marks_missing_or_uncertain_evidence():
    result = interpret_assessment_input(
        "ตอนนี้มีแนวคิดกับเอกสารวิจัยเบื้องต้น แต่ยังไม่ได้ทดสอบต้นแบบและยังไม่แน่ใจเรื่องการใช้งานจริง"
    )

    assert result.evidence["trl_1_documented_research"].status == "supported"
    assert result.evidence["trl_4_lab_validation"].status in {"missing", "conflicting"}
    assert result.uncertain_evidence


def test_assessment_agent_records_conflicting_signals():
    result = interpret_assessment_input(
        "เรามีต้นแบบในห้องปฏิบัติการ แต่ยังไม่ได้ทดสอบในห้องปฏิบัติการจริงและผลยังไม่ชัดเจน"
    )

    assert "trl_4_lab_validation" in result.conflicts


def test_assessment_agent_infers_integrated_components_from_lab_tested_prototype_performance():
    result = interpret_assessment_input(
        "ทีมงานได้พัฒนา prototype เครื่องกรองน้ำต้นแบบขนาดเล็ก โดยมีการกำหนดข้อกำหนดทางวิศวกรรมครบถ้วน "
        "มีการระบุวัสดุและกระบวนการผลิตชัดเจน ต้นแบบถูกทดสอบในห้องปฏิบัติการ "
        "และสามารถแสดงประสิทธิภาพในการกรองได้ตามเกณฑ์ที่ตั้งไว้ "
        "มีการวัดผลและบันทึกข้อมูลการทดสอบอย่างเป็นระบบ แต่ breadboard ยังไม่ได้ทดสอบ"
    )

    assert result.evidence["trl_4_lab_validation"].status == "supported"
    assert result.evidence["trl_4_integrated_components"].status == "supported"
    assert result.evidence["trl_4_integrated_components"].notes is not None


def test_assessment_agent_keeps_negation_local_to_relevant_clause():
    result = interpret_assessment_input(
        "มีผลทดสอบในสภาพแวดล้อมที่เกี่ยวข้องแล้ว แต่ยังไม่มีข้อมูลสมรรถนะหรือความปลอดภัยรองรับผลการทดสอบ"
    )

    assert result.evidence["trl_5_relevant_environment_test"].status == "supported"
    assert result.evidence["trl_5_supporting_performance_data"].status == "missing"


def test_assessment_agent_detects_uncertain_evidence_without_overwriting_supported_clause():
    result = interpret_assessment_input(
        "เรามีต้นแบบและทดสอบในห้องปฏิบัติการแล้ว แต่ผลในสภาพแวดล้อมที่เกี่ยวข้องยังไม่ชัดเจน"
    )

    assert result.evidence["trl_4_lab_validation"].status == "supported"
    assert result.evidence["trl_5_relevant_environment_test"].status == "uncertain"


def test_assessment_agent_detects_natural_thai_trl_1_basic_principles():
    result = interpret_assessment_input("โครงการนี้อยู่ในขั้นศึกษาหลักการทางคณิตศาสตร์")

    assert result.evidence["trl_1_basic_principles"].status == "supported"


def test_assessment_agent_detects_natural_thai_trl_1_documented_research():
    result = interpret_assessment_input("ทีมงานกำลังทบทวนงานวิจัยที่เกี่ยวข้องและทำ literature review")

    assert result.evidence["trl_1_documented_research"].status == "supported"


def test_assessment_agent_detects_hypothesis_as_trl_2_concept_signal():
    result = interpret_assessment_input("มีการรวบรวมเอกสารเพื่อสนับสนุนสมมติฐานของโครงการ")

    assert result.evidence["trl_2_concept_formulated"].status == "supported"


def test_assessment_agent_marks_missing_technology_development_direction():
    result = interpret_assessment_input("โครงการนี้ยังไม่มีการกำหนดแนวทางพัฒนาเทคโนโลยี")

    assert result.evidence["trl_2_application_defined"].status == "missing"


def test_assessment_agent_marks_missing_experiment_for_trl_3_evidence():
    result = interpret_assessment_input("งานนี้ยังไม่มีการทดลองใดๆ")

    assert result.evidence["trl_3_proof_of_concept"].status == "missing"
    assert result.evidence["trl_3_analytical_results"].status == "missing"


def test_assessment_agent_target_scenario_produces_early_stage_evidence_signals():
    result = interpret_assessment_input(
        "โครงการนี้ยังอยู่ในขั้นศึกษาหลักการทางคณิตศาสตร์และทบทวนงานวิจัยที่เกี่ยวข้องเพื่อสนับสนุนสมมติฐาน "
        "โดยยังไม่มีการกำหนดแนวทางพัฒนาเทคโนโลยีหรือการทดลองใดๆ คุณว่างานของฉันอยู่ใน TRL level ไหน"
    )

    assert result.evidence["trl_1_basic_principles"].status == "supported"
    assert result.evidence["trl_1_documented_research"].status == "supported"
    assert result.evidence["trl_2_concept_formulated"].status == "supported"
    assert result.evidence["trl_2_application_defined"].status == "missing"
    assert result.evidence["trl_3_proof_of_concept"].status == "missing"
    assert result.evidence["trl_3_analytical_results"].status == "missing"
