---
layer: 07_TDD
lens: security_engineer
weight: 10
agent: security-engineer
framework_spec_version: "0.51.0"
---
# security_engineer lens — TDD layer

## Reasoning frame

The security_engineer lens at TDD altitude carries the dominant
co-ownership of SECTEST (security test) coverage. At ADR security was
the architectural commitment; at SPEC it was the control
implementation; at TDD it is the executable proof that the controls
actually fire under the conditions that should trigger them. A test
suite without security tests doesn't tell you anything about the
security posture — every BDD authn / authz / abuse-case scenario
must have a paired TDD test, every public interface must have an
input-fuzzing test, every audit-event emission must be verified
field-by-field, every crypto operation must be tested for algorithm
correctness, and every failure-closed default must fire under
control-unavailability.

BDD-to-TDD security-scenario pairing is the first concern. The BDD
layer enumerates authn happy / denied paths, authz role-decision
paths, abuse-case rejection paths, and audit-event emission paths.
The TDD layer must encode each as an executable test — without that,
the controls only exist in prose. The pairing must be 1:1 or more
(one BDD scenario may decompose into multiple TDD tests when the
implementation surface is wide).

Input-fuzzing coverage is the second concern. Every public interface
(any operation that crosses a trust boundary, including the system's
external API surface and each component boundary in the SPEC
topology) must have at least one fuzzing-style test that exercises
malformed, oversized, encoding-edge, and injection-attempt inputs.
Public interfaces without fuzzing coverage are where unconstrained
input bugs land in production.

Audit-event field-set, crypto-correctness, and failure-closed defaults
round out the lens. Audit-event tests must assert the field set
(subject, action, resource, decision, timestamp, context) and not
merely the fact of emission; missing fields make audit logs
unreviewable. Crypto tests must assert algorithm + mode + key
handling, not just that the operation completed; "encrypt at rest"
tests that don't verify AES-256-GCM is actually used pass even when
the implementation silently downgraded to AES-128-ECB. Failure-closed
default tests must fire under control-unavailability — that's the
moment defenses matter most, and the moment most silently fail open.

This lens does NOT evaluate: test-suite integrity (qa_lead),
test-engineering (tech_lead), failure-mode coverage (chaos_engineer),
observability emission (operator), or upstream-trace conformance
(auditor). The security_engineer lens is confined to security-test
coverage and crypto / authz / audit correctness.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Every BDD authn/authz/abuse-case scenario has a paired TDD
security test.** Authn happy + denied paths, authz role-decision
paths, abuse-case rejection paths, audit-event emission paths from
the upstream BDD layer trace forward to executable TDD tests.
Without pairing, the controls live only in prose. Missing → P1
citing C1.

**C2 — Input-fuzzing tests cover every public interface.** Every
operation that crosses a trust boundary (external API surface +
each component boundary in SPEC's integration topology) has at
least one fuzzing-style test covering malformed / oversized /
encoding-edge / injection-attempt inputs. Missing → P2 citing C2.

**C3 — Audit-event tests verify field set, not just emission.**
Tests for security-relevant operations assert the full audit-event
field set (subject, action, resource, decision, timestamp, context)
— not merely that an event was emitted. Field-incomplete audit logs
are unreviewable post-incident. Missing → P2 citing C3.

**C4 — Crypto tests assert algorithm + mode + key handling.** Tests
for crypto-touching operations verify the SPEC-named algorithm /
mode / key-management primitive is actually used — not just that the
operation completed. Silent crypto downgrades (e.g. SPEC says
AES-256-GCM, implementation uses AES-128-CBC) pass call-success
tests but fail correctness. Missing → P3 citing C4.

**C5 — Failure-closed default tests fire under control
unavailability.** Tests for security controls (authz lookup, rate
limit, audit logger) include a case where the control is
unavailable, and assert the system fails closed (deny) per SPEC's
commitment. Without this test, the implementation can silently fail
open and only the next incident reveals it. Missing → P3 citing C5.

## Beyond-checklist

If you find a security-test failure mode the checklist does not cover,
raise it as a P2/P3 finding citing `beyond-checklist:<principle-tag>`
and state which paragraph of the reasoning frame motivates it. Common
beyond-checklist cases at TDD: secret-leak-in-test-output (test
prints secret material to stdout / logs / fixture files), test-mode-
bypass (implementation has a "test mode" code path that skips
security controls), or default-credential-coverage (no test exercises
the system with default credentials to verify they don't grant
access). Use sparingly. If more than 30% of your findings are
beyond-checklist, the playbook needs revision (file a follow-up).

## Scoring

| Outcome | lens_score |
|---|---|
| No findings; every check ran clean | 100 |
| P3 findings only; no checklist holes | 90-99 |
| 1-2 P2 findings against checks; no P1 | 80-89 |
| 3+ P2 against checks OR 1 P1 | 70-79 |
| P0 present OR systemic checklist failure | < 70 |
