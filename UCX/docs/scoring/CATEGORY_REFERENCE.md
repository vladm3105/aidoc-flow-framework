# UCX Category Reference

Complete reference for scoring categories, element codes, and keywords.

---

## Category Definitions

### CAT-01: Functional (functional)

**Description**: Functional requirements completeness - coverage of features, capabilities, and use cases.

**Element Codes**: 01, 22, 24

**Keywords**:
- functional
- feature
- capability
- use case
- user story

**Primary Personas**: Product Owner, Tech Lead, Business Analyst

**Examples**:
- Missing user authentication feature
- Incomplete payment flow specification
- Undefined error handling for transactions

---

### CAT-02: Quality (quality)

**Description**: Quality attributes coverage - non-functional requirements like performance, security, reliability.

**Element Codes**: 02, 91, 92, 93, 94, 95, 96, 97, 98, 99

**Keywords**:
- performance
- scalability
- reliability
- availability
- maintainability
- security
- usability
- portability

**Primary Personas**: Architect, Operator, Tech Lead

**Examples**:
- No performance benchmarks defined
- Missing scalability requirements
- Undefined availability SLA

---

### CAT-03: Compliance (compliance)

**Description**: Regulatory and compliance requirements - industry-specific regulations and standards.

**Element Codes**: None (cross-cutting, keyword-matched)

**Default Keywords (Fintech)**:
- FinCEN, OFAC, PCI-DSS, AML, KYC, SAR, CTR, MTL
- BSA, FFIEC, SOX, GLBA
- GDPR, CCPA, SOC2, ISO27001
- compliance, regulatory, regulation, mandate, license

**Primary Personas**: Auditor

**Examples**:
- Missing KYC verification requirements
- SAR reporting process undefined
- No PCI-DSS compliance mention for card data

**Industry Templates**:
- `fintech_compliance` - Financial services
- `healthcare_compliance` - HIPAA, FDA
- `general_compliance` - GDPR, SOC2
- `government_compliance` - FedRAMP, FISMA

---

### CAT-04: Constraints (constraints)

**Description**: Constraints and assumptions - project boundaries, limitations, and prerequisites.

**Element Codes**: 03, 04

**Keywords**:
- constraint
- assumption
- limitation
- boundary
- scope
- prerequisite
- dependency

**Primary Personas**: Business Analyst, Strategist

**Examples**:
- Unstated budget constraint
- Undefined technology assumption
- Missing timeline limitation

---

### CAT-05: Integration (integration)

**Description**: Dependencies and integrations - external systems, APIs, and partner connections.

**Element Codes**: 05, 16, 20

**Keywords**:
- integration
- interface
- API
- dependency
- external
- third-party
- partner
- connector
- webhook

**Primary Personas**: Integration Lead, Architect

**Examples**:
- Undefined partner API contract
- Missing external system dependency
- Webhook payload not specified

---

### CAT-06: Acceptance (acceptance)

**Description**: Acceptance criteria and testability - measurable criteria for requirement satisfaction.

**Element Codes**: 06, 14, 40, 41, 42, 43, 44, 45

**Keywords**:
- acceptance
- test
- testable
- measurable
- verifiable
- criteria
- validation
- verification
- BDD
- scenario

**Primary Personas**: Product Owner, Integration Lead, Tech Lead

**Examples**:
- No acceptance criteria defined
- Criteria not measurable
- Missing test scenarios

---

### CAT-07: Risk (risk)

**Description**: Risk identification and mitigation - threats, vulnerabilities, and contingencies.

**Element Codes**: 07

**Keywords**:
- risk
- mitigation
- contingency
- threat
- vulnerability
- impact
- likelihood
- severity

**Primary Personas**: Strategist, Auditor, Operator

**Examples**:
- Unidentified security risk
- Missing mitigation strategy
- No contingency plan

---

### CAT-08: Architecture (architecture)

**Description**: Architecture decisions - system design, patterns, and component structure.

**Element Codes**: 10, 12, 13, 32

**Keywords**:
- architecture
- decision
- ADR
- design
- pattern
- component
- module
- system
- structure

**Primary Personas**: Architect, Strategist

**Examples**:
- Missing ADR for technology choice
- Undefined system component
- No design pattern specified

---

### CAT-99: Other (other)

**Description**: Findings that could not be categorized - fallback for uncategorizable items.

**Element Codes**: None

**Keywords**: None

**Weight**: 0% (tracked but doesn't affect score)

**Note**: Findings in this category indicate a gap in category mapping. Review persona prompts to improve categorization.

---

## Element Code Mapping

### Full Element Code Table

| Code | Category | Description |
|------|----------|-------------|
| 01 | functional | Functional requirements |
| 02 | quality | Quality attributes |
| 03 | constraints | Constraints |
| 04 | constraints | Assumptions |
| 05 | integration | Dependencies |
| 06 | acceptance | Acceptance criteria |
| 07 | risk | Risks |
| 10 | architecture | Architecture overview |
| 12 | architecture | System components |
| 13 | architecture | Component interactions |
| 14 | acceptance | User acceptance |
| 16 | integration | External interfaces |
| 20 | integration | Integration points |
| 22 | functional | Use cases |
| 24 | functional | User stories |
| 32 | architecture | Design decisions |
| 40-45 | acceptance | Test specifications |
| 91-99 | quality | Quality sub-attributes |

### Quality Sub-Attributes (91-99)

| Code | Attribute |
|------|-----------|
| 91 | Performance |
| 92 | Scalability |
| 93 | Availability |
| 94 | Reliability |
| 95 | Security |
| 96 | Maintainability |
| 97 | Portability |
| 98 | Operability |
| 99 | Other quality |

---

## Keyword Lists by Industry

### Fintech (Default)

```yaml
compliance:
  keywords:
    - FinCEN
    - OFAC
    - PCI-DSS
    - AML
    - KYC
    - SAR
    - CTR
    - MTL
    - BSA
    - FFIEC
    - SOX
    - GLBA
```

### Healthcare

```yaml
compliance:
  keywords:
    - HIPAA
    - PHI
    - ePHI
    - BAA
    - HITECH
    - FDA
    - 21 CFR Part 11
    - CLIA
```

### Government

```yaml
compliance:
  keywords:
    - FedRAMP
    - FISMA
    - NIST 800-53
    - FIPS
    - IL4
    - IL5
    - ITAR
    - EAR
```

### General Technology

```yaml
compliance:
  keywords:
    - GDPR
    - CCPA
    - SOC2
    - ISO27001
    - PII
    - encryption
    - audit
```

---

## Category Detection Algorithm

```python
def categorize_finding(finding) -> Category:
    # 1. Check explicit tag [CAT:xxx]
    if finding.raw_category_tag:
        return get_category_by_name(finding.raw_category_tag)

    # 2. Check element code in ID
    element_code = extract_element_code(finding.id)
    if element_code:
        category = categorize_by_element_code(element_code)
        if category:
            return category

    # 3. Check keywords in text
    category = categorize_by_keyword(finding.text)
    if category:
        return category

    # 4. Use persona default
    category = get_persona_primary_category(finding.persona)
    if category:
        return category

    # 5. Fallback
    return Category.OTHER
```

---

*Version: 1.12.0 | Created: 2026-03-12*
