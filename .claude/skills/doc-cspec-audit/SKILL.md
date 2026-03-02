---
name: doc-cspec-audit
description: Unified CSPEC quality gate - validates structure, detects issues, computes CODE-Ready score, and produces report for fixer
metadata:
  tags:
    - sdd-workflow
    - layer-9-artifact
    - cspec-artifact
    - quality-assurance
  custom_fields:
    layer: 9
    subtype_code: 50
    artifact_type: CSPEC
    deliverable_type: code
    architecture_approaches: [ai-agent-based]
    priority: primary
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [CSPEC]
    downstream_artifacts: [Audit Report]
    version: "1.0"
    last_updated: "2026-03-01"
---

# doc-cspec-audit

## Purpose

Unified **CSPEC quality gate** that combines structural validation, content review, and CODE-Ready scoring into a single comprehensive audit. Produces a standardized report that can be consumed by `doc-cspec-fixer` for automated remediation.

**Layer**: 9.50 (CSPEC Quality Gate)

**Upstream**: CSPEC document

**Downstream**: Audit Report (`CSPEC-NN.A_audit_report_vNNN.md`)

---

## When to Use

Use `doc-cspec-audit` when:
- **Pre-Release Check**: Final quality gate before TSPEC/TASKS generation
- **Comprehensive Review**: Need both structural and content validation
- **Score Verification**: Need official CODE-Ready score
- **CI/CD Integration**: Automated quality checks in pipeline

**Preferred over individual skills when**:
- Need single comprehensive report
- Running automated pipeline
- Need consistent scoring methodology

---

## Audit Components

### 1. Structure Validation (30%)
- File location compliance
- YAML syntax validity
- Required sections present
- Metadata completeness

### 2. Content Quality (40%)
- Interface definitions complete
- CTR compliance verified
- Algorithm specifications present
- Implementation guidance adequate

### 3. Traceability (15%)
- Cumulative tags complete
- REQ mappings valid
- CTR references valid
- Test mappings complete

### 4. Readiness Metrics (15%)
- CODE-Ready score calculation
- Downstream readiness assessment
- Risk identification

---

## CODE-Ready Score Calculation

| Component | Weight | Scoring Criteria |
|-----------|--------|------------------|
| Interface Completeness | 20% | All interfaces documented with full signatures |
| CTR Compliance | 20% | All CTR contracts implemented correctly |
| Algorithm Specification | 15% | Core algorithms documented with complexity analysis |
| Error Handling | 15% | Exception handling defined for all interfaces |
| Test Mapping | 15% | Unit and integration tests mapped |
| Traceability | 15% | All cumulative tags present and valid |

**Thresholds**:
- **PASS**: ≥90%
- **CONDITIONAL**: 80-89%
- **FAIL**: <80%

---

## Audit Report Format

```markdown
# CSPEC-NN Audit Report

## Document Information
- **CSPEC ID**: CSPEC-NN
- **Title**: {title}
- **Audit Date**: YYYY-MM-DD
- **Audit Version**: vNNN

## Executive Summary
- **CODE-Ready Score**: NN% [PASS/CONDITIONAL/FAIL]
- **Critical Issues**: N
- **Warnings**: N
- **Recommendations**: N

## Detailed Findings

### Structure Validation
| Check | Status | Details |
|-------|--------|---------|
| File Location | PASS/FAIL | |
| YAML Syntax | PASS/FAIL | |
| Required Sections | PASS/FAIL | |
| Metadata | PASS/FAIL | |

### Content Quality
| Check | Status | Details |
|-------|--------|---------|
| Interfaces | NN% | |
| CTR Compliance | NN% | |
| Algorithms | NN% | |
| Error Handling | NN% | |

### Traceability
| Tag | Present | Valid |
|-----|---------|-------|
| @brd | Yes/No | Yes/No |
| @prd | Yes/No | Yes/No |
| ... | | |

### Issues

#### Critical (Must Fix)
1. [Issue description]

#### Warnings (Should Fix)
1. [Warning description]

#### Recommendations (Nice to Have)
1. [Recommendation]

## Metrics Summary
| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| CODE-Ready | NN% | ≥90% | |
| Interface Coverage | NN% | 100% | |
| CTR Compliance | NN% | 100% | |
| Test Mapping | NN% | 90% | |

## Next Steps
1. Run `doc-cspec-fixer` with this report
2. Re-audit after fixes applied
3. Proceed to TSPEC generation when PASS
```

---

## Output Files

| File | Purpose |
|------|---------|
| `CSPEC-NN.A_audit_report_vNNN.md` | Comprehensive audit report |

---

## Integration

### Audit → Fix → Re-Audit Cycle
```
doc-cspec-audit → CSPEC-NN.A_audit_report.md → doc-cspec-fixer → doc-cspec-audit
```

### CI/CD Pipeline
```yaml
steps:
  - name: CSPEC Audit
    run: invoke doc-cspec-audit --cspec docs/09_SPEC/CSPEC/CSPEC-NN/
  - name: Check Score
    run: check CODE-Ready >= 90%
  - name: Fix if Needed
    run: invoke doc-cspec-fixer --report CSPEC-NN.A_audit_report.md
```

---

## References

- Template: `ai_dev_ssd_flow/09_SPEC/CSPEC/CSPEC-MVP-TEMPLATE.yaml`
- Schema: `ai_dev_ssd_flow/09_SPEC/CSPEC/CSPEC_MVP_SCHEMA.yaml`
- Validation Rules: `ai_dev_ssd_flow/09_SPEC/CSPEC/CSPEC_MVP_VALIDATION_RULES.md`
- Creation Rules: `ai_dev_ssd_flow/09_SPEC/CSPEC/CSPEC_MVP_CREATION_RULES.md`
