# Sprint 12 Plan: QA Retrieval Reliability and Multi-Format Source Ingestion

## Sprint Details
*   **Sprint Goal**: Restore reliable Thai TRL question answering by fixing the QA retrieval flow, expanding source ingestion beyond PDF, and improving traceability for RAG-based answers.
*   **Duration**: 2 Weeks
*   **Methodology**: Agile & Test-Driven Development (TDD)
*   **Standard**: ISO/IEC 29110 Basic Profile

## Definition of Done (DoD)
A ticket in this sprint is considered "Done" when:
1.  **QA Flow is Reliable**: General TRL questions such as `TRL 4 คืออะไร` return grounded answers when matching content exists in indexed sources.
2.  **Multi-Format Ingestion Works**: The indexing pipeline can ingest supported files from `source/` including `.pdf` and `.txt` without requiring format-specific workflow changes by the user.
3.  **TDD Coverage is Present**: New and updated tests protect prompt inputs, retrieval behavior, ingestion behavior, and QA fallback conditions.
4.  **Documentation is Synced**: PM and SI documentation reflect the revised ingestion pipeline, QA flow, supported source types, and operational limitations.

---

## Sprint Backlog

### Ticket 12.1: QA Retrieval Flow Defect Fix (5 Story Points)
*   **Description**: Resolve the current QA path defect so the retrieval chain passes the correct prompt inputs and does not incorrectly fall back to insufficient evidence when relevant source content exists.
*   **Acceptance Criteria (TDD)**:
    *   **RED/GREEN**: Add or update tests covering the prompt-variable contract between the retrieval chain and the QA prompt.
    *   Queries such as `TRL 4 คืออะไร` return a grounded answer when indexed content contains the requested TRL definition.
    *   QA fallback messages are only used when retrieval genuinely returns no usable answer or the source base is insufficient.
    *   Failure logs distinguish retrieval failure, prompt-input failure, and empty-answer fallback.

### Ticket 12.2: Multi-Format Source Ingestion Pipeline (5 Story Points)
*   **Description**: Refactor the ingestion pipeline from PDF-only indexing to a source-document pipeline that supports both `.pdf` and `.txt` files in `source/`.
*   **Acceptance Criteria (TDD)**:
    *   **RED/GREEN**: Add tests for discovery, parsing, and indexing of `.txt` files alongside `.pdf` files.
    *   Files added under `source/` are selected for ingestion based on supported extensions rather than PDF-only logic.
    *   Metadata such as `access` and `source_file` remains preserved for all supported file types.
    *   Unsupported file types are skipped safely with clear logging.

### Ticket 12.3: RAG Source Grounding and Answer Safety Review (3 Story Points)
*   **Description**: Tighten the QA behavior so responses stay grounded in retrieved source chunks while making fallback messages more accurate and easier to diagnose.
*   **Acceptance Criteria (TDD)**:
    *   **RED/GREEN**: Add tests for grounded QA answers, empty-answer handling, and off-topic responses.
    *   QA fallback wording reflects the actual failure condition as closely as possible.
    *   Retrieved-source assumptions and answer boundaries remain aligned with the RAG prompt design.
    *   The user-facing response remains Thai-first and markdown-safe.

### Ticket 12.4: Reindexing and Operations Update (3 Story Points)
*   **Description**: Update the reindexing workflow and operational guidance so admins can refresh the knowledge base after adding supported source documents.
*   **Acceptance Criteria**:
    *   Reindexing supports `.pdf` and `.txt` documents from the expected source directories.
    *   Admin usage guidance explains how to add new supported files and trigger reindexing.
    *   Logging is sufficient to identify which files were discovered, indexed, skipped, or failed.
    *   Operational assumptions and limitations are documented.

### Ticket 12.5: Documentation and Verification Evidence (2 Story Points)
*   **Description**: Update project documentation and verification artifacts to reflect the revised QA and ingestion architecture.
*   **Acceptance Criteria**:
    *   PM planning artifacts reflect Sprint 12 scope and risks.
    *   SI design and user-facing documents reflect supported source formats and QA behavior.
    *   Test evidence for the new QA and ingestion flows is recorded.
    *   Known limitations and future expansion points such as `.md` or other loaders are noted.

---

## Risks and Notes
*   Prompt-variable mismatches in LangChain can silently degrade QA quality if tests only mock final `answer` payloads.
*   Adding new file loaders increases ingestion flexibility but also requires disciplined metadata normalization.
*   The current fallback message may overstate document insufficiency when the actual issue is retrieval or prompt wiring.
*   Pinecone index freshness remains a dependency; newly added files are not searchable until reindexing completes.

---

## Resource Mapping
*   **Total Sprint Effort**: 18 Story Points
*   **Documentation**: Updates across `PM/`, `SI/02_Software_Design/`, `SI/04_Test_Cases_and_Procedures/`, `SI/05_Test_Reports/`, and `SI/06_User_Manual/`
*   **Source Code**: QA orchestration, prompt integration, retrieval flow, reindexing pipeline, and document loaders
*   **Test Logs**: Automated to `SI/05_Test_Reports/`

---
*Status: READY FOR EXECUTION*
