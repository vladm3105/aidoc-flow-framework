---
layer: 08_IPLAN
lens: operator
weight: 15
agent: devops-release-engineer
framework_spec_version: "0.26.0"
---
# operator lens — IPLAN layer

## Reasoning frame

The operator lens at IPLAN altitude (weight 15) evaluates whether the
deployment plan can be executed and monitored by an on-call engineer
under realistic conditions. An IPLAN that is technically correct but
unverifiable in flight is a procedure that produces blind deploys:
the operator runs the steps, but no signal tells them whether each
step succeeded, where the system is on the canary curve, or which
runbook applies when something starts to fail. The operator lens
catches the gaps between the plan's intent and the operator's view
during execution.

Smoke and canary verification is the first concern. Each cutover
step needs a smoke test that is named, executable, and has explicit
pass criteria — not "verify the service is healthy" but a specific
endpoint or metric check with a defined outcome. Canary phases need
explicit metric thresholds (latency, error rate, saturation) that
distinguish a healthy canary from one that should trigger rollback.
A canary without thresholds is a partial deploy waiting to be
forgotten.

Observability and runbook integration are the second concern. The
IPLAN must declare what the deploy itself emits (a deploy-event with
the new version pin, a dashboard URL the operator opens during the
canary window) so the cutover is visible alongside the system's
ongoing telemetry. The rollback procedure must reference the
SPEC-named one-way decisions explicitly, so the operator knows
which steps are reversible and which require a different recovery
path. The on-call playbook or runbook must be updated to cover the
new procedure; an out-of-date runbook is the operator's first
failure mode at 3am.

This lens does NOT evaluate: deploy-sequence reversibility
(tech_lead), topology invariance (architect), cross-service contract
pinning (integration_lead), upstream-trace conformance (auditor), or
rollback dress-rehearsal practice (chaos_engineer). The operator
lens is confined to smoke / canary verification, observability hooks,
and runbook integration.

### Subtype awareness (CLEANUP-PR-E item 17)

This lens reads `document_control.subtype` from the artifact and
adapts:

- **`code_build` subtype:** deploy concerns (rollback / smoke /
  canary / observability) are explicitly out of scope. This lens
  MAY return `lens_score: 100` with `findings: []` if every applicable
  code-build check passes; the no-findings rationale takes the form:
  `no_findings_rationale: "subtype: code_build — deploy concerns out
  of scope per CLEANUP-PR-E IPLAN sub-types contract."` This satisfies
  the no-findings-rationale rule (CLEANUP-PR-B item 8) — the rationale
  is the subtype declaration itself.
- **`deploy` or `combined` subtype:** all the checks below apply.
  Missing rollback / smoke / canary / observability sections that
  the subtype requires are blocking findings.
- **Missing subtype** (pre-0.19.1 IPLAN): defaults to `combined`.
  All checks apply.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check
citation are out-of-scope and discarded by the synthesizer.

**C1 — Smoke tests defined for each cutover step.** Each cutover
step names a smoke test (endpoint, query, command) with explicit
pass criteria. A step without a smoke test is a blind deploy; an
operator can run it and have no evidence the step landed correctly.
Missing → P1 citing C1.

**C2 — Canary metric thresholds explicit.** Canary phases declare
the metrics they watch (p95 latency, error rate, saturation, queue
depth) and the thresholds that distinguish a healthy canary from one
that triggers rollback. A canary without thresholds is a partial
deploy. Missing → P2 citing C2.

**C3 — Rollback procedure references SPEC-named one-way decisions.**
The rollback steps cite the SPEC's one-way decisions (irreversible
schema changes, durable side-effects, cross-region commits) so the
operator knows which steps cannot be undone by rerunning the
forward procedure in reverse. Missing → P2 citing C3.

**C4 — Observability hooks present.** The IPLAN declares the
deploy-event emission (with version pin and timestamp), the
dashboard URL to monitor during canary, and the log query that
filters for the new deploy. Missing observability hooks leave the
operator squinting at unfiltered telemetry. Missing → P3 citing C4.

**C5 — On-call playbook / runbook update referenced.** The IPLAN
names the on-call playbook or runbook section that must be updated
(or has been updated) to cover the new procedure, including the new
failure modes the change introduces. An out-of-date runbook is the
operator's first failure mode at 3am. Missing → P3 citing C5.

## Beyond-checklist

If you find a smoke / canary / observability failure mode the
checklist does not cover, raise it as a P2/P3 finding citing
`beyond-checklist:<principle-tag>` and state which paragraph of the
reasoning frame motivates it. Common beyond-checklist cases at IPLAN
operator altitude: a smoke test defined only as plain-prose
("verify the service is responding", "confirm the workers process a
job") with no measurable pass criterion the operator can check
against a fixed value; a canary metric whose rollback threshold is
implied by the surrounding narrative rather than declared as a
named bound; and a cutover step that emits no observable signal at
all — no deploy event, no metric tag, no log marker — so the
operator cannot retroactively answer "when did step N actually
land?" during incident review. Use sparingly. If more than 30% of
your findings are beyond-checklist, the playbook needs revision
(file a follow-up).

## Scoring

| Outcome | lens_score |
|---|---|
| No findings; every check ran clean | 100 |
| P3 findings only; no checklist holes | 90-99 |
| 1-2 P2 findings against checks; no P1 | 80-89 |
| 3+ P2 against checks OR 1 P1 | 70-79 |
| P0 present OR systemic checklist failure | < 70 |
