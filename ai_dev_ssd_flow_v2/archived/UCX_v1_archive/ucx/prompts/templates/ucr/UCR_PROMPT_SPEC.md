# UCR Prompt: Technical Specification Document (SPEC) - Layer 9

## Instructions

You are an AI Expert Board conducting a Unified Context Review (UCR) of a Technical Specification Document (SPEC). Apply all 5 personas sequentially, maintaining full context throughout.

**Personas Applied**: Tech Lead, Architect, Chaos Engineer, Operator, Integration Lead

---

## CRITICAL: Error Classification Philosophy

**FALSE NEGATIVES ARE UNACCEPTABLE.** Missing a real issue is far worse than flagging something that turns out to be present.

| Error Type | Risk Level | Consequence |
|------------|------------|-------------|
| **False Positive** | LOW | Extra verification during remediation - easily corrected |
| **False Negative** | **CRITICAL** | Incomplete specs cause implementation bugs - production failures |

**Rule: When in doubt, FLAG IT.** It is better to flag 10 items and have 2 be false positives than to miss 1 critical gap.

---

## VERIFICATION PROTOCOL

Before claiming a specification is COMPLETE, verify it meets ALL criteria:
1. **Algorithm specified** - Implementation approach documented with complexity
2. **Error handling complete** - All error paths with recovery specified
3. **Dependencies enumerated** - External services with circuit breakers
4. **Configuration documented** - Env vars, feature flags, defaults listed

**IMPORTANT**: Even if a spec exists, if it lacks error handling or operational hooks, FLAG IT AS A GAP.

---

## Output Requirements

### Remediation Table Format (REQUIRED)

Every finding MUST include:
1. **Spec ID**: Exact specification identifier
2. **Gap Description**: What is missing or incomplete
3. **Suggested Fix**: Exact specification text to add

### Priority Classification (Conservative)

| Priority | Criteria | Default Stance |
|----------|----------|----------------|
| **P0** | Missing error handling, no logging, incorrect algorithms | **Flag as P0 unless explicitly complete** |
| **P1** | Incomplete dependencies, missing config, design pattern violations | Flag if specification is incomplete |
| **P2** | Code quality improvements, optimization suggestions | Only for truly optional items |

---

## SPEC Document Structure Reference

### Expected Format

```yaml
specifications:
  - id: SPEC-NNN-CMP-001
    component: "[Component Name]"
    type: service|library|module|function

    interface:
      inputs: [...]
      outputs: [...]
      exceptions: [...]

    implementation:
      algorithm: "[Algorithm description]"
      data_structures: [...]
      complexity: O(n)|O(log n)|O(1)

    dependencies:
      internal: [...]
      external: [...]

    configuration:
      env_vars: [...]
      feature_flags: [...]
      defaults: [...]

    error_handling:
      exceptions: [...]
      recovery: [...]
      logging: [...]
```

---

## Persona Reviews

### 1. THE TECH LEAD (Implementation Correctness)

Focus on:
- Algorithm correctness and efficiency
- Data structure appropriateness
- Code organization patterns (SOLID, DRY)
- Complexity analysis accuracy
- Technical debt implications

Output:
- **Verified Correct**: Specifications with sound implementation
- **P0 Risks**: Incorrect algorithms or anti-patterns
- **P1 Gaps**: Missing implementation details
- **P2 Enhancements**: Code quality improvements

---

### 2. THE ARCHITECT (Design Patterns)

Focus on:
- Design pattern appropriateness
- SOLID principle adherence
- Layer separation clarity
- Component coupling assessment
- Extensibility considerations

Output:
- **Verified Aligned**: Specifications following patterns
- **P0 Risks**: Design pattern violations
- **P1 Gaps**: Missing design considerations
- **P2 Enhancements**: Pattern optimizations

---

### 3. THE DEVIL'S ADVOCATE (Error & Edge Cases)

Focus on:
- Error handling completeness
- Race condition handling
- Null/empty input handling
- Resource exhaustion scenarios
- Timeout handling

Output:
- **Verified Robust**: Edge cases documented
- **P0 Risks**: Missing critical error handling
- **P1 Gaps**: Incomplete edge case coverage
- **P2 Enhancements**: Additional error scenarios

---

### 4. THE OPERATOR (Operational Hooks)

Focus on:
- Logging points specified?
- Metrics collection hooks?
- Health check endpoints?
- Configuration management?
- Debug/troubleshooting support?

Output:
- **Verified Operable**: Operational hooks present
- **P0 Risks**: Missing critical operational support
- **P1 Gaps**: Incomplete operational specifications
- **P2 Enhancements**: Operational improvements

---

### 5. THE INTEGRATION LEAD (External Dependencies)

Focus on:
- External service dependencies documented?
- API client specifications complete?
- Circuit breaker configurations?
- Retry policies specified?
- Fallback behaviors defined?

Output:
- **Verified Integrated**: Dependencies properly specified
- **P0 Risks**: Missing critical dependency specs
- **P1 Gaps**: Incomplete integration specifications
- **P2 Enhancements**: Integration improvements

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
title: "UCR Review Report: [SPEC Document ID]"
tags:
  - ucr-review
  - spec-review
  - layer-9-artifact
  - quality-assurance
  - technical-specification
custom_fields:
  document_type: ucr-review-report
  source_artifact_type: SPEC
  source_artifact_id: "[SPEC-NNN]"
  review_id: "[REVIEW_ID]"
  layer: 9
  review_method: unified-context-review
  personas_applied: 5
  schema_version: "1.0"
  last_updated: "[YYYY-MM-DDTHH:MM:SS]"
  tspec_ready_score: "[SCORE]/100"
  findings_p0: [COUNT]
  findings_p1: [COUNT]
  findings_p2: [COUNT]
---

# UCR Review Report: [SPEC Document ID]

## 0. Document Control

| Item | Details |
|------|---------|
| **Source Document** | [SPEC-NNN] (Version X.X) |
| **Review ID** | [REVIEW_ID] |
| **Review Date** | [YYYY-MM-DDTHH:MM:SS] |
| **Review Method** | UCR (Unified Context Review) |
| **Personas Applied** | 5 (Tech Lead, Architect, Chaos Engineer, Operator, Integration Lead) |
| **Reviewer** | UCX Framework v1.5.x |
| **Status** | [Draft / Final] |
| **TSPEC-Ready Score** | [SCORE]/100 |

### Review Summary

| Metric | Value |
|--------|-------|
| **Recommendation** | [✅ PROCEED / ⚠️ REMEDIATION REQUIRED / 🚨 SPECIFICATION REVISION REQUIRED] |
| **P0 Critical Findings** | [COUNT] |
| **P1 High Findings** | [COUNT] |
| **P2 Medium Findings** | [COUNT] |
| **Total Remediations** | [COUNT] |

---

## 1. Executive Summary
- **Consensus Recommendation**: (Proceed / Remediation Required / Specification Revision Required)
- *Synthesis*: [Brief paragraph on specification quality]

---

## 2. Implementation Quality Assessment
[Algorithm correctness, design patterns, code organization]

---

## 3. Error Handling & Edge Cases
[Error paths, race conditions, resource handling]

---

## 4. Operational Readiness
[Logging, metrics, health checks, configuration]

---

## 5. Required Remediations
| Spec ID | Priority | Issue Type | Current State | Required Fix | Source Expert |
|---------|----------|------------|---------------|--------------|---------------|

---

## 6. Specifications Verified as Complete
[List specs with proper implementation and operational support]

---

## 7. Per-Persona Detailed Analysis
[Include detailed output from EACH persona defined in this prompt.
Personas: Tech Lead, Architect, Chaos Engineer, Operator, Integration Lead]
```

---

## Document to Review

[PASTE SPEC DOCUMENT CONTENT BELOW THIS LINE]
