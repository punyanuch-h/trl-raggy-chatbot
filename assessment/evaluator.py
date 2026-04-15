from __future__ import annotations

from pydantic import BaseModel

from assessment.rules import RuleBaseEntry, load_rule_base


class EvaluationResult(BaseModel):
    candidate_level: int
    matched_level: int
    missing_evidence: list[dict[str, str]]
    reasoning_summary: str


SUPPORTED_EVIDENCE_STATES = {"supported", "conflicting", "true", "yes", "present"}
MISSING_EVIDENCE_STATES = {"missing", "rejected", "explicitly_missing", "false", "no", "absent"}
UNCERTAIN_EVIDENCE_STATES = {"uncertain", "unknown", "maybe"}


def _evidence_state(value: object) -> str:
    if value is True:
        return "supported"
    if value is False or value is None:
        return "unknown"
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in SUPPORTED_EVIDENCE_STATES:
            return "supported"
        if normalized in MISSING_EVIDENCE_STATES:
            return "missing"
        if normalized in UNCERTAIN_EVIDENCE_STATES:
            return "uncertain"
    return "supported" if bool(value) else "unknown"


def _evaluate_single_level(rule: RuleBaseEntry, evidence: dict[str, object]) -> list[dict[str, str]]:
    missing = []
    for item in rule.required_evidence:
        state = _evidence_state(evidence.get(item.id))
        if state != "supported":
            missing.append({"id": item.id, "description_th": item.description_th, "status": state})
    return missing


def _has_explicit_missing(missing: list[dict[str, str]]) -> bool:
    return any(item.get("status") in {"missing", "uncertain"} for item in missing)


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
                blocker_note = " โดยมีหลักฐานบางส่วนที่ผู้ใช้ระบุชัดว่ายังไม่มีหรือยังไม่แน่ใจ" if _has_explicit_missing(last_missing) else ""
                summary = (
                    f"หลักฐานของ TRL {highest_attempt.level} ยังไม่ครบ จึงลดระดับมาที่ TRL {rule.level} "
                    f"ซึ่งมีหลักฐานครบตามเกณฑ์{blocker_note}"
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
