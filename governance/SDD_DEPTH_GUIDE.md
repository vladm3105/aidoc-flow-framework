# SDD Depth Guide: Lite, Standard, and Full

This document explains the three depth variants of Specification-Driven Development (SDD) and helps you choose the right level for your project.

---

## Quick Decision Matrix

| If your project... | Use |
|:-------------------|:----|
| Is an MVP or prototype | **SDD-Lite** |
| Has 1-3 month timeline | **SDD-Lite** |
| Is solo developer + AI | **SDD-Lite** |
| Needs rapid iteration | **SDD-Lite** |
| Has 3-6 month timeline | **SDD-Standard** |
| Has small team (2-5 people) | **SDD-Standard** |
| Needs moderate traceability | **SDD-Standard** |
| Has regulatory requirements (SEC, FINRA, FDA, ISO) | **SDD-Full** |
| Needs complete audit trails | **SDD-Full** |
| Has multiple teams | **SDD-Full** |
| Spans 6+ months to years | **SDD-Full** |
| Requires formal architecture decisions | **SDD-Full** |

---

## SDD Depth Comparison

| Aspect | SDD-Lite | SDD-Standard | SDD-Full |
|:-------|:---------|:-------------|:---------|
| **Layers** | 3-4 | 7-8 | 15 |
| **Setup Time** | Hours | Days | Weeks |
| **Best For** | MVPs, prototypes | Production apps | Enterprise systems |
| **Team Size** | Solo + AI | Small team | Multiple teams |
| **Timeline** | 1-3 months | 3-6 months | 6+ months |
| **Traceability** | Basic (REF→TASKS) | Moderate (requirements chain) | Full bidirectional |
| **Change Management** | PR-based | PR + review gates | 4-Gate CHG system |
| **Documentation** | Minimal | Moderate | Comprehensive |

---

## Layer Mapping by Depth

### SDD-Lite (3-4 Layers)

```
Layer 0: REF (Project Description)
    ↓
Layer 1: BRD (Business Requirements - simplified)
    ↓
Layer 2: PRD (Product Requirements - simplified)
    ↓
Layer 11: TASKS (Implementation Tasks)
    ↓
GitHub Issues → Code → Deploy
```

**Layers Used:**
| Layer | Artifact | Required | Notes |
|:------|:---------|:---------|:------|
| 0 | REF | Yes | Human-written project description |
| 1 | BRD | Yes | Use `BRD-TEMPLATE.yaml` |
| 2 | PRD | Yes | Use `PRD-TEMPLATE.yaml` |
| 11 | TASKS | Yes | Use `TASKS-TEMPLATE.yaml` |

**Skipped Layers:** EARS, BDD, ADR, SYS, REQ, CTR, SPEC, TSPEC

**Traceability:** `@ref` → `@brd` → `@prd` → `@tasks`

---

### SDD-Standard (7-8 Layers)

```
Layer 0: REF (Project Description)
    ↓
Layer 1: BRD (Business Requirements)
    ↓
Layer 2: PRD (Product Requirements)
    ↓
Layer 3: EARS (Formal Requirements Syntax)
    ↓
Layer 5: ADR (Architecture Decisions)
    ↓
Layer 6: SYS (System Requirements)
    ↓
Layer 7: REQ (Atomic Requirements)
    ↓
Layer 11: TASKS (Implementation Tasks)
    ↓
GitHub Issues → Code → Tests → Deploy
```

**Layers Used:**
| Layer | Artifact | Required | Notes |
|:------|:---------|:---------|:------|
| 0 | REF | Yes | Human-written project description |
| 1 | BRD | Yes | Full business requirements |
| 2 | PRD | Yes | Full product requirements |
| 3 | EARS | Yes | Formal WHEN-THE-SHALL syntax |
| 5 | ADR | Yes | Architecture Decision Records |
| 6 | SYS | Yes | System requirements |
| 7 | REQ | Yes | Atomic requirements |
| 11 | TASKS | Yes | Full task breakdown |

**Optional Layers:** BDD (Layer 4), CTR (Layer 8)

**Skipped Layers:** SPEC, TSPEC (use inline in TASKS)

**Traceability:** Full requirements chain with `@brd` → `@prd` → `@ears` → `@adr` → `@sys` → `@req` → `@tasks`

---

### SDD-Full (15 Layers)

```
Layer 0: REF (Strategy/Reference Documents)
    ↓
Layer 1: BRD (Business Requirements)
    ↓
Layer 2: PRD (Product Requirements)
    ↓
Layer 3: EARS (Formal Requirements)
    ↓
Layer 4: BDD (Behavior Tests - Gherkin)
    ↓
Layer 5: ADR (Architecture Decisions)
    ↓
Layer 6: SYS (System Requirements)
    ↓
Layer 7: REQ (Atomic Requirements)
    ↓
Layer 8: CTR (API Contracts) [optional]
    ↓
Layer 9: SPEC (Technical Specifications - YAML)
    ↓
Layer 10: TSPEC (Test Specifications)
    ↓
Layer 11: TASKS (Code Generation Plans)
    ↓
Layer 12: IMPL (Implementation)
    ↓
Layer 13: Tests
    ↓
Layer 14: Validation
```

**All Layers Required** (except CTR which is optional)

**Change Management:** 4-Gate CHG system

| Gate | Layers | Approval Required |
|:-----|:-------|:------------------|
| GATE-01 | L1-L2 (Business/Product) | Business owner |
| GATE-05 | L5 (Architecture) | Architect |
| GATE-09 | L9-L10 (Tech Specs) | Tech lead |
| GATE-12 | L12+ (Implementation) | Developer |

**Traceability:** Full bidirectional with cumulative `@tags` in code

---

## Issue Creation by Depth

All SDD depths follow the same issue creation pattern:

```
Human creates REF/ (Project Description)
    ↓
AI Agent generates specification layers (depth varies)
    ↓
AI Agent creates GitHub Issues from TASKS
    ↓
AI Agent executes issues (ai:ready → ai:in-progress → PR)
    ↓
Review → Merge → Deploy
```

**Key Difference:** The number of specification layers between REF and TASKS varies by depth, affecting issue precision and traceability.

| Depth | Specification Layers | Issue Precision |
|:------|:--------------------|:----------------|
| **SDD-Lite** | 2 (BRD, PRD) | Good for MVPs |
| **SDD-Standard** | 6 (BRD→PRD→EARS→ADR→SYS→REQ) | Production-ready |
| **SDD-Full** | 10 (all layers) | Enterprise-grade |

---

## Scaling Between Depths

### Starting with SDD-Lite, Scaling Up

Projects can start with SDD-Lite and add layers as complexity grows:

**Phase 1 (MVP):** SDD-Lite
- REF → BRD → PRD → TASKS

**Phase 2 (Production):** Add Standard layers
- Add EARS for formal requirements
- Add ADR for architecture decisions
- Add SYS/REQ for traceability

**Phase 3 (Enterprise):** Add Full layers
- Add BDD for behavior tests
- Add SPEC/TSPEC for detailed specifications
- Enable 4-Gate CHG system

### Layer Addition Checklist

When adding layers to an existing project:

1. [ ] Generate new layer from upstream artifacts
2. [ ] Add traceability tags to existing documents
3. [ ] Update TASKS to reference new layer
4. [ ] Regenerate issues with enhanced traceability
5. [ ] Update validation scripts

---

## Templates by Depth

### SDD-Lite Templates

| Artifact | Template |
|:---------|:---------|
| BRD | `ai_dev_ssd_flow/01_BRD/BRD-TEMPLATE.yaml` |
| PRD | `ai_dev_ssd_flow/02_PRD/PRD-TEMPLATE.yaml` |
| TASKS | `ai_dev_ssd_flow/11_TASKS/TASKS-TEMPLATE.yaml` |

### SDD-Standard Templates

| Artifact | Template |
|:---------|:---------|
| BRD | `ai_dev_ssd_flow/01_BRD/BRD-TEMPLATE.yaml` |
| PRD | `ai_dev_ssd_flow/02_PRD/PRD-TEMPLATE.yaml` |
| EARS | `ai_dev_ssd_flow/03_EARS/EARS-TEMPLATE.yaml` |
| ADR | `ai_dev_ssd_flow/05_ADR/ADR-TEMPLATE.yaml` |
| SYS | `ai_dev_ssd_flow/06_SYS/SYS-TEMPLATE.yaml` |
| REQ | `ai_dev_ssd_flow/07_REQ/REQ-TEMPLATE.yaml` |
| TASKS | `ai_dev_ssd_flow/11_TASKS/TASKS-TEMPLATE.yaml` |

### SDD-Full Templates

All templates in `ai_dev_ssd_flow/` - see [ai_dev_ssd_flow/README.md](../ai_dev_ssd_flow/README.md)

---

## Governance by Depth

| Governance Aspect | SDD-Lite | SDD-Standard | SDD-Full |
|:------------------|:---------|:-------------|:---------|
| **Branching** | [BRANCHING_STRATEGY.md](./BRANCHING_STRATEGY.md) | Same | Same |
| **PR Review** | [AI_PR_Review/](./AI_PR_Review/) | Same | Same |
| **Definition of Done** | [DEFINITION_OF_DONE.md](./DEFINITION_OF_DONE.md) | Same | Same + gate approvals |
| **Release Process** | [RELEASE_PROCESS.md](./RELEASE_PROCESS.md) | Same | Same + CHG tracking |
| **Issue Lifecycle** | [AI_ISSUE_LIFECYCLE.md](./AI_ISSUE_LIFECYCLE.md) | Same | Same |
| **Change Management** | PR-based | PR + review | 4-Gate CHG |

---

## Testing Requirements by Depth

| Depth | UTEST | ITEST | STEST/FTEST | BDD |
|-------|-------|-------|-------------|-----|
| **Lite** | >=60% coverage | Optional | Optional | Not required |
| **Standard** | >=80% coverage | >=60% coverage | Critical paths | Optional |
| **Full** | >=80% coverage | >=60% coverage | Full coverage | Required |

### Execution Model

All depths follow the same test pyramid execution model:
- **CI Pipeline**: UTEST + ITEST (development)
- **QA Staging**: STEST + FTEST + BDD (pre-production)

See: [`ai_dev_ssd_flow/10_TSPEC/TEST_PYRAMID_GUIDE.md`](../ai_dev_ssd_flow/10_TSPEC/TEST_PYRAMID_GUIDE.md)

---

## Summary

| Choose | When |
|:-------|:-----|
| **SDD-Lite** | MVP, prototype, solo + AI, rapid iteration, 1-3 months |
| **SDD-Standard** | Production app, small team, moderate traceability, 3-6 months |
| **SDD-Full** | Enterprise, regulated, multiple teams, full audit trail, 6+ months |

All three depths use the same SDD methodology - the difference is how many specification layers you generate before creating implementation tasks and issues.
