# `.aidoc/` — AI working notes, documentation of provenance

`.aidoc/` is the **third committed tier** of every project that uses the
framework. It holds the audit, review, remediation, validation,
security, and quality reports that AI personas produced while authoring
the project's chain.

The question `.aidoc/` answers: **"how did the AI arrive at the output
in `docs/`?"** Without this tier, that question can only be answered by
re-running the acceptance suite. With it, the answer lives in the repo
alongside the artifacts.

## The four tiers at a glance

```
<project>/
├── seed/, chg/         — human inputs (committed)
├── docs/               — AI outputs, the produced chain (committed)
├── .aidoc/             — AI working notes (committed) ← this tier
└── logs/<TS>/          — tool internals (gitignored)
```

| Tier | What | Lifecycle |
|---|---|---|
| Inputs | human-authored seeds + change requests | committed |
| Outputs | the produced 8-layer chain (BRD → IPLAN) | committed |
| Provenance (`.aidoc/`) | audit reports, review consensus, remediation logs, validation reports, security reviews, quality suggestions, project profile | committed |
| Tool internals (`logs/`) | execution metadata, raw skill stdout, timing, exit codes | gitignored |

## What `.aidoc/` contains

```
.aidoc/
├── profile.yaml                       # project profile — the personas + review crews
├── audit/<NN>_<LAYER>-audit.md        # per-layer audit reports
├── remediation/<NN>_<LAYER>-fix.md    # per-layer fix reports (when fixer ran)
├── review/
│   ├── <layer>-consensus.md           # review-team consensus per layer (committed)
│   └── .blackboard/                   # transient per-persona scratch (gitignored)
├── validation/                        # doc-validator, doc-ref, gate-check reports
├── security/review.md                 # security-audit
└── quality/suggestions.md             # quality-advisor
```

### `profile.yaml` — the project profile

Per [`framework/governance/ADAPTATION.md`](../governance/ADAPTATION.md):

> The project profile (`.aidoc/profile.yaml`) is the single input an
> engine reads when authoring or auditing. Version-controlled, so audits
> are reproducible in CI.

Effective precedence: `framework defaults < user-global seed < project
profile`.

Engines consult `profile.yaml` to determine which personas perform
review and remediation. If a project has no `profile.yaml`, the
acceptance suite bootstraps one by copying
`framework/governance/REVIEW_CREWS.yaml` as the default.

### `audit/`, `remediation/`, `review/`, `validation/`, `security/`, `quality/`

Each subdirectory holds the report a particular review/remediation
skill produced when the chain was last authored or updated. These are
the AI's working notes — what it found, why, and what it recommended.

## Why this is committed (not in `logs/`)

The audit and review reports aren't execution metadata — they're
**evidence of the gate decision**. A future contributor reviewing why
`SPEC-01` is structured the way it is should be able to read
`.aidoc/review/spec-consensus.md` in git history without running the
suite.

Tool internals (claude -p stdout buffers, exit codes, run timing) stay
in `logs/<TS>/` and are gitignored.

## The blackboard split

`.aidoc/review/` formerly was entirely gitignored as "transient
blackboard." The split:

- `.aidoc/review/.blackboard/` — per-persona scratch state during a
  multi-persona review crew run. Still gitignored.
- `.aidoc/review/<layer>-consensus.md` and other final reports —
  committed as documentation of provenance.

## How the acceptance suite populates `.aidoc/`

When `tests/scripts/test-acceptance.sh` runs, it routes skill outputs to
the correct tier:

| Skill | Tier | Path |
|---|---|---|
| `doc-<layer>-autopilot` | docs | `docs/<NN>_<LAYER>/<TYPE>-01.md` |
| `doc-<layer>-audit` | .aidoc | `.aidoc/audit/<NN>_<LAYER>-audit.md` |
| `doc-<layer>-fixer` | .aidoc | `.aidoc/remediation/<NN>_<LAYER>-fix.md` |
| `review-team` | .aidoc | `.aidoc/review/<layer>-consensus.md` |
| `doc-validator`, `doc-ref`, `gate-check` | .aidoc | `.aidoc/validation/<report>.md` |
| `security-audit` | .aidoc | `.aidoc/security/review.md` |
| `quality-advisor` | .aidoc | `.aidoc/quality/suggestions.md` |
| Other utility / agent / command probes | logs | `logs/<TS>/elements/<name>.log` |

After a successful run, `--promote` runs `git add docs/ .aidoc/` +
commit. The next contributor sees both the chain and the personas'
working notes side-by-side.

## See also

- [`framework/governance/ADAPTATION.md`](../governance/ADAPTATION.md) — profile semantics
- [`framework/governance/REVIEW_TEAM.md`](../governance/REVIEW_TEAM.md) — multi-persona review model
- [`framework/governance/REVIEW_REMEDIATION_FLOW.md`](../governance/REVIEW_REMEDIATION_FLOW.md) — review/remediation gate flow
- [`examples/url-shortener/ACCEPTANCE_TEST_PLAN.md`](../../examples/url-shortener/ACCEPTANCE_TEST_PLAN.md) — example acceptance test using `.aidoc/`
