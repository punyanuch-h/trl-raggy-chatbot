from __future__ import annotations

from pydantic import BaseModel

from agents.assessment_agent import RULE_LEVELS, interpret_assessment_input
from assessment.evaluator import evaluate_trl_level
from assessment.response_templates import get_response_message
from assessment.rules import RuleBaseEntry, load_rule_base
from assessment.session_state import AssessmentSessionState, InMemoryAssessmentSessionStore


class AssessmentTurnResult(BaseModel):
    session_id: str
    answer_text: str
    candidate_level: int
    matched_level: int
    decision_status: str
    reasoning_summary: str
    missing_evidence: list[dict[str, str]]
    next_question: str | None = None
    next_evidence_id: str | None = None


def _get_rule(level: int) -> RuleBaseEntry:
    for rule in load_rule_base():
        if rule.level == level:
            return rule
    raise ValueError(f"Unknown TRL level: {level}")


def _mark_unique(target: list[str], evidence_id: str) -> None:
    if evidence_id not in target:
        target.append(evidence_id)


def _remove_if_present(target: list[str], evidence_id: str) -> None:
    if evidence_id in target:
        target.remove(evidence_id)


def _merge_interpretation(state: AssessmentSessionState, query: str) -> None:
    interpretation = interpret_assessment_input(query)
    state.candidate_level = max(state.candidate_level, interpretation.candidate_level_hint)

    for evidence_id, signal in interpretation.evidence.items():
        if signal.status == "supported":
            state.collected_evidence[evidence_id] = True
            _remove_if_present(state.rejected_evidence_ids, evidence_id)
            _remove_if_present(state.uncertain_evidence_ids, evidence_id)
        elif signal.status == "missing":
            state.collected_evidence.pop(evidence_id, None)
            _mark_unique(state.rejected_evidence_ids, evidence_id)
            _remove_if_present(state.uncertain_evidence_ids, evidence_id)
        else:
            state.collected_evidence.pop(evidence_id, None)
            _mark_unique(state.uncertain_evidence_ids, evidence_id)


def _build_follow_up_question(rule: RuleBaseEntry, evidence_id: str, description_th: str) -> str:
    required_ids = [item.id for item in rule.required_evidence]
    if evidence_id in required_ids:
        question_index = min(required_ids.index(evidence_id), len(rule.follow_up_questions) - 1)
        return rule.follow_up_questions[question_index]
    return f"ขอข้อมูลเพิ่มเติมเกี่ยวกับประเด็นนี้หน่อยครับ: {description_th}"


def _pick_next_question(
    state: AssessmentSessionState,
    missing_evidence: list[dict[str, str]],
) -> tuple[str | None, str | None]:
    if not missing_evidence:
        return None, None

    rule = _get_rule(state.candidate_level)
    for item in missing_evidence:
        evidence_id = item["id"]
        if evidence_id in state.asked_evidence_ids:
            continue
        question = _build_follow_up_question(rule, evidence_id, item["description_th"])
        _mark_unique(state.asked_evidence_ids, evidence_id)
        state.last_asked_question = question
        return evidence_id, question

    return None, None


def _join_thai_list(items: list[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} และ {items[1]}"
    return f"{', '.join(items[:-1])} และ {items[-1]}"


def _build_additional_recommendation(
    matched_level: int,
    collected_evidence: dict[str, bool],
) -> str | None:
    max_level = max(rule.level for rule in load_rule_base())
    if matched_level < 1 or matched_level >= max_level:
        return None

    current_rule = _get_rule(matched_level)
    next_rule = _get_rule(matched_level + 1)

    current_strengths = [
        item.description_th
        for item in current_rule.required_evidence
        if bool(collected_evidence.get(item.id))
    ]
    missing_next_level_items = [
        item.description_th
        for item in next_rule.required_evidence
        if not bool(collected_evidence.get(item.id))
    ]
    if not missing_next_level_items:
        return None

    strengths_text = _join_thai_list(current_strengths[:2]) if current_strengths else current_rule.summary_th
    gaps_text = _join_thai_list(missing_next_level_items)

    lines = [
        "คำแนะนำเพิ่มเติมหลังการประเมิน:",
        (
            f"จากหลักฐานที่มีอยู่ ตอนนี้งานวิจัยอยู่ในช่วง {current_rule.name_th} "
            f"(TRL {matched_level}) ได้ค่อนข้างชัด โดยเฉพาะในส่วนของ {strengths_text}"
        ),
    ]

    if len(missing_next_level_items) == 1:
        lines.append(
            f"หากต้องการขยับไปสู่ {next_rule.name_th} (TRL {next_rule.level}) "
            f"ประเด็นที่ควรเร่งเติมให้ชัดคือ {missing_next_level_items[0]}"
        )
    else:
        lines.append(
            f"สำหรับการไปต่อสู่ {next_rule.name_th} (TRL {next_rule.level}) "
            f"ยังควรทำให้เห็นเพิ่มในเรื่อง {gaps_text}"
        )

    lines.append(
        f"ประเด็นเหล่านี้จะช่วยให้ผลงานสอดคล้องกับลักษณะของระดับถัดไปที่เน้นว่า {next_rule.summary_th}"
    )
    lines.append(
        f"ถ้าสามารถอธิบายผลการพัฒนาและแนบหลักฐานของส่วนนี้ได้ชัดขึ้น "
        f"น้ำหนักของการประเมินเพื่อยืนยัน TRL {next_rule.level} จะดีขึ้นมาก"
    )
    return "\n".join(lines)


def _build_completed_answer(result: AssessmentTurnResult, collected_evidence: dict[str, bool]) -> str:
    lines = [
        f"ผลการประเมิน TRL: ขณะนี้หลักฐานรองรับอยู่ที่ TRL {result.matched_level}",
        result.reasoning_summary,
    ]
    if result.decision_status == "downgraded":
        lines.append(f"ระดับที่พยายามประเมินก่อนหน้าอยู่ที่ TRL {result.candidate_level} แต่หลักฐานยังไม่ครบตามเกณฑ์")
    additional_recommendation = _build_additional_recommendation(result.matched_level, collected_evidence)
    if additional_recommendation:
        lines.append(additional_recommendation)
    return "\n\n".join(lines)


def _build_follow_up_answer(candidate_level: int, matched_level: int, next_question: str) -> str:
    if matched_level > 0:
        status_line = f"ผลการประเมิน TRL เบื้องต้น: หลักฐานที่มีตอนนี้รองรับได้ถึง TRL {matched_level}"
    else:
        status_line = get_response_message("insufficient_evidence", mode="assessment")
    return (
        f"{status_line}\n\n"
        f"ยังยืนยัน TRL {candidate_level} ไม่ได้ เพราะยังมีหลักฐานที่ต้องยืนยันเพิ่มเติม\n\n"
        f"คำถามถัดไป: {next_question}"
    )


def _infer_progressive_floor(state: AssessmentSessionState) -> int:
    if state.candidate_level <= 1:
        return 0

    has_candidate_level_signal = any(
        state.collected_evidence.get(evidence_id)
        for evidence_id, level in RULE_LEVELS.items()
        if level == state.candidate_level
    )
    if has_candidate_level_signal:
        return state.candidate_level - 1
    return 0


def run_assessment_turn(
    query: str,
    session_id: str | None = None,
    store: InMemoryAssessmentSessionStore | None = None,
    candidate_level: int | None = None,
) -> AssessmentTurnResult:
    session_store = store or InMemoryAssessmentSessionStore()
    state = session_store.get(session_id) if session_id else None
    if state is None:
        state = session_store.create(session_id=session_id)

    if candidate_level is not None:
        state.candidate_level = max(state.candidate_level, candidate_level)

    _merge_interpretation(state, query)

    evaluation = evaluate_trl_level(state.collected_evidence, target_level=state.candidate_level)
    state.matched_level = evaluation.matched_level
    state.missing_evidence = evaluation.missing_evidence
    progressive_floor = _infer_progressive_floor(state)
    current_supported_level = max(evaluation.matched_level, progressive_floor)

    missing_ids = {item["id"] for item in evaluation.missing_evidence}
    explicit_blockers = missing_ids.intersection(state.rejected_evidence_ids + state.uncertain_evidence_ids)

    if evaluation.matched_level == state.candidate_level and not evaluation.missing_evidence:
        state.status = "completed"
        state.last_asked_question = None
        result = AssessmentTurnResult(
            session_id=state.session_id,
            answer_text="",
            candidate_level=state.candidate_level,
            matched_level=evaluation.matched_level,
            decision_status="completed",
            reasoning_summary=evaluation.reasoning_summary,
            missing_evidence=[],
        )
        result.answer_text = _build_completed_answer(result, state.collected_evidence)
        session_store.save(state)
        return result

    if evaluation.missing_evidence and not explicit_blockers:
        next_evidence_id, next_question = _pick_next_question(state, evaluation.missing_evidence)
        if next_question:
            state.status = "collecting"
            result = AssessmentTurnResult(
                session_id=state.session_id,
                answer_text=_build_follow_up_answer(
                    candidate_level=state.candidate_level,
                    matched_level=current_supported_level,
                    next_question=next_question,
                ),
                candidate_level=state.candidate_level,
                matched_level=current_supported_level,
                decision_status="needs_more_evidence",
                reasoning_summary=evaluation.reasoning_summary,
                missing_evidence=evaluation.missing_evidence,
                next_question=next_question,
                next_evidence_id=next_evidence_id,
            )
            session_store.save(state)
            return result

    state.status = "completed"
    state.last_asked_question = None
    final_supported_level = max(evaluation.matched_level, progressive_floor)
    decision_status = "downgraded" if final_supported_level > 0 else "insufficient_evidence"
    reasoning_summary = evaluation.reasoning_summary
    if decision_status == "insufficient_evidence":
        answer_text = get_response_message("insufficient_evidence", mode="assessment")
    else:
        answer_text = ""

    result = AssessmentTurnResult(
        session_id=state.session_id,
        answer_text=answer_text,
        candidate_level=state.candidate_level,
        matched_level=final_supported_level,
        decision_status=decision_status,
        reasoning_summary=reasoning_summary,
        missing_evidence=evaluation.missing_evidence,
    )
    if decision_status == "downgraded":
        result.answer_text = _build_completed_answer(result, state.collected_evidence)

    session_store.save(state)
    return result


__all__ = [
    "AssessmentTurnResult",
    "InMemoryAssessmentSessionStore",
    "run_assessment_turn",
]
