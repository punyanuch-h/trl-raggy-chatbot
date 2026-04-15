# TRL Random QA and Assessment Manual Test Cases

## Purpose
This document converts the sample request bank in `examples/api_requests/trl_random_qa_assessment_cases.json` into manual API test cases for `POST /raggy/trl`.

Use these cases to verify that Raggy Bot can:
- answer general TRL questions in QA mode
- recognize assessment requests from natural Thai project descriptions
- complete assessment sessions across follow-up turns
- return the expected TRL level when the user provides enough evidence

## Test Data Source
- File: `examples/api_requests/trl_random_qa_assessment_cases.json`
- Endpoint: `POST /raggy/trl`
- Content-Type: `application/json`
- Authorization: `Bearer <token>`

## Preconditions
- API server is running at `http://127.0.0.1:8080`
- A valid JWT token is available in `$TOKEN`
- Request body is copied from each case in `trl_random_qa_assessment_cases.json`
- For session cases, send the turns in order using the same `session_id`

## Common Validation Rules
- QA cases should return `mode = "qa"`
- Assessment cases should return `mode = "assessment"`
- Complete assessment cases should return `assessment_result.matched_level` equal to `expected_matched_level`
- Session assessment cases should first return `decision_status = "needs_more_evidence"` and finish with `decision_status = "completed"`
- Final session assessment result should match `expected_matched_level_after_final_turn`

## QA Test Cases

| Test Case ID | Source Case ID | Input Summary | Expected Result |
| --- | --- | --- | --- |
| TRL-RQA-TC-001 | `qa_random_001` | Ask what TRL 4 means in simple Thai | Response is QA mode and explains TRL 4 |
| TRL-RQA-TC-002 | `qa_random_002` | Ask difference between TRL 5 and TRL 6 | Response is QA mode and compares the two levels |
| TRL-RQA-TC-003 | `qa_random_003` | Ask which TRL applies when there is only concept and research review | Response is QA mode and explains early-stage TRL guidance |
| TRL-RQA-TC-004 | `qa_random_004` | Ask what evidence is required for TRL 8 delivery readiness | Response is QA mode and explains TRL 8 evidence |
| TRL-RQA-TC-005 | `qa_random_005` | Ask which TRL fits a real deployed system with post-delivery tracking | Response is QA mode and relates the case to TRL 9 |

## Complete Assessment Test Cases

| Test Case ID | Source Case ID | Candidate Level | Input Evidence Summary | Expected Result |
| --- | --- | --- | --- | --- |
| TRL-RQA-TC-006 | `assessment_trl_1_complete` | 1 | Basic principles, theory, research document, literature review | Assessment completed with matched TRL 1 |
| TRL-RQA-TC-007 | `assessment_trl_2_complete` | 2 | Technology concept, hypothesis, application direction, use case | Assessment completed with matched TRL 2 |
| TRL-RQA-TC-008 | `assessment_trl_3_complete` | 3 | Proof of concept, preliminary experiment, analysis result | Assessment completed with matched TRL 3 |
| TRL-RQA-TC-009 | `assessment_trl_4_complete` | 4 | Prototype tested in lab, integrated components, lab measurement record | Assessment completed with matched TRL 4 |
| TRL-RQA-TC-010 | `assessment_trl_5_complete` | 5 | Prototype tested in relevant environment with performance and safety data | Assessment completed with matched TRL 5 |
| TRL-RQA-TC-011 | `assessment_trl_6_complete` | 6 | Prototype demonstration with relevant-environment evidence | Assessment completed with matched TRL 6 |
| TRL-RQA-TC-012 | `assessment_trl_7_complete` | 7 | System prototype tested in operational environment with real-work demo evidence | Assessment completed with matched TRL 7 |
| TRL-RQA-TC-013 | `assessment_trl_8_complete` | 8 | Real system qualified against standards and ready for delivery | Assessment completed with matched TRL 8 |
| TRL-RQA-TC-014 | `assessment_trl_9_complete` | 9 | Real system in successful operation with post-delivery evaluation report | Assessment completed with matched TRL 9 |

## Session Assessment Test Cases

| Test Case ID | Source Case ID | Session ID | Candidate Level | Turn 1 Expected | Final Expected |
| --- | --- | --- | --- | --- | --- |
| TRL-RQA-TC-015 | `assessment_trl_1_session` | `sess-random-trl-1` | 1 | Needs more evidence after basic principles are provided | Completed with matched TRL 1 after research document evidence |
| TRL-RQA-TC-016 | `assessment_trl_2_session` | `sess-random-trl-2` | 2 | Needs more evidence after concept evidence is provided | Completed with matched TRL 2 after application/use-case evidence |
| TRL-RQA-TC-017 | `assessment_trl_3_session` | `sess-random-trl-3` | 3 | Needs more evidence after proof-of-concept evidence is provided | Completed with matched TRL 3 after experiment/result evidence |
| TRL-RQA-TC-018 | `assessment_trl_4_session` | `sess-random-trl-4` | 4 | Needs more evidence after lab prototype evidence is provided | Completed with matched TRL 4 after integration and lab record evidence |
| TRL-RQA-TC-019 | `assessment_trl_5_session` | `sess-random-trl-5` | 5 | Needs more evidence after relevant-environment test evidence is provided | Completed with matched TRL 5 after performance/safety evidence |
| TRL-RQA-TC-020 | `assessment_trl_6_session` | `sess-random-trl-6` | 6 | Needs more evidence after prototype demonstration evidence is provided | Completed with matched TRL 6 after relevant-environment demonstration result |
| TRL-RQA-TC-021 | `assessment_trl_7_session` | `sess-random-trl-7` | 7 | Needs more evidence after operational-environment test evidence is provided | Completed with matched TRL 7 after real-field demonstration evidence |
| TRL-RQA-TC-022 | `assessment_trl_8_session` | `sess-random-trl-8` | 8 | Needs more evidence after certification/standard evidence is provided | Completed with matched TRL 8 after delivery-readiness evidence |
| TRL-RQA-TC-023 | `assessment_trl_9_session` | `sess-random-trl-9` | 9 | Needs more evidence after real-operation evidence is provided | Completed with matched TRL 9 after post-delivery evaluation evidence |

## Manual Execution Procedure

1. Open `examples/api_requests/trl_random_qa_assessment_cases.json`.
2. For each `qa_cases` entry, send the `request` object as the request body.
3. Confirm the response has `mode = "qa"`.
4. For each `assessment_cases` entry with `case_type = "complete_question"`, send the `request` object as the request body.
5. Confirm the response has `mode = "assessment"` and `assessment_result.matched_level` equals the case's `expected_matched_level`.
6. For each `assessment_cases` entry with `case_type = "session_followup"`, send each item in `turns` in order.
7. Confirm each turn's `assessment_result.decision_status` matches `expected_status`.
8. Confirm the final turn's `assessment_result.matched_level` equals `expected_matched_level_after_final_turn`.

## PowerShell Example

```powershell
$headers = @{
    Authorization = "Bearer $TOKEN"
    "Content-Type" = "application/json"
    "X-Request-ID" = "req-random-manual-001"
}

$body = @{
    query = "TRL 4 คืออะไร อธิบายแบบสั้นๆ ให้เข้าใจง่าย"
} | ConvertTo-Json -Depth 5

Invoke-RestMethod `
    -Uri "http://127.0.0.1:8080/raggy/trl" `
    -Method Post `
    -Headers $headers `
    -Body $body
```

## Pass Criteria
- All 5 QA cases return QA mode.
- All 9 complete assessment cases return assessment mode and the expected matched level.
- All 9 session assessment cases preserve session context and complete at the expected matched level after the final turn.

---
*Status: Added for manual verification coverage using the random TRL QA and assessment request bank.*
