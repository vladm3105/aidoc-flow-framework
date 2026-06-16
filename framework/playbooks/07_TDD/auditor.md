---
layer: 07_TDD
lens: auditor
weight: 10
agent: traceability-auditor
framework_spec_version: "0.23.0"
---
# auditor lens — TDD layer

## Reasoning frame

The auditor lens at TDD altitude validates conformance to the formal
rules that govern test-document structure: ID naming, upstream-trace
resolution against TDD's necessary-upstream set (EARS, BDD, ADR, SPEC
per NECESSARY-UPSTREAM-001, framework `0.16.0`), test-coverage-
matrix↔body parity, and cross-TDD reference form. TDD is the
downstream end of the trace chain; PRD and BRD lineage is reachable
transitively through the EARS/BDD `@`-tag chain (one hop per layer).

Traceability at TDD altitude runs across the necessary-upstream set
plus any decorative cumulative-trace tags the author chose to emit.
Every `@bdd: BDD.NN…` / `@spec: SPEC.NN…` / `@ears: EARS.NN…` /
`@adr: ADR-NN` tag in the TDD document MUST resolve to a named
element in the corresponding upstream document. Optional `@prd:` or
`@brd:` tags MAY appear as decorative-lineage hints; if emitted,
they must also resolve, but their absence is not a finding (the
necessary-upstream contract is the gate). The TDD layer is where
the trace chain pays off: when a TDD test fails, the operator should
be able to walk back through the trace tags to understand which
upstream commitment was violated. Broken tags collapse the chain.

Test-case ID conformance is the second concern. Every test case must
carry an ID matching `TDD.NN.SS.xxxx` (4-hex content-hash) so that
test failures can be referenced unambiguously in incident reports,
traceability matrices, and change-management records.

Test-coverage matrix↔body parity, necessary-upstream trace header,
and cross-TDD reference form round out the lens. The test-coverage
matrix at the top of the TDD document indexes test cases; every
matrix row must trace to a body test case, and every body test case
must appear in the matrix. The `@bdd: / @spec: / @ears: / @adr:`
header at the doc level (declared once and applying to every test
case) must resolve cleanly. Cross-TDD references must use the right
form: dash for doc-level refs (`@tdd: TDD-NN`), dotted for element-
level (`@tdd: TDD.NN.SS.xxxx`).

This lens does NOT evaluate: test-suite integrity (qa_lead),
test-engineering (tech_lead), failure-mode coverage (chaos_engineer),
security-test coverage (security_engineer), or observability
emission (operator). The auditor lens is confined to formal trace
conformance and ID hygiene at TDD altitude.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Upstream tags resolve to existing IDs.** Every required
necessary-upstream tag — `@ears:` / `@bdd:` / `@adr:` / `@spec:` —
in the TDD (whether in the doc-level header or per-test) MUST
resolve to an existing element ID in the corresponding upstream
document. Optional decorative `@prd:` / `@brd:` tags, when emitted,
must also resolve — but their absence is not a finding (necessary-
upstream contract; see NECESSARY-UPSTREAM-001). Broken required tag
→ P1 citing C1; broken decorative tag → P2 citing C1.

**C2 — Element IDs conform to `TDD.NN.SS.xxxx` 4-hex pattern.**
Every test-case ID in the TDD body follows the canonical pattern.
Non-conformant IDs cannot be referenced unambiguously in incident
reports, traceability matrices, or change-management records.
Non-conformant → P1 citing C2.

**C3 — Test-coverage matrix rows paired with body test cases.**
Every row in the TDD's top-of-document test-coverage matrix has a
paired body test case carrying the matching ID. Conversely, every
body test case appears in the matrix. Orphan row / orphan body
case → P2 citing C3.

**C4 — Necessary-upstream header resolves.** The doc-level upstream
header carries TDD's necessary-upstream set per the
necessary-upstream contract (NECESSARY-UPSTREAM-001, framework
`0.16.0`): `@ears | @bdd | @adr | @spec`. **TDD does NOT include
`@prd` or `@brd` in its required header** — PRD and BRD lineage is
reachable transitively through the EARS/BDD `@`-tag chain
(`REVIEW_TEAM.md` §Necessary upstream + transitive trace). A broken
necessary-upstream header cascades into every body element. Missing
required tag or unresolvable reference → P2 citing C4.
*Origin update:* the pre-0.16.0 cumulative-trace version of this
check listed `@brd / @prd` in the header; updated by CLEANUP-PR-B
item 7 (2026-06-11) to match the necessary-upstream contract that
was already in effect on disk.

**C5 — Cross-TDD references use correct form.** `@tdd:` references
use the dash form (`@tdd: TDD-NN`) when pointing to a whole document
and the dotted form (`@tdd: TDD.NN.SS.xxxx`) when pointing to a
specific test case. Tools branch on the form; wrong form produces
broken cross-links. Wrong form → P3 citing C5.

## Beyond-checklist

If you find a trace-hygiene failure mode the checklist does not cover,
raise it as a P2/P3 finding citing `beyond-checklist:<principle-tag>`
and state which paragraph of the reasoning frame motivates it. Common
beyond-checklist cases at TDD: stale-trace (a tag resolves but the
upstream element has changed semantics since the tag was written),
unused-upstream (an upstream element has no downstream TDD test —
the trace tree has gaps), or fingerprint-collision (two test cases
have the same 4-hex slug in the same document). Use sparingly. If
more than 30% of your findings are beyond-checklist, the playbook
needs revision (file a follow-up).


*Cross-layer cardinality note (CLEANUP-PR-F item 18):* apparent-orphan
downstream docs (e.g., `PRD-02` declaring `@brd: BRD-01` when `PRD-01`
also exists with the same upstream) MAY be valid siblings of the same
upstream, not actual orphans. Validate the trace by tag resolution, not
by doc-number alignment. See `framework/governance/ID_NAMING_STANDARDS.md`
§Cross-layer cardinality.
## No-findings rationale

A lens returning `lens_score: 100` with `findings: []` (zero findings)
MUST accompany its persona-output record with a `no_findings_rationale`
field naming at least one specific section where the lens *did* examine
the artifact and explicitly cleared. Example for this lens:

> `no_findings_rationale: "§<section-number> <topic> — examined and
> verified clean against checks C1-C5; no deviation from upstream
> required attributes."`

The synthesizer treats a missing or empty `no_findings_rationale` on
a `lens_score: 100 / findings: []` output as a structural error and
caps the lens at 95 (with a `STRUCTURE-RAT-001` advisory in the
verdict). The cap is a calibration nudge against "convergence theater"
— a lens that genuinely cleared the artifact must say *what* it
cleared, otherwise the score is unsubstantiated.

Filing findings (any priority, including P3 nits) bypasses the
rationale requirement — findings ARE the rationale.

## Scoring

| Outcome | lens_score |
|---|---|
| No findings; every check ran clean | 100 |
| P3 findings only; no checklist holes | 90-99 |
| 1-2 P2 findings against checks; no P1 | 80-89 |
| 3+ P2 against checks OR 1 P1 | 70-79 |
| P0 present OR systemic checklist failure | < 70 |
