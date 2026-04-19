# Sprint 15 Plan: Bilingual TRL QA and Assessment

## Sprint Details
- **Sprint Goal**: ทำให้ Raggy Bot รองรับ input/output ทั้งภาษาไทยและภาษาอังกฤษในระดับ contract, routing, QA, และ assessment โดยยังคง deterministic assessment behavior เป็นแกนหลัก
- **Duration**: 2 Weeks
- **Methodology**: Agile & Test-Driven Development (TDD)
- **Standard**: ISO/IEC 29110 Basic Profile

## Problem Statement
ปัจจุบันระบบถูกออกแบบแบบ Thai-first และแม้จะตอบภาษาอื่นได้บางกรณี แต่ยังไม่ใช่ capability ระดับระบบ ทำให้ English queries อาจถูก route ผิด fallback เกินจำเป็น หรือได้ response template ที่ไม่สอดคล้อง ขณะเดียวกัน rule base และ assessment patterns ยังไม่ครบสำหรับ English evidence language

Sprint นี้จึงมีเป้าหมายเพื่อยกระดับ bilingual support ให้ครอบคลุมตั้งแต่ request contract ไปจนถึง QA และ rule-based assessment จริง

## Target User Scenarios

### Scenario A: Thai Definition QA
Input:

```json
{
  "query": "TRL 4 คืออะไร"
}
```

Expected behavior:
- Route ไปที่ `qa`
- ตอบเป็นภาษาไทย
- Response ระบุ `language` เป็น `th`
- ไม่หลุด fallback โดยไม่จำเป็น

### Scenario B: English Definition QA
Input:

```json
{
  "query": "What is TRL 4?"
}
```

Expected behavior:
- Route ไปที่ `qa`
- ตอบเป็นภาษาอังกฤษ
- Response ระบุ `language` เป็น `en`
- เนื้อหายังคง grounded กับ source เดิม

### Scenario C: Thai Query with English Response Override
Input:

```json
{
  "query": "TRL 5 คืออะไร",
  "response_language": "en"
}
```

Expected behavior:
- Route ไปที่ `qa`
- ตอบเป็นภาษาอังกฤษแม้ input จะเป็นภาษาไทย
- Response แสดงภาษาที่ใช้ตอบอย่างชัดเจน

### Scenario D: English Assessment Request
Input:

```json
{
  "query": "Please assess my project. We have tested the prototype in a relevant environment."
}
```

Expected behavior:
- Route ไปที่ `assessment`
- ระบบ parse English evidence ได้
- ผลประเมินยังคง deterministic และไม่ถูกตอบเป็น QA ธรรมดา

### Scenario E: Mixed-Language Request
Input:

```json
{
  "query": "ช่วย assess project นี้หน่อย เรามี prototype tested in relevant environment แล้ว"
}
```

Expected behavior:
- Route อย่างปลอดภัยตาม policy ที่กำหนด
- ระบบตรวจจับว่าเป็น `mixed` หรือ map ไปยังภาษาหลักตาม heuristic
- Assessment ยังคงใช้ evidence extraction ได้อย่างมีเหตุผล

## Definition of Done (DoD)
งานใน Sprint 15 จะถือว่าเสร็จเมื่อ:

1. ระบบรองรับ query ภาษาไทย ภาษาอังกฤษ และ mixed-language ในระดับ API contract
2. Response templates สำหรับ QA, assessment, fallback, และ follow-up questions รองรับอย่างน้อยไทยและอังกฤษ
3. Intent router แยก English QA กับ English assessment ได้แม่นยำขึ้นและมี regression tests รองรับ
4. Assessment parser รองรับ English evidence, negative evidence, และ uncertainty phrases ที่สำคัญ
5. Bilingual regression suite ถูกเพิ่มและผ่านโดยไม่ทำให้ behavior เดิมจาก Sprint 13-14 เสีย
6. เอกสารตัวอย่าง request/response สำหรับ bilingual behavior ถูกอัปเดต

---

## Sprint Backlog

### Ticket 15.1: Language Detection and Request Contract Upgrade (5 Story Points)
- **Description**: เพิ่มกลไกตรวจจับภาษา query และขยาย request/response contract ให้รองรับการระบุภาษาที่ต้องการ
- **Implementation Scope**:
  - เพิ่ม language detection เช่น `th`, `en`, `mixed`
  - เพิ่ม request option เช่น `response_language`
  - เพิ่ม response field เช่น `language`
  - กำหนด fallback rule เมื่อ language detection ไม่ชัดเจน
- **Acceptance Criteria (TDD)**:
  - Query ภาษาไทยถูกจัดเป็น `th`
  - Query ภาษาอังกฤษถูกจัดเป็น `en`
  - Query ไทยปนอังกฤษถูกจัดเป็น `mixed` หรือ mapped ตามกติกาที่กำหนด
  - Client สามารถ override ภาษา response ได้ผ่าน request

### Ticket 15.2: Bilingual Response Template Library (5 Story Points)
- **Description**: แยก response templates สำหรับ QA, assessment, fallback, error, และ follow-up questions เป็นไทยและอังกฤษ
- **Implementation Scope**:
  - ปรับ `assessment/response_templates.py` และส่วนที่เกี่ยวข้องให้รองรับหลายภาษา
  - รักษา markdown-safe formatting
  - ทำให้ fallback message สอดคล้องกับภาษาที่ตอบ
- **Acceptance Criteria (TDD)**:
  - QA ไทยได้ heading และ body ภาษาไทย
  - QA อังกฤษได้ heading และ body ภาษาอังกฤษ
  - Assessment follow-up questions ใช้ภาษาตาม response contract
  - Error/fallback ไม่หลุดภาษา

### Ticket 15.3: Bilingual Intent Router Upgrade (5 Story Points)
- **Description**: ขยาย `agents/intent_router.py` ให้เข้าใจ English QA, English assessment requests, และคำขอแบบ mixed-language
- **Implementation Scope**:
  - เพิ่ม English keyword hints สำหรับ definition, comparison, evidence QA, assessment, ambiguous, และ off-topic
  - เพิ่ม debug/rationale info สำหรับ test/admin mode
  - ปรับ priority rule ระหว่าง QA กับ assessment
- **Acceptance Criteria (TDD)**:
  - `What is TRL 4?` routes to `qa`
  - `Compare TRL 5 and TRL 6` routes to `qa`
  - `Please assess my project. We have tested the prototype in a relevant environment.` routes to `assessment`
  - Query ที่กำกวม เช่น `Can you check this?` ถูกจัดการอย่างปลอดภัย

### Ticket 15.4: English Assessment Evidence and Rule Mapping (6 Story Points)
- **Description**: เพิ่ม English evidence patterns, negative evidence, และ uncertainty language สำหรับ rule-based assessment
- **Implementation Scope**:
  - เพิ่ม pattern เช่น `prototype tested`, `validated`, `demonstrated`, `not yet tested`, `possibly`, `not sure`, `may have`
  - เพิ่มฟิลด์ภาษาอังกฤษใน rule base เช่น `question_en`, `description_en`, `summary_en`
  - ทำให้ evidence extraction ทำงานกับ domain-specific phrasing เบื้องต้น
- **Acceptance Criteria (TDD)**:
  - Evidence ภาษาอังกฤษถูก map เข้า required criteria ได้
  - Negative evidence ภาษาอังกฤษช่วยลดการ overestimate ได้
  - Uncertainty phrases ถูกเก็บแยกจาก supported evidence
  - Assessment อังกฤษยังคง deterministic result

### Ticket 15.5: Bilingual QA and Assessment Regression Suite (5 Story Points)
- **Description**: เพิ่ม automated tests และตัวอย่าง request cases สำหรับไทย อังกฤษ และ mixed-language
- **Implementation Scope**:
  - เพิ่ม cases ใน `examples/api_requests/trl_random_qa_assessment_cases.json` หรือไฟล์ evaluation แยก
  - เพิ่ม unit/API tests สำหรับ bilingual routing, QA, และ assessment
  - ป้องกัน regression ของ Thai-first behavior เดิม
- **Acceptance Criteria (TDD)**:
  - Definition QA ไทยและอังกฤษผ่าน
  - Comparison QA ไทยและอังกฤษผ่าน
  - Assessment อังกฤษผ่านโดยไม่ route เป็น QA
  - Mixed-language request ได้ behavior ตาม policy ที่กำหนด

---

## Expected Final Behavior
ตัวอย่าง response ที่คาดหวังสำหรับ English definition QA:

```json
{
  "mode": "qa",
  "language": "en",
  "answer_markdown": "## TRL Answer\n\nTRL 4 refers to component and/or breadboard validation in a laboratory environment..."
}
```

ตัวอย่าง response ที่คาดหวังสำหรับ English assessment:

```json
{
  "mode": "assessment",
  "language": "en",
  "assessment_result": {
    "matched_level": 5,
    "decision_status": "completed"
  }
}
```

---

## Risks and Notes
- การ match keyword ภาษาอังกฤษกว้างเกินไปอาจทำให้ definition QA ถูก route เข้า assessment
- Mixed-language behavior ต้องชัดเจนว่าระบบจะใช้ detected language หรือ `response_language` เป็นตัวตัดสินหลัก
- การเพิ่มฟิลด์ภาษาอังกฤษใน rule base ต้องไม่กระทบ traceability เดิมของภาษาไทย
- Bilingual support ต้องไม่ลดคุณภาพ deterministic assessment ที่มีอยู่แล้ว

## Resource Mapping
- **Total Sprint Effort**: 26 Story Points
- **Primary Source Code**: `rag_prompts.py`, `assessment/response_templates.py`, `agents/intent_router.py`, `agents/assessment_agent.py`, `rules/trl_rules.json`, `main.py`
- **Primary Tests**: `tests/test_intent_router.py`, `tests/test_assessment_agent.py`, `tests/test_api.py`, `tests/test_random_api_request_cases.py`
- **Primary Example Data**: `examples/api_requests/trl_random_qa_assessment_cases.json`
- **Documentation**: PM, SI, user/developer docs สำหรับ bilingual API behavior

## Sprint Success Summary
Sprint 15 จะสำเร็จเมื่อ Raggy Bot ไม่ได้รองรับเฉพาะ Thai-first behavior อีกต่อไป แต่สามารถรับและตอบคำถามรวมถึงประเมิน TRL ได้ทั้งไทยและอังกฤษ โดย intent routing และ rule-based assessment ยังคงเสถียรและตรวจสอบได้

---
**Plan Status**: Ready for Sprint 15 backlog grooming and implementation.
