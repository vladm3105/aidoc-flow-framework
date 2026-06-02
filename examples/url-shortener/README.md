# url-shortener — pre-deployment acceptance example

This directory is the **release-gate acceptance test** for the
aidoc-flow Claude Code plugin. The seed at
[`seed/initial-requirements.md`](seed/initial-requirements.md) is driven
through every plugin surface element — 63 total: 50 skills, 11 agents,
one command, one hook — and the chain produced under `docs/` is the
evidence that the plugin works end-to-end.

The acceptance suite is described in detail in
[`ACCEPTANCE_TEST_PLAN.md`](ACCEPTANCE_TEST_PLAN.md). This README is
the user-facing summary.

## Directory layout

```text
url-shortener/
├── ACCEPTANCE_TEST_PLAN.md       # design reference (do not edit casually)
├── README.md                     # this file
├── seed/
│   └── initial-requirements.md   # the acceptance-test input
├── chg/
│   └── test-change.md            # change-set exercised by Phase 2
├── docs/                         # latest release-gate cascade output
│                                 # (populated by --promote; see below)
├── docs-archive/                 # historical cascades, one dir per release
│   └── v<X.Y.Z>/                 # archived by --promote before overwriting docs/
└── logs/<TS>/                    # ephemeral per-run logs (gitignored)
    ├── plugin-test.log
    ├── summary.{txt,json}
    ├── skills/, agents/, command/, hook/, cascade/, negative/, sandbox/
    └── …
```

## Running the suite

From the framework root:

```bash
# Full deterministic + live run (release gate). ~$11–20 in token cost.
LIVE=1 bash tests/scripts/test-acceptance.sh url-shortener --live

# Live run that also promotes the cascade output to docs/ on success.
LIVE=1 bash tests/scripts/test-acceptance.sh url-shortener --live --promote

# Promote AND push to origin in one step (CI / release-tag automation).
LIVE=1 bash tests/scripts/test-acceptance.sh url-shortener --live --promote --push

# Cheap deterministic-only smoke (no LLM cost; ~5 seconds).
bash tests/scripts/test-acceptance.sh url-shortener --no-live

# Replay a recorded run for free script-development iteration.
bash tests/scripts/test-acceptance.sh url-shortener --mock=logs/<TS>
```

Outcomes:

+ **PASS** — all 63 surface elements produced gate-meeting output.
+ **FAIL** — at least one element produced sub-threshold output or
  errored. Inspect `logs/<TS>/summary.txt` for the per-element table
  and `logs/<TS>/<subdir>/<name>.log` for the failing element's raw
  output.

## What `docs/` contains

After a `--promote`-flagged run, `docs/` holds the 8-layer chain
(`01_BRD/` through `08_IPLAN/`, plus `09_CHG/` if Phase 2 ran)
produced by driving the seed through every `doc-<layer>-autopilot`
skill. A `.version` marker records which plugin release the chain
came from.

Before the first cascade lands, `docs/` is empty — the suite operates
in bootstrap mode (Phase 0 detects this and skips chain-dependent
checks until the first cascade produces content).

## What `docs-archive/` contains

`--promote` archives the previous `docs/` content to
`docs-archive/v<previous-version>/` before overwriting. Archived
chains are never deleted — they're the regression baseline for
skill-drift tracking (per plan §3.2 retention policy: pre-1.0 keep
every archive uncompressed; post-1.0 compress beyond the 5 most recent
if `docs-archive/` exceeds 5 MB).

## What gets exercised — quick reference

| Phase | Surface elements | Count |
|------:|---|---:|
| 0 — Bootstrap | manifest validate + lint smoke + state detection | (infra) |
| 1.1 — Cascade | `doc-{brd…iplan}-{base,autopilot,audit,fixer}` | 32 |
| 1.2 — Negative validation | 6 shared fixtures at `tests/acceptance/fixtures/negative/` | (assertions, not skills) |
| 2 — CHG | `doc-chg`, `doc-chg-{autopilot,audit,fixer}` | 4 |
| 3 — Utilities | `doc-flow`, `doc-validator`, …, `project-profile` | 14 |
| 4 — Agents + command + hook | 11 agents + `/aidoc-flow:save-plan` + `hooks/sdd-doc-review.sh` | 13 |
| **Total surface elements** | | **63** |

See [`ACCEPTANCE_TEST_PLAN.md`](ACCEPTANCE_TEST_PLAN.md) §7 + §8 for the
per-skill minimum-coverage thresholds that prevent empty-output
false-PASS.

## What this proves

A passing `--live` run demonstrates:

+ The full **8-layer chain** authoring works end-to-end from a seed.
+ **Cumulative traceability**: each downstream layer carries
  `@brd … @tdd` tags referencing real upstream element IDs (4-segment
  `TYPE.NN.SS.xxxx`).
+ The **C4 + DFD + sequence diagram** contract per layer
  (`framework/governance/DIAGRAM_STANDARDS.md`): BRD `c4-l1`/`dfd-l1`,
  PRD `c4-l2`/`dfd-l2`/`sequence`, ADR decision `sequence`, SPEC
  `c4-l3`/`dfd-l3`.
+ Every utility, agent, command, and hook produces gate-meeting output
  against the produced chain.

## Adding a second example

`payment-gateway`, `multi-tenant`, etc. follow the same shape — copy
this directory's structure (just `seed/` and `chg/`), run
`bash tests/scripts/test-acceptance.sh <NEW-NAME> --live`. No script
changes required. See `ACCEPTANCE_TEST_PLAN.md` §12 for the procedure.
