# Unit tests

**Path:** `tests/unit/`
**Runs:** manually — no CI workflow or hook executes this suite
**Determinism:** deterministic

## What this suite covers

Focused unit checks for lint/test helpers (pin-currency reader, trace
resolution, template checks, sync-script guards). Modules whose subject was
deleted with the plugin/tools archivals skip with a cited issue (#665) until
the delete-or-reanchor remedy. Pure-Python, no LLM, no network.

## Quickstart

```bash
python3 -m unittest discover -s tests/unit -v
```

## Environment

- Required: Python ≥3.11, PyYAML.
- Optional: none.

## See also

- Scenarios: `../SCENARIOS.md`
- How-to-use: `../HOWTO.md`
- Troubleshooting: `../TROUBLESHOOTING.md`
