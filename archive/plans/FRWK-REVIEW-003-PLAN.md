# FRWK-REVIEW-003 Plan — remediate the 2026-07-19 framework spec review

| Field          | Value                                                                 |
| -------------- | --------------------------------------------------------------------- |
| Task           | FRWK-REVIEW-003                                                        |
| Type           | bugfix                                                                 |
| Status         | DRAFT (surface-remediated) — 2026-07-19T00:00:00Z                                          |
| Depends on     | none (branch `feat/mvp-templates-and-bdd-docs` @ `dad219a7` is the subject) |
| Feeds          | framework spec remediation series; unblocks the MVP-templates branch    |
| Version impact | framework spec — **Task 2 MINOR; Tasks 3–9 PATCH each** (Task 7 becomes MINOR if fork B is chosen). Task 1 moves no version stream. Absolute numbers are deliberately not pinned (`PLAN_STANDARD.md:52-54`) |

## Objective

A five-lens review of the `framework/` engine-agnostic spec (2026-07-19, report
at `plans/reviews/FRAMEWORK-SPEC-REVIEW-2026-07-19.md`) found 2 blockers, 11 majors, and
~20 minors; a twelfth major (M12) surfaced while verifying this plan's ledger.
Both blockers were introduced by the MVP-templates commit `dad219a7` on the
current branch: the release-gate test is failing, and the 8 new MVP skeletons
are non-conformant with the framework's own normative governance — a document
authored from them cannot pass `sdd_doc_lint`. Underneath sits pre-existing
drift where **prose contracts and machine contracts disagree**:
`saga.schema.json` rejects IDs the registry allows, the `chg/` gates still teach
a trace contract abolished because it caused trace fabrication, and the
top-level README sells that same abolished contract as a headline feature.

This plan remediates every finding, and — because the largest clusters are
*recurrences of one failure mode* (a rule stated in prose with no mechanical
enforcement) — adds the missing conformance assertions so each class cannot
regress silently.

## Scope

**In:**

- BL-1 (release-gate test failing) and BL-2 (MVP skeletons non-conformant).
- All 12 MAJOR findings M1–M12 (M12 is new — see Approach §M12).
- All MINOR findings, each assigned to the task owning its surface
  (including the five the first draft of this plan dropped — see Task 4, 7, 9).
- Two new conformance assertions closing the prose-vs-machine gap
  (MVP registration/parity; saga↔registry ID-pattern lockstep).

**Out of scope (deferred — one-liners only, do not design here):**

- **TREND-1** — emit `AGENTS.md` in scaffolded target projects. → `plans/FRAMEWORK-TODO.md`.
- **TREND-2** — a Spec-Kit-style `constitution` slot for project principles. → `plans/FRAMEWORK-TODO.md`.
- **TREND-3** — post-implementation spec↔code drift detection (gates stop at IPLAN). → `plans/FRAMEWORK-TODO.md`.
- **TREND-4** — require spec citations in commit metadata. → `plans/FRAMEWORK-TODO.md`.
- **A generator that derives MVP skeletons from the full templates.** Task 2
  makes the skeletons correct and adds a test that *catches* divergence; a
  generator that *prevents* it is a larger build with no discovered issue
  demanding it yet.
- **Repo-wide GATE-SPEC E001–E004 compliance** (per-PR CHG records). The repo is
  currently non-compliant; that is a standing condition affecting every spec PR,
  not a defect this review found. See Approach §CHG-record status.
- Kiro `requirements.md` → EARS import (interop, no current consumer).
- The `examples/url-shortener/` corpus — the system-under-test, regenerated
  wholesale after framework changes, never hand-edited
  (CLAUDE.md §"Never hand-edit example artifacts").

## Approach / Design

### Per-PR obligations (apply to every task except Task 1)

Every task except Task 1 edits `framework/**` and is routed to **GATE-SPEC** by
target, not by resemblance to a layer (`GATE-SPEC_FRAMEWORK.md:48`). Four
mechanical obligations attach to each such PR:

| # | Obligation | Source | Notes |
| - | ---------- | ------ | ----- |
| O1 | Bump `framework/VERSION` (GATE-SPEC-E005) | `tests/chg/spec_gate.py:86` | Increment class per task, below |
| O2 | Both platform `FRAMEWORK_SPEC_VERSION` pins match (E006) | `scripts/sync-version-refs.sh:257` | Mechanical **only if** `framework/VERSION` is staged in the same commit *and* pre-commit is installed in the clone; V7 is the backstop |
| O3 | **Re-sync the plugin's vendored bundle** | `docs/PROJECT.md:131` | `bash tools/sync-plugin-framework.sh`, committed in the same change; `tests/conformance/platforms/test_plugin_framework_bundle.py` fails CI otherwise |
| O4 | `CHANGELOG.md` updated in the same diff (E008) | `tests/chg/spec_gate.py:86` | E007 (conformance green) is V2 |

**O3 is the one most easily missed and the most expensive to miss.** The plugin
ships a byte-identical copy of `framework/{layers,governance,registry}` so it
installs self-contained (D-0022). For scale: `dad219a7` touched **74** vendored
files alongside its 8 template additions. Every task below that edits
`framework/**` carries O1–O4 implicitly; they are not repeated per task.

Per GATE-SPEC-W003, agent-facing spec changes warrant a `SECURITY_REVIEW.md`
assessment. Tasks 2 and 8 change agent-facing guidance (templates, playbooks)
and carry that checklist; the rest correct non-behavioral prose.

### CHG-record status (E001–E004)

`GATE-SPEC_FRAMEWORK.md:147` lists `- [ ] CHG document created (>= C2)` in the
gate's exit checklist, and E003 requires `change_level ≥ C2` for any spec
change. **The repo does not currently produce these records** — `git ls-files`
finds CHG artifacts only in the example corpus and in `plans/`, and the most
recent spec PR (#306) landed on founder ratification plus the CI checks.

This plan continues the existing practice rather than unilaterally introducing
per-PR CHG paperwork. Stating it precisely: this is **pre-existing
non-compliance with a normative checklist item**, not an optional formality the
plan is declining to adopt. Whether to close that gap is a founder decision
affecting all spec PRs; it is listed Out of scope and should not be silently
resolved inside this remediation.

### Increment classes (no absolute version numbers)

`PLAN_STANDARD.md:52-54` authoring rule 5 forbids pinning absolute versions in a
plan, because they drift before the change lands. Per task:

| Task | Increment | Rationale |
| ---- | --------- | --------- |
| 1 | none | No `framework/**` in the diff |
| 2 | **MINOR** | Registry gains an `mvp_template:` field (additive). *Counter-precedent to note at PR time:* `dad219a7` added all 8 MVP templates as a PATCH, so classing their registration MINOR is arguably inconsistent with how their addition was versioned — flag it in the PR body and accept the founder's call |
| 3–6, 8, 9 | PATCH | Corrections to existing statements |
| 7 | PATCH (fork A) / MINOR (fork B) | See §Task 7 fork; fork B adds template + linter capability |

Tasks land in ascending order by default, but Tasks 3–9 are mutually
independent and may be reordered or reviewed in parallel; each PR takes the next
available version at the time it opens.

### Why nine PRs

Not a forced constraint — the first draft of this plan claimed governance Rule 1
compelled the split, which was wrong. `CLAUDE.md:333-337` defines a governance PR
as one touching `DECISIONS.md`, plan files, `CLAUDE.md`, or `.github/ai-review/`;
templates, the registry, playbooks and `framework/governance/*.md` prose are
**not** in that list, so Rule 1 is silent on eight of the nine tasks.

The split rests on reviewability and repo precedent instead: FRWK-REVIEW-002
shipped as four sequential spec PRs, and the clusters here are independently
revertible with disjoint blast radii. Two real constraints remain:

- **Task 2 should precede Tasks 3 and 9**, which reference the corrected MVP
  surface.
- **Task 6 is the one genuine governance PR** (it touches
  `governance/DECISIONS.md`). Note that Rule 1's 3-surface cap is in tension
  with the mandatory per-PR docs (O1–O4 plus HANDOFF/ROADMAP): Task 6 will touch
  ~7 surfaces regardless. Obtain the founder OK + commit-message audit line that
  Rule 1 requires for exceptions, or split the DECISIONS.md edit out.

### Task 2 — the MVP skeleton cluster (BL-2, M1, M2, M3)

Root cause is M1: the skeletons were added to `layers/*/` but never registered in
`LAYER_REGISTRY.yaml`, so the conformance suite never saw them. The suite passes
208/208 *because* the MVP surface is invisible to it — which is why the bodies
could ship non-conformant.

1. **Register.** Add `mvp_template: "<TYPE>-MVP-TEMPLATE.yaml"` to each of the 8
   layer entries, beside the existing `template:` field (`:30,43,56,76,89,102,115,128`).
2. **Define the profile.** The skeletons introduce `lifecycle: "mvp"` and a
   `document_control:` block defined in no governance doc. Add an **MVP profile**
   subsection to `governance/DOC_GOVERNANCE_CORE.md`: the full template is the
   default; the MVP skeleton is a non-standalone structural fast-pass; **an
   MVP-authored document is held to the identical lint contract** (this clause is
   what makes BL-2 a defect rather than a policy choice).
3. **Correct the 8 bodies:**
   - Legacy sequential element IDs → conforming placeholders, at
     `BRD-MVP:49`, `EARS-MVP:20`, `BDD-MVP:25`, `TDD-MVP:29`.
   - Add required upstream `@`-tag slots. Three skeletons omit required upstreams
     outright: `SPEC-MVP:70` lists only ADR (registry `:97` requires ears+bdd+adr),
     `TDD-MVP:62` only SPEC (registry `:110` requires ears+bdd+adr+spec),
     `IPLAN-MVP:52` only TDD (registry `:123` requires spec+tdd).
   - BDD carrier: the `ears:` key at `BDD-MVP:29` is already correctly nested
     inside the scenario — the defect is its **value** (`"REQ-E-01"`, a legacy
     sequential ID where an `EARS.NN.SS.hash` element ID is required). Also add
     `name:` and switch `priority:` (`:28`) to the
     `p0-critical|p1-high|p2-medium|p3-low` enum.
   - **Add the `metadata:` block.** All 8 skeletons have zero `metadata:` blocks;
     `test_layers.py:35-49` requires `metadata.layer` + `metadata.document_type`
     of a registered template.
   - Align section **key names** to the full templates
     (`architecture_decision_topics`→`adr_topics`, `execution`→`execution_commands`,
     etc.) — this is what closes M3's §-numbering misfire.
   - **Correct the `BRD-MVP:2` claim rather than trying to satisfy it.** Renaming
     keys does *not* make an MVP document validate against the full schema: BRD
     has 20 full keys vs 11 MVP, PRD 19 vs 10, IPLAN 12 vs 8. Satisfying
     "validates against the same schema" would require adding every required
     section — at which point the skeleton *is* the full template and its reason
     to exist evaporates. Replace the line with something true, e.g. *"section
     keys are a strict subset of `BRD-TEMPLATE.yaml`; a document authored from
     this skeleton must be completed against the full template before it validates."*
   - `brd_id: "BRD-00"` → `BRD-01` (`BRD-MVP:6`); `-00` is the reserved index
     number. `iplan_id: "IPLAN-001"` → `IPLAN-NN` (`IPLAN-MVP:5`), matching
     `IPLAN-TEMPLATE.yaml:61`.
   - Minors folded here: BRD-MVP's `upstream_documents`/`downstream_artifacts`
     key drift; lowercase status enums (`"draft"`) that no `Approved`-matching
     tool will match; the missing MVP reference line in
     `layers/08_IPLAN/IPLAN-00_index.TEMPLATE.yaml`; the `IPLAN-MVP:25` comment
     `# from TDD contract` sitting on a SPEC ID.
4. **Guard** — new file `tests/conformance/test_mvp_templates.py` with **three**
   assertions. A subset test alone is insufficient: it passes by construction on
   a *missing* required key, which is exactly the PRD-MVP
   (`functional_requirements` absent) and IPLAN-MVP (`execution` vs
   `execution_commands`) defects. Assert:
   - every registry-`required_tags` entry has a slot, and required section keys
     are **present** (not merely a subset);
   - no MVP-only keys exist that the full template lacks;
   - `metadata:` parses and matches the registry, mirroring `test_layers.py:35-49`.

   `test_layers.py` itself needs **no change** — it validates `layer["template"]`
   and continues to. Extending it to `mvp_template` would fail 8× on the missing
   `metadata:` blocks before step 3 lands.

M3 is closed by step 2's identical-lint-contract clause, step 3's key alignment,
and one line in each auditor playbook's C3 stating checks are calibrated to the
full-template profile (Task 8).

### Task 7 — threshold model reconciliation (M8): decision fork

`THRESHOLD_NAMING_RULES.md:42-57` mandates threshold blocks in **BRD, PRD and
ADR** with citations like `@threshold: ADR.15.circuit.failure.count`. Only
`PRD-TEMPLATE.yaml` carries the structure, and the reference linter resolves PRD
citations only (`sdd_doc_lint/__init__.py:2375`). Every BRD/ADR citation the
rules mandate is **unresolvable by design and unchecked**.

- **(A) Narrow the rules to PRD — recommended.** Matches the linter, the
  templates, and TH-RES-001 as implemented. One doc edit. **PATCH.**
- **(B) Widen the implementation to BRD/ADR.** Threshold blocks in both
  templates + linter regex + corpus regen. **MINOR.**

Recommend (A): the mandate has gone unimplemented long enough that nothing
depends on it, and (B) expands surface area to satisfy a rule no consumer asked
for. Task 7 also folds the LINT_RULES/REVIEW_TEAM severity mismatch (flat
`error` vs two-tier P1/P2) either way.

### M12 — new finding: the README sells an abolished contract

Not in the original report; found while verifying this plan's ledger. The repo
README describes the headline traceability feature as "**cumulative** `@`-tags"
at `README.md:90,158,189,261`. But `TRACEABILITY.md:12` states the contract is
"**not** the cumulative closure of every preceding" layer, and `:42` records that
NECESSARY-UPSTREAM-001 *replaced* the cumulative contract after it caused trace
fabrication.

`DESC.md` mirrors the same five lines and must be fixed in the same task, or the
verification passes green with half the surface untouched.

## File structure

### Created

| Path | Purpose |
| ---- | ------- |
| `tests/conformance/test_mvp_templates.py` | MVP registration, required-key presence, no-extra-keys, `metadata:` parity (Task 2) |
| `tmp/mvp-lint-fixtures/<TYPE>-MVP-sample.yaml` ×8 | Throwaway documents authored from each corrected skeleton, to run V5. `tmp/` per CLAUDE.md — not committed |

### Modified

| Path | Change | Task |
| ---- | ------ | ---- |
| `framework/VERSION` + `platforms/*/FRAMEWORK_SPEC_VERSION` | O1/O2 bump + pin sync | 2–9 |
| `platforms/claude-code-plugin/framework/**` | O3 vendored-bundle re-sync (~74 files/PR) | 2–9 |
| `CHANGELOG.md` | Task 1: stamp the Unreleased MVP entry (`### Added`, `:15`); then O4 entry per PR | all |
| `framework/registry/LAYER_REGISTRY.yaml` | `mvp_template:` ×8; `:230` dead anchor; `:127` IPLAN tmp path; `optional:` semantics | 2, 3 |
| `framework/layers/*/[A-Z]*-MVP-TEMPLATE.yaml` (8) | IDs, tag slots, `metadata:`, key names, enums, BDD carrier, `:2` claim | 2 |
| `framework/governance/DOC_GOVERNANCE_CORE.md` | MVP-profile subsection | 2 |
| `framework/layers/{06_SPEC,07_TDD,08_IPLAN}/README.md` | Upstream rows → registry truth; drop "Single unified template" | 3 |
| `framework/governance/chg/gates/{GATE-01,GATE-03,GATE-08}_*.md`, `GATE_ERROR_CATALOG.md` | Cumulative-4-tag resolutions; element-level tag examples | 4 |
| `framework/governance/chg/CHG-00_index.TEMPLATE.md` | Title `CHG-000` → `CHG-00` | 4 |
| `framework/governance/saga.schema.json` | `^[A-Z]+-[0-9]{2}$` → `^[A-Z]+-\d{2,}$` (`:29`) | 5 |
| `framework/governance/{PROFILE-TEMPLATE.yaml,TRACEABILITY.md,THRESHOLD_NAMING_RULES.md,ADAPTATION_SURFACE.yaml}` | Knob count + engine token; `spec_trace`; segment cap; `review_mode` default | 5 |
| `framework/governance/{DEFINITION_OF_DONE.md,REVIEW_REMEDIATION_FLOW.md,DECISIONS.md}` | Name the real invariant (judge ≠ generator) | 6 |
| `framework/governance/{THRESHOLD_NAMING_RULES.md,LINT_RULES.md,REVIEW_TEAM.md}` | Threshold model + severity tiering (fork); `:145` dead anchor; `:305` auditor-layer list | 7 |
| `framework/playbooks/{08_IPLAN/auditor.md,02_PRD/auditor.md,01_BRD/auditor.md,08_IPLAN/operator.md,05_ADR/architect.md,07_TDD/operator.md}` | Align checks to spec + real template sections | 8 |
| `README.md`, `DESC.md`, `docs/REPO_STRUCTURE.md`, `docs/PARITY.md` | Content-hash + cumulative claims; staleness; stub-removal contradiction | 9 |
| `framework/{README.md,QUICK_REFERENCE.md,AI_ASSISTANT_RULES.md,SPEC_DRIVEN_DEVELOPMENT_GUIDE.md,layers/04_BDD/README.md}` | MVP integration; EARS 5 patterns; drop the Gherkin-output claim | 9 |
| `plans/{FRAMEWORK-TODO.md,HANDOFF.md,DECISIONS.md}`, `ROADMAP.md` | TREND entries; continuity; fork resolutions | all |

## Implementation sequence

### Task 1 (T1): Unblock the release-gate test (BL-1)

- Retitle the `[Unreleased]` MVP entry (`CHANGELOG.md:15`) to carry the version
  stamp the file's own convention requires:
  `### Added — Framework Spec 0.37.1 → 0.37.2 — MVP skeleton templates …`.
- Append the four TREND one-liners + a cross-reference to this plan to
  `plans/FRAMEWORK-TODO.md` Open (per its "don't double-track" rule).
- **Test-first:** `python3 -m unittest tests.release.test_changelog_entry` fails
  now (verified); it must pass after.
- **Why this fix shape is right:** the test was already corrected on 2026-06-29
  (`RELEASE-CHANGELOG-TEST-CONVENTION-GAP`, closed) to accept the version in
  *either* a released `## [X.Y.Z]` heading *or* an `[Unreleased]`
  `### … X → Y` subsection. So this is not a convention mismatch to work
  around — the Unreleased entry simply omits the version string the
  supported convention requires. Adding the stamp is the intended usage.
- **Sequencing note:** this is a *latent local* failure — no CI workflow runs
  `tests/release/` (`grep -rn "tests/release" .github/workflows/` → empty;
  `CHANGELOG.md:854` records the same). So nothing is currently misreporting CI
  state. Land it first because it is one line and removes a false signal from
  local runs, not because it blocks anything.

### Task 2 (T2): MVP skeleton conformance + registration (BL-2, M1, M2, M3)

- **Test-first:** write `tests/conformance/test_mvp_templates.py` with the three
  assertions above. It must fail against the current 8 skeletons before any body
  is edited — that failure is the machine-checkable restatement of BL-2.
- Execute Approach §Task 2 steps 1→4 in order.
- Re-run the full conformance suite; the 208 existing tests stay green.
- Carry the `SECURITY_REVIEW.md` checklist (W003).

### Task 3 (T3): Registry + layer-README truth-up (M4 + registry minors)

- SPEC/TDD/IPLAN README upstream rows → registry `required_tags` (`:97`, `:110`,
  `:123`); drop the now-false "Single unified template" rows.
- Registry `:230` dead anchor → the real heading ("Coverage gates"); `:127`
  IPLAN `tmp/` path → the project-docs-relative convention.
- Give `optional:` defined semantics tied to `ADAPTATION_SURFACE.yaml`
  `skippable`, **or delete it** — no tool reads it today, and an unread boolean
  in the "single source of truth" is what invited this drift. Record the call in
  `plans/DECISIONS.md`.

### Task 4 (T4): `chg/` subtree staleness sweep (M6)

- Delete the cumulative-4-tag resolution at `GATE-03:233-238` and the equivalent
  at `GATE_ERROR_CATALOG.md:206` + its 4-tag template block; both contradict the
  E007 row in their own files (`GATE-03:78`, `catalog:63`).
- Convert document-level tag examples (`GATE-01:199`, `GATE-03:235-238`) to
  element-level form per GD-03/REFGRAN01 — **restricted to element-declaring
  layers** (`@brd`, `@prd`, `@ears`, `@bdd`, `@adr`, `@tdd`). **Exclude `@spec:`
  and `@iplan:`**: `GATE-08:227` reads `@spec: SPEC-XX`, which is the *correct*
  doc-level form because SPEC is element-ID-exempt (`TAG_SYNTAX.md:24`). Task 8
  relies on that same fact; converting it here would contradict Task 8.
- Sweep the whole subtree for both classes; fix the `CHG-00_index` title
  (`CHG-000` → `CHG-00`).

### Task 5 (T5): Machine-contract lockstep (M5 + governance minors)

- **Test-first:** add a conformance assertion that `saga.schema.json`
  `artifact_id.pattern` equals `LAYER_REGISTRY.yaml` `id_patterns.document`. It
  fails today (`^[A-Z]+-[0-9]{2}$` at `:29` vs `^[A-Z]+-\d{2,}$` at `:215`).
- Fix the schema pattern. The schema's own comment demanded a lockstep change
  that prose could not enforce — the assertion is the point of this task.
- Fold: PROFILE-TEMPLATE knob count (5→6, add `quality_loop_max_iterations`) and
  its Claude-Code vocabulary leak; `TRACEABILITY.md:122` `spec_trace` on an EARS
  gate; THRESHOLD segment-cap self-contradiction; `review_mode` default
  qualification.

### Task 6 (T6): Name the self-approval invariant (M7) — governance PR

- Replace "mirrors CHG **C1**" at `DEFINITION_OF_DONE.md:21` and
  `REVIEW_REMEDIATION_FLOW.md:134`, and "failure code **C1**" at
  `governance/DECISIONS.md:236`, with the real invariant — **judge ≠ generator**
  (the term `DEFINITION_OF_DONE.md:20` already uses correctly one line above).
- The citation is not merely vague, it is **inverted**: in the CHG overlay C1 is
  the *trivial* level whose approval matrix reads "Self"
  (`GATE_INTERACTION_DIAGRAM.md:244`).
- Add the P0–P3 ↔ critical/medium/low mapping (or state the vocabularies are
  independent).
- This PR exceeds Rule 1's 3-surface cap once O1–O4 + HANDOFF are counted —
  obtain the founder OK + audit-trail commit line, or split the DECISIONS.md
  edit into its own follow-up.

### Task 7 (T7): Threshold model reconciliation (M8) — **needs the founder's call**

- Resolve the fork in Approach §Task 7 (recommended: **A**, narrow to PRD).
- Fold the LINT_RULES/REVIEW_TEAM severity mismatch.
- Fold two `REVIEW_TEAM.md` minors while in the file: the `:145` dead anchor
  (§"Structural floor checks" exists nowhere) and the `:305` Auditor-C1 layer
  list (omits IPLAN/CHG which do carry the lens; includes BRD which does not).
- **Ordering note:** Task 5 also edits `THRESHOLD_NAMING_RULES.md` (segment cap).
  Whichever lands second rebases onto a changed file.

### Task 8 (T8): Playbook corrections (M9, M10 + playbook minors)

- `08_IPLAN/auditor.md:65` — stop mandating `IPLAN.NN.SS.xxxx` step IDs at P1;
  `ID_NAMING_STANDARDS.md:173` says **MAY** and `:191` says "do not penalize".
  Same file's C1 must use doc-level `@spec: SPEC-NN` (SPEC declares no elements).
- `02_PRD/auditor.md:59` — replace the fictitious 15-section outline with the
  real one from `PRD-TEMPLATE.yaml` (`total_sections: 15`, Document Control §1);
  fix the C4/C5 §-pointers that shift with it.
- Minors: BRD auditor's "§Personas" (PRD owns personas); the `{doc-slug}`
  element-ID pattern in the BRD/PRD auditors; `08_IPLAN/operator.md` attributing
  reversibility to SPEC (ADR owns it).
- **Playbook-vs-template field gaps** — ADR reversibility label and TDD per-class
  runtime/flake budgets are demanded by playbooks but scaffolded by no template,
  so every conformant document draws those findings. Resolve each in one
  direction (add the template field **or** drop the check) and record it in
  `plans/DECISIONS.md`. Do not leave a check that cannot be satisfied.
- Add the one-line full-template-profile calibration note to each auditor C3
  (closes M3's playbook half).
- **Deferred, explicitly:** the "No-findings rationale" block duplicated in 19 of
  51 playbooks and absent from 32. It is a consistency nit with no correctness
  impact, and deduplicating it touches all 51 files — out of proportion to this
  remediation. Log to `plans/FRAMEWORK-TODO.md`.
- Carry the `SECURITY_REVIEW.md` checklist (W003).

### Task 9 (T9): Entry-doc accuracy (M11, M12 + doc minors)

- **M11** — qualify the content-hash claim at `README.md:84,90,158,189,261`; the
  spec says IDs are "intended as" content hashes with verification opt-in and
  advisory (`ID_NAMING_STANDARDS.md:129,142-146`).
- **M12** — replace "cumulative `@`-tags" at the same lines **and the mirrored
  five lines in `DESC.md`** per `TRACEABILITY.md:12,42`.
- MVP integration into `QUICK_REFERENCE.md` Templates table,
  `AI_ASSISTANT_RULES.md:5`, and the `framework/README.md:61-64` layout.
- Minors: `docs/PARITY.md` stub-removal contradiction (`:10` v1.0.0 vs `:148`
  v0.6.0); `docs/REPO_STRUCTURE.md` as-built drift (3 of 16 workflows, missing
  `playbooks/`, 3 of 10 tools); EARS reduced to one of five patterns;
  `layers/04_BDD/README.md:22-23` claiming Gherkin output support that exists
  nowhere; `DESC.md` — wire into `sync-version-refs.sh`, shrink to an abstract,
  or delete (referenced from nowhere, drifted twice).

## Verification

| #  | Check (command or observable) | Expected result | Maps to |
| -- | ----------------------------- | --------------- | ------- |
| V1 | `python3 -m unittest tests.release.test_changelog_entry` | PASS (fails today) | T1 / BL-1 |
| V2 | `python3 -m pytest tests/conformance -q` | 208 existing + new tests green | every task / E007 |
| V3 | `python3 -m unittest tests.conformance.test_mvp_templates` | Fails before T2 body edits, passes after | T2 / BL-2 |
| V4 | Saga↔registry pattern-equality assertion | Fails before T5, passes after | T5 / M5 |
| V5 | `PYTHONPATH=tools python3 -m sdd_doc_lint tmp/mvp-lint-fixtures/` | Zero TAG01 / ID03 / REFGRAN01 / BDD-SCHEMA-001 / STRUCT01 findings | T2 / BL-2 |
| V6 | `python3 tests/chg/spec_gate.py` on each PR diff | E005 + E008 satisfied | all / O1, O4 |
| V7 | `cat framework/VERSION platforms/*/FRAMEWORK_SPEC_VERSION` | All three identical | all / O2 |
| V8 | `bash tools/sync-plugin-framework.sh && git diff --exit-code platforms/claude-code-plugin/framework/` | No diff (bundle already re-synced); `test_plugin_framework_bundle` green | all / O3 |
| V9 | Registry `required_tags` vs the three layer README Upstream rows | Equal for SPEC, TDD, IPLAN | T3 / M4 |
| V10 | `grep -rniE "all 4 upstream\|4 traceability tags" framework/governance/chg/` | Zero hits (each phrasing currently matches exactly one line) | T4 / M6 |
| V11 | `grep -rn "CHG \*\*C1\*\*" framework/governance/` | Zero hits | T6 / M7 |
| V12 | `grep -rn "@threshold: \(BRD\|ADR\)\." framework/governance/` | Zero hits under fork A; resolvable under fork B | T7 / M8 |
| V13 | Re-run the affected auditor playbooks against the regenerated corpus | Zero findings from checks the templates cannot satisfy; before/after readiness scores recorded | T8 / M9, M10 |
| V14 | `grep -rn "cumulative" README.md DESC.md` | No survivals asserting cumulative tags as current | T9 / M12 |
| V15 | Fresh-context agent re-runs the five review lenses on the final state | Zero surviving BLOCKER/MAJOR from this report | plan closure |

## Docs to update

- [ ] `CHANGELOG.md` — entry per PR (O4/E008 makes this blocking)
- [ ] `framework/VERSION` + both platform pins (O1/O2)
- [ ] `platforms/claude-code-plugin/framework/**` — re-synced bundle (O3)
- [ ] `ROADMAP.md` — bullet for the remediation series
- [ ] `plans/HANDOFF.md` — narrative + next steps, refreshed per PR
- [ ] `plans/DECISIONS.md` — T7 fork; the `optional:`-field call (T3); each
      playbook field-gap direction (T8)
- [ ] `plans/FRAMEWORK-TODO.md` — four TREND entries (T1) + the deferred
      playbook-section dedup (T8)

## Risks

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | Correcting the `BRD-MVP:2` schema claim (rather than satisfying it) may read as weakening a guarantee | med | It is the only truthful option — measured today the MVP skeletons carry 11 of 20 BRD keys, 10 of 19 PRD, 8 of 12 IPLAN. Satisfying the claim collapses the skeleton into the full template. State the subset relationship precisely instead |
| R2 | Forgetting the O3 vendored-bundle re-sync lands the PR red | **high** | It is the single most-missed obligation (74 files in `dad219a7`); V8 is a hard gate, and O3 is listed once per-PR rather than per-task so it cannot be read as optional |
| R3 | Nine PRs each bumping VERSION produces churn and a long review tail | med | Tasks 3–9 are independent and reviewable in parallel; only Task 2 must precede 3 and 9 |
| R4 | The T7 fork stalls on the founder, blocking the series | med | T7 is independent — sequence it last; the rest proceeds |
| R5 | Corpus drift: tag/registry/playbook changes invalidate `examples/url-shortener/` | high | CLAUDE.md §Development workflow item 2 mandates a corpus cross-check for exactly these change classes; corpus is fixed by regen, never by hand |
| R6 | Fixing playbook checks (T8) shifts readiness scores on regenerated corpora | med | Expected and desirable — the checks were unsatisfiable. V13 records before/after so the shift is attributable |
| R7 | Pre-existing CI `composition` / `audit-trail` `startup_failure` blocks normal merges | high | Founder-owned and pre-existing (HANDOFF); every PR may need `--admin`. Not this plan's problem; do not attempt a CI fix here |
| R8 | Task 6 exceeds governance Rule 1's 3-surface cap once mandatory per-PR docs are counted | med | Get the founder OK + audit-trail commit line Rule 1 requires, or split the DECISIONS.md edit into a follow-up |

## Claim ledger

> Citations are `path:line` opened and read while drafting. Paths are relative to
> the repo root (`/opt/data/aidoc-flow/framework`).

| #  | Claim | Symbol | Citation |
| -- | ----- | ------ | -------- |
| 1  | Framework spec version is `0.37.2` | 0.37.2 | framework/VERSION:1 |
| 2  | The release-gate test exists and fails on this branch | def test_changelog_has_entry_for_current_version | tests/release/test_changelog_entry.py:19 |
| 3  | The Unreleased heading needing the version stamp | ### Added | CHANGELOG.md:15 |
| 4  | No CI workflow runs `tests/release/`, so BL-1 is latent-local not CI-red | so it was latently RED at HEAD (invisible only because CI doesn't | CHANGELOG.md:855 |
| 5  | BRD-MVP uses a banned sequential element ID | id: "FR-01" | framework/layers/01_BRD/BRD-MVP-TEMPLATE.yaml:49 |
| 6  | EARS-MVP likewise | id: "REQ-E-01" | framework/layers/03_EARS/EARS-MVP-TEMPLATE.yaml:20 |
| 7  | BDD-MVP likewise | id: "SC-01" | framework/layers/04_BDD/BDD-MVP-TEMPLATE.yaml:25 |
| 8  | TDD-MVP likewise | id: "TC-01" | framework/layers/07_TDD/TDD-MVP-TEMPLATE.yaml:29 |
| 9  | BDD-MVP priority is off-enum | priority: "P1" | framework/layers/04_BDD/BDD-MVP-TEMPLATE.yaml:28 |
| 10 | BDD-MVP `ears:` is correctly nested; its **value** is a legacy ID | ears: | framework/layers/04_BDD/BDD-MVP-TEMPLATE.yaml:29 |
| 11 | BRD-MVP asserts full-schema validity | Validates against the same schema | framework/layers/01_BRD/BRD-MVP-TEMPLATE.yaml:2 |
| 12 | BRD-MVP claims the reserved index number | brd_id: "BRD-00" | framework/layers/01_BRD/BRD-MVP-TEMPLATE.yaml:6 |
| 13 | IPLAN-MVP uses a 3-digit ID | iplan_id: "IPLAN-001" | framework/layers/08_IPLAN/IPLAN-MVP-TEMPLATE.yaml:5 |
| 14 | …contradicting the full template | iplan_id: "IPLAN-NN" | framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml:61 |
| 15 | IPLAN-MVP comment misattributes a SPEC ID to TDD | # from TDD contract | framework/layers/08_IPLAN/IPLAN-MVP-TEMPLATE.yaml:25 |
| 16 | SPEC requires 3 upstream tags | required_tags: [ears, bdd, adr] | framework/registry/LAYER_REGISTRY.yaml:97 |
| 17 | SPEC-MVP declares only ADR | - type: "ADR" | framework/layers/06_SPEC/SPEC-MVP-TEMPLATE.yaml:70 |
| 18 | TDD requires 4 upstream tags | required_tags: [ears, bdd, adr, spec] | framework/registry/LAYER_REGISTRY.yaml:110 |
| 19 | TDD-MVP declares only SPEC | - type: "SPEC" | framework/layers/07_TDD/TDD-MVP-TEMPLATE.yaml:62 |
| 20 | IPLAN requires spec+tdd | required_tags: [spec, tdd] | framework/registry/LAYER_REGISTRY.yaml:123 |
| 21 | IPLAN-MVP declares only TDD | - type: "TDD" | framework/layers/08_IPLAN/IPLAN-MVP-TEMPLATE.yaml:52 |
| 22 | Registry registers one template per layer; no `mvp_template` key exists | template: "BRD-TEMPLATE.yaml" | framework/registry/LAYER_REGISTRY.yaml:30 |
| 23 | Conformance validates only the registered `template` | layer["template"] | tests/conformance/test_layers.py:19 |
| 24 | …and requires a `metadata:` block of it (which all 8 MVP files lack) | class LayerTemplateMetadata | tests/conformance/test_layers.py:34 |
| 25 | Element IDs are mandated in `TYPE.NN.SS.hash` form | element: | framework/registry/LAYER_REGISTRY.yaml:216 |
| 26 | Saga schema rejects 3+ digit document IDs | "^[A-Z]+-[0-9]{2}$" | framework/governance/saga.schema.json:29 |
| 27 | …while the registry allows them | document: "^[A-Z]+-\\d{2,}$" | framework/registry/LAYER_REGISTRY.yaml:215 |
| 28 | GATE-03 E007 row states 2 required ADR tags | @ears @bdd (2 tags | framework/governance/chg/gates/GATE-03_REQUIREMENTS_ARCHITECTURE.md:78 |
| 29 | …its own resolution demands 4 | ADR must have all 4 upstream tags: | framework/governance/chg/gates/GATE-03_REQUIREMENTS_ARCHITECTURE.md:233 |
| 30 | Error catalog repeats it in different wording (so V10 needs both patterns) | Add 4 traceability tags to ADR | framework/governance/chg/gates/GATE_ERROR_CATALOG.md:206 |
| 31 | …contradicting its own 2-tag row | Add the 2 required upstream tags | framework/governance/chg/gates/GATE_ERROR_CATALOG.md:63 |
| 32 | `GATE-08:227` `@spec:` is doc-level and CORRECT — exclude it from T4's sweep | @spec: SPEC-XX (Component Definition) | framework/governance/chg/gates/GATE-08_IPLAN.md:227 |
| 33 | Cumulative trace was abolished for causing fabrication | NECESSARY-UPSTREAM-001 | framework/governance/TRACEABILITY.md:42 |
| 34 | Contract is explicitly not cumulative | **not** the cumulative closure | framework/governance/TRACEABILITY.md:12 |
| 35 | README still sells cumulative tags (M12) | Content-hash element IDs + cumulative | README.md:90 |
| 36 | …and repeats it | Content-hash IDs + cumulative tags | README.md:261 |
| 37 | DESC.md mirrors the same claim, so V14 must cover it | Content-hash element IDs + cumulative | DESC.md:90 |
| 38 | "CHG C1 = no self-approval" cited in DoD | mirrors CHG **C1** | framework/governance/DEFINITION_OF_DONE.md:21 |
| 39 | …and in the remediation flow | mirrors CHG **C1** | framework/governance/REVIEW_REMEDIATION_FLOW.md:134 |
| 40 | …and in the governance decision log | **C1** across the CHG gates | framework/governance/DECISIONS.md:236 |
| 41 | But CHG C1 *permits* self-approval | C1 (Patch) | framework/governance/chg/gates/GATE_INTERACTION_DIAGRAM.md:244 |
| 42 | IPLAN step element IDs are optional by spec | step-level operations **MAY** carry | framework/governance/ID_NAMING_STANDARDS.md:173 |
| 43 | …and auditors are told not to penalize them | do not penalize | framework/governance/ID_NAMING_STANDARDS.md:191 |
| 44 | Yet the IPLAN auditor mandates them at P1 | C2 — IPLAN step IDs conform | framework/playbooks/08_IPLAN/auditor.md:65 |
| 45 | PRD auditor enforces a non-existent outline | §1 Overview, §2 Problem Statement | framework/playbooks/02_PRD/auditor.md:59 |
| 46 | …against a template whose §1 is Document Control | total_sections: 15 | framework/layers/02_PRD/PRD-TEMPLATE.yaml:30 |
| 47 | SPEC README understates required upstreams | \| Upstream \| ADR + BDD \| | framework/layers/06_SPEC/README.md:37 |
| 48 | TDD README omits EARS | \| Upstream \| SPEC + ADR + BDD \| | framework/layers/07_TDD/README.md:26 |
| 49 | IPLAN README adds a non-required ADR | \| Upstream contract \| TDD + SPEC + ADR \| | framework/layers/08_IPLAN/README.md:59 |
| 50 | REVIEW_TEAM dead anchor (dropped minor, now assigned to T7) | Structural floor checks | framework/governance/REVIEW_TEAM.md:145 |
| 51 | REVIEW_TEAM auditor-layer list is wrong at both ends | lives at BRD, PRD, BDD, ADR, TDD | framework/governance/REVIEW_TEAM.md:305 |
| 52 | CHG index template title uses 3 digits | CHG-000 | framework/governance/chg/CHG-00_index.TEMPLATE.md:2 |
| 53 | PARITY self-contradicts on stub removal | 14 utilities + 2 deprecated redirect stubs | docs/PARITY.md:10 |
| 54 | …versus | redirect stubs (scheduled for removal in | docs/PARITY.md:148 |
| 55 | GATE-SPEC governs any `framework/` edit, by target | routed to GATE-SPEC by its **target** | framework/governance/chg/gates/GATE-SPEC_FRAMEWORK.md:48 |
| 56 | GATE-SPEC's exit checklist requires a CHG record (repo is non-compliant) | - [ ] CHG document created (>= C2) | framework/governance/chg/gates/GATE-SPEC_FRAMEWORK.md:147 |
| 57 | E005/E008 are CI-enforced per PR | GATE-SPEC-E005 | tests/chg/spec_gate.py:86 |
| 58 | Platform spec pins are auto-synced when VERSION is staged | platforms/*/FRAMEWORK_SPEC_VERSION | scripts/sync-version-refs.sh:257 |
| 59 | **A spec change must re-sync the plugin's vendored bundle** | bash tools/sync-plugin-framework.sh | docs/PROJECT.md:134 |
| 60 | …guarded by a conformance drift test | test_plugin_framework_bundle.py | docs/PROJECT.md:136 |
| 61 | …and the spec gate reminds on every run | bash tools/sync-plugin-framework.sh | tests/chg/spec_gate.py:120 |
| 62 | Rule 1 applies only to DECISIONS/plan/CLAUDE.md/ai-review PRs | A **governance PR** is any PR that touches | CLAUDE.md:334 |
| 63 | Rule 1's 3-surface cap | ### Rule 1 — Small scope (≤3 doc surfaces per PR) | CLAUDE.md:341 |
| 64 | Plans must not pin absolute version numbers | **No magic version strings.** | framework/layers/08_IPLAN/PLAN_STANDARD.md:51 |
| 65 | The plan standard's section catalog | ## Section catalog | framework/layers/08_IPLAN/PLAN_STANDARD.md:55 |

## Review log

### Pass 1 — 2026-07-19 — self-review

- **Nine PRs read as over-engineering against CLAUDE.md §"Minimal-and-realistic
  plans".** Re-checked: every task maps to discovered findings, zero speculative
  features. Added a justification subsection. The four TREND items — the only
  speculative material — were parked as Out-of-scope one-liners, not designed.
- **Change-management framing was missing entirely.** Every task edits
  `framework/**` and routes to GATE-SPEC; without the obligations table the plan
  would produce PRs that fail CI on arrival. Added.
- **M8 was drafted as a unilateral fix.** It is a genuine fork with different
  version impacts. Restructured with a recommendation, and a risk so it cannot
  block the rest of the series.
- **New finding M12 surfaced while verifying a ledger row** — the README sells
  the exact contract TRACEABILITY.md records as abolished for causing trace
  fabrication. Folded into Task 9.
- **Task 2 originally said "fix IDs and tags"** without addressing section keys,
  leaving `BRD-MVP:2`'s claim false and M3 unresolved. Added the key-alignment step.

### Pass 2 — 2026-07-19 — independent (fresh-context)

Adversarial review against source; 27 findings, 16 load-bearing. All verified
before folding — the reviewer was correct on every point I re-checked, including
one filename detail it got slightly wrong (the drift guard is at
`tests/conformance/platforms/test_plugin_framework_bundle.py`, not
`tests/conformance/`). Folded:

- **The vendored plugin-bundle re-sync was absent from the entire plan** — the
  single most consequential finding. `docs/PROJECT.md:134` makes
  `bash tools/sync-plugin-framework.sh` a per-spec-change obligation, guarded by
  a conformance drift test; `dad219a7` touched **74** such files. Eight of nine
  PRs would have landed red. Added as obligation O3 with R2, V8, a File-structure
  row, and a docs-to-update item.
- **"The release gate is red" was false.** No CI workflow runs `tests/release/`
  (verified; `CHANGELOG.md:854` says the same). Restated Task 1 as a latent local
  failure and removed the "first and alone" forced framing.
- **Governance Rule 1 does not force the nine-PR split.** `CLAUDE.md:334`'s
  definition covers DECISIONS/plan/CLAUDE.md/ai-review PRs only — not templates,
  registry, playbooks or governance prose. Rewrote the justification to rest on
  reviewability + FRWK-REVIEW-002 precedent, and admitted the contradiction the
  reviewer caught: Task 6 exceeds the 3-surface cap anyway once O1–O4 are
  counted (now R8, with the founder-OK path).
- **The absolute version ladder violated `PLAN_STANDARD.md:51` authoring rule 5**
  ("no magic version strings") and broke under this plan's own reordering
  allowance. Replaced with increment classes; noted the `dad219a7`-was-PATCH
  counter-precedent for Task 2's MINOR.
- **Task 2's "align section keys" did not achieve its stated goal.** Renaming
  keys while keeping a subset does not make an MVP document validate against the
  full schema (BRD 11 of 20 keys, PRD 10 of 19, IPLAN 8 of 12). Re-resolved as
  align names **and** correct the `:2` claim to a true subset statement; R1 rewritten.
- **The proposed subset test could not catch two named BL-2 defects** — a subset
  assertion passes by construction on a *missing* required key, which is exactly
  PRD-MVP's absent `functional_requirements` and IPLAN-MVP's `execution` vs
  `execution_commands`. Test respecified with three assertions (required-key
  presence, no MVP-only keys, `metadata:` parity).
- **The `metadata:` sub-finding of BL-2 was dropped.** Verified: all 8 skeletons
  have zero `metadata:` blocks. Added to Task 2 step 3 — and this is why
  extending `test_layers.py` (as the first draft proposed in one table while
  proposing a new file in another) would fail 8× immediately. Contradiction
  resolved in favour of the new file; `test_layers.py` now correctly listed as
  unchanged.
- **Tasks 4 and 8 gave contradictory instructions about `@spec:`.** `GATE-08:227`
  is doc-level *correctly* (SPEC is element-ID-exempt), which Task 8 itself
  asserts. Scoped Task 4's conversion to element-declaring layers and excluded
  `@spec:`/`@iplan:` explicitly.
- **V9 could not detect the defect it was assigned.** `"all 4 upstream tags"`
  matches exactly one line; the catalog uses different wording. Replaced with a
  two-pattern check (now V10).
- **Five minors were silently dropped** despite Scope claiming "All MINOR
  findings": two REVIEW_TEAM nits → Task 7, the IPLAN-MVP comment → Task 2, the
  `CHG-000` title → Task 4. The playbook "No-findings rationale" duplication is
  now an *explicit* deferral with a rationale, not an omission.
- **M12's verification covered half its surface** — `DESC.md` mirrors the same
  five lines. V14 and the Task 9 step now name it.
- **The CHG-record framing was wrong.** `GATE-SPEC_FRAMEWORK.md:147` lists a CHG
  record in the exit checklist, so this is pre-existing *non-compliance*, not
  "new paperwork" the founder might optionally want. Restated honestly, moved to
  Out of scope, ledgered.
- **Four tasks had no verification row** (T3, T6, T7, T8 — T8 being the largest
  behavioral change). Added V9, V11, V12, V13.
- **E006 "Automatic" was overstated** — conditional on VERSION being staged and
  pre-commit being installed. Qualified.
- **`sdd_doc_lint` invocation would not resolve** without `PYTHONPATH=tools`, and
  V5's fixture documents existed in no task. Both fixed.
- Six ledger citations corrected (`BRD-MVP` `brd_id` `:5`→`:6` — a regression I
  introduced by over-applying an IPLAN-specific line correction; `CLAUDE.md`
  `:298`→`:341`; `BDD-MVP` `:27`→`:28/:29` with the claim restated to name the
  *value* not the placement; `GATE-SPEC` `:47`→`:48`; `DECISIONS.md` `:235`→`:236`;
  `LAYER_REGISTRY` `:214`→`:216`). Ledger grew 50 → 65 rows, adding the
  previously-uncited bundle, CI, plan-standard, `metadata:` and Rule 1 claims.
- Objective's "12 majors" corrected to 11 found by the review + 1 added here.
- Task headings renamed to the `### Task N` form the plan standard specifies,
  retaining `(TN)` labels so the tables still key cleanly.

### Pass 3 — 2026-07-19 — self-review of Pass 2 folds

Re-validated that Pass 2's edits introduced no new inconsistency:

- Task/label usage is now uniform: nine `### Task N (TN)` headings, and the
  increment-class, File-structure, Verification and Risk tables all key on
  `T1`–`T9` with no orphans in either direction.
- V15 (fresh-context re-run of the five lenses) remains the closure check and now
  has V8–V14 beneath it covering every task individually.
- The O3 obligation is stated once in the per-PR table rather than repeated per
  task, matching how O1/O2/O4 are handled — no task-level drift possible.
- Confirmed the two surviving cross-task file collisions are documented as
  ordering notes, not conflicts (`THRESHOLD_NAMING_RULES.md` in Tasks 5 and 7;
  `REVIEW_TEAM.md` in Tasks 7 and 8's calibration note).

**Result:** ready — no further load-bearing findings.
