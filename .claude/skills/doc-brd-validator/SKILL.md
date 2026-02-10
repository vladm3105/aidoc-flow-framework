---
name: doc-brd-validator
description: Validate Business Requirements Documents (BRD) against Layer 1 MVP schema standards
tags:
  - sdd-workflow
  - layer-1-artifact
  - validation
  - shared-architecture
custom_fields:
  layer: 1
  artifact_type: BRD
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  skill_category: quality-assurance
  upstream_artifacts: []
  downstream_artifacts: [PRD]
  version: "2.1"
  last_updated: "2026-02-10T15:00:00"
---

# doc-brd-validator

Validate Business Requirements Documents (BRD) against Layer 1 MVP schema standards.

## Purpose

Validates BRD documents for:

- YAML frontmatter metadata compliance
- Section structure (18 sections for comprehensive template)
- Document Control completeness
- Traceability tag format and presence
- PRD-Ready scoring
- File naming conventions
- Architecture Decision Requirements completeness

## Activation

Invoke when:

- User requests validation of BRD documents
- After creating/modifying BRD artifacts
- Before generating downstream artifacts (PRD)
- As part of quality gate checks

## Schema Reference

| Item | Value |
|------|-------|
| Schema | `ai_dev_flow/01_BRD/BRD_MVP_SCHEMA.yaml` |
| Template | `ai_dev_flow/01_BRD/BRD-MVP-TEMPLATE.md` |
| Creation Rules | `ai_dev_flow/01_BRD/BRD_CREATION_RULES.md` |
| Validation Rules | `ai_dev_flow/01_BRD/BRD_VALIDATION_RULES.md` |
| Layer | 1 |
| Artifact Type | BRD |

## Validation Checklist

### 1. Metadata Validation

```yaml
Required custom_fields:
  document_type: ["brd", "template"]
  artifact_type: "BRD"
  layer: 1
  architecture_approaches: [array format]
  priority: ["primary", "shared", "fallback"]
  development_status: ["active", "draft", "deprecated", "reference"]

Required tags:
  - brd (or brd-template)
  - layer-1-artifact

Forbidden tag patterns:
  - "^business-requirements$"
  - "^brd-\\d{3}$"
```

### 2. Structure Validation

**Required Sections (18 Total)**:

| Section | Title | Required |
|---------|-------|----------|
| 0 | Document Control | MANDATORY |
| 1 | Executive Summary | MANDATORY |
| 2 | Business Context | MANDATORY |
| 3 | Stakeholder Analysis | MANDATORY |
| 4 | Business Requirements | MANDATORY |
| 5 | Success Criteria | MANDATORY |
| 6 | Constraints and Assumptions | MANDATORY |
| 7 | Architecture Decision Requirements | MANDATORY |
| 8 | Risk Assessment | MANDATORY |
| 9 | Traceability | MANDATORY |
| 10-18 | Additional sections | Per template |

**Section Format**: `## N. Title` (numbered H2 headings)

### 3. Document Control Required Fields

| Field | Description | Required |
|-------|-------------|----------|
| Project Name | Project identifier | MANDATORY |
| Document Version | Semantic versioning (X.Y.Z) | MANDATORY |
| Date Created | YYYY-MM-DD format | MANDATORY |
| Last Updated | YYYY-MM-DD format | MANDATORY |
| Document Owner | Owner name | MANDATORY |
| Prepared By | Author name | MANDATORY |
| Status | Draft/In Review/Approved/Superseded | MANDATORY |
| PRD-Ready Score | `XX/100 (Target: ≥90)` | MANDATORY |

### 4. Content Validation

**Business Objectives Format** (Section 3):
- Pattern: `BRD.NN.23.SS` (unified 4-segment format)
- Required fields: ID, Objective, Priority, Success Criteria, Measurement Method

**Business Requirements Format** (Section 4):
- Pattern: `BRD.NN.01.SS` (unified 4-segment format)
- Required fields: ID, Requirement, Type, Priority, Source, Rationale
- Priority values: Critical (P1), High (P2), Medium (P3), Low (P4)
- Type values: Functional, Non-Functional, Regulatory, Operational

**PRD-Ready Score**:
- Minimum threshold: 90%
- Components: Business objectives, requirements completeness, success metrics, constraints, stakeholder analysis, risk assessment, traceability, ADR topics completeness

### 5. Architecture Decision Requirements (Section 7.2) - MANDATORY

**7 Mandatory ADR Topic Categories**:

| # | Category | Element ID | Status Values |
|---|----------|------------|---------------|
| 1 | Infrastructure | BRD.NN.32.01 | Selected/Pending/N/A |
| 2 | Data Architecture | BRD.NN.32.02 | Selected/Pending/N/A |
| 3 | Integration | BRD.NN.32.03 | Selected/Pending/N/A |
| 4 | Security | BRD.NN.32.04 | Selected/Pending/N/A |
| 5 | Observability | BRD.NN.32.05 | Selected/Pending/N/A |
| 6 | AI/ML | BRD.NN.32.06 | Selected/Pending/N/A |
| 7 | Technology Selection | BRD.NN.32.07 | Selected/Pending/N/A |

**Element Type Code**: `32` = Architecture Topic (see `doc-naming` skill)

**Required Fields Per Topic (Status=Selected)**:
- Status (Selected/Pending/N/A)
- Business Driver
- Business Constraints
- Alternatives Overview table (Option | Function | Est. Monthly Cost | Selection Rationale)
- Cloud Provider Comparison table (Criterion | GCP | Azure | AWS)
- Recommended Selection
- PRD Requirements

**Required Fields Per Topic (Status=Pending)**:
- Status with reason
- Business Driver
- Business Constraints
- PRD Requirements

**Required Fields Per Topic (Status=N/A)**:
- Status with explicit reason
- PRD Requirements (can be "None for current scope")

### 6. Naming Compliance (doc-naming integration)

**Element ID Validation**:
- Format: `BRD.NN.TT.SS` (4-segment unified format)
- Valid element type codes for BRD: 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 22, 23, 24, 32, 33
- No legacy patterns (BO-XXX, FR-XXX, AC-XXX, BC-XXX)

**File Naming Convention**:
- Pattern: `BRD-NN_{descriptive_slug}.md`
- `NN`: 2+ digit number (01, 02, ... 99, 100)
- `descriptive_slug`: lowercase with underscores

**Sectioned BRD Pattern**: `docs/01_BRD/BRD-NN_{slug}/BRD-NN.S_{section}.md`

### 7. Traceability Validation

**Layer 1 Tags**:
- No upstream artifacts required (BRD is the entry point)
- Tag count: 0

**Downstream Expected**:
- PRD documents (Layer 2)
- EARS statements (Layer 3)
- ADR documents (Layer 5)

**Same-Type References**:
- `@related-brd: BRD-NN`
- `@supersedes-brd: BRD-NN`
- `@depends-brd: BRD-NN`

## Error Codes

| Code | Severity | Description |
|------|----------|-------------|
| BRD-E001 | ERROR | Missing required tag 'brd' |
| BRD-E002 | ERROR | Missing required tag 'layer-1-artifact' |
| BRD-E003 | ERROR | Invalid document_type value |
| BRD-E004 | ERROR | Invalid architecture_approaches format (must be array) |
| BRD-E005 | ERROR | Forbidden tag pattern detected |
| BRD-E006 | ERROR | Missing required section |
| BRD-E007 | ERROR | Multiple H1 headings detected |
| BRD-E008 | ERROR | Section numbering not sequential |
| BRD-E009 | ERROR | Document Control missing required fields |
| BRD-E010 | ERROR | Missing Business Objectives (Section 3) |
| BRD-E011 | ERROR | Missing Business Requirements (Section 4) |
| BRD-E012 | ERROR | Missing Traceability (Section 9) |
| BRD-E013 | ERROR | Missing Section 7.2 (Architecture Decision Requirements) |
| BRD-E014 | ERROR | Missing mandatory ADR topic category |
| BRD-E015 | ERROR | ADR topic missing required Status field |
| BRD-E016 | ERROR | Selected ADR topic missing Alternatives Overview table |
| BRD-E017 | ERROR | Selected ADR topic missing Cloud Provider Comparison table |
| BRD-E018 | ERROR | N/A ADR topic missing explicit reason |
| BRD-E019 | ERROR | Invalid element ID format (not BRD.NN.TT.SS) |
| BRD-E020 | ERROR | Element type code not valid for BRD (see doc-naming) |
| BRD-E021 | ERROR | Deprecated ID pattern used (BO-XXX, FR-XXX, etc.) |
| BRD-W001 | WARNING | Objectives not using BRD.NN.23.SS format |
| BRD-W002 | WARNING | Requirements not using BRD.NN.01.SS format |
| BRD-W003 | WARNING | Missing Success Metrics (Section 5) |
| BRD-W004 | WARNING | PRD-Ready Score below 90% |
| BRD-W005 | WARNING | Missing Stakeholder Analysis |
| BRD-W006 | WARNING | File name does not match format BRD-NN_{slug}.md |
| BRD-W007 | WARNING | ADR topic missing cost estimates in Alternatives Overview |
| BRD-W008 | WARNING | ADR topic missing PRD Requirements field |
| BRD-W009 | WARNING | Missing Document Revision History table |
| BRD-I001 | INFO | Consider adding regulatory compliance requirements |
| BRD-I002 | INFO | Consider adding market analysis context |
| BRD-I003 | INFO | Consider completing Pending ADR topics before PRD creation |

## Validation Commands

```bash
# Validate single BRD document
python ai_dev_flow/scripts/validate_brd.py docs/01_BRD/BRD-01_example.md

# Validate all BRD documents in directory
python ai_dev_flow/scripts/validate_brd.py docs/01_BRD/

# Validate with verbose output
python ai_dev_flow/scripts/validate_brd.py docs/01_BRD/ --verbose

# Validate with auto-fix
python ai_dev_flow/scripts/validate_brd.py docs/01_BRD/ --auto-fix

# Cross-document validation
python ai_dev_flow/scripts/validate_cross_document.py --document docs/01_BRD/BRD-01.md --auto-fix
```

## Validation Workflow

1. Parse YAML frontmatter
2. Check required metadata fields (document_type, artifact_type, layer)
3. Validate tag taxonomy (brd, layer-1-artifact)
4. Verify section structure (18 sections)
5. Validate Document Control table completeness
6. Check business objectives format (BRD.NN.23.SS)
7. Check business requirements format (BRD.NN.01.SS)
8. Validate Section 7.2 ADR Topics:
   - Verify all 7 mandatory categories present
   - Check Status field (Selected/Pending/N/A)
   - For Selected: Verify Alternatives Overview table, Cloud Provider Comparison table
   - For N/A: Verify explicit reason provided
   - Validate element ID format (BRD.NN.32.SS)
9. Calculate PRD-Ready Score (includes ADR completeness)
10. Verify file naming convention
11. Check element ID format compliance (per doc-naming)
12. Detect deprecated patterns
13. Generate validation report

## Auto-Fix Actions

| Issue | Auto-Fix Action |
|-------|-----------------|
| Invalid element ID format | Convert to BRD.NN.TT.SS format |
| Missing traceability section | Insert from template |
| Missing Document Control fields | Add placeholder fields |
| Deprecated ID patterns | Convert to unified format |
| Missing PRD-Ready Score | Calculate and insert |

## Integration

- **Invoked by**: doc-flow, doc-brd (post-creation), doc-prd-autopilot
- **Feeds into**: trace-check (cross-document validation)
- **Reports to**: quality-advisor

## Output Format

```
BRD Validation Report
=====================
Document: BRD-01_platform_architecture.md
Status: PASS/FAIL

PRD-Ready Score: 92% (Target: ≥90%) ✓

Errors: 0
Warnings: 2
Info: 1

[BRD-W006] WARNING: File name should use lowercase slug
[BRD-W009] WARNING: Missing Document Revision History table
[BRD-I001] INFO: Consider adding regulatory compliance requirements
```

## Related Resources

- **Naming Standards**: `.claude/skills/doc-naming/SKILL.md` (element IDs, element type codes)
- **BRD Skill**: `.claude/skills/doc-brd/SKILL.md`
- **BRD Template**: `ai_dev_flow/01_BRD/BRD-MVP-TEMPLATE.md`
- **BRD Schema**: `ai_dev_flow/01_BRD/BRD_MVP_SCHEMA.yaml`
- **Creation Rules**: `ai_dev_flow/01_BRD/BRD_CREATION_RULES.md`
- **Validation Rules**: `ai_dev_flow/01_BRD/BRD_VALIDATION_RULES.md`
- **Shared Standards**: `.claude/skills/doc-flow/SHARED_CONTENT.md`

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.1 | 2026-02-10 | Added element type code 33 (Benefit Statement) to valid BRD codes per doc-naming v1.5 |
| 2.0 | 2026-02-08 | Complete rewrite: Added YAML frontmatter, doc-naming integration (BRD-E019/E020/E021), updated section structure to 18 sections, fixed file paths with numbered prefixes, added PRD-Ready score validation |
| 1.0 | 2025-01-06 | Initial version (outdated 12-section structure) |
