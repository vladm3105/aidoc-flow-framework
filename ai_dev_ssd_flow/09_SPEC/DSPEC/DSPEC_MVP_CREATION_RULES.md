---
title: "DSPEC MVP Creation Rules"
tags:
  - creation-rules
  - layer-9-artifact
  - dspec-subtype
custom_fields:
  document_type: rules
  artifact_type: DSPEC
  layer: 9
  subtype_code: 51
---

# DSPEC MVP Creation Rules

## Purpose

Guidelines for creating Document Specification (DSPEC) documents - specifications for documentation artifacts including user guides, API documentation, compliance documents, and training materials.

## When to Create DSPEC

Create a DSPEC when:
- REQ document has `deliverable_type: document`
- Requirement results in documentation output
- Documentation requires structured specification
- Multiple reviewers or stakeholders involved

## Prerequisites

Before creating DSPEC:

1. **REQ Document**: Atomic requirement with `deliverable_type: document`
2. **Source Materials**: Technical specifications, design docs, or API specs to document
3. **Audience Definition**: Clear understanding of target readers
4. **ADR Document**: Architecture decisions for documentation tooling (optional)

## File Naming

```
DSPEC-NN_document_name.yaml
```

- `NN`: Sequential number (01, 02, 03...)
- `document_name`: Snake_case, descriptive name

## Required Sections

| Section | Required | Description |
|---------|----------|-------------|
| metadata | Yes | Document control with `deliverable_type: document` |
| traceability | Yes | Must include REQ reference |
| document_specification | Yes | Document type, format, audience, content outline |
| style_requirements | Yes | Tone, voice, reading level |
| review_criteria | Yes | Accuracy, completeness, clarity standards |
| dependencies | No | Source materials, SMEs |
| verification | Yes | Review workflow, testing |
| implementation | Yes | Output location, publication channel |

## Element ID Format

```
DSPEC.{DOC}.{TYPE}.{SEQ}
```

| Code | Type | Example |
|------|------|---------|
| 55 | section | DSPEC.01.55.01 |
| 56 | topic | DSPEC.01.56.01 |
| 57 | example | DSPEC.01.57.01 |
| 58 | reference | DSPEC.01.58.01 |

## CTR Requirement

DSPEC does **not require** CTR (Contract) reference:
- CTR is optional, include for API documentation
- If documenting an API, reference the relevant CTR
- For user guides and training materials, CTR is typically not needed

## Document Types

| Type | Description | Typical Audience |
|------|-------------|------------------|
| user_guide | End-user instructions | end_users |
| api_doc | API reference documentation | developers |
| compliance_doc | Regulatory/audit documentation | auditors |
| training_material | Learning and onboarding content | end_users, operators |
| reference | Technical reference material | developers |

## Content Outline Requirements

Each section in content_outline must specify:

```yaml
content_outline:
  - id: "DSPEC.NN.55.SS"
    section: "[Section Name]"
    purpose: "[Why this section exists]"
    content_requirements: "[What must be included]"
```

## Quality Gate

**DOC-Ready Score Target**: >= 85%

| Criterion | Weight |
|-----------|--------|
| Content Outline Completeness | 25% |
| Audience Clarity | 20% |
| Format Specification | 15% |
| Review Criteria | 20% |
| Traceability | 20% |

## Validation Checklist

- [ ] `deliverable_type: document` in metadata
- [ ] REQ reference in traceability
- [ ] Document type specified (user_guide, api_doc, etc.)
- [ ] Output format specified (markdown, pdf, etc.)
- [ ] Target audience specified (end_users, developers, etc.)
- [ ] Content outline has at least one section
- [ ] Style requirements defined (tone, reading level)
- [ ] Review criteria defined (accuracy, completeness, clarity)
- [ ] Output location specified in implementation

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
