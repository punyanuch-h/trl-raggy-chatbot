# Raggy Bot User Manual

## 1. Purpose
Raggy Bot is a Thai-first API for Technology Readiness Level work. It supports:
- TRL question answering from indexed documents
- multi-turn TRL assessment with deterministic rule evaluation

## 2. Prerequisites
- a valid JWT bearer token
- access to the deployed API URL or local URL `http://127.0.0.1:8080`

## 3. Main Endpoint
- `POST /raggy/trl`

## 4. Request Headers
- `Content-Type: application/json`
- `Authorization: Bearer <your_jwt_token>`
- optional `X-Request-ID`
- optional `X-Session-ID`

## 5. Request Body
```json
{
  "query": "ช่วยประเมิน TRL ให้หน่อย ตอนนี้มีผลทดสอบในสภาพแวดล้อมที่เกี่ยวข้องแล้ว",
  "session_id": "sess_optional_001",
  "candidate_level": 5
}
```

## 6. Response Shapes
General QA example:
```json
{
  "answer_markdown": "## คำตอบ TRL\n\nTRL 4 คือการทดสอบต้นแบบในห้องปฏิบัติการ",
  "mode": "qa"
}
```

Assessment example:
```json
{
  "answer_markdown": "## ผลการประเมิน TRL\n\nผลการประเมิน TRL เบื้องต้น...",
  "session_id": "sess_optional_001",
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

## 7. How To Use Each Mode
- **QA mode**
  - ask TRL concepts, differences, or explanations
  - the response returns `mode: "qa"`
- **Assessment mode**
  - provide evidence about the project state
  - keep sending follow-up answers with the same `session_id`
  - the response may include `next_question` until the system can confirm or downgrade the level

## 8. Understanding Key Fields
- `answer_markdown`
  - canonical display field for frontend rendering
- `mode`
  - tells whether the response came from QA or assessment flow
- `assessment_result`
  - contains `candidate_level`, `matched_level`, `decision_status`, and `reasoning_summary`
- `missing_evidence`
  - shows which evidence items are still not supported
- `next_question`
  - tells the user what evidence to provide next

## 9. Roles and Access
- `researcher`
  - can use public TRL sources only
- `admin`
  - can use public and restricted sources
  - can access internal metadata review endpoints

## 10. Troubleshooting
- If the response asks you to log in again:
  - the JWT is missing, invalid, or expired
- If the response says there is a technical issue:
  - the API could not complete the workflow and returned a safe fallback
- If the assessment response contains `next_question`:
  - continue with the same `session_id`
- If the assessment result seems lower than expected:
  - review `missing_evidence` and provide the requested proof

## 11. Metadata Review
The system stores metadata only for audit and troubleshooting. It does not store transcript content in the metadata records.

Stored fields:
- `request_id`
- `session_id`
- `user_id`
- `role`
- `timestamp`
- `response_status`
- `route_path`
- `model_name`
- `workflow_mode`
- `decision_status`

Admin-only internal endpoints:
- `GET /internal/metadata/requests?limit=20`
- `GET /internal/metadata/sessions/{session_id}`
