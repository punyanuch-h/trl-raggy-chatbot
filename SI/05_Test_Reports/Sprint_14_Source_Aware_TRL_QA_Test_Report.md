# Sprint 14 Source-Aware TRL QA Test Report

## Summary
Sprint 14 upgraded TRL QA so deterministic questions can be answered from refreshed local source files before Pinecone/RAG fallback. It also migrated rule traceability to the renamed authoritative definition source and documented the source refresh/reindex workflow.

## Implemented Scope
- Source registry for active TRL files
- Multi-source local QA for definition, comparison, evidence, and transition questions
- Robust section extraction for definition and comparison sources
- API QA orchestration changed to source-first, RAG-second
- Quality-focused API fixture assertions
- Rule source reference migration
- Reindex and source refresh workflow documentation

## Verification Commands
```powershell
python -m pytest tests/test_random_api_request_cases.py tests/test_trl_rules.py tests/test_reindex.py -q
python -m pytest tests/test_api.py tests/test_source_qa.py tests/test_source_audit.py -q
python -m pytest tests/test_source_document_parser.py -q
```

## Observed Results
```text
33 passed
40 passed
3 passed
```

`tests/test_source_document_parser.py` is included in the source refresh coverage and passed as a standalone verification command.

## Manual Review Notes
- `qa_random_002` now asserts that the API answer contains `TRL 5`, `TRL 6`, and either `ต้นแบบ` or `prototype`.
- Deterministic QA cases forbid the insufficient-evidence fallback text.
- `rules/trl_rules.json` now points to `source/Technology_Readiness_Level_Definition.txt`.
- The old authoritative source path is no longer required by active source audit, source QA, rule, reindex, or random API tests.

## Status
Implemented and verified.
