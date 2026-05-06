---
name: ucx-kb-maintenance
description: |
  Governance-oriented KB maintenance workflow for post-IPLAN implementation
  evidence, ensuring KB updates do not alter UCX V3 lifecycle gate authority.
version: 1.1.0
category: spec-driven-development
author: UCX Framework Team
requires: []
---

# UCX KB Maintenance Skill

## Purpose

Define when and how Hermes should update knowledge base content after
implementation evidence is validated.

Reference documents:

- `KB_GENERAL_RULES.md` in this skill directory (mandatory policy baseline).
- `KB_ENTRY_TEMPLATE.md` in this skill directory (canonical record structure).

## Write Policy

KB maintenance follows mandatory coverage and gate rules from
`KB_GENERAL_RULES.md`.

Only perform KB write/update actions after all conditions are true:

1. IPLAN execution evidence exists (tests, code changes, implementation docs).
2. Relevant UCX lifecycle gates are complete for the change scope.
3. Human/operator policy allows KB write-back for the project.

If any condition is false, skip KB writes and record pending state.

## What to Store

- Accepted remediation patterns with scope tags.
- Repeated failure signatures and validated mitigations.
- Domain constraints and glossary terms confirmed during reviews.
- Cross-reference keys to affected artifacts and issue/PR identifiers.

## What Not to Store

- Secrets or raw credentials.
- Unverified hypotheses.
- Temporary notes without traceability context.

## Consistency Rules

- Keep KB entries traceable to artifact IDs and lifecycle stage outputs.
- Prefer additive updates; avoid destructive rewrites without approval.
- Mark superseded entries explicitly instead of silent replacement.

## Operational Sequence

1. Enumerate required artifact coverage per `KB_GENERAL_RULES.md`.
2. Collect accepted lifecycle artifacts and approved implementation evidence.
3. Normalize facts into KB entry candidates using `KB_ENTRY_TEMPLATE.md`.
4. Validate traceability links, sensitivity rules, and supersession mapping.
5. Write/update KB entries.
6. Emit coverage and ingestion summary for operator review.

## Tool Mapping (project-knowledge MCP)

Use these tools for KB write/update operations after admission conditions pass.

Precondition:

- Apply this mapping only in downstream project runtimes where `project-knowledge` is registered and `ucx_kb` is initialized.
- In framework-only environments, skip write calls and emit `kb_mode=unavailable` summary.

1. Artifact text ingestion
   - Tool: `kb_embed`
   - Input:

```json
{
  "file_path": "<artifact path>",
  "force": false
}
```

2. Structured note ingestion (pattern or finding summary)
   - Tool: `kb_embed_text`
   - Input:

```json
{
  "text": "<validated summary>",
  "doc_id": "<entry_id>",
  "source_type": "remediation_pattern",
  "entity_id": "<domain key optional>"
}
```

3. Graph extraction from artifact
   - Tool: `kb_extract`
   - Input:

```json
{
  "file_path": "<artifact path>",
  "commit": true
}
```

4. Graph extraction from synthesized note
   - Tool: `kb_extract_text`
   - Input:

```json
{
  "text": "<validated summary>",
  "doc_id": "<entry_id>",
  "source_type": "remediation_pattern"
}
```

## Conflict and Supersession Handling

- If a new entry supersedes prior guidance, keep old content and mark status as `superseded` using template fields.
- Prefer additive inserts over destructive edits.
- Reuse `entry_id` only for strict updates of the same record scope; use a new `entry_id` for new scope.

## Failure Handling

- If any write call returns an error payload, stop the batch and emit partial-ingestion report.
- Do not mask KB write errors as lifecycle gate outcomes.
- Keep lifecycle state unchanged when KB write/update fails.

## Coverage Summary Minimum Fields

Each maintenance run should output at least:

- `project`
- `batch_id`
- `artifacts_expected`
- `artifacts_ingested`
- `entries_created`
- `entries_updated`
- `entries_superseded`
- `failed_operations`
- `kb_mode` (`ready` | `degraded` | `unavailable`)

## Boundary with UCX V3 Lifecycle

- KB updates do not advance document layers.
- UCX V3 MCP stage outputs remain source of truth for gate decisions.
- KB serves retrieval and continuity, not stage transition authority.
