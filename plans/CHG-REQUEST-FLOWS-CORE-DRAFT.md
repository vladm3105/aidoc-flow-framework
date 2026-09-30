# CHG Request Flows — core document (DRAFT for review, 2026-09-22)

| Field | Value |
|---|---|
| Status | RATIFIED via PR #674 (CHG-06, 0.57.0, merged 2026-09-22) — this draft remains the review audit trail only |
| Proposed placement | `framework/governance/DOC_GOVERNANCE_CORE.md` new §3.1.3 (normative flow definitions + router); router summary mirrored in `framework/layers/09_CHG/README.md` + `framework/governance/chg/README.md`; `change_source: direct` row + C1 guidance note in `CHG-TEMPLATE.yaml` (both copies, pending P1-2 canon — see #667) |
| Type of change | Flow 3 (brownfield governance change): full SDD chain, C2/C3, SDD-first cascade |
| Version impact | MINOR (governance prose + template guidance + new lint checks; CHG-05 precedent). Sequencing vs the STALE P1 batch (also MINOR-bound): fold = one shared `0.57.0`; standalone = next MINOR. Decided at CHG authoring |
| Issues | Flow 2 machinery → new issue at CHG authoring (mint-`direct` + C1/IPLAN ruling + lint rule). Flows 1/3/4 are naming/routing only, no new issues |
| Depends on | STALE P1-2 (#667, CHG template canon) for the template half; the §3.1.3 prose half is independent |

> How to read: §§F1–F4 below are the proposed normative text (MUST language intentional — it lands in `DOC_GOVERNANCE_CORE.md`).
> §5 lists the mechanical template/lint deltas (applied at implementation, not in this draft).
> §6 records the open decisions with recommendations.

## Flow selector (normative router)

Every artifact change MUST be classified into exactly one flow — or into a governed non-flow path (Emergency,
Type-R) that yields to its own section — before a CHG is authored. Classify in this order — the first matching
row wins:

| # | Flow | Trigger | `change_source` | `change_level` | Entry gate | SDD cascade? | IPLAN shape | Verification |
|---|---|---|---|---|---|---|---|---|
| F1 | Greenfield development | New product / new layer chain, no prior implementation | `upstream` | C3 | GATE-01 | Yes — full 10-layer authoring per §3.1.1 | Full (all code steps, full manifest) | EVAL cycles |
| F2 | Direct request | Human or AI-agent request, unrelated to any prior IPLAN, no product-behavior change (docs, scripts, hooks, small tooling) | `direct` (new — see F2) | C1 (docs-only: no CHG/IPLAN; code-touching: C1 CHG + scoped IPLAN) | GATE-CODE | No (`sdd_lifecycle: []`) | Scoped (manifest + steps only, §F2.3) | Verification commands in the scoped IPLAN |
| F3 | Brownfield behavior change | Product design or behavior change to an implemented product | `upstream` / `midstream` / `design` (by lowest affected layer) | C2 / C3 (C3 if cross-layer or new requirements) | GATE-01 / 03 / 06 (by source) | Yes — SDD-first restart per §3.1.1 (affected layers and everything below) | Full, referencing NEW SDD versions | EVAL cycles |
| F4 | Bugfix on implemented IPLAN | Defect found in EVAL, manual test, or field use, traceable to a `Completed`/`Verified` parent IPLAN | `feedback` | C1 CHG (CHG-05 vehicle) | GATE-CODE | No (parent SDD stands; fix-IPLAN carries `validation_findings`) | Bugfix-subtype (`parent_iplan` + `source_chg`, repair-scoped manifest, rollback) | Regression suite + parent revision entry |
| — | Emergency (non-flow path) | Critical production issue requiring fix before authorization | `Emergency` level | Emergency | Post-hoc | Document within 48h + post-mortem | Fix IPLAN post-hoc as directed by the Emergency section | Post-mortem verification |
| — | Type-R reconciliation (non-flow path) | Verified working codebase preceding its specs (non-emergency empirical work) | `reconciliation` | C2 typical (classify by cascade breadth) | GATE-CODE | Reverse — Code→TDD→SPEC→BDD→EARS per §3.1.2 | Reverse-authored (ground truth from code) | §3.1.2 Phase-3 battery |

### F1 — Greenfield development

The initial 10-layer SDD flow (BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → CHG → EVAL → Code/Docs/Scripts).
`change_source: upstream`, `change_level: C3` (cross-layer by construction; `gate_approval.approver` required before status leaves `Proposed` per GOV-012),
entry GATE-01. SDD-first order (§3.1.1) applies end to end: no IPLAN before the SDD versions it references exist;
no code before an `In Progress` IPLAN exists (§3.13). This flow is fully governed today; it is named here so the
router is total — authors MUST NOT file greenfield work as F2 or F4 to dodge the cascade.

### F2 — Direct request (new machinery)

A change request from a human or another AI agent that is NOT related to a previous IPLAN implementation and does
NOT change product behavior: documentation edits, hook/script/tooling tweaks (`hooks/`, `framework/scripts/`,
`sdd_doc_lint/` tooling), template typo fixes, non-normative prose. No full SDD chain is required because there is
no SDD contract at stake — but the IPLAN Gate (§3.13) still applies to everything it does not exempt.

**F2.1 — `change_source: direct` (new value).** Definition: origin is a direct requester instruction, not a layer
artifact, not production feedback, not an empirical codebase. Entry gate: GATE-CODE — its entry criteria apply
conditionally ("If cascade: upstream gates passed"; "IPLAN updated (if file manifest changes)"), so a
cascade-free change enters cleanly, and its RCA + regression-scope rows fit small changes. GATE-08 MUST NOT be
used: it requires upstream gates passed and TDD test cases defined unconditionally (`GATE-08_IPLAN.md:49-78`),
which a cascade-free change cannot satisfy. `External` MUST NOT be used for direct requests: `External (business)` routes to GATE-01 and
`External (technical)` to GATE-03 with multi-layer cascades (regulatory, CVE, dependency, 3rd-party API) —
routing a script tweak through either would mandate a phantom cascade. If the requester cites a regulation, CVE,
or vendor-API change, the flow is NOT F2 (reclassify: External → F3-shaped cascade).

**F2.2 — C1 ruling (resolves the C1/§3.13 contradiction).** The template's C1 row ("None — direct commit") is
reaffirmed AND bounded:

- Docs-only, non-normative C1 (typo, formatting, clarification touching no code/scripts and no normative
  template/governance text): direct commit, no CHG, no IPLAN. Unchanged.
- Code- or script-touching C1 (any `*.sh`, `*.py`, hook, workflow, or normative-template edit): a C1 CHG +
  a scoped IPLAN are REQUIRED. §3.13 admits exactly the AGENTS.md exceptions plus this sentence: the IPLAN Gate
  is satisfied by a scoped IPLAN (`In Progress`, `source_chg` naming the C1 CHG, manifest covering every touched
  file). "Small diff" is not an exemption; the IPLAN is what makes small diffs auditable.
- Normative-text C1 (a one-line governance/template fix that changes a contract): C1 CHG + scoped IPLAN; the
  prose change itself ships in the same diff. (This is how §7-type one-line fixes avoid full F3 ceremony
  without evading review.)

**F2.3 — Minimal shapes.** The C1 CHG carries: change control (`direct`, C1), `sdd_lifecycle: []` (EMPTY —
any entry reclassifies the change to F1/F3) PAIRED WITH SDD-free `artifacts_modified` (GOV-014 binds the two:
no SDD document may appear in `artifacts_modified` unless the lifecycle lists it — for F2 both are empty of
SDD), implementation steps limited to IPLAN creation, and the requester citation (who asked, verbatim ask or
link — carried in the change description; no new template field). The scoped IPLAN carries: manifest,
steps/commands, and tests or verification commands; SDD-trace sections stay empty by construction. Anything
larger than this shape is NOT F2.

**F2.4 — Misclassification guard (lint).** A CHG with a code/script manifest AND (`sdd_lifecycle: []` without
`source: direct`, OR no IPLAN reference, OR no `parent_iplan` where F4 applies) fails lint — candidate
GOV-018, see §5. The failure message MUST name the suspected correct flow (F2/F3/F4) so the author reclassifies
instead of force-passing.

### F3 — Brownfield behavior change

A product design or behavior change to an implemented product restarts the full SDD chain at the lowest affected
layer: source `upstream` (BRD/PRD-level) / `midstream` (EARS/BDD/ADR) / `design` (SPEC/TDD), level C2 (single-layer
refinement, peer review) or C3 (cross-layer or new requirements, formal gate + approver), entry GATE-01/03/06 by
source. The §3.1.1 cascade is MANDATORY and ordered: Phase 0 archive → rewrite → bump (upper layers first),
Phase 1 IPLAN referencing the NEW versions, Phase 2 code. `change_source: spec` (framework self-changes:
templates/governance/registry/VERSION, GATE-SPEC, level ≥ C2 per GATE-SPEC-E003) is the special case of F3 where
the "product" is the framework itself — this very document ships as F3/spec. F3 MUST NOT be filed as F2 (no SDD
cascade) even when the diff looks small: behavior change without SDD update is the exact defect §3.1.1 exists to
prevent. F3 MUST NOT be filed as F4: F4 repairs output to match standing SDD; F3 changes what the SDD promises.

### F4 — Bugfix on implemented IPLAN

A defect found during EVAL, manual test, or field use, traceable to a `Completed`/`Verified` parent IPLAN, is
repaired exclusively through the CHG-05 vehicle (0.56.0, canon — `LINT_RULES.md:131` GOV-013 carve-out): the parent
stays immutable (no reopening, no backward transitions); a C1 CHG authorizes; a scoped bugfix-subtype IPLAN
(`parent_iplan` + `source_chg`, `In Progress`, repair-scoped manifest, rollback with PENDING→DONE/SKIPPED markers)
satisfies §3.13 as the governed path, not an exemption. Source is `feedback` (production/user-originated defect);
`execution` (IPLAN-level correction pre-completion) stays on the parent IPLAN itself and never becomes F4.
No-fix-on-fix: a failed attempt runs rollback; retry is a new sibling citing `prior_attempts`. F4 MUST NOT be used
for behavior change (that's F3) or for defects in `Draft`/`Approved`/`In Progress` plans (fix on the active IPLAN
itself — the AGENTS.md exception — no CHG required).

## Router procedure (replaces ad-hoc classification)

1. Critical production issue requiring fix before authorization? → **Emergency path** (fix → deploy → document
   - post-mortem within 48h). The router yields. F2 is never the speed lane for production incidents.
2. Verified working codebase preceding its specs (non-emergency empirical work)? → **Type-R**: §3.1.2 governs
   (reverse-authored IPLAN, GATE-CODE, Phase-3 battery). The router yields; F1 MUST NOT claim it.
3. Is there a defect traceable to a `Completed`/`Verified` IPLAN? → **F4**.
4. Does the change alter product behavior, requirements, specs, or test contracts? → **F3** (at the lowest affected layer; framework self-change → F3/spec).
5. Is there any prior IPLAN this change relates to, or any SDD contract at stake? If neither: code/script-touching → **F2 with C1 CHG + scoped IPLAN**; docs-only non-normative → **C1 direct commit** (no flow, no CHG).
6. Otherwise → **F1** (new chain) — the default for anything that reaches IPLAN without a parent.

Steps 0–5 are ordered as a decision list: Emergency first (safety), Type-R second (chronology), F4 third (narrowest
flow), behavior fourth, direct fifth, greenfield default. When two rows seem to match, the EARLIER row wins;
record the rejected candidate and one-line rationale in the CHG so reclassification is auditable.

## Mechanical deltas (applied at implementation, NOT in this draft)

1. `CHG-TEMPLATE.yaml` (both copies — after #667 canon): add `direct` row to the `change_source` guidance table
   (Definition: direct requester instruction; Entry GATE-CODE; Affected: IPLAN→Code, no SDD) AND the `direct`
   value to the `value: null # …` enum comment (`:110`); extend the C1 row with
   the F2.2 bound (docs-only direct commit vs code-touching C1 CHG + scoped IPLAN); extend `entry_gate` comment
   (`None (C1 docs-only)`).
2. `DOC_GOVERNANCE_CORE.md`: insert §§F1–F4 + non-flow paths + router as §3.1.3; §3.13 appends the F2.2 IPLAN-Gate sentence.
3. Lint: candidate `GOV-018` (F2.4 misclassification guard — GOV-017 is taken: EARS/BDD ID existence, D21–D22) + `chg_lint` check (code manifest ∧ empty lifecycle ∧
   source ≠ `direct` ∧ no `parent_iplan` → error naming the suspected flow); fixtures: one C1-direct golden
   (empty lifecycle + scoped IPLAN ref, green) and one misclassified golden (code manifest, no source, red).
4. Conformance: router-agreement test (F1–F4 × source × gate × cascade-flag matrix, mirroring the
   `test_iplan_bugfix_lifecycle.py:103-116` codes-vs-catalog pattern); `09_CHG/README.md` + `chg/README.md` gain
   the selector table.
5. Pre-flight at CHG authoring: confirm no `change_source` enum is locked in `saga.schema.json` or linter
   allowlists that would reject `direct` (STALE P1-6 triple-lock, #671 — fix in the same pass if locked).

## Open decisions (recommendations stand unless overturned in review)

- (a) Emergency handling: router step 0 yields to the Emergency path (fix → deploy → document + post-mortem 48h) —
  Emergency keeps its post-hoc procedure unchanged; the change here is routing only (previously the router could
  misroute incidents to F3). F2 is never a speed lane for production incidents (Type-R §3.1.2
  Emergency-exclusion applies).
- (b) `direct` vs broadening `External`: `direct` recommended — `External`'s GATE-01/03 cascades are load-bearing;
  broadening it would route script tweaks through phantom multi-layer cascades.
- (c) Who may select F2: any author recommended, with the F2.4 lint guard as the backstop (misclassification fails
  closed with the suspected flow named) rather than a human approval gate.

## Review pass 1 — gap analysis (2026-09-22, every claim re-checked live)

Method: `ls`/`grep`/`sed` against the 0.56.0 tree (`GATE-08_IPLAN.md:49-78`, `GATE-CODE_IMPLEMENTATION.md` §2/§6.2,
`LINT_RULES.md:128-135`, `chg_lint.py:28,167-199,477`). Per `AGENTS.md` these are review findings on an unlanded
draft (recorded here, not filed as issues); issues get filed at CHG authoring per the header.

### Blocking (fix before the plan PR)

- **G1 — Router has no Emergency branch.** Steps 1–4 never yield Emergency: a critical production incident matches
  step 2 ("alters product behavior") and misroutes to F3, forbidding the post-hoc Emergency path the draft claims
  is "untouched" (§6a). Fix: step 0 triage — critical production issue → Emergency (fix → deploy → document +
  post-mortem 48h), router yields. Also closes the abuse path where a prod incident files as F2 (code manifest +
  `direct` source would lint green).
- **G2 — Router has no Type-R / reconciliation branch.** `change_source: reconciliation` (§3.1.2) matches no row:
  step 2 misreads doc-sync as behavior change, step 3's "no SDD contract at stake" is false for it, and the F1
  default demands the SDD-first order Type-R exists precisely because it cannot honestly follow. Fix: explicit
  row — verified codebase → reverse-authored IPLAN → upstream reconciliation per §3.1.2, entry GATE-CODE; the
  router names it and yields (no new rules, §3.1.2 already governs). Five flows routed, four flows built.
- **G3 — F2 → GATE-08 contradicts GATE-08's own entry criteria.** `GATE-08_IPLAN.md:49-78` requires upstream
  gates passed (GATE-01/03/06) and TDD test cases defined — UNCONDITIONAL. An F2 change (empty lifecycle, no SDD)
  cannot enter. Fix: route F2 → **GATE-CODE**, whose entry criteria are conditional ("If cascade: upstream gates
  passed"; "IPLAN updated (if file manifest changes)"; RCA + regression-scope rows fit small changes) and which
  already hosts the non-SDD-first shapes (feedback bubble-up §6.2, Type-R carve-out, hotfix/bugfix checklist rows).
  Corrects the selector table, F2.1, and §5.1 (guidance-table Entry column).
- **G4 — GOV-017 collision.** `LINT_RULES.md:135` already defines GOV-017 (EARS/BDD element-ID existence, D21–D22;
  wired in `test_chg_lint.py:12` and cited at `chg_lint.py:28,477`). The draft's "candidate GOV-017" must become
  **candidate GOV-018**. Fix all three references (§F2.4, §5.3, header-adjacent text).

### Non-blocking (fix in the same pass)

- **G5 — Empty-lifecycle interplay underspecified.** F2.3 mandates `sdd_lifecycle: []` but doesn't bind
  `artifacts_modified`: GOV-014 only bites when lifecycle omits a doc listed in `artifacts_modified`, so state
  both halves (empty lifecycle AND SDD-free `artifacts_modified`). Compatible with current L004 (warn-only,
  `chg_lint.py:167-199`) and aligned with the STALE T2 direction (IPLAN ref via `implementation.steps[]`
  `phase: iplan_creation`).
- **G6 — Requester-citation home unspecified.** F2.3 requires a citation but names no field. Ruling: the CHG
  change description carries it (verbatim ask or link) — no new template field, no schema churn.
- **G7 — Enum comment missed.** §5.1 adds the `direct` guidance-table row but not the `value: null # upstream |
  …` enum comment (`CHG-TEMPLATE.yaml:110`). Both must change together (triple-lock discipline, #671).
- **G8 — No verification column.** Add EVAL/verification expectations to the selector: F1/F3 → EVAL cycles;
  F2 → verification commands in the scoped IPLAN; F4 → regression suite + parent revision entry (CHG-05 vehicle).
- **G9 — Version sequencing.** STALE pass 2 settled the P1 batch as MINOR `0.56.0 → 0.57.0` — the same number this
  draft claims. Fold = one shared `0.57.0`; standalone = next MINOR. Decide at CHG authoring, not here.
- **G10 — Router step 3 editorial.** "F4/F1 impossible" reads as a proof; rewrite as plain routing ("no prior
  IPLAN and no SDD contract → F2 if code/script-touching, C1 direct-commit if docs-only non-normative").

### Checked, not gaps

- Grandfathering: no instance CHG directory exists in-tree (verified: no `docs/sdd/`), so no in-flight CHG needs
  a migration rule.
- F4 `feedback` vs `execution`: consistent with the D4 active-IPLAN definition and `GATE-CODE §6.2` bubble-up
  (upstream fix as dependent CHG); `execution` pre-completion work stays on the parent IPLAN.
- F2 C1-approver question: GOV-012 binds C3 only — C1 CHGs need no approver under any status. No ruling needed.
