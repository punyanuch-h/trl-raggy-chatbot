# Sprint 8 Plan: Source Stabilization & Rule-Based TRL Foundation

## Sprint Details
*   **Sprint Goal**: Establish a trusted Thai source of truth, convert TRL criteria into a machine-readable rule base, and implement the first deterministic evaluation engine for TRL assessment.
*   **Duration**: 2 Weeks
*   **Methodology**: Agile & Test-Driven Development (TDD)
*   **Standard**: ISO/IEC 29110 Basic Profile

## Definition of Done (DoD)
A ticket in this sprint is considered "Done" when:
1.  **Code is Complete**: Implementation satisfies all Acceptance Criteria.
2.  **TDD Confirmed**: New tests for source parsing, rule validation, and deterministic evaluation pass locally via `pytest`.
3.  **Thai Source Integrity**: Authoritative TRL content in `source/` is verified readable in UTF-8 without corruption.
4.  **Documentation Synced**: Rule design and source traceability are updated in `SI/02_Software_Design/` and related PM/SI records.

---

## Sprint Backlog

### Ticket 8.1: Source Audit and Encoding Stabilization (3 Story Points)
*   **Description**: Audit authoritative files in `source/` and normalize Thai source-of-truth files into UTF-8 so the runtime and tests can consume them safely.
*   **Acceptance Criteria (TDD)**:
    *   **RED/GREEN**: Add tests proving authoritative source files can be read correctly as UTF-8.
    *   A repeatable verification method exists to detect broken Thai encoding.
    *   The team identifies and documents which files are authoritative for TRL assessment.
    *   A short source lineage note is added to PM or SI documentation.

### Ticket 8.2: Rule Base Schema Design (3 Story Points)
*   **Description**: Define a machine-readable schema for TRL assessment criteria covering all levels from 1 to 9.
*   **Acceptance Criteria (TDD)**:
    *   **RED/GREEN**: Add schema validation tests for both valid and malformed rule entries.
    *   The schema supports `required_evidence`, `optional_evidence`, `domain_notes`, and `follow_up_questions`.
    *   The schema can represent missing evidence and level-specific criteria.
    *   The schema is documented for implementation use.

### Ticket 8.3: Source-to-Rule Extraction (5 Story Points)
*   **Description**: Convert authoritative TRL criteria from `source/04_Technology Readiness Level-TRL.txt` into structured rule files that can be loaded by the application.
*   **Acceptance Criteria (TDD)**:
    *   **RED/GREEN**: Add tests proving rule files for TRL 1-9 load successfully.
    *   Every rule entry includes traceable source wording or source section references.
    *   Extraction output can be consumed by the application without manual runtime edits.
    *   Any normalization or interpretation decisions are documented.

### Ticket 8.4: Deterministic TRL Evaluation Engine (5 Story Points)
*   **Description**: Implement the core rule engine that checks collected evidence against TRL criteria and determines the highest justified level.
*   **Acceptance Criteria (TDD)**:
    *   **RED/GREEN**: Add tests proving each level 1-9 can pass with complete evidence.
    *   The evaluator returns matched level, missing evidence, and a reasoning summary.
    *   The evaluator can step down to lower levels when higher-level evidence is incomplete.
    *   The evaluator is independent from the LLM layer.

### Ticket 8.5: Thai Response Templates and Fallback Catalog (3 Story Points)
*   **Description**: Replace English-first fallback and system responses with standardized Thai templates for all user-facing situations.
*   **Acceptance Criteria (TDD)**:
    *   **RED/GREEN**: Add API and formatter tests expecting Thai fallback messages.
    *   Validation, auth, technical error, insufficient evidence, and off-topic responses are available in Thai.
    *   Response templates distinguish between QA mode and assessment mode.
    *   Output format remains safe and consistent for frontend rendering.

---

## Resource Mapping
*   **Total Sprint Effort**: 19 Story Points
*   **Documentation**: Updates to `SI/02_Software_Design/Architecture_Design.md`, requirements traceability notes, and PM source lineage records
*   **Source Code**: Project root and new rule/evaluation modules as required
*   **Source Data**: `source/04_Technology Readiness Level-TRL.txt`
*   **Test Logs**: Automated to `SI/05_Test_Reports/`

---
*Status: READY FOR EXECUTION*

## Implementation Note
Sprint 8 foundation has been implemented in code with the following delivery slices:
* UTF-8 source verification and authoritative-source manifest in `assessment/source_audit.py`
* Structured TRL 1-9 rule base in `rules/trl_rules.json`
* Deterministic evaluator in `assessment/evaluator.py`
* Thai-first response template catalog in `assessment/response_templates.py`
* Automated verification coverage in `tests/test_source_audit.py`, `tests/test_trl_rules.py`, `tests/test_trl_evaluator.py`, and `tests/test_response_templates.py`
