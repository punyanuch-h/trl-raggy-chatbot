# Raggy Bot: Technology Readiness Level (TRL) Expert

Raggy Bot is a FastAPI-based Retrieval-Augmented Generation (RAG) API for answering Technology Readiness Level questions in healthcare and education contexts.

## Key points
- The primary endpoint is `POST /raggy/trl`.
- The current response contract returns one canonical field: `answer_markdown`.
- Local runs default to `http://127.0.0.1:8080`.
- Cloud deployments use the `PORT` environment variable.

## Local setup
```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a root `.env` file:

```env
JWT_SECRET=your_secure_random_string
OPENAI_API_KEY=sk-your-openai-key
OPENAI_BASE_URL=https://api.openai.com/v1
PINECONE_API_KEY=your-pinecone-key
PINECONE_INDEX_NAME=trl-raggy-chatbot
FIRESTORE_PROJECT_ID=your-gcp-project-id
FIRESTORE_DATABASE_ID=(default)
FIRESTORE_METADATA_COLLECTION=request_metadata
```

Optional local toggle:

```env
METADATA_STORE_ENABLED=true
```

## Knowledge ingestion
Place PDFs in:
- `source/` for general documents
- `source/private/` for admin-only documents

Then re-index:

```bash
python reindex.py
```

## Run locally
```bash
python main.py
```

The API and Swagger UI will be available at:
- `http://127.0.0.1:8080`
- `http://127.0.0.1:8080/docs`

## `/raggy/trl` contract
Request:

```json
{
  "query": "What are TRL levels 1 to 9?"
}
```

Response:

```json
{
  "answer_markdown": "## TRL Response\n\nTRL 1 begins with basic principles..."
}
```

`answer_markdown` is the canonical output intended for frontend rendering. The API no longer duplicates the same content into a second plain-text field.

The API also accepts optional audit headers:
- `X-Request-ID` to reuse a caller-generated correlation id
- `X-Session-ID` to group related requests without storing transcript content

Successful responses echo `X-Request-ID` in the response headers.

## Internal metadata review
Sprint 7 adds metadata-only persistence for audit and monitoring. Phase 1 intentionally excludes `query`, `answer`, `answer_markdown`, and retrieved context.

Admin-only verification endpoints:
- `GET /internal/metadata/requests?limit=20`
- `GET /internal/metadata/sessions/{session_id}`

Stored fields:
- `request_id`
- `session_id`
- `user_id`
- `role`
- `timestamp`
- `response_status`
- `route_path`
- `model_name`

## Testing
Run the standard local suite:

```powershell
.\run_tests.bat
```

Or run targeted tests:

```powershell
.\.venv\Scripts\pytest.exe tests\test_api.py tests\test_integration.py tests\test_response_formatter.py tests\test_prompts.py
```

## Documentation
- [LOCALHOST_API_GUIDE_TH.md](/c:/Users/hcuna/Documents/Senior/trl-raggy-chatbot/LOCALHOST_API_GUIDE_TH.md)
- [SI/06_User_Manual/User_Manual.md](/c:/Users/hcuna/Documents/Senior/trl-raggy-chatbot/SI/06_User_Manual/User_Manual.md)
- [SI/02_Software_Design/Architecture_Design.md](/c:/Users/hcuna/Documents/Senior/trl-raggy-chatbot/SI/02_Software_Design/Architecture_Design.md)
- [SI/02_Software_Design/openapi.json](/c:/Users/hcuna/Documents/Senior/trl-raggy-chatbot/SI/02_Software_Design/openapi.json)
