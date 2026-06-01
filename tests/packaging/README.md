# Packaging tests

**Path:** `tests/packaging/`
**Pyramid tier:** 5
**Runs:** every PR
**Determinism:** deterministic

## What this suite covers

Bundle integrity (byte-identity via allow-list parse against source tree),
VERSION ↔ FRAMEWORK_SPEC_VERSION alignment gate, and
`claude plugin validate --strict` manifest schema enforcement.

## Quickstart

```bash
cd framework && python3 -m unittest discover tests/packaging -v
```

## Environment

- Required: Python ≥3.11, `claude` CLI (for `--strict` validate).
- Optional: none.

## See also

- Scenarios: `../SCENARIOS.md`
- How-to-use: `../HOWTO.md`
- Troubleshooting: `../TROUBLESHOOTING.md`
