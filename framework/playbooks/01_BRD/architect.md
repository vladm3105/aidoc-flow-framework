---
layer: 01_BRD
lens: architect
weight: 30
agent: solutions-architect
framework_spec_version: "0.34.2"
---
# architect lens — BRD layer

## Reasoning frame

The architect lens at BRD altitude operates at the capability boundary, not the
implementation boundary. A capability is a named business ability — "the system
can ingest N events per hour" — not a container, service, or class. At this
layer the architect asks: are the stated capabilities internally consistent,
individually measurable, and collectively sufficient to satisfy the document's
objectives? Container diagrams, sequence flows, and component allocations all
belong in PRD (structural intent) or SPEC (component specification); they are
out of scope here.

At PRD altitude the architect lens shifts to structural intent — how the
declared capabilities translate to bounded contexts, service responsibilities,
and integration contracts. At SPEC altitude the lens narrows to component-level
decisions, fault isolation, and data-flow precision. The BRD architect lens
must resist the temptation to pre-solve structural questions that have not yet
been shaped by product prioritisation (PRD) or detailed requirements (EARS).

The BRD architect lens does NOT evaluate: per-requirement testability (qa_lead
at EARS), implementation feasibility (tech_lead at PRD/SPEC), operational
runbooks (operator), or regulatory compliance wording (auditor). Cross-cutting
concerns — which capability owns a shared service, which capability is
authoritative for a data entity — are within scope because they expose boundary
gaps at the earliest, least expensive moment.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Altitude guard.** Scan every capability statement, diagram
reference, and requirement for implementation-layer vocabulary: container
names, service mesh identifiers, class names, database table names, API path
patterns, port numbers. Any such term at BRD altitude signals premature
descent. Missing → P2 finding citing C1.

**C2 — Capability decomposition consistency.** Verify that every capability
named in §Objectives also appears in §Scope, §Requirements, and §Acceptance
Criteria (or is explicitly noted as out-of-scope with rationale). Orphan
capabilities (named in one section, absent from others) indicate decomposition
drift. Missing → P2 finding citing C2.

**C3 — Measurable outcomes on every capability.** Each capability must carry
a baseline ("current state: X") and a target ("goal state: Y") using
observable, numeric metrics. Phrases like "improve performance," "reduce
latency," or "better reliability" without baseline + target are not
measurable. Missing → P1 finding citing C3.

**C4 — Cross-capability boundary explicitness.** Where two capabilities share
a resource, data entity, or user-facing surface, the boundary must be named:
which capability owns the entity, which consumes it. Undeclared shared
ownership at BRD altitude becomes integration conflict at PRD. Missing → P2
finding citing C4.

**C5 — NFRs declared at capability altitude.** Availability targets,
durability classes, peak-throughput envelopes, and latency SLOs that the
business commits to should be stated at BRD when they constrain capability
design. If the BRD explicitly defers an NFR to an ADR, it must name the ADR
reference slot. Silent NFR omission (neither stated nor deferred) → P2 finding
citing C5.

**C6 — Scope boundary closed.** §Scope must enumerate what is explicitly
excluded as well as included, with a rationale for each exclusion. An open
scope boundary leaves capabilities undefined until PRD, where the cost of
discovery is higher. Missing → P2 finding citing C6.

**C7 — No circular capability dependencies.** If Capability A requires
Capability B to be delivered first, and B requires A, the circular dependency
must be named and resolved in the BRD (decompose, sequence, or collapse into
one capability). Silent circularity → P2 finding citing C7.

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
