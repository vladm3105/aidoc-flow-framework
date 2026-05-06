# Hermes Integration for UCX SDD Workflows

## What Changed

The UCX MCP server (`ucx_hermes`) now enforces an API-only executor model
for LLM-enabled stages through LiteLLM. Deterministic stages do not invoke
executors. Legacy CLI executor paths are unsupported.

Previously, `sdd_review`, `sdd_remediate`, `sdd_validate` (fix path), and
`sdd_create_build` could be routed through stateless executor workflows that
caused:

- **Context loss**: Each tool call spawned a fresh agent with no memory
- **Unverified rewrites**: AI output was written to files without structural validation
- **Bypassed human gates**: Documents could be auto-remediated without approval

## Patch Summary

### tool_registry.py changes

| Tool | Before | After |
|------|--------|-------|
| `sdd_validate` (fix path) | Optional executor argument in legacy flows | Deterministic validation/fix artifacts; no executor path |
| `sdd_create_build` | Optional executor argument in legacy flows | Deterministic prompt/template assembly |
| `sdd_review` | Mixed CLI/API executor routing | API-only executor routing via LiteLLM |
| `sdd_remediate` | Mixed CLI/API executor routing | API-only executor routing via LiteLLM + deterministic findings/fix artifacts |

### What still works

- `sdd_validate` — 100% deterministic structural validation
- `sdd_next_action` — folder inspection and stage recommendation
- `sdd_run_lifecycle` — pipeline orchestration with API executor usage for LLM stages
- All scoring, scanning, consistency, link validation, preflight tools

## Architecture: Hermes + UCX

```
Human Engineer
      |
      v
Hermes Agent (stateful, conversational, memory)
      |-- Loads SDD persona guidance (business_analyst, qa_lead, auditor, etc.)
      |-- Maintains project context across turns
      |-- Reasons about findings, asks clarifying questions
      |
      v
UCX MCP Server (deterministic, rule-based)
      |-- sdd_validate: regex + YAML schema + template matching
      |-- sdd_review: prompt assembly + API executor stage
      |-- sdd_remediate: deterministic findings + fix artifacts + API executor stage
      |-- sdd_create_build: prompt + template assembler (no executor)
      |
      v
Document Artifacts (ucx_flow_v3/)
```

## Configuration

### 1. Hermes MCP Config

In `~/.hermes/.mcp.json`:

```json
{
  "mcpServers": {
    "sdd-lifecycle": {
      "command": "/opt/data/ucx_framework/.venv/bin/python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/opt/data/ucx_framework/ucx_hermes/src"
    }
  }
}
```

### 2. Hermes Skills

Install the bridge skill into Hermes:

```bash
cp -r /opt/data/ucx_framework/ucx_hermes/skills/hermes/ucx-sdd-bridge \
  ~/.hermes/skills/
```

Enable bridge skill, then load personas/skills available in your Hermes environment:

```bash
hermes skills enable ucx-sdd-bridge
hermes skills enable business-analyst
# Optional if installed in Hermes runtime:
# hermes skills enable sdd-orchestrator
# hermes skills enable sdd-cross-validation
```

Skill version note:

- Use `ucx-sdd-bridge` `v1.1.1+` for API-only executor guidance,
  fan-out/fan-in (`saga_parallel`) review controls, and executor troubleshooting.
- Optional KB skills:
  - `ucx-kb-context` for retrieval enrichment during UCX V3 lifecycle stages
  - `ucx-kb-maintenance` for post-IPLAN knowledge updates with governance controls
  - `ucx-kb-maintenance/KB_GENERAL_RULES.md` for mandatory coverage and ingestion policy across all document artifacts
  - `ucx-kb-maintenance/KB_ENTRY_TEMPLATE.md` for KB admission checklist and canonical entry structure
- Governance skills:
  - `ucx-github-governance` for issue/PR label flow and round-based merge governance
  - `ucx-github-deploy-governance` for CI/CD, QA, staging/prod readiness, and post-deploy issue loops

Skill activation matrix:

| Scenario | Primary Skill | Optional Companion | Notes |
|----------|---------------|--------------------|-------|
| BRD->IPLAN lifecycle orchestration in `ucx_flow_v3` | `ucx-sdd-bridge` | `ucx-kb-context` | Keep document-layer flow MCP-only; do not use CLI lifecycle commands. |
| Multi-persona review with fan-out/fan-in (`review_mode=saga_parallel`) | `ucx-sdd-bridge` | `ucx-kb-context` | Use KB retrieval before review for prior findings/constraints. |
| Remediation planning and policy-gated apply | `ucx-sdd-bridge` | `ucx-kb-context` | Use API executor for `sdd_remediate`; use KB for accepted remediation patterns. |
| Post-IPLAN implementation knowledge capture | `ucx-kb-maintenance` | `ucx-sdd-bridge` | Run after approved implementation evidence; KB updates do not advance lifecycle stages. |
| KB unavailable or stale | `ucx-sdd-bridge` | none | Continue lifecycle gates; log reduced-confidence context and escalate high-impact assumptions. |

### 3. Project Setup

For each project using UCX:

```bash
# 1) Start Hermes session
hermes chat

# 2) Enable UCX bridge skill in the Hermes session
/skill ucx-sdd-bridge

# 3) Initialize project-scoped UCX assets (required once per project)
sdd_init project=/absolute/path/to/project

# 4) Verify runtime readiness for this project
sdd_preflight project=/absolute/path/to/project context=any

# 5) (Optional) inspect project persona mappings and environment keys
sdd_personas_show project=/absolute/path/to/project
sdd_env_show project=/absolute/path/to/project
```

Initialization contract:

- `sdd_init` is idempotent in default mode; existing project files are not overwritten.
- Use `update=true` to sync stale framework-owned files.
- Use `update=true` and `update_mappings=true` to reset `persona_mappings.yaml`.
- `update_mappings=true` without `update=true` is invalid.

Preflight pass criteria (`sdd_preflight context=any`):

- **Go**: status `ready` (exit code 0).
- **Conditional go**: status `degraded` (exit code 0) with documented risk acceptance and no missing required project assets.
- **No-go**: status `blocked` (exit code 1).
- **Operational error**: command runtime error (exit code 2), treat as no-go until corrected.

Minimum checks before first lifecycle run:

- `UCX/` scaffold exists for the target project.
- `persona_mappings.yaml` exists and persona mapping health check does not report missing persona files.
- Required executor environment keys are present for the configured provider path.

### 4. KB Preflight and Degraded Mode

Framework baseline:

- Keep framework MCP config minimal (`sdd-lifecycle` only).
- Register `project-knowledge` only in a real project runtime where `ucx_kb` is initialized.

Project-level MCP registration snippet (add in project runtime config):

```json
{
  "mcpServers": {
    "project-knowledge": {
      "command": "/opt/data/ucx_framework/.venv/bin/python",
      "args": ["-m", "ucx_kb.mcp.server"],
      "cwd": "/opt/data/ucx_framework"
    }
  }
}
```

Before lifecycle calls that depend on KB context:

1. Call `kb_status`.
2. Call `kb_graph_status`.
3. Determine KB mode:
   - `ready`: both calls succeed.
   - `degraded`: one call fails.
   - `unavailable`: both calls fail.

If mode is `degraded` or `unavailable`, continue UCX lifecycle gates and record reduced-confidence reasoning notes. Do not block stage progression due to KB availability.

### 5. KB Smoke Test (Operator Runbook)

Run from `/opt/data/ucx_framework` after DB services are up and `.env` is configured for `ucx_kb`:

```bash
python -m ucx_kb.mcp.server
```

In Hermes session, verify these calls succeed:

- `kb_status` (RAG status payload)
- `kb_graph_status` (graph status payload)
- `kb_search` with a small query (result or empty result without error)

Pass criteria:

- No MCP server startup exception
- No tool contract error for the three calls above
- Hermes can continue `sdd_*` lifecycle calls regardless of KB result cardinality

## Standard Workflow

Hermes is the default AI agent orchestrating this workflow from PR submission through merge-time escalation.

UCX V3 boundary:

- Use UCX MCP tools for `ucx_flow_v3` document-layer lifecycle work (BRD through IPLAN).
- Do not use CLI lifecycle commands for document-layer stages.
- CLI usage is reserved for approved IPLAN implementation execution tasks (tests, source code changes, and implementation documentation updates).
- No lifecycle-stage document creation starts before planning-first artifacts are reviewed and approved.

### Parallel Persona Review Saga (Planned)

For multi-persona review runs, Hermes can use a Saga fan-out/fan-in mode:

1. fan out persona branches in bounded parallel execution
2. apply branch-level retry and compensation on failures
3. merge findings with deterministic reducer behavior
4. run chairperson synthesis and continue governance gates

Reference:

- `docs/architecture/MCP_SAGA_ORCHESTRATION_PATTERN.md`
- `docs/plans/IPLAN-006_parallel_persona_review_saga_orchestration.md`

### Recommended Delivery Pattern

Use this default split for implementation work:

- Hermes: BRD through IPLAN (control plane)
- Claude Code, Codex, or another code-generation agent: code implementation from approved IPLAN (execution plane)
- Hermes: post-implementation validation/review gates

Issue-fix, PR governance, and deployment pattern:

- Observability stack emits incidents, anomalies, and SLO/SLA alerts.
- Hermes triages signal severity and creates GitHub issues with traceability references and acceptance criteria.
- Execution agents process only issues in `ai:ready`, then execute fix -> PR -> round-based governance gates -> deploy.
- Hermes validates post-deployment outcomes and closes issues when evidence is complete.

Detailed ownership split:

1. Hermes monitors observability signals through integrated telemetry systems and triage inputs.
2. Hermes opens and prioritizes GitHub issues with implementation traceability (`@spec`, `@tdd`, `@iplan`) and acceptance criteria.
3. Only `ai:ready` issues are eligible for autonomous execution.
4. Execution agents (Claude Code, Codex, OpenCode, or equivalent) perform fix implementation, PR submission, validation, and deployment workflows.
5. Hermes reviews post-deployment evidence and closes issues when monitoring and acceptance gates pass.

### PR Governance Sequence (Default)

```
1) Task defined (human or AI-originated)
2) Hermes creates planning-first artifacts (layer roadmap, planning index, changelog plan)
3) Hermes reviews planning artifacts for gaps and records closure or explicit deferral
4) Hermes creates per-document IPLAN artifacts and records approval (human reviewer or independent LLM-as-judge session)
5) Hermes creates GitHub issue with acceptance criteria and traceability tags
6) Work performed to resolve issue according to approved plans
7) PR submitted
8) Round 1: sdd_validate -> sdd_review -> sdd_remediate -> post-remediation sdd_validate -> Hermes final blocker-gap check
9) If Round 1 fails: run Round 2 with same sequence
10) If Round 2 fails: escalate to human review and block merge
11) If gates pass: merge PR and close linked issue(s)
```

Alert channels for human escalation are implementation-defined (TBD).

### Phase 1: Planning-First Governance

```
Operator/Agent: "Start BRD layer planning"
Hermes: Analyzes provided sources, constraints, and dependencies
Hermes: Produces layer roadmap, planning index, and changelog plan artifacts
Hermes: Reviews planning artifacts for gaps and resolves or defers with explicit rationale
Hermes: Produces per-document IPLAN artifacts and records plan approval
Hermes: Blocks document creation until approval exists
```

### Phase 2: Initialization

```
Hermes: sdd_init project=/opt/data/b-local/b-local-telegram-ui
UCX: Scaffolds UCX/ directory with templates, personas, layer aliases
Hermes: Confirm and show persona mappings
```

### Phase 3: Document Creation (Policy-Gated)

```
Operator/Agent: "Draft BRD for BEE-001"
Hermes: sdd_create_build doc_type=brd layer=01_BRD template=BRD-TEMPLATE
UCX: Returns creation prompt + template
Hermes: Reasons about prompt, drafts content using project memory
Hermes: Writes to ucx_flow_v3/01_BRD/BEE-001.md
Hermes: Applies configured gate policy for acceptance or escalation
```

### Phase 4: Structural Validation (Deterministic Gate)

```
Hermes: sdd_validate doc_type=brd layer=01_BRD document=BEE-001.md
UCX: Runs:
  - cross_section: traceability IDs, readiness scores, diagrams, tags
  - brd_rules: ADT propagation, phase alignment, entity consistency,
               currency scope, FR acceptance criteria, traceability links
UCX: Returns structured report: errors, warnings, passes
Hermes: Applies configured gate policy. If blocking errors persist, continue round handling or escalate.
```

### Phase 5: Expert Review (Hermes + Skills)

```
Operator/Agent: "Review for security and testability"
Hermes: sdd_review doc_type=brd document=BEE-001.md
UCX: Assembles review prompt and invokes configured API executor
Hermes: Loads `auditor` + `qa_lead` persona guidance
Hermes: Uses prompt as context, applies skill knowledge, examines document
Hermes: Emits structured findings for policy evaluation and downstream remediation
```

### Phase 6: Remediation (Policy-Gated)

```
Operator/Agent: "Fix the 3 errors found"
Hermes: sdd_remediate doc_type=brd layer=01_BRD document=BEE-001.md executor=api/claude-sonnet
UCX: Generates deterministic findings and fix artifacts, then invokes API executor for apply stage
Hermes: Reviews findings, applies gate policy, and verifies remediation quality signals
Hermes: Re-runs sdd_validate to confirm
```

### Phase 7: Stage Advancement

```
Hermes: sdd_next_action document=ucx_flow_v3/01_BRD/BEE-001
UCX: Returns current_stage, next_action, next_tool
Hermes: Selects next layer action according to lifecycle state (for example PRD)
```

### Phase 8: Code Implementation Handoff (Code Generation Agent)

```
Operator/Agent: "IPLAN approved. Start implementation."
Hermes: Confirms IPLAN readiness and acceptance criteria coverage
Hermes: Hands implementation scope to selected coding agent using IPLAN tasks/contracts
Coding Agent: Implements code, tests, and local verification from IPLAN
Hermes: Collects implementation evidence and returns to UCX validation/review gates
```

### Phase 9: Observability-Driven Issue Loop

```
Observability Stack: Emits alert/event with service impact data
Hermes: Triages alert and creates GitHub issue with severity, repro context, and traceability links
Hermes: Applies governance approval gate and transitions executable issues to `ai:ready`
Execution Agent: Fixes issue, submits PR, runs CI checks, and deploys through pipeline
Hermes: Verifies post-deploy monitoring and acceptance criteria, then closes issue
```

### Phase 10: Merge-Time Escalation

```
Hermes: Evaluates final-round gate outputs at merge decision time
If any blocking gate fails in Round 2: set escalation status REQUIRED
Hermes: Alert human developer (channel TBD)
Merge: blocked until human review resolves escalation or subsequent round passes
```

## Dangerous Patterns (Avoid)

| Pattern | Risk | Safe Alternative |
|---------|------|------------------|
| `sdd_validate ... executor=claude` | Unsupported parameter/path | `sdd_validate` |
| `sdd_review ... executor=claude` | Unknown executor (CLI not supported) | Use API executor (`api/openrouter` or project API override) |
| `sdd_remediate ... executor=claude fix=true` | Unknown executor (CLI not supported) | Use API executor (`api/claude-sonnet` or project API override) |
| `sdd_run_lifecycle ... executor=claude` | Unknown executor in review/remediate stages | Use API executor names for LLM stages |
| Auto-applying remediation without gate policy | May introduce unresolved blocker gaps | Apply round gates and escalate on Round 2 failure |

## Tool Reference: Safe vs Unsafe

### Safe (Deterministic)

- `sdd_validate`
- `sdd_validate_chg`
- `sdd_consistency`
- `sdd_validate_links`
- `sdd_preflight`
- `sdd_scan`
- `sdd_score_show`
- `sdd_score_validate`
- `sdd_score_compare`
- `sdd_next_action`
- `sdd_clean`
- `sdd_init`
- `sdd_personas_show/set/diff`
- `sdd_env_show`
- `sdd_prescreen`
- `sdd_list_executors`
- `sdd_register_executor`

### LLM Stages (API Executor Required)

- `sdd_review` (requires API executor)
- `sdd_remediate` (requires API executor)

## Hermes Memory State

Track project state in Hermes memory for continuity:

```
[UCX Project State]
Project: BeeLocal
Root: /opt/data/b-local/b-local-telegram-ui
Active document: BEE-001
Current layer: 01_BRD
Current stage: validated
Last validation: 2026-05-02 (0 errors, 1 warning)
Next action: review
```

## Troubleshooting

### Unknown executor error for `claude`/`codex`

**Expected behavior.** The runtime does not support CLI executors.
Use API executor names such as `api/openrouter`, `api/claude-sonnet`,
or project API overrides from `UCX/executors.json`.

### Validation report shows errors I already fixed

Hermes should re-run `sdd_validate` after each edit. If errors persist:
1. Check the exact error message — it may be a new error introduced by the fix
2. Verify file was saved to the correct path
3. Run `sdd_preflight` to check for environment issues

### sdd_review returns a huge prompt_text

This is correct. The prompt contains:
- Document content broken into sections
- Persona instructions from `UCX/skills/personas/`
- Layer assets and templates

The response may include `prompt_text` for traceability and reproducibility. Treat it as audit context and preserve it in stage artifacts when required by policy.

### How do I actually apply remediation fixes?

`sdd_remediate` returns:
- `findings[]` with `priority`, `message`, `recommended_action`
- `fix_report_text` with step-by-step instructions
- API executor output/exit status for the remediation apply stage

Hermes presents findings and applies the configured gate policy. On Round 2
blocking failure, Hermes escalates to human review; otherwise Hermes applies
edits and re-runs `sdd_validate` to confirm.

## Migration from Pre-UCX V3 Runtime

If you are migrating from a pre-UCX V3 runtime:

1. Update to UCX V3 runtime in `ucx_hermes/`
2. Replace any legacy CLI executor names with API executor names in scripts
3. Install the `ucx-sdd-bridge` skill
4. Test with `sdd_validate` on an existing document — should return structured
   JSON without spawning external processes

## Version Compatibility

| Component | Required Version |
|-----------|-----------------|
| UCX MCP Server | ucx_hermes v2.0.0+ |
| Hermes Agent | Any with MCP support |
| ucx-sdd-bridge skill | v1.1.1+ |
| Python | 3.11+ |

## Files Modified

- `src/mcp_server/tool_registry.py` — Enforced API-only executor behavior for
  LLM stages (`sdd_review`, `sdd_remediate`) and deterministic behavior for
  non-LLM stages (`sdd_validate`, `sdd_create_build`)

## Files Added

- `skills/hermes/ucx-sdd-bridge/SKILL.md` — Hermes bridge skill for safe UCX
  integration
- `docs/HERMES_INTEGRATION.md` — This document

## See Also

- `MCP_RUNTIME_ARCHITECTURE.md` — UCX server architecture
- `MCP_PERSONA_DESIGN_GUIDE.md` — Persona skill authoring
- `MCP_CLI_REFERENCE.md` — CLI tool reference
- `HERMES_UCX_RUNTIME_ENVIRONMENT.md` — Original runtime environment spec
