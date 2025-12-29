---
name: "doc-bdd: BDD Test Scenarios (Layer 4)"
name: doc-bdd
description: Layer 4 artifact for Behavior-Driven Development test scenarios using Gherkin Given-When-Then format
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
  upstream_artifacts: [BRD, PRD, EARS]
  downstream_artifacts: [ADR, SYS, REQ]
---

# doc-bdd

## Purpose

Create **BDD (Behavior-Driven Development)** test scenarios - Layer 4 artifact in the SDD workflow that defines executable test scenarios using Gherkin syntax.

**Layer**: 4

**Upstream**: BRD (Layer 1), PRD (Layer 2), EARS (Layer 3)

**Downstream**: ADR (Layer 5), SYS (Layer 6), REQ (Layer 7)

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

**Structure Selection** (Section-Based ONLY):
- **Section Files**: `BDD-NN.SS_{slug}.feature` (max 500 lines, max 12 scenarios per Feature)
- **Subsections**: `BDD-NN.SS.mm_{slug}.feature` (when section >500 lines)
- **Aggregators**: `BDD-NN.SS.00_{slug}.feature` (redirect stubs with @redirect tag, 0 scenarios)
- **Index File**: `BDD-NN.0_index.md` (MANDATORY for all BDD suites)

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

  @requirement:REQ-03
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
@requirement:REQ-03
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

### 5. ADR-Ready Scoring System

**Purpose**: Measures BDD maturity and readiness for progression to Architecture Decision Records (ADR) phase.

**Format in Document Control**:
```markdown
| **ADR-Ready Score** | ✅ 95% (Target: ≥90%) |
```

**Status and ADR-Ready Score Mapping**:

| ADR-Ready Score | Required Status |
|-----------------|-----------------|
| ≥90% | Approved |
| 70-89% | In Review |
| <70% | Draft |

**Scoring Criteria**:
- **Scenario Completeness (35%)**: EARS translation, coverage (success/error/edge), verifications
- **Testability (30%)**: Automatable scenarios, Examples tables, quantifiable benchmarks
- **Architecture Requirements Clarity (25%)**: Quality attributes, integration points
- **Business Validation (10%)**: Acceptance criteria, measurable outcomes

**Quality Gate**: Score <90% blocks ADR artifact creation.

### 6. Threshold Registry Integration

**Purpose**: Prevent magic numbers by referencing centralized threshold registry.

**Format**:
```gherkin
@threshold: PRD.NNN.perf.api.p95_latency
Then response time is less than @threshold: PRD.NNN.perf.api.p95_latency
```

**When Required**:
- Performance targets (response times, SLA validations)
- Timeout expectations
- Rate limit validations
- Business-critical values (compliance thresholds)

**Example**:
```gherkin
# ❌ WRONG (hardcoded):
Then response time is less than 200ms

# ✅ CORRECT (threshold reference):
Then response time is less than @threshold: PRD.035.perf.api.p95_latency
```

### 7. Section-Based Structure (Mandatory Format)

**Purpose**: All BDD suites MUST use section-based flat structure at `docs/BDD/` root level. No directory-based or single-file legacy formats permitted.

**Valid Section-Based Patterns** (ONLY 3 patterns):

1. **Section-Only Format**: `BDD-NN.SS_{slug}.feature`
   - Example: `BDD-02.14_query_result_filtering.feature`
   - Use for: Standard sections within a suite

2. **Subsection Format**: `BDD-NN.SS.mm_{slug}.feature`
   - Example: `BDD-02.24.01_quality_performance.feature`
   - Use when: Section exceeds 500 lines or 12 scenarios

3. **Aggregator Format**: `BDD-NN.SS.00_{slug}.feature`
   - Example: `BDD-02.12.00_query_graph_traversal.feature`
   - Use when: Section has 5+ subsections (redirect stub only)
   - Requirements: `@redirect` tag, 0 scenarios

**Prohibited Patterns** (ERROR if found):
- ❌ `_partN` suffix (e.g., `BDD-02_query_part1.feature`)
- ❌ Single-file format (e.g., `BDD-02_knowledge_engine.feature`)
- ❌ Directory-based structure (e.g., `BDD-02_{slug}/features/`)

**File Organization**:
```
docs/BDD/
├── BDD-02.0_index.md                    # REQUIRED: Suite index
├── BDD-02.1_ingest.feature              # Section 1
├── BDD-02.2_query.feature               # Section 2
├── BDD-02.3_learning.feature            # Section 3
├── BDD-02.12.00_traversal.feature       # Aggregator (if 5+ subsections)
├── BDD-02.12.01_depth_first.feature     # Subsection 1
├── BDD-02.12.02_breadth_first.feature   # Subsection 2
└── archive/                             # OPTIONAL: Legacy files
```

**Critical Rules**:
1. **All `.feature` files at BDD root** (no subdirectories except `archive/`)
2. **Index file mandatory**: `BDD-NN.0_index.md` for all suites
3. **Max 500 lines per section file** (soft limit: 400)
4. **Max 12 scenarios per Feature block**
5. **Section metadata tags required**: `@section`, `@parent_doc`, `@index`

**Section Split Strategy** (Prioritized):
1. **Domain/Module Boundaries** (Preferred): Ingest, Query, Learning, Monitoring
2. **Lifecycle/Phase Management**: Setup, Operation, Teardown, Recovery
3. **Quality Attributes** (Cross-cutting): Performance, Security, Reliability
4. **Requirement Groups** (EARS/PRD Alignment): Map EARS sections to BDD sections

**Section File Example**:
```gherkin
# Traceability Tags
@section: 2.14
@parent_doc: BDD-02
@index: BDD-02.0_index.md
@brd:BRD.02.01.03
@prd:PRD.02.07.02
@ears:EARS.02.14.01

Feature: BDD-02.14: Query Result Filtering
  As a data analyst
  I want filtered query results
  So that I can focus on relevant data

  Background:
    Given the system timezone is "America/New_York"
    And the current time is "09:30:00" in "America/New_York"
```

**Subsection File Example** (when section >500 lines):
```gherkin
# Traceability Tags
@section: 2.24.01
@parent_section: 2.24
@parent_doc: BDD-02
@index: BDD-02.0_index.md
@brd:BRD.02.01.03
@prd:PRD.02.07.02
@ears:EARS.02.24.01

Feature: BDD-02.24.01: Quality Attribute - Performance
  As a system administrator
  I want performance monitoring
  So that I can ensure system responsiveness
```

**Aggregator File Example** (redirect stub for 5+ subsections):
```gherkin
# Traceability Tags
@redirect
@section: 2.12.00
@parent_doc: BDD-02
@index: BDD-02.0_index.md

Feature: BDD-02.12: Query Graph Traversal (Aggregator)

  This is a redirect stub. Test scenarios are in subsections:
  - BDD-02.12.01_depth_first.feature - Depth-first traversal tests
  - BDD-02.12.02_breadth_first.feature - Breadth-first traversal tests
  - BDD-02.12.03_bidirectional.feature - Bidirectional search tests

  Background:
    Given the system timezone is "America/New_York"
    # No scenarios in aggregator - redirect only
```

**Index File Template** (`BDD-NN.0_index.md`):
```markdown
# BDD-02.0: Knowledge Engine Test Suite Index

## Suite Overview
**Purpose**: Test scenarios for Knowledge Engine functionality
**Scope**: Ingest, Query, Learning, Performance Monitoring

## Section File Map
| Section | File | Scenarios | Lines | Status | Description |
|---------|------|-----------|-------|--------|-------------|
| 02.1 | BDD-02.1_ingest.feature | 8 | 350 | Active | Ingest and analysis tests |
| 02.2 | BDD-02.2_query.feature | 10 | 420 | Active | Query processing tests |
| 02.3 | BDD-02.3_learning.feature | 7 | 280 | Active | Learning adaptation tests |

## Traceability Matrix
| BDD Section | Upstream Source | Description |
|-------------|----------------|-------------|
| BDD-02.1 | EARS.02.01-05 | Ingest requirements |
| BDD-02.2 | EARS.02.06-12 | Query requirements |
```

**Quality Gates**:
- [ ] Index file exists: `BDD-NN.0_index.md`
- [ ] All .feature files at `docs/BDD/` root (no subdirectories)
- [ ] All files match section-based pattern (one of 3 valid patterns)
- [ ] No file exceeds 500 lines
- [ ] No Feature block exceeds 12 scenarios
- [ ] All section files have metadata tags: `@section`, `@parent_doc`, `@index`
- [ ] Aggregators have `@redirect` tag and 0 scenarios
- [ ] All quantitative values use `@threshold:` keys
- [ ] Times include seconds (HH:MM:SS), timezone is America/New_York
- [ ] NO Markdown tables/prose in .feature files

**Canonical Step Phrases** (for step reuse):
```gherkin
Given the current time is "HH:MM:SS" in America/New_York
And the system timezone is "America/New_York"
Given the system is in <STATE>
Given the system is in <PHASE> phase
When the system attempts to transition to <STATE/PHASE>
Then the validation result SHALL be <RESULT>
And error code "<ERROR_CODE>" SHALL be returned
Then it SHALL complete WITHIN @threshold:PRD.NN.timeout.<key>
```

**Migration from Legacy Formats**:
- Use `ai_dev_flow/scripts/migrate_bdd_to_sections.py` for automated migration
- Archive legacy files in `archive/` directory with `.txt` extension
- See `ai_dev_flow/BDD/BDD_GENERATION_CHECKLIST.md` for step-by-step guidance

**Reference**: `ai_dev_flow/BDD/BDD_SPLITTING_RULES.md` (authoritative source)

## Tag Format Convention (By Design)

The SDD framework uses two distinct notation systems for cross-references:

| Notation | Format        | Artifacts                               | Purpose                                                             |
|----------|---------------|----------------------------------------|---------------------------------------------------------------------|
| Dash     | TYPE-NN      | ADR, SPEC, CTR, IPLAN, ICON            | Technical artifacts - references to files/documents                 |
| Dot      | TYPE.NN.TT.SS | BRD, PRD, EARS, BDD, SYS, REQ, IMPL, TASKS | Hierarchical artifacts - references to elements inside documents |

**Key Distinction**:
- `@adr: ADR-033` → Points to the document `ADR-033_risk_limit_enforcement.md`
- `@brd: BRD.17.01.01` → Points to element 01.01 inside document `BRD-017.md`

## Unified Element ID Format (MANDATORY)

**For hierarchical requirements (BRD, PRD, EARS, BDD, SYS, REQ)**:
- **Always use**: `TYPE.NN.TT.SS` (dot separator, 4-segment unified format)
- **Never use**: `TYPE-NN:NNN` (colon separator - DEPRECATED)
- **Never use**: `TYPE.NN.TT` (3-segment format - DEPRECATED)

Examples:
- `@brd: BRD.17.01.01` ✅
- `@brd: BRD.017.001` ❌ (old 3-segment format)


## Cumulative Tagging Requirements

**Layer 4 (BDD)**: Must include tags from Layers 1-3 (BRD, PRD, EARS)

**Tag Count**: 3+ tags (@brd, @prd, @ears)

**Format** (in companion .md file or feature file header):
```markdown
@brd: BRD.01.01.03
@prd: PRD.01.07.02
@ears: EARS.01.24.01, EARS.01.24.02
```

**Gherkin Tag Format** (in .feature file):
```gherkin
# Tags linking to requirements and architecture decisions
@requirement:REQ.03.26.01
@requirement:EARS.01.24.01
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
- `@related-bdd: BDD-NN` - BDD features sharing test context
- `@depends-bdd: BDD-NN` - BDD that must pass before this one

## Creation Process

### Step 1: Read Upstream Artifacts

Read BRD, PRD, and EARS to understand requirements to test.

### Step 2: Reserve ID Number

Check `docs/BDD/` for next available ID number (e.g., BDD-01, BDD-02).

### Step 3: Select Structure and Create BDD Suite

**Structure Selection Criteria**:
- **Single-File** (<300 lines, <25 scenarios, single domain):
  - **File naming**: `docs/BDD/BDD-NN_{slug}.feature`
  - **Example**: `docs/BDD/BDD-01_position_limits.feature`

- **Split-File** (≥300 lines, ≥25 scenarios, multiple domains):
  - **Directory**: `docs/BDD/BDD-NN_{slug}/`
  - **Required files**: README.md, TRACEABILITY.md, GLOSSARY.md, features/ subdirectory
  - **Feature files**: `features/BDD-NN_domain.feature`
  - **Redirect stub**: `docs/BDD/BDD-NN_{slug}.feature` (@redirect tag, 0 scenarios)
  - **Reference**: See Section 7 for complete split-file structure guidance

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
@requirement:EARS.01.24.01
@adr:ADR-033
@priority:P0
Scenario: Reject trade exceeding limit
```

### Step 7: Create Companion Documentation (Optional)

Create `docs/BDD/BDD-NN_{slug}.md` with:
- Document Control section
- Feature overview
- Test execution instructions
- Cumulative tags (@brd, @prd, @ears)

### Step 8: Create/Update Traceability Matrix

**MANDATORY**: Update `docs/BDD/BDD-000_TRACEABILITY_MATRIX.md`

### Step 9: Validate BDD

```bash
# BDD validation (using cross-document validator)
python ai_dev_flow/scripts/validate_cross_document.py --document docs/BDD/BDD-01_*.feature --auto-fix

# Cumulative tagging validation
python ai_dev_flow/scripts/validate_tags_against_docs.py --artifact BDD-01 --expected-layers brd,prd,ears --strict
```

### Step 10: Commit Changes

Commit BDD feature file and traceability matrix.

## Validation

### Automated Validation

```bash
# Quality gates
./scripts/validate_quality_gates.sh docs/BDD/BDD-01_limits.feature

# Gherkin syntax validation
cucumber --dry-run docs/BDD/BDD-01_limits.feature

# Split-file structure validation (for multi-file suites only)
./scripts/validate_bdd_split_structure.sh docs/BDD/BDD-NN_slug/

# Tag validation
python ai_dev_flow/scripts/validate_tags_against_docs.py \
  --artifact BDD-01 \
  --expected-layers brd,prd,ears \
  --strict
```

### Manual Checklist

**Single-File Structure**:
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

**Split-File Structure** (additional checks):
- [ ] Suite directory created: `docs/BDD/BDD-NN_slug/`
- [ ] README.md with suite overview and file map
- [ ] TRACEABILITY.md with cumulative tags and upstream/downstream links
- [ ] GLOSSARY.md with domain terms, threshold keys, timezone policy
- [ ] features/ subdirectory created
- [ ] ALL .feature files in features/ subdirectory (NONE at suite root)
- [ ] Redirect stub at `docs/BDD/BDD-NN_slug.feature` with @redirect tag and 0 scenarios
- [ ] Each .feature file <300 lines (soft limit: 250)
- [ ] Each Feature block ≤12 scenarios
- [ ] NO Markdown tables/prose in .feature files (moved to companion files)
- [ ] All quantitative values use @threshold: keys
- [ ] All times include seconds (HH:MM:SS), timezone is America/New_York

### Diagram Standards
All diagrams MUST use Mermaid syntax. Text-based diagrams (ASCII art, box drawings) are prohibited.
See: `ai_dev_flow/DIAGRAM_STANDARDS.md` and `mermaid-gen` skill.

## Common Pitfalls

1. **Missing tags**: Every scenario needs @requirement tags
2. **No error scenarios**: Must test failure paths, not just success
3. **Vague steps**: Use specific, testable assertions
4. **Missing cumulative tags**: Layer 4 must include Layers 1-3 tags
5. **No traceability**: Each scenario must link to upstream requirement
6. **Incorrect split-file structure**:
   - ❌ .feature files at suite root level (should be in features/ subdirectory)
   - ❌ Missing redirect stub at docs/BDD/BDD-NN_slug.feature
   - ❌ Missing companion files (README.md, TRACEABILITY.md, GLOSSARY.md)
   - ❌ Files exceeding 300 lines (split into smaller domain-focused files)
   - ❌ Markdown tables/prose in .feature files (move to companion files)

## Post-Creation Validation (MANDATORY - NO CONFIRMATION)

**CRITICAL**: Execute this validation loop IMMEDIATELY after document creation. Do NOT proceed to next document until validation passes.

### Automatic Validation Loop

```
LOOP:
  1. Run: python ai_dev_flow/scripts/validate_cross_document.py --document {doc_path} --auto-fix
  2. IF errors fixed: GOTO LOOP (re-validate)
  3. IF warnings fixed: GOTO LOOP (re-validate)
  4. IF unfixable issues: Log for manual review, continue
  5. IF clean: Mark VALIDATED, proceed
```

### Validation Command

```bash
# Per-document validation (Phase 1)
python ai_dev_flow/scripts/validate_cross_document.py --document docs/BDD/BDD-NN_slug.feature --auto-fix

# Layer validation (Phase 2) - run when all BDD documents complete
python ai_dev_flow/scripts/validate_cross_document.py --layer BDD --auto-fix
```

### Layer-Specific Upstream Requirements

| This Layer | Required Upstream Tags | Count |
|------------|------------------------|-------|
| BDD (Layer 4) | @brd, @prd, @ears | 3 tags |

### Auto-Fix Actions (No Confirmation Required)

| Issue | Fix Action |
|-------|------------|
| Missing @brd/@prd/@ears tag | Add with upstream document reference |
| Invalid tag format | Correct to TYPE.NN.TT.SS (4-segment) or TYPE-NN format |
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

- **Template**: `ai_dev_flow/BDD/BDD-TEMPLATE.feature` (primary authority)
- **Schema**: `ai_dev_flow/BDD/BDD_SCHEMA.yaml` (machine-readable validation)
- **BDD Creation Rules**: `ai_dev_flow/BDD/BDD_CREATION_RULES.md`
- **BDD Validation Rules**: `ai_dev_flow/BDD/BDD_VALIDATION_RULES.md`
- **BDD Splitting Rules**: `ai_dev_flow/BDD/BDD_SPLITTING_RULES.md` (split-file structure authority)
- **BDD README**: `ai_dev_flow/BDD/README.md`
- **Main Guide**: `ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`
- **Shared Standards**: `.claude/skills/doc-flow/SHARED_CONTENT.md`

**Section Templates** (for companion .md files >25K tokens):
- Index template: `ai_dev_flow/BDD/BDD-SECTION-0-TEMPLATE.md`
- Content template: `ai_dev_flow/BDD/BDD-SECTION-TEMPLATE.md`
- Reference: `ai_dev_flow/ID_NAMING_STANDARDS.md` (Section-Based File Splitting)
- Note: Section templates are for splitting large companion .md documentation, not .feature files (use domain-based split for .feature files)

## Quick Reference

**BDD Purpose**: Define executable test scenarios

**Layer**: 4

**Tags Required**: @brd, @prd, @ears (3 tags)

**Format**: Gherkin Given-When-Then

**Structure Selection**:
- **Single-File**: <300 lines, <25 scenarios, single domain → `docs/BDD/BDD-NN_slug.feature`
- **Split-File**: ≥300 lines, ≥25 scenarios, multiple domains → `docs/BDD/BDD-NN_slug/features/`

**Split-File Critical Rules**:
- ALL .feature files in `features/` subdirectory (NONE at suite root)
- Redirect stub at `docs/BDD/BDD-NN_slug.feature` (@redirect tag, 0 scenarios)
- Required companion files: README.md, TRACEABILITY.md, GLOSSARY.md
- Max 300 lines per file (soft: 250), max 12 scenarios per Feature block
- Reference: Section 7, BDD_SPLITTING_RULES.md

**ADR-Ready Score**: ≥90% required for "Approved" status

**Scenario Types**:
- Success path (@primary)
- Error conditions (@negative)
- Edge cases (@edge_case)
- Alternative paths (@alternative)
- Data-driven (@data_driven)
- Integration (@integration)
- Quality attributes (@quality_attribute)
- Failure recovery (@failure_recovery)

**Critical**: Use @threshold tags for all quantitative values

**Next**: doc-adr
