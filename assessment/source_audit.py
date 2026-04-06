from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
AUTHORITATIVE_SOURCE_PATH = PROJECT_ROOT / "source" / "04_Technology Readiness Level-TRL.txt"
AUTHORITATIVE_THAI_PHRASES = (
    "คำอธิบายเพิ่มเติมเกี่ยวกับระดับของ Technology Readiness Level",
    "สำนักพัฒนาวิทยาศาสตร์และเทคโนโลยีแห่งชาติ",
    "หลักการพื้นฐานได้รับการพิจารณาและมีการรายงาน",
)
MOJIBAKE_MARKERS = ("à¸", "à¹", "Ã", "�")


def get_authoritative_source_manifest() -> list[dict[str, str]]:
    return [
        {
            "path": "source/04_Technology Readiness Level-TRL.txt",
            "purpose": "trl_assessment_rule_base",
            "encoding": "utf-8",
            "owner": "Sprint 8 rule-base foundation",
        }
    ]


def verify_source_text_integrity(text: str) -> dict[str, object]:
    issues: list[str] = []
    if any(marker in text for marker in MOJIBAKE_MARKERS):
        issues.append("mojibake")
    if not any("\u0E00" <= char <= "\u0E7F" for char in text):
        issues.append("missing_thai_characters")
    if not any(phrase in text for phrase in AUTHORITATIVE_THAI_PHRASES):
        issues.append("missing_expected_phrases")
    return {"is_valid": not issues, "issues": issues}


def load_authoritative_source_text() -> str:
    text = AUTHORITATIVE_SOURCE_PATH.read_text(encoding="utf-8")
    report = verify_source_text_integrity(text)
    if not report["is_valid"]:
        raise ValueError(f"Authoritative source integrity check failed: {report['issues']}")
    return text
