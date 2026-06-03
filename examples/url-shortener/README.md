# url-shortener — pre-deployment acceptance example

This directory is the **canonical instance** of the framework's
acceptance test methodology. The seed at
[`seed/initial-requirements.md`](seed/initial-requirements.md) is
driven through every plugin surface element (50 skills + 11 agents +
1 command + 1 hook = 63 total); the chain it produces under `docs/`
is the release-gate evidence that the plugin works end-to-end.

**For the methodology** (driver script, log layout, schema, `--promote`
algorithm, phase definitions, design decisions, cost ballpark, CI
integration), see
[`tests/ACCEPTANCE.md`](../../tests/ACCEPTANCE.md).

**For the `.aidoc/` provenance tier** (audit, review, remediation,
validation, security, quality reports — the "AI's working notes"),
see [`framework/docs/AIDOC.md`](../../framework/docs/AIDOC.md).

**For project history** (how the suite was designed and built across
2026-05 / 2026-06, with rationale for each PR), see
[`plans/ACCEPTANCE-SUITE-HISTORY.md`](../../plans/ACCEPTANCE-SUITE-HISTORY.md).

This file covers **what's unique about this example**.

## What this example is

A URL-shortener service is the smallest realistic seed that exercises
every layer of the SDD flow:

- Concrete business value (shorten, redirect, count visits)
- Quality targets that exercise non-functional requirements (p95
  redirect latency, availability, collision-freedom)
- Explicit out-of-scope to test scope-discipline (vanity domains,
  accounts, dashboards)

The seed is in
[`seed/initial-requirements.md`](seed/initial-requirements.md) — keep
it short and concrete so the cascade exercises the autopilots'
ability to fill detail, not their ability to consume detail.

## Directory layout

The four-tier output separation per
[`framework/docs/AIDOC.md`](../../framework/docs/AIDOC.md):

```text
url-shortener/
├── README.md                     # this file
├── seed/                         # human input — acceptance-test seed
│   └── initial-requirements.md
├── chg/                          # human input — change request for Phase 2
│   └── test-change.md
├── docs/                         # AI outputs — produced 8-layer chain (committed)
│   ├── 01_BRD/BRD-01.md
│   ├── 02_PRD/PRD-01.md
│   ├── …
│   └── .version                  # records the plugin version of this chain
├── .aidoc/                       # AI provenance — committed
│   ├── profile.yaml              # project profile (bootstrap from framework default)
│   ├── audit/<NN>_<LAYER>-audit.md
│   ├── remediation/<NN>_<LAYER>-fix.md
│   ├── review/<layer>-consensus.md
│   ├── validation/, security/, quality/
│   └── review/.blackboard/       # transient per-persona scratch (gitignored)
└── logs/<TS>/                    # tool internals — gitignored, ephemeral
    ├── plugin-test.log
    ├── summary.{txt,json}
    └── elements/<name>.log
```

## Change request for Phase 2

[`chg/test-change.md`](chg/test-change.md) is the change-set Phase 2
of the acceptance suite applies after the cascade completes. Topic:
**add visit-rate analytics dashboard**. It was chosen to exercise
realistic propagation across all 8 layers — the change touches BRD
scope (move "analytics dashboards" from out-of-scope to in-scope),
PRD non-functional requirements (retention and p95 latency), EARS
formal requirements, BDD scenarios, a new ADR (storage choice), then
SPEC and TDD coverage deltas, and IPLAN task additions.

If you adapt this example, update both `seed/initial-requirements.md`
and `chg/test-change.md` together — the change request is meaningful
only against the seed it amends.

## Running the suite against this example

Quick reference; for the full flag inventory see
[`tests/ACCEPTANCE.md`](../../tests/ACCEPTANCE.md)
§3.

```bash
cd framework

# Smoke (no LLM cost, ~5s)
bash tests/scripts/test-acceptance.sh url-shortener --no-live

# Preview before spending
bash tests/scripts/test-acceptance.sh url-shortener --dry-run

# Full live run (60-120 min, ~$15-25)
bash tests/scripts/test-acceptance.sh url-shortener --live

# Promote on success (git commit docs/ + .aidoc/)
bash tests/scripts/test-acceptance.sh url-shortener --live --promote

# Generate only the PRD against existing BRD
bash tests/scripts/test-acceptance.sh url-shortener --live --element=doc-prd-autopilot

# Resume after Ctrl-C
bash tests/scripts/test-acceptance.sh url-shortener --live --skip-completed
```

## What a passing live run demonstrates

- The full **8-layer chain** authored end-to-end from the seed.
- **Cumulative traceability**: each downstream layer carries
  `@brd … @tdd` tags referencing real upstream element IDs (4-segment
  `TYPE.NN.SS.xxxx`).
- The **C4 + DFD + sequence diagram** contract per layer (see
  [`framework/governance/DIAGRAM_STANDARDS.md`](../../framework/governance/DIAGRAM_STANDARDS.md)):
  BRD `c4-l1`/`dfd-l1`, PRD `c4-l2`/`dfd-l2`/`sequence`, ADR decision
  `sequence`, SPEC `c4-l3`/`dfd-l3`.
- All 14 utility skills produce gate-meeting output.
- All 11 agents + the `/aidoc-flow:save-plan` command + the
  `sdd-doc-review.sh` hook function correctly.
- All 6 negative fixtures are correctly flagged by their intended
  detectors.

## Adding a sibling example

`payment-gateway`, `multi-tenant`, etc. follow the same shape — copy
this directory's `seed/` and `chg/` (substituting domain-specific
content), then run:

```bash
bash tests/scripts/test-acceptance.sh <NEW-NAME> --live
```

No script changes required. See
[`tests/ACCEPTANCE.md`](../../tests/ACCEPTANCE.md)
§11 for the full procedure.
