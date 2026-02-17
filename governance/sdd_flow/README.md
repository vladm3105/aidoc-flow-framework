# SDD Flow Governance

Governance references for **AI Dev SDD Flow** (Specification-Driven Development) - the 15-layer formal documentation framework for large/enterprise/regulated projects.

> **Note**: SDD Flow documentation lives in [`ai_dev_ssd_flow/`](../../ai_dev_ssd_flow/). This directory provides governance references and quick links.

---

## When to Use SDD Flow

| Criteria | Use SDD Flow |
|:---------|:-------------|
| Project size | Large/enterprise |
| Timeline | Months to years |
| Compliance | SEC, FINRA, FDA, ISO required |
| Traceability | Full audit trails needed |
| Team size | Multiple teams |
| Documentation | Formal requirements hierarchy |

For small-medium AI-first projects, see [`issues_flow/`](../issues_flow/).

---

## Core Documentation

| Document | Purpose |
|:---------|:--------|
| [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../../ai_dev_ssd_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) | Complete SDD methodology (15-layer architecture) |
| [ID_NAMING_STANDARDS.md](../../ai_dev_ssd_flow/ID_NAMING_STANDARDS.md) | Document ID format (BRD-01, PRD-02, etc.) |
| [TRACEABILITY.md](../../ai_dev_ssd_flow/TRACEABILITY.md) | Cumulative tagging hierarchy (@brd, @prd, etc.) |
| [TRACEABILITY_SETUP.md](../../ai_dev_ssd_flow/TRACEABILITY_SETUP.md) | Validation setup and CI/CD integration |

---

## 15-Layer Architecture

```
Layer 0:  Strategy (external documents)
Layer 1:  BRD (Business Requirements)
Layer 2:  PRD (Product Requirements)
Layer 3:  EARS (Formal Requirements)
Layer 4:  BDD (Behavior Tests)
Layer 5:  ADR (Architecture Decisions)
Layer 6:  SYS (System Requirements)
Layer 7:  REQ (Atomic Requirements)
Layer 8:  CTR (API Contracts) [optional]
Layer 9:  SPEC (Technical Specifications)
Layer 10: TSPEC (Test Specifications)
Layer 11: TASKS (Code Generation Plans)
Layer 12: Code (Implementation)
Layer 13: Tests (Test Suite)
Layer 14: Validation (Production)
```

---

## Issue Creation in SDD Flow

Unlike Issues Flow where issues are created directly from project description, SDD Flow creates formal documentation first:

```
00_REF (Project Description)
    ↓
BRD → PRD → EARS → BDD → ADR → SYS → REQ → SPEC → TASKS
    ↓
Issues derived from TASKS layer (Layer 11)
```

Each TASKS document contains TODO items that become GitHub issues for implementation.

---

## Change Management

SDD Flow uses the **4-Gate CHG System** for change control:

| Gate | Layer | Purpose |
|:-----|:------|:--------|
| GATE-01 | L1-L2 | Business/Product requirement changes |
| GATE-05 | L5 | Architecture decision changes |
| GATE-09 | L9-L10 | Technical specification changes |
| GATE-12 | L12+ | Implementation/code changes |

See [CHG/](../../ai_dev_ssd_flow/CHG/) for change management documentation.

---

## Domain Adaptation

| Document | Purpose |
|:---------|:--------|
| [DOMAIN_ADAPTATION_GUIDE.md](../../ai_dev_ssd_flow/DOMAIN_ADAPTATION_GUIDE.md) | Adapting framework to specific domains |
| [FINANCIAL_DOMAIN_CONFIG.md](../../ai_dev_ssd_flow/FINANCIAL_DOMAIN_CONFIG.md) | Financial sector configuration |
| [SOFTWARE_DOMAIN_CONFIG.md](../../ai_dev_ssd_flow/SOFTWARE_DOMAIN_CONFIG.md) | Generic software configuration |

---

## Validation Scripts

Located in [`ai_dev_ssd_flow/scripts/`](../../ai_dev_ssd_flow/scripts/):

| Script | Purpose |
|:-------|:--------|
| `extract_tags.py` | Extract @tags from source files |
| `validate_tags_against_docs.py` | Validate cumulative tagging hierarchy |
| `generate_traceability_matrices.py` | Auto-generate bidirectional matrices |
| `validate_requirement_ids.py` | Validate REQ-ID format |

---

## Shared Governance

SDD Flow also uses shared governance documents:

- [AI PR Review](../shared/AI_PR_Review/) - Automated PR review
- [Branching Strategy](../shared/BRANCHING_STRATEGY.md) - Git workflow
- [Definition of Done](../shared/DEFINITION_OF_DONE.md) - Completion criteria
- [Release Process](../shared/RELEASE_PROCESS.md) - Versioning and deployment
