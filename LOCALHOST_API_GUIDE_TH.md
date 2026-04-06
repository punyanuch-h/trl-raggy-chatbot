# คู่มือรันโปรเจกต์และทดสอบ API บน localhost

เอกสารนี้อัปเดตตาม implementation ปัจจุบันของ Raggy Bot ซึ่งรองรับทั้งการตอบคำถาม TRL และการประเมิน TRL แบบหลายรอบสนทนาผ่าน endpoint เดียวคือ `/raggy/trl`

## 1. สิ่งที่ต้องมี
- Python 3.10 ขึ้นไป
- PowerShell บน Windows
- OpenAI API Key
- Pinecone API Key
- JWT ที่ตรวจสอบด้วย `RS256`

## 2. ติดตั้งโปรเจกต์

```powershell
git clone <repo-url>
cd trl-raggy-chatbot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

ถ้า PowerShell block การ activate:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## 3. ตั้งค่า `.env`

```env
JWT_PUBLIC_KEY=
JWT_PUBLIC_KEY_V1=
JWT_PUBLIC_KEY_FILE=
JWT_AUDIENCE=
JWT_ISSUER=
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_INDEX_NAME=raggy-bot-trl
OPENAI_API_KEY=your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
FIRESTORE_PROJECT_ID=your-gcp-project-id
FIRESTORE_DATABASE_ID=(default)
FIRESTORE_METADATA_COLLECTION=request_metadata
METADATA_STORE_ENABLED=true
```

หมายเหตุ:
- `main.py` โหลดค่าจาก `.env` อัตโนมัติสำหรับ local
- ถ้าใช้ `kid` ใน JWT header เช่น `v1` สามารถตั้ง `JWT_PUBLIC_KEY_V1` ได้
- ถ้าไม่ต้องการใส่ public key ตรง ๆ สามารถใช้ `JWT_PUBLIC_KEY_FILE` แทนได้

## 4. เตรียมเอกสารสำหรับ RAG

วางไฟล์ใน:
- `source/` สำหรับเอกสารทั่วไป
- `source/private/` สำหรับเอกสารที่ `admin` เท่านั้นควรเข้าถึงได้

จากนั้นรัน:

```powershell
python reindex.py
```

## 5. รัน API

```powershell
python main.py
```

เปิดใช้งานได้ที่:
- `http://127.0.0.1:8080`
- `http://127.0.0.1:8080/docs`

## 6. รูปแบบ request ปัจจุบัน

```json
{
  "query": "ช่วยประเมิน TRL ให้หน่อย ตอนนี้มีผลทดสอบในสภาพแวดล้อมที่เกี่ยวข้องแล้ว",
  "session_id": "sess_optional_001",
  "candidate_level": 5
}
```

header ที่ใช้บ่อย:
- `Authorization: Bearer <token>`
- `Content-Type: application/json`
- `X-Request-ID` ถ้าต้องการ correlation id
- `X-Session-ID` ถ้าต้องการส่ง session ผ่าน header

## 7. ตัวอย่างเรียก QA mode

```powershell
$headers = @{
    Authorization = "Bearer $TOKEN"
    "Content-Type" = "application/json"
}

$body = @{
    query = "TRL 4 คืออะไร"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8080/raggy/trl" -Method Post -Headers $headers -Body $body
```

ตัวอย่าง response:

```json
{
  "answer_markdown": "## คำตอบ TRL\n\nTRL 4 คือการทดสอบต้นแบบในห้องปฏิบัติการ",
  "mode": "qa"
}
```

## 8. ตัวอย่างเรียก assessment mode

รอบแรก:

```powershell
$body = @{
    query = "ช่วยประเมิน TRL ให้หน่อย ตอนนี้มีผลทดสอบในสภาพแวดล้อมที่เกี่ยวข้องแล้ว"
    session_id = "sess-demo-001"
    candidate_level = 5
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8080/raggy/trl" -Method Post -Headers $headers -Body $body
```

รอบถัดไป ใช้ `session_id` เดิม:

```powershell
$body = @{
    query = "มีข้อมูลสมรรถนะและความปลอดภัยรองรับผลการทดสอบแล้ว"
    session_id = "sess-demo-001"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8080/raggy/trl" -Method Post -Headers $headers -Body $body
```

ตัวอย่าง response รอบแรก:

```json
{
  "answer_markdown": "## ผลการประเมิน TRL\n\nผลการประเมิน TRL เบื้องต้น...",
  "session_id": "sess-demo-001",
  "mode": "assessment",
  "assessment_result": {
    "candidate_level": 5,
    "matched_level": 4,
    "decision_status": "needs_more_evidence",
    "reasoning_summary": "หลักฐานของ TRL 5 ยังไม่ครบ"
  },
  "missing_evidence": [
    {
      "id": "trl_5_supporting_performance_data",
      "description_th": "มีข้อมูลสมรรถนะหรือความปลอดภัยที่รองรับผลการทดสอบ"
    }
  ],
  "next_question": "มีข้อมูลด้านประสิทธิภาพหรือความปลอดภัยที่รองรับผลการทดสอบระดับนี้อย่างไร?"
}
```

## 9. การทดสอบอัตโนมัติ

คำสั่ง regression ที่ใช้อยู่ตอนนี้:

```powershell
& '.\.venv_local\Scripts\python.exe' -m pytest `
  tests/test_api.py `
  tests/test_integration.py `
  tests/test_conversational_assessment.py `
  tests/test_assessment_agent.py `
  tests/test_assessment_session.py `
  tests/test_intent_router.py `
  tests/test_qa_agent.py `
  tests/test_trl_evaluator.py `
  tests/test_trl_rules.py `
  tests/test_source_audit.py `
  tests/test_response_templates.py `
  tests/test_metadata_store.py `
  tests/test_prompts.py `
  tests/test_response_formatter.py -q
```

## 10. ปัญหาที่พบบ่อย

### 10.1 ตอบให้ login ใหม่
- token ไม่มี
- token หมดอายุ
- public key ไม่ตรง
- audience หรือ issuer ไม่ตรงกับค่าที่ตั้ง

### 10.2 ได้ข้อความ technical fallback
- retrieval chain หรือ workflow ภายในทำงานไม่สำเร็จ
- ระบบจะพยายาม fallback อย่างปลอดภัยแทนการตอบ raw error

### 10.3 assessment ไม่จบในรอบเดียว
- เป็น behavior ปกติเมื่อหลักฐานยังไม่ครบ
- ให้ตอบคำถามใน `next_question` และส่ง `session_id` เดิมกลับมา
