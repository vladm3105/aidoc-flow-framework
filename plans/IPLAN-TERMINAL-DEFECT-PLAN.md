# IPLAN Post-Completion Defect Plan — implement #656 (via #657 vehicle)

| Field | Value |
|-------|-------|
| Task | IPLAN-TERMINAL-DEFECT |
| Type | feature |
| Status | DRAFT — 2026-09-21T00:00:00Z |
| Depends on | #656 (gap report), #657 (design proposal); GD-30 / Type-R flow (landed 0.55.0); #569 precedent (status as write-target) |
| Feeds | mirror PR for #657 Phase 3; IPLAN-VERIFY guidance; GOV-013 linter carve-out |
| Version impact | MINOR stream (`0.55.0 → 0.56.0`, to confirm at implementation kickoff): additive template fields + governance prose + new lint checks; no removal of `combined` default, no registry shape change |

## GitHub issues — triage (2026-09-21)

| Issue | State | Verdict | Wired into |
|-------|-------|---------|------------|
| #656 IPLAN lifecycle has no terminal-state / post-completion defect pattern | OPEN | **Real but narrow — in scope as the gap.** Lifecycle-completeness + broken TMP reference + validation-completeness; not a missing lifecycle. Its fix shape ("both terminal", mandatory `detection_gap`, `Related-IPLAN` bypass) is **rejected**; the vehicle comes from #657 | Decisions D1–D3, D6, D9; Tasks 2–4 |
| #657 Scoped bugfix IPLAN for terminal-plan defects | OPEN | **In scope as the vehicle.** Supersedes #656's annotation-only shape ("without a new IPLAN" already conceded insufficient by the same author). Its 5 maintainer questions are the acceptance gate for the mirror | Decisions D3, D7, D10; Task 8 |
| #569 IPLAN status as write-target (DECISIONS.md:853-867) | CLOSED | **Applicable precedent** — "framework had no contract to violate" is the same defect class; the fix here must be contract + enforcement, not prose alone | Decision D10; Task 5 |
| #393 CI canon drift (linked from #656 body as merge PR) | — | **Filing error, not applicable** — link appears copy-pasted; comment on #656 to clarify actual IPLAN-47 merge PR | Task 8 |

## Objective

Close the real gap behind #656 with the smallest canon change that makes post-completion repair plannable, manifested, and acceptance-defined: clarify `Completed` (validatable) vs `Verified` (terminal); define the lightweight C1 repair vehicle (scoped bugfix IPLAN parented on the closed plan, parent immutable); repair the broken `tmp/` promise; harden migration validation (rebuild + live-DB dry-run); and enforce the new contract in lint + conformance. Anything broader — new layer, registry change, template fork, mandatory new schema field — is explicitly out.

## Scope (In / Out)

**In:**

- Lifecycle prose: `Completed` vs `Verified` semantics in `08_IPLAN/README.md` + `DOC_GOVERNANCE_CORE.md` §IPLAN Lifecycle; definition of "active IPLAN" for the §3.13 exception.
- Repair vehicle: scoped bugfix IPLAN on the existing template (new `bugfix` subtype **or** extended `audit_fix` — Decision D7 picks one, not both) with `parent_iplan`/`source_chg` homes, scope-limited manifest, rollback, closure criteria.
- TMP promise repair: either a real `layers/08_IPLAN/tmp/` contract or removal of the `LAYER_REGISTRY.yaml:155` + `GATE-08:70` references. One or the other; no dangling third state.
- Validation hardening: migration VERIFY/smoke requires fresh-rebuild + live-DB `apply --dry-run` (fmt/lint alone insufficient).
- Lint: GOV-013 carve-out for the bugfix vehicle + new checks (naming, parent originality, scope, rollback, manifest accuracy); hook-vs-CI wiring decided in writing at kickoff.
- Conformance: new test(s) for the subtype + lifecycle invariants; goldens updated explicitly, never silently regenerated.
- Corpus cross-check per CLAUDE.md Development workflow (lint-rule change triggers it).

**Out of scope (deferred):**

- New SDD layer, `LAYER_REGISTRY.yaml` shape change, new layer number, separate bugfix template file (rejected per #657 Claim-6; registry diff stays empty).
- `revision_history` on the IPLAN template or mandatory `detection_gap` field (rejected; record homes already exist — D6).
- `Related-IPLAN` authorisation bypass of §3.13 (rejected; the vehicle satisfies §3.13 instead of bypassing it).
- Reopening/mutating `Verified` plans or backward status transitions (forbidden; parent stays immutable).
- The b-local-privy IPLAN-47 data fix itself (consumer-side, already repaired via its own PRs).
- Merge-policy reversal (no retroactive "must have been Verified" rule; forward rule only — D5).

## Approach / Design

### Decision D1 — verdict on #656 (what is real)

Real, threefold, narrow: (a) **lifecycle-completeness** — no proportionate ceremony for a code-only repair to closed output (full CHG cascade vs. edit-without-authorisation is the entire menu); (b) **broken reference** — `LAYER_REGISTRY.yaml:155` and `GATE-08:70` promise `IPLAN/tmp/` bugfix plans that do not exist on disk (7 files in `08_IPLAN/`, no `tmp/`, no template); (c) **validation-completeness** — `atlas fmt exit 0` vs `apply exit 1` plus stale-image masking shows migration VERIFY can go green on a broken artefact. Not a missing lifecycle: the validation-window pattern (VERIFY over `Completed`) and the heavyweight post-`Verified` pattern (CHG + new IPLAN) both exist.

### Decision D2 — terminal semantics (reject #656's "both terminal")

`Completed` = validatable (VERIFY window open, may still be merged — see D5). `Verified` = terminal/immutable, no backward transitions ever. #656's "declare Completed/Verified terminal" would break `README.md:148-161` (Completed → VERIFY → Verified). Both issues' loose "terminal (Completed)" usage is corrected to canon terminology in all touched docs.

### Decision D3 — vehicle: adopt #657, supersede #656's shape

The fix vehicle is #657's scoped bugfix IPLAN (fix vehicle, not record). #656's annotation-only shape is superseded by its own author's concession in #657 ("§3.14 … provided no fix vehicle"). The plan answers #657's 5 maintainer questions as acceptance criteria (Task 8); no mirror PR until direction is recorded.

### Decision D4 — define "active IPLAN" (close the §3.13 ambiguity)

`DOC_GOVERNANCE_CORE.md:253` ("Bug fixes on active IPLANs may skip CHG creation") never defines "active". Ruling: **active = Draft \| Approved \| In Progress**. The exception does **not** cover `Completed`/`Verified`. Post-completion repairs always carry a CHG (C1 allowed) + a bugfix IPLAN in `In Progress` satisfying §3.13 pre-write verification (exists, `In Progress`, `source_chg` cites the CHG, files listed in manifest, CHG `In-Progress`/`Implemented`).

### Decision D5 — merge-policy finding (no retroactive rule)

GATE-CODE exit is "audit trail updated + ready for merge" with no "must be Verified first" text, so merging at `Completed` was not textually forbidden — IPLAN-47's merge is partly a process-window event, not proof of a missing gate. Forward rule (minimal): a `Completed` plan merged before VERIFY keeps an **explicit open VERIFY obligation** (index `validated_by` pending); post-`Verified` defects use the bugfix vehicle. No retroactive "must have been Verified" enforcement.

### Decision D6 — record homes (reject new mandatory fields)

No `revision_history` on IPLAN, no mandatory `detection_gap`. Recording uses existing homes: fix-IPLAN (`validation_findings`, `cross_iplan_impact.original_iplan`, severity), authorising CHG (`revision_history` + RCA), index (`validated_by`, `findings_resolved`, `status_history`). A `detection` note per finding is **recommended prose** (what gate missed it), not a schema key — keeps the change additive and avoids a second mandatory-field rollout.

### Decision D7 — subtype mechanism (one of two, maintainer picks)

Either (A) new `bugfix` subtype or (B) extended `audit_fix` with `parent_iplan` + bugfix checklist. Recommendation: **(A)** — `audit_fix` guidance ("audit-driven, severity-ordered") would need contortion to cover field defects, while a `bugfix` subtype states parentage, scope-limits, and rollback natively. Whichever is picked: fields live in the existing template (no new template file), `combined` stays the default, normative step order fix → regression test → rollback → parent revision entry last, rollback required with PENDING→DONE/SKIPPED markers, no-fix-on-fix (failed attempt runs rollback; retry is a new sibling citing `prior_attempts`; thrashing escalates to reviewer judgment, no counters).

### Decision D8 — migration validation hardening

VERIFY/smoke for migration IPLANs MUST include fresh-image rebuild + live-DB `schema apply --dry-run`. `fmt`/lint/unit green is necessary but not sufficient. Template `execution_commands.validation` examples gain the dry-run form; deploy/combined smoke guidance names it.

### Decision D9 — attribution (no blame-chain prescription)

No prescribed blame fallback chain. Attribution = fix-IPLAN `parent_iplan` + `cross_iplan_impact` (multi-owner files) + existing per-session `code_inventory`/`files_touched` + index history. `git blame` is investigative technique, not canon.

### Decision D10 — contract + enforcement (the #569 lesson)

Prose alone repeats #569. Every new contract line ships with a check: GOV-013 carve-out text plus new lint checks (naming `IPLAN-{NEW}_bugfix_{FIXED}_{slug}`, minter max+1 from directory listing, parent-is-original-terminal, scope ⊆ repair files, rollback present + markers resolved, manifest accuracy per §3.5-equivalent), and conformance tests holding template–README–registry wording together. Linter home: IPLAN-side script; hook-vs-CI wiring decided in writing at implementation kickoff (recorded in the plan before code).

### Decision D11 — naming + minter

`IPLAN-{NEW_ID}_bugfix_{FIXED_ID}_{slug}.yaml`, `document_id` + `parent_iplan` + `@depends`; minter = max+1 from directory listing, never counters; DAG edges backward-only; parent link sections immutable. Directory-listing minter is an IPLAN-scope rule only; base-IPLAN counter behaviour untouched.

## File structure (Created / Modified)

| File | Action | Purpose |
|------|--------|---------|
| `framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml` | Modify | `bugfix` subtype (or extended `audit_fix`): `parent_iplan`, `source_chg` homes, bugfix checklist, step-order + rollback markers guidance |
| `framework/layers/08_IPLAN/README.md` | Modify | Completed vs Verified semantics; post-completion repair pattern; "active" definition pointer; TMP/VERIFY routing |
| `framework/layers/08_IPLAN/IPLAN-VERIFY-TEMPLATE.yaml` | Modify | Guidance: migration dry-run requirement; `validating_iplan`/`original_iplan` usage for post-merge VERIFY window |
| `framework/layers/08_IPLAN/IPLAN-00_index.TEMPLATE.yaml` | Modify (small) | `validated_by` pending state for merged-at-Completed plans; bugfix-parent linkage fields |
| `framework/governance/DOC_GOVERNANCE_CORE.md` | Modify | §3.13 "active" definition + bugfix-vehicle authorisation; §IPLAN Lifecycle post-completion pattern; migration VERIFY rule |
| `framework/governance/chg/CHG-TEMPLATE.yaml` (+ `framework/layers/09_CHG/CHG-TEMPLATE.yaml` if mirrored) | Check/modify | Confirm C1 `entry_gate: None` path suffices for bugfix CHGs; only touch if prose blocks it |
| `framework/layers/09_CHG/gates/GATE-08_IPLAN.md` (+ governance mirror) | Modify | Fix `tmp/` promise: point at the bugfix contract or remove; pre-gate checklist entry for repair vehicle |
| `framework/layers/09_CHG/gates/GATE-CODE_IMPLEMENTATION.md` | Modify (small) | Migration smoke note (rebuild + dry-run); feedback-defect routing to bugfix vehicle |
| `framework/governance/LINT_RULES.md` | Modify | GOV-013 carve-out + new check IDs (naming/parent/scope/rollback/manifest) |
| `sdd_doc_lint/` (new or extended check module) | Create/modify | Implement the new checks; single canonical copy only (the #648 lesson) |
| `tests/conformance/test_iplan_bugfix_lifecycle.py` (new) | Create | Subtype, lifecycle, naming, parent-originality, scope, rollback-marker invariants |
| `tests/conformance/` goldens/fixtures | Modify | Explicit golden updates for template/wording changes |
| `framework/registry/LAYER_REGISTRY.yaml` | Modify iff D11 needs it | Expected: **no change** (no new layer); only the `tmp/` sentence if the TMP promise is removed rather than built |
| `CHANGELOG.md`, `framework/CHANGELOG.md`, `plans/DECISIONS.md` | Modify | Entries + spec-governance decision record; version bump to `0.56.0` (confirm) |

## Implementation sequence

### Task 1 — Authorising record + maintainer direction (no code)

Record the CHG-equivalent authorisation for this framework change (plan is the authorising record pre-plan-PR per repo flow; implementation CHG/IPLAN minted after plan PR merge per §Governance Gate), post triage comment on #656 (real-but-narrow verdict, wrong-#393-link clarification request, verbatim §3.14 text request per verbatim-move rule), and post the 5-question direction request on #657. **Do not touch code until plan PR is merged** (CLAUDE.md Development workflow).

### Task 2 — Template + index changes (D7, D11)

Add `bugfix` subtype fields to `IPLAN-TEMPLATE.yaml` (`parent_iplan`, `source_chg` homes, checklist, order/rollback guidance); small VERIFY-template and index-template edits (pending-`validated_by`, parent linkage). Keep `combined` default; keep `_required_when_subtype` wiring consistent; no new template file.

### Task 3 — Governance prose (D2, D4, D5, D8, D9)

README lifecycle section, DOC_GOVERNANCE_CORE §§3.13/lifecycle, GATE-08 TMP fix, GATE-CODE migration smoke note. Every prose claim must match the template fields added in Task 2 (same-PR consistency; the #569 lesson).

### Task 4 — Linter (D10)

Implement new checks in the single canonical `sdd_doc_lint` copy; GOV-013 carve-out text; record hook-vs-CI wiring decision in writing before coding it. Run `python sdd_doc_lint/chg_lint.py` equivalents pre-commit / pre-implementation / pre-merge.

### Task 5 — Conformance (D10)

New `test_iplan_bugfix_lifecycle.py` + explicit golden updates. Full conformance suite green; no weakened assertions (the "conformance stays green" non-negotiable — fix spec or code, never the check).

### Task 6 — Corpus cross-check + verification pass

`python3 -m sdd_doc_lint examples/<NAME>/docs/` (mandatory for lint-rule changes); `sdd_doc_lint` self-tests; pre-push hook behaviour on fixture pair (clean + violating bugfix IPLAN). Zero *unexpected* findings.

### Task 7 — Changelog / decisions / version

`CHANGELOG.md` + `framework/CHANGELOG.md` entries, `framework/governance/DECISIONS.md` GD entry, `plans/DECISIONS.md` ISO-stamped record, version bump confirm (`0.56.0`).

### Task 8 — Issue coordination + mirror path

Comment pointers on #656 (verdict + what shipped) and #657 (direction outcome + mirror PR link when opened from a fresh clone). Never edit example artifacts directly; never push to `main` (feature branch → `dev` PR).

## Test-first step `[CODE]`

For each behavior changed, a failing test precedes implementation: new conformance test first asserts the bugfix-subtype contract (naming, parent-originality, scope, rollback markers, manifest accuracy) against the unmodified template and fails; then Task 2 makes it pass. Linter checks likewise gain a red fixture before the check implementation. One line per task at implementation time; no test-first stubs survive into the impl PR.

## Verification

| Check | Expected result |
|-------|-----------------|
| `python -m unittest discover -s tests/conformance` (or repo runner) | Green; goldens updated explicitly in the impl PR |
| `sdd_doc_lint` self-tests | Green |
| Corpus cross-check `python3 -m sdd_doc_lint examples/<NAME>/docs/` | Zero unexpected findings (TH01/TRACE-RES-001/etc. reviewed, not silently regenerated) |
| Fixture pair through linter (clean + 7-violation bugfix IPLAN) | Clean passes; violating fixture fails on exactly the expected check IDs |
| `python sdd_doc_lint/chg_lint.py` on the authorising CHG (when minted) | Exit 0 pre-commit / pre-implementation / pre-merge |
| Pre-push hook (if hook wiring chosen) | Fires on fixture push, blocks violating fixture |
| `gh issue view 656/657` read-back | Triage + direction comments published (non-zero body length verified) |

## Docs to update

- [ ] `CHANGELOG.md` + `framework/CHANGELOG.md` (MINOR entry, issue links, `Closes #656` only on the impl PR — one keyword per reference)
- [ ] `plans/DECISIONS.md` (ISO-stamped: vehicle choice A-vs-B, hook-vs-CI, version confirm)
- [ ] `framework/governance/DECISIONS.md` (GD entry: terminal semantics, "active" definition, merge-window rule)
- [ ] Any version-quoting doc touched by the version bump (`framework/VERSION`, pinned `framework_spec_version` frontmatter if changed)

## Risks

| Risk | Mitigation |
|------|------------|
| Maintainer picks (B) extended-`audit_fix` over (A) `bugfix` after template work starts | Task 1 gates Task 2; template diff kept minimal until direction recorded |
| New subtype breaks existing goldens / `_required_when_subtype` wiring | Task 5 runs full suite before prose; golden churn updated explicitly or subtype re-scoped |
| Hook-vs-CI dispute stalls landing | Decide in writing at Task 4 kickoff; either wiring acceptable if recorded + verified on fixtures |
| Scope creep into mandatory `detection_gap` / blame-chain / bypass | D6/D9 rejections are normative in this plan; review passes check them |
| Amendment-PR smell (shipping plan then patching) | Two-cycle rule enforced: plan PR opens only after a zero-gap pass; impl PR carries only the final shape |

## Claim ledger

| Claim | `file:line` actually read |
|-------|---------------------------|
| Lifecycle Draft→…→Completed→Verified; Verified immutable | `framework/layers/08_IPLAN/README.md:129-146`, `:163-173` |
| VERIFY covers Completed IPLANs; validation IPLAN closes Completed | `framework/layers/08_IPLAN/IPLAN-VERIFY-TEMPLATE.yaml:4-7,44-49`; `README.md:148-161` |
| VERIFY attribution homes exist (`validating_iplan`, `original_iplan`, `cross_iplan_impact`) | `IPLAN-VERIFY-TEMPLATE.yaml:58,160-173` |
| Index carries `validated_by`, `findings_resolved`, `status_history`, registry statuses | `IPLAN-00_index.TEMPLATE.yaml:36,50-52,159-162,180-184` |
| No `revision_history` on IPLAN; present on CHG/BRD/PRD/EARS/BDD/ADR/EVAL | grep `revision_history` → 14 hits, none in `IPLAN-TEMPLATE.yaml` |
| `tmp/` promise vs absence (7 files, no `tmp/`, no template) | `LAYER_REGISTRY.yaml:155`; `GATE-08_IPLAN.md:70`; `PLAN_STANDARD.md:24`; `ls framework/layers/08_IPLAN/` |
| §3.13 gate: `In Progress` + `source_chg` + manifest + CHG state; "active" exception undefined | `DOC_GOVERNANCE_CORE.md:235-253` |
| CHG lifecycle incl. C1 `entry_gate: None` for non-spec changes | `governance/chg/CHG-TEMPLATE.yaml:99-111` |
| GATE-CODE feedback path (RCA, regression scope, incident link, C1 = 1 peer reviewer) | `GATE-CODE_IMPLEMENTATION.md:54-79,102-116,142-164,186-204,247-255` |
| SDD-sync-on-completion + CHG-tracks-completion rules | `DOC_GOVERNANCE_CORE.md:270-276`; `LINT_RULES.md:136 (CHG-L012)`; `IPLAN-TEMPLATE.yaml:99-117` |
| #569 precedent (no contract to violate; manifest write-target) | `framework/governance/DECISIONS.md:853-867` |
| Current framework version | `framework/VERSION` = `0.55.0` |

## Review log

### Pass 1 (self, 2026-09-21) — gaps found and folded

1. Draft initially echoed #656's "Completed terminal" phrasing in D1 — corrected to D2 (Completed validatable, Verified terminal) with `README.md:129-146` citations.
2. Draft had no merge-policy answer (gap §2 of the self-review) — added D5 after reading GATE-CODE exit/routing (`:142-164`): no "Verified before merge" text; forward window rule instead of retroactive enforcement.
3. Draft cited the §3.13 exception without defining "active" — added D4 (active = Draft/Approved/In Progress) as a normative ruling to be ratified in review.
4. Draft proposed record fields without rejecting `detection_gap` crisply — added D6 rejections + existing-homes table (fix-IPLAN/CHG/index).
5. Draft listed LINT_RULES change without the mandatory corpus cross-check — added Task 6 + Verification row per CLAUDE.md Development workflow item 2.
6. Draft did not reconcile #656 vs #657 contradiction — added D3 supersession + Task 1/8 direction gating + #393-link filing-error triage.
7. Draft omitted hook-vs-CI decision discipline and single-canonical-linter constraint (#648 lesson) — added to D10/Task 4.
8. Re-validated all `file:line` citations against the tree; fixed two (index `validated_by` lines, VERIFY lifecycle comment lines).

### Pass 2 (re-review, 2026-09-21) — re-read of the patched plan

- Re-checked D2 against `README.md:148-161` + VERIFY template `:44-49`: Completed→VERIFY→Verified flow preserved; "both terminal" appears only in rejection contexts (triage row, D2 title, this bullet) — never as adopted terminology.
- Re-checked D4/D5 against `DOC_GOVERNANCE_CORE.md:235-276` + GATE-CODE: no new inconsistency; D5's "not textually forbidden" is hedged as a finding with the forward rule, not a retroactive claim.
- Re-checked D6/D9 rejections against Scope-Out list: `revision_history`-on-IPLAN, mandatory `detection_gap`, blame-chain, bypass appear in neither File structure nor Tasks (grep confirms only in D6/D9/Out-of-scope as rejected).
- Re-checked File structure ↔ Tasks ↔ Verification triangular consistency: every Modified/Created file is touched by exactly one task and covered by a verification row; `LAYER_REGISTRY.yaml` conditional edit matches "registry diff empty by default".
- Re-checked PLAN_STANDARD.md applicability (feature): metadata, objective, scope, approach, file structure, implementation sequence, test-first, verification, docs-to-update, risks, claim ledger, review log — all present; no empty headings or `N/A` stubs.
- **Result: zero new substantive gaps.** Plan is ready for plan-PR flow (open PR only after this pass; implementation begins only after plan PR merge).
