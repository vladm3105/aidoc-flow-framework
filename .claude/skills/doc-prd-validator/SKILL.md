---
name: doc-prd-validator
description: Validate Product Requirements Documents (PRD) against Layer 2 MVP schema standards
tags:
  - sdd-workflow
  - layer-2-artifact
  - validation
  - shared-architecture
custom_fields:
  layer: 2
  artifact_type: PRD
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  skill_category: quality-assurance
  upstream_artifacts: [BRD]
  downstream_artifacts: [EARS, BDD, ADR]
  version: "2.0"
  last_updated: "2026-02-08"
---

# doc-prd-validator

Validate Product Requirements Documents (PRD) against Layer 2 MVP schema standards.

## Purpose

Validates PRD documents for:

- YAML frontmatter metadata compliance
- Section structure (17 sections for MVP template)
- Document Control completeness
- Traceability tag format and presence
- Dual scoring requirements (SYS-Ready + EARS-Ready)
- File naming conventions

## Activation

Invoke when:

- User requests validation of PRD documents
- After creating/modifying PRD artifacts
- Before generating downstream artifacts (EARS, BDD, ADR)
- As part of quality gate checks

## Schema Reference

| Item | Value |
|------|-------|
| Schema | `ai_dev_flow/02_PRD/PRD_MVP_SCHEMA.yaml` |
| Template | `ai_dev_flow/02_PRD/PRD-MVP-TEMPLATE.md` |
| Creation Rules | `ai_dev_flow/02_PRD/PRD_MVP_CREATION_RULES.md` |
| Validation Rules | `ai_dev_flow/02_PRD/PRD_MVP_VALIDATION_RULES.md` |
| Layer | 2 |
| Artifact Type | PRD |

## Validation Checklist

### 1. Metadata Validation

```yaml
Required custom_fields:
  document_type: ["prd", "template"]
  artifact_type: "PRD"
  layer: 2
  architecture_approaches: [array format]
  priority: ["primary", "shared", "fallback"]
  development_status: ["active", "draft", "deprecated", "reference"]

Required tags:
  - prd (or prd-template)
  - layer-2-artifact

Forbidden tag patterns:
  - "^product-requirements$"
  - "^product-prd$"
  - "^feature-prd$"
```

### 2. Structure Validation (MVP Template - 17 Sections)

**Required Sections (MVP Template)**:

| Section | Title | Required |
|---------|-------|----------|
| 1 | Document Control | MANDATORY |
| 2 | Executive Summary | MANDATORY |
| 3 | Problem Statement | MANDATORY |
| 4 | Target Audience & User Personas | MANDATORY |
| 5 | Success Metrics (KPIs) | MANDATORY |
| 6 | Scope & Requirements | MANDATORY |
| 7 | User Stories & User Roles | MANDATORY |
| 8 | Functional Requirements | MANDATORY |
| 9 | Quality Attributes | MANDATORY |
| 10 | Architecture Requirements | MANDATORY |
| 11 | Constraints & Assumptions | MANDATORY |
| 12 | Risk Assessment | MANDATORY |
| 13 | Implementation Approach | MANDATORY |
| 14 | Acceptance Criteria | MANDATORY |
| 15 | Budget & Resources | MANDATORY |
| 16 | Traceability | MANDATORY |
| 17 | Glossary | Optional |
| 18 | Appendix A: Future Roadmap | Optional |
| 19 | Migration to Full PRD Template | Optional |

**Section Format**: `## N. Title` (numbered H2 headings)

### 3. Document Control Required Fields

| Field | Description | Required |
|-------|-------------|----------|
| Status | Draft/Review/Approved/Implemented | MANDATORY |
| Version | Semantic versioning (X.Y.Z) | MANDATORY |
| Date Created | YYYY-MM-DD format | MANDATORY |
| Last Updated | YYYY-MM-DD format | MANDATORY |
| Author | Product Manager/Owner Name | MANDATORY |
| Reviewer | Technical reviewer name | MANDATORY |
| Approver | Final approver name | MANDATORY |
| BRD Reference | `@brd: BRD.NN.TT.SS` format | MANDATORY |
| SYS-Ready Score | `XX/100 (Target: ≥85 for MVP)` | MANDATORY |
| EARS-Ready Score | `XX/100 (Target: ≥85 for MVP)` | MANDATORY |

### 4. Dual Scoring Requirements

| Score | MVP Threshold | Full Template Threshold |
|-------|---------------|------------------------|
| SYS-Ready Score | ≥85% | ≥90% |
| EARS-Ready Score | ≥85% | ≥90% |

Both scores must be present and meet thresholds for downstream artifact generation.

### 5. File Naming Convention

**Pattern**: `PRD-NN_{descriptive_slug}.md`

- `NN`: 2+ digit number (01, 02, ... 99, 100)
- `descriptive_slug`: lowercase with underscores

**Examples**:

- `PRD-01_user_authentication.md` (correct)
- `PRD-001_feature.md` (incorrect - use 2 digits minimum, expand only as needed)
- `PRD-1_feature.md` (incorrect - minimum 2 digits)

**Sectioned PRD Pattern**: `docs/PRD/PRD-NN_{slug}/PRD-NN.S_{section}.md`

### 6. Traceability Validation

**Layer 2 Cumulative Tags (Required)**:

```markdown
@brd: BRD.NN.TT.SS
```

**Unified Element ID Format**:

| Element Type | Code | Example |
|--------------|------|---------|
| Functional Requirement | 01 | PRD.02.01.01 |
| Quality Attribute | 02 | PRD.02.02.01 |
| Constraint | 03 | PRD.02.03.01 |
| Assumption | 04 | PRD.02.04.01 |
| Dependency | 05 | PRD.02.05.01 |
| Acceptance Criteria | 06 | PRD.02.06.01 |
| Risk | 07 | PRD.02.07.01 |
| Metric | 08 | PRD.02.08.01 |
| User Story | 09 | PRD.02.09.01 |
| Use Case | 11 | PRD.02.11.01 |
| Feature Item | 22 | PRD.02.22.01 |
| Stakeholder Need | 24 | PRD.02.24.01 |

**Deprecated Patterns (Do NOT use)**:

- `US-NNN` → Use `PRD.NN.09.SS`
- `FR-NNN` → Use `PRD.NN.01.SS`
- `AC-NNN` → Use `PRD.NN.06.SS`
- `F-NNN` → Use `PRD.NN.22.SS`

**Same-Type References**:

- `@related-prd: PRD-NN`
- `@depends-prd: PRD-NN`

**Downstream Expected**:

- EARS statements (Layer 3)
- BDD scenarios (Layer 4)
- ADR documents (Layer 5)

### 7. Content Validation

**User Story Format** (Section 7):

- Pattern: `PRD.NN.09.SS`
- Format: "As a [role], I want [capability] so that [benefit]"
- Must include layer separation scope note

**Functional Requirement Format** (Section 8):

- Pattern: `PRD.NN.01.SS`
- Required fields: ID, Requirement, Priority, Acceptance Criteria
- Priority values: P1 (Must Have), P2 (Should Have), P3 (Could Have), P4 (Won't Have)

## Error Codes

| Code | Severity | Description |
|------|----------|-------------|
| PRD-E001 | ERROR | Missing required tag 'prd' |
| PRD-E002 | ERROR | Missing required tag 'layer-2-artifact' |
| PRD-E003 | ERROR | Invalid document_type value |
| PRD-E004 | ERROR | Invalid architecture_approaches format (must be array) |
| PRD-E005 | ERROR | Forbidden tag pattern detected |
| PRD-E006 | ERROR | Missing required section |
| PRD-E007 | ERROR | Multiple H1 headings detected |
| PRD-E008 | ERROR | Section numbering not sequential |
| PRD-E009 | ERROR | Document Control missing required fields |
| PRD-E010 | ERROR | Missing User Stories (Section 7) |
| PRD-E011 | ERROR | Missing Functional Requirements (Section 8) |
| PRD-E012 | ERROR | Missing Traceability (Section 16) |
| PRD-E013 | ERROR | Missing upstream @brd tag |
| PRD-E014 | ERROR | Invalid element ID format (not PRD.NN.TT.SS) |
| PRD-E015 | ERROR | SYS-Ready Score missing or below threshold |
| PRD-E016 | ERROR | EARS-Ready Score missing or below threshold |
| PRD-E017 | ERROR | Deprecated ID pattern used (US-NNN, FR-NNN, etc.) |
| PRD-E018 | ERROR | Invalid threshold tag format (must be @threshold: PRD.NN.key) |
| PRD-E019 | ERROR | Element type code not valid for PRD (see doc-naming) |
| PRD-W001 | WARNING | File name does not match format PRD-NN_{slug}.md |
| PRD-W002 | WARNING | Missing optional section (Glossary, Appendix) |
| PRD-W003 | WARNING | Score below recommended threshold but above minimum |
| PRD-W004 | WARNING | Missing Document Revision History table |
| PRD-W005 | WARNING | Architecture Decision Requirements reference ADR numbers |
| PRD-I001 | INFO | Consider adding success metrics with quantified targets |
| PRD-I002 | INFO | Consider adding competitive analysis |

## Validation Commands

```bash
# Validate single PRD document
python ai_dev_flow/scripts/validate_prd.py docs/PRD/PRD-01_example.md

# Validate all PRD documents in directory
python ai_dev_flow/scripts/validate_prd.py docs/PRD/

# Validate with verbose output
python ai_dev_flow/scripts/validate_prd.py docs/PRD/ --verbose

# Validate with auto-fix
python ai_dev_flow/scripts/validate_prd.py docs/PRD/ --auto-fix

# Cross-document validation
python ai_dev_flow/scripts/validate_cross_document.py --document docs/PRD/PRD-01.md --auto-fix

# Layer-wide validation
python ai_dev_flow/scripts/validate_cross_document.py --layer PRD --auto-fix
```

## Validation Workflow

1. Parse YAML frontmatter
2. Check required metadata fields (document_type, artifact_type, layer)
3. Validate tag taxonomy (prd, layer-2-artifact)
4. Verify section structure (1-17 for MVP)
5. Validate Document Control table completeness
6. Check dual scoring (SYS-Ready + EARS-Ready ≥85%)
7. Validate upstream @brd reference format
8. Check element ID format (PRD.NN.TT.SS)
9. Detect deprecated patterns (US-NNN, FR-NNN)
10. Verify file naming convention
11. Generate validation report

## Auto-Fix Actions

| Issue | Auto-Fix Action |
|-------|-----------------|
| Missing cumulative @brd tag | Add with upstream document reference |
| Invalid element ID format | Convert to PRD.NN.TT.SS format |
| Missing traceability section | Insert from template |
| Missing Document Control fields | Add placeholder fields |
| Deprecated ID patterns | Convert to unified format |

## Integration

- **Invoked by**: doc-flow, doc-prd (post-creation), doc-prd-autopilot
- **Feeds into**: trace-check (cross-document validation)
- **Reports to**: quality-advisor

## Output Format

```
PRD Validation Report
=====================
Document: PRD-01_user_authentication.md
Status: PASS/FAIL

Scores:
  SYS-Ready:  92% (Target: ≥85%) ✓
  EARS-Ready: 88% (Target: ≥85%) ✓

Errors: 0
Warnings: 2
Info: 1

[PRD-W001] WARNING: File name should use lowercase slug
[PRD-W004] WARNING: Missing Document Revision History table
[PRD-I001] INFO: Consider adding quantified success metrics
```

## Related Resources

- **Naming Standards**: `.claude/skills/doc-naming/SKILL.md` (element IDs, threshold tags)
- **PRD Skill**: `.claude/skills/doc-prd/SKILL.md`
- **PRD Template**: `ai_dev_flow/02_PRD/PRD-MVP-TEMPLATE.md`
- **PRD Schema**: `ai_dev_flow/02_PRD/PRD_MVP_SCHEMA.yaml`
- **Creation Rules**: `ai_dev_flow/02_PRD/PRD_MVP_CREATION_RULES.md`
- **Validation Rules**: `ai_dev_flow/02_PRD/PRD_MVP_VALIDATION_RULES.md`
- **Shared Standards**: `.claude/skills/doc-flow/SHARED_CONTENT.md`

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.1 | 2026-02-08 | Added doc-naming integration: PRD-E018 (threshold format), PRD-E019 (element type codes) |
| 2.0 | 2026-02-08 | Complete rewrite: Updated to MVP template (17 sections), unified element IDs, correct paths |
| 1.0 | 2025-01-06 | Initial version (outdated 13-section structure) |
