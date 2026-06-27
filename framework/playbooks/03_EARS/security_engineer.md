---
layer: 03_EARS
lens: security_engineer
weight: 8
agent: security-engineer
framework_spec_version: "0.23.1"
---
# security_engineer lens — EARS layer

## Reasoning frame

The security_engineer lens at EARS altitude verifies that every abuse
case named in the PRD has a corresponding EARS line pair: an event-driven
positive rule that specifies the control behaviour, and an unwanted-
behaviour rule that specifies the system's response when the abuse
condition is detected. At PRD altitude this lens performed abuse-case
discovery — enumerating what could go wrong and capturing the system's
assumptions about threat actors and trust boundaries. At EARS altitude
the lens no longer discovers; it validates that every PRD-identified
abuse case has been translated into testable EARS obligations.

The structural requirement is a line pair, not a single line, because
security controls require both a normal-path obligation and a failure-path
obligation. An event-driven rule ("When the user submits authentication
credentials, the system shall validate them against the credential store")
without a paired unwanted rule ("If the credential validation fails more
than N times within M seconds, the system shall lock the account and
return HTTP 429") leaves the abuse case without a testable response. The
paired-line requirement is the EARS-layer encoding of defence-in-depth:
every control has both a specified behaviour and a specified failure
behaviour.

At SPEC altitude downstream the security_engineer lens will descend to
per-component trust boundaries, token validation logic, and
privilege-separation contracts. At EARS the lens does not examine
component internals — it validates only that the system-boundary security
obligations are present and structured.

This lens does NOT evaluate: EARS-pattern syntax (requirements_specialist),
implementability of the control mechanism (tech_lead), BDD coverage
mapping (qa_lead), or failure-mode AC completeness for non-security
scenarios (chaos_engineer). The lens is confined to abuse-case
traceability and security-control structural completeness.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Every PRD abuse case has an EARS line pair.** For each abuse case
identified in the PRD, the EARS document must contain at minimum two
lines: (a) an event-driven rule specifying the control behaviour for
that abuse vector, and (b) an unwanted-pattern rule specifying the
system's response when the abuse condition is detected or the control
is triggered. A PRD abuse case represented by only one EARS line — or
by no EARS line — is not a testable security requirement. Missing →
P1 finding citing C1.

**C2 — Input-validation rules cover all submission paths.** For every
path in the EARS document through which external data enters the system
(form submission, API request body, query parameter, file upload,
header value), at least one EARS line must specify the validation rule
applied to that input. "The system shall accept the request" is not a
validation rule. Acceptable forms: enumerated accepted formats, stated
maximum lengths, named schema reference, or an explicit ADR-deferred
marker with a validation plan reference. Missing → P2 finding citing C2.

**C3 — Rate-limiting rules carry explicit bounds.** Every EARS line that
describes a rate-limiting, throttling, or quota-enforcement control
must state the numeric bound: maximum requests per time window, maximum
concurrent sessions, or maximum payload size per interval. A rate-limit
EARS line without a bound ("the system shall enforce rate limits") is
not implementable or testable. Acceptable deferral: `[ADR-deferred:
ADR-NNN]` with a named ADR that will specify the bound. Missing →
P2 finding citing C3.

**C4 — Audit-log rules cover authentication and authorization decisions.**
Every EARS line that specifies an authentication event (login, token
issuance, token refresh, logout) or an authorization decision (access
granted, access denied, privilege escalation) must be paired with or
reference an EARS line that specifies the audit-log entry produced.
Authentication and authorization events without audit-log obligations
are not compliant with standard security traceability requirements.
Missing → P3 finding citing C4.

**C5 — Data-classification constraints matched to access rules.** Where
the PRD names data classifications (PII, confidential, restricted,
internal, public), the EARS document must contain at least one EARS
line per classification level that specifies the access control rule
applied to data of that classification. A system that handles classified
data without EARS-layer access rules for each classification level has
unspecified security obligations at the implementation layer. Missing
→ P2 finding citing C5.

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
