# Hermes Integration for UCX SDD Workflows

## What Changed

The UCX MCP server (`ucx_hermes`) has been patched to remove AI executor delegation
from document-critical tools. Previously, `sdd_review`, `sdd_remediate`,
`sdd_validate` (fix path), and `sdd_create_build` would spawn stateless CLI or
API AI agents to rewrite documents. This caused:

- **Context loss**: Each tool call spawned a fresh agent with no memory
- **Unverified rewrites**: AI output was written to files without structural validation
- **Bypassed human gates**: Documents could be auto-remediated without approval

## Patch Summary

### tool_registry.py changes

| Tool | Before | After |
|------|--------|-------|
| `sdd_validate` (fix path) | Spawned executor to auto-fix derived copy | Returns fix report text only; no AI rewrite |
| `sdd_create_build` | Spawned executor to generate content from template | Returns creation prompt and template; no AI generation |
| `sdd_review` | Spawned executor to perform multi-persona review | Returns assembled review prompt_text; Hermes/human performs review |
| `sdd_remediate` | Spawned executor to apply fixes to derived copy | Returns deterministic findings and fix instructions; no AI rewrite |

### What still works

- `sdd_validate` without `executor` — 100% deterministic structural validation
- `sdd_next_action` — folder inspection and stage recommendation
- `sdd_run_lifecycle` — pipeline orchestration (safe if no executor stages)
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
      |-- sdd_review: prompt assembler (no executor)
      |-- sdd_remediate: finding generator (no executor)
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

### 3. Project Setup

For each project using UCX:

```bash
# In project root
hermes chat
/skill ucx-sdd-bridge
Call sdd_init for this project
```

## Standard Workflow

Hermes is the default AI agent orchestrating this workflow from PR submission through merge-time escalation.

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
- Execution agents process only approved issues, then execute fix -> PR -> round-based governance gates -> deploy.
- Hermes validates post-deployment outcomes and closes issues when evidence is complete.

Detailed ownership split:

1. Hermes monitors observability signals through integrated telemetry systems and triage inputs.
2. Hermes opens and prioritizes GitHub issues with implementation traceability (`@spec`, `@tdd`, `@iplan`) and acceptance criteria.
3. Only approved issues (for example `ai:approved`) are eligible for autonomous execution.
4. Execution agents (Claude Code, Codex, OpenCode, or equivalent) perform fix implementation, PR submission, validation, and deployment workflows.
5. Hermes reviews post-deployment evidence and closes issues when monitoring and acceptance gates pass.

### PR Governance Sequence (Default)

```
1) Task defined (human or AI-originated)
2) Hermes creates GitHub issue with acceptance criteria and traceability tags
3) Work performed to resolve issue
4) PR submitted
5) Round 1: sdd_validate -> sdd_review -> sdd_remediate -> post-remediation sdd_validate -> Hermes final blocker-gap check
6) If Round 1 fails: run Round 2 with same sequence
7) If Round 2 fails: escalate to human review and block merge
8) If gates pass: merge PR and close linked issue(s)
```

Alert channels for human escalation are implementation-defined (TBD).

### Phase 1: Initialization

```
Hermes: sdd_init project=/opt/data/b-local/b-local-telegram-ui
UCX: Scaffolds UCX/ directory with templates, personas, layer aliases
Hermes: Confirm and show persona mappings
```

### Phase 2: Document Creation (Policy-Gated)

```
Operator/Agent: "Draft BRD for BEE-001"
Hermes: sdd_create_build doc_type=brd layer=01_BRD template=BRD-TEMPLATE
UCX: Returns creation prompt + template
Hermes: Reasons about prompt, drafts content using project memory
Hermes: Writes to ucx_flow_v3/01_BRD/BEE-001.md
Hermes: Applies configured gate policy for acceptance or escalation
```

### Phase 3: Structural Validation (Deterministic Gate)

```
Hermes: sdd_validate doc_type=brd layer=01_BRD document=BEE-001.md
UCX: Runs:
  - cross_section: traceability IDs, readiness scores, diagrams, tags
  - brd_rules: ADT propagation, phase alignment, entity consistency,
               currency scope, FR acceptance criteria, traceability links
UCX: Returns structured report: errors, warnings, passes
Hermes: Applies configured gate policy. If blocking errors persist, continue round handling or escalate.
```

### Phase 4: Expert Review (Hermes + Skills)

```
Operator/Agent: "Review for security and testability"
Hermes: sdd_review doc_type=brd document=BEE-001.md
UCX: Returns assembled multi-persona prompt (no executor run)
Hermes: Loads `auditor` + `qa_lead` persona guidance
Hermes: Uses prompt as context, applies skill knowledge, examines document
Hermes: Emits structured findings for policy evaluation and downstream remediation
```

### Phase 5: Remediation (Policy-Gated)

```
Operator/Agent: "Fix the 3 errors found"
Hermes: sdd_remediate doc_type=brd layer=01_BRD document=BEE-001.md
UCX: Returns deterministic findings with recommended actions
Hermes: Presents each finding with context and recommended fix
Hermes: Applies edits according to configured gate policy
Hermes: Re-runs sdd_validate to confirm
```

### Phase 6: Stage Advancement

```
Hermes: sdd_next_action document=ucx_flow_v3/01_BRD/BEE-001
UCX: Returns current_stage, next_action, next_tool
Hermes: Selects next layer action according to lifecycle state (for example PRD)
```

### Phase 7: Code Implementation Handoff (Code Generation Agent)

```
Operator/Agent: "IPLAN approved. Start implementation."
Hermes: Confirms IPLAN readiness and acceptance criteria coverage
Hermes: Hands implementation scope to selected coding agent using IPLAN tasks/contracts
Coding Agent: Implements code, tests, and local verification from IPLAN
Hermes: Collects implementation evidence and returns to UCX validation/review gates
```

### Phase 8: Observability-Driven Issue Loop

```
Observability Stack: Emits alert/event with service impact data
Hermes: Triages alert and creates GitHub issue with severity, repro context, and traceability links
Hermes: Applies approval gate (for example ai:approved)
Execution Agent: Fixes issue, submits PR, runs CI checks, and deploys through pipeline
Hermes: Verifies post-deploy monitoring and acceptance criteria, then closes issue
```

### Phase 9: Merge-Time Escalation

```
Hermes: Evaluates final-round gate outputs at merge decision time
If any blocking gate fails in Round 2: set escalation status REQUIRED
Hermes: Alert human developer (channel TBD)
Merge: blocked until human review resolves escalation or subsequent round passes
```

## Dangerous Patterns (Avoid)

| Pattern | Risk | Safe Alternative |
|---------|------|------------------|
| `sdd_validate ... executor=claude` | Auto-rewrite without validation | `sdd_validate` without executor |
| `sdd_review ... executor=claude` | Stateless review, context lost | `sdd_review` without executor, then Hermes reviews |
| `sdd_remediate ... executor=claude fix=true` | Unverified document rewrite | `sdd_remediate` without executor, then apply policy-gated remediation |
| `sdd_run_lifecycle stages=["validate","review","remediate"] executor=claude` | Pipeline runs unsafe stages | Stage-by-stage with deterministic and policy gates |
| Auto-applying remediation without gate policy | May introduce unresolved blocker gaps | Apply round gates and escalate on Round 2 failure |

## Tool Reference: Safe vs Unsafe

### Safe (Deterministic)

- `sdd_validate` (without executor)
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

### Unsafe (Disabled / Patched)

- `sdd_validate` (with executor parameter) — **patched to ignore**
- `sdd_create_build` (with executor) — **patched to ignore**
- `sdd_review` (with executor) — **patched to ignore**
- `sdd_remediate` (with executor) — **patched to ignore**

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

### "executor" parameter ignored

**Expected behavior.** The patched server deliberately ignores the `executor`
parameter on `sdd_validate`, `sdd_review`, `sdd_remediate`, and `sdd_create_build`.
You will receive prompt text or fix reports instead of AI-generated output.

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

Hermes should use this as context for reasoning, not pass it to another AI.

### How do I actually apply remediation fixes?

The patched `sdd_remediate` returns:
- `findings[]` with `priority`, `message`, `recommended_action`
- `fix_report_text` with step-by-step instructions

Hermes presents findings and applies the configured gate policy. On Round 2
blocking failure, Hermes escalates to human review; otherwise Hermes applies
edits and re-runs `sdd_validate` to confirm.

## Migration from Pre-Patched UCX

If you have an older UCX server:

1. Update to the patched version in `ucx_hermes/`
2. Remove any `executor` parameters from your Hermes prompts or scripts
3. Install the `ucx-sdd-bridge` skill
4. Test with `sdd_validate` on an existing document — should return structured
   JSON without spawning external processes

## Version Compatibility

| Component | Required Version |
|-----------|-----------------|
| UCX MCP Server | ucx_hermes v2.0.0+ |
| Hermes Agent | Any with MCP support |
| ucx-sdd-bridge skill | v1.0.0+ |
| Python | 3.11+ |

## Files Modified

- `src/mcp_server/tool_registry.py` — Removed `_maybe_run_executor()` calls from
  `sdd_validate` fix path, `sdd_create_build`, `sdd_review`, `sdd_remediate`

## Files Added

- `skills/hermes/ucx-sdd-bridge/SKILL.md` — Hermes bridge skill for safe UCX
  integration
- `docs/HERMES_INTEGRATION.md` — This document

## See Also

- `MCP_RUNTIME_ARCHITECTURE.md` — UCX server architecture
- `MCP_PERSONA_DESIGN_GUIDE.md` — Persona skill authoring
- `MCP_CLI_REFERENCE.md` — CLI tool reference
- `HERMES_UCX_RUNTIME_ENVIRONMENT.md` — Original runtime environment spec
