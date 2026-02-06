---
title: "Gate Error Catalog"
tags:
  - change-management
  - gate-system
  - error-codes
  - shared-architecture
custom_fields:
  document_type: reference
  artifact_type: CHG
  development_status: active
---

# Gate Error Catalog

This document provides a complete catalog of all error and warning codes across the 4-Gate Change Management System.

## 1. Error Code Format

```
GATE-NN-SNNN

Where:
  NN   = Gate number (01, 05, 09, 12)
  S    = Severity (E=Error, W=Warning, I=Info)
  NNN  = Sequential number within gate and severity
```

**Exit Code Mapping**:
| Exit Code | Meaning | Action |
|-----------|---------|--------|
| 0 | Pass (no errors, no warnings) | Proceed |
| 1 | Pass with warnings | Review warnings, proceed |
| 2 | Fail (blocking errors) | Fix errors before proceeding |

## 2. GATE-01: Business/Product Errors

### 2.1 Blocking Errors (E)

| Code | Category | Description | Resolution |
|------|----------|-------------|------------|
| GATE-01-E001 | Documentation | BRD change must have business justification | Add "Business Justification" section with measurable impact |
| GATE-01-E002 | Traceability | PRD change must link to BRD objective | Add `@brd:` tag with valid BRD reference |
| GATE-01-E003 | Syntax | EARS must follow WHEN-THE-SHALL syntax | Fix WHEN-THE-SHALL-WITHIN format |
| GATE-01-E004 | Syntax | BDD must have Given-When-Then format | Fix Given-When-Then structure in .feature file |
| GATE-01-E005 | Classification | Breaking change missing L3 classification | Escalate change level to L3 |
| GATE-01-E006 | Approval | No stakeholder approval for L3 change | Obtain and document stakeholder signature |

### 2.2 Warnings (W)

| Code | Category | Description | Resolution |
|------|----------|-------------|------------|
| GATE-01-W001 | Scope | Large scope (>5 layers) without L3 | Consider elevating to L3 or phased implementation |
| GATE-01-W002 | Approval | Missing stakeholder sign-off for L2 | Obtain Product Owner approval |
| GATE-01-W003 | Planning | Cascade affects >10 artifacts | Create detailed implementation plan |
| GATE-01-W004 | Documentation | External trigger without CVE/compliance ref | Add reference number |

## 3. GATE-05: Architecture/Contract Errors

### 3.1 Blocking Errors (E)

| Code | Category | Description | Resolution |
|------|----------|-------------|------------|
| GATE-05-E001 | Structure | ADR must document context, decision, consequences | Add Context, Decision, Consequences sections |
| GATE-05-E002 | Quality | SYS quality attributes must be measurable | Add quantified thresholds (e.g., "< 100ms") |
| GATE-05-E003 | Traceability | REQ must have 6 upstream traceability tags | Add @brd, @prd, @ears, @bdd, @adr, @sys tags |
| GATE-05-E004 | Validation | CTR schema must validate (YAML + MD sync) | Fix YAML schema or synchronize MD document |
| GATE-05-E005 | Classification | Breaking API change without L3 classification | Escalate to L3 |
| GATE-05-E006 | Security | External change missing security review | Complete security assessment |

### 3.2 Warnings (W)

| Code | Category | Description | Resolution |
|------|----------|-------------|------------|
| GATE-05-W001 | Documentation | External security change without CVE reference | Add CVE-YYYY-NNNN reference |
| GATE-05-W002 | Documentation | CTR version increment without changelog | Document API changes in changelog |
| GATE-05-W003 | Completeness | ADR alternatives section missing | Document considered alternatives |
| GATE-05-W004 | Readiness | REQ SPEC-Ready score < 90% | Improve requirement completeness |

## 4. GATE-09: Design/Test Errors

### 4.1 Blocking Errors (E)

| Code | Category | Description | Resolution |
|------|----------|-------------|------------|
| GATE-09-E001 | Readiness | SPEC must have implementation readiness score >= 90% | Complete missing sections, clarify ambiguities |
| GATE-09-E002 | Coverage | TSPEC must cover all SPEC interfaces | Add test specifications for all interfaces |
| GATE-09-E003 | Traceability | TASKS must link to SPEC and TSPEC | Add @spec and @tspec tags |
| GATE-09-E004 | Consistency | TSPEC change without corresponding SPEC alignment | Synchronize TSPEC with SPEC changes |
| GATE-09-E005 | TDD | SPEC breaking change without TSPEC update | Update TSPEC first (TDD compliance) |
| GATE-09-E006 | Dependencies | TASKS dependency cycle detected | Resolve dependency graph cycles |

### 4.2 Warnings (W)

| Code | Category | Description | Resolution |
|------|----------|-------------|------------|
| GATE-09-W001 | Performance | Algorithm change without performance baseline | Document current performance metrics |
| GATE-09-W002 | Coverage | TSPEC missing edge case coverage | Add boundary condition tests |
| GATE-09-W003 | Complexity | SPEC implementation complexity > 4 | Consider decomposition |
| GATE-09-W004 | Planning | TASKS estimated effort exceeds sprint capacity | Split into multiple sprints |
| GATE-09-W005 | Coverage | TSPEC missing negative test cases | Add failure scenario tests |

## 5. GATE-12: Implementation Errors

### 5.1 Blocking Errors (E)

| Code | Category | Description | Resolution |
|------|----------|-------------|------------|
| GATE-12-E001 | Analysis | Root cause analysis must be completed | Add RCA section with 5-Whys or fishbone analysis |
| GATE-12-E002 | Layer | Fix must be at correct layer (not symptom masking) | Trace to actual problem layer |
| GATE-12-E003 | Testing | Regression tests included | Add tests covering the fix |
| GATE-12-E004 | Review | Code review required for L2/L3 changes | Complete review process |
| GATE-12-E005 | Build | Build must pass before merge | Fix CI pipeline errors |
| GATE-12-E006 | Coverage | Test coverage must not decrease | Add tests to maintain coverage |

### 5.2 Warnings (W)

| Code | Category | Description | Resolution |
|------|----------|-------------|------------|
| GATE-12-W001 | TDD | Code fix without corresponding TSPEC update | Update TSPEC for TDD compliance |
| GATE-12-W002 | Classification | Large code change as L1 | Consider L2 classification |
| GATE-12-W003 | Performance | Performance-critical code without benchmark | Add performance test |
| GATE-12-W004 | Security | Security-sensitive code without security review | Request security review |
| GATE-12-W005 | Quality | Dead code detected | Remove unused code |

## 6. Emergency Bypass Errors

### 6.1 Blocking Errors (E)

| Code | Category | Description | Resolution |
|------|----------|-------------|------------|
| EMG-E001 | Authorization | Emergency not authorized by incident commander | Obtain authorization |
| EMG-E002 | Classification | Non-critical issue using emergency bypass | Use standard gate process |
| EMG-E003 | Documentation | Emergency stub not created | Create CHG-EMG-{timestamp}.md |
| EMG-E004 | Timeline | Post-mortem not completed within 72 hours | Complete POST_MORTEM-{CHG-ID}.md |
| EMG-E005 | Closure | Emergency CHG not closed | Complete all closure requirements |

### 6.2 Warnings (W)

| Code | Category | Description | Resolution |
|------|----------|-------------|------------|
| EMG-W001 | Documentation | Emergency stub missing incident reference | Add incident ticket number |
| EMG-W002 | Follow-up | Preventive measure CHG not created | Create follow-up CHG |
| EMG-W003 | Review | Post-mortem missing root cause | Complete 5-Whys analysis |

## 7. Cross-Gate Errors

### 7.1 Routing Errors

| Code | Category | Description | Resolution |
|------|----------|-------------|------------|
| ROUTE-E001 | Routing | Invalid gate entry for change source | Route to correct gate per source |
| ROUTE-E002 | Cascade | Skipped mandatory gate | Pass all required gates in sequence |
| ROUTE-E003 | Approval | Missing upstream gate approval | Complete upstream gate first |
| ROUTE-E004 | Classification | Change level mismatch across gates | Maintain consistent level |

### 7.2 Validation Errors

| Code | Category | Description | Resolution |
|------|----------|-------------|------------|
| VAL-E001 | Schema | CHG document fails schema validation | Fix YAML frontmatter |
| VAL-E002 | Structure | Required section missing | Add missing section |
| VAL-E003 | Traceability | Broken cross-reference | Fix or remove invalid reference |
| VAL-E004 | Status | Invalid status transition | Follow status workflow |

## 8. Error Resolution Quick Reference

### 8.1 Most Common Errors

| Error | Frequency | Quick Fix |
|-------|-----------|-----------|
| GATE-05-E003 | High | Add 6 traceability tags to REQ |
| GATE-09-E001 | High | Improve SPEC completeness |
| GATE-12-E001 | Medium | Add RCA section |
| GATE-01-E005 | Medium | Escalate breaking change to L3 |

### 8.2 Resolution Templates

```markdown
## GATE-05-E003 Resolution
Add all 6 upstream traceability tags:

### 11. Traceability
@brd: BRD-XXX
@prd: PRD-XXX.YY
@ears: EARS.XXX.YY.ZZ
@bdd: SCEN-XXX
@adr: ADR-XXX
@sys: SYS-XXX-XXX

## GATE-12-E001 Resolution
Add Root Cause Analysis section:

### Root Cause Analysis
**5-Whys Analysis**:
1. Why? [First-level cause]
2. Why? [Second-level cause]
3. Why? [Third-level cause]
4. Why? [Fourth-level cause]
5. Why? [Root cause]

**Root Cause Layer**: L[N] - [Layer Name]
**Fix Approach**: [How this fix addresses root cause]
```

## 9. Validation Commands

### 9.1 Individual Gate Validation

```bash
# GATE-01 validation
./CHG/scripts/validate_gate01.sh <CHG_FILE> [--verbose]

# GATE-05 validation
./CHG/scripts/validate_gate05.sh <CHG_FILE> [--verbose]

# GATE-09 validation
./CHG/scripts/validate_gate09.sh <CHG_FILE> [--verbose]

# GATE-12 validation
./CHG/scripts/validate_gate12.sh <CHG_FILE> [--verbose]
```

### 9.2 All Gates Validation

```bash
# Validate all gates
./CHG/scripts/validate_all_gates.sh <CHG_FILE> [--verbose]

# Routing validation
python CHG/scripts/validate_chg_routing.py <CHG_FILE>
```

### 9.3 Exit Codes

| Code | Meaning | Action Required |
|------|---------|-----------------|
| 0 | All checks pass | Proceed to next gate |
| 1 | Warnings present | Review warnings, may proceed |
| 2 | Errors present | Fix errors before proceeding |
| 3 | Invalid input | Check file path/format |

---

**Related Documents**:
- [GATE-01_BUSINESS_PRODUCT.md](./GATE-01_BUSINESS_PRODUCT.md)
- [GATE-05_ARCHITECTURE_CONTRACT.md](./GATE-05_ARCHITECTURE_CONTRACT.md)
- [GATE-09_DESIGN_TEST.md](./GATE-09_DESIGN_TEST.md)
- [GATE-12_IMPLEMENTATION.md](./GATE-12_IMPLEMENTATION.md)
- [GATE_INTERACTION_DIAGRAM.md](./GATE_INTERACTION_DIAGRAM.md)
