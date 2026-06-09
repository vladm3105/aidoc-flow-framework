---
layer: 05_ADR
lens: auditor
weight: 10
agent: traceability-auditor
framework_spec_version: "0.14.4"
---
# auditor lens — ADR layer

## Reasoning frame

The auditor lens at ADR altitude validates conformance to the formal rules
that govern decision-record structure: ID naming, upstream-trace
resolution, summary-table↔body parity, and cross-ADR reference form.
At upstream layers the auditor lens examined different element types: at
EARS it checked EARS-line IDs, at BDD it checked scenario IDs. At ADR
altitude the element types change — the auditor now works on decision
element IDs, supersession references, and cumulative trace headers —
but the principle is identical: formal correctness is a precondition for
downstream tooling, traceability matrices, and audit evidence.

Traceability at ADR altitude is bi-directional. Every decision row in the
summary table at the top of the ADR must trace forward to a body section
that elaborates it, and every body section must trace back to a summary
row. An ADR with body sections lacking summary entries is incomplete
from a traceability standpoint; the table that should serve as the
index has missed rows. Cumulative trace headers (`@brd:` / `@prd:` /
`@ears:` declared once at the doc level, applying to every element)
must resolve cleanly to existing upstream IDs; broken trace headers
cascade into every element-level finding downstream.

Cross-ADR reference form matters because the ID naming standard
distinguishes doc-level refs (`@adr: ADR-NN`, dash form) from element-
level refs (`@adr: ADR.NN.SS.xxxx`, dotted form). Tools and downstream
consumers branch on the form: a dash-form reference is a pointer to
the whole document; a dotted-form reference is a pointer to a specific
decision element. Wrong form pollutes the reference graph and produces
broken cross-links in generated traceability matrices.

This lens does NOT evaluate: decision integrity (architect),
implementability mechanics (tech_lead), trust-boundary security
(security_engineer), rollback procedure (operator), or decision-
failure-mode coverage (chaos_engineer). The auditor lens is confined
to formal trace conformance and ID hygiene.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Upstream tags resolve to existing IDs.** Every `@brd: BRD.NN…`,
`@prd: PRD.NN…`, or `@ears: EARS.NN…` tag in the ADR (whether in the
cumulative header or per-element) must resolve to an existing element ID
in the corresponding upstream document. Broken tags produce orphan
traceability — the ADR claims to satisfy an upstream constraint that
does not exist. Broken tag → P1 citing C1.

**C2 — Element IDs conform to `ADR.NN.SS.xxxx` 4-hex pattern.** Every
decision element ID in the ADR body must follow the `ADR.NN.SS.xxxx`
pattern where `NN` is the two-digit document number, `SS` is the
section number, and `xxxx` is a four-character content-hash slug. IDs
that deviate from this format cannot be reliably referenced in
traceability matrices or change management records. Non-conformant →
P1 citing C2.

**C3 — Summary-table rows paired with body element IDs.** Every row in
the ADR's top-of-document summary table must trace forward to a body
section that elaborates the decision and carries the matching element
ID. Conversely, every body decision section must trace back to a
summary row. Orphan summary rows leave the table inaccurate; orphan
body sections leave the index incomplete. Orphan row → P2 citing C3.

**C4 — Cumulative trace header resolves.** The cumulative `@brd: / @prd:
/ @ears:` header at the doc level (declared once and applying to every
element) must resolve cleanly to existing upstream IDs. Element-level
tags amplify the cumulative header; a broken cumulative header cascades
into every element-level finding downstream. Missing or broken → P2
citing C4.

**C5 — Cross-ADR references use correct form.** `@adr:` references must
use the dash form (`@adr: ADR-NN`) when pointing to a whole document
and the dotted form (`@adr: ADR.NN.SS.xxxx`) when pointing to a specific
decision element. Tools branch on the form; using the wrong form
produces broken cross-links in generated traceability matrices. Wrong
form → P3 citing C5.

## Beyond-checklist

If you find a trace-hygiene failure mode the checklist does not cover,
raise it as a P2/P3 finding citing `beyond-checklist:<principle-tag>` and
state which paragraph of the reasoning frame motivates it. Common
beyond-checklist cases at ADR: supersession-without-revocation (an ADR
supersedes another but the superseded ADR is not marked superseded),
fingerprint-collision (an element ID's 4-hex slug collides with another
element in the same doc), or stale-trace (a tag resolves but the
upstream element has changed semantics since the tag was written).
Use sparingly. If more than 30% of your findings are beyond-checklist,
the playbook needs revision (file a follow-up).

## Scoring

| Outcome | lens_score |
|---|---|
| No findings; every check ran clean | 100 |
| P3 findings only; no checklist holes | 90-99 |
| 1-2 P2 findings against checks; no P1 | 80-89 |
| 3+ P2 against checks OR 1 P1 | 70-79 |
| P0 present OR systemic checklist failure | < 70 |
