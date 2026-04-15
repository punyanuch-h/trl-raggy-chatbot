# Sprint 13 Assessment Intelligence Test Report

## Summary
Sprint 13 upgraded Raggy Bot's TRL assessment intelligence so natural Thai project descriptions can be routed to assessment mode, parsed into richer evidence states, evaluated safely, and explained clearly to users.

Verification result: **PASS**

## Execution Details
- Date: 2026-04-15
- Environment: local Windows PowerShell workspace
- Raw log: `SI/05_Test_Reports/test_log_2026-04-15_sprint13_assessment_intelligence.txt`

Command:

```powershell
python -m pytest `
  tests/test_intent_router.py `
  tests/test_assessment_agent.py `
  tests/test_trl_evaluator.py `
  tests/test_conversational_assessment.py `
  tests/test_api.py `
  tests/test_integration.py -q
```

Observed result:

```text
64 passed in 171.96s (0:02:51)
```

## Verified Scope
- Intent router keeps definition and comparison questions in `general_qa`.
- Intent router sends natural project-level questions to `trl_assessment`.
- Parser recognizes natural Thai TRL 1-3 evidence.
- Parser recognizes explicit missing evidence such as no technology development direction or no experiment.
- Evaluator distinguishes `unknown`, `missing`, and `uncertain` evidence states.
- Conversation flow downgrades safely when evidence is explicitly denied.
- Conversation flow can ask follow-up questions when evidence is simply not mentioned.
- Assessment response explains the matched level, higher-level blockers, and next action.
- API contract covers the Sprint 13 target early-stage scenario.

## Target Scenario Evidence
Target query:

```json
{
  "query": "โครงการนี้ยังอยู่ในขั้นศึกษาหลักการทางคณิตศาสตร์และทบทวนงานวิจัยที่เกี่ยวข้องเพื่อสนับสนุนสมมติฐาน โดยยังไม่มีการกำหนดแนวทางพัฒนาเทคโนโลยีหรือการทดลองใดๆ คุณว่างานของฉันอยู่ใน TRL level ไหน"
}
```

Expected and verified behavior:
- `mode = assessment`
- `candidate_level = 2`
- `matched_level = 1`
- `decision_status = downgraded`
- `missing_evidence` includes `trl_2_application_defined` with `status = missing`
- response text explains TRL 1 evidence, TRL 2 application gap, and TRL 3 experiment blocker

Automated coverage:
- `tests/test_intent_router.py`
- `tests/test_assessment_agent.py`
- `tests/test_conversational_assessment.py`
- `tests/test_api.py`

## Known Notes
- The optional LLM classifier described in Ticket 13.6 is a design spike only and is not implemented in runtime code.
- Final TRL assignment remains deterministic through `assessment/evaluator.py`.
- Raw user query text is not persisted in metadata records.

---
*Status: Sprint 13 verification evidence recorded for Ticket 13.7.*
