# Acceptance tests

**Path:** `tests/acceptance/`
**Pyramid tier:** 3 + 4
**Runs:** deterministic in every PR (`.github/workflows/acceptance.yml`); live
in nightly + release
**Gating:** the workflow runs on every push/PR. Promotion to a *required* check
is a branch-protection change, tracked as `ACCEPTANCE-TIER-REQUIRED-CHECK`
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

## Accepted warnings (`expected_warnings/`)

A golden directory must be **gate-clean** (`rc == 0`, zero `error` findings) and
emit **exactly** the warnings pinned in `expected_warnings/<target>.yaml`. The
match is a multiset on `(code, file, ref)` + `count`, and it runs **both ways**:

- an emitted warning that is not pinned **fails** — that is new drift;
- a pinned warning that no longer fires **also fails** — delete the entry.

So clearing a fixture tells you to shrink the manifest; the file cannot rot into
a permanent excuse list. Every entry carries a `reason` naming what would clear
it. Manifests live here, **not** under `fixtures/`: a manifest inside a
`NN_LAYER/` directory is ingested by the linter as an artifact, and the live
harness copies `valid/` contents into exactly such a directory.

**Adding a new advisory lint rule?** It will fire on these fixtures and turn this
check red until the manifests are updated in the same PR (and block merges once
the check is required). That is intended — it is what stops the tier from
silently reddening — but budget for it.

### Manifest schema

Filename is the lint target's path relative to `fixtures/` with `/` → `__`:
`layer_07_tdd/valid` → `expected_warnings/layer_07_tdd__valid.yaml`.

```yaml
target: layer_07_tdd/valid       # must match the filename; the loader asserts it
expected_warnings:
  - code: REFGRAN01
    file: SPEC-01_golden.yaml    # relative to `target` (the linter emits
                                 # CWD-relative or absolute; the loader normalizes)
    ref: "@adr: ADR-01"          # per-code discriminator, see below
    count: 2                     # multiplicity of this exact key
    reason: >                    # required and non-empty; say what would clear it
      ...
```

`ref` identifies *which* finding, since counts alone cannot detect substitution:

| code | `ref` | why |
|---|---|---|
| `ACC01`, `COV02` | the element ID (`BDD.01.04.bbbb`) | taken as the single-quoted token, then validated with `ELEM_FORM` |
| `REFGRAN01` | the cited tag (`@adr: ADR-01`) | its message carries no element ID, only a literal `TYPE.NN.SS.xxxx` placeholder |

A code exposing neither makes the loader **raise** rather than degrade to
counting. Extend `_finding_ref()` in `_harness.py` deliberately.

Origin: `plans/ACCEPTANCE-TIER-DRIFT-UNTRACKED-PLAN.md`, [#365](https://github.com/vladm3105/aidoc-flow-framework/issues/365).

## Environment

- Required: Python ≥3.11, PyYAML.
- Optional: `LIVE=1` + `claude` CLI + `ANTHROPIC_API_KEY` for live tests.

## See also

- Scenarios: `../SCENARIOS.md`
- How-to-use: `../HOWTO.md`
- Troubleshooting: `../TROUBLESHOOTING.md`
