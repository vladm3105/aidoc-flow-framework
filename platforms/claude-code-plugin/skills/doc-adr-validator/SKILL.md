---
name: doc-adr-validator
description: Validate Architecture Decision Records (ADR) against Layer 5 schema standards
metadata:
  tags:
    - sdd-workflow
    - layer-5-artifact
    - quality-assurance
  custom_fields:
    layer: 5
    artifact_type: ADR
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: shared
    development_status: active
    skill_category: quality-assurance
    upstream_artifacts: [ADR]
    downstream_artifacts: []
    version: "1.4"
    last_updated: "2026-05-22"
  versioning_policy: "tracks ADR-TEMPLATE schema_version"
---

# doc-adr-validator

Validate Architecture Decision Records (ADR) against Layer 5 schema standards.

## Activation

Invoke when user requests validation of ADR documents or after creating/modifying ADR artifacts.

## Validation Schema Reference

Template (single source of truth): `framework/layers/05_ADR/ADR-TEMPLATE.yaml`
Standards: `framework/governance/ID_NAMING_STANDARDS.md`, `framework/layers/05_ADR/README.md`
Layer: 5
Artifact Type: ADR

## Validation Checklist

### 0. Folder Structure Validation (BLOCKING)

**Nested Folder Rule**: ALL ADR documents MUST be in nested folders regardless of size.

**Required Structure**:

| ADR Type | Required Location |
|----------|-------------------|
| Monolithic | `docs/05_ADR/ADR-NN_{slug}/ADR-NN_{slug}.md` |

**Validation**:

```
1. Check document is inside a nested folder: docs/05_ADR/ADR-NN_{slug}/
2. Verify folder name matches ADR ID pattern: ADR-NN_{slug}
3. Verify file name matches folder: ADR-NN_{slug}.md
4. Parent path must be: docs/05_ADR/
```

**Example Valid Structure**:

```
docs/05_ADR/
├── ADR-01_f1_iam/
│   ├── ADR-01_f1_iam.md           ✓ Valid
│   ├── ADR-01.A_audit_report_v001.md
│   ├── ADR-01.R_review_report_v001.md  (legacy)
│   └── .drift_cache.json
├── ADR-02_f2_session/
│   └── ADR-02_f2_session.md       ✓ Valid
```

**Invalid Structure**:

```
docs/05_ADR/
├── ADR-01_f1_iam.md               ✗ NOT in nested folder
```

**Error Codes**:

| Code | Severity | Description |
|------|----------|-------------|
| ADR-E020 | ERROR | ADR not in nested folder (BLOCKING) |
| ADR-E021 | ERROR | Folder name doesn't match ADR ID |
| ADR-E022 | ERROR | File name doesn't match folder name |
| VAL-H001 | ERROR | Drift cache missing hash for upstream document |
| VAL-H002 | ERROR | Invalid hash format (must be sha256:<64 hex chars>) |

**This check is BLOCKING** - ADR must pass folder structure validation before other checks proceed.

---

### 1. Metadata Validation

```yaml
Required custom_fields:
  - document_type: ["adr", "template"]
  - artifact_type: "ADR"
  - layer: 5
  - architecture_approaches: [array format]
  - priority: ["primary", "shared", "fallback"]
  - development_status: ["active", "draft", "deprecated", "reference"]

Required tags:
  - adr (or adr-template)
  - layer-5-artifact

Forbidden tag patterns:
  - "^architecture-decision$"
  - "^decision-record$"
  - "^adr-\\d{3}$"
```

### 2. Structure Validation

**MVP Template Structure (11 Sections):**

| # | Section | Required | Purpose |
|---|---------|----------|---------|
| 1 | Document Control | MANDATORY | Metadata with SPEC-Ready Score |
| 2 | Context | MANDATORY | Problem Statement, Technical Context |
| 3 | Decision | MANDATORY | Chosen Solution, Key Components, Approach |
| 4 | Alternatives Considered | MANDATORY | Options with pros/cons |
| 5 | Consequences | MANDATORY | Positive/Negative Outcomes, Costs |
| 6 | Architecture Flow | MANDATORY | Mermaid diagrams, Integration Points |
| 7 | Implementation Assessment | MANDATORY | Phases, Rollback, Monitoring |
| 8 | Verification | MANDATORY | Success Criteria, BDD Scenarios |
| 9 | Traceability | MANDATORY | Upstream/Downstream, Tags, Cross-Links |
| 10 | Related Decisions | MANDATORY | Dependencies, Supersessions |
| 11 | MVP Lifecycle | MANDATORY | Iteration guidance |

**Title (H1):** `# ADR-NN: Title`

**Document Control Required Fields:**
- Project Name
- Document Version
- Date
- Document Owner
- Prepared By
- Status

**File Naming:**
Pattern: `ADR-NN_descriptive_name.md`

### 3. Content Validation

**Status Values:**
- Proposed
- Accepted
- Deprecated
- Superseded

**Context Subsections (Required):**
- 4.1 Problem Statement
- 4.2 Background
- 4.3 Driving Forces
- 4.4 Constraints

**Decision Subsections (Required):**
- 5.1 Chosen Solution
- 5.2 Key Components
- 5.3 Implementation Approach

**Consequences Subsections (Required):**
- 7.1 Positive Outcomes
- 7.2 Negative Outcomes

**Architecture Flow:**
- Must contain Mermaid diagram
- Allowed types: flowchart, sequenceDiagram, stateDiagram-v2

**ADR-Ready Score:**
- Minimum threshold: 90%
- Components: Problem statement, context, decision clarity, consequences, architecture diagram, implementation assessment, traceability

**Element-ID Naming Compliance:**
- Element IDs MUST use the 4-segment `ADR.NN.SS.xxxx` format (`NN` = doc number, `SS` = section, `xxxx` = 4-char hex hash) per `framework/governance/ID_NAMING_STANDARDS.md`.
- Document-level references MUST use the dash form `ADR-NN` (and `SPEC-NN` / `IPLAN-NN` for downstream artifacts).
- REJECT legacy forms: 3-segment `ADR.NN.xxxx`, numeric type-code segments (e.g. `ADR.NN.13.SS`), `DEC-XXX` / `ALT-XXX` / `CON-XXX`, and `ADR-NNN` (extra leading zero).

### 4. Traceability Validation

**Layer 5 Cumulative Tags** (4-segment element IDs `TYPE.NN.SS.xxxx`, `SS` = section, `xxxx` = 4-char hex hash):
- @brd: BRD.NN.SS.xxxx (required)
- @prd: PRD.NN.SS.xxxx (required)
- @ears: EARS.NN.SS.xxxx (required)
- @bdd: BDD.NN.SS.xxxx (required)

**Downstream Expected:**
- SPEC (Layer 6) — component specifications
- TDD (Layer 7) — test case definitions
- IPLAN (Layer 8) — execution plan

**Same-Type References:**
- @related-adr: ADR-NN
- @supersedes: ADR-NN
- @depends-adr: ADR-NN

## Error Codes

| Code | Severity | Description |
|------|----------|-------------|
| ADR-E001 | error | Missing required tag 'adr' |
| ADR-E002 | error | Missing required tag 'layer-5-artifact' |
| ADR-E003 | error | Invalid document_type |
| ADR-E004 | error | Invalid architecture_approaches format |
| ADR-E005 | error | Forbidden tag pattern detected |
| ADR-E006 | error | Missing required section |
| ADR-E007 | error | Multiple H1 headings detected |
| ADR-E008 | error | Missing Context section (Section 4) |
| ADR-E009 | error | Missing Decision section (Section 5) |
| ADR-E010 | error | Missing Consequences section (Section 7) |
| ADR-E011 | error | Context missing Problem Statement subsection |
| ADR-E012 | error | Decision missing Chosen Solution subsection |
| ADR-E013 | error | Consequences missing outcomes |
| ADR-E014 | warning | File name does not match format |
| ADR-E015 | error | Invalid element ID format (not 4-segment `ADR.NN.SS.xxxx`) |
| ADR-E016 | error | Legacy element ID / numeric type code / `ADR-NNN` document ID detected |
| ADR-W001 | warning | Missing Architecture Flow Mermaid diagram |
| ADR-W002 | warning | Context missing Constraints subsection |
| ADR-W003 | warning | Missing upstream tags (@prd, @ears, @bdd) |
| ADR-W004 | warning | Implementation Assessment missing Complexity |
| ADR-W005 | warning | SPEC-Ready Score below 90% |
| ADR-W006 | warning | Requirements Satisfied table missing |
| ADR-I001 | info | Consider adding Alternatives Considered |
| ADR-I002 | info | Consider adding Security Considerations |
| ADR-I003 | info | Consider adding Rollback Plan |

## How Validation Runs

The framework ships no runtime scripts — **this skill is the validator**. There
is no external `validate_adr.py` to call. Apply the Validation Checklist and
Validation Workflow below directly against the target document(s), checking each
against `framework/layers/05_ADR/ADR-TEMPLATE.yaml`,
`framework/governance/ID_NAMING_STANDARDS.md`, and
`framework/layers/05_ADR/README.md`:

- Single ADR document: apply the checklist to `docs/05_ADR/ADR-NN_{slug}/ADR-NN_{slug}.md`.
- All ADR documents: apply the checklist across every document under `docs/05_ADR/`.
- Emit the Output Format report (below), listing errors/warnings/info by severity.

## Validation Workflow

1. Parse YAML frontmatter
2. Check required metadata fields
3. Validate tag taxonomy
4. Verify 4-part structure
5. Validate required sections (1-10)
6. Check Context subsections
7. Check Decision subsections
8. Check Consequences subsections
9. Verify Mermaid diagram presence
10. Validate upstream references
11. Validate element-ID naming compliance (4-segment `ADR.NN.SS.xxxx`; `ADR-NN` document refs)
12. Calculate SPEC-Ready Score
13. Verify file naming convention
14. Generate validation report

## Integration

- Invoked by: doc-flow, doc-adr (post-creation)
- Feeds into: trace-check (cross-document validation)
- Reports to: quality-advisor

## Output Format

```
ADR Validation Report
=====================
Document: ADR-01_example.md
Status: PASS/FAIL

Structure:
- Context: Complete/Incomplete
- Decision: Complete/Incomplete
- Consequences: Complete/Incomplete
- Architecture Flow: Present/Missing

Errors: N
Warnings: N
Info: N

[Details listed by severity]
```

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.4 | 2026-05-22 | Migrated to the framework 8-layer model: schema/standards references repointed to `framework/layers/05_ADR/` + `framework/governance/`; removed runtime `validate_adr.py` calls (the skill is the validator); cumulative tags + downstream rebuilt to 4-segment IDs / SPEC,TDD,IPLAN; added element-ID naming-compliance check (ADR-E015/E016) enforcing `ADR.NN.SS.xxxx` and `ADR-NN`, rejecting legacy forms; `ADR-NN` file naming; SPEC-Ready terminology | System |
| 1.3 | 2026-02-27 | Migrated frontmatter to `metadata`; normalized schema/command references to the legacy ADR flow path; updated valid structure example for preferred `ADR-NN.A_audit_report_vNNN.md` with legacy reviewer compatibility | System |
| 1.2 | 2026-02-26 | Updated structure validation to 11-section MVP template (aligned with ADR-MVP-TEMPLATE.md v1.1) |
| 1.1 | 2026-02-11 | **Nested Folder Rule**: Added Section 0 Folder Structure Validation (BLOCKING); ADR must be in `docs/05_ADR/ADR-NN_{slug}/` folders; Added error codes ADR-E020, ADR-E021, ADR-E022 |
| 1.0 | 2026-02-08 | Initial validator skill definition with YAML frontmatter | System |

## Implementation Plan Consistency (IPLAN-004)

- Treat plan-derived outputs as valid source mode and verify intent preservation from implementation plan scope/objectives.
- Validate upstream autopilot precedence assumption: `--iplan > --ref > --prompt`.
- Flag objective/scope conflicts between plan context and artifact output as blocking issues requiring clarification.
- Do not introduce legacy fallback paths such as `docs-v2.0/00_REF`.

