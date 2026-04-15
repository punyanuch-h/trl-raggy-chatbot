# Architecture & Software Design: Raggy Bot

## Overview
This document describes the current implementation of Raggy Bot after the Thai-first TRL assessment transformation. The service now supports both document-grounded TRL QA and deterministic multi-turn TRL assessment through the same API endpoint.

## 1. High-Level Architecture
- **API Layer**: FastAPI application in `main.py`
- **Primary Route**: `POST /raggy/trl`
- **Retrieval Store**: Pinecone for document grounding
- **Audit Store**: Firestore for metadata-only request records
- **LLM Usage**: OpenAI via LangChain for QA generation only
- **Deterministic Assessment Core**: local `assessment/` modules and `rules/trl_rules.json`

## 2. Main Processing Paths
- **General QA Flow**:
  - request
  - JWT auth
  - intent routing
  - RBAC retriever
  - LangChain retrieval chain
  - QA agent response shaping
  - markdown response
- **Assessment Flow**:
  - request
  - JWT auth
  - intent routing or session resume
  - assessment interpretation
  - session-state merge
  - deterministic evaluator
  - follow-up question or final assessment summary
  - markdown plus structured assessment fields

## 3. Auth and RBAC Design
- Bearer auth is enforced with FastAPI security middleware.
- JWT verification uses `RS256`.
- Public key material can come from direct env values, `kid`-specific env values, or a PEM file path.
- Users resolve to either `admin` or `researcher`.
- `researcher` retrieval excludes restricted chunks from `source/private/`.

## 4. Component Responsibilities
- `agents/intent_router.py`
  - classifies TRL QA versus TRL assessment
  - flags ambiguous cases for clarification
- `agents/qa_agent.py`
  - handles off-topic redirection
  - shapes safe QA fallback behavior
- `agents/assessment_agent.py`
  - extracts evidence-like signals from Thai user statements
  - does not assign the final TRL
- `agents/orchestrator.py`
  - coordinates router and QA/assessment agent logic for non-session orchestration
- `assessment/rules.py`
  - loads and validates the structured rule base
- `assessment/evaluator.py`
  - determines the highest supported TRL from collected evidence
- `assessment/conversation.py`
  - manages assessment turn logic, follow-up generation, downgrade rules, and final summaries
- `assessment/session_state.py`
  - stores assessment state across turns
- `metadata_store.py`
  - persists safe request metadata only

## 5. Endpoint Contract
- **Request**:
  - `query`
  - optional `session_id`
  - optional `candidate_level`
- **QA Response**:
  - `answer_markdown`
  - `mode: "qa"`
- **Assessment Response**:
  - `answer_markdown`
  - `session_id`
  - `mode: "assessment"`
  - `assessment_result`
  - `missing_evidence`
  - optional `next_question`

## 6. Response Formatting Rules
- `answer_markdown` is the canonical display field for all user-facing responses.
- The formatter constrains output to safe markdown patterns suitable for frontend rendering.
- Structured assessment fields complement `answer_markdown` but do not replace it.

## 7. Assessment Design
- The authoritative TRL source is normalized into `rules/trl_rules.json`.
- Evidence is evaluated deterministically against required criteria.
- Natural Thai project descriptions can be interpreted without requiring a rigid evidence template.
- Evidence signals can distinguish supported, explicitly missing, uncertain, and unknown evidence.
- If a candidate level is not fully supported:
  - the system asks targeted Thai follow-up questions when more evidence may still be available
  - the system downgrades only when missing evidence is explicitly blocked or remains unsupported
- Assessment decisions use statuses such as:
  - `completed`
  - `needs_more_evidence`
  - `downgraded`
  - `insufficient_evidence`

## 8. Failure Isolation and Hardening
- Validation and authentication failures return polite conversational payloads.
- Router failure falls back safely to general QA handling.
- QA retrieval/orchestration failures degrade to:
  - the retrieved RAG answer when still available
  - or a Thai technical fallback message
- Assessment workflow failure preserves assessment mode and returns an assessment-specific technical fallback.
- Metadata persistence is best-effort and must not block the primary response.

## 9. Metadata and Operational Review
- Stored metadata fields:
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
- Excluded content:
  - raw query text
  - generated answer text
  - markdown payload
  - retrieved context
- Admin-only review routes:
  - `GET /internal/metadata/requests`
  - `GET /internal/metadata/sessions/{session_id}`

## 10. OpenAPI Reference
The formal API contract reference is stored in `SI/02_Software_Design/openapi.json`.

## 11. Future Router Design Note
Sprint 13 added a design spike for a possible hybrid router. The future design is documented in `SI/02_Software_Design/Hybrid_Router_Design_Guardrails.md`.

Key guardrail: any optional LLM classifier may classify workflow intent only. Final TRL assessment must remain deterministic through the local rule base and evaluator.

---
*Status: Updated to current implementation*
