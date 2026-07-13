---
layer: 06_SPEC
lens: integration_lead
weight: 20
agent: solutions-architect
framework_spec_version: "0.37.2"
---
# integration_lead lens — SPEC layer

## Reasoning frame

The integration_lead lens first appears at SPEC altitude because the
SPEC is the layer where cross-component contracts crystallize. The
ADR named the architectural commitments; the SPEC encodes how those
commitments meet at each boundary between this service and the
adjacent components it talks to. integration_lead evaluates the
edges of the SPEC — every place where a contract has to hold across
two independent code paths owned by potentially different teams.

A boundary without a named contract is the most expensive defect at
SPEC altitude. When two components meet without a written contract,
each team will encode a slightly different mental model of the
interface, and the integration test discovers the mismatch — usually
at the worst possible moment. The contract must name the interface
(method or message), the version (so consumers know what they bind
to), and the delivery semantics (sync request / async event / batched
push). All three together define the boundary; any one missing leaves
ambiguity.

Compatibility matrices matter when the boundary supports multiple
consumer versions. A SPEC that names version 2 of an interface but
does not state whether version 1 callers are still supported leaves
the SPEC's deployment story underdetermined. The matrix declares
which versions are supported simultaneously and which are deprecated
or removed.

Failure semantics across the boundary, schema evolution policy, and
cross-boundary observability round out the lens. Failure semantics
state what happens when the boundary fails — timeout values, retry
policy, circuit-breaker thresholds, dead-letter destinations. Schema
evolution names the rules for changing the data shape at the boundary
— backward (old senders work with new receivers), forward (new
senders work with old receivers), both, or breaking. Observability
declares which side of the boundary exposes the trace, metric, or
log when the boundary is crossed; without this, two operators chase
the same incident on opposite sides of the same boundary.

This lens does NOT evaluate: specification integrity (architect),
implementability mechanics (tech_lead), resilience-under-load
(chaos_engineer), or security-control implementation
(security_engineer). The integration_lead lens is confined to
cross-component contracts and their lifecycle.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Every component boundary has a named contract.** Every place
this service meets an adjacent component has a contract that names
(a) the interface (method or message), (b) the version, and (c) the
delivery semantics (sync request / async event / batched push).
Boundaries without a named contract are the highest-cost defect at
SPEC altitude. Missing → P1 citing C1.

**C2 — Compatibility matrix declared on multi-version boundaries.**
When the boundary supports multiple consumer versions (or producer
versions), the SPEC declares which versions are supported
simultaneously and which are deprecated or removed. Hand-wave ("we
support old clients") → P2 citing C2.

**C3 — Failure semantics stated across the boundary.** The SPEC
names the timeout value, retry policy, circuit-breaker threshold,
and dead-letter destination (where applicable) for every cross-
component call. Implicit failure handling leads to silent retries,
duplicate side effects, or hung callers. Missing → P2 citing C3.

**C4 — Schema-evolution policy named for shared data.** For data
that crosses the boundary (request/response shapes, event payloads,
shared persistent records), the SPEC names the evolution rule:
backward-compatible / forward-compatible / both / breaking-on-MAJOR.
Missing → P2 citing C4.

**C5 — Observability across the boundary.** The SPEC declares which
component exposes which trace, metric, or log when the boundary is
crossed (e.g., the producer emits an outbound-event span; the
consumer emits a processing-latency histogram). Without this, two
operators chase the same incident on opposite sides of the same
boundary. Missing → P3 citing C5.

## Beyond-checklist

If you find a cross-component-contract failure mode the checklist does
not cover, raise it as a P2/P3 finding citing
`beyond-checklist:<principle-tag>` and state which paragraph of the
reasoning frame motivates it. Common beyond-checklist cases at SPEC:
implicit-back-pressure (the boundary specifies inbound flow but not
the back-pressure response when the receiver is overloaded), undeclared-
ordering-guarantee (the boundary implies an order without stating
whether ordering is per-key, global, or none), or feature-flag-crossing
(the SPEC introduces a feature flag that crosses the boundary without
declaring which side gates the behavior). Use sparingly. If more than
30% of your findings are beyond-checklist, the playbook needs revision
(file a follow-up).

## Scoring

| Outcome | lens_score |
|---|---|
| No findings; every check ran clean | 100 |
| P3 findings only; no checklist holes | 90-99 |
| 1-2 P2 findings against checks; no P1 | 80-89 |
| 3+ P2 against checks OR 1 P1 | 70-79 |
| P0 present OR systemic checklist failure | < 70 |
