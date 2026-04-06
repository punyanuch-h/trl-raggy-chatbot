# Sprint 10 Plan: Conversational TRL Assessment Flow

## Sprint Details
*   **Sprint Goal**: Deliver a stateful multi-turn TRL assessment workflow that can ask Thai follow-up questions, collect missing evidence, and return a justified TRL result.
*   **Duration**: 2 Weeks
*   **Methodology**: Agile & Test-Driven Development (TDD)
*   **Standard**: ISO/IEC 29110 Basic Profile

## Definition of Done (DoD)
A ticket in this sprint is considered "Done" when:
1.  **Code is Complete**: Implementation satisfies all Acceptance Criteria.
2.  **TDD Confirmed**: Session-state, multi-turn flow, contract, and metadata tests pass locally via `pytest`.
3.  **Assessment Usability Verified**: The system can ask Thai follow-up questions and conclude with a best-supported TRL level and explanation.
4.  **Documentation Synced**: API contract, state model, and metadata behavior are updated in `SI/02_Software_Design/` and related documents.

---

## Sprint Backlog

### Ticket 10.1: Assessment Session State Model (3 Story Points)
*   **Description**: Design and implement the conversation state required for iterative TRL assessment across multiple turns.
*   **Acceptance Criteria (TDD)**:
    *   **RED/GREEN**: Add tests for session creation, resume, and state serialization.
    *   Session state stores collected evidence, missing evidence, candidate level, and last asked question.
    *   Session resume works safely through a session identifier.
    *   The state model minimizes unnecessary personal data storage.

### Ticket 10.2: Follow-Up Question Generator (3 Story Points)
*   **Description**: Generate Thai follow-up questions directly from evaluator-identified missing evidence.
*   **Acceptance Criteria (TDD)**:
    *   **RED/GREEN**: Add tests mapping missing evidence to Thai follow-up questions.
    *   Questions are concise, Thai-first, and understandable for non-technical users.
    *   The system avoids repeating already answered questions.
    *   Questions clearly indicate what information is still needed.

### Ticket 10.3: Progressive Level Evaluation Flow (5 Story Points)
*   **Description**: Implement the multi-turn logic that checks a candidate level, asks for missing evidence, and downgrades only when justified by the rules.
*   **Acceptance Criteria (TDD)**:
    *   **RED/GREEN**: Add multi-turn scenario tests covering confirm, ask-more, and downgrade paths.
    *   Downgrading logic is explicit and testable.
    *   The system can terminate with a best-supported level and justification.
    *   The final user explanation is returned in Thai.

### Ticket 10.4: API Contract Revision (5 Story Points)
*   **Description**: Update request and response contracts to support session-aware assessment while preserving a manageable migration path for existing consumers.
*   **Acceptance Criteria (TDD)**:
    *   **RED/GREEN**: Add contract tests for both QA mode and assessment mode.
    *   The contract supports session-aware assessment and returns fields such as `mode`, `assessment_result`, `missing_evidence`, and `next_question` when applicable.
    *   Backward compatibility behavior or migration guidance is documented.
    *   OpenAPI output is updated to reflect the new contract.

### Ticket 10.5: Metadata and Audit Enhancement (3 Story Points)
*   **Description**: Extend metadata handling to support debugging and audit of multi-step TRL assessments without exposing unnecessary conversation content.
*   **Acceptance Criteria (TDD)**:
    *   **RED/GREEN**: Add tests for metadata persistence and admin metadata endpoint regression.
    *   Metadata captures workflow mode and high-level decision status.
    *   Sensitive conversation content is excluded unless explicitly approved by scope.
    *   Audit fields are documented for admin review.

---

## Resource Mapping
*   **Total Sprint Effort**: 19 Story Points
*   **Documentation**: Updates to `SI/02_Software_Design/openapi.json`, `SI/02_Software_Design/Architecture_Design.md`, and audit-related design notes
*   **Source Code**: Session state, assessment flow, contract models, metadata handling
*   **Test Logs**: Automated to `SI/05_Test_Reports/`

---
*Status: READY FOR EXECUTION*
