# Technical Requirements Specification: Raggy Bot (Version 3)

## 1. Core Architecture Stack
* **Operating Language**: Python
* **Web Framework**: FastAPI
* **LLM Provider**: OpenAI
* **Vector Database**: Pinecone (Serverless Cloud DB)
  * *Dimensions Rule*: Pinecone must be configured for `1536`-dimension vectors to align with the embedding model
* **Embedding Model**: OpenAI `text-embedding-3-small`
* **Orchestration Library**: LangChain
* **Testing Suite**: `pytest`

## 2. API Security, CORS, and Runtime
* **API Execution**: The Uvicorn ASGI server runs as the FastAPI host process. The local default port is `8080`. Cloud execution uses the `PORT` environment variable.
* **CORS Configuration**: The API explicitly allows browser requests from `http://localhost:3000`.
* **Endpoint Route**: The system exposes one conversational endpoint at `POST /raggy/trl`.
* **API JWT Handling**:
  * Clients must send `Authorization: Bearer <token>`
  * The API verifies the token with `JWT_SECRET`
  * If `role` is missing or malformed, access safely downgrades to `researcher`

## 3. Request and Response Contract
* **Input Contract**: The endpoint accepts a JSON body with a single `query` string
* **Primary Response Contract**: The endpoint returns a JSON object containing:
  * `answer_markdown` as the canonical markdown response field
* **API Clarity Rule**: The contract uses a single answer field because there is no confirmed production frontend or external consumer that requires backward compatibility with an older plain-text field
* **Formatting Rule**: `answer_markdown` must remain safe for frontend markdown rendering

## 4. Safe Request Exception Engine
* **Graceful Exception Constraint**: Validation, authentication, and internal failures must return polite conversational payloads instead of raw framework errors
* **Response Shape Consistency**:
  * *Input Example Response Shape*: `{"answer_markdown": "..."}`
  * *Security Error Example Response Shape*: `{"answer_markdown": "..."}`

## 5. LLM Generation Directives
* **Prompt Engineering Structure**: The system prompt must enforce a polite, supportive, professional tone suitable for healthcare and education contexts
* **Markdown Safety Rule**: The model output must use only safe markdown constructs suitable for frontend rendering
  * Allowed structures: one level-2 heading, short paragraphs, and hyphen bullet lists
  * Disallowed structures: raw HTML, tables, code fences, numbered lists, and deep heading levels

## 6. Data Pipeline and Privacy Control
* **Document Ingestion**:
  * `source/` contains general documents
  * `source/private/` contains restricted documents
* **Filter Logic**:
  * Private documents must be tagged for admin-only access
  * `researcher` retrieval must exclude restricted chunks before context reaches the LLM

## 7. Evaluation and TDD Directives
* **Deterministic Elements**: PDF extraction, JWT decoding, JSON serialization, CORS checks, response formatting, and prompt constraints must be covered by `pytest`
* **Non-Deterministic Outcomes**: Generated answers should be evaluated for faithfulness, relevance, politeness, and output structure consistency

## 8. Metadata Persistence Controls
* **Phase 1 Storage Scope**: The system may persist request metadata for operational audit and monitoring, but it must not persist transcript content
* **Approved Metadata Fields**:
  * `request_id`
  * `session_id` when provided
  * `user_id` derived from JWT `sub` or stable user claim
  * `role`
  * `timestamp`
  * `response_status`
  * `route_path`
  * `model_name`
* **Explicitly Excluded Fields**:
  * `query`
  * `answer`
  * `answer_markdown`
  * retrieved context or prompt content
* **Storage Backend**: Firestore is the preferred metadata backend for Phase 1 because it supports low-volume per-request writes, simple operational queries, and free-tier alignment for an internal user base of about 100 users
* **Operational Review Path**: Internal inspection access is admin-only and limited to metadata list and read-by-session workflows
* **Budget and Retention Guidance**:
  * Keep metadata in a dedicated collection, default `request_metadata`
  * Apply time-bounded retention, recommended 30 to 90 days depending on governance approval
  * Grant the Cloud Run service account only the minimum Firestore document read/write permissions required for this collection
