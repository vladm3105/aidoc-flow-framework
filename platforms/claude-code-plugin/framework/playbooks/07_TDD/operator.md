---
layer: 07_TDD
lens: operator
weight: 10
agent: devops-release-engineer
framework_spec_version: "0.41.1"
---
# operator lens — TDD layer

## Reasoning frame

The operator lens at TDD altitude evaluates whether the test suite
captures the operational properties that on-call engineers depend on:
SLO-relevant operations actually emit the metrics, logs, and traces
the SPEC named; one-way ADR decisions have smoke / canary / rollback
tests so a bad deploy can be caught and unwound; the test suite's
runtime is characterized so CI doesn't degrade silently; flake-rate
budgets are declared so noisy tests don't normalize; and CI failure
modes (network outage during a job, registry timeout pulling
dependencies) are tested. The operator lens turns the test suite
into a live operational signal source rather than a one-time
correctness checkpoint.

Observability emission verification is the first concern. SPEC's
NFRs and ADR's audit / security control choices name specific
metrics, logs, and traces that production code paths must emit. The
operator lens evaluates whether the test suite verifies these
emissions — not just that a test passes, but that the test actually
checks the metric was emitted with the right labels, the log was
written at the correct severity, the span was opened with the
expected name. Without this verification, the metric pipeline in
production can be silently broken and only the next incident reveals
it.

Smoke / canary / rollback tests are the second concern. Every ADR
that adopts a one-way decision (per the ADR's reversibility
classification) needs a smoke test that fires immediately after
deploy and a rollback procedure that's been tested in a non-prod
environment. Two-way and reversible decisions need rollback tests so
the toggle works under load. Without these, the operator's incident-
response playbook is invented at 03:00 under stress.

Suite-runtime characterization, flake-rate budgets, and CI failure-
mode tests round out the lens. Suite runtime should be measured per
test class (`pytest --durations=N` baseline); regressions should be
flagged before they normalize. Each test class declares its flake-
rate budget (acceptable false-failure rate); tests that consistently
exceed should be quarantined and root-caused, not muted. CI failure
modes (network blip, package registry timeout, secrets-vault
slowness) need at least one test that exercises the failure to
verify graceful behavior — these are the moments production
incidents start in the build path.

This lens does NOT evaluate: test-suite integrity (qa_lead),
test-engineering (tech_lead), failure-mode coverage (chaos_engineer),
security-test coverage (security_engineer), or upstream-trace
conformance (auditor). The operator lens is confined to operability
of the test suite + emission verification.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — Tests for SLO-relevant operations emit SPEC-named metrics/
logs/traces.** Each test exercising an operation whose SLO is named
in SPEC includes assertions on the operation's observability
emission: metric is recorded with the right labels, log is written
at the correct severity, span is opened with the expected name. Pass-
without-verifying-emission masks broken telemetry. Missing → P2
citing C1.

**C2 — Smoke / canary / rollback tests for each ADR-named one-way
decision.** Every one-way ADR decision (per ADR's reversibility
classification) has (a) a smoke test that runs at deploy time and
(b) a rollback procedure tested in a non-prod environment. Two-way
and reversible decisions still need rollback tests for the toggle.
Missing → P2 citing C2.

**C3 — Test-suite runtime characterized.** Each test class records a
runtime baseline (`pytest --durations=N` or equivalent); regressions
> 50% from baseline trigger investigation. Suites without baselines
degrade silently. Missing → P3 citing C3.

**C4 — Flake-rate budget declared per test class.** Each test class
declares its acceptable flake rate (% of CI runs that may legitimately
flake — usually 0% for unit, < 0.5% for integration). Tests
consistently exceeding budget are quarantined and root-caused — never
muted. Missing → P3 citing C4.

**C5 — CI failure-mode tests covered.** At least one test exercises
each CI failure mode that has caused outages in the past (network
blip mid-build, package registry timeout, secrets-vault slowness).
These failures start in the build path; testing them verifies graceful
behavior. Missing → P3 citing C5.

## Beyond-checklist

If you find an operability failure mode the checklist does not cover,
raise it as a P2/P3 finding citing `beyond-checklist:<principle-tag>`
and state which paragraph of the reasoning frame motivates it. Common
beyond-checklist cases at TDD: oncall-runbook-drift (test names
reference an old runbook path; on-call won't find it under the new
path), deploy-time-test-gap (tests pass at PR time but the canary
fails on first deploy because the test stack differs from prod), or
metric-cardinality-explosion (test asserts metric emission but does
not bound the cardinality of label values). Use sparingly. If more
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
