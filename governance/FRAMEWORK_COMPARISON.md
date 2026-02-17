# Framework Comparison: Issues Flow vs SDD Flow

This document explains the two complementary frameworks in the Docs Flow Framework repository and helps you choose the right one for your project.

---

## Quick Decision Matrix

| If your project... | Use |
|:-------------------|:----|
| Is an MVP or prototype | **Issues Flow** |
| Has 1-6 month timeline | **Issues Flow** |
| Is solo or small team + AI | **Issues Flow** |
| Needs rapid iteration | **Issues Flow** |
| Has regulatory requirements (SEC, FINRA, FDA, ISO) | **SDD Flow** |
| Needs complete audit trails | **SDD Flow** |
| Has multiple teams | **SDD Flow** |
| Spans months to years | **SDD Flow** |
| Requires formal architecture decisions | **SDD Flow** |

---

## Side-by-Side Comparison

| Aspect | Issues Flow | SDD Flow |
|:-------|:------------|:---------|
| **Directory** | `governance/issues_flow/` | `ai_dev_ssd_flow/` |
| **Full Name** | AI Project Issues Flow | AI Dev Specification-Driven Development |
| **Purpose** | Lightweight AI-first project governance | Formal requirements traceability |
| **Project Size** | Small-medium | Large/enterprise |
| **Timeline** | 1-6 months | Months to years |
| **Team Size** | Solo or small team + AI | Multiple teams |
| **Documentation** | PROJECT_PLAN + IPLANs | 15-layer formal hierarchy |

---

## Issue Creation: The Key Difference

### Issues Flow: Direct from Project Description

```
00_REF/ (Project Description)
       ↓
  Human reads requirements
       ↓
  Human creates GitHub issue
       ↓
  AI agent executes when ai:ready
       ↓
  PR → Review → Merge → Deploy
```

**Characteristics:**
- Fast setup (minutes)
- Human judgment for task breakdown
- GitHub issues are the tracking unit
- Traceability via issue links
- 4-stage loop: Dev → Deploy → QA → Bug Fix

### SDD Flow: Via 15-Layer Documentation

```
00_REF/ (Project Description)
       ↓
  Layer 1: BRD (Business Requirements)
       ↓
  Layer 2: PRD (Product Requirements)
       ↓
  Layer 3: EARS (Formal Requirements)
       ↓
  Layer 4: BDD (Behavior Tests)
       ↓
  Layer 5: ADR (Architecture Decisions)
       ↓
  Layer 6: SYS (System Requirements)
       ↓
  Layer 7: REQ (Atomic Requirements)
       ↓
  Layer 8: CTR (API Contracts) [optional]
       ↓
  Layer 9: SPEC (Technical Specifications)
       ↓
  Layer 10: TSPEC (Test Specifications)
       ↓
  Layer 11: TASKS (Code Generation Plans)
       ↓
  Issues derived from TASKS
       ↓
  Code → Tests → Validation → Production
```

**Characteristics:**
- Thorough documentation (days-weeks setup)
- AI generates most layers automatically
- TASKS documents define implementation
- Cumulative @tags for traceability
- 4-Gate change management (CHG)

---

## Documentation Artifacts

### Issues Flow Documents

| Document | Purpose |
|:---------|:--------|
| `PROJECT_PLAN.md` | Phases, sprints, task specs |
| `ROADMAP.md` | Timeline and dependencies |
| `IPLAN-*.md` | Session-scoped execution plans |
| GitHub Issues | Task tracking and acceptance criteria |

### SDD Flow Documents (15 Layers)

| Layer | Artifact | Purpose |
|:------|:---------|:--------|
| 0 | Strategy | External business documents |
| 1 | BRD | Business requirements |
| 2 | PRD | Product requirements |
| 3 | EARS | Formal WHEN-THE-SHALL requirements |
| 4 | BDD | Gherkin behavior tests |
| 5 | ADR | Architecture decisions |
| 6 | SYS | System requirements |
| 7 | REQ | Atomic requirements |
| 8 | CTR | API contracts (optional) |
| 9 | SPEC | Technical specifications (YAML) |
| 10 | TSPEC | Test specifications |
| 11 | TASKS | Code generation plans |
| 12-14 | Code/Tests/Validation | Implementation |

---

## Traceability

### Issues Flow: GitHub Links

```markdown
## Issue #42: Implement user auth

Closes #41 (parent epic)
Related: #38, #39
Blocks: #45
```

Traceability is maintained through:
- GitHub issue references (`#NNN`)
- PR links (`Closes #NNN`)
- Project board columns
- Labels (phase, component, priority)

### SDD Flow: Cumulative Tags

```python
"""User authentication service.

@brd: BRD.01.01.30, BRD.01.01.06
@prd: PRD.02.07.05
@ears: EARS.03.24.01
@bdd: BDD.04.13.01
@adr: ADR-010
@sys: SYS.08.25.02
@req: REQ-045
@spec: SPEC-003
@tasks: TASKS-015
@impl-status: complete
"""
```

Traceability is maintained through:
- Cumulative @tags in code
- Automated matrix generation
- Validation scripts
- Complete audit trails

---

## Change Management

### Issues Flow: PR-Based

1. Developer creates PR
2. AI review via Claude Code CLI
3. Human approval (1+ reviewer)
4. Merge to main
5. Phase-gated deployment

### SDD Flow: 4-Gate CHG System

| Gate | Layers | Approval |
|:-----|:-------|:---------|
| GATE-01 | L1-L2 (Business/Product) | Business owner |
| GATE-05 | L5 (Architecture) | Architect |
| GATE-09 | L9-L10 (Tech Specs) | Tech lead |
| GATE-12 | L12+ (Implementation) | Developer |

---

## Shared Governance

Both frameworks use these shared documents:

| Document | Purpose |
|:---------|:--------|
| `shared/AI_PR_Review/` | Automated PR review workflows |
| `shared/BRANCHING_STRATEGY.md` | Git workflow conventions |
| `shared/DEFINITION_OF_DONE.md` | Completion criteria |
| `shared/RELEASE_PROCESS.md` | Versioning and deployment |
| `shared/github/` | GitHub Actions, tools, GHES runner |

---

## When to Switch Frameworks

### Start with Issues Flow, Move to SDD Flow When:

- Project scope expands significantly
- Regulatory compliance becomes required
- Multiple teams need coordination
- Formal audit trails are needed
- Architecture decisions need documentation

### Start with SDD Flow, Simplify to Issues Flow When:

- Project is simpler than expected
- Speed becomes critical
- Formal documentation is overhead
- Solo developer or small team

---

## Getting Started

### Issues Flow Quick Start

```bash
# Copy issues_flow governance to your project
cp -r governance/issues_flow/ /path/to/your/project/governance/

# Configure placeholders
./governance/scripts/project_setup/validate_configuration.sh

# Create your first issue with ai:ready label
```

### SDD Flow Quick Start

```bash
# Copy SDD templates to your project
cp -r ai_dev_ssd_flow/ /path/to/your/project/docs/

# Start with BRD
cp ai_dev_ssd_flow/BRD/BRD-MVP-TEMPLATE.md docs/BRD/BRD-001.md

# AI generates downstream layers automatically
```

---

## Summary

| Choose | When |
|:-------|:-----|
| **Issues Flow** | Speed matters, small team, MVP/prototype, 1-6 months |
| **SDD Flow** | Compliance matters, multiple teams, enterprise, long-term |
| **Both** | Start Issues Flow for MVP, add SDD layers as project matures |
