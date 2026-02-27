---
title: "ADR-MVP-TEMPLATE: Architecture Decision Record (MVP)"
tags:
  - adr-template
  - mvp-template
  - layer-5-artifact
  - document-template
  - shared-architecture
custom_fields:
  document_type: template
  artifact_type: ADR
  layer: 5
  template_variant: mvp
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  schema_version: "1.1"
  last_updated: "2026-02-26"
  total_sections: 11
  complexity: 1 # 1-5 scale
---
> ** Dual-Format Note**:
>
> This MD template is the **primary source** for human workflow.
> - **For Autopilot**: See `ADR-MVP-TEMPLATE.yaml` (YAML template)
> - **Shared Validation**: Both formats are validated by `ADR_MVP_SCHEMA.yaml`
> - **Complete Explanation**: See [DUAL_MVP_TEMPLATES_ARCHITECTURE.md](../DUAL_MVP_TEMPLATES_ARCHITECTURE.md) for full comparison of formats, authority hierarchy, and when to use each.
>
<!--
AI_CONTEXT_START
Role: AI Software Architect
Objective: Create a streamlined MVP Architecture Decision Record.
Constraints:
- Focus on the single decision at hand.
- Analyze 2-3 viable alternatives maximum.
- Be decisive; clear recommendation required.
- Keep implementation notes focused on immediate MVP needs.
- Maintain single-file structure (no document splitting in MVP).
AI_CONTEXT_END
-->

> **MVP Template** — Single-file, streamlined ADR for rapid MVP decisions.
> Use this template for MVP architecture decisions with 2-3 alternatives.

> **Validation Note**: This is the standard ADR template. Some legacy validators may report warnings - this is expected behavior. See `scripts/README.md` → "MVP Template Validation" for guidance.

> References: Schema `ADR_MVP_SCHEMA.yaml` | Rules `ADR_MVP_CREATION_RULES.md`, `ADR_MVP_VALIDATION_RULES.md` | Matrix `ADR-00_TRACEABILITY_MATRIX-TEMPLATE.md`

# ADR-NN: [Architecture Decision Title]

## 1. Document Control

| Item | Details |
|------|---------|
| **Status** | Proposed / Accepted / Deprecated / Superseded |
| **Date** | YYYY-MM-DDTHH:MM:SS |
| **Decision Makers** | [Names/Roles] |
| **Author** | [Architect/Lead Name] |
| **Version** | 1.0 |
| **SYS-Ready Score** | [Score]/100 (Target: ≥90) |

---

## 2. Context

### 2.1 Problem Statement

**Originating Topic**: BRD.NN.32.SS - [Topic Name from BRD Section 7.2]

[1-2 paragraph description of the architectural challenge or decision needed]

**Business Driver**: [Why this decision matters to the business - from BRD §7.2]

**Key Constraints**:
- [Constraint 1 - e.g., budget limit, regulatory requirement]
- [Constraint 2 - e.g., timeline, team expertise]
- [Constraint 3 - e.g., existing infrastructure, integration requirement]

### 2.2 Technical Context

[Brief background on existing system state and technical environment]

**Current State**:
- [What exists today]
- [What's working/not working]

**MVP Requirements**:
- [Core requirement this decision must satisfy]
- [Quality attribute targets - e.g., p95 < 200ms]

---

## 3. Decision

**ID Format**: `ADR.NN.10.SS` (Decision)

### 3.1 Chosen Solution (ADR.NN.10.01)

**We will use**: [Selected option/technology/approach]

**Because**:
1. [Primary reason - aligned with business driver]
2. [Secondary reason - technical fit]
3. [Tertiary reason - cost/time advantage]

### 3.2 Key Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| [Component 1] | [What it does] | [Specific tech] |
| [Component 2] | [What it does] | [Specific tech] |
| [Component 3] | [What it does] | [Specific tech] |

### 3.3 Implementation Approach

[2-3 sentences on how this will be implemented for MVP]

**MVP Scope**: [What's included in MVP implementation]

**Next Cycle Scope**: [What's deferred to next MVP iteration]

---

## 4. Alternatives Considered

**ID Format**: `ADR.NN.12.SS` (Alternative)

### 4.1 Option A: [Selected Option Name]  (ADR.NN.12.01)

**Description**: [Brief description of the chosen approach]

**Pros**:
- [Advantage 1]
- [Advantage 2]

**Cons**:
- [Trade-off 1]
- [Trade-off 2]

**Est. Cost**: $[X]/month | **Fit**: Best

---

### 4.2 Option B: [Alternative Option Name] (ADR.NN.12.02)

**Description**: [Brief description]

**Pros**:
- [Advantage 1]
- [Advantage 2]

**Cons**:
- [Disadvantage 1 - why rejected]
- [Disadvantage 2]

**Rejection Reason**: [Specific reason why not selected]

**Est. Cost**: $[X]/month | **Fit**: Good/Poor

---

### 4.3 Option C: [Alternative Option Name] (Optional) (ADR.NN.12.03)

**Description**: [Brief description]

**Pros**:
- [Advantage 1]

**Cons**:
- [Disadvantage 1]

**Rejection Reason**: [Specific reason]

**Est. Cost**: $[X]/month | **Fit**: Poor

---

## 5. Consequences

**ID Format**: `ADR.NN.13.SS` (Consequence)

### 5.1 Positive Outcomes (ADR.NN.13.01)

- [Benefit 1]: [Quantifiable impact]
- [Benefit 2]: [Quantifiable impact]
- [Benefit 3]: [Qualitative benefit]

### 5.2 Trade-offs & Risks (ADR.NN.13.02)

| Risk/Trade-off | Impact | Mitigation |
|----------------|--------|------------|
| [Trade-off 1] | [H/M/L] | [How we'll address it] |
| [Trade-off 2] | [H/M/L] | [How we'll address it] |
| [Risk 1] | [H/M/L] | [Mitigation strategy] |

### 5.3 Cost Estimate

| Category | MVP Phase | Monthly Ongoing |
|----------|-----------|-----------------|
| Development | [X] person-weeks | - |
| Infrastructure | $[X] one-time | $[X]/month |
| Third-party services | $[X] setup | $[X]/month |
| **Total** | **$[X]** | **$[X]/month** |

---

## 6. Architecture Flow

### 6.1 High-Level Flow

```mermaid
flowchart TD
    A[Input/Trigger] --> B[Core Component]
    B --> C{Decision Point}
    C --> D[Success Path]
    C --> E[Error Path]
    
    subgraph "MVP Scope"
        B
        D
    end
    
    subgraph "External"
        F[External Service]
    end
    
    B --> F
```

### 6.2 Key Integration Points

| System | Integration Type | Purpose |
|--------|-----------------|---------|
| [System 1] | [REST/gRPC/Async] | [What data flows] |
| [System 2] | [REST/gRPC/Async] | [What data flows] |

### 6.3 Required Decision Diagram Contract (MVP)

For ADR, include:
- `@diagram: c4-l3` for decision-level component scope.
- Decision `sequenceDiagram` for chosen interaction pattern.
- Conditional `@diagram: dfd-l2` when the decision materially changes data movement or data boundaries.

Required declaration block:

```markdown
@diagram: c4-l3
@diagram: sequence-async
@diagram-condition: include dfd-l2 when data-impacting=true
@diagram-lifecycle: mvp-prod-newmvp
```

---

## 7. Implementation Assessment

### 7.1 MVP Development Phases

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Phase 1 | [X] weeks | [Core implementation] |
| Phase 2 | [X] weeks | [Integration & testing] |

### 7.2 Rollback Plan

**Rollback Trigger**: [Conditions requiring reversion]

**Rollback Steps**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Estimated Rollback Time**: [X] minutes/hours

### 7.3 Monitoring (MVP Baseline)

| Metric | Alert Threshold | Action |
|--------|-----------------|--------|
| Error rate | > [X]% | [Response] |
| Latency (p95) | > [X]ms | [Response] |
| Availability | < [X]% | [Response] |

---

## 8. Verification

### 8.1 Success Criteria

- [ ] [Measurable technical outcome 1]
- [ ] [Measurable technical outcome 2]
- [ ] [Performance target met]
- [ ] [Integration working]

### 8.2 BDD Scenarios

[Reference to BDD scenarios that validate this decision]

- Feature: [Feature name] - `04_BDD/BDD-NN_{suite}/BDD-NN.SS_{slug}.feature`

---

## 9. Traceability

### 9.1 Upstream References

| Source | Document | Relevant Section |
|--------|----------|------------------|
| BRD | BRD.NN | §7.2 - Architecture Decision Requirements |
| PRD | PRD.NN | §18 - Architecture Decision Topics |
| EARS | EARS.NN | [Relevant requirements] |

### 9.2 Downstream Artifacts

| Artifact | Status | Relationship |
|----------|--------|--------------|
| SYS-NN | TBD | System requirements derived from this ADR |
| REQ-NN | TBD | Atomic requirements |
| SPEC-NN | TBD | Technical specifications |

### 9.3 Traceability Tags

```markdown
@brd: BRD.NN.32.SS
@prd: PRD.NN.EE.SS
@ears: EARS.NN.24.SS
```

### 9.4 Cross-Links (Same-Layer)

Use machine-parseable tags to document relationships between ADRs:
- `@depends: ADR-NN` — hard prerequisite ADR(s) that must be satisfied first.
- `@discoverability: ADR-NN (short rationale); ADR-NN (short rationale)` — related ADRs with brief reasons to aid AI search and ranking.

Prefer these tags over legacy "See also …" strings.

---

## 10. Related Decisions

| Relationship | ADR | Description |
|--------------|-----|-------------|
| Depends On | ADR-NN | [What this decision depends on] |
| Related | ADR-NN | [Related parallel decision] |
| Supersedes | ADR-NN | [Previous decision replaced] |

---

## 11. MVP Lifecycle (MVP → PROD → NEW MVP)

> **Lifecycle Principle**: Each ADR represents decisions for ONE iteration cycle. New architectural decisions require a NEW ADR.

### 11.1 Lifecycle Phases

| Phase | Duration | Focus | ADR Output |
|-------|----------|-------|------------|
| **MVP** | 1-2 weeks | Core architecture decisions | This ADR → SYS → Implementation |
| **PROD** | 30-90 days | Operate, validate decisions, collect feedback | Decision outcomes, lessons learned |
| **NEW MVP** | 1-2 weeks | Next architecture decisions | Create ADR-02, ADR-03, etc. |

### 11.2 When to Create a New ADR

- [ ] Current ADR decisions are validated in production
- [ ] New architectural decisions needed for next iteration
- [ ] Decision context has significantly changed
- [ ] Business case for new architecture approved

### 11.3 Cross-ADR Traceability

When creating the next ADR iteration:

1. **Link to previous cycle**: Add `@depends: ADR-01` in Related Decisions section
2. **Reference production outcomes**: Include validation data from previous cycle
3. **Supersedes pattern**: Use when replacing a previous decision entirely
4. **Update index**: Add new ADR to ADR-00_index.md with cross-references

**Note**: There is no "full ADR" template. This MVP template IS the standard. Expansion happens through NEW ADRs, not template migration.

---

**Document Version**: 1.0
**Template Version**: 1.1 (MVP - 11 sections)
**Last Updated**: 2026-02-26
**Maintained By**: [Architecture Team]

---

> **MVP Template Notes**:
> - This is the standard ADR template (11 sections: 1-11)
> - Single file - no sectioning per user requirement
> - Focus on decision + rationale + alternatives
> - Maintains ai_dev_flow framework compliance
> - **Lifecycle**: MVP → PROD → NEW MVP (no separate "full ADR" template)
