---
title: "Change Management Guide"
tags:
  - framework-guide
  - change-management
  - shared-architecture
custom_fields:
  document_type: guide
  priority: shared
  development_status: active
  version: "2.0"
  last_updated: "2026-02-05"
  workflow_layers: 15
---

# Change Management Guide

This guide defines the universal standard for managing changes in any AI Development Flow project, from minor bug fixes to major architectural pivots.

## 1. Overview

### 1.1 Change Management Philosophy

The SDD framework handles changes through a structured approach that:
- **Preserves history** through immutable artifacts
- **Maintains traceability** across all 15 layers
- **Scales appropriately** from patches to pivots
- **Supports TDD workflow** with TSPEC integration

### 1.2 Key Concepts

| Concept | Description |
|---------|-------------|
| **Change Level** | L1 (Patch), L2 (Minor), L3 (Major) |
| **Change Source** | Where the change originates (5 sources) |
| **Impact Scope** | Which layers are affected |
| **Regeneration** | Downstream artifacts that need updating |

## 2. Change Classification System

### 2.1 Three Levels of Change

```text
┌─────────────────────────────────────────────────────────────────────┐
│                    CHANGE CLASSIFICATION                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  L1 PATCH          L2 MINOR           L3 MAJOR                     │
│  ──────────        ──────────         ──────────                   │
│  Bug fixes         Feature adds       Architecture pivots          │
│  Typos             Enhancements       Breaking changes             │
│  Clarifications    Non-breaking       Mass deprecation             │
│                                                                     │
│  Edit in place     Lightweight CHG    Full CHG process             │
│  Version bump      Partial regen      Full cascade                 │
│                                                                     │
│  ◄── Increasing Impact & Process Overhead ──►                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Level Decision Flowchart

```text
                    ┌─────────────────────┐
                    │  Change Requested   │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Breaks backward     │
                    │ compatibility?      │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │ No             │                │ Yes
              ▼                │                ▼
    ┌─────────────────┐        │      ┌─────────────────┐
    │ Requires ADR    │        │      │    L3 MAJOR     │
    │ changes?        │        │      │  Full CHG       │
    └────────┬────────┘        │      └─────────────────┘
             │                 │
    ┌────────┼────────┐        │
    │ No     │        │ Yes    │
    ▼        │        ▼        │
┌────────┐   │   ┌─────────────────┐
│Affects │   │   │    L3 MAJOR     │
│2+ layers│  │   │  Full CHG       │
└───┬────┘   │   └─────────────────┘
    │        │
┌───┼───┐    │
│No │   │Yes │
▼   │   ▼    │
┌───────┐ ┌─────────────────┐
│L1     │ │    L2 MINOR     │
│PATCH  │ │ Lightweight CHG │
└───────┘ └─────────────────┘
```

## 3. Five Change Sources

### 3.1 Change Source Map

```text
┌─────────────────────────────────────────────────────────────────────┐
│                      CHANGE SOURCES                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│     ┌──────────────┐                                                │
│     │ 1. UPSTREAM  │◄── Business/Product/Market                     │
│     │   (L1-L4)    │    BRD, PRD, EARS, BDD                        │
│     └──────┬───────┘                                                │
│            ▼                                                        │
│     ┌──────────────┐                                                │
│     │ 2. MIDSTREAM │◄── Architecture/Design                         │
│     │   (L5-L11)   │    ADR, SYS, REQ, CTR, SPEC, TSPEC, TASKS     │
│     └──────┬───────┘                                                │
│            ▼                                                        │
│     ┌──────────────┐                                                │
│     │ 3. DOWNSTREAM│◄── Implementation/Defects                      │
│     │   (L12-L14)  │    Code, Tests, Validation                    │
│     └──────┬───────┘                                                │
│            ▼                                                        │
│     ┌──────────────┐                                                │
│     │ 4. EXTERNAL  │◄── Environment/Dependencies                    │
│     │   (Outside)  │    Security, APIs, Libraries                  │
│     └──────┬───────┘                                                │
│            ▼                                                        │
│     ┌──────────────┐                                                │
│     │ 5. FEEDBACK  │◄── Production/Operations                       │
│     │   (Post-L14) │    Incidents, User feedback                   │
│     └──────────────┘                                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Source Details

#### Source 1: UPSTREAM (Business-Driven)

**Origin**: Layers 1-4 (BRD, PRD, EARS, BDD)
**Direction**: Top-down cascade to L14

| Trigger | Example | Typical Level |
|---------|---------|---------------|
| Market feedback | "Customers need mobile support" | L2-L3 |
| Stakeholder request | "Add compliance reporting" | L2-L3 |
| Regulatory change | "GDPR data export required" | L2-L3 |
| User story refinement | "Clarify acceptance criteria" | L1-L2 |

**Guide**: `sources/UPSTREAM_CHANGE_GUIDE.md`

#### Source 2: MIDSTREAM (Architecture-Driven)

**Origin**: Layers 5-11 (ADR, SYS, REQ, CTR, SPEC, TSPEC, TASKS)
**Direction**: Bi-directional (may bubble up or cascade down)

| Trigger | Example | Typical Level |
|---------|---------|---------------|
| Architecture pivot | "Switch to microservices" | L3 |
| Technology decision | "Use GraphQL instead of REST" | L3 |
| Contract change | "API v2 with breaking changes" | L2-L3 |
| Spec optimization | "Better algorithm found" | L1-L2 |
| Test strategy change | "Add performance testing" | L2 |

**Guide**: `sources/MIDSTREAM_CHANGE_GUIDE.md`

#### Source 3: DOWNSTREAM (Defect-Driven)

**Origin**: Layers 12-14 (Code, Tests, Validation)
**Direction**: Bottom-up (may bubble to source layer)

| Trigger | Example | Typical Level |
|---------|---------|---------------|
| Code bug | "Null pointer exception" | L1 |
| Test failure | "Integration test fails" | L1-L2 |
| Validation issue | "Performance below threshold" | L1-L3 |

**Guide**: `sources/DOWNSTREAM_CHANGE_GUIDE.md`

#### Source 4: EXTERNAL (Environment-Driven)
**Origin**: Outside the layer system
**Direction**: Inject at appropriate layer

| Trigger | Example | Typical Level |
|---------|---------|---------------|
| Security vulnerability | "CVE in dependency" | L1-L3 |
| Dependency deprecation | "Library v2 EOL" | L2-L3 |
| Third-party API change | "Payment API changed" | L2-L3 |
| Infrastructure change | "Cloud service deprecated" | L3 |

**Guide**: `sources/EXTERNAL_CHANGE_GUIDE.md`

#### Source 5: FEEDBACK (Production-Driven)
**Origin**: Post-Layer 14 (Production environment)
**Direction**: Loop back to source layer

| Trigger | Example | Typical Level |
|---------|---------|---------------|
| Production incident | "Service crashed under load" | L1-L3 |
| User feedback | "Feature confusing" | L2 |
| Performance issue | "Response time degraded" | L1-L2 |
| Analytics insight | "Feature unused by 90%" | L2-L3 |

**Guide**: `sources/FEEDBACK_CHANGE_GUIDE.md`

## 4. 4-Gate Change Management System

The SDD framework implements a formal 4-Gate system for validating changes at layer boundaries.

### 4.1 Gate Overview

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                        4-GATE CHANGE MANAGEMENT SYSTEM                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│    CHANGE REQUEST                                                           │
│          │                                                                  │
│          ▼                                                                  │
│    ┌───────────────────────────────────────────────────────────────┐       │
│    │                   ROUTING DETERMINATION                        │       │
│    │              (validate_chg_routing.py)                         │       │
│    └───────────────────────────────┬───────────────────────────────┘       │
│                                    │                                        │
│         ┌──────────────────────────┼──────────────────────────────┐        │
│         │                          │                              │        │
│         ▼                          ▼                              ▼        │
│    ┌─────────┐              ┌─────────┐                    ┌──────────┐    │
│    │ GATE-01 │              │ GATE-05 │                    │ EMERGENCY│    │
│    │ L1-L4   │──────────────│ L5-L8   │                    │  BYPASS  │    │
│    │ Business│              │ Arch/Ctr│                    │  P1/Sec  │    │
│    └────┬────┘              └────┬────┘                    └────┬─────┘    │
│         │                        │                               │         │
│         │      ┌─────────────────┘                               │         │
│         ▼      ▼                                                 │         │
│    ┌─────────────┐                                               │         │
│    │   GATE-09   │◄──────────────────────────────────────────────┘         │
│    │   L9-L11    │         (Post-mortem review)                            │
│    │ Design/Test │                                                         │
│    └──────┬──────┘                                                         │
│           │                                                                 │
│           ▼                                                                 │
│    ┌─────────────┐                                                         │
│    │   GATE-12   │                                                         │
│    │   L12-L14   │                                                         │
│    │Implementation│                                                         │
│    └──────────────┘                                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Gate Definitions

| Gate | Position | Layers | Purpose |
|------|----------|--------|---------|
| **GATE-01** | Before L1-L4 | BRD, PRD, EARS, BDD | Validate business/product changes |
| **GATE-05** | Before L5-L8 | ADR, SYS, REQ, CTR | Validate architecture/contract changes |
| **GATE-09** | Before L9-L11 | SPEC, TSPEC, TASKS | Validate design/test changes (TDD) |
| **GATE-12** | Before L12-L14 | Code, Tests, Validation | Validate implementation changes |

### 4.3 Routing by Change Source

| Source | Entry Gate | Cascade Path |
|--------|------------|--------------|
| Upstream | GATE-01 | 01 → 05 → 09 → 12 |
| Midstream | GATE-05 | 05 → 09 → 12 (may bubble up to 01) |
| Design | GATE-09 | 09 → 12 |
| Downstream | GATE-12 | 12 only (may bubble up based on RCA) |
| External | GATE-05 | 05 → 09 → 12 (or EMERGENCY) |
| Feedback | GATE-12 | 12 (or EMERGENCY for P1) |

### 4.4 Approval Matrix

| Change Level | GATE-01 | GATE-05 | GATE-09 | GATE-12 |
|--------------|---------|---------|---------|---------|
| **L1** | Self | Self | Self | Self |
| **L2** | PO + TL | TL + Domain | TL | TL + QA |
| **L3** | PO + Arch + Stakeholder | Arch + Security | TL + Domain | TL + Arch |

### 4.5 Validation Scripts

```bash
# Validate individual gates
./CHG/scripts/validate_gate01.sh <CHG_FILE>
./CHG/scripts/validate_gate05.sh <CHG_FILE>
./CHG/scripts/validate_gate09.sh <CHG_FILE>
./CHG/scripts/validate_gate12.sh <CHG_FILE>

# Validate all applicable gates
./CHG/scripts/validate_all_gates.sh <CHG_FILE>

# Determine routing
python CHG/scripts/validate_chg_routing.py <CHG_FILE>
```

### 4.6 Emergency Bypass

For P1 incidents or critical security (CVSS >= 9.0):

1. **Triage** (0-30 min): Declare emergency, authorize bypass, create stub
2. **Hotfix** (30 min - 4h): Implement fix, minimal test, deploy
3. **Post-Incident** (24-72h): Complete CHG, post-mortem, retroactive gates

**Gate Documentation**: See `gates/` directory for complete gate specifications.

---

## 5. Core Principles

### 5.1 Immutable History (CRITICAL)

> **NEVER edit an approved artifact for a major change.**
> **ALWAYS archive the old and create a new artifact.**

| Level | Immutability Rule |
|-------|-------------------|
| L1 | Edit in place, increment patch version |
| L2 | Version or create new, document change |
| L3 | MUST archive old, MUST create new ID |

### 5.2 Formal Audit Trail

Every L2+ change must be tracked via a CHG artifact.

### 5.3 Complete Traceability

Migration is not complete until all links are repaired across all 15 layers.

### 5.4 TDD Integration

Changes affecting L9+ MUST include TSPEC updates to maintain test-first workflow.

## 6. The 15-Layer Impact Model

### 6.1 Layer Reference

| Layer | Artifact | Purpose |
|-------|----------|---------|
| 0 | Strategy | External business context |
| 1 | BRD | Business requirements |
| 2 | PRD | Product requirements |
| 3 | EARS | Formal requirements syntax |
| 4 | BDD | Behavior tests |
| 5 | ADR | Architecture decisions |
| 6 | SYS | System requirements |
| 7 | REQ | Atomic requirements |
| 8 | CTR | API contracts |
| 9 | SPEC | Technical specifications |
| **10** | **TSPEC** | **Test specifications (TDD)** |
| 11 | TASKS | Implementation tasks |
| 12 | Code | Source code |
| 13 | Tests | Test implementations |
| 14 | Validation | Production readiness |

### 6.2 Cascade Rules

```text
Change at Layer N typically requires regeneration of Layers N+1 through 14

Example: BRD change (L1)
├── Cascades to: PRD (L2)
├── Cascades to: EARS (L3)
├── Cascades to: BDD (L4)
├── Cascades to: ADR (L5) - if architecture affected
├── Cascades to: SYS (L6)
├── Cascades to: REQ (L7)
├── Cascades to: CTR (L8) - if interface affected
├── Cascades to: SPEC (L9)
├── Cascades to: TSPEC (L10) ← NEW: Test specs must be updated
├── Cascades to: TASKS (L11)
├── Cascades to: Code (L12)
├── Cascades to: Tests (L13)
└── Cascades to: Validation (L14)
```

## 7. Workflows by Level

### 7.1 L1 Patch Workflow

```text
┌─────────────────────────────────────────────┐
│            L1 PATCH WORKFLOW                │
├─────────────────────────────────────────────┤
│                                             │
│  1. Identify bug/issue                      │
│         │                                   │
│         ▼                                   │
│  2. Fix in place                            │
│     - Edit artifact directly                │
│     - Increment patch version (1.0.0→1.0.1) │
│         │                                   │
│         ▼                                   │
│  3. Validate                                │
│     - Run affected tests                    │
│         │                                   │
│         ▼                                   │
│  4. Commit with message                     │
│     "fix: [brief description]"              │
│                                             │
└─────────────────────────────────────────────┘
```

**No CHG document required.**

### 7.2 L2 Minor Workflow

```text
┌─────────────────────────────────────────────┐
│           L2 MINOR WORKFLOW                 │
├─────────────────────────────────────────────┤
│                                             │
│  1. Create CHG directory                    │
│     docs/CHG/CHG-XX_{slug}/                 │
│         │                                   │
│         ▼                                   │
│  2. Document change (CHG-MVP-TEMPLATE)      │
│     - Change summary                        │
│     - Affected layers                       │
│     - Impact assessment                     │
│         │                                   │
│         ▼                                   │
│  3. Update affected artifacts               │
│     - Version increment or new artifact     │
│     - Update TSPEC if L9+ affected         │
│         │                                   │
│         ▼                                   │
│  4. Repair traceability                     │
│     - Update cross-references               │
│         │                                   │
│         ▼                                   │
│  5. Validate & Close                        │
│     - Run tests                             │
│     - Update CHG status to Completed        │
│                                             │
└─────────────────────────────────────────────┘
```

**Use `CHG-MVP-TEMPLATE.md`**

### 7.3 L3 Major Workflow

```text
┌─────────────────────────────────────────────┐
│           L3 MAJOR WORKFLOW                 │
├─────────────────────────────────────────────┤
│                                             │
│  STEP 1: INITIALIZE                         │
│  ─────────────────                          │
│  - Create CHG directory with archive/       │
│  - Create CHG document (CHG-TEMPLATE)       │
│  - Create implementation_plan.md            │
│         │                                   │
│         ▼                                   │
│  STEP 2: ARCHIVE & DEPRECATE                │
│  ───────────────────────────                │
│  - Move obsolete artifacts to archive/      │
│  - Add deprecation notices to each          │
│         │                                   │
│         ▼                                   │
│  STEP 3: SUPERSEDE                          │
│  ─────────────────                          │
│  - Create new artifacts in standard paths   │
│  - Update "Supersedes" metadata             │
│         │                                   │
│         ▼                                   │
│  STEP 4: REPAIR TRACEABILITY                │
│  ──────────────────────────                 │
│  - Update all downstream references         │
│  - Verify no orphaned links                 │
│         │                                   │
│         ▼                                   │
│  STEP 5: EXECUTE                            │
│  ───────────────                            │
│  - Implement new TASKS                      │
│  - Run TSPEC tests                          │
│  - Validate all layers                      │
│         │                                   │
│         ▼                                   │
│  STEP 6: CLOSE                              │
│  ──────────                                 │
│  - Update CHG status to Completed           │
│  - Document lessons learned                 │
│                                             │
└─────────────────────────────────────────────┘
```

**Use `CHG-TEMPLATE.md`**

## 8. File Organization

### 8.1 CHG Directory Structure

```text
docs/CHG/
├── CHANGE_MANAGEMENT_GUIDE.md      # This file
├── CHANGE_CLASSIFICATION_GUIDE.md  # L1/L2/L3 decision guide
├── CHG-TEMPLATE.md                 # L3 Major template
├── CHG-MVP-TEMPLATE.md             # L2 Minor template
├── CHG_MVP_CREATION_RULES.md       # Creation rules
├── CHG_MVP_SCHEMA.yaml             # Validation schema
│
├── sources/                        # Change source guides
│   ├── UPSTREAM_CHANGE_GUIDE.md
│   ├── MIDSTREAM_CHANGE_GUIDE.md
│   ├── DOWNSTREAM_CHANGE_GUIDE.md
│   ├── EXTERNAL_CHANGE_GUIDE.md
│   └── FEEDBACK_CHANGE_GUIDE.md
│
├── scripts/                        # Validation scripts
│   ├── validate_chg_routing.py     # CHG routing validation
│   ├── validate_gate01.sh          # GATE-01 validation
│   ├── validate_gate05.sh          # GATE-05 validation
│   ├── validate_gate09.sh          # GATE-09 validation
│   ├── validate_gate12.sh          # GATE-12 validation
│   ├── validate_all_gates.sh       # All gates validation
│   └── validate_emergency_bypass.sh # Emergency bypass validation
│
└── CHG-XX_{slug}/                  # Individual CHG records
    ├── CHG-XX_{slug}.md
    ├── implementation_plan.md
    └── archive/                    # L3 only
        └── [archived artifacts]
```

## 9. Integration with TDD Workflow

### 9.1 TSPEC in Change Management

The TSPEC layer (L10) plays a critical role in change management:

```text
Change → SPEC update → TSPEC update → TASKS update → Code → Tests
                           │
                           └── Test specifications MUST be
                               updated BEFORE code changes
                               (Test-Driven Development)
```

### 9.2 Defect Root Cause Analysis

When tests fail, trace to the source:

| Failure Type | Root Cause Layer | Fix Approach |
|--------------|------------------|--------------|
| Unit test fails | Code (L12) | L1: Fix code |
| TSPEC mismatch | TSPEC (L10) | L1: Fix test spec |
| Integration fails | CTR/SPEC (L8-L9) | L2: Update contract/spec |
| Acceptance fails | BDD/REQ (L4-L7) | L2-L3: Update requirements |

## 10. Quality Gates

### 10.1 Change Completion Criteria

| Criterion | L1 | L2 | L3 |
|-----------|----|----|----|
| CHG document created | ○ | ● | ● |
| Impact analysis complete | ○ | ● | ● |
| Artifacts archived | ○ | ○ | ● |
| New artifacts validated | ● | ● | ● |
| TSPEC tests pass | ● | ● | ● |
| Traceability verified | ○ | ● | ● |
| Status set to Completed | ○ | ● | ● |

**Legend**: ○ Not required | ● Required

### 10.2 Validation Commands

```bash
# Validate CHG routing and structure
python CHG/scripts/validate_chg_routing.py docs/CHG/CHG-XX/CHG-XX.md

# Validate all gates
./CHG/scripts/validate_all_gates.sh docs/CHG/CHG-XX/CHG-XX.md

# Check traceability
python ai_dev_flow/scripts/validate_traceability_matrix.py

# Verify no broken references
python ai_dev_flow/scripts/validate_forward_references.py

# Run pytest tests
pytest tests/
```

## 11. Quick Reference

### 11.1 Level Selection Cheat Sheet

| If your change... | Use Level |
|-------------------|-----------|
| Fixes a bug without changing contracts | L1 |
| Adds a feature without breaking existing | L2 |
| Changes architecture or breaks compatibility | L3 |
| Updates a dependency with minor API changes | L2 |
| Responds to a critical security vulnerability | L1-L3 (based on scope) |
| Refactors code without changing behavior | L1 |

### 11.2 Source Selection Cheat Sheet

| If change originates from... | Source |
|------------------------------|--------|
| Business/stakeholder request | Upstream |
| Architecture/design decision | Midstream |
| Test failure or bug report | Downstream |
| Security patch or dependency update | External |
| Production incident or user feedback | Feedback |

---

## 12. Glossary

| Acronym | Full Name | Description |
|---------|-----------|-------------|
| **ADR** | Architecture Decision Record | Layer 5 artifact documenting architecture decisions |
| **BDD** | Behavior-Driven Development | Layer 4 artifact with Given-When-Then scenarios |
| **BRD** | Business Requirements Document | Layer 1 artifact defining business needs |
| **CHG** | Change Management | Change management procedure and artifact |
| **CTR** | Contract | Layer 8 artifact defining API contracts |
| **CVE** | Common Vulnerabilities and Exposures | Standard identifier for security vulnerabilities |
| **CVSS** | Common Vulnerability Scoring System | Scoring system for security vulnerability severity (0.0-10.0) |
| **EARS** | Easy Approach to Requirements Syntax | Layer 3 artifact using WHEN-THE-SHALL-WITHIN format |
| **EOL** | End of Life | Sunset date for deprecated software or services |
| **IC** | Incident Commander | Role responsible for coordinating emergency response |
| **PO** | Product Owner | Role responsible for product requirements and prioritization |
| **PRD** | Product Requirements Document | Layer 2 artifact defining product features |
| **QA** | Quality Assurance | Role or process ensuring quality standards |
| **RCA** | Root Cause Analysis | Process to identify the underlying cause of issues |
| **REQ** | Atomic Requirement | Layer 7 artifact with granular testable requirements |
| **SDD** | Specification-Driven Development | Development methodology using layered documentation |
| **SPEC** | Technical Specification | Layer 9 artifact with implementation details |
| **SYS** | System Requirements | Layer 6 artifact defining system-level requirements |
| **TASKS** | Task Breakdown | Layer 11 artifact with implementation tasks |
| **TDD** | Test-Driven Development | Development practice writing tests before code |
| **TL** | Technical Lead | Role responsible for technical decisions and code quality |
| **TSPEC** | Test Specification | Layer 10 artifact with test specifications |

---

**Related Documents**:
- [CHANGE_CLASSIFICATION_GUIDE.md](./CHANGE_CLASSIFICATION_GUIDE.md)
- [CHG-TEMPLATE.md](./CHG-TEMPLATE.md)
- [CHG-MVP-TEMPLATE.md](./CHG-MVP-TEMPLATE.md)
- [CHG_MVP_CREATION_RULES.md](./CHG_MVP_CREATION_RULES.md)
