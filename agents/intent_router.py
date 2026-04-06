from __future__ import annotations

from pydantic import BaseModel


class IntentDecision(BaseModel):
    intent: str
    needs_clarification: bool = False
    rationale: str


ASSESSMENT_HINTS = (
    "ประเมิน",
    "ช่วยประเมิน",
    "อยู่ trl ไหน",
    "ระดับไหน",
    "ต้นแบบ",
    "ห้องปฏิบัติการ",
    "ใช้งานจริง",
    "พร้อมส่งมอบ",
    "ผ่านการทดสอบ",
    "สภาพแวดล้อมที่เกี่ยวข้อง",
    "assessment",
)
QA_HINTS = (
    "คืออะไร",
    "หมายถึง",
    "ต่างจาก",
    "อธิบาย",
    "trl ",
    "technology readiness level",
)
AMBIGUOUS_HINTS = (
    "ช่วยดูให้หน่อย",
    "ช่วยหน่อย",
)


def route_trl_intent(query: str) -> IntentDecision:
    normalized = query.strip().lower()
    assessment_score = sum(1 for hint in ASSESSMENT_HINTS if hint in normalized)
    qa_score = sum(1 for hint in QA_HINTS if hint in normalized)
    ambiguous = any(hint in normalized for hint in AMBIGUOUS_HINTS) and assessment_score == 0

    if assessment_score > max(qa_score, 0):
        return IntentDecision(intent="trl_assessment", needs_clarification=False, rationale="assessment_keywords_detected")

    if ambiguous:
        return IntentDecision(intent="general_qa", needs_clarification=True, rationale="ambiguous_short_trl_request")

    return IntentDecision(intent="general_qa", needs_clarification=False, rationale="default_safe_general_qa")
