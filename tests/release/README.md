# Release tests

**Path:** `tests/release/`
**Pyramid tier:** 6
**Runs:** release tags only
**Determinism:** deterministic

## What this suite covers

The marketplace pre-publish gate: CHANGELOG version section presence and no
placeholder lines, bundle size and skill-count caps (`limits.yaml`), zero
network egress in plugin code, no `--dangerously-skip-permissions` defaults
in any SKILL.md, and plugin manifest schema present.

## Quickstart

```bash
cd framework && python3 -m unittest discover tests/release -v
```

## Environment

- Required: Python ≥3.11.
- Optional: none.

## See also

- Scenarios: `../SCENARIOS.md`
- How-to-use: `../HOWTO.md`
- Troubleshooting: `../TROUBLESHOOTING.md`
