# TRL Source Lineage and Normalization Note

## Purpose
This note records the source-of-truth lineage for Sprint 8 and explains how the Thai TRL criteria were normalized into runtime rule files without changing the original meaning.

## Authoritative Source
* Runtime authority for TRL assessment in Sprint 8 is `source/04_Technology Readiness Level-TRL.txt`
* The file is stored as UTF-8 and is loaded explicitly with `encoding="utf-8"`
* Verification is implemented in `assessment/source_audit.py`

## Verification Method
The repeatable integrity check used by tests and runtime utilities confirms:
* the file decodes as UTF-8
* Thai characters are present
* expected Thai anchor phrases are present
* common mojibake markers such as `à¸`, `à¹`, `Ã`, and replacement characters are absent

## Normalized Runtime Output
The authoritative text is converted into `rules/trl_rules.json` for deterministic evaluation.
Each TRL entry contains:
* `required_evidence`
* `optional_evidence`
* `domain_notes`
* `follow_up_questions`
* `source_references`

## Interpretation Decisions
The runtime rule base is a normalized representation, not a verbatim copy of the source document.
The following transformations were applied intentionally:
* Long free-text criteria were split into short evidence items with stable IDs
* Domain-specific wording was preserved as short `domain_notes`
* Follow-up questions were added in Thai to support later conversational assessment work
* Source traceability was retained through section names and short source excerpts

## Difference Summary
The most important differences between the source text and the normalized rule file are structural, not semantic:
* The source file is narrative and mixed-domain
* The rule file is level-by-level and machine-readable
* Evidence expectations are expressed as boolean-checkable items for deterministic evaluation

## Change Control
Any future update to `source/04_Technology Readiness Level-TRL.txt` must trigger:
1. source integrity re-verification
2. rule review against the changed section
3. regression testing for schema loading and evaluator behavior
