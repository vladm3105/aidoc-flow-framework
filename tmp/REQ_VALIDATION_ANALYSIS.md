# REQ Validation Scripts - Comprehensive Analysis

**Generated**: 2025-11-19  
**Source**: `/opt/data/docs_flow_framework/` validation scripts  
**Scope**: REQ (Requirements Layer 7) validation capabilities and integration

---

## Executive Summary

The docs_flow_framework contains a sophisticated validation ecosystem with **7 specialized REQ validation scripts** integrated into a 16-layer Specification-Driven Development (SDD) workflow. These scripts enforce structural compliance, traceability, quality metrics, and SPEC-generation readiness for atomic requirement documents.

**Key Capabilities**:
- REQ ID format validation with duplicate detection
- V2 template compliance checking (12 mandatory sections)
- SPEC-readiness scoring (0-100%)
- Cumulative tagging hierarchy validation
- Traceability matrix generation and validation
- Documentation path integrity checks
- IPLAN naming convention enforcement

---

## 1. Validation Scripts Inventory

### 1.1 REQ-Specific Validation Scripts

| Script | Purpose | Inputs | Outputs | Exit Codes |
|--------|---------|--------|---------|-----------|
| `validate_requirement_ids.py` | ID format, duplicate detection, V2 sections | REQ file or directory | Validation report | 0=pass, 1=fail |
| `validate_req_spec_readiness.py` | SPEC-generation readiness scoring | REQ file or directory | Score (0-100%), pass/fail | 0=pass, 1=fail |
| `validate_tags_against_docs.py` | Cumulative tagging compliance, cross-refs | Tags JSON + docs | Tag coverage report | 0=pass, 1=fail |
| `validate_traceability_matrix.py` | Matrix consistency vs actual documents | Matrix file + docs | Validation report | 0=pass, 1=fail |
| `generate_traceability_matrix.py` | Auto-generate matrices from documents | Document directory | Markdown matrix | 0=success, 1=error |
| `update_traceability_matrix.py` | Incremental matrix updates | Existing matrix + docs | Updated matrix | 0=success, 1=error |
| `validate_documentation_paths.py` | Broken link detection, path resolution | Documentation directory | Path validation report | 0=pass, 1=fail |

### 1.2 Supporting Validation Scripts

| Script | Scope | Purpose |
|--------|-------|---------|
| `validate_iplan_naming.py` | IPLAN/Layer 12 | Timestamp-based naming validation |
| `validate_documentation_consistency.py` | Framework-wide | Markdown links, layer refs, deprecated terms |
| `fix_matrix_numbering.py` | Templates | Section numbering fixes |
| `skills_compliance_report.py` | Claude Skills | Token counts, paths, terminology |
| `validate_skill_code_blocks.py` | Claude Skills | Code block size (>50 lines enforcement) |
| `validate_skill_paths.py` | Claude Skills | Relative path vs {project_root} |
| `validate_skill_terminology.py` | Claude Skills | Deprecated term detection |

---

## 2. REQ Validation Architecture

### 2.1 Validation Hierarchy

```
Layer 7: REQ (Atomic Requirements)
├── ID & Format Validation (validate_requirement_ids.py)
│   ├── Filename format: REQ-NNN_slug.md
│   ├── ID format: REQ-NNN (3-4 digits)
│   ├── No duplicate IDs
│   ├── ID-filename match
│   └── Directory organization: REQ/{category}/{subcategory}/
│
├── Structural Compliance (validate_requirement_ids.py --check-v2-sections)
│   ├── Section 1: Description
│   ├── Section 2: Document Control
│   ├── Section 3: Interface Specifications (CRITICAL)
│   ├── Section 4: Data Schemas (CRITICAL)
│   ├── Section 5: Error Handling (CRITICAL)
│   ├── Section 6: Configuration (CRITICAL)
│   ├── Section 7: Non-Functional Requirements
│   ├── Section 8: Implementation Guidance
│   ├── Section 9: Acceptance Criteria
│   ├── Section 10: Verification Methods
│   ├── Section 11: Traceability
│   └── Section 12: Change History
│
├── SPEC-Readiness Validation (validate_req_spec_readiness.py)
│   ├── Presence checks (6 sections × 10pts = 60pts)
│   ├── Quality checks (4 areas × 10pts = 40pts)
│   ├── Score: 0-100%, Pass threshold: ≥90%
│   └── Min score configurable (default: 90)
│
├── Traceability Validation
│   ├── Tag compliance (validate_tags_against_docs.py)
│   │   ├── Cumulative hierarchy: @brd, @prd, @ears, @bdd, @adr, @sys
│   │   └── Ref verification: Document exists + has referenced ID
│   │
│   ├── Matrix generation (generate_traceability_matrix.py)
│   │   ├── Auto-extract metadata from Section 7
│   │   ├── Build inventory tables
│   │   └── Calculate coverage %
│   │
│   ├── Matrix validation (validate_traceability_matrix.py)
│   │   ├── Count verification
│   │   ├── Cross-ref resolution
│   │   ├── Orphan detection
│   │   └── Strict mode available
│   │
│   └── Matrix update (update_traceability_matrix.py)
│       ├── Detect new/modified/deleted docs
│       ├── Preserve manual edits
│       ├── Create backups
│       └── Dry-run mode
│
└── Cross-Validation
    ├── Documentation path integrity (validate_documentation_paths.py)
    │   ├── Broken link detection
    │   ├── Missing file detection
    │   ├── Case mismatch detection
    │   └── Severity: HIGH/MEDIUM/LOW
    │
    └── Consistency checks (validate_documentation_consistency.py)
        ├── Layer number validation (0-15)
        ├── Deprecated terminology (TASKS_PLANS → IPLAN)
        └── Template reference validation
```

### 2.2 Validation Layers (16-Layer SDD Workflow)

REQ documents exist in **Layer 7** within the 16-layer workflow:

```
Layer 0: Strategy (STRAT)
Layer 1: Business Requirements (BRD)
Layer 2: Product Requirements (PRD)
Layer 3: EARS (Engineering Requirement Statements)
Layer 4: BDD (Behavior-Driven Development tests)
Layer 5: Architecture Decisions (ADR)
Layer 6: System Requirements (SYS)
→ Layer 7: REQUIREMENTS (REQ) ← YOU ARE HERE
Layer 8: Implementation Plans (IMPL)
Layer 9: API Contracts (CTR)
Layer 10: Technical Specifications (SPEC)
Layer 11: Tasks (TASKS)
Layer 12: Implementation Work Plans (IPLAN)
Layer 13: Code
Layer 14: Tests
Layer 15: Validation
```

---

## 3. Detailed Validation Scripts

### 3.1 validate_requirement_ids.py

**Purpose**: Validate REQ-NNN ID format, filenames, duplicate detection, V2 compliance

**Class**: `RequirementIDValidator`

#### Validation Rules

| Rule | Pattern | Example | Error Level |
|------|---------|---------|------------|
| Filename format | `REQ-NNN_slug.md` | `REQ-001_api_integration.md` | Error |
| ID format | `REQ-(\d{3})` | `REQ-001` | Error |
| ID-Filename match | Extract from H1 = filename prefix | Both = REQ-001 | Error |
| Duplicate IDs | No REQ-NNN used twice | Check across all files | Error |
| Document Control | Required fields present | Status, Version, Priority, Category | Warning |
| V2 Sections (optional) | 12 sections if checked | Sections 1-12 | Warning/Error |

#### Critical Sections (Sections 3-6)

When `--check-v2-sections` flag is used:
- **Section 3**: Interface Specifications (Protocol/ABC required)
- **Section 4**: Data Schemas (JSON Schema, Pydantic, or SQLAlchemy)
- **Section 5**: Error Handling (Exception catalog table)
- **Section 6**: Configuration (YAML config examples)

Missing critical sections = **Error** (blocks SPEC-readiness)

#### Invocation Examples

```bash
# Validate single file
python validate_requirement_ids.py --req-file REQ/api/REQ-001_integration.md

# Validate directory with V2 checking
python validate_requirement_ids.py --directory REQ/ --check-v2-sections

# CI/CD usage
python validate_requirement_ids.py --directory REQ/ || exit 1
```

#### Output Format

```
================================================================================
REQUIREMENT ID VALIDATION REPORT
================================================================================

Total Files: 7
Valid: 6
Invalid: 1
Unique REQ-IDs: 7

⚠️  ID Gaps: REQ-004

❌ FAIL REQ-002_missing_sections.md
    ❌ ERROR: Missing critical V2 sections: 3, 4, 5, 6
    ⚠️  WARNING: Missing Document Control fields: Status, Priority

✅ Valid files with warnings: 1
    REQ-001_integration.md
        ⚠️  Missing Document Control fields: Category
```

#### Exit Codes

- `0`: All validations passed
- `1`: Errors found (invalid IDs, duplicates, missing critical sections)

---

### 3.2 validate_req_spec_readiness.py

**Purpose**: Score REQ documents for SPEC-generation readiness (0-100%)

**Class**: `REQSpecReadinessValidator`

#### Scoring Methodology

**Total: 100 Points**

**Section Presence Checks (10 points each = 60 points)**:
1. **Section 3**: Interface Specifications (Protocol or ABC)
2. **Section 4**: Data Schemas (≥2 of: JSON Schema, Pydantic, SQLAlchemy)
3. **Section 5**: Error Handling (Exception catalog table)
4. **Section 6**: Configuration (YAML examples)
5. **Section 7**: Non-Functional Requirements (performance targets)
6. **No Placeholders** (no [PLACEHOLDER], [TODO], <insert>, ...)

**Quality Checks (10 points each = 40 points)**:
7. **Type Annotations**: ≥3 annotated functions
8. **Error Recovery**: ≥2 recovery strategies (retry, fallback, circuit breaker)
9. **Concrete Examples**: ≥10 domain-specific indicators (stock symbols, dates, IDs)
10. **State Machines**: Mermaid diagrams for complex workflows

#### Placeholder Patterns Detected

```python
[PLACEHOLDER], [TODO], [TBD], <insert X>, <fill in>, ...
```

#### Example Scoring

| REQ File | Score | Status | Issues |
|----------|-------|--------|--------|
| REQ-001_api_integration.md | 100% | ✅ PASS | None |
| REQ-002_data_validation.md | 75% | ❌ FAIL | No state diagrams, limited examples |
| REQ-003_position_limits.md | 50% | ❌ FAIL | Missing sections 3, 4, 6 |

#### Configuration

```bash
# Default min score: 90%
python validate_req_spec_readiness.py --directory REQ/

# Custom threshold
python validate_req_spec_readiness.py --directory REQ/ --min-score 80

# Single file
python validate_req_spec_readiness.py --req-file REQ/api/REQ-001.md --min-score 90
```

#### Output Format

```
================================================================================
REQ SPEC-READINESS VALIDATION REPORT
================================================================================

Total Files: 3
Passed (≥90%): 1
Failed (<90%): 2
Average Score: 75.0%

✅ PASS [100%] REQ-001_api_integration.md
❌ FAIL [ 75%] REQ-002_data_validation.md
    ❌ ERROR: Missing Section 3: Interface Specifications
    ⚠️  WARNING: No Mermaid state machine diagrams found
❌ FAIL [ 50%] REQ-003_position_limits.md
    ❌ ERROR: Missing Section 4: Data Schemas
    ❌ ERROR: Missing Section 6: Configuration Specifications
```

#### Exit Codes

- `0`: All validations passed (≥min_score)
- `1`: Validation failed (any file <min_score)

---

### 3.3 validate_tags_against_docs.py

**Purpose**: Validate cumulative tagging hierarchy and cross-references

**Layer Coverage**: Enforces tag compliance across all 16 layers

#### Cumulative Tagging Hierarchy

REQ documents (Layer 7) **MUST** include these tags (in order of upstream layers):

```markdown
@brd: BRD-NNN:REQUIREMENT-ID
@prd: PRD-NNN:REQUIREMENT-ID
@ears: EARS-NNN:STATEMENT-ID
@bdd: BDD-NNN:SCENARIO-ID
@adr: ADR-NNN
@sys: SYS-NNN:SECTION-ID
```

**Tag Count for REQ**: Exactly 6 tags (brd + prd + ears + bdd + adr + sys)

#### Validation Checks

| Check | Validates | Error Type |
|-------|-----------|-----------|
| Tag format | `@type: DOC-NNN` or `@type: DOC-NNN:ID` | HIGH |
| Reference exists | Document ID is real file | HIGH |
| Requirement exists | Referenced ID within document | HIGH |
| Cumulative order | All upstream tags present | MEDIUM |
| Tag count | Layer-specific tag count | MEDIUM |

#### Tag Resolution Process

1. Extract tags from REQ document (Section 11 Traceability)
2. Parse each tag: `@adr: ADR-033` → layer=5, doc=ADR-033
3. Locate document: `ai_dev_flow/ADR/ADR-033_*.md`
4. Verify document exists
5. Verify referenced requirement ID (if specified) exists in source

#### Example Tags

```markdown
@brd: BRD-001:FR-030
@prd: PRD-003:FEATURE-002
@ears: EARS-001:EVENT-003
@bdd: BDD-003:scenario-realtime-quote
@adr: ADR-033
@sys: SYS-008:PERF-001
```

#### Invocation

```bash
# Validate cumulative tagging
python validate_tags_against_docs.py \
  --tags docs/generated/tags.json \
  --docs ai_dev_flow/ \
  --strict

# Validate specific source directory
python validate_tags_against_docs.py \
  --source ai_dev_flow/REQ/ \
  --docs ai_dev_flow/ \
  --validate-cumulative
```

#### Output Format

```
Tag Validation Report:
  Total documents: 7
  Valid tags: 6
  Invalid tags: 1
  Cumulative compliance: 85%

Issues:
  ❌ REQ-001: Missing @sys tag
  ❌ REQ-002: @adr references non-existent ADR-099
  ⚠️  REQ-003: @bdd references non-existent scenario
```

#### Exit Codes

- `0`: All tags valid, cumulative hierarchy satisfied
- `1`: Invalid tags or hierarchy violations

---

### 3.4 validate_traceability_matrix.py

**Purpose**: Validate matrix consistency against actual documents

**Format**: Markdown matrix with auto-generated sections

#### Validation Scope

| Check | Validates |
|-------|-----------|
| **Document Count** | Matrix claims N docs = actual N docs |
| **Document Inventory** | All REQ-NNN files listed in matrix |
| **Cross-References** | Upstream/downstream links resolve |
| **Coverage Metrics** | Percentages accurate |
| **Orphaned Documents** | Docs without upstream traceability |
| **Broken Links** | Dead references in matrix |

#### Key Metrics

- **Inventory**: List of all documents with metadata
- **Coverage**: % of documents with upstream/downstream refs
- **Completeness**: % of documents with all required sections
- **Traceability**: % of cross-references that resolve

#### Invocation

```bash
# Validate REQ matrix
python validate_traceability_matrix.py \
  --matrix ai_dev_flow/REQ/REQ-000_TRACEABILITY_MATRIX-TEMPLATE.md \
  --input ai_dev_flow/REQ/ \
  --strict

# Save report
python validate_traceability_matrix.py \
  --matrix ai_dev_flow/REQ/matrix.md \
  --input ai_dev_flow/REQ/ \
  --output validation_report.md
```

#### Output Format

```
TRACEABILITY MATRIX VALIDATION REPORT
================================================================================

Matrix: ai_dev_flow/REQ/REQ-000_TRACEABILITY_MATRIX-TEMPLATE.md
Input Directory: ai_dev_flow/REQ/

Document Count Verification:
  Matrix claims: 5 documents
  Actual found: 5 documents
  ✅ PASS

Document Inventory Check:
  ✅ REQ-001 found and listed
  ✅ REQ-002 found and listed
  ✅ REQ-003 found and listed
  ⚠️  REQ-004 listed but file not found
  ❌ REQ-099 in filesystem but not in matrix

Cross-Reference Validation:
  ✅ 14/15 upstream references resolve
  ✅ 12/12 downstream references valid

Coverage Metrics:
  Document Coverage: 80%
  Traceability Coverage: 93%
  Link Validity: 94%

Issues Found: 2
  ⚠️  Orphaned: REQ-002 (no upstream REQ)
  ❌ Broken: Link to BRD-999 (not found)
```

#### Exit Codes

- `0`: Validation passed (all critical checks OK)
- `1`: Validation failed (errors found)

---

### 3.5 generate_traceability_matrix.py

**Purpose**: Auto-generate matrices from documents

**Metadata Extraction**:
1. Scan directory for `TYPE-NNN_*.md` files
2. Extract from each document:
   - Title (H1 heading)
   - Status (Document Control section)
   - Date (Document Control section)
   - Upstream sources (Section 7 → Upstream Sources)
   - Downstream artifacts (Section 7 → Downstream Artifacts)
   - Category (from directory path)

#### Generation Process

```bash
python generate_traceability_matrix.py \
  --type REQ \
  --input ai_dev_flow/REQ/ \
  --output ai_dev_flow/REQ/TRACEABILITY_MATRIX_REQ.md
```

#### Output Structure

```markdown
# REQ Traceability Matrix

## 1. Document Inventory

| ID | Title | Status | Date | Category |
|----|----|--------|------|----------|
| REQ-001 | API Integration | Approved | 2025-01-15 | api |
| REQ-002 | Data Validation | Draft | 2025-01-10 | data |

## 2. Coverage Metrics

Document Coverage: 100% (all REQ files listed)
Upstream Coverage: 95% (REQ-001 missing SYS)
...

## 3. Upstream Sources

| REQ ID | Source | Type | Requirement |
|--------|--------|------|------------|
| REQ-001 | SYS-008 | System | PERF-001 |

## 4. Downstream Artifacts

| REQ ID | Artifact | Type | Implementation |
|--------|----------|------|----------------|
| REQ-001 | SPEC-003 | Spec | Interface defs |

## 5. Cross-Reference Map

Mermaid diagram showing document relationships
```

#### Exit Codes

- `0`: Matrix generated successfully
- `1`: Error during generation

---

### 3.6 update_traceability_matrix.py

**Purpose**: Incrementally update matrices without manual re-generation

#### Detection Strategy

1. **New Documents**: Files not in matrix
2. **Modified Documents**: Metadata changed (status, date)
3. **Deleted Documents**: Matrix entries without files
4. **Preserved Edits**: Manual sections outside auto-generated areas

#### Invocation

```bash
# Preview changes (dry-run)
python update_traceability_matrix.py \
  --matrix ai_dev_flow/REQ/TRACEABILITY_MATRIX_REQ.md \
  --input ai_dev_flow/REQ/ \
  --dry-run

# Apply update with changelog
python update_traceability_matrix.py \
  --matrix ai_dev_flow/REQ/TRACEABILITY_MATRIX_REQ.md \
  --input ai_dev_flow/REQ/ \
  --changelog changelog.md

# In CI/CD pipeline
python update_traceability_matrix.py \
  --matrix ai_dev_flow/REQ/matrix.md \
  --input ai_dev_flow/REQ/ || exit 1
```

#### Output Format

```
TRACEABILITY MATRIX UPDATE REPORT
================================================================================

Matrix: ai_dev_flow/REQ/TRACEABILITY_MATRIX_REQ.md
Input Directory: ai_dev_flow/REQ/

Changes Detected:
  New documents: 2
    - REQ-005 added
    - REQ-006 added
  Modified documents: 1
    - REQ-002 (status changed: Draft → Review)
  Deleted documents: 0
  Backup created: TRACEABILITY_MATRIX_REQ.md.backup

Changes Applied:
  ✅ Added REQ-005 to inventory
  ✅ Added REQ-006 to inventory
  ✅ Updated REQ-002 status
  ✅ Recalculated coverage metrics

Changelog:
  2025-01-15T14:30:00 - Added 2 new documents (REQ-005, REQ-006)
  2025-01-15T14:30:00 - Updated status for REQ-002
```

#### Backup Strategy

- Creates `FILENAME.backup` before modifying
- Restores on error
- Keeps manual edits outside auto-generated sections

---

### 3.7 validate_documentation_paths.py

**Purpose**: Detect broken links, missing files, path issues

**Scope**: All Markdown files in documentation

#### Detection Methods

| Issue Type | Severity | Detection Method |
|-----------|----------|-----------------|
| Space in link path | HIGH | `(.. /file.md)` pattern |
| Missing file | HIGH | Resolve path, check exists |
| Case mismatch | MEDIUM | Case-sensitive path check |
| Invalid syntax | HIGH | Link format validation |

#### Placeholder Filtering

Automatically skips intentional placeholders:
```
XXX, NNN, PPP, {variable}
BRD-001, REQ-003, ADR-033 (example IDs)
example, some_, your_, _file (example keywords)
```

#### Invocation

```bash
# Scan all documentation
python validate_documentation_paths.py

# Strict mode (MEDIUM issues = errors)
python validate_documentation_paths.py --strict

# Specific directory
python validate_documentation_paths.py --root ai_dev_flow/REQ/
```

#### Output Format

```
DOCUMENTATION PATH VALIDATION REPORT
================================================================================

Total Issues Found: 2
  HIGH:   1
  MEDIUM: 1
  LOW:    0

HIGH SEVERITY ISSUES
────────────────────────────────────────────────────────────────────────────

ai_dev_flow/REQ/REQ-001.md:150
  [HIGH] MISSING_FILE
  Referenced file not found: '../../SPEC/../REQ-001.md'
  💡 Suggestion: Verify the file exists or update the link

MEDIUM SEVERITY ISSUES
────────────────────────────────────────────────────────────────────────────

ai_dev_flow/REQ/REQ-002.md:45
  [MEDIUM] CASE_MISMATCH
  File found but case mismatch: 'req-001.md' vs 'REQ-001.md'
  💡 Suggestion: Update link to match actual filename case

✅ VALIDATION PASSED (0 HIGH issues)
```

#### Exit Codes

- `0`: No HIGH severity issues (or MEDIUM issues if not strict)
- `1`: HIGH severity issues found, or MEDIUM issues in strict mode

---

## 4. Validation Standards & Compliance

### 4.1 REQ Document Structure (V2 Template)

REQ documents follow a **12-section template** (Version 2):

```
1. Description              - Requirement statement + context
2. Document Control         - Status, version, metadata
3. Interface Specifications - Protocol/ABC with type signatures
4. Data Schemas            - JSON Schema, Pydantic, SQLAlchemy
5. Error Handling          - Exception catalog + recovery
6. Configuration           - YAML + validation schemas
7. Non-Functional Reqs     - Performance, reliability, security
8. Implementation Guidance - Algorithms, patterns, DI
9. Acceptance Criteria     - AC-001, AC-002, ... (measurable)
10. Verification Methods   - BDD, unit tests, integration tests
11. Traceability           - Upstream & downstream references
12. Change History         - Version history table
```

**Critical Sections for SPEC-Readiness**: 3, 4, 5, 6

### 4.2 ID Naming Standards

**Format**: `REQ-NNN_descriptive_slug.md`

- **NNN**: 3-4 digit sequential number (001-999, 1000+)
- **slug**: lowercase, underscore-separated, no hyphens or spaces
- **Location**: `REQ/{category}/{subcategory}/REQ-NNN_slug.md`

**Example**:
```
REQ/api/av/REQ-001_alpha_vantage_integration.md
REQ/risk/lim/REQ-003_position_limit_enforcement.md
```

### 4.3 Document Control Fields (Mandatory)

| Field | Values | Example |
|-------|--------|---------|
| Status | Draft/Review/Approved/Implemented/Verified/Retired | Approved |
| Version | Semantic (X.Y.Z) | 2.0.1 |
| Date Created | YYYY-MM-DD | 2025-01-15 |
| Last Updated | YYYY-MM-DD | 2025-01-15 |
| Author | Name + role | John Doe / Engineer |
| Priority | Critical/High/Medium/Low | High |
| Category | Functional/Non-Functional/Security/Performance | Functional |
| Verification Method | BDD/Spec/Unit/Integration/Contract | BDD |
| SPEC-Ready Score | 0-100% | 95% |

### 4.4 Acceptance Criteria Format

**Pattern**: `AC-NNN: Condition + Expected Outcome`

```
✅ AC-001: API connection established within 5 seconds
  - Verification: Integration test with test credentials
  - Pass Criteria: Connection succeeds <5s for 100% of attempts

✅ AC-002: Data retrieval completes within SLA (p95 <500ms)
  - Verification: Load test with 1000 requests
  - Pass Criteria: p95 <500ms, p99 <1000ms
```

### 4.5 Cumulative Tagging (Layer 7 Requirements)

REQ documents must tag **ALL upstream artifacts**:

```markdown
@brd: BRD-001:FR-030
@prd: PRD-003:FEATURE-002
@ears: EARS-001:EVENT-003
@bdd: BDD-003:scenario-realtime-quote
@adr: ADR-033
@sys: SYS-008:PERF-001
```

**Validation**: Each tag must reference valid document + requirement ID

---

## 5. Error Reporting & Fix Suggestions

### 5.1 Error Categories & Remediation

#### ID & Format Errors

```
❌ Invalid filename format: REQ_api_integration.md
   Expected: REQ-NNN_descriptive_title.md
   Fix: Rename to REQ-001_api_integration.md

❌ Duplicate REQ-ID: REQ-001 found in multiple files
   Files: ai_dev_flow/REQ/api/REQ-001_integration.md
          ai_dev_flow/REQ/auth/REQ-001_access_control.md
   Fix: Renumber one file to REQ-004_access_control.md

❌ Filename ID (REQ-002) does not match document ID (REQ-001)
   Fix: Ensure filename starts with document's H1 ID
```

#### Structural Errors

```
❌ Missing Section 3: Interface Specifications
   Fix: Add Section 3 with Protocol or ABC class definition
   Template: See REQ-TEMPLATE.md Section 3.1

❌ Missing critical V2 section: Section 5 (Error Handling)
   Fix: Add Section 5 with exception catalog table
   Minimum: | Exception Type | HTTP Code | Retry? | Recovery |

❌ Missing Document Control fields: Status, Priority
   Fix: Add to Document Control table:
        | Status | Draft |
        | Priority | High |
```

#### SPEC-Readiness Errors

```
❌ FAIL [60%] REQ-001_integration.md
   ❌ Missing Section 3: Interface Specifications
      → Add Protocol class with method signatures (add 10pts)
   ❌ Missing Section 4 quality: Only 1/3 schema types
      → Add Pydantic + SQLAlchemy models (add 10pts)
   ⚠️  No state machines found
      → Add Mermaid stateDiagram for connection lifecycle (add 10pts)

   Total after fixes: ~90% (PASS threshold)
```

#### Traceability Errors

```
❌ REQ-001: Missing @sys tag in Traceability
   Tags found: @brd, @prd, @ears, @bdd, @adr
   Missing: @sys
   Fix: Add to Section 11 Traceability:
        @sys: SYS-008:PERF-001

❌ REQ-002: @adr references non-existent ADR-099
   Fix: Update to valid ADR ID (e.g., ADR-033)
        Verify referenced requirement exists within ADR

❌ REQ-003: @bdd references non-existent scenario
   Referenced: BDD-003:scenario-realtime-quote
   Fix: Verify scenario exists in ai_dev_flow/BDD/BDD-003_*.feature
        Update if file renamed
```

#### Path & Link Errors

```
❌ Broken link in ai_dev_flow/REQ/REQ-001.md
   [REQ Template](.. /REQ-TEMPLATE.md)  ← SPACE in path
   Fix: Remove space: (../REQ-TEMPLATE.md)

❌ Referenced file not found: ../../SPEC/../REQ.md
   Fix: Simplify or correct path resolution
        Use relative: ../REQ-TEMPLATE.md
        Or absolute: {project_root}/ai_dev_flow/REQ/REQ-TEMPLATE.md

❌ Case mismatch: 'req-001.md' vs 'REQ-001.md'
   Fix: Update link to match actual case: ../REQ-001_integration.md
```

### 5.2 Common Fix Patterns

| Issue | Root Cause | Fix Steps |
|-------|-----------|-----------|
| SPEC-readiness <90% | Missing interface/schema definitions | Use REQ-TEMPLATE.md Sections 3-6 as template |
| Duplicate IDs | Manual numbering collision | Audit all REQ-NNN files, renumber gaps |
| Missing tags | Incomplete traceability | Check each upstream layer, add missing tags |
| Broken links | File moved/renamed | Search for actual file, update link |
| Placeholder content | Incomplete documentation | Replace [TODO], [PLACEHOLDER] with concrete values |

---

## 6. CI/CD Integration Examples

### 6.1 Pre-Commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Validating REQ documents..."

# ID validation
python ai_dev_flow/scripts/validate_requirement_ids.py \
  --directory ai_dev_flow/REQ/ \
  --check-v2-sections || exit 1

# SPEC-readiness check
python ai_dev_flow/scripts/validate_req_spec_readiness.py \
  --directory ai_dev_flow/REQ/ \
  --min-score 90 || exit 1

# Traceability validation
python ai_dev_flow/scripts/validate_traceability_matrix.py \
  --matrix ai_dev_flow/REQ/REQ-000_TRACEABILITY_MATRIX-TEMPLATE.md \
  --input ai_dev_flow/REQ/ \
  --strict || exit 1

# Tag validation
python ai_dev_flow/scripts/validate_tags_against_docs.py \
  --source ai_dev_flow/REQ/ \
  --docs ai_dev_flow/ \
  --validate-cumulative || exit 1

# Path integrity
python ai_dev_flow/scripts/validate_documentation_paths.py \
  --root ai_dev_flow/REQ/ \
  --strict || exit 1

echo "✅ All REQ validations passed!"
```

### 6.2 GitHub Actions Workflow

```yaml
name: Validate REQ Documents

on: [push, pull_request]

jobs:
  validate-req:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Validate REQ IDs
        run: |
          python ai_dev_flow/scripts/validate_requirement_ids.py \
            --directory ai_dev_flow/REQ/ \
            --check-v2-sections

      - name: Check SPEC-Readiness
        run: |
          python ai_dev_flow/scripts/validate_req_spec_readiness.py \
            --directory ai_dev_flow/REQ/ \
            --min-score 90

      - name: Validate Traceability
        run: |
          python ai_dev_flow/scripts/validate_traceability_matrix.py \
            --matrix ai_dev_flow/REQ/REQ-000_TRACEABILITY_MATRIX-TEMPLATE.md \
            --input ai_dev_flow/REQ/ \
            --strict

      - name: Check Tags & References
        run: |
          python ai_dev_flow/scripts/validate_tags_against_docs.py \
            --source ai_dev_flow/REQ/ \
            --docs ai_dev_flow/ \
            --validate-cumulative

      - name: Validate Documentation Paths
        run: |
          python ai_dev_flow/scripts/validate_documentation_paths.py \
            --root ai_dev_flow/ \
            --strict

      - name: Upload Validation Report
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: validation-report
          path: tmp/validation_report.md
```

### 6.3 Manual Validation Workflow

```bash
#!/bin/bash
# scripts/validate_all_req.sh

set -e  # Exit on first error

echo "=== REQ VALIDATION SUITE ==="
echo

# Step 1: ID validation
echo "Step 1: Validating REQ IDs and structure..."
python ai_dev_flow/scripts/validate_requirement_ids.py \
  --directory ai_dev_flow/REQ/ \
  --check-v2-sections

# Step 2: SPEC-readiness
echo "Step 2: Checking SPEC-readiness scores..."
python ai_dev_flow/scripts/validate_req_spec_readiness.py \
  --directory ai_dev_flow/REQ/ \
  --min-score 90

# Step 3: Traceability matrix validation
echo "Step 3: Validating traceability matrix..."
python ai_dev_flow/scripts/validate_traceability_matrix.py \
  --matrix ai_dev_flow/REQ/REQ-000_TRACEABILITY_MATRIX-TEMPLATE.md \
  --input ai_dev_flow/REQ/

# Step 4: Tag validation
echo "Step 4: Validating cumulative tags..."
python ai_dev_flow/scripts/validate_tags_against_docs.py \
  --source ai_dev_flow/REQ/ \
  --docs ai_dev_flow/ \
  --validate-cumulative

# Step 5: Path integrity
echo "Step 5: Checking documentation paths..."
python ai_dev_flow/scripts/validate_documentation_paths.py \
  --root ai_dev_flow/ \
  --strict

echo
echo "✅ All REQ validations passed successfully!"
```

---

## 7. Dependencies & Requirements

### 7.1 Runtime Requirements

**Python**: 3.7+

**Standard Library Only**: No external dependencies
- `argparse` - CLI argument parsing
- `os`, `pathlib` - File operations
- `re` - Regular expressions
- `json` - JSON parsing
- `sys` - System operations
- `datetime` - Date/time handling
- `shutil` - File utilities
- `typing` - Type hints
- `collections` - Data structures

### 7.2 File Structure Requirements

```
project/
├── ai_dev_flow/
│   ├── REQ/
│   │   ├── REQ-000_TRACEABILITY_MATRIX-TEMPLATE.md
│   │   ├── REQ-TEMPLATE.md
│   │   ├── README.md
│   │   ├── api/
│   │   │   ├── av/
│   │   │   │   └── REQ-001_alpha_vantage_integration.md
│   │   │   └── ib/
│   │   │       └── REQ-002_ib_gateway_integration.md
│   │   ├── risk/
│   │   │   └── lim/
│   │   │       └── REQ-003_position_limit_enforcement.md
│   │   └── archived/
│   │       └── (old REQ files)
│   ├── BRD/, PRD/, SYS/, ADR/, EARS/, SPEC/, etc.
│   └── scripts/
│       ├── validate_requirement_ids.py
│       ├── validate_req_spec_readiness.py
│       ├── validate_tags_against_docs.py
│       ├── validate_traceability_matrix.py
│       ├── generate_traceability_matrix.py
│       ├── update_traceability_matrix.py
│       └── validate_documentation_paths.py
└── tmp/
    └── validation_reports/
```

### 7.3 Optional Tools

- **GitHub Actions**: CI/CD workflow automation
- **Git Hooks**: Pre-commit validation
- **Mermaid**: Diagram generation (for state machines, flows)
- **Pydantic**: Data validation (documented in REQ, not required)
- **SQLAlchemy**: ORM examples (documented in REQ, not required)

---

## 8. Implementation Complexity Assessment

| Aspect | Complexity | Notes |
|--------|-----------|-------|
| Script Installation | 1/5 | Python scripts, no dependencies |
| Configuration | 2/5 | CLI flags, directory paths |
| Integration | 2/5 | Basic shell/GitHub Actions |
| Operation | 2/5 | Single command execution |
| Troubleshooting | 3/5 | Clear error messages, patterns to fix |
| Scaling | 1/5 | Handles 100+ documents linearly |

---

## 9. Resource Constraints & Performance

| Metric | Value | Notes |
|--------|-------|-------|
| Memory/Doc | <1MB | Single file loaded, processed sequentially |
| Speed | 100 docs/sec | Linear O(n) processing |
| Scalability | Tested to 1000+ | No external dependencies |
| Disk I/O | Sequential only | No caching, always fresh read |
| Concurrency | Single-threaded | No async I/O |

---

## 10. Validation Workflow Summary

### Quick Reference: Which Script When?

```
Scenario: "I added a new REQ file"
→ Use: validate_requirement_ids.py --req-file REQ/api/REQ-004.md

Scenario: "I want to score SPEC-readiness before marking complete"
→ Use: validate_req_spec_readiness.py --req-file REQ/api/REQ-004.md --min-score 90

Scenario: "I'm committing changes to REQ folder"
→ Use: (all of the above) + validate_documentation_paths.py + validate_tags_against_docs.py

Scenario: "Matrix is out of sync with actual REQ files"
→ Use: update_traceability_matrix.py --matrix REQ/matrix.md --input REQ/

Scenario: "I need to verify traceability consistency"
→ Use: validate_traceability_matrix.py --matrix REQ/matrix.md --input REQ/ --strict

Scenario: "Complete validation suite before PR merge"
→ Use: CI/CD workflow (GitHub Actions) running all scripts in sequence
```

---

## Appendix: Example REQ Document

**Location**: `ai_dev_flow/REQ/examples/api/av/REQ-001_alpha_vantage_integration.md`

**Key Sections**:
- ✅ Section 1: Description with use case scenarios
- ✅ Section 2: Document Control metadata
- ✅ Section 3: Interface Specifications (Protocol + ABC)
- ✅ Section 4: Data Schemas (JSON Schema + Pydantic)
- ✅ Section 5: Error Handling (Exception catalog)
- ✅ Section 6: Configuration (YAML + Pydantic)
- ✅ Section 7: NFRs (Performance/Reliability/Security)
- ✅ Section 11: Traceability (Cumulative tags)

**SPEC-Ready Score**: 95%+ (Passes all validators)

---

**End of Analysis**

---

## Document Metadata

| Item | Value |
|------|-------|
| Generated | 2025-11-19 |
| Source | `/opt/data/docs_flow_framework/` |
| Scripts Analyzed | 7 (REQ-specific) + 7 (supporting) |
| Template | 12-section V2 REQ template |
| Layer | Layer 7 of 16-layer SDD workflow |
| Compliance Framework | AI-Driven Specification-Driven Development (SDD) |

