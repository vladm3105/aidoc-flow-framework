# Review tests

**Path:** `tests/review/`
**Pyramid tier:** 8
**Runs:** opt-in (`REVIEW=1`)
**Determinism:** live

## What this suite covers

LLM code-reviewer hook over the current diff (`BASE_REF`..HEAD). Reviewer
must emit zero findings classified BLOCKER or CRITICAL; lower severities are
informational and do not fail the suite.

## Quickstart

```bash
cd framework && REVIEW=1 python3 -m unittest discover tests/review -v
```

## Environment

- Required: `claude` CLI, `ANTHROPIC_API_KEY`, `REVIEW=1`.
- Optional: `BASE_REF` (default `origin/main`), `MAX_DIFF_BYTES`
  (default 262144).

## See also

- Scenarios: `../SCENARIOS.md`
- How-to-use: `../HOWTO.md`
- Troubleshooting: `../TROUBLESHOOTING.md`
