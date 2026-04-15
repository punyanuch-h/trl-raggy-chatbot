import pytest
from pydantic import ValidationError

from assessment.rules import RuleBaseEntry, load_main_screening_questions, load_rule_base


def test_rule_base_loads_all_trl_levels():
    rule_base = load_rule_base()

    assert [entry.level for entry in rule_base] == list(range(1, 10))
    assert all(entry.required_evidence for entry in rule_base)
    assert all(entry.follow_up_questions for entry in rule_base)
    assert all(entry.diagnostic_questions for entry in rule_base)


def test_main_screening_questions_load_with_level_ranges():
    screening_questions = load_main_screening_questions()

    assert len(screening_questions) == 8
    assert screening_questions[0].id == "prototype_exists"
    assert screening_questions[0].yes_levels == [4, 5, 6, 7, 8, 9]
    assert screening_questions[0].no_levels == [1, 2, 3]
    assert screening_questions[-1].id == "hypothesis_feasibility"
    assert screening_questions[-1].yes_levels == [2]
    assert screening_questions[-1].no_levels == [1]


def test_rule_base_entries_keep_traceable_source_references():
    rule_base = load_rule_base()

    for entry in rule_base:
        assert entry.source_references
        assert all(ref.source_file == "source/Technology_Readiness_Level_Definition.txt" for ref in entry.source_references)
        assert all(ref.section for ref in entry.source_references)


def test_rule_schema_rejects_malformed_rule_entry():
    with pytest.raises(ValidationError):
        RuleBaseEntry.model_validate(
            {
                "level": 4,
                "name_th": "การตรวจสอบระดับห้องปฏิบัติการ",
                "summary_th": "ขาด required_evidence",
                "name_en": "Malformed Entry",
                "optional_evidence": [],
                "domain_notes": {},
                "follow_up_questions": [],
                "diagnostic_questions": [],
                "source_references": [],
            }
        )
