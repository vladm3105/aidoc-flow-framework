---
layer: 08_IPLAN
lens: auditor
weight: 10
agent: traceability-auditor
framework_spec_version: "0.29.1"
---
# auditor lens — IPLAN layer

## Reasoning frame

The auditor lens at IPLAN altitude (weight 10) validates the formal
rules that govern IPLAN structure: ID conformance, upstream-trace
resolution to SPEC and TDD, deployment-step matrix↔body parity, the
necessary-upstream trace header at the doc level, and cross-IPLAN reference
form. IPLAN is the final document layer before code touches a
running environment; its auditor lens must keep the trace chain
intact so that, when a deploy step fails or a rollback fires, the
operator can walk from the failing step back to the SPEC commitment
and TDD test the step was meant to honor.

Trace resolution at IPLAN altitude runs primarily to SPEC and TDD —
the layers that fix what the IPLAN is deploying. Every
`@spec: SPEC.NN…` and `@tdd: TDD.NN…` tag on a deploy step or
rollback step must resolve to an existing element in the upstream
document. Broken tags collapse the chain at exactly the moment the
operator needs it most — mid-incident, mid-cutover, when the
question "what was this step supposed to do?" must have an
immediate answer.

Element-ID conformance is the second concern. Every deploy step
must carry an ID matching `IPLAN.NN.SS.xxxx` (4-hex content-hash)
so that incident reports, deploy logs, and post-mortems can
reference steps unambiguously. A step ID that drifts from the
pattern cannot be tracked across the toolchain.

Matrix-body parity, the necessary-upstream trace header, and cross-IPLAN
reference form round out the lens. The deployment-step matrix at
the top of the IPLAN indexes every cutover step; matrix and body
must stay in lockstep. The necessary-upstream `@spec / @tdd` header at the
doc level (declared once, applying to every step) must resolve
cleanly — the necessary-upstream contract requires it. Cross-IPLAN
references must use the right form: dash for doc-level
(`@iplan: IPLAN-NN`), dotted for element-level
(`@iplan: IPLAN.NN.SS.xxxx`).

This lens does NOT evaluate: deploy-sequence reversibility
(tech_lead), topology invariance (architect), smoke-test /
observability emission (operator), cross-service compatibility
(integration_lead), or rollback dress-rehearsal practice
(chaos_engineer). The auditor lens is confined to formal trace
conformance and ID hygiene at IPLAN altitude.

## Required evidence checks

Every finding MUST cite which check fired. Findings without a check
citation are out-of-scope and discarded by the synthesizer.

**C1 — Every `@spec: SPEC.NN…` / `@tdd: TDD.NN…` tag resolves to an
existing upstream element.** Every upstream tag on a deploy step or
rollback step resolves to a named element in the corresponding
SPEC or TDD document. Broken tags collapse the trace chain at the
moment the operator needs it — mid-incident. Broken → P1 citing C1.

**C2 — IPLAN step IDs conform to `IPLAN.NN.SS.xxxx` 4-hex content-
hash pattern.** Every deploy step ID in the IPLAN body follows the
canonical pattern. Non-conformant IDs cannot be referenced
unambiguously in incident reports, deploy logs, or post-mortems.
Non-conformant → P1 citing C2.

**C3 — Each row in the deployment-step matrix has a paired body
step.** Every row in the IPLAN's top-of-document deployment-step
matrix has a paired body step carrying the matching ID. Conversely,
every body step appears in the matrix. Orphan row / orphan body
step → P2 citing C3.

**C4 — Necessary-upstream `@spec / @tdd` header at doc level resolves
cleanly.** The header at the doc level (declared once, applying to every
deploy step) resolves cleanly to existing upstream IDs. A broken header
cascades into every body step — the necessary-upstream contract requires it.
Missing or broken → P2 citing C4.

**C5 — Cross-IPLAN `@iplan` references use correct form.**
`@iplan:` references use the dash form (`@iplan: IPLAN-NN`) when
pointing to a whole IPLAN document and the dotted form
(`@iplan: IPLAN.NN.SS.xxxx`) when pointing to a specific step.
Tools branch on the form; wrong form produces broken cross-links.
Wrong form → P3 citing C5.

## Beyond-checklist

If you find an upstream-trace or ID-conformance failure mode the
checklist does not cover, raise it as a P2/P3 finding citing
`beyond-checklist:<principle-tag>` and state which paragraph of the
reasoning frame motivates it. Common beyond-checklist cases at IPLAN
auditor altitude: an `@spec:` or `@tdd:` citation whose target ID
exists upstream but in a different document than the host step
implies, so the trace resolves but to the wrong commitment; an IPLAN
step ID written as a 3-segment form (`IPLAN.NN.SS`) rather than the
canonical 4-segment `IPLAN.NN.SS.xxxx` content-hash form, which
parses without erroring but cannot be referenced unambiguously; and
trace-tag prose that resolves only because a lint-skip rule applies
to the section, leaving the binding force on the citation effectively
disabled. Use sparingly. If more than 30% of your findings are
beyond-checklist, the playbook needs revision (file a follow-up).


*Cross-layer cardinality note (CLEANUP-PR-F item 18):* apparent-orphan
downstream docs (e.g., `PRD-02` declaring `@brd: BRD-01` when `PRD-01`
also exists with the same upstream) MAY be valid siblings of the same
upstream, not actual orphans. Validate the trace by tag resolution, not
by doc-number alignment. See `framework/governance/ID_NAMING_STANDARDS.md`
§Cross-layer cardinality.
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
