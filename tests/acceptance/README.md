# Acceptance tests

**Path:** `tests/acceptance/`
**Pyramid tier:** 3 + 4
**Runs:** deterministic in every PR; live in nightly + release
**Determinism:** deterministic (default) | live (`LIVE=1`)

## What this suite covers

Per-layer acceptance (Tier 3) on golden fixtures and broken-fixture lint-code
expectations across BRD → IPLAN, plus the Tier 4 full-path chain
(forward-tag closure, section coverage, broken-chain marker). Live counterparts
exercise the actual `doc-<layer>` skills via `claude -p`.

## Quickstart

```bash
cd framework && python3 -m unittest discover tests/acceptance -v
LIVE=1 python3 -m unittest discover tests/acceptance/live -v
```

## Environment

- Required: Python ≥3.11, PyYAML.
- Optional: `LIVE=1` + `claude` CLI + `ANTHROPIC_API_KEY` for live tests.

## See also

- Scenarios: `../SCENARIOS.md`
- How-to-use: `../HOWTO.md`
- Troubleshooting: `../TROUBLESHOOTING.md`
