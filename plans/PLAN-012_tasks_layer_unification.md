# PLAN-012: TASKS Layer Unification — FINAL LAYER

**Status**: Complete
**Created**: 2026-03-30
**Scope**: Unify TASKS (Layer 11) into single YAML template — completes ALL SDD layers
**Depends on**: Layers 1-10 unified (v0.2.0-v0.11.0)
**Risk**: Low — follows proven pattern, but TASKS is unique (code-generation guide)

---

## Problem

TASKS layer has the standard dual-file pattern plus implementation plan templates:

### Core files to consolidate

| File | Lines | Role |
|------|-------|------|
| `TASKS-MVP-TEMPLATE.md` | 436 | Human narrative template (13 sections + extras) |
| `TASKS-MVP-TEMPLATE.yaml` | 468 | YAML template for autopilot |
| `TASKS_MVP_SCHEMA.yaml` | 476 | Validation schema |
| `TASKS_MVP_CREATION_RULES.md` | 744 | Authoring guidance |
| `TASKS_MVP_VALIDATION_RULES.md` | 548 | Validation rules |
| `TASKS_MVP_QUALITY_GATE_VALIDATION.md` | 532 | Quality gates |
| **Total** | **3,204** | 6 core files |

### Implementation Plan templates (KEEP ACTIVE — separate concern)

| File | Lines | Role | Action |
|------|-------|------|--------|
| `IMPLEMENTATION_PLAN_README.md` | 492 | Development Plan tracking guide | **KEEP** — project-level orchestrator guide |
| `IMPLEMENTATION_PLAN_TEMPLATE.md` | 261 | Central command center template | **KEEP** — project-level orchestrator |
| `IMPLEMENTATION_PLAN_TEMPLATE.yaml` | 158 | Phase tracking YAML structure | **KEEP** — project-level orchestrator |
| `TASKS_IMPLEMENTATION_GUIDE.md` | 65 | Workflow guide | **ARCHIVE** — embed key concepts in `_guidance` |

**NOTE**: IMPLEMENTATION_PLAN is a project-level orchestrator (one per project) that
organizes multiple TASKS into phased execution. It is NOT a per-task template.
TASKS-TEMPLATE.yaml is the per-task specification. Both are needed.

### Additionally to archive

| File | Lines | Reason |
|------|-------|--------|
| `TASKS-MVP-TEMPLATE_FIX_PLAN.md` | 550 | Completed gap analysis |
| `TASKS-00_TRACEABILITY_MATRIX-TEMPLATE.md` | 413 | Redundant |
| `TASKS_AI_VALIDATION_DECISION_GUIDE.md` | 66 | Scaffold |
| `TASKS_VALIDATION_STRATEGY.md` | 66 | References scripts |
| `TASKS_VALIDATION_COMMANDS.md` | 59 | References scripts |
| `TASKS-TEMPLATE.md` | — | Symlink (will break after archiving target) |
| `TASKS_IMPLEMENTATION_GUIDE.md` | 65 | Key concepts embedded as `_guidance` |
| `examples/` | 295 | Old format |
| `scripts/` (9 files) | — | Validation via mcp_ucx |
| `README.md` | 675 | Old version |

---

## What Makes TASKS Unique (Code-Generation Bridge)

TASKS is NOT a standard documentation layer — it's the **AI agent's implementation guide**:

1. **Execution Commands** (Section 4): Runnable bash/shell commands for environment
   setup, implementation, and validation. No other layer has executable commands.

2. **Implementation Contracts** (Section 7): Defines Protocol/ABC interfaces, Pydantic
   models, and dependency contracts for contract-first parallel development.

3. **Development Plan Tracking**: Embedded YAML with pre/post-execution verification
   checklists that enforce workflow discipline. Pre-check includes **full upstream
   chain verification** (BRD→PRD→EARS→BDD→ADR→SYS→REQ→CTR→SPEC→TSPEC) — the AI
   agent must verify all 10 upstream layers are complete before generating code.

4. **Phased Implementation Plan** (Section 3): Multi-phase breakdown with task
   dependencies, deliverables, acceptance criteria, and duration estimates.

5. **Session Log** (Section 12): Per-day progress tracking for audit trail and continuity.

6. **Execution-Ready Score**: >=90/100 required before code generation handoff.

7. **Complete Traceability** (Section 8): Links to ALL 10 upstream layers + downstream
   code/test file paths (@impl, @code, @tests). Unlike other layers, TASKS downstream
   is actual source files — not another SDD layer.

8. **Session Handoff Protocol**: File-based state tracking for stateless MCP executor
   calls. Each CLI agent call is independent — handoff state lives in the TASKS
   document itself, not in session memory. Prevents:
   - Regenerating already-completed code (token waste)
   - Missing partially-created files (bugs)
   - Overwriting working code from previous session

   Handoff state includes:
   - Per-step completion markers (NOT_STARTED | IN_PROGRESS | COMPLETED | PARTIAL)
   - Code inventory: files created/modified with verification commands
   - Test state: last run results, pass/fail counts, coverage
   - Partial work marker: exactly what's incomplete if session ended mid-step
   - Resume directive: what the next executor call should do first

---

## C4 Model Position

TASKS is NOT a C4 level. It bridges Code (SPEC) to actual source code implementation.

```text
Code (SPEC)      — implementation-ready specifications
  └─ TSPEC       — test specifications (validates SPEC)
  └─ TASKS       — AI implementation guide (execution bridge)     ← this layer
       └─ Source Code + Tests
```

No `c4_level.value` — use `_guidance` only.

---

## Target State

```text
11_TASKS/
├── TASKS-TEMPLATE.yaml                  ← per-task spec template (13 sections)
├── IMPLEMENTATION_PLAN_TEMPLATE.md      ← project orchestrator (keep active)
├── IMPLEMENTATION_PLAN_TEMPLATE.yaml    ← project orchestrator YAML (keep active)
├── IMPLEMENTATION_PLAN_README.md        ← orchestrator guide (keep active)
├── TASKS-00_index.md                    ← TASKS registry
├── README.md                            ← new, concise (~100 lines)
└── TASKS_v1_archive/                    ← deprecated template/rules/scripts files
```

---

## Phase 1: Section Analysis

TASKS has 13 content sections + Document Control + Development Plan Tracking.
All are TASKS-layer concerns — minimal removal needed.

### Proposed structure: 2 pre-content + 13 numbered sections + glossary (16 total)

| # | Section | Content |
|---|---------|---------|
| — | Document Control | Metadata, Execution-Ready score, effort tracking |
| — | Development Plan Tracking | YAML pre/post-execution checklists with full upstream chain verification |
| 1 | Objective | What implementation accomplishes, deliverables, business value |
| 2 | Scope | Inclusions, exclusions, prerequisites |
| 3 | Implementation Plan | Phased breakdown with dependencies and deliverables |
| 4 | Execution Commands | Bash/shell commands for setup, implementation, validation |
| 5 | Constraints | Technical, quality, performance constraints |
| 6 | Acceptance Criteria | Functional, quality, operational criteria |
| 7 | Implementation Contracts | Protocols provided/consumed, data models |
| 8 | Traceability | All upstream tags + downstream @impl/@code/@tests |
| 9 | Risk & Mitigation | Risk matrix with mitigation strategies |
| 10 | Unit Test Results | Test suite results and coverage metrics |
| 11 | Implementation Summary | Accomplishments, issues, remaining work |
| 12 | Session Log | Per-day progress tracking |
| 13 | Change History | Version control audit trail |
| — | Glossary | Flat terms list |

No sections removed. TASKS needs all 13 for the code-generation workflow.

---

## Phase 2: Create TASKS-TEMPLATE.yaml

- `metadata.c4_level`: `_guidance` only (execution bridge, no C4 level)
- `metadata.diagram_standard`: no diagram tags (implementation level)
- `metadata.validation.tool: sdd_validate` / `server: mcp_ucx`
- `metadata.id_standard`: `{doc_type}.{doc_id}.{section_id}.{hash}`, SHA256
- `document_control.execution_ready_score` (>=90/100 for code generation)

### TASKS-specific `_guidance` to embed

**CRITICAL**: TASKS creation rules have unique content not found in other layers.
The SPEC dependency analysis and implementation contracts guidance must be embedded
thoroughly — these gate code generation quality.

| Source | Embed in | Content | Priority |
|--------|----------|---------|----------|
| Creation Rules §0: SPEC dependency analysis | `implementation_plan._guidance` | MANDATORY first step — inventory SPECs, extract deps, topological sort, parallelizable phases | **CRITICAL** |
| Creation Rules §5: Phase breakdown | `implementation_plan._guidance` | 4-phase structure with dependencies, deliverables, duration | HIGH |
| Creation Rules §8: Implementation contracts | `implementation_contracts._guidance` | Protocol/ABC, Pydantic, DI, state machines, exception hierarchies | **CRITICAL** |
| Creation Rules §4: Execution command format | `execution_commands._guidance` | Bash patterns for setup, implementation, validation | HIGH |
| Creation Rules §9: Traceability tags | `traceability._guidance` | 8-10 cumulative tags (most of any layer) | HIGH |
| Creation Rules §12: Quality checklist | `document_control._guidance` | 13-section verification checklist | HIGH |
| Full upstream chain verification | `development_plan._guidance` | Pre-check must verify ALL 10 upstream layers (BRD→PRD→EARS→BDD→ADR→SYS→REQ→CTR→SPEC→TSPEC) are complete before code generation | **CRITICAL** |
| Creation Rules §13: Anti-patterns | `_antipatterns` in relevant sections | Vague scope, unclear steps, missing constraints | MEDIUM |
| Validation Rules: Execution-Ready scoring | `metadata.validation._guidance` | Score rubric, >=90/100 threshold | **CRITICAL** |
| Validation Rules: 13-section completeness | `metadata.validation._guidance` | All sections required, no placeholders | HIGH |
| Implementation Guide (archived) | `development_plan._guidance` | Workflow concepts, cross-ref to IMPLEMENTATION_PLAN_TEMPLATE | MEDIUM |
| Session handoff protocol | `session_log._guidance` + `implementation_plan._guidance` | File-based handoff for stateless MCP calls: per-step markers, code inventory, test state, partial work marker, resume directive | **CRITICAL** |

### Element ID Format

```text
Format: TASKS.{doc_id}.{section_id}.{hash}
Example: TASKS.01.03.g7k2
```

### Traceability (ALL upstream layers → Code)

```yaml
traceability:
  tags:
    - "@tasks: TASKS-NN"
  upstream:
    - "@spec: SPEC.NN.05.xxxx"
    - "@tspec: TSPEC.NN.04.xxxx"
    - "@req: REQ.NN.03.xxxx"
    - "@ctr: CTR.NN.05.xxxx"
    - "@sys: SYS.NN.04.xxxx"
    - "@adr: ADR.NN.03.xxxx"
    - "@bdd: BDD.NN.03.xxxx"
    - "@ears: EARS.NN.03.xxxx"
    - "@prd: PRD.NN.09.xxxx"
    - "@brd: BRD.NN.07.xxxx"
  downstream:
    - "@impl: src/module/component.py"
    - "@code: src/module/"
    - "@tests: tests/unit/test_component.py"
```

---

## Phase 3-8: Standard Execution

- Phase 3: Archive to `TASKS_v1_archive/` (remove symlink, consolidate existing `archive/` dir)
- Phase 4: Update `TASKS-00_index.md`
- Phase 5: Create new `README.md` (emphasize code-generation guide role)
- Phase 6: Copy `TASKS-TEMPLATE.yaml` to `mcp_ucx/templates/` (NEW — completes 11 templates).
  mcp_ucx is the agent-agnostic execution layer — any CLI agent (Claude, Codex, Gemini,
  OpenCode, Copilot) can call `sdd_create` with `doc_type=tasks, layer=11_TASKS`.
  Claude skills (doc-tasks, etc.) are one client of mcp_ucx, not the only one.
- Phase 7: Cross-ref updates:
  - SPEC/TSPEC downstream TASKS descriptions verified
  - BRD-00_GLOSSARY.md: add TASKS definition
  - MCP Ops Doc: update "not yet migrated (TASKS)" → all layers complete
- Phase 8: Tests, changelog v0.12.0, roadmap — MILESTONE: ALL 11 LAYERS COMPLETE

**Note**: No mcp_ucx creation/review/remediation prompts exist for TASKS.
Claude skills (doc-tasks, etc.) handle TASKS lifecycle directly. mcp_ucx serves
the template via `sdd_create` but UCC/UCR/UCRem prompts are future work.

---

## Key Differences

| Aspect | Layers 1-10 | TASKS |
|--------|-----------|-------|
| Purpose | Documentation/specification | **Code generation guide** |
| Sections | 5-15 | **13** (none removable) |
| Executable content | None | **Bash commands** (Section 4) |
| Contracts | None | **Implementation contracts** (Section 7) |
| Session tracking | None | **Session log** (Section 12) |
| Workflow enforcement | None | **Development Plan Tracking** (pre/post checks) |
| Downstream | Next layer | **Source code + tests** |
| C4 level | Various/none | None (execution bridge) |
| Readiness score | Various | **Execution-Ready** (>=90/100) |
| Session handoff | None | **File-based handoff protocol** for stateless MCP calls |
| Upstream verification | Partial | **Full 10-layer chain** verification before code generation |

---

## Decisions (Resolved)

1. **All 13 sections kept**: TASKS needs every section for the code-generation workflow.
2. **Implementation Plan templates**: KEEP ACTIVE as separate files (project-level orchestrator).
   Cross-reference from TASKS-TEMPLATE.yaml `_guidance` field.
3. **Symlink**: Remove `TASKS-TEMPLATE.md` symlink (target will be archived).
4. **No diagram tags**: TASKS operates at implementation level, not architecture.
5. **mcp_ucx**: NEW template — completes the full set of 11 unified YAML templates.
   TASKS template goes into `mcp_ucx/templates/` so ANY CLI AI agent can use it
   via the executor registry. Claude skills (doc-tasks, etc.) are one client of mcp_ucx.
6. **MILESTONE**: This is the FINAL layer. After TASKS, all SDD layers are unified.
