---
layer: 04_BDD
lens: security_engineer
weight: 6
agent: security-engineer
framework_spec_version: "0.23.0"
---
# security_engineer lens — BDD layer

## Reasoning frame

The security_engineer lens at BDD altitude translates abuse-case EARS lines
into executable security scenarios. At EARS altitude this lens validated that
every abuse case discovered at PRD altitude had a corresponding pair of EARS
lines: one specifying the system's detection or rejection behaviour, and one
specifying normal behaviour under the same access path. At BDD altitude the
obligation advances: each abuse-case EARS line must become at least one
Gherkin scenario that exercises the abuse condition and asserts the specified
security response.

Security scenarios at BDD altitude have two planes. The first is access-control
correctness: scenarios must cover both the authorised path (authenticated,
permitted request succeeds) and the denied path (unauthenticated or
unpermitted request is rejected with the specified status and no data leak).
A security scenario that only exercises the authorised path verifies
functionality, not security. A scenario that only exercises the denied path
verifies rejection behaviour without confirming that legitimate access still
works. Both paths are required. The second plane is input validation: every
endpoint that accepts external input must have at least one scenario that
exercises a malformed, oversized, or structurally invalid input and asserts
the rejection response.

At PRD altitude this lens focused on abuse-case discovery: identifying the
attack surfaces and threat actors. At EARS altitude it validated that each
discovery produced a specification. At BDD altitude it validates that each
specification has an executable test. This lens does NOT evaluate: EARS
coverage completeness (qa_lead), step-definition implementability (tech_lead),
failure-mode scenario coverage (chaos_engineer), observability hooks (operator),
or ID and lint conformance (auditor).

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Every abuse-case EARS line has a security scenario.** For each
abuse-case unwanted-behaviour EARS line (those specifying system response to
unauthorised access, malformed input, injection attempt, or other adversarial
condition), the BDD layer must contain at least one scenario that exercises
that abuse condition and asserts the specified response. An abuse-case EARS
line without a corresponding scenario leaves the security control untested.
Missing → P2 citing C1.

**C2 — AuthN/authZ scenarios cover both happy and denied paths.** For every
authentication or authorisation control in the system, the scenario set must
include both an authorised-access scenario (valid credentials, permitted role,
correct scope — system grants access) and a denied-access scenario (invalid
credentials, insufficient role, expired token — system rejects with the
correct HTTP status and no data in the response body). Missing → P2 citing C2.

**C3 — Input-fuzzing scenarios for every accepting endpoint.** For every
system endpoint, API route, or message-consumer path that accepts external
input, the scenario set must include at least one input-fuzzing scenario that
submits structurally invalid data (empty body, oversized payload, invalid
encoding, injection-pattern strings) and asserts the rejection response and
absence of server-side error disclosure. Missing → P3 citing C3.

**C4 — Audit-log assertions present where rules require them.** For every
EARS line that specifies an audit-log or event-recording obligation as part
of a security response (access denial recorded, privilege escalation attempt
logged, sensitive-data access noted), the corresponding BDD scenario must
include a Then step that asserts the audit record was created with the
required fields. Missing → P3 citing C4.

**C5 — Regulatory-compliance scenarios where applicable.** Where the EARS
document names a regulatory obligation (PCI-DSS, GDPR, HIPAA, SOC 2 control,
or equivalent), the BDD layer must contain at least one scenario per named
obligation that asserts the compliance behaviour. Compliance obligations
named in EARS without BDD scenarios cannot be evidenced during an audit.
Missing → P3 citing C5.

## Beyond-checklist

If you find a layer-specific failure mode the checklist does not cover, raise
it as a P2/P3 finding citing `beyond-checklist:<principle-tag>` and state
which paragraph of the reasoning frame motivates it. Use sparingly. If
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
