from assessment.source_audit import load_authoritative_source_text, load_registered_source_text
from source_qa import answer_query_from_source, extract_comparison_section, extract_level_section


COMPARISON_SOURCE_PATH = "source/compare_each_level_of_trl.txt"


def test_source_qa_returns_authoritative_trl_definition_from_source_text():
    answer = answer_query_from_source("TRL 4 คืออะไร")

    assert answer is not None
    assert "TRL 4 คือ" in answer
    assert "ห้องปฏิบัติการ" in answer


def test_source_qa_returns_adjacent_level_comparison_from_comparison_source():
    answer = answer_query_from_source("ช่วยเปรียบเทียบ TRL 5 กับ TRL 6 ว่าต่างกันตรงไหน")

    assert answer is not None
    assert "TRL 5" in answer
    assert "TRL 6" in answer
    assert "ต้นแบบ" in answer or "prototype" in answer
    assert "ข้อมูลจากเอกสารอ้างอิงยังไม่เพียงพอ" not in answer


def test_source_qa_returns_evidence_guidance_for_level_from_definition_source():
    answer = answer_query_from_source("TRL 8 ต้องมีหลักฐานอะไรบ้างก่อนบอกว่าพร้อมส่งมอบ")

    assert answer is not None
    assert "TRL 8" in answer
    assert "หลักฐาน" in answer
    assert "พร้อมส่งมอบ" in answer


def test_source_qa_returns_transition_guidance_from_comparison_source():
    answer = answer_query_from_source("จะขยับจาก TRL 5 ไป TRL 6 ต้องมีอะไร")

    assert answer is not None
    assert "TRL 5" in answer
    assert "TRL 6" in answer


def test_extract_level_section_stops_before_next_trl_definition():
    text = load_authoritative_source_text()

    section = extract_level_section(5, text)

    assert section is not None
    assert section.startswith("TRL 5 คือ")
    assert "Relevant Environments" in section
    assert "TRL 6 คือ" not in section


def test_extract_level_section_for_trl_6_stops_before_trl_7():
    text = load_authoritative_source_text()

    section = extract_level_section(6, text)

    assert section is not None
    assert section.startswith("TRL 6 คือ")
    assert "prototype" in section.lower()
    assert "TRL 7 คือ" not in section


def test_extract_comparison_section_returns_only_requested_adjacent_pair():
    text = load_registered_source_text(COMPARISON_SOURCE_PATH)

    section = extract_comparison_section(5, 6, text)

    assert section is not None
    assert section.startswith("TRL 5 เทียบกับ TRL 6")
    assert "TRL 5:" in section
    assert "TRL 6:" in section
    assert "TRL 4 เทียบกับ TRL 5" not in section
    assert "TRL 6 เทียบกับ TRL 7" not in section


def test_extract_comparison_section_supports_reversed_query_order():
    text = load_registered_source_text(COMPARISON_SOURCE_PATH)

    section = extract_comparison_section(6, 5, text)

    assert section is not None
    assert section.startswith("TRL 5 เทียบกับ TRL 6")
    assert "prototype" in section or "ต้นแบบ" in section
    assert "TRL 7:" not in section


def test_source_qa_ignores_non_definition_queries():
    assert answer_query_from_source("ช่วยประเมิน TRL ให้หน่อย ตอนนี้มีต้นแบบแล้ว") is None


def test_source_qa_returns_english_definition_when_requested():
    answer = answer_query_from_source("What is TRL 4?", language="en")

    assert answer is not None
    assert "TRL 4" in answer
    assert "laboratory environment" in answer.lower()


def test_source_qa_returns_english_comparison_when_requested():
    answer = answer_query_from_source("Compare TRL 5 and TRL 6", language="en")

    assert answer is not None
    assert "TRL 5 vs TRL 6" in answer
    assert "prototype" in answer.lower() or "relevant environment" in answer.lower()
