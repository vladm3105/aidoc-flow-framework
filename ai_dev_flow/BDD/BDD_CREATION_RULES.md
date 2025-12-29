# =============================================================================
# 📋 Document Role: This is a DERIVATIVE of BDD-TEMPLATE.feature
# - Authority: BDD-TEMPLATE.feature is the single source of truth for BDD structure
# - Purpose: AI guidance for document creation (derived from template)
# - On conflict: Defer to BDD-TEMPLATE.feature
# =============================================================================
---
title: "BDD Creation Rules"
tags:
  - creation-rules
  - layer-4-artifact
  - shared-architecture
custom_fields:
  document_type: creation-rules
  artifact_type: BDD
  layer: 4
  priority: shared
  development_status: active
---

> **📋 Document Role**: CREATION GUIDANCE for BDD documents (DERIVATIVE).
> - **Authority**: `BDD-TEMPLATE.feature` is the PRIMARY STANDARD (single source of truth)
> - **Purpose**: Human-readable explanation of Template structure
> - **Scope**: Does NOT define new rules - only explains Template
> - **Conflict Resolution**: If this conflicts with Template, update this document
> - **Validation**: Use `BDD_VALIDATION_RULES.md` after BDD creation/changes

# BDD Creation Rules

**Version**: 1.3
**Date**: 2025-11-19
**Last Updated**: 2025-12-26
**Source**: Derived from BDD-TEMPLATE.feature, EARS requirements, Gherkin best practices, and BDD_SPLITTING_RULES.md
**Purpose**: Complete reference for creating BDD feature files according to AI Dev Flow SDD framework
**Changes**: Added Split-File Structure section (v1.3). Previous: Threshold Registry Integration section (v1.2)

---

## Table of Contents

1. [File Organization and Directory Structure](#1-file-organization-and-directory-structure)
   1.1. [YAML Frontmatter Metadata](#11-yaml-frontmatter-metadata-required-for-md-files)
   1.2. [Split-File Structure (Multi-File BDD Suites)](#12-split-file-structure-multi-file-bdd-suites)
2. [Document Structure (Gherkin Syntax)](#2-document-structure-gherkin-syntax)
3. [Document Control Requirements](#3-document-control-requirements)
4. [Feature File Standards](#4-feature-file-standards)
5. [Scenario Types and Structure](#5-scenario-types-and-structure)
6. [ADR Relationship Guidelines](#6-adr-relationship-guidelines)
7. [ADR-Ready Scoring System](#7-adr-ready-scoring-system)
8. [Traceability Requirements](#8-traceability-requirements)
9. [Quality Attributes](#9-quality-attributes)
10. [Quality Gates](#10-quality-gates)
11. [Additional Requirements](#11-additional-requirements)
12. [Common Mistakes to Avoid](#12-common-mistakes-to-avoid)
13. [Upstream Artifact Verification Process](#13-upstream-artifact-verification-process)
14. [Threshold Registry Integration](#14-threshold-registry-integration)

---

## 1. File Organization and Directory Structure

Note: Some examples in this document show a portable `docs/` root. In this repository, artifact folders live at the ai_dev_flow root without the `docs/` prefix; see README → “Using This Repo” for path mapping.

### 1.0 Structure Selection Criteria

**Single-File Structure** (use when):
- Feature file < 500 lines
- <25 scenarios total
- Single domain/feature scope
- Simple requirement coverage

**Split-File Structure** (use when):
- Feature file would exceed 500 lines
- ≥25 scenarios
- Multiple domains/modules
- Complex requirement coverage (see Section 1.2)

### 1.0.1 Single-File Structure (Legacy - Prohibited)

- Legacy guidance shown for historical context only. Use section-based nested suite structure instead (see 1.0.2).

**Example**:
```
docs/BDD/
├── BDD-03_graph_database_architecture.feature  (131 scenarios)
├── BDD-04_vector_search_embeddings.feature     (84 scenarios)
└── BDD-12_technical_infrastructure.feature     (77 scenarios)
```

### 1.0.2 Split-File Structure (Required)

- **Location**: `docs/BDD/BDD-NN_{descriptive_slug}/` within project docs directory
- **Naming**: Section-based files inside suite folder: `BDD-NN.0_index.md`, `BDD-NN.SS_{slug}.feature`, `BDD-NN.SS.mm_{slug}.feature`, `BDD-NN.SS.00_{slug}.feature` (aggregator)
- **Structure**: Multiple section/subsection feature files organized by suite, no `features/` subdirectory
- **Recommended**: Optional companion docs inside suite folder: `BDD-NN_README.md`, `BDD-NN_TRACEABILITY.md`

**Example**:
```
docs/BDD/
├── BDD-06_level0_system_agents/
│   ├── BDD-06.0_index.md
│   ├── BDD-06.1_health_monitor.feature        (38 scenarios)
│   ├── BDD-06.2_data_guardian.feature         (38 scenarios)
│   ├── BDD-06.3_position_reconciliation.feature (37 scenarios)
│   ├── BDD-06.4_integration.feature           (37 scenarios)
│   ├── BDD-06_README.md                       (optional)
│   └── BDD-06_TRACEABILITY.md                 (optional)
└── BDD-06_level0_system_agents.feature  (redirect stub - 0 scenarios)
```

**Key Rule**: All `.feature` files MUST reside at the suite folder root (no `features/` subdirectory). Aggregator and section/subsection files live together.

**See Section 1.2 for complete split-file structure details.**

---

## 1.1 YAML Frontmatter Metadata (Required for .md files)

All BDD markdown files MUST include YAML frontmatter metadata consistent with other SDD artifacts (BRD, PRD, EARS).

**Required YAML Frontmatter Structure**:

```yaml
---
title: "BDD-NN: Feature Title"
tags:
  - bdd
  - layer-4-artifact
  - shared-architecture  # or ai-agent-primary for agent-based features
  - feature-specific-tag
custom_fields:
  document_type: bdd
  artifact_type: BDD
  layer: 4
  architecture_approaches: [ai-agent-based, traditional-8layer]  # or single approach
  priority: shared  # or primary/fallback
  development_status: active
  agent_id: AGENT-NN  # Only for ai-agent-primary documents
  requirements_verified:
    - EARS-NN
    - BRD-NN
  traceability:
    upstream: [BRD-NN, PRD-NN, EARS-NN]
    downstream: [ADR, SYS, REQ, SPEC, Code, Tests]
---
```

**Shared Architecture Example** (most BDD files):
```yaml
---
title: "BDD-NN: [Descriptive Title]"
tags:
  - bdd
  - layer-4-artifact
  - shared-architecture
  - example
custom_fields:
  document_type: bdd
  artifact_type: BDD
  layer: 4
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  requirements_verified:
    - EARS-NN
    - BRD-NN
  traceability:
    upstream: [BRD-NN, PRD-NN, EARS-NN]
    downstream: [ADR, SYS, REQ, SPEC, Code, Tests]
---
```

**AI-Agent Primary Example** (agent-based features):
```yaml
---
title: "BDD-022: Fraud Detection Agent (ML-based Risk)"
tags:
  - bdd
  - layer-4-artifact
  - ai-agent-primary
  - recommended-approach
  - fraud-detection
  - ml-risk
custom_fields:
  document_type: bdd
  artifact_type: BDD
  layer: 4
  architecture_approach: ai-agent-based
  priority: primary
  development_status: active
  agent_id: AGENT-001
  requirements_verified:
    - EARS-022
    - BRD-22
  traceability:
    upstream: [BRD-22, PRD-022, EARS-022]
    downstream: [ADR, SYS, REQ, SPEC, Code, Tests]
---
```

**Key Differences from .feature files**:
- YAML frontmatter replaces comment-based header (`# ===...`)
- Traceability information moves to `custom_fields.traceability`
- Architecture classification uses standard tags (`shared-architecture`, `ai-agent-primary`)
- Agent ID included for AI-agent documents

---

## 1.2 Section-Based File Organization (MANDATORY)

### Purpose
Unify BDD naming with PRD/BRD section-based standards. All BDD files use section-based numbering (dot notation) with a nested suite folder structure at `docs/BDD/BDD-NN_{slug}/`.

**Section-based format is MANDATORY**. No backward compatibility with legacy formats (single-file `BDD-NN_slug.feature` or directory-based `BDD-NN_slug/features/`).

**When to Use Section-Based Organization**:
- ALL new BDD suites (required structure)
- BDD suite would exceed 500 lines in single file
- ≥25 scenarios total
- Multiple domains/modules/agents
- Complex requirement coverage across multiple EARS sections

**Authority**: See `BDD_SPLITTING_RULES.md` for comprehensive guidance.

### 1.2.1 Three Valid File Patterns (ONLY)

All BDD files must match one of these three patterns:

#### 1. Section-Only Format (Primary)
**Pattern**: `^BDD-\d{2,}\.\d+_[a-z0-9_]+\.feature$`
**Example**: `BDD-02.14_query_result_filtering.feature`
**Use When**: Standard section file (≤500 lines, ≤12 scenarios)

```gherkin
# File: BDD-02.14_query_result_filtering.feature
@section: 2.14
@parent_doc: BDD-02
@index: BDD-02.0_index.md
@brd:BRD.02.03.14
@prd:PRD.02.05.14
@ears:EARS.02.14.01

Feature: BDD-02.14: Query Result Filtering
  As a user querying the knowledge graph
  I want to filter results by multiple criteria
  So that I can find precisely relevant information
```

#### 2. Subsection Format (When Section >500 Lines)
**Pattern**: `^BDD-\d{2,}\.\d+\.\d{2}_[a-z0-9_]+\.feature$`
**Example**: `BDD-02.24.01_quality_performance.feature`
**Use When**: Section requires splitting (each subsection ≤500 lines)

```gherkin
# File: BDD-02.24.01_quality_performance.feature
@section: 2.24.01
@parent_section: 2.24
@parent_doc: BDD-02
@index: BDD-02.0_index.md

Feature: BDD-02.24.01: Performance Quality Attributes
  Performance scenarios for knowledge engine operations
```

#### 3. Aggregator Format (Optional Redirect Stub)
**Pattern**: `^BDD-\d{2,}\.\d+\.00_[a-z0-9_]+\.feature$`
**Example**: `BDD-02.12.00_query_graph_traversal.feature`
**Use When**: Organizing multiple subsections under one section

**Requirements**:
- `@redirect` tag MUST be present
- 0 scenarios (no executable tests)
- References to subsections in comments

```gherkin
# File: BDD-02.12.00_query_graph_traversal.feature
@redirect
@section: 2.12.00
@parent_doc: BDD-02
@index: BDD-02.0_index.md

Feature: BDD-02.12: Query Graph Traversal (Aggregator)

  This is a redirect stub. Test scenarios are in subsections:
  - BDD-02.12.01_basic_traversal.feature
  - BDD-02.12.02_path_finding.feature
  - BDD-02.12.03_relationship_queries.feature

Background:
  Given the system timezone is "America/New_York"
  # No scenarios - redirect only
```

### 1.2.2 Prohibited Patterns (Cause Validation ERROR)

These legacy formats are **PROHIBITED** and will cause validation failure:

❌ **_partN Suffix**: `BDD-02_query_part1.feature`, `BDD-02_query_part2.feature`
✅ **Use instead**: `BDD-02.2.01_query_semantic.feature`, `BDD-02.2.02_query_graph.feature`

❌ **Single-File Format**: `BDD-02_knowledge_engine.feature` (legacy)
✅ **Use instead**: `BDD-02.1_ingest.feature`, `BDD-02.2_query.feature` (section-based)

❌ **Directory-Based Structure**: `BDD-02_knowledge_engine/features/`
✅ **Use instead**: Nested suite folder `docs/BDD/BDD-NN_{slug}/` with section-based naming

### 1.2.3 File Organization Structure

**Nested suite structure** (one folder per suite):

```
docs/BDD/BDD-02_knowledge_engine/
├── BDD-02.0_index.md                          # Index file (MANDATORY)
├── BDD-02.1_ingest.feature                    # Section 1
├── BDD-02.2_query.feature                     # Section 2
├── BDD-02.3.00_learning.feature               # Section 3 aggregator
├── BDD-02.3.01_learning_path.feature          # Section 3, subsection 01
├── BDD-02.3.02_bias_detection.feature         # Section 3, subsection 02
├── BDD-02_README.md                           # Optional companion doc
└── BDD-02_TRACEABILITY.md                     # Optional companion doc
```

**Key Rules**:
- ALL `.feature` files inside `docs/BDD/BDD-NN_{slug}/` suite folder
- NO additional subdirectories (no `features/` folder)
- Each suite MUST have index file: `BDD-NN.0_index.md`
- Optional companion docs: `BDD-NN_README.md`, `BDD-NN_TRACEABILITY.md`, `BDD-NN_GLOSSARY.md`

### 1.2.4 Numbering Scheme

#### Index Files (.0 suffix)
**Format**: `BDD-NN.0_index.md`
**Example**: `BDD-02.0_index.md`
**Status**: MANDATORY for each BDD suite

```markdown
# BDD-02.0: Knowledge Engine Test Suite Index

## Sections

| Section | File | Scenarios | Lines | Status |
|---------|------|-----------|-------|--------|
| 2.1 | BDD-02.1_ingest.feature | 42 | 387 | Active |
| 2.2 | BDD-02.2_query.feature | 38 | 421 | Active |
| 2.3 | BDD-02.3_learning.feature | 35 | 358 | Active |
```

#### Content Sections (.1, .2, .3, ...)
**Format**: `BDD-NN.SS_{slug}.feature`
**Numbering**: Sequential from 1 (no gaps)
**Example**: `BDD-02.1_ingest.feature`, `BDD-02.2_query.feature`

#### Subsections (.SS.01, .SS.02, ...)
**Format**: `BDD-NN.SS.mm_{slug}.feature`
**Numbering**: Sequential from 01 within each section
**Example**: `BDD-02.3.01_learning_path.feature`, `BDD-02.3.02_bias_detection.feature`

#### Aggregators (.SS.00)
**Format**: `BDD-NN.SS.00_{slug}.feature`
**Fixed Subsection**: Always .00
**Example**: `BDD-02.2.00_query.feature`

### 1.2.5 Split Strategy (Prioritized)

When creating or splitting BDD suites, use these criteria in order:

#### 1. Domain Modules (Preferred)
Group by functional domain or lifecycle phase:
- Ingest and Analysis
- Query and Search
- Learning and Adaptation
- State Management
- Validation and Safeguards
- Governance and Compliance

**Example**:
```
BDD-02.1_ingest_analysis.feature        # Ingest domain
BDD-02.2_query_semantic_search.feature  # Query domain
BDD-02.3_learning_adaptation.feature    # Learning domain
```

#### 2. Requirement Groups (EARS/PRD Alignment)
Align with upstream EARS or PRD sections:
- Group contiguous EARS sections (2-3 per BDD section)
- Map to PRD feature areas

**Example**:
```
# EARS sections 01-05 → BDD section 1
BDD-02.1_data_ingestion.feature

# EARS sections 06-12 → BDD section 2
BDD-02.2_query_processing.feature
```

#### 3. Quality Attributes (Cross-Cutting)
When scenarios span all domains:
- Performance testing
- Security scenarios
- Reliability testing
- Operational scenarios

**Example**:
```
BDD-02.24_quality_performance.feature
BDD-02.25_quality_security.feature
BDD-02.26_quality_reliability.feature
```

### 1.2.6 File Size & Scenario Limits

#### File Size Limits
- **Target**: 300–500 lines per `.feature` file
- **Maximum**: 600 lines (absolute)
- **Action**: If section exceeds 600 lines or approaches the upper target → Split into subsections (`.SS.mm` format)

#### Scenario Limits
- **Maximum**: 12 scenarios per Feature block
- **Recommendation**: 6-10 scenarios per Feature
- **Action**: If Feature exceeds 12 scenarios → Split into multiple Feature blocks or subsections

#### Splitting Decision Tree
```
Is section >500 lines?
├─ NO  → Keep as section-only format (BDD-NN.SS_{slug}.feature)
└─ YES → Create subsections
    ├─ 2-4 subsections?
    │  └─ Create: BDD-NN.SS.01_{slug}.feature, BDD-NN.SS.02_{slug}.feature, ...
    └─ 5+ subsections?
       ├─ Create: BDD-NN.SS.00_{slug}.feature (aggregator)
       └─ Create: BDD-NN.SS.01_{slug}.feature, BDD-NN.SS.02_{slug}.feature, ...
```

### 1.2.7 Section Metadata Requirements

All `.feature` files MUST include section metadata tags:

```gherkin
@section: NN.SS              # Section number (e.g., 2.1, 2.14)
@parent_doc: BDD-NN          # Parent BDD suite (e.g., BDD-02)
@index: BDD-NN.0_index.md    # Index file reference
@brd:BRD.NN.EE.SS            # Upstream BRD element
@prd:PRD.NN.EE.SS            # Upstream PRD element
@ears:EARS.NN.SS.RR          # Upstream EARS requirement
```

**Feature Title Format**:
```gherkin
Feature: BDD-NN.SS: Domain Description
```

**Example**:
```gherkin
@section: 2.14
@parent_doc: BDD-02
@index: BDD-02.0_index.md

Feature: BDD-02.14: Query Result Filtering
```

### 1.2.8 Gherkin Standards

**Content Rules**:
- NO non-Gherkin Markdown in `.feature` files
- Put tables and prose in companion markdown files

**Time and Timezone**:
- All times include seconds (HH:MM:SS)
- Use IANA timezone format: `America/New_York`, `America/Los_Angeles`
- Avoid ambiguous abbreviations (EST/EDT/PST/PDT)

**Threshold Assertions**:
- All quantitative values use `@threshold:PRD.NN.category.key`
- No raw numbers for durations, retries, or limits
- Format: `@threshold:PRD.NN.category.key`

**Error Code Formatting**:
- Quoted in steps: `And error code "ERROR_CODE" SHALL be returned`
- Unquoted or `null` in Examples tables

**Step Wording**:
- Use canonical forms for reusability
- Examples:
  - `Given the system is in "active" state`
  - `When the system attempts to transition to "shutdown" state`
  - `Then the validation result SHALL be "success"`

### 1.2.9 Suite Generation Workflow

**Step 1**: Create index file from template
```bash
# Create BDD-NN.0_index.md from BDD-SECTION-0-TEMPLATE.md
cp ai_dev_flow/BDD/BDD-SECTION-0-TEMPLATE.md docs/BDD/BDD-02.0_index.md
```

**Step 2**: Design section split (3-8 sections recommended)
- Identify logical domains or EARS groupings
- Estimate scenarios per section (target: 6-10)
- Plan for subsections if needed (>500 lines)

**Step 3**: Create section files from template
```bash
# Use BDD-SECTION-TEMPLATE.feature for standard sections
# Use BDD-SUBSECTION-TEMPLATE.feature for subsections
# Use BDD-AGGREGATOR-TEMPLATE.feature for aggregators
```

**Step 4**: Add section metadata tags
- `@section`, `@parent_doc`, `@index`
- Upstream traceability: `@brd`, `@prd`, `@ears`

**Step 5**: Replace raw numbers with threshold keys
- Add to PRD threshold registry first if key missing

**Step 6**: Update index file
- List all section files with scenario counts
- Add traceability matrix

**Step 7**: Run validation
```bash
python3 scripts/validate_bdd_suite.py --root BDD
```

### 1.2.10 Optional Companion Files

**BDD-NN_README.md** - Suite Overview:
```markdown
# BDD-02: Knowledge Engine Test Suite

Section-based BDD suite for knowledge engine functionality.

## Sections
- `BDD-02.1_ingest.feature` — Data ingestion and analysis (42 scenarios)
- `BDD-02.2_query.feature` — Query processing and search (38 scenarios)
- `BDD-02.3_learning.feature` — Learning and adaptation (35 scenarios)

See `BDD-02.0_index.md` for complete section map.
```

**BDD-NN_TRACEABILITY.md** - Upstream/Downstream Mapping:
```markdown
# BDD-02: Knowledge Engine — Traceability

## Upstream Sources
| BDD Section | Upstream | Description |
|-------------|----------|-------------|
| BDD-02.1 | BRD.02.03.01, EARS.02.01.001-009 | Data ingestion |
| BDD-02.2 | BRD.02.03.06, EARS.02.06.001-012 | Query processing |
```

**BDD-NN_GLOSSARY.md** - Domain Terms:
```markdown
# Glossary — Knowledge Engine (BDD-02)

## Threshold Registry Keys
- PRD.02.timeout.query_response
- PRD.02.perf.api.p95_latency

## Timezone Policy
- Use `America/New_York` (ET) with HH:MM:SS
```

### 1.2.11 Quality Gates (Pre-Commit)

**File Structure**:
- ✅ All `.feature` files live inside suite folders: `docs/BDD/BDD-NN_{slug}/`
- ✅ Index file exists inside each suite folder: `BDD-NN.0_index.md`
- ✅ No `.feature` file exceeds 500 lines
- ✅ No Feature block exceeds 12 scenarios

**File Naming**:
- ✅ All files match one of 3 valid patterns (section-only, subsection, aggregator)
- ✅ No prohibited patterns (`_partN`, single-file format, directory-based)

**Metadata**:
- ✅ All quantitative values use `@threshold:` keys
- ✅ Times include seconds (HH:MM:SS) with IANA timezone
- ✅ Section metadata tags present in all `.feature` files

**Aggregators**:
- ✅ Aggregator files (.00) have `@redirect` tag
- ✅ Aggregator files have 0 scenarios

**Validation**:
- ✅ Validation passes: `python validate_bdd_suite.py --root docs/BDD`

### 1.2.12 Canonical Step Phrases

Use consistent wording to maximize step reuse:

**Time and Timezone**:
```gherkin
Given the current time is "14:30:00" in "America/New_York"
And the system timezone is "America/New_York"
```

**State and Phase**:
```gherkin
Given the system is in "active" state
Given the system is in "pre_market" phase
```

**Transitions**:
```gherkin
When the system attempts to transition to "shutdown" state
```

**Validation Results**:
```gherkin
Then the validation result SHALL be "success"
And error code "VAL_001" SHALL be returned
```

**Threshold Assertions**:
```gherkin
Then it SHALL complete WITHIN @threshold:PRD.02.timeout.query_response
And memory usage SHALL NOT exceed @threshold:PRD.02.perf.max_memory
```

### 1.2.13 Examples

**Example 1: Simple Suite** (3 sections, no subsections):
```
docs/BDD/
├── BDD-03.0_index.md
├── BDD-03.1_registration.feature       # 25 scenarios, 312 lines
├── BDD-03.2_login.feature              # 28 scenarios, 367 lines
├── BDD-03.3_password_reset.feature     # 18 scenarios, 245 lines
└── BDD-03_README.md                     # Optional
```

**Example 2: Complex Suite** (with subsections):
```
docs/BDD/
├── BDD-02.0_index.md
├── BDD-02.1_ingest.feature             # 42 scenarios, 387 lines
├── BDD-02.2_query.feature              # 38 scenarios, 421 lines
├── BDD-02.3.00_learning.feature        # Aggregator (0 scenarios)
├── BDD-02.3.01_learning_path.feature   # 20 scenarios, 298 lines
├── BDD-02.3.02_bias_detection.feature  # 15 scenarios, 215 lines
├── BDD-02_README.md                     # Optional
└── BDD-02_TRACEABILITY.md               # Optional
```

**Example 3: Quality Attributes** (cross-cutting scenarios):
```
docs/BDD/
├── BDD-02.24_quality_performance.feature
├── BDD-02.25_quality_security.feature
└── BDD-02.26_quality_reliability.feature
```

---

## 2. Document Structure (Gherkin Syntax)

**Required Structure for BDD Feature Files**:

```gherkin
# Header with traceability and control metadata
## Document Control | metadata table |
@brd: BRD.NN.EE.SS
@prd: PRD.NN.EE.SS
@ears: EARS.NN.EE.SS

Feature: [Business Capability Title]
  As a [stakeholder role]
  I want [specific capability]
  So that [business benefit]

  Background: [Common context for all scenarios]

  @primary @functional @acceptance
  Scenario: [Primary success path]
    Given [initial context]
    When [primary action]
    Then [expected outcome]

  @negative @error_handling
  Scenario: [Error condition handling]
    Given [error precondition]
    When [invalid action]
    Then [error response]
```

---

## 3. Document Control Requirements

**Location**: Header comment section at top of .feature file

**Required Document Control Fields (7 mandatory)**:
1. Project Name
2. Document Version
3. Date
4. Document Owner
5. Prepared By
6. Status
7. ADR-Ready Score (format: `✅ NN% (Target: ≥90%)`)

**Format**:
```gherkin
## Document Control

| Item | Details |
|------|---------|
| **Project Name** | [Service Platform v2.0] |
| **ADR-Ready Score** | ✅ 95% (Target: ≥90%) |
```

### Status and ADR-Ready Score Mapping

| ADR-Ready Score | Required Status |
|-----------------|-----------------|
| >= 90% | Approved |
| 70-89% | In Review |
| < 70% | Draft |

---

## 4. Feature File Standards

**Section Filename**: `BDD-NN.SS_{slug}.feature`

**Feature Declaration**:
- Business-focused title
- User role (As a...)
- Specific capability (I want...)
- Business benefit (So that...)

**Required Tags**:
- `@brd: BRD.NN.EE.SS` - Business requirements upstream (sub-ID dot notation)
- `@prd: PRD.NN.EE.SS` - Product requirements upstream (sub-ID dot notation)
- `@ears: EARS.NN.EE.SS` - Engineering requirements upstream (sub-ID dot notation)

### 4.1 Element ID Format (MANDATORY)

**Pattern**: `BDD.{DOC_NUM}.{ELEM_TYPE}.{SEQ}` (4 segments, dot-separated)

| Element Type | Code | Example |
|--------------|------|---------|
| Test Scenario | 14 | BDD.02.14.01 |
| Step | 15 | BDD.02.15.01 |

> ⚠️ **REMOVED PATTERNS** - Do NOT use:
> - `SCENARIO-XXX` → Use `BDD.NN.14.SS`
> - `STEP-XXX` → Use `BDD.NN.15.SS`
> - `TC-XXX` → Use `BDD.NN.14.SS`
>
> **Reference**: [ID_NAMING_STANDARDS.md — Cross-Reference Link Format](../ID_NAMING_STANDARDS.md#cross-reference-link-format-mandatory)

---

## 5. Scenario Types and Structure

### Step Ordering Rule

**Step Ordering Rule**: Steps MUST follow this sequence:
1. **Given** (preconditions) - FIRST
2. **When** (actions) - SECOND
3. **Then** (outcomes) - THIRD
4. **And/But** (continuations) - After any step type

**Invalid Sequences**:
- `When` before `Given` ❌
- `Then` before `When` ❌
- `Then` before `Given` ❌

**Valid Sequences**:
- `Given → When → Then` ✅
- `Given → And → When → Then → And` ✅
- `Given → When → And → Then → And → But` ✅

---

**5.1 Success Path Scenarios** (@primary):
- Primary business functionality
- Expected successful outcomes
- Measurable business value

**5.2 Error Path Scenarios** (@negative):
- Invalid inputs and error conditions
- Graceful error handling
- security boundary validation

**5.3 Edge Case Scenarios** (@boundary @edge_case):
- Boundary conditions and limits
- Performance boundaries
- Concurrent operations

**5.4 Alternative Path Scenarios** (@alternative):
- Optional parameters and configurations
- Alternative workflows and outcomes

**5.5 Quality Attribute Scenarios** (@quality_attribute):
- Performance, security, reliability testing

---

## 6. ADR Relationship Guidelines

**EARS → BDD → ADR Workflow**:
- BDD scenarios provide concrete test cases that drive architectural decisions
- ADR processes evaluate technical alternatives against BDD requirements
- Failed BDD scenarios may necessitate ADR changes

**ADR Impact Analysis**:
- BDD scenarios define the "what" that ADRs must enable
- Architecture selection must support all BDD scenario outcomes
- Performance targets in BDD scenarios drive scaling decisions

---

## 7. ADR-Ready Scoring System ⭐ NEW

### Overview
ADR-ready scoring measures BDD maturity and readiness for progression to Architecture Decision Records (ADR) phase.

### ADR-Ready Score Format Specification

**Format**: `✅ NN% (Target: ≥90%)`

**Format Rules**:
- Must include checkmark emoji (✅) at start
- Percentage as integer (1-100)
- Target threshold in parentheses
- Example: `✅ 85% (Target: ≥90%)`

**Location**: Document Control table (mandatory field)
**Validation**: Enforced before ADR creation

### Scoring Criteria

**Scenario Completeness (35%)**:
- All EARS statements translated to BDD scenarios: 15%
- Comprehensive coverage (success/error/edge cases): 15%
- Observable verification methods specified: 5%

**Testability (30%)**:
- Scenarios are automatable: 15%
- Data-driven scenarios use Examples tables: 10%
- Performance benchmarks quantifiable: 5%

**Architecture Requirements Clarity (25%)**:
- Performance, security, scalability quality attributes specified: 15%
- Integration points and external dependencies defined: 10%

**Business Validation (10%)**:
- Business acceptance criteria traceable: 5%
- Measurable success outcomes defined: 5%

### Quality Gate Enforcement
- Score <90% prevents ADR artifact creation
- Format validation requires ✅ emoji and percentage
- Threshold enforcement at pre-commit

---

## 8. Traceability Requirements (MANDATORY - Layer 4)

**Required Tags** (ALL are MANDATORY per BDD-TEMPLATE.feature):
```gherkin
@brd: BRD.NN.EE.SS    # MANDATORY - business requirements
@prd: PRD.NN.EE.SS    # MANDATORY - product requirements
@ears: EARS.NN.EE.SS  # MANDATORY - engineering requirements
```

**Format**: Extended format with requirement ID suffix (`:NN`) is REQUIRED.

**Layer 4 Requirements**: BDD must reference ALL upstream artifacts (BRD + PRD + EARS)

**Downstream Linkages**:
- ADR decisions must satisfy BDD scenarios
- Code implementation must pass BDD tests
- Specification artifacts must align with BDD acceptance criteria

---

## 9. Quality Attributes

**Automated Execution**: All scenarios must be executable by test automation frameworks

**Performance Validation**: Response time and throughput benchmarks included

**security Testing**: Authentication, authorization, and data protection scenarios

**Reliability Validation**: Error handling and resilience scenarios

**Scalability Testing**: Boundary conditions and load scenarios

---

## 10. Quality Gates (Pre-Commit Validation)

- BDD syntax validation
- ADR-ready score verification (≥90%)
- Scenario coverage completeness
- Traceability chain validation

---

## 11. Additional Requirements

- Business language in scenario descriptions
- Observable pass/fail criteria
- Integration with CI/CD pipelines
- Regular test execution and regression prevention

---

**Framework Compliance**: 100% AI Dev Flow SDD framework (Layer 4)

---

## 12. Common Mistakes to Avoid

| Mistake | Correct |
|---------|---------|
| `Status: Approved` (with <90% ADR-Ready score) | `Status: In Review` or `Status: Draft` |
| Missing @ears traceability tag | `@ears: EARS.NN.EE.SS` |
| Scenario without tags | Add `@primary`, `@negative`, `@boundary` tags |
| `Given-When-Then` without concrete values | Use specific data in steps |
| Vague outcomes like "should work" | Observable verification: "response status code is 200" |
| Missing Background section | Add common preconditions to Background |
| `response time is less than 200ms` (hardcoded) | `response time is less than @threshold: PRD.NN.perf.api.p95_latency` |
| `timeout after 5000ms` (magic number) | `timeout after @threshold: PRD.NN.timeout.default` |
| `rate limit of 100 requests` (hardcoded) | `rate limit of @threshold: PRD.NN.limit.api.requests_per_second` |

### 12.1 Critical Anti-Patterns (Visual Examples)

#### Anti-Pattern 1: Tags in Comments (BLOCKING)

**❌ WRONG** (Gherkin frameworks cannot parse comment-based tags):
```gherkin
# @brd: BRD.01.01.01
# @prd: PRD.01.01.01
# @ears: EARS.01.24.01
Feature: My Feature
```

**✅ CORRECT** (Gherkin-native tags before Feature):
```gherkin
@brd:BRD.01.01.01
@prd:PRD.01.01.01
@ears:EARS.01.24.01
Feature: My Feature
```

**Why this matters**: BDD test frameworks (Cucumber, Behave, pytest-bdd) use tags for filtering, reporting, and execution control. Comment-based tags are invisible to these tools.

#### Anti-Pattern 2: ADR-Ready Score Format (BLOCKING)

**❌ WRONG** (missing checkmark and ≥ symbol):
```markdown
| **ADR-Ready Score** | 75% (Target: 90%) |
```

**✅ CORRECT** (with checkmark and ≥ symbol):
```markdown
| **ADR-Ready Score** | ✅ 75% (Target: ≥90%) |
```

**Why this matters**: Automated validation scripts parse this exact format. Inconsistent formatting breaks dashboard reporting and quality gates.

#### Anti-Pattern 3: Hardcoded Magic Numbers (HIGH)

**❌ WRONG** (hardcoded values):
```gherkin
Then response time is less than 200ms
And timeout occurs after 5000ms
And rate limit is 100 requests per second
```

**✅ CORRECT** (threshold registry references):
```gherkin
Then response time is less than @threshold: PRD.035.perf.api.p95_latency
And timeout occurs after @threshold: PRD.035.timeout.default
And rate limit is @threshold: PRD.035.limit.api.requests_per_second
```

**Why this matters**: Hardcoded values become stale, are difficult to update consistently, and break traceability to requirements.

#### Anti-Pattern 4: Missing Scenario Categories (MEDIUM)

**❌ WRONG** (only success scenarios):
```gherkin
@primary @functional
Scenario: User logs in successfully
  Given valid credentials
  When user submits login
  Then user is authenticated
```

**✅ CORRECT** (all 8 categories represented):
```gherkin
# Include scenarios for: @primary, @alternative, @negative,
# @edge_case, @data_driven, @integration, @quality_attribute, @failure_recovery
```

**Why this matters**: Incomplete scenario coverage leads to untested edge cases and potential production failures.

---

## 13. Upstream Artifact Verification Process

### Before Creating This Document

**Step 1: Inventory Existing Upstream Artifacts**

```bash
# List existing upstream artifacts for this layer
ls -la docs/BRD/    # Layer 1
ls -la docs/PRD/    # Layer 2
ls -la docs/EARS/   # Layer 3
ls -la docs/BDD/    # Layer 4
ls -la docs/ADR/    # Layer 5
ls -la docs/SYS/    # Layer 6
ls -la docs/REQ/    # Layer 7
# ... continue for applicable layers
```

**Step 2: Map Existing Documents to Traceability Tags**

| Tag | Required for This Layer | Existing Document | Action |
|-----|------------------------|-------------------|--------|
| @brd | Yes/No | BRD-01 or null | Reference/Create/Skip |
| @prd | Yes/No | PRD-01 or null | Reference/Create/Skip |
| ... | ... | ... | ... |

**Step 3: Decision Rules**

| Situation | Action |
|-----------|--------|
| Upstream exists | Reference with exact document ID |
| Upstream required but missing | Skip that functionality - do NOT implement |
| Upstream optional and missing | Use `null` in traceability tag |
| Upstream not applicable | Omit tag entirely |

### Traceability Tag Rules

- **NEVER** use placeholder IDs like `BRD-XXX` or `TBD`
- **NEVER** reference documents that don't exist
- **ALWAYS** verify document exists before adding reference
- **USE** `null` only when artifact type is genuinely not applicable

### Same-Type References (Conditional)

Include ONLY if relationships exist between BDD features sharing domain context or implementation dependencies.

**Tags**:
```markdown
@related-bdd: BDD-NN
@depends-bdd: BDD-NN
```

---

## 14. Threshold Registry Integration

**Purpose**: Prevent magic numbers by referencing centralized threshold registry in BDD scenarios.

### When @threshold Tag is Required

Use `@threshold` for ALL quantitative values in BDD scenarios that are:
- Performance targets (response times, SLA validations)
- Timeout expectations (operation timeouts, circuit breaker tests)
- Rate limit validations (requests per second, concurrent users)
- Business-critical values (compliance thresholds, transaction limits)

### @threshold Tag Format in Gherkin

**Scenario Tag Format**:
```gherkin
@threshold: PRD.NN.perf.api.p95_latency
Scenario: API responds within performance threshold
```

**Step Definition Format**:
```gherkin
Then the response time SHOULD be less than @threshold: PRD.NN.perf.api.p95_latency
```

**Examples**:
- `@threshold: PRD.035.perf.api.p95_latency`
- `@threshold: PRD.035.sla.uptime.target`
- `@threshold: PRD.035.compliance.travel_rule.amount`

### BDD-Specific Threshold Categories

| Category | BDD Usage | Example Key |
|----------|-----------|-------------|
| `perf.*` | Performance scenario validation | `perf.api.p95_latency` |
| `sla.*` | SLA scenario validation | `sla.uptime.target` |
| `limit.*` | Rate limit scenario testing | `limit.api.requests_per_second` |
| `compliance.*` | Compliance boundary testing | `compliance.travel_rule.amount` |
| `timeout.*` | Timeout scenario validation | `timeout.request.sync` |

### Magic Number Detection

**Invalid (hardcoded values)**:
```gherkin
Scenario: API performance validation
  Given the system is under normal load
  When a client sends a request
  Then the response time SHOULD be less than 200ms
```

**Valid (registry references)**:
```gherkin
@threshold: PRD.NN.perf.api.p95_latency
Scenario: API performance validation
  Given the system is under normal load
  When a client sends a request
  Then the response time SHOULD be less than @threshold: PRD.NN.perf.api.p95_latency
```

### Examples Table Integration

Use threshold references in Examples tables for data-driven scenarios:

```gherkin
Scenario Outline: Transaction limit validation
  Given a user with role "<role>"
  When they attempt a transaction of <amount>
  Then the transaction SHOULD be <result>

  Examples:
    | role   | amount                                         | result   |
    | user   | @threshold: PRD.NN.limit.transaction.max     | rejected |
    | admin  | @threshold: PRD.NN.limit.transaction.max     | approved |
```

### Traceability Requirements Update

Add `@threshold` to Required Tags:

| Tag | Format | When Required |
|-----|--------|---------------|
| @threshold | PRD-NN:category.key | When scenarios validate performance, SLA, limits, or compliance values |

### Validation

Run `detect_magic_numbers.py` to verify:
1. No hardcoded quantitative values in Then steps
2. No hardcoded values in performance scenarios
3. All `@threshold` references resolve to valid registry keys
4. All Examples tables use threshold references for numeric limits

---

## 15. Cross-Document Validation (MANDATORY)

**CRITICAL**: Execute cross-document validation IMMEDIATELY after creating any BDD document. Do NOT proceed to downstream artifacts until validation passes.

### Automatic Validation Loop

```
LOOP:
  1. Run: python scripts/validate_cross_document.py --document {doc_path} --auto-fix
  2. IF errors fixed: GOTO LOOP (re-validate)
  3. IF warnings fixed: GOTO LOOP (re-validate)
  4. IF unfixable issues: Log for manual review, continue
  5. IF clean: Mark VALIDATED, proceed to next layer
```

### Validation Command

```bash
# Per-document validation (Phase 1)
python scripts/validate_cross_document.py --document docs/BDD/BDD-NN_slug.md --auto-fix

# Layer validation (Phase 2) - run when all BDD documents complete
python scripts/validate_cross_document.py --layer BDD --auto-fix
```

### Layer-Specific Upstream Requirements

| This Layer | Required Upstream Tags | Tag Count |
|------------|------------------------|-----------|
| BDD (Layer 4) | @brd, @prd, @ears | 3 |

### Auto-Fix Actions (No Confirmation Required)

| Issue | Fix Action |
|-------|------------|
| Missing @brd/@prd/@ears tag | Add with upstream document reference |
| Invalid tag format | Correct to TYPE.NN.TT.SS or TYPE-NN format |
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

**Blocking**: YES - Cannot proceed to ADR creation until Phase 1 validation passes with 0 errors.
