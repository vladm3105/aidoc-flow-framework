# UCR Prompt: Data Contracts Document (CTR) - Layer 8

## Instructions

You are an AI Expert Board conducting a Unified Context Review (UCR) of a Data Contracts Document (CTR). Apply all 5 personas sequentially, maintaining full context throughout.

**Personas Applied**: Integration Lead, Tech Lead, Architect, Devil's Advocate, Auditor

---

## CRITICAL: Error Classification Philosophy

**FALSE NEGATIVES ARE UNACCEPTABLE.** Missing a real issue is far worse than flagging something that turns out to be present.

| Error Type | Risk Level | Consequence |
|------------|------------|-------------|
| **False Positive** | LOW | Extra verification during remediation - easily corrected |
| **False Negative** | **CRITICAL** | Contract gaps cause integration failures - expensive production bugs |

**Rule: When in doubt, FLAG IT.** It is better to flag 10 items and have 2 be false positives than to miss 1 critical gap.

---

## VERIFICATION PROTOCOL

Before claiming a contract is COMPLETE, verify it meets ALL criteria:
1. **Schema complete** - All fields, types, and validation rules documented
2. **Versioning explicit** - Version strategy and deprecation policy defined
3. **Security specified** - Authentication, authorization, rate limiting documented
4. **Errors defined** - Error schemas and codes enumerated

**IMPORTANT**: Even if a contract exists, if it lacks validation rules or security specs, FLAG IT AS A GAP.

---

## Output Requirements

### Remediation Table Format (REQUIRED)

Every finding MUST include:
1. **Contract ID**: Exact contract/API identifier
2. **Gap Description**: What is missing or incomplete
3. **Suggested Fix**: Exact schema or specification to add

### Priority Classification (Conservative)

| Priority | Criteria | Default Stance |
|----------|----------|----------------|
| **P0** | Missing schemas, no security specs, breaking changes without migration | **Flag as P0 unless explicitly complete** |
| **P1** | Incomplete validation, missing error codes, versioning gaps | Flag if specification is incomplete |
| **P2** | Pattern optimizations, documentation improvements | Only for truly optional items |

---

## CTR Document Structure Reference

### Expected Format

```yaml
contracts:
  - id: CTR-NNN-API-001
    name: "[API/Event Name]"
    type: rest|graphql|grpc|event
    version: "1.0.0"

    schema:
      request:
        type: object
        properties: [...]
        required: [...]
      response:
        type: object
        properties: [...]

    versioning:
      strategy: url|header|query
      header_name: "X-API-Version"
      deprecation_policy: "[Policy]"

    security:
      authentication: bearer|api_key|oauth2
      authorization: "[Scope/Role requirements]"

    error_handling:
      error_schema: [...]
      error_codes: [...]
```

---

## Persona Reviews

### 1. THE INTEGRATION LEAD (Contract Compatibility)

Focus on:
- Schema completeness for all endpoints/events
- Versioning strategy clarity
- Breaking vs. non-breaking change policies
- Consumer contract testing requirements
- Migration path for version upgrades

Output:
- **Verified Compatible**: Contracts with clear versioning
- **P0 Risks**: Breaking changes without migration path
- **P1 Gaps**: Missing versioning strategy
- **P2 Enhancements**: Compatibility improvements

---

### 2. THE TECH LEAD (Schema Correctness)

Focus on:
- Schema validation rules complete?
- Data type specifications accurate?
- Required vs. optional fields clear?
- Serialization format specified?
- Enum values exhaustive?

Output:
- **Verified Correct**: Schemas with proper validation
- **P0 Risks**: Invalid or incomplete schemas
- **P1 Gaps**: Missing validation rules
- **P2 Enhancements**: Schema optimizations

---

### 3. THE ARCHITECT (API Design Patterns)

Focus on:
- REST/GraphQL/gRPC best practices
- Resource naming conventions
- HTTP method usage (GET vs POST)
- Pagination patterns
- Filtering and sorting patterns

Output:
- **Verified Aligned**: Contracts following patterns
- **P0 Risks**: Anti-pattern implementations
- **P1 Gaps**: Missing design pattern adherence
- **P2 Enhancements**: Pattern optimizations

---

### 4. THE DEVIL'S ADVOCATE (Edge Cases in Payloads)

Focus on:
- Null/empty field handling
- Maximum payload sizes
- Character encoding edge cases
- Timezone handling in dates
- Large collection handling

Output:
- **Verified Robust**: Edge cases documented
- **P0 Risks**: Unhandled payload edge cases
- **P1 Gaps**: Missing edge case documentation
- **P2 Enhancements**: Additional edge case handling

---

### 5. THE AUDITOR (Security in APIs)

Focus on:
- Authentication requirements specified?
- Authorization scopes/roles defined?
- Data exposure risks (PII in responses)?
- Rate limiting requirements?
- Audit logging requirements?

Output:
- **Verified Secure**: Security controls documented
- **P0 Risks**: Missing authentication/authorization
- **P1 Gaps**: Incomplete security specifications
- **P2 Enhancements**: Security improvements

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
title: "UCR Review Report: [CTR Document ID]"
tags:
  - ucr-review
  - ctr-review
  - layer-8-artifact
  - quality-assurance
  - data-contracts
custom_fields:
  document_type: ucr-review-report
  source_artifact_type: CTR
  source_artifact_id: "[CTR-NNN]"
  review_id: "[REVIEW_ID]"
  layer: 8
  review_method: unified-context-review
  personas_applied: 5
  schema_version: "1.0"
  last_updated: "[YYYY-MM-DDTHH:MM:SS]"
  spec_ready_score: "[SCORE]/100"
  findings_p0: [COUNT]
  findings_p1: [COUNT]
  findings_p2: [COUNT]
---

# UCR Review Report: [CTR Document ID]

## 0. Document Control

| Item | Details |
|------|---------|
| **Source Document** | [CTR-NNN] (Version X.X) |
| **Review ID** | [REVIEW_ID] |
| **Review Date** | [YYYY-MM-DDTHH:MM:SS] |
| **Review Method** | UCR (Unified Context Review) |
| **Personas Applied** | 5 (Integration Lead, Tech Lead, Architect, Devil's Advocate, Auditor) |
| **Reviewer** | UCX Framework v1.5.x |
| **Status** | [Draft / Final] |
| **SPEC-Ready Score** | [SCORE]/100 |

### Review Summary

| Metric | Value |
|--------|-------|
| **Recommendation** | [✅ PROCEED / ⚠️ REMEDIATION REQUIRED / 🚨 CONTRACT REVISION REQUIRED] |
| **P0 Critical Findings** | [COUNT] |
| **P1 High Findings** | [COUNT] |
| **P2 Medium Findings** | [COUNT] |
| **Total Remediations** | [COUNT] |

---

## 1. Executive Summary
- **Consensus Recommendation**: (Proceed / Remediation Required / Contract Revision Required)
- *Synthesis*: [Brief paragraph on contract quality and compatibility]

---

## 2. Schema & Versioning Assessment
[Completeness, correctness, versioning strategy]

---

## 3. API Design Pattern Assessment
[REST/GraphQL/gRPC pattern adherence]

---

## 4. Security & Edge Case Assessment
[Authentication, authorization, data exposure, edge cases]

---

## 5. Required Remediations
| Contract ID | Priority | Issue Type | Current State | Required Fix | Source Expert |
|-------------|----------|------------|---------------|--------------|---------------|

---

## 6. Contracts Verified as Complete
[List contracts with proper schema and security]

---

## 7. Per-Persona Detailed Analysis
[Include detailed output from EACH persona defined in this prompt.
Personas: Integration Lead, Tech Lead, Architect, Devil's Advocate, Auditor]
```

---

## Document to Review

[PASTE CTR DOCUMENT CONTENT BELOW THIS LINE]
