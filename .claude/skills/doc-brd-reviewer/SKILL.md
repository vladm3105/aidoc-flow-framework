---
name: doc-brd-reviewer
description: Comprehensive content review and quality assurance for BRD documents - validates link integrity, requirement completeness, strategic alignment, and identifies issues requiring manual attention
tags:
  - sdd-workflow
  - quality-assurance
  - brd-review
  - layer-1-artifact
  - shared-architecture
custom_fields:
  layer: 1
  artifact_type: BRD
  architecture_approaches: [ai-agent-based]
  priority: primary
  development_status: active
  skill_category: quality-assurance
  upstream_artifacts: [Strategy, Stakeholder Input]
  downstream_artifacts: []
  version: "1.3"
  last_updated: "2026-02-10T14:30:00"
---

# doc-brd-reviewer

## Purpose

Comprehensive **content review and quality assurance** for Business Requirements Documents (BRD). This skill performs deep content analysis beyond structural validation, checking link integrity, requirement completeness, ADR topic coverage, strategic alignment, and identifying issues that require manual business review.

**Layer**: 1 (BRD Quality Assurance)

**Upstream**: Strategy documents, stakeholder requirements

**Downstream**: None (final QA gate before PRD generation)

---

## When to Use This Skill

Use `doc-brd-reviewer` when:

- **After BRD Generation**: Run immediately after `doc-brd-autopilot` completes
- **Manual BRD Edits**: After making manual changes to a BRD
- **Pre-PRD Check**: Before running `doc-prd-autopilot`
- **Periodic Review**: Regular quality checks on existing BRDs
- **CI/CD Integration**: Automated review gate in documentation pipelines

**Do NOT use when**:
- BRD does not exist yet (use `doc-brd` or `doc-brd-autopilot` first)
- Need structural/schema validation only (use `doc-brd-validator`)
- Generating new BRD content (use `doc-brd`)

---

## Skill vs Validator: Key Differences

| Aspect | `doc-brd-validator` | `doc-brd-reviewer` |
|--------|---------------------|-------------------|
| **Focus** | Schema compliance, PRD-Ready score | Content quality, strategic alignment |
| **Checks** | Required sections, field formats | Link integrity, ADR completeness, placeholders |
| **Auto-Fix** | Structural issues only | Content issues (links, dates, placeholders) |
| **Output** | PRD-Ready score (numeric) | Review score + issue list |
| **Phase** | Phase 4 (Validation) | Phase 5 (Final Review) |
| **Blocking** | PRD-Ready < threshold blocks | Review score < threshold flags |

---

## Review Workflow

```mermaid
flowchart TD
    A[Input: BRD Path] --> B[Load BRD Files]
    B --> C{Sectioned or Monolithic?}

    C -->|Sectioned| D[Load All Section Files]
    C -->|Monolithic| E[Load Single File]

    D --> F[Run Review Checks]
    E --> F

    subgraph Review["Review Checks"]
        F --> G[1. Link Integrity]
        G --> H[2. Requirement Completeness]
        H --> I[3. ADR Topic Coverage]
        I --> J[4. Placeholder Detection]
        J --> K[5. Traceability Tags]
        K --> L[6. Section Completeness]
        L --> M[7. Strategic Alignment]
        M --> M2[8. Naming Compliance]
        M2 --> M3[9. Upstream Drift Detection]
    end

    M3 --> N{Issues Found?}
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

### 1. Link Integrity

Validates all internal document links resolve correctly.

**Scope**:
- Navigation links (`[Previous: ...]`, `[Next: ...]`)
- Section cross-references (`[See Section 7.2](...)`)
- Index to section links
- External documentation links (warns if unreachable)

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| REV-L001 | Error | Broken internal link |
| REV-L002 | Warning | External link unreachable |
| REV-L003 | Info | Link path uses absolute instead of relative |

---

### 2. Requirement Completeness

Validates all business requirements have complete specifications.

**Scope**:
- Each requirement has acceptance criteria
- Success metrics defined
- Scope boundaries clear (in/out)
- Priority assignments present
- Dependencies documented

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| REV-R001 | Error | Requirement missing acceptance criteria |
| REV-R002 | Error | No success metrics defined |
| REV-R003 | Warning | Scope boundaries unclear |
| REV-R004 | Warning | Missing priority assignment |
| REV-R005 | Info | Dependency not documented |

---

### 3. ADR Topic Coverage

Validates Section 7.2 ADR Topics have complete coverage.

**Scope**:
- All 7 mandatory categories present (Infrastructure, Data Architecture, Integration, Security, Observability, AI/ML, Technology Selection)
- Each topic has Status, Alternatives Overview, Decision Drivers
- Selected topics have Cloud Provider Comparison table
- Deferred topics have justification

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| REV-ADR001 | Error | Mandatory ADR category missing |
| REV-ADR002 | Error | Topic missing Alternatives Overview |
| REV-ADR003 | Error | Selected topic missing comparison table |
| REV-ADR004 | Warning | Topic missing Decision Drivers |
| REV-ADR005 | Info | Deferred topic needs justification |

---

### 4. Placeholder Detection

Identifies incomplete content requiring replacement.

**Scope**:
- `[TODO]`, `[TBD]`, `[PLACEHOLDER]` text
- Template dates: `YYYY-MM-DDTHH:MM:SS`, `MM/DD/YYYY`
- Template names: `[Name]`, `[Author]`, `[Reviewer]`
- Empty sections: `<!-- Content here -->`
- Lorem ipsum or sample text

**Auto-Fix**:
- Replace `YYYY-MM-DDTHH:MM:SS` with current datetime
- Replace `[Name]` with document author from metadata
- Remove empty comment placeholders
- Flag `[TODO]`/`[TBD]` for manual completion

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| REV-P001 | Error | [TODO] placeholder found |
| REV-P002 | Error | [TBD] placeholder found |
| REV-P003 | Warning | Template date not replaced |
| REV-P004 | Warning | Template name not replaced |
| REV-P005 | Warning | Empty section content |

---

### 5. Traceability Tags

Validates `@strategy:` and cross-reference tags.

**Scope**:
- `@strategy: DOC-XX` tags reference valid source documents
- Element IDs properly formatted
- Cross-references consistent

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| REV-TR001 | Error | Invalid strategy reference |
| REV-TR002 | Warning | Missing element ID |
| REV-TR003 | Info | Inconsistent cross-reference format |
| REV-TR004 | Warning | Tag format malformed |

---

### 6. Section Completeness

Verifies all required sections have substantive content.

**Scope**:
- Minimum word count per section (configurable)
- Section headers present
- Tables have data rows (not just headers)
- Mermaid diagrams render properly

**Minimum Word Counts** (configurable):

| Section | Minimum Words |
|---------|---------------|
| Executive Summary | 100 |
| Problem Statement | 75 |
| Business Objectives | 150 |
| Functional Requirements | 200 |
| Non-Functional Requirements | 150 |
| ADR Topics | 300 |
| Appendices | 100 |

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| REV-S001 | Error | Required section missing entirely |
| REV-S002 | Warning | Section below minimum word count |
| REV-S003 | Warning | Table has no data rows |
| REV-S004 | Error | Mermaid diagram syntax error |

---

### 7. Strategic Alignment

Validates BRD aligns with business strategy and objectives.

**Scope**:
- Business objectives trace to strategic goals
- Success metrics align with KPIs
- Scope matches project charter
- Stakeholder concerns addressed

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| REV-SA001 | Warning | Business objective not traced to strategy |
| REV-SA002 | Info | Success metric may not align with KPI |
| REV-SA003 | Warning | Scope may exceed project charter |
| REV-SA004 | Flag | Requires stakeholder review |

---

### 8. Naming Compliance

Validates element IDs follow `doc-naming` standards.

**Scope**:
- Element IDs use `BRD.NN.TT.SS` format
- Element type codes valid for BRD (01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 22, 23, 24, 32, 33)
- No legacy patterns (BO-NNN, FR-NNN, etc.)

**Auto-Fix**:
- Convert legacy patterns to unified format
- Suggest correct element type codes

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| REV-N001 | Error | Invalid element ID format |
| REV-N002 | Error | Element type code not valid for BRD |
| REV-N003 | Error | Legacy pattern detected |
| REV-N004 | Warning | Inconsistent ID sequencing |

---

### 9. Upstream Drift Detection

Detects when upstream source documents have been modified after the BRD was created or last updated.

**Purpose**: Identifies stale BRD content that may not reflect current source documentation. When upstream documents (strategy specs, technical specifications, stakeholder inputs) change, the BRD may need updates to maintain alignment.

**Scope**:
- `@ref:` tag targets (technical specifications, strategy documents)
- `@strategy:` tag references
- Traceability section upstream artifact links
- GAP analysis document references
- Any markdown links to `../00_REF/` or source documents

**Detection Methods**:

| Method | Description | Precision |
|--------|-------------|-----------|
| **Timestamp Comparison** | Compares source doc `mtime` vs BRD creation/update date | Medium |
| **Content Hash** | SHA-256 hash of referenced sections | High |
| **Version Tracking** | Checks `version` field in YAML frontmatter | High |

**Algorithm**:

```
1. Extract all upstream references from BRD:
   - @ref: tags → [path, section anchor]
   - @strategy: tags → [document ID]
   - Links to ../00_REF/ → [path]
   - Traceability table upstream artifacts → [path]

2. For each upstream reference:
   a. Resolve path to absolute file path
   b. Check file exists (already covered by Check #1)
   c. Get file modification time (mtime)
   d. Compare mtime > BRD last_updated date
   e. If mtime > BRD date → flag as DRIFT

3. Optional (high-precision mode):
   a. Extract specific section referenced by anchor
   b. Compute SHA-256 hash of section content
   c. Compare to cached hash (stored in .drift_cache.json)
   d. If hash differs → flag as CONTENT_DRIFT
```

**Drift Cache File** (optional):

Location: `docs/01_BRD/{BRD_folder}/.drift_cache.json`

```json
{
  "brd_version": "1.0",
  "brd_updated": "2026-02-10T14:30:00",
  "upstream_hashes": {
    "../../00_REF/foundation/F1_IAM_Technical_Specification.md#3-authentication": "a1b2c3d4...",
    "../../00_REF/foundation/GAP_Foundation_Module_Gap_Analysis.md": "e5f6g7h8..."
  }
}
```

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| REV-D001 | Warning | Upstream document modified after BRD creation |
| REV-D002 | Warning | Referenced section content has changed (hash mismatch) |
| REV-D003 | Info | Upstream document version incremented |
| REV-D004 | Info | New content added to upstream document |
| REV-D005 | Error | Critical upstream document substantially modified (>20% change) |

**Report Output**:

```markdown
## Upstream Drift Analysis

| Upstream Document | BRD Reference | Last Modified | BRD Updated | Days Stale | Severity |
|-------------------|---------------|---------------|-------------|------------|----------|
| F1_IAM_Technical_Specification.md | @ref Section 3 | 2026-02-08T10:15:00 | 2026-02-05T09:00:00 | 3 | Warning |
| GAP_Foundation_Module_Gap_Analysis.md | Traceability | 2026-02-10T14:30:00 | 2026-02-05T09:00:00 | 5 | Warning |

**Recommendation**: Review upstream changes and update BRD if requirements have changed.
```

**Auto-Actions**:
- Update `.drift_cache.json` with current hashes after review
- Add `[DRIFT]` marker to affected @ref tags (optional)
- Generate drift summary in review report

**Configuration**:

| Setting | Default | Description |
|---------|---------|-------------|
| `drift_threshold_days` | 7 | Days before drift becomes Warning |
| `critical_threshold_days` | 30 | Days before drift becomes Error |
| `enable_hash_check` | false | Enable SHA-256 content hashing |
| `tracked_patterns` | `@ref:`, `@strategy:` | Patterns to track for drift |

---

## Review Score Calculation

**Scoring Formula**:

| Category | Weight | Calculation |
|----------|--------|-------------|
| Link Integrity | 10% | (valid_links / total_links) × 10 |
| Requirement Completeness | 18% | (complete_reqs / total_reqs) × 18 |
| ADR Topic Coverage | 18% | (covered_topics / required_topics) × 18 |
| Placeholder Detection | 10% | (no_placeholders ? 10 : 10 - (count × 2)) |
| Traceability Tags | 10% | (valid_tags / total_tags) × 10 |
| Section Completeness | 14% | (complete_sections / total_sections) × 14 |
| Strategic Alignment | 5% | (aligned_objectives / total_objectives) × 5 |
| Naming Compliance | 10% | (valid_ids / total_ids) × 10 |
| Upstream Drift | 5% | (fresh_refs / total_refs) × 5 |

**Total**: Sum of all categories (max 100)

**Thresholds**:
- **PASS**: ≥ 90 (configurable)
- **WARNING**: 80-89
- **FAIL**: < 80

---

## Command Usage

### Basic Usage

```bash
# Review specific BRD
/doc-brd-reviewer BRD-01

# Review BRD by path
/doc-brd-reviewer docs/01_BRD/BRD-01_platform/

# Review all BRDs
/doc-brd-reviewer all
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--min-score` | 90 | Minimum passing review score |
| `--auto-fix` | true | Apply automatic fixes |
| `--no-auto-fix` | false | Disable auto-fix (report only) |
| `--check` | all | Specific checks to run (comma-separated) |
| `--skip` | none | Checks to skip (comma-separated) |
| `--verbose` | false | Detailed output per check |
| `--report` | true | Generate markdown report |

---

## Output Report

Review reports are stored alongside the reviewed document per project standards.

**File Naming**: `BRD-NN.R_review_report_vNNN.md`

**Location**: Same folder as the reviewed BRD document.

### Versioning Rules

1. **First Review**: Creates `BRD-NN.R_review_report_v001.md`
2. **Subsequent Reviews**: Auto-increments version (v002, v003, etc.)
3. **Same-Day Reviews**: Each review gets unique version number

**Version Detection Algorithm**:

```
1. Scan folder for pattern: BRD-NN.R_review_report_v*.md
2. Extract highest version number (N)
3. Create new file with version (N + 1)
```

**Example**:

```
docs/01_BRD/BRD-03_f3_observability/
├── BRD-03.R_review_report_v001.md    # First review
├── BRD-03.R_review_report_v002.md    # After fixes
└── BRD-03.R_review_report_v003.md    # Final review
```

### Delta Reporting

When previous reviews exist, include score comparison:

```markdown
## Score Comparison

| Metric | Previous (v002) | Current (v003) | Delta |
|--------|-----------------|----------------|-------|
| Overall Score | 85 | 94 | +9 |
| Errors | 3 | 0 | -3 |
| Warnings | 5 | 2 | -3 |
```

See `REVIEW_DOCUMENT_STANDARDS.md` for complete requirements.

---

## Integration with doc-brd-autopilot

This skill is invoked during Phase 5 of `doc-brd-autopilot`:

```mermaid
flowchart LR
    A[Phase 4: Validation] --> B[Phase 5: Final Review]
    B --> C{doc-brd-reviewer}
    C --> D[Phase 6: Continue]
```

---

## Related Skills

| Skill | Relationship |
|-------|--------------|
| `doc-naming` | Naming standards for Check #8 |
| `doc-brd-autopilot` | Invokes this skill in Phase 5 |
| `doc-brd-validator` | Structural validation (Phase 4) |
| `doc-brd-fixer` | Applies fixes based on review findings |
| `doc-brd` | BRD creation rules |
| `doc-prd-autopilot` | Downstream consumer |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.3 | 2026-02-10 | Added Check #9: Upstream Drift Detection - detects when source documents modified after BRD creation; REV-D001-D005 error codes; drift cache support; configurable thresholds |
| 1.2 | 2026-02-10 | Added element type code 33 (Benefit Statement) to valid BRD codes per doc-naming v1.5 |
| 1.1 | 2026-02-10 | Added review versioning support (_vNNN pattern); Delta reporting for score comparison |
| 1.0 | 2026-02-10 | Initial skill creation with 8 review checks; ADR topic coverage validation; Strategic alignment check |
