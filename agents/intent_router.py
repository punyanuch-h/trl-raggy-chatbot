from __future__ import annotations

from pydantic import BaseModel

from agents.assessment_agent import interpret_assessment_input


class IntentDecision(BaseModel):
    intent: str
    needs_clarification: bool = False
    rationale: str


ASSESSMENT_HINTS = (
    "ประเมิน",
    "ช่วยประเมิน",
    "ช่วยดู trl",
    "ดู trl",
    "assessment",
    "assess",
    "evaluate",
    "check my project",
    "what trl level",
    "which trl level",
    "what level are we at",
    "อยู่ trl ไหน",
    "trl level ไหน",
    "trl ระดับไหน",
    "ควรเป็น trl อะไร",
    "ระดับไหน",
)
ASSESSMENT_CONTEXT_HINTS = (
    "เรามี",
    "เราทำ",
    "ตอนนี้มี",
    "ทีมงาน",
    "โครงการ",
    "งานของฉัน",
    "งานของเรา",
    "ต้นแบบ",
    "prototype",
    "project",
    "we have",
    "our project",
    "our team",
    "tested",
    "validated",
    "demonstrated",
    "relevant environment",
    "operational environment",
)
QA_HINTS = (
    "คืออะไร",
    "หมายถึง",
    "ต่างจาก",
    "อธิบาย",
    "นิยาม",
    "เกณฑ์",
    "อะไรบ้าง",
    "what is",
    "what's",
    "compare",
    "difference",
    "definition",
    "describe",
    "criteria",
    "evidence",
    "technology readiness level",
)
DIRECT_ASSESSMENT_CONTEXT_HINTS = (
    "ช่วยประเมิน",
    "ช่วยดู trl",
    "ประเมิน trl",
    "ประเมินว่า",
    "assessment",
    "assess",
    "evaluate",
    "we have",
    "our project",
    "project",
    "prototype",
    "tested",
    "validated",
    "demonstrated",
    "ตอนนี้มี",
    "ตอนนี้เรา",
    "โครงการ",
    "งานนี้",
    "ระบบของเรา",
)
GENERAL_KNOWLEDGE_QUESTION_HINTS = (
    "ถ้า",
    "ต้องมี",
    "อะไรบ้าง",
    "เกี่ยวข้องกับ",
    "ควรนับเป็น",
    "what does",
    "what is required",
    "what evidence",
    "compare",
    "difference",
)
AMBIGUOUS_HINTS = (
    "ช่วยดูให้หน่อย",
    "ช่วยหน่อย",
    "can you check this",
    "can you check",
    "help me with this",
)
LEVEL_QUESTION_HINTS = (
    "อยู่ trl ไหน",
    "trl level ไหน",
    "trl ระดับไหน",
    "ควรเป็น trl อะไร",
    "อยู่ใน trl",
    "level ไหน",
    "อยู่ระดับไหน",
    "what trl level",
    "which trl level",
    "what level",
)


def route_trl_intent(query: str) -> IntentDecision:
    normalized = query.strip().lower()
    interpretation = interpret_assessment_input(query)
    evidence_hits = sum(
        1 for signal in interpretation.evidence.values() if signal.status in {"supported", "missing", "uncertain", "conflicting"}
    )

    assessment_score = sum(1 for hint in ASSESSMENT_HINTS if hint in normalized)
    assessment_context_score = sum(1 for hint in ASSESSMENT_CONTEXT_HINTS if hint in normalized)
    direct_assessment_context_score = sum(1 for hint in DIRECT_ASSESSMENT_CONTEXT_HINTS if hint in normalized)
    qa_score = sum(1 for hint in QA_HINTS if hint in normalized)
    explicit_definition_question = any(
        hint in normalized
        for hint in ("คืออะไร", "หมายถึง", "ต่างจาก", "อธิบาย", "what is", "what's", "compare", "difference", "describe")
    )
    general_knowledge_question = any(hint in normalized for hint in GENERAL_KNOWLEDGE_QUESTION_HINTS)
    asks_for_level = any(hint in normalized for hint in LEVEL_QUESTION_HINTS) or "ประเมิน" in normalized or "assess" in normalized
    ambiguous = any(hint in normalized for hint in AMBIGUOUS_HINTS)

    if explicit_definition_question and assessment_score == 0 and evidence_hits <= 1:
        return IntentDecision(intent="general_qa", needs_clarification=False, rationale="definition_style_trl_question")

    if general_knowledge_question and direct_assessment_context_score == 0:
        return IntentDecision(intent="general_qa", needs_clarification=False, rationale="general_knowledge_trl_question")

    if asks_for_level and (assessment_context_score > 0 or evidence_hits > 0):
        return IntentDecision(intent="trl_assessment", needs_clarification=False, rationale="assessment_request_with_context")

    if direct_assessment_context_score > 0 and evidence_hits > 0 and qa_score == 0:
        return IntentDecision(intent="trl_assessment", needs_clarification=False, rationale="direct_context_with_assessment_evidence")

    if evidence_hits >= 2 and qa_score == 0 and direct_assessment_context_score > 0:
        return IntentDecision(intent="trl_assessment", needs_clarification=False, rationale="multiple_assessment_evidence_signals")

    if ambiguous and assessment_score == 0 and evidence_hits == 0:
        return IntentDecision(intent="general_qa", needs_clarification=True, rationale="ambiguous_short_trl_request")

    if assessment_score > max(qa_score, 0) and (assessment_context_score > 0 or evidence_hits > 0):
        return IntentDecision(intent="trl_assessment", needs_clarification=False, rationale="assessment_keywords_detected")

    return IntentDecision(intent="general_qa", needs_clarification=False, rationale="default_safe_general_qa")
