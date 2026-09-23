# CHG Request Flows

## Document Control

| Field | Value |
|-------|-------|
| Version | 1.0 |
| Status | Approved |
| Last Updated | 2026-09-22 |
| Author | Framework Maintainer |
| Framework Version | 0.59.2 |

| Field | Value |
|---|---|
| Status | **RATIFIED** (0.57.0, CHG-06) — REVIEWED 2/2; F3/spec vehicle landed the §7 deltas. Normative from this version |
| Version applicability | MINOR `0.56.0 → 0.57.0` (standalone; STALE P1 batch takes the next MINOR if shipped separately) |
| Provenance | Converted 2026-09-22 from `plans/CHG-REQUEST-FLOWS-CORE-DRAFT.md` (pass-1 gaps G1–G10 applied); ratified via CHG-06 + IPLAN-06 (`framework/archive/CHG-06/`); review history in Appendix A |
| Normative dependencies (LANDED in 0.57.0) | `change_source: direct` (template enum + guidance); F2.2 §3.13 sentence; GOV-018 + `chg_lint` CHG-L013 + fixtures; conformance router-agreement test |

> **Ratified 0.57.0 (CHG-06).** All §7 deltas landed: `direct` is a valid template value, the F2.2
> ruling governs §3.13, and CHG-L013/GOV-018 enforces the router.

## 1. Flow selector (normative router)

Every artifact change MUST be classified into exactly one flow — or into a governed non-flow path (Emergency,
Type-R) that yields to its own section — before a CHG is authored. Classify in this order — the first matching
row wins:

| # | Flow | Trigger | `change_source` | `change_level` | Entry gate | SDD cascade? | IPLAN shape | Verification |
|---|---|---|---|---|---|---|---|---|
| F1 | Greenfield development | New product / new layer chain, no prior implementation | `upstream` | C3 | GATE-01 | Yes — full 10-layer authoring per §3.1.1 | Full (all code steps, full manifest) | EVAL cycles |
| F2 | Direct request | Human or AI-agent request, unrelated to any prior IPLAN, no product-behavior change (docs, scripts, hooks, small tooling) | `direct` (new — see §3) | C1 (docs-only: no CHG/IPLAN; code-touching: C1 CHG + scoped IPLAN) | GATE-CODE | No (`sdd_lifecycle: []`) | Scoped (manifest + steps only, §3.3) | Covering tests + verification commands in the scoped IPLAN |
| F3 | Brownfield behavior change | Product design or behavior change to an implemented product | `upstream` / `midstream` / `design` (by lowest affected layer) | C2 / C3 (C3 if cross-layer or new requirements) | GATE-01 / 03 / 06 (by source) | Yes — SDD-first restart per §3.1.1 (affected layers and everything below) | Full, referencing NEW SDD versions | EVAL cycles |
| F4 | Bugfix on implemented IPLAN | Defect found in EVAL, manual test, or field use, traceable to a `Completed`/`Verified` parent IPLAN | `feedback` | C1 CHG (CHG-05 vehicle) | GATE-CODE | No (parent SDD stands; fix-IPLAN carries `validation_findings`) | Bugfix-subtype (`parent_iplan` + `source_chg`, repair-scoped manifest, rollback) | Regression suite + parent revision entry |
| — | Emergency (non-flow path) | Critical production issue requiring fix before authorization | `Emergency` level | Emergency | Post-hoc | Document within 48h + post-mortem | Fix IPLAN post-hoc per `09_CHG/README.md:318` + `templates/POST_MORTEM-TEMPLATE.md` (post-mortem ≤48h) | Post-mortem verification |
| — | Type-R reconciliation (non-flow path) | Verified working codebase preceding its specs (non-emergency empirical work) | `reconciliation` | C2 typical (classify by cascade breadth) | GATE-CODE | Reverse — Code→TDD→SPEC→BDD→EARS per §3.1.2 | Reverse-authored (ground truth from code) | §3.1.2 Phase-3 battery |

## 2. F1 — Greenfield development

The initial 10-layer SDD flow (BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → CHG → EVAL → Code/Docs/Scripts).
`change_source: upstream`, `change_level: C3` (cross-layer by construction; `gate_approval.approver` required before status leaves `Proposed` per GOV-012),
entry GATE-01. SDD-first order (§3.1.1) applies end to end: no IPLAN before the SDD versions it references exist;
no code before an `In Progress` IPLAN exists (§3.13). This flow is fully governed today; it is named here so the
router is total — authors MUST NOT file greenfield work as F2 or F4 to dodge the cascade.

## 3. F2 — Direct request

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
steps/commands, covering test cases (REQUIRED for code-touching changes — GATE-CODE entry demands test cases
exist for changed code; verification commands alone do not satisfy entry), and verification commands;
SDD-trace sections stay empty by construction. Anything
larger than this shape is NOT F2.

**F2.4 — Misclassification guard (lint).** A CHG with a code/script manifest AND (`sdd_lifecycle: []` without
`source: direct`, OR no IPLAN reference, OR no `parent_iplan` where F4 applies) fails lint — candidate
GOV-018, see §7. The failure message MUST name the suspected correct flow (F2/F3/F4) so the author reclassifies
instead of force-passing. Known limit (pass 2): the guard is SYNTACTIC — a behavior change filed with a
well-formed F2 shape (source `direct` + scoped IPLAN + code manifest) lints green. Semantic misclassification
relies on human review of the requester citation (§F2.3) and the rejected-candidate record (§6, router rule).

## 4. F3 — Brownfield behavior change

A product design or behavior change to an implemented product restarts the full SDD chain at the lowest affected
layer: source `upstream` (BRD/PRD-level) / `midstream` (EARS/BDD/ADR) / `design` (SPEC/TDD), level C2 (single-layer
refinement, peer review) or C3 (cross-layer or new requirements, formal gate + approver), entry GATE-01/03/06 by
source. The §3.1.1 cascade is MANDATORY and ordered: Phase 0 archive → rewrite → bump (upper layers first),
Phase 1 IPLAN referencing the NEW versions, Phase 2 code. `change_source: spec` (framework self-changes:
templates/governance/registry/VERSION, GATE-SPEC, level ≥ C2 per GATE-SPEC-E003) is the special case of F3 where
the "product" is the framework itself. F3 MUST NOT be filed as F2 (no SDD
cascade) even when the diff looks small: behavior change without SDD update is the exact defect §3.1.1 exists to
prevent. F3 MUST NOT be filed as F4: F4 repairs output to match standing SDD; F3 changes what the SDD promises.

## 5. F4 — Bugfix on implemented IPLAN

A defect found during EVAL, manual test, or field use, traceable to a `Completed`/`Verified` parent IPLAN, is
repaired exclusively through the CHG-05 vehicle (0.56.0, canon — `LINT_RULES.md:131` GOV-013 carve-out): the parent
stays immutable (no reopening, no backward transitions); a C1 CHG authorizes; a scoped bugfix-subtype IPLAN
(`parent_iplan` + `source_chg`, `In Progress`, repair-scoped manifest, rollback with PENDING→DONE/SKIPPED markers)
satisfies §3.13 as the governed path, not an exemption. Source is `feedback` (production/user-originated defect);
`execution` (IPLAN-level correction pre-completion) stays on the parent IPLAN itself and never becomes F4.
No-fix-on-fix: a failed attempt runs rollback; retry is a new sibling citing `prior_attempts`. F4 MUST NOT be used
for behavior change (that's F3) or for defects in `Draft`/`Approved`/`In Progress` plans (fix on the active IPLAN
itself — the AGENTS.md exception — no CHG required).

## 6. Router procedure (replaces ad-hoc classification)

1. Critical production issue requiring fix before authorization? → **Emergency path** (fix → deploy → document
   + post-mortem within 48h). The router yields. F2 is never the speed lane for production incidents.
2. Verified working codebase preceding its specs (non-emergency empirical work)? → **Type-R**: §3.1.2 governs
   (reverse-authored IPLAN, GATE-CODE, Phase-3 battery). The router yields; F1 MUST NOT claim it.
3. Is there a defect traceable to a `Completed`/`Verified` IPLAN? → **F4**.
4. Does the change alter product behavior, requirements, specs, or test contracts? → **F3** (at the lowest affected layer; framework self-change → F3/spec).
5. Is there any prior IPLAN this change relates to, or any SDD contract at stake? If neither: code/script-touching → **F2 with C1 CHG + scoped IPLAN**; docs-only non-normative → **C1 direct commit** (no flow, no CHG).
6. Otherwise → **F1** (new chain) — the default for anything that reaches IPLAN without a parent.

Steps 1–6 are ordered as a decision list: Emergency first (safety), Type-R second (chronology), F4 third (narrowest
flow), behavior fourth, direct fifth, greenfield default. When two rows seem to match, the EARLIER row wins;
record the rejected candidate and one-line rationale in the CHG so reclassification is auditable.

## 7. Ratification deltas (REQUIRED before this document takes effect)

1. `CHG-TEMPLATE.yaml` (both copies — after #667 canon): add `direct` row to the `change_source` guidance table
   (Definition: direct requester instruction; Entry GATE-CODE; Affected: IPLAN→Code, no SDD) AND the `direct`
   value to the `value: null # …` enum comment (`:110`); extend the C1 row with
   the F2.2 bound (docs-only direct commit vs code-touching C1 CHG + scoped IPLAN); extend `entry_gate` comment
   (`None (C1 docs-only)`).
2. `DOC_GOVERNANCE_CORE.md`: fold §§1–6 in as §3.1.3 (this file then becomes the overflow record or is retired
   with a pointer); §3.13 appends the F2.2 IPLAN-Gate sentence.
3. Lint: candidate `GOV-018` (F2.4 misclassification guard — GOV-017 is taken: EARS/BDD ID existence, D21–D22) + `chg_lint` check (code manifest ∧ empty lifecycle ∧
   source ≠ `direct` ∧ no `parent_iplan` → error naming the suspected flow); fixtures: one C1-direct golden
   (empty lifecycle + scoped IPLAN ref, green) and one misclassified golden (code manifest, no source, red).
4. Conformance: router-agreement test (F1–F4 × source × gate × cascade-flag matrix, mirroring the
   `test_iplan_bugfix_lifecycle.py:103-116` codes-vs-catalog pattern); `09_CHG/README.md` + `chg/README.md` gain
   the selector table.
5. Pre-flight at CHG authoring: confirm no `change_source` enum is locked in `saga.schema.json` or linter
   allowlists that would reject `direct` (STALE P1-6 triple-lock, #671 — fix in the same pass if locked).
6. Ratification vehicle: F3/spec authoring CHG + IPLAN per the Governance Gate; Flow 2 machinery filed as its
   own issue at CHG authoring (mint-`direct` + C1/IPLAN ruling + lint rule).

## 8. Open decisions (pass 2 verdicts — all CONFIRMED 2026-09-22)

- (a) Emergency handling: CONFIRMED — router step 1 yields to the Emergency path (fix → deploy → document +
  post-mortem 48h); Emergency keeps its post-hoc procedure unchanged (`09_CHG/README.md:22,102,318`,
  `templates/POST_MORTEM-TEMPLATE.md` in both CHG homes); the change here is routing only. F2 is never a speed
  lane for production incidents (Type-R §3.1.2 Emergency-exclusion applies).
- (b) `direct` vs broadening `External`: `direct` CONFIRMED — `External`'s GATE-01/03 cascades are load-bearing
  (`CHG-TEMPLATE.yaml:70-111` re-read at pass 2: business→GATE-01, technical→GATE-03); broadening it would route
  script tweaks through phantom multi-layer cascades.
- (c) Who may select F2: any author CONFIRMED, with two backstops acknowledged: the syntactic F2.4 lint guard
  (fails closed, names the suspected flow) for malformed filings, and human review of the citation +
  rejected-candidate record for well-formed-but-wrong filings (documented limit in F2.4). No human approval gate.

## Appendix A — Review history (condensed from the draft)

- Pass 0 (2026-09-22): initial draft — 4 flows (F1 greenfield, F2 direct, F3 brownfield, F4 bugfix).
- Pass 1 (2026-09-22): 10 gaps, all applied — G1 Emergency branch added (was misroutable to F3); G2 Type-R
  branch added (was falling into the F1 default); G3 F2 entry GATE-08 → GATE-CODE (`GATE-08_IPLAN.md:49-78`
  requires upstream gates + TDD unconditionally); G4 misclassification guard GOV-017 → GOV-018 (`LINT_RULES.md:135`
  collision); G5 lifecycle/artifacts binding; G6 citation home (change description); G7 enum comment; G8
  verification column; G9 version sequencing; G10 router rewrite. Method: `ls`/`grep`/`sed` against the 0.56.0 tree.
- Pass 2 (pending): final confirmation — §8 decisions, GATE-CODE routing for F2, version slot. Full log:
  `plans/CHG-REQUEST-FLOWS-CORE-DRAFT.md`.
- Pass 2 (2026-09-22, on this file): §8 all CONFIRMED with live re-verification (`09_CHG/README.md:22,102,318`,
  `templates/POST_MORTEM-TEMPLATE.md` both homes, `CHG-TEMPLATE.yaml:70-111`, GATE-CODE §2 entry). Amendments:
  F2.3 covering-tests REQUIRED for code-touching F2 (GATE-CODE entry demands test cases exist — commands alone
  insufficient); F2.4 documented syntactic-guard limit (semantic misclassification → human review of citation +
  rejected-candidate record); Emergency row cites `:318` + post-mortem template; §8 rewritten as verdicts.
  Memory cross-check: no conflicting prior decision found. Next: F3/spec vehicle (authoring CHG + IPLAN, Flow 2
  machinery issue) → §7 deltas → ratification flip of the header banner.
