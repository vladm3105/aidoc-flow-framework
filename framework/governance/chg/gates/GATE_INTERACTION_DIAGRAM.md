---
title: "Gate Interaction Diagram"
tags:
  - change-management
  - gate-system
  - visualization
  - shared-architecture
custom_fields:
  document_type: reference
  artifact_type: CHG
---

# Gate Interaction Diagram

Visual representation of the 5-Gate Change Management System across the 8-layer SDD workflow.

## 1. System Overview

```
                         5-GATE CHANGE MANAGEMENT SYSTEM
                           8-Layer SDD Framework

    CHANGE REQUEST

                        ROUTING DETERMINATION
         Analyzes: source, scope, layer, change level (C1/C2/C3)


     GATE-01       GATE-03       GATE-06       GATE-08       EMERGENCY
     L1-L2         L3-L5         L6-L7         L8            BYPASS
     Business      Reqs/Arch     Design/Test   IPLAN         P1/Security


       GATE-CODE
       Code

      DEPLOYED
```

### 1.1 GATE-SPEC — the meta gate (orthogonal)

GATE-SPEC sits *beside* the cascade above, not inside it. The artifact gates
govern a project's artifact instances; GATE-SPEC governs the **`framework/` spec
that defines the layers**. It has no cascade successor — instead, a passed spec
change obliges every platform to re-declare `FRAMEWORK_SPEC_VERSION` and re-pass
the shared conformance suite.

```
   CHANGE TO framework/ (templates · governance · registry · VERSION)
                              │
                          GATE-SPEC  (meta — see GATE-SPEC_FRAMEWORK.md)
                              │
                           PASSED
                              │
        both platforms re-declare FRAMEWORK_SPEC_VERSION
              and re-pass the shared conformance suite
```

## 2. Gate-to-Layer Mapping

```
                          GATE-TO-LAYER MAPPING

   GATE-01      GATE-03        GATE-06       GATE-08       GATE-CODE

    L1  BRD     L3  EARS       L6  SPEC      L8  IPLAN      Code
    L2  PRD     L4  BDD        L7  TDD
                L5  ADR

   Business/    Requirements/   Design/Test   Execution     Implementation
   Product      Architecture
```

## 3. Change Source Routing

```
                         CHANGE SOURCE ROUTING

   UPSTREAM (Business/Product)

    Market feedback
    Stakeholder req    GATE-01  GATE-03  GATE-06  GATE-08  GATE-CODE
    Regulatory change  (L1-L2)  (L3-L5)  (L6-L7)  (L8)     (Code)

   MIDSTREAM (Requirements/Architecture)

    Requirement change
    BDD scenario add    GATE-03  GATE-06  GATE-08  GATE-CODE
    ADR architecture    (L3-L5)  (L6-L7)  (L8)     (Code)

   DESIGN (Specification/Test)

    SPEC interface
    TDD test cases      GATE-06  GATE-08  GATE-CODE
                        (L6-L7)  (L8)     (Code)

   EXECUTION (IPLAN)

    IPLAN file manifest
    Session handoff     GATE-08  GATE-CODE
    Command sequence    (L8)     (Code)

   DOWNSTREAM / FEEDBACK (Defects)

    Bug reports
    Test failures       GATE-CODE
    Code issues         (Code)
                                    (if root cause upstream)
                                    Bubble up to GATE-08/06/03/01

   EXTERNAL (Environment)

    Security CVE        Critical?  EMERGENCY BYPASS
    Dependency update
    Third-party API     Standard  GATE-03  GATE-06  GATE-08  GATE-CODE

   FEEDBACK (Production)

    P1 incident         P1?  EMERGENCY BYPASS
    User feedback
    Performance issue   P2-P4  GATE-CODE (with RCA)
```

## 4. Cascade Flow Patterns

### 4.1 Full Cascade (L1 to Code)

```
UPSTREAM Change (new business requirement)

 GATE-01  GATE-03  GATE-06  GATE-08  GATE-CODE
  L1-L2     L3-L5     L6-L7     L8       Code
 passed    passed    passed    passed    passed

  Update:   Update:    Update:   Update:   Update:
  BRD, PRD  EARS, BDD  SPEC      IPLAN     Source
            ADR        TDD                 Code
```

### 4.2 Midstream Entry (L3 to Code)

```
MIDSTREAM Change (requirements/architecture change)

 GATE-03  GATE-06  GATE-08  GATE-CODE
  L3-L5     L6-L7     L8       Code
 passed    passed    passed    passed

  Update:   Update:   Update:   Update:
  EARS, BDD SPEC      IPLAN     Source
  ADR       TDD                 Code
```

### 4.3 Design Entry (L6 to Code)

```
DESIGN Change (SPEC/TDD change)

 GATE-06  GATE-08  GATE-CODE
  L6-L7     L8       Code
 passed    passed    passed

  Update:   Update:   Update:
  SPEC      IPLAN     Source
  TDD                 Code
```

### 4.4 Execution Entry (L8 to Code)

```
EXECUTION Change (IPLAN change)

 GATE-08   GATE-CODE
  L8        Code
 passed     passed

  Update:   Update:
  IPLAN     Source
            Code
```

## 5. Emergency Bypass Flow

```
                          EMERGENCY BYPASS FLOW

   PHASE 1: TRIAGE (0-30 min)

    1. Incident declared (P1 or Security CVSS >= 9.0)
    2. On-call engineer assesses severity
    3. Incident commander authorizes bypass
    4. Create CHG-EMG-{timestamp}.yaml (minimal stub)

   PHASE 2: HOTFIX (30 min - 4 hours)

    1. Implement hotfix (bypass gates)
    2. Minimal smoke testing
    3. Deploy to production
    4. Monitor for resolution

   PHASE 3: POST-INCIDENT (24-72 hours)

    1. Complete CHG document with full details
    2. Conduct post-mortem (POST_MORTEM-{CHG-ID}.md)
    3. Retroactively pass applicable gates
    4. Create follow-up CHGs for preventive measures
    5. Close emergency CHG
```

## 6. Bubble-Up Pattern

```
                             BUBBLE-UP PATTERN
               (When root cause is found in upstream layer)

   Defect discovered at Code level (test fails)

                 ROOT CAUSE ANALYSIS
     Q: Where is the actual problem?


    Code        IPLAN       TDD/SPEC    EARS/BDD    PRD/BRD
    bug         wrong       wrong       wrong       wrong
                order       interface   scenario    requirement

   GATE-CODE    GATE-08     GATE-06     GATE-03     GATE-01
   Fix code     Fix IPLAN   Fix SPEC    Fix EARS    Fix BRD
                            Fix TDD     Fix BDD     Fix PRD
                                        Fix ADR

                Cascade     Cascade     Cascade     Full
                to Code     to IPLAN    to SPEC     Cascade
                                          →TDD→IPLAN
```

## 7. Approval Flow Matrix

```
                            APPROVAL MATRIX

                      GATE-01    GATE-03     GATE-06    GATE-08    GATE-CODE
   Change Level       (Business) (Reqs/Arch) (Design)   (IPLAN)    (Impl)

   C1 (Patch)         Self       Self        Self       Self       Self+Peer

   C2 (Minor)         PO + TL    TL+Domain   TL         TL         TL + QA

   C3 (Major)         PO+Arch    Arch+       TL+        TL+        TL + Arch
                      +Stakehld  Security    Domain     Domain     +Full Review

   Emergency          Skip       Skip        Skip       Skip       Incident
                                                                    Commander
                                                                    Post-mortem

Legend:
   PO = Product Owner
   TL = Technical Lead
   Arch = Architecture Board
   QA = QA Lead
   Domain = Domain Expert
   Stakehld = Business Stakeholder
```

## 8. Quick Reference

### 8.1 Gate Selection Guide

| Change Origin | Entry Gate | Cascade Path |
|---------------|------------|--------------|
| Business requirement | GATE-01 | 01 → 03 → 06 → 08 → CODE |
| Requirement/architecture | GATE-03 | 03 → 06 → 08 → CODE |
| SPEC/TDD change | GATE-06 | 06 → 08 → CODE |
| IPLAN change | GATE-08 | 08 → CODE |
| Code fix | GATE-CODE | CODE only |
| Security vulnerability | GATE-03 or EMERGENCY | Depends on CVSS |
| P1 Production incident | EMERGENCY | Bypass + Post-mortem |
| `framework/` spec change | GATE-SPEC | Meta — no cascade; both platforms re-sync |

### 8.2 Gate Entry Points by Change Source

| Change Source | Primary Gate | Conditions |
|---------------|--------------|------------|
| Upstream | GATE-01 | Always |
| Midstream | GATE-03 | Requirements/Architecture changes |
| Design | GATE-06 | SPEC/TDD changes |
| Execution | GATE-08 | IPLAN changes |
| Downstream | GATE-CODE | Implementation fixes |
| External | GATE-03 | Security/API changes |
| External | EMERGENCY | Critical vulnerabilities |
| Feedback | GATE-CODE | Defect fixes |
| Feedback | EMERGENCY | P1 incidents |
| Spec | GATE-SPEC | Changes to the `framework/` spec (meta) |

---

**Related Documents**:
- [GATE-01_BUSINESS_PRODUCT.md](./GATE-01_BUSINESS_PRODUCT.md)
- [GATE-03_REQUIREMENTS_ARCHITECTURE.md](./GATE-03_REQUIREMENTS_ARCHITECTURE.md)
- [GATE-06_DESIGN_TEST.md](./GATE-06_DESIGN_TEST.md)
- [GATE-08_IPLAN.md](./GATE-08_IPLAN.md)
- [GATE-CODE_IMPLEMENTATION.md](./GATE-CODE_IMPLEMENTATION.md)
- [GATE-SPEC_FRAMEWORK.md](./GATE-SPEC_FRAMEWORK.md)
- [GATE_ERROR_CATALOG.md](./GATE_ERROR_CATALOG.md)
```
