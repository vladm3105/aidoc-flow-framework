# Unit tests

**Path:** `tests/unit/`
**Pyramid tier:** 2
**Runs:** every PR
**Determinism:** deterministic

## What this suite covers

Per-skill SKILL.md manifest validation, lint-code targeting matrix
(each code fires on its own fixture only), sync-script idempotency, helper
resolution, and orphan-governance guards. Pure-Python, no LLM, no network.

## Quickstart

```bash
cd framework && python3 -m unittest discover tests/unit -v
```

## Environment

- Required: Python ≥3.11, PyYAML.
- Optional: none.

## See also

- Scenarios: `../SCENARIOS.md`
- How-to-use: `../HOWTO.md`
- Troubleshooting: `../TROUBLESHOOTING.md`
