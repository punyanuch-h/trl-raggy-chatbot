from typing import Optional


def format_answer_markdown(answer_text: str, title: Optional[str] = None) -> str:
    """Wrap raw answer text in a predictable markdown-safe structure."""
    clean_answer = answer_text.strip()
    heading = title or "คำตอบ TRL"
    return f"## {heading}\n\n{clean_answer}"
