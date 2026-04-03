# PLAN-023: Merge sdd_validate into sdd_validate_fix

## Context

`sdd_validate` and `sdd_validate_fix` are two separate MCP tools that run sequentially:
1. `sdd_validate` — runs structural checks, produces `*.ucx.validate.json/.txt`
2. `sdd_validate_fix` — reads that report, creates a derived copy, wraps same errors with boilerplate fix instructions

Without an executor, `sdd_validate_fix` adds minimal value — it just copies the error list and produces a derived file. This creates unnecessary pipeline complexity (two tools, two stages, two CLI commands) for what should be a single operation.

**Goal**: Merge into a single `sdd_validate` tool that runs checks AND produces derived copy + fix instructions when errors exist. Deprecate `sdd_validate_fix` as standalone tool.

---

## Design Decisions

1. **Tool name**: Keep `sdd_validate`. `sdd_validate_fix` becomes a deprecated alias routing to `sdd_validate`.
2. **Derived copy**: Only created when validation fails (errors found). No copy on clean pass. The `_validate_copy` file is only consumed by the executor — review and remediate stages read the original source (review explicitly excludes `_validate_copy` at cli/main.py:274).
3. **Preserve `tier1_only` / `strict` / `format` flags** on merged tool.
4. **Add `executor` / `timeout` / `validation_report` params** to `sdd_validate`.
5. **`validation_report` param**: When provided, skip re-validation, load errors from existing report, go straight to fix generation. Response includes `report_path` pointing to the provided report and `errors`/`warnings` extracted from it.
6. **`passed` semantics change**: The pipeline (`_handle_lifecycle_pipeline` line 910) stops on `passed: False`. Currently `sdd_validate` returns `passed: False` on errors, blocking downstream stages. **Fix**: merged tool returns `passed: True` always (stage completed). New `is_valid: bool` field carries the validation pass/fail result. CLI exit code still uses `is_valid` (exit 1 on errors).
7. **Pipeline compat**: Map `"validate_fix"` stage to `sdd_validate` with absorption — skip if `validate` already ran in the same pipeline.

---

## Implementation Steps

### Step 1: Update `sdd_validate` Tool Definition

**File**: `mcp_sdd/src/mcp_server/tool_registry.py` (lines 49-66)

Add to `sdd_validate` inputSchema properties:
```python
"validation_report": {"type": "string", "description": "Path to existing validation report. Skips re-validation, generates fix artifacts from this report."},
"executor": {"type": "string", "description": "Executor name. Omit to return fix report text."},
"timeout": {"type": "integer", "description": "Executor timeout in seconds", "default": 300},
```

Update description:
```
"Run structural validation against layer schema/template assets. When errors are found, creates a source-protected derived copy with fix instructions. If executor specified, spawns agent to apply fixes."
```

Remove `sdd_validate_fix` Tool from TOOLS list (lines 294-311).

### Step 2: Merge Dispatch Handlers

**File**: `mcp_sdd/src/mcp_server/tool_registry.py`

**2a. Rewrite `sdd_validate` handler (lines 559-603):**

```python
if name == "sdd_validate":
    from mcp_server.validation import run_project_validation_build
    from mcp_server.remediation import run_validate_fix_build
    from mcp_server.core.stage_output import STAGE_VALIDATE, resolve_stage_output_dir

    project_root = _path(arguments, "project")
    document_path = _path(arguments, "document")
    output_dir = resolve_stage_output_dir(
        stage=STAGE_VALIDATE,
        project_root=project_root,
        output_dir=_opt_path(arguments, "out"),
        document_dir=document_path if document_path.is_dir() else document_path.parent,
    )

    # --- Phase 1: Validate (or load existing report) ---
    existing_report = _opt_path(arguments, "validation_report")
    if existing_report and existing_report.exists():
        # Skip validation, load from existing report
        report_data = json.loads(existing_report.read_text(encoding="utf-8"))
        errors = report_data.get("errors", [])
        warnings = report_data.get("warnings", [])
        report_path = existing_report
        summary_path = None
    else:
        result = run_project_validation_build(
            project_root=project_root,
            doc_type=arguments["doc_type"],
            layer=arguments["layer"],
            document_path=document_path,
            output_dir=output_dir,
        )
        payload = result.report
        errors = payload.get("errors", []) if isinstance(payload, dict) else []
        warnings = payload.get("warnings", []) if isinstance(payload, dict) else []
        report_path = result.report_path
        summary_path = result.summary_path

    # Apply tier1/strict filters
    tier1_only = arguments.get("tier1_only", False)
    strict = arguments.get("strict", False)
    if tier1_only:
        effective_errors = [
            item for item in errors if isinstance(item, str)
            and (item.startswith("Missing required custom field")
                 or item.startswith("Missing required tag"))
        ]
    else:
        effective_errors = [item for item in errors if isinstance(item, str)]
    effective_warnings = [item for item in warnings if isinstance(item, str)]
    is_valid = len(effective_errors) == 0 and (not strict or len(effective_warnings) == 0)

    # --- Phase 2: Fix (conditional) ---
    fix_generated = False
    fix_response = {}
    if not is_valid:
        fix_result = run_validate_fix_build(
            project_root=project_root,
            doc_type=arguments["doc_type"],
            layer=arguments["layer"],
            document_path=document_path,
            validation_report=report_path,
            output_dir=output_dir,
        )
        fix_response = {
            "fix_generated": True,
            "fix_report_path": str(fix_result.report_path) if fix_result.report_path else None,
            "fix_summary_path": str(fix_result.summary_path) if fix_result.summary_path else None,
            "derived_paths": [str(p) for p in fix_result.derived_paths],
        }
        fix_generated = True

    response = {
        "report_path": str(report_path) if report_path else None,
        "summary_path": str(summary_path) if summary_path else None,
        "tier1_only": tier1_only,
        "strict": strict,
        "errors": effective_errors,
        "warnings": effective_warnings,
        "is_valid": is_valid,
        "passed": True,  # Stage completed — pipeline continues
        "fix_generated": fix_generated,
        **fix_response,
    }

    # Optional executor
    if fix_generated and arguments.get("executor"):
        return await _maybe_run_executor(
            arguments, fix_result.report_text, response, working_dir=project_root,
        )
    return response
```

**2b. Remove standalone `sdd_validate_fix` handler (lines 808-830):**
Delete the entire `if name == "sdd_validate_fix":` block.

**2c. Add deprecation alias at top of `_dispatch()` (before any handler):**
```python
if name == "sdd_validate_fix":
    import warnings
    warnings.warn("sdd_validate_fix is deprecated. Use sdd_validate.", DeprecationWarning)
    name = "sdd_validate"
```

### Step 3: Update Next-Action Logic

**File**: `mcp_sdd/src/mcp_server/tool_registry.py`, `_inspect_document_folder()` (lines 488-495 only — do NOT touch lines 496-499 which are the `elif source_files:` branch)

Replace lines 488-495:
```python
elif has_validation_copy:
    current_stage = "validation_fixed"
    next_action = "review"
    next_tool = "sdd_review"
elif has_validation_report:
    current_stage = "validated"
    next_action = "validate_fix"
    next_tool = "sdd_validate_fix"
```

With:
```python
elif has_validation_report or has_validation_copy:
    current_stage = "validated"
    next_action = "review"
    next_tool = "sdd_review"
```

### Step 4: Update Pipeline Stage Handlers

**File**: `mcp_sdd/src/mcp_server/tool_registry.py`

**4a. Stage handlers** (lines 887-893) — map both to same tool:
```python
stage_handlers = {
    "validate": "sdd_validate",
    "validate_fix": "sdd_validate",  # Deprecated — absorbed into validate
    "review": "sdd_review",
    "remediate": "sdd_remediate",
    "remediate_fix": "sdd_remediate_fix",
}
```

**4b. Pipeline absorption** — insert before `stage_result = await _dispatch(...)` (line 907):
```python
# Skip validate_fix if validate already produced fix output
if stage == "validate_fix" and "validate" in results:
    results[stage] = {**results["validate"], "_absorbed": True}
    continue
```

**4c. `sdd_pipeline` stages enum** (line 220) — keep `"validate_fix"` for backward compat.

### Step 5: Merge CLI Subcommands

**File**: `mcp_sdd/src/mcp_server/cli/main.py`

**5a. Update `validate` subparser** (lines 115-130) — add optional args:
```python
validate_parser.add_argument("--validation-report", default=None)
validate_parser.add_argument("--executor", default=None)
validate_parser.add_argument("--timeout", type=int, default=300)
```

**5b. Update `validate` handler** (lines 506-569):

After the existing validation + tier1/strict filtering (through line 548), add fix phase:

```python
# Existing: failed = len(effective_errors) > 0 or (args.strict and ...)
# After building response_payload...

fix_generated = False
if failed:
    from mcp_server.remediation import run_validate_fix_build
    fix_result = run_validate_fix_build(
        project_root=project_root,
        doc_type=args.doc_type,
        layer=args.layer,
        document_path=document_path,
        validation_report=validation_result.report_path,
        output_dir=output_dir,
    )
    response_payload["fix_generated"] = True
    response_payload["fix_report_path"] = str(fix_result.report_path)
    response_payload["fix_summary_path"] = str(fix_result.summary_path)
    response_payload["derived_paths"] = [str(p) for p in fix_result.derived_paths]
    fix_generated = True

    if args.format != "json":
        print(f"Fix report: {fix_result.report_path}")
        print(f"Derived copies: {len(fix_result.derived_paths)}")
else:
    response_payload["fix_generated"] = False

# Add is_valid alongside passed for clarity
response_payload["is_valid"] = not failed

# CLI exit code: still 0=pass, 1=fail (based on is_valid, not pipeline "passed")
return 0 if not failed else 1
```

**5c. Deprecate `validate-fix` subparser** (lines 170-187):
Update help text to `"[DEPRECATED] Use 'validate' instead"`.

**5d. `validate-fix` handler** (lines 622-648):
```python
if args.command == "validate-fix":
    import sys
    print("WARNING: validate-fix is deprecated. Use 'validate' instead.", file=sys.stderr)
    # Delegate to validate handler — set args.command to trigger same code path
    args.command = "validate"
    args.tier1_only = False
    args.strict = False
    args.format = "json"
    # Fall through to validate handler below
```

Or extract shared logic into a helper function called from both handlers.

**5e. Handle `--validation-report` in validate handler** — when provided, skip `run_project_validation_build()` and load report from file instead (same as MCP handler Phase 1 skip logic).

### Step 6: Update Tests

**File**: `tests/unit/test_server.py`

| Test | Current | Change |
|------|---------|--------|
| `test_deterministic_tool_names` (L46) | `sdd_validate` in set | Keep — core validation is still deterministic |
| `test_llm_dependent_tool_names` (L60) | `sdd_validate_fix` in set | Remove `sdd_validate_fix` (tool removed from TOOLS list) |
| `test_llm_tools_have_executor_param` (L68) | `sdd_validate_fix` in list | Replace with `sdd_validate` |
| `test_sdd_validate_has_control_params` (L76) | Asserts `tier1_only`, `strict`, `format` | Add: `executor`, `timeout`, `validation_report` |
| `test_after_validation` (L210) | `next_action == "validate_fix"` | Change to `next_action == "review"`, `next_tool == "sdd_review"` |
| `test_after_validation_fix` (L217) | `current_stage == "validation_fixed"` | Change to `current_stage == "validated"`, `next_action == "review"` |
| `test_pipeline_stops_on_failure` (L254) | Stages `["validate", "validate_fix", "review"]`, mock returns `passed:False` on call 2 | **Redesign**: Stages `["validate", "review"]`. Mock: call 1 (validate) returns `{"passed": True, "is_valid": False}`, call 2 (review) returns `{"passed": False}`. Assert stopped at `"review"`. |
| `test_pipeline_completes_all_stages` (L285) | Stages `["validate", "validate_fix"]` | Change to `["validate", "review"]` or keep `["validate", "validate_fix"]` and verify absorption |

New test: `test_validate_fix_stage_absorbed`:
```python
# Pipeline ["validate", "validate_fix"] — validate_fix is absorbed
# Mock: validate returns {"passed": True, "fix_generated": True}
# Assert: validate_fix result has "_absorbed": True, call_count == 1
```

New test: `test_deprecated_alias_forwards`:
```python
# Dispatch "sdd_validate_fix" → routed to sdd_validate handler
```

**File**: `tests/unit/test_cli_main.py`

| Test | Change |
|------|--------|
| `test_main_validate_without_out_uses_document_dir` (L296) | After validation with errors, assert `*.ucx.validate_fix.json` and `*_validate_copy.*` also exist in document dir |

New test: `test_main_validate_pass_no_fix_artifacts`:
```python
# Validate a passing document. Assert validate report exists but NO validate_fix report or validate_copy.
```

**File**: `tests/integration/test_migration_flows.py`

| Test | Change |
|------|--------|
| `test_validate_to_fix_to_remediate_flow` (L60) | Remove `validate-fix` CLI call (lines 107-126). After `validate`, assert `*.ucx.validate.json` AND `*_validate_copy.md` both exist. Then proceed to `remediate` CLI call unchanged. |
| `test_validate_ears_directory_flow` (L180) | No change needed — this test only calls `validate` and checks validate report |

### Step 7: Update Documentation

**File**: `docs/architecture/MCP_OPERATIONAL_FLOWS.md`
- Collapse Stage 2 (validate) and Stage 3 (validate_fix) into single "Validate" stage
- Update output table: validate now produces `validation_report.json/.txt` + `*_validate_copy.*` (when errors) + `validate_fix_report.*` (when errors)
- Update artifact lineage diagram
- Update source artifact resolution table: remove validate_fix row

**File**: `docs/architecture/MCP_OPERATOR_RUNBOOK.md`
- Remove section 3.6 (Validate-fix procedure)
- Update section 3.5 (Validate procedure): mention derived copy output when errors found
- Update troubleshooting table: remove validate-fix output missing row

---

## Files Modified (Summary)

| File | Change |
|------|--------|
| `mcp_sdd/src/mcp_server/tool_registry.py` | Merge tool defs, handlers, next-action, pipeline, `passed`→`is_valid` split |
| `mcp_sdd/src/mcp_server/cli/main.py` | Merge CLI, deprecate validate-fix, add --validation-report/--executor/--timeout |
| `tests/unit/test_server.py` | Tool sets, params, next-action, pipeline stop semantics |
| `tests/unit/test_cli_main.py` | CLI validate test for merged output |
| `tests/integration/test_migration_flows.py` | Remove validate-fix step |
| `docs/architecture/MCP_OPERATIONAL_FLOWS.md` | Collapse validate stages |
| `docs/architecture/MCP_OPERATOR_RUNBOOK.md` | Remove validate_fix procedure |

**Unchanged** (verified):
- `validation/runner.py` — core engine, `ValidationRunResult.is_valid` field unchanged
- `remediation/runner.py` — `run_validate_fix_build()` and helpers called as-is
- `consistency/runner.py` — reads `*.ucx.validate.json` (name preserved)
- `core/stage_output.py` — `STAGE_VALIDATE` constant preserved
- `utils/source_files.py` — `_DERIVED_STEMS` unchanged
- `logging_config.py` — uses `is_valid`, not `passed`
- `scoring/runner.py` — `validate_score()` is a different tool

---

## Gaps Identified in Review 3

### G1: `_maybe_run_executor` drops response fields when executor runs
When `_maybe_run_executor` is called WITH an executor (line 433), it returns a **new dict** with `executor`, `exit_code`, `output`, `stderr`, `prompt_file`, and nests our response under `"deterministic_result"`. The `passed`, `is_valid`, `errors` fields are NOT at top level. 

**Impact on pipeline**: If pipeline reads `stage_result.get("passed")` after an executor run, it gets `None` (not `True`). The pipeline would NOT stop (since `None is False` evaluates to `False`), but the `_completed_stages` logic might behave unexpectedly.

**Fix**: After `_maybe_run_executor`, ensure `passed` and `is_valid` are preserved at top level. Add to Step 2a:
```python
if fix_generated and arguments.get("executor"):
    exec_response = await _maybe_run_executor(
        arguments, fix_result.report_text, response, working_dir=project_root,
    )
    # Preserve pipeline-critical fields at top level
    exec_response["passed"] = True
    exec_response["is_valid"] = is_valid
    exec_response["fix_generated"] = True
    return exec_response
```

### G2: Pipeline passes ALL arguments to every stage including `validation_report`
`_handle_lifecycle_pipeline` (line 901-904) forwards all arguments (except `stages`) to every stage. If user passes `validation_report` for the validate stage, it would also be passed to `sdd_review`, `sdd_remediate`, etc. Those handlers call `_opt_path(arguments, "validation_report")` — but they don't have that parameter, so `_opt_path` returns `None` (harmless). **No fix needed** — confirmed safe.

### G3: CLI delegation pattern for validate-fix is fragile
Step 5d proposes `args.command = "validate"` + fall-through. But the CLI `main()` uses `if/elif` chain, not fall-through. The validate handler is at line 506 and validate-fix at line 622. Setting `args.command = "validate"` won't re-enter the if block.

**Fix**: Extract the validate handler logic into a helper function `_run_validate_command(args, ...)` called from both `if args.command == "validate"` and `if args.command == "validate-fix"`. For validate-fix, set default values for missing args (`tier1_only=False`, `strict=False`, `format="json"`) before calling the helper.

### G4: CLI validate-fix has try/except for FileNotFoundError/ValueError (line 642)
The current validate-fix handler wraps `run_validate_fix_build()` in a try/except. The merged validate handler (Step 5b) doesn't include this error handling for the fix phase.

**Fix**: Add try/except around the `run_validate_fix_build()` call in the validate handler:
```python
if failed:
    try:
        fix_result = run_validate_fix_build(...)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Fix generation failed: {exc}", file=sys.stderr)
        # Still return validation exit code — fix failure is non-fatal
```

### G5: CLI validate handler has extra type guards (lines 528-531)
The existing handler has `if not isinstance(errors, list): errors = []` guards that the plan's MCP handler code (Step 2a) omits.

**Fix**: Add the same guards in the MCP handler after extracting errors/warnings from `payload`.

### G6: `_dispatch` is async but `run_validate_fix_build` is sync
The plan's Step 2a handler code uses `await _maybe_run_executor(...)` correctly since `_dispatch` is async. But `run_project_validation_build()` and `run_validate_fix_build()` are sync functions called without `await` — this is correct (matches existing pattern). **No fix needed**.

### G7: Missing `--validation-report` skip logic in CLI handler
Step 5e mentions handling `--validation-report` in the CLI but doesn't provide the code. The CLI handler needs:
```python
if args.validation_report:
    validation_report_path = Path(args.validation_report).expanduser().resolve()
    report_data = json.loads(validation_report_path.read_text(encoding="utf-8"))
    errors = report_data.get("errors", [])
    warnings = report_data.get("warnings", [])
    # Skip run_project_validation_build(), set report_path to provided path
else:
    validation_result = run_project_validation_build(...)
    # existing logic
```

### G8: Plan should save to both plan directories
Plan should be saved to `mcp_sdd/docs/plans/PLAN-023_merge_validate_tools.md` (already done) AND referenced in the framework `plans/` directory or changelog when implemented.

---

## Verification

1. `sdd_validate` on BRD-03 (has errors) → validate report + derived copy + fix prompt in one call
2. `sdd_validate` on passing document → validate report only, `fix_generated=False`, no derived copy
3. `sdd_validate` with `--validation-report` → skip validation, produce fix from existing report
4. `sdd_validate_fix` MCP call → deprecation warning, forwards to `sdd_validate`, same output
5. CLI `validate-fix` → stderr deprecation warning, same output as `validate`
6. `sdd_pipeline ["validate", "review"]` → validate completes (`passed: True`, `is_valid: False`), pipeline continues to review
7. `sdd_pipeline ["validate", "validate_fix", "review"]` → validate_fix absorbed, review runs
8. `sdd_next_action` → "created" → `sdd_validate`, "validated" → `sdd_review`
9. CLI exit code: `0` on pass, `1` on errors (uses `is_valid`, not `passed`)
10. `pytest mcp_sdd/tests/ -x` — all tests pass
