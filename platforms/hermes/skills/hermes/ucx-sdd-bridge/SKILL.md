---
name: ucx-sdd-bridge
description: |
  Bridge Hermes conversational reasoning with UCX deterministic SDD tools.
  Enforces safe SDD workflow: UCX validates structurally, Hermes reviews
  interactively, human or LLM-as-judge approvers validate policy-gated outcomes.
version: 1.3.0
category: spec-driven-development
author: UCX Framework Team
requires: []
---

# UCX SDD Bridge Skill

## Changelog

| Version | Date (EST) | Changes |
|---------|------------|---------|
| 1.3.0 | 2026-05-06 | Aligned to UCX plan taxonomy and required development flow: initialization (`sdd_init`/`sdd_preflight`), planning package review, gap fixing, plan approval, implementation start. |
| 1.2.0 | 2026-05-06 | Added planning-first governance gate: roadmap, planning index, changelog planning, gap review, and per-document IPLAN approval before lifecycle creation. |
| 1.1.2 | 2026-05-05 | Added UCX V3 KB integration guidance and cross-skill references for `ucx-kb-context` and `ucx-kb-maintenance`. |
| 1.1.1 | 2026-05-05 | Added known-good executor policy snippet, executor troubleshooting table, and fan-out/fan-in (`saga_parallel`) operational guidance. |
| 1.1.0 | 2026-05-05 | Updated skill to API-only executor runtime model for LLM stages; removed legacy patched/no-executor guidance. |

## Purpose

This skill makes Hermes the interactive orchestrator for UCX SDD lifecycle
workflows. UCX provides deterministic validation and structural enforcement.
Hermes provides conversational reasoning, memory, and policy-gated decision
support.

## Core Principle

> **UCX enforces lifecycle contracts. Hermes orchestrates. Human or LLM-as-judge approvers validate policy-gated outcomes.**

Planning-first rule:

- Before any layer document creation, Hermes completes planning-first artifacts (layer roadmap, planning index, changelog plan), runs a gap review pass, fixes or explicitly defers gaps, creates required plan artifacts (document-layer IPLAN and/or permanent development plan), and records approval.
- Before BRD `sdd_create_build`, Hermes confirms runtime startup gate: `sdd-lifecycle` is running, and in KB-enabled mode `project-knowledge` is running with `kb_status`/`kb_graph_status` success.
- Environment bootstrap and required framework tool availability are mandatory before any document creation stage starts.
- No document/test/code implementation starts without approved plans.

Use API executors for LLM stages (`sdd_review`, `sdd_remediate`).
Do not use legacy CLI executor names such as `claude`, `codex`, or `gemini`.

## UCX V3 Invocation Boundary

For `framework` document-layer lifecycle work, use UCX MCP tools only.

- Scope: BRD through IPLAN document layers in `framework/`.
- Allowed: `sdd_*` MCP tool calls for create/validate/review/remediate/advance.
- Not allowed for document layers: CLI lifecycle invocation patterns (for example `python -m mcp_server.cli.main validate ...`).
- CLI is allowed only after approved IPLAN for implementation execution tasks (tests, source code changes, and implementation documentation updates).

## UCX KB Integration (Optional)

`ucx_hermes` is the SDD runtime (`sdd-lifecycle`). UCX Knowledge Base (`kb` / `project-knowledge`) is a separate sub-framework.

Use KB as contextual enrichment, not as a replacement for lifecycle gates.

- Source of truth for document-layer progression remains UCX V3 stage artifacts and MCP gate outputs.
- Use KB for retrieval tasks such as prior decisions, glossary reuse, domain constraints, and historical issue context.
- If KB is unavailable, continue with SDD lifecycle flow; do not block BRD->IPLAN progression.
- Treat KB write/update operations as governance-controlled actions, typically after approved implementation evidence.

Recommended Hermes sequence when KB is available:

1. Pre-create context fetch from KB before `sdd_create_build`.
2. Review-time context fetch from KB before `sdd_review` (especially in `saga_parallel`).
3. Post-implementation knowledge update after IPLAN execution evidence is validated.

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
| `sdd_run_lifecycle` | Pipeline orchestration (use API executor names for LLM stages) |
| `sdd_clean` | Remove obsolete stage artifacts |
| `sdd_init` | Scaffold UCX assets for a project |
| `sdd_personas_show/set/diff` | Manage persona mappings |
| `sdd_env_show` | List `.env` keys without exposing values |
| `sdd_prescreen` | Identify high-priority remediation candidates |
| `sdd_list_executors` / `sdd_register_executor` | API executor registry management |

## Dangerous Patterns (Never Do)

| Pattern | Why It Is Dangerous | Correct Alternative |
|---------|---------------------|---------------------|
| Pass CLI executor names (for example `executor=claude`) | Unsupported in API-only runtime; returns UnknownExecutor | Use API executor names (`api/claude-sonnet`, `api/openrouter`) |
| Pass `executor` to `sdd_validate` | Unsupported parameter/path | Call `sdd_validate` without executor |
| Omit executor policy for LLM stages | Runtime default may differ from project governance policy | Set `executor` explicitly for `sdd_review` and `sdd_remediate` |
| Treat `sdd_review`/`sdd_remediate` as deterministic-only | Misses API executor output and stage status | Capture both deterministic artifacts and executor result fields |
| Auto-run full pipeline without round gates | Can skip human escalation policy at merge decision points | Keep round-based validate/review/remediate gates with escalation checks |

## Standard SDD Workflow with Hermes + UCX

### Stage 0: Planning-First Governance Gate

```
Hermes: Analyze provided source information and constraints
Hermes: Create layer roadmap + planning index + changelog plan
Hermes: Review planning artifacts for dependency and traceability gaps
Hermes: Resolve gaps or record explicit deferrals with rationale
Hermes: Create required plan artifacts (document-layer IPLAN and/or permanent development plan)
Hermes: Review plan artifacts for acceptance-criteria mapping completeness
Hermes: Block lifecycle creation until planning approval exists
```

### Stage 1: Scaffold

```
Hermes: Confirm runtime startup gate before BRD creation (`sdd-lifecycle`, optional `project-knowledge`)
Hermes: Call sdd_init for project /opt/data/b-local/b-local-telegram-ui
UCX: Creates UCX/ directory with templates, personas, schemas
Hermes: Confirm scaffold created, show persona mappings
Hermes: Run sdd_preflight and proceed only when readiness criteria are met
```

### Stage 2: Create Document (Policy-Gated)

```
Human: "Draft a BRD for BEE-001"
Hermes: Call sdd_create_build to see the creation prompt and template
UCX: Returns prompt_text, template, inspection metadata
Hermes: Uses prompt_text + project context + memory to draft BRD sections
Hermes: Writes draft to framework/01_BRD/BEE-001.md
Hermes: Call sdd_validate on the draft
UCX: Returns errors/warnings/passes (deterministic)
Hermes: Present findings; route to approver (human reviewer or independent LLM-as-judge session) for approve/revise decision
```

### Stage 3: Validate (Deterministic Gate)

```
Human: "Validate this BRD"
Hermes: Call sdd_validate with `doc_type=brd`, `layer=01_BRD`, `document=BEE-001.md`
UCX: Runs cross_section, brd_rules, template checks
UCX: Returns structured report with errors/warnings/passes
Hermes: Interpret report for human. If errors → revise. If clean → proceed.
```

### Stage 4: Review (Hermes + API Executor)

```
Human: "Review this BRD for testability and security"
Hermes: Call sdd_review with `doc_type=brd`, `document=BEE-001.md`, `executor=api/openrouter`
UCX: Assembles review prompt and runs configured API executor
Hermes: Loads `qa_lead` and `auditor` persona guidance
Hermes: Uses `prompt_text` and executor output as review evidence
Hermes: Presents structured findings and governance recommendation to human
```

### Stage 5: Remediate (Policy-Gated Apply)

```
Human: "Fix the issues found"
Hermes: Call sdd_remediate with `doc_type=brd`, `layer=01_BRD`, `document=BEE-001.md`, `executor=api/claude-sonnet`
UCX: Produces deterministic findings/fix artifacts and runs API executor apply stage
Hermes: Presents findings, executor status, and recommended actions
Approver: Approves each fix or requests alternative approach (human reviewer or independent LLM-as-judge session)
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
Pending: Approver decision for remediation (human reviewer or independent LLM-as-judge session)
```

This allows Hermes to maintain continuity across the multi-turn SDD workflow
that UCX's stateless tools cannot provide.

## Tool Calling Rules

1. **Use API executors for LLM stages** (`sdd_review`, `sdd_remediate`), and avoid CLI executor names
2. **Always call `sdd_validate` before advancing stage** — structural gate
3. **Always enforce planning-first approval before create/test/code work**
4. **Always present validation reports to the approver authority** — do not auto-remediate
5. **Use `sdd_next_action` to confirm stage state** — avoid assumptions
6. **Save project state to Hermes memory** after each significant action

## Known-Good Executor Policy

Use an explicit executor policy so review/remediation behavior is deterministic across environments.

Example policy:

```yaml
review:
  mode: prompt_only
  executor: api/openrouter
remediate:
  executor: api/claude-sonnet
fallback:
  unknown_executor: fail_fast
```

Operational guidance:

- Set `executor` explicitly on `sdd_review` and `sdd_remediate` calls.
- Keep `sdd_validate` and `sdd_create_build` executor-free.
- Use project overrides in `UCX/executors.json` only for API executors.
- Treat unknown executor names as blocking configuration errors.

## Fan-Out/Fan-In Review Guidance

Use `review_mode=saga_parallel` for multi-persona fan-out/fan-in when persona count or context size makes sequential review costly.

Invocation pattern (MCP tool arguments, not CLI command):

```text
sdd_review:
  doc_type: brd
  document: BEE-001.md
  review_mode: saga_parallel
  executor: api/openrouter
  max_parallel_branches: 4
  branch_timeout_seconds: 120
  max_branch_retries: 1
  retry_backoff_seconds: 2
  saga_branch_llm_enabled: true
```

Expected behavior:

- Runtime fans out persona branches with bounded concurrency and retry controls.
- Runtime performs deterministic reducer merge at fan-in and returns merged findings.
- Hermes reads `review_mode`, `saga_status`, `review_run_id`, and branch/reducer summaries before gate decisions.
- If `saga_status=ESCALATED` or `passed=false`, block merge path and escalate per policy.

When to prefer `prompt_only`:

- Single persona or low-complexity review.
- No need for branch-level telemetry or retry/compensation controls.

## Troubleshooting

| Symptom | Likely Cause | Action |
|---------|--------------|--------|
| `UnknownExecutor` | Legacy CLI executor name provided (`claude`, `codex`, `gemini`) | Replace with API executor name (for example `api/claude-sonnet`) |
| `ExecutorTypeNotAllowed` | Non-API executor resolved for LLM stage | Register/select API executor in `UCX/executors.json` or call-level args |
| `ExecutorFailed` with non-zero `exit_code` | API provider/auth/network/runtime error | Check provider credentials/env keys, then retry with same run policy |
| `UnsupportedReviewMode` | Invalid `review_mode` value | Use `prompt_only` or `saga_parallel` |
| Saga review escalates (`saga_status=ESCALATED`) | Branch retry/timeout exhaustion or synthesis gate failure | Keep artifacts, escalate to human, rerun with adjusted saga controls |

## Integration with Existing Hermes SDD Skills

This skill works with UCX personas and optional Hermes-native skills:
- `business-analyst` — Use for BRD gap analysis after `sdd_validate`
- `qa_lead` persona — Use for testability review after `sdd_review` evidence is returned
- `auditor` persona — Use for compliance reasoning after `sdd_review` evidence
- `ucx-kb-context` — Use for retrieval enrichment before create/review/remediate calls when a KB server is available
- `ucx-kb-maintenance` — Use after approved IPLAN implementation evidence to update project knowledge under governance policy
- If Hermes-native skills exist in your environment (`sdd-orchestrator`, `sdd-cross-validation`), use them as optional overlays

## Error Handling

If UCX returns an error:
1. Log the tool name and arguments to Hermes memory
2. Present the error clearly to the human
3. Do not retry the same call blindly — ask human for direction
4. If `sdd_preflight` fails, stop and resolve environment issues before proceeding

## Migration Notes

This skill targets UCX Hermes runtime (`ucx_hermes/`) v2.0.0+ with API-only
executor support for LLM stages. If migrating from mixed CLI/API runtimes,
replace legacy executor names with API executor names and keep deterministic
stages executor-free.
