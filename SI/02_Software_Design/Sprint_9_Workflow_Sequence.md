# Sprint 9 Workflow Sequence

## Component Roles
* **Orchestrator**: receives the query and selects the workflow based on router output
* **Intent Router**: classifies `general_qa` versus `trl_assessment`
* **QA Agent**: returns Thai QA output or Thai off-topic redirection
* **Assessment Interpretation Agent**: extracts structured evidence signals from Thai user statements
* **Deterministic Evaluator**: confirms the highest supported TRL and reports missing evidence

## General QA Sequence
1. User sends a question to `POST /raggy/trl`
2. JWT auth is validated
3. Intent router classifies the input as `general_qa`
4. The RAG chain retrieves source-grounded context and drafts an answer
5. The QA agent validates the response path and applies Thai guardrails
6. The API returns `answer_markdown`

## Assessment Sequence
1. User sends an assessment-style statement to `POST /raggy/trl`
2. JWT auth is validated
3. Intent router classifies the input as `trl_assessment`
4. Assessment interpretation agent maps statements into evidence IDs and signal states
5. Deterministic evaluator checks the highest supported level and downgrades when required evidence is incomplete
6. The orchestrator produces a Thai assessment summary
7. The API returns `answer_markdown`

## Failure Paths
* Missing or invalid auth returns the existing Thai auth fallback
* Invalid payload returns the existing Thai validation fallback
* Ambiguous TRL requests remain in `general_qa` with clarification guidance
* Technical exceptions return the Thai technical fallback without leaking internals
