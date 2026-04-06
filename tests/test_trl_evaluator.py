from assessment.evaluator import evaluate_trl_level
from assessment.rules import load_rule_base


def _evidence_for_level(level: int) -> dict[str, bool]:
    evidence = {}
    for entry in load_rule_base():
        if entry.level <= level:
            for item in entry.required_evidence:
                evidence[item.id] = True
    return evidence


def test_each_trl_level_passes_with_complete_required_evidence():
    for level in range(1, 10):
        result = evaluate_trl_level(_evidence_for_level(level))
        assert result.matched_level == level
        assert result.missing_evidence == []


def test_evaluator_reports_missing_required_evidence():
    evidence = _evidence_for_level(4)
    evidence["trl_4_lab_validation"] = False

    result = evaluate_trl_level(evidence, target_level=4)

    assert result.matched_level == 3
    assert result.candidate_level == 4
    assert any(item["id"] == "trl_4_lab_validation" for item in result.missing_evidence)


def test_evaluator_downgrades_when_higher_level_is_incomplete():
    evidence = _evidence_for_level(8)
    evidence["trl_8_qualification"] = False

    result = evaluate_trl_level(evidence)

    assert result.matched_level == 7
    assert result.candidate_level == 8
    assert "ลดระดับ" in result.reasoning_summary
