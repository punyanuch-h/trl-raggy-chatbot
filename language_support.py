from __future__ import annotations

import re


SUPPORTED_RESPONSE_LANGUAGES = {"th", "en"}
THAI_CHAR_PATTERN = re.compile(r"[\u0E00-\u0E7F]")
LATIN_WORD_PATTERN = re.compile(r"[A-Za-z]+")


LEVEL_SUMMARIES_EN: dict[int, str] = {
    1: "Basic principles have been observed and documented in research or reference material.",
    2: "A technology concept and likely application have been formulated, but practical validation has not started yet.",
    3: "Proof-of-concept work has started with early analytical or experimental results.",
    4: "Components or breadboards have been integrated and validated in a laboratory environment.",
    5: "Integrated components have been tested in a relevant environment closer to real use.",
    6: "A clearer prototype or system model has been demonstrated in a relevant environment.",
    7: "A prototype has been demonstrated in an operational environment.",
    8: "The actual system is completed, qualified, and ready for delivery or deployment.",
    9: "The actual system has been proven through successful real-world operations.",
}

EVIDENCE_DESCRIPTIONS_EN: dict[str, str] = {
    "trl_1_basic_principles": "Basic principles or foundational knowledge relevant to the technology are clearly identified.",
    "trl_1_documented_research": "Published research, references, or documented study results support the foundational work.",
    "trl_2_concept_formulated": "The technology concept or hypothesis has been clearly formulated.",
    "trl_2_application_defined": "A target application, use case, or development direction has been defined.",
    "trl_3_proof_of_concept": "There is early proof-of-concept or preliminary experimental validation.",
    "trl_3_analytical_results": "Analytical results or recorded test results support the concept.",
    "trl_4_lab_validation": "The prototype or breadboard has been validated in a laboratory environment.",
    "trl_4_integrated_components": "Integrated components have been shown to work together.",
    "trl_5_relevant_environment_test": "The integrated prototype has been tested in a relevant environment.",
    "trl_5_supporting_performance_data": "Performance or safety data support the relevant-environment testing results.",
    "trl_6_prototype_demonstration": "A clearer prototype or system model has been demonstrated.",
    "trl_6_relevant_environment_results": "Demonstration results in a relevant environment support the prototype.",
    "trl_7_operational_prototype": "A prototype has been demonstrated in an operational environment.",
    "trl_7_operational_results": "Operational or real-use results support the prototype demonstration.",
    "trl_8_qualification": "The actual system has been qualified through testing, standards, or certification evidence.",
    "trl_8_delivery_readiness": "There is evidence that the system is ready for delivery or deployment.",
    "trl_9_successful_operations": "The actual system is already operating successfully in real use.",
    "trl_9_post_deployment_results": "Post-deployment or post-delivery results confirm successful operation.",
}

FOLLOW_UP_QUESTION_EN: dict[str, str] = {
    "trl_1_basic_principles": "What foundational scientific or technical principles already support this work?",
    "trl_1_documented_research": "What published research, references, or documented studies support this work?",
    "trl_2_concept_formulated": "How has the technology concept or hypothesis been clearly formulated?",
    "trl_2_application_defined": "What application, use case, or development direction has already been defined?",
    "trl_3_proof_of_concept": "What proof-of-concept or preliminary experiment has already been completed?",
    "trl_3_analytical_results": "What analytical results or recorded test results support the concept?",
    "trl_4_lab_validation": "What laboratory validation has been completed for the prototype or breadboard?",
    "trl_4_integrated_components": "What evidence shows that the integrated components work together?",
    "trl_5_relevant_environment_test": "What testing has been completed in a relevant environment?",
    "trl_5_supporting_performance_data": "What performance or safety data support those relevant-environment tests?",
    "trl_6_prototype_demonstration": "What prototype or system demonstration has already been completed?",
    "trl_6_relevant_environment_results": "What relevant-environment results support that demonstration?",
    "trl_7_operational_prototype": "What prototype testing has been completed in an operational environment?",
    "trl_7_operational_results": "What real-use or operational results support that prototype?",
    "trl_8_qualification": "What evidence shows that the actual system has been qualified or certified?",
    "trl_8_delivery_readiness": "What evidence shows that the system is ready for delivery or deployment?",
    "trl_9_successful_operations": "What evidence shows successful real-world operation?",
    "trl_9_post_deployment_results": "What post-deployment results or follow-up reports confirm success?",
}


def detect_language(text: str) -> str:
    has_thai = bool(THAI_CHAR_PATTERN.search(text))
    has_latin = bool(LATIN_WORD_PATTERN.search(text))
    if has_thai and has_latin:
        return "mixed"
    if has_thai:
        return "th"
    return "en"


def primary_language(text: str) -> str:
    detected = detect_language(text)
    if detected != "mixed":
        return detected

    thai_count = len(THAI_CHAR_PATTERN.findall(text))
    latin_count = len(LATIN_WORD_PATTERN.findall(text))
    return "th" if thai_count >= latin_count else "en"


def normalize_response_language(language: str | None) -> str | None:
    if language is None:
        return None
    normalized = language.strip().lower()
    return normalized if normalized in SUPPORTED_RESPONSE_LANGUAGES else None


def resolve_response_language(query: str, requested_language: str | None = None) -> str:
    return normalize_response_language(requested_language) or primary_language(query)


def choose_text(thai_text: str, english_text: str, language: str) -> str:
    return english_text if language == "en" else thai_text


def join_list(items: list[str], language: str) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        connector = " and " if language == "en" else " และ "
        return f"{items[0]}{connector}{items[1]}"
    connector = "and" if language == "en" else "และ"
    return f"{', '.join(items[:-1])}, {connector} {items[-1]}" if language == "en" else f"{', '.join(items[:-1])} และ {items[-1]}"


def evidence_description(evidence_id: str, description_th: str, language: str) -> str:
    if language == "en":
        return EVIDENCE_DESCRIPTIONS_EN.get(evidence_id, description_th)
    return description_th


def localize_missing_evidence(items: list[dict[str, str]], language: str) -> list[dict[str, str]]:
    localized: list[dict[str, str]] = []
    for item in items:
        description_th = item.get("description_th", "")
        localized.append(
            {
                **item,
                "description": evidence_description(item.get("id", ""), description_th, language),
            }
        )
    return localized
