# UCX Tool Behavior Quirks (session notes)

## sdd_review: Requires API Executor

Attempting `sdd_review` without specifying an `executor` (or with a local/default one) fails:

```json
{
  "passed": false,
  "error": "ExecutorRequired: sdd_review requires an API executor.",
  "error_code": "ExecutorRequired"
}
```

### Available Executors (TradeGent CC env)

| Name | Model | Status |
|------|-------|--------|
| `api/gpt-4o` | gpt-4o | active |
| `api/claude-sonnet` | claude-sonnet-4-20250514 | active |
| `api/gemini-pro` | gemini/gemini-2.5-pro | active |
| `api/openrouter` | openrouter/auto | active |

All use cloud API (not local Ollama). Timeout default: 300s.

### Recovery Pattern

If you hit ExecutorRequired:

1. List executors: `sdd_list_executors()`
2. Pick an active API executor (e.g., `api/claude-sonnet`)
3. Re-run `sdd_review` with `executor: "<name>"`

## sdd_run_lifecycle: Stops at First Failure

`sdd_run_lifecycle` runs stages in sequence: `validate → review → remediate`. If any stage errors, the pipeline HALTS at that stage — downstream stages do not run.

### Symptom (2026-05-14 session)

```json
{
  "validate": {"error": "while parsing a block mapping... id: ADR-NN"},
  "_stopped_at": "validate",
  "_reason": "while parsing a block mapping..."
}
```

`review` and `remediate` never executed. The pipeline returned after `validate` failure.

### Workaround

Run stages individually so failures can be diagnosed and bypassed without losing all downstream work:

```python
# Instead of: sdd_run_lifecycle(stages=["validate","review","remediate"])
# Do:
sdd_validate(...)          # if this fails, fix and retry
sdd_review(...)            # only after validate passes
sdd_remediate(...)         # only after review produces a report
```

This is slower but avoids losing review/remediate work due to an upstream config/template issue.

## sdd_validate: Error Output Format

- **PASS**: Returns a plain-text string with "PASS" marker
- **FAIL**: Returns JSON with `error` key (string) and `is_valid: false`

Do NOT assume JSON always. Parse text first — if it doesn't start with `{`, treat as text. If it does, safe_decode JSON for structured error/warning lists.

## sdd_init: Regenerates Missing Project Files

`sdd_init` discovers which template/prompt/schema files are MISSING from the project's `UCX/` directory and scaffolds them from the UCX framework source. It does NOT delete or overwrite project-owned files (protected by checksum match).

**Trap**: If you moved colliding templates aside to `/tmp`, `sdd_init` will recreate them.
Re-apply the workaround after every `sdd_init` call.

## sdd_set_project: Persistent Across Session

`sdd_set_project` sets the session default. It persists for the lifetime of the MCP connection. To clear:

```
sdd_set_project("")
```

This is useful for isolation — work on project `/tmp/...` without the session default leaking back to the real project.
