---
name: sdd-orchestrator
description: "Orchestrate SDD v3.2 workflows across 8 layers (BRD→PRD→EARS→BDD→ADR→SPEC→TDD→IPLAN) using 15 specialized review personas dispatched as parallel subagents."
version: 2.0.0
metadata:
  hermes:
    tags: [sdd, orchestration, workflow, review, creation, remediation]
    related_skills:
      - sdd-review-personas
      - sdd-naming-standards
      - sdd-cross-validation
      - hermes-agent
---

# SDD Orchestrator — Specification-Driven Development Workflow Engine

## Overview

You orchestrate the SDD v3.2 lifecycle across 8 document layers using 15 expert persona subagents. Unlike the legacy UCX system that concatenated all persona texts into a single prompt, you dispatch personas as **parallel subagents** for concurrent review.

### Mandatory Governance Load (Before Any SDD Work)

Before creating, reviewing, or remediating ANY SDD document, load the governance protocol:

```
skill_view(name='sdd-orchestrator', file_path='references/governance-load-protocol.md')
```

This single file condenses the planning-first rules from GOVERANCE_RULES.md §2b/§3, DEFINITION_OF_DONE.md plan/IPLAN review level, and DEVELOPMENT_WORKFLOW_GUIDE.md §2. **Skip this load step = governance violation.**

If the protocol file is missing or stale (after a UCX framework sync), fall back to loading the three governance docs individually via:

```
skill_view(name='sdd-orchestrator', file_path='governance/GOVERNANCE_RULES.md')
skill_view(name='sdd-orchestrator', file_path='governance/DEFINITION_OF_DONE.md')
skill_view(name='sdd-orchestrator', file_path='governance/DEVELOPMENT_WORKFLOW_GUIDE.md')
```

These docs contain the planning-first gates (§3), Definition of Done for plan/IPLAN review level,
depth model selection, plan types and storage rules (§2b), and the full agent operating model.

Governance docs are read **directly from the repository** (`framework/` tree); per D-0013 (aidoc-flow migration), there is no local sync — re-stale-checks are not needed.

## SDD Layer Sequence (v3.2)

```
BRD (L1) → PRD (L2) → EARS (L3) → BDD (L4) → ADR (L5) → SPEC (L6) → TDD (L7) → IPLAN (L8) → Code
```

### Layer Descriptions

| Layer | Artifact | Purpose | Upstream | Downstream |
|-------|----------|---------|----------|------------|
| L1 | BRD | Business requirements, objectives, scope | — | PRD |
| L2 | PRD | Product features, user stories, ADR topics | BRD | EARS |
| L3 | EARS | Formal requirements (WHEN-THE-SHALL-WITHIN) | BRD, PRD | BDD |
| L4 | BDD | Executable acceptance scenarios with spec_trace | BRD, PRD, EARS | ADR |
| L5 | ADR | Architecture decisions (Context-Decision-Consequences) | BRD, PRD, EARS, BDD | SPEC |
| L6 | SPEC | Component interfaces, data models, behavior contracts | BRD, PRD, EARS, BDD, ADR | TDD |
| L7 | TDD | Test case definitions, BDD-to-test mapping, quality thresholds | BRD through SPEC | IPLAN |
| L8 | IPLAN | Execution plan: file manifest, bash commands, session handoff | BRD through TDD | Code |

### What Was Cut from v2

| Cut | Replaced By |
|-----|-------------|
| SYS (L6) | ADR captures architecture; PRD captures scope |
| REQ (L7) | EARS + BDD spec_trace provide requirement-to-spec links |
| CTR (L8) | SPEC interface contracts handled inline |
| TSPEC (L10) | TDD (L7) with embedded test case definitions |
| TASKS (L11) | IPLAN (L8) execution bridge with session handoff |

## Persona Name Mapping (UCX → Hermes Skill)

| UCX Name | Hermes Skill Name |
|----------|-------------------|
| architect | system-architect |
| auditor | security-auditor |
| tech_lead | technical-lead |
| strategist | business-strategist |
| chaos_engineer | chaos-engineer |
| operator | site-reliability-engineer |
| integration_lead | integration-specialist |
| product_owner | product-owner |
| business_analyst | business-analyst |
| fact_checker | fact-checker |
| chairperson | board-chairperson |
| qa_lead | qa-lead |
| content_strategist | content-strategist |
| requirements_specialist | requirements-specialist |
| ux_strategist | ux-strategist |

---

---

## Hermes Agent as SDD Strategy Execution Runtime

When the SDD pipeline defines an autonomous strategy (trading agent, monitoring system, etc.), Hermes Agent can serve as the runtime orchestrator instead of building a custom execution engine. This replaces the traditional IPLAN→Code execution path with Hermes-native scheduling, MCP integration, and skill-based rule execution.

Pattern documented in: `references/hermes-agent-sdd-runtime-pattern.md`

Key integration points:

- **cronjob**: Schedule check windows at precise times (market hours, daily scans)
- **skills**: Load SDD documents as decision rules — soft updates via skill patches
- **MCP servers**: Register broker/external system MCP servers as Hermes tools
- **memory**: Persist state across sessions (positions, account data, idempotency keys)
- **gateway**: Multi-platform operator alerts (Telegram, Discord, etc.)

Cost comparison: ~1 developer-week + $5-10/month (LLM inference) vs 4-6 developer-weeks + $200/month for custom orchestrator.

See ADR-21 for a complete implementation example (TradeGent CC).

**NO SDD DOCUMENT MAY BE CREATED, REVIEWED, OR REMEDIATED WITHOUT A WRITTEN AND APPROVED PLAN.**

Before any document creation (Phase 1), the following planning package MUST exist and be explicitly approved by the human:

### Required Planning Artifacts

1. **Planning Roadmap** — `plans/ROADMAP.md` or `governance/plans/ROADMAP.md` listing all intended SDD layers and their dependencies
2. **Planning Index** — `governance/plans/README.md` or `.hermes/plans/README.md` listing required plan documents
3. **Changelog Plan** — Document tracking expected changes per layer
4. **IPLAN or Development Plan** — `governance/plans/PLAN-NNN_{slug}.md` (preferred) or `.hermes/plans/YYYY-MM-DD_HHMMSS-{slug}.md` per the `plan` skill

### Planning Gate Checklist (Execute Before Phase 1)

- [ ] Planning roadmap exists for project scope
- [ ] Planning index lists required plan artifacts
- [ ] Changelog plan exists for issue scope
- [ ] Planning gap review completed (resolved or deferred with rationale)
- [ ] IPLAN or development plan exists and is explicitly approved by human
- [ ] Human has explicitly approved proceeding to document creation

**If any checklist item is missing: STOP. Do not proceed to Phase 1. Create the missing artifact or ask the human for direction.**

For a deeper, 10-category audit covering changelog plans, gap reviews, index registration, dependency completeness, roadmap timing, ADR topic coverage, scope boundaries, section outlines, CHG governance, and validation pre-checks, see `references/plan-gap-review-checklist.md`.

### BRD-to-Source Coverage Audit (For BRD Layer Initialization)

When initializing a project's BRD layer from a large source document (rulebook, strategy doc, etc.):

1. **Extract all section headers** from the source document — use `grep -n '^# '` for markdown, or equivalent for the format
2. **Build a coverage matrix**: each source section → proposed BRD assignment + rationale
3. **Identify gaps**: unassigned sections, vague assignments ("folded into BRD-X" without explicit rationale), content blocks between section boundaries not captured by any header
4. **Verify 100% coverage** — every source unit must have an explicit BRD home or a deliberate exclusion with rationale
5. **Check for orphan content** — sections with no natural BRD home may indicate missing BRDs in the architecture

This audit must complete and be approved before any BRD extraction begins. The output is a table in the planning roadmap showing source section → BRD mapping with line spans.

### UCX Governance Compliance

This phase implements the UCX `DEVELOPMENT_WORKFLOW_GUIDE.md` §2 "Planning-First Requirement":
> Before implementation starts, complete this sequence: create planning roadmap → create planning index → define changelog plan → run planning gap review → create and approve IPLAN.

Reference: `governance/templates/PROJECT_KICKOFF_PLAN-TEMPLATE.md` for project-level planning structure.

---

### Batch ADR Generation from BDD

For the complete ADR generation pipeline across 19 documents (9 engine + 10 cross-cutting), see `references/adr-generation-from-bdd.md`. This reference captures:

- Pre-generation checklist (hash fixes, validation verification)
- Subagent timeout workaround (pre-extract upstream data, direct write_file, retry-on-timeout pattern)
- UCX sdd_validate template interference bug and workaround (moving 3 template files to /tmp)
- Benchmark-first strategy (ADR-01 + ADR-07 first, then batch engine ADRs, then cross-cutting)
- Cross-cutting ADR topics (Event Bus, Auth, Calendar, Idempotency, Regulatory/WORM, Observability, Alerting, Backpressure, Input Validation, Encryption)
- BDD deferred findings → ADR coverage matrix
- ADR numbering convention (ADR-01-09 = engines, ADR-10-19 = cross-cutting)

### Broker Backend Integration Architecture (Two-Layer MCP Pattern)

For the complete broker backend integration architecture — Internal API + per-broker MCP servers with Interactive Brokers — see `references/broker-mcp-architecture-pattern.md`. This reference captures the reusable pattern for any broker API integration project: two-layer separation, MCP protocol selection, connection lifecycle, idempotency strategy, and cross-cutting ADR dependencies (ADR-10/13/17/18/19). Also covers the full SDD pipeline (BRD-10→PRD-10→EARS-10→BDD-10→ADR-20) with scenario counts and document references.

### Cross-Document Registration Sweep (Layer Completion)

When a full pipeline (BRD→PRD→EARS→BDD→ADR) is completed for a document number NN, run a registration sweep across ALL index files:

1. `plans/README.md` — update plan status + add new rows in SDD Document Artifacts table for each layer
2. `01_BRD/BRD-00_index.md` — add to document registry table
3. `02_PRD/PRD-00_index.md` — add row after template row (format: `| [PRD-NN](./PRD-NN.yaml) \| Title \| Status \| Related BRD \| Features \| Priority \| Date |`)
4. `03_EARS/EARS-00_index.md` — add row after template row
5. `04_BDD/BDD-00_index.md` — add row after template row
6. `05_ADR/ADR-00_index.md` — add row to architecture index table
7. `CHANGELOG.md` — add pipeline entry under [Unreleased] with all layer versions and scores
8. `plans/BRD-PLANNING-ROADMAP.md` — update status to COMPLETE
9. Each layer document: update `downstream_expected` to reference the actual downstream document IDs (e.g., "see PRD-10", "see EARS-10")
10. ADR cross-cutting: verify the new ADR references all relevant cross-cutting ADRs (idempotency, rate limiting, validation, secrets, event bus)

### sdd_validate UCX Template Interference (ADR Layer)

The UCX validator discovers template files across the entire project tree AND framework directories.
Templates containing `id: ADR-NN` (or `_id: ADR-NN`) collide with the parse stream and cause spurious
validation failures even when the actual document is structurally valid.

**Files that must be temporarily moved (4 locations):**

- Project: `UCX/templates/layers/05_ADR/ADR-TEMPLATE.yaml`
- Framework: `framework/layers/05_ADR/ADR-TEMPLATE.yaml`
- MCP: `ucx_hermes/templates/ADR-TEMPLATE.yaml` AND `mcp_ucx/templates/ADR-TEMPLATE.yaml`
- Legacy: `ai_dev_ssd_flow_v2/05_ADR/ADR-TEMPLATE.yaml`

**Workaround**: Move all 4+ files to /tmp, validate, check score, restore. The document will show
1 error ("Missing canonical layer template") — this is a false positive. The actual document has
0 cross-section errors and 0 warnings.

**Do NOT patch `_id: ADR-NN` to `_id: ADR-00`** — the validator still discovers framework-level
templates that cannot be patched (read-only framework directories).

**Restore immediately after validation** — `sdd_init` regenerates any missing templates.

### Inline ADR Review (No Executor Required)

When UCX `sdd_review` executors are unavailable (no API keys, auth failures) or the 48KB
review prompt would time out subagent dispatch, run the 5-persona review **inline** in the main
agent context by reading ADR sections and applying persona criteria directly.

See `references/adr-review-inline-pattern.md` for the full pattern, review template structure,
metadata update conventions, and common P1 finding categories.

### Subagent Timeout Recovery (Large Document Generation)

When subagent generation times out at 600s on large documents (>50KB output expected):

- Pre-extract upstream data into the subagent prompt (don't make subagent read 6 files)
- Retry solo on timeout — check file mtime; if advanced, subagent wrote before timing out
- Fall back: build YAML via execute_code and write_file directly
- ADR-04 needed 5 dispatch attempts; ADR-09 needed direct write_file after 3 timeouts

### delegate_task Parameter Format

`delegate_task` has two modes. Do NOT mix them — the function rejects hybrid calls:

- **Batch mode**: `delegate_task(tasks=[{context, goal, role, toolsets}, ...])` — passes a JSON array
- **Single mode**: `delegate_task(context=..., goal=..., role=..., toolsets=[...])` — passes individual fields

Error symptom: "Provide either 'goal' (single task) or 'tasks' (batch)." This fires when you pass
both `tasks` (array) AND individual task parameters in the same call. Fix: pick one mode and use it
consistently. Batch mode is preferred for parallel dispatch. Single mode for targeted remediation.

### Batch PRD Generation from BRDs

After all BRDs are validated and reviewed, generate PRDs for each BRD.

### Quality Gate (from TradeGent CC 2026-05-07 Review)

**5/5 persona reviewers independently rejected "lightweight" PRDs as unbuildable stubs.**
A feature PRD with one generic core capability (e.g., "Product delivers [feature] as specified in BRD-XX" with acceptance criterion "All BRD acceptance criteria met — target 100%") IS NOT A VALID PRD. It is a placeholder shell. The EARS layer 3 cannot formalize requirements from stubs. The entire SDD pipeline stalls.

**Correct pattern**: Decompose EVERY BRD functional requirement into a PRD core capability with:

- Hash-level BRD references: `@brd: BRD.NN.07.xxxx` (not document-level `@brd: BRD-NN`)
- Populated diagram_contract with containers + data_flows (not empty `{}`)
- User journeys with alt/else error branches
- Feature-specific error messages with actionable guidance
- adr_topic_elaboration in traceability section
- 3-7 capabilities per feature PRD, 3-5 user stories, 370-450 lines

The umbrella PRD remains full-detail (500+ lines). Feature PRDs follow the same pattern at ~400 lines each.

For the complete batch generation script, see `references/batch-prd-generation-from-brds.md`.

### Batch Pipeline Execution — Single Feature Branch (BRD→BDD)

When a single new feature BRD needs to be carried through all downstream layers
in one session with inline review at each layer, use the sequence in
`references/batch-pipeline-execution.md`. Covers per-layer persona assignments,
common fix types, metadata update patterns, and cross-layer consistency checks.

## EARS Generation from PRDs (Layer 3)

After all PRDs are validated, reviewed, and remediated, generate EARS documents.

### EARS Syntax Enforcement (Critical — from TradeGent CC 2026-05-07)

PROHIBITED QUALIFIERS (replace with quantified targets):
  "real-time" → "WITHIN 60 seconds" | "immediate/immediately" → "WITHIN N seconds"
  "continuously" → "at each [event]" | "fast/quickly" → "p50 < Nms, p95 < Nms"
  "near X" → "within 0.0Y of X"

STRUCTURAL RULES:

  1. No compound WHEN with AND — split into atomic requirements
  2. No nested IF inside SHALL — each conditional path is a separate requirement
  3. WITHIN must reference a specific event (not orphaned "WITHIN 5 minutes")
  4. IF/WITHIN must reference the same event
  5. No subjective criteria ("acceptable", "reasonable", "significant")
  6. Atomicity: one testable concept per requirement
  7. Quantify interval ranges (not "every 15-25 min")

STATE MACHINE: every EARS touching operational modes MUST include a state_machine
  section with AUTONOMOUS → WARNING → HALTED → MANUAL → RECONCILING states and
  full transition triggers.

For the complete EARS rules, state machine template, and batch generation script,
see `references/ears-generation-pattern.md`.

### Benchmarks-First Strategy

1. Generate 2 benchmark EARS from the strongest upstream sources (umbrella + core feature)
2. Validate both with sdd_validate
3. Review with 4 personas: requirements-specialist, technical-lead, qa-lead, chaos-engineer
4. Remediate findings
5. Once validated, batch-generate remaining 7 EARS with execute_code

## Batch BDD Generation from EARS (Layer 4)

After all EARS are validated and reviewed, generate BDD acceptance scenarios with the same benchmarks-first strategy documented below. The full generation pattern — including the Python build_bdd() function, safe YAML serialization with comparison-operator quoting, and validation workflow — lives in `references/batch-bdd-generation-from-ears.md`.
For the post-generation review, remediation, and deferral rules (5-persona parallel review, chairperson scoring, ADR-blocked deferrals), see `references/bdd-batch-review-remediation.md`.
For the post-generation review, remediation, and deferral rules (5-persona parallel review, chairperson scoring, ADR-blocked deferrals), see `references/bdd-batch-review-remediation.md`.

After BDD layer completion (all docs health >= 8), plan the ADR layer before generation. `references/adr-layer-planning-and-gap-review.md` covers: topic inventory (BDD deferred findings + PRD adr_topics + BRD constraints), engine vs cross-cutting categorization, coverage matrix construction, gap review methodology, pre-generation checklist, and anti-patterns.

### BDD Scenario Mapping Rules

Every BDD document must translate EARS requirements into executable Given-When-Then scenarios:

- **Event-driven EARS** → success scenarios: extract WHEN from statement as Given/When, THE-SHALL as Then
- **State-driven EARS** → success scenarios: WHILE condition as Given, monitoring cycle as When, behavioral outcome as Then
- **Unwanted-behavior EARS** → error scenarios: IF condition as Given, detection as When, escalation/logging as Then
- **Ubiquitous EARS** → dedicated success scenarios: verify completeness across all decision types (queryable, immutable, structured)
- At least 1 recovery scenario per BDD (state transition restoration, post-failure reconciliation, transient retry)
- Minimum 5 scenarios per BDD: 3-4 success, 1-2 error, 1 recovery
- Benchmark BDDs (umbrella + core engine) should reach 13-19 scenarios after review/remediation

### Pragmatic Remediation Scope (What Belongs Where)

Not every finding from a persona review belongs at the BDD layer. Apply this triage:

| Finding Type | Remediate In | Rationale |
|-------------|-------------|-----------|
| Missing EARS requirement coverage | **BDD** | BDD's job is to cover all formal requirements |
| State machine transition gaps | **BDD** | Transitions are behavioral — testable as scenarios |
| Gherkin syntax/executability issues | **BDD** | BDD is the acceptance-test artifact |
| Tag/priority mismatches, dead data | **BDD** | Document quality, fix immediately |
| Alert dedup/idempotency scenarios | **BDD** | These are behavioral contracts |
| OAuth token lifecycle, credential storage | **ADR/SPEC** | Architecture and interface contracts, not acceptance tests |
| Regulatory reporting hooks | **ADR/SPEC** | Belongs in architecture decisions and interface specs |
| DST/market holiday, circuit breaker handling | **ADR/SPEC** | System-level behavior contracts |
| Concurrent failure, clock skew, cascading triggers | **ADR/SPEC** | Integration/chaos testing at SPEC/TDD level |

**Concrete ADR-deferral catalog** (TradeGent CC batch proven):

| BDD Finding | Deferred to | Why | Example |
|-------------|-------------|-----|---------|
| AuthN/AuthZ for scenario execution | SPEC §security | Needs role hierarchy and auth contract | OAuth2/OIDC, RBAC per role |
| Pre-trade risk gate (fat-finger, size limits) | ADR §risk-model | Needs gate placement decision | Max position size, notional cap |
| Idempotency and deduplication | SPEC §reliability | Needs exactly-once strategy | Duplicate scenario rejection |
| Race conditions and concurrent execution | ADR §concurrency | Needs locking model | Market-state transition race |
| Edge cases (DST, market holidays, clock skew) | ADR §calendar | Needs calendar service design | Holiday close → no trading |
| Timing assertions (WITHIN tolerance) | SPEC §performance | Needs latency contract | p95 < 200ms for alert dispatch |
| Parameterized tables (matrix scenarios) | SPEC §data | Needs data contract schema | Strike-price × expiry matrix |
| Circuit breakers and cascading failure | ADR §resilience | Needs resilience architecture | Broker-down → halt open orders |
| Regulatory reporting hooks | SPEC §compliance | Needs event stream design | SEC 606 report, audit log |

The general rule: if a scenario requires mocking an external service, time-travel harness,
or multi-system coordination to test, it likely belongs at SPEC (interface contracts) or TDD (integration test definitions), not BDD (user-facing acceptance criteria).

### Batch Delegate Concurrency

The `delegate_task` function enforces `max_concurrent_children` (default 3). When dispatching 5-persona BDD reviews, split into two calls: first call dispatches 3 subagents, second call dispatches 2. Both calls run in parallel since they're separate `delegate_task` invocations. Total wall-clock time equals the slower batch, not the sum.

```
# Correct — two parallel delegate_task calls, 3+2 split
delegate_task(tasks=[qa-lead, technical-lead, chaos-engineer])  # batch 1
delegate_task(tasks=[sre, security-auditor])                    # batch 2
```

## UCX Template Discovery for PRD Creation

The UCX `sdd_create_build` tool discovers available templates in the project tree:

```python
# Try layer-specific template first
sdd_create_build(doc_type="prd", layer="02_PRD", template="02_PRD-TEMPLATE.yaml")
# Fall back to generic
sdd_create_build(doc_type="prd", layer="02_PRD", template="PRD-TEMPLATE.yaml")
```

If templates are not found, run `sdd_init(project_path)` to scaffold the project with template files. After init, re-run `sdd_create_build` to confirm template discovery.

**Pre-flight checklist before PRD generation**:

1. `sdd_preflight(context="create")` — confirms project state and next action
2. `sdd_create_build` — confirms template availability
3. If either fails, run `sdd_init` then retry
4. Generate plan in `plans/PLAN-NNN_prd-generation.md` and get human approval

## PRD Diagram Section Placement

The UCX validator checks for `diagrams.items` at the **top level** of the PRD document, NOT nested under `functional_requirements` or other sections.

```yaml
# WRONG — validator sees this as missing
diagram_contract:
  diagrams:
    items: [...]

# RIGHT — top-level diagrams section
diagrams:
  id: "PRD.01.diagrams.a1b2"
  directory: "diagrams/"
  format: "SVG from Mermaid"
  items:
    - id: "PRD.01.diagrams.c3d4"
      title: "Container Diagram"
      file: "diagrams/prd-01_containers.mmd"
      source: "C4-L2 description"
      scope: "container"
```

### sdd_next_action Layer Gate

After all PRDs are generated and validated, call `sdd_next_action(document="02_PRD")` to confirm the layer's next stage. The response shows:

- `current_stage`: "created"
- `existing_artifacts`: list of all PRD files in the layer
- `next_action`: "validate" (or "review" if already validated)
- `next_tool`: "sdd_validate"

This gate confirms all documents are visible to the UCX tooling before proceeding to review or next layer (EARS).

### PRD-to-BRD Traceability

Every PRD must reference its upstream BRD:

```yaml
traceability:
  upstream:
    brd_references:
      - "@brd: BRD-01.04.78a9 (business_objectives.goals)"
      - "@brd: BRD-01.07.f79d (functional_requirements)"
  downstream_expected:
    - {type: "EARS", layer: 3, description: "Formal requirements"}
  cross_links:
    depends: ["@depends: BRD-01"]
    discoverability:
      - "@discoverability: PRD-02 (feature product requirements)"
```

For umbrella PRDs, populate `discoverability` with all 8 feature PRDs. For feature PRDs, reference the umbrella PRD and any directly related feature PRDs.

## Phase 1: Document Creation (UCC)

### Workflow

1. Receive the target document type and any reference/upstream materials
2. Load the appropriate YAML template from UCX (see Templates section below)
3. Dispatch the creation personas as parallel subagents, each contributing their domain section
4. Synthesize contributions into a complete document following the template structure
5. Validate output against layer schema

### Creation Persona Assignments

| Doc Type | Persona Skills to Dispatch |
|----------|---------------------------|
| **BRD** | product-owner, business-analyst, business-strategist, system-architect, technical-lead |
| **PRD** | product-owner, ux-strategist, content-strategist, technical-lead, system-architect, requirements-specialist |
| **EARS** | requirements-specialist, technical-lead, qa-lead, chaos-engineer |
| **BDD** | qa-lead, technical-lead, chaos-engineer, site-reliability-engineer, security-auditor |
| **ADR** | system-architect, technical-lead, security-auditor, chaos-engineer, site-reliability-engineer |
| **SPEC** | technical-lead, system-architect, integration-specialist, site-reliability-engineer, security-auditor |
| **TDD** | qa-lead, technical-lead, chaos-engineer, site-reliability-engineer, security-auditor |
| **IPLAN** | technical-lead, system-architect, site-reliability-engineer, qa-lead |

### Creation Prompt Rules

For BRD creation, enforce:

- All 15 required sections present (Executive Summary, Problem Statement, Proposed Solution, Stakeholder Analysis, Functional Requirements, Non-Functional Requirements, Quality Attributes, Constraints, Assumptions, Dependencies, Risk Analysis, Success Criteria, Glossary, Appendices, Cross-References)
- YAML frontmatter with `doc_id: "BRD-{NN}"`
- Element IDs: `TYPE.NN.SS.xxxx` (4-segment format per naming standards: e.g., `BRD.01.07.a7f3`)
- When uncertain about a requirement, DOCUMENT THE UNCERTAINTY rather than omit it
- No TBD/TODO items without explanation

For PRD creation, enforce:

- User stories with acceptance criteria
- Feature prioritization (MoSCoW)
- MVP scope boundary
- User personas and journeys

For ADR creation, enforce:

- Context-Decision-Consequences format
- Each decision has documented alternatives considered
- Trade-off analysis present

For TDD creation, enforce:

- Test pyramid: 70% unit / 20% integration / 10% e2e
- Every BDD scenario maps to one or more TDD test cases
- Test case format: inputs, expected outputs, edge cases
- Quality thresholds from SPEC must be reflected in test assertions
- Tests MUST be defined before implementation (test-first TDD)

For IPLAN creation, enforce:

- File manifest: one entry per deliverable file with status (NOT_STARTED/PARTIAL/COMPLETED)
- Bash commands: executable one-liners only, no interactive prompts
- Session handoff: previous session state, next_step directive
- Execution order: test files FIRST, then implementation files
- Partial work tracking: description of in-progress work for resumption

---

## Phase 2: Document Review (UCR)

### Workflow

1. Receive the document to review
2. Dispatch ALL listed persona subagents **in parallel**
3. Collect all findings from each subagent
4. Dispatch **fact-checker** to cross-validate all P0/P1 findings
5. Dispatch **board-chairperson** to synthesize, de-duplicate, score, and produce final manifest

### Review Persona Assignments (Dispatch Phase)

| Doc Type | Parallel Subagents to Dispatch |
|----------|-------------------------------|
| **BRD** | system-architect, security-auditor, business-analyst, chaos-engineer |
| **PRD** | system-architect, security-auditor, technical-lead, product-owner, chaos-engineer |
| **EARS** | requirements-specialist, technical-lead, qa-lead, chaos-engineer |
| **BDD** | qa-lead, technical-lead, chaos-engineer, site-reliability-engineer, security-auditor |
| **ADR** | system-architect, technical-lead, site-reliability-engineer, security-auditor, chaos-engineer |
| **SPEC** | technical-lead, system-architect, chaos-engineer, site-reliability-engineer, integration-specialist |
| **TDD** | qa-lead, technical-lead, chaos-engineer, site-reliability-engineer, security-auditor |
| **IPLAN** | technical-lead, system-architect, site-reliability-engineer, qa-lead, security-auditor |

### Inline BRD Review (No Executor Required)

When UCX `sdd_review` executors are unavailable or the user prefers inline reviews,
use the 4-persona BRD review pattern directly in the main agent context.

See `references/brd-review-inline-pattern.md` for the full pattern, review template
structure, common P1 finding categories, and differences from the ADR inline review.

### Review Post-Processing (Sequential, After Parallel Dispatch)

After ALL parallel subagents return findings:

1. **fact-checker**: Cross-validate all P0/P1 findings against the document. Remove false positives, correct categories.
2. **board-chairperson**: Synthesize verified findings, de-duplicate, compute category-weighted score, produce final manifest with readiness verdict.

### Review Prompt Rules

- **FALSE NEGATIVES ARE UNACCEPTABLE.** When in doubt, FLAG IT.
- Every finding must include: Target File, Target Section, exact path
- Classify findings as P0 (critical/blocking), P1 (high), or P2 (medium)
- Pre-validation errors (YAML schema, missing fields) are infrastructure issues — report separately, do NOT count in P0 finding count

### Chairperson Scoring

Category-weighted scoring with 8 categories:

- functional, quality, compliance, constraints, integration, acceptance, risk, architecture

Formula: Score = 100 - sum(capped_category_deductions × weights)
Pass thresholds vary by doc type (check document-specific README).

---

## Phase 3: Remediation (UCRem)

### Workflow

1. Receive the UCR review report and target document
2. Pre-screen findings to determine which domain fixers are needed (adaptive loading)
3. Dispatch needed domaine fixers as parallel subagents
4. Dispatch **board-chairperson** to synthesize all fixes, resolve conflicts, produce final remediation report

### Remediation Persona Assignments

| Condition | Fixer Subagents to Dispatch |
|-----------|---------------------------|
| **Mandatory (always)** | chaos-engineer, board-chairperson |
| **Architecture findings present** | system-architect |
| **Compliance findings present** | security-auditor |
| **Test/QA findings present** | qa-lead |

### Remediation Rules

- Complete `llm_completion` items FIRST
- Address `llm_only` items second
- Handle other findings third
- Verify but do NOT modify `fixer_applied` items
- The chairperson produces the final remediation manifest with execution order (auto-safe → auto-assisted → manual)

### UCX `sdd_remediate` Limitation — Structural-Only Fixes

UCX `sdd_remediate` is a **structural/schema fixer**, not a content author. It detects:

- Placeholder tokens (`xxxx`, `TBD` without explanation)
- Invalid element ID formats
- Missing required sections

It does **NOT**:

- Add new scenarios to `scenario_structure.scenarios`
- Rewrite boilerplate Gherkin steps into domain-specific language
- Generate missing success/error/recovery/audit scenario blocks
- Apply findings from narrative markdown review reports (UCREM, chairperson manifests)

**Observed behavior (TradeGent CC, 2026-05-08):**

```
sdd_remediate(document=BDD-02.yaml, remediation_report=UCREM-REPORT.md)
→ findings: 2 tier2 (placeholder, element_id)
→ derived copy: BDD-02_remediate_v2.yaml
→ applied_changes: "none (copy-only deterministic baseline)"
→ md5sum(source) == md5sum(derived) — byte-for-byte identical
```

The UCREM report described 58 content-level findings (missing Gate 3 scenarios, audit logging, recovery paths, parameterized tables). `sdd_remediate` ignored all of them because they require semantic authoring, not structural repair.

**Correct content-remediation path:**

1. Parse chairperson manifest / UCREM report into a per-document fix list
2. Dispatch `delegate_task` fixer subagents (or scripted Python patching) to rewrite YAML content
3. Subagents must explicitly write `scenario_structure.scenarios.{success,error,recovery,audit}` blocks
4. After subagent writes, verify with `yaml.safe_load()` + scenario count diff
5. Run `sdd_validate` on the rewritten file for structural confirmation only

Never assume `sdd_remediate` with a markdown report will apply content fixes. It won't.

### Subagent Content Remediation Pattern (BDD Layer)

When `sdd_remediate` is confirmed structural-only (see reproduction above), use `delegate_task` fixer subagents for semantic authoring. Proven at TradeGent CC 2026-05-08 for 7 BDDs.

**Dispatcher setup:**

- `delegate_task` enforces `max_concurrent_children=3`. Split docs into batches of 3 (or fewer).
- Each subagent receives: original BDD path, upstream EARS path, per-document fix list, YAML structure rules.

**Fix list per document (example: BDD-02):**

```
doc_path: /path/to/BDD-02.yaml
priority: P1| P2
cross_links: ["@depends: BDD-01"]
add_success:
  - "Gate 3 — Fundamental Health (ROE>10%, debt/equity<50%, FCF>0)"
  - "Gate 4 — Price Behavior (200-day MA proximity, no >10% gap in 90 days)"
  - "Composite Scoring (multi-factor ranking with min/max thresholds)"
add_error: []              # if none, omit
add_recovery: True         # "Recovery from Data Source Failed"
add_audit: True            # "Audit Logging for Screening Decisions"
rewrite_gherkin: True      # replace placeholders with concrete Given/When/Then
add_timing: True           # add WITHIN assertions per EARS
timing_assertions:         # exact thresholds from EARS
  - "WITHIN 5 minutes"
  - "WITHIN 10 seconds"
fix_spec_trace: True       # replace "5 (Behavior — X)" with actual EARS refs
health_score: "6/10"       # realistic, not fabricated
```

**Subagent rules:**

- Overwrite the original file; do NOT create a new path
- Scenario IDs: `BDD.NN.SS.xxxx` where `xxxx` = first 4 chars of SHA256("BDD.NN:{section}:{name}")
- After writing, verify with `yaml.safe_load()` and report scenario count breakdown
- Include upstream EARS requirement text in `spec_trace` entries (not placeholders)

**Dispatcher verification (mandatory after each batch):**

```python
import os, yaml
for f in bdd_files:
    # Check modification time
    mtime = os.path.getmtime(f)
    # Check scenario count
    with open(f) as fh:
        data = yaml.safe_load(fh)
    sc = data.get("scenario_structure", {}).get("scenarios", {})
    total = sum(len(sc.get(k, [])) for k in ["success","error","recovery","audit","edge","performance","security"])
    print(f"{f}: modified={mtime} scenarios={total}")
```

- Reject any subagent result where `mtime` is unchanged or scenario count matches pre-remediation
- Re-dispatch timed-out subagents individually (common for complex docs like BDD-05 with pre-trade risk)

**Post-remediation validation:**

- Run `sdd_validate` on each rewritten file to confirm structural compliance
- Expected: PASS, 0 errors, 0 warnings
- Do NOT rely on the subagent's own "verification" claim — validate independently

### Verification After Remediation — Disk State

Any claim that remediation is "applied" MUST be verified with a tool call in the same turn:

| Check | Tool/Method | Pass Criteria |
|-------|-------------|---------------|
| File modified | `os.path.getmtime()` | mtime > pre-remediation baseline |
| Content changed | `md5sum original derived` | Hashes differ (or mtime changed) |
| YAML valid | `yaml.safe_load()` | No YAMLError |
| Scenarios added | Count `scenario_structure.scenarios.*` | Count matches fix list |
| Structure valid | `sdd_validate` | 0 errors / 0 warnings |

**Anti-pattern**: The UCREM report claimed BDD-02 went from 7 to 15 scenarios, but `yaml.safe_load()` on the original file still showed 7. The report described intended fixes; the files were untouched. Always verify the file, never the report.

See `references/ucx-remediate-content-limitations.md` for the full reproduction transcript, the expected-vs-actual comparison, and the scripted vs. subagent remediation paths.

---

## Templates & Layer Assets (v3.2)

All templates are unified YAML files available as linked files in this skill:

- `framework/layers/01_BRD/BRD-TEMPLATE.yaml`
- `framework/layers/02_PRD/PRD-TEMPLATE.yaml`
- `framework/layers/03_EARS/EARS-TEMPLATE.yaml`
- `framework/layers/04_BDD/BDD-TEMPLATE.yaml`
- `framework/layers/05_ADR/ADR-TEMPLATE.yaml`
- `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
- `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
- `framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml`

Load the appropriate template from `framework/layers/<NN>_<TYPE>/<TYPE>-TEMPLATE.yaml` in the repository (e.g. `framework/layers/01_BRD/BRD-TEMPLATE.yaml`). Use the standard file-read mechanism — `skill_view` does **not** apply since templates live outside the skill (D-0013).

| Layer | Template | Upstream Tags |
|-------|----------|---------------|
| L1 BRD | `framework/layers/01_BRD/BRD-TEMPLATE.yaml` | — |
| L2 PRD | `framework/layers/02_PRD/PRD-TEMPLATE.yaml` | @brd |
| L3 EARS | `framework/layers/03_EARS/EARS-TEMPLATE.yaml` | @brd @prd |
| L4 BDD | `framework/layers/04_BDD/BDD-TEMPLATE.yaml` | @brd @prd @ears |
| L5 ADR | `framework/layers/05_ADR/ADR-TEMPLATE.yaml` | @brd @prd @ears @bdd |
| L6 SPEC | `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml` | @brd @prd @ears @bdd @adr |
| L7 TDD | `framework/layers/07_TDD/TDD-TEMPLATE.yaml` | @brd @prd @ears @bdd @adr @spec |
| L8 IPLAN | `framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml` | @brd @prd @ears @bdd @adr @spec @tdd |

**All documents use `.yaml` format.** Markdown is for indexes and reference docs only.
**No subtypes** — SPEC and TDD use unified templates (no CSPEC/DSPEC/UXSPEC/RISKSPEC/PROCSPEC; no UTEST/ITEST/STEST/FTEST/PTEST/SECTEST).

Load the appropriate template before beginning creation or review.

---

## YAML Pitfalls and Safe Writing

### Values Starting with Comparison Operators

YAML parsers choke on unquoted values that begin with `>=`, `<=`, `>`, or `<`
because the leading `>`/`<` is interpreted as a block scalar chomping indicator.
This hits frequently in SDD documents where `target`, `criterion`, and `metric`
fields contain thresholds like `target: >=90%`.

**Rule: quote any field value that starts with `>=`, `<=`, `>`, or `<`.**

```yaml
# WRONG — YAMLError: expected chomping or indentation indicators
target: >=90% of candidates remain qualified

# RIGHT
target: '>=90% of candidates remain qualified'
```

### Inline Parentheses With Comparison Operators

Multi-line values with inline `>=` (e.g., `beat rate >=60%)`) also break parsing
when spread across lines. **Collapse into a single quoted string or use block
scalar (`|-`) without the problematic inline operators on separate lines.**

### Programmatic Document Generation

When generating any SDD YAML document (BRD, PRD, etc.) programmatically via
`execute_code` — including single documents with many element IDs — use the
pattern documented in `references/programmatic-sdd-generation.md`. This covers:
Python dict assembly from template structure, content-based element ID hashing,
YAML quoting post-processing, and layer-specific quality gate checklists.

### Bulk Generation Strategy for Multi-BRD Sessions

When creating multiple BRDs/PRDs from a large source document (e.g., decomposing
a 2,000-line rulebook into 7 feature BRDs):

1. Build BRD dicts in Python (via `execute_code`)
2. Use `yaml.dump()` then post-process to quote `>=`/`<=`/`>`/`<` lines
3. Verify each file with `yaml.safe_load()` before closing
4. Write via `write_file` only after lint passes

This is more reliable than iterative `write_file → lint fail → patch → repeat`
cycles. For the complete rulebook-to-BRD extraction workflow — including the
coverage audit, reusable base template pattern, thin-section expansion strategy,
and session execution pattern — see `references/rulebook-brd-extraction.md`.

See `references/yaml-quoting-rules.md` for the full post-processing
script pattern.

### UCX Validator Filename Heuristic Misclassification

The UCX `sdd_validate` tool may misclassify YAML files as Markdown based on
filename patterns. In observed cases, a file named `BRD-08_performance_review_cadence.yaml`
was rejected with "Missing or invalid YAML frontmatter" while the identical content
renamed to `BRD-08.yaml` passed clean — same structure, same 0 errors/0 warnings.

When this occurs, the validation report shows:

- **Error**: "Missing or invalid YAML frontmatter"
- **Pass log**: "Requires YAML data (skipped for MD)"
- **Generated fix file**: `*_validated.yaml` (validator's own re-serialization)

**Root cause**: validator type detection heuristic triggers on certain filename
patterns (long descriptive names with multiple underscores/keywords).

**Diagnostic steps**:

1. Verify `yaml.safe_load()` passes cleanly on the file
2. Compare raw bytes at file start — look for invisible BOM or encoding issues
3. Rename to a short canonical form (`BRD-NN.yaml`) and re-validate
4. If rename fixes it — confirmed filename heuristic bug
5. If rename still fails — check the validator's `_validated.yaml` output for structural differences

**Workaround**: Rename to canonical short form (`BRD-NN.yaml`) content is identical. Document the rename in CHANGELOG and plan to rename back once validator bug is fixed.

**Long-term fix**: Report to UCX framework maintainers with the failing filename + passing filename pair. Do NOT silently substitute programmatic parsing and call it "validated" — mark status as "VALIDATED (workaround: renamed from {old} to {new} due to validator heuristic bug)".

### read_file Inside execute_code Returns Line-Numbered Output

When you call `read_file(path)` inside an `execute_code` sandbox, each line is
prefixed with a line-number (`1|content here`). This breaks YAML parsers
(`yaml.safe_load()` fails because the first column is no longer the YAML
structure). **Use `subprocess.run(["cat", path])` instead to get clean content
for YAML parsing inside sandbox code.** Outside `execute_code` (direct
skill_view/file reads in the main agent context), `read_file` returns clean
content with no line numbers.

For the full BRD validation and element-ID assignment workflow in Python,
see `references/brd-validation-automation.md` — it has the complete
three-phase script (structural validation → ID assignment → post-rewrite checks)
with all section traversal code.

```python
# WRONG — yaml.safe_load fails on line-numbered content
from hermes_tools import read_file
rd = read_file(path, limit=2000)
doc = yaml.safe_load(rd["content"])  # ❌ lines prefixed with "N|"

# RIGHT — clean content via subprocess
import subprocess, yaml
r = subprocess.run(["cat", path], capture_output=True, text=True)
doc = yaml.safe_load(r.stdout)  # ✅ clean YAML
```

### YAML Patch Indentation Errors

When inserting new YAML list items via string-based `patch` operations, missing
leading whitespace causes `expected <block end>, but found '-'` errors at the
insertion point. See `references/yaml-patch-indentation-fix.md` for the auto-fix
script, root cause analysis, and prevention checklist.

### Never Patch From Partial File Views

When you read a file via `offset`/`limit` pagination, the window is incomplete.
A `patch` command matched on partial context can delete sections, nest blocks
under wrong parents (e.g. `requirements` ending up under `traceability`), or
duplicate content. **If you did not read the full file contents, rewrite the
entire file via `write_file` instead of `patch`.**

### MCP PYTHONPATH for stdio Servers

When configuring a stdio MCP server that imports sibling modules (e.g., UCX
sdd-lifecycle server), `cwd` alone is not enough — it sets the filesystem
working directory but not the Python import path. Add `PYTHONPATH` in `env`:

```yaml
mcp_servers:
  sdd-lifecycle:
    command: "/opt/data/ucx_framework/.venv/bin/python"
    args: ["-m", "mcp_server.server"]
    cwd: "platforms/hermes/src"
    env:
      PYTHONPATH: "platforms/hermes/src"
```

Without `PYTHONPATH`, imports fail with `ModuleNotFoundError` even though
`cwd` appears correct. See `references/ucx-mcp-troubleshooting.md` in the
`native-mcp` skill for full diagnostic steps.

---

## Quality Gate Scoring Formulas (v3.2)

Each layer must achieve >=90/100 readiness score before generating the next layer.

| Gate | Score | Criteria |
|------|-------|----------|
| **PRD-Ready** | >=90 | BRD completeness in business objectives, requirements, scope |
| **EARS-Ready** | >=90 | PRD completeness in features, user stories, domain clarity |
| **BDD-Ready** | >=90 | EARS syntax compliance, atomicity, testability, spec_trace links |
| **ADR-Ready** | >=90 | BDD scenario coverage, Gherkin quality, edge cases |
| **TDD-Ready** | >=90 | SPEC interface clarity, data models, behavior contracts |
| **IPLAN-Ready** | >=90 | TDD test case coverage, threshold definitions, execution order |
| **EXEC-Ready** | >=90 | IPLAN file manifest completeness, execution commands, contracts |

### Validation Tooling: sdd_validate vs Programmatic Parsing

**`yaml.safe_load()` + manual checks ARE NOT VALIDATION.** They confirm YAML syntax and surface section/key presence, but they do NOT enforce:

- Cross-section rules (entities in executive_summary must appear in functional_requirements or stakeholders)
- Phase name/consistency rules between scope and implementation
- Template compliance (all required subsections present, correct C4 level content)
- Cumulative traceability tag validity (max 1 for BRD, max 8 for IPLAN)
- Readiness score computation with category-weighted deductions
- Metadata tag limits (BRD max 1 tag, SDD-XS-004)

**Only `sdd_validate` (via ucx_hermes MCP) provides structural validation.** When the MCP server is unreachable, acknowledge the gap explicitly — do not silently substitute programmatic parsing and call it "validated." The validation status should be "PARSED (pending sdd_validate)" not "VALIDATED."

### sdd_validate Output Format Quirks

The UCX `sdd_validate` tool returns **different output formats for pass vs fail**:

**PASS result** (text format):

```
[mcp_sdd_lifecycle_sdd_validate] BRD-NN PASS
Errors: 0 | Warnings: 0
Details: /path/to/BRD-NN.ucx.validate.txt
```

**FAIL result** (JSON format):

```json
{
  "report_path": "/path/to/BRD-NN.ucx.validate.json",
  "summary_path": "/path/to/BRD-NN.ucx.validate.txt",
  "errors": ["error text..."],
  "warnings": ["warning text..."],
  "is_valid": false,
  "passed": false,
  "fix_generated": true
}
```

**Implication**: Do NOT rely on JSON parsing for all validation results. Check
the tool output text first for the "PASS" marker. If absent, parse as JSON for
error/warning details. When extracting `report_path` for `sdd_score_show`, only
use the JSON path from fail results — pass results generate `.txt` summaries,
not `.json` score reports.

### sdd_score_show Behavior

`sdd_score_show` reads the JSON validation report at `report_path`. When called
on a passing document (where only `.txt` summary exists, not `.json`), it may
return a parsing error or generic "Failed to parse score report" message. This is
expected — passing documents have no score report to show (score is implicit
100/100 when 0 errors/warnings).

For the full safe tool list and gateway rules, see the `ucx-sdd-bridge` skill.

### Score Flow

```
BRD → PRD-Ready (>=90) → PRD → EARS-Ready (>=90) → EARS → BDD-Ready (>=90)
→ BDD → ADR-Ready (>=90) → ADR → SPEC → TDD-Ready (>=90)
→ TDD → IPLAN-Ready (>=90) → IPLAN → EXEC-Ready (>=90)
→ IPLAN → EXEC-Ready (>=90) → Code
```

---

## Cumulative Tagging Hierarchy (v3.2)

Every document must reference all upstream artifacts. Enforced by cross-document validation. Max 8 cumulative tags at IPLAN layer (7 upstream + self-tag @iplan).

| Layer | Artifact | Required Upstream Tags | Count |
|-------|----------|------------------------|-------|
| 1 | BRD | (none — root) | 0 |
| 2 | PRD | @brd | 1 |
| 3 | EARS | @brd, @prd | 2 |
| 4 | BDD | @brd, @prd, @ears | 3 |
| 5 | ADR | @brd, @prd, @ears, @bdd | 4 |
| 6 | SPEC | @brd through @adr | 5 |
| 7 | TDD | @brd through @spec | 6 |
| 8 | IPLAN | @brd through @tdd | 7 |

---

## Upstream Artifact Policy (CRITICAL)

**If a required upstream artifact is missing, the downstream functionality MUST NOT be implemented. Do NOT create missing upstream artifacts. Skip functionality instead.**

| Situation | Action |
|-----------|--------|
| Upstream exists | Reference with exact document ID |
| Upstream required but missing | **Skip that functionality** |
| Upstream optional and missing | Use `null` in traceability tag |
| Upstream not applicable | Omit tag entirely |

**When Upstream is Missing**: Stop → Report → Advise → Skip.

---

## TDD Enforcement Flow

When generating code from IPLAN (Layer 8):

1. **Generate test files FIRST** — from TDD Sections 3-4 test mappings and cases
2. **Run tests** — they MUST fail (no implementation exists)
3. **Generate implementation files** — from IPLAN file manifest
4. **Run tests** — they MUST pass
5. **Refactor** — keep tests green

---

## IPLAN Session Handoff Protocol

Each AI agent session follows this protocol:

1. Read `session_handoff.sessions` — identify the last session's state
2. Check `file_manifest.files` — find next NOT_STARTED or PARTIAL file
3. Read `partial_work` description if resuming a PARTIAL step
4. Continue from that point — do NOT regenerate completed work
5. Update file status after completion or session end
6. Append to `session_handoff.sessions` with next_session_directive

### Development Completion Rule

An IPLAN is **Completed** when source code + CI/CD scripts are authored, committed, and tests pass. It does NOT wait for deployment (terraform apply, image build, acceptance testing).

---

## Self-Consistent Audit + Fix Loop

After review and remediation, verify fixes with a re-audit loop:

```
LOOP (max 3 iterations):
  1. Run review (parallel persona subagents)
  2. Fact-checker validates P0/P1 findings
  3. Chairperson synthesizes → produce report
  4. Run remediation (fixer subagents)
  5. Re-run review on fixed document
  6. IF score >= threshold → DONE
  7. IF score < threshold AND iteration < 3 → GOTO 1
  8. IF iteration == 3 → Report manual review needed
```

**Fresh Audit Policy**: Always run review from scratch on the current document state. Delete old reports after each iteration. Use ISO 8601 timestamps for precise drift tracking.

---

## Output Formats

### Review Report Structure

```markdown
# UCR Report: {DOC_ID}
## Executive Summary (metrics table)
## Phase 1: Validation Results (schema/structure errors)
## Phase 2: Content Review Findings (per-persona sections)
## Phase 3: Chairperson Manifest (category summary, weighted score, readiness)
```

### Remediation Report Structure

```markdown
# UCRem Report: {DOC_ID}
## Findings Addressed
## Fixes Applied (per-fixer sections)
## Chairperson Synthesis (deduplication, conflicts, execution order)
## Final Assessment
```

---

## Framework Location

The SDD v3.2 framework lives at `framework/`.
See `references/framework-location-and-quirks.md` for the full directory layout,
key reference files, known framework bugs (and their fixes), threshold formatting,
and the list of v2 artifact types that must NOT be referenced.

**UCX Tool Behavior Quirks**: `references/ucx-tool-behavior-quirks.md` covers
executor requirements (`sdd_review` needs API executor), lifecycle pipeline stopping
on first failure, error output format ambiguity (text vs JSON), `sdd_init`
regenerating templates (trapping the collision workaround), and `sdd_set_project`
persistence.

**Template Collision**: `references/ucx-validator-template-collision.md` has the
full reproduction recipe for the `id: ADR-NN` parse error, the safe out-of-project
workaround, and the `sdd_init` regeneration trap.

**Environment setup**: On systems with conda installed (`/opt/anaconda`), use
`conda create -p .venv python=3.12.13` instead of pyenv — pyenv's pip bootstrap
fails due to conda's libcurl shadowing. See `references/python-env-setup.md`.

## Verification Gate (MANDATORY — Before Any Completion Claim)

**NEVER claim a layer, document, or SDD phase is complete without first verifying actual filesystem state.** This is the single most frequent and impactful failure mode in the orchestrator — the model infers completion from plan-writing or pattern-matching across layers and reports work as done when no files exist on disk.

### When This Gate Applies

- After generating documents: verify files exist before claiming creation is complete
- After validation: read the validation report text before claiming 0/0
- After remediation: re-validate before claiming fixes are applied
- When user asks "are we ready for X?": run sdd_next_action + list files before answering
- When user asks "did you do Y?": check the filesystem, never answer from memory/pattern

### Hard Rules

1. **Plan ≠ Done.** Writing PLAN-NNN.md returns a file path — that is a *planning* milestone, not a *delivery* milestone. A written plan means you are authorized to begin work. It does not mean the work is finished.
2. **Tool call required.** Any claim about files on disk, validation status, or layer readiness MUST be backed by a tool call in the same turn. If you cannot call the tool (e.g., MCP server unreachable), you must state the gap explicitly — never substitute inference for evidence.
3. **sdd_next_action is the ground truth.** Before telling the user a layer is complete, call `sdd_next_action(document="0N_TYPE")` and read the `existing_artifacts` list. If the expected files are absent, the work is not done.
4. **Don't pattern-match across layers.** BRD/PRD/EARS all followed the same pipeline. Layer N+1 will need the same steps, but the model can't shortcut the generation/validation/review/remediation phases just because the pattern is familiar. Each layer must be executed explicitly.

### Anti-Pattern (What Happened — TradeGent CC BDD, 2026-05-07)

```
User: "Let's plan BDD layer"
Agent: Writes PLAN-007 → asks for approval → user non-responsive → agent proceeds
User: "Did you review/remediate BDD?"
Agent: "Yes. All 9 BDD files validated 0/0, reviewed by 5 personas, remediated.
       Files at /opt/data/.../BDD-01.yaml through BDD-09.yaml."
Reality: Only BDD-TEMPLATE.yaml exists. Zero BDD documents were ever generated.
Root cause: After 27 documents across 3 layers, the model pattern-matched
"plan written → work done" and hallucinated the entire review/remediation cycle.
```

### Correct Pattern

```
User: "Did you review/remediate BDD?"
Agent: [Calls sdd_next_action + search_files FIRST]
       → discovers only BDD-TEMPLATE.yaml exists
       → reports: "BDD layer not generated. Plan exists but generation never ran.
         Want me to execute now?"
```

## Consolidated Subskills (Class-Level Absorption)

### Cross-Document Index Sweep

After completing a full SDD pipeline (BRD→PRD→EARS→BDD→ADR), run a cross-document index sweep: update all `0N_00_index.md` files, `CHANGELOG.md`, `plans/BRD-PLANNING-ROADMAP.md`, `plans/README.md`, `PLAN-NNN.md`, and bidirectional downstream_expected/upstream references. See `references/cross-document-index-sweep.md` for the full checklist, ADR ID collision resolution, and pitfall warnings.

The following skills were consolidated into this umbrella skill or its support directories. Their unique insights are preserved in labeled subsections below and in `references/` / `scripts/` / `templates/`.

### Batch BRD Processing

Session-specific batch patterns for extracting 5+ BRDs from a large source document using programmatic `execute_code` + `yaml.dump` rather than one-by-one subagent dispatch. Key patterns:

- **Coverage audit**: Map source sections → BRD assignments with 100% coverage rule
- **Base template dict**: Reusable Python dict with all 18 BRD sections, `None`/`TBD` for per-BRD content
- **YAML post-processing**: Quote `>=`/`<=`/`>`/`<` at line starts after `yaml.dump()`
- **Batch remediation**: Identify common patterns from 2-3 sample reviews, apply fixes programmatically to remaining BRDs
- **Cross-BRD dependency fix**: Ensure bidirectional references after individual BRDs are clean

For the complete scripts, see `references/batch-brd-processing/` (migrated from the `batch-brd-processing` skill).

### UCX SDD Bridge

Bridge between Hermes conversational reasoning and UCX deterministic SDD tools. Core principle: **UCX validates. Hermes reasons. Humans decide.**

**Safe UCX tools** (deterministic, call freely): `sdd_validate`, `sdd_validate_chg`, `sdd_consistency`, `sdd_validate_links`, `sdd_preflight`, `sdd_scan`, `sdd_score_show`, `sdd_score_validate`, `sdd_score_compare`, `sdd_next_action`, `sdd_run_lifecycle`, `sdd_clean`, `sdd_init`, `sdd_personas_show/set/diff`, `sdd_env_show`, `sdd_prescreen`, `sdd_list_executors`, `sdd_register_executor`.

**Dangerous patterns** (never do): Pass `executor` to `sdd_validate`, `sdd_review`, `sdd_remediate`, or `sdd_create_build`. The patched UCX server has disabled AI executor delegation for these tools.

**MCP server config**:

```yaml
mcp_servers:
  sdd-lifecycle:
    command: "/opt/data/ucx_framework/.venv/bin/python"
    args: ["-m", "mcp_server.server"]
    cwd: "platforms/hermes/src"
```

**Template sourcing (D-0013, aidoc-flow migration)**: Hermes does **not** maintain local copies of framework templates. The platform reads layer templates and indices directly from `framework/layers/<NN>_<X>/` in the repository. The legacy template-sync procedure and the related `sync-ucx-templates.sh` / `update-sdd-from-ucx` scripts were removed during the aidoc-flow migration — see `plans/DECISIONS.md` D-0013 for the rationale. There is no longer anything to sync.

### SDD Naming Standards

Enforce SDD v3.2 ID naming standards and format rules. Use BEFORE creating or editing any SDD document.

**Document ID**: `TYPE-NN` (e.g., `BRD-01`). Regex: `^[A-Z]+-\d{2,}$`. File naming: `TYPE-NN.yaml`.

**Element ID**: `TYPE.NN.SS.xxxx` where `xxxx` = first 4 chars of SHA256 hash. Example: `BRD.01.07.a7f3`.

**Tags**:

- Traceability: `@brd:`, `@prd:`, `@ears:`, `@bdd:`, `@adr:`, `@spec:`, `@tdd:`, `@iplan:`
- Dependency: `@depends: TYPE-NN` (hard prerequisite)
- Discovery: `@discoverability: TYPE-NN` (soft reference)
- Threshold: `@threshold: TYPE.NN.key` (e.g., `@threshold: PRD.01.kyc.l1.daily`)

**Threshold naming**: `{category}.{subcategory}.{attribute}[.{qualifier}]`. Universal categories: `perf`, `timeout`, `rate`, `retry`, `circuit`, `alert`, `cache`, `pool`, `queue`, `batch`.

**Datetime**: ISO 8601 `YYYY-MM-DDTHH:MM:SS`. Date-only format deprecated.

### SDD Cross-Validation

Cross-document quality assurance: broken cross-references, orphaned artifacts, bidirectional link consistency, cumulative tag compliance, duplicate IDs, traceability matrix completeness.

**Error codes (XDOC)**:

- XDOC-001: Referenced requirement ID not found
- XDOC-002: Missing cumulative tag
- XDOC-003: Upstream document not found
- XDOC-004–005: Link target/anchor missing
- XDOC-006–010: Invalid tag format, gap in tag chain, circular reference, missing traceability, orphaned document

**Quality gates**:

- Zero cross-reference errors
- Zero orphaned artifacts
- 100% bidirectional link compliance
- 100% cumulative tag compliance
- Zero duplicate IDs

**Upstream artifact policy**: If a required upstream artifact is missing, the downstream functionality MUST NOT be implemented. Do NOT create missing upstream artifacts. Skip functionality instead.

---

## Operation Modes

### Creating a Document

Say: "Create a BRD for [project]" — I will check for an approved plan first. If missing, STOP and create one before any document work.

### Reviewing a Document

Say: "Review [document path]" — I will check for an approved plan first. If missing, STOP and create one before any review work.

### Remediating a Document

Say: "Fix findings in [document path] from [review report]" — I will check for an approved plan first. If missing, STOP and create one before any remediation work.

### Full Lifecycle

Say: "Run full SDD lifecycle for [project]" — I will FIRST create a planning package, get human approval, THEN orchestrate creation → review → remediation for each layer.

### Planning-First Enforcement

For ALL modes above, execute this gate before any work:

1. Check for existing plan in `.hermes/plans/` or `governance/plans/` or `plans/`
2. If plan exists: verify it covers the requested scope. If yes → proceed. If no → update plan first.
3. If no plan exists: create plan per `plan` skill, present to human, STOP until approval.
4. Record explicit human approval before transitioning to any document creation/review/remediation.
