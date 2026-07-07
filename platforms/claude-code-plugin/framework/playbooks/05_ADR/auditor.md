---
layer: 05_ADR
lens: auditor
weight: 10
agent: traceability-auditor
framework_spec_version: "0.34.1"
---
# auditor lens — ADR layer

## Reasoning frame

The auditor lens at ADR altitude validates conformance to the formal rules
that govern decision-record structure: ID naming, upstream-trace
resolution, summary-table↔body parity, and cross-ADR reference form.
At upstream layers the auditor lens examined different element types: at
EARS it checked EARS-line IDs, at BDD it checked scenario IDs. At ADR
altitude the element types change — the auditor now works on decision
element IDs, supersession references, and necessary-upstream trace headers —
but the principle is identical: formal correctness is a precondition for
downstream tooling, traceability matrices, and audit evidence.

Traceability at ADR altitude is bi-directional. Every decision row in the
summary table at the top of the ADR must trace forward to a body section
that elaborates it, and every body section must trace back to a summary
row. An ADR with body sections lacking summary entries is incomplete
from a traceability standpoint; the table that should serve as the
index has missed rows. The necessary-upstream trace header (the ADR's
`@ears:` / `@bdd:` tags declared once at the doc level, applying to every
element) must resolve cleanly to existing upstream IDs; a broken trace header
cascades into every element-level finding downstream. (`@brd`/`@prd`, if
present, are optional provenance reached transitively — not required.)

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

**C1 — Required-upstream tags resolve to existing IDs.** Every
`@ears: EARS.NN…` and `@bdd: BDD.NN…` tag in the ADR (whether in the
header or per-element) must resolve to an existing element ID in the
corresponding upstream document. Per the necessary-upstream contract
(NECESSARY-UPSTREAM-001), ADR's `required_tags` is `[ears, bdd]`; tags
above the required set (e.g., decorative `@brd:` or `@prd:` lineage)
are permitted but the structural lint floor (`sdd_doc_lint TRACE-RES-001`)
enforces resolution on any emitted tag at any depth. Broken required
tag → P1 citing C1.

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

**C4 — Necessary-upstream trace header resolves.** The ADR's `@ears: / @bdd:`
header at the doc level (declared once and applying to every element) must
resolve cleanly to existing upstream IDs. Element-level tags amplify the
header; a broken header cascades into every element-level finding downstream.
Missing or broken → P2 citing C4.

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
