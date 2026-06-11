---
layer: 07_TDD
lens: auditor
weight: 10
agent: traceability-auditor
framework_spec_version: "0.18.0"
---
# auditor lens — TDD layer

## Reasoning frame

The auditor lens at TDD altitude validates conformance to the formal
rules that govern test-document structure: ID naming, upstream-trace
resolution across the longest chain in the framework (BRD → PRD →
EARS → BDD → SPEC, with ADR commitments inherited), test-coverage-
matrix↔body parity, and cross-TDD reference form. TDD is the
downstream end of the trace chain; its auditor lens has the most
upstream layers to resolve against.

Traceability at TDD altitude runs across the full upstream chain.
Every `@bdd: BDD.NN…` / `@spec: SPEC.NN…` / `@ears: EARS.NN…` /
`@adr: ADR-NN` / `@prd: PRD.NN…` / `@brd: BRD.NN…` tag in the TDD
document must resolve to a named element in the corresponding
upstream document. The TDD layer is where the trace chain pays off:
when a TDD test fails, the operator should be able to walk back
through the trace tags to understand which upstream commitment was
violated. Broken tags collapse the chain.

Test-case ID conformance is the second concern. Every test case must
carry an ID matching `TDD.NN.SS.xxxx` (4-hex content-hash) so that
test failures can be referenced unambiguously in incident reports,
traceability matrices, and change-management records.

Test-coverage matrix↔body parity, cumulative trace header, and
cross-TDD reference form round out the lens. The test-coverage matrix
at the top of the TDD document indexes test cases; every matrix row
must trace to a body test case, and every body test case must appear
in the matrix. The cumulative `@bdd: / @spec: / @ears: / @adr:` /
`@prd:` / `@brd:` header at the doc level (declared once and
applying to every test case) must resolve cleanly. Cross-TDD
references must use the right form: dash for doc-level refs
(`@tdd: TDD-NN`), dotted for element-level (`@tdd: TDD.NN.SS.xxxx`).

This lens does NOT evaluate: test-suite integrity (qa_lead),
test-engineering (tech_lead), failure-mode coverage (chaos_engineer),
security-test coverage (security_engineer), or observability
emission (operator). The auditor lens is confined to formal trace
conformance and ID hygiene at TDD altitude.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Upstream tags resolve to existing IDs.** Every `@bdd:` /
`@spec:` / `@ears:` / `@adr:` / `@prd:` / `@brd:` tag in the TDD
(whether in the cumulative header or per-test) resolves to an
existing element ID in the corresponding upstream document. Broken
tags collapse the longest trace chain in the framework. Broken tag
→ P1 citing C1.

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

**C4 — Cumulative trace header resolves.** The cumulative `@bdd: /
@spec: / @ears: / @adr: / @prd: / @brd:` header at the doc level
(declared once, applying to every test) resolves cleanly to existing
upstream IDs. A broken cumulative header cascades into every body
element. Missing or broken → P2 citing C4.

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

## Scoring

| Outcome | lens_score |
|---|---|
| No findings; every check ran clean | 100 |
| P3 findings only; no checklist holes | 90-99 |
| 1-2 P2 findings against checks; no P1 | 80-89 |
| 3+ P2 against checks OR 1 P1 | 70-79 |
| P0 present OR systemic checklist failure | < 70 |
