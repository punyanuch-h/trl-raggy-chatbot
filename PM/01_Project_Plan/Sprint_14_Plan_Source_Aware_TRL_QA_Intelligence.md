# Sprint 14 Plan: Source-Aware TRL QA Intelligence

## Sprint Details
*   **Sprint Goal**: Upgrade Raggy Bot so TRL QA answers can use the refreshed `source/` knowledge files directly, especially renamed TRL definition content and the new level-comparison source, instead of falling back to "insufficient evidence" when the answer already exists locally.
*   **Duration**: 2 Weeks
*   **Methodology**: Agile & Test-Driven Development (TDD)
*   **Standard**: ISO/IEC 29110 Basic Profile

## Problem Statement
The current QA path can correctly route some user questions to `qa` mode but still return a weak fallback response:

```json
{
  "answer_markdown": "## คำตอบ TRL\n\nข้อมูลจากเอกสารอ้างอิงยังไม่เพียงพอสำหรับตอบคำถามนี้อย่างมั่นใจ กรุณาระบุคำถามใหม่ให้เฉพาะเจาะจงเกี่ยวกับ TRL",
  "mode": "qa"
}
```

This happens even for questions where the source files contain enough information, such as:

```text
ช่วยเปรียบเทียบ TRL 5 กับ TRL 6 ว่าต่างกันตรงไหน
```

The user has renamed the old authoritative TRL source from:

```text
source/04_Technology Readiness Level-TRL.txt
```

to:

```text
source/Technology_Readiness_Level_Definition.txt
```

and added a comparison-focused source:

```text
source/compare_each_level_of_trl.txt
```

The runtime, source audit, rule references, source QA fallback, and tests must now understand this richer source layout.

## Source Files In Scope
*   `source/Technology_Readiness_Level_Definition.txt`
    *   Primary source for TRL 1-9 definitions, supporting evidence, examples, and domain-specific mapping.
*   `source/compare_each_level_of_trl.txt`
    *   Source for adjacent-level and level-to-level comparison questions.
    *   Should answer questions like `TRL 5 กับ TRL 6 ต่างกันตรงไหน`.
*   `source/helper_classification_domain_of_research.txt`
    *   Helper source for classifying research domain when needed.
*   `source/helper_classification_level_trl.txt`
    *   Helper source for level classification guidance when needed.

## Target User Scenarios

### Scenario A: Definition QA
Input:

```json
{
  "query": "TRL 4 คืออะไร"
}
```

Expected behavior:
*   Route remains `qa`.
*   The system answers from `Technology_Readiness_Level_Definition.txt`.
*   The answer includes TRL 4 definition and key evidence.
*   The answer does not return the insufficient-evidence fallback.

### Scenario B: Comparison QA
Input:

```json
{
  "query": "ช่วยเปรียบเทียบ TRL 5 กับ TRL 6 ว่าต่างกันตรงไหน"
}
```

Expected behavior:
*   Route remains `qa`.
*   The system answers from `compare_each_level_of_trl.txt` or local source QA before falling back to RAG.
*   The answer clearly contrasts TRL 5 and TRL 6.
*   The answer mentions that TRL 5 focuses on component/breadboard validation in a relevant environment, while TRL 6 focuses on prototype/system demonstration in a relevant environment.

### Scenario C: Evidence Requirement QA
Input:

```json
{
  "query": "TRL 8 ต้องมีหลักฐานอะไรบ้างก่อนบอกว่าพร้อมส่งมอบ"
}
```

Expected behavior:
*   Route remains `qa`.
*   The system answers from definition/rule source content.
*   The answer lists concrete evidence needed for TRL 8.
*   It does not start an assessment session unless the user describes their own project and asks to evaluate it.

### Scenario D: Assessment Still Works
Input:

```json
{
  "query": "ช่วยประเมิน TRL ตอนนี้มีต้นแบบและทดสอบต้นแบบในห้องปฏิบัติการแล้ว",
  "candidate_level": 4
}
```

Expected behavior:
*   Route goes to `assessment`.
*   The existing deterministic assessment flow remains stable.
*   Source QA changes do not weaken Sprint 13 assessment behavior.

## Definition of Done (DoD)
A ticket in this sprint is considered "Done" when:
1.  **New Source Paths Are First-Class**: Runtime code and tests no longer depend on the old `source/04_Technology Readiness Level-TRL.txt` path.
2.  **Local Source QA Handles Deterministic TRL Questions**: Definition, comparison, evidence, and transition questions can be answered directly from source files.
3.  **RAG Is Still Available But Not Required For Simple TRL QA**: Deterministic source QA should answer high-confidence questions before the system returns fallback.
4.  **QA Tests Check Answer Quality**: Tests verify that answers are not merely non-empty, but also contain relevant TRL content and avoid fallback text when source data exists.
5.  **Reindex Guidance Is Documented**: The project documents how to reindex Pinecone after source changes.
6.  **Full Regression Suite Passes**: Existing assessment, router, API, source, and reindex tests pass after the changes.

---

## Sprint Backlog

### Ticket 14.1: Source Registry and Source Audit Refresh (3 Story Points)
*   **Description**: Replace the single hard-coded authoritative source path with a small source registry that understands the new `source/` layout.
*   **Implementation Scope**:
    *   Update `assessment/source_audit.py` to reference `source/Technology_Readiness_Level_Definition.txt`.
    *   Add registry entries for:
        *   `Technology_Readiness_Level_Definition.txt`
        *   `compare_each_level_of_trl.txt`
        *   `helper_classification_domain_of_research.txt`
        *   `helper_classification_level_trl.txt`
    *   Preserve UTF-8/Thai integrity checks.
    *   Keep compatibility clear: the old file path should no longer be required for tests.
*   **Acceptance Criteria (TDD)**:
    *   `load_authoritative_source_text()` reads `Technology_Readiness_Level_Definition.txt`.
    *   Source manifest returns all expected source files with purpose metadata.
    *   Source integrity tests pass against the renamed definition source.
    *   Missing source files fail clearly with actionable error messages.

### Ticket 14.2: Multi-Source Local QA Engine (5 Story Points)
*   **Description**: Expand `source_qa.py` from a single-level definition fallback into a deterministic local QA engine for common TRL questions.
*   **Implementation Scope**:
    *   Detect definition queries, such as `TRL 4 คืออะไร`.
    *   Detect comparison queries, such as `เปรียบเทียบ TRL 5 กับ TRL 6`, `TRL 5 ต่างจาก TRL 6`.
    *   Detect evidence requirement queries, such as `TRL 8 ต้องมีหลักฐานอะไรบ้าง`.
    *   Detect transition queries, such as `จะขยับจาก TRL 3 ไป TRL 4 ต้องมีอะไร`.
    *   Read `Technology_Readiness_Level_Definition.txt` for definition/evidence answers.
    *   Read `compare_each_level_of_trl.txt` for comparison/transition answers.
    *   Return `None` for true assessment requests so `/raggy/trl` can still use the assessment workflow.
*   **Acceptance Criteria (TDD)**:
    *   `answer_query_from_source("TRL 4 คืออะไร")` returns a Thai answer containing `TRL 4`.
    *   `answer_query_from_source("ช่วยเปรียบเทียบ TRL 5 กับ TRL 6 ว่าต่างกันตรงไหน")` returns a Thai answer containing `TRL 5`, `TRL 6`, and `ต้นแบบ` or `prototype`.
    *   `answer_query_from_source("TRL 8 ต้องมีหลักฐานอะไรบ้างก่อนบอกว่าพร้อมส่งมอบ")` returns TRL 8 evidence guidance.
    *   `answer_query_from_source("ช่วยประเมิน TRL ตอนนี้มีต้นแบบแล้ว")` returns `None`.
    *   No deterministic QA answer should return the insufficient-evidence fallback.

### Ticket 14.3: Section Extraction for TRL Definition and Comparison Files (5 Story Points)
*   **Description**: Add robust text extraction helpers so the local QA engine can pull the right section from source files without brittle full-document matching.
*   **Implementation Scope**:
    *   Implement `extract_level_section(level, text)` for TRL definition sections.
    *   Implement `extract_comparison_section(level_a, level_b, text)` for comparison sections.
    *   Support adjacent comparisons such as TRL 5 vs TRL 6.
    *   Support reversed phrasing such as TRL 6 vs TRL 5 if the source contains TRL 5 vs TRL 6.
    *   Normalize whitespace and mojibake-sensitive text safely.
    *   Keep extracted output concise enough for API answers.
*   **Acceptance Criteria (TDD)**:
    *   TRL 5 definition extraction stops before TRL 6.
    *   TRL 6 definition extraction stops before TRL 7.
    *   TRL 5 vs TRL 6 comparison extraction returns only the relevant comparison block.
    *   Reversed query order still returns a coherent comparison.
    *   Extracted text does not include unrelated levels unless needed for comparison.

### Ticket 14.4: QA Orchestration Order Upgrade (3 Story Points)
*   **Description**: Adjust `/raggy/trl` QA flow so high-confidence local source answers are attempted before expensive or unreliable retrieval fallback for deterministic TRL questions.
*   **Implementation Scope**:
    *   In the QA branch of `main.py`, call `answer_query_from_source()` before or alongside RAG when the query is deterministic.
    *   Avoid Pinecone dependency for simple definition/comparison/evidence questions.
    *   Keep RAG as fallback for open-ended TRL questions.
    *   Preserve existing QA orchestration and technical fallback behavior.
*   **Acceptance Criteria (TDD)**:
    *   API call for `ช่วยเปรียบเทียบ TRL 5 กับ TRL 6 ว่าต่างกันตรงไหน` returns `mode = qa`.
    *   API answer does not include `ข้อมูลจากเอกสารอ้างอิงยังไม่เพียงพอ`.
    *   When local source QA returns an answer, API does not require Pinecone to succeed.
    *   Existing tests for retrieval failure fallback still pass.

### Ticket 14.5: Quality-Focused API Regression Tests (5 Story Points)
*   **Description**: Upgrade QA tests so they validate answer quality, not just response shape.
*   **Implementation Scope**:
    *   Add assertions to random QA cases where the answer should be known from local source.
    *   Add tests that detect accidental fallback text.
    *   Keep broad random cases but tag deterministic QA cases separately.
    *   Add API tests for definition, comparison, and evidence requirement questions.
*   **Acceptance Criteria (TDD)**:
    *   `qa_random_002` must return an answer containing `TRL 5` and `TRL 6`.
    *   `qa_random_002` must not return the insufficient-evidence fallback.
    *   Definition QA and comparison QA pass without network/Pinecone access.
    *   Assessment API tests from Sprint 13 remain green.

### Ticket 14.6: Rule Source Reference Migration (3 Story Points)
*   **Description**: Update rule-base source references so assessment traceability points to the renamed authoritative definition file.
*   **Implementation Scope**:
    *   Update `rules/trl_rules.json` references from `source/04_Technology Readiness Level-TRL.txt` to `source/Technology_Readiness_Level_Definition.txt`.
    *   Update tests such as `tests/test_trl_rules.py` that assert the old path.
    *   Update documentation that names the old file path where it is part of current runtime behavior.
*   **Acceptance Criteria (TDD)**:
    *   Rule loading tests pass.
    *   Source reference tests assert the new definition filename.
    *   Assessment responses and source lineage remain traceable.

### Ticket 14.7: Reindex and Source Refresh Workflow Documentation (2 Story Points)
*   **Description**: Document how to refresh Pinecone after adding or renaming files in `source/`.
*   **Implementation Scope**:
    *   Add reindex instructions for source updates.
    *   Clarify that local source QA can answer deterministic questions even before Pinecone refresh, but full RAG quality still requires reindexing.
    *   Record the expected source files and their purpose.
    *   Add troubleshooting notes for fallback responses.
*   **Acceptance Criteria**:
    *   Documentation includes the reindex command used by the project.
    *   Documentation explains when fallback means missing source vs retrieval failure vs unsupported query.
    *   Documentation names all active public source files.

---

## Expected Final Behavior

For:

```json
{
  "query": "ช่วยเปรียบเทียบ TRL 5 กับ TRL 6 ว่าต่างกันตรงไหน"
}
```

Expected response shape:

```json
{
  "mode": "qa",
  "answer_markdown": "## คำตอบ TRL\n\nTRL 5 ...\n\nTRL 6 ...\n\nสรุปความต่าง ..."
}
```

Expected answer meaning:
*   TRL 5 focuses on component or breadboard validation in a relevant environment.
*   TRL 6 focuses on system/subsystem model or prototype demonstration in a relevant environment.
*   The core difference is that TRL 5 validates integrated components or subsystem behavior, while TRL 6 demonstrates a clearer prototype/system model that is closer to real use.
*   The answer should be concise, Thai-first, and grounded in `source/compare_each_level_of_trl.txt` or `source/Technology_Readiness_Level_Definition.txt`.

---

## Risks and Notes
*   The new comparison source may contain simplified wording; answers should still stay consistent with the authoritative definition file.
*   Over-aggressive source QA could answer assessment requests as QA; assessment-intent guardrails must remain active.
*   RAG/Pinecone may still need reindexing after source changes. Local source QA should reduce dependency on retrieval for deterministic questions, but it does not replace the full RAG index.
*   Existing source files may contain mojibake if they were saved with the wrong encoding. Source integrity checks should catch this clearly.
*   Tests should avoid requiring network access for deterministic source QA behavior.

---

## Resource Mapping
*   **Total Sprint Effort**: 26 Story Points
*   **Primary Source Code**: `source_qa.py`, `assessment/source_audit.py`, `main.py`, `rules/trl_rules.json`
*   **Primary Tests**: `tests/test_source_qa.py`, `tests/test_source_audit.py`, `tests/test_api.py`, `tests/test_random_api_request_cases.py`, `tests/test_trl_rules.py`
*   **Primary Source Files**: `source/Technology_Readiness_Level_Definition.txt`, `source/compare_each_level_of_trl.txt`, `source/helper_classification_domain_of_research.txt`, `source/helper_classification_level_trl.txt`
*   **Documentation**: Updates across `PM/`, `SI/02_Software_Design/`, `SI/04_Test_Cases_and_Procedures/`, and `SI/05_Test_Reports/`
*   **Verification Evidence**: Automated pytest output, API response sample, and reindex command log if Pinecone is refreshed

---

## Sprint Success Summary
Sprint 14 succeeds when Raggy Bot can answer deterministic TRL QA questions from the refreshed `source/` files, especially definition and comparison questions, without returning an insufficient-evidence fallback when the answer is already present locally. The system should still route true project-evaluation requests to the assessment workflow and preserve all Sprint 13 regression behavior.

---

## Execution Evidence
Sprint 14 implementation and documentation were completed on 2026-04-15.

Primary verification artifacts:
*   `SI/02_Software_Design/Source_Refresh_Reindex_Workflow.md`
*   `SI/04_Test_Cases_and_Procedures/Sprint_14_Source_Aware_TRL_QA_Test_Cases.md`
*   `SI/05_Test_Reports/Sprint_14_Source_Aware_TRL_QA_Test_Report.md`
*   `examples/api_requests/trl_random_qa_assessment_cases.json`

Verification commands:

```powershell
python -m pytest tests/test_random_api_request_cases.py tests/test_trl_rules.py tests/test_reindex.py -q
python -m pytest tests/test_api.py tests/test_source_qa.py tests/test_source_audit.py -q
python -m pytest tests/test_source_document_parser.py -q
```

Observed result:

```text
33 passed
40 passed
3 passed
```

`tests/test_source_document_parser.py` passed as the source-refresh parser verification set.

*Status: IMPLEMENTED AND VERIFIED*
