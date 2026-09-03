---
layer: 05_ADR
lens: chaos_engineer
weight: 8
agent: chaos-engineer
framework_spec_version: "0.50.0"
---
# chaos_engineer lens — ADR layer

## Reasoning frame

The chaos_engineer lens at ADR altitude evaluates the decision against
the question "what breaks if this decision is wrong?" The lens carries
the lighter weight in the security/reliability split (8 vs security's
12) because ADRs are first-order codifications of architecture; the
failure-mode analysis that BDD scenarios will exercise is a downstream
concern. But the lens is not trivial at ADR — a decision that names a
failure mode and bounds the blast radius up front lets downstream
SPEC/TDD design defenses, while a decision silent on failure modes
forces downstream layers to discover the failure space empirically in
production.

Failure-mode naming is the central concept. Every decision can be
wrong — the queue technology can be the wrong choice for the workload,
the trust boundary can be drawn at the wrong layer, the protocol can
have a fatal mismatch with the consumers. The chaos_engineer lens
forces the ADR to name at least one concrete failure scenario: under
what condition does this decision produce a bad outcome? An ADR that
cannot name a failure mode either does not constrain anything (which
is suspicious) or has not been thought through.

Blast radius classification bounds the cost of being wrong. A decision
whose failure affects a single service is recoverable with focused
work; a decision whose failure crosses services or risks data loss
demands more careful adoption (canary, dual-write, pre-built
mitigation). The lens flags ADRs that lack a blast-radius classification
as P2 because the absence pushes the classification cost onto the
operator at incident time.

Detection-time bounds, pre-built mitigations, and at-most-once /
at-least-once semantics round out the lens. Detection-time matters
because a failure mode is only meaningful if the team can recognize
it before the blast radius widens to its maximum. Pre-built mitigations
matter when the decision is one-way and high blast: the team commits
in advance to a recovery path because there is no rollback. Side-effect
semantics matter because the at-most-once vs at-least-once choice
constrains every downstream interaction — a decision that touches
side-effect-producing operations without declaring the semantics
silently commits the system to one of the two, and the downstream
implementer may pick the other.

This lens does NOT evaluate: decision integrity (architect),
implementability mechanics (tech_lead), trust-boundary security
(security_engineer), rollback procedure (operator), or upstream-tag
conformance (auditor). The chaos_engineer lens is confined to
failure-mode rigor at the architectural altitude.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — "What breaks if this decision is wrong?" answered.** The ADR
names at least one concrete failure scenario: a condition under which
this decision produces a bad outcome. An ADR that cannot articulate
a failure mode either does not constrain anything or has not been
thought through; downstream SPEC/TDD inherits the burden of discovering
the failure space empirically. Missing → P2 citing C1.

**C2 — Blast radius classified.** The failure mode named in C1 is
classified by blast radius: single-service (recoverable with focused
work), cross-service (requires coordinated response), or data-loss-
possible (demands canary + dual-write + pre-built mitigation). Absence
of classification pushes the cost onto the operator at incident time
when classification under pressure is unreliable. Missing → P2 citing C2.

**C3 — Detection-time bound stated.** The ADR states how fast the team
will recognize the failure mode in production — a time bound expressed
in seconds, minutes, or hours, and the signal that triggers detection.
A failure mode without a detection bound is meaningful only after the
blast radius reaches its maximum. Missing → P3 citing C3.

**C4 — Mitigation pre-built when one-way + high blast radius.** When
the decision is one-way (per architect lens C4) and the blast radius
is cross-service or data-loss-possible, the ADR names a mitigation
that is committed to in advance — not "we'll figure it out" but a
concrete pre-built recovery path. Missing pre-built mitigation on
high-stakes one-way decisions → P3 citing C4.

**C5 — At-most-once vs at-least-once semantics declared.** When the
decision touches an operation that produces side effects (message
publish, payment, external API call, persistent state mutation), the
ADR declares whether the semantics are at-most-once or at-least-once
and why. A decision silent on semantics commits the system to one of
the two by accident, and the downstream implementer may pick the
other; the resulting inconsistency is invisible until a specific
failure pattern surfaces it. Missing → P3 citing C5.

## Beyond-checklist

If you find an architectural-failure-mode failure the checklist does not
cover, raise it as a P2/P3 finding citing `beyond-checklist:<principle-tag>`
and state which paragraph of the reasoning frame motivates it. Common
beyond-checklist cases at ADR: cascading-failure-potential (the decision
introduces a new failure that can propagate through the system), retry-
storm risk (the decision admits unbounded retries during a partial outage),
or saturation-curve unknown (the decision's behavior under load is not
characterised). Use sparingly. If more than 30% of your findings are
beyond-checklist, the playbook needs revision (file a follow-up).

## Scoring

| Outcome | lens_score |
|---|---|
| No findings; every check ran clean | 100 |
| P3 findings only; no checklist holes | 90-99 |
| 1-2 P2 findings against checks; no P1 | 80-89 |
| 3+ P2 against checks OR 1 P1 | 70-79 |
| P0 present OR systemic checklist failure | < 70 |
