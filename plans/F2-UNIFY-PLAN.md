# F2 Unify Plan — always-traced direct requests + docs-compliance rule

## Objective

Close issue #772: unify F2 so agent-authored changes always carry a CHG +
scoped IPLAN (no silent docs-only direct commits by agents), and add the
framework self-change docs-compliance rule. Chain:
issue → CHG → IPLAN → code/documentation/governance/AGENTS.md.

## Status

- Issue: #772 OPEN; issue #773 OPEN (owner-directed mandatory-trackability rule, triaged 2026-09-28).
- This plan: ready (pass 3) + D2 AMENDED (see below) — merged vehicle with #773 per triage ordering.

## Scope

In scope (framework self-change, `change_source: spec`, GATE-SPEC):

1. `framework/governance/CHG_REQUEST_FLOWS.md` §3 (F2.2) — agent-authored
   docs-only C1 requires C1 CHG + scoped IPLAN; direct commit retained only
   as an explicit human-only exception (or removed — decision D2).
2. `framework/governance/chg/CHG-TEMPLATE.yaml` C1 row + layer mirror
   `framework/layers/09_CHG/CHG-TEMPLATE.yaml` (byte-identical pair).
3. Both `09_CHG/README.md` mirrors (`framework/layers/09_CHG/README.md` +
   `framework/governance/chg/README.md`, byte-identical per #770) — C1 row,
   Direct routing row, flows pointer.
4. `framework/governance/DOC_GOVERNANCE_CORE.md` §3.1.3 F2 row + §3.13 F2.2
   paragraph — same unification wording.
5. `framework/governance/LINT_RULES.md` GOV-018 scope note. The guard stays
   syntactic and fires only on code/script manifests, so docs-only agent
   filings cannot trip it — selecting the enforcement vehicle for untraced
   agent docs-only edits (extend GOV-018/CHG-L013 vs recorded reviewer-lens
   with rationale) is a mandatory CHG deliverable; the rule does not land
   unenforced.
6. `AGENTS.md` Governance Gate exceptions + IPLAN Gate paragraph — agents
   always traced; docs-compliance review step required on self-changes.
7. New docs-compliance rule: every framework self-change CHG includes a
   verification step that governance docs comply with the new behavior.
   Normative-home candidate: `DOC_GOVERNANCE_CORE.md` self-change block +
   `09_CHG/README.md` Framework Self-Changes section; final at CHG.
8. `framework/governance/CHG_REQUEST_FLOWS.md` §6 router step 5 + §8(c)
   (any-author F2 selection) — amended for the agent/human split.
9. `framework/VERSION` bump + `semver_impact` declaration (E005);
   `SECURITY_REVIEW.md` checklist (W003 — agent-facing guidance change).
10. Both CHANGELOGs + `sync-version-refs` pin sweep; router-agreement
    (`test_chg_flows_router.py`) + mirror-twin suites updated for the
    unified F2 row.

Out of scope: F1/F3/F4 routing, Emergency/Type-R paths, linter engine
changes beyond the GOV-018 note, platform code.

## Approach

F3/spec vehicle per the Governance Gate: plan (2 review passes) → CHG
(C2 minimum per GATE-SPEC-E003; C3 iff the breaking-change analysis finds
consumer-breaking impact — E002 is one-directional major⇒C3, E004 puts
human approval on C3) → CHG `sdd_lifecycle`-phase archive→rewrite steps for
every touched framework doc (`archive/{CHG-ID}/` + `supersedes`, satisfying
CHG-L005 for `spec` source) → IPLAN (`In Progress`, `source_chg` naming
the CHG) → edits → verification → PR `feature/772-f2-unify` → `dev`.
Implementation runs in a per-task worktree + branch; the main checkout
stays on `dev`. This plan file is the design record, not the execution
manifest.

Minimal traced shape for future agent docs-only C1 filings (the rule being
introduced — not this vehicle's classification, which stays F3/spec ≥ C2):
CHG (`direct`, C1, `sdd_lifecycle: []`, requester citation) + scoped IPLAN
(manifest, steps/commands, verification; covering tests N/A-allowed for
pure prose).

## Decisions

- D1: Default for agents becomes always-traced. No agent exception.
- D2 (SUPERSEDED by #773, 2026-09-28): was "retain direct commit as an explicit
  human-only exception". The owner-directed #773 rule (mandatory CHG+IPLAN for
  every post-seed activity, seed-phase drafting the sole exception) overrides
  it: NO direct-commit path survives, for any author. The CHG-12 record carries
  the new rejected candidate (retain-human-exception) with rationale, per the
  router mandate. Scope delta from the supersede: AGENTS.md exceptions collapse
  fully, template/C1 rows lose the human carve-out, seed-phase exception added
  everywhere a carve-out was cited.
- D3: Docs-only C1 CHG entry gate: None (peer review) vs GATE-CODE.
  Recommendation: keep the existing C1 split — None for human docs-only,
  GATE-CODE for anything code-touching or agent-authored.
- D4: The change applies its own new rule to itself — the IPLAN carries a
  docs-compliance verification step over every file in §Scope.

## Verification

- `python3 sdd_doc_lint/chg_lint.py <chg-file>` clean (CHG-L004/L005/L013 scope).
- Conformance green, router-agreement + mirror-twin suites updated for the
  unified F2 row (`tests/conformance/test_chg_flows_router.py`).
- E005–E008 CI checks: VERSION bumped, pins match (`sync-version-refs`
  clean), both CHANGELOGs cut; W003 security review recorded.
- `gh pr checks` green on the new head before any merge decision.

## Claim ledger

| # | Claim | Symbol | Citation |
|---|-------|--------|----------|
| 1 | F2.2 keeps docs-only non-normative C1 as direct commit, no CHG/IPLAN | Docs-only, non-normative C1 | framework/governance/CHG_REQUEST_FLOWS.md:63 |
| 2 | Template C1 row encodes docs-only direct commit vs code-touching C1 CHG + scoped IPLAN | C1 \| Typo, formatting, clarification | framework/governance/chg/CHG-TEMPLATE.yaml:65 |
| 3 | 09_CHG README C1 row mirrors the same split | C1 \| Typo, formatting, clarification | framework/layers/09_CHG/README.md:101 |
| 4 | GOV-018 fires only on code/script manifests with empty lifecycle | GOV-018 | framework/governance/LINT_RULES.md:177 |
| 5 | AGENTS.md exempts docs-only non-normative C1 (direct commit) | docs-only non-normative C1 (direct commit) | AGENTS.md:105 |
| 6 | AGENTS.md IPLAN Gate: docs-only non-normative C1 needs neither CHG nor IPLAN | Docs-only non-normative C1 needs neither CHG nor IPLAN | AGENTS.md:124 |
| 7 | Governance core §3.13 repeats the F2.2 direct-commit carve-out | Direct-request C1 (F2.2) | framework/governance/DOC_GOVERNANCE_CORE.md:313 |
| 8 | Governance core §3.1.3 F2 row: docs-only = no CHG/IPLAN | Direct request (human/AI ask, no behavior change, no prior IPLAN) | framework/governance/DOC_GOVERNANCE_CORE.md:167 |
| 9 | Layer/governance CHG copies are kept byte-identical, governance wins | kept byte-identical | framework/layers/09_CHG/README.md:24 |
| 10 | Issue #772 is OPEN — blocks Phase 1 (CHG authoring cites the issue) | — | PROBE: `gh issue view 772 -R vladm3105/aidoc-flow-framework --json state --jq .state` |
| 11 | Worktree clean on `dev` at plan time — blocks Phase 3 (worktree/branch creation) | — | PROBE: `git status --short --branch` |
| 12 | `major` ⇒ C3 required; `minor`/`patch` may be C2 (NEW@pass1) | SemVer impact declared; `major` must be C3 | framework/governance/chg/gates/GATE-SPEC_FRAMEWORK.md:108 |
| 13 | Spec change never C1 (NEW@pass1) | A framework-spec change is never C1 | framework/governance/chg/gates/GATE-SPEC_FRAMEWORK.md:109 |
| 14 | VERSION must bump on normative `framework/**` change (NEW@pass1) | `framework/VERSION` must bump when normative `framework/**` changes | framework/governance/chg/gates/GATE-SPEC_FRAMEWORK.md:111 |
| 15 | CHANGELOG must be updated (NEW@pass1) | `CHANGELOG.md` updated | framework/governance/chg/gates/GATE-SPEC_FRAMEWORK.md:114 |
| 16 | Agent-facing spec change needs SECURITY_REVIEW assessment (NEW@pass1) | Agent-facing spec change (template/governance guidance) without a recorded `SECURITY_REVIEW.md` assessment | framework/governance/chg/gates/GATE-SPEC_FRAMEWORK.md:127 |
| 17 | SDD-first: lifecycle-carrying sources need SDD steps before IPLAN (NEW@pass1) | SDD-first order | framework/governance/LINT_RULES.md:155 |
| 18 | Router test pins both template mirrors + both README mirrors + Direct row (NEW@pass1) | CHG request-flows router agreement | tests/conformance/test_chg_flows_router.py:1 |
| 19 | Any author may select F2, backstopped by lint + human review (NEW@pass1) | Who may select F2: any author CONFIRMED | framework/governance/CHG_REQUEST_FLOWS.md:182 |
| 20 | Router step 5 restates the docs-only carve-out (NEW@pass1) | C1 direct commit | framework/governance/CHG_REQUEST_FLOWS.md:146 |
| 21 | Archive/rewrite phases count as SDD steps in CHG-L005 (NEW@pass2) | archive | sdd_doc_lint/chg_lint.py:284 |
| 22 | IPLAN steps with zero SDD steps error on `spec` source (NEW@pass2) | no SDD lifecycle steps | sdd_doc_lint/chg_lint.py:322 |
| 23 | C3 spec change requires human approval (NEW@pass2) | C3 spec change requires human approval | framework/governance/chg/gates/GATE-SPEC_FRAMEWORK.md:110 |
| 24 | Reclassification must record the rejected candidate + rationale (NEW@pass2) | rejected candidate | framework/governance/CHG_REQUEST_FLOWS.md:149 |

## Review log

### Pass 1 - 2026-09-28 - independent

8 load-bearing findings, verdict `revise`: (1) E002 inverted — minor does
not force C3; (2) minimal direct/C1 shape is the future F2 rule, not this
vehicle's classification (F3/spec ≥ C2); (3) scope omitted VERSION bump
(E005); (4) scope omitted §6 router step 5 + §8(c); (5) "fail-closed" false
— GOV-018 fires only on code/script manifests, enforcement TBD at CHG;
(6) ledger omitted E003/spec-vehicle/E005/E008/CHG-L005; (7) docs-compliance
rule named no normative home — candidate added, final at CHG;
(8) router-agreement + mirror-twin suites not dispositioned. Fold: Approach
corrected, scope items 3/5/8/9/10 added or rewritten, verification
retargeted to E005–E008 + W003, ledger rows 12–20 added NEW@pass1.

### Pass 2 - 2026-09-28 - independent

4 load-bearing findings, verdict `revise`: (1) CHG-L005 trips on `spec` +
IPLAN steps with zero SDD steps — verified in `chg_lint.py`, archive/rewrite
phases count; (2) C2 default unjustified without breaking-change analysis,
E004 approval unaddressed; (3) TBD enforcement + open D2 left the rule
reviewer-lens-only and un-actionable; (4) §8(c) reversal lacked the
router-mandated rejected-candidate rationale. Fold: Approach now carries the
archive→rewrite lifecycle, the breaking-change-gated C2/C3 call, and E004;
D2 decided (human-only exception retained, rejection recorded in CHG);
enforcement selection made a mandatory CHG deliverable; ledger rows 21–24
added NEW@pass2. Fold complete — awaiting gate + confirm pass.

### Pass 3 - 2026-09-28 - independent

Confirm scope: Pass 2 fold surface only. Verified (a) archive→rewrite
satisfies CHG-L005 for `spec`; (b) breaking-change-gated C2/C3 with E002
one-directional + E004; (c) decided D2 consistent with §8(c) given the
recorded rejected candidate; (d) no unledgered claim in the fold. One nit:
E003 cited in Approach without a NEW@pass2 row — covered by row 13, no
change. **Result:** ready
