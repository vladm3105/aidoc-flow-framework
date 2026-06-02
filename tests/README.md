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

## Tier overview

| Tier | Path | Runs on |
|------|------|---------|
| 1 — Static | `tests/packaging/test_manifest_strict.py` + pre-commit | every commit |
| 2 — Unit | `tests/unit/` | every PR |
| 3 — Per-layer (det) | `tests/acceptance/deterministic/test_layer_*.py` | every PR |
| 3 — Per-layer (live) | `tests/acceptance/live/test_layer_*_live.py` | nightly + release |
| 4 — Full-path (det) | `tests/acceptance/deterministic/test_fullpath.py` | every PR |
| 4 — Full-path (live) | `tests/acceptance/live/test_fullpath_live.py` | release + nightly |
| 5 — Packaging | `tests/packaging/` | every PR |
| 6 — Release gate | `tests/release/` | release tags only |
| 7 — Post-deploy | `tests/smoke/` | manual / after publish |
| 8 — LLM review | `tests/review/` | opt-in, REVIEW=1 |

## Quick reference

| Goal | Command |
|------|---------|
| Run everything deterministic | `bash tests/scripts/test-plugin.sh --suite=pre-deploy` |
| Run one layer | `bash tests/scripts/test-layer.sh brd` |
| Full BRD→IPLAN chain | `bash tests/scripts/test-fullpath.sh` |
| Include LLM probes | append `--live` |
| Run LLM code review | `REVIEW=1 bash tests/scripts/test-plugin.sh --suite=review` |

## Conventions

- All tests use `unittest` for parity with the existing `tests/conformance/` suite.
- Live tests live under `tests/acceptance/live/` and skip unless `LIVE=1`.
- LLM-review tests live under `tests/review/` and skip unless `REVIEW=1`.
- Fixtures under `tests/acceptance/fixtures/` are committed; never generate on the fly.

## Three-tier acceptance-suite output

`tests/scripts/test-acceptance.sh` writes its outputs across three tiers per example:

- `examples/<NAME>/docs/` — produced 8-layer chain (committed)
- `examples/<NAME>/.aidoc/` — audit, review, remediation, validation, security, quality reports (committed; AI provenance documentation)
- `examples/<NAME>/logs/<TS>/` — execution metadata + raw stdout (gitignored)

See [`../framework/docs/AIDOC.md`](../framework/docs/AIDOC.md) for the canonical
description of `.aidoc/`.
