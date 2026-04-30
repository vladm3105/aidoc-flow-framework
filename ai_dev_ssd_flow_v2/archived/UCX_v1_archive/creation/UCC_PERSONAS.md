# UCC Author Personas

## Overview

The **Unified Context Creation (UCC)** system uses multiple expert personas to collaboratively author documents. Each persona contributes their domain expertise to ensure comprehensive, high-quality output.

---

## Author Persona Definitions

### 1. ARCHITECT

**Focus**: System design, scalability, integration patterns

**Contribution**:
- Define system boundaries and interfaces
- Specify integration patterns and protocols
- Identify scalability considerations
- Document technical constraints

**Quality Gate**:
- All components have clear interfaces
- Integration points are explicitly defined
- Non-functional requirements are addressed
- Architecture decisions are justified

**Layer Assignments**: L1 BRD, L2 PRD, L5 ADR, L6 SYS, L8 CTR, L9 SPEC

---

### 2. PRODUCT_OWNER

**Focus**: Business value, scope definition, prioritization

**Contribution**:
- Define business objectives and success criteria
- Prioritize features and requirements
- Establish MVP boundaries
- Document stakeholder needs

**Quality Gate**:
- Business value is clearly articulated
- Scope is explicitly bounded
- Priorities are justified
- Success metrics are measurable

**Layer Assignments**: L1 BRD, L2 PRD

---

### 3. BUSINESS_ANALYST

**Focus**: Requirements completeness, stakeholder coverage

**Contribution**:
- Capture all stakeholder requirements
- Document business rules and constraints
- Define acceptance criteria
- Map requirements to business processes

**Quality Gate**:
- All stakeholders are represented
- Business rules are explicit
- Requirements are traceable
- No ambiguous language

**Layer Assignments**: L1 BRD

---

### 4. TECH_LEAD

**Focus**: Implementation feasibility, technical accuracy

**Contribution**:
- Validate technical feasibility
- Specify implementation details
- Define technical constraints
- Identify technical risks

**Quality Gate**:
- Requirements are implementable
- Technical specifications are complete
- Dependencies are documented
- Risks have mitigations

**Layer Assignments**: L1 BRD, L2 PRD, L3 EARS, L4 BDD, L5 ADR, L6 SYS, L7 REQ, L8 CTR, L9 SPEC, L10 TSPEC

---

### 5. STRATEGIST

**Focus**: Economics, trade-offs, long-term viability

**Contribution**:
- Analyze cost-benefit trade-offs
- Document strategic alignment
- Identify market considerations
- Assess long-term implications

**Quality Gate**:
- Economic assumptions are validated
- Trade-offs are explicitly documented
- Strategic fit is justified
- Risk-reward is balanced

**Layer Assignments**: L1 BRD, L2 PRD, L5 ADR

---

### 6. QA_LEAD

**Focus**: Testability, quality assurance, coverage

**Contribution**:
- Define test strategies
- Specify acceptance criteria
- Document quality gates
- Identify test scenarios

**Quality Gate**:
- Requirements are testable
- Acceptance criteria are measurable
- Test coverage is comprehensive
- Quality metrics are defined

**Layer Assignments**: L2 PRD, L3 EARS, L4 BDD, L6 SYS, L7 REQ, L10 TSPEC

---

### 7. UX_STRATEGIST

**Focus**: User experience, accessibility, usability

**Contribution**:
- Define user journeys
- Specify accessibility requirements
- Document usability criteria
- Identify friction points

**Quality Gate**:
- User needs are addressed
- Accessibility is considered
- Usability is measurable
- Edge cases are covered

**Layer Assignments**: L2 PRD

---

### 8. REQUIREMENTS_SPECIALIST

**Focus**: EARS/INCOSE syntax, atomic structure

**Contribution**:
- Ensure syntax compliance
- Validate atomic structure
- Check traceability
- Verify completeness

**Quality Gate**:
- EARS syntax is correct
- Requirements are atomic
- All categories are covered
- IDs are properly assigned

**Layer Assignments**: L3 EARS, L7 REQ

---

### 9. DEVILS_ADVOCATE

**Focus**: Edge cases, failure modes, assumptions

**Contribution**:
- Identify failure scenarios
- Challenge assumptions
- Document edge cases
- Highlight gaps

**Quality Gate**:
- Failure modes are addressed
- Assumptions are explicit
- Edge cases are documented
- Gaps are flagged

**Layer Assignments**: L3 EARS, L4 BDD, L5 ADR, L6 SYS

---

### 10. OPERATOR

**Focus**: Observability, deployment, operations

**Contribution**:
- Define operational requirements
- Specify monitoring needs
- Document deployment constraints
- Identify SLI/SLO requirements

**Quality Gate**:
- Observability is specified
- Deployment is documented
- Operations are considered
- SLIs/SLOs are defined

**Layer Assignments**: L4 BDD, L5 ADR, L6 SYS, L9 SPEC, L10 TSPEC

---

### 11. INTEGRATION_EXPERT

**Focus**: Dependencies, contracts, interfaces

**Contribution**:
- Document external dependencies
- Specify interface contracts
- Define integration patterns
- Identify coupling risks

**Quality Gate**:
- Dependencies are explicit
- Contracts are complete
- Interfaces are versioned
- Coupling is minimized

**Layer Assignments**: L6 SYS, L7 REQ, L8 CTR, L9 SPEC

---

## Layer-to-Persona Mapping

| Layer | Document | Author Personas |
|-------|----------|-----------------|
| L1 | BRD | architect, product_owner, business_analyst, strategist, tech_lead |
| L2 | PRD | product_owner, ux_strategist, tech_lead, qa_lead, architect |
| L3 | EARS | requirements_specialist, tech_lead, qa_lead, chaos_engineer |
| L4 | BDD | qa_lead, tech_lead, chaos_engineer, operator |
| L5 | ADR | architect, tech_lead, strategist, chaos_engineer, operator |
| L6 | SYS | architect, tech_lead, operator, integration_expert |
| L7 | REQ | requirements_specialist, tech_lead, integration_expert |
| L8 | CTR | architect, tech_lead, integration_expert |
| L9 | SPEC | tech_lead, architect, operator, integration_expert |
| L10 | TSPEC | qa_lead, tech_lead, operator |

---

## Collaboration Protocol

### During Document Creation

1. **Lead Persona First**: The primary persona for the layer initiates content
2. **Expert Review**: Each persona reviews sections in their domain
3. **Cross-Validation**: Chaos Engineer challenges all assumptions
4. **Integration Check**: Integration Expert validates cross-references
5. **Final Synthesis**: All personas approve final content

### Quality Gates

Each section must pass:
- [ ] Primary persona approval
- [ ] Domain expert review
- [ ] Chaos Engineer challenge
- [ ] Cross-reference validation
