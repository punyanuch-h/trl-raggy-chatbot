# Source Refresh and Reindex Workflow

## Purpose
This note explains how to refresh Raggy Bot after adding, renaming, or editing files in `source/`.

Sprint 14 adds deterministic local source QA for common TRL questions. That means definition, comparison, evidence, and transition questions can be answered from local files before Pinecone is consulted. Full RAG quality still depends on reindexing Pinecone after source changes.

## Active Public Source Files
| Source file | Purpose |
| --- | --- |
| `source/Technology_Readiness_Level_Definition.txt` | Authoritative TRL 1-9 definitions, evidence guidance, examples, and rule traceability |
| `source/compare_each_level_of_trl.txt` | Adjacent-level comparison and transition QA, such as TRL 5 vs TRL 6 |
| `source/helper_classification_domain_of_research.txt` | Helper source for research domain classification |
| `source/helper_classification_level_trl.txt` | Helper source for TRL level classification guidance |

Private or restricted material should remain under `source/private/` so reindexing applies admin-only metadata.

## When To Reindex
Run a full reindex when:
- a supported `.txt` or `.pdf` source file is added, renamed, removed, or edited
- `source/Technology_Readiness_Level_Definition.txt` changes
- `source/compare_each_level_of_trl.txt` changes
- source content looks correct in local QA but broader RAG answers still use stale wording

Local deterministic source QA can answer known questions before reindexing, but Pinecone retrieval will not know about changed source chunks until reindexing completes.

## Reindex Command
From the repository root:

```powershell
python reindex.py
```

The command discovers supported files under `source/` and `source/private/`, parses them, chunks them, and uploads the chunks to Pinecone.

Required environment configuration for a live reindex includes Pinecone credentials, especially:
- `PINECONE_API_KEY`
- `PINECONE_INDEX_NAME`

## Verification After Source Refresh
Run the deterministic source QA and API regression tests:

```powershell
python -m pytest tests/test_source_audit.py tests/test_source_qa.py tests/test_api.py tests/test_random_api_request_cases.py -q
```

Run rule and ingestion traceability tests:

```powershell
python -m pytest tests/test_trl_rules.py tests/test_reindex.py tests/test_source_document_parser.py -q
```

## Fallback Troubleshooting
If an answer says `ข้อมูลจากเอกสารอ้างอิงยังไม่เพียงพอ`:
- For definition, evidence, comparison, or transition questions, check whether the query pattern is supported by `source_qa.py` and whether the relevant local source file contains the section.
- For broader open-ended QA, check Pinecone connectivity and whether `python reindex.py` has been run after source changes.
- For project evaluation requests, check the router and assessment workflow instead of RAG. Assessment requests should return `mode: "assessment"` and use `rules/trl_rules.json`.
- If Thai text appears corrupted, run source audit tests and inspect encoding. Active source files must be UTF-8 and must not contain mojibake markers such as `à¸`, `à¹`, `Ã`, or replacement characters.

## Change Control
After source changes:
1. Update or add the source file under `source/`.
2. Run local source QA tests.
3. Review rule traceability if the definition source changed.
4. Run `python reindex.py` for Pinecone refresh.
5. Run API regression tests.
6. Record the verification command and result in the sprint test report.
