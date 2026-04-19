# Sprint 16 Plan: Explainable Assessment and Source Citation

## Sprint Details
- **Sprint Goal**: ทำให้ผลประเมิน TRL และคำตอบแบบ QA ตรวจสอบย้อนหลังได้ อธิบายเหตุผลได้ชัดเจน และช่วยผู้ใช้เข้าใจว่าได้ระดับใดเพราะอะไรและต้องมีอะไรต่อ
- **Duration**: 2 Weeks
- **Methodology**: Agile & Test-Driven Development (TDD)
- **Standard**: ISO/IEC 29110 Basic Profile

## Problem Statement
แม้ระบบปัจจุบันจะมี assessment response พื้นฐานที่ดี แต่ยังสามารถเพิ่ม explainability และ source traceability ได้อีกมาก ผู้ใช้ยังอาจไม่เห็นภาพชัดว่าหลักฐานใดรองรับระดับปัจจุบัน หลักฐานใดยังไม่พอ และระดับที่สูงกว่ายังไม่ผ่านเพราะอะไร

Sprint นี้จึงเน้นการขยาย response contract ให้มีโครงสร้าง explainability ชัดเจน และเพิ่ม `sources` หรือ citation ที่ตรวจสอบย้อนกลับได้ทั้ง QA และ assessment

## Target User Scenarios

### Scenario A: Explainable Assessment Result
Input:

```json
{
  "query": "ช่วยประเมิน TRL ตอนนี้มีต้นแบบและทดสอบใน relevant environment แล้ว"
}
```

Expected behavior:
- Response อยู่ใน `assessment` mode
- มี `supported_evidence`
- มี `missing_evidence` หรือ `next_level_requirements`
- มี `decision_explanation` ที่อธิบายอ่านง่าย

### Scenario B: Citation-Aware QA Response
Input:

```json
{
  "query": "TRL 8 ต้องมีหลักฐานอะไรบ้าง"
}
```

Expected behavior:
- Response อยู่ใน `qa` mode
- มี `sources`
- ระบุ source file และ section หรือ level ที่เกี่ยวข้องได้

### Scenario C: Domain-Specific Assessment Hint
Input:

```json
{
  "query": "Assess my software project. We have deployed a working prototype and monitored real usage.",
  "domain": "software"
}
```

Expected behavior:
- Assessment explanation ใช้ภาษาที่สอดคล้องกับ domain `software`
- Follow-up หรือ next-level recommendation สื่อถึงหลักฐานที่เกี่ยวกับ software มากขึ้น

## Definition of Done (DoD)
งานใน Sprint 16 จะถือว่าเสร็จเมื่อ:

1. Assessment response contract รองรับ `supported_evidence`, `uncertain_evidence`, `conflicting_evidence`, `next_level_requirements`, และ `decision_explanation`
2. QA และ assessment response มี `sources` หรือ citation model ที่สอดคล้องกับ source ที่ถูกใช้จริง
3. Response narrative อธิบายได้ว่าระบบตัดสินใจอย่างไรและระดับถัดไปต้องมีอะไร
4. Domain-specific request มีผลต่อ wording หรือ next-step recommendation อย่างน้อยในระดับพื้นฐาน
5. Citation และ explainability verification tests ถูกเพิ่มและผ่าน
6. Bilingual behavior จาก Sprint 15 ยังไม่ regress

---

## Sprint Backlog

### Ticket 16.1: Explainable Assessment Response Contract (5 Story Points)
- **Description**: ขยาย response contract ของ assessment ให้รองรับ explainability แบบเป็นโครงสร้าง
- **Implementation Scope**:
  - เพิ่ม `supported_evidence`
  - เพิ่ม `uncertain_evidence`
  - เพิ่ม `conflicting_evidence`
  - เพิ่ม `next_level_requirements`
  - เพิ่ม `decision_explanation`
- **Acceptance Criteria (TDD)**:
  - Assessment response มี field ใหม่ครบตาม contract
  - หลักฐานแต่ละประเภทถูกจัดกลุ่มอย่างสอดคล้อง
  - `decision_explanation` อ่านง่ายและไม่ยาวเกินจำเป็น
  - Frontend-safe JSON shape ถูกทดสอบ

### Ticket 16.2: Source Citation for QA and Assessment (5 Story Points)
- **Description**: เพิ่ม `sources` ใน API response เพื่อระบุ source file และ section หรือ level ที่ใช้อ้างอิง
- **Implementation Scope**:
  - สร้าง citation model สำหรับ QA และ assessment
  - รองรับ source file, section, และ level reference
  - เก็บ traceability เฉพาะที่ไม่ขัดกับ privacy design
- **Acceptance Criteria (TDD)**:
  - QA definition answers มี `sources`
  - QA comparison answers มี `sources`
  - Assessment response สามารถอ้างถึง rule/source ที่เกี่ยวข้อง
  - Citation ไม่อ้างถึง source ที่ไม่ถูกใช้จริง

### Ticket 16.3: Assessment Decision Narrative Upgrade (5 Story Points)
- **Description**: ปรับ logic การสรุปผล assessment ให้เน้นเหตุผลเชิงตัดสินใจและ next-step recommendation
- **Implementation Scope**:
  - สร้าง summary ที่อธิบายว่าหลักฐานใดรองรับระดับปัจจุบัน
  - อธิบายว่าทำไมระดับที่สูงกว่ายังไม่ผ่าน
  - สร้าง next-level checklist ที่ผูกกับระดับถัดไป
  - รักษา bilingual support จาก Sprint 15
- **Acceptance Criteria (TDD)**:
  - ผู้ใช้เห็นได้ชัดว่าเหตุผลของ matched level คืออะไร
  - Missing evidence ถูกแปลงเป็น next-step ได้
  - Response ไม่สับสนระหว่าง “ไม่มีข้อมูล” กับ “มีข้อมูลที่ขัดแย้ง”
  - Thai และ English response quality ถูกทดสอบ

### Ticket 16.4: Domain-Specific Response Refinement (4 Story Points)
- **Description**: เริ่มใช้ข้อมูล domain notes ให้มากขึ้นในการสร้างคำถาม follow-up และคำแนะนำ
- **Implementation Scope**:
  - เพิ่ม request field `domain` เช่น `software`, `medical_device`, `biotech`, `agriculture`
  - ถ้า domain ไม่ชัดเจน ระบบสามารถถามเพิ่มได้
  - ปรับ evidence examples และ next-level recommendations ตาม domain
- **Acceptance Criteria (TDD)**:
  - Domain-specific request ได้คำอธิบายที่ตรงบริบทมากขึ้น
  - Follow-up questions เปลี่ยนตาม domain
  - ถ้าไม่ระบุ domain ระบบยังทำงานได้โดยใช้ generic behavior

### Ticket 16.5: Citation and Explainability Verification Suite (5 Story Points)
- **Description**: เพิ่ม test cases และ report criteria สำหรับ citation correctness และ explanation quality
- **Implementation Scope**:
  - เพิ่ม evaluation cases สำหรับ source citation
  - เพิ่ม assertions กัน regression เรื่อง explanation fields
  - เพิ่มตัวอย่าง response ใช้ใน test report และ user manual
- **Acceptance Criteria (TDD)**:
  - Citation tests ตรวจได้ว่า source สอดคล้องกับ answer
  - Explanation tests ตรวจได้ว่า response มีเหตุผลที่ชัดเจน
  - Sprint 15 bilingual regression ยังผ่าน

---

## Expected Final Behavior
ตัวอย่าง response ที่คาดหวัง:

```json
{
  "mode": "assessment",
  "language": "th",
  "assessment_result": {
    "matched_level": 5,
    "decision_status": "completed",
    "supported_evidence": [
      "มีต้นแบบที่ผ่านการทดสอบใน relevant environment"
    ],
    "uncertain_evidence": [],
    "conflicting_evidence": [],
    "next_level_requirements": [
      "มีผลการสาธิตต้นแบบในสภาพแวดล้อมที่ใกล้เคียงการใช้งานจริงมากขึ้น"
    ],
    "decision_explanation": "หลักฐานปัจจุบันรองรับ TRL 5 แต่ยังไม่เพียงพอสำหรับ TRL 6"
  },
  "sources": [
    {
      "source_file": "source/Technology_Readiness_Level_Definition.txt",
      "section": "TRL 5"
    }
  ]
}
```

---

## Risks and Notes
- Citation model ที่ละเอียดเกินไปอาจเพิ่มความซับซ้อนของ runtime และ tests
- ต้องระวังไม่ให้ `sources` กลายเป็นข้อมูลที่อ้างเกินกว่าที่ระบบใช้จริง
- Explanation ที่ยาวเกินไปจะทำให้ response อ่านยากและยากต่อ frontend rendering
- Domain-specific wording ควรเริ่มจากระดับที่ปลอดภัยก่อน ไม่ควร overfit กับ domain ใด domain หนึ่ง

## Resource Mapping
- **Total Sprint Effort**: 24 Story Points
- **Primary Source Code**: `assessment/conversation.py`, `assessment/evaluator.py`, `assessment/response_templates.py`, `response_formatter.py`, `source_qa.py`, `main.py`
- **Primary Tests**: `tests/test_conversational_assessment.py`, `tests/test_trl_evaluator.py`, `tests/test_api.py`, `tests/test_source_qa.py`, citation/explainability test sets ใหม่
- **Documentation**: PM, SI design docs, test cases, test reports, user/developer docs

## Sprint Success Summary
Sprint 16 จะสำเร็จเมื่อ Raggy Bot สามารถอธิบายผลการประเมินได้อย่างเป็นระบบมากขึ้น และคำตอบทั้งแบบ QA และ assessment มี citation หรือ traceability ที่ตรวจสอบย้อนกลับได้จริง ทำให้ระบบมีความน่าเชื่อถือและเหมาะกับงานวิจัยหรือการประเมินมากขึ้น

---
**Plan Status**: Ready for Sprint 16 backlog grooming and implementation.
