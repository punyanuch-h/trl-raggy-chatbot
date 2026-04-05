# Architecture & Software Design: Raggy Bot

## Overview
This document describes the current software design of the Raggy Bot API. It reflects the implementation state after the response-contract simplification and Sprint 7 metadata persistence: `/raggy/trl` returns a single canonical markdown field, `answer_markdown`, while Phase 1 stores only low-risk request metadata for audit visibility.

## 1. High-Level Architecture
* **Microservice Framework**: FastAPI
* **Operating Port**: Local default `8080`; cloud execution uses the `PORT` environment variable
* **Database**: Pinecone (Serverless) for retrieval, Firestore for metadata-only audit records
* **LLM Engine**: OpenAI through LangChain orchestration

## 2. API Specifications (OpenAPI/Swagger)
The generated API contract is stored in `SI/02_Software_Design/openapi.json`. This file is the formal contract reference for `/raggy/trl`.

## 3. JWT Security and Auth Flow
The endpoint is protected by FastAPI security middleware using bearer tokens.
* The API reads `Authorization: Bearer <token>`
* The token is verified with `HS256` and `JWT_SECRET`
* Missing or malformed `role` claims downgrade safely to `researcher`
* Authentication failures are converted into polite conversational responses rather than raw 401 payloads

## 4. Data Ingestion Pipeline
* **Parser**: `pdf_parser.py` scans PDF files recursively
* **Chunker**: `RecursiveCharacterTextSplitter` with configured chunk size and overlap
* **Embedder**: OpenAI `text-embedding-3-small`
* **Vector Store**: Pinecone with metadata-based RBAC filtering

## 5. RAG Retrieval and Prompting
* **RBAC Retriever**: `researcher` requests exclude admin-only chunks
* **Prompt Layer**: `rag_prompts.py` enforces tone, grounding, and markdown-safety instructions
* **Generative Chain**: LangChain `create_retrieval_chain` combines retrieval with LLM synthesis

## 6. Response Formatting Layer
The response-formatting layer is intentionally small and centralized.
* **Canonical Response Field**: `answer_markdown`
* **Formatting Utility**: `response_formatter.py` wraps successful and fallback responses in a predictable markdown-safe structure
* **Consistency Rule**: Success, validation fallback, authentication fallback, and technical-error fallback all use the same response shape

## 7. Markdown Safety Design
To keep frontend rendering predictable, output is constrained to:
* one level-2 heading
* short paragraphs
* simple hyphen bullet lists

The design intentionally excludes raw HTML, tables, code fences, and deep heading hierarchies.

## 8. Current Endpoint Contract
* **Endpoint**: `POST /raggy/trl`
* **Request Model**: `{"query": "<string>"}`
* **Response Model**: `{"answer_markdown": "<markdown text>"}`
* **Rendering Intent**: Clients should render `answer_markdown` directly as markdown instead of relying on a duplicated plain-text field

## 9. Metadata Persistence Layer
Sprint 7 adds a metadata-only storage path that is intentionally separated from transcript content.
* **Storage Adapter**: `metadata_store.py`
* **Integration Flow**: Route -> metadata record builder -> metadata store adapter -> Firestore collection
* **Collection Default**: `request_metadata`
* **Document Key**: `request_id`
* **Safe Fields Only**:
  * `request_id`
  * `session_id`
  * `user_id`
  * `role`
  * `timestamp`
  * `response_status`
  * `route_path`
  * `model_name`
* **Excluded by Design**:
  * raw user query
  * generated answer
  * markdown answer payload
  * retrieved context
* **Failure Policy**: Metadata persistence is best-effort. If Firestore write fails, `/raggy/trl` still returns the main answer safely and the failure is logged.

## 10. Internal Operational Review
Phase 1 does not expose user transcript history. It adds only minimal admin-only read paths for verification and troubleshooting.
* **List Recent Records**: `GET /internal/metadata/requests`
* **Read by Session**: `GET /internal/metadata/sessions/{session_id}`
* **Authorization Rule**: only `admin` JWT users may access these routes

## 11. Cost and Permission Rationale
Firestore was selected for Phase 1 because it fits low-volume per-request metadata writes well and avoids building custom file lifecycle logic.
* **Scale Assumption**: approximately 100 internal users
* **Cost Posture**: metadata-only records are small and free-tier friendly under light internal usage
* **IAM Guidance**: the Cloud Run service account should have only the minimum Firestore permissions needed for metadata documents
* **Retention Guidance**: keep metadata time-bounded, recommended 30 to 90 days subject to hospital governance review

---
*Status: Updated to current implementation*
