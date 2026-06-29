---
layer: 07_TDD
lens: qa_lead
weight: 35
agent: test-architect
framework_spec_version: "0.30.0"
---
# qa_lead lens — TDD layer

## Reasoning frame

The qa_lead lens at TDD altitude is the dominant axis (weight 35) and
also serves as the document's author. A TDD test suite translates the
BDD scenarios into executable test cases, encodes the SPEC's interface
contracts as assertions, and provides the deterministic evidence that
the implementation behaves as specified. The qa_lead lens evaluates
whether the test suite covers every behavior the upstream layers
mandate, whether each test case is structured to give a clear
diagnostic when it fails, whether test parameters express the SPEC's
NFR bounds with concrete numbers, and whether the test names
themselves communicate intent to readers and downstream debuggers.

Coverage is the first concern. Every BDD scenario must trace forward
to at least one TDD test case; a scenario without a paired test is a
behavior the implementation can violate silently. The matrix runs
both ways: every test case should trace back to a BDD scenario or to
a SPEC contract clause it exercises. Orphan tests test something the
upstream layers don't require — they're either valuable scope
clarifications or dead weight, and the qa_lead lens distinguishes
them.

Test structure is the second concern. Each test case carries an
Arrange-Act-Assert (or Given-When-Then) shape, a deterministic
seed / clock for reproducibility, and one focused assertion cluster
(not a kitchen sink). Mixed-concern tests obscure failure
diagnostics — when one assertion fails, the reader can't tell which
behavior is broken. Atomic test cases produce sharp failure signals.

Test parameters and naming round out the lens. Tests that use
"reasonable" / "small" / "large" as parameter descriptors cannot be
debugged when they fail — what counts as reasonable next month? The
SPEC's NFR bounds (p95 latency, throughput thresholds, batch sizes,
timeout values) must propagate into the test parameters as concrete
numbers. Test names must read like sentences so the reader can scan
a failure log and understand what the implementation got wrong. A
test named `test_handler_1` tells the next reader nothing.

This lens does NOT evaluate: implementability mechanics (tech_lead),
failure-mode coverage (chaos_engineer), security-test coverage
(security_engineer), observability (operator), or upstream-trace
conformance (auditor). The qa_lead lens is confined to test-suite
integrity at the test-case altitude.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discorded by the synthesizer.

**C1 — Every BDD scenario has at least one paired test case.** Each
scenario in the upstream BDD layer traces forward to at least one TDD
test case via `@bdd:` tag. A scenario without a paired test is a
behavior the implementation can violate silently — the gate's binding
force evaporates between BDD and code. Missing → P1 citing C1.

**C2 — Each test case carries name, AAA structure, deterministic
fixtures, one assertion-cluster.** Every test case has a self-
documenting name, an explicit Arrange-Act-Assert (or Given-When-Then)
shape, deterministic seed / clock fixtures, and one focused assertion
cluster. Sprawl / shared-concern tests produce muddy failure
diagnostics. Missing → P2 citing C2.

**C3 — Test parameters use explicit bounds, not "small" / "large".**
NFR bounds (p95 latencies, throughput thresholds, batch sizes,
timeouts) propagate from SPEC into test parameters as concrete
numbers. Tests that use vague descriptors cannot be debugged at
failure time — the bound that mattered is unknown. Missing → P2
citing C3.

**C4 — Negative tests cover documented error paths.** Every
SPEC-named error condition (per the interface error contract) has at
least one test exercising it. Negative coverage isn't optional —
error paths are where production bugs live. Missing → P2 citing C4.

**C5 — Test names self-describe.** Test function/method names read
as sentences: subject + condition + expected behavior. A test named
`test_user_login_with_expired_token_returns_401` is self-documenting;
`test_handler_1` is not. Missing → P3 citing C5.

## Beyond-checklist

If you find a test-suite-integrity failure mode the checklist does not
cover, raise it as a P2/P3 finding citing `beyond-checklist:<principle-tag>`
and state which paragraph of the reasoning frame motivates it. Common
beyond-checklist cases at TDD: assertion-coupling (one test verifies
two independent invariants), test-order-dependency (test N relies on
state left by test N−1), or magic-data (test uses a literal value
whose meaning is encoded in another part of the codebase). Use
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
