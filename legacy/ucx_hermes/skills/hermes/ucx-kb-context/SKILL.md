---
name: ucx-kb-context
description: |
  Use UCX Knowledge Base retrieval to enrich Hermes decisions during UCX V3
  SDD lifecycle runs without overriding MCP gate outcomes.
version: 1.0.0
category: spec-driven-development
author: UCX Framework Team
requires: []
---

# UCX KB Context Skill

## Purpose

Provide a retrieval-first pattern for Hermes when a KB server is available
(`project-knowledge` / `kb`) while keeping UCX V3 lifecycle control in
`sdd-lifecycle`.

## Core Rule

> KB informs decisions. UCX V3 MCP gates decide progression.

- Do not use KB results to bypass `sdd_validate`, `sdd_review`, or `sdd_remediate`.
- If KB retrieval fails, continue with lifecycle execution and log reduced confidence.
- Keep document-layer orchestration MCP-only for `ucx_flow_v3` layers.

## Recommended Retrieval Checkpoints

1. Before `sdd_create_build`: fetch domain glossary, prior accepted constraints, and similar artifact patterns.
2. Before `sdd_review`: fetch prior findings, policy exceptions, and historical failure modes.
3. Before `sdd_remediate`: fetch previously accepted remediation approaches and anti-patterns.

## Runtime Preconditions

Before using KB context in a lifecycle round, run this preflight sequence:

- Ensure project initialization has been completed (`sdd_init`) and readiness verified (`sdd_preflight`) for the target project context.

- Assume `project-knowledge` server may be absent in framework-only environments.
- Activate KB retrieval only when downstream project runtime registers `project-knowledge` and `ucx_kb` is initialized.

1. Call `kb_status`.
2. Call `kb_graph_status`.
3. Mark KB mode:
   - `ready`: both calls succeed and return usable status payloads.
   - `degraded`: one call fails or returns an error payload.
   - `unavailable`: both calls fail.

KB mode affects confidence only. It does not alter UCX lifecycle gate authority.

## Tool Recipes

Use `project-knowledge` MCP tools with compact, intent-focused inputs.

### Pre-create retrieval

- Tool: `kb_search`
- Input pattern:

```json
{
  "query": "constraints prior decision glossary for <artifact scope>",
  "source_type": "constraint",
  "top_k": 5
}
```

### Pre-review retrieval

- Tool: `kb_hybrid_context`
- Input pattern:

```json
{
  "query": "known issue prior findings accepted remediation for <topic>",
  "entity_id": "<domain or ticker key>",
  "analysis_type": "review",
  "adaptive": true
}
```

### Pre-remediate retrieval

- Tool: `kb_search`
- Input pattern:

```json
{
  "query": "accepted remediation anti-pattern failure mode for <issue>",
  "source_type": "remediation_pattern",
  "top_k": 8
}
```

### Optional graph expansion

- Tool: `kb_graph_search`
- Input pattern:

```json
{
  "entity_id": "<domain or ticker key>",
  "depth": 2
}
```

## Minimal Prompting Pattern

When calling KB tools from Hermes, use concise retrieval scopes:

- query intent: "constraints"
- query intent: "prior decision"
- query intent: "known issue"
- query intent: "accepted remediation"

## Output Handling

- Preserve KB references in Hermes reasoning notes (IDs/links where available).
- Distinguish facts from suggestions in responses.
- Escalate to human when KB evidence conflicts with current UCX stage artifacts.

When KB tool outputs include `error`, treat the retrieval step as failed and continue in reduced-confidence mode.

## Boundaries

- No CLI lifecycle commands for document layers.
- CLI allowed only for approved IPLAN implementation execution tasks.
- No autonomous KB write-back during active document-layer gates.

## Failure Handling

If KB is unavailable or stale:

1. Continue UCX V3 MCP flow.
2. Mark KB context status as unavailable/stale.
3. Require explicit human confirmation for high-impact assumptions.

## Degraded-Mode Contract

If KB mode is `degraded` or `unavailable`:

- Continue `sdd_create_build`, `sdd_validate`, `sdd_review`, and `sdd_remediate` as planned.
- Add a reasoning note: `kb_mode=<mode>` and list failed KB calls.
- Avoid introducing new high-impact assumptions without explicit human confirmation.
- Retry KB preflight at the next lifecycle checkpoint instead of repeated immediate retries.
