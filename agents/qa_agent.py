from __future__ import annotations

from pydantic import BaseModel

from assessment.response_templates import get_response_message


class QAAgentResponse(BaseModel):
    mode: str = "qa"
    answer_text: str
    source: str


OFF_TOPIC_HINTS = (
    "ขนม",
    "อาหาร",
    "ท่องเที่ยว",
    "เพลง",
    "ฟุตบอล",
)
TRL_HINTS = ("trl", "technology readiness level", "ความพร้อม", "ต้นแบบ", "เทคโนโลยี")


def is_trl_related(query: str) -> bool:
    normalized = query.lower()
    return any(hint in normalized for hint in TRL_HINTS)


def answer_general_qa(query: str, rag_answer: str | None) -> QAAgentResponse:
    normalized = query.lower()
    if any(hint in normalized for hint in OFF_TOPIC_HINTS) and not is_trl_related(query):
        return QAAgentResponse(
            answer_text=get_response_message("off_topic", mode="qa"),
            source="off_topic_guard",
        )

    if rag_answer:
        return QAAgentResponse(answer_text=rag_answer.strip(), source="rag_chain")

    return QAAgentResponse(
        answer_text=get_response_message("insufficient_evidence", mode="qa"),
        source="qa_fallback",
    )
