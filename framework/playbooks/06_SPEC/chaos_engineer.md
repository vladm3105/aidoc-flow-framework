---
layer: 06_SPEC
lens: chaos_engineer
weight: 10
agent: chaos-engineer
framework_spec_version: "0.36.0"
---
# chaos_engineer lens — SPEC layer

## Reasoning frame

The chaos_engineer lens at SPEC altitude carries equal weight with
security_engineer (10 / 10) per the REVIEW_CREWS.yaml rationale —
SPEC specifies both performance/resilience and security controls,
and both axes warrant equal review attention. The lens evaluates
whether the SPEC has characterized its resilience envelope: what
the system is expected to do under nominal load, what happens when
load exceeds the design point, how the system degrades, how long
recovery takes after a transient fault, and what semantic guarantees
each side-effect-producing interface offers.

Performance NFRs are the first concern. An NFR that says "fast
enough" or "low latency" cannot be tested, cannot be debugged when
violated, and cannot serve as the basis for capacity planning. A
proper NFR carries a concrete target: p95 / p99 latency, throughput
in requests per second, error budget in errors per million, and a
named measurement methodology (which probe, which percentile,
which window). Missing concrete targets at SPEC altitude pushes
NFR definition into the TDD or implementation phase, where the
team lacks the architectural context to choose the right number.

Saturation curves are the second concern. Every system has a load
point beyond which it stops behaving as designed. The SPEC must
characterize this — what is the design load, what is the safe
overload margin, and what is the system's behavior beyond that
margin (graceful degradation / drop / queue / crash). A SPEC silent
on saturation commits the operator to discover the curve in
production at 03:00.

Degradation order, recovery time, and side-effect semantics round
out the lens. Degradation order names which features the system
sheds first when overloaded and which it preserves — explicit
prioritization is the difference between graceful degradation and
random failure. Recovery time after a transient fault bounds the
MTTR; if not stated, the team will inherit an unbounded recovery
expectation. Side-effect semantics (at-most-once vs at-least-once)
must be stated at every side-effect-producing interface so consumers
can choose the right downstream guarantee.

This lens does NOT evaluate: specification integrity (architect),
implementability mechanics (tech_lead), cross-component contracts
(integration_lead), or security-control implementation
(security_engineer). The chaos_engineer lens is confined to
resilience-under-load and operational semantics.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Performance NFRs have concrete targets.** Every performance
NFR in the SPEC names a concrete target: percentile latency (p95 /
p99), throughput (req/s or events/s), error budget (errors per
million or % per window), and the measurement methodology. Missing
or vague targets push NFR definition into downstream layers where
the team lacks architectural context. Missing/vague → P1 citing C1.

**C2 — Saturation curve characterized.** The SPEC names the design
load, the safe overload margin, and the system's behavior beyond
that margin (graceful degradation / drop / queue / crash). A SPEC
silent on saturation forces the operator to discover the curve in
production. Unknown → P2 citing C2.

**C3 — Degradation order specified.** When overloaded, the SPEC
names which features the system sheds first and which it preserves.
Explicit prioritization is the difference between graceful
degradation and random failure under load. Missing → P2 citing C3.

**C4 — Recovery time after a transient fault bounded.** The SPEC
names the MTTR target — how fast the system returns to nominal
behavior after a transient fault (network blip, dependency timeout,
restart). Without this, the team inherits an unbounded recovery
expectation. Missing → P3 citing C4.

**C5 — At-most-once vs at-least-once semantics stated per side-effect.**
Every interface that produces a side effect (message publish,
external API call, persistent write) declares its semantics. A
SPEC silent on this commits the system to one of the two by
accident, and consumers may pick the other. Missing → P3 citing C5.

## Beyond-checklist

If you find a resilience or operational-semantics failure mode the
checklist does not cover, raise it as a P2/P3 finding citing
`beyond-checklist:<principle-tag>` and state which paragraph of the
reasoning frame motivates it. Common beyond-checklist cases at SPEC:
backpressure-policy-undefined (the SPEC takes input from a queue but
does not state what the producer sees when consumption is slow),
cold-start-window-unknown (the SPEC implies a warm-up period but
does not bound it), or noisy-neighbor-isolation (the SPEC describes
multi-tenant behavior without naming the isolation mechanism). Use
sparingly. If more than 30% of your findings are beyond-checklist,
the playbook needs revision (file a follow-up).

## Scoring

| Outcome | lens_score |
|---|---|
| No findings; every check ran clean | 100 |
| P3 findings only; no checklist holes | 90-99 |
| 1-2 P2 findings against checks; no P1 | 80-89 |
| 3+ P2 against checks OR 1 P1 | 70-79 |
| P0 present OR systemic checklist failure | < 70 |
