---
name: doc-req-reviewer
description: Comprehensive content review and quality assurance for REQ documents - validates atomic requirement completeness, SYS alignment, implementation paths, and identifies issues requiring manual attention
tags:
  - sdd-workflow
  - quality-assurance
  - req-review
  - layer-7-artifact
  - shared-architecture
custom_fields:
  layer: 7
  artifact_type: REQ
  architecture_approaches: [ai-agent-based]
  priority: primary
  development_status: active
  skill_category: quality-assurance
  upstream_artifacts: [REQ]
  downstream_artifacts: []
  version: "1.1"
  last_updated: "2026-02-10"
---

# doc-req-reviewer

## Purpose

Comprehensive **content review and quality assurance** for Atomic Requirements (REQ) documents. This skill performs deep content analysis beyond structural validation, checking requirement atomicity, SYS alignment, implementation paths, unit test coverage, and identifying issues that require manual review.

**Layer**: 7 (REQ Quality Assurance)

**Upstream**: REQ (from `doc-req-autopilot` or `doc-req`)

**Downstream**: None (final QA gate before SPEC/CTR generation)

---

## When to Use This Skill

Use `doc-req-reviewer` when:

- **After REQ Generation**: Run immediately after `doc-req-autopilot` completes
- **Manual REQ Edits**: After making manual changes to REQ
- **Pre-SPEC Check**: Before running `doc-spec-autopilot`
- **Pre-CTR Check**: Before running `doc-ctr-autopilot`
- **Periodic Review**: Regular quality checks on existing REQs

**Do NOT use when**:
- REQ does not exist yet (use `doc-req` or `doc-req-autopilot` first)
- Need structural/schema validation only (use `doc-req-validator`)
- Generating new REQ content (use `doc-req`)

---

## Skill vs Validator: Key Differences

| Aspect | `doc-req-validator` | `doc-req-reviewer` |
|--------|---------------------|-------------------|
| **Focus** | Schema compliance, SPEC-Ready score | Content quality, implementation readiness |
| **Checks** | Required sections, 12-section format | Atomicity, implementation paths, test coverage |
| **Auto-Fix** | Structural issues only | Content issues (links, formatting) |
| **Output** | SPEC-Ready + IMPL-Ready scores | Review score + issue list |
| **Phase** | Phase 4 (Validation) | Phase 5 (Final Review) |
| **Blocking** | Score < threshold blocks | Review score < threshold flags |

---

## Review Checks

### 1. Requirement Atomicity

Validates each requirement is truly atomic.

**Scope**:
- Single responsibility
- No compound requirements
- Independently testable
- Clear scope boundaries

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| REV-RA001 | Error | Requirement has multiple responsibilities |
| REV-RA002 | Warning | Compound requirement (contains AND/OR) |
| REV-RA003 | Warning | Not independently testable |
| REV-RA004 | Info | Scope boundaries could be clearer |

---

### 2. SYS Alignment

Validates REQ traces to SYS requirements.

**Scope**:
- Every REQ maps to SYS requirement
- Decomposition is complete
- No orphaned requirements
- Functional coverage maintained

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| REV-SA001 | Error | REQ without SYS source |
| REV-SA002 | Warning | SYS requirement not fully decomposed |
| REV-SA003 | Warning | Orphaned requirement detected |
| REV-SA004 | Info | Multiple REQs from single SYS (acceptable) |

---

### 3. Acceptance Criteria Quality

Validates acceptance criteria are comprehensive.

**Scope**:
- Minimum 10 functional criteria
- Minimum 5 quality criteria
- Categories covered ([Logic], [Validation], [State], [Edge], [Security])
- Measurable outcomes

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| REV-AC001 | Error | Less than 10 functional criteria |
| REV-AC002 | Error | Less than 5 quality criteria |
| REV-AC003 | Warning | Missing [Security] criteria |
| REV-AC004 | Warning | Criterion not measurable |
| REV-AC005 | Info | [Edge] case criteria could be expanded |

---

### 4. Implementation Path Completeness

Validates Section 11 implementation guidance.

**Scope**:
- Code implementation paths defined
- Module locations specified
- Dependencies documented
- Method signatures suggested

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| REV-IP001 | Error | No implementation paths defined |
| REV-IP002 | Warning | Module location not specified |
| REV-IP003 | Warning | Dependencies not documented |
| REV-IP004 | Info | Method signatures not suggested |

---

### 5. Unit Test Category Coverage

Validates Section 8 test categories.

**Scope**:
- All 5 categories present ([Logic], [Validation], [State], [Edge], [Security])
- Minimum test cases per category
- Test rationale documented

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| REV-UT001 | Error | Missing test category |
| REV-UT002 | Warning | Insufficient tests in category |
| REV-UT003 | Info | Test rationale not documented |

---

### 6. Cross-Link Integrity

Validates Section 10.5 cross-links.

**Scope**:
- @discoverability tags valid
- Related REQs exist
- Bidirectional links present

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| REV-CL001 | Error | Broken cross-link |
| REV-CL002 | Warning | Missing bidirectional link |
| REV-CL003 | Info | @discoverability target not yet created |

---

### 7. Placeholder Detection

Identifies incomplete content requiring replacement.

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| REV-P001 | Error | [TODO] placeholder found |
| REV-P002 | Error | [TBD] placeholder found |
| REV-P003 | Warning | Template value not replaced |

---

### 8. Naming Compliance

Validates element IDs follow `doc-naming` standards.

**Scope**:
- Element IDs use `REQ.NN.TT.SS` format
- Element type codes valid for REQ (01, 05, 06, 27)
- Atomic file naming convention

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| REV-N001 | Error | Invalid element ID format |
| REV-N002 | Error | Element type code not valid for REQ |
| REV-N003 | Error | Legacy pattern detected |

---

## Review Score Calculation

**Scoring Formula**:

| Category | Weight | Calculation |
|----------|--------|-------------|
| Requirement Atomicity | 15% | (atomic / total_reqs) × 15 |
| SYS Alignment | 15% | (aligned / total_reqs) × 15 |
| Acceptance Criteria Quality | 20% | (quality_score) × 20 |
| Implementation Path Completeness | 15% | (complete_paths / total) × 15 |
| Unit Test Category Coverage | 15% | (covered_categories / 5) × 15 |
| Cross-Link Integrity | 5% | (valid_links / total) × 5 |
| Placeholder Detection | 5% | (no_placeholders ? 5 : 5 - count) |
| Naming Compliance | 10% | (valid_ids / total_ids) × 10 |

**Total**: Sum of all categories (max 100)

**Thresholds**:
- **PASS**: ≥ 90
- **WARNING**: 80-89
- **FAIL**: < 80

---

## Command Usage

```bash
# Review specific REQ module
/doc-req-reviewer REQ-03

# Review specific atomic REQ
/doc-req-reviewer REQ-03-001

# Review REQ by path
/doc-req-reviewer docs/07_REQ/REQ-03_f3_observability/

# Review all REQs
/doc-req-reviewer all
```

---

## Output Report

Review reports are stored alongside the reviewed document per project standards.

**File Naming**: `REQ-NN.R_review_report_vNNN.md` (module-level) or `REQ-NN-SSS.R_review_report_vNNN.md` (atomic-level)

**Location**: Same folder as the reviewed REQ document.

### Versioning Rules

1. **First Review**: Creates `REQ-NN.R_review_report_v001.md`
2. **Subsequent Reviews**: Auto-increments version (v002, v003, etc.)
3. **Same-Day Reviews**: Each review gets unique version number

**Version Detection**: Scans folder for existing `REQ-NN.R_review_report_v*.md` files and increments.

**Example**:

```
docs/07_REQ/REQ-03_f3_observability/
├── REQ-03-001_metrics_collection.md
├── REQ-03-001.R_review_report_v001.md    # First review
└── REQ-03-001.R_review_report_v002.md    # After fixes
```

### Delta Reporting

When previous reviews exist, include score comparison in the report.

See `REVIEW_DOCUMENT_STANDARDS.md` for complete versioning requirements.

---

## Integration with doc-req-autopilot

This skill is invoked during Phase 5 of `doc-req-autopilot`:

```mermaid
flowchart LR
    A[Phase 4: Validation] --> B[Phase 5: Final Review]
    B --> C{doc-req-reviewer}
    C --> D[Phase 6: Continue]
```

---

## Related Skills

| Skill | Relationship |
|-------|--------------|
| `doc-naming` | Naming standards for Check #8 |
| `doc-req-autopilot` | Invokes this skill in Phase 5 |
| `doc-req-validator` | Structural validation (Phase 4) |
| `doc-req` | REQ creation rules |
| `doc-sys-reviewer` | Upstream QA |
| `doc-spec-autopilot` | Downstream consumer |
| `doc-ctr-autopilot` | Downstream consumer (for external APIs) |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.1 | 2026-02-10 | Added review versioning support (_vNNN pattern); Delta reporting for score comparison |
| 1.0 | 2026-02-10 | Initial skill creation with 8 review checks; Atomicity validation; Acceptance criteria quality; Implementation path completeness |
