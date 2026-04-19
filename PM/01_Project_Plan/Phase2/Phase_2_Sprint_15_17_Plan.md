# Phase 2 Plan Overview: Sprint 15-17

## 1. Plan Overview
- **Initiative Name**: Raggy Bot Phase 2
- **Objective**: ยกระดับ Raggy Bot จาก Thai-first TRL assistant ไปสู่ระบบที่รองรับสองภาษา อธิบายผลการประเมินได้ชัดเจน อ้างอิง source ได้ และพร้อมใช้งานบน production มากขึ้น
- **Methodology**: Agile Scrum with Test-Driven Development (TDD)
- **Compliance Standard**: ISO/IEC 29110 Basic Profile
- **Sprint Cadence**: 3 sprints, 2 weeks per sprint
- **Primary Delivery Focus**: Bilingual QA and assessment, explainability, traceability, persistent assessment sessions, and evaluation framework

## 2. Strategic Direction
- ระบบต้องรองรับทั้งภาษาไทยและภาษาอังกฤษอย่างเป็นระบบ ไม่ใช่เพียงให้ LLM แปลคำตอบ
- การประเมิน TRL ต้องยังคงใช้ deterministic rule-based evaluation เป็นแกนหลัก
- คำตอบเชิง QA และ assessment ต้องอ้างอิง source ได้ชัดเจนขึ้น
- ผลการประเมินต้องอธิบายเหตุผล หลักฐานที่รองรับ หลักฐานที่ยังขาด และสิ่งที่ต้องมีเพื่อไปยังระดับถัดไป
- ระบบต้องรองรับ session persistence สำหรับ assessment บน cloud deployment ได้อย่างเสถียร
- ทีมต้องมี evaluation framework ที่วัดคุณภาพ routing, QA, bilingual behavior, assessment accuracy, และ citation accuracy ได้ต่อเนื่อง

## 3. Phase 2 Scope
- Bilingual input and output support (`th`, `en`, `mixed`)
- Bilingual intent routing and bilingual rule/evidence patterns
- Bilingual response templates and request contract
- Explainable assessment response contract
- Source citation and traceability in API response
- Domain-aware assessment refinement
- Persistent session storage for assessment
- Evaluation suite for regression and release readiness
- Documentation upgrade for developer and integration use

## 4. Definition of Done for Phase 2
งานใน Phase 2 จะถือว่าเสร็จเมื่อครบทุกข้อด้านล่าง:

1. ระบบตอบคำถามและประเมิน TRL ได้ทั้งไทยและอังกฤษ โดย behavior หลักถูกครอบด้วย automated tests
2. Assessment response มีทั้ง `supported_evidence`, `missing_evidence`, และคำอธิบายการตัดสินใจที่สื่อความหมายได้
3. QA และ assessment response มี `sources` หรือ traceability metadata ตามขอบเขตที่เหมาะสม
4. Session assessment สามารถ resume ได้หลัง service restart ตาม storage strategy ที่เลือก
5. Evaluation cases และ regression suite ถูกเพิ่มและรันได้จริง
6. เอกสาร PM, SI, test cases, test reports, และ user/developer guide ถูกอัปเดตสอดคล้องกับของจริง
7. ไม่มี regression สำคัญต่อ behavior จาก Sprint 13-14

## 5. Sprint Backlog Summary

| Sprint | Theme | Primary Outcome | Plan File |
| :--- | :--- | :--- | :--- |
| 15 | Bilingual TRL QA and Assessment | ระบบรองรับไทย-อังกฤษทั้ง routing, response, และ assessment evidence | `Sprint_15_Plan_Bilingual_TRL_QA_and_Assessment.md` |
| 16 | Explainable Assessment and Source Citation | ผลประเมินอธิบายได้และคำตอบมี citation/traceability ที่ชัดเจน | `Sprint_16_Plan_Explainable_Assessment_and_Source_Citation.md` |
| 17 | Production Readiness and Evaluation | session persistence, evaluation framework, monitoring-safe metadata, และ release readiness | `Sprint_17_Plan_Production_Readiness_and_Evaluation.md` |

## 6. Sprint Files
- [Sprint_15_Plan_Bilingual_TRL_QA_and_Assessment.md](/c:/Users/hcuna/Documents/Senior/trl-raggy-chatbot/PM/01_Project_Plan/Phase2/Sprint_15_Plan_Bilingual_TRL_QA_and_Assessment.md)
- [Sprint_16_Plan_Explainable_Assessment_and_Source_Citation.md](/c:/Users/hcuna/Documents/Senior/trl-raggy-chatbot/PM/01_Project_Plan/Phase2/Sprint_16_Plan_Explainable_Assessment_and_Source_Citation.md)
- [Sprint_17_Plan_Production_Readiness_and_Evaluation.md](/c:/Users/hcuna/Documents/Senior/trl-raggy-chatbot/PM/01_Project_Plan/Phase2/Sprint_17_Plan_Production_Readiness_and_Evaluation.md)

## 7. Cross-Sprint Technical Enablers
- แยก language handling ออกจาก business logic ให้ทดสอบได้ง่าย
- รักษา deterministic evaluator เป็น final authority เสมอ
- ทำ citation model ให้ใช้ซ้ำได้ทั้ง QA และ assessment
- ออกแบบ session storage โดยรองรับ privacy-by-design
- แยก evaluation fixtures ออกจาก random manual cases
- ใช้ source-controlled examples สำหรับไทย อังกฤษ และ mixed-language

## 8. Cross-Sprint Risks and Mitigations

| Risk | Impact | Mitigation |
| :--- | :--- | :--- |
| English routing แม่นไม่พอ | QA/assessment route ผิด | เพิ่ม bilingual routing tests และ ambiguous guardrails |
| Translation drift ระหว่างไทยและอังกฤษ | คำอธิบายไม่สม่ำเสมอ | ใช้ template และ structured fields แยกจาก freeform text |
| Citation ชี้ source ไม่ตรง | ลดความน่าเชื่อถือ | เพิ่ม citation verification tests และ traceability rules |
| Session persistence เก็บข้อมูลเกินจำเป็น | เสี่ยงด้าน privacy | แยก content กับ metadata และกำหนด retention policy |
| Evaluation suite ซับซ้อนเกินไป | ใช้งานจริงยาก | เริ่มจาก metric ที่จำเป็นและค่อยขยาย |
| เพิ่ม feature แล้ว regression ต่อ Sprint 13-14 | พฤติกรรมเดิมเสีย | รัน full regression suite และ lock critical scenarios |

## 9. ISO/IEC 29110 Artifact Mapping

| Area | Expected Artifact Update |
| :--- | :--- |
| PM | Sprint plans, roadmap updates, progress records, risk updates |
| SI/01_Requirements_Specification | Additional bilingual, explainability, traceability, and persistence requirements |
| SI/02_Software_Design | Language routing design, citation contract, assessment explainability, session persistence design, evaluation workflow |
| SI/04_Test_Cases_and_Procedures | Bilingual QA cases, explainability cases, citation cases, session restore cases |
| SI/05_Test_Reports | Sprint 15-17 regression reports and evaluation benchmark outputs |
| SI/06_User_Manual | API usage examples, bilingual behavior, assessment interpretation guide |
| SI/07_Product_Release | Phase 2 release summary and readiness evidence |

## 10. Recommended Build Order
1. Sprint 15 Ticket 15.1
2. Sprint 15 Ticket 15.2
3. Sprint 15 Ticket 15.3
4. Sprint 15 Ticket 15.4
5. Sprint 15 Ticket 15.5
6. Sprint 16 Ticket 16.1
7. Sprint 16 Ticket 16.2
8. Sprint 16 Ticket 16.3
9. Sprint 16 Ticket 16.4
10. Sprint 16 Ticket 16.5
11. Sprint 17 Ticket 17.1
12. Sprint 17 Ticket 17.2
13. Sprint 17 Ticket 17.3
14. Sprint 17 Ticket 17.4
15. Sprint 17 Ticket 17.5

## 11. Success Summary
Phase 2 จะถือว่าสำเร็จเมื่อ Raggy Bot ไม่ได้เป็นเพียง Thai-first TRL chatbot อีกต่อไป แต่กลายเป็นผู้ช่วยประเมิน TRL ที่รองรับสองภาษา อธิบายผลได้ อ้างอิง source ได้ เก็บ session ได้อย่างเหมาะสม และมี evaluation framework รองรับการพัฒนาต่อในระยะยาว

---
**Plan Status**: Ready for backlog grooming and Sprint 15-17 execution.
