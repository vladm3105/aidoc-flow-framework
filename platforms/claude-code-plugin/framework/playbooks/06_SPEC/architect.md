---
layer: 06_SPEC
lens: architect
weight: 30
agent: solutions-architect
framework_spec_version: "0.14.3"
---
# architect lens — SPEC layer

## Reasoning frame

The architect lens at SPEC altitude evaluates whether the specification
captures every committed architectural decision in implementable form
and whether the layout of the document respects the SPEC contract from
the template. The SPEC sits between ADR (decisions) and TDD (test
design); it is where the ADR commitments get translated into concrete
interface contracts, sequence diagrams, NFRs, and security controls
that downstream implementation can encode without re-deriving the
architecture. An ADR that adopted "event-driven communication" must
land in the SPEC as a named queue technology, specific delivery
semantics, and a named boundary; if the SPEC re-restates the ADR
abstractly it has not done its job.

A well-formed SPEC document carries every section the SPEC template
mandates: identifying header, interface catalog, sequence diagrams,
non-functional requirements, security controls, integration contracts,
and the inherited ADR table. Each section serves a downstream consumer
(TDD reads NFRs to author resilience scenarios; implementation reads
interfaces; security review reads controls). A missing section is a
defect because the downstream consumer is left to guess what the
architect intended. Each interface in the catalog must be defined as
(name, inputs, outputs, errors, semantics) — a tuple-style definition
the implementer can mechanically translate to code. Hand-wavy interface
descriptions ("returns the user object") push design decisions into the
implementation phase, where the implementer lacks the architectural
context.

The SPEC must not contradict any ADR commitment it inherits. The ADR
chose a one-way trust boundary; the SPEC cannot quietly relax it. The
ADR chose async delivery; the SPEC cannot quietly assume sync. The
lens enforces consistency with the upstream commitment graph and flags
contradictions as P1 because a SPEC that contradicts an ADR creates an
unresolvable inconsistency: either the ADR is wrong (separate change
management) or the SPEC is wrong (this PR must fix it).

SPEC altitude is the final concern. A SPEC that re-states EARS
requirements is too low (EARS already exists; restating wastes
reader time and creates drift surface). A SPEC that designs at
class-level granularity is too low (the TDD will do that). A SPEC
that operates at decision-level granularity is too high (the ADR
already exists). The right altitude is interface contracts, sequence
diagrams, NFR targets, and control implementation — concrete enough
to bind downstream layers, abstract enough to leave implementation
choices to the implementer.

This lens does NOT evaluate: implementability mechanics (tech_lead),
cross-component contracts (integration_lead), resilience-under-load
(chaos_engineer), or security-control implementation
(security_engineer). The architect lens is confined to specification
integrity, ADR consistency, and altitude maintenance.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Required template sections present.** Every section the SPEC
template mandates is present in the document (identifying header,
interface catalog, sequence diagrams, NFRs, security controls,
integration contracts, inherited-ADR table). A missing section is a
defect because the downstream consumer is left to guess. Missing →
P1 citing C1.

**C2 — Each interface defined as (name, inputs, outputs, errors, semantics).**
Every interface in the catalog carries the tuple a downstream
implementer can mechanically translate to code. Hand-wavy descriptions
push design decisions into the implementation phase. Hand-wavy →
P2 citing C2.

**C3 — Inherited ADR commitments respected (no contradiction).** The
SPEC does not contradict any ADR commitment it inherits. ADR-named
trust boundaries, delivery semantics, crypto choices, etc. are
preserved in the SPEC. Quietly relaxing an ADR commitment is a
defect, not a trade-off. Contradiction → P1 citing C3.

**C4 — SPEC altitude maintained.** The document operates at
interface-contract / sequence / NFR / control altitude — not too low
(restating EARS or designing classes) and not too high (deciding
architecture). Wrong altitude pollutes the documentation chain and
forces downstream layers to compensate. Wrong altitude → P2 citing C4.

**C5 — Section-level traceability.** Every section traces to an
upstream ADR or EARS reference, or explicitly declares "no upstream"
when the section captures SPEC-original content (e.g., template
boilerplate). Orphan sections leave the reader unable to navigate
from the SPEC back to the commitment that drove it. Orphan → P3
citing C5.

## Beyond-checklist

If you find a specification-integrity failure mode the checklist does not
cover, raise it as a P2/P3 finding citing `beyond-checklist:<principle-tag>`
and state which paragraph of the reasoning frame motivates it. Common
beyond-checklist cases at SPEC: under-specified-extension-point (a SPEC
section names an extension point but does not constrain it), late-
binding-coupling (the SPEC binds two components more tightly than the
ADR allowed), or template-drift (the SPEC uses an older template than
the project standard). Use sparingly. If more than 30% of your findings
are beyond-checklist, the playbook needs revision (file a follow-up).

## Scoring

| Outcome | lens_score |
|---|---|
| No findings; every check ran clean | 100 |
| P3 findings only; no checklist holes | 90-99 |
| 1-2 P2 findings against checks; no P1 | 80-89 |
| 3+ P2 against checks OR 1 P1 | 70-79 |
| P0 present OR systemic checklist failure | < 70 |
