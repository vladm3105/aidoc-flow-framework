---
title: "Sprint Document Preparation Guide"
tags:
  - framework-guide
  - shared-architecture
  - project-management
  - sdd-workflow
  - sprint-governance
custom_fields:
  document_type: guide
  artifact_type: REF
  layer: 0
  priority: shared
  development_status: active
  location: ai_dev_ssd_flow/PROJECT/SPRINT_DOCUMENT_GUIDE.md
  created: 2026-02-16
  updated: 2026-02-16
---

# Sprint Document Preparation Guide

**Version**: 1.0
**Reference**: PROJECT_MODEL.md v2.2

---

## Overview

The SDD Project Model v2.2 organizes document preparation into three tiers aligned with sprint phases:

```

                        DOCUMENT PREPARATION TIMELINE                         

                                                                              
  SPRINT 0            SPRINT 1 (Prep)       SPRINT N (Implementation)      
  (Research)          (Specification)       (Execution)                    
                            
                                                                            
                              
   TIER 1            TIER 2              TIER 3                      
   Strategic      Spec           Execution                   
   L1-L5             L6-L11              L12-L14                     
                              
                                                                            
  BRD, PRD, EARS      SYS, REQ, CTR         Code, Tests                    
  BDD, ADR            SPEC, TSPEC, TASKS    CHG (if changes)               
                                                                            
  GATE-01            GATE-05, GATE-09     GATE-12                       
                                                                            

```

---

## Sprint 0: Research & Strategic Foundation

**Purpose**: Establish business intent and resolve blocking questions before implementation.

**Duration**: 5-7 days (before Sprint 1)

### Documents to Prepare

| Layer | Artifact | Purpose | Owner | Skill |
|:-----:|----------|---------|-------|-------|
| **L1** | **BRD** | Business requirements, objectives, success metrics | Business Owner | `/doc-brd` |
| **L2** | **PRD** | Product features, user stories, constraints | Product Manager | `/doc-prd-autopilot` |
| **L3** | **EARS** | Formal requirements (shall/when/if/where syntax) | BA/Architect | `/doc-ears-autopilot` |
| **L4** | **BDD** | Behavior scenarios (Given/When/Then) | QA Lead | `/doc-bdd-autopilot` |
| **L5** | **ADR** | Architecture decisions from research | Architect | `/doc-adr` |

### Sprint 0 Checklist

```
 0.1  Identify blocking technical questions
 0.2  Research each question
 0.3  Document decisions as ADRs (ADR-01 through ADR-NN)
 0.4  Validate BRD completeness (score ≥90)
 0.5  Generate PRD from BRD
 0.6  Generate EARS from PRD
 0.7  Generate BDD from EARS
 0.8  Set up GitHub Project board
 0.9  Pass GATE-01 validation
```

### Exit Criteria

- [ ] All Tier 1 artifacts exist and pass validation
- [ ] GATE-01 score ≥90%
- [ ] ADRs document all blocking decisions
- [ ] BDD scenarios cover all EARS requirements
- [ ] GitHub board configured with labels

### Commands

```bash
# Generate Sprint 0 artifacts
/doc-brd                      # Create BRD manually or from refs
/doc-prd-autopilot BRD-01     # Generate PRD from BRD
/doc-ears-autopilot PRD-01    # Generate EARS from PRD
/doc-bdd-autopilot EARS-01    # Generate BDD from EARS
/doc-adr                      # Create ADRs for decisions

# Validate Sprint 0 readiness
python scripts/sprint0_setup.py --check-readiness
python scripts/validate_artifact.py --path docs/ --gate GATE-01
```

---

## Sprint 1: Specification & Planning

**Purpose**: Transform business requirements into implementable specifications.

**Duration**: 2 weeks (or first implementation sprint)

### Documents to Prepare

| Layer | Artifact | Purpose | Owner | Skill |
|:-----:|----------|---------|-------|-------|
| **L6** | **SYS** | System requirements from ADR decisions | Architect | `/doc-sys-autopilot` |
| **L7** | **REQ** | Atomic requirements (single responsibility) | Architect | `/doc-req-autopilot` |
| **L8** | **CTR** | Data contracts, API schemas | Developer | `/doc-ctr-autopilot` |
| **L9** | **SPEC** | Technical specifications (YAML format) | Developer | `/doc-spec-autopilot` |
| **L10** | **TSPEC** | Test specifications (unit, integration, e2e) | QA Lead | `/doc-tspec-autopilot` |
| **L11** | **TASKS** | Task breakdown for implementation | Developer | `/doc-tasks-autopilot` |

### Sprint 1 Workflow

```
ADR-01  SYS-01  REQ-01  SPEC-01  TSPEC-01  TASKS-01
                                                            
                                                            
                                                      GitHub Issues
                                                            
                                 CTR-01                      
                                 (optional)                  
                                                             
              
                                                   
                                                   
GATE-05 validation                           GATE-09 validation
```

### Exit Criteria

- [ ] SYS requirements decomposed from ADRs
- [ ] REQ elements have single responsibility
- [ ] CTR contracts defined (if external APIs)
- [ ] SPEC has implementation-ready YAML
- [ ] TSPEC defines test cases per requirement
- [ ] TASKS breakdown synced to GitHub Issues
- [ ] GATE-05 and GATE-09 validation ≥90%

### Commands

```bash
# Generate Sprint 1 specification artifacts
/doc-sys-autopilot ADR-01      # Generate SYS from ADR
/doc-req-autopilot SYS-01      # Generate REQ from SYS
/doc-ctr-autopilot REQ-01      # Generate CTR from REQ (optional)
/doc-spec-autopilot REQ-01     # Generate SPEC from REQ
/doc-tspec-autopilot SPEC-01   # Generate TSPEC from SPEC
/doc-tasks-autopilot SPEC-01   # Generate TASKS from SPEC

# Sync to GitHub
python scripts/tasks_to_github.py \
  --tasks-file docs/11_TASKS/TASKS-01.yaml \
  --repo owner/repo \
  --project-number 31

# Validate
python scripts/validate_artifact.py --path docs/ --gate GATE-05
python scripts/validate_artifact.py --path docs/ --gate GATE-09
```

---

## Sprint N: Implementation Execution

**Purpose**: Implement code and tests based on specifications.

**Duration**: 2 weeks per sprint

### Documents Created During Implementation

| Layer | Artifact | Purpose | When Created |
|:-----:|----------|---------|--------------|
| **L12** | **Code** | Implementation with traceability tags | During sprint |
| **L13** | **Tests** | Unit, integration, e2e tests | During sprint |
| **L14** | **Release** | Deployment validation | Sprint end |
| - | **CHG** | Change requests (if scope changes) | As needed |

### Implementation Sprint Workflow

```
Sprint Planning  Development  PR Review  Sprint Review
                                                       
                                                       
                                                       
 TASKS→Issues        Code + Tests    Validation      Retrospective
                                                       
                                                       
                                                       
                                   GATE-12         CHG (if needed)
                                                       
                         
                                         
      
                    Feedback Loop
```

### Code Implementation Requirements

```python
# Example: Code with traceability tags
# @brd: BRD-01:FR-03
# @prd: PRD-01:PRD.01.03
# @spec: SPEC-01
# @tasks: TASKS-01.02.01

def check_budget_threshold(current_spend: Decimal, budget: Decimal) -> bool:
    """Check if current spend exceeds budget threshold."""
    ...
```

### CHG Documents (Created Only If Needed)

| Trigger | CHG Level | Documents Updated |
|---------|-----------|-------------------|
| Bug fix (no spec change) | L1 (Patch) | TASKS only |
| Scope change | L2 (Minor) | PRD → TASKS cascade |
| Architecture change | L3 (Major) | Full re-specification |

### Exit Criteria

- [ ] All TASKS completed and issues closed
- [ ] Tests passing with coverage ≥85%
- [ ] Traceability tags in code match specs
- [ ] GATE-12 validation passed
- [ ] CHG documents created for any scope changes
- [ ] Drift check shows <7 days lag

### Commands

```bash
# During implementation
/trace-check                   # Validate traceability tags

# At sprint end
python scripts/validate_artifact.py --path src/ --gate GATE-12
python scripts/drift_check.py --sdd-root docs/ --repo owner/repo

# If changes needed
python scripts/chg_generator.py \
  --description "Scope change description" \
  --affected-layers 2,9,11 \
  --output docs/CHG/
```

---

## Complete Document Flow Summary

```
SPRINT 0                    SPRINT 1                    SPRINT N
(Research)                  (Specification)             (Implementation)


                           
    BRD L1                    SYS L6
                           
                                 
                                 
                           
    PRD L2                    REQ L7                    
                                                  Code L12
                                                          
                                                   
                                                       
    EARS L3                                    
                          CTR L8  SPEC L9        Tests L13
                                                
                                                            
                                                        
    BDD L4                                       
                                    TSPEC L10      Release L14
                                                   
                                       
    ADR L5                                                 
                                                  CHG
                                        TASKS L11   
                                                    (if needed)
                                           
                                           
                                     GitHub Issues


    GATE-01                    GATE-05 + GATE-09              GATE-12
```

---

## Quick Reference Table

| Sprint | Gate | Layers | Documents | Skills |
|--------|------|--------|-----------|--------|
| **Sprint 0** | GATE-01 | L1-L5 | BRD, PRD, EARS, BDD, ADR | `/doc-brd`, `/doc-prd-autopilot`, `/doc-ears-autopilot`, `/doc-bdd-autopilot`, `/doc-adr` |
| **Sprint 1** | GATE-05, GATE-09 | L6-L11 | SYS, REQ, CTR, SPEC, TSPEC, TASKS | `/doc-sys-autopilot`, `/doc-req-autopilot`, `/doc-ctr-autopilot`, `/doc-spec-autopilot`, `/doc-tspec-autopilot`, `/doc-tasks-autopilot` |
| **Sprint N** | GATE-12 | L12-L14 | Code, Tests, Release, CHG | Implementation, `/trace-check` |

---

## Decision Matrix: When to Create Documents

| Scenario | Sprint 0 | Sprint 1 | Sprint N |
|----------|:--------:|:--------:|:--------:|
| New feature | Full Tier 1 | Full Tier 2 | Code + Tests |
| Enhancement | Update PRD→BDD | Update REQ→TASKS | Code + Tests |
| Bug fix | - | - | TASKS + Code |
| Hotfix | - | - | Code only (72h retroactive docs) |
| Config change | - | ADR + TASKS | Code + Tests |
| Refactoring | - | ADR + SPEC→TASKS | Code + Tests |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-16 | Initial guide |
