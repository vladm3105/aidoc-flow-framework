---
title: "BDD Pre-Generation Checklist"
tags:
  - bdd-checklist
  - layer-4-artifact
  - shared-architecture
custom_fields:
  document_type: checklist
  artifact_type: BDD
  layer: 4
  priority: shared
  development_status: active
---

# =============================================================================
# 📋 Document Role: This is a DERIVATIVE of BDD-MVP-TEMPLATE.feature
# - Authority: BDD-MVP-TEMPLATE.feature is the single source of truth for BDD structure
# - Purpose: Pre-generation checklist to prevent common errors
# - Scope: Use BEFORE generating any BDD feature file
# - On conflict: Defer to BDD-MVP-TEMPLATE.feature
# =============================================================================
---
title: "BDD Pre-Generation Checklist"
tags:
  - pre-generation-checklist
  - layer-4-artifact
  - shared-architecture
custom_fields:
  document_type: pre-generation-checklist
  artifact_type: BDD
  layer: 4
  priority: shared
  development_status: active
---

# BDD Pre-Generation Checklist

**Version**: 1.0
**Date**: 2025-11-30
**Purpose**: Prevent common BDD generation errors by verifying requirements before creation
**Use Case**: Run this checklist BEFORE generating any BDD feature file

---

## Quick Reference: Critical Format Requirements

### ADR-Ready Score Format (MANDATORY)

```markdown
| **ADR-Ready Score** | ✅ 75% (Target: ≥90%) |
```

**Checklist**:
- [ ] Contains `✅` checkmark emoji at start of value
- [ ] Percentage is integer (1-100)
- [ ] Contains `≥` symbol before 90
- [ ] Format exactly: `✅ NN% (Target: ≥90%)`

### Feature-Level Tags Format (MANDATORY)

```gherkin
@brd:BRD.NN.01.SS
@prd:PRD.NN.EE.SS
@ears:EARS.NN.24.SS
Feature: [Feature Title]
```

**Checklist**:
- [ ] Tags are Gherkin-native (NOT in comments)
- [ ] Tags appear on separate lines BEFORE `Feature:` keyword
- [ ] All three tags present: @brd, @prd, @ears
- [ ] Extended format with unified TYPE.NN.TT.SS suffix (4-segment Unified Element ID)
- [ ] NO spaces after colon in tag (use `@brd:BRD.01.01.01` not `@brd: BRD.01.01.01`)

### AI-Agent Files Additional Requirements

```gherkin
@brd:BRD.NN.01.SS
@prd:PRD.NN.EE.SS
@ears:EARS.NN.24.SS
@ctr:CTR-005
Feature: [Agent Feature Title]
  Architecture: AI-Agent Primary (AGENT-NNN)
```

**Checklist**:
- [ ] Contains `@ctr:CTR-005` tag for A2A Protocol
- [ ] Document Control includes `Architecture: AI-Agent Primary (AGENT-NNN)`
- [ ] AGENT-NNN matches Agent ID Registry (see BDD_AI_AGENT_EXTENSION.md)

---

## Pre-Generation Verification Steps

### Step 1: Verify Upstream Artifacts Exist

Before generating a BDD file, confirm these documents exist:

```bash
# Check for required upstream artifacts
ls docs/01_BRD/BRD-NNN*.md   # Business Requirements
ls docs/02_PRD/PRD-NNN*.md   # Product Requirements
ls docs/03_EARS/EARS-NN*.md # Engineering Requirements
```

**Rules**:
- NEVER use placeholder IDs like `BRD-XXX` or `TBD`
- NEVER reference documents that don't exist
- If upstream artifact is missing, skip that functionality

### Step 2: Determine Architecture Type

| Question | If YES | If NO |
|----------|--------|-------|
| Does this feature use AI agents? | AI-Agent Primary | Traditional |
| Does it involve A2A Protocol? | Add `@ctr:CTR-005` | Skip CTR tag |
| Does it have ML inference? | Add ML scenarios | Skip ML scenarios |

### Step 3: Gather Required Information

**For ALL BDD files**:
- [ ] BRD document ID and requirement IDs
- [ ] PRD document ID and requirement IDs
- [ ] EARS document ID and requirement IDs
- [ ] Feature description (business capability)
- [ ] Stakeholder role for "As a..." statement
- [ ] Business benefit for "So that..." statement

**For AI-Agent BDD files (additional)**:
- [ ] Agent ID from registry (AGENT-001, AGENT-002, etc.)
- [ ] A2A Protocol requirements from CTR-005
- [ ] PRD entity references (if applicable)
- [ ] Threshold keys for performance scenarios

### Step 4: Plan Scenario Categories

Ensure all 8 categories are planned:

| Category | Tag | Minimum Scenarios |
|----------|-----|-------------------|
| Success Path | `@primary @functional` | 2 |
| Alternative Path | `@alternative @functional` | 1 |
| Error Path | `@negative @error_handling` | 3 |
| Edge Case | `@edge_case @boundary` | 2 |
| Data-Driven | `@data_driven` | 1 |
| Integration | `@integration @end_to_end` | 1 |
| Quality Attribute | `@quality_attribute` | 2 |
| Failure Recovery | `@failure_recovery @resilience` | 2 |

**Total minimum**: 14 scenarios per BDD file

---

## Template Selection Guide

### Traditional BDD File

Use `BDD-MVP-TEMPLATE.feature` directly.

**Copy-paste the following tags**:
```gherkin
@brd:BRD.NN.01.SS
@prd:PRD.NN.EE.SS
@ears:EARS.NN.24.SS
Feature: [Feature Title]
```

### AI-Agent Primary BDD File

Use `BDD-MVP-TEMPLATE.feature` + `BDD_AI_AGENT_EXTENSION.md`.

**Copy-paste the following tags**:
```gherkin
@brd:BRD.NN.01.SS
@prd:PRD.NN.EE.SS
@ears:EARS.NN.24.SS
@ctr:CTR-005
Feature: [Agent Feature Title]
  Architecture: AI-Agent Primary (AGENT-NNN)
```

**Required additional sections**:
- A2A Communication Scenarios
- ML Inference Scenarios (if ML-based)
- Model Drift Scenarios (if ML-based)
- Agent Fallback Scenarios

---

## Common Anti-Patterns to Avoid

### ❌ Anti-Pattern 1: Tags in Comments

```gherkin
# WRONG - frameworks cannot parse
# @brd: BRD.01.01.01
Feature: My Feature
```

```gherkin
# CORRECT - Gherkin-native tags
@brd:BRD.01.01.01
Feature: My Feature
```

### ❌ Anti-Pattern 2: ADR-Ready Score Wrong Format

```markdown
# WRONG - missing checkmark and ≥
| **ADR-Ready Score** | 75% (Target: 90%) |
```

```markdown
# CORRECT - with checkmark and ≥
| **ADR-Ready Score** | ✅ 75% (Target: ≥90%) |
```

### ❌ Anti-Pattern 3: Hardcoded Magic Numbers

```gherkin
# WRONG - hardcoded values
Then response time is less than 200ms
```

```gherkin
# CORRECT - threshold registry reference
Then response time is less than @threshold:PRD.035.perf.api.p95_latency
```

### ❌ Anti-Pattern 4: Wrong Step Order

```gherkin
# WRONG - When before Given
When I click submit
Given I am on the login page
Then I see an error
```

```gherkin
# CORRECT - Given → When → Then
Given I am on the login page
When I click submit
Then I see an error
```

---

## Post-Generation Verification

After generating a BDD file, run:

```bash
# Validate format compliance
./scripts/validate_bdd_format.sh docs/04_BDD/BDD-NN_{slug}/BDD-NN.SS_{slug}.feature

# Check for tags in comments (should return nothing)
grep -n "^#.*@brd:" docs/04_BDD/BDD-NN_*/BDD-NN*.feature
grep -n "^#.*@prd:" docs/04_BDD/BDD-NN_*/BDD-NN*.feature
grep -n "^#.*@ears:" docs/04_BDD/BDD-NN_*/BDD-NN*.feature

# Verify ADR-Ready Score format
grep "ADR-Ready Score" docs/04_BDD/BDD-NN_*/BDD-NN*.feature | grep -v "✅"
```

---

## Quick Validation Checklist

Before committing any BDD file, verify:

- [ ] Document Control table has 7 required fields
- [ ] ADR-Ready Score: `✅ NN% (Target: ≥90%)`
- [ ] Feature-level tags are Gherkin-native (not comments)
- [ ] All three upstream tags present: @brd, @prd, @ears
- [ ] For AI-agent: `@ctr:CTR-005` tag included
- [ ] For AI-agent: Architecture line in Document Control
- [ ] All 8 scenario categories represented
- [ ] @threshold tags used for quantitative values
- [ ] Gherkin syntax valid (Given → When → Then order)
- [ ] Scenario count matches what will be in index

---

**Maintained By**: Project Engineering Team
**Review Frequency**: Updated with BDD framework changes
