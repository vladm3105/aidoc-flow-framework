# UCX Persona → Category Mapping

How review personas map to scoring categories.

---

## Overview

Each UCX review persona has primary and secondary category assignments. When a finding cannot be categorized by element code or keyword, the persona's primary category is used as fallback.

---

## Persona Mapping Table

| Persona | Primary Categories | Secondary | Finding Prefix |
|---------|-------------------|-----------|----------------|
| Architect | architecture, quality, integration | functional | `ARCH-` |
| Auditor | compliance, constraints, risk | - | `AUD-` |
| Tech Lead | functional, quality, integration | acceptance | `TL-` |
| Strategist | constraints, risk, architecture | functional | `STRAT-` |
| Devil's Advocate | (all - validation role) | - | `DA-` |
| Operator | quality (ops-focused), risk | - | `OPS-` |
| Integration Lead | integration, acceptance | functional | `INT-` |
| Product Owner | functional, acceptance | constraints | `PO-` |
| Business Analyst | constraints, functional | risk | `BA-` |
| Fact Checker | (cross-validation role) | - | `FC-` |
| Chairperson | (synthesis only) | - | - |

---

## Detailed Persona Assignments

### Architect

**Role**: System design, architecture decisions, technical patterns

**Primary Categories**:
1. **architecture** (CAT-08): ADRs, design patterns, system structure
2. **quality** (CAT-02): Performance, scalability, reliability
3. **integration** (CAT-05): System integration, interfaces

**Secondary Categories**:
- functional (CAT-01): Feature architecture impact

**Finding Examples**:
- `ARCH-P0-001`: Missing failover architecture
- `ARCH-P1-002`: Scalability approach undefined

---

### Auditor

**Role**: Compliance verification, regulatory requirements, audit trails

**Primary Categories**:
1. **compliance** (CAT-03): Regulatory requirements, standards
2. **constraints** (CAT-04): Compliance constraints, limitations
3. **risk** (CAT-07): Compliance risks, audit findings

**Secondary Categories**: None

**Finding Examples**:
- `AUD-P0-001`: SAR reporting not addressed
- `AUD-P0-002`: KYC verification incomplete

---

### Tech Lead

**Role**: Technical implementation, code quality, team alignment

**Primary Categories**:
1. **functional** (CAT-01): Feature implementation
2. **quality** (CAT-02): Code quality, maintainability
3. **integration** (CAT-05): API implementation, dependencies

**Secondary Categories**:
- acceptance (CAT-06): Technical acceptance criteria

**Finding Examples**:
- `TL-P0-001`: API contract undefined
- `TL-P1-002`: Error handling not specified

---

### Strategist

**Role**: Business strategy, constraints, risk assessment

**Primary Categories**:
1. **constraints** (CAT-04): Business constraints, scope
2. **risk** (CAT-07): Strategic risks, market risks
3. **architecture** (CAT-08): Strategic architecture decisions

**Secondary Categories**:
- functional (CAT-01): Strategic feature priorities

**Finding Examples**:
- `STRAT-P0-001`: Budget constraint not documented
- `STRAT-P1-002`: Market risk unaddressed

---

### Devil's Advocate

**Role**: Challenge assumptions, stress test requirements

**Primary Categories**: All (validation role)

**Secondary Categories**: None

**Behavior**: Validates findings from other personas, assigns most relevant category based on finding content.

**Finding Examples**:
- `DA-P1-001`: Assumption contradicts constraint
- `DA-P2-002`: Edge case not considered

---

### Operator

**Role**: Operations, deployment, monitoring, support

**Primary Categories**:
1. **quality** (CAT-02): Operability (91, 92, 93, 98)
2. **risk** (CAT-07): Operational risks

**Secondary Categories**: None

**Quality Sub-Focus**:
- 91: Performance monitoring
- 92: Scalability operations
- 93: Availability/uptime
- 98: Operability

**Finding Examples**:
- `OPS-P0-001`: No monitoring defined
- `OPS-P1-002`: Deployment rollback not specified

---

### Integration Lead

**Role**: External integrations, partner connections, APIs

**Primary Categories**:
1. **integration** (CAT-05): External systems, partners
2. **acceptance** (CAT-06): Integration testing

**Secondary Categories**:
- functional (CAT-01): Integration features

**Finding Examples**:
- `INT-P0-001`: Partner API contract missing
- `INT-P1-002`: Webhook retry logic undefined

---

### Product Owner

**Role**: Product features, user value, acceptance

**Primary Categories**:
1. **functional** (CAT-01): Product features, user stories
2. **acceptance** (CAT-06): User acceptance criteria

**Secondary Categories**:
- constraints (CAT-04): Product constraints

**Finding Examples**:
- `PO-P0-001`: User story incomplete
- `PO-P1-002`: Acceptance criteria missing

---

### Business Analyst

**Role**: Business requirements, constraints, process

**Primary Categories**:
1. **constraints** (CAT-04): Business constraints, assumptions
2. **functional** (CAT-01): Business features

**Secondary Categories**:
- risk (CAT-07): Business risks

**Finding Examples**:
- `BA-P0-001`: Business rule undefined
- `BA-P1-002`: Process flow missing

---

### Fact Checker

**Role**: Verify accuracy, cross-reference, consistency

**Primary Categories**: None (cross-validation role)

**Behavior**: Validates facts across personas, verifies category assignments from other personas.

**Finding Examples**:
- `FC-P1-001`: Inconsistency between sections
- `FC-P2-002`: Reference incorrect

---

### Chairperson

**Role**: Synthesis, final report, manifest generation

**Primary Categories**: None (synthesis only)

**Behavior**: Aggregates findings, calculates scores, generates manifest. Does not generate findings.

---

## Category Tag Requirements

All non-synthesis personas must include category tags in their findings:

### Required Format

```
[CAT:category_name] Finding description

Example:
[CAT:compliance] KYC verification process lacks document retention requirements
```

### Valid Category Tags

- `[CAT:functional]`
- `[CAT:quality]`
- `[CAT:compliance]`
- `[CAT:constraints]`
- `[CAT:integration]`
- `[CAT:acceptance]`
- `[CAT:risk]`
- `[CAT:architecture]`

### Tag Placement

Tags can appear:
- At the beginning of the finding
- Within the finding text
- At the end of the finding

The scoring system will extract and remove the tag before processing.

---

## Fallback Resolution

When categorizing a finding:

1. **Explicit tag** `[CAT:xxx]` → Use tag
2. **Element code** in ID → Use code mapping
3. **Keyword** in text → Use keyword mapping
4. **Persona default** → Use first primary category
5. **Fallback** → Assign to `other` (0% weight)

---

*Version: 1.12.0 | Created: 2026-03-12*
