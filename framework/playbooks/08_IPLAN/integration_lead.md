---
layer: 08_IPLAN
lens: integration_lead
weight: 12
agent: solutions-architect
framework_spec_version: "0.27.0"
---
# integration_lead lens — IPLAN layer

## Reasoning frame

The integration_lead lens appears for the first time at IPLAN
altitude (weight 12) because IPLAN is the first layer where multiple
services touch a real environment together over a real time window.
Earlier layers reason about a static system: the ADR fixes the
topology, the SPEC fixes the contracts, the TDD fixes the test
suite. The IPLAN is where those static contracts have to survive a
moving cutover, during which the producer and consumer of an
interface may be on different versions, behind different flag
states, for a measurable duration. The integration_lead lens
evaluates whether the IPLAN holds the cross-service compatibility
invariants intact across that window.

This lens is distinct from architect and operator. The architect
lens asks "does the deployed topology match the architecture?" — a
question about the static graph. The operator lens asks "can the
on-call engineer see what is happening during the cutover?" — a
question about telemetry. The integration_lead lens asks a third
question: "while service A is on version N and service B is on
version M, can A still call B (and vice versa) without breaking
either party's contract?" That question lives at the seams between
services and is invisible to both a static topology audit and a
live telemetry feed until something has already broken.

Contract version pinning, dependency-rollout order, and
backward-compatibility windows are the practical concerns. Each
cutover step that crosses a service boundary must pin the contract
version both sides accept; feature flags must declare their default
state (off, on, percentage) per environment; the rollout order
must walk the SPEC's component DAG from upstream to downstream so
producers reach the new contract before consumers; and the
backward-compatibility window (how long old and new run side-by-
side) must be declared so consumers have a deterministic deadline
for upgrading. Pre-cutover integration test gates close the loop:
they run at each phase boundary and assert the cross-service
contracts still hold before the next phase begins.

This lens does NOT evaluate: deploy-sequence reversibility
(tech_lead), topology invariance (architect), smoke-test /
observability emission (operator), upstream-trace conformance
(auditor), or rollback dress-rehearsal practice (chaos_engineer).
The integration_lead lens is confined to cross-service
compatibility across the cutover window.

### Subtype awareness (CLEANUP-PR-E item 17)

This lens reads `document_control.subtype` from the artifact and
adapts:

- **`code_build` subtype:** deploy concerns (rollback / smoke /
  canary / observability) are explicitly out of scope. This lens
  MAY return `lens_score: 100` with `findings: []` if every applicable
  code-build check passes; the no-findings rationale takes the form:
  `no_findings_rationale: "subtype: code_build — deploy concerns out
  of scope per CLEANUP-PR-E IPLAN sub-types contract."` This satisfies
  the no-findings-rationale rule (CLEANUP-PR-B item 8) — the rationale
  is the subtype declaration itself.
- **`deploy` or `combined` subtype:** all the checks below apply.
  Missing rollback / smoke / canary / observability sections that
  the subtype requires are blocking findings.
- **Missing subtype** (pre-0.19.1 IPLAN): defaults to `combined`.
  All checks apply.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check
citation are out-of-scope and discarded by the synthesizer.

**C1 — Cross-service contract versions explicitly pinned per cutover
step.** Each cutover step that crosses a service boundary names the
contract version both producer and consumer must accept during that
step. A step without a pinned version permits a producer-consumer
mismatch when one side moves ahead. Missing → P1 citing C1.

**C2 — Integration test gates run pre-cutover at each phase
boundary.** Each phase boundary names the integration test suite
that must pass before the next phase begins. Integration gates
that only run at the start (or only at the end) leave the middle
phases unverified. Missing → P2 citing C2.

**C3 — Dependency rollout order reflects the SPEC's component DAG
(upstream first).** Producers in the SPEC's component DAG roll out
before their consumers; consumer-first ordering creates a window
where the new consumer calls an old producer. The IPLAN's step
sequence must follow the DAG. Wrong order → P2 citing C3.

**C4 — Feature-flag default state declared per flag.** Each feature
flag introduced or flipped by the IPLAN declares its default state
(off / on / percentage value) per environment. A flag without a
declared default depends on whatever state happens to exist at
deploy time. Missing → P3 citing C4.

**C5 — Backward-compatible API window declared.** When the IPLAN
introduces a new API or contract revision, it declares how long the
old and new run side-by-side before the old is retired. A window
without a deadline lets the old version linger; no window at all
forces consumers to upgrade in lockstep. Missing → P3 citing C5.

## Beyond-checklist

If you find a cross-service compatibility failure mode the checklist
does not cover, raise it as a P2/P3 finding citing
`beyond-checklist:<principle-tag>` and state which paragraph of the
reasoning frame motivates it. Common beyond-checklist cases at IPLAN
integration altitude: a contract reference written as "latest"
rather than pinned to a specific version, so producer and consumer
land on whichever version their build resolved at deploy time; a
cross-service handoff whose backward-compatibility window is implied
("we'll keep the old one around for a while") rather than declared
with a retirement deadline; a feature-flag default left implicit, so
the consuming service's behavior at cutover depends on the runtime
flag state rather than the IPLAN's stated intent; and a dependency
rollout sequence that assumes simultaneous upgrade across services
rather than walking the SPEC's DAG in order. Use sparingly. If more
than 30% of your findings are beyond-checklist, the playbook needs
revision (file a follow-up).

## Scoring

| Outcome | lens_score |
|---|---|
| No findings; every check ran clean | 100 |
| P3 findings only; no checklist holes | 90-99 |
| 1-2 P2 findings against checks; no P1 | 80-89 |
| 3+ P2 against checks OR 1 P1 | 70-79 |
| P0 present OR systemic checklist failure | < 70 |
