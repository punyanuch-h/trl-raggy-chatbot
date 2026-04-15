# Sprint 13 TRL Assessment Intelligence Test Cases

## Purpose
This document records the regression test cases for Sprint 13. The sprint improves routing, natural Thai evidence parsing, explicit missing-evidence handling, assessment response quality, and API coverage for natural project descriptions.

## Scope
- Intent routing between `general_qa` and `trl_assessment`
- Natural Thai evidence extraction for TRL 1-3
- Explicit missing evidence for TRL 2 application and TRL 3 experiment/results
- Deterministic evaluator behavior for `supported`, `missing`, `uncertain`, and `unknown`
- User-facing assessment response quality
- API contract behavior for `/raggy/trl`

## Key Test Cases

| ID | Area | Input / Condition | Expected Result | Automated Coverage |
| --- | --- | --- | --- | --- |
| S13-TC-01 | Router QA definition | `TRL 4 คืออะไร` | Routes to `general_qa` | `tests/test_intent_router.py` |
| S13-TC-02 | Router QA comparison | `ช่วยอธิบายความต่างระหว่าง TRL 2 กับ TRL 3` | Routes to `general_qa` | `tests/test_intent_router.py` |
| S13-TC-03 | Router assessment | `โครงการนี้มีต้นแบบแล้ว อยู่ TRL ไหน` | Routes to `trl_assessment` | `tests/test_intent_router.py` |
| S13-TC-04 | Router explicit missing evidence | `ยังไม่มีการทดลองใดๆ งานฉันอยู่ TRL level ไหน` | Routes to `trl_assessment` | `tests/test_intent_router.py` |
| S13-TC-05 | Parser TRL 1 basic principles | `ศึกษาหลักการทางคณิตศาสตร์` | Supports `trl_1_basic_principles` | `tests/test_assessment_agent.py` |
| S13-TC-06 | Parser TRL 1 research review | `ทบทวนงานวิจัยที่เกี่ยวข้อง` | Supports `trl_1_documented_research` | `tests/test_assessment_agent.py` |
| S13-TC-07 | Parser TRL 2 concept | `สนับสนุนสมมติฐาน` | Supports `trl_2_concept_formulated` | `tests/test_assessment_agent.py` |
| S13-TC-08 | Parser missing TRL 2 application | `ยังไม่มีการกำหนดแนวทางพัฒนาเทคโนโลยี` | Marks `trl_2_application_defined` as `missing` | `tests/test_assessment_agent.py` |
| S13-TC-09 | Parser missing TRL 3 experiment | `ยังไม่มีการทดลองใดๆ` | Marks TRL 3 proof/result evidence as `missing` | `tests/test_assessment_agent.py` |
| S13-TC-10 | Evaluator unknown evidence | TRL 3 requested but experiments not mentioned | Asks follow-up; missing status is `unknown` | `tests/test_conversational_assessment.py` |
| S13-TC-11 | Evaluator explicit missing evidence | TRL 3 requested and experiments explicitly missing | Downgrades; no duplicate follow-up | `tests/test_conversational_assessment.py` |
| S13-TC-12 | Target scenario API | Natural early-stage Thai project description | API returns `mode = assessment`, `matched_level = 1`, `decision_status = downgraded` | `tests/test_api.py` |
| S13-TC-13 | Response quality | Target scenario answer text | Explains TRL 1 evidence, TRL 2 gap, TRL 3 experiment blocker, and next step | `tests/test_conversational_assessment.py` |

## Target Scenario
The primary Sprint 13 regression scenario is:

```json
{
  "query": "โครงการนี้ยังอยู่ในขั้นศึกษาหลักการทางคณิตศาสตร์และทบทวนงานวิจัยที่เกี่ยวข้องเพื่อสนับสนุนสมมติฐาน โดยยังไม่มีการกำหนดแนวทางพัฒนาเทคโนโลยีหรือการทดลองใดๆ คุณว่างานของฉันอยู่ใน TRL level ไหน"
}
```

Expected API-level behavior:
- `mode` is `assessment`
- `assessment_result.candidate_level` is `2`
- `assessment_result.matched_level` is `1`
- `assessment_result.decision_status` is `downgraded`
- `missing_evidence` includes `trl_2_application_defined` with `status = missing`
- `answer_markdown` mentions TRL 1 support and explains why TRL 3 is not supported without experiments

## Regression Command
Recommended Sprint 13 verification command:

```powershell
python -m pytest `
  tests/test_intent_router.py `
  tests/test_assessment_agent.py `
  tests/test_trl_evaluator.py `
  tests/test_conversational_assessment.py `
  tests/test_api.py `
  tests/test_integration.py -q
```

---
*Status: Added for Sprint 13 Ticket 13.7 documentation and verification.*
