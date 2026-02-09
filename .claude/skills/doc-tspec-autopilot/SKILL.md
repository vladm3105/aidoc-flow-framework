---
name: doc-tspec-autopilot
description: Automated TSPEC generation from SPEC - generates test specifications for UTEST, ITEST, STEST, FTEST with TASKS-Ready scoring
tags:
  - sdd-workflow
  - layer-10-artifact
  - automation-workflow
  - shared-architecture
custom_fields:
  layer: 10
  artifact_type: TSPEC
  architecture_approaches: [ai-agent-based]
  priority: primary
  development_status: active
  skill_category: automation-workflow
  upstream_artifacts: [BRD, PRD, EARS, BDD, ADR, SYS, REQ, CTR, SPEC]
  downstream_artifacts: [TASKS]
  version: "1.0"
  last_updated: "2026-02-08"
---

# doc-tspec-autopilot

## Purpose

Automated **Test Specifications (TSPEC)** generation pipeline that processes SPEC documents to generate comprehensive test specifications for UTEST, ITEST, STEST, and FTEST with TASKS-Ready scoring.

**Layer**: 10

**Upstream**: SPEC (Layer 9)

**Downstream**: TASKS (Layer 11)

---

## Skill Dependencies

| Skill | Purpose | Phase |
|-------|---------|-------|
| `doc-naming` | Element ID format (TSPEC.NN.TT.SS, codes 40-43) | All Phases |
| `doc-spec-validator` | Validate SPEC TASKS-Ready score | Phase 2 |
| `doc-tspec` | TSPEC creation rules, test type structure | Phase 3 |
| `quality-advisor` | Real-time quality feedback | Phase 3 |
| `doc-tspec-validator` | Validation with TASKS-Ready scoring | Phase 4 |

---

## Workflow Overview

```mermaid
flowchart TD
    subgraph Phase1["Phase 1: SPEC Analysis"]
        A[Start] --> B[Read SPEC Documents]
        B --> C[Extract Methods]
        C --> D[Extract Interfaces]
        D --> E[Extract Data Models]
        E --> F[Catalog Test Targets]
    end

    subgraph Phase2["Phase 2: Test Coverage Planning"]
        F --> G[Check SPEC TASKS-Ready Score]
        G --> H{Score >= 90%?}
        H -->|No| I[Flag SPEC Issues]
        I --> J{Auto-Fixable?}
        J -->|Yes| K[Fix SPEC Issues]
        K --> G
        J -->|No| L[Abort - Manual Fix Required]
        H -->|Yes| M[Plan Test Coverage]
        M --> N[Allocate Test Types]
    end

    subgraph Phase3["Phase 3: TSPEC Generation"]
        N --> O[Generate UTEST Specs]
        O --> P[Generate ITEST Specs]
        P --> Q[Generate STEST Specs]
        Q --> R[Generate FTEST Specs]
        R --> S[quality-advisor: Real-time Feedback]
        S --> T[Build Coverage Matrix]
        T --> U[Add Traceability Tags]
        U --> V[Write TSPEC Files]
    end

    subgraph Phase4["Phase 4: TSPEC Validation"]
        V --> W[Run doc-tspec-validator]
        W --> X{TASKS-Ready >= 90%?}
        X -->|No| Y[Auto-Fix TSPEC Issues]
        Y --> Z[Re-validate TSPEC]
        Z --> X
        X -->|Yes| AA[Mark TSPEC Validated]
    end

    subgraph Phase5["Phase 5: Final Review"]
        AA --> AB[Verify Coverage Matrix]
        AB --> AC[Check All Types Present]
        AC --> AD[Update Traceability Matrix]
        AD --> AE[Generate Summary Report]
    end

    AE --> AF[Complete]
    L --> AG[Exit with Error]
```

---

## Test Types

| Type | Code | Purpose | Target |
|------|------|---------|--------|
| **UTEST** | 40 | Unit tests | Individual functions/methods |
| **ITEST** | 41 | Integration tests | Component interactions |
| **STEST** | 42 | Smoke tests | Critical path verification |
| **FTEST** | 43 | Functional tests | End-to-end workflows |

---

## TSPEC Structure

```
docs/10_TSPEC/
├── TSPEC-01_authentication/
│   ├── TSPEC-01.0_index.md
│   ├── TSPEC-01.1_utest.md      # Unit tests
│   ├── TSPEC-01.2_itest.md      # Integration tests
│   ├── TSPEC-01.3_stest.md      # Smoke tests
│   └── TSPEC-01.4_ftest.md      # Functional tests
└── TSPEC-01_authentication.md    # Redirect stub
```

---

## Coverage Matrix Format

| SPEC Element | UTEST | ITEST | STEST | FTEST | Coverage |
|--------------|-------|-------|-------|-------|----------|
| SPEC.01.28.01 | TSPEC.01.40.01 | TSPEC.01.41.01 | TSPEC.01.42.01 | - | 75% |
| SPEC.01.28.02 | TSPEC.01.40.02 | TSPEC.01.41.02 | - | TSPEC.01.43.01 | 75% |

---

## Element ID Format

| Test Type | Code | Pattern | Example |
|-----------|------|---------|---------|
| UTEST | 40 | TSPEC.NN.40.SS | TSPEC.01.40.01 |
| ITEST | 41 | TSPEC.NN.41.SS | TSPEC.01.41.01 |
| STEST | 42 | TSPEC.NN.42.SS | TSPEC.01.42.01 |
| FTEST | 43 | TSPEC.NN.43.SS | TSPEC.01.43.01 |

---

## Cumulative Tags (8 Required)

```markdown
@brd: BRD.NN.TT.SS
@prd: PRD.NN.TT.SS
@ears: EARS.NN.TT.SS
@bdd: BDD.NN.TT.SS
@adr: ADR-NN
@sys: SYS.NN.TT.SS
@req: REQ.NN.TT.SS
@spec: SPEC.NN.TT.SS
@ctr: CTR.NN.TT.SS  # Optional
```

---

## Related Resources

- **TSPEC Skill**: `.claude/skills/doc-tspec/SKILL.md`
- **TSPEC Validator**: `.claude/skills/doc-tspec-validator/SKILL.md`
- **Naming Standards**: `.claude/skills/doc-naming/SKILL.md`
- **Quality Advisor**: `.claude/skills/quality-advisor/SKILL.md`
- **TSPEC Template**: `ai_dev_flow/10_TSPEC/TSPEC-TEMPLATE.md`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-08 | Initial skill creation with 5-phase workflow; Integrated doc-naming, doc-tspec, quality-advisor, doc-tspec-validator; Support for all 4 test types |
