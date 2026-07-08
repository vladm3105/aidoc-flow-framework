---
layer: 07_TDD
lens: tech_lead
weight: 25
agent: solutions-architect
framework_spec_version: "0.34.2"
---
# tech_lead lens — TDD layer

## Reasoning frame

The tech_lead lens at TDD altitude evaluates whether the test suite
binds correctly to the architecture and is engineered to remain
reliable over time. A test suite that exercises internal class names
instead of SPEC-named interface contracts drifts the moment the
internals change. A suite with shared mutable fixtures has order
dependencies that hide bugs and surface false failures. A suite that
uses real wall-clock sleeps to test concurrency is flaky from the
moment it ships. The tech_lead lens enforces test engineering
discipline so the suite remains a stable safety net rather than a
liability.

Interface-contract binding is the first concern. Tests should bind
to the names the SPEC's interface catalog declares — request shapes,
response shapes, error contracts, exposed operations. Tests that
reach into private class names or implementation-internal symbols
break the contract: refactoring the implementation should not require
test changes unless the SPEC changes. A suite where each refactor
rewrites tests indicates internals-binding, not contract-binding.

Fixture independence is the second concern. Every test must be
runnable in isolation: no test should depend on residue from another
test (shared in-memory state, leftover database rows, lingering
processes). Idempotent setup and teardown are the price of admission;
tests that pass only when run in a specific order are not engineered
tests, they are coincidences. Most CI flakes trace to fixture
leakage.

Concurrency and dependency-mocking conventions round out the lens.
Concurrency tests must use deterministic primitives (event signals,
semaphore counts, controllable schedulers) — never `sleep(2)` to
"wait for something to happen." Tests using a sleep race with the
event they're trying to detect; they pass on a fast machine and fail
on a slow CI runner. External-dependency tests must use ONE mocking
strategy consistent across the project (all mocks, or all spies, or
all in-memory fakes); mixed strategies make the test suite hard to
reason about. Retry-semantics tests must actually exercise
idempotency — call the operation twice with the same input and assert
identical observable state — not just count the retry attempts.

This lens does NOT evaluate: test-suite integrity (qa_lead),
failure-mode test coverage (chaos_engineer), security-test coverage
(security_engineer), observability emission (operator), or
upstream-trace conformance (auditor). The tech_lead lens is confined
to test engineering and stability.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Tests bind to SPEC interface contracts, not internal class
names.** Each test exercises a name that appears in the SPEC's
interface catalog (request shape, response shape, error contract,
exposed operation). Tests that reach into implementation-private
symbols drift on refactor. Drift / wrong-binding → P1 citing C1.

**C2 — Fixture setup/teardown idempotent + isolated.** Every test
runs in isolation: no shared mutable in-memory state, no leftover
database rows, no lingering processes. Setup is idempotent; teardown
restores baseline. Tests passing only in a specific order are not
engineered tests. Missing → P2 citing C2.

**C3 — Concurrency tests use deterministic primitives.** Any test
exercising concurrent behavior uses controllable signals (event
flags, semaphores, controllable schedulers) — never `sleep(N)` /
real wall-clock waits to detect events. Sleep-races are flaky from
day one. Sleep-based concurrency tests → P2 citing C3.

**C4 — External-dependency mocking strategy consistent.** All
external-dependency tests use one mocking strategy (all mocks, or
all spies, or all in-memory fakes) per the project's convention.
Mixed strategies make the suite hard to reason about and tend to
mask real integration bugs. Mixed → P3 citing C4.

**C5 — Retry-semantics tests exercise idempotency.** Tests for
retry-bearing operations actually call the operation twice and assert
identical observable state, not just count retry attempts.
Count-only retry tests pass when the implementation is non-idempotent
(a serious production hazard). Missing → P3 citing C5.

## Beyond-checklist

If you find a test-engineering or stability failure mode the checklist
does not cover, raise it as a P2/P3 finding citing
`beyond-checklist:<principle-tag>` and state which paragraph of the
reasoning frame motivates it. Common beyond-checklist cases at TDD:
hidden-shared-mock (a mock registered globally affects unrelated
tests), tight-coupling-via-test (test asserts implementation
sequence rather than observable outcome), or environment-leakage
(test depends on environment variable that may not be set in CI).
Use sparingly. If more than 30% of your findings are beyond-checklist,
the playbook needs revision (file a follow-up).

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
