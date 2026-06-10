---
layer: 03_EARS
lens: tech_lead
weight: 25
agent: solutions-architect
framework_spec_version: "0.17.0"
---
# tech_lead lens — EARS layer

## Reasoning frame

The tech_lead lens at EARS altitude evaluates implementability: given the
trigger-response pairs written in EARS syntax, can an engineer implement
each rule unambiguously? At PRD altitude this lens evaluated whether §11
gates and numeric values were measurable in a product document — container
altitude, document-scoped assertions. At EARS altitude the question
sharpens: is each individual requirement line implementable as written,
without an engineer needing to make a product judgement call to fill in
gaps? At SPEC altitude downstream the tech_lead lens will descend to
component contracts, interface definitions, and fault-injection conditions.
EARS sits between those two: the rules must be specific enough to implement
but are still stated at system boundary altitude, not component altitude.

The implementability failure modes most common at EARS altitude are
dimensional ambiguity (a number without units), hand-waving in the
response clause (a system shall "handle appropriately"), overlapping
rules that produce conflicting obligations for the same system state, and
ADR-deferred placeholders that look like resolved requirements. This lens
applies calibrated checks for each pattern. Dimensional analysis is
non-negotiable: a bound of "500" without "ms" or "req/s" or "bytes" is
not a bound — it is a guess waiting to be argued over in code review.

This lens does NOT evaluate: EARS-pattern syntax compliance
(requirements_specialist), BDD traceability (qa_lead), failure-mode AC
completeness (chaos_engineer), or abuse-case coverage (security_engineer).
The lens is confined to whether each rule, taken individually, can be
implemented and validated by an engineer.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Triggers and responses are technically implementable.** Each EARS
line's trigger clause must name a detectable system event or state
transition, and the response clause must name a concrete, executable
action. Triggers such as "whenever necessary" or "under high load" are
not detectable without a threshold. Responses such as "behaves well",
"takes appropriate action", or "manages the situation" are not
implementable. An engineer must be able to write a passing test from
the line without additional product input. Missing → P2 finding citing C1.

**C2 — Overlapping rules on the same state flagged.** Where multiple
ubiquitous or state-driven rules govern the same system state or the
same combination of trigger + state, the document must resolve the
precedence explicitly. Overlapping rules create ambiguous behaviour at
implementation time — the engineer must choose which rule wins, which
is a product decision, not an engineering one. Missing → P2 finding
citing C2.

**C3 — Every numeric bound carries units.** Every numeric threshold or
capacity value in an EARS line must specify its unit: milliseconds (ms),
requests per second (req/s), bytes (B / KB / MB), percentage (%), count,
or an explicit ADR-deferred marker. A bare number without a unit is not
a bound — it cannot be validated in a test harness without guessing the
measurement context. Applies to latency targets, payload limits,
timeout values, rate limits, retry counts, and any other quantified
response element. Missing → P2 finding citing C3.

**C4 — ADR-deferred placeholders explicitly marked.** Where a numeric
bound, algorithm choice, or implementation mechanism has been deferred
to an ADR, the EARS line must carry an explicit deferral marker (e.g.,
`[ADR-deferred: ADR-NNN]`). Implicit deferral — a requirement that
reads as if resolved but depends on an un-linked ADR — creates a silent
assumption that survives review and surfaces as an integration surprise.
Missing → P3 finding citing C4.

**C5 — Terminology consistent with PRD glossary.** Every domain term
used in EARS lines must match the term defined in the PRD glossary
exactly. Term drift — using "user" in EARS where the PRD uses
"subscriber", or "timeout" where the PRD uses "deadline" — introduces
ambiguity at the boundary between the EARS document and downstream BDD
scenarios. Inconsistent terms must be resolved in the EARS document or
a glossary extension entry added. Missing → P3 finding citing C5.

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
