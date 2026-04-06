# Technical Requirements Specification: Raggy Bot (Current Product State)

## 1. Core Stack
- **Language**: Python
- **Web Framework**: FastAPI
- **LLM Provider**: OpenAI
- **Vector Store**: Pinecone
- **Embedding Model**: OpenAI `text-embedding-3-small`
- **Orchestration Layer**: LangChain plus local deterministic orchestration modules
- **Test Framework**: `pytest`

## 2. Runtime and Security
- The service runs on local port `8080` by default and uses `PORT` in cloud environments.
- Browser access is currently whitelisted for `http://localhost:3000`.
- Clients must send `Authorization: Bearer <token>`.
- JWT verification must use `RS256`.
- Public key material may be loaded from:
  - `JWT_PUBLIC_KEY`
  - `JWT_PUBLIC_KEY_<KID>`
  - `JWT_PUBLIC_KEY_FILE`
- Optional audience and issuer validation may use:
  - `JWT_AUDIENCE`
  - `JWT_ISSUER`
- Missing or malformed `role` claims must safely downgrade to `researcher`.

## 3. Endpoint Contract
- **Primary Route**: `POST /raggy/trl`
- **Request Body**:
  - `query: string`
  - `session_id: optional string`
  - `candidate_level: optional integer`
- **Canonical Response Field**: `answer_markdown`
- **QA Response Mode**: includes `mode: "qa"`
- **Assessment Response Mode**: may include:
  - `session_id`
  - `mode: "assessment"`
  - `assessment_result`
  - `missing_evidence`
  - `next_question`

## 4. QA and Assessment Behavior
- General QA must use RAG-grounded answering and Thai-first response behavior.
- Assessment flow must use deterministic rule evaluation as the final authority.
- Assessment interpretation may infer structured evidence, but must not assign the final TRL directly.
- Assessment sessions must support multi-turn progression through a session-aware state store.

## 5. Structured Rule Requirements
- The rule base must support TRL levels 1 through 9.
- Each level must support:
  - `required_evidence`
  - `optional_evidence`
  - `domain_notes`
  - `follow_up_questions`
  - `source_references`
- Rule loading must be validated before runtime use.

## 6. Graceful Failure Design
- Validation and auth failures must return polite conversational payloads.
- Router failures must fall back safely to QA handling.
- QA orchestration failures should still return a retrieved answer when available.
- Assessment workflow failures should return an assessment technical fallback instead of raw server errors.
- Metadata write failures must not block the primary API response.

## 7. Metadata Controls
- Metadata storage is audit-only and must exclude transcript content.
- Approved stored fields:
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
- Excluded fields:
  - `query`
  - `answer`
  - `answer_markdown`
  - retrieved context
  - prompt content

## 8. Test Coverage Expectations
- Automated tests must cover:
  - auth behavior
  - metadata persistence safety
  - intent routing
  - QA and assessment API contracts
  - evaluator and rules validation
  - source audit behavior
  - conversational assessment flow
  - failure-path hardening
