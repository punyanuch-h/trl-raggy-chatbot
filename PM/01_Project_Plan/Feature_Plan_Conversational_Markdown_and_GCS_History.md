# Feature Plan: Conversational Markdown Response & Phased Metadata Persistence

## 1. Feature Overview
*   **Feature Goal**: Extend Raggy Bot from a single-field answer API into a more presentation-aware and auditable service that can:
    1. Return formal, markdown-compatible answers suitable for a hospital education system frontend.
    2. Persist only essential request metadata in an initial low-risk phase to support operational monitoring and basic audit needs.
*   **Methodology**: Agile (Sprint-based), ISO/IEC 29110 Basic Profile, Test-Driven Development (TDD).
*   **Planning Scope**: This feature plan introduces a controlled evolution of the current single-turn, stateless API while keeping persistence deliberately minimal in Phase 1.

## 1.1 Plain-Language Summary for Advisor Review
*   **What changes now**: The API will return cleaner markdown-ready answers and store only low-risk metadata for monitoring.
*   **What does not change now**: The chatbot still works as a single-turn TRL assistant and does not gain long-term conversational memory.
*   **What is intentionally postponed**: Full chat transcript storage, end-user history pages, advanced search, and analytics.
*   **Why this is the recommended direction**: It protects privacy, reduces cloud cost, and keeps the team focused on TRL answer quality.

---

## 2. Current-State Assessment
*   **Current API Contract**: The current route returns `{"answer_markdown": "<markdown string>"}` from `/raggy/trl`.
*   **Current Interaction Model**: The approved business requirement defines the system as a **single-turn** service with **no retained conversational memory across requests**.
*   **Current Cloud Requirement**: The approved cloud requirement defines the API as **stateless**.
*   **Current Tone Control**: The answer style is currently governed by the LangChain system prompt in `rag_prompts.py`.
*   **Current Identity Model Gap**: The backend currently derives authorization primarily from `role` and does not yet expose a stable user ownership key such as JWT `sub` for history partitioning.
*   **Current Traceability Gap**: The existing route does not yet define `session_id`, `request_id`, or correlation metadata required for reliable audit history.

---

## 3. Feasibility Decision

### 3.1 Formal Markdown Response
*   **Decision**: **Feasible without architectural risk**.
*   **Rationale**:
    *   The current LLM output is already centralized through `rag_prompts.py`, so answer style can be refined there.
    *   The API can be extended later with additional metadata such as `format`, `sources`, or `disclaimer` if a concrete client need appears.
    *   The frontend can safely render markdown if the backend contract explicitly declares the content format.
*   **Recommended Direction**:
    *   Use a single canonical field: `answer_markdown`.
    *   Do not add a duplicate plain-text `answer` field until a real consumer proves the need.
    *   Keep the serializer focused on one authored payload to avoid contract drift and extra maintenance.
    *   Introduce a stricter response template for hospital education tone, for example:
        *   short title
        *   concise explanation
        *   bullet summary
        *   formal closing note when information is incomplete

### 3.2 Metadata Persistence (Phase 1)
*   **Decision**: **Strongly recommended as the safest first step**.
*   **Rationale**:
    *   Persisting only metadata avoids storing sensitive free-text content while still giving the team visibility into usage and failures.
    *   Metadata storage does not require changing the RAG engine or introducing conversation memory.
    *   This approach minimizes privacy risk, implementation effort, and ongoing cloud cost.
*   **Architectural Caveat**:
    *   Phase 1 should not store full user question and answer content unless there is a later approved requirement.
    *   Phase 1 should not expose metadata directly to end users unless a concrete frontend use case exists.
    *   If the future requirement expands into full transcript viewing, search, or analytics, a later phase can add a richer storage model.
*   **Recommended Direction**:
    *   Store one metadata record per request.
    *   Keep the payload limited to technical and audit fields such as request identifiers, user ownership, timestamps, status, and model metadata.
    *   Treat metadata as operational telemetry, not conversation history.
    *   Use a storage abstraction so full history can be added later without changing the route contract.

---

## 4. Proposed Scope Change
This feature plan formally extends the existing requirements in the following way:

1. **Response Format Extension**:
   The API returns one markdown-compatible answer field intended for client rendering.
2. **Presentation Governance**:
   The prompt and response serializer must enforce a more formal, institution-appropriate tone for hospital education usage.
3. **History Persistence**:
   Phase 1 stores only minimal metadata records required for audit and operational visibility.
4. **Controlled State Model**:
   The API runtime remains stateless in execution, while persistence is delegated to external cloud storage.
5. **Ownership-Based Access**:
   Any persisted records must be scoped by a stable user identifier from JWT claims, not by role alone.

---

## 4.1 Review Outcome: Main Concerns To Address Before Implementation
The plan is viable, but the following items should be treated as mandatory improvements rather than optional nice-to-haves:

1. **Identity correctness must be solved first**:
   Role-based checks alone are insufficient for history retrieval. The implementation should require a stable JWT claim such as `sub` or equivalent institutional user ID.
2. **History must not become hidden conversation memory**:
   The stored transcript can support audit and UI display, but it should not be implicitly reused as prompt context unless a separate approved requirement is created.
3. **PII and sensitive content boundaries need explicit rules**:
    User queries may contain names, project titles, or regulated details. The plan should define redaction policy, retention period, and deletion workflow before production release.
4. **Retrieval scope should start at zero unless clearly needed**:
   If the immediate goal is only audit and monitoring, there is no need to build an end-user history page in Phase 1.
5. **Write failures need idempotent handling**:
   Retries, duplicate submissions, or partial failures can create duplicate history objects unless request identifiers and object naming rules are defined early.

---

## 5. Non-Functional Requirements for the New Feature
*   **Backward Compatibility**: If a future consumer needs plain text, a versioned contract or explicitly added field should be introduced only when justified by real usage.
*   **Security**: Persisted metadata records must respect JWT identity and role boundaries.
*   **Privacy**: Phase 1 must avoid storing free-text prompts, answers, or retrieved document chunks by default.
*   **Auditability**: Every persisted record should contain timestamp, role, session identifier when available, and request identifier.
*   **Maintainability**: Storage logic must be isolated behind a service module rather than embedded directly in the FastAPI route.
*   **Testability**: All new serializers, persistence adapters, and route handlers must be implemented using RED-GREEN-REFACTOR.
*   **Deterministic Ownership**: Persisted records must be partitioned by a stable identity claim such as `sub`, not by display name or role.
*   **Observability**: Failed writes, rejected reads, and serialization fallbacks must be logged with request correlation IDs.
*   **Idempotency**: Repeated submissions with the same request identifier must not create duplicate audit objects unless duplication is explicitly intended.
*   **Cost Control**: The selected storage must remain within free tier or near-zero cost for approximately 100 users under expected usage.
*   **Render Safety**: Frontend rendering must sanitize markdown output and the backend must restrict unsupported markdown constructs.

---

## 6. Definition of Done (Feature-Level)
This feature is considered complete only when:
1.  **Formal Response Ready**: The API can return markdown-compatible formal answers for TRL questions.
2.  **Contract Simplified**: The API exposes one canonical answer field with no duplicate payloads.
3.  **Metadata Persisted**: Successful question-answer exchanges write only the approved metadata schema.
4.  **No Sensitive Transcript Storage by Default**: Free-text query and answer content are excluded from Phase 1 persistence unless separately approved.
5.  **TDD Evidence**: All new tests pass and logs are exported to `SI/05_Test_Reports/`.
6.  **Documentation Synced**: Requirements, architecture, API specification, and release notes are updated in `SI/`.
7.  **Ownership Enforced**: Metadata partitioning is validated against stable JWT subject ownership.
8.  **Retention Defined**: Retention, redaction, and delete/expiry behavior are documented and approved.

---

## 7. Sprint Breakdown

## Sprint 6: Formal Markdown Response Contract
*   **Advisor-Friendly Purpose**: Improve answer presentation quality without changing the core TRL reasoning pipeline.
*   **Sprint Goal**: Upgrade the answer model and prompt behavior so Raggy Bot can produce markdown-compatible, formal responses for hospital education workflows.
*   **Duration**: 2 Weeks
*   **Methodology**: Agile + TDD

### Ticket 6.1: Approve the New Answer Format (2 Story Points)
*   **Description**: Update business and technical requirements to permit markdown delivery and frontend rendering.
*   **Acceptance Criteria (TDD/ISO)**:
    *   Requirements documents in `SI/01_Requirements_Specification/` are updated.
    *   The feature remains explicitly scoped as single-turn retrieval, not multi-turn memory.
    *   API contract change rationale is documented.

### Ticket 6.2: Add Canonical Markdown Output (3 Story Points)
*   **Description**: Extend the FastAPI response model to support formal markdown-compatible output with a single canonical field.
*   **Acceptance Criteria (TDD)**:
    *   **RED**: Write failing API tests for a response containing `answer_markdown`.
    *   **GREEN**: Implement the new response model and serializer.
    *   **REFACTOR**: Centralize response formatting in a dedicated helper/service module.
    *   The route returns only `answer_markdown` to keep the contract unambiguous.

### Ticket 6.3: Make the Answer Style More Formal and Consistent (3 Story Points)
*   **Description**: Refine `rag_prompts.py` so answers remain grounded in retrieved context while using a more formal style appropriate for the hospital education department.
*   **Acceptance Criteria**:
    *   Prompt explicitly instructs markdown-safe structure.
    *   Missing-information responses remain polite and controlled.
    *   Tone evaluation checklist is updated in `SI/04_Test_Cases_and_Procedures/`.

### Ticket 6.4: Define Safe Markdown Rules for Frontend Display (3 Story Points)
*   **Description**: Define what markdown constructs are allowed and ensure backend output stays predictable for frontend rendering.
*   **Acceptance Criteria (TDD)**:
    *   **RED**: Add tests asserting headings, bullets, and paragraph structure for formal TRL answers.
    *   **GREEN**: Implement post-processing or prompt-guard logic as needed.
    *   Output excludes unsafe or unnecessary markdown constructs.
    *   Output policy explicitly disallows raw HTML, inline scripts, tables unless approved, and unbounded heading depth.

### Ticket 6.5: Update API Documents and Regression Tests (2 Story Points)
*   **Description**: Regenerate and document the updated OpenAPI specification and ensure the simplified contract stays stable.
*   **Acceptance Criteria**:
    *   `SI/02_Software_Design/openapi.json` reflects the updated schema.
    *   Regression tests confirm `answer_markdown` remains populated across success and fallback responses.
    *   Test evidence saved in `SI/05_Test_Reports/`.

---

## Sprint 7: Phase 1 Metadata Persistence
*   **Advisor-Friendly Purpose**: Add basic monitoring and audit visibility with minimal privacy and cost risk.
*   **Sprint Goal**: Add low-risk metadata persistence for audit and monitoring without storing full conversation content and without distracting from TRL answer accuracy work.
*   **Duration**: 2 Weeks
*   **Methodology**: Agile + TDD

### Ticket 7.1: Define What Metadata Is Safe to Store (3 Story Points)
*   **Description**: Define the persisted metadata schema and retention behavior for request audit records.
*   **Acceptance Criteria**:
    *   JSON schema includes `session_id` when available, stable `user_id` or JWT `sub`, `role`, `timestamp`, `request_id`, `response_status`, and model or route trace metadata.
    *   The schema explicitly excludes `query`, `answer`, `answer_markdown`, and retrieved context in Phase 1.
    *   Access rules for internal operational review are documented.
    *   Retention and deletion policy is documented for hospital governance review.
    *   The schema documents whether any fields require masking or exclusion for privacy reasons.

### Ticket 7.2: Build the Firestore Metadata Storage Layer (5 Story Points)
*   **Description**: Build a dedicated storage adapter for writing and reading metadata records.
*   **Acceptance Criteria (TDD)**:
    *   **RED**: Add failing unit tests for write, read-by-session, and read-list behaviors.
    *   **GREEN**: Implement a `metadata_store.py` style adapter or equivalent service layer.
    *   **REFACTOR**: Separate storage SDK concerns from route logic.
    *   The selected backend is documented with cost rationale and free-tier fit for approximately 100 users.

### Ticket 7.3: Save Metadata After Each Successful Request (3 Story Points)
*   **Description**: Persist approved metadata after the RAG response is generated.
*   **Acceptance Criteria (TDD)**:
    *   **RED**: Add failing tests proving a successful response triggers a metadata write.
    *   **GREEN**: Integrate persistence after answer generation.
    *   If metadata persistence fails, the main Q&A response still returns safely and the failure is logged.
    *   A `request_id` is generated or accepted so retries can be detected.

### Ticket 7.4: Add Internal-Only Metadata Review Access (2 Story Points)
*   **Description**: Add only the minimum secure read path required for internal verification, not a user-facing transcript history feature.
*   **Acceptance Criteria (TDD)**:
    *   **RED**: Add failing tests for authorized metadata inspection if an endpoint is required.
    *   **GREEN**: Implement an internal-only endpoint or admin-only verification path only if operationally necessary.
    *   No end-user transcript retrieval is added in Phase 1.

### Ticket 7.5: Lock Down Permissions and Budget Controls (3 Story Points)
*   **Description**: Add required storage configuration and align deployment documents with the new minimal-persistence feature.
*   **Acceptance Criteria**:
    *   Storage naming, IAM permissions, and environment variables are documented.
    *   Cloud Run service account has minimum required permissions only.
    *   Release report and architecture document are updated.
    *   Budget alert or cost monitoring guidance is documented.
    *   Lifecycle rules for automatic expiry are documented if retention is time-bounded.

---

## 8. TDD Execution Policy
For every implementation ticket above, the following sequence is mandatory:
1.  **RED**: Create or extend failing tests first in `tests/`.
2.  **GREEN**: Implement the minimum code required to satisfy the acceptance criteria.
3.  **REFACTOR**: Improve structure while preserving test pass status.
4.  **EVIDENCE**: Export execution logs to `SI/05_Test_Reports/`.
5.  **TRACEABILITY**: Update impacted design and requirement artifacts in `SI/`.

---

## 9. Sprint Documentation Output
Each sprint in this feature must produce a short, reusable summary file so the team can build final project documentation incrementally instead of reconstructing work later.

*   **Required Output Per Sprint**:
    *   One sprint summary markdown file in `SI/07_Product_Release/`
    *   One linked test evidence entry in `SI/05_Test_Reports/`
    *   One short change log section describing what was planned, completed, deferred, and learned
*   **Recommended File Names**:
    *   `SI/07_Product_Release/Sprint_6_Summary.md`
    *   `SI/07_Product_Release/Sprint_7_Summary.md`
*   **Minimum Summary Sections**:
    *   Sprint Goal
    *   Planned Tickets
    *   Completed Work
    *   Test Evidence
    *   Risks / Issues Found
    *   Deferred Items
    *   Next Sprint Preparation
*   **Documentation Rule**:
    *   The sprint summary should be updated at sprint close, not postponed until release week.

---

## 10. ISO/IEC 29110 Artifact Impact
The following artifacts must be updated during execution:
*   **Requirements**: `SI/01_Requirements_Specification/`
*   **Architecture & OpenAPI**: `SI/02_Software_Design/`
*   **Test Procedures**: `SI/04_Test_Cases_and_Procedures/`
*   **Test Evidence**: `SI/05_Test_Reports/`
*   **Release Summary**: `SI/07_Product_Release/`

---

## 11. Recommended Technical Design Notes
*   **Response Contract**:
    *   Use `answer_markdown: str`
    *   Keep the authored response in one field only
    *   Optionally add `format: "markdown"` later if a client needs explicit content typing
    *   Consider optional metadata fields such as `request_id`, `session_id`, and `sources`
*   **Recommended Phase 1 Metadata Fields**:
    *   `request_id`
    *   `timestamp`
    *   `user_id` or JWT `sub`
    *   `role`
    *   `session_id` when available
    *   `route`
    *   `model_name`
    *   `response_status`
    *   `latency_ms`
    *   `error_code` when applicable
*   **Recommended Firestore Collection Design**:
    *   Collection: `request_metadata`
    *   Document ID: `request_id`
    *   Optional secondary path later: `users/{user_id}/request_metadata/{request_id}` only if the team needs per-user partitioning in the document path
*   **Recommended Storage Choice for Phase 1**:
    *   Prefer Firestore for low-cost metadata storage because it supports per-record writes and simple queries without building file-management logic
    *   Defer GCS for transcript archives or exported logs in a later phase if needed
*   **Storage Abstraction**:
    *   Route -> Application Service -> Metadata Store Interface -> Firestore Adapter
    *   Add a separate serializer for persistence payloads so stored audit records are not tightly coupled to response DTOs
*   **Retrieval Scope for V1**:
    *   Prefer no user-facing retrieval
    *   Allow only minimal internal verification if required
    *   Defer transcript display, full-text search, and cross-session analytics
*   **Future Migration Path**:
    *   If a later phase needs transcript display, add a separate transcript store and keep the metadata store unchanged.

---

## 12. Firestore Metadata Schema Proposal
### 12.1 Phase 1 Required Fields
*   `request_id: string`
*   `timestamp: string`
*   `user_id: string`
*   `role: "admin" | "researcher"`
*   `session_id: string | null`
*   `route: string`
*   `model_name: string`
*   `response_status: "success" | "error"`
*   `latency_ms: number`
*   `error_code: string | null`

### 12.2 Optional Low-Risk Fields
*   `query_length: number`
*   `answer_length: number`
*   `client_app_version: string | null`
*   `trace_id: string | null`
*   `environment: "local" | "staging" | "production"`

### 12.3 Fields Explicitly Excluded in Phase 1
*   `query`
*   `answer_markdown`
*   retrieved document chunks
*   raw JWT
*   request headers unless separately approved for debugging

### 12.4 Example Firestore Document
```json
{
  "request_id": "req_20260404_000123",
  "timestamp": "2026-04-04T10:15:23Z",
  "user_id": "user_0142",
  "role": "researcher",
  "session_id": "sess_20260404_a1b2",
  "route": "/raggy/trl",
  "model_name": "gpt-4o-mini",
  "response_status": "success",
  "latency_ms": 1284,
  "error_code": null,
  "query_length": 146,
  "answer_length": 612,
  "client_app_version": "web-1.3.0",
  "trace_id": "trace_7f92c1",
  "environment": "production"
}
```

### 12.5 Example Query Patterns
*   Recent requests for one user ordered by latest timestamp
*   Failed requests in the last 7 days
*   Requests by route for operational monitoring
*   Requests by session for internal troubleshooting only

---

## 13. Risks & Mitigations
*   **Risk**: Markdown output becomes inconsistent across prompts.
    *   **Mitigation**: Enforce serializer-level formatting and snapshot-style response tests.
*   **Risk**: Persisted records accidentally include sensitive transcript data.
    *   **Mitigation**: Define a strict metadata schema that excludes prompt and answer text by default.
*   **Risk**: A future client may request plain text output.
    *   **Mitigation**: Add a new field or versioned response only when a real consumer requires it.
*   **Risk**: Metadata authorization is implemented with role only and leaks records across users.
    *   **Mitigation**: Require stable subject ownership in JWT claims and add negative tests for cross-user access.
*   **Risk**: Retries or duplicate submissions create duplicate audit records.
    *   **Mitigation**: Introduce `request_id`, deterministic naming rules, and duplicate-write tests.
*   **Risk**: Markdown renders unsafely or inconsistently in the frontend.
    *   **Mitigation**: Define an allowlist of supported constructs, sanitize on render, and snapshot-test serializer output.
*   **Risk**: Storage work distracts from the main TRL accuracy objective.
    *   **Mitigation**: Limit Phase 1 to metadata-only persistence and defer transcript-history features.

---

## 14. Approval Outcome
*   **Implementation Recommendation**: Proceed.
*   **Business Fit**: High.
*   **Architecture Impact**: Low to moderate and controlled in Phase 1.
*   **Priority Recommendation**: Execute Sprint 6 first, then a metadata-only Sprint 7. Defer full history storage and retrieval to a separate later phase if the product proves it is needed.

---
*Status: READY FOR REVIEW*
