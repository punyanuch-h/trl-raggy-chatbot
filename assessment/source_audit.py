from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
AUTHORITATIVE_SOURCE_RELATIVE_PATH = "source/Technology_Readiness_Level_Definition.txt"
AUTHORITATIVE_SOURCE_PATH = PROJECT_ROOT / AUTHORITATIVE_SOURCE_RELATIVE_PATH
AUTHORITATIVE_THAI_PHRASES = (
    "คำอธิบายเพิ่มเติมเกี่ยวกับระดับของ Technology Readiness Level",
    "สำนักพัฒนาวิทยาศาสตร์และเทคโนโลยีแห่งชาติ",
    "หลักการพื้นฐานได้รับการพิจารณาและมีการรายงาน",
)
MOJIBAKE_MARKERS = ("à¸", "à¹", "Ã", "�")
SOURCE_REGISTRY: tuple[dict[str, str], ...] = (
    {
        "path": AUTHORITATIVE_SOURCE_RELATIVE_PATH,
        "purpose": "trl_definition_authoritative_source",
        "encoding": "utf-8",
        "owner": "Sprint 14 source-aware TRL QA",
    },
    {
        "path": "source/compare_each_level_of_trl.txt",
        "purpose": "trl_level_comparison_and_transition_qa",
        "encoding": "utf-8",
        "owner": "Sprint 14 source-aware TRL QA",
    },
    {
        "path": "source/helper_classification_domain_of_research.txt",
        "purpose": "research_domain_classification_helper",
        "encoding": "utf-8",
        "owner": "Sprint 14 source-aware TRL QA",
    },
    {
        "path": "source/helper_classification_level_trl.txt",
        "purpose": "trl_level_classification_helper",
        "encoding": "utf-8",
        "owner": "Sprint 14 source-aware TRL QA",
    },
)


def get_authoritative_source_manifest() -> list[dict[str, str]]:
    return [dict(entry) for entry in SOURCE_REGISTRY]


def verify_source_text_integrity(
    text: str,
    expected_phrases: tuple[str, ...] = AUTHORITATIVE_THAI_PHRASES,
) -> dict[str, object]:
    issues: list[str] = []
    if any(marker in text for marker in MOJIBAKE_MARKERS):
        issues.append("mojibake")
    if not any("\u0E00" <= char <= "\u0E7F" for char in text):
        issues.append("missing_thai_characters")
    if expected_phrases and not any(phrase in text for phrase in expected_phrases):
        issues.append("missing_expected_phrases")
    return {"is_valid": not issues, "issues": issues}


def load_registered_source_text(relative_path: str) -> str:
    registered_paths = {entry["path"] for entry in SOURCE_REGISTRY}
    if relative_path not in registered_paths:
        raise ValueError(
            f"Unknown TRL source '{relative_path}'. Register it in assessment/source_audit.py SOURCE_REGISTRY."
        )

    source_path = PROJECT_ROOT / relative_path
    if not source_path.exists():
        raise FileNotFoundError(
            f"Required TRL source file is missing: {relative_path}. "
            "Restore the file under source/ or update SOURCE_REGISTRY."
        )

    text = source_path.read_text(encoding="utf-8")
    expected_phrases = (
        AUTHORITATIVE_THAI_PHRASES
        if relative_path == AUTHORITATIVE_SOURCE_RELATIVE_PATH
        else ()
    )
    report = verify_source_text_integrity(text, expected_phrases=expected_phrases)
    if not report["is_valid"]:
        raise ValueError(f"Source integrity check failed for {relative_path}: {report['issues']}")
    return text


def load_authoritative_source_text() -> str:
    return load_registered_source_text(AUTHORITATIVE_SOURCE_RELATIVE_PATH)
