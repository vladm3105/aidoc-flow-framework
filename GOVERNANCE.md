# Governance

This repository is the **source of truth** for aidoc-flow project governance.
The engine-agnostic standards live in
[`framework/governance/`](framework/governance/README.md) and apply across every
aidoc-flow repository. Consuming repositories reference this governance; they do
not copy it.

## Standards

See [`framework/governance/README.md`](framework/governance/README.md) for the
full index. Key documents:

- `DOC_GOVERNANCE_CORE.md` — core principles (single source of truth, YAML-first
  templates, immutability, validation baseline).
- `ID_NAMING_STANDARDS.md` — document IDs, element IDs, traceability tags, file
  naming.
- `TRACEABILITY.md` — the traceability chain and readiness gates.
- `REVIEW_TEAM.md` + `REVIEW_CREWS.yaml` — the multi-persona review model.
- `REVIEW_REMEDIATION_FLOW.md` — the review to remediation to gate quality loop + the independent `pre_merge` review gate.
- `DEFINITION_OF_DONE.md` — completion criteria (artifact + spec change) and the risk-tiered human-in-loop.
- `SECURITY_REVIEW.md` — safety checks for agent-authored artifacts.
- `AUTHORING_STYLE.md` — token-efficient authoring rules.
- `DIAGRAM_STANDARDS.md` + `THRESHOLD_NAMING_RULES.md` — diagram and threshold
  conventions.
- `ADAPTATION.md` + `ADAPTATION_SURFACE.yaml` — how a consuming repo adapts the
  flow without forking.
- `DECISIONS.md` — durable register of governance and spec decisions.
- `chg/` — the change-management overlay and GATE-SPEC (CHG-D1), the meta gate
  governing changes to the `framework/` spec itself.

## Changing governance

Governance changes are proposed and ratified here through the CHG / GATE-SPEC
process (`framework/governance/chg/`). The spec defines the gates; each
consuming platform implements enforcement against this shared contract (record
validator, CI, protected-branch review). This model is recorded as GD-01 in
`framework/governance/DECISIONS.md`.
