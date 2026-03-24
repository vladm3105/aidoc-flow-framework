# PLAN-014: PRD-Layer MCP Tool Namespace

**Document ID**: PLAN-014_prd_mcp_tool_namespace
**Created**: 2026-03-23
**Updated**: 2026-03-23
**Status**: Completed
**Target Version**: UCX v1.23.0
**Related Plans**: PLAN-012_prd_derived_artifact_flow.md, PLAN-013_prd_fix_plan_generalization.md

---

## Objective

Design and implement a layer-specific MCP tool namespace for the PRD SDD layer, exposing the complete PLAN-012 six-stage derived-artifact workflow as a set of discrete, agentic tools callable by AI agents via the MCP protocol.

This plan establishes the structural prototype for future SDD-layer tool namespaces (BRD, EARS, ADR, SYS, REQ) and defines the design invariants that all layer namespaces must follow.

---

## Problem Statement

Prior to this plan, the UCX MCP server exposed only generic tools with a flat `ucx_*` namespace:

```
ucx_autopilot   ucx_create   ucx_review   ucx_remediate
ucx_check_drift ucx_validate ucx_batch    ucx_status
```

These tools do not express PLAN-012 workflow structure. They:

- Do not distinguish PRD-specific stages (validate-fix, remediate-apply) from generic operations
- Do not return artifact paths in structured form, requiring agents to infer file locations
- Do not encode the `next_step` recommendation, forcing agents to reconstruct workflow ordering from prompting alone
- Do not enforce PLAN-012 contract at the tool boundary (stage validation, report-type validation)
- Cannot be auto-discovered by a layer-specific agent operating on the PRD SDD layer only
- Share namespace with tools that operate on all document types, making intent ambiguous

The result is that any agent calling `ucx_remediate` on a PRD must carry workflow knowledge in its prompt that belongs in the tool layer.

---

## Design Principles

### 1. Layer Isolation

Each SDD layer gets its own tool class and its own namespace prefix.

- PRD layer: `prd_*`
- Future: `brd_*`, `ears_*`, `adr_*`, `sys_*`, `req_*`

A layer-specific agent loads only its own namespace. Generic `ucx_*` tools remain available for cross-layer or utility operations.

### 2. Workflow Encoding at the Tool Boundary

Tool names map directly to PLAN-012 stages. The call sequence is expressed in tool names, not in system prompts:

```
prd_validate_fix → prd_review → prd_remediate → prd_remediate_apply
```

### 3. Structured Returns with Artifact Paths

Every tool that produces a file returns its output path in a structured dict. Agents never need to reconstruct paths by pattern-matching directory contents after a tool call.

Example:

```python
{
  "output_path": ".../PRD-01_platform_architecture_validation.md",
  "fixes_applied": 4,
  "next_step": "prd_review(prd_path='...')"
}
```

### 4. Next-Step Field

Every tool return includes a `next_step` field — a ready-to-call tool invocation string pointing to the recommended successor operation. Agents may execute it directly or use it as a prompt suggestion.

### 5. Contract Enforcement at the Tool Layer

PLAN-012 contract rules (stage preconditions, report-type validation) are enforced inside the tool implementation, not in agent prompts. An agent calling `prd_remediate` with a source-stage PRD receives a `ValueError` immediately, not a hallucinated success.

### 6. Shared Logic Lives in `artifact_ops`

Logic used by both MCP tools and CLI commands (UCX-ACTION block parsing, lineage metadata injection, derivation history) lives in `ucx/validators/prd/artifact_ops.py`. Neither the CLI module nor the MCP module own this logic directly.

---

## Workflow: PRD PLAN-012 Stages and Tool Mapping

The complete PLAN-012 six-stage workflow expressed as MCP tool calls:

```
Stage 1  create canonical source PRD
         → ucx create prd  (generic, no PRD-specific tool needed)

Stage 2  generate validation report
         → ucx validate prd  (generic)

Stage 3  create _validation copy with fixes
         → prd_validate_fix(source_prd_path=..., dry_run=False, max_iterations=3)

Stage 4  review _validation copy → versioned review report
         → prd_review(prd_path=...)

Stage 5  generate fix proposals → versioned remediation report
         → prd_remediate(validation_prd_path=..., review_report_path=...)

Stage 6  apply fixes → _remediated copy
         → prd_remediate_apply(validation_prd_path=..., remediation_report_path=...)
```

Discovery tools (callable at any point):

```
prd_artifacts(prd_dir=...)   → classify all artifacts in a directory
prd_status(prd_dir=...)      → stage completion with next_step recommendation
```

---

## Tool Specifications

### `prd_validate_fix`

**Stage**: 3

**Preconditions**:
- `source_prd_path` must exist
- `identify_prd_artifact_stage(source_prd_path)` must return `"source"`

**Failure modes**:
- `FileNotFoundError` — input does not exist
- `ValueError` — input is not stage `"source"` (e.g. `_validation` or `_remediated` copy passed by mistake)

**Inputs**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `source_prd_path` | str | required | Path to canonical source PRD |
| `dry_run` | bool | `False` | Show output path only; do not write |
| `max_iterations` | int | `3` | Maximum validate/fix loop passes |

**Returns**:

| Key | Type | Description |
|-----|------|-------------|
| `output_path` | str \| None | Written file path; None when dry_run |
| `output_path_preview` | str | Expected output path in all cases |
| `fixes_applied` | int | Auto-fixes applied during loop |
| `iterations_run` | int | Actual loop iterations |
| `remaining_issue_count` | int | Issues not resolved after loop |
| `dry_run` | bool | Echoed flag |
| `processing_stage` | str | Always `"validation-fixed"` |
| `source_doc_id` | str | Parsed doc_id from source PRD |
| `next_step` | str | Ready-to-call `prd_review(...)` string |

**Filename rule**: `{source_stem}_validation.md` via `prd_validation_copy_name()`

**Metadata injected**:
```yaml
custom_fields:
  processing_stage: validation-fixed
  source_doc_id: PRD-01
  source_version: 0.1.0
  derived_from: PRD-01_platform_architecture.md
```

---

### `prd_review`

**Stage**: 4

**Auto-redirect**: If a source-stage PRD is passed, `resolve_prd_review_target()` locates the corresponding `_validation` copy automatically. No error is raised.

**Inputs**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prd_path` | str | required | Path to `_validation` PRD (or source—auto-redirected) |

**Returns**:

| Key | Type | Description |
|-----|------|-------------|
| `score` | int | UCR review score 0–100 |
| `status` | str | Review status value |
| `report_path` | str | Versioned review report path |
| `findings` | dict | `{"P0": N, "P1": N, "P2": N}` |
| `has_critical` | bool | True if P0 findings exist |
| `total_findings` | int | Sum across all priorities |
| `validation_prd_path` | str | Resolved `_validation` copy path |
| `elapsed_time` | float | Seconds elapsed |
| `next_step` | str | Ready-to-call `prd_remediate(...)` string |

**Report naming**: Versioned via existing `_get_versioned_output_path()` — `*.UCX_review_report_vNNN.md`

---

### `prd_remediate`

**Stage**: 5

**Preconditions** (PLAN-012 contract, enforced by `UCRemPhase._enforce_prd_remediation_contract()`):
- `validation_prd_path` must have `processing_stage: validation-fixed`
- `review_report_path` filename must contain `.UCX_review_report_`

**Failure modes**:
- `FileNotFoundError` — either input missing
- `ValueError` — stage or report-type contract violated

**Inputs**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `validation_prd_path` | str | required | Path to `_validation` PRD |
| `review_report_path` | str | required | Path to `*.UCX_review_report_vNNN.md` |

**Returns**:

| Key | Type | Description |
|-----|------|-------------|
| `report_path` | str | Written remediation report path |
| `fix_count` | int | Total fix proposals generated |
| `auto_safe_count` | int | AUTO_SAFE proposals |
| `manual_review_count` | int | Proposals requiring human review |
| `fixes_summary` | list[dict] | First 10 fixes (description, confidence, gate_code) |
| `next_step` | str | Ready-to-call `prd_remediate_apply(...)` string |

**Report naming**: Versioned — `*.UCX_remediation_report_vNNN.md`

---

### `prd_remediate_apply`

**Stage**: 6

**Preconditions**:
- `validation_prd_path` must have `processing_stage: validation-fixed`
- `remediation_report_path` must exist

**Failure modes**:
- `FileNotFoundError` — either input missing
- `ValueError` — input is not stage `"validation-fixed"`

**Inputs**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `validation_prd_path` | str | required | Path to `_validation` PRD |
| `remediation_report_path` | str | required | Path to `*.UCX_remediation_report_vNNN.md` |
| `dry_run` | bool | `False` | Show output path only; do not write |

**Returns**:

| Key | Type | Description |
|-----|------|-------------|
| `output_path` | str \| None | Written file path; None when dry_run |
| `output_path_preview` | str | Expected output path in all cases |
| `fixes_applied` | int | UCX-ACTION blocks applied |
| `processing_stage` | str | Always `"remediated"` |
| `derived_from` | str | Name of `_validation` PRD |
| `dry_run` | bool | Echoed flag |
| `next_step` | str | Promotion guidance or dry-run note |

**Filename rule**: `{validation_stem_without_validation_suffix}_remediated.md` via `prd_remediated_copy_name()`

**Metadata injected**:
```yaml
custom_fields:
  processing_stage: remediated
  source_doc_id: PRD-01
  source_version: 0.1.0
  derived_from: PRD-01_platform_architecture_validation.md
```

---

### `prd_artifacts`

**Purpose**: Discovery — classify all PLAN-012 artifacts in a directory.

**Inputs**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `prd_dir` | str | Path to PRD document directory |

**Classification rules** (applied in order):

1. Filename contains `.UCX_review_report_v` → review report
2. Filename contains `.UCX_remediation_report_v` → remediation report
3. Filename ends with `_validation_report.md` → validation report
4. Otherwise: call `identify_prd_artifact_stage()` → source / validation-fixed / remediated

**Returns**:

| Key | Type | Description |
|-----|------|-------------|
| `source_prds` | list[str] | Source-stage PRD paths |
| `validation_copies` | list[str] | `_validation` copy paths |
| `validation_reports` | list[str] | `PRD-NN_validation_report.md` paths |
| `review_reports` | list[str] | `*.UCX_review_report_vNNN.md` paths |
| `remediation_reports` | list[str] | `*.UCX_remediation_report_vNNN.md` paths |
| `remediated_copies` | list[str] | `_remediated` copy paths |
| `total_artifacts` | int | Sum of all lists |

---

### `prd_status`

**Purpose**: Workflow stage check — determine how far the PLAN-012 flow has progressed and what to do next.

**Inputs**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `prd_dir` | str | Path to PRD document directory |

**Stage ID → Artifact criteria**:

| Stage ID | Criterion |
|----------|-----------|
| `stage-1-source-exists` | At least one source-stage PRD present |
| `stage-2-validation-report` | At least one `_validation_report.md` present |
| `stage-3-validation-copy` | At least one `_validation` copy present |
| `stage-4-review-report` | At least one `*.UCX_review_report_v*` present |
| `stage-5-remediation-report` | At least one `*.UCX_remediation_report_v*` present |
| `stage-6-remediated-copy` | At least one `_remediated` copy present |

**Returns**:

| Key | Type | Description |
|-----|------|-------------|
| `completed_stages` | list[str] | Stage IDs that are complete |
| `workflow_complete` | bool | True when stage-6 artifact exists |
| `next_step` | str | Ready-to-call tool string or completion message |
| `artifacts` | dict | Full artifact paths by category (same keys as `prd_artifacts`) |

**`next_step` decision tree**:

```
no source PRD          → guidance: create source PRD first
no validation copy     → prd_validate_fix(source_prd_path=...)
no review report       → prd_review(prd_path=...)
no remediation report  → prd_remediate(validation_prd_path=..., review_report_path=...)
no remediated copy     → prd_remediate_apply(validation_prd_path=..., remediation_report_path=...)
remediated copy exists → workflow complete; promote guidance
```

---

## Shared Utility: `apply_ucx_action_fixes`

**Location**: `ucx/validators/prd/artifact_ops.py`

**Signature**:
```python
def apply_ucx_action_fixes(content: str, report_content: str) -> dict:
```

**Purpose**: Parse `UCX-ACTION` blocks from a remediation report and apply `old_content → suggested_fix` text substitutions to a document string.

**Returns**: `{"content": str, "count": int}`

**Prior location**: This logic was duplicated in `ucx/cli/main.py` as `_apply_ucx_action_fixes()`. That function now delegates to `artifact_ops.apply_ucx_action_fixes()`. The implementation is no longer duplicated across surfaces.

**UCX-ACTION block structure parsed**:

```
<!-- UCX-ACTION[GATE-CODE] ...
old_content: |
    <text to replace>
suggested_fix: |
    <replacement text>
-->
```

Blocks without `old_content` are skipped (no-match safe). Indentation of 4+ spaces is stripped before comparison.

---

## Implementation Changes

### Files Created

| File | Purpose |
|------|---------|
| `UCX/ucx/mcp/tools_prd.py` | `PRDTools` class with 6 `prd_*` tools |

### Files Modified

| File | Change |
|------|--------|
| `UCX/ucx/validators/prd/artifact_ops.py` | Added `apply_ucx_action_fixes()` function |
| `UCX/ucx/cli/main.py` | `_apply_ucx_action_fixes()` now delegates to `artifact_ops` |
| `UCX/ucx/mcp/server.py` | `_register_tools()` now instantiates and registers `PRDTools` |

---

## Server Registration

`UCXMCPServer._register_tools()` registers two tool groups:

```python
tools = UCXTools(self._config)        # generic ucx_* namespace
tools.register(self._mcp)

prd_tools = PRDTools(self._config)    # layer-specific prd_* namespace
prd_tools.register(self._mcp)
```

Both groups coexist in the same FastMCP instance. A PRD-agent connects to the MCP server and uses only the `prd_*` tools. A generic orchestrator uses `ucx_*` tools. No server segmentation is required.

---

## Canonical Agent Workflow (Agentic Trace)

The sequence below is what a PRD-layer AI agent issues when processing a PRD folder from scratch, using only tool return values to chain calls — no additional filesystem knowledge required:

```
1. Agent calls: prd_status(prd_dir="docs/02_PRD/PRD-01/")
   → {completed_stages: ["stage-1-source-exists", "stage-2-validation-report"], next_step: "prd_validate_fix(...)"}

2. Agent calls: prd_validate_fix(source_prd_path="{source from status.artifacts}")
   → {output_path: ".../PRD-01_platform_architecture_validation.md", next_step: "prd_review(...)"}

3. Agent calls: prd_review(prd_path="{output_path from step 2}")
   → {report_path: ".../PRD-01_platform_architecture_validation.UCX_review_report_v001.md", next_step: "prd_remediate(...)"}

4. Agent calls: prd_remediate(validation_prd_path="{...}", review_report_path="{report_path from step 3}")
   → {report_path: ".../PRD-01_platform_architecture_validation.UCX_remediation_report_v001.md", next_step: "prd_remediate_apply(...)"}

5. Agent calls: prd_remediate_apply(validation_prd_path="{...}", remediation_report_path="{report_path from step 4}")
   → {output_path: ".../PRD-01_platform_architecture_remediated.md", next_step: "Review and promote..."}
```

The agent carries zero workflow topology in its system prompt — all ordering is encoded in tool return values.

---

## Relationship to Prior Plans

### PLAN-012 Impact

PLAN-014 is the MCP execution surface for PLAN-012. The six-stage workflow defined in PLAN-012 is directly expressed as six MCP tool calls. PLAN-014 does not change or extend the workflow; it makes it callable by AI agents without CLI access.

### PLAN-013 Impact

PLAN-013 generalized the remediation fix plan structure. `apply_ucx_action_fixes` extracted in PLAN-014 is the shared runtime function underpinning `prd_remediate_apply`, which maps to the UCX-ACTION block application step described in PLAN-013.

### Future Layer Namespaces

PLAN-014 establishes the prototype. To add a BRD-layer namespace:

1. Create `ucx/mcp/tools_brd.py` with class `BRDTools`
2. Implement `brd_*` tools following the same structural pattern (contract enforcement, structured returns, `next_step` field)
3. Register `BRDTools` alongside `UCXTools` and `PRDTools` in `server.py`

No server changes are required beyond adding the registration call.

---

## Acceptance Criteria

### Functional

- `prd_validate_fix` creates a `_validation` copy from a source PRD and returns its path
- `prd_review` returns the review report path and score
- `prd_remediate` returns the remediation report path and fix counts
- `prd_remediate_apply` creates a `_remediated` copy and returns its path
- `prd_artifacts` correctly classifies all expected artifact types in a PRD directory
- `prd_status` returns correct completed stages and a callable `next_step` string

### Contract Enforcement

- `prd_validate_fix` raises `ValueError` if input is not a source-stage PRD
- `prd_remediate` raises `ValueError` if input is not a `validation-fixed`-stage PRD
- `prd_remediate` raises `ValueError` if review report does not contain `.UCX_review_report_` in its name
- `prd_remediate_apply` raises `ValueError` if input is not a `validation-fixed`-stage PRD

### Shared Utility

- `apply_ucx_action_fixes` in `artifact_ops.py` produces identical results to the prior `_apply_ucx_action_fixes` in `main.py`
- `main.py`'s `_apply_ucx_action_fixes` delegates to `artifact_ops` (no duplication)

### Integration

- `UCXMCPServer` registers both `UCXTools` and `PRDTools` from a single `_register_tools()` call
- All six `prd_*` tools are discoverable via the MCP server after server startup

---

## Test Strategy

### Unit Tests (candidates)

- `prd_artifacts` classification against a fixture directory containing all six artifact types
- `prd_status` next-step decision tree for each incomplete stage combination
- `prd_validate_fix(dry_run=True)` returns expected output path without writing
- `prd_remediate_apply(dry_run=True)` returns expected output path without writing
- Contract rejection: `prd_validate_fix` with `_validation` input
- Contract rejection: `prd_remediate_apply` with source-stage input

### Regression Tests

- `apply_ucx_action_fixes` in `artifact_ops` output matches prior CLI implementation for matching and non-matching blocks
- Existing PLAN-012 CLI tests (validate-fix, remediate-apply) still pass after `main.py` delegation change

---

## Revision History

| Version | Date | Author | Changes Made |
|---------|------|--------|--------------|
| 0.1.0 | 2026-03-23 | UCX Framework | Initial plan — PRD MCP namespace prototype, shared utility extraction, server registration |
