# Business Requirements Specification: Raggy Bot (Current Product State)

## 1. Executive Summary
Raggy Bot is a Thai-first backend service for Technology Readiness Level work. It helps users in healthcare and education contexts by supporting:
- general TRL question answering from project documents
- deterministic TRL assessment through iterative conversation

The business objective is to reduce the time and ambiguity involved in understanding TRL criteria and judging the current readiness of a project.

## 2. System Scope
- **System Type**: headless API backend
- **Primary Interface**: REST endpoint `POST /raggy/trl`
- **Primary Output**: markdown-ready answer content for frontend rendering
- **Primary Knowledge Sources**:
  - indexed documents in `source/` and `source/private/`
  - structured rule base in `rules/trl_rules.json`
- **Primary Product Capability**: TRL assessment
- **Secondary Capability**: TRL knowledge Q&A

## 3. User Goals
- **Researcher**
  - ask TRL questions in Thai
  - understand the likely TRL of a project
  - continue an assessment across multiple turns using a session id
- **Admin**
  - access the same product capabilities with broader document visibility
  - review safe metadata for audit and troubleshooting

## 4. Authentication, Access, and Privacy
- Clients must authenticate with a JWT bearer token.
- The backend must verify access safely and avoid leaking security details.
- `researcher` users must not receive content grounded in `source/private/`.
- `admin` users may access both public and restricted TRL source content.
- Metadata storage must exclude transcript content and generated answer content.

## 5. Required Product Behavior
- The service must respond in Thai by default for user-facing guidance, fallback text, and assessment follow-up questions.
- The service must decide whether a request is:
  - TRL question answering
  - TRL assessment
- Final TRL assignment must come from deterministic rule evaluation rather than unconstrained LLM judgment.
- If evidence is incomplete, the system must ask targeted follow-up questions before confirming or downgrading the candidate TRL.
- The service must support session-aware continuation for assessment conversations.

## 6. Error Handling Expectations
- Validation, authentication, and internal workflow failures must return polite conversational payloads instead of raw framework errors.
- Failure in one workflow path should degrade gracefully rather than crash the whole request.
- Assessment failures must preserve an assessment-safe response shape when possible.

## 7. Business Success Criteria
- Researchers can obtain grounded TRL explanations in Thai.
- Researchers can complete a multi-turn TRL assessment without losing progress between turns.
- Admins can review metadata needed for operational monitoring without exposing transcripts.
- The system remains safe, auditable, and predictable enough for controlled pilot use.
