# Sprint 9 Plan: Multi-Agent Orchestration for Thai TRL Workflows

## Sprint Details
*   **Sprint Goal**: Introduce a multi-agent backend that routes requests between Thai general TRL question answering and rule-based TRL assessment workflows.
*   **Duration**: 2 Weeks
*   **Methodology**: Agile & Test-Driven Development (TDD)
*   **Standard**: ISO/IEC 29110 Basic Profile

## Definition of Done (DoD)
A ticket in this sprint is considered "Done" when:
1.  **Code is Complete**: Implementation satisfies all Acceptance Criteria.
2.  **TDD Confirmed**: Routing, orchestration, and evidence extraction tests pass locally via `pytest`.
3.  **Deterministic Control Preserved**: The rule evaluator remains the final authority for TRL assessment outcomes.
4.  **Documentation Synced**: Multi-agent architecture and workflow sequencing are updated in `SI/02_Software_Design/`.

---

## Sprint Backlog

### Ticket 9.1: Target Architecture Definition (2 Story Points)
*   **Description**: Define the backend target architecture for the orchestrator, QA agent, assessment interpretation agent, rule evaluator, and follow-up question generator.
*   **Acceptance Criteria**:
    *   Roles and responsibilities are defined for each component.
    *   Major request flows are documented for both `general_qa` and `trl_assessment`.
    *   Failure-handling paths are identified.
    *   Architecture traceability is recorded against the updated requirements.

### Ticket 9.2: Intent Router Implementation (3 Story Points)
*   **Description**: Add a routing layer that identifies whether a Thai user input is a general TRL question or an assessment conversation.
*   **Acceptance Criteria (TDD)**:
    *   **RED/GREEN**: Add tests for representative Thai inputs covering `general_qa`, `trl_assessment`, and ambiguous cases.
    *   The router outputs one of the supported intents consistently.
    *   Ambiguous inputs follow a safe default or clarification path.
    *   The router is testable without external network dependency.

### Ticket 9.3: General TRL QA Agent (3 Story Points)
*   **Description**: Create a dedicated agent path for answering general TRL questions in Thai while staying constrained to TRL domain knowledge.
*   **Acceptance Criteria (TDD)**:
    *   **RED/GREEN**: Add tests expecting Thai responses and Thai off-topic redirection.
    *   Agent answers in Thai consistently.
    *   Agent remains constrained to TRL-related content.
    *   Agent can cite or summarize source-grounded content safely.

### Ticket 9.4: Assessment Interpretation Agent (5 Story Points)
*   **Description**: Create an agent that translates Thai user statements into structured evidence matching the rule schema without directly assigning a final TRL level.
*   **Acceptance Criteria (TDD)**:
    *   **RED/GREEN**: Add tests for evidence extraction from complete, incomplete, and conflicting Thai inputs.
    *   Extracted evidence maps to the agreed rule schema.
    *   Uncertain or missing evidence is marked explicitly.
    *   The agent never bypasses the rule evaluator.

### Ticket 9.5: Orchestrator Integration (5 Story Points)
*   **Description**: Integrate the router and agents into the FastAPI flow so the correct workflow is selected while the deterministic evaluator remains authoritative.
*   **Acceptance Criteria (TDD)**:
    *   **RED/GREEN**: Add integration tests for both major user flows.
    *   Orchestrator selects the correct workflow by intent.
    *   Assessment outcomes are confirmed by the rule engine rather than direct LLM judgment.
    *   Existing authentication behavior remains intact and covered by regression tests.

---

## Resource Mapping
*   **Total Sprint Effort**: 18 Story Points
*   **Documentation**: Updates to `SI/02_Software_Design/Architecture_Design.md` and sequence/workflow documentation
*   **Source Code**: Orchestrator, routing, agent modules, and API integration layers
*   **Test Logs**: Automated to `SI/05_Test_Reports/`

---
*Status: READY FOR EXECUTION*

## Implementation Note
Sprint 9 orchestration has been implemented with the following code slices:
* Intent routing in `agents/intent_router.py`
* QA agent guardrails in `agents/qa_agent.py`
* Assessment interpretation in `agents/assessment_agent.py`
* Workflow orchestration in `agents/orchestrator.py`
* API integration through `main.py` while preserving `POST /raggy/trl`
* Automated coverage in `tests/test_intent_router.py`, `tests/test_qa_agent.py`, `tests/test_assessment_agent.py`, and updated integration tests
