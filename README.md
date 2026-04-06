# Raggy Bot: Thai-First TRL QA and Assessment API

Raggy Bot is a FastAPI service for Technology Readiness Level (TRL) work. The current product supports two modes behind the same endpoint:
- Thai-first TRL question answering grounded in indexed source documents
- deterministic multi-turn TRL assessment driven by structured rules in `rules/trl_rules.json`

## Current Product State
- Primary endpoint: `POST /raggy/trl`
- Canonical presentation field: `answer_markdown`
- QA responses return `mode: "qa"`
- Assessment responses return `mode: "assessment"` and may also include `session_id`, `assessment_result`, `missing_evidence`, and `next_question`
- Authentication uses JWT bearer tokens verified with `RS256`
- Metadata audit storage excludes transcript content

## Local Setup
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a root `.env` file:

```env
JWT_PUBLIC_KEY=
JWT_PUBLIC_KEY_V1=
JWT_PUBLIC_KEY_FILE=
JWT_AUDIENCE=
JWT_ISSUER=
OPENAI_API_KEY=sk-your-openai-key
OPENAI_BASE_URL=https://api.openai.com/v1
PINECONE_API_KEY=your-pinecone-key
PINECONE_INDEX_NAME=trl-raggy-chatbot
FIRESTORE_PROJECT_ID=your-gcp-project-id
FIRESTORE_DATABASE_ID=(default)
FIRESTORE_METADATA_COLLECTION=request_metadata
METADATA_STORE_ENABLED=true
```

## Knowledge Ingestion
Place PDF files in:
- `source/` for general documents
- `source/private/` for admin-only documents

Then re-index:

```powershell
python reindex.py
```

## Run Locally
```powershell
python main.py
```

Local URLs:
- `http://127.0.0.1:8080`
- `http://127.0.0.1:8080/docs`

## Current `/raggy/trl` Contract
Request:

```json
{
  "query": "ช่วยอธิบาย TRL 4",
  "session_id": "sess_optional_001",
  "candidate_level": 5
}
```

General QA response:

```json
{
  "answer_markdown": "## คำตอบ TRL\n\nTRL 4 คือการทดสอบต้นแบบในห้องปฏิบัติการ",
  "mode": "qa"
}
```

Assessment response:

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

## Metadata Audit Scope
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

Explicitly excluded:
- `query`
- `answer`
- `answer_markdown`
- retrieved context
- prompt content

Admin-only metadata endpoints:
- `GET /internal/metadata/requests?limit=20`
- `GET /internal/metadata/sessions/{session_id}`

## Testing
Recommended regression command:

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

## Documentation
- [LOCALHOST_API_GUIDE_TH.md](LOCALHOST_API_GUIDE_TH.md)
- [Architecture_Design.md](SI/02_Software_Design/Architecture_Design.md)
- [User_Manual.md](SI/06_User_Manual/User_Manual.md)
- [Final_Release_Report.md](SI/07_Product_Release/Final_Release_Report.md)
