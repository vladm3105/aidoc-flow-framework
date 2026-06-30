---
layer: 02_PRD
lens: architect
weight: 25
agent: solutions-architect
framework_spec_version: "0.32.4"
---
# architect lens — PRD layer

## Reasoning frame

The architect lens at PRD altitude operates at the container boundary, not
the capability boundary and not the component boundary. A container is a named
deployable unit — a service, a datastore, an API gateway — that corresponds to
a distinct runtime process. At this layer the architect asks: do the declared
containers form a coherent structural intent that is internally consistent,
diagram-reconciled, and bounded at container altitude? Capability decomposition
belongs to BRD; class-level, interface-level, and method-level decisions belong
to SPEC. PRD architect work is the span between.

At BRD altitude the architect lens evaluated capability-level coherence with no
structural vocabulary allowed. At PRD altitude the lens ascends to container
diagrams (C4-L2), data-flow diagrams (DFD-L2), and sequence diagrams. At SPEC
altitude it descends again to component-level fault isolation, interface
contracts, and error-propagation paths. The PRD architect lens must prevent two
failure modes: premature descent (class names appearing in §9) and structural
underspecification (containers implied but unnamed, flows implied but undiagrammed).

The PRD architect lens does NOT evaluate: whether the scope definition matches
BRD authorization (product_owner), whether §11 validation cells are measurable
(tech_lead), whether failure-mode paths are covered by ACs (chaos_engineer),
whether trust boundaries are authorized (security_engineer), or whether IDs
conform to naming standards (auditor). This lens is confined to structural
coherence, diagram reconciliation, and altitude guard.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Diagram reconciliation.** C4-L2, DFD-L2, and sequence-sync diagrams
must reconcile: every named entity, flow, and trust boundary that appears in
one diagram must appear in all others where relevant. An entity present in the
C4-L2 but absent from the DFD-L2 (or vice versa) is a structural gap. Missing
→ P2 finding citing C1.

**C2 — Container altitude guard.** Every capability statement, diagram
annotation, and §9 requirement must remain at container altitude. Class names,
method signatures, database table names, API path patterns, and port numbers
are SPEC-altitude vocabulary. Any such term in the PRD signals premature descent.
Missing → P2 finding citing C2.

**C3 — Decomposition notes on every diagram.** Every diagram must carry a
`decomposition note` explaining which structural simplifications apply for MVP
and how the structure is expected to evolve in post-MVP iterations (e.g.,
"single link-store for MVP; split read/write stores in Phase 2"). A diagram
without a decomposition note obscures MVP scope decisions and creates
misalignment at SPEC. Missing → P3 finding citing C3.

**C4 — ADR-deferral pattern consistency.** When a structural decision is
explicitly deferred to an ADR, every such deferral must follow a consistent
signpost format (e.g., `[ADR-TBD: <decision-slug>]`). Inconsistent deferral
markers (some prose, some coded, some absent) prevent the synthesizer from
locating open decisions. Missing → P3 finding citing C4.

**C5 — NFR bounds scope-matched to §5.** NFR bounds stated in §11 (e.g.,
p95 < 50 ms) must define the same measurement boundary as the corresponding
§5 (Success Metrics) target. A §11 gate scoped to "read path" while §5 is
scoped to "end-to-end" creates an undetectable compliance gap. Missing → P2
finding citing C5.

**C6 — Integration contracts named at container boundary.** Where two
containers exchange data, the integration contract must be named at container
altitude (protocol family, data format, direction). Unnamed integrations leave
the SPEC author to infer contracts from context, which is a reliability risk.
Missing → P3 finding citing C6.

## Beyond-checklist

If you find a layer-specific failure mode the checklist does not cover, raise
it as a P2/P3 finding citing `beyond-checklist:<principle-tag>` and state
which paragraph of the reasoning frame above motivates it. Use sparingly. If
more than 30% of your findings are beyond-checklist, the playbook needs
revision (file a follow-up).

## Scoring

| Outcome | lens_score |
|---|---|
| No findings; every check ran clean | 100 |
| P3 findings only; no checklist holes | 90-99 |
| 1-2 P2 findings against checks; no P1 | 80-89 |
| 3+ P2 against checks OR 1 P1 | 70-79 |
| P0 present OR systemic checklist failure | < 70 |
