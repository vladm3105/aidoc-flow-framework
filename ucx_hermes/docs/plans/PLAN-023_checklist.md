# PLAN-023 Checklist: Merge sdd_validate into sdd_validate_fix

> **Historical Context**: This document records release/implementation history across the `mcp_ucx` -> `ucx_hermes` transition. Any `mcp_ucx` paths or tool-surface references are legacy snapshots, not active runtime guidance.

**Reference**: `PLAN-023_merge_validate_tools.md`

---

## Phase 1: Tool Registry — Tool Definition and Dispatch

### 1.1 Update `sdd_validate` Tool Definition
**File**: `mcp_ucx/src/mcp_server/tool_registry.py`

- [ ] Add `validation_report` property to `sdd_validate` inputSchema (line 62)
  ```python
  "validation_report": {"type": "string", "description": "Path to existing validation report. Skips re-validation, generates fix artifacts from this report."},
  ```
- [ ] Add `executor` property to `sdd_validate` inputSchema (line 62)
  ```python
  "executor": {"type": "string", "description": "Executor name. Omit to return fix report text."},
  ```
- [ ] Add `timeout` property to `sdd_validate` inputSchema (line 62)
  ```python
  "timeout": {"type": "integer", "description": "Executor timeout in seconds", "default": 300},
  ```
- [ ] Update `sdd_validate` description (line 51) to:
  `"Run structural validation against layer schema/template assets. When errors are found, creates a source-protected derived copy with fix instructions. If executor specified, spawns agent to apply fixes."`
- [ ] Remove `sdd_validate_fix` Tool from TOOLS list (delete lines 294-311, inclusive of closing paren)

### 1.2 Add Deprecation Alias
**File**: `mcp_ucx/src/mcp_server/tool_registry.py`, `_dispatch()` (line 549)

- [ ] Add deprecation alias block at the top of `_dispatch()`, before the first `if name ==` handler:
  ```python
  if name == "sdd_validate_fix":
      import warnings
      warnings.warn("sdd_validate_fix is deprecated. Use sdd_validate.", DeprecationWarning)
      name = "sdd_validate"
  ```

### 1.3 Rewrite `sdd_validate` Handler
**File**: `mcp_ucx/src/mcp_server/tool_registry.py`, handler at line 559

- [ ] Add import for `run_validate_fix_build` from `mcp_server.remediation`
- [ ] Implement Phase 1 — validation-report skip path:
  - [ ] Read `validation_report` via `_opt_path(arguments, "validation_report")`
  - [ ] If exists: load JSON, extract `errors`/`warnings`, set `report_path` to provided path, `summary_path = None`
  - [ ] Else: call `run_project_validation_build()` as before
- [ ] Add type guards after extracting errors/warnings (G5):
  ```python
  if not isinstance(errors, list): errors = []
  if not isinstance(warnings, list): warnings = []
  ```
- [ ] Keep existing tier1_only/strict filtering logic
- [ ] Compute `is_valid` instead of `failed`:
  ```python
  is_valid = len(effective_errors) == 0 and (not strict or len(effective_warnings) == 0)
  ```
- [ ] Implement Phase 2 — conditional fix generation:
  - [ ] If `not is_valid`: call `run_validate_fix_build()` with `report_path` as `validation_report`
  - [ ] Build `fix_response` dict with `fix_generated`, `fix_report_path`, `fix_summary_path`, `derived_paths`
- [ ] Build merged response dict with:
  - [ ] `passed: True` (always — stage completed, pipeline continues)
  - [ ] `is_valid: bool` (validation pass/fail)
  - [ ] `fix_generated: bool`
  - [ ] All existing fields: `report_path`, `summary_path`, `tier1_only`, `strict`, `errors`, `warnings`
  - [ ] Fix fields when applicable: `fix_report_path`, `fix_summary_path`, `derived_paths`
- [ ] Implement executor call with G1 fix — preserve pipeline fields:
  ```python
  if fix_generated and arguments.get("executor"):
      exec_response = await _maybe_run_executor(
          arguments, fix_result.report_text, response, working_dir=project_root,
      )
      exec_response["passed"] = True
      exec_response["is_valid"] = is_valid
      exec_response["fix_generated"] = True
      return exec_response
  ```
- [ ] Return response dict

### 1.4 Remove Standalone `sdd_validate_fix` Handler
**File**: `mcp_ucx/src/mcp_server/tool_registry.py`

- [ ] Delete the entire `if name == "sdd_validate_fix":` block (lines 808-830)

### 1.5 Verify Phase 1 — run quick smoke test
- [ ] Run: `PYTHONPATH=mcp_ucx/src python -c "from mcp_server.tool_registry import TOOLS; print([t.name for t in TOOLS])"` — confirm `sdd_validate_fix` not in list, `sdd_validate` present
- [ ] Run validation on BRD-03 via direct Python call — confirm merged output (validate report + derived copy)

---

## Phase 2: Next-Action and Pipeline Logic

### 2.1 Update `_inspect_document_folder()` Next-Action
**File**: `mcp_ucx/src/mcp_server/tool_registry.py` (lines 488-495 only — do NOT touch 496-499 `elif source_files:`)

- [ ] Replace the two-branch logic (lines 488-495):
  ```python
  # DELETE lines 488-495:
  elif has_validation_copy:
      current_stage = "validation_fixed"
      next_action = "review"
      next_tool = "sdd_review"
  elif has_validation_report:
      current_stage = "validated"
      next_action = "validate_fix"
      next_tool = "sdd_validate_fix"
  ```
  With single branch:
  ```python
  elif has_validation_report or has_validation_copy:
      current_stage = "validated"
      next_action = "review"
      next_tool = "sdd_review"
  ```
- [ ] Verify `elif source_files:` branch (lines 496-499) remains unchanged

### 2.2 Update Pipeline Stage Handlers
**File**: `mcp_ucx/src/mcp_server/tool_registry.py` (lines 887-893)

- [ ] Change `"validate_fix"` mapping from `"sdd_validate_fix"` to `"sdd_validate"`

### 2.3 Add Pipeline Absorption Logic
**File**: `mcp_ucx/src/mcp_server/tool_registry.py`, `_handle_lifecycle_pipeline()` (before line 907)

- [ ] Insert absorption check before `stage_result = await _dispatch(...)`:
  ```python
  if stage == "validate_fix" and "validate" in results:
      results[stage] = {**results["validate"], "_absorbed": True}
      continue
  ```

### 2.4 Preserve `validate_fix` in Pipeline Stages Enum
**File**: `mcp_ucx/src/mcp_server/tool_registry.py`, `sdd_run_lifecycle` tool (line 220)

- [ ] Verify `"validate_fix"` remains in the `stages` enum array for backward compat:
  ```python
  "items": {"type": "string", "enum": ["validate", "validate_fix", "review", "remediate", "remediate_fix"]},
  ```

### 2.5 Verify Phase 2
- [ ] Test `_inspect_document_folder()` with validation report present — expect `next_tool == "sdd_review"`
- [ ] Test `_inspect_document_folder()` with validate_copy present — expect `next_tool == "sdd_review"`
- [ ] Test `_inspect_document_folder()` with source only — expect `next_tool == "sdd_validate"`

---

## Phase 3: CLI Merge

### 3.1 Extract Shared Validate Logic into Helper (G3 fix)
**File**: `mcp_ucx/src/mcp_server/cli/main.py`

- [ ] Create helper function `_run_validate_command(project_root, document_path, doc_type, layer, output_dir, tier1_only, strict, format_, validation_report_path) -> int` containing:
  - [ ] Validation-report skip path (G7): if `validation_report_path` provided, load JSON and extract errors/warnings instead of running `run_project_validation_build()`
  - [ ] Tier1/strict filtering logic
  - [ ] Fix generation with try/except (G4):
    ```python
    if failed:
        try:
            fix_result = run_validate_fix_build(...)
        except (FileNotFoundError, ValueError) as exc:
            import sys
            print(f"Fix generation failed: {exc}", file=sys.stderr)
    ```
  - [ ] Response payload construction with `is_valid` and `fix_generated`
  - [ ] JSON / text output formatting
  - [ ] Return exit code `0` (pass) or `1` (fail)

### 3.2 Update `validate` Subparser
**File**: `mcp_ucx/src/mcp_server/cli/main.py` (lines 115-130)

- [ ] Add `--validation-report` argument (default=None)
- [ ] Add `--executor` argument (default=None) — reserved for future CLI executor support
- [ ] Add `--timeout` argument (type=int, default=300) — reserved for future CLI executor support

### 3.3 Update `validate` Handler
**File**: `mcp_ucx/src/mcp_server/cli/main.py` (lines 506-569)

- [ ] Replace handler body with call to `_run_validate_command()` helper

### 3.4 Deprecate `validate-fix` Subparser
**File**: `mcp_ucx/src/mcp_server/cli/main.py` (lines 170-187)

- [ ] Update help text to `"[DEPRECATED] Use 'validate' instead. Generates validation + fix artifacts."`

### 3.5 Update `validate-fix` Handler
**File**: `mcp_ucx/src/mcp_server/cli/main.py` (lines 622-648)

- [ ] Add stderr deprecation warning:
  ```python
  import sys
  print("WARNING: validate-fix is deprecated. Use 'validate' instead.", file=sys.stderr)
  ```
- [ ] Set default values for missing args (`tier1_only=False`, `strict=False`, `format_="json"`)
- [ ] Call `_run_validate_command()` helper with `validation_report_path` from `args.validation_report`

### 3.6 Verify Phase 3
- [ ] Run CLI: `python -m mcp_server.cli.main validate --project ... --doc-type brd --layer 01_BRD --document ...` — confirm both validate + fix artifacts
- [ ] Run CLI: `python -m mcp_server.cli.main validate-fix --project ...` — confirm deprecation warning + same output
- [ ] Run CLI on passing document — confirm no fix artifacts, exit code 0

---

## Phase 4: Update Tests

### 4.1 Unit Tests — Tool Registry
**File**: `tests/unit/test_server.py`

Note: `sdd_validate` is now **conditionally LLM-dependent** — deterministic without executor, LLM-dependent with executor. Same pattern as `sdd_remediate_fix`. Keep in deterministic set AND add to executor-aware set.

- [ ] `test_deterministic_tool_names` (L46): Keep `sdd_validate` in deterministic set (core validation is still deterministic)
- [ ] `test_llm_dependent_tool_names` (L60): Remove `sdd_validate_fix` from set (tool removed from TOOLS list)
- [ ] `test_llm_tools_have_executor_param` (L68): Replace `sdd_validate_fix` with `sdd_validate` (verify executor param present)
- [ ] `test_sdd_validate_has_control_params` (L76): Add assertions for `executor`, `timeout`, `validation_report`

### 4.2 Unit Tests — Next-Action
**File**: `tests/unit/test_server.py`

- [ ] `test_after_validation` (L210): Change to `next_action == "review"`, `next_tool == "sdd_review"`
- [ ] `test_after_validation_fix` (L217): Change to `current_stage == "validated"`, `next_action == "review"`

### 4.3 Unit Tests — Pipeline
**File**: `tests/unit/test_server.py`

- [ ] `test_pipeline_stops_on_failure` (L254): Redesign:
  - Stages: `["validate", "review"]`
  - Mock call 1 (validate): `{"passed": True, "is_valid": False, "fix_generated": True}`
  - Mock call 2 (review): `{"passed": False, "errors": ["Missing section"]}`
  - Assert: stopped at `"review"`, call_count == 2
- [ ] `test_pipeline_completes_all_stages` (L285): Update stages to `["validate", "review"]`
  - Mock always returns `{"passed": True, "report_text": "ok"}`
  - Assert: both stages in `_completed_stages`
- [ ] Add `test_validate_fix_stage_absorbed`:
  - Stages: `["validate", "validate_fix"]`
  - Mock validate returns `{"passed": True, "fix_generated": True}`
  - Assert: `validate_fix` result has `"_absorbed": True`, mock call_count == 1
- [ ] Add `test_deprecated_alias_forwards`:
  - Dispatch `"sdd_validate_fix"` with valid arguments
  - Assert: routed to `sdd_validate` handler (produces same response structure)
- [ ] Add `test_validate_with_executor_preserves_pipeline_fields`:
  - Mock `run_executor` to return a successful ExecutorResult
  - Dispatch `sdd_validate` with executor arg on a failing document
  - Assert: top-level `passed == True`, `is_valid == False`, `fix_generated == True` in response
  - Verifies G1 fix: pipeline-critical fields survive `_maybe_run_executor` nesting

### 4.4 Unit Tests — CLI
**File**: `tests/unit/test_cli_main.py`

- [ ] `test_main_validate_without_out_uses_document_dir` (L296): Add assertions for fix artifacts when validation fails:
  - Assert `*.ucx.validate_fix.json` exists in document dir
  - Assert `*_validate_copy.*` exists in document dir
- [ ] Add `test_main_validate_pass_no_fix_artifacts`:
  - Create a passing document (all required sections present)
  - Run validate CLI
  - Assert: `*.ucx.validate.json` exists
  - Assert: NO `*.ucx.validate_fix.json` exists
  - Assert: NO `*_validate_copy.*` exists
  - Assert: exit code 0

### 4.5 Integration Tests
**File**: `tests/integration/test_migration_flows.py`

- [ ] `test_validate_to_fix_to_remediate_flow` (L60):
  - Remove `validate-fix` CLI call (lines 107-126)
  - After `validate` CLI call, assert both `*.ucx.validate.json` AND `*_validate_copy.md` exist
  - `remediate` CLI call proceeds unchanged

### 4.6 Run Full Test Suite
- [ ] Run: `cd /opt/data/ucx_framework && PYTHONPATH=mcp_ucx/src pytest mcp_ucx/tests/ -x -v`
- [ ] Confirm all tests pass
- [ ] Confirm no unexpected warnings

---

## Phase 5: Documentation

### 5.1 Operational Flows
**File**: `mcp_ucx/docs/architecture/MCP_OPERATIONAL_FLOWS.md`

- [ ] Collapse Stage 2 (validate) and Stage 3 (validate_fix) into single "Validate" stage
- [ ] Update output table: validate produces `validation_report.json/.txt` + `*_validate_copy.*` (when errors) + `validate_fix_report.*` (when errors)
- [ ] Update artifact lineage diagram — remove validate_fix as separate node
- [ ] Update source artifact resolution table — remove validate_fix row

### 5.2 Operator Runbook
**File**: `mcp_ucx/docs/architecture/MCP_OPERATOR_RUNBOOK.md`

- [ ] Remove section 3.6 (Validate-fix procedure)
- [ ] Update section 3.5 (Validate): mention derived copy output when errors found
- [ ] Update troubleshooting table: remove "validate-fix output missing" row
- [ ] Add note: `sdd_validate_fix` is deprecated, use `sdd_validate`

---

## Phase 6: End-to-End Verification

### 6.1 MCP Tool Verification
- [ ] `sdd_validate` on BRD-03 (has errors):
  - Produces `BRD-03.ucx.validate.json` + `.txt`
  - Produces `BRD-03.ucx.validate_fix.json` + `.txt`
  - Produces `BRD-03_security_compliance_validate_copy.yaml`
  - Response has `passed: True`, `is_valid: False`, `fix_generated: True`
- [ ] `sdd_validate` on passing document:
  - Produces `*.ucx.validate.json` + `.txt`
  - NO `*.ucx.validate_fix.*` or `*_validate_copy.*`
  - Response has `passed: True`, `is_valid: True`, `fix_generated: False`
- [ ] `sdd_validate` with `validation_report` param:
  - Skips validation, loads report, produces fix artifacts
  - Response has `passed: True`, `is_valid: False`, `fix_generated: True`
- [ ] `sdd_validate_fix` MCP call (deprecated alias):
  - Logs deprecation warning
  - Returns same output as `sdd_validate`

### 6.2 CLI Verification
- [ ] `validate` command on failing document — exit code 1, fix artifacts produced
- [ ] `validate` command on passing document — exit code 0, no fix artifacts
- [ ] `validate-fix` command — stderr deprecation warning, same behavior as `validate`
- [ ] `validate --validation-report <path>` — skips validation, produces fix from report

### 6.3 Pipeline Verification
- [ ] `sdd_pipeline ["validate", "review"]` — validate completes, pipeline continues to review
- [ ] `sdd_pipeline ["validate", "validate_fix", "review"]` — validate_fix absorbed, review runs
- [ ] `sdd_next_action` on document with source only → `sdd_validate`
- [ ] `sdd_next_action` on document with validation report → `sdd_review`

### 6.4 Test Suite
- [ ] `pytest mcp_ucx/tests/ -x -v` — all pass
- [ ] No deprecation warnings from own code (only from deprecated alias test)
