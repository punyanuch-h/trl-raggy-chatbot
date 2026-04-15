from __future__ import annotations

import re

from assessment.source_audit import load_authoritative_source_text, load_registered_source_text


TRL_LEVEL_PATTERN = re.compile(r"\btrl\s*([1-9])\b", re.IGNORECASE)
SECTION_PATTERN_TEMPLATE = r"^TRL {level}\s+คือ\s+(.*?)(?=^TRL [1-9]\s+คือ|\Z)"
COMPARISON_SECTION_PATTERN_TEMPLATE = (
    r"^TRL {level_a}\s+เทียบกับ\s+TRL {level_b}\s*(.*?)(?=^TRL [1-9]\s+เทียบกับ\s+TRL [1-9]|\n-{{10,}}|\Z)"
)
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
    "ประเมินระดับ",
    "assessment",
    "evaluate",
    "อยู่ trl ไหน",
    "trl level ไหน",
    "อยู่ระดับไหน",
    "ควรเป็น trl",
)
COMPARISON_QUERY_HINTS = (
    "เปรียบเทียบ",
    "ต่างกัน",
    "ต่างจาก",
    "เทียบกับ",
    "compare",
    "difference",
    "vs",
)
EVIDENCE_QUERY_HINTS = (
    "หลักฐาน",
    "ต้องมีอะไร",
    "อะไรบ้าง",
    "พร้อมส่งมอบ",
    "qualified",
    "evidence",
)
TRANSITION_QUERY_HINTS = (
    "ขยับจาก",
    "ไป trl",
    "เลื่อนจาก",
    "ยกระดับ",
    "move from",
    "transition",
)
COMPARISON_SOURCE_PATH = "source/compare_each_level_of_trl.txt"
INSUFFICIENT_EVIDENCE_FALLBACK_PHRASE = "ข้อมูลจากเอกสารอ้างอิงยังไม่เพียงพอ"


def _clean_line(text: str) -> str:
    return " ".join(text.replace("\u00a0", " ").split())


def _normalize_source_text(text: str) -> str:
    normalized = text.replace("\ufeff", "").replace("\u00a0", " ")
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(line.rstrip() for line in normalized.split("\n"))


def extract_level_section(level: int, text: str) -> str | None:
    normalized_text = _normalize_source_text(text)
    match = re.search(
        SECTION_PATTERN_TEMPLATE.format(level=level),
        normalized_text,
        flags=re.DOTALL | re.MULTILINE,
    )
    if not match:
        return None
    return _clean_source_excerpt(match.group(0).strip(), max_chars=2600)


def extract_comparison_section(level_a: int, level_b: int, text: str) -> str | None:
    normalized_text = _normalize_source_text(text)
    candidate_pairs = [(level_a, level_b)]
    if level_a != level_b:
        candidate_pairs.append((level_b, level_a))
    if abs(level_a - level_b) == 1:
        low, high = sorted((level_a, level_b))
        candidate_pairs.append((low, high))

    for first, second in candidate_pairs:
        match = re.search(
            COMPARISON_SECTION_PATTERN_TEMPLATE.format(level_a=first, level_b=second),
            normalized_text,
            flags=re.DOTALL | re.MULTILINE,
        )
        if match:
            heading = f"TRL {first} เทียบกับ TRL {second}"
            return _clean_source_excerpt(f"{heading}\n{match.group(1).strip()}".strip(), max_chars=2200)
    return None


_extract_level_section = extract_level_section
_extract_comparison_section = extract_comparison_section


def _clean_source_excerpt(text: str, max_chars: int = 1800) -> str:
    lines = [_clean_line(line) for line in text.splitlines()]
    compact_lines = [line for line in lines if line]
    excerpt = "\n".join(compact_lines)
    if len(excerpt) <= max_chars:
        return excerpt
    return excerpt[:max_chars].rsplit("\n", 1)[0].strip()


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


def _build_evidence_answer(level: int, section: str) -> str | None:
    lines = [_clean_line(line) for line in section.splitlines() if _clean_line(line)]
    if not lines:
        return None

    title_line = lines[0]
    description_lines: list[str] = []
    evidence_lines: list[str] = []
    collecting = False
    for line in lines[1:]:
        if line.startswith("ข้อมูลสนับสนุน"):
            collecting = True
            continue
        if collecting and line.startswith("ตัวอย่างผลงาน"):
            break
        if collecting:
            evidence_lines.append(line)
        elif line not in {"คำอธิบาย", "คำอธิบาย:"}:
            description_lines.append(line)

    if not evidence_lines:
        return _build_level_answer(level, section)

    context_text = "\n".join(description_lines[:3])
    evidence_text = "\n".join(evidence_lines[:6])
    return f"{title_line}\n{context_text}\nหลักฐาน/ข้อมูลสนับสนุนที่ควรมี:\n{evidence_text}".strip()


def _build_comparison_answer(level_a: int, level_b: int, comparison_section: str) -> str:
    body = _clean_source_excerpt(comparison_section)
    if level_a > level_b and f"TRL {level_b} เทียบกับ TRL {level_a}" in body:
        body += f"\nหมายเหตุ: คำถามถามในลำดับ TRL {level_a} กับ TRL {level_b}; ข้อมูลอ้างอิงเป็นคู่เดียวกันในลำดับ TRL {level_b} ไป TRL {level_a}."
    return body


def _looks_like_assessment_request(normalized_query: str) -> bool:
    return any(hint in normalized_query for hint in ASSESSMENT_QUERY_HINTS)


def _looks_like_comparison_request(normalized_query: str) -> bool:
    return any(hint in normalized_query for hint in COMPARISON_QUERY_HINTS)


def _looks_like_evidence_request(normalized_query: str) -> bool:
    return any(hint in normalized_query for hint in EVIDENCE_QUERY_HINTS)


def _looks_like_transition_request(normalized_query: str) -> bool:
    return any(hint in normalized_query for hint in TRANSITION_QUERY_HINTS)


def answer_query_from_source(query: str) -> str | None:
    normalized_query = query.strip().lower()
    levels = [int(match) for match in TRL_LEVEL_PATTERN.findall(query)]
    if not levels:
        return None

    if _looks_like_assessment_request(normalized_query):
        return None

    if len(levels) >= 2 and (
        _looks_like_comparison_request(normalized_query) or _looks_like_transition_request(normalized_query)
    ):
        comparison_text = load_registered_source_text(COMPARISON_SOURCE_PATH)
        comparison_section = _extract_comparison_section(levels[0], levels[1], comparison_text)
        if not comparison_section:
            return None
        return _build_comparison_answer(levels[0], levels[1], comparison_section)

    if len(levels) != 1:
        return None

    level = levels[0]
    definition_text = load_authoritative_source_text()
    section = _extract_level_section(level, definition_text)
    if not section:
        return None

    if _looks_like_evidence_request(normalized_query):
        return _build_evidence_answer(level, section)

    if not any(hint in normalized_query for hint in DEFINITION_QUERY_HINTS):
        compact_query = " ".join(normalized_query.split())
        if compact_query not in {f"trl {level}", f"trl{level}"} and "?" not in compact_query:
            return None

    answer = _build_level_answer(level, section)
    if answer and INSUFFICIENT_EVIDENCE_FALLBACK_PHRASE in answer:
        return None
    return answer
