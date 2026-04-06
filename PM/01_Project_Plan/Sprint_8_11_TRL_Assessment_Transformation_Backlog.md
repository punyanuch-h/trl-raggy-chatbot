# Sprint 8-11 Plan: Thai-First Multi-Agent TRL Assessment Transformation

## 1. Plan Overview
- **Initiative Name**: Raggy Bot Transformation for Thai-First TRL Assessment
- **Objective**: Transform Raggy Bot from a single-agent RAG question-answering service into a Thai-first multi-agent system focused on deterministic TRL assessment using rule-based evaluation grounded in the `source/` folder.
- **Methodology**: Agile Scrum with strict Test-Driven Development (TDD)
- **Compliance Standard**: ISO/IEC 29110 Basic Profile
- **Sprint Cadence**: 4 sprints, 2 weeks per sprint
- **Primary Delivery Focus**: Reliable TRL assessment workflow in Thai, with question-answering as a secondary capability

## 2. Business Direction and Scope
- Raggy must respond in Thai by default across normal responses, recovery messages, and clarification prompts.
- Raggy must support two primary modes:
  - General TRL question answering in Thai
  - TRL level assessment through iterative conversation with the user
- The source of truth for TRL assessment must come from files in `source/`, especially the rule-base details in `source/04_Technology Readiness Level-TRL.txt`.
- The assessment result must be determined by rules, not by unconstrained LLM judgment.
- If evidence is incomplete for a candidate level, the system must ask follow-up questions and progressively evaluate lower levels when needed.

## 3. Definition of Done for the Initiative
A sprint item is considered done only when all of the following are true:
1. Tests are written first and pass locally.
2. Acceptance criteria are satisfied with evidence.
3. Thai-language behavior is verified for user-facing output.
4. Relevant PM and SI documents are updated.
5. No regression is introduced to authentication, metadata logging, or existing API stability unless explicitly planned.

## 4. Delivery Assumptions
- Existing FastAPI service and JWT-based access control remain the delivery base.
- Backward compatibility for `POST /raggy/trl` should be preserved initially, unless a later sprint explicitly introduces versioned contracts.
- The team will convert rule content from free-text documents into machine-readable structures before depending on it for runtime decisions.

## 5. Sprint Backlog Summary

| Sprint | Theme | Primary Outcome |
| :--- | :--- | :--- |
| 8 | Foundation and Rule Base | Clean Thai source data, structured TRL rules, and deterministic evaluator skeleton |
| 9 | Multi-Agent Orchestration | Intent routing and coordinated agents for QA and assessment |
| 10 | Conversational Assessment Flow | Stateful evidence collection, follow-up questioning, and API contract refinement |
| 11 | Hardening and Release Readiness | Verification, regression safety, ISO/IEC 29110 documentation completion, and release readiness |

## 6. Sprint 8 Backlog: Foundation and Rule Base

### Sprint Goal
Establish a trusted rule base and core evaluation engine so the project can assess TRL levels deterministically from source-controlled criteria.

### Ticket 8.1: Source Audit and Encoding Stabilization
- **Description**: Audit files in `source/` and normalize Thai source-of-truth files into UTF-8 without content loss.
- **Acceptance Criteria**:
  - All source files used by the runtime can be read correctly as UTF-8.
  - A repeatable verification method exists to detect broken encoding in Thai text.
  - The team identifies which files are authoritative for TRL assessment.
  - A short data lineage note is added to PM or SI documentation.
- **Suggested Tests**:
  - Encoding read test for authoritative files
  - Snapshot test for key Thai phrases expected in the source text

### Ticket 8.2: Rule Base Schema Design
- **Description**: Define a machine-readable schema for TRL assessment criteria.
- **Acceptance Criteria**:
  - A schema is created for TRL levels 1-9.
  - The schema supports `required_evidence`, `optional_evidence`, `domain_notes`, and `follow_up_questions`.
  - The schema can represent level-specific criteria and evidence gaps.
  - Schema validation tests exist and pass.
- **Suggested Tests**:
  - Schema validation test for a valid rule file
  - Negative test for malformed rule entries

### Ticket 8.3: Source-to-Rule Extraction
- **Description**: Convert authoritative TRL criteria from `source/` into structured rule files.
- **Acceptance Criteria**:
  - Structured rule files exist for TRL 1-9.
  - Each rule entry references traceable source wording or source sections.
  - Extraction output can be loaded by the application without manual edits during runtime.
  - Differences between source text and normalized rules are documented.
- **Suggested Tests**:
  - Rule loading test
  - Traceability test confirming every level has source references

### Ticket 8.4: Deterministic TRL Evaluation Engine
- **Description**: Implement the core rule engine that decides the highest supported TRL level from collected evidence.
- **Acceptance Criteria**:
  - The evaluator checks each level against complete required evidence.
  - The evaluator returns matched level, missing evidence, and reasoning summary.
  - If the current level fails, the evaluator can evaluate lower levels.
  - The evaluator is independent of the LLM layer.
- **Suggested Tests**:
  - Pass test for each level 1-9 with complete evidence
  - Fail test when a required criterion is missing
  - Downgrade test when higher-level evidence is incomplete

### Ticket 8.5: Thai Response Templates and Fallback Catalog
- **Description**: Replace English-first messaging with standardized Thai templates for all user-facing situations.
- **Acceptance Criteria**:
  - Validation, auth, technical error, insufficient evidence, and off-topic responses are available in Thai.
  - Response templates distinguish between QA mode and assessment mode.
  - Output format remains safe for frontend rendering.
  - Existing formatter behavior is covered by tests.
- **Suggested Tests**:
  - API fallback tests expecting Thai messages
  - Formatter tests verifying Thai title and content rendering

### Sprint 8 Exit Criteria
- Deterministic rule evaluation works in isolation.
- Thai source data is stable and test-protected.
- User-facing fallback text is no longer English-first.

## 7. Sprint 9 Backlog: Multi-Agent Orchestration

### Sprint Goal
Introduce a multi-agent architecture that routes requests reliably between general TRL QA and TRL assessment workflows.

### Ticket 9.1: Target Architecture Definition
- **Description**: Design the target orchestration pattern for the multi-agent backend.
- **Acceptance Criteria**:
  - Roles are defined for orchestrator, QA agent, assessment agent, rule evaluator, and follow-up question generator.
  - Component boundaries and responsibilities are documented.
  - Interaction sequence for both major user flows is documented.
  - Failure-handling paths are defined.
- **Suggested Tests**:
  - Design review checklist completion
  - Architecture traceability mapping to requirements

### Ticket 9.2: Intent Router Implementation
- **Description**: Add a routing layer that identifies whether a request is a general TRL question or an assessment conversation.
- **Acceptance Criteria**:
  - Router outputs one of at least two intents: `general_qa` or `trl_assessment`.
  - Ambiguous inputs can be handled with a safe default or clarification path.
  - The router result is testable without network access.
  - Thai examples are included in tests.
- **Suggested Tests**:
  - Intent classification tests for representative Thai inputs
  - Ambiguous input tests

### Ticket 9.3: General TRL QA Agent
- **Description**: Create a dedicated agent path for answering general TRL questions in Thai.
- **Acceptance Criteria**:
  - Agent answers in Thai consistently.
  - Agent remains constrained to TRL domain scope.
  - Agent can cite or summarize source-grounded content.
  - Off-topic handling returns Thai redirection text.
- **Suggested Tests**:
  - Thai response tests
  - Off-topic response tests
  - Prompt contract tests

### Ticket 9.4: Assessment Interpretation Agent
- **Description**: Create an agent that converts user statements into structured evidence for the evaluator.
- **Acceptance Criteria**:
  - Extracted evidence is mapped to the rule schema.
  - Uncertain or missing evidence is marked explicitly.
  - The extraction format is deterministic enough for downstream evaluation.
  - The agent does not assign a final TRL level directly.
- **Suggested Tests**:
  - Evidence extraction tests from Thai user statements
  - Tests for incomplete and conflicting evidence

### Ticket 9.5: Orchestrator Integration
- **Description**: Integrate router and agents into the application flow while keeping the evaluator authoritative.
- **Acceptance Criteria**:
  - Orchestrator chooses the correct workflow by intent.
  - Assessment decisions are confirmed by the rule engine.
  - The orchestration path logs decisions for debugging and audit.
  - Existing authentication flow continues to work.
- **Suggested Tests**:
  - Integration tests for both user flows
  - Regression tests for auth-protected endpoint behavior

### Sprint 9 Exit Criteria
- Multi-agent workflow exists in code.
- Intent routing and orchestration are covered by automated tests.
- Rule engine remains the final authority for assessment results.

## 8. Sprint 10 Backlog: Conversational Assessment Flow

### Sprint Goal
Deliver a production-usable conversational TRL assessment flow that can gather missing evidence from users over multiple turns.

### Ticket 10.1: Assessment Session State Model
- **Description**: Design and implement the conversation state required for iterative TRL assessment.
- **Acceptance Criteria**:
  - Session state stores collected evidence, missing evidence, current candidate level, and last asked question.
  - Session state can be resumed safely using a session identifier.
  - Session state does not store more personal data than needed.
  - The state model is documented.
- **Suggested Tests**:
  - Session creation and resume tests
  - State serialization tests

### Ticket 10.2: Follow-Up Question Generator
- **Description**: Generate Thai follow-up questions based on missing evidence from the evaluator.
- **Acceptance Criteria**:
  - Questions are derived from missing criteria, not generic prompting.
  - Questions are concise, Thai-first, and understandable for non-technical users.
  - The system avoids repeating already answered questions.
  - The generated question references the evidence gap clearly enough for the user to respond.
- **Suggested Tests**:
  - Missing-evidence-to-question mapping tests
  - Repetition avoidance tests

### Ticket 10.3: Progressive Level Evaluation Flow
- **Description**: Implement the conversation logic that attempts the target level, requests missing data, and downgrades only when justified.
- **Acceptance Criteria**:
  - The system can evaluate a candidate level and determine whether to confirm, ask more, or downgrade.
  - Downgrading logic is explicit and testable.
  - The system can terminate with a best-supported level and justification.
  - The user receives a Thai explanation of why the level was assigned.
- **Suggested Tests**:
  - Multi-turn scenario tests
  - Downgrade decision tests
  - Final result explanation tests

### Ticket 10.4: API Contract Revision
- **Description**: Update the request and response contract to support multi-turn assessment without breaking clients unnecessarily.
- **Acceptance Criteria**:
  - The contract supports session-aware assessment.
  - The response can return `mode`, `assessment_result`, `missing_evidence`, and `next_question` where relevant.
  - Existing consumers have a documented migration path.
  - OpenAPI documentation is updated.
- **Suggested Tests**:
  - Contract tests for QA mode
  - Contract tests for assessment mode
  - Backward compatibility tests if legacy behavior is retained

### Ticket 10.5: Metadata and Audit Enhancement
- **Description**: Extend metadata capture to support debugging and auditability of multi-step assessments.
- **Acceptance Criteria**:
  - Metadata captures workflow mode and high-level decision status.
  - Sensitive conversation content is excluded unless explicitly approved by scope.
  - Admin review endpoints continue to function.
  - Audit fields are documented.
- **Suggested Tests**:
  - Metadata persistence tests
  - Regression tests for internal admin metadata endpoints

### Sprint 10 Exit Criteria
- End-to-end conversational TRL assessment works over multiple turns.
- API schema supports assessment state and follow-up questions.
- Metadata remains safe and useful.

## 9. Sprint 11 Backlog: Hardening and Release Readiness

### Sprint Goal
Make the transformed system release-ready through broader testing, documentation updates, and controlled release preparation.

### Ticket 11.1: Regression Test Expansion
- **Description**: Expand automated coverage to protect both QA and assessment flows.
- **Acceptance Criteria**:
  - Tests cover Thai language responses, intent routing, evaluation logic, and session flow.
  - Critical regressions from current auth and metadata behavior are covered.
  - Test execution instructions are updated.
  - Coverage targets are defined and met by team agreement.
- **Suggested Tests**:
  - Full regression suite
  - Golden-path and edge-case scenarios

### Ticket 11.2: Rule Quality Review and Domain Validation
- **Description**: Validate the structured TRL rules against the authoritative source and project expectations.
- **Acceptance Criteria**:
  - Every level 1-9 is reviewed for completeness.
  - Any interpretation decisions are documented.
  - Domain-specific caveats are captured.
  - Review evidence is stored in project documentation.
- **Suggested Tests**:
  - Traceability verification checklist
  - Sample assessment review against expected outcomes

### Ticket 11.3: Performance and Stability Hardening
- **Description**: Improve stability, predictability, and operational observability of the orchestrated system.
- **Acceptance Criteria**:
  - Failures in one agent path do not crash the whole request.
  - Timeout and fallback behavior are defined.
  - Logs are sufficient to diagnose routing and evaluation issues.
  - Operational guidance is updated.
- **Suggested Tests**:
  - Failure-path integration tests
  - Timeout simulation tests

### Ticket 11.4: ISO/IEC 29110 Documentation Completion
- **Description**: Update project documents to reflect the transformed product and completed verification evidence.
- **Acceptance Criteria**:
  - PM documents reflect sprint execution, risks, and change scope.
  - SI documents reflect updated requirements, architecture, test cases, and reports.
  - User-facing documentation reflects Thai-first assessment workflow.
  - Release summary is prepared.
- **Suggested Outputs**:
  - Updated requirements specification
  - Updated architecture design
  - Updated test cases and test reports
  - Updated user manual

### Ticket 11.5: Release Readiness Review
- **Description**: Conduct a final readiness review before pilot or production rollout.
- **Acceptance Criteria**:
  - Open defects are triaged and categorized.
  - Known limitations are documented.
  - Release go/no-go decision is recorded.
  - Rollback or mitigation notes are prepared.
- **Suggested Outputs**:
  - Release checklist
  - Final review notes

### Sprint 11 Exit Criteria
- Multi-agent Thai-first TRL assessment is verified as release-ready.
- Documentation and test evidence meet team expectations for ISO/IEC 29110 Basic Profile delivery.

## 10. Cross-Sprint Technical Enablers
- Maintain a stable module structure such as `assessment/`, `agents/`, `rules/`, `state/`, and `api/`.
- Keep deterministic logic isolated from prompt engineering.
- Preserve testability without requiring live external model calls.
- Prefer source-controlled fixtures for Thai language and TRL examples.

## 11. Cross-Sprint Risks and Mitigations

| Risk | Impact | Mitigation |
| :--- | :--- | :--- |
| Thai source encoding corruption | Incorrect rule extraction and poor UX | Normalize UTF-8 early and protect with tests |
| Over-reliance on LLM judgment | Incorrect TRL assignment | Use deterministic evaluator as final authority |
| Ambiguous user evidence | Unstable assessment result | Add structured follow-up questions and explicit uncertainty handling |
| Session state inconsistency | Broken multi-turn assessment | Add state model tests and contract tests |
| Backward compatibility break | Frontend integration disruption | Preserve endpoint behavior initially and version the contract when needed |

## 12. ISO/IEC 29110 Artifact Mapping

| Area | Expected Artifact Update |
| :--- | :--- |
| PM | Sprint plans, progress records, risk updates, scope change record |
| SI/01_Requirements_Specification | New functional and non-functional requirements for Thai-first QA and assessment |
| SI/02_Software_Design | Multi-agent architecture, state flow, evaluator design, API changes |
| SI/04_Test_Cases_and_Procedures | TDD-aligned unit, integration, and conversation test cases |
| SI/05_Test_Reports | Evidence of rule validation, regression testing, and assessment scenarios |
| SI/06_User_Manual | User flow for Thai TRL assessment and general QA |
| SI/07_Product_Release | Release summary and readiness evidence |

## 13. Ready-to-Start Recommended Build Order
1. Sprint 8 Ticket 8.1
2. Sprint 8 Ticket 8.2
3. Sprint 8 Ticket 8.3
4. Sprint 8 Ticket 8.4
5. Sprint 8 Ticket 8.5
6. Sprint 9 Ticket 9.2
7. Sprint 9 Ticket 9.4
8. Sprint 9 Ticket 9.5
9. Sprint 10 Ticket 10.1
10. Sprint 10 Ticket 10.2
11. Sprint 10 Ticket 10.3
12. Sprint 10 Ticket 10.4
13. Sprint 11 hardening and release tasks

## 14. Execution Note
- The project team should treat TRL assessment as the primary product capability and general TRL QA as a supporting capability.
- Any future change to the authoritative TRL criteria in `source/` must trigger rule review, traceability review, and regression testing before release.

---
**Plan Status**: Ready for development backlog grooming and sprint execution.
