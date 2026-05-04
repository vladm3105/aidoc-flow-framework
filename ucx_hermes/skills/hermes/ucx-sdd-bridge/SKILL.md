---
name: ucx-sdd-bridge
description: |
  Bridge Hermes conversational reasoning with UCX deterministic SDD tools.
  Enforces safe SDD workflow: UCX validates structurally, Hermes reviews
  interactively, humans approve all document writes. Never delegates document
  creation, review, or remediation to stateless AI executors.
version: 1.0.0
category: spec-driven-development
author: UCX Framework Team
requires: []
---

# UCX SDD Bridge Skill

## Purpose

This skill makes Hermes the interactive orchestrator for UCX SDD lifecycle
workflows. UCX provides deterministic validation and structural enforcement.
Hermes provides conversational reasoning, memory, and human-gated decision
support.

## Core Principle

> **UCX validates. Hermes reasons. Humans decide.**

Never use the `executor` parameter on any UCX MCP tool. The patched UCX server
has disabled AI executor delegation for `sdd_validate`, `sdd_review`,
`sdd_remediate`, and `sdd_create_build`.

## Safe UCX Tools (Deterministic)

Call these freely. They are 100% rule-based, no AI delegation:

| Tool | Purpose |
|------|---------|
| `sdd_validate` | Structural validation: sections, tags, IDs, scores, traceability |
| `sdd_validate_chg` | CHG governance: change levels, gate routing, approval reqs |
| `sdd_consistency` | Artifact lineage and stage consistency |
| `sdd_validate_links` | Markdown link existence and anchor resolution |
| `sdd_preflight` | Environment readiness before create/review/remediate |
| `sdd_scan` | Extract category counts from validation/remediation reports |
| `sdd_score_show` | Compute quality score from report |
| `sdd_score_validate` | Pass/fail against threshold |
| `sdd_score_compare` | Delta between baseline and candidate reports |
| `sdd_next_action` | Inspect folder and recommend next lifecycle stage |
| `sdd_run_lifecycle` | Pipeline orchestration (safe when used stage-by-stage with human gates) |
| `sdd_clean` | Remove obsolete stage artifacts |
| `sdd_init` | Scaffold UCX assets for a project |
| `sdd_personas_show/set/diff` | Manage persona mappings |
| `sdd_env_show` | List `.env` keys without exposing values |
| `sdd_prescreen` | Identify high-priority remediation candidates |
| `sdd_list_executors` / `sdd_register_executor` | Executor registry (legacy, now unused) |

## Dangerous Patterns (Never Do)

| Pattern | Why It Is Dangerous | Correct Alternative |
|---------|---------------------|---------------------|
| Pass `executor` to `sdd_validate` | Deprecated compatibility parameter; ignored and can mislead operators | Omit `executor`; use validation/fix reports for human-approved edits |
| Pass `executor` to `sdd_review` | Patched — returns prompt only | Use returned `prompt_text` to guide Hermes reasoning |
| Pass `executor` to `sdd_remediate` | Patched — returns findings only | Use `sdd_validate` + human discussion to plan fixes |
| Pass `executor` to `sdd_create_build` | Patched — returns prompt only | Use `sdd_create` (template-only) or draft interactively with Hermes |
| Auto-run full pipeline with `executor` | Context lost between stages, unverified rewrites | Stage-by-stage with human gates between each |

## Standard SDD Workflow with Hermes + UCX

### Stage 1: Scaffold

```
Hermes: Call sdd_init for project /opt/data/b-local/b-local-telegram-ui
UCX: Creates UCX/ directory with templates, personas, schemas
Hermes: Confirm scaffold created, show persona mappings
```

### Stage 2: Create Document (Human-Gated)

```
Human: "Draft a BRD for BEE-001"
Hermes: Call sdd_create_build to see the creation prompt and template
UCX: Returns prompt_text, template, inspection metadata
Hermes: Uses prompt_text + project context + memory to draft BRD sections
Hermes: Writes draft to ucx_flow_v3/01_BRD/BEE-001.md
Hermes: Call sdd_validate on the draft
UCX: Returns errors/warnings/passes (deterministic)
Hermes: Present findings; ask human to approve or revise
```

### Stage 3: Validate (Deterministic Gate)

```
Human: "Validate this BRD"
Hermes: Call sdd_validate --doc_type=brd --layer=01_BRD --document=BEE-001.md
UCX: Runs cross_section, brd_rules, template checks
UCX: Returns structured report with errors/warnings/passes
Hermes: Interpret report for human. If errors → revise. If clean → proceed.
```

### Stage 4: Review (Hermes Reasoning, Not AI Executor)

```
Human: "Review this BRD for testability and security"
Hermes: Call sdd_review --doc_type=brd --document=BEE-001.md
UCX: Returns assembled multi-persona prompt_text (no executor run)
Hermes: Loads `qa_lead` and `auditor` persona guidance
Hermes: Uses prompt_text as context, applies skill knowledge, examines document
Hermes: Presents structured findings to human
```

### Stage 5: Remediate (Human-Gated)

```
Human: "Fix the issues found"
Hermes: Call sdd_remediate --doc_type=brd --layer=01_BRD --document=BEE-001.md
UCX: Returns deterministic findings and fix instructions (no AI rewrite)
Hermes: Presents findings with recommended actions
Human: Approves each fix or requests alternative approach
Hermes: Applies approved edits to document
Hermes: Re-runs sdd_validate to confirm fixes
```

### Stage 6: Advance to Next Layer

```
Human: "Advance to PRD"
Hermes: Call sdd_next_action on document folder
UCX: Returns current_stage="validated", next_action="create", next_tool="sdd_create"
Hermes: Loads PRD template, uses BRD content + project memory to draft PRD
Hermes: Repeats Stage 2-5 for PRD layer
```

## Hermes Memory Conventions

When working with UCX projects, save to session memory:

```
Project: BeeLocal
Root: /opt/data/b-local/b-local-telegram-ui
Active document: BEE-001
Current stage: BRD validation
Last validation: 2026-05-02 (3 errors, 1 warning)
Pending: Human approval for remediation
```

This allows Hermes to maintain continuity across the multi-turn SDD workflow
that UCX's stateless tools cannot provide.

## Tool Calling Rules

1. **Always omit `executor` parameter** on all UCX tool calls
2. **Always call `sdd_validate` before advancing stage** — structural gate
3. **Always present validation reports to human** — do not auto-remediate
4. **Use `sdd_next_action` to confirm stage state** — avoid assumptions
5. **Save project state to Hermes memory** after each significant action

## Integration with Existing Hermes SDD Skills

This skill works with UCX personas and optional Hermes-native skills:
- `business-analyst` — Use for BRD gap analysis after `sdd_validate`
- `qa_lead` persona — Use for testability review after `sdd_review` prompt returned
- `auditor` persona — Use for compliance reasoning after `sdd_review` prompt
- If Hermes-native skills exist in your environment (`sdd-orchestrator`, `sdd-cross-validation`), use them as optional overlays

## Error Handling

If UCX returns an error:
1. Log the tool name and arguments to Hermes memory
2. Present the error clearly to the human
3. Do not retry the same call blindly — ask human for direction
4. If `sdd_preflight` fails, stop and resolve environment issues before proceeding

## Migration Notes

This skill targets UCX Hermes runtime (`ucx_hermes/`) v2.0.0+ where AI executor
delegation has been removed from `sdd_validate`, `sdd_review`,
`sdd_remediate`, and `sdd_create_build`. If using an older UCX server,
ensure no `executor` parameter is passed to prevent unsafe auto-rewrites.
