from __future__ import annotations

from pydantic import BaseModel

from assessment.rules import RuleBaseEntry, load_rule_base


class EvaluationResult(BaseModel):
    candidate_level: int
    matched_level: int
    missing_evidence: list[dict[str, str]]
    reasoning_summary: str


def _evaluate_single_level(rule: RuleBaseEntry, evidence: dict[str, object]) -> list[dict[str, str]]:
    missing = []
    for item in rule.required_evidence:
        if not bool(evidence.get(item.id)):
            missing.append({"id": item.id, "description_th": item.description_th})
    return missing


def evaluate_trl_level(evidence: dict[str, object], target_level: int | None = None) -> EvaluationResult:
    rules = load_rule_base()
    if target_level is None:
        inferred_candidate = 0
        for rule in rules:
            if any(bool(evidence.get(item.id)) for item in rule.required_evidence):
                inferred_candidate = rule.level
        highest_level = inferred_candidate or rules[0].level
    else:
        highest_level = target_level
    eligible_rules = [rule for rule in rules if rule.level <= highest_level]
    highest_attempt = eligible_rules[-1]
    last_missing: list[dict[str, str]] = []

    for rule in reversed(eligible_rules):
        missing = _evaluate_single_level(rule, evidence)
        if not missing:
            if rule.level == highest_attempt.level:
                summary = f"หลักฐานรองรับครบตามเกณฑ์ TRL {rule.level}"
            else:
                summary = (
                    f"หลักฐานของ TRL {highest_attempt.level} ยังไม่ครบ จึงลดระดับมาที่ TRL {rule.level} "
                    "ซึ่งมีหลักฐานครบตามเกณฑ์"
                )
            return EvaluationResult(
                candidate_level=highest_attempt.level,
                matched_level=rule.level,
                missing_evidence=last_missing if rule.level != highest_attempt.level else [],
                reasoning_summary=summary,
            )
        if rule.level == highest_attempt.level:
            last_missing = missing

    first_rule = eligible_rules[0]
    return EvaluationResult(
        candidate_level=highest_attempt.level,
        matched_level=0,
        missing_evidence=last_missing or _evaluate_single_level(first_rule, evidence),
        reasoning_summary="ยังไม่มีหลักฐานเพียงพอสำหรับยืนยัน TRL ขั้นต่ำตามกฎที่กำหนด",
    )
