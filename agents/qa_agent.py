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


def answer_general_qa(
    query: str,
    rag_answer: str | None,
    retrieval_status: str = "completed",
    language: str = "th",
) -> QAAgentResponse:
    normalized = query.lower()
    if any(hint in normalized for hint in OFF_TOPIC_HINTS) and not is_trl_related(query):
        return QAAgentResponse(
            answer_text=get_response_message("off_topic", mode="qa", language=language),
            source="off_topic_guard",
        )

    if rag_answer and rag_answer.strip():
        return QAAgentResponse(answer_text=rag_answer.strip(), source="rag_chain")

    if retrieval_status == "retrieval_failed":
        return QAAgentResponse(
            answer_text=get_response_message("technical_error", mode="qa", language=language),
            source="retrieval_failure_fallback",
        )

    return QAAgentResponse(
        answer_text=get_response_message("insufficient_evidence", mode="qa", language=language),
        source="qa_fallback",
    )
