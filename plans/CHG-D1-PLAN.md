# CHG-D1 Plan — the framework-spec change gate (GATE-SPEC), end to end

| Field      | Value                          |
|------------|--------------------------------|
| Task       | CHG-D1                         |
| Depends on | D-0019 / ADAPT (knowledge-extractor spec→CHG draft is *blocked* on this), `framework/governance/chg/` overlay, P3-T7 (`doc-chg` + `gate-check`), Hermes `validation/chg_rules.py` (P2-T9), `docs/PROJECT.md` §6, ROADMAP CHG-D1 |
| Status     | DONE — 2026-05-23T00:00:00Z (5 commits; framework spec 0.3.0; conformance 43; Hermes CHG 8/8) |
| Feeds      | unblocks knowledge-extractor's spec promotion; CHG-D2 (record as a `framework/governance/` decision) |

## Objective

ROADMAP CHG-D1: implement change management as **skills + CI/CD**, twice against
the same `framework/` spec (plugin skills + Hermes server-side). The concrete
gap is that the five existing gates (GATE-01/03/06/08/CODE) all govern a change
to an **artifact instance** in a project's BRD→Code chain — none governs a
change to the **`framework/` spec itself** (templates, governance, registry,
VERSION). That missing gate is the `docs/PROJECT.md` §6 "Process" role and is
exactly what `knowledge-extractor`'s spec→CHG drafts are stamped *blocked* on.
This task adds **GATE-SPEC** — the framework-spec governance gate — to the
shared spec, wires it into both platforms (plugin skills + Hermes server-side),
adds the automatable CI enforcement, and unblocks the spec-promotion path.

## Scope

**In:**

- **Shared spec (the contract):** a new `GATE-SPEC` gate definition + a `spec`
  `change_source`; ripple through the error catalog, interaction diagram,
  CHG-TEMPLATE enums, `chg/README.md`, `governance/README.md`; conformance
  guards.
- **Plugin (Platform B) skills:** `gate-check` runs GATE-SPEC; `doc-chg`
  classifies a spec-targeting change to `change_source: spec`/GATE-SPEC;
  `knowledge-extractor` **unblocked** (spec target → real CHG record + GATE-SPEC,
  no longer "blocked on the unbuilt gate").
- **CI/CD (automatable, repo-level):** a diff-aware guard script
  (`tests/chg/spec_gate.py`) + a workflow that runs it and the conformance suite
  as a required status check. The **human** approval half is GitHub branch
  protection / required reviewers — *documented*, never self-approved.
- **Hermes (Platform A) server-side:** extend `validation/chg_rules.py` to route
  - validate `spec`/GATE-SPEC records; extend its unit tests.
- **Close:** decision record, version bump (spec minor `0.2.0 → 0.3.0` + ripple),
  CHANGELOG/ROADMAP/PROJECT §6/PARITY/MIGRATION_TODO/HANDOFF.

**Out (deferred):**

- **CHG-D2** — graduating this decision into a formal `framework/governance/`
  record (separate ROADMAP item; noted as the immediate follow-up).
- **Building** GitHub branch protection itself — repo-settings, user-only; we
  document the required configuration.
- **Relocating** the new workflow into `.github/workflows/` — in-container lacks
  the `workflows` permission (5th documented restriction); file stages at
  `plans/workflows-pending/` for the user, same pattern as P4-T3.
- The artifact-cascade gates' own behavior — untouched.

## Approach

### GATE-SPEC is orthogonal to the artifact cascade

The 01→03→06→08→CODE gates govern a project's **artifact instances** and cascade
down the layer chain. GATE-SPEC governs the **shared contract that defines the
layers** — it is a *meta* gate. Its "cascade" is not L1→Code; it is: *a spec
change forces both platforms to re-declare `FRAMEWORK_SPEC_VERSION` and re-pass
the shared conformance suite.* The docs must frame it this way so it is never
wired into the artifact cascade.

### The checks, split by enforcer (ROADMAP CHG-D1's three-way split)

**Record-level** — `gate-check` skill + Hermes `chg_rules.py` read the CHG yaml:

- `GATE-SPEC-E001` (Provenance) — spec change carries justification:
  `change_description.why` **and** `.trigger` non-empty; a promotion references
  the motivating `.aidoc/learnings.md` / profile signal.
- `GATE-SPEC-E002` (Classification) — `change_control.semver_impact` present and
  one of `major|minor|patch`; a `major` (breaking) change must be C3.
- `GATE-SPEC-E003` (Classification) — a framework-spec change is **never C1**
  (it always reaches ≥2 consumers); must be ≥ C2.
- `GATE-SPEC-E004` (Approval) — a C3 spec change requires
  `gate_approval.gate == GATE-SPEC` + a non-null `approver` (human sign-off; the
  skill never fills it).

**Repo-level** — CI workflow + conformance suite (diff-aware / static):

- `GATE-SPEC-E005` (Versioning) — `framework/VERSION` changed when any
  `framework/**` content changed in the PR. *(diff-aware → CI)*
- `GATE-SPEC-E006` (Conformance) — both platforms' `FRAMEWORK_SPEC_VERSION` ==
  `framework/VERSION`. *(static → already `test_version_declaration`; the gate
  references it)*
- `GATE-SPEC-E007` (Conformance) — the shared conformance suite passes.
  *(CI runs it)*
- `GATE-SPEC-E008` (Documentation) — `CHANGELOG.md` updated in the PR.
  *(diff-aware → CI)*

**Human** — repo settings (documented, not code):

- GATE-SPEC approval = branch protection / required reviewers on `framework/**`.

**Warnings:** `W001` major change without a per-platform migration note;
`W002` change touches only one platform's conformance (parity drift).

### Approval matrix (added for GATE-SPEC)

| Level | Spec-change approvers |
|-------|-----------------------|
| C2 | framework maintainer + 1 platform owner |
| C3 (breaking) | framework maintainer + **both** platform owners |
| Emergency | not a typical spec path (spec changes are not production hotfixes) |

### Branch

Continue on **`claude/skill-revision`** — the current HEAD, where ADAPT +
`knowledge-extractor` (the unblock target) live, recorded user-confirmed in
HANDOFF. The task-setup default `claude/multi-platform-migration-AamWB` would
orphan this work from its dependency; do **not** switch (R4).

## Step sequence

**Increment 1 — shared spec (the contract).**

1. NEW `framework/governance/chg/gates/GATE-SPEC_FRAMEWORK.md` — full gate def
   mirroring GATE-01's structure (purpose/scope, entry criteria, E/W checklist
   E001–E008 + W001–W002, approval matrix, exit criteria, routing, error
   catalog), with the explicit *orthogonal/meta* framing.
2. EDIT `gates/GATE_ERROR_CATALOG.md` — new "GATE-SPEC: Framework Spec Errors"
   section; update the `GATE-NN-SNNN` note (NN ∈ {01,03,06,08,CODE,SPEC}); add
   to Related Documents.
3. EDIT `gates/GATE_INTERACTION_DIAGRAM.md` — a small separate "Spec-governance
   gate (meta)" block + rows in the selection / source-entry tables; Related.
4. EDIT `chg/CHG-TEMPLATE.yaml` — additive only: `spec` in the `change_source`
   guidance table + value comments; `GATE-SPEC` in `entry_gate` +
   `gate_approval.gate` enums; new `change_control.semver_impact: null` field
   with guidance; glossary "Gate" definition updated.
5. EDIT `chg/README.md` — GATE-SPEC in the Files table + a `Spec` row in Change
   Source Routing + a short "Spec-governance gate" subsection (the Process
   role, orthogonal to the cascade).
6. EDIT `governance/README.md` — soften the "CHG returns post-Phase-5" line to
   note the spec gate now exists.
7. EDIT `tests/conformance/test_governance.py` — add the gate file to
   `EXPECTED_FILES` (enforced present + not "unexpected"); add a GATE-SPEC
   well-formedness test (error catalog contains `GATE-SPEC-E001..E004`;
   CHG-TEMPLATE `change_source` guidance + enums mention `spec`/`GATE-SPEC`).
8. **Verify**: conformance green; CHG-TEMPLATE parses.

**Increment 2 — plugin skills.**
9. EDIT `gate-check/SKILL.md` — GATE-SPEC row (selected by **target** = the
   change edits `framework/`, not by artifact layer); runs E001–E004; names
   E005–E008 as CI-enforced; human approval via branch protection.
10. EDIT `doc-chg/SKILL.md` (+ `-autopilot`/`-audit`/`-fixer` as the review of
    the family shows necessary, R8) — classify a `framework/`-targeting change →
    `change_source: spec`, `entry_gate: GATE-SPEC`, set `semver_impact`, ≥C2.
11. EDIT `knowledge-extractor/SKILL.md` — **unblock**: spec target → real CHG
    record + GATE-SPEC (hand to `doc-chg` → `gate-check`); drop the "blocked on
    the unbuilt spec-gate" stamp; update Output contract + Quick Reference.
    First **grep the plugin skills + `ADAPTATION.md` §7** for `blocked` /
    `not yet built` / `CHG-D1` to catch every spot that asserts the gate is
    missing (the doc-level D-0019/HANDOFF references are updated at close).
11b. EDIT `doc-flow/SKILL.md` (Change-management section enumerates the gates as
    "GATE-01/03/06/08/CODE") + `skill-recommender` if it lists gates — add
    GATE-SPEC. Check `chg/CHG-00_index.TEMPLATE.md` for a gate/source enumeration
    too.
12. **Verify**: `plm_lint --all` clean; conformance green; manual walk-through
    (extractor → spec CHG record → gate-check GATE-SPEC).

**Increment 3 — CI enforcement (automatable repo-level).**
13. NEW `tests/chg/spec_gate.py` — diff-aware guard (`--base <ref>`), owning the
    **diff-aware** codes only: if `framework/**` changed → assert
    `framework/VERSION` changed (E005) + `CHANGELOG.md` changed (E008); exit
    nonzero with the `GATE-SPEC-E005/E008` codes. **No-op (exit 0)** on a
    non-`framework/` diff. E006 (FSV match) + E007 (suite green) are *not*
    duplicated here — the workflow covers them via the conformance suite step.
14. NEW `plans/workflows-pending/chg-gate.yml` — runs `spec_gate.py` (with the
    PR base) **and** the conformance suite (E006+E007) as a required check.
    Staged, not in `.github/workflows/` (R1). Document the branch-protection
    requirement (the human GATE-SPEC approval half).
15. EDIT `tests/conformance/` — a lightweight guard that `tests/chg/spec_gate.py`
    is importable and declares the codes it owns (`GATE-SPEC-E005`, `E008`), so
    the script can't silently rot out of sync with the gate def.
16. **Verify**: run `python tests/chg/spec_gate.py --base <merge-base>` on a
    synthetic spec-change vs a non-spec diff; conformance green.

**Increment 4 — Hermes server-side.**
17. EDIT `platforms/hermes/src/mcp_server/validation/chg_rules.py` — add
    `GATE-SPEC` to `_VALID_GATES`; `spec → GATE-SPEC` in `_SOURCE_TO_GATE`;
    in `check_gate_layer_coverage`, **return a pass early for GATE-SPEC** (its
    scope is the framework, not L1–L8 — do *not* add an artifact-layer mapping,
    which would trip the "not in typical scope" warning); new
    `check_spec_change_requirements` (≥C2, provenance, `semver_impact`,
    C3→approval) wired into `run_chg_validation_checks`. **First grep Hermes for
    a strict CHG key-schema** (e.g. a JSON/YAML schema enumerating allowed keys)
    that the new `semver_impact` field could violate (R7); validation here is
    `.get`-based and permissive, so additive should be safe.
18. EDIT `platforms/hermes/tests/unit/test_chg_rules.py` — cases: spec routes to
    GATE-SPEC; missing provenance fails; C1 spec rejected; valid C3 spec passes.
19. **Verify**: `pytest platforms/hermes/tests/unit/test_chg_rules.py` + full
    Hermes suite green; conformance green.

**Increment 5 — close.**
20. `plans/DECISIONS.md` D-00XX (design + 3-way enforcer split + branch-
    protection model). Confirm the **version bump** with the user (spec minor
    `0.2.0 → 0.3.0` + ripple to both `FRAMEWORK_SPEC_VERSION` + 54 skills'
    `framework_spec_version` + `last_updated`, same as ADAPT close).
21. `CHANGELOG.md` `[Unreleased]`; `docs/PROJECT.md` §6 (TODO → implemented);
    `ROADMAP.md` (CHG-D1 done; CHG-D2 remaining); `docs/PARITY.md` (both
    platforms implement GATE-SPEC); `plans/MIGRATION_TODO.md` tick; HANDOFF.
22. **Verify** (full suite below). **Land** per increment with conventional
    commits; push to `claude/skill-revision`.

## Verification

- `python3 -m unittest discover -s tests/conformance` — green at every increment
  (currently 37; +GATE-SPEC well-formedness + spec_gate-importable guard → ~39).
- `python3 tests/conformance/platforms/plm_lint.py --all` — clean.
- `python3 tests/chg/spec_gate.py --base <merge-base>` — passes on a compliant
  spec change; fails with `GATE-SPEC-E005` (no VERSION bump) / `E008` (no
  CHANGELOG) on a non-compliant spec diff; **no-ops** (exit 0) on a
  non-`framework/` diff.
- `cd platforms/hermes && python -m pytest tests/unit/test_chg_rules.py` (and the
  full suite) — green; additive only.
- Version-match: `framework/VERSION` == both `FRAMEWORK_SPEC_VERSION` == every
  plugin skill's `framework_spec_version` after the close bump.
- Manual: a spec promotion flows extractor → `doc-chg` (`change_source: spec`)
  → `gate-check` (GATE-SPEC, E001–E004 run, E005–E008 named, approval left to a
  human) with no "blocked" stamp.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | In-container can't push `.github/workflows/**` (no `workflows` perm — 5th restriction). | Workflow stages at `plans/workflows-pending/chg-gate.yml`; document relocation (P4-T3 pattern). Never include workflow edits in an in-container push. |
| R2 | GATE-SPEC wrongly wired into the artifact cascade (it is orthogonal/meta). | Explicit meta framing in the gate def + diagram; Hermes coverage check special-cases it (scope = framework, not L1–L8). |
| R3 | Hermes change breaks its 447-test suite. | Additive only; `.get`-based permissive validation; run the full Hermes suite. |
| R4 | Branch discrepancy (`skill-revision` vs the task-setup default). | Continue on `skill-revision` — current HEAD, holds the dependency (`knowledge-extractor`), user-confirmed in HANDOFF; do not switch. |
| R5 | Version-bump ripple must keep the version-match test green (both FSV + 54 skills). | Scripted, identical to ADAPT close; conformance enforces. |
| R6 | Implying we *enforce* the human-approval half (we can't — it's GitHub settings). | Document the branch-protection requirement; reiterate the hard "skill never self-approves" rule (already in `gate-check`). |
| R7 | New `semver_impact` field ripples to Hermes' CHG schema validation. | Additive optional field; Hermes reads via `.get`; verify Hermes suite. |
| R8 | `doc-chg` *family* (autopilot/audit/fixer), not just the base, may need the spec source. | Increment 2 reviews the whole family; wire only what authors/checks the source/gate. |

## Review log

### Pass 1 — 2026-05-23T00:00:00Z

- **E006 duplicated.** spec_gate.py originally recomputed the FSV-match (already
  a static conformance test). Scoped the script to the diff-aware codes it
  uniquely owns (E005, E008); E006/E007 stay with the conformance suite, which
  the workflow runs alongside. (steps 13–15, Verification)
- **Hermes coverage mapping.** Adding `_GATE_TO_LAYERS["GATE-SPEC"]` would trip
  the "layer not in typical scope" warning (a spec change's areas —
  template/governance/registry — aren't L1–L8). Changed to an early pass-return
  for GATE-SPEC instead; no artifact-layer mapping. (step 17)
- **"Blocked" text lives in more than one place.** knowledge-extractor stamps it
  in the body, the Output-contract table, and Quick Reference — plus possibly
  `ADAPTATION.md` §7. Added a grep-first sweep so none is missed. (step 11)
- **doc-flow / skill-recommender / CHG-00 index enumerate the gate set.** Added
  step 11b to add GATE-SPEC there for accuracy.
- **`semver_impact` schema risk.** Added an explicit grep-first for a strict
  Hermes CHG key-schema before adding the field. (step 17, R7)

### Pass 2 — 2026-05-23T00:00:00Z

- **Change-level vs semver_impact coupling (E002).** The gate ties `major` →
  must be C3. But C2 is "section update" and C3 is "cross-layer". A `minor`
  (additive) spec change like GATE-SPEC *itself* is C2 yet reaches both
  platforms. Confirmed the rule is one-directional and sound: only `major`
  forces C3; `minor`/`patch` may be C2. No plan change, but the gate def must
  state the mapping as `major→C3 (required)`, `minor/patch→C2 allowed` to avoid
  a false E002 on legitimate additive changes (like this very task).
- **This task is itself a GATE-SPEC change** (it edits `framework/`). It is a
  `minor` (additive: new gate + new source) spec change → C2; lands under the
  same interim PR-review controls as D-0019 (the gate can't gate its own
  introduction). Noted so the close commit/CHANGELOG frame it correctly; not a
  bootstrap paradox because E005/E008 (VERSION + CHANGELOG bump) *are* satisfied
  by increment 5.
- **spec_gate.py base ref in CI.** A push/PR workflow needs the merge-base, not
  a raw `origin/main` (which may be ahead). Plan says "with the PR base"; the
  workflow will use `git merge-base origin/<base> HEAD` (or the PR base SHA from
  the event) — pinned in the workflow file, not the script. No script change.
- No further findings — plan is implementable. Proceeding.
