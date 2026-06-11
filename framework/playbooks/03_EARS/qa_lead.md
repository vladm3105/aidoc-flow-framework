---
layer: 03_EARS
lens: qa_lead
weight: 20
agent: test-architect
framework_spec_version: "0.20.0"
---
# qa_lead lens — EARS layer

## Reasoning frame

The qa_lead lens first enters the review crew at EARS altitude. At BRD
and PRD layers this lens is not present — those layers operate at
capability and feature altitude, where testability is a concern but not
yet the primary structural obligation. At EARS altitude, the
trigger-response structure of each EARS line is precisely the information
a BDD scenario needs: the trigger maps to a Given/When clause and the
response maps to a Then clause. The qa_lead lens validates that every
EARS line is written in a form that allows that mechanical translation
without interpretation. At BDD downstream the lens shifts role from
reviewer to author: it designs the scenarios that implement the
acceptance criteria the EARS layer defines.

Testability at EARS altitude has two dimensions. The first is per-line
testability: each trigger must be unambiguous enough to be reproduced in
a test harness, and each response must be verifiable by observable
output without human judgement. The second is coverage completeness: the
set of EARS lines in the document must be sufficient to cover every PRD
functional requirement — no PRD row can be left without at least one
corresponding EARS line, and therefore without at least one BDD scenario
downstream. Untested requirements are not requirements in practice; they
are aspirations.

This lens does NOT evaluate: EARS-pattern syntax (requirements_specialist),
numeric-unit completeness (tech_lead), failure-mode AC coverage
(chaos_engineer), or abuse-case enumeration (security_engineer). The
qa_lead lens targets testability per line and coverage completeness
across the document.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Every EARS line maps to ≥1 BDD scenario slot.** Each EARS line
must be annotated or cross-referenced to indicate the BDD scenario it
will become. This annotation may be a `@bdd:` tag, a scenario ID
placeholder (e.g., `[BDD-pending: feature/auth]`), or a reference in a
coverage matrix appended to the document. An EARS line with no BDD
traceability slot cannot be verified to have test coverage at the BDD
layer. Missing → P2 finding citing C1.

**C2 — Coverage matrix is present and bidirectional.** The EARS document
must include or reference a coverage matrix that maps each EARS line to
its PRD §9 row (upstream) and to its expected BDD scenario (downstream).
A unidirectional mapping — EARS to PRD only, or EARS to BDD only — is
insufficient. Bidirectional traceability is required to detect both
orphan EARS lines (no PRD parent) and uncovered PRD rows (no EARS
child). Missing → P3 finding citing C2.

**C3 — Triggers are free of ambiguity markers.** Trigger clauses in
event-driven and state-driven EARS lines must not contain words or
phrases that prevent deterministic test reproduction: "occasionally",
"sometimes", "if appropriate", "when needed", "periodically", "under
certain conditions", or equivalent hedges. Each trigger must be a
precisely reproducible condition. A test harness must be able to assert
that the trigger fired without relying on probabilistic or judgement-based
conditions. Missing → P2 finding citing C3.

**C4 — Unwanted patterns paired with positive counterparts.** Every
unwanted-behaviour EARS line (negative case: "If <condition>, the system
shall <safe response>") must be paired with a corresponding positive
EARS line that states normal-path behaviour under the same or related
conditions. An unwanted line with no positive counterpart leaves the
normal path unspecified and creates a test suite that validates only
failure behaviour without a correctness anchor. Missing → P2 finding
citing C4.

**C5 — Idempotency declared for stateful rules.** For any EARS line
whose response modifies persistent state (creates a record, updates a
counter, writes to a log, transitions a workflow state), the document
must declare whether the operation is idempotent and under what
conditions re-execution is safe. Stateful EARS lines without idempotency
declarations leave test-harness designers unable to determine whether
repeated trigger-fire in a test scenario is valid. Missing → P3 finding
citing C5.

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
