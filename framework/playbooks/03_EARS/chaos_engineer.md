---
layer: 03_EARS
lens: chaos_engineer
weight: 12
agent: chaos-engineer
framework_spec_version: "0.35.0"
---
# chaos_engineer lens — EARS layer

## Reasoning frame

The chaos_engineer lens at EARS altitude verifies failure-mode acceptance
criteria completeness. At PRD altitude this lens evaluated §13 risk-row
symmetry: does every risk row have a user-facing surface, an AC gate, and
a non-functional anchor? At EARS altitude the question advances: for each
failure mode the PRD named, does the EARS document contain at least one
unwanted-behaviour EARS line that specifies the system's response? A PRD
that names a failure mode without a downstream EARS line for it has
committed the system to handling that failure without specifying what
"handling" means — the obligation is invisible to BDD authors, testers,
and implementers.

The chaos_engineer lens at EARS altitude carries a heavier weight than
the security_engineer lens (12 > 8) because failure-mode acceptance
criteria are more frequently absent than abuse-case ACs in practice.
Engineers tend to write happy-path EARS lines fluently and deprioritise
the unwanted patterns that encode failure behaviour. The result is an
EARS document that produces a test suite covering only successful paths,
leaving failure paths untested until they surface in production. This
lens forces parity between happy-path and failure-path requirements at
the most actionable point: before BDD scenario design begins.

At SPEC altitude downstream the chaos_engineer lens will descend further
to component-level fault injection: which component owns detection,
isolation, and recovery, and what are the injected fault conditions. At
EARS the lens does not ask those questions — it only validates that every
PRD-declared failure mode has an EARS-layer obligation.

This lens does NOT evaluate: EARS-pattern syntax (requirements_specialist),
per-trigger implementability (tech_lead), BDD coverage mapping (qa_lead),
or input-validation and auth rules (security_engineer). The lens is
confined to failure-mode AC completeness against the PRD §13 inventory.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Every PRD §13 failure mode has an unwanted-behaviour EARS line.**
For each failure mode (risk row) named in PRD §13, the EARS document
must contain at least one unwanted-pattern line ("If <failure condition>,
the system shall <bounded safe response>") that specifies the observable
system behaviour. A PRD risk row without a corresponding EARS unwanted
line leaves that failure mode outside the testable requirements set.
Missing → P2 finding citing C1.

**C2 — Timeout-vs-deadline coupling explicit.** Every EARS line that
names a timeout, wait period, or deadline must state whether the bound
is a timeout (the operation is abandoned and an error response returned)
or a deadline (the operation is continued but a warning or SLO breach is
recorded). Unbounded waits — EARS lines that describe waiting behaviour
without a named maximum duration — are not implementable. A line that
says "the system shall wait for the upstream response" without a numeric
bound is a specification of indefinite blocking. Missing → P2 finding
citing C2.

**C3 — Retry budgets bounded.** Any EARS line that includes a retry,
re-attempt, or backoff obligation must specify a maximum retry count or
maximum total retry duration. Unbounded retry loops convert transient
failures into sustained resource exhaustion. "The system shall retry
until success" is not an EARS requirement — it is an infinite loop.
Acceptable bounds: a fixed count ("at most 3 retries"), a time ceiling
("retry for up to 30 s"), or an explicit ADR-deferred marker. Missing
→ P2 finding citing C3.

**C4 — Cascading-failure boundary stated.** Where the EARS document
specifies failure behaviour for a system that depends on multiple
upstream services or components, at least one EARS line must name the
firebreak: the point at which failure propagation is stopped and a local
safe response is returned. A failure-mode EARS line that says "if the
cache is unavailable, fall back to the database" without naming what
happens if the database is also unavailable describes only one failure
depth. Systemic failure boundary must be explicit. Missing → P3 finding
citing C4.

**C5 — Recovery rules paired with detection rules.** Every EARS line
that specifies a recovery action ("when the circuit breaker resets, the
system shall resume normal processing") must be paired with a
corresponding detection rule ("if the upstream error rate exceeds X%
for Y seconds, the system shall open the circuit breaker"). Detection
without recovery leaves the system in a known-bad state indefinitely.
Recovery without detection leaves the trigger for recovery unspecified.
Missing → P2 finding citing C5.

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
