---
title: "DSPEC-MVP-TEMPLATE: Document Specification (MVP)"
tags:
  - dspec-template
  - mvp-template
  - layer-9-artifact
  - shared-architecture
  - document-template
custom_fields:
  document_type: template
  instance_document_type: dspec-document
  deliverable_type: document
  artifact_type: DSPEC
  layer: 9
  subtype_code: 51
  parent_type: SPEC
  ctr_required: false
  readiness_score: DOC-Ready
  schema_reference: "DSPEC_MVP_SCHEMA.yaml"
  schema_version: "1.0"
---

> **Dual-Format Note**:
>
> This MD template is the **primary source** for human workflow.
> - **For Autopilot**: See `DSPEC-MVP-TEMPLATE.yaml` (YAML template)
> - **Shared Validation**: Both formats are validated by `DSPEC_MVP_SCHEMA.yaml`
> - **Parent**: SPEC (orchestrator) - routes here when `deliverable_type == 'document'`

---

> **Document Authority**: This is the STANDARD for DSPEC (Document Specification) structure.
> Schema: `DSPEC_MVP_SCHEMA.yaml v1.0` | Rules: `DSPEC_MVP_CREATION_RULES.md`, `DSPEC_MVP_VALIDATION_RULES.md`

<!--
AI_CONTEXT_START
Role: AI Technical Writer / Documentation Architect
Objective: Create document specification for documentation artifacts.
Constraints:
- One DSPEC per documentation deliverable.
- Define WHAT content to include and HOW to structure it.
- CTR is OPTIONAL - reference only if API documentation.
- DOC-Ready threshold: >= 85%.
- Include content outline with section purposes.
- Define audience and reading level.
- Specify review criteria for accuracy, completeness, clarity.
- Element IDs use codes 55-58 for sections, topics, examples, references.
AI_CONTEXT_END
-->

**MVP Template** - Document Specification for documentation artifacts.

References: Schema `DSPEC_MVP_SCHEMA.yaml` | Rules `DSPEC_MVP_CREATION_RULES.md`, `DSPEC_MVP_VALIDATION_RULES.md`

# DSPEC-NN: [Document Name] Document Specification

**Deliverable Type**: `document`
**CTR Required**: No (optional - include for API documentation)

## 1. Document Control

| Item | Details |
|------|---------|
| **Status** | Draft / Review / Approved / Published |
| **Version** | 1.0.0 |
| **Date Created** | YYYY-MM-DDTHH:MM:SS |
| **Last Updated** | YYYY-MM-DDTHH:MM:SS |
| **Author** | [Author name] |
| **Document Title** | [Title of documentation artifact] |
| **Deliverable Type** | document |
| **CTR Reference** | @ctr: CTR-NN (if applicable) |
| **DOC-Ready Score** | [XX]% (Target: >= 85%) |

---

## 2. Traceability

### 2.1 Upstream Sources

| Type | ID | Title | Relevant Sections |
|------|-----|-------|-------------------|
| REQ | REQ-NN | [Requirements title] | [Sections] |
| ADR | ADR-NN | [Architecture decision] | [Sections] |

### 2.2 Cumulative Tags

```yaml
brd: "@brd: BRD.NN.EE.SS"
prd: "@prd: PRD.NN.EE.SS"
ears: "@ears: EARS.NN.EE.SS"
bdd: "@bdd: BDD.NN.EE.SS"
adr: "@adr: ADR-NN"
sys: "@sys: SYS.NN.EE.SS"
req: "@req: REQ.NN.EE.SS"
ctr: "@ctr: CTR-NN"  # Optional for DSPEC
```

### 2.3 Downstream Consumers

| Type | ID | Purpose |
|------|-----|---------|
| TASKS | TASKS-NN | Documentation tasks |
| Docs | docs/[category]/ | Documentation output |

---

## 3. Document Specification

### 3.1 Document Type and Format

| Property | Value |
|----------|-------|
| Document Type | [user_guide / api_doc / compliance_doc / training_material / reference] |
| Output Format | [markdown / pdf / html / docx] |
| Target Audience | [end_users / developers / auditors / operators] |

### 3.2 Content Outline

| ID | Section | Purpose | Content Requirements |
|----|---------|---------|---------------------|
| DSPEC.NN.55.01 | [Section Name] | [Section purpose] | [What must be included] |
| DSPEC.NN.55.02 | [Section Name] | [Section purpose] | [What must be included] |
| DSPEC.NN.55.03 | [Section Name] | [Section purpose] | [What must be included] |

### 3.3 Topic Details

| ID | Topic | Parent Section | Description | Prerequisites |
|----|-------|----------------|-------------|---------------|
| DSPEC.NN.56.01 | [Topic Name] | DSPEC.NN.55.01 | [Topic description] | [Required knowledge] |
| DSPEC.NN.56.02 | [Topic Name] | DSPEC.NN.55.01 | [Topic description] | [Required knowledge] |

### 3.4 Examples

| ID | Example | Context | Purpose |
|----|---------|---------|---------|
| DSPEC.NN.57.01 | [Example Name] | [Where used] | [What it demonstrates] |
| DSPEC.NN.57.02 | [Example Name] | [Where used] | [What it demonstrates] |

### 3.5 References

| ID | Reference | Type | URL/Path |
|----|-----------|------|----------|
| DSPEC.NN.58.01 | [Reference Name] | [external / internal] | [URL or path] |

---

## 4. Style Requirements

### 4.1 Tone and Voice

| Property | Value |
|----------|-------|
| Tone | [formal / informal / technical] |
| Voice | [active / passive / mixed] |
| Person | [first / second / third] |
| Reading Level | [basic / intermediate / advanced] |

### 4.2 Formatting Standards

| Element | Standard |
|---------|----------|
| Headings | [Heading conventions] |
| Code Blocks | [Code formatting requirements] |
| Lists | [List formatting requirements] |
| Tables | [Table formatting requirements] |
| Images | [Image requirements and captions] |

### 4.3 Terminology

| Term | Definition | Usage Context |
|------|------------|---------------|
| [Term 1] | [Definition] | [When to use] |
| [Term 2] | [Definition] | [When to use] |

---

## 5. Review Criteria

### 5.1 Accuracy

| Criterion | Verification Method |
|-----------|---------------------|
| Technical Accuracy | [How to verify technical content] |
| Code Examples | [How to verify code works] |
| Links | [How to verify links are valid] |

### 5.2 Completeness

| Criterion | Coverage Requirement |
|-----------|---------------------|
| All Sections | [All outline sections must be present] |
| All Features | [All features must be documented] |
| All Examples | [Required examples must be included] |

### 5.3 Clarity

| Criterion | Readability Standard |
|-----------|---------------------|
| Sentence Length | [Maximum sentence length] |
| Paragraph Length | [Maximum paragraph length] |
| Jargon | [Jargon usage policy] |
| Readability Score | [Target Flesch-Kincaid or similar] |

---

## 6. Dependencies

### 6.1 Source Materials

| Source | Type | Status |
|--------|------|--------|
| [Source 1] | [API spec / design doc / etc.] | [Available / Pending] |
| [Source 2] | [API spec / design doc / etc.] | [Available / Pending] |

### 6.2 Subject Matter Experts

| Expert | Domain | Contact |
|--------|--------|---------|
| [Name] | [Domain expertise] | [Contact info] |

---

## 7. Verification

### 7.1 Review Workflow

| Stage | Reviewer | Criteria |
|-------|----------|----------|
| Technical Review | [Reviewer role] | [Technical accuracy] |
| Editorial Review | [Reviewer role] | [Style and clarity] |
| Final Approval | [Approver role] | [Publication readiness] |

### 7.2 Testing

| Test Type | Description |
|-----------|-------------|
| Link Validation | All internal and external links verified |
| Code Testing | All code examples executed and verified |
| Screenshot Accuracy | All screenshots match current UI |

---

## 8. Implementation

| Property | Value |
|----------|-------|
| Output Location | docs/[category]/ |
| File Naming | [Naming convention] |
| Version Control | [Git branch strategy] |
| Publication Channel | [Where published] |

### 8.1 Tools

| Tool | Purpose |
|------|---------|
| [Tool 1] | [Purpose] |
| [Tool 2] | [Purpose] |

---

**Template Version**: 1.0
**Last Updated**: 2026-03-01
