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
    "อยู่ trl ไหน",
    "trl level ไหน",
    "trl ระดับไหน",
    "งานของฉันอยู่ trl",
    "งานของฉันอยู่ใน trl",
    "งานของฉันอยู่ระดับไหน",
    "โครงการนี้อยู่ระดับไหน",
    "คุณว่างานของฉันอยู่ใน trl",
    "ควรเป็น trl อะไร",
    "ถือว่าอยู่ระดับไหน",
    "ระดับไหน",
    "ตอนนี้อยู่",
    "พร้อมส่งมอบ",
    "ผ่านการทดสอบ",
    "หลักฐาน",
    "assessment",
)
ASSESSMENT_CONTEXT_HINTS = (
    "เรามี",
    "เราทำ",
    "ตอนนี้มี",
    "ทีมงาน",
    "โครงการ",
    "โครงการนี้",
    "งานของฉัน",
    "งานของเรา",
    "ต้นแบบ",
    "ห้องปฏิบัติการ",
    "สภาพแวดล้อมที่เกี่ยวข้อง",
    "ใช้งานจริง",
    "มีการ",
    "ยังไม่มี",
    "ศึกษา",
    "ทบทวน",
    "ทดลอง",
    "พัฒนา",
)
QA_HINTS = (
    "คืออะไร",
    "หมายถึง",
    "ต่างจาก",
    "อธิบาย",
    "นิยาม",
    "เกณฑ์",
    "อะไรบ้าง",
    "เกี่ยวข้องกับ",
    "technology readiness level",
)
DIRECT_ASSESSMENT_CONTEXT_HINTS = (
    "ช่วยประเมิน",
    "ประเมิน trl",
    "ประเมินว่า",
    "เรามี",
    "เราทำ",
    "ตอนนี้มี",
    "ตอนนี้เรา",
    "โครงการ",
    "โครงการนี้",
    "งานของฉัน",
    "งานของเรา",
    "งานฉัน",
    "งานนี้",
    "ระบบของเรา",
)
GENERAL_KNOWLEDGE_QUESTION_HINTS = (
    "ถ้า",
    "ต้องมี",
    "อะไรบ้าง",
    "เกี่ยวข้องกับ",
    "ควรนับเป็น",
)
AMBIGUOUS_HINTS = (
    "ช่วยดูให้หน่อย",
    "ช่วยหน่อย",
)
LEVEL_QUESTION_HINTS = (
    "อยู่ trl ไหน",
    "trl level ไหน",
    "trl ระดับไหน",
    "งานของฉันอยู่ trl",
    "งานของฉันอยู่ใน trl",
    "งานของฉันอยู่ระดับไหน",
    "โครงการนี้อยู่ระดับไหน",
    "คุณว่างานของฉันอยู่ใน trl",
    "ควรเป็น trl อะไร",
    "ถือว่าอยู่ระดับไหน",
    "อยู่ใน trl",
    "ระดับไหน",
    "level ไหน",
    "อยู่ระดับไหน",
    "ตอนนี้อยู่",
)


def route_trl_intent(query: str) -> IntentDecision:
    normalized = query.strip().lower()
    interpretation = interpret_assessment_input(query)
    evidence_hits = sum(1 for signal in interpretation.evidence.values() if signal.status in {"supported", "missing", "uncertain", "conflicting"})

    assessment_score = sum(1 for hint in ASSESSMENT_HINTS if hint in normalized)
    assessment_context_score = sum(1 for hint in ASSESSMENT_CONTEXT_HINTS if hint in normalized)
    direct_assessment_context_score = sum(1 for hint in DIRECT_ASSESSMENT_CONTEXT_HINTS if hint in normalized)
    qa_score = sum(1 for hint in QA_HINTS if hint in normalized)
    explicit_definition_question = any(hint in normalized for hint in ("คืออะไร", "หมายถึง", "ต่างจาก", "อธิบาย"))
    general_knowledge_question = any(hint in normalized for hint in GENERAL_KNOWLEDGE_QUESTION_HINTS)
    asks_for_level = any(hint in normalized for hint in LEVEL_QUESTION_HINTS) or "ประเมิน" in normalized
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
