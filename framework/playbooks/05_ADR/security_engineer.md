---
layer: 05_ADR
lens: security_engineer
weight: 12
agent: security-engineer
framework_spec_version: "0.34.1"
---
# security_engineer lens — ADR layer

## Reasoning frame

The security_engineer lens at ADR altitude carries the dominant weight
in the security/reliability split (12 > chaos's 8) because ADRs are the
layer at which security commitments are first codified. By the time a
decision reaches SPEC the trust boundaries, authentication choices,
authorization model, and crypto primitives are fixed; the SPEC merely
encodes them. An ADR that crosses a trust boundary silently, that
adopts an authentication mechanism without specifying which identities
it admits, that names "encryption" without naming the algorithm or
key-management model, or that introduces a security control without
declaring failure-closed vs failure-open behavior commits the system
to a security posture by omission.

Trust boundaries are the central concept. Every distributed system has
boundaries — process, network, tenant, role — across which data and
authority flow. A boundary crossing changes the threat model: the
adversary's capabilities differ on each side, the controls available
differ on each side, and the consequence of a compromise differs on
each side. An ADR that introduces a new boundary crossing without
naming the boundary leaves the threat model implicit and untestable.
At minimum the ADR must name the boundary and state how identity is
preserved or translated across it.

AuthN (who) and AuthZ (what) are separate concerns that frequently get
conflated. AuthN establishes identity; AuthZ decides what an identity
may do. An ADR that says "we will use OAuth" specifies an authentication
protocol but leaves authorization unstated — and an OAuth token alone
authorizes nothing. The lens flags decisions that touch either axis
without naming both.

Crypto choices and threat models are the remaining pillars. An ADR
that hand-waves "encrypt at rest" without naming the algorithm, key
length, key-management model, and key-rotation cadence commits to a
posture that may not survive scrutiny six months later. A security
control without a named threat model defends against nothing in
particular — the lens forces decisions to state which threats they
mitigate and (crucially) which they do not.

This lens does NOT evaluate: decision integrity (architect),
implementability mechanics (tech_lead), rollback procedure (operator),
upstream-tag conformance (auditor), or decision-failure-mode coverage
(chaos_engineer). The security_engineer lens is confined to trust-
boundary, authn/authz, crypto, and threat-model rigor.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Trust boundaries explicitly named when crossed.** When the decision
introduces or modifies a boundary crossing (process / network / tenant /
role), the ADR names the boundary and states how identity is preserved or
translated across it. A boundary crossed silently leaves the threat model
implicit and untestable; the SPEC author has no signal that authorization
checks belong at this point. Crossed silently → P1 citing C1.

**C2 — AuthN choice and AuthZ choice both called out.** When the decision
touches authentication or authorization, the ADR names both: who the
system will accept as a valid identity (AuthN) and what those identities
are permitted to do (AuthZ). An ADR that names only the authentication
protocol leaves authorization unstated, which is operationally equivalent
to authorize-all. Missing either axis on a decision that touches either →
P1 citing C2.

**C3 — Crypto algorithm + key-management choice specified.** When the
decision touches encryption (data-at-rest, data-in-transit, signing,
hashing), the ADR names the algorithm, key length where applicable, the
key-management model (KMS / vault / static / per-tenant), and the rotation
cadence. A hand-wave like "we will encrypt at rest" commits the system to
a posture that cannot be audited or tested. Hand-wave → P2 citing C3.

**C4 — Threat model named (in-scope vs out-of-scope threats).** When the
decision introduces a security control, the ADR names which threat the
control mitigates and (crucially) which threats it does NOT mitigate. A
control without a named threat defends against nothing in particular,
and a control without out-of-scope threats invites scope creep — future
readers assume it covers more than it does. Missing → P2 citing C4.

**C5 — Failure-closed vs failure-open behavior stated.** When the decision
touches a security control (rate limit, auth check, secret lookup, audit
log), the ADR states whether the control fails closed (deny when broken)
or fails open (allow when broken) and gives the rationale. Failure-mode
behavior is a security primitive — a system that fails open under control
unavailability degrades from a defended posture to an undefended posture
during the most chaotic moments. Missing → P2 citing C5.

## Beyond-checklist

If you find a security-posture failure mode the checklist does not cover,
raise it as a P2/P3 finding citing `beyond-checklist:<principle-tag>` and
state which paragraph of the reasoning frame motivates it. Common
beyond-checklist cases at ADR: blast-radius widening (the decision
increases the radius of a compromise without compensating control),
insecure default (the decision adopts a configuration whose insecure mode
is the default), or audit-evidence gap (the decision affects a regulated
flow but does not preserve the evidence trail). Use sparingly. If more
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
