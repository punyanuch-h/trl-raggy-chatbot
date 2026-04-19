# Sprint 17 Plan: Production Readiness and Evaluation

## Sprint Details
- **Sprint Goal**: ทำให้ระบบพร้อมใช้บน production มากขึ้นด้วย session persistence, evaluation framework, monitoring-safe metadata, และเอกสารสำหรับ release readiness
- **Duration**: 2 Weeks
- **Methodology**: Agile & Test-Driven Development (TDD)
- **Standard**: ISO/IEC 29110 Basic Profile

## Problem Statement
Assessment session ปัจจุบันหากเก็บแบบ in-memory อาจหายเมื่อ service restart หรือ scale หลาย instance บน cloud ขณะเดียวกันทีมยังต้องมี evaluation suite ที่วัดคุณภาพในระดับ behavior ไม่ใช่เฉพาะ unit/API shape และต้องมี release evidence ที่พร้อมสำหรับการสรุปผลและ review

Sprint นี้จึงเน้นการทำให้ระบบใช้งานจริงได้มั่นคงขึ้น พร้อมมี benchmark และเอกสารกำกับการปล่อยระบบ

## Target User Scenarios

### Scenario A: Session Resume After Restart
Input Flow:
1. ผู้ใช้เริ่ม assessment session
2. ระบบ restart หรือ request ไปตกคนละ instance
3. ผู้ใช้ส่งคำตอบ follow-up ด้วย session id เดิม

Expected behavior:
- Session ถูก restore ได้
- ระบบยังรู้ว่า evidence ก่อนหน้าคืออะไร
- ไม่ถามคำถามเดิมซ้ำโดยไม่จำเป็น

### Scenario B: Behavioral Evaluation Run
Input:

```text
Run evaluation suite for bilingual QA, domain assessment, and source citation.
```

Expected behavior:
- มี workflow หรือ runner ที่รัน evaluation ได้ซ้ำ
- ได้ผลลัพธ์เชิง metric เช่น routing accuracy, fallback rate, bilingual accuracy, assessment accuracy, citation accuracy
- ใช้เป็น baseline ของ release ได้

### Scenario C: Safe Monitoring Metadata
Input:

```text
Request processed in assessment mode with English response and source citation enabled.
```

Expected behavior:
- Metadata เก็บข้อมูลที่พอสำหรับ debug
- ไม่เก็บข้อมูลอ่อนไหวเกินขอบเขต
- ช่วยแยกสาเหตุได้ว่าเป็น fallback เพราะ routing, retrieval, citation, หรือ storage

## Definition of Done (DoD)
งานใน Sprint 17 จะถือว่าเสร็จเมื่อ:

1. Assessment sessions ถูก persist และ restore ได้หลัง restart ตาม policy ที่กำหนด
2. Session expiry และ privacy-safe storage behavior ถูกกำหนดและถูกทดสอบ
3. Evaluation framework มี case files, runner หรือ workflow, และ metric baseline สำหรับ Phase 2
4. Monitoring-safe metadata ครอบคลุม mode, language, decision status, fallback reason, citation availability, และ session state status
5. เอกสาร developer-facing และ release-facing ถูกอัปเดตให้รองรับ capability ใหม่
6. มี release readiness note หรือ summary report พร้อม known limitations และ regression evidence

---

## Sprint Backlog

### Ticket 17.1: Persistent Assessment Session Store (6 Story Points)
- **Description**: ย้าย assessment session state ไปเก็บใน persistent storage เช่น Firestore หรือ database ที่เหมาะสม
- **Implementation Scope**:
  - ออกแบบ schema/session document
  - รองรับ create, restore, update, expiry
  - แยก metadata audit จากเนื้อหาที่อ่อนไหวตาม privacy design
  - รองรับ graceful fallback หาก storage unavailable
- **Acceptance Criteria (TDD)**:
  - Session สามารถ resume ได้หลัง restart
  - Session expiry ทำงานตาม policy
  - ไม่จำเป็นต้องเก็บ transcript เต็มถ้าไม่อยู่ใน scope
  - API behavior ยังคงเสถียรเมื่อ storage มีปัญหาชั่วคราว

### Ticket 17.2: Evaluation Framework and Behavioral Benchmarks (6 Story Points)
- **Description**: สร้าง evaluation framework สำหรับวัดคุณภาพ routing, QA, bilingual behavior, assessment accuracy, และ citation accuracy
- **Implementation Scope**:
  - สร้าง evaluation case files เช่น
    - `examples/evaluation/qa_bilingual_cases.json`
    - `examples/evaluation/assessment_domain_cases.json`
    - `examples/evaluation/source_citation_cases.json`
  - สร้าง runner/report format สำหรับ evaluation
  - กำหนด metric thresholds สำหรับ regression review
- **Acceptance Criteria (TDD)**:
  - มี evaluation runner หรือ workflow ที่รันได้ซ้ำ
  - มี metric อย่างน้อย routing accuracy, fallback rate, bilingual accuracy, assessment accuracy, citation accuracy
  - มี baseline result สำหรับ Phase 2 release

### Ticket 17.3: Monitoring-Safe Metadata and Operational Diagnostics (4 Story Points)
- **Description**: เพิ่ม metadata สำหรับ monitoring และ debugging โดยไม่เก็บข้อมูลเกินจำเป็น
- **Implementation Scope**:
  - เก็บ mode, language, decision status, fallback reason, citation availability, session state status
  - แยก operational metadata ออกจาก user content
  - ปรับเอกสาร troubleshooting และ admin/test mode behavior
- **Acceptance Criteria (TDD)**:
  - Metadata เพียงพอสำหรับ debug ปัญหาหลัก
  - ไม่มีการเก็บข้อมูลอ่อนไหวเกิน scope
  - Monitoring fields ถูกอธิบายไว้ในเอกสาร

### Ticket 17.4: Documentation and Developer Experience Upgrade (4 Story Points)
- **Description**: อัปเดตเอกสารเพื่อให้ทีมพัฒนาและระบบภายนอก integrate ได้ง่ายขึ้น
- **Implementation Scope**:
  - อัปเดต API guide เรื่อง bilingual behavior
  - อัปเดต assessment response contract
  - อัปเดต source citation contract
  - เพิ่มคู่มือเพิ่ม TRL rules เพิ่ม source documents และรัน evaluation suite
  - เพิ่ม troubleshooting สำหรับ insufficient evidence และ citation mismatch
- **Acceptance Criteria**:
  - เอกสาร developer-facing ครบตาม capability ใหม่
  - มี request/response examples ทั้งไทยและอังกฤษ
  - มีขั้นตอนทดสอบและ release verification ชัดเจน

### Ticket 17.5: Release Readiness Review and Regression Evidence (4 Story Points)
- **Description**: สรุป readiness ของ Phase 2 พร้อมหลักฐานการทดสอบและ known limitations
- **Implementation Scope**:
  - รัน regression suite รวม Sprint 13-17 ที่เกี่ยวข้อง
  - บันทึกผล evaluation benchmark
  - สรุป open risks, deferred improvements, และ release recommendation
- **Acceptance Criteria**:
  - มี release readiness note หรือ summary report
  - Known limitations ถูกบันทึก
  - Go/No-Go decision มีข้อมูลรองรับเพียงพอ

---

## Expected Final Behavior
ผลลัพธ์ที่คาดหวังเมื่อจบ Sprint 17:
- Assessment session สามารถทำงานข้าม request และข้าม instance ได้อย่างเสถียร
- ทีมสามารถรัน evaluation suite เพื่อดู baseline quality ของระบบได้ทุกครั้งก่อน release
- Operational metadata ช่วย debug ปัญหาได้โดยไม่กระทบ privacy design
- เอกสาร deployment, evaluation, และ troubleshooting ช่วยให้ทีมใช้งานและส่งมอบระบบได้ง่ายขึ้น

---

## Risks and Notes
- การเพิ่ม persistent storage อาจเพิ่ม operational complexity และ dependency ใหม่
- Evaluation framework ที่กว้างเกินไปอาจดูแลยาก จึงควรเริ่มจาก metrics ที่ให้ signal สูงก่อน
- Monitoring metadata ต้องออกแบบให้พอใช้จริง แต่ไม่ล้ำเข้าไปเก็บ user content เกินจำเป็น
- Release readiness ควรอิง evidence ที่รันได้จริง ไม่ควรสรุปจากการคาดการณ์

## Resource Mapping
- **Total Sprint Effort**: 24 Story Points
- **Primary Source Code**: `assessment/session_state.py`, `metadata_store.py`, `main.py`, storage integration modules ใหม่, evaluation runner/modules ใหม่
- **Primary Tests**: session restore/expiry tests, API regression tests, evaluation workflow tests, metadata tests
- **Primary Example Data**: `examples/evaluation/qa_bilingual_cases.json`, `examples/evaluation/assessment_domain_cases.json`, `examples/evaluation/source_citation_cases.json`
- **Documentation**: PM, SI design docs, test cases, test reports, release notes, user/developer guides

## Sprint Success Summary
Sprint 17 จะสำเร็จเมื่อ Raggy Bot พร้อมขึ้นสำหรับ production deployment ทั้งในแง่ session persistence, quality evaluation, operational diagnostics, และ release evidence ทำให้ Phase 2 ปิดได้อย่างมีหลักฐานรองรับและต่อยอดสู่ release ถัดไปได้มั่นคง

---
**Plan Status**: Ready for Sprint 17 backlog grooming and implementation.
