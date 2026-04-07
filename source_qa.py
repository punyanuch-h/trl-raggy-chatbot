from __future__ import annotations

import re

from assessment.source_audit import load_authoritative_source_text


TRL_LEVEL_PATTERN = re.compile(r"\btrl\s*([1-9])\b", re.IGNORECASE)
SECTION_PATTERN_TEMPLATE = r"TRL {level}\s+คือ\s+(.*?)(?=\nTRL [1-9]\s+คือ|\Z)"
DEFINITION_QUERY_HINTS = (
    "คืออะไร",
    "คือ",
    "what is",
    "what's",
    "meaning",
    "อธิบาย",
)
ASSESSMENT_QUERY_HINTS = (
    "ประเมิน",
    "assessment",
    "evaluate",
    "evidence",
    "หลักฐาน",
)


def _clean_line(text: str) -> str:
    return " ".join(text.replace("\u00a0", " ").split())


def _extract_level_section(level: int, text: str) -> str | None:
    match = re.search(
        SECTION_PATTERN_TEMPLATE.format(level=level),
        text,
        flags=re.DOTALL,
    )
    if not match:
        return None
    return match.group(0).strip()


def _build_level_answer(level: int, section: str) -> str | None:
    lines = [_clean_line(line) for line in section.splitlines() if _clean_line(line)]
    if len(lines) < 4:
        return None

    title_line = lines[0]
    description_lines: list[str] = []
    for line in lines[1:]:
        if line.startswith("ข้อมูลสนับสนุน") or line.startswith("ตัวอย่างผลงาน"):
            break
        if line == "คำอธิบาย" or line == "คำอธิบาย:":
            continue
        description_lines.append(line)

    if not description_lines:
        return title_line

    summary = description_lines[0]
    return f"{title_line} {summary}".strip()


def answer_query_from_source(query: str) -> str | None:
    normalized_query = query.strip().lower()
    levels = [int(match) for match in TRL_LEVEL_PATTERN.findall(query)]
    if len(levels) != 1:
        return None
    if any(hint in normalized_query for hint in ASSESSMENT_QUERY_HINTS):
        return None
    if not any(hint in normalized_query for hint in DEFINITION_QUERY_HINTS):
        compact_query = " ".join(normalized_query.split())
        if compact_query not in {f"trl {levels[0]}", f"trl{levels[0]}"} and "?" not in compact_query:
            return None

    text = load_authoritative_source_text()
    section = _extract_level_section(levels[0], text)
    if not section:
        return None

    return _build_level_answer(levels[0], section)
