---
title: "DSPEC MVP Validation Rules"
tags:
  - validation-rules
  - layer-9-artifact
  - dspec-subtype
custom_fields:
  document_type: rules
  artifact_type: DSPEC
  layer: 9
  subtype_code: 51
---

# DSPEC MVP Validation Rules

## Purpose

Validation checklist for Document Specification (DSPEC) documents after creation.

## Validation Checklist

### Structure Validation

- [ ] File is valid YAML
- [ ] File name matches `DSPEC-NN_name.yaml` format
- [ ] All required sections present
- [ ] `instance_document_type: dspec-document`
- [ ] `deliverable_type: document`

### Metadata Validation

- [ ] Version is semantic version format (X.Y.Z)
- [ ] Status is valid (draft, review, approved, published)
- [ ] Dates are YYYY-MM-DD format
- [ ] At least one author specified
- [ ] `ctr_required: false` (or true if API documentation)

### Traceability Validation

- [ ] REQ reference present (required)
- [ ] CTR reference present (optional - for API docs)
- [ ] All cumulative tags complete (BRD through REQ)
- [ ] Downstream artifacts defined (TASKS, docs paths)
- [ ] Element IDs use DSPEC.NN.TT.SS format

### Document Specification Validation

- [ ] document_type is valid (user_guide, api_doc, compliance_doc, training_material, reference)
- [ ] format is valid (markdown, pdf, html, docx)
- [ ] audience is valid (end_users, developers, auditors, operators)
- [ ] content_outline has at least one section
- [ ] Each section has id, section name, purpose, content_requirements

### Style Requirements Validation

- [ ] tone specified (formal, informal, technical)
- [ ] reading_level specified (basic, intermediate, advanced)
- [ ] formatting standards defined

### Review Criteria Validation

- [ ] accuracy criteria defined
- [ ] completeness criteria defined
- [ ] clarity criteria defined

### Verification Validation

- [ ] review_workflow defined with stages
- [ ] testing requirements specified

### Implementation Validation

- [ ] output_location specified
- [ ] file_naming convention defined
- [ ] publication_channel specified

## DOC-Ready Score Calculation

| Criterion | Weight | Check |
|-----------|--------|-------|
| Content Outline Completeness | 25% | All sections with purpose and requirements |
| Audience Clarity | 20% | Target audience and reading level defined |
| Format Specification | 15% | Output format and style defined |
| Review Criteria | 20% | Accuracy, completeness, clarity standards |
| Traceability | 20% | All upstream/downstream links |

**Target**: >= 85%

## Error Codes

| Code | Severity | Message |
|------|----------|---------|
| DSPEC-E001 | Error | File is not valid YAML |
| DSPEC-E002 | Error | Missing required field |
| DSPEC-E003 | Error | deliverable_type must be 'document' |
| DSPEC-E004 | Error | Missing REQ reference |
| DSPEC-E005 | Error | Missing document_type specification |
| DSPEC-E006 | Error | Missing content_outline |
| DSPEC-E007 | Error | Missing output_location |
| DSPEC-W001 | Warning | Missing reading_level |
| DSPEC-W002 | Warning | Missing clarity criteria |
| DSPEC-W003 | Warning | Missing publication_channel |
| DSPEC-I001 | Info | CTR reference not required for DSPEC |

## Scoring Example

```yaml
# DOC-Ready Score Calculation Example
content_outline_completeness: 25%  # All 3 sections defined with requirements
audience_clarity: 20%              # end_users, intermediate level
format_specification: 15%          # markdown, formal tone
review_criteria: 20%               # All three criteria defined
traceability: 20%                  # REQ and downstream links present

total_score: 100%  # [PASS] >= 85%
```

---

**Rules Version**: 1.0
**Last Updated**: 2026-03-01

---

## DEPRECATED: Template+Schema migration (2026-03-24)

This file is deprecated and retained for backward compatibility only.

Active references for MCP and framework tooling must use:
- `*-MVP-TEMPLATE.*`
- `*_MVP_SCHEMA.yaml`

Do not add new dependencies on this file.
