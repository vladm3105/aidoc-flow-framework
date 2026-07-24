---
layer: 08_IPLAN
lens: chaos_engineer
weight: 8
agent: chaos-engineer
framework_spec_version: "0.38.0"
---
# chaos_engineer lens — IPLAN layer

## Reasoning frame

The chaos_engineer lens at IPLAN altitude (weight 8) evaluates
whether the rollback procedure has been exercised under realistic
conditions before the IPLAN is allowed to drive a production
cutover. A rollback that exists only on paper is a rollback that
has never been tested against the actual failure modes it claims
to recover from — and incident-time is the wrong moment to discover
that the documented procedure assumes a state the system no longer
holds, a tool that no longer exists, or a credential that has
since rotated. The chaos_engineer lens enforces a pre-cutover dress
rehearsal: rollback exercised in a non-prod environment, with
injected failure conditions, against the recovery-time bounds the
SPEC committed to.

Dress-rehearsal practice is the first concern. The rollback must
have been run end-to-end in a non-prod environment under conditions
that match production at the relevant scale: realistic data volume,
realistic load, realistic failure injection. A rehearsal against an
empty staging environment proves the procedure parses correctly but
not that it returns the system to a usable state under load.
Recovery-time assertions during rehearsal must reference the MTTR
bound the SPEC named, not just "rolled back successfully" — open-
ended success masks slow rollbacks that would breach SLO in
production.

Blast-radius reduction and stop-the-world criteria are the second
concern. The IPLAN must declare an explicit blast-radius reduction
(canary → partial rollout → full rollout) so that a failing change
affects the smallest possible population before it is caught. Stop-
the-world abort criteria must be documented: what condition triggers
immediate rollback regardless of the canary's progress through its
windows? Without a documented abort, the operator hesitates between
"give it more time" and "abort now" exactly when speed matters
most.

This lens does NOT evaluate: deploy-sequence reversibility
(tech_lead), topology invariance (architect), smoke-test /
observability emission (operator), cross-service compatibility
(integration_lead), or upstream-trace conformance (auditor). The
chaos_engineer lens is confined to rollback rehearsal evidence and
failure-mode preparation at IPLAN altitude.

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

**C1 — Rollback exercised in a non-prod environment with realistic
conditions.** The IPLAN documents a pre-cutover rollback rehearsal
run end-to-end in a non-prod environment with realistic data volume,
load, and failure injection. A paper rollback (documented but never
run) is not a rehearsal. Missing → P1 citing C1.

**C2 — Recovery-time assertions reference the SPEC's MTTR bound.**
The rehearsal asserts recovery within the MTTR bound the SPEC named,
not just "rolled back successfully." Open-ended recovery assertions
mask slow rollbacks that would breach SLO in production. Missing →
P2 citing C2.

**C3 — Failure-injection step exists in the pre-cutover dress
rehearsal.** The dress rehearsal injects at least one failure
condition (dependency timeout, partial network failure, pool
exhaustion) so the rollback is exercised against the kind of
condition that triggers it in production, not just against a clean
revert. Missing → P2 citing C3.

**C4 — Blast-radius reduction step declared.** The IPLAN declares a
blast-radius reduction sequence (canary → partial → full) so a
failing change affects the smallest possible population before it
is caught. Missing → P3 citing C4.

**C5 — Stop-the-world abort criteria documented.** The IPLAN
documents the conditions that trigger immediate rollback regardless
of canary progress (error-rate spike beyond threshold, dependency
outage, security alert). Without a documented abort, the operator
hesitates when speed matters most. Missing → P3 citing C5.

## Beyond-checklist

If you find a rollback-rehearsal or failure-preparation failure mode
the checklist does not cover, raise it as a P2/P3 finding citing
`beyond-checklist:<principle-tag>` and state which paragraph of the
reasoning frame motivates it. Common beyond-checklist cases at IPLAN
chaos altitude: a rollback documented step-by-step in the IPLAN but
never actually exercised end-to-end against a realistic environment
— a paper rehearsal that has never proven the documented procedure
parses against the real system; an MTTR claim made in the IPLAN
without a measurement to back it ("rollback completes well within
SLO") so the assertion cannot be falsified; a blast-radius reduction
sequence that skips a stage in the canary → partial → full
progression, exposing a larger population than necessary before the
gate is checked; and stop-the-world abort criteria stated as
"operator judgment" rather than a named, measurable condition. Use
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
