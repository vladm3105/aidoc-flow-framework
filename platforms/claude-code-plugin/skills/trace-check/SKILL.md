---
title: "trace-check: Validate bidirectional traceability across SDD artifacts"
name: trace-check
description: Validate and update bidirectional traceability across the 8-layer SDD flow (BRD through IPLAN to Code)
tags:
  - sdd-workflow
  - shared-architecture
  - quality-assurance
custom_fields:
  layer: null
  artifact_type: null
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  skill_category: quality-assurance
  upstream_artifacts: []
  downstream_artifacts: []
  version: "3.0.0"
  last_updated: "2026-05-22T00:00:00"
---

# trace-check

## Purpose

Automated traceability validation across all SDD artifacts.

**Core Functions**:
- Validates bidirectional link consistency (upstream/downstream symmetry)
- Verifies ID format compliance (document refs `TYPE-NN`; element refs `TYPE.NN.SS.xxxx`)
- Tests markdown link resolution (file paths and anchors)
- Validates cumulative tagging hierarchy (each layer includes ALL upstream tags)
- Layer-specific tag count validation (an artifact at layer N must carry tags from layers 1 through N-1)
- Calculates coverage metrics (% artifacts with complete traceability)
- Detects orphaned artifacts (no upstream or downstream links)
- Auto-fixes broken links with backup creation

**SDD Workflow** (8-layer model — see `framework/registry/LAYER_REGISTRY.yaml`):
```
Business Layer:        BRD (L1) → PRD (L2) → EARS (L3) →
Testing Layer:         BDD (L4) →
Architecture Layer:    ADR (L5) →
Technical Specs Layer: SPEC (L6) →
Test Definition Layer: TDD (L7) →
Execution Planning Layer: IPLAN (L8) →
Code & Validation Layer:  Code → Tests → Validation → Review → Production
```

**Reference**: `framework/governance/TRACEABILITY.md`

**Complexity**: Medium (requires parsing multiple file formats)

**Resource Requirements**:
- CPU: Moderate (file parsing, regex matching)
- Memory: 100-500MB for 100-200 artifacts
- Disk: 1-10MB for backup archives
- Network: None (local file operations only)

**Failure Modes**:
- Invalid ID format: Reports non-compliant document IDs
- Broken links: Reports file paths that do not resolve
- Missing anchors: Reports markdown anchors not found in target files
- Bidirectional gaps: Reports asymmetric traceability links
- Orphaned artifacts: Reports documents with no upstream or downstream references

## When to Use This Skill

**Use trace-check when**:
- Before committing changes to documentation
- After creating new artifacts (BRD, PRD, SPEC, etc.)
- After updating existing artifacts
- During periodic audits (weekly/sprint/release)
- Validating traceability matrix completeness
- Detecting orphaned artifacts
- Verifying ID format compliance
- Establishing baseline quality metrics

**Do NOT use trace-check when**:
- Working on code implementation (use code review tools)
- Validating code traceability (use docstring validators)
- For non-SDD documentation projects
- During active editing sessions (wait until stable state)

## Skill Inputs

| Input | Type | Description | Example/Default |
|-------|------|-------------|-----------------|
| project_root_path | Required | Path to project documentation root | `{project_root}/docs/` |
| artifact_types | Optional | Specific artifact types to validate | `["BRD", "SPEC"]` or `["all"]` (default) |
| strictness_level | Optional | Validation strictness | `"strict"` (default), `"permissive"`, `"pedantic"` |
| validate_cumulative | Optional | **NEW**: Validate cumulative tagging hierarchy | `true` or `false` (default) |
| auto_fix | Optional | Auto-fix broken links | `true` or `false` (default) |
| report_format | Optional | Output report format | `"markdown"` (default), `"json"`, `"text"` |

**Strictness Levels**:
- `permissive`: Warnings only, no failures for missing reverse links
- `strict`: Fails on broken links and missing bidirectional consistency
- `pedantic`: Fails on any traceability gaps including "To Be Created" sections

## Skill Workflow

### Step 1: Discover All Artifacts

**Actions**:
- Scan `docs/` directory for all artifact types
- Parse filenames to extract document IDs (BRD-01, SPEC-01, etc.)
- Build artifact inventory with file paths
- Filter by artifact_types parameter if specified

**Expected Results**:
- 50-200 artifacts per project
- Inventory mapping: ID → file path
- Coverage: All .md, .yaml, .feature files

**Validation**:
- Verify directory structure: `docs/{NN}_{TYPE}/` exists (e.g. `docs/01_BRD/`, `docs/06_SPEC/`)
- Confirm file naming: `{TYPE}-{NN}_{description}.{ext}` (two-digit number)
- Check for duplicate IDs within same type

### Step 2: Parse Traceability Sections

**Actions**:
- Read each artifact's Section 7 "Traceability"
- Extract upstream sources (documents this derives from)
- Extract downstream artifacts (documents derived from this)
- Parse markdown links: `[ID](path#anchor)` format
- Store bidirectional relationship map

**Markdown Pattern Recognition**:
```
**Upstream Sources:**
- [BRD-01](../01_BRD/BRD-01_file.yaml#BRD-01) - Title (Status, Date)

**Downstream Artifacts:**
**In Progress:**
- [SPEC-01](../06_SPEC/SPEC-01_file.yaml#anchor) - Title (Status, Date)

**To Be Created:**
- SPEC-02+: Description (TBD)
```

**Data Structure**:
- Upstream map: {artifact_id: [upstream_ids]}
- Downstream map: {artifact_id: [downstream_ids]}
- Link details: {source_id, target_id, file_path, line_number, anchor}

### Step 2.5: Extract Traceability Tags from Code

**Actions**:
1. Scan all source files (.py, .md, .yaml, .feature) for tag patterns
2. Parse `@brd:`, `@prd:`, `@ears:`, `@bdd:`, `@adr:`, `@spec:`, `@tdd:`, `@iplan:`, `@impl-status:` tags
3. Validate format: element refs use 4-segment `TYPE.NN.SS.xxxx`; document refs use `TYPE-NN` (`@spec:`/`@iplan:`)
4. Build tag-to-document mapping
5. Cross-reference with actual document existence

**Tag Extraction Regex**:
```python
import re

TAG_PATTERN = r'@(\w+(?:-\w+)?):\s*([\w\.\-]+(?:[\.:]\w[\w\.\-]*)?(?:\s*,\s*[\w\.\-]+(?:[\.:]\w[\w\.\-]*)?)*)'

# Example matches (4-segment element refs + dash document refs):
# @brd: BRD.01.07.a7f3, BRD.01.09.1dbc
# @adr: ADR.01.03.e5b1
# @spec: SPEC-01
# @tdd: TDD.01.04.a3c1
# @iplan: IPLAN-01
```

**Validation Rules**:
1. **Format Check:** Element-level tags (`@brd/@prd/@ears/@bdd/@adr/@tdd`) use 4-segment `TYPE.NN.SS.xxxx`; document-level tags (`@spec/@iplan`) use `TYPE-NN`
2. **Document Exists:** DOCUMENT-ID must reference existing file in `docs/{NN}_{TYPE}/`
3. **Element Exists:** Element ID must exist within the referenced document
4. **No Orphans:** All tags must resolve to actual elements
5. **Implementation Status:** @impl-status must be one of: pending|in-progress|complete|deprecated

**Output**:
```json
{
  "src/[project_module]/gateway/connection_service.py": {
    "tags": {
      "brd": ["BRD.01.07.a7f3", "BRD.01.07.1dbc", "BRD.01.09.3c20"],
      "adr": ["ADR.01.03.e5b1"],
      "spec": ["SPEC-01"],
      "tdd": ["TDD.01.04.a3c1"],
      "impl-status": ["complete"]
    },
    "line_numbers": {
      "BRD.01.07.a7f3": 15,
      "BRD.01.07.1dbc": 15
    }
  }
}
```

**Error Detection**:
- ❌ `@brd: 030` - Missing document, section, and element ID
- ❌ `@brd: BRD.99.07.a7f3` - Document BRD-99 doesn't exist
- ❌ `@brd: BRD.01.99.a7f3` - Section 99 not in BRD-01
- ❌ `@brd: BRD.01.0130` - Legacy 3-segment format (must be 4-segment `TYPE.NN.SS.xxxx`)
- ✅ `@brd: BRD.01.07.a7f3` - Valid format and exists

**Validation method**: This skill IS the checker — the framework ships the spec only (no
runtime scripts). Apply the declarative checklists below directly, deferring to
`framework/governance/ID_NAMING_STANDARDS.md`, `framework/governance/TRACEABILITY.md`,
and the per-layer `framework/layers/<NN>_<X>/README.md` as the authority for tag and ID rules.

### Step 2.6: Validate Cumulative Tagging Hierarchy

**Actions**:
1. For each artifact, determine its layer position (1-8) in the SDD flow
2. Verify artifact includes ALL required upstream tags for its layer (per `LAYER_REGISTRY.yaml` `can_reference`)
3. Check tag-family count matches the expected count for that layer
4. Ensure tag chain completeness (if `@adr` exists, `@brd` through `@bdd` must also exist)

**Expected Cumulative Tag Families by Layer** (source of truth: `LAYER_REGISTRY.yaml` `can_reference`):
```
Business Layer:
  BRD   (L1): 0 tags (top level)
  PRD   (L2): 1 tag  (@brd)
  EARS  (L3): 2 tags (@brd, @prd)

Testing Layer:
  BDD   (L4): 3 tags (@brd, @prd, @ears)

Architecture Layer:
  ADR   (L5): 4 tags (@brd, @prd, @ears, @bdd)

Technical Specs Layer:
  SPEC  (L6): 5 tags (@brd, @prd, @ears, @bdd, @adr)

Test Definition Layer:
  TDD   (L7): 6 tags (@brd, @prd, @ears, @bdd, @adr, @spec)

Execution Planning Layer:
  IPLAN (L8): 7 tags (@brd, @prd, @ears, @bdd, @adr, @spec, @tdd)

Code & Validation Layer:
  Code:  carries the IPLAN cumulative set (@brd through @iplan, 8 tag families)
  Tests/Validation: ALL tags from every upstream artifact
```

**Note**: Each layer adds its predecessor's tag family. The chain is strictly
cumulative and has no optional layers — every layer L1-L8 is required, so an
artifact at layer N must carry exactly the N-1 upstream tag families listed
above.

**Validation method (declarative)**:
- For each artifact, look up its layer's `can_reference` set in `framework/registry/LAYER_REGISTRY.yaml`.
- Confirm every referenced layer appears as a cumulative tag family; report any missing family.
- Confirm no extraneous downstream tag families appear (e.g., a SPEC must not carry `@tdd`).

**Validation Rules**:
1. **Complete Chain**: Each artifact must include ALL upstream tag families
2. **Layer Validation**: An artifact at layer N must carry all tag families from layers 1..N-1
3. **Tag Chain Completeness**: If a higher-layer tag exists (e.g., `@adr`), all lower-layer tags must exist (`@brd` through `@bdd`)
4. **No Gaps**: No missing tags in the cumulative chain
5. **No Future Tags**: An artifact must not reference a downstream layer

**Error Detection**:
- ❌ `SPEC missing @brd tag` - Incomplete upstream chain
- ❌ `TDD has @adr but missing @bdd` - Gap in cumulative chain
- ❌ `IPLAN has 5 tag families but should have 7 (@brd through @tdd)` - Incorrect tag count for layer
- ✅ `SPEC has all 5 required tag families (@brd through @adr)` - Valid cumulative tagging

**Benefits**:
- Regulatory compliance (SEC, FINRA, FDA, ISO audit trails)
- Complete impact analysis (upstream → downstream traceability)
- Automated validation prevents gaps in traceability chain
- CI/CD enforcement ensures 100% compliance

### Step 3: Validate ID Format Compliance

**Checks**:
- Document ID format: `TYPE-NN` (two-digit number)
- Element ID format: `TYPE.NN.SS.xxxx` (4-segment: document, section, 4-char hex hash)
- H1 header contains full document ID: `# BRD-01`
- Zero-padding: `01` not `1`
- No ID collisions (each NN unique per type)
- Valid TYPE: BRD, PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN

**Reference**: `framework/governance/ID_NAMING_STANDARDS.md`

**Failure Examples**:
- `BRD-9` → Should be `BRD-01` (two-digit)
- `SPEC-1` → Should be `SPEC-01`
- `BRD.01.0130` → Legacy 3-segment; should be `BRD.01.07.a7f3` (4-segment)

### Step 3.6: Validate Architecture Decision Topics

**Purpose**: Validate architecture topic subsections across BRD Section 7.2, PRD Section 18, and ADR Section 4.1 for layer separation compliance.

**Layer Separation Principle**:
```
BRD Section 7.2          →    PRD Section 18         →    ADR Section 4.1
(WHAT & WHY)                  (HOW to evaluate)          (Final decision)
─────────────────────────────────────────────────────────────────────────
Business drivers              Technical options          Selected option
Business constraints          Evaluation criteria        Trade-off analysis
```

**Subsection ID Format**: `TYPE.NN.SS.xxxx` (4-segment element ID per `framework/governance/ID_NAMING_STANDARDS.md`)

| Component | Description | Example |
|-----------|-------------|---------|
| `TYPE` | Document type prefix | `BRD` |
| `.NN` | Two-digit document number | `.01` = BRD-01 |
| `.SS` | Two-digit section number | `.07` = Section 7 |
| `.xxxx` | 4-char hex content hash | `.a7f3` |

**Validation Logic**:
```python
def validate_architecture_topics(docs_dir):
    """Validate architecture decision topic traceability."""
    errors = []

    # 1. Extract BRD Section 7.2 topics
    brd_topics = extract_brd_section_72_topics(docs_dir)

    # 2. Validate topic ID format (4-segment element ID: TYPE.NN.SS.xxxx)
    for topic_id, content in brd_topics.items():
        if not re.match(r'^[A-Z]+\.\d{2,}\.\d{2,}\.[a-f0-9]{4,8}$', topic_id):
            errors.append(f"{topic_id}: Invalid format (expected TYPE.NN.SS.xxxx)")

        # 3. Check business-only content (no technical options)
        if has_technical_content(content):
            errors.append(f"{topic_id}: Contains technical content (should be business-only)")

    # 4. Validate PRD Section 18 elaborations
    prd_topics = extract_prd_section_18_topics(docs_dir)
    for topic_id, content in prd_topics.items():
        # Check upstream reference exists
        if content.get('upstream') not in brd_topics:
            errors.append(f"PRD {topic_id}: Upstream BRD topic not found")

        # Check has technical content
        if not has_technical_options(content):
            errors.append(f"PRD {topic_id}: Missing technical options")

    # 5. Validate ADR Section 4.1 originating topics
    adr_topics = extract_adr_originating_topics(docs_dir)
    for adr_id, content in adr_topics.items():
        topic_ref = content.get('originating_topic')
        if topic_ref and topic_ref not in brd_topics:
            errors.append(f"{adr_id}: Originating topic {topic_ref} not found in BRD")

    return errors
```

**Content Validation Rules**:

| Layer | Section | Required Content | Forbidden Content |
|-------|---------|------------------|-------------------|
| BRD (Layer 1) | 7.2 | Business Driver, Business Constraints | Technical options, Evaluation criteria |
| PRD (Layer 2) | 18 | Technical Options, Evaluation Criteria, Upstream reference | Business constraints (duplicated from BRD) |
| ADR (Layer 5) | 4.1 | Originating Topic, Decision, References | Missing upstream references |

**Validation Regex Patterns**:
```python
# BRD Section 7.2 subsection header (H3-H5 depending on document context)
ARCHITECTURE_TOPIC_PATTERN = r'^#{3,5}\s+([A-Z]+\.\d{2,}\.\d{2,}\.[a-f0-9]{4,8}):\s+.+'

# PRD Section 18 upstream reference
PRD_UPSTREAM_PATTERN = r'\*\*Upstream\*\*:\s*BRD-\d{2,}\s+§7\.2'

# ADR Section 4.1 originating topic
ADR_ORIGINATING_PATTERN = r'\*\*Originating Topic\*\*:\s*([A-Z]+\.\d{2,}\.\d{2,}\.[a-f0-9]{4,8})\s*-\s*.+'
```

**Cross-Reference Validation**:
1. Each BRD Section 7.2 topic should have corresponding PRD Section 18 elaboration
2. Each PRD Section 18 topic should reference ADR (pending or actual)
3. Each ADR Section 4.1 should reference originating BRD topic

**Error Examples**:
- `BRD.01.7.a7f3: Invalid format` → Section must be two-digit: `BRD.01.07.a7f3`
- `BRD.01.0130: Invalid format` → Legacy 3-segment; should be `BRD.01.07.a7f3` (4-segment)
- `BRD.01.07.a7f3: Contains technical content` → "WebSocket" in BRD (move to PRD)
- `PRD 18.1: Upstream BRD topic not found` → References non-existent BRD topic
- `ADR-01: Originating topic BRD.99.07.a7f3 not found` → Invalid topic reference

**Success Criteria**:
- ✅ All BRD Section 7.2 topics use `TYPE.NN.SS.xxxx` format
- ✅ All BRD Section 7.2 topics contain business-only content
- ✅ All PRD Section 18 topics reference valid BRD topics
- ✅ All PRD Section 18 topics contain technical elaboration
- ✅ All ADR Section 4.1 topics reference valid originating topics

### Step 4: Check Link Resolution

**Tests**:
- File exists: All markdown link paths resolve
- Relative paths: Correct from source file location
- Anchors exist: All `#anchor` references valid
- YAML files: Check `id:` field matches anchor
- Feature files: Verify `Scenario:` lines create anchors

**Relative Path Calculation**:
- From: `/docs/06_SPEC/SPEC-01.yaml`
- To: `/docs/01_BRD/BRD-01.yaml`
- Link: `[BRD-01](../01_BRD/BRD-01.yaml#BRD-01)`

**Anchor Validation**:
- Markdown: `# BRD-01` → anchor `#BRD-01`
- YAML: `id: ib_gateway_connection_service` → anchor `#ib_gateway_connection_service`
- Feature: `Scenario: User connects to IB Gateway` → anchor varies

**Failure Examples**:
- Link: `[SPEC-01](../06_SPEC/SPEC-01.yaml)` → File not found
- Link: `[BRD-01](../01_BRD/BRD-01.yaml#BRD-02)` → Anchor mismatch

### Step 5: Generate Bidirectional Consistency from Tags

**Logic - Tag-Based Approach**:
- Extract tags from code and documentation
- Build forward matrix: Requirements → Implementing files
- Build reverse matrix: Files → Requirements
- Auto-generate bidirectional traceability matrices
- Validate tag references against actual documents

**Forward Matrix (BRD → Code)**:
```markdown
| Requirement | Implementing Files | Status |
|-------------|-------------------|--------|
| BRD.01.07.a7f3 | src/[project_module]/gateway/connection_service.py:15 | ✓ Complete |
| BRD.01.07.1dbc | src/[project_module]/gateway/connection_service.py:15 | ✓ Complete |
| BRD.01.09.3c20 | src/[project_module]/services/account_service.py:12 | ⚠️ In Progress |
```

**Reverse Matrix (Code → BRD)**:
```markdown
| Source File | BRD Requirements | Implementation Status |
|-------------|------------------|---------------------|
| src/[project_module]/gateway/connection_service.py | BRD.01.07.a7f3, BRD.01.07.1dbc, BRD.01.09.3c20 | Complete |
| src/[project_module]/services/account_service.py | BRD.01.09.5e2a, BRD.01.09.8f4c, BRD.01.10.e5b1 | In Progress |
```

**Traditional Section 7 Validation** (Optional):
- For each A→B link in document A, verify B→A exists in document B
- Check upstream/downstream symmetry
- Detect missing reverse references
- Calculate consistency score: (matched pairs / total links) × 100%

**Scoring**:
- Target: ≥95% consistency
- Warning: 90-94% consistency
- Failure: <90% consistency

**Note:** Matrices are auto-generated from tags. Manual Section 7 is optional when using tag-based approach.

### Step 6: Calculate Coverage Metrics

**Metrics**:
- Count artifacts with complete traceability sections
- Calculate: (artifacts with Section 7 / total artifacts) × 100%
- Identify orphaned artifacts (no upstream/downstream links)
- Report coverage by artifact type

**Coverage Requirements**:
- Section 7 exists
- At least one upstream source listed (except BRD)
- Downstream artifacts identified or "To Be Created" noted

**Orphan Detection**:
- Root artifacts: BRD can have no upstream (business-driven)
- Leaf artifacts: IPLAN can have no downstream (Code is the endpoint)
- Warning: EARS with no upstream (should link to BRD/PRD)
- Warning: SPEC with no downstream (should generate TDD)

### Step 7: Generate Validation Report

**Report Sections**:

1. **Summary**: Pass/fail, coverage %, consistency score
2. **Broken Links**: File:line references with error details
3. **Missing Traceability**: Artifacts without Section 7
4. **Bidirectional Gaps**: A→B exists but B→A missing
5. **Orphaned Artifacts**: No upstream or downstream links
6. **Suggested Fixes**: Auto-fix commands or manual steps
7. **Coverage by Type**: Table with metrics per artifact type

**Report Format**:
- Markdown: Human-readable with tables and emojis
- JSON: Machine-readable for CI/CD integration
- Text: Plain text for console output

### Step 8: Auto-Fix Broken Links (if auto_fix=true)

**Actions**:
1. Create backup before modifications: `docs_backup_YYYYMMDD_HHMMSS.tar.gz`
2. Update document revision history (version bump, changelog)
3. Add missing downstream references to upstream documents
4. Fix relative path errors (../../ corrections)
5. Suggest new traceability entries based on filename patterns

**Safety Measures**:
- Backup creation mandatory before any changes
- Dry-run mode available for preview
- Rollback command provided in report
- Modification log generated

**Backup Command**:
```bash
cd {project_root}/docs
tar -czf ../backups/docs_backup_$(date +%Y%m%d_%H%M%S).tar.gz .
```

## Validation Checks

### ID Format Check

**Compliance**:
- Document ID format: `TYPE-NN` (two-digit number)
- Element ID format: `TYPE.NN.SS.xxxx` (4-segment, 4-char hex hash)
- H1 header: Contains full document ID
- Zero-padding: two digits (01, not 1)
- No collisions: Each NN unique per type

**Document Regex Pattern**: `^(BRD|PRD|EARS|BDD|ADR|SPEC|TDD|IPLAN)-\d{2,}$`
**Element Regex Pattern**: `^(BRD|PRD|EARS|BDD|ADR|TDD)\.\d{2,}\.\d{2,}\.[a-f0-9]{4,8}$`

**Failure Examples**:
- `BRD-9` → Should be `BRD-01` (two-digit)
- `SPEC-1` → Should be `SPEC-01`
- `BRD.01.0130` → Legacy 3-segment; should be `BRD.01.07.a7f3` (4-segment)

### Link Resolution Check

**Tests**:
- File exists: Path resolves to valid file
- Extension correct: .yaml, .feature as expected
- Relative path: Correct from source file location
- Anchor exists: `#anchor` found in target file

**Failure Examples**:
- `[SPEC-01](../06_SPEC/SPEC-01.yaml)` → File not found
- `[BRD-01](../../01_BRD/BRD-01.yaml#BRD-01)` → Wrong path depth
- `[EARS-01](../03_EARS/EARS-01.yaml#EARS-01)` → File exists but anchor missing

### Anchor Validation Check

**Anchor Creation Rules**:
- Markdown: `# {ID}` → anchor `#{ID}`
- YAML: `id: {snake_case_name}` → anchor `#{snake_case_name}`
- Feature: `Scenario: {title}` → anchor varies by parser

**Validation**:
- Extract anchor from link: `[ID](path#anchor)`
- Parse target file for anchor existence
- Verify anchor format matches file type

**Failure Examples**:
- Link: `[SPEC-01](../06_SPEC/SPEC-01.yaml#SPEC-01)` → YAML has `id:` field, not H1
- Link: `[BDD-01](../04_BDD/BDD-01.feature#ib-gateway-connection)` → Scenario title mismatch

### Bidirectional Consistency Check

**Logic**:
- Forward exists: A→B link in document A Section 7.2
- Reverse exists: B→A link in document B Section 7.1
- Symmetry: Both directions present

**Scoring**: (matched pairs / total links) × 100%

**Failure Examples**:
- SPEC-01→BRD-01 exists, but BRD-01→SPEC-01 missing (50% consistency for this pair)
- BRD-01→PRD-01 exists, PRD-01→BRD-01 exists (100% consistency)

### Coverage Check

**Requirements**:
- Section 7 "Traceability" present
- At least one upstream source listed (except BRD - BRD is the only artifact type with OPTIONAL upstream)
- Downstream artifacts: OPTIONAL - only link to documents that already exist (no placeholders)

**Calculation**: (complete / total) × 100%

**Failure Examples**:
- SPEC-01 created but no upstream BRD reference (incomplete)
- TDD-01 with no upstream SPEC reference (incomplete - SPEC is required upstream)

### Orphan Detection Check

**Definitions**:
- No upstream: Artifact has no source documents
- No downstream: Artifact generates no other artifacts

**Traceability Rules**:
| Document Type | Upstream Traceability | Downstream Traceability |
|---------------|----------------------|------------------------|
| **BRD** | OPTIONAL (to other BRDs) | OPTIONAL |
| **All Other Documents** | REQUIRED | OPTIONAL |

**Key Rules**:
- **Upstream REQUIRED** (except BRD): Document MUST reference its upstream sources
- **Downstream OPTIONAL**: Only link to documents that already exist
- **No-TBD Rule**: NEVER use placeholder IDs (TBD, XXX, NNN) - leave empty or omit section

**Expected Behavior**:
- Root artifact: BRD can have no upstream (top-level business document)
- All other artifacts: MUST have upstream references
- Leaf artifacts: IPLAN/Code can have no downstream (endpoint of chain)
- Downstream: OPTIONAL for all artifacts - only add when downstream docs exist

**Failure Examples**:
- EARS-01 with no BRD/PRD upstream (ERROR - upstream REQUIRED)
- PRD-02 with no BRD upstream (ERROR - upstream REQUIRED)
- SPEC-01 with no downstream TDD (OK - downstream is OPTIONAL)
- Any document using "TBD", "XXX", or "NNN" placeholders (ERROR - No-TBD rule)

## Example Usage Scenarios

### Scenario 1: Quick Validation Before Commit

**User Request**: "Validate traceability before I commit SPEC-01"

**Assistant Action**: Uses trace-check skill with:
- project_root_path: `{project_root}/docs/`
- artifact_types: `["SPEC"]`
- strictness_level: `"strict"`
- auto_fix: `false`

**Output**:
```
✅ SPEC-01: ID format valid
✅ SPEC-01: Links resolve (BRD-01, EARS-01, BDD-02, ADR-02)
❌ SPEC-01: Bidirectional gap - BRD-01 missing reverse link
Coverage: SPEC artifacts 100% (1/1)
Consistency: 75% (3/4 links bidirectional)

Recommendation: Update BRD-01 Section 7.2 to add SPEC-01 reference
```

### Scenario 2: Full Audit with Auto-Fix

**User Request**: "Run full traceability audit and fix issues"

**Assistant Action**: Uses trace-check skill with:
- project_root_path: `{project_root}/docs/`
- artifact_types: `["all"]`
- strictness_level: `"strict"`
- auto_fix: `true`

**Actions**:
1. Scanned 87 artifacts (13 BRD, 15 PRD, 8 EARS, 30 BDD, 8 SPEC, 5 TDD)
2. Found 12 broken links - fixed 10, flagged 2 for manual review
3. Added 5 missing downstream references
4. Updated 5 document revision histories
5. Generated backup: `docs_backup_20251111_174001.tar.gz`

**Output**:
```
✅ Coverage: 98% (85/87 artifacts)
✅ Consistency: 96% (245/255 links)
⚠️ 2 orphaned artifacts: EARS-07, BDD-22 (no upstream)
📋 Auto-fixed: 15 issues
📝 Manual review: 2 issues (see report)
```

### Scenario 3: Specific Artifact Type Validation

**User Request**: "Check all SPEC files for traceability issues"

**Assistant Action**: Uses trace-check skill with:
- project_root_path: `{project_root}/docs/`
- artifact_types: `["SPEC"]`
- strictness_level: `"pedantic"`

**Output**:
```
Validated: 8 SPEC files
✅ SPEC-01: Perfect (100% traceability)
✅ SPEC-02: Perfect (100% traceability)
⚠️ SPEC-03: Missing BDD reference
❌ SPEC-04: Broken link to EARS-15 (file not found)
Coverage: 88% (7/8 SPEC with complete traceability)
```

### Scenario 4: Coverage Report Generation

**User Request**: "Generate traceability coverage report"

**Assistant Action**: Uses trace-check skill with:
- project_root_path: `{project_root}/docs/`
- report_format: `"markdown"`

**Output**:
```markdown
| Artifact Type | Total | Complete | Coverage | Orphaned |
|---------------|-------|----------|----------|----------|
| BRD           | 13    | 13       | 100%     | 0        |
| PRD           | 15    | 15       | 100%     | 0        |
| EARS          | 8     | 8        | 100%     | 0        |
| BDD           | 51    | 51       | 100%     | 0        |
| ADR           | 6     | 6        | 100%     | 0        |
| SPEC          | 8     | 7        | 88%      | 0        |
| TDD           | 5     | 5        | 100%     | 0        |
| IPLAN         | 8     | 6        | 75%      | 2        |
| **Total**     | **114** | **111** | **97%** | **2**  |
```

### Scenario 5: Cumulative Tagging Validation

**User Request**: "Validate cumulative tagging compliance across all artifacts"

**Assistant Action**: Uses trace-check skill with:
- project_root_path: `{project_root}/docs/`
- artifact_types: `["all"]`
- strictness_level: `"strict"`
- validate_cumulative: `true`

**Actions**:
1. Scanned 87 artifacts across the 8 SDD layers (BRD through IPLAN)
2. Validated tag-family count for each artifact against its layer's `can_reference` set
3. Checked for gaps in cumulative tag chains
4. Confirmed no artifact references a downstream layer

**Output**:
```
✅ Layer Validation: 85/87 artifacts compliant (98%)
✅ Tag Chain Completeness: 100% (no gaps detected)
⚠️ Tag Count Issues: 2 artifacts
  - SPEC-04: Has 4 tag families but Layer 6 requires 5 (missing @adr)
  - TDD-02: Has 5 tag families but Layer 7 requires 6 (missing @spec)
❌ Cumulative Chain Gaps: 0 artifacts

Recommendations:
1. SPEC-04: Add missing @adr tag family (Layer 5 is required upstream of SPEC)
2. TDD-02: Add missing @spec tag family (SPEC is required upstream of TDD)
3. Run validation weekly to catch gaps early
```

**Benefits**:
- Ensures regulatory compliance (complete audit trails)
- Prevents gaps in upstream traceability
- Automated enforcement of cumulative tagging standard

## Output Report Format

### Summary Section

```markdown
## Traceability Validation Report

**Project**: IB API MCP Server
**Validation Date**: 2025-11-11 17:40:01 EST
**Scope**: All artifacts (114 documents)

### Summary
- ✅ Overall Status: PASS (with warnings)
- 📊 Coverage: 97% (111/114 complete)
- 🔗 Consistency: 96% (245/255 bidirectional)
- ⚠️ Warnings: 3 issues require attention
- ❌ Errors: 0 blocking issues
```

### Broken Links Section

```markdown
## Broken Links (2 found)

| Source | Line | Target | Error |
|--------|------|--------|-------|
| SPEC-04 | 56 | EARS-15 | File not found: ../03_EARS/EARS-15.yaml |
| BDD-12 | 134 | SPEC-03 | Anchor not found: #ib_service_spec |
```

### Missing Traceability Section

```markdown
## Missing Traceability (3 artifacts)

| Artifact | Issue | Severity | Recommendation |
|----------|-------|----------|----------------|
| EARS-07 | No upstream sources | Warning | Add BRD/PRD reference |
| BDD-22 | No upstream sources | Warning | Add EARS reference |
| SPEC-03 | No BDD reference | Info | Add BDD-XX when tests created |
```

### Bidirectional Gaps Section

```markdown
## Bidirectional Inconsistencies (10 found)

| Forward Link | Reverse Link | Status | Fix Command |
|--------------|--------------|--------|-------------|
| SPEC-01 → BRD-01 | BRD-01 → SPEC-01 | ✅ Fixed | Added to BRD-01:463 |
| TDD-02 → SPEC-03 | SPEC-03 → TDD-02 | ❌ Missing | Add to SPEC-03 Section 7 |
```

### Coverage by Type

```markdown
## Coverage Metrics

| Type  | Total | Complete | Coverage | Target | Status |
|-------|-------|----------|----------|--------|--------|
| BRD   | 13    | 13       | 100%     | 100%   | ✅     |
| PRD   | 15    | 15       | 100%     | 100%   | ✅     |
| SPEC  | 8     | 7        | 88%      | 100%   | ⚠️     |
| IPLAN | 8     | 6        | 75%      | 100%   | ⚠️     |
```

## Quality Gates

### Definition of Done

- [ ] 100% link resolution (all markdown links resolve)
- [ ] 100% ID format compliance (document `TYPE-NN`; element `TYPE.NN.SS.xxxx`)
- [ ] ≥95% bidirectional consistency (forward and reverse links)
- [ ] Zero orphaned root artifacts (BRD must have downstream)
- [ ] Zero orphaned mid-chain artifacts (every non-leaf must have downstream)
- [ ] All artifacts have Section 7 "Traceability"
- [ ] All auto-fixes logged in document revision history

### Acceptance Criteria

**Performance**:
- Report generation: <30 seconds for 100 artifacts
- Memory usage: <500MB for 200 artifacts
- Backup creation: <5 seconds for 100MB documentation

**Accuracy**:
- Zero false positives for valid traceability patterns
- Zero false negatives for broken links
- 100% detection of bidirectional gaps

**Safety**:
- Backup created before any auto-fix modifications
- Rollback command provided in report
- Modification log includes file:line details

**Compatibility**:
- Handles all 8 SDD artifact types (BRD through IPLAN)
- Supports .md, .yaml, .feature file formats
- Works with relative paths from any project root

## Auto-Fix Capabilities

### 1. Update Document Revision History

**Action**: Increment version and add changelog entry

**Example**:
```markdown
## Revision History

| Version | Date       | Author | Changes |
|---------|------------|--------|---------|
| 2.1     | 2025-11-11 | trace-check skill | Updated traceability: Added SPEC-01 reference |
| 2.0     | 2025-11-10 | User | Initial complete draft |
```

### 2. Add Missing Downstream References

**Detection**: SPEC-01 references BRD-01, but BRD-01 does not reference SPEC-01

**Action**: Add to BRD-01 Section 7.2 "Downstream Artifacts"

**Before**:
```markdown
**To Be Created:**
- SPEC-XXX: Technical implementation specifications
```

**After**:
```markdown
**In Progress:**
- [SPEC-01](../06_SPEC/SPEC-01_ib_gateway_connection_service.yaml#ib_gateway_connection_service) - IB Gateway Connection Service (Status: Draft, Created: 2025-11-11)

**To Be Created:**
- SPEC-02+: Additional technical specifications (TBD)
```

### 3. Fix Relative Path Errors

**Detection**: Link `[BRD-01](../../01_BRD/BRD-01.yaml#BRD-01)` from `/docs/06_SPEC/SPEC-01.yaml`

**Calculation**:
- From: `/docs/06_SPEC/SPEC-01.yaml`
- To: `/docs/01_BRD/BRD-01.yaml`
- Correct: `../01_BRD/BRD-01.yaml`

**Action**: Update link to `[BRD-01](../01_BRD/BRD-01.yaml#BRD-01)`

### 4. Suggest New Traceability Entries

**Pattern Analysis**:
- SPEC-01 likely relates to EARS-01, BDD-01
- TDD-04 likely relates to SPEC-04
- BDD-03 likely relates to EARS-03

**Suggestion Format**:
```markdown
## Suggested Traceability Entries

**SPEC-03** (Missing BDD reference):
- Add to Section 7.2: `[BDD-03](../04_BDD/BDD-03_file.feature#scenario-id) - Test scenarios (To Be Created)`

**EARS-07** (No upstream):
- Add to Section 7.1: `[BRD-04](../01_BRD/BRD-04_file.yaml#BRD-04) - Source requirement (Verify)`
```

### 5. Backup Before Modifications

**Command**:
```bash
cd {project_root}/docs
tar -czf ../backups/docs_backup_$(date +%Y%m%d_%H%M%S).tar.gz .
```

**Verification**:
```bash
ls -lh ../backups/docs_backup_20251111_174001.tar.gz
# Output: 15M Nov 11 17:40 docs_backup_20251111_174001.tar.gz
```

**Rollback Command** (provided in report):
```bash
cd {project_root}/docs
tar -xzf ../backups/docs_backup_20251111_174001.tar.gz
```

## Related Documentation

### SDD Workflow Standards

**Primary References**:
- `framework/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` - Authoritative workflow definition
- `framework/governance/ID_NAMING_STANDARDS.md` - ID format rules and conventions
- `framework/governance/TRACEABILITY.md` - Traceability requirements and cumulative tagging standards
- `framework/registry/LAYER_REGISTRY.yaml` - Single source of truth for layers and `can_reference`/`downstream` chains
- `framework/governance/DOC_GOVERNANCE_CORE.md` - Governance core for documentation rules

**Workflow Sequence** (8-layer): BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code

### Related Skills

**Complementary Skills**:
- `../doc-flow/` - Create SDD artifacts from templates
- `../adr-roadmap/` - Generate implementation roadmaps from ADRs

**Workflow Integration**:
1. Use `doc-flow` to create new artifacts
2. Use `trace-check` to validate traceability
3. Use `adr-roadmap` to generate implementation plans

### Artifact Templates

**Template Locations** (single source of truth — D-0013):
- BRD: `framework/layers/01_BRD/BRD-TEMPLATE.yaml`
- PRD: `framework/layers/02_PRD/PRD-TEMPLATE.yaml`
- EARS: `framework/layers/03_EARS/EARS-TEMPLATE.yaml`
- BDD: `framework/layers/04_BDD/BDD-TEMPLATE.yaml`
- ADR: `framework/layers/05_ADR/ADR-TEMPLATE.yaml`
- SPEC: `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml`
- TDD: `framework/layers/07_TDD/TDD-TEMPLATE.yaml`
- IPLAN: `framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml`

**All templates include**:
- Section 7: Traceability with upstream/downstream structure
- Revision history table
- Document metadata header

### Validation Authority

The framework is spec-only — it ships no runtime validation scripts. This skill
IS the validator: apply its declarative checklists above and defer to the
governance authority for the rules:
- `framework/governance/` - ID, tagging, traceability, and diagram standards
- `framework/layers/<NN>_<X>/README.md` - per-layer requirements
- `framework/registry/LAYER_REGISTRY.yaml` - the authoritative `can_reference`/`downstream` chains

## Version Information

**Version**: 3.0.0
**Last Updated**: 2026-05-22
**Created**: 2025-11-11
**Status**: Active
**Author**: SDD Framework Team

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 3.0.0 | 2026-05-22 | **MAJOR**: Migrated to the 8-layer model (BRD·PRD·EARS·BDD·ADR·SPEC·TDD·IPLAN·Code). Removed SYS/REQ/CTR layers and the CTR dual-file step; TSPEC→TDD (L7), TASKS→IPLAN (L8), SPEC renumbered to L6. Cumulative-tag chains rebuilt from `LAYER_REGISTRY.yaml` `can_reference` (tag set @brd,@prd,@ears,@bdd,@adr,@spec,@tdd,@iplan). Element IDs are 4-segment `TYPE.NN.SS.xxxx`; document refs are `TYPE-NN` (`@spec:`/`@iplan:` document-level). Paths point at `framework/layers/<NN>_<X>/`; dead validation-script references removed (the skill IS the checker, deferring to `framework/governance/`). |
| 2.1.1 | 2025-12-15 | Architecture Decision Topic format update |
| 2.1.0 | 2025-12-13 | Added Step 3.6 Architecture Decision Topic validation; cross-reference and content validation |
| 2.0.1 | 2025-11-13 | Clarity improvements |
| 2.0.0 | 2025-11-13 | Major update: cumulative tagging hierarchy validation |
| 1.0.0 | 2025-11-11 | Initial release with full validation and auto-fix capabilities |
