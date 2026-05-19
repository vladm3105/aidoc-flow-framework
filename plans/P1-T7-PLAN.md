# P1-T7 Plan — Framework Root Assembly: the 4 Methodology Docs

| Field      | Value                                      |
|------------|--------------------------------------------|
| Task       | P1-T7                                      |
| Depends on | P1-T2/T3/T4 (layers, registry, governance in place) |
| Status     | DONE — 2026-05-19T10:00:00Z                |
| Feeds      | Phase 1 close (P1-T8 tags)                 |

## Objective

Complete `framework/` by extracting the 4 engine-agnostic methodology docs
from `legacy/ucx_flow_v3/` into the `framework/` root, adapted to the new
layout. After this task `framework/` is fully assembled.

## Scope

**In:** copy + transform 4 docs into `framework/`; add a conformance test for
the framework root.
**Out:** `framework/README.md` (done in P1-T5); `framework/VERSION` (P1-T6);
git tags (P1-T8).

## Source → target

| Legacy file | Target |
|-------------|--------|
| `legacy/ucx_flow_v3/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` | `framework/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` |
| `legacy/ucx_flow_v3/QUICK_REFERENCE.md` | `framework/QUICK_REFERENCE.md` |
| `legacy/ucx_flow_v3/AI_ASSISTANT_RULES.md` | `framework/AI_ASSISTANT_RULES.md` |
| `legacy/ucx_flow_v3/TESTING_STRATEGY_TDD.md` | `framework/TESTING_STRATEGY_TDD.md` |

`legacy/` is frozen — copy, never move. Keep all genuinely engine-agnostic
methodology content verbatim; transform only what the rules below require.

## Transformation rules

- **T1 — version strings.** Neutralize `SDD v3.2` / `v3.2` / `v3.0` everywhere
  (titles, prose, table headers): `SDD v3.2` → `SDD`, `## v3.2 Layer
  Responsibilities` → `## Layer Responsibilities`, `v3.2 Owner` → `Owner`.
- **T2 — QUICK_REFERENCE internal links.** Repoint for the new layout:
  `0N_TYPE/TYPE-TEMPLATE.yaml` → `layers/0N_TYPE/TYPE-TEMPLATE.yaml`;
  `LAYER_REGISTRY.yaml` → `registry/LAYER_REGISTRY.yaml`;
  `ID_NAMING_STANDARDS.md` / `TRACEABILITY.md` / `DIAGRAM_STANDARDS.md` /
  `THRESHOLD_NAMING_RULES.md` → `governance/<file>`. `SPEC_DRIVEN_…`,
  `TESTING_STRATEGY_TDD` stay (same dir).
- **T3 — AI_ASSISTANT_RULES template path.** `ucx_flow_v3/0X_TYPE/TYPE-TEMPLATE.yaml`
  → `layers/0X_TYPE/TYPE-TEMPLATE.yaml` (the `ucx_` token is engine/legacy and
  is banned by the hygiene check).
- **T4 — drop stale migration history.** Remove the `## v3.2 Changes from
  v3.0` sections from `SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` and
  `TESTING_STRATEGY_TDD.md` — they document the legacy SDD version lineage,
  which the fresh `framework/` `0.1.0` stream does not continue, and they
  carry banned `v3.x` tokens. The layer order they explain is already stated
  as current fact elsewhere in each doc.
- **T5 — drop the dead CHG_MIGRATION_PLAN link.** Remove that row from the
  QUICK_REFERENCE "Key Files" table — it points to a legacy v2→v3 migration
  doc not carried into `framework/`.
- **T6 — minor cleanup.** `AI_ASSISTANT_RULES.md` "CHG/ gates — not a v3
  concern" → "CHG gates — a governance overlay, outside layer authoring";
  drop the stray trailing ` |` at the end of `SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`.

## Conformance

Add `tests/conformance/test_root.py`: `framework/` root contains exactly
`README.md`, `VERSION`, and the 4 methodology docs. The 4 docs' *content* is
already covered by `test_spec_hygiene` (it scans all of `framework/`).

## Step sequence

1. Copy + transform the 4 docs into `framework/`.
2. Add `tests/conformance/test_root.py`.
3. **Verify** (below).
4. **Land:** commit; update `CHANGELOG.md`, `HANDOFF.md`, `MIGRATION_TODO.md`;
   record T4/T5 content removals in `DECISIONS.md` if non-obvious.

## Verification

- `python3 -m unittest discover -s tests/conformance` → all tests pass
  (hygiene confirms the 4 docs carry no `ucx_` / `SDD v3` / `v3.x` tokens;
  `test_root` confirms the root file set).
- Every repointed QUICK_REFERENCE link target resolves to a real file under
  `framework/` — checked explicitly.
- `diff` each transformed doc against its legacy source — confirm only the
  T1–T6 lines changed, nothing else.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Over-stripping — removing agnostic methodology content | T4 removes only the version-history sections; everything else copied verbatim; `diff` review in Verification |
| R2 | Repointed links silently broken | Verification resolves every QUICK_REFERENCE link target against disk |
| R3 | A missed `v3.x` / `ucx_` token | `test_spec_hygiene` scans the new files and fails the suite if any remain |

## Implementation (2026-05-19T10:00:00Z)

The 4 methodology docs copied + transformed into `framework/`;
`tests/conformance/test_root.py` added. Suite green at **25 tests**.
Verification all passed: every diff line maps to a T1–T6 rule (no accidental
edits — confirmed by `diff` against each legacy source); all 15 repointed
QUICK_REFERENCE links resolve to real files; hygiene scan finds no residual
`ucx_` / `SDD v3` / `v3.x` tokens. T4/T5 content removals recorded as D-0010.
`framework/` is now fully assembled. No deviations from plan.

## Review log

### Pass 1 — 2026-05-19T09:45:00Z

- **G1.** The `## v3.2 Changes from v3.0` sections (GUIDE, TESTING_STRATEGY)
  carry banned `v3.x` tokens and document legacy version lineage irrelevant to
  the fresh `0.1.0` stream. → T4 removes them; the layer order they explain is
  already stated as current fact in each doc (R1 guards over-stripping).
- **G2.** `AI_ASSISTANT_RULES.md` line 5 hard-codes `ucx_flow_v3/` — an
  engine/legacy path the hygiene check bans. → T3 repoints to `layers/`.
- **G3.** QUICK_REFERENCE links assume the legacy flat layout. → T2 repoints
  templates to `layers/`, registry to `registry/`, governance docs to
  `governance/`; T5 drops the dead `CHG_MIGRATION_PLAN.md` row.
- **G4.** `AI_ASSISTANT_RULES.md` "not a v3 concern" carries a `v3` token and
  is now inaccurate (CHG lives in `framework/governance/`). → T6 rewords it.
- **G5.** The 4 docs land in `framework/` root with no suite check on the root
  file set (the P1-T5 G3 blind-spot lesson). → add `test_root.py`.

### Pass 2 — 2026-05-19T09:50:00Z

Cross-checked Verification and scope:

- **G6.** Verification is sound: the suite's `test_spec_hygiene` already scans
  every `framework/` file, so a missed token fails the suite (R3) — no false
  negative. The per-doc `diff` catches accidental edits — no silent
  over-strip.
- **G7.** T2 link repointing is only safe if targets exist. Verified the
  target tree from the P1-T5 work: `framework/layers/0N_*/`,
  `framework/registry/LAYER_REGISTRY.yaml`, and the four `framework/governance/`
  docs all exist. Verification re-checks each link against disk.
- **G8.** A QUICK_REFERENCE link-checker in the conformance suite would be
  durable but is scope creep for P1-T7 — noted as a possible future
  enhancement, not added here.
- No new blockers. Ready to implement.
