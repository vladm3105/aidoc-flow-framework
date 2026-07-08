---
layer: 09_CHG
lens: auditor
weight: 10
agent: traceability-auditor
framework_spec_version: "0.35.1"
---
# auditor lens — CHG layer

## Reasoning frame

The auditor lens at CHG altitude (weight 10) evaluates traceability
and gate-routing bookkeeping. CHG is a governance overlay: its value
to future readers is that the artifact record itself tells them what
changed, why, under which authority, and through which gate. A CHG
that propagates updates without back-references, that classifies its
change level inconsistently with its scope, or that leaves the
gate_approval block ambiguous is a CHG whose audit trail will not
survive contact with the next CHG that touches the same artifacts.

Back-references are the central concept. Every artifact the CHG
modified must carry a `@chg: CHG-NN` tag pointing back to this CHG,
so that a future reader looking at a BRD / PRD / EARS / etc. update
can trace it to the governing change record. Without that
back-reference, the modified artifact looks like an unsourced edit,
indistinguishable from a hand-edit. The auditor lens also verifies
that the change-level classification (C1 / C2 / C3 / Emergency)
matches the actual scope of the propagation — a C3-scope change
filed as C2 skips the formal gate; a C2-scope change filed as C3
imposes unnecessary process — and that the gate_approval section is
either filled or explicitly waived per the declared level.

Re-gate routing and pre/post-state ID resolution are the remaining
pillars. Every CHG ends with a re-gate path: after implementation,
which gate re-validates that the change landed correctly? An
absent re-gate path leaves the CHG in an implementation-without-
validation posture — the change went out but no gate confirmed the
landing. And every document ID the CHG names (pre-state baseline,
post-state target) must resolve to a real artifact; an unresolved
ID is an orphan tag and a sign the CHG was assembled without the
artifacts at hand.

This lens does NOT evaluate: propagation completeness (integration_
lead), component-boundary preservation (architect), rollback /
emergency-path (chaos_engineer), operability impact (operator), or
threat-model delta (security_engineer). The auditor lens is confined
to back-reference tagging, gate_approval completeness, change-level
classification accuracy, ID resolution, and re-gate routing.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check
citation are out-of-scope and discarded by the synthesizer.

**C1 — Every modified artifact carries `@chg: CHG-NN` back-reference.**
Each artifact the CHG modifies (named in `impact_assessment` with a
propagated diff) must include a `@chg: CHG-NN` back-reference
pointing to this CHG, so future readers can trace the edit. A
modified artifact without the back-reference is indistinguishable
from an unsourced hand-edit. Missing on any modified artifact → P1
citing C1.

**C2 — `gate_approval` section filled or explicitly waived per
change level.** The CHG's `gate_approval` section is either
completed per the entry gate (approver, date, gate decision) or
explicitly waived with the reason allowed by the change level (C1:
no gate required; Emergency: post-hoc approval pending). A
gate_approval section left blank on a C2/C3 change is a process
skip. Missing → P1 citing C2.

**C3 — Change-level classification matches the actual scope.** The
declared `change_level` (C1 / C2 / C3 / Emergency) is consistent
with the propagation scope per `framework/governance/chg/README.md`:
C1 is typo / formatting (no propagation); C2 is section update
(single-layer); C3 is cross-layer (impact_assessment names ≥2
layers); Emergency is post-hoc with post-mortem. A C3-scope change
filed as C2 skips the formal gate. Mis-classification → P1 citing
C3.

**C4 — All pre-state / post-state document IDs resolve.** Every
artifact ID the CHG cites (pre-state baseline, post-state target,
referenced artifacts in impact_assessment) must resolve to a real
artifact in the project's document registry. An unresolved ID is
an orphan tag indicating the CHG was assembled without verifying
the artifacts exist. Any unresolved → P2 citing C4.

**C5 — Re-gate path declared.** The CHG names which gate re-
validates the change after implementation (GATE-01 / 03 / 06 / 08 /
CODE / SPEC), or explicitly states "no re-gate required" with
reason. A CHG without a re-gate path leaves the change in an
implementation-without-validation posture; no gate confirms the
landing. Missing → P2 citing C5.

## Beyond-checklist

If you find a traceability or gate-routing failure mode the
checklist does not cover, raise it as a P2/P3 finding citing
`beyond-checklist:<principle-tag>` and state which paragraph of the
reasoning frame motivates it. Common beyond-checklist cases at CHG
auditor altitude: a CHG that updates an artifact but does not bump
that artifact's own version pointer (silent version drift); a
gate_approval form referenced by name but not by URL / path
(approval trail unverifiable); a change-source recorded as
`external` (regulatory / vendor) with no citation of the external
authority (rule / version / contract clause); and a re-gate path
declared but routed to the same entry gate that approved the
change (no independent re-validation). Use sparingly. If more than
30% of your findings are beyond-checklist, the playbook needs
revision (file a follow-up).

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
