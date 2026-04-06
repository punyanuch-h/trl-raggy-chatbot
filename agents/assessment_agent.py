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
    "trl_1_basic_principles": ("หลักการพื้นฐาน", "องค์ความรู้พื้นฐาน"),
    "trl_1_documented_research": ("เอกสารวิจัย", "รายงานวิจัย", "ตีพิมพ์", "เอกสารอ้างอิง"),
    "trl_2_concept_formulated": ("แนวคิด", "สมมติฐาน", "concept"),
    "trl_2_application_defined": ("ประยุกต์ใช้", "กรณีใช้งาน", "การใช้งาน"),
    "trl_3_proof_of_concept": ("พิสูจน์แนวคิด", "proof of concept", "ผลทดลองเบื้องต้น"),
    "trl_3_analytical_results": ("ผลวิเคราะห์", "บันทึกผลทดสอบ", "ผลทดลอง"),
    "trl_4_lab_validation": ("ห้องปฏิบัติการ", "lab", "ทดสอบต้นแบบ"),
    "trl_4_integrated_components": ("องค์ประกอบทำงานร่วมกัน", "ทำงานร่วมกันได้", "เชื่อมต่อกัน", "มีต้นแบบ", "ต้นแบบระบบ"),
    "trl_5_relevant_environment_test": ("สภาพแวดล้อมที่เกี่ยวข้อง", "relevant environment", "แปลงสาธิต"),
    "trl_5_supporting_performance_data": ("ความปลอดภัย", "สมรรถนะ", "performance"),
    "trl_6_prototype_demonstration": ("สาธิตต้นแบบ", "prototype demonstration"),
    "trl_6_relevant_environment_results": ("ผลการสาธิต", "ผลในสภาพแวดล้อมที่เกี่ยวข้อง"),
    "trl_7_operational_prototype": ("สภาพแวดล้อมปฏิบัติการ", "operational environment"),
    "trl_7_operational_results": ("ผลการใช้งานจริง", "ผลการสาธิตในงานจริง"),
    "trl_8_qualification": ("ผ่านการรับรอง", "qualified", "มาตรฐาน", "gmp", "iso", "ce mark"),
    "trl_8_delivery_readiness": ("พร้อมส่งมอบ", "พร้อมใช้งาน"),
    "trl_9_successful_operations": ("ใช้งานจริง", "successful operations", "ปฏิบัติการได้สำเร็จ"),
    "trl_9_post_deployment_results": ("ติดตามผล", "หลังส่งมอบ", "ประเมินผล"),
}

NEGATION_MARKERS = ("ยังไม่ได้", "ยังไม่", "ไม่มี", "ไม่เคย", "ไม่")
UNCERTAIN_MARKERS = ("ยังไม่แน่ใจ", "ไม่แน่ใจ", "อาจ", "น่าจะ", "ยังไม่ชัดเจน")
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
TEST_MARKERS = ("ทดสอบ", "ทดลอง", "ตรวจสอบ", "validate", "validation")
PERFORMANCE_MARKERS = (
    "ประสิทธิภาพ",
    "สมรรถนะ",
    "ทำงานได้",
    "ผ่านเกณฑ์",
    "ตามเกณฑ์",
)
MEASUREMENT_MARKERS = (
    "วัดผล",
    "วัดค่า",
    "บันทึกข้อมูล",
    "บันทึกผล",
    "เก็บข้อมูล",
    "อย่างเป็นระบบ",
)
INTEGRATION_NEGATION_MARKERS = (
    "ยังไม่ได้ประกอบ",
    "ยังไม่ประกอบ",
    "ยังไม่เชื่อมต่อ",
    "ยังทำงานร่วมกันไม่ได้",
    "ยังไม่สามารถทำงานร่วมกัน",
)


def _split_segments(text: str) -> list[str]:
    return [
        segment.strip()
        for segment in re.split(r"[,.!?\n]|แต่|และ", text.lower())
        if segment.strip()
    ]


def _contains_any(text: str, markers: tuple[str, ...]) -> bool:
    return any(marker in text for marker in markers)


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


def _apply_inferred_evidence(text: str, segments: list[str], evidence: dict[str, EvidenceSignal]) -> None:
    normalized_text = text.lower()
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
    segments = _split_segments(text)
    evidence: dict[str, EvidenceSignal] = {}
    uncertain_evidence: list[str] = []
    conflicts: list[str] = []

    for evidence_id, patterns in SUPPORTED_RULE_PATTERNS.items():
        statuses: list[str] = []
        matched_phrases: list[str] = []
        for segment in segments:
            for pattern in patterns:
                if pattern in segment:
                    matched_phrases.append(segment)
                    if any(marker in segment for marker in UNCERTAIN_MARKERS):
                        statuses.append("uncertain")
                    elif any(marker in segment for marker in NEGATION_MARKERS):
                        statuses.append("missing")
                    else:
                        statuses.append("supported")
                    break

        if not statuses:
            continue

        unique_statuses = set(statuses)
        if "supported" in unique_statuses and ("missing" in unique_statuses or "uncertain" in unique_statuses):
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
            matched_text=" | ".join(matched_phrases),
        )

    _apply_inferred_evidence(text, segments, evidence)

    candidate_level_hint = max((RULE_LEVELS[evidence_id] for evidence_id, signal in evidence.items() if signal.status in {"supported", "conflicting", "uncertain"}), default=1)
    return AssessmentInterpretation(
        evidence=evidence,
        candidate_level_hint=candidate_level_hint,
        uncertain_evidence=uncertain_evidence,
        conflicts=conflicts,
        final_level_proposed=None,
    )
