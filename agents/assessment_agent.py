from __future__ import annotations

import re

from pydantic import BaseModel


class EvidenceSignal(BaseModel):
    status: str
    matched_text: str | None = None
    notes: str | None = None


class AssessmentInterpretation(BaseModel):
    evidence: dict[str, EvidenceSignal]
    candidate_level_hint: int
    uncertain_evidence: list[str]
    conflicts: list[str]
    final_level_proposed: int | None = None


SUPPORTED_RULE_PATTERNS: dict[str, tuple[str, ...]] = {
    "trl_1_basic_principles": (
        "ศึกษาหลักการ",
        "หลักการทางคณิตศาสตร์",
        "หลักการพื้นฐาน",
        "ทฤษฎีพื้นฐาน",
        "องค์ความรู้พื้นฐาน",
        "basic principles",
        "foundational principles",
        "fundamental principles",
    ),
    "trl_1_documented_research": (
        "ทบทวนงานวิจัย",
        "วรรณกรรมที่เกี่ยวข้อง",
        "เอกสารวิจัย",
        "รายงานวิจัย",
        "ตีพิมพ์",
        "เอกสารอ้างอิง",
        "paper",
        "literature review",
        "published research",
        "documented research",
    ),
    "trl_2_concept_formulated": (
        "แนวคิด",
        "สมมติฐาน",
        "concept",
        "กรอบแนวคิด",
        "hypothesis",
        "technology concept",
    ),
    "trl_2_application_defined": (
        "แนวทางพัฒนาเทคโนโลยี",
        "แนวทางประยุกต์ใช้",
        "ประยุกต์ใช้",
        "กรณีใช้งาน",
        "การใช้งาน",
        "use case",
        "application defined",
        "target application",
        "intended application",
    ),
    "trl_3_proof_of_concept": (
        "ทดลองเบื้องต้น",
        "พิสูจน์แนวคิด",
        "proof of concept",
        "ทดสอบสมมติฐาน",
        "ผลทดลองเบื้องต้น",
        "preliminary experiment",
        "initial experiment",
        "tested",
    ),
    "trl_3_analytical_results": (
        "ผลทดลอง",
        "ผลวิเคราะห์",
        "บันทึกผลทดสอบ",
        "analytical results",
        "test results",
        "recorded results",
        "results",
    ),
    "trl_4_lab_validation": (
        "ห้องปฏิบัติการ",
        "lab",
        "laboratory",
        "tested the prototype",
        "prototype tested",
        "validated in the lab",
        "lab validation",
        "ทดสอบต้นแบบ",
    ),
    "trl_4_integrated_components": (
        "องค์ประกอบทำงานร่วมกัน",
        "ทำงานร่วมกันได้",
        "เชื่อมต่อกัน",
        "มีต้นแบบ",
        "ต้นแบบระบบ",
        "integrated components",
        "components work together",
        "integrated prototype",
    ),
    "trl_5_relevant_environment_test": (
        "สภาพแวดล้อมที่เกี่ยวข้อง",
        "relevant environment",
        "tested in a relevant environment",
        "prototype tested in relevant environment",
        "แปลงสาธิต",
    ),
    "trl_5_supporting_performance_data": (
        "ความปลอดภัย",
        "สมรรถนะ",
        "performance",
        "safety data",
        "performance data",
        "validated",
    ),
    "trl_6_prototype_demonstration": (
        "สาธิตต้นแบบ",
        "prototype demonstration",
        "demonstrated prototype",
        "prototype demonstrated",
        "system demonstration",
    ),
    "trl_6_relevant_environment_results": (
        "ผลการสาธิต",
        "ผลในสภาพแวดล้อมที่เกี่ยวข้อง",
        "demonstration results",
        "results in relevant environment",
    ),
    "trl_7_operational_prototype": (
        "สภาพแวดล้อมปฏิบัติการ",
        "operational environment",
        "tested in operation",
        "tested in real use",
    ),
    "trl_7_operational_results": (
        "ผลการใช้งานจริง",
        "ผลการสาธิตในงานจริง",
        "operational results",
        "real-world results",
        "field results",
    ),
    "trl_8_qualification": (
        "ผ่านการรับรอง",
        "qualified",
        "มาตรฐาน",
        "gmp",
        "iso",
        "ce mark",
        "certified",
    ),
    "trl_8_delivery_readiness": (
        "พร้อมส่งมอบ",
        "พร้อมใช้งาน",
        "ready for delivery",
        "ready for deployment",
        "delivery readiness",
    ),
    "trl_9_successful_operations": (
        "ใช้งานจริง",
        "successful operations",
        "ปฏิบัติการได้สำเร็จ",
        "successful real-world operation",
        "in production",
    ),
    "trl_9_post_deployment_results": (
        "ติดตามผล",
        "หลังส่งมอบ",
        "ประเมินผล",
        "post-deployment",
        "post deployment",
        "follow-up results",
    ),
}

MISSING_RULE_PATTERNS: dict[str, tuple[str, ...]] = {
    "trl_2_application_defined": (
        "ยังไม่มีการกำหนดแนวทางพัฒนาเทคโนโลยี",
        "ยังไม่ได้กำหนดแนวทางพัฒนาเทคโนโลยี",
        "ไม่มีการกำหนดแนวทางพัฒนาเทคโนโลยี",
        "ยังไม่มีแนวทางประยุกต์ใช้",
        "not yet defined",
        "no use case yet",
        "application not defined",
    ),
    "trl_3_proof_of_concept": (
        "ยังไม่มีการทดลอง",
        "ยังไม่ได้ทดลอง",
        "ไม่มีการทดลอง",
        "ไม่มีผลทดลอง",
        "ยังไม่มีการทดสอบ",
        "ยังไม่ได้ทดสอบ",
        "ไม่มีการทดสอบ",
        "หรือการทดลองใดๆ",
        "not yet tested",
        "not tested yet",
        "no proof of concept yet",
        "no prototype test yet",
    ),
    "trl_3_analytical_results": (
        "ยังไม่มีการทดลอง",
        "ยังไม่ได้ทดลอง",
        "ไม่มีการทดลอง",
        "ยังไม่มีการทดสอบ",
        "ยังไม่ได้ทดสอบ",
        "ไม่มีการทดสอบ",
        "ยังไม่มีผลทดลอง",
        "ยังไม่มีผลวิเคราะห์",
        "ไม่มีผลทดสอบ",
        "ยังไม่มีผลทดสอบ",
        "หรือการทดลองใดๆ",
        "no test results",
        "no analytical results",
        "results not available yet",
        "not sure about the results",
    ),
}

NEGATION_MARKERS = (
    "ยังไม่ได้",
    "ยังไม่",
    "ไม่มี",
    "ไม่เคย",
    "ไม่ได้",
    "not yet",
    "no ",
    "without",
    "never",
)
UNCERTAIN_MARKERS = (
    "ยังไม่แน่ใจ",
    "ไม่แน่ใจ",
    "อาจ",
    "น่าจะ",
    "ยังไม่ชัดเจน",
    "possibly",
    "maybe",
    "may have",
    "not sure",
    "unclear",
)
RULE_LEVELS = {
    "trl_1_basic_principles": 1,
    "trl_1_documented_research": 1,
    "trl_2_concept_formulated": 2,
    "trl_2_application_defined": 2,
    "trl_3_proof_of_concept": 3,
    "trl_3_analytical_results": 3,
    "trl_4_lab_validation": 4,
    "trl_4_integrated_components": 4,
    "trl_5_relevant_environment_test": 5,
    "trl_5_supporting_performance_data": 5,
    "trl_6_prototype_demonstration": 6,
    "trl_6_relevant_environment_results": 6,
    "trl_7_operational_prototype": 7,
    "trl_7_operational_results": 7,
    "trl_8_qualification": 8,
    "trl_8_delivery_readiness": 8,
    "trl_9_successful_operations": 9,
    "trl_9_post_deployment_results": 9,
}
PROTOTYPE_MARKERS = ("ต้นแบบ", "prototype", "model")
LAB_MARKERS = ("ห้องปฏิบัติการ", "lab", "laboratory")
TEST_MARKERS = ("ทดสอบ", "ทดลอง", "ตรวจสอบ", "validate", "validation", "tested")
PERFORMANCE_MARKERS = (
    "ประสิทธิภาพ",
    "สมรรถนะ",
    "ทำงานได้",
    "ผ่านเกณฑ์",
    "ตามเกณฑ์",
    "performance",
    "safety",
)
MEASUREMENT_MARKERS = (
    "วัดผล",
    "วัดค่า",
    "บันทึกข้อมูล",
    "บันทึกผล",
    "เก็บข้อมูล",
    "อย่างเป็นระบบ",
    "measured",
    "recorded",
)
INTEGRATION_NEGATION_MARKERS = (
    "ยังไม่ได้ประกอบ",
    "ยังไม่ประกอบ",
    "ยังไม่เชื่อมต่อ",
    "ยังทำงานร่วมกันไม่ได้",
    "still not integrated",
    "not integrated yet",
)
CLAUSE_BOUNDARY_PATTERN = re.compile(r"[.!?\n;]|\s*(?:แต่|ทว่า|อย่างไรก็ตาม|however|but)\s*")
SPACE_PATTERN = re.compile(r"\s+")


def _normalize_text(text: str) -> str:
    return SPACE_PATTERN.sub(" ", text.strip().lower())


def _split_segments(text: str) -> list[str]:
    normalized = _normalize_text(text)
    return [segment.strip() for segment in CLAUSE_BOUNDARY_PATTERN.split(normalized) if segment.strip()]


def _contains_any(text: str, markers: tuple[str, ...]) -> bool:
    return any(marker in text for marker in markers)


def _collect_marker_spans(window: str, markers: tuple[str, ...]) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    for marker in markers:
        search_start = 0
        while True:
            marker_index = window.find(marker, search_start)
            if marker_index == -1:
                break
            spans.append((marker_index, marker_index + len(marker)))
            search_start = marker_index + 1
    return spans


def _nearest_marker_distance(
    window: str,
    pattern: str,
    markers: tuple[str, ...],
    *,
    before_only: bool = False,
    exclude_spans: list[tuple[int, int]] | None = None,
) -> int | None:
    pattern_index = window.find(pattern)
    if pattern_index == -1:
        return None

    nearest_distance: int | None = None
    for marker in markers:
        search_start = 0
        while True:
            marker_index = window.find(marker, search_start)
            if marker_index == -1:
                break
            marker_end = marker_index + len(marker)
            if exclude_spans and any(marker_index < span_end and marker_end > span_start for span_start, span_end in exclude_spans):
                search_start = marker_index + 1
                continue
            if before_only and marker_index > pattern_index:
                search_start = marker_index + 1
                continue

            if before_only:
                distance = pattern_index - marker_end
            else:
                distance = min(abs(pattern_index - marker_index), abs((pattern_index + len(pattern)) - marker_end))
            if distance <= 24:
                nearest_distance = distance if nearest_distance is None else min(nearest_distance, distance)
            search_start = marker_index + 1
    return nearest_distance


def _extract_context_window(text: str, pattern: str, start_index: int) -> str:
    left_boundary = 0
    right_boundary = len(text)
    for match in CLAUSE_BOUNDARY_PATTERN.finditer(text):
        if match.end() <= start_index:
            left_boundary = match.end()
        elif match.start() >= start_index + len(pattern):
            right_boundary = match.start()
            break
    return text[left_boundary:right_boundary].strip()


def _classify_match_status(window: str, pattern: str) -> str:
    uncertainty_spans = _collect_marker_spans(window, UNCERTAIN_MARKERS)
    negation_distance = _nearest_marker_distance(
        window,
        pattern,
        NEGATION_MARKERS,
        before_only=True,
        exclude_spans=uncertainty_spans,
    )
    uncertainty_distance = _nearest_marker_distance(window, pattern, UNCERTAIN_MARKERS)

    if uncertainty_distance is not None and (negation_distance is None or uncertainty_distance <= negation_distance):
        return "uncertain"
    if negation_distance is not None:
        return "missing"
    return "supported"


def _upsert_supported_evidence(
    evidence: dict[str, EvidenceSignal],
    evidence_id: str,
    matched_segments: list[str],
    notes: str,
) -> None:
    current = evidence.get(evidence_id)
    if current and current.status in {"missing", "conflicting"}:
        return

    evidence[evidence_id] = EvidenceSignal(
        status="supported",
        matched_text=" | ".join(dict.fromkeys(matched_segments)) or None,
        notes=notes,
    )


def _upsert_missing_evidence(
    evidence: dict[str, EvidenceSignal],
    evidence_id: str,
    matched_segments: list[str],
    notes: str,
) -> None:
    current = evidence.get(evidence_id)
    matched_text = " | ".join(dict.fromkeys(matched_segments)) or None

    if current and current.status == "supported":
        evidence[evidence_id] = EvidenceSignal(
            status="conflicting",
            matched_text=" | ".join(dict.fromkeys([item for item in (current.matched_text, matched_text) if item])) or None,
            notes=notes,
        )
        return

    if current and current.status in {"missing", "conflicting"}:
        return

    evidence[evidence_id] = EvidenceSignal(
        status="missing",
        matched_text=matched_text,
        notes=notes,
    )


def _apply_explicit_missing_evidence(text: str, evidence: dict[str, EvidenceSignal]) -> None:
    normalized_text = _normalize_text(text)

    for evidence_id, patterns in MISSING_RULE_PATTERNS.items():
        matched_segments: list[str] = []
        for pattern in patterns:
            start = 0
            while True:
                match_index = normalized_text.find(pattern, start)
                if match_index == -1:
                    break
                context_window = _extract_context_window(normalized_text, pattern, match_index)
                if context_window:
                    matched_segments.append(context_window)
                start = match_index + len(pattern)

        if matched_segments:
            _upsert_missing_evidence(
                evidence,
                evidence_id,
                matched_segments,
                "Explicitly marked missing by the user's assessment description.",
            )


def _apply_inferred_evidence(text: str, segments: list[str], evidence: dict[str, EvidenceSignal]) -> None:
    normalized_text = _normalize_text(text)
    has_prototype = _contains_any(normalized_text, PROTOTYPE_MARKERS)
    has_lab_context = _contains_any(normalized_text, LAB_MARKERS)
    has_test_activity = _contains_any(normalized_text, TEST_MARKERS)
    has_performance_signal = _contains_any(normalized_text, PERFORMANCE_MARKERS)
    has_measurement_signal = _contains_any(normalized_text, MEASUREMENT_MARKERS)
    has_explicit_integration_negation = _contains_any(normalized_text, INTEGRATION_NEGATION_MARKERS)

    inferred_segments = [
        segment
        for segment in segments
        if (
            _contains_any(segment, PROTOTYPE_MARKERS)
            or _contains_any(segment, LAB_MARKERS)
            or _contains_any(segment, TEST_MARKERS)
            or _contains_any(segment, PERFORMANCE_MARKERS)
            or _contains_any(segment, MEASUREMENT_MARKERS)
        )
    ]

    if has_prototype and has_lab_context and has_test_activity:
        _upsert_supported_evidence(
            evidence,
            "trl_4_lab_validation",
            inferred_segments,
            "Inferred from prototype testing activity in a laboratory context.",
        )

    if has_explicit_integration_negation:
        return

    if has_prototype and has_lab_context and has_test_activity and (has_performance_signal or has_measurement_signal):
        _upsert_supported_evidence(
            evidence,
            "trl_4_integrated_components",
            inferred_segments,
            "Inferred from a lab-tested prototype showing integrated performance or measured results.",
        )


def interpret_assessment_input(text: str) -> AssessmentInterpretation:
    normalized_text = _normalize_text(text)
    segments = _split_segments(text)
    evidence: dict[str, EvidenceSignal] = {}
    uncertain_evidence: list[str] = []
    conflicts: list[str] = []

    for evidence_id, patterns in SUPPORTED_RULE_PATTERNS.items():
        statuses: list[str] = []
        matched_phrases: list[str] = []
        seen_contexts: set[str] = set()

        for pattern in patterns:
            start = 0
            while True:
                match_index = normalized_text.find(pattern, start)
                if match_index == -1:
                    break
                context_window = _extract_context_window(normalized_text, pattern, match_index)
                if context_window:
                    matched_phrases.append(context_window)
                    if context_window not in seen_contexts:
                        statuses.append(_classify_match_status(context_window, pattern))
                        seen_contexts.add(context_window)
                start = match_index + len(pattern)

        if not statuses:
            continue

        unique_statuses = set(statuses)
        if "supported" in unique_statuses and ("missing" in unique_statuses or "uncertain" in unique_statuses):
            status = "conflicting"
            conflicts.append(evidence_id)
        elif "uncertain" in unique_statuses and "missing" in unique_statuses:
            status = "conflicting"
            conflicts.append(evidence_id)
        elif "uncertain" in unique_statuses:
            status = "uncertain"
            uncertain_evidence.append(evidence_id)
        elif "missing" in unique_statuses:
            status = "missing"
        else:
            status = "supported"

        evidence[evidence_id] = EvidenceSignal(
            status=status,
            matched_text=" | ".join(dict.fromkeys(matched_phrases)) or None,
        )

    _apply_explicit_missing_evidence(text, evidence)
    _apply_inferred_evidence(text, segments, evidence)

    supported_like_levels = [
        RULE_LEVELS[evidence_id]
        for evidence_id, signal in evidence.items()
        if signal.status in {"supported", "conflicting"}
    ]
    uncertain_levels = [
        RULE_LEVELS[evidence_id]
        for evidence_id, signal in evidence.items()
        if signal.status == "uncertain"
    ]
    candidate_level_hint = max(supported_like_levels or uncertain_levels or [1])
    return AssessmentInterpretation(
        evidence=evidence,
        candidate_level_hint=candidate_level_hint,
        uncertain_evidence=uncertain_evidence,
        conflicts=conflicts,
        final_level_proposed=None,
    )
