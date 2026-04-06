# Sprint 11 Release Readiness Review

## Review Date
- 2026-04-06

## Release Candidate
- Raggy Bot Thai-first TRL assessment service

## Decision
- Go for controlled pilot release

## Decision Basis
- core Thai QA and conversational TRL assessment flows are covered by automated regression tests
- deterministic rule evaluation remains the authority for TRL decisions
- authentication and metadata regressions are covered
- failure-path hardening now returns graceful API responses when routing or workflow components fail

## Open Defects
- No open critical defects were identified in the Sprint 11 regression scope
- Non-blocking runtime warning remains for Python `3.10.11` support horizon in `google.api_core`

## Known Limitations
- performance under concurrent production-scale load has not been benchmarked
- external LLM and retrieval dependencies are still represented by mocked tests in most automated scenarios
- timeout observability relies on application log output and fallback behavior rather than dedicated metrics dashboards

## Mitigation and Rollback Notes
- if QA orchestration fails, the service can still return safe Thai fallback responses or a retrieved RAG answer when available
- if assessment workflow execution fails, the API preserves the assessment response shape and returns an assessment technical fallback message
- pilot rollout should monitor request logs for `[WARN]` routing, retrieval, orchestration, and assessment workflow messages
- rollback path: redeploy the previous stable container revision and preserve metadata logs for incident comparison

## Recommended Follow-Up Before Broad Release
- upgrade the runtime baseline to Python `3.11+`
- add explicit timeout simulation tests and lightweight performance benchmarks
- wire operational alerts to the hardening warning paths
