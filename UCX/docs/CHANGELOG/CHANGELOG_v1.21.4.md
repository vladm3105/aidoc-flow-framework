# CHANGELOG v1.21.4

**Release Date**: 2026-03-20
**Type**: Patch

## Summary

This release consolidates recent PRD/UCX hardening work across creation, remediation, validation, AI preflight checks, and documentation alignment. It also standardizes remediation reporting to a single canonical UCX artifact per run.

## Changes

### 1. Canonical Remediation Report Consolidation

**Problem**:
Some remediation flows produced a wrapper UCX report plus a separate UCRem sidecar report containing fix YAML blocks, which caused report ambiguity and reduced reliability of auto-apply flows.

**Fix**:
- UCRem now consolidates externally referenced UCRem content into the canonical UCX remediation report body.
- Canonical output remains versioned as `{DOC_ID}.UCX_remediation_report_v{NNN}.md`.
- When sidecar and canonical report versions match, duplicate UCRem sidecar artifacts are removed.
- Consolidation regex also matches `"UCRem report generated at"` variant (without "remediation" keyword), observed with Claude Opus.

**Impact**:
- Single remediation artifact per run.
- `--apply-auto-safe` operates on fix blocks in the canonical UCX remediation report.

### 1.1 Remediation Source Protection (Report-Only Safety)

**Problem**:
Certain model/tool paths could mutate source PRD/BRD files during remediation generation, even when the command was expected to produce reports only.

**Fix**:
- `UCRemPhase.generate_fixes()` now defaults `protect_source=True`.
- Source markdown files under the target path are snapshotted before generation.
- Companion reports and hidden session files are excluded from source snapshots.
- Any unexpected source-file mutations detected after generation are automatically restored.
- A warning is emitted listing restored files when restoration occurs.

**Impact**:
- `ucx remediate <doc-path>` remains report-oriented by default.
- Source artifacts remain unchanged unless users explicitly apply fixes.

### 2. AI Probe Command and Preflight Enhancements

Added `ucx ai probe` to run shared preflight checks without running full create/review/remediate flows.

**CLI additions**:
- `ucx ai probe`
- `ucx ai probe --cli-tool <provider> --model <model>`
- `ucx ai probe --full-output`

**Preflight changes (CLI + LiteLLM clients)**:
- Phase-3 probe switched from ISO-date output validation to UTC epoch validation mapped back to UTC date.
- Preflight methods now support structured details (`return_details=True`) for diagnostic output.

### 3. PRD Creation Guardrails and Runtime Controls

PRD creation behavior was expanded with explicit runtime controls and stronger post-generation normalization.

**New environment controls**:
- `UCX_UPSTREAM_SECTION_CHARS`
- `UCX_UPSTREAM_TOTAL_CHARS`
- `UCX_PRD_LLM_AUDIT_COPY`

**Behavior updates**:
- Upstream clipping defaults to unlimited unless positive env values are set.
- LLM audit appendix capture is optional and disabled by default.
- PRD output guardrails now enforce exact `custom_fields` values:
  - `document_type: prd`
  - `artifact_type: PRD`
  - `layer: 2`
- Required Section 8 layer-separation note is injected when missing.

### 4. Creation Audit Report on Every Create Run

`ucx create` now emits a versioned UCX creation report for both success and failure paths.

**Report pattern**:
- `{DOC_ID}.UCX_creation_report_v{NNN}.md`

**Report content includes**:
- run status
- invocation parameters
- output paths
- validation metadata
- retry indicator

### 5. PRD Validation Rule Adjustments

**Validation improvements**:
- PRD Gate-05 now avoids false positives for document-level PRD references while still flagging element-style misuse.
- Section 8 layer-separation note detection updated for current canonical phrasing.
- LLM response capture validation is now conditional (only enforced when capture blocks are present).

### 6. Prompt and Documentation Alignment

Updated prompt contracts and user documentation to reflect runtime behavior and naming standards:
- PRD prompt guidance for minimum ID-family coverage thresholds.
- Explicit frontmatter contract requirements and placeholder restrictions.
- UCX review/remediation naming alignment in docs (`UCX_review_report`, `UCX_remediation_report`).
- PLAN-010 revised to v10 with canonical remediation artifact model.

## Files Changed (High-Level)

### Code
- `ucx/api/remediation.py`
- `ucx/api/creation.py`
- `ucx/cli/main.py`
- `ucx/ai/cli_client.py`
- `ucx/ai/litellm_client.py`
- `ucx/validators/prd/quality_gate.py`
- `ucx/validators/prd/schema.py`
- `ucx/validators/prd/__init__.py`

### Tests
- `tests/unit/test_remediation_consolidation.py` (new)
- `tests/unit/test_remediation_source_protection.py` (new)
- `tests/integration/test_cli.py`
- `tests/unit/test_ai.py`
- `tests/creation/test_prd_creation.py`
- `tests/validators/test_prd_validator.py`

### Documentation and Plans
- `README.md`
- `docs/HOW_TO_CREATE_PRD.md`
- `docs/HOW_TO_USE.md`
- `docs/QUICK_START.md`
- `docs/UNIFIED_CONTEXT_REVIEW.md`
- `docs/plans/PLAN-010_prd_validation.md`
- `creation/UCC_PROMPT_PRD.md`

## Validation

Focused tests executed for newly introduced remediation consolidation behavior:
- `pytest -q tests/unit/test_remediation_source_protection.py tests/unit/test_remediation_consolidation.py`
- Result: 4 passed

Integration verification for AI probe command was run previously in this change set via:
- `python3 -m pytest tests/integration/test_cli.py -q`
- `ucx ai probe --full-output --cli-tool codex`
