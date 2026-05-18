# 4-Gate CHG System Implementation Plan

**Created**: 2026-02-05
**Status**: Pending Approval
**Scope**: Comprehensive 4-gate change management system for 15-layer SDD framework

## Overview

Implement a formal 4-Gate Change Management System for the 15-layer SDD framework with:
- 4 mandatory gates at layer boundaries
- 5 change source workflows
- Emergency bypass with post-incident documentation
- Validation scripts following REQ GATE patterns

## Gate Structure

| Gate | Position | Layers | Change Sources | Purpose |
|------|----------|--------|----------------|---------|
| **GATE-01** | Before L1-L4 | BRD, PRD, EARS, BDD | Upstream | Business/Product changes |
| **GATE-05** | Before L5-L8 | ADR, SYS, REQ, CTR | Midstream, External | Architecture/Contract changes |
| **GATE-09** | Before L9-L11 | SPEC, TSPEC, TASKS | Design optimization | Design/Test changes |
| **GATE-12** | Before L12-L14 | Code, Tests, Validation | Downstream, Feedback | Implementation/Defect fixes |

## Gate Flow Diagram

```
                    ┌─────────────────────────────────────────────────────────┐
                    │                    CHANGE REQUEST                        │
                    └──────────────────────────┬──────────────────────────────┘
                                               │
                                               ▼
                    ┌─────────────────────────────────────────────────────────┐
                    │              ROUTING DETERMINATION                       │
                    │        (validate_chg_routing.py)                        │
                    │  Analyzes: source, scope, breaking changes, layers      │
                    └──────────────────────────┬──────────────────────────────┘
                                               │
          ┌────────────────┬──────────────────┼────────────────┬──────────────┐
          │                │                  │                │              │
          ▼                ▼                  ▼                ▼              ▼
    ┌──────────┐    ┌──────────┐      ┌──────────┐      ┌──────────┐  ┌──────────┐
    │ GATE-01  │    │ GATE-05  │      │ GATE-09  │      │ GATE-12  │  │ EMERGENCY│
    │ L1-L4    │    │ L5-L8    │      │ L9-L11   │      │ L12-L14  │  │ BYPASS   │
    │ Business │    │ Arch/Ctr │      │ Design   │      │ Impl     │  │ P1/Sec   │
    └────┬─────┘    └────┬─────┘      └────┬─────┘      └────┬─────┘  └────┬─────┘
         │               │                 │                 │              │
         ▼               ▼                 ▼                 ▼              ▼
    ┌──────────┐    ┌──────────┐      ┌──────────┐      ┌──────────┐  ┌──────────┐
    │ CASCADE  │    │ CASCADE  │      │ CASCADE  │      │ FIX +    │  │ HOTFIX   │
    │ L1→L14   │    │ L5→L14   │      │ L9→L14   │      │ VALIDATE │  │ + POST   │
    │          │    │          │      │          │      │          │  │ MORTEM   │
    └──────────┘    └──────────┘      └──────────┘      └──────────┘  └──────────┘
```

## Files to Create

### Phase 1: Gate Documents (6 files)

```
CHG/gates/
├── GATE-01_BUSINESS_PRODUCT.md      # L1-L4 gate
├── GATE-05_ARCHITECTURE_CONTRACT.md # L5-L8 gate
├── GATE-09_DESIGN_TEST.md           # L9-L11 gate
├── GATE-12_IMPLEMENTATION.md        # L12-L14 gate
├── GATE_INTERACTION_DIAGRAM.md      # Gate flow visualization
└── GATE_ERROR_CATALOG.md            # All error codes
```

### Phase 2: Workflow Documents (5 files)

```
CHG/workflows/
├── UPSTREAM_WORKFLOW.md      # Gate-01 entry
├── MIDSTREAM_WORKFLOW.md     # Gate-05 entry
├── DESIGN_WORKFLOW.md        # Gate-09 entry
├── DOWNSTREAM_WORKFLOW.md    # Gate-12 entry
└── EMERGENCY_WORKFLOW.md     # P1/Security bypass
```

### Phase 3: Templates (3 files)

```
CHG/templates/
├── CHG-EMERGENCY-TEMPLATE.md  # Emergency stub
├── POST_MORTEM-TEMPLATE.md    # Post-incident
└── GATE_APPROVAL_FORM.md      # Gate sign-off
```

### Phase 4: Validation Scripts (7 files)

```
CHG/scripts/
├── validate_gate01.sh         # GATE-01 validation
├── validate_gate05.sh         # GATE-05 validation
├── validate_gate09.sh         # GATE-09 validation
├── validate_gate12.sh         # GATE-12 validation
├── validate_chg_routing.py    # Gate routing logic
├── validate_emergency_bypass.sh
└── validate_all_gates.sh      # Orchestrator
```

### Phase 5: Update Existing Files (9 files)

- `CHG/CHG_MVP_SCHEMA.yaml` - Add gate schema section
- `CHG/CHG-TEMPLATE.md` - Add gate information section
- `CHG/CHG-MVP-TEMPLATE.md` - Add gate reference
- `CHG/CHANGE_MANAGEMENT_GUIDE.md` - Add gate system section
- `CHG/sources/UPSTREAM_CHANGE_GUIDE.md` - Add gate entry references
- `CHG/sources/MIDSTREAM_CHANGE_GUIDE.md` - Add gate entry references
- `CHG/sources/DOWNSTREAM_CHANGE_GUIDE.md` - Add gate entry references
- `CHG/sources/EXTERNAL_CHANGE_GUIDE.md` - Add gate entry references
- `CHG/sources/FEEDBACK_CHANGE_GUIDE.md` - Add gate entry references

## Gate Document Structure

Each gate document includes:

1. **Purpose & Scope** - What the gate validates
2. **Entry Criteria** - Prerequisites to enter gate
3. **Validation Checklist** - Error/warning checks with codes
4. **Approval Workflow** - Who approves at each level
5. **Exit Criteria** - Conditions to pass gate
6. **Routing Rules** - Where to go next
7. **Error Catalog** - Gate-specific error codes

## Gate Validation Checks

### GATE-01: Business/Product (L1-L4)

| Check ID | Description | Severity |
|----------|-------------|----------|
| GATE-01-E001 | BRD change must have business justification | ERROR |
| GATE-01-E002 | PRD change must link to BRD objective | ERROR |
| GATE-01-E003 | EARS must follow WHEN-THE-SHALL syntax | ERROR |
| GATE-01-E004 | BDD must have Given-When-Then format | ERROR |
| GATE-01-W001 | Large scope (>5 layers) without L3 | WARNING |
| GATE-01-W002 | Missing stakeholder approval for L3 | WARNING |

### GATE-05: Architecture/Contract (L5-L8)

| Check ID | Description | Severity |
|----------|-------------|----------|
| GATE-05-E001 | ADR must document context, decision, consequences | ERROR |
| GATE-05-E002 | SYS quality attributes must be measurable | ERROR |
| GATE-05-E003 | REQ must have 6 upstream traceability tags | ERROR |
| GATE-05-E004 | CTR schema must validate (YAML + MD sync) | ERROR |
| GATE-05-E005 | Breaking API change without L3 classification | ERROR |
| GATE-05-W001 | External security change without CVE reference | WARNING |

### GATE-09: Design/Test (L9-L11)

| Check ID | Description | Severity |
|----------|-------------|----------|
| GATE-09-E001 | SPEC must have implementation readiness score >= 90% | ERROR |
| GATE-09-E002 | TSPEC must cover all SPEC interfaces | ERROR |
| GATE-09-E003 | TASKS must link to SPEC and TSPEC | ERROR |
| GATE-09-W001 | Algorithm change without performance baseline | WARNING |
| GATE-09-W002 | TSPEC missing edge case coverage | WARNING |

### GATE-12: Implementation (L12-L14)

| Check ID | Description | Severity |
|----------|-------------|----------|
| GATE-12-E001 | Root cause analysis completed | ERROR |
| GATE-12-E002 | Fix at correct layer (not symptom masking) | ERROR |
| GATE-12-E003 | Regression tests included | ERROR |
| GATE-12-W001 | Code fix without corresponding TSPEC update | WARNING |
| GATE-12-W002 | Large code change as L1 | WARNING |

## Approval Matrix

| Change Level | GATE-01 | GATE-05 | GATE-09 | GATE-12 |
|--------------|---------|---------|---------|---------|
| **L1** | Self | Self | Self | Self |
| **L2** | PO + TL | TL + Domain | TL | TL + QA |
| **L3** | PO + Arch + Stakeholder | Arch + Security | TL + Domain | TL + Arch |

Legend: PO=Product Owner, TL=Technical Lead, Arch=Architecture Board, QA=QA Lead

## Validation Script Pattern

Following REQ GATE pattern from `07_REQ/scripts/validate_req_quality_score.sh`:

```bash
#!/bin/bash
# Exit codes:
# 0 = Pass (no errors, no warnings)
# 1 = Pass with warnings (non-blocking)
# 2 = Fail (blocking errors)

# Error code format: GATE-NN-SNNN
# NN = gate number (01, 05, 09, 12)
# S = severity (E=error, W=warning, I=info)
# NNN = sequential number

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Counters
ERRORS=0
WARNINGS=0
```

## Emergency Bypass Process

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      EMERGENCY BYPASS WORKFLOW                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  PHASE 1: TRIAGE (0-30 minutes)                                         │
│  ────────────────────────────────                                        │
│  1. Incident declared (P1/Security CVSS ≥ 9.0)                          │
│  2. On-call engineer assesses severity                                  │
│  3. Emergency bypass authorized by incident commander                   │
│  4. Minimal CHG stub created: CHG-EMG-{timestamp}                       │
│                                                                          │
│  PHASE 2: HOTFIX (30 min - 4 hours)                                     │
│  ─────────────────────────────────                                       │
│  1. Implement hotfix directly (bypass gates)                            │
│  2. Minimal testing (smoke test only)                                   │
│  3. Deploy to production                                                │
│  4. Monitor for resolution                                              │
│                                                                          │
│  PHASE 3: POST-INCIDENT DOCUMENTATION (24-72 hours)                     │
│  ──────────────────────────────────────────────────                      │
│  1. Complete CHG document with full details                             │
│  2. Conduct post-mortem                                                 │
│  3. Retroactively pass all applicable gates                             │
│  4. Create follow-up CHGs for preventive measures                       │
│  5. Close emergency CHG                                                 │
│                                                                          │
│  REQUIRED ARTIFACTS:                                                     │
│  • CHG-EMG-{timestamp}.md (emergency stub)                              │
│  • POST_MORTEM-{CHG-ID}.md (within 72 hours)                            │
│  • Follow-up CHG documents (preventive measures)                        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Implementation Order

| # | Task | Files | Dependencies |
|---|------|-------|--------------|
| 1 | Create gates/ directory and GATE-01 | 1 file | None |
| 2 | Create GATE-05, GATE-09, GATE-12 | 3 files | Task 1 |
| 3 | Create GATE_INTERACTION_DIAGRAM.md | 1 file | Task 2 |
| 4 | Create GATE_ERROR_CATALOG.md | 1 file | Task 2 |
| 5 | Create workflows/ directory and files | 5 files | Task 2 |
| 6 | Create templates/ directory and files | 3 files | Task 5 |
| 7 | Create validation scripts | 7 files | Task 4 |
| 8 | Update CHG_MVP_SCHEMA.yaml | 1 file | Task 7 |
| 9 | Update CHG templates | 2 files | Task 8 |
| 10 | Update CHANGE_MANAGEMENT_GUIDE.md | 1 file | Task 9 |
| 11 | Update source guides (5 files) | 5 files | Task 10 |

**Total: 30 files (21 new, 9 updates)**

## Critical Files to Modify

| File | Changes |
|------|---------|
| `CHG/CHG_MVP_SCHEMA.yaml` | Add `gate_system` section with 4 gates + emergency bypass |
| `CHG/CHG-TEMPLATE.md` | Add "Gate Information" section with entry gate, status, validation results |
| `CHG/CHG-MVP-TEMPLATE.md` | Add gate reference field |
| `CHG/CHANGE_MANAGEMENT_GUIDE.md` | Add "4-Gate System" section with flow diagram |
| `CHG/sources/*.md` | Add "Gate Entry Point" section to each source guide |

## Verification Checklist

After implementation:

1. **Structure Validation**
   ```bash
   ls -la CHG/gates/
   ls -la CHG/workflows/
   ls -la CHG/templates/
   ls -la CHG/scripts/
   ```

2. **Script Execution Test**
   ```bash
   bash CHG/scripts/validate_all_gates.sh --help
   python CHG/scripts/validate_chg_routing.py --help
   ```

3. **Schema Validation**
   - Verify YAML syntax in CHG_MVP_SCHEMA.yaml
   - Verify gate definitions are complete

4. **Cross-Reference Check**
   - All gate documents reference correct layers
   - All workflows reference correct gates
   - All source guides have gate entry sections

## Related Documents

- `/opt/data/ucx_framework/ai_dev_flow/07_REQ/scripts/validate_req_quality_score.sh` - Reference pattern for validation scripts
- `/opt/data/ucx_framework/ai_dev_flow/CHG/CHANGE_MANAGEMENT_GUIDE.md` - Main guide to update
- `/opt/data/ucx_framework/ai_dev_flow/CHG/CHG_MVP_SCHEMA.yaml` - Schema to extend
