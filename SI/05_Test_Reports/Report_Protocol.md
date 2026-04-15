# ISO/IEC 29110 Test Reporting Protocol

## Directory Purpose
`SI/05_Test_Reports/` stores the verification evidence required by the project Definition of Done. Each sprint increment must leave behind enough information for the team to answer:
- what was tested
- when it was tested
- how it was executed
- what the outcome was

## Minimum Evidence Per Sprint
Every completed sprint ticket should leave:
- a reproducible test command
- the raw console log or a referenced log file
- a short narrative summary of scope and result
- any known warnings, exclusions, or risks

## Standard Local Test Execution
The current local baseline uses the project virtual environment in `.venv_local`.

Recommended regression command:

```powershell
& '.\.venv_local\Scripts\python.exe' -m pytest `
  tests/test_api.py `
  tests/test_integration.py `
  tests/test_conversational_assessment.py `
  tests/test_assessment_agent.py `
  tests/test_assessment_session.py `
  tests/test_intent_router.py `
  tests/test_qa_agent.py `
  tests/test_trl_evaluator.py `
  tests/test_trl_rules.py `
  tests/test_source_audit.py `
  tests/test_response_templates.py `
  tests/test_metadata_store.py `
  tests/test_prompts.py `
  tests/test_response_formatter.py -q
```

## Logging Convention
Raw logs should be saved with a timestamped name such as:
`test_log_YYYY-MM-DD_sprint11_regression.txt`

Legacy timestamped files may still exist from earlier sprints and remain valid historical evidence.

## Sprint 11 Verification Focus
Sprint 11 test evidence should explicitly cover:
- Thai-first QA responses
- deterministic TRL assessment behavior
- session resume behavior
- authentication and metadata regression safety
- failure-path hardening for routing, orchestration, and graceful fallback

## Sprint 13 Verification Focus
Sprint 13 test evidence should explicitly cover:
- smarter routing for natural Thai project-level questions
- QA preservation for definition and comparison questions
- natural Thai evidence parsing for TRL 1-3
- explicit missing evidence states for TRL 2 and TRL 3 blockers
- deterministic downgrade behavior when users deny required evidence
- response text explaining matched level, higher-level blockers, and next action
- API contract coverage for the target early-stage project scenario

## Notes
- A full suite pass is required before a sprint ticket is marked done.
- Warnings that do not fail the suite must still be recorded in the accompanying test report.
