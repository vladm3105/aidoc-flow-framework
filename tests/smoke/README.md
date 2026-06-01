# Smoke tests

**Path:** `tests/smoke/`
**Pyramid tier:** 7
**Runs:** manual / post-publish
**Determinism:** live

## What this suite covers

Post-deploy verification: install the published plugin from
`MARKETPLACE_URL`, invoke the `doc-flow` probe via `claude -p`, assert the
response carries dual-axis structure and contains zero banned confabulation
phrases.

## Quickstart

```bash
cd framework && MARKETPLACE_URL=<url> python3 -m unittest discover tests/smoke -v
```

## Environment

- Required: `claude` CLI, `ANTHROPIC_API_KEY`, `MARKETPLACE_URL`.
- Optional: see `COMMANDS.md` for verified install commands.

## See also

- Scenarios: `../SCENARIOS.md`
- How-to-use: `../HOWTO.md`
- Troubleshooting: `../TROUBLESHOOTING.md`
