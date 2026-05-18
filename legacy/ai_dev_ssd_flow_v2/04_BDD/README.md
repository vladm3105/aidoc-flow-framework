# Behavior-Driven Development (BDD) — Layer 4

## Overview

BDD defines executable acceptance scenarios using Given-When-Then (Gherkin) syntax,
translating EARS formal requirements into testable behaviors.

**Workflow**: BRD → PRD → EARS → BDD → ADR → SYS → REQ → CTR → SPEC → TSPEC → TASKS → Code

**Execution**: QA STAGING ONLY — do NOT run in CI pipeline. Use UTEST/ITEST for CI.

## C4 Model Position

BDD is a **refinement step** alongside EARS that formalizes the transition from
Context (BRD) to Container (PRD). BDD translates EARS requirements into executable
Given-When-Then scenarios.

```text
Context (BRD)    — business environment, actors, boundaries
  └─ EARS/BDD    — formalize Context→Container transition              ← this layer
Container (PRD)  — product features, functional blocks
  └─ ADR         — decisions that shape Component architecture
Component (SYS)  — system structure, interfaces, quality attributes
  └─ REQ/CTR     — decompose Component→Code into atomic units
Code (SPEC)      — implementation-ready specifications
  └─ TSPEC       — test specifications
  └─ TASKS       — implementation task breakdown
```

## Files

| File | Purpose |
|------|---------|
| `BDD-TEMPLATE.yaml` | Single source of truth — template with Gherkin guidance in `_example` fields |
| `BDD-00_index.md` | BDD registry — tracks planned and active BDD documents per project |

BDD instances (actual test files) are `.yaml` files generated from the YAML template.

## Template Sync Rule

**IMPORTANT**: `BDD-TEMPLATE.yaml` exists in two locations that must stay in sync:

| Location | Role |
|----------|------|
| `ucx_flow_v3/04_BDD/BDD-TEMPLATE.yaml` | **Canonical source** — edit here |
| `mcp_sdd/templates/BDD-TEMPLATE.yaml` | **Runtime copy** — used by MCP tools |

After any change to the canonical source, copy it to the runtime location:

```bash
cp ucx_flow_v3/04_BDD/BDD-TEMPLATE.yaml mcp_sdd/templates/BDD-TEMPLATE.yaml
```

## MCP Tools (mcp_sdd)

| Tool | Purpose |
|------|---------|
| `sdd_create` | Generate BDD from template |
| `sdd_validate` | Structural validation |
| `sdd_score_validate` | ADR-Ready score (>=90/100 to proceed to ADR) |
| `sdd_consistency` | Cross-document traceability check |
| `sdd_next_action` | Lifecycle advisor |

## Gherkin Syntax Quick Reference

```gherkin
@scenario-type:success @p0-critical @scenario-id:BDD.01.03.xxxx
Scenario: User logs in with valid credentials
  Given a registered user with valid credentials
  When the user submits login request
  Then the system SHALL authenticate the user
  And a session token SHALL be returned WITHIN @threshold:PRD.01.perf.auth.p95
```

## Element IDs

Hash-based, content-derived IDs scoped to BDD content:

```text
Format: BDD.{doc_id}.{section_id}.{hash}
Example: BDD.01.03.d7a2
```

## Upstream Traceability

BDD requires cumulative tags (Layer 4 — all three mandatory):

```text
@ears:EARS.NN.03.xxxx    (links to EARS requirement)
@prd:PRD.NN.09.xxxx      (links to PRD functional requirement)
@brd:BRD.NN.07.xxxx      (links to BRD functional requirement)
```

Note: NO spaces after colon in Gherkin tags.

## Archive

`BDD_v1_archive/` contains deprecated files from the previous dual-file template
approach. See `BDD_v1_archive/README.md` for migration details.
