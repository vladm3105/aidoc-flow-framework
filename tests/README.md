# Framework Test Suite

Navigation hub for the tiered test suite. Start here, then drill into the
companion docs below.

## Companion documents

| Doc | When to read it |
|-----|-----------------|
| [SCENARIOS.md](SCENARIOS.md) | "What does the suite cover?" — catalog of every test case |
| [HOWTO.md](HOWTO.md) | "How do I run X?" — common commands + flags |
| [ENVIRONMENT.md](ENVIRONMENT.md) | "What do I need installed?" — prerequisites + secrets |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | "Why did this fail?" — common failures + fixes |
| [CONTRIBUTING.md](CONTRIBUTING.md) | "How do I add a test?" — fixtures, lint codes, new skills |

(Phase 11.5 commits add the four companion docs above.)

## Tier overview (live suites — CHG-08 #670)

| Suite | Path | Runs on |
|------|------|---------|
| Unit | `tests/unit/` | every PR (green-or-skipped; skips cite their issue) |
| Conformance | `tests/conformance/` | every PR |
| Linter | `sdd_doc_lint/tests` | every PR |
| Acceptance (deterministic) | `tests/acceptance/deterministic/` | every PR (required CI gate) |
| CHG gates | `tests/chg/` | every PR |

> Retired tiers (packaging, release-gate, post-deploy smoke, LLM review, live
> acceptance) were removed with the plugin harness. Their methodology record is
> [`plans/ACCEPTANCE-HISTORY.md`](../plans/ACCEPTANCE-HISTORY.md).

## Quick reference

| Goal | Command |
|------|---------|
| Run unit tests | `python3 -m unittest discover -s tests/unit` |
| Run conformance | `python3 -m unittest discover -s tests/conformance` |
| Run linter tests | `python3 -m unittest discover -s sdd_doc_lint/tests` |
| Run acceptance (det) | `python3 -m unittest discover -s tests/acceptance/deterministic` |
| Run one layer | `bash tests/scripts/test-layer.sh brd` |
| Full BRD→IPLAN chain | `bash tests/scripts/test-fullpath.sh` |

## Conventions

- All tests use `unittest` for parity with the existing `tests/conformance/` suite.
- Fixtures under `tests/acceptance/fixtures/` are committed; never generate on the fly.

## Three-tier acceptance-suite output (retired)

The plugin-era pre-deployment acceptance test (`tests/scripts/test-acceptance.sh`,
deleted) exercised every active plugin surface element against a named example's
seed across three output tiers (`examples/<NAME>/docs/`, `.aidoc/`, `logs/`).
The system it measured is archived; the live methodology is
[`tests/acceptance/README.md`](acceptance/README.md), and the retired record is
[`plans/ACCEPTANCE-HISTORY.md`](../plans/ACCEPTANCE-HISTORY.md).

See [`framework/governance/aidoc/AIDOC.md`](../framework/governance/aidoc/AIDOC.md)
for the canonical description of `.aidoc/`.
