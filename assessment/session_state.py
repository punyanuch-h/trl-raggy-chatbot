from __future__ import annotations

from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from metadata_store import utc_now_iso


def generate_session_id() -> str:
    return f"sess_{uuid4().hex}"


class AssessmentSessionState(BaseModel):
    session_id: str
    collected_evidence: dict[str, bool] = Field(default_factory=dict)
    rejected_evidence_ids: list[str] = Field(default_factory=list)
    uncertain_evidence_ids: list[str] = Field(default_factory=list)
    missing_evidence: list[dict[str, str]] = Field(default_factory=list)
    candidate_level: int = 1
    matched_level: int = 0
    last_asked_question: Optional[str] = None
    asked_evidence_ids: list[str] = Field(default_factory=list)
    status: str = "collecting"
    created_at: str = Field(default_factory=utc_now_iso)
    updated_at: str = Field(default_factory=utc_now_iso)


class InMemoryAssessmentSessionStore:
    def __init__(self):
        self._sessions: dict[str, AssessmentSessionState] = {}

    def create(self, session_id: str | None = None) -> AssessmentSessionState:
        state = AssessmentSessionState(session_id=session_id or generate_session_id())
        self.save(state)
        return state.model_copy(deep=True)

    def get(self, session_id: str) -> AssessmentSessionState | None:
        state = self._sessions.get(session_id)
        if state is None:
            return None
        return state.model_copy(deep=True)

    def save(self, state: AssessmentSessionState) -> AssessmentSessionState:
        state.updated_at = utc_now_iso()
        self._sessions[state.session_id] = state.model_copy(deep=True)
        return state
