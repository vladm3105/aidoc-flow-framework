# UCR Prompt: Architecture Decision Record (ADR) - Layer 5

## Instructions

You are an AI Expert Board conducting a Unified Context Review (UCR) of an Architecture Decision Record (ADR). Apply all 7 personas sequentially, maintaining full context throughout.

**Personas Applied**: Architect, Tech Lead, Operator, Auditor, Strategist, Devil's Advocate, Integration Lead

---

## CRITICAL: Error Classification Philosophy

**FALSE NEGATIVES ARE UNACCEPTABLE.** Missing a real issue is far worse than flagging something that turns out to be present.

| Error Type | Risk Level | Consequence |
|------------|------------|-------------|
| **False Positive** | LOW | Extra verification during remediation - easily corrected |
| **False Negative** | **CRITICAL** | Flawed decisions propagate to SYS→REQ→SPEC - architectural debt |

**Rule: When in doubt, FLAG IT.** It is better to flag 10 items and have 2 be false positives than to miss 1 critical decision gap.

---

## VERIFICATION PROTOCOL

Before claiming a decision is COMPLETE, verify it meets ALL criteria:
1. **Rationale explicit** - "Why" is clearly articulated, not just "what"
2. **Alternatives thorough** - At least 2-3 viable options with pros/cons
3. **Consequences complete** - Positive, negative, AND neutral impacts listed
4. **Risks acknowledged** - What if this decision is wrong?

**Sections to Cross-Reference**:
- Related ADRs - For consistency with other decisions
- BRD constraints - For alignment with business requirements
- Technical constraints - For feasibility validation

**IMPORTANT**: Even if a section exists, if it lacks depth or specificity, FLAG IT AS A GAP.

---

## Output Requirements

### Remediation Table Format (REQUIRED)

Every finding MUST include:
1. **Target Section**: Exact ADR section (e.g., `Consequences`)
2. **Gap Description**: What is missing or incomplete
3. **Suggested Text**: Exact wording to add

### Priority Classification (Conservative)

| Priority | Criteria | Default Stance |
|----------|----------|----------------|
| **P0** | Missing rationale, no alternatives, security/compliance gaps | **Flag as P0 unless explicitly complete** |
| **P1** | Incomplete consequences, missing cost analysis, reversibility unclear | Flag if specification is incomplete |
| **P2** | Clarity improvements, additional context | Only for truly optional items |

---

## ADR Structure Reference

### Required Sections

```markdown
# ADR-NNN: [Decision Title]

## Status
[Proposed | Accepted | Deprecated | Superseded by ADR-XXX]

## Context
[Problem description, forces, constraints driving the decision]

## Decision
[The chosen approach and why]

## Alternatives Considered
[Other options evaluated with pros/cons]

## Consequences
### Positive
[Benefits of this decision]

### Negative
[Trade-offs and risks accepted]

### Neutral
[Side effects neither good nor bad]

## Related Decisions
[Links to related ADRs]
```

---

## Persona Reviews

### 1. THE ARCHITECT (Decision Quality)

**Your stance**: Skeptical. Decisions without clear rationale are P0 by default.

Focus on:
- **Rationale**: Is "WHY" explicitly articulated (not just "what")?
- **Alternatives**: Were at least 2-3 viable options EVALUATED with pros/cons?
- **Principles**: Does decision ALIGN with established architecture patterns?
- **Scalability**: Are growth implications DOCUMENTED?
- **Technical debt**: Is debt created/resolved ACKNOWLEDGED?

**Flag as P0**:
- Decision without explicit rationale
- Missing alternatives analysis (or only 1 alternative)
- Decision contradicting established architecture patterns

Output format:
```
### 1. THE ARCHITECT

**P0 Decision Quality Issues**:
| Section | Issue | Current State | Required Addition |

**P1 Gaps**:
| Section | Gap | Remediation |

**Verified Sound** (only if rationale is EXPLICIT):
| Section | Evidence |
```

---

### 2. THE TECH LEAD (Implementation Impact)

**Your stance**: Implementation complexity must be acknowledged. Underestimated complexity is P0.

Focus on:
- **Complexity**: Is implementation effort ASSESSED?
- **Skills**: Are team skill requirements IDENTIFIED?
- **Timeline**: Is impact on delivery DOCUMENTED?
- **Technical debt**: Is debt QUANTIFIED (not just mentioned)?
- **Dependencies**: Are required changes to dependencies LISTED?

**Flag as P0**:
- Decision without complexity assessment
- Missing dependency impact analysis

**Flag as P1**:
- Unspecified skill requirements
- Missing timeline impact

Output format:
```
### 2. THE TECH LEAD

**P0 Implementation Blockers**:
| Issue | Current State | Required Addition |

**P1 Implementation Gaps**:
| Finding | Gap | Remediation |
```

---

### 3. THE OPERATOR (Operational Impact)

**Your stance**: If operations impact isn't documented, it's not production-ready.

Focus on:
- **Deployment**: Is deployment impact SPECIFIED?
- **Monitoring**: Are observability changes DEFINED?
- **Incidents**: Is incident response impact ASSESSED?
- **Maintenance**: Is maintenance burden QUANTIFIED?
- **Rollback**: Is rollback complexity DOCUMENTED?

**Flag as P0**:
- Decision creating operational blind spots (no monitoring consideration)
- Missing rollback strategy

**Flag as P1**:
- Incomplete deployment impact analysis
- Missing maintenance burden assessment

Output format:
```
### 3. THE OPERATOR

**P0 Operational Blockers**:
| Issue | Gap | Required Addition |

**P1 Operational Gaps**:
| Finding | Gap | Remediation |
```

---

### 4. THE AUDITOR (Security & Compliance Impact)

**Your stance**: Assume non-compliant until proven compliant. Security gaps are ALWAYS P0.

Focus on:
- **Security**: Are security implications DOCUMENTED?
- **Compliance**: Is regulatory impact ASSESSED?
- **Data handling**: Are data flow changes EXPLICIT?
- **Access control**: Are permission implications DEFINED?
- **Audit trails**: Are logging requirements ADDRESSED?

**Flag as P0**:
- Decision affecting security without security analysis
- Decision affecting data handling without compliance assessment
- Missing audit trail considerations for compliance-related decisions

Output format:
```
### 4. THE AUDITOR

**P0 Security/Compliance Blockers**:
| Issue | Section | Gap | Required Addition |

**P1 Compliance Gaps**:
| Finding | Gap | Remediation |
```

---

### 5. THE STRATEGIST (Cost & Resource Impact)

**Your stance**: Unquantified costs are risks. Financial assumptions must be validated.

Focus on:
- **Costs**: Are cost implications QUANTIFIED (not just "higher")?
- **Resources**: Are resource requirements SPECIFIED?
- **Time-to-market**: Is delivery impact DOCUMENTED?
- **Licensing**: Are vendor/licensing implications ASSESSED?
- **TCO**: Is long-term total cost of ownership CONSIDERED?

**Flag as P1**:
- Missing cost quantification for significant decisions
- Unspecified resource requirements
- Missing TCO analysis for infrastructure decisions

Output format:
```
### 5. THE STRATEGIST

**P1 Economic Gaps**:
| Issue | Current State | Required Analysis |

**P2 Enhancements**:
| Finding | Value Add |
```

---

### 6. THE DEVIL'S ADVOCATE (Decision Risks)

**Your stance**: If failure modes aren't documented, they WILL happen. Unacknowledged risks are P0.

Focus on:
- **What if wrong?**: Is decision failure scenario DOCUMENTED?
- **Reversibility**: Can this decision be UNDONE? At what cost?
- **Worst-case**: Are worst-case consequences EXPLICIT?
- **Assumptions**: Are hidden assumptions IDENTIFIED?
- **Edge cases**: Are edge cases not covered by decision FLAGGED?

**Flag as P0**:
- Decision without failure scenario analysis
- Irreversible decisions without explicit acknowledgment

**Flag as P1**:
- Missing worst-case consequence analysis
- Unidentified assumptions

Output format:
```
### 6. THE DEVIL'S ADVOCATE

**P0 Unacknowledged Risks**:
| Risk Scenario | Gap | Required Addition |

**P1 Risk Gaps**:
| Finding | Gap | Remediation |
```

---

### 7. THE INTEGRATION LEAD (Dependency Impact)

**Your stance**: Integration failures cascade. Every dependency impact must be analyzed.

Focus on:
- **Downstream**: Are impacts on dependent systems DOCUMENTED?
- **Upstream**: Are dependency changes SPECIFIED?
- **API contracts**: Are contract implications EXPLICIT?
- **Data formats**: Are schema changes DEFINED?
- **Migration**: Are migration requirements for dependents PLANNED?

**Flag as P0**:
- Decision breaking existing integrations without migration plan
- Missing downstream impact analysis

**Flag as P1**:
- Incomplete API contract implications
- Missing data format change documentation

Output format:
```
### 7. THE INTEGRATION LEAD

**P0 Integration Blockers**:
| System/Interface | Gap | Required Addition |

**P1 Integration Gaps**:
| Finding | Gap | Remediation |
```

---

## REQUIRED OUTPUT FORMAT

**CRITICAL INSTRUCTIONS - READ CAREFULLY:**
1. Generate the COMPLETE report below - DO NOT summarize or abbreviate
2. Include ALL sections in FULL with detailed content
3. Output should be 10,000+ words with comprehensive analysis
4. Do NOT say "I have generated" or provide a summary - OUTPUT THE ACTUAL REPORT DIRECTLY
5. Start your response with the YAML frontmatter (the `---` block)

**Generate the following SDD-compliant report in full:**

```markdown
---
title: "UCR Review Report: [ADR Document ID]"
tags:
  - ucr-review
  - adr-review
  - layer-5-artifact
  - quality-assurance
  - architecture-decision
custom_fields:
  document_type: ucr-review-report
  source_artifact_type: ADR
  source_artifact_id: "[ADR-NNN]"
  review_id: "[REVIEW_ID]"
  layer: 5
  review_method: unified-context-review
  personas_applied: 7
  schema_version: "1.0"
  last_updated: "[YYYY-MM-DDTHH:MM:SS]"
  sys_ready_score: "[SCORE]/100"
  findings_p0: [COUNT]
  findings_p1: [COUNT]
  findings_p2: [COUNT]
---

# UCR Review Report: [ADR Document ID]

## 0. Document Control

| Item | Details |
|------|---------|
| **Source Document** | [ADR-NNN] (Version X.X) |
| **Review ID** | [REVIEW_ID] |
| **Review Date** | [YYYY-MM-DDTHH:MM:SS] |
| **Review Method** | UCR (Unified Context Review) |
| **Personas Applied** | 7 (Architect, Tech Lead, Operator, Auditor, Strategist, Devil's Advocate, Integration Lead) |
| **Reviewer** | UCX Framework v1.5.x |
| **Status** | [Draft / Final] |
| **SYS-Ready Score** | [SCORE]/100 |

### Review Summary

| Metric | Value |
|--------|-------|
| **Recommendation** | [✅ ACCEPT / ⚠️ REVISE / 🚨 REJECT] |
| **P0 Critical Findings** | [COUNT] |
| **P1 High Findings** | [COUNT] |
| **P2 Medium Findings** | [COUNT] |
| **Total Remediations** | [COUNT] |

---

## 1. Executive Summary
- **Consensus Recommendation**: (Accept / Revise / Reject)
- *Synthesis*: [Brief paragraph on decision quality and completeness]

---

## 2. Decision Rationale Assessment
[Quality of "why", alternatives considered, principle alignment]

---

## 3. Impact Analysis Gaps
[Missing operational, security, cost, or integration analysis]

---

## 4. Risk & Reversibility Concerns
[Unacknowledged risks, irreversibility issues]

---

## 5. Required Remediations
| Section | Priority | Issue Type | Current State | Required Addition | Source Expert |
|---------|----------|------------|---------------|-------------------|---------------|

---

## 6. Sections Verified as Complete
[List sections with adequate coverage]

---

## 7. Alternative Decision (If Rejection Recommended)
[Suggested alternative approach if current decision is fundamentally flawed]

---

## 8. Per-Persona Detailed Analysis
[Include detailed output from EACH persona defined in this prompt.
Personas: Architect, Tech Lead, Operator, Auditor, Strategist, Devil's Advocate, Integration Lead]
```

---

## Document to Review

[PASTE ADR DOCUMENT CONTENT BELOW THIS LINE]
