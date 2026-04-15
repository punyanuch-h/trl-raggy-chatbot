# แนวทางการพัฒนาโปรเจกต์ Raggy Bot ต่อในระยะถัดไป

## ภาพรวม

จากสถานะปัจจุบัน Raggy Bot เป็นระบบ API สำหรับตอบคำถามและประเมิน Technology Readiness Level (TRL) ที่มีจุดแข็งสำคัญคือการออกแบบแบบ Thai-first, การใช้ RAG เพื่ออ้างอิงเอกสาร, การมี deterministic TRL assessment ผ่าน rule base, การรองรับ session สำหรับการประเมินหลายรอบสนทนา และการมีชุดทดสอบที่ครอบคลุมหลายส่วนของระบบแล้ว

อย่างไรก็ตาม ระบบยังสามารถพัฒนาต่อให้มีความพร้อมใช้งานจริงมากขึ้นได้อีกหลายด้าน โดยเฉพาะการรองรับสองภาษา ไทยและอังกฤษ, การอธิบายเหตุผลของผลประเมินให้ชัดเจนขึ้น, การอ้างอิงแหล่งข้อมูลในคำตอบ, การเพิ่มความทนทานสำหรับ production และการวัดคุณภาพของคำตอบอย่างเป็นระบบ

## 1. พัฒนาระบบให้รองรับทั้งภาษาไทยและอังกฤษ

ปัจจุบันระบบถูกออกแบบให้ตอบภาษาไทยเป็นหลัก และมีคำสั่งใน prompt ว่าให้ตอบภาษาไทยโดยค่าเริ่มต้น เว้นแต่ผู้ใช้จะขอภาษาอื่น แนวทางต่อไปคือทำให้ bilingual support เป็นความสามารถระดับระบบ ไม่ใช่เพียงการให้ LLM แปลคำตอบในบางกรณี

แนวทางที่ควรพัฒนา:

- เพิ่มการตรวจจับภาษา input เช่น `th`, `en`, หรือ `mixed`
- เพิ่ม field ใน response เช่น `language` เพื่อบอกว่าระบบตอบด้วยภาษาใด
- เพิ่ม request option เช่น `response_language` เพื่อให้ frontend หรือ client ระบุภาษาที่ต้องการได้
- แยก response template เป็นภาษาไทยและอังกฤษ
- เพิ่ม `question_en`, `description_en`, `summary_en` ใน rule base สำหรับ assessment
- เพิ่ม test cases ภาษาอังกฤษและภาษาไทยปนอังกฤษ

ตัวอย่างพฤติกรรมที่ควรรองรับ:

- ผู้ใช้ถามว่า `TRL 4 คืออะไร` ระบบตอบไทย
- ผู้ใช้ถามว่า `What is TRL 4?` ระบบตอบอังกฤษ
- ผู้ใช้ถามไทยแต่ระบุว่า `ตอบเป็นภาษาอังกฤษ` ระบบตอบอังกฤษ
- ผู้ใช้ให้ข้อมูล assessment เป็นอังกฤษ ระบบยังประเมินระดับ TRL ได้ถูกต้อง

ประโยชน์ที่ได้คือระบบจะใช้งานได้กว้างขึ้น ทั้งกับนักวิจัยไทย ผู้ประเมินต่างชาติ เอกสารวิชาการภาษาอังกฤษ และระบบ frontend ที่ต้องรองรับผู้ใช้หลายกลุ่ม

## 2. ยกระดับ Intent Router ให้เข้าใจหลายภาษา

ระบบมี intent router สำหรับแยกคำถามทั่วไปเกี่ยวกับ TRL ออกจากคำขอประเมิน TRL แล้ว แต่ยังควรเพิ่มความสามารถในการเข้าใจภาษาอังกฤษให้ครบขึ้น

ตัวอย่าง intent ที่ควรรองรับ:

- Definition QA: `What is TRL 5?`
- Comparison QA: `Compare TRL 5 and TRL 6`
- Evidence QA: `What evidence is required for TRL 8?`
- Assessment: `Please assess my project. We have tested the prototype in a relevant environment.`
- Ambiguous request: `Can you check this?`

แนวทางพัฒนา:

- เพิ่ม keyword hints ภาษาอังกฤษใน router
- เพิ่มชุด test สำหรับ routing accuracy
- แยก test เป็นกลุ่ม `qa`, `assessment`, `ambiguous`, `off_topic`
- เพิ่ม rationale/debug information สำหรับ admin หรือ test mode

ผลลัพธ์ที่ต้องการคือคำถามภาษาอังกฤษไม่ควรถูก fallback โดยไม่จำเป็น และคำขอประเมินไม่ควรถูกตอบเป็น QA ธรรมดา

## 3. เพิ่มความสามารถของ Rule-based Assessment

ระบบประเมิน TRL ตอนนี้มีจุดแข็งเพราะไม่ได้พึ่ง LLM ทั้งหมด แต่ใช้ rule base และ evidence patterns ทำให้ผลประเมินมีความคงที่ ตรวจสอบได้ และเหมาะกับงานที่ต้องการความน่าเชื่อถือ

สิ่งที่ควรพัฒนาต่อ:

- เพิ่ม evidence patterns ภาษาอังกฤษให้ครบทุกระดับ TRL
- เพิ่มการตรวจจับข้อความที่แสดงความไม่แน่ใจ เช่น `possibly`, `not sure`, `may have`
- เพิ่มการตรวจจับข้อความปฏิเสธ เช่น `not yet tested`, `no prototype`, `without validation`
- เพิ่มการสรุป evidence ที่รองรับแล้วและ evidence ที่ยังขาด
- เพิ่ม checklist ของแต่ละ TRL level ใน response
- รองรับ domain-specific assessment เช่น software, medical device, biotech, agriculture

ตัวอย่างผลลัพธ์ที่ควรได้ในอนาคต:

```text
Matched Level: TRL 5
Supported Evidence:
- Prototype tested in a relevant environment
- Performance data available

Missing Evidence for TRL 6:
- Prototype demonstration result
- Demonstration data in relevant environment
```

การทำเช่นนี้จะช่วยให้ผู้ใช้เข้าใจว่าเหตุใดระบบจึงให้ระดับนั้น และต้องเตรียมหลักฐานอะไรเพื่อขยับไปยังระดับถัดไป

## 4. เพิ่ม Source Citation และ Traceability

ระบบมี source-aware QA แล้ว แต่สามารถทำให้คำตอบน่าเชื่อถือขึ้นได้อีกโดยเพิ่ม citation ใน response อย่างเป็นระบบ

แนวทางพัฒนา:

- เพิ่ม field `sources` ใน API response
- ระบุชื่อไฟล์ source ที่ใช้ตอบ เช่น `Technology_Readiness_Level_Definition.txt`
- ระบุ section หรือ TRL level ที่อ้างอิง
- แยก citation สำหรับ QA และ assessment
- เก็บ source reference ใน metadata เฉพาะส่วนที่ไม่ละเมิด privacy

ตัวอย่าง response ที่ควรมีในอนาคต:

```json
{
  "mode": "qa",
  "language": "th",
  "answer_markdown": "...",
  "sources": [
    {
      "source_file": "source/Technology_Readiness_Level_Definition.txt",
      "section": "TRL 8"
    }
  ]
}
```

ประโยชน์คือผู้ใช้สามารถตรวจสอบที่มาของคำตอบได้ โดยเฉพาะในบริบทงานวิจัยหรือการประเมินที่ต้องการความโปร่งใส

## 5. เพิ่ม Explainability ของผลประเมิน

ปัจจุบัน response ของ assessment มี `assessment_result`, `missing_evidence`, และ `next_question` ซึ่งเป็นพื้นฐานที่ดีแล้ว แต่สามารถทำให้ผู้ใช้เข้าใจผลลัพธ์ได้มากขึ้น

สิ่งที่ควรเพิ่ม:

- `supported_evidence`: หลักฐานที่ระบบพบและใช้ประกอบการประเมิน
- `uncertain_evidence`: หลักฐานที่ยังไม่ชัดเจน
- `conflicting_evidence`: หลักฐานที่ขัดแย้งกัน
- `next_level_requirements`: สิ่งที่ต้องมีเพื่อไปสู่ TRL ถัดไป
- `decision_explanation`: เหตุผลแบบสั้น กระชับ และอ่านง่าย

ตัวอย่าง:

```json
{
  "matched_level": 8,
  "decision_status": "completed",
  "supported_evidence": [
    "ระบบจริงผ่านการรับรองตามมาตรฐาน",
    "มีหลักฐานว่าพร้อมส่งมอบตามข้อกำหนด"
  ],
  "next_level_requirements": [
    "มีผลการใช้งานจริงต่อเนื่อง",
    "มีรายงานติดตามผลหลังส่งมอบ"
  ]
}
```

ฟีเจอร์นี้จะทำให้ระบบไม่ได้เป็นเพียง chatbot แต่กลายเป็นผู้ช่วยประเมินที่อธิบายได้

## 6. รองรับ Domain-specific TRL ให้ชัดขึ้น

ใน rule base มีข้อมูล domain notes อยู่แล้ว เช่น software, medical device, biotech และ agriculture ดังนั้นควรใช้ข้อมูลนี้ให้เกิดประโยชน์มากขึ้น

แนวทางพัฒนา:

- เพิ่ม field `domain` ใน request เช่น `software`, `medical_device`, `biotech`, `agriculture`
- ให้ระบบถาม domain เพิ่มเมื่อข้อมูลยังไม่ชัดเจน
- ปรับคำถาม follow-up ตาม domain
- ปรับตัวอย่าง evidence ตาม domain
- เพิ่ม test cases แยกตาม domain

ตัวอย่าง:

- Software อาจเน้น system prototype, integration test, production deployment, monitoring
- Medical device อาจเน้น clinical validation, ISO 13485, CE mark, safety evidence
- Biotech อาจเน้น lab validation, scale-up, pivotal study, regulatory approval
- Agriculture อาจเน้น field trial, farm-scale validation, adoption evidence

การทำ domain-specific assessment จะช่วยให้คำแนะนำไม่กว้างเกินไปและตรงกับลักษณะงานวิจัยมากขึ้น

## 7. พัฒนา Session Persistence สำหรับ Production

ตอนนี้ระบบมี session สำหรับ assessment หลายรอบสนทนา แต่ถ้าใช้ in-memory store อย่างเดียว session อาจหายเมื่อ server restart หรือเมื่อ deploy แบบหลาย instance

แนวทางพัฒนา:

- ย้าย assessment session ไปเก็บใน Firestore หรือ database
- กำหนด session expiration
- เก็บเฉพาะข้อมูลที่จำเป็น ไม่เก็บ transcript เต็มหากไม่จำเป็น
- แยก metadata audit ออกจากเนื้อหาคำถามและคำตอบตาม privacy design เดิม
- เพิ่ม test สำหรับ session restore และ session expiry

ผลลัพธ์คือระบบจะพร้อมใช้งานบน cloud มากขึ้น และรองรับผู้ใช้หลาย session ได้เสถียรกว่าเดิม

## 8. เพิ่ม Evaluation Framework สำหรับวัดคุณภาพระบบ

ระบบมี unit tests และ API tests แล้ว แต่ควรเพิ่ม evaluation framework ที่วัดคุณภาพเชิงพฤติกรรมของระบบโดยตรง

ตัวชี้วัดที่ควรมี:

- Routing accuracy: แยก QA กับ assessment ถูกหรือไม่
- Answer groundedness: คำตอบอ้างอิงจาก source จริงหรือไม่
- Fallback rate: ระบบ fallback บ่อยแค่ไหน
- Bilingual accuracy: ภาษาอังกฤษและไทยตอบถูกต้องเทียบเท่ากันหรือไม่
- Assessment accuracy: ประเมิน TRL ได้ตรง expected level หรือไม่
- Citation accuracy: source ที่อ้างตรงกับคำตอบหรือไม่
- Regression stability: การแก้ feature ใหม่ไม่ทำให้ behavior เดิมเสียหรือไม่

ควรมีไฟล์ evaluation cases แยกจาก manual random cases เช่น:

```text
examples/evaluation/qa_bilingual_cases.json
examples/evaluation/assessment_domain_cases.json
examples/evaluation/source_citation_cases.json
```

สิ่งนี้จะช่วยให้โปรเจกต์มีหลักฐานคุณภาพที่ชัดเจนขึ้น และเหมาะสำหรับรายงานหรือการนำเสนอ project defense

## 9. ปรับปรุง Documentation และ Developer Experience

เอกสารปัจจุบันมีหลายส่วนแล้ว เช่น API guide, architecture, sprint plan และ test report แต่ควรต่อยอดให้ developer หรือผู้ใช้ใหม่เข้าใจระบบเร็วขึ้น

เอกสารที่ควรเพิ่ม:

- Bilingual API behavior
- Assessment response contract
- Source citation contract
- How to add new TRL rules
- How to add new source documents
- How to run evaluation suite
- Troubleshooting เมื่อระบบตอบ insufficient evidence

ควรเพิ่มตัวอย่าง request/response ทั้งภาษาไทยและอังกฤษ เพื่อให้ frontend หรือระบบภายนอก integrate ได้ง่าย

## 10. แนวทาง Sprint ถัดไปที่แนะนำ

ถ้าต้องจัดเป็น sprint ต่อไป ผมเสนอให้ทำเป็นลำดับดังนี้

### Sprint 15: Bilingual TRL QA and Assessment

เป้าหมาย:

- รองรับ input/output ภาษาไทยและอังกฤษ
- เพิ่ม language detection
- เพิ่ม response templates สองภาษา
- เพิ่ม English routing และ English assessment patterns
- เพิ่ม bilingual test cases

ไฟล์หลักที่น่าจะเกี่ยวข้อง:

- `rag_prompts.py`
- `assessment/response_templates.py`
- `agents/intent_router.py`
- `agents/assessment_agent.py`
- `rules/trl_rules.json`
- `examples/api_requests/trl_random_qa_assessment_cases.json`
- `tests/test_intent_router.py`
- `tests/test_assessment_agent.py`
- `tests/test_api.py`

### Sprint 16: Explainable Assessment and Source Citation

เป้าหมาย:

- เพิ่ม `supported_evidence`
- เพิ่ม `sources`
- เพิ่ม traceability ของคำตอบ
- เพิ่ม next-level recommendation
- เพิ่ม test ตรวจ citation และ explanation quality

### Sprint 17: Production Readiness and Evaluation

เป้าหมาย:

- ทำ persistent session store
- เพิ่ม evaluation framework
- เพิ่ม monitoring metadata ที่ไม่เก็บข้อมูลอ่อนไหว
- เพิ่ม regression report สำหรับ QA, assessment, bilingual และ citation

## สรุป

แนวทางที่เหมาะสมที่สุดสำหรับการพัฒนา Raggy Bot ต่อ คือไม่ควรเพิ่มฟีเจอร์แบบกระจัดกระจาย แต่ควรยกระดับระบบจาก Thai-first TRL chatbot ให้กลายเป็น source-grounded, bilingual, explainable TRL assessment assistant

ลำดับที่แนะนำคือเริ่มจาก bilingual support ก่อน เพราะเป็นฐานให้ระบบใช้งานได้กว้างขึ้น จากนั้นจึงเพิ่ม explainability และ source citation เพื่อเพิ่มความน่าเชื่อถือ แล้วค่อยพัฒนา production readiness และ evaluation framework เพื่อให้ระบบพร้อมใช้งานจริงในระยะยาว

