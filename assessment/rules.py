from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field, field_validator


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RULE_BASE_PATH = PROJECT_ROOT / "rules" / "trl_rules.json"


class EvidenceItem(BaseModel):
    id: str
    description_th: str


class DiagnosticQuestion(BaseModel):
    id: str
    question_th: str


class ScreeningQuestion(BaseModel):
    id: str
    question_th: str
    yes_levels: list[int]
    no_levels: list[int]

    @field_validator("yes_levels", "no_levels")
    @classmethod
    def validate_levels(cls, value: list[int]) -> list[int]:
        if not value:
            raise ValueError("levels must not be empty")
        if any(level < 1 or level > 9 for level in value):
            raise ValueError("levels must be within TRL 1-9")
        return value


class SourceReference(BaseModel):
    source_file: str
    section: str
    excerpt: str


class RuleBaseEntry(BaseModel):
    level: int = Field(ge=1, le=9)
    name_th: str
    name_en: str
    summary_th: str
    required_evidence: list[EvidenceItem]
    optional_evidence: list[EvidenceItem]
    domain_notes: dict[str, str]
    follow_up_questions: list[str]
    diagnostic_questions: list[DiagnosticQuestion]
    source_references: list[SourceReference]

    @field_validator("required_evidence", "follow_up_questions", "diagnostic_questions", "source_references")
    @classmethod
    def validate_non_empty(cls, value):
        if not value:
            raise ValueError("field must not be empty")
        return value


class RuleBasePayload(BaseModel):
    main_screening_questions: list[ScreeningQuestion]
    levels: list[RuleBaseEntry]

    @field_validator("main_screening_questions", "levels")
    @classmethod
    def validate_non_empty(cls, value):
        if not value:
            raise ValueError("field must not be empty")
        return value


@lru_cache(maxsize=1)
def load_rule_catalog() -> RuleBasePayload:
    payload = json.loads(RULE_BASE_PATH.read_text(encoding="utf-8"))
    catalog = RuleBasePayload.model_validate(payload)
    catalog.levels.sort(key=lambda item: item.level)
    return catalog


@lru_cache(maxsize=1)
def load_rule_base() -> list[RuleBaseEntry]:
    return load_rule_catalog().levels


@lru_cache(maxsize=1)
def load_main_screening_questions() -> list[ScreeningQuestion]:
    return load_rule_catalog().main_screening_questions
