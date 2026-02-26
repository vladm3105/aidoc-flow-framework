---
title: "PRD-MVP-TEMPLATE: Product Requirements Document (MVP)"
tags:
  - prd-template
  - mvp-template
  - layer-2-artifact
  - document-template
  - shared-architecture
custom_fields:
  document_type: template
  artifact_type: PRD
  layer: 2
  template_variant: mvp
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  schema_version: "1.0"
  complexity: 1 # 1-5 scale
---

> ** Dual-Format Note**:
>
> This MD template is the **primary source** for human workflow.
> - **For Autopilot**: See `PRD-MVP-TEMPLATE.yaml` (YAML template)
> - **Shared Validation**: Both formats are validated by `PRD_MVP_SCHEMA.yaml`
> - **Complete Explanation**: See [DUAL_MVP_TEMPLATES_ARCHITECTURE.md](../DUAL_MVP_TEMPLATES_ARCHITECTURE.md) for full comparison of formats, authority hierarchy, and when to use each.
> ---

<!--
  AI_CONTEXT_START
Role: AI Product Manager
Objective: Create a streamlined MVP Product Requirements Document.
Constraints:
  - Focus on hypothesis validation and core user stories
  - Keep functional requirements atomic and testable
  - Do not split file; keep it monolithic
AI_CONTEXT_END
---
title: "PRD-MVP-TEMPLATE: Product Requirements Document (MVP)"
tags:
  - prd-template
  - mvp-template
  - layer-2-artifact
  - document-template
custom_fields:
  document_type: prd
  artifact_type: PRD
  layer: 2
  template_variant: mvp
  architecture_approaches: [ai-agent-based]
  priority: shared
  development_status: draft
  template_for: mvp-product-requirements-document
  descriptive_slug: null
  schema_reference: "PRD_MVP_SCHEMA.yaml"
  schema_version: "1.0"
  schema_status: optional
---
  creation_rules_reference: "PRD_MVP_CREATION_RULES.md"
  validation_rules_reference: "PRD_MVP_VALIDATION_RULES.md"
  traceability_matrix_template: "PRD-00_TRACEABILITY_MATRIX-TEMPLATE.md"
---

> **MVP-First Template** — Single-file PRD for the **MVP → PROD → NEW MVP** lifecycle.
> Use this template for each iteration cycle with 5-15 core features.

> **Lifecycle**: Each PRD corresponds to ONE BRD cycle. After production deployment and feedback collection, create NEW PRD for next features (linked to NEW BRD).

> **Validation Note**: MVP templates use ≥90% score thresholds. See `scripts/README.md` → "MVP Template Validation" for guidance.

> References: Schema `PRD_MVP_SCHEMA.yaml` | Rules `PRD_MVP_CREATION_RULES.md`, `PRD_MVP_VALIDATION_RULES.md` | Matrix `PRD-00_TRACEABILITY_MATRIX-TEMPLATE.md`

# PRD-NN: [MVP Product/Feature Name]

**[WARN] MVP Scope**: This PRD focuses on core hypothesis validation. Use MVP only.

**Upstream guardrails**: Use only existing upstream artifacts (BRD/ADR/EARS/BDD/SYS); set `null` only when a layer is absent.

**Thresholds pointer**: Define thresholds once; reuse via `@threshold:` tags; follow `THRESHOLD_NAMING_RULES.md`.

**User-story scope**: PRD holds role/story summaries; detailed behaviors live in EARS and executable scenarios in BDD.

## 1. Document Control

| Item | Details |
|------|---------|
| **Status** | Draft / Review / Approved |
| **Version** | 0.1.0 |
| **Date Created** | YYYY-MM-DDTHH:MM:SS |
| **Last Updated** | YYYY-MM-DDTHH:MM:SS |
| **Author** | [Product Manager Name] |
| **Reviewer** | [Technical Lead Name] |
| **Approver** | [Stakeholder Name] |
| **BRD Reference** | @brd: BRD.NN.TT.SS |
| **Priority** | High |
| **Target Release** | [MVP Launch Date] |
| **Estimated Effort** | [X person-weeks] |
| **SYS-Ready Score** | [Score]/100 (Target: ≥90) |
| **EARS-Ready Score** | [Score]/100 (Target: ≥90) |

### 1.1 Document Revision History

| Version | Date | Author | Changes Made |
|---------|------|--------|--------------|
| 0.1.0 | YYYY-MM-DDTHH:MM:SS | [Author] | Initial MVP draft |

---

## 2. Executive Summary

[2-3 sentences: What problem does this MVP solve? Who benefits? What's the expected business impact?]

### 2.1 MVP Hypothesis

**We believe that** [target users] **will** [key behavior/outcome] **if we** [MVP solution].

**We will know this is true when** [measurable validation criteria].

### 2.2 Timeline Overview

| Phase | Dates | Duration |
|-------|-------|----------|
| Development | YYYY-MM-DDTHH:MM:SS to YYYY-MM-DDTHH:MM:SS | X weeks |
| Testing | YYYY-MM-DDTHH:MM:SS to YYYY-MM-DDTHH:MM:SS | X weeks |
| MVP Launch | YYYY-MM-DDTHH:MM:SS | - |
| Validation Period | +30 days post-launch | 30 days |

---

## 3. Problem Statement

### 3.1 Current State

[Brief description of the current situation and pain points - 3-5 bullet points]

- [Pain point 1]: [Impact]
- [Pain point 2]: [Impact]
- [Pain point 3]: [Impact]

### 3.2 Business Impact

[Quantify the problem - use available data]

- Revenue/efficiency impact: [estimate]
- Customer satisfaction impact: [estimate]
- Competitive disadvantage: [brief description]

### 3.3 Opportunity

[1-2 sentences: What market or business opportunity does this MVP address?]

---

## 4. Target Audience & User Personas

### 4.1 Primary User Persona

**[Persona Name]** - [Role/Description]

- **Key characteristic**: [What defines this user]
- **Main pain point**: [What problem they face]
- **Success criteria**: [What outcome they need]
- **Usage frequency**: [How often they'll use the product]

### 4.2 Secondary Users (Optional)

[List any secondary users if relevant for MVP - keep brief]

---

## 5. Success Metrics (KPIs)

### 5.1 MVP Validation Metrics (30-Day)

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| [Adoption metric] | 0 | [target] | [how measured] |
| [Engagement metric] | N/A | [target] | [how measured] |
| [Satisfaction metric] | N/A | ≥[target]/5 | User survey |

### 5.2 Business Success Metrics (90-Day)

| Metric | Target | Decision Threshold |
|--------|--------|-------------------|
| [Primary business metric] | [target] | < [threshold] = Pivot |
| [Secondary metric] | [target] | < [threshold] = Iterate |

### 5.3 Go/No-Go Decision Gate

**At MVP+90 days**, evaluate:
- [PASS] **Proceed to Full Product**: All targets met
-  **Iterate**: 60-80% of targets met
- [FAIL] **Pivot/Shutdown**: <60% of targets met

---

## 6. Scope & Requirements

### 6.1 In-Scope (MVP Core Features)

[List 5-15 must-have features for MVP - prioritized]

| # | Feature | Priority | Description |
|---|---------|----------|-------------|
| 1 | [Feature name] | P1-Must | [Brief description] |
| 2 | [Feature name] | P1-Must | [Brief description] |
| 3 | [Feature name] | P1-Must | [Brief description] |
| 4 | [Feature name] | P2-Should | [Brief description] |
| 5 | [Feature name] | P2-Should | [Brief description] |

### 6.2 Dependencies (keep short)
- Technical: [System/API/infra] — status, impact
- Business: [Org/process prerequisite] — owner, date
- External: [Vendor/regulatory] — status, impact

### 6.3 Out-of-Scope (Next MVP Cycle)
- [Feature]: Candidate for BRD-NN+1 - [reason]
- [Feature]: Candidate for BRD-NN+1 - [reason]
- [Integration]: Not included in this cycle - [reason]

> **Lifecycle Note**: Out-of-scope items become candidates for the next BRD/PRD cycle.

### 6.4 Dependencies

| Dependency | Status | Impact | Owner |
|------------|--------|--------|-------|
| [Technical dependency] | [Status] | [Blocking/Non-blocking] | [Team] |
| [Business dependency] | [Status] | [Blocking/Non-blocking] | [Owner] |

**Dependency checklist**: status current; owner assigned; blocking noted; fallback path defined.

---

## 7. User Stories & User Roles

**Scope split**: PRD = roles + story summaries; EARS = detailed behaviors; BDD = executable scenarios.

### 7.1 Core User Stories

| ID | User Story | Priority | Acceptance Criteria |
|----|------------|----------|---------------------|
| PRD.NN.09.01 | As a [persona], I want to [action], so that [benefit] | P1 | [Brief criteria] |
| PRD.NN.09.02 | As a [persona], I want to [action], so that [benefit] | P1 | [Brief criteria] |
| PRD.NN.09.03 | As a [persona], I want to [action], so that [benefit] | P1 | [Brief criteria] |
| PRD.NN.09.04 | As a [persona], I want to [action], so that [benefit] | P2 | [Brief criteria] |
| PRD.NN.09.05 | As a [persona], I want to [action], so that [benefit] | P2 | [Brief criteria] |

### 7.2 User Roles (brief)
| Role | Purpose | Permissions |
|------|---------|-------------|
| [Role] | [What they do] | [Access level] |
| [Role] | [What they do] | [Access level] |

### 7.3 Story Summary

| Priority | Count | Notes |
|----------|-------|-------|
| P1 (Must-Have) | [X] | Required for MVP launch |
| P2 (Should-Have) | [X] | Include if time permits |
| **Total** | [X] | |

---

## 8. Functional Requirements

### 8.1 Core Capabilities (brief)
| ID | Capability | Success Criteria |
|----|------------|------------------|
| PRD.NN.01.01 | [Capability name] | [How to validate] |
| PRD.NN.01.02 | [Capability name] | [How to validate] |
| PRD.NN.01.03 | [Capability name] | [How to validate] |

### 8.2 User Journey (happy path)
1. User [action] → System [response]
2. User [action] → System [response]
3. [Outcome]

### 8.3 Error Handling (MVP)
| Error Scenario | User Experience | System Behavior |
|----------------|-----------------|-----------------|
| [Error type] | [What user sees] | [What system does] |

---

## 9. Quality Attributes

### 9.1 Performance (baseline)
| Metric | Target | Notes |
|--------|--------|-------|
| API Response Time (p95) | < [X]ms | Core endpoints |
| Page Load Time | < [X]s | Primary screens |
| Concurrent Users | [X] | MVP capacity |

### 9.2 Security (baseline)
- [ ] Authentication approach noted
- [ ] Encryption at transit/rest
- [ ] Input validation in place

### 9.3 Availability (baseline)
- Uptime target: [95-99]% (MVP)
- Planned maintenance window: [if any]

---

## 10. Architecture Requirements

> Brief: Capture architecture topics needing ADRs. Keep MVP summaries short; full ADRs live separately.

**ID Format**: `PRD.NN.32.SS`

- Infrastructure: status, driver, approach
- Data: status, driver, approach
- Integrations: status, driver, approach
- Security: status, driver, approach
- Observability: status, driver, approach
- AI/ML (if relevant): status, driver, approach
- Tech selection: status, driver, approach


**Estimated Cost**: $[X]/month

---

### 10.2 Data Architecture (PRD.NN.32.02)

**Status**: [ ] Selected | [ ] Pending | [ ] N/A

**Business Driver**: [Why MVP needs this decision]

**MVP Approach**: [Selected option or recommendation]

**Rationale**: [1-2 sentence justification]

---

### 10.3 Integration (PRD.NN.32.03)

**Status**: [ ] Selected | [ ] Pending | [ ] N/A

**Business Driver**: [Key integrations for MVP]

**MVP Approach**: [Selected option or keep minimal]

**Rationale**: [1-2 sentence justification]

---

### 10.4 Security (PRD.NN.32.04)

**Status**: [ ] Selected | [ ] Pending | [ ] N/A

**Business Driver**: [Security requirements for MVP]

**MVP Approach**: [Authentication/authorization approach]

**Rationale**: [1-2 sentence justification]

---

### 10.5 Observability (PRD.NN.32.05)

**Status**: [ ] Selected | [ ] Pending | [ ] N/A (MVP/prototype)

**Business Driver**: [Monitoring needs for MVP validation]

**MVP Approach**: [Basic logging, error tracking]

**Rationale**: [1-2 sentence justification]

---

### 10.6 AI/ML (PRD.NN.32.06)

**Status**: [ ] Selected | [ ] Pending | [ ] N/A

**Business Driver**: [AI/ML requirements if any]

**MVP Approach**: [Approach or N/A for MVP]

**Rationale**: [1-2 sentence justification]

---

### 10.7 Technology Selection (PRD.NN.32.07)

**Status**: [ ] Selected | [ ] Pending | [ ] N/A

**Business Driver**: [Key technology choices]

**MVP Selection**: [Framework/language/platform]

**Rationale**: [1-2 sentence justification]

---

## 11. Constraints & Assumptions (brief)
- Budget/timeline limits: [X]
- Resource limits: [team/skills]
- Technical constraints: [stack/infra]
- Key assumptions (H/M/L risk): [list 2-3]

**Constraints/Risks (short)**: surface single blockers; pair each risk with owner and trigger.

---

## 12. Risk Assessment (brief)
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk 1] | H/M/L | H/M/L | [Mitigation] |
| [Risk 2] | H/M/L | H/M/L | [Mitigation] |

---

## 13. Implementation Approach

### 13.1 MVP Development Phases

| Phase | Duration | Deliverables | Success Criteria |
|-------|----------|--------------|------------------|
| **Phase 1: Core** | [X] weeks | [Core features] | [Criteria] |
| **Phase 2: Polish** | [X] weeks | [Secondary features, bug fixes] | [Criteria] |
| **Phase 3: Launch** | [X] days | [Deployment, monitoring] | [Criteria] |

### 13.2 Testing Strategy (MVP)

| Test Type | Coverage | Responsible |
|-----------|----------|-------------|
| Unit Tests | [X]% minimum | Development |
| Integration Tests | Critical paths | Development |
| UAT | Core user stories | Product/QA |
| Performance | Baseline metrics | QA |

---

## 14. Acceptance Criteria

### 14.1 Acceptance Criteria (trimmed)
- Business: P1 features deliver observable user value; KPIs instrumented.
- Technical: Core journeys pass; perf targets met; logging/monitoring enabled; security baseline checked.
- QA: Critical bugs resolved; basic docs/support ready; analytics tracking configured.
- [ ] User feedback collected
- [ ] Initial satisfaction survey

**Small messaging table** (core flows only)
| Channel | Message | Owner |
|---------|---------|-------|
| [Email/Push/In-app] | [Copy stub] | [Name] |

**Compliance note**: capture data handling notes; confirm PII scope; log approvals.

---

## 15. Budget & Resources

### 15.1 MVP Development Cost

| Category | Estimate | Notes |
|----------|----------|-------|
| Development | $[X] | [X] person-weeks × rate |
| Infrastructure (3 months) | $[X] | Cloud hosting, services |
| Third-party services | $[X] | APIs, tools |
| **Total MVP Cost** | **$[X]** | |

### 15.2 ROI Hypothesis

**Investment**: $[MVP cost]

**Expected Return**: [Describe expected value if MVP succeeds]

**Payback Period**: [Estimated timeframe if hypothesis validated]

**Decision Logic**: If MVP metrics met → Full product investment of $[X] justified.

---

## 16. Traceability

### 16.1 Upstream References

| Source | Document | Relationship |
|--------|----------|--------------|
| BRD | @brd: BRD.NN.TT.SS | Business requirements source |
| Strategy | [Strategic document] | Strategic alignment |

### 16.2 Downstream Artifacts

| Artifact Type | Status | Notes |
|---------------|--------|-------|
| EARS | TBD | Created after PRD approval |
| BDD | TBD | Created after EARS |
| ADR | TBD | Created for selected architecture decisions |

### 16.3 Traceability Tags

```markdown
@brd: BRD.NN.TT.SS
```

### 16.4 Cross-Links (Same-Layer)

Use machine-parseable tags to document relationships between PRDs:
- `@depends: PRD-NN` — hard prerequisite PRD(s) that must be satisfied first.
- `@discoverability: PRD-NN (short rationale); PRD-NN (short rationale)` — related PRDs with brief reasons to aid AI search and ranking.

Prefer these tags over legacy "See also …" strings.

---

## 17. Glossary

| Term | Definition |
|------|------------|
| [Term 1] | [Definition relevant to this MVP] |
| [Term 2] | [Definition relevant to this MVP] |

**Master Glossary Reference**: See [BRD-00_GLOSSARY.md](../01_BRD/BRD-00_GLOSSARY.md)

---

## 18. Appendix A: Future Roadmap (Next MVP Cycle)

### 18.1 Phase 2 Features (If MVP Succeeds)

| Feature | Priority | Estimated Effort | Dependency |
|---------|----------|------------------|------------|
| [Feature] | P1 | [X] weeks | MVP complete |
| [Feature] | P2 | [X] weeks | [Dependency] |

### 18.2 Scaling Considerations

[Brief notes on what needs to change for full product scale]

- Infrastructure: [Scaling approach]
- Performance: [Optimization needs]
- Features: [Expansion areas]

---

## 19. MVP Lifecycle (MVP → PROD → NEW MVP)

> **Lifecycle Principle**: Each PRD represents ONE iteration cycle. New features require a NEW PRD.

### 19.1 Lifecycle Phases

| Phase | Duration | Focus | PRD Output |
|-------|----------|-------|------------|
| **MVP** | 1-2 weeks | Core features (5-15) | This PRD → EARS → Implementation |
| **PROD** | 30-90 days | Operate, measure, collect feedback | Production metrics, user feedback |
| **NEW MVP** | 1-2 weeks | Next feature set | Create PRD-02, PRD-03, etc. |

### 19.2 When to Create a New PRD

- [ ] Current PRD features are in production
- [ ] New feature set identified (next 5-15 features)
- [ ] Production feedback collected and analyzed
- [ ] Business case for new iteration approved

### 19.3 Cross-PRD Traceability

When creating the next PRD iteration:

1. **Link to previous cycle**: Add `@depends: PRD-01` in Section 16.2
2. **Reference production metrics**: Include validation data from previous cycle
3. **Carry forward learnings**: Document technical debt or deferred features
4. **Update index**: Add new PRD to PRD-00_index.md with cross-references

### 19.4 Iteration Cycle Example

```
PRD-01 (MVP) → Production → PRD-02 (New Features) → Production → PRD-03 ...
     ↓                           ↓                         ↓
   EARS-01                     EARS-02                   EARS-03
```

**Note**: There is no "full PRD" template. This MVP template IS the standard. Expansion happens through NEW PRDs, not template migration.

---

**Document Version**: 0.1.0
**Template Version**: 1.0 (MVP)
**Last Updated**: YYYY-MM-DDTHH:MM:SS
**Maintained By**: [Product Manager]

---

> **MVP Template Notes**:
> - This is the standard PRD template (~500 lines)
> - Single file - no sectioning per user requirement
> - Maintains ai_dev_flow framework compliance
> - **Lifecycle**: MVP → PROD → NEW MVP (no separate "full PRD" template)
