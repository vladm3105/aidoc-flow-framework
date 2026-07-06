# ENG-STALE-DEPTH-DOCS Plan — reconcile the Hermes sdd-orchestrator's published root-docs + governance docs to the single-path model (dead Lite/Standard/Full depth-variant tables + a dead-link to a nonexistent SDD_DEPTH_GUIDE.md)

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | ENG-STALE-DEPTH-DOCS (FRAMEWORK-TODO P2; the Hermes legs of H-11a) |
| Type           | fix (doc accuracy)                          |
| Status         | READY — 2026-07-06 (Pass 2 independent fresh-context; Pass 3 self) |
| Depends on     | none (completes H-11 / D-0053's deferred H-11a) |
| Feeds          | the sdd-orchestrator's user-facing setup docs stop advertising a review-model the engine abandoned |
| Version impact | **Hermes PATCH** (`0.7.1 → 0.7.2`; skill `2.1.0 → 2.1.1`). **No framework change** — Hermes-published docs corrected to the already-decided single-path model. No GATE-SPEC, no re-vendor. **No new decision** — governed by the 2026-06-12 legacy-sdd-depth cleanup + [[D-0053]]; this plan closes the tracked TODO, no D-NNNN minted. |

## Objective

The v3.2-era **SDD-Lite / SDD-Standard / SDD-Full depth-variant** model was removed on
2026-06-12 (single-path adaptive loop; all 8 layers required per NECESSARY-UPSTREAM-001).
That cleanup fixed `sdd_config.yaml` + the repo `README.md`, and [[D-0053]] (H-11) fixed
the two **loaded** governance files. But the sdd-orchestrator's **user-facing published
docs** still advertise the dead model, and one file **contradicts itself**:

- **`root-docs/README.md`** — the `:3` tagline still says "with **Scalable Depth**" and
  `:100-106` still publishes the **"SDD Depth Variants"** table (SDD-Lite/Standard/Full,
  a nonexistent `REF` layer, and per-tier month "timelines") — while `:224-229` of the
  **same file** already states the correct single-path model ("no `lite | standard | full`
  depth tiers"). A reader hitting the table first gets the wrong model.
- **`root-docs/MULTI_PROJECT_QUICK_REFERENCE.md:15-17`** + **`MULTI_PROJECT_SETUP_GUIDE.md:17-25`**
  — two more SDD-Lite/Standard/Full selection tables (a setup guide telling a user to
  "select" a dead tier).
- **`MULTI_PROJECT_SETUP_GUIDE.md:52`** + **`governance/README.md:38`** — both link to
  **`governance/SDD_DEPTH_GUIDE.md`**, which **does not exist** (dead links).
- **`governance/CHG_GOVERNANCE_BRIDGE.md:19-20`** — "Full-depth programs require all CHG
  gates. Lite/Standard may use subset gates by policy" (a governance rule keyed on the dead
  tiers).
- **`governance/github/LABEL_REGISTRY.yaml:155`** + **`scripts/setup-ai-pr-review-labels.sh:86-87`**
  — CHG-label group comments named "SDD-Full" (a dead term; cosmetic, not behavioral).

The FRAMEWORK-TODO entry named only 2 of these surfaces; the grounding grep found **6**.

## Scope

**In (behavior-/accuracy-correcting):**

- **`root-docs/README.md`** — `:3` drop "with Scalable Depth"; replace the `:100-106`
  "SDD Depth Variants" section with the single-path model (all 8 layers required;
  MVP → PROD → NEW MVP; CHG overlay), consistent with the file's own `:224-229` prose. Do
  not enumerate a `REF` layer (it does not exist) or month timelines (violates the
  no-time-estimates rule).
- **`root-docs/MULTI_PROJECT_QUICK_REFERENCE.md:15-17`** — replace the depth-variant table
  with the single 8-layer path.
- **`root-docs/MULTI_PROJECT_SETUP_GUIDE.md`** — `:17-25` replace "SDD Depth Selection" +
  table with the single-path model; `:52` remove the dead `SDD_DEPTH_GUIDE.md` link (keep
  the live `framework/README.md` reference); `:1273` — the embedded v2.4 changelog line
  "SDD Depth Selection now shows v3 8-layer pipeline" references the heading being removed
  (and still carries the dead "Depth Selection" term) → reword to "SDD setup now shows the
  single 8-layer pipeline" (de-references the removed heading; preserves the historical
  fact).
- **`governance/README.md:38`** — remove the dead `governance/SDD_DEPTH_GUIDE.md` list
  entry.
- **`governance/CHG_GOVERNANCE_BRIDGE.md:19-20`** — replace the Lite/Standard subset-gate
  rule with the current model: CHG is an orthogonal governance overlay (its gates apply to
  changes; there are no depth tiers to key a subset off).
- **`governance/github/LABEL_REGISTRY.yaml:155`** (a YAML comment) + **`scripts/setup-ai-pr-review-labels.sh:86`**
  (a shell comment) + **`:87`** (a `log_info` runtime string "Creating CHG labels (SDD-Full
  only)...") — drop the dead "SDD-Full" term (→ "CHG change management" / "Creating CHG
  labels..."). **No `create_label` name/color/value is touched** — the emitted labels are
  identical.
- Bump Hermes `0.7.1 → 0.7.2`, skill `version: 2.1.0 → 2.1.1`; both CHANGELOGs; close
  `ENG-STALE-DEPTH-DOCS` in FRAMEWORK-TODO; note the H-11a partial-close in
  `HERMES-BACKLOG.md`; HANDOFF.

**Out of scope (deferred — with rationale):**

- **The public GitHub README render leg** (ENG-STALE-DEPTH-DOCS leg (a) — "guard against
  the stale public render at the released tag"). This repo's own `README.md` is already
  single-flow (grep-clean); the "public render" concern is about a released-tag snapshot /
  downstream mirror, not an editable file in this tree. Track as a one-line residual in the
  TODO close-note; not an edit here.
- **Authoring an `SDD_DEPTH_GUIDE.md`.** The correct fix for the two dead links is to
  **remove the references** (the depth guide describes a dead model — recreating it would
  re-publish the anachronism). No new file.
- **The remaining cosmetic "v3.2" string residue** across the 72-file inherited governance
  scaffold (H-11a proper) — unchanged; still deferred. This plan closes only the
  **behavioral depth-model** legs of H-11a, not the version-string sweep.

## Approach / Design

Single canonical replacement model, adapted from the clean 2026-06-12 deprecation note
already vetted in `governance/templates/sdd_config.yaml:4-15`: *"The framework runs a
**single SDD path** — all 8 layers (BRD → PRD →
EARS → BDD → ADR → SPEC → TDD → IPLAN) are required by the **necessary-upstream contract**
(NECESSARY-UPSTREAM-001); there are no Lite/Standard/Full depth tiers. The adaptive
lifecycle is MVP → PROD → NEW MVP; reality deltas enter via the **CHG** governance
overlay."* Point at `framework/README.md` / `TRACEABILITY.md` as the authority rather than
re-enumerate layer sets, so the docs cannot re-drift.

Dead links are **removed**, not repointed (the target describes a dead model). No
`framework/` file is touched → no GATE-SPEC, no re-vendor. No engine code. No new decision
(the model was decided 2026-06-12 + reaffirmed in D-0053).

## File structure

### Modified

| Path | Change |
| ---- | ------ |
| `.../sdd-orchestrator/root-docs/README.md` | `:3` tagline + `:100-106` depth table → single-path |
| `.../sdd-orchestrator/root-docs/MULTI_PROJECT_QUICK_REFERENCE.md` | `:15-17` table → single-path |
| `.../sdd-orchestrator/root-docs/MULTI_PROJECT_SETUP_GUIDE.md` | `:17-25` table + `:52` dead link + `:1273` embedded-changelog line → single-path, link removed, heading de-referenced |
| `.../sdd-orchestrator/governance/README.md` | `:38` dead `SDD_DEPTH_GUIDE.md` entry removed |
| `.../sdd-orchestrator/governance/CHG_GOVERNANCE_BRIDGE.md` | `:19-20` subset-gate rule → CHG overlay |
| `.../sdd-orchestrator/governance/github/LABEL_REGISTRY.yaml` + `.../governance/scripts/setup-ai-pr-review-labels.sh` | "SDD-Full" comment → "CHG governance" |
| `.../sdd-orchestrator/SKILL.md` | `version: 2.1.0 → 2.1.1` |
| `platforms/hermes/VERSION` (→ `0.7.2`) + Hermes CHANGELOG + root CHANGELOG | version + entries |
| `plans/FRAMEWORK-TODO.md` (close ENG-STALE-DEPTH-DOCS) / `plans/HERMES-BACKLOG.md` (H-11a partial) / `plans/HANDOFF.md` | docs |

## Verification

| #  | Check | Expected | Maps to |
| -- | ----- | -------- | ------- |
| V1 | grep the 6 target docs for `SDD-Lite`/`SDD-Standard`/`SDD Depth Variants`/`SDD Depth Selection`/`Scalable Depth`/`subset gates` | absent | dead-table removal |
| V2 | grep the orchestrator tree for `SDD_DEPTH_GUIDE` | absent (dead links removed) | dead-link fix |
| V3 | grep the orchestrator tree for behavioral depth phrasing (`SDD-Lite`/`SDD-Full`/`depth variant`/`depth selection`/`scalable depth`) — excluding legitimate negations ("no … depth tiers") + the `sdd_config.yaml` deprecation note (which correctly state the model is dead and are KEPT) | absent (incl. the `:1273` changelog line, reworded) | full sweep |
| V4 | `root-docs/README.md` no longer self-contradicts (`:100` region agrees with the `:224-229` single-path prose) | consistent | README self-contradiction |
| V5 | `git diff` of `LABEL_REGISTRY.yaml` + `setup-ai-pr-review-labels.sh` shows **no `create_label` name/color/description value changed** — only the comment + `log_info` string | label names/values identical | no label behavior change |
| V6 | `SKILL.md version` = `2.1.1`; `platforms/hermes/VERSION` = `0.7.2` | bumped | version |
| V7 | `git diff --stat` touches no `framework/**` path | zero framework files | no GATE-SPEC |
| V8 | `python -m pytest tests/conformance -q` + `platforms/hermes/tests -q` | green (prose/comment-only) | no regression |

## Docs to update

- [ ] `platforms/hermes/CHANGELOG.md` — `[0.7.2]`
- [ ] root `CHANGELOG.md` — Hermes `0.7.1 → 0.7.2`
- [ ] `plans/FRAMEWORK-TODO.md` — move `ENG-STALE-DEPTH-DOCS` to Closed (Hermes legs; public-render leg noted as residual)
- [ ] `plans/HERMES-BACKLOG.md` — note H-11a's behavioral-depth legs closed (version-string sweep still open)
- [ ] `plans/HANDOFF.md` — progress

## Risks

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | Rewording the `LABEL_REGISTRY.yaml`/script comments accidentally changes a label name → breaks label setup | low | comment-only edits; V5 diffs the values; the CHG label names are unchanged |
| R2 | Removing the `SDD_DEPTH_GUIDE.md` links orphans a real navigation need | low | the file does not exist (already a dead link); `framework/README.md` is the live target and stays |
| R3 | Missed a depth-table surface | low | V3 full-tree grep for behavioral phrasing (not just the named files) |
| R4 | Scope creep into the cosmetic v3.2 sweep (H-11a proper) | low | only behavioral depth-MODEL content in scope; version-string residue explicitly deferred |

## Claim ledger

| #  | Claim | Symbol | Citation |
| -- | ----- | ------ | -------- |
| 1  | README tagline advertises "Scalable Depth" | `Scalable Depth` | platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/root-docs/README.md:3 |
| 2  | README publishes the dead "SDD Depth Variants" table | `## SDD Depth Variants` | platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/root-docs/README.md:100 |
| 3  | The same README already states the correct single-path model (self-contradiction) | `depth tiers` | platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/root-docs/README.md:227 |
| 4  | QUICK_REFERENCE publishes a second SDD-Lite/Standard/Full table | `SDD-Lite` | platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/root-docs/MULTI_PROJECT_QUICK_REFERENCE.md:15 |
| 5  | SETUP_GUIDE has an "SDD Depth Selection" table | `SDD Depth Selection` | platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/root-docs/MULTI_PROJECT_SETUP_GUIDE.md:17 |
| 6  | SETUP_GUIDE dead-links to a nonexistent SDD_DEPTH_GUIDE.md | `SDD_DEPTH_GUIDE.md` | platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/root-docs/MULTI_PROJECT_SETUP_GUIDE.md:52 |
| 7  | governance/README.md lists the nonexistent SDD_DEPTH_GUIDE.md | `SDD_DEPTH_GUIDE.md` | platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/governance/README.md:38 |
| 8  | CHG_GOVERNANCE_BRIDGE keys a governance rule on the dead tiers | `Lite/Standard may use subset gates` | platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/governance/CHG_GOVERNANCE_BRIDGE.md:20 |
| 9  | LABEL_REGISTRY comment uses the dead "SDD-Full" term | `SDD-Full` | platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/governance/github/LABEL_REGISTRY.yaml:155 |
| 10 | The canonical single-path replacement wording already exists (the clean deprecation note) | `the v3.2-era` | platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/governance/templates/sdd_config.yaml:5 |
| 11 | Single-path authority — necessary-upstream contract | `NECESSARY-UPSTREAM-001` | framework/governance/TRACEABILITY.md:38 |
| 12 | Current Hermes version is 0.7.1 (→ 0.7.2 PATCH) | `0.7.1` | platforms/hermes/VERSION:1 |
| 13 | Skill version is 2.1.0 (→ 2.1.1) | `version: 2.1.0` | platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/SKILL.md:4 |
| 14 | ENG-STALE-DEPTH-DOCS is the open FRAMEWORK-TODO entry being closed | `ENG-STALE-DEPTH-DOCS` | plans/FRAMEWORK-TODO.md:615 |

## Review log

### Pass 1 — 2026-07-06 — self-review

Initial draft. Grounded the scope against the tree (grep-verified 6 surfaces vs the TODO's
2). Confirmed: `sdd_config.yaml` + `README.md:224-229` are already clean (not in scope);
`SDD_DEPTH_GUIDE.md` does not exist (dead links → remove, not repoint); the
`LABEL_REGISTRY`/script hits are comment-only (cosmetic term, included as trivial). No
`framework/` file involved → no GATE-SPEC. No new decision (model decided 2026-06-12 +
D-0053). Pending: independent Pass 2.

### Pass 2 — 2026-07-06 — independent (fresh-context adversarial)

All 14 citations verified at source; framework-boundary, no-new-D-number, dead-link-removal,
and "SDD_DEPTH_GUIDE.md does not exist" calls confirmed sound; the two other tree hits
(`GOVERNANCE_RULES.md` / `governance-load-protocol.md`) are correct negations already fixed
by H-11/D-0053 and rightly excluded. Findings folded:

- **[LOAD-BEARING] Missed surface `MULTI_PROJECT_SETUP_GUIDE.md:1273`** — an embedded v2.4
  changelog line "SDD Depth Selection now shows v3 8-layer pipeline" matches V3's grep and
  references the `:17` heading being removed; left unscoped, V3 "absent" would be false and
  the removed heading would be orphaned. → **Pulled into scope** (reword to drop "Depth
  Selection"); V3 note updated.
- **[MINOR] `setup-ai-pr-review-labels.sh:87` is a `log_info` runtime string, not a
  comment** — the plan mis-labeled `:86-87` "comment-only." → Scope + V5 reworded to "no
  `create_label` name/value changed" (the edit is still safe; labels identical).
- **[NIT] Ledger #3 anchor `no` was non-unique** → changed to `depth tiers`.
- **[NIT] Approach said "verbatim"** while the wording differs slightly from
  `sdd_config.yaml` → changed to "adapted from."

### Pass 3 — 2026-07-06 — self-review (re-validate the Pass-2 fold)

Re-checked: the `:1273` reword de-references the removed heading AND clears the last "Depth
Selection" token so V3's clean-sweep assertion holds; V5 now diffs `create_label` values
(not "comment-only"), correctly covering the `log_info` edit; the KEEP set (the two H-11
negations + `sdd_config.yaml` + README `:224-229`) is explicitly excluded from V3 so the
sweep won't false-positive on the legitimate deprecation notes. Scope now = 7 orchestrator
doc/script surfaces + version + docs-of-record; still Hermes-only (no `framework/`), no new
decision. No new gaps.

**Result:** ready
