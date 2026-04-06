# ตัวอย่าง Request สำหรับแต่ละ Use Case

เอกสารนี้อ้างอิงจาก implementation ปัจจุบันใน `main.py` และ OpenAPI ของโปรเจกต์ โดย endpoint หลักที่ใช้งานคือ `POST /raggy/trl`

## Endpoint

- URL: `http://127.0.0.1:8080/raggy/trl`
- Method: `POST`
- Content-Type: `application/json`

## Request Body Parameters

### `query`

- ประเภท: `string`
- จำเป็น: `required`
- ใช้สำหรับ:
  - ถามความรู้ทั่วไปเกี่ยวกับ TRL
  - เริ่มต้นการประเมิน TRL
  - ตอบคำถามต่อเนื่องใน session เดิมของการประเมิน
- หมายเหตุ:
  - ถ้าไม่ส่ง field นี้ ระบบจะเข้า validation fallback และตอบกลับเป็นข้อความสุภาพแทน
  - ตัว router จะใช้ข้อความนี้แยกว่าเป็น `qa` หรือ `assessment`

ตัวอย่าง:

```json
{
  "query": "TRL 4 คืออะไร"
}
```

### `session_id`

- ประเภท: `string | null`
- จำเป็น: `optional`
- ใช้สำหรับ:
  - ผูกหลาย request ให้อยู่ใน assessment conversation เดียวกัน
  - resume การประเมินรอบก่อนหน้า
- ควรใช้เมื่อ:
  - ต้องการส่งคำตอบต่อจาก `next_question`
  - ต้องการบังคับให้ request นี้อยู่ใน session เดิม
- หมายเหตุ:
  - ส่งได้ทั้งใน body และ header `X-Session-ID`
  - ถ้าส่งมาทั้งสองที่ ระบบจะใช้ `session_id` ใน body ก่อน
  - ถ้าเป็น assessment และไม่มี `session_id` ระบบสามารถสร้างใหม่ให้ได้

ตัวอย่าง:

```json
{
  "query": "มีข้อมูลสมรรถนะและความปลอดภัยรองรับผลการทดสอบแล้ว",
  "session_id": "sess-demo-001"
}
```

### `candidate_level`

- ประเภท: `integer | null`
- จำเป็น: `optional`
- ใช้สำหรับ:
  - ระบุ TRL เป้าหมายที่ต้องการให้ระบบประเมิน
- ควรใช้เมื่อ:
  - เริ่ม assessment รอบแรก
  - ต้องการบอกระบบชัดเจนว่าอยากประเมิน เช่น TRL 5 หรือ TRL 6
- หมายเหตุ:
  - มีประโยชน์กับ assessment มากกว่า QA
  - ถ้าไม่ส่ง ระบบจะประเมินจากบริบทของคำถามตาม workflow ภายใน

ตัวอย่าง:

```json
{
  "query": "ช่วยประเมิน TRL ให้หน่อย ตอนนี้มีผลทดสอบในสภาพแวดล้อมที่เกี่ยวข้องแล้ว",
  "candidate_level": 5
}
```

## Headers ที่ใช้บ่อย

### `Authorization`

- รูปแบบ: `Bearer <token>`
- จำเป็น: `required`
- ใช้สำหรับยืนยันตัวตนด้วย JWT แบบ `RS256`
- หมายเหตุ:
  - ถ้าไม่มีหรือ token ไม่ถูกต้อง ระบบจะตอบกลับเป็นข้อความสุภาพ ไม่คืน `401` ตรง ๆ

ตัวอย่าง:

```http
Authorization: Bearer <your-jwt-token>
```

### `X-Request-ID`

- ประเภท: `string`
- จำเป็น: `optional`
- ใช้สำหรับ:
  - correlation id
  - trace log
  - ผูก request กับ metadata record
- หมายเหตุ:
  - ถ้าไม่ส่ง ระบบจะ generate เอง
  - response header จะมี `X-Request-ID` กลับมา

ตัวอย่าง:

```http
X-Request-ID: req-demo-001
```

### `X-Session-ID`

- ประเภท: `string`
- จำเป็น: `optional`
- ใช้สำหรับส่ง session ผ่าน header แทน body
- หมายเหตุ:
  - ถ้ามี `session_id` ใน body ด้วย ระบบจะเลือกค่าจาก body

ตัวอย่าง:

```http
X-Session-ID: sess-demo-001
```

## Use Case ที่แนะนำ

### 1. ถามความรู้ทั่วไป TRL แบบ QA

ไฟล์ตัวอย่าง: `qa_basic.json`

```json
{
  "query": "TRL 4 คืออะไร"
}
```

เหมาะเมื่อ:

- ต้องการถามความหมายหรือความแตกต่างของระดับ TRL
- ไม่ต้องมี session ต่อเนื่อง

### 2. เริ่มประเมิน TRL รอบแรก

ไฟล์ตัวอย่าง: `assessment_start_level_5.json`

```json
{
  "query": "ช่วยประเมิน TRL ให้หน่อย ตอนนี้มีผลทดสอบในสภาพแวดล้อมที่เกี่ยวข้องแล้ว",
  "session_id": "sess-demo-001",
  "candidate_level": 5
}
```

เหมาะเมื่อ:

- ต้องการให้ระบบประเมินหลักฐานตามระดับเป้าหมาย
- ต้องการเก็บ session ไว้ถามต่อในรอบถัดไป

### 3. ตอบคำถามต่อเนื่องใน assessment เดิม

ไฟล์ตัวอย่าง: `assessment_followup_same_session.json`

```json
{
  "query": "มีข้อมูลสมรรถนะและความปลอดภัยรองรับผลการทดสอบแล้ว",
  "session_id": "sess-demo-001"
}
```

เหมาะเมื่อ:

- ได้ `next_question` จากรอบก่อนหน้าแล้วต้องการตอบกลับ
- ต้องการให้ระบบใช้บริบทเดิมของ assessment session

### 4. เริ่ม assessment แต่ส่ง session ผ่าน header

ไฟล์ตัวอย่าง: `assessment_start_header_session.json`

```json
{
  "query": "ช่วยประเมิน TRL ของต้นแบบนี้ ตอนนี้มีการทดสอบในสภาพแวดล้อมที่เกี่ยวข้องแล้ว",
  "candidate_level": 5
}
```

ใช้ร่วมกับ header:

```http
X-Session-ID: sess-header-001
```

## ตัวอย่างเรียกใช้งานด้วย PowerShell

### QA

```powershell
$headers = @{
    Authorization = "Bearer $TOKEN"
    "Content-Type" = "application/json"
    "X-Request-ID" = "req-qa-001"
}

$body = Get-Content .\examples\api_requests\qa_basic.json -Raw

Invoke-RestMethod -Uri "http://127.0.0.1:8080/raggy/trl" -Method Post -Headers $headers -Body $body
```

### Assessment รอบแรก

```powershell
$headers = @{
    Authorization = "Bearer $TOKEN"
    "Content-Type" = "application/json"
    "X-Request-ID" = "req-assessment-001"
}

$body = Get-Content .\examples\api_requests\assessment_start_level_5.json -Raw

Invoke-RestMethod -Uri "http://127.0.0.1:8080/raggy/trl" -Method Post -Headers $headers -Body $body
```

### Assessment รอบต่อเนื่อง

```powershell
$headers = @{
    Authorization = "Bearer $TOKEN"
    "Content-Type" = "application/json"
    "X-Request-ID" = "req-assessment-002"
}

$body = Get-Content .\examples\api_requests\assessment_followup_same_session.json -Raw

Invoke-RestMethod -Uri "http://127.0.0.1:8080/raggy/trl" -Method Post -Headers $headers -Body $body
```

## ตัวอย่าง response ที่คาดหวัง

### QA response

```json
{
  "answer_markdown": "## คำตอบ TRL\n\nTRL 4 คือการทดสอบต้นแบบในห้องปฏิบัติการ",
  "mode": "qa"
}
```

### Assessment response

```json
{
  "answer_markdown": "## ผลการประเมิน TRL\n\nผลการประเมินเบื้องต้น...",
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

## สรุปการเลือกใช้ Parameter แบบเร็ว

- ใช้ `query` ทุกครั้ง
- ใช้ `candidate_level` เมื่อต้องการระบุระดับ TRL เป้าหมาย
- ใช้ `session_id` เมื่อต้องการคุย assessment ต่อเนื่องหลายรอบ
- ใช้ `X-Request-ID` เมื่อต้องการ trace request ให้ชัดเจน
- ใช้ `X-Session-ID` ได้เมื่อไม่อยากใส่ `session_id` ใน body
