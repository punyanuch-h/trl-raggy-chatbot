from __future__ import annotations

from pydantic import BaseModel

from agents.assessment_agent import interpret_assessment_input
from agents.intent_router import route_trl_intent
from agents.qa_agent import answer_general_qa
from assessment.evaluator import evaluate_trl_level
from assessment.response_templates import get_response_message


class OrchestrationResult(BaseModel):
    mode: str
    answer_text: str
    intent: str
    needs_clarification: bool = False


def build_assessment_answer(query: str) -> str:
    interpretation = interpret_assessment_input(query)
    evaluator_input = {
        evidence_id: signal.status == "supported"
        for evidence_id, signal in interpretation.evidence.items()
    }
    result = evaluate_trl_level(evaluator_input, target_level=interpretation.candidate_level_hint)

    if result.matched_level <= 0:
        return get_response_message("insufficient_evidence", mode="assessment")

    lines = [
        f"ระบบประเมินว่าหลักฐานปัจจุบันรองรับได้ถึง TRL {result.matched_level}",
        result.reasoning_summary,
    ]
    if result.missing_evidence:
        missing = ", ".join(item["description_th"] for item in result.missing_evidence)
        lines.append(f"หลักฐานที่ยังขาดสำหรับระดับที่สูงกว่าคือ: {missing}")
    return "\n\n".join(lines)


def orchestrate_query(query: str, rag_answer: str | None = None) -> OrchestrationResult:
    decision = route_trl_intent(query)
    if decision.intent == "trl_assessment":
        return OrchestrationResult(
            mode="assessment",
            answer_text=build_assessment_answer(query),
            intent=decision.intent,
            needs_clarification=decision.needs_clarification,
        )

    qa_response = answer_general_qa(query=query, rag_answer=rag_answer)
    if decision.needs_clarification and qa_response.source != "off_topic_guard":
        answer_text = (
            "หากต้องการคำอธิบาย TRL ผมช่วยตอบได้ทันที แต่ถ้าต้องการให้ประเมินระดับ TRL "
            "กรุณาเล่าหลักฐาน เช่น แนวคิด ต้นแบบ ผลทดสอบ หรือการใช้งานจริง"
        )
    else:
        answer_text = qa_response.answer_text
    return OrchestrationResult(
        mode=qa_response.mode,
        answer_text=answer_text,
        intent=decision.intent,
        needs_clarification=decision.needs_clarification,
    )
