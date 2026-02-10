---
name: doc-adr-reviewer
description: Comprehensive content review and quality assurance for ADR documents - validates decision completeness, BRD alignment, consequence coverage, and identifies issues requiring manual attention
tags:
  - sdd-workflow
  - quality-assurance
  - adr-review
  - layer-5-artifact
  - shared-architecture
custom_fields:
  layer: 5
  artifact_type: ADR
  architecture_approaches: [ai-agent-based]
  priority: primary
  development_status: active
  skill_category: quality-assurance
  upstream_artifacts: [ADR]
  downstream_artifacts: []
  version: "1.2"
  last_updated: "2026-02-10T14:30:00"
---

# doc-adr-reviewer

## Purpose

Comprehensive **content review and quality assurance** for Architecture Decision Records (ADR). This skill performs deep content analysis beyond structural validation, checking decision completeness, BRD topic alignment, consequence coverage, alternative evaluation, and identifying issues that require manual architectural review.

**Layer**: 5 (ADR Quality Assurance)

**Upstream**: ADR (from `doc-adr-autopilot` or `doc-adr`)

**Downstream**: None (final QA gate before SYS generation)

---

## When to Use This Skill

Use `doc-adr-reviewer` when:

- **After ADR Generation**: Run immediately after `doc-adr-autopilot` completes
- **Manual ADR Edits**: After making manual changes to ADR
- **Pre-SYS Check**: Before running `doc-sys-autopilot`
- **Periodic Review**: Regular quality checks on existing ADRs
- **Architecture Reviews**: During formal architecture review sessions

**Do NOT use when**:
- ADR does not exist yet (use `doc-adr` or `doc-adr-autopilot` first)
- Need structural/schema validation only (use `doc-adr-validator`)
- Generating new ADR content (use `doc-adr`)

---

## Skill vs Validator: Key Differences

| Aspect | `doc-adr-validator` | `doc-adr-reviewer` |
|--------|---------------------|-------------------|
| **Focus** | Schema compliance, SYS-Ready score | Content quality, decision rationale |
| **Checks** | Required sections, format | Consequence coverage, alternative evaluation |
| **Auto-Fix** | Structural issues only | Content issues (links, formatting) |
| **Output** | SYS-Ready score (numeric) | Review score + issue list |
| **Phase** | Phase 4 (Validation) | Phase 5 (Final Review) |
| **Blocking** | SYS-Ready < threshold blocks | Review score < threshold flags |

---

## Review Workflow

```mermaid
flowchart TD
    A[Input: ADR Path] --> B[Load ADR Files]
    B --> C{Single or Multiple?}

    C -->|Multiple| D[Load All ADR Files]
    C -->|Single| E[Load Single File]

    D --> F[Run Review Checks]
    E --> F

    subgraph Review["Review Checks"]
        F --> G[1. Decision Completeness]
        G --> H[2. BRD Topic Alignment]
        H --> I[3. Consequence Coverage]
        I --> J[4. Alternative Evaluation]
        J --> K[5. Cross-Reference Integrity]
        K --> L[6. Placeholder Detection]
        L --> M[7. Naming Compliance]
        M --> N2[8. Upstream Drift Detection]
    end

    N2 --> N{Issues Found?}
    N -->|Yes| O[Categorize Issues]
    O --> P{Auto-Fixable?}
    P -->|Yes| Q[Apply Auto-Fixes]
    Q --> R[Re-run Affected Checks]
    P -->|No| S[Flag for Manual Review]
    R --> N
    S --> T[Generate Report]
    N -->|No| T
    T --> U[Calculate Review Score]
    U --> V{Score >= Threshold?}
    V -->|Yes| W[PASS]
    V -->|No| X[FAIL with Details]
```

---

## Review Checks

### 1. Decision Completeness

Validates ADR has all required decision components.

**Scope**:
- Context clearly stated
- Decision explicitly documented
- Rationale provided
- Status defined
- Date recorded

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| REV-DC001 | Error | Context section missing or empty |
| REV-DC002 | Error | Decision not explicitly stated |
| REV-DC003 | Error | Rationale missing |
| REV-DC004 | Warning | Status not defined |
| REV-DC005 | Warning | Date not recorded |

---

### 2. BRD Topic Alignment

Validates ADR addresses BRD Section 7.2 topics.

**Scope**:
- ADR maps to BRD ADR topic
- Topic category correct (Infrastructure, Data, Security, etc.)
- Decision matches topic requirements
- All BRD topics have corresponding ADRs

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| REV-BA001 | Error | ADR not linked to BRD topic |
| REV-BA002 | Error | Topic category mismatch |
| REV-BA003 | Warning | Decision doesn't fully address topic |
| REV-BA004 | Info | BRD topic not yet addressed by ADR |

---

### 3. Consequence Coverage

Validates positive and negative consequences documented.

**Scope**:
- Positive consequences listed
- Negative consequences/trade-offs acknowledged
- Risk assessment included
- Mitigation strategies defined

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| REV-CC001 | Error | No consequences documented |
| REV-CC002 | Warning | Only positive consequences (unrealistic) |
| REV-CC003 | Warning | Negative consequences without mitigation |
| REV-CC004 | Info | Risk assessment could be more detailed |

---

### 4. Alternative Evaluation

Validates alternatives were properly considered.

**Scope**:
- Multiple alternatives evaluated
- Comparison criteria defined
- Trade-off analysis present
- Rejection reasons documented

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| REV-AE001 | Error | No alternatives considered |
| REV-AE002 | Warning | Only one alternative (insufficient) |
| REV-AE003 | Warning | Missing comparison criteria |
| REV-AE004 | Info | Alternative rejection reason unclear |

---

### 5. Cross-Reference Integrity

Validates links to related ADRs and documents.

**Scope**:
- Related ADRs referenced
- Superseded ADRs linked
- BRD/PRD traceability tags present
- External references valid

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| REV-CR001 | Error | Broken cross-reference |
| REV-CR002 | Warning | Missing related ADR link |
| REV-CR003 | Warning | Superseded ADR not referenced |
| REV-CR004 | Info | External link unverified |

---

### 6. Placeholder Detection

Identifies incomplete content requiring replacement.

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| REV-P001 | Error | [TODO] placeholder found |
| REV-P002 | Error | [TBD] placeholder found |
| REV-P003 | Warning | Template value not replaced |

---

### 7. Naming Compliance

Validates element IDs follow `doc-naming` standards.

**Scope**:
- Element IDs use `ADR.NN.TT.SS` format
- Element type codes valid for ADR (13, 14, 15, 16)
- ADR numbering sequential

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| REV-N001 | Error | Invalid element ID format |
| REV-N002 | Error | Element type code not valid for ADR |
| REV-N003 | Warning | ADR numbering gap detected |

---

### 8. Upstream Drift Detection

Detects when upstream source documents have been modified after the ADR was created or last updated.

**Purpose**: Identifies stale ADR content that may not reflect current BDD scenarios or BRD topic definitions. When upstream documents change, the ADR may need updates to maintain alignment.

**Upstream Documents**:
- **BDD documents**: Feature files and scenario definitions that ADR decisions must support
- **BRD Section 7.2**: ADR topic definitions that scope this decision

**Scope**:
- `@bdd:` tag targets (BDD feature files)
- `@brd:` tag references (BRD topic sections)
- Traceability section upstream artifact links
- Any markdown links to `../04_BDD/` or `../01_BRD/`

**Detection Methods**:

| Method | Description | Precision |
|--------|-------------|-----------|
| **Timestamp Comparison** | Compares source doc `mtime` vs ADR creation/update date | Medium |
| **Content Hash** | SHA-256 hash of referenced sections | High |
| **Version Tracking** | Checks `version` field in YAML frontmatter | High |

**Algorithm**:

```
1. Extract all upstream references from ADR:
   - @bdd: tags → [path, scenario anchor]
   - @brd: tags → [document ID, section 7.2 topic]
   - Links to ../04_BDD/ → [path]
   - Links to ../01_BRD/ → [path]
   - Traceability table upstream artifacts → [path]

2. For each upstream reference:
   a. Resolve path to absolute file path
   b. Check file exists (already covered by Check #5)
   c. Get file modification time (mtime)
   d. Compare mtime > ADR last_updated date
   e. If mtime > ADR date → flag as DRIFT

3. Optional (high-precision mode):
   a. Extract specific section referenced by anchor
   b. Compute SHA-256 hash of section content
   c. Compare to cached hash (stored in .drift_cache.json)
   d. If hash differs → flag as CONTENT_DRIFT
```

**Drift Cache File** (optional):

Location: `docs/05_ADR/.drift_cache.json`

```json
{
  "adr_version": "1.0",
  "adr_updated": "2026-02-10T14:30:00",
  "upstream_hashes": {
    "../../04_BDD/BDD-01_authentication.feature": "a1b2c3d4...",
    "../../01_BRD/BRD-01_platform/07_technical_requirements.md#7.2": "e5f6g7h8..."
  }
}
```

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| REV-D001 | Warning | Upstream document modified after ADR creation |
| REV-D002 | Warning | Referenced section content has changed (hash mismatch) |
| REV-D003 | Info | Upstream document version incremented |
| REV-D004 | Info | New content added to upstream document |
| REV-D005 | Error | Critical upstream document substantially modified (>20% change) |

**Report Output**:

```markdown
## Upstream Drift Analysis

| Upstream Document | ADR Reference | Last Modified | ADR Updated | Days Stale | Severity |
|-------------------|---------------|---------------|-------------|------------|----------|
| BDD-01_authentication.feature | @bdd Section 3 | 2026-02-08T10:15:00 | 2026-02-05T09:00:00 | 3 | Warning |
| BRD-01 Section 7.2 | @brd Topic | 2026-02-10T14:30:00 | 2026-02-05T09:00:00 | 5 | Warning |

**Recommendation**: Review upstream changes and update ADR if decision context has changed.
```

**Auto-Actions**:
- Update `.drift_cache.json` with current hashes after review
- Add `[DRIFT]` marker to affected @bdd/@brd tags (optional)
- Generate drift summary in review report

**Configuration**:

| Setting | Default | Description |
|---------|---------|-------------|
| `drift_threshold_days` | 7 | Days before drift becomes Warning |
| `critical_threshold_days` | 30 | Days before drift becomes Error |
| `enable_hash_check` | false | Enable SHA-256 content hashing |
| `tracked_patterns` | `@bdd:`, `@brd:` | Patterns to track for drift |

---

## Review Score Calculation

**Scoring Formula**:

| Category | Weight | Calculation |
|----------|--------|-------------|
| Decision Completeness | 24% | (complete_fields / required_fields) × 24 |
| BRD Topic Alignment | 19% | (aligned_topics / total_topics) × 19 |
| Consequence Coverage | 19% | (coverage_score) × 19 |
| Alternative Evaluation | 14% | (alternatives_evaluated / 3) × 14 |
| Cross-Reference Integrity | 5% | (valid_refs / total_refs) × 5 |
| Placeholder Detection | 5% | (no_placeholders ? 5 : 5 - count) |
| Naming Compliance | 9% | (valid_ids / total_ids) × 9 |
| Upstream Drift | 5% | (fresh_refs / total_refs) × 5 |

**Total**: Sum of all categories (max 100)

**Thresholds**:
- **PASS**: ≥ 90
- **WARNING**: 80-89
- **FAIL**: < 80

---

## Command Usage

```bash
# Review specific ADR
/doc-adr-reviewer ADR-01

# Review ADR by path
/doc-adr-reviewer docs/05_ADR/ADR-01_authentication_strategy.md

# Review all ADRs
/doc-adr-reviewer all
```

---

## Output Report

Review reports are stored alongside the reviewed document per project standards.

**File Naming**: `ADR-NN.R_review_report_vNNN.md`

**Location**: Same folder as the reviewed ADR document.

### Versioning Rules

1. **First Review**: Creates `ADR-NN.R_review_report_v001.md`
2. **Subsequent Reviews**: Auto-increments version (v002, v003, etc.)
3. **Same-Day Reviews**: Each review gets unique version number

**Version Detection**: Scans folder for existing `ADR-NN.R_review_report_v*.md` files and increments.

**Example**:

```
docs/05_ADR/
├── ADR-01_authentication_strategy.md
├── ADR-01.R_review_report_v001.md    # First review
└── ADR-01.R_review_report_v002.md    # After fixes
```

### Delta Reporting

When previous reviews exist, include score comparison in the report.

See `REVIEW_DOCUMENT_STANDARDS.md` for complete versioning requirements.

---

## Integration with doc-adr-autopilot

This skill is invoked during Phase 5 of `doc-adr-autopilot`:

```mermaid
flowchart LR
    A[Phase 4: Validation] --> B[Phase 5: Final Review]
    B --> C{doc-adr-reviewer}
    C --> D[Phase 6: Continue]
```

---

## Related Skills

| Skill | Relationship |
|-------|--------------|
| `doc-naming` | Naming standards for Check #7 |
| `doc-adr-autopilot` | Invokes this skill in Phase 5 |
| `doc-adr-validator` | Structural validation (Phase 4) |
| `doc-adr-fixer` | Applies fixes based on review findings |
| `doc-adr` | ADR creation rules |
| `doc-bdd-reviewer` | Upstream QA |
| `doc-sys-autopilot` | Downstream consumer |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.2 | 2026-02-10 | Added Check #8: Upstream Drift Detection - detects when BDD/BRD documents modified after ADR creation; REV-D001-D005 error codes; drift cache support; configurable thresholds; Added doc-adr-fixer to Related Skills |
| 1.1 | 2026-02-10 | Added review versioning support (_vNNN pattern); Delta reporting for score comparison |
| 1.0 | 2026-02-10 | Initial skill creation with 7 review checks; Decision completeness; Consequence coverage; Alternative evaluation |
