# Hermes Skills (UCX V3)

This directory contains Hermes runtime skills for UCX V3 lifecycle, governance, and KB operations.

## Skill Set

| Skill | Purpose |
|-------|---------|
| `ucx-sdd-bridge` | UCX V3 lifecycle orchestration (BRD->IPLAN), MCP-only document-layer flow, round-based review/remediation gates |
| `ucx-github-governance` | GitHub issue/PR governance flow, label transitions, acceptance-criteria sync, merge escalation policy |
| `ucx-github-deploy-governance` | CI/CD governance, QA/staging/prod readiness checks, post-deploy issue reopen loop |
| `ucx-kb-context` | Retrieval enrichment from KB for create/review/remediate phases |
| `ucx-kb-maintenance` | Governance-controlled KB writes and coverage tracking after approved IPLAN evidence |

## Required Development Flow (Normative)

Hermes skills follow this sequence for issue execution readiness:

1. Project initialization (`sdd_init`) when project UCX assets are not present.
2. Preflight readiness check (`sdd_preflight`).
3. Issue analysis.
4. Planning package creation (roadmap, planning index, changelog plan).
5. Planning review and gap fixing (or explicit deferral rationale).
6. Plan approval for required artifact set (document-layer IPLAN and/or permanent development plan).
7. Implementation start (`ai:ready -> ai:in-progress`).

Plan taxonomy alignment:

- Document-layer IPLAN: `IPLAN-NNN_{slug}` in lifecycle document context.
- Permanent development plan: `PLAN-NNN_{slug}` (preferred) in `plans/` or `governance/plans/`.
- Temporary plans remain in `tmp/` and are not governance-history records.

## Supporting KB Policy Files

- `ucx-kb-maintenance/KB_GENERAL_RULES.md`
- `ucx-kb-maintenance/KB_ENTRY_TEMPLATE.md`

## Operating Boundaries

- Use UCX MCP tools for `framework` document-layer lifecycle stages.
- Do not use CLI lifecycle commands for document layers.
- CLI usage is reserved for approved IPLAN implementation execution tasks.
- KB augments retrieval/continuity; UCX lifecycle gates remain source of truth.

## Related Documentation

- `ucx_hermes/docs/HERMES_INTEGRATION.md`
- `governance/GOVERNANCE_RULES.md`
- `governance/AI_ISSUE_LIFECYCLE.md`
- `ucx_kb/README.md`
