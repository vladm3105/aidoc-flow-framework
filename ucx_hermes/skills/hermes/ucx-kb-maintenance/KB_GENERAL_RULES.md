# UCX KB General Rules (UCX V3)

## Scope

These rules apply to UCX V3 projects using `ucx_flow_v3` lifecycle artifacts.

## Mandatory Coverage

All document artifacts must be represented in the KB project.

- Include canonical lifecycle artifacts across layers (BRD->TASKS).
- Include lifecycle stage outputs needed for traceability (validation, review, remediation artifacts).
- Include implementation-linked documentation updates produced during approved IPLAN execution.

## Ingestion Timing

1. Ingest or update KB records after each accepted lifecycle gate outcome.
2. Ingest final consolidated records after approved IPLAN execution evidence is available.
3. Reconcile superseded entries when artifacts are replaced by newer accepted versions.

## Required Metadata

Each KB record must include:

- Project identifier
- Artifact identifier and layer
- Lifecycle stage and status
- Source path or canonical artifact reference
- Related issue/PR/IPLAN references when applicable
- Sensitivity classification
- Timestamp with timezone

## Quality and Governance Rules

- Do not store secrets, credentials, or unverified claims.
- Keep entries traceable to UCX V3 stage outputs.
- Prefer additive updates; mark superseded entries explicitly.
- Preserve source-of-truth semantics: KB does not decide gate progression.

## Runtime Boundary

- Document-layer lifecycle orchestration remains MCP-only.
- CLI usage remains limited to approved IPLAN implementation execution tasks.
- KB retrieval/write failures must not silently alter lifecycle gating decisions.

## Minimum Operator Controls

- Enforce write authorization policy per project.
- Emit an ingestion summary after each KB update batch.
- Flag missing artifact coverage as a policy violation for follow-up.
