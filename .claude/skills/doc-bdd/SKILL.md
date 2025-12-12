---
title: "doc-bdd: Create BDD test scenarios (Layer 4)"
name: doc-bdd
description: Create BDD (Behavior-Driven Development) test scenarios - Layer 4 artifact using Gherkin Given-When-Then format
tags:
  - sdd-workflow
  - layer-4-artifact
  - shared-architecture
custom_fields:
  layer: 4
  artifact_type: BDD
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  skill_category: core-workflow
  upstream_artifacts: [BRD,PRD,EARS]
  downstream_artifacts: [ADR,SYS]
---

# doc-bdd

## Purpose

Create **BDD (Behavior-Driven Development)** test scenarios - Layer 4 artifact in the SDD workflow that defines executable test scenarios using Gherkin syntax.

**Layer**: 4

**Upstream**: BRD (Layer 1), PRD (Layer 2), EARS (Layer 3)

**Downstream Artifacts**: ADR (Layer 5), SYS (Layer 6), REQ (Layer 7)

## Prerequisites

### Upstream Artifact Verification (CRITICAL)

**Before creating this document, you MUST:**

1. **List existing upstream artifacts**:
   ```bash
   ls docs/BRD/ docs/PRD/ docs/EARS/ docs/BDD/ docs/ADR/ docs/SYS/ docs/REQ/ 2>/dev/null
   ```

2. **Reference only existing documents** in traceability tags
3. **Use `null`** only when upstream artifact type genuinely doesn't exist
4. **NEVER use placeholders** like `BRD-XXX` or `TBD`
5. **Do NOT create missing upstream artifacts** - skip functionality instead


Before creating BDD, read:

1. **Shared Standards**: `.claude/skills/doc-flow/SHARED_CONTENT.md`
2. **Upstream BRD, PRD, EARS**: Read artifacts that drive these test scenarios
3. **Template**: `ai_dev_flow/BDD/BDD-TEMPLATE.feature`
4. **Creation Rules**: `ai_dev_flow/BDD/BDD_CREATION_RULES.md`
5. **Validation Rules**: `ai_dev_flow/BDD/BDD_VALIDATION_RULES.md`

## When to Use This Skill

Use `doc-bdd` when:
- Have completed BRD (Layer 1), PRD (Layer 2), EARS (Layer 3)
- Need to define executable test scenarios
- Validating EARS formal requirements with Given-When-Then format
- Creating acceptance criteria for features
- You are at Layer 4 of the SDD workflow

## BDD-Specific Guidance

### 1. Gherkin Syntax

**Format**: Given-When-Then structure

**Components**:
- **Feature**: High-level description of functionality
- **Scenario**: Specific test case
- **Given**: Initial context/preconditions
- **When**: Action or event
- **Then**: Expected outcome
- **And/But**: Additional steps

**Example**:
```gherkin
Feature: Position Risk Limit Validation

  @requirement:REQ-003
  @adr:ADR-033
  Scenario: Reject trade when position limit exceeded
    Given the current portfolio delta is 0.45
    And the position limit is set to 0.50
    When a new trade would increase delta to 0.55
    Then the system should reject the trade
    And display error message "Position limit exceeded"
    And log the rejection event
```

### 2. Required Sections

**Document Control** (MANDATORY - First section in companion .md file):
- Project Name
- Document Version
- Date (YYYY-MM-DD)
- Document Owner
- Prepared By
- Status (Draft, In Review, Approved, Superseded)
- Document Revision History table

**Feature File Structure**:
```gherkin
Feature: [Feature Name]
  [Feature Description]

  Background: [Optional - shared setup for all scenarios]
    Given [common preconditions]

  @requirement:[REQ-ID]
  @adr:[ADR-ID]
  Scenario: [Scenario Name]
    Given [preconditions]
    When [action]
    Then [expected outcome]

  @requirement:[REQ-ID]
  Scenario Outline: [Parameterized Scenario]
    Given [preconditions with <parameter>]
    When [action with <parameter>]
    Then [expected outcome with <parameter>]
    Examples:
      | parameter1 | parameter2 | expected |
      | value1     | value2     | result1  |
```

### 3. BDD Tags for Traceability

**Gherkin Tags** (at Feature or Scenario level):
- `@requirement:[REQ-ID]` - Links to requirement
- `@adr:[ADR-ID]` - Links to architecture decision
- `@priority:[P0|P1|P2]` - Test priority
- `@type:[smoke|regression|integration]` - Test type

**Example**:
```gherkin
@requirement:REQ-003
@adr:ADR-033
@priority:P0
@type:smoke
Scenario: Critical path validation
```

### 4. Scenario Types

**Success Path**: Happy path scenarios
```gherkin
Scenario: Successful trade execution
  Given valid trade order
  When order is submitted
  Then trade executes successfully
```

**Error Conditions**: Failure scenarios
```gherkin
Scenario: Trade rejected due to insufficient funds
  Given account balance is $1000
  When trade requires $5000
  Then trade is rejected
  And error code "INSUFFICIENT_FUNDS" is returned
```

**Edge Cases**: Boundary conditions
```gherkin
Scenario: Trade at exact position limit
  Given current delta is 0.499
  And position limit is 0.50
  When trade increases delta to 0.50
  Then trade is accepted
```

**Scenario Outlines**: Parameterized tests
```gherkin
Scenario Outline: Validate price precision
  Given instrument <symbol>
  When price is <price>
  Then precision should be <decimals> decimal places
  Examples:
    | symbol | price  | decimals |
    | SPY    | 450.25 | 2        |
    | AMZN   | 3250.5 | 1        |
```

## Tag Format Convention (By Design)

The SDD framework uses two distinct notation systems for cross-references:

| Notation | Format       | Artifacts                               | Purpose                                                             |
|----------|--------------|----------------------------------------|---------------------------------------------------------------------|
| Dash     | TYPE-NNN     | ADR, SPEC, CTR, IPLAN, ICON            | Technical artifacts - references to files/documents                 |
| Dot      | TYPE.NNN.NNN | BRD, PRD, EARS, BDD, SYS, REQ, IMPL, TASKS | Hierarchical artifacts - references to features inside documents |

**Key Distinction**:
- `@adr: ADR-033` → Points to the document `ADR-033_risk_limit_enforcement.md`
- `@brd: BRD.017.001` → Points to feature 001 inside document `BRD-017.md`

## Unified Feature ID Format (MANDATORY)

**For hierarchical requirements (BRD, PRD, EARS, BDD, SYS, REQ)**:
- **Always use**: `TYPE.NNN.NNN` (dot separator)
- **Never use**: `TYPE-NNN:NNN` (colon separator - DEPRECATED)

Examples:
- `@brd: BRD.017.001` ✅
- `@brd: BRD-017:001` ❌


## Cumulative Tagging Requirements

**Layer 4 (BDD)**: Must include tags from Layers 1-3 (BRD, PRD, EARS)

**Tag Count**: 3+ tags (@brd, @prd, @ears)

**Format** (in companion .md file or feature file header):
```markdown
@brd: BRD.001.003
@prd: PRD.001.002
@ears: EARS.001.001, EARS.001.002
```

**Gherkin Tag Format** (in .feature file):
```gherkin
# Tags linking to requirements and architecture decisions
@requirement:REQ.003.001
@requirement:EARS.001.001
@adr:ADR-033
```

## Upstream/Downstream Artifacts

**Upstream Sources**:
- **BRD** (Layer 1) - Business objectives
- **PRD** (Layer 2) - Product features
- **EARS** (Layer 3) - Formal requirements

**Downstream Artifacts**:
- **ADR** (Layer 5) - Architecture decisions
- **SYS** (Layer 6) - System requirements
- **REQ** (Layer 7) - Atomic requirements
- **Code** (Layer 13) - Implementation that passes these tests

**Same-Type Document Relationships** (conditional):
- `@related-bdd: BDD-NNN` - BDD features sharing test context
- `@depends-bdd: BDD-NNN` - BDD that must pass before this one

## Creation Process

### Step 1: Read Upstream Artifacts

Read BRD, PRD, and EARS to understand requirements to test.

### Step 2: Reserve ID Number

Check `docs/BDD/` for next available ID number (e.g., BDD-001, BDD-002).

### Step 3: Create BDD Feature File

**File naming**: `docs/BDD/BDD-NNN_{slug}.feature`

**Example**: `docs/BDD/BDD-001_position_limits.feature`

### Step 4: Add Feature Description

```gherkin
Feature: Position Risk Limit Validation
  As a risk manager
  I want position limits enforced automatically
  So that portfolio risk stays within defined parameters

  Background:
    Given the risk management system is initialized
    And position limits are configured
```

### Step 5: Write Scenarios

For each requirement from EARS/PRD:
1. **Success path scenario**
2. **Error condition scenarios** (2-3)
3. **Edge case scenarios** (1-2)
4. **Scenario outlines** (for parameterized tests)

### Step 6: Add Traceability Tags

Add @requirement and @adr tags to each scenario:
```gherkin
@requirement:EARS.001.001
@adr:ADR-033
@priority:P0
Scenario: Reject trade exceeding limit
```

### Step 7: Create Companion Documentation (Optional)

Create `docs/BDD/BDD-NNN_{slug}.md` with:
- Document Control section
- Feature overview
- Test execution instructions
- Cumulative tags (@brd, @prd, @ears)

### Step 8: Create/Update Traceability Matrix

**MANDATORY**: Update `docs/BDD/BDD-000_TRACEABILITY_MATRIX.md`

### Step 9: Validate BDD

```bash
# BDD validation
./ai_dev_flow/scripts/validate_bdd_template.sh docs/BDD/BDD-001_*.feature

# Cumulative tagging validation
python ai_dev_flow/scripts/validate_tags_against_docs.py --artifact BDD-001 --expected-layers brd,prd,ears --strict
```

### Step 10: Commit Changes

Commit BDD feature file and traceability matrix.

## Validation

### Automated Validation

```bash
# Quality gates
./scripts/validate_quality_gates.sh docs/BDD/BDD-001_limits.feature

# Gherkin syntax validation
cucumber --dry-run docs/BDD/BDD-001_limits.feature

# Tag validation
python ai_dev_flow/scripts/validate_tags_against_docs.py \
  --artifact BDD-001 \
  --expected-layers brd,prd,ears \
  --strict
```

### Manual Checklist

- [ ] Document Control in companion .md file (if created)
- [ ] Feature description with user story format
- [ ] Background section (if shared setup needed)
- [ ] All scenarios use Given-When-Then format
- [ ] @requirement and @adr tags on scenarios
- [ ] Success path scenarios included
- [ ] Error condition scenarios included
- [ ] Edge case scenarios included
- [ ] Scenario outlines for parameterized tests (where applicable)
- [ ] Cumulative tags: @brd, @prd, @ears in companion file or feature header
- [ ] Traceability matrix updated
- [ ] Gherkin syntax valid

## Common Pitfalls

1. **Missing tags**: Every scenario needs @requirement tags
2. **No error scenarios**: Must test failure paths, not just success
3. **Vague steps**: Use specific, testable assertions
4. **Missing cumulative tags**: Layer 4 must include Layers 1-3 tags
5. **No traceability**: Each scenario must link to upstream requirement

## Post-Creation Validation (MANDATORY - NO CONFIRMATION)

**CRITICAL**: Execute this validation loop IMMEDIATELY after document creation. Do NOT proceed to next document until validation passes.

### Automatic Validation Loop

```
LOOP:
  1. Run: python scripts/validate_cross_document.py --document {doc_path} --auto-fix
  2. IF errors fixed: GOTO LOOP (re-validate)
  3. IF warnings fixed: GOTO LOOP (re-validate)
  4. IF unfixable issues: Log for manual review, continue
  5. IF clean: Mark VALIDATED, proceed
```

### Validation Command

```bash
# Per-document validation (Phase 1)
python scripts/validate_cross_document.py --document docs/BDD/BDD-NNN_slug.feature --auto-fix

# Layer validation (Phase 2) - run when all BDD documents complete
python scripts/validate_cross_document.py --layer BDD --auto-fix
```

### Layer-Specific Upstream Requirements

| This Layer | Required Upstream Tags | Count |
|------------|------------------------|-------|
| BDD (Layer 4) | @brd, @prd, @ears | 3 tags |

### Auto-Fix Actions (No Confirmation Required)

| Issue | Fix Action |
|-------|------------|
| Missing @brd/@prd/@ears tag | Add with upstream document reference |
| Invalid tag format | Correct to TYPE.NNN.NNN or TYPE-NNN format |
| Broken link | Recalculate path from current location |
| Missing traceability section | Insert from template |

### Validation Codes Reference

| Code | Description | Severity |
|------|-------------|----------|
| XDOC-001 | Referenced requirement ID not found | ERROR |
| XDOC-002 | Missing cumulative tag | ERROR |
| XDOC-003 | Upstream document not found | ERROR |
| XDOC-006 | Tag format invalid | ERROR |
| XDOC-007 | Gap in cumulative tag chain | ERROR |
| XDOC-009 | Missing traceability section | ERROR |

### Quality Gate

**Blocking**: YES - Cannot proceed to next document until Phase 1 validation passes with 0 errors.

---

## Next Skill

After creating BDD, use:

**`doc-adr`** - Create Architecture Decision Records (Layer 5)

The ADR will:
- Document architectural decisions for topics identified in BRD/PRD
- Include `@brd`, `@prd`, `@ears`, `@bdd` tags (cumulative)
- Use Context-Decision-Consequences format
- Reference BDD scenarios that validate the architecture

## Reference Documents

For supplementary documentation related to BDD artifacts:
- **Format**: `BDD-REF-NNN_{slug}.md`
- **Skill**: Use `doc-ref` skill
- **Validation**: Minimal (non-blocking)
- **Examples**: Test strategy guides, Gherkin style guides

## Related Resources

- **Main Guide**: `ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`
- **BDD Creation Rules**: `ai_dev_flow/BDD/BDD_CREATION_RULES.md`
- **BDD Validation Rules**: `ai_dev_flow/BDD/BDD_VALIDATION_RULES.md`
- **BDD README**: `ai_dev_flow/BDD/README.md`
- **Shared Standards**: `.claude/skills/doc-flow/SHARED_CONTENT.md`

## Quick Reference

**BDD Purpose**: Define executable test scenarios

**Layer**: 4

**Tags Required**: @brd, @prd, @ears (3 tags)

**Format**: Gherkin Given-When-Then

**Scenario Types**:
- Success path
- Error conditions
- Edge cases
- Scenario outlines (parameterized)

**Next**: doc-adr
