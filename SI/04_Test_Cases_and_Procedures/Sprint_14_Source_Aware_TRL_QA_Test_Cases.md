# Sprint 14 Source-Aware TRL QA Test Cases

## Scope
These test cases verify that Raggy Bot answers deterministic TRL QA questions from refreshed local source files and preserves assessment behavior.

## Test Cases
| ID | Area | Input | Expected result |
| --- | --- | --- | --- |
| S14-SQA-001 | Source registry | Load authoritative source text | Reads `source/Technology_Readiness_Level_Definition.txt` and passes UTF-8/Thai integrity checks |
| S14-SQA-002 | Source manifest | Request source manifest | Manifest includes definition, comparison, domain helper, and TRL level helper files |
| S14-SQA-003 | Definition QA | `TRL 4 คืออะไร` | Returns QA answer containing `TRL 4` and laboratory validation wording |
| S14-SQA-004 | Comparison QA | `ช่วยเปรียบเทียบ TRL 5 กับ TRL 6 ว่าต่างกันตรงไหน` | Returns QA answer containing `TRL 5`, `TRL 6`, and `ต้นแบบ` or `prototype`; does not return insufficient-evidence fallback |
| S14-SQA-005 | Evidence QA | `TRL 8 ต้องมีหลักฐานอะไรบ้างก่อนบอกว่าพร้อมส่งมอบ` | Returns QA answer containing `TRL 8`, `หลักฐาน`, `ผลทดสอบ`, and `พร้อมส่งมอบ` |
| S14-SQA-006 | Transition QA | `จะขยับจาก TRL 5 ไป TRL 6 ต้องมีอะไร` | Returns comparison/transition guidance from local source |
| S14-SQA-007 | Assessment guardrail | `ช่วยประเมิน TRL ให้หน่อย ตอนนี้มีต้นแบบแล้ว` | Local source QA returns `None`; API uses assessment workflow |
| S14-SQA-008 | Extraction boundary | Extract TRL 5 definition | Section stops before `TRL 6 คือ` |
| S14-SQA-009 | Reversed comparison | Extract TRL 6 vs TRL 5 | Returns coherent TRL 5 vs TRL 6 comparison block |
| S14-SQA-010 | API source-first QA | API comparison request while retriever is unavailable | Returns `mode: "qa"` without requiring Pinecone |
| S14-SQA-011 | Open-ended QA fallback | API open-ended TRL strategy question | Falls back to RAG when local source QA has no deterministic answer |
| S14-SQA-012 | Rule traceability | Load `rules/trl_rules.json` | All source references point to `source/Technology_Readiness_Level_Definition.txt` |
| S14-SQA-013 | Reindex discovery | Discover supported source files | `.txt` and `.pdf` files under `source/` are discovered, including renamed definition source |

## Automation Commands
```powershell
python -m pytest tests/test_source_audit.py tests/test_source_qa.py -q
python -m pytest tests/test_api.py tests/test_random_api_request_cases.py -q
python -m pytest tests/test_trl_rules.py tests/test_reindex.py tests/test_source_document_parser.py -q
```
