---
layer: 02_PRD
lens: chaos_engineer
weight: 8
agent: chaos-engineer
framework_spec_version: "0.16.1"
---
# chaos_engineer lens — PRD layer

## Reasoning frame

The chaos_engineer lens at PRD altitude evaluates failure-path acceptance
criteria: does the PRD commit to how the system behaves when components fail,
capacity is exhausted, or dependent services become unreachable? At BRD altitude
this lens confirmed that the business declared its resilience posture. At PRD
altitude the lens asks a harder question: are those commitments translated into
verifiable, bounded acceptance criteria that the QA and EARS layers can inherit
without making reliability assumptions themselves?

The PRD chaos_engineer lens applies three calibrated patterns derived from
the PRD-01 live cascade findings (CE-1, CE-2, CE-3): §13 risk-row symmetry,
bounded degraded mode, and failure-branch gating. These are not speculative —
each was a confirmed gap in a reviewed PRD that the synthesizer's earlier pass
did not surface. The checks encode the exact failure signatures so the same
gaps cannot recur across future PRDs.

This lens does NOT evaluate: BRD-authorization of gates (product_owner),
structural diagram coherence (architect), input-domain bounds (tech_lead),
trust-boundary authorization (security_engineer), or ID conformance (auditor).
The lens is confined to failure-path coverage: does every risk have a
user-facing surface, a gate, a mitigation anchor, and a bound?

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check citation
are out-of-scope and discarded by the synthesizer.

**C1 — §13 risk-row symmetry (CE-1 calibration).** Every risk row in §13
must have three anchors: (a) a §10 user-facing surface that exposes this risk
to users, (b) a §11 AC gate that verifies the mitigation is in place, and (c)
a §12 non-functional anchor (NFR, SLO, or ADR deferral). A risk row that
names a mitigation but lacks any of the three anchors is structurally
incomplete — the PRD-01 pool-exhaustion risk had §13 text and §10 surface but
no §11 gate, which let the risk pass review undetected. Missing → P2 finding
citing C1.

**C2 — Bounded degraded mode (CE-3 calibration).** Every degraded-mode
commitment in the PRD (any prose of the form "the system falls back to…",
"returns degraded response when…", or "operates in limited mode") must carry
a numeric bound or an explicit ADR-deferral marker. Unbounded degraded-mode
prose — such as "returns 5xx but continues accepting requests" without a
lookup-deadline or timeout value — is not implementable or testable. Missing
→ P2 finding citing C2.

**C3 — Failure-branch gating (CE-2 calibration).** Every §11 control AC that
verifies a mitigation or protection is in place must also include a gate for
the control's failure mode: what happens when the control itself fails or the
protected resource is unreachable. A gate that only validates "control in
place" (happy path) leaves the failure branch unverified — the PRD-01
reputation-source unreachable scenario was specified in §12 and §10 but §11
only validated the happy-path presence of the control. Missing → P2 finding
citing C3.

**C4 — Capacity-exhausted non-retryable.** Any capacity bound declared in the
PRD must specify that the exhaustion response is non-retryable at the
caller-facing boundary (or explicitly ADR-deferred). An unbounded retry loop
on a capacity-exhausted resource converts a load spike into a sustained
overload. Missing → P3 finding citing C4.

**C5 — Best-effort vs. synchronous path separation.** Where the PRD mixes
best-effort operations (e.g., visit-count increments, analytics writes) with
synchronous user-facing operations (e.g., redirects, link creation), the two
must be explicitly separated so that best-effort failures do not block the
synchronous path. Implicit mixing is a latency and availability risk. Missing
→ P3 finding citing C5.

## Beyond-checklist

If you find a layer-specific failure mode the checklist does not cover, raise
it as a P2/P3 finding citing `beyond-checklist:<principle-tag>` and state
which paragraph of the reasoning frame above motivates it. Use sparingly. If
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
