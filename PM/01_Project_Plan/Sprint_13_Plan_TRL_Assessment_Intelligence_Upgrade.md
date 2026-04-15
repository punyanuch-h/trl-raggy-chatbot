# Sprint 13 Plan: TRL Assessment Intelligence Upgrade

## Sprint Details
*   **Sprint Goal**: Improve Raggy Bot's ability to choose between QA and TRL assessment workflows, understand natural Thai project descriptions, and produce more accurate TRL assessment results without requiring users to follow a rigid input template.
*   **Duration**: 2 Weeks
*   **Methodology**: Agile & Test-Driven Development (TDD)
*   **Standard**: ISO/IEC 29110 Basic Profile

## Problem Statement
The current `/raggy/trl` endpoint can misclassify natural assessment-style user input as `general_qa`. For example, a user may describe that a project is still studying mathematical principles, reviewing related research, has no technology development approach, and has no experiments, then ask which TRL level it belongs to. A human clearly understands this as an assessment request, but the current rule-based router may send it to the QA/RAG path instead of the assessment workflow.

This sprint improves the system so users can write naturally while the backend remains safe, evidence-based, and testable.

## Target User Scenario
Input:

```json
{
  "query": "โครงการนี้ยังอยู่ในขั้นศึกษาหลักการทางคณิตศาสตร์และทบทวนงานวิจัยที่เกี่ยวข้องเพื่อสนับสนุนสมมติฐาน โดยยังไม่มีการกำหนดแนวทางพัฒนาเทคโนโลยีหรือการทดลองใดๆ คุณว่างานของฉันอยู่ใน TRL level ไหน"
}
```

Expected behavior:
*   The request is routed to `trl_assessment`, not `general_qa`.
*   The system recognizes evidence for early-stage research activity.
*   The system recognizes explicit absence of technology development and experiments.
*   The assessment response explains why the project is closer to TRL 1 than TRL 2 or TRL 3.
*   The response remains Thai-first, markdown-safe, and grounded in the rule-based assessment model.

## Definition of Done (DoD)
A ticket in this sprint is considered "Done" when:
1.  **Assessment Intent Is Correctly Routed**: Natural user questions such as "งานฉันอยู่ TRL level ไหน" are routed to `trl_assessment` when project context is present.
2.  **Evidence Extraction Is More Expressive**: The assessment parser recognizes Thai natural-language evidence for TRL 1-3 and key negative evidence signals.
3.  **Assessment Decisions Use Missing Evidence Safely**: Explicitly missing evidence such as "ยังไม่มีการทดลอง" helps prevent overestimating TRL level.
4.  **User-Facing Response Is Clear**: Assessment answers explain the matched level, why higher levels are not yet supported, and what evidence is needed next.
5.  **Regression Tests Protect Routing and Evaluation**: Unit and API tests cover QA routing, assessment routing, parser behavior, evaluator behavior, and the target user scenario.
6.  **Documentation Is Synced**: PM and SI documentation reflect the smarter routing and assessment behavior.

---

## Sprint Backlog

### Ticket 13.1: Phase 1 - Smarter Intent Router for QA vs Assessment (5 Story Points)
*   **Description**: Improve `agents/intent_router.py` so natural questions asking which TRL level a project belongs to are routed to assessment when project context or evidence-like language is present.
*   **Implementation Scope**:
    *   Add stronger assessment intent patterns such as `อยู่ TRL ไหน`, `TRL level ไหน`, `งานของฉันอยู่ระดับไหน`, `โครงการนี้อยู่ระดับไหน`, `คุณว่างานของฉันอยู่ใน TRL`, `ควรเป็น TRL อะไร`, and `ถือว่าอยู่ระดับไหน`.
    *   Add logic that prioritizes assessment when the query contains both project context and a level-seeking question.
    *   Keep definition-style questions such as `TRL 4 คืออะไร` and `อธิบาย TRL 5` in `general_qa`.
    *   Prefer assessment over QA fallback when the query asks for a TRL level and includes project status.
*   **Acceptance Criteria (TDD)**:
    *   `TRL 4 คืออะไร` routes to `general_qa`.
    *   `ช่วยอธิบายความต่างระหว่าง TRL 2 กับ TRL 3` routes to `general_qa`.
    *   `โครงการนี้มีต้นแบบแล้ว อยู่ TRL ไหน` routes to `trl_assessment`.
    *   `ยังไม่มีการทดลองใดๆ งานฉันอยู่ TRL level ไหน` routes to `trl_assessment`.
    *   The target user scenario routes to `trl_assessment`.

### Ticket 13.2: Phase 2 - Natural Thai Evidence and Negative Evidence Parser (5 Story Points)
*   **Description**: Expand `agents/assessment_agent.py` so it detects a broader set of Thai natural-language signals for TRL 1-3 and explicit missing evidence.
*   **Implementation Scope**:
    *   Map phrases such as `ศึกษาหลักการ`, `หลักการทางคณิตศาสตร์`, `ทฤษฎีพื้นฐาน`, and `องค์ความรู้พื้นฐาน` to `trl_1_basic_principles`.
    *   Map phrases such as `ทบทวนงานวิจัย`, `วรรณกรรมที่เกี่ยวข้อง`, `เอกสารวิจัย`, `paper`, and `literature review` to `trl_1_documented_research`.
    *   Map phrases such as `สมมติฐาน`, `แนวคิด`, `concept`, and `กรอบแนวคิด` to `trl_2_concept_formulated`.
    *   Map phrases such as `แนวทางพัฒนาเทคโนโลยี`, `แนวทางประยุกต์ใช้`, `use case`, and `การใช้งาน` to `trl_2_application_defined`.
    *   Map phrases such as `ทดลองเบื้องต้น`, `proof of concept`, and `ทดสอบสมมติฐาน` to `trl_3_proof_of_concept`.
    *   Map phrases such as `ผลทดลอง`, `ผลวิเคราะห์`, and `บันทึกผลทดสอบ` to `trl_3_analytical_results`.
    *   Treat phrases such as `ยังไม่มีการกำหนดแนวทางพัฒนาเทคโนโลยี` as missing evidence for `trl_2_application_defined`.
    *   Treat phrases such as `ยังไม่มีการทดลอง`, `ยังไม่ได้ทดลอง`, and `ไม่มีผลทดลอง` as missing evidence for TRL 3 proof-of-concept and analytical-result evidence.
*   **Acceptance Criteria (TDD)**:
    *   `ศึกษาหลักการทางคณิตศาสตร์` supports `trl_1_basic_principles`.
    *   `ทบทวนงานวิจัยที่เกี่ยวข้อง` supports `trl_1_documented_research`.
    *   `สนับสนุนสมมติฐาน` supports or weakly signals `trl_2_concept_formulated`.
    *   `ยังไม่มีการกำหนดแนวทางพัฒนาเทคโนโลยี` marks `trl_2_application_defined` as missing.
    *   `ยังไม่มีการทดลองใดๆ` marks `trl_3_proof_of_concept` and `trl_3_analytical_results` as missing.
    *   The target user scenario produces useful evidence signals instead of an empty evidence dictionary.

### Ticket 13.3: Phase 3 - Evidence-State Evaluation Improvements (5 Story Points)
*   **Description**: Improve the assessment evaluation flow so explicit `supported`, `missing`, and `uncertain` states are handled more meaningfully than simple boolean evidence.
*   **Implementation Scope**:
    *   Review the current boundary between `AssessmentInterpretation`, session state, and `evaluate_trl_level`.
    *   Preserve explicit missing evidence from user text instead of treating all absent evidence as unknown.
    *   Prevent follow-up questions that ask users to confirm evidence they have already explicitly denied.
    *   Use confirmed missing evidence to downgrade safely when a higher TRL level is not supported.
    *   Keep final TRL decisions deterministic and rule-based.
*   **Acceptance Criteria (TDD)**:
    *   If the user does not mention experiments, the system may ask for clarification.
    *   If the user explicitly says `ยังไม่มีการทดลอง`, the system should not overestimate TRL 3+.
    *   If TRL 1 evidence is supported and TRL 2 application evidence is explicitly missing, the system can explain why TRL 1 is the current supported level.
    *   The target user scenario returns an assessment-mode response with `matched_level` close to TRL 1.
    *   Existing assessment sessions continue to work across multiple turns.

### Ticket 13.4: Phase 4 - Assessment Response Quality Upgrade (3 Story Points)
*   **Description**: Improve assessment wording so responses explain the matched level, the evidence used, the reason higher levels are not supported, and the next useful action.
*   **Implementation Scope**:
    *   Update `assessment/conversation.py` response builders where needed.
    *   Make downgraded results more understandable for early-stage projects.
    *   Include concise explanations for why TRL 2 or TRL 3 is not supported when negative evidence is explicit.
    *   Keep markdown output compatible with `format_answer_markdown`.
*   **Acceptance Criteria (TDD)**:
    *   The response for the target user scenario includes `TRL 1`.
    *   The answer explains that the project has evidence of basic principles and research review.
    *   The answer explains that technology development direction or application is not yet defined.
    *   The answer explains that no experiment means TRL 3 is not yet supported.
    *   The answer recommends what to add to move toward TRL 2.

### Ticket 13.5: Phase 5 - Regression Test Expansion for Routing, Parser, Evaluation, and API (5 Story Points)
*   **Description**: Add tests that prevent future regressions in routing and assessment behavior.
*   **Implementation Scope**:
    *   Add or update intent router tests.
    *   Add or update assessment parser tests.
    *   Add or update evaluator/conversation tests.
    *   Add or update API tests for `/raggy/trl`.
    *   Include both positive assessment cases and QA definition cases.
*   **Acceptance Criteria (TDD)**:
    *   Router tests cover QA definition questions, assessment questions, ambiguous questions, and the target user scenario.
    *   Parser tests cover positive TRL 1-3 evidence and negative evidence.
    *   Conversation/evaluator tests cover supported, missing, uncertain, and downgraded outcomes.
    *   API test confirms the target user scenario returns `mode = assessment`.
    *   API test confirms the target user scenario returns a meaningful `assessment_result`.

### Ticket 13.6: Phase 6 - Hybrid Router Design Spike and Guardrails (3 Story Points)
*   **Description**: Design a future hybrid router that combines deterministic rules, evidence parsing, and an optional LLM classifier fallback for ambiguous cases.
*   **Implementation Scope**:
    *   Document a proposed router decision order: rule-based decision, evidence parser decision, then optional LLM classifier fallback.
    *   Define guardrails so the LLM can classify intent but cannot directly assign final TRL level.
    *   Define a compact JSON contract for any future LLM classifier.
    *   Identify when the fallback is allowed and when deterministic logic must win.
    *   Capture risks, cost implications, privacy considerations, and test strategy.
*   **Acceptance Criteria**:
    *   A design note is created or added to SI documentation.
    *   The design explicitly states that final TRL evaluation remains rule-based.
    *   The design includes a sample JSON output such as `intent`, `confidence`, and `reason`.
    *   The design includes fallback behavior for low-confidence classifications.
    *   The design is ready for implementation in a later sprint but does not block Sprint 13 delivery.

### Ticket 13.7: Documentation and Verification Evidence (2 Story Points)
*   **Description**: Update project documentation to reflect the smarter assessment flow and record verification evidence.
*   **Implementation Scope**:
    *   Update relevant PM and SI documents with the revised routing and assessment behavior.
    *   Add target scenario to user-facing examples if appropriate.
    *   Record test execution evidence after implementation.
    *   Document known limitations and remaining future work.
*   **Acceptance Criteria**:
    *   PM planning artifacts reflect Sprint 13 scope and target behavior.
    *   SI design documentation reflects improved router and parser behavior.
    *   Test cases and test reports include the target user scenario.
    *   User-facing documentation explains that users can describe project status naturally.

---

## Expected Final Behavior
For the target user scenario, the desired API response should be approximately:

```json
{
  "mode": "assessment",
  "assessment_result": {
    "candidate_level": 2,
    "matched_level": 1,
    "decision_status": "downgraded",
    "reasoning_summary": "หลักฐานรองรับ TRL 1 แต่ยังไม่ครบสำหรับ TRL 2 เนื่องจากยังไม่มีการกำหนดแนวทางพัฒนาเทคโนโลยีหรือการประยุกต์ใช้"
  }
}
```

The final `answer_markdown` should explain:
*   Why the project currently fits TRL 1.
*   Why TRL 2 is not yet fully supported.
*   Why TRL 3 is not supported because there is no experiment or proof-of-concept result.
*   What evidence should be added to progress toward TRL 2.

---

## Risks and Notes
*   Over-broad keyword matching can incorrectly route definition questions into assessment; QA and assessment examples must both be covered by tests.
*   Negative evidence must be handled carefully so the system does not confuse "not mentioned" with "confirmed missing".
*   Thai natural-language phrasing is diverse; this sprint should improve high-value common cases without pretending to solve every possible phrasing.
*   A future LLM classifier can improve ambiguity handling, but it should not replace deterministic TRL evaluation.
*   Existing sessions and metadata behavior must remain backward compatible.

---

## Resource Mapping
*   **Total Sprint Effort**: 28 Story Points
*   **Primary Source Code**: `agents/intent_router.py`, `agents/assessment_agent.py`, `assessment/conversation.py`, `assessment/evaluator.py`, `main.py`
*   **Primary Tests**: `tests/test_assessment_agent.py`, `tests/test_api.py`, and new or existing intent router and evaluator tests
*   **Documentation**: Updates across `PM/`, `SI/02_Software_Design/`, `SI/04_Test_Cases_and_Procedures/`, `SI/05_Test_Reports/`, and `SI/06_User_Manual/`
*   **Verification Evidence**: Automated test output and target scenario API response sample

---

## Sprint Success Summary
Sprint 13 succeeds when users can describe early-stage project evidence naturally and ask which TRL level they are in, while Raggy Bot reliably chooses assessment mode, extracts meaningful evidence, avoids overestimating readiness, and provides a clear Thai explanation of the result.

---
## Execution Evidence
Sprint 13 implementation and regression documentation were completed on 2026-04-15.

Primary verification artifacts:
*   `SI/04_Test_Cases_and_Procedures/Sprint_13_TRL_Assessment_Intelligence_Test_Cases.md`
*   `SI/05_Test_Reports/Sprint_13_Assessment_Intelligence_Test_Report.md`
*   `SI/05_Test_Reports/test_log_2026-04-15_sprint13_assessment_intelligence.txt`
*   `SI/02_Software_Design/Hybrid_Router_Design_Guardrails.md`

Verification command:

```powershell
python -m pytest tests/test_intent_router.py tests/test_assessment_agent.py tests/test_trl_evaluator.py tests/test_conversational_assessment.py tests/test_api.py tests/test_integration.py -q
```

Observed result:

```text
64 passed in 171.96s (0:02:51)
```

*Status: IMPLEMENTED AND VERIFIED*
