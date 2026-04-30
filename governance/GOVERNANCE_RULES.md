# Governance Rules

**Framework**: Specification-Driven Development (SDD v3.2)

## Canonical Flow

All active governance workflows align to:

`BRD->PRD->EARS->BDD->ADR->SPEC->TDD->IPLAN->Code`

- Artifact registry: `ucx_flow_v3/LAYER_REGISTRY.yaml`
- Governance core: `ucx_flow_v3/DOC_GOVERNANCE_CORE.md`
- CHG overlay: `ucx_flow_v3/CHG/`

## Depth Model

| Depth | Required Artifacts |
|---|---|
| Lite | BRD, PRD, IPLAN |
| Standard | BRD, PRD, EARS, ADR, SPEC, TDD, IPLAN |
| Full | BRD, PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN + CHG gates |

Legacy SYS/REQ/CTR/TSPEC/TASKS layers are deprecated for active governance.

## Issue Source and Traceability

Issues may originate from v3 artifacts. When issue label `source:sdd` is present:

1. Issue includes trace tags (`@brd`, `@prd`, `@ears`, `@adr`, `@spec`, `@tdd`)
2. Issue references upstream artifact IDs
3. IPLAN references the issue and upstream IDs for execution traceability

## AI Workflow Labels

`ai:ready -> ai:in-progress -> ai:review-requested`

## Mandatory Pre-Implementation Gate

Before coding, AI agents must:
1. Complete issue analysis
2. Create IPLAN
3. Refine IPLAN
4. Transition issue to `ai:in-progress`

## Deprecated Compatibility

- Legacy TASKS-sync tooling is deprecated.
- Legacy framework root references are not allowed in active governance docs.
- Any retained compatibility alias must include a deprecation note and removal criteria.
