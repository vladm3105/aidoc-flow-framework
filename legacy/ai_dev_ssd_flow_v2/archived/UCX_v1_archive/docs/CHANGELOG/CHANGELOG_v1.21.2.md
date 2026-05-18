# CHANGELOG v1.21.2

**Release Date**: 2026-03-20
**Type**: Patch

## Summary

This release hardens `ucx create prd` to reduce post-create validation failures from metadata drift and malformed frontmatter.

## Changes

### 1. Prompt Composition: Framework + Project Merge

**Problem**:
Project-specific PRD prompts could replace framework prompt contracts, allowing required structural metadata rules to be omitted during generation.

**Fix**:
Creation prompt loading now merges framework PRD prompt contracts with project-specific PRD overrides.

**Behavior**:
- Framework PRD contracts are always included when available
- Project-specific prompt content is appended as overrides/context
- If only one prompt source exists, UCX uses that source

### 2. Deterministic Output Contract Injection

**Problem**:
Generated PRD output could drift from target document identity (e.g., wrong `doc_id` and element prefix).

**Fix**:
UCX now injects an explicit output contract derived from the target path before generation.

**Contract includes**:
- Target `doc_id`
- Required frontmatter fields
- Required H1 prefix
- Required Document Control `Document ID`
- Required element prefix alignment (`PRD.NN.*`)

### 3. PRD Pre-Write Guardrails

**Problem**:
Malformed or incomplete frontmatter could be written to disk and only fail later during validation.

**Fix**:
Before writing generated PRD output, UCX now normalizes:
- Required frontmatter fields: `title`, `doc_id`, `version`, `status`, `tags`
- Required tags (`prd`, `layer-2-artifact`)
- Core custom fields (`document_type`, `artifact_type`, `layer`)
- Identity consistency across frontmatter, H1, and Document Control
- Element ID doc-number prefix to target `PRD.NN.*`

### 4. Frontmatter Delimiter Tolerance

**Problem**:
YAML frontmatter delimiters with trailing spaces could be flagged as malformed.

**Fix**:
Frontmatter parsing now accepts delimiter lines with trailing whitespace.

## Files Changed

- `ucx/api/creation.py`
- `ucx/validators/common/patterns.py`
- `ucx/validators/base.py`
- `tests/creation/test_prd_creation.py`
- `README.md`
- `docs/HOW_TO_CREATE_PRD.md`
- `docs/HOW_TO_USE.md`

## Validation

Targeted regression tests for creation guardrails and prompt merging passed:
- `tests/creation/test_prd_creation.py` (selected tests)
- Result: 3 passed
