# Hybrid Router Design and Guardrails

## Purpose
This note defines a future router design for ambiguous `/raggy/trl` requests. The goal is to improve intent classification between `general_qa` and `trl_assessment` while preserving deterministic, rule-based TRL evaluation.

The hybrid router may use deterministic rules, evidence parsing, and an optional LLM classifier fallback. The LLM classifier can only classify workflow intent. It must not assign the final TRL level.

## Decision Order
1. **Deterministic rule router**
   - Runs first for all requests.
   - Wins immediately for clear definition, comparison, and assessment requests.
   - Examples that must remain deterministic:
     - `TRL 4 คืออะไร` -> `general_qa`
     - `ช่วยอธิบายความต่างระหว่าง TRL 2 กับ TRL 3` -> `general_qa`
     - `โครงการนี้มีต้นแบบแล้ว อยู่ TRL ไหน` -> `trl_assessment`
     - target Sprint 13 early-stage project scenario -> `trl_assessment`
2. **Evidence parser signal check**
   - Runs when the deterministic router is not confident enough.
   - Uses `agents/assessment_agent.py` to detect project evidence, missing evidence, uncertainty, and early TRL signals.
   - If meaningful project evidence is present with a level-seeking question, classify as `trl_assessment`.
   - If the text is definition-style and evidence is absent, classify as `general_qa`.
3. **Optional LLM classifier fallback**
   - Runs only for unresolved ambiguous cases.
   - Returns a compact JSON classification result.
   - Cannot return `matched_level`, `candidate_level`, evidence IDs, or final assessment decisions.
   - Its output is advisory and must pass confidence and guardrail checks before use.
4. **Low-confidence fallback**
   - If all stages are low confidence, default to `general_qa` with clarification guidance.
   - If an active assessment session exists, continue `trl_assessment` to preserve session continuity.

## Deterministic Rules That Must Win
The optional LLM classifier is not allowed to override these outcomes:

- Active assessment session exists: continue assessment mode.
- Clear definition or comparison question without project context: `general_qa`.
- Clear level-seeking project-status question: `trl_assessment`.
- Explicit project evidence plus a question asking what TRL level it belongs to: `trl_assessment`.
- Router exception or classifier exception: safe fallback to `general_qa`, unless there is an active assessment session.

## LLM Classifier Contract
The classifier should return JSON only:

```json
{
  "intent": "trl_assessment",
  "confidence": 0.82,
  "reason": "The user describes project status and asks which TRL level it belongs to.",
  "needs_clarification": false
}
```

Allowed `intent` values:
- `general_qa`
- `trl_assessment`
- `ambiguous`

Field rules:
- `confidence` must be a number from `0.0` to `1.0`.
- `reason` must be short and must not include hidden chain-of-thought.
- `needs_clarification` is optional but recommended.
- Any extra field related to final TRL assignment must be ignored and logged as a classifier contract violation.

## Confidence Policy
- `confidence >= 0.80`: classifier result may be used if no deterministic rule conflicts.
- `0.50 <= confidence < 0.80`: prefer clarification or `general_qa` fallback unless evidence parser strongly supports assessment.
- `confidence < 0.50`: ignore classifier result and use low-confidence fallback.
- Invalid JSON, missing confidence, unsupported intent, or timeout: ignore classifier result.

## Assessment Guardrails
- Final TRL evaluation remains rule-based in `assessment/evaluator.py`.
- Evidence extraction remains local and testable in `agents/assessment_agent.py`.
- The LLM cannot directly set:
  - `candidate_level`
  - `matched_level`
  - `decision_status`
  - `missing_evidence`
  - session evidence state
- Assessment response wording may use deterministic assessment outputs, but not an LLM-assigned level.
- Classifier prompts must explicitly state that final TRL assignment is outside the classifier's authority.

## Fallback Behavior
- If the classifier says `ambiguous`, ask for clarification or use QA guidance.
- If deterministic router and classifier disagree, deterministic router wins.
- If evidence parser finds explicit missing or supported assessment evidence and the user asks for a level, assessment wins.
- If only generic words such as `TRL`, `ช่วยดู`, or `อธิบาย` are present, QA or clarification wins.

## Privacy and Security
- Do not send JWTs, user IDs, metadata records, retrieved chunks, or session history to the classifier.
- Send only the current user query and minimal routing instructions.
- Do not persist the raw query in metadata.
- Store only the chosen workflow mode, decision status, request id, session id, user id, and role, consistent with current metadata policy.

## Cost and Latency Considerations
- The classifier fallback should be disabled by default until a measured need exists.
- It should run only after deterministic and parser checks fail.
- Add a short timeout so classifier latency cannot block the API for long.
- Track fallback usage rate through metadata-safe counters or logs before enabling broadly.

## Risks
- Over-routing definitions to assessment can degrade QA usefulness.
- Over-routing assessments to QA can miss natural project-status requests.
- LLM classifier drift can change behavior without code changes.
- Privacy risk increases if prompts include unnecessary context.
- Cost and latency increase if the classifier runs too often.

## Test Strategy
Automated tests should cover:

- deterministic QA definition cases
- deterministic QA comparison cases
- deterministic assessment cases with project context
- target Sprint 13 early-stage project scenario
- evidence-parser assisted routing
- classifier high-confidence assessment result
- classifier high-confidence QA result
- classifier low-confidence fallback
- classifier invalid JSON fallback
- deterministic rule wins over conflicting classifier output
- active assessment session bypasses QA fallback

The classifier itself should be mocked in unit and API tests. Network-dependent tests are not required for the router contract.

## Implementation Notes for a Later Sprint
- Keep `agents/intent_router.py` as the first decision layer.
- Add a separate `agents/intent_classifier.py` only if the fallback is implemented.
- Gate classifier usage behind an environment variable such as `ENABLE_LLM_INTENT_CLASSIFIER=false`.
- Keep the classifier prompt and JSON schema small.
- Log classifier contract failures without exposing user text.

---
*Status: Design spike for Sprint 13 Ticket 13.6. Not implemented in runtime code.*
