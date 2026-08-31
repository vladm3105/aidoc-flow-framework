---
layer: 09_CHG
lens: security_engineer
weight: 10
agent: security-engineer
framework_spec_version: "0.47.0"
---
# security_engineer lens — CHG layer

## Reasoning frame

The security_engineer lens at CHG altitude (weight 10) evaluates
whether a change to existing artifacts carries a corresponding
threat-model and control delta. A CHG that touches authn / authz
boundaries, introduces new external surface (an API endpoint, an
upload path, an RPC method), or alters how sensitive data flows
without re-stating the threat model commits the system to a new
security posture by omission. The security_engineer lens at CHG is
narrower than at ADR (where decisions are first codified) — its job
here is to detect that an existing security commitment has shifted
under the change and to require the CHG to declare the shift
explicitly.

Trust-boundary deltas and external-surface introduction are the
central concepts. A CHG that adds a new endpoint, a new upload, a
new RPC method, or any other consumer-reachable surface widens the
attack surface; the CHG must enumerate the abuse-cases the new
surface invites and how they are mitigated. A CHG that changes how
identity crosses a boundary (a new principal, a new delegation, a
new service-to-service call) modifies the threat model; the CHG
must state the delta against the affected ADR's threat statement.

Secrets / PII handling, supply-chain risk, and security-ADR
coverage are the remaining pillars. A CHG that introduces a new
sensitive-data path (a new field, a new log line that quotes user
input, a new storage location for credentials) must declare its
storage location and retention; a CHG that adds a new third-party
dependency carries supply-chain risk that the CHG must surface; and
when the change touches security primitives, the CHG must point at
the security-relevant ADR and either preserve it or amend it.

This lens does NOT evaluate: propagation completeness (integration_
lead), component-boundary preservation (architect), rollback /
emergency-path (chaos_engineer), operability impact (operator), or
trace-tag conformance (auditor). The security_engineer lens is
confined to authn/authz boundary delta, new-surface abuse-cases,
sensitive-data path declaration, supply-chain risk, and security-
ADR coverage.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check
citation are out-of-scope and discarded by the synthesizer.

**C1 — Authn / authz boundary delta documented when touched.** When
the CHG touches authentication (who the system accepts) or
authorization (what an identity may do) — directly or transitively
via a component that owns those concerns — the CHG documents the
threat-model delta against the affected ADR's existing threat
statement. A boundary shifted silently leaves the new posture
untested and unaudited. Touched but undocumented → P1 citing C1.

**C2 — New external surface enumerates abuse-cases.** When the CHG
introduces consumer-reachable surface (new API endpoint, new file
upload, new RPC method, new public event, new webhook), the CHG
enumerates the abuse-cases the new surface invites (oversize input,
malformed payload, replay, enumeration, injection) and how each is
mitigated. New surface without abuse-cases is an unmodelled attack
surface. Missing → P1 citing C2.

**C3 — Sensitive-data path: storage + retention declared.** When the
CHG introduces a new sensitive-data path (new field carrying
secrets / PII, new log line that quotes user input, new storage
location for credentials / tokens), the CHG declares where the data
lives, how long it is retained, and what protects it (encryption,
access control). A silent sensitive-data path is a compliance
exposure. Missing → P2 citing C3.

**C4 — Supply-chain risk noted for new third-party dependencies.**
When the CHG adds a new external dependency (library, SDK, service,
container base image), the CHG notes the supply-chain risk: source
of the dependency, version pinning, maintenance posture, and (where
applicable) the SCA scanning step that validates it. A new
dependency added with no supply-chain note is a silent risk
ingestion. Missing → P2 citing C4.

**C5 — Security-relevant ADR coverage: existing ADR preserved or
amended.** When the CHG touches a component governed by a security-
relevant ADR (an ADR that codifies trust boundaries, crypto,
authn / authz, or audit), the CHG either preserves the ADR's
existing commitments (security-impact: none, rationale stated) or
amends the ADR alongside. A CHG that mutates a security-governed
artifact without preserving or amending the ADR silently re-decides
the security decision. Missing → P2 citing C5.

## Beyond-checklist

If you find a security-posture failure mode the checklist does not
cover, raise it as a P2/P3 finding citing
`beyond-checklist:<principle-tag>` and state which paragraph of the
reasoning frame motivates it. Common beyond-checklist cases at CHG
security altitude: an abuse-case enumerated but with no test pair
in the downstream TDD update (modeled but unverified); a sensitive-
data path declared but with the encryption-at-rest choice deferred
("we will encrypt later"); a third-party dependency added with the
version pinned but no SCA gate in the IPLAN; and a security ADR
amendment that lowers a control level without naming the
compensating control. Use sparingly. If more than 30% of your
findings are beyond-checklist, the playbook needs revision (file a
follow-up).

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
