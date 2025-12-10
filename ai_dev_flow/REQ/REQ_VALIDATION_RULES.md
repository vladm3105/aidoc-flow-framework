# =============================================================================
# 📋 Document Role: This is a DERIVATIVE of REQ-TEMPLATE.md
# - Authority: REQ-TEMPLATE.md is the single source of truth for REQ structure
# - Purpose: AI checklist after document creation (derived from template)
# - Scope: Includes all rules from REQ_CREATION_RULES.md plus validation extensions
# - On conflict: Defer to REQ-TEMPLATE.md
# =============================================================================

> **📋 Document Role**: This is the **POST-CREATION VALIDATOR** for REQ documents.
> - Apply these rules after REQ creation or modification
> - **Authority**: Validates compliance with `REQ-TEMPLATE.md` (the primary standard)
> - **Scope**: Use for quality gates before committing REQ changes

# REQ Validation Rules Reference

**Version**: 3.0.0
**Date**: 2025-11-18
**Last Updated**: 2025-11-19
**Purpose**: Complete validation rules for REQ documents
**Script**: `scripts/validate_req_template_v3.sh`
**Primary Template**: `REQ-TEMPLATE-V3.md` (v3.0)
**Baseline Template**: `REQ-TEMPLATE.md` (v2.0)
**Framework**: doc_flow SDD (100% compliant)

---

## Table of Contents

1. [Overview](#overview)
2. [Validation Checks](#validation-checks)
3. [Error Fix Guide](#error-fix-guide)
4. [Quick Reference](#quick-reference)
5. [Common Mistakes](#common-mistakes)

---

## Overview

The REQ validation script (`validate_req_template_v3.sh`) performs **18 validation checks** to ensure compliance with:

- **REQ-TEMPLATE-V3.md**: Current template (v3.0 - 100% doc_flow compliant)
- **doc_flow SDD Framework**: Traceability and ID naming standards
- **Cumulative Tagging Hierarchy**: Layer 7 requirements (6 upstream tags)
- **Document Control**: 12 required fields (v3.0 enhancement)

### Validation Tiers

| Tier | Type | Exit Code | Description |
|------|------|-----------|-------------|
| **Tier 1** | Errors | 1 | Blocking issues - must fix before commit |
| **Tier 2** | Warnings | 0 | Quality issues - recommended to fix |
| **Tier 3** | Info | 0 | Informational - no action required |

---

## Validation Checks

### CHECK 1: Required sections

**Purpose**: Verify all 12 mandatory sections exist
**Type**: Error (blocking)

**Required sections**:
```markdown
## 1. Description
## 2. Functional Requirements
## 3. Interface Specifications
## 4. Data Schemas
## 5. Error Handling Specifications
## 6. Configuration Specifications
## 7. Quality Attributes
## 8. Implementation Guidance
## 9. Acceptance Criteria
## 10. Verification Methods
## 11. Traceability
## 12. Change History
```

**Error Message**:
```
❌ MISSING: ## 3. Interface Specifications
```

**Fix**:
1. Add missing section header
2. Ensure exact spelling and numbering
3. sections must be in order (1-12)

---

### CHECK 2: Document Control Fields

**Purpose**: Validate metadata table completeness
**Type**: Error (blocking)

**Required Fields** (11 total):
- Status
- Version
- Date Created
- Last Updated
- Author
- Priority
- Category
- Source Document
- Verification Method
- Assigned Team
- SPEC-Ready Score
- Template Version

**Error Message**:
```
❌ MISSING: Source Document
❌ MISSING: Author
❌ MISSING: Category
❌ MISSING: Verification Method
```

**Fix**:
```markdown
| **Source Document** | SYS-002 section 3.1.1 |
| **Author** | System Architect |
| **Category** | Functional |
| **Verification Method** | BDD + Integration Test |
| **Assigned Team** | IB Integration Team |
```

---

### CHECK 3: Traceability Structure

**Purpose**: Verify traceability subsections exist
**Type**: Error + Warning

**Required Subsections**:
- `### Upstream Sources` (Error if missing)
- `### Downstream Artifacts` (Warning if missing)
- `### Code Implementation Paths` (Warning if missing)

**Error Message**:
```
❌ MISSING: Upstream Sources subsection in section 11
```

**Fix**:
```markdown
## 11. Traceability

### Upstream Sources

| Source Type | Document ID | Document Title | Relevant sections | Relationship |
|-------------|-------------|----------------|-------------------|--------------|
| BRD | [BRD-001](../../BRD/BRD-001.md) | ... | ... | ... |
```

---

### CHECK 4: Upstream Traceability Chain (LEGACY)

**Purpose**: Deprecated in v3.0 - see CHECK 15
**Type**: Info

**Message**:
```
ℹ️  This check is deprecated in v3.0 - see CHECK 15 for complete validation
```

---

### CHECK 5: Version Format Validation

**Purpose**: Ensure semantic versioning (X.Y.Z)
**Type**: Error (blocking)

**Valid Examples**:
- `2.0.0` ✅
- `2.0.1` ✅
- `1.5.3` ✅

**Invalid Examples**:
- `2.0` ❌
- `v2.0.0` ❌
- `Version 2.0` ❌

**Error Message**:
```
❌ INVALID version format: 'v2.0' (expected X.Y.Z)
```

**Fix**:
```markdown
| **Version** | 2.0.1 |
```

---

### CHECK 6: Date Format Validation

**Purpose**: Validate ISO 8601 date format (YYYY-MM-DD)
**Type**: Error (blocking)

**Valid Examples**:
- `2025-11-18` ✅
- `2025-01-09` ✅

**Invalid Examples**:
- `Nov 18, 2025` ❌
- `11/18/2025` ❌
- `18-11-2025` ❌

**Error Message**:
```
❌ INVALID Date Created format: 'Nov 18, 2025' (expected YYYY-MM-DD)
```

**Logical Check**:
- Last Updated ≥ Date Created (or error)

**Fix**:
```markdown
| **Date Created** | 2025-11-18 |
| **Last Updated** | 2025-11-18 |
```

---

### CHECK 7: Priority Format Validation

**Purpose**: Ensure priority includes P-level designation
**Type**: Warning

**Valid Examples**:
- `Critical (P1)` ✅
- `High (P2)` ✅
- `Medium (P3)` ✅
- `Low (P4)` ✅

**Invalid Examples**:
- `Critical` ❌
- `P1` ❌
- `High Priority` ❌

**Warning Message**:
```
⚠️  WARNING: Priority should include P-level: Critical (P1), High (P2), Medium (P3), Low (P4)
```

**Fix**:
```markdown
| **Priority** | High (P2) |
```

---

### CHECK 8: Source Document Format

**Purpose**: Verify source includes document ID + section
**Type**: Warning

**Valid Examples**:
- `SYS-002 section 3.1.1` ✅
- `BRD-001 section 4.2` ✅

**Invalid Examples**:
- `SYS-002` ❌
- `section 3.1.1` ❌

**Warning Message**:
```
⚠️  WARNING: Source Document should include section number (e.g., 'SYS-002 section 3.1.1')
```

**Fix**:
```markdown
| **Source Document** | SYS-002 section 3.1.1 |
```

---

### CHECK 9: SPEC-Ready Score

**Purpose**: Validate score format and threshold
**Type**: Error + Warning

**Valid Examples**:
- `✅ 95% (Target: ≥90%)` ✅
- `✅ 92% (Target: ≥90%)` ✅

**Invalid Examples**:
- `95%` ❌
- `✓ 95%` ❌
- `High` ❌

**Error Message** (format):
```
❌ MISSING: SPEC-Ready Score with ✅ emoji and percentage
```

**Warning Message** (threshold):
```
⚠️  WARNING: SPEC-Ready Score below 90%: 85%
```

**Fix**:
```markdown
| **SPEC-Ready Score** | ✅ 95% (Target: ≥90%) |
```

---

### CHECK 10: Template Version

**Purpose**: Verify template version is 3.0
**Type**: Error (blocking)

**Valid Examples**:
- `3.0` ✅

**Invalid Examples**:
- `2.0` ❌ (deprecated)
- `1.0` ❌ (deprecated)
- `Template 3.0` ❌
- `v3.0` ❌

**Error Message**:
```
❌ ERROR: Template Version is '2.0' (expected 3.0)
❌ ERROR: Template Version is 'v3.0' (expected 3.0, not 'v3.0')
```

**Fix**:
```markdown
| **Template Version** | 3.0 |
```

---

### CHECK 11: Change History

**Purpose**: Verify change history table exists and matches version
**Type**: Error + Warning

**Requirements**:
1. At least 1 entry in table
2. Latest entry version matches Document Control version

**Error Message**:
```
❌ MISSING: Change History entries
```

**Warning Message**:
```
⚠️  WARNING: Latest change history version (2.0.0) doesn't match document version (2.0.1)
```

**Fix**:
```markdown
## 12. Change History

| Date | Version | Change | Author |
|------|---------|--------|---------|
| 2025-11-18 | 2.0.1 | Fixed source document reference (3.1.2→3.1.1) | System Architect |
| 2025-11-11 | 2.0.0 | Created using Template V2 | System Architect |
```

---

### CHECK 12: Filename/ID Format Validation ⭐ NEW

**Purpose**: Validate filename matches ID naming standards
**Type**: Error (blocking)

**Valid Examples**:
- `REQ-002_connection_heartbeat.md` ✅
- `REQ-023_quote_retrieval.md` ✅
- `REQ-009-01_prerequisite.md` ✅

**Invalid Examples**:
- `REQ-002.md` ❌ (missing description)
- `req-002_connection.md` ❌ (wrong case)
- `REQ002_connection.md` ❌ (missing hyphen)
- `REQ-002_Connection.md` ❌ (uppercase in slug)

**Pattern**: `REQ-\d{3,4}(-\d{2,3})?_[a-z0-9_]+\.md`

**Error Messages**:
```
❌ ERROR: Invalid filename format: req-002_connection.md
         Expected: REQ-NNN_{slug}.md or REQ-NNN-YY_{slug}.md

❌ ERROR: H1 header ID doesn't match filename
         Filename ID: REQ-002
         H1 Header: # REQ-003: Connection Monitoring
```

**Fix**:
1. Rename file to match pattern
2. Ensure H1 header ID matches filename ID
3. Use lowercase with underscores in slug

**Reference**: `ID_NAMING_STANDARDS.md`

---

### CHECK 13: Resource Tag Validation (Template 2.0) ⭐ NEW

**Purpose**: Verify [RESOURCE_INSTANCE] tag in H1 for Template 2.0
**Type**: Error (blocking for Template 2.0)

**Applies To**: Template 2.0 only (skipped for Template 1.0)

**Valid Examples**:
```markdown
# REQ-001: [EXTERNAL_SERVICE_GATEWAY] IB Gateway Connection ✅
# REQ-002: [HEALTH_CHECK_SERVICE] Heartbeat Monitoring ✅
# REQ-003: [RESILIENCE_PATTERN] Automatic Reconnection ✅
```

**Invalid Examples**:
```markdown
# REQ-001: IB Gateway Connection ❌ (missing tag)
# REQ-002: Connection Monitoring ❌ (missing tag)
```

**Valid Resource Tags**:

**Note**: Resource tags are project-specific. See project architecture documentation (ADR) for the authoritative resource taxonomy. The examples below represent common patterns but are not exhaustive.

**Common Examples**:
- `[EXTERNAL_SERVICE_GATEWAY]`
- `[HEALTH_CHECK_SERVICE]`
- `[STATE_MACHINE]`
- `[RESILIENCE_PATTERN]`
- `[CONFIGURATION_LAYER]`
- `[OBSERVABILITY]`
- `[DATA_VALIDATION]`
- `[ASYNC_PROCESSING]`

**Projects may define custom resource tags in their architecture documentation.**

**Error Message**:
```
❌ ERROR: Template 2.0 requires [RESOURCE_INSTANCE] tag in H1
         Current H1: # REQ-002: Connection Monitoring
         Expected: # REQ-002: [HEALTH_CHECK_SERVICE] Connection Monitoring
```

**Fix**:
```markdown
# REQ-002: [HEALTH_CHECK_SERVICE] Connection Heartbeat Monitoring
```

**Reference**: `REQ-TEMPLATE-V3.md` (H1 Header Format - includes resource instance tags)

---

### CHECK 14: Cumulative Tagging Hierarchy (Layer 7) ⭐ NEW

**Purpose**: Enforce complete traceability chain via embedded tags
**Type**: Error (blocking) - **CRITICAL**

**Required Tags** (all 6 mandatory):
```markdown
@brd: BRD.NNN.NNN
@prd: PRD.NNN.NNN
@ears: EARS.NNN.NNN
@bdd: BDD.NNN.NNN
@adr: ADR-NNN
@sys: SYS.NNN.NNN
```

**Valid Examples**:
```markdown
@brd: BRD.009.015, BRD.009.006 ✅
@prd: PRD.016.003 ✅
@ears: EARS.012.002 ✅
@bdd: BDD.015.007 ✅
@adr: ADR-033 ✅
@sys: SYS.012.001 ✅
```

**Invalid Examples**:
```markdown
@brd BRD.009.015 ❌ (missing colon after tag type)
@brd: BRD-009 ❌ (missing sub-ID)
brd: BRD.009.015 ❌ (missing @ prefix)
```

**Error Messages**:
```
❌ ERROR: Missing cumulative tags (Layer 7 requires all 6):
         Missing: @ears @bdd @adr
         Required: @brd, @prd, @ears, @bdd, @adr, @sys
         Reference: doc-flow TRACEABILITY.md section 2.5

❌ ERROR: Invalid tag format: @brd BRD.009.015
         Expected: @type: DOC-ID:NNN (numeric sub-ID)
         Example: @brd: BRD.009.015
```

**Fix**:
1. Add all 6 missing tags to section 11 (Traceability)
2. Use format: `@type: TYPE.NNN.NNN (Unified Feature ID)`
3. Verify all referenced documents exist

**Reference**: `TRACEABILITY.md` section 2.5 (Cumulative Tagging Hierarchy)

---

### CHECK 15: Complete Upstream Chain (6 Layers) ⭐ NEW

**Purpose**: Verify upstream sources table includes all required artifact types
**Type**: Error (blocking)

**Required Upstream Layers**:
1. **BRD** - Business Requirements
2. **PRD** - Product Requirements
3. **EARS** - Easy Approach to Requirements Syntax
4. **BDD** - Behavior-Driven Development scenarios
5. **ADR** - Architecture Decision Records
6. **SYS** - System Requirements

**Valid Example**:
```markdown
### Upstream Sources

| Source Type | Document ID | Document Title | Relevant sections | Relationship |
|-------------|-------------|----------------|-------------------|--------------|
| BRD | [BRD-001](...) | ... | ... | Primary business need |
| PRD | [PRD-001](...) | ... | ... | Product requirement |
| EARS | [EARS-012](...) | ... | ... | Formal requirement |
| BDD | [BDD-015](...) | ... | ... | Acceptance test |
| ADR | [ADR-033](...) | ... | ... | Architecture decision |
| SYS | [SYS-002](...) | ... | ... | Parent system requirement |
```

**Error Message**:
```
❌ ERROR: Incomplete upstream chain - missing: EARS BDD ADR
         Complete chain required: BRD → PRD → EARS → BDD → ADR → SYS
         Reference: REQ-TEMPLATE-V3.md section 11 (Traceability)
```

**Fix**:
1. Add missing upstream source types to table
2. Ensure markdown links include relative paths
3. Add specific relationship descriptions (not generic)

**Reference**: `REQ-TEMPLATE-V3.md` section 11 (Traceability - Complete Upstream Chain)

---

### CHECK 16: Markdown Link Resolution ⭐ NEW

**Purpose**: Validate all cross-reference links resolve to existing files
**Type**: Error + Warning

**Valid Link Format**:
```markdown
[REQ-003](../REQ/risk/lim/REQ-003_resource_limit.md#REQ-003) ✅
[ADR-033](../../ADR/ADR-033_architecture.md#ADR-033) ✅
```

**Invalid Examples**:
```markdown
[REQ-003](REQ-003.md) ❌ (missing relative path)
[ADR-033](../../ADR/ADR-999.md) ❌ (file doesn't exist)
```

**Error Message** (broken link):
```
❌ ERROR: Broken link - file not found
         Link: ../../ADR/ADR-999_architecture.md
         Resolved: [project_root]/docs/ADR/ADR-999_architecture.md
```

**Warning Message** (missing anchor):
```
⚠️  WARNING: Anchor possibly missing in ADR-033_architecture.md: #ADR-033
```

**Fix**:
1. Verify file exists at specified path
2. Use correct relative path from current file location
3. Ensure anchor (#ID) exists in target document

---

### CHECK 17: Traceability Matrix (Complex REQs) ⭐ NEW

**Purpose**: Recommend matrix for complex requirements
**Type**: Warning

**Complexity Indicators**:
- Upstream sources ≥ 5
- Sub-components present (REQ-NNN:COMP-ID format)

**Warning Message**:
```
⚠️  WARNING: Complex REQ detected but section 11.4 (Traceability Matrix) missing
         Upstream sources: 7 (≥5 suggests complexity)
         Sub-components: yes
         Recommendation: Add section 11.4 or create separate REQ-NNN_TRACEABILITY_MATRIX.md
         Reference: REQ-TEMPLATE-V3.md section 11 (Traceability)
```

**Fix Options**:

**Option 1 - Inline Matrix** (3-10 components):
```markdown
### 11.4 Traceability Matrix

| Component ID | Upstream Sources | Downstream Artifacts | Status |
|--------------|------------------|---------------------|--------|
| REQ.045.001 | SYS.012.001, ADR-033 | SPEC-018, CTR-005 | Complete |
| REQ.045.002 | SYS.012.002, ADR-033 | SPEC-018 | Complete |
```

**Option 2 - Separate File** (10+ components):
- Create: `REQ-045_TRACEABILITY_MATRIX.md`
- Template: Available in doc_flow framework
- Link from section 11

**Reference**: `REQ-TEMPLATE-V3.md` section 11 (Traceability - includes matrix guidance)

---

### CHECK 18: SPEC-Ready Content Validation ⭐ NEW

**Purpose**: Verify SPEC-ready documents have actual implementation code
**Type**: Warning

**Applies When**: SPEC-Ready Score ≥ 90%

**Checks**:
1. **section 3**: Protocol/ABC class present
2. **section 4**: Pydantic/dataclass models present
3. **section 5**: Exception definitions present
4. **section 6**: YAML configuration present

**Warning Messages**:
```
⚠️  WARNING: SPEC-Ready ≥90% but no Protocol/ABC class in section 3
⚠️  WARNING: SPEC-Ready ≥90% but no Pydantic/dataclass models in section 4
⚠️  WARNING: SPEC-Ready ≥90% but no exception definitions in section 5
⚠️  WARNING: SPEC-Ready ≥90% but no YAML configuration in section 6
```

**Fix**: Add missing code examples to achieve claimed SPEC-Ready score

**Example - section 3**:
```python
from typing import Protocol

class HealthCheckMonitor(Protocol):
    async def start_monitoring(self, connection: IbConnection) -> MonitoringSession:
        ...
```

**Example - section 4**:
```python
from pydantic import BaseModel, Field

class HeartbeatConfig(BaseModel):
    heartbeat_interval_regulatory: float = Field(30.0, ge=1.0, le=300.0)
    connection_timeout_regulatory: float = Field(5.0, gt=0, le=60.0)
```

### CHECK 19: IMPL-Ready Score Validation ⭐ NEW

**Purpose**: Validate IMPL-ready score format and threshold for project management transition
**Type**: Error (blocking)

**Valid Examples**: `✅ 95% (Target: ≥90%)`

**Error Message**: `❌ MISSING: IMPL-Ready Score with ✅ emoji and percentage`

**Applies To**: All REQ documents progressing to project management layer

**Action**: Enforces REQ → IMPL progression quality gates

---

## Error Fix Guide

### Quick Fix Matrix

| Error Check | Quick Fix |
|-------------|-----------|
| **CHECK 1** | Add missing section: `## N. section Name` |
| **CHECK 2** | Add all 11 required fields to Document Control table |
| **CHECK 5** | Change version to semver: `2.0.1` |
| **CHECK 6** | Change dates to ISO 8601: `2025-11-18` |
| **CHECK 9** | Update score format: `✅ 95% (Target: ≥90%)` |
| **CHECK 10** | Update template version to: `3.0` |
| **CHECK 11** | Add change history entry for current version |
| **CHECK 12** | Rename file to match pattern, update H1 header |
| **CHECK 13** | Add resource tag to H1: `[HEALTH_CHECK_SERVICE]` |
| **CHECK 14** | Add all 6 cumulative tags (@brd through @sys) |
| **CHECK 15** | Add missing upstream sources (BRD/PRD/EARS/BDD/ADR/SYS) |
| **CHECK 16** | Fix broken links, use relative paths |

---

## Quick Reference

### Pre-Commit Validation

```bash
# Validate single file
./scripts/validate_req_template_v3.sh docs/REQ/api/ib/REQ-002_connection_heartbeat.md

# Validate all REQ files
find docs/REQ -name "REQ-*.md" -exec ./scripts/validate_req_template_v3.sh {} \;
```

### Expected Output

**Success (no errors/warnings)**:
```
✅ PASSED: All validation checks passed with no warnings

Errors: 0
Warnings: 0
```

**Success with warnings**:
```
⚠️  PASSED WITH WARNINGS: Document valid but has 2 warnings

Errors: 0
Warnings: 2
```

**Failure**:
```
❌ FAILED: 3 critical errors found

Errors: 3
Warnings: 1
```

### Validation Tiers Summary

| Tier | Checks | Type | Action |
|------|--------|------|--------|
| **Tier 1** | 1, 2, 3 (Upstream Sources), 5, 6, 9, 10, 11, 12, 13, 14, 15, 16 | Error | Must fix before commit |
| **Tier 2** | 3 (Downstream/Code paths), 7, 8, 17, 18 | Warning | Recommended to fix |
| **Tier 3** | 4 | Info | No action required |

---

## Common Mistakes

### Mistake #1: Missing Cumulative Tags

**Error**:
```
❌ ERROR: Missing cumulative tags (Layer 7 requires all 6):
         Missing: @ears @bdd @adr
```

**Cause**: REQ document missing upstream artifact tags

**Fix**:
```markdown
## 11. Traceability

@brd: BRD.009.015
@prd: PRD.016.003
@ears: EARS.012.002
@bdd: BDD.015.007
@adr: ADR-033
@sys: SYS.012.001
```

---

### Mistake #2: Invalid Filename Format

**Error**:
```
❌ ERROR: Invalid filename format: REQ-002.md
         Expected: REQ-NNN_{slug}.md
```

**Cause**: Missing descriptive slug in filename

**Fix**: Rename file to `REQ-002_connection_heartbeat_monitoring.md`

---

### Mistake #3: H1 Header Mismatch

**Error**:
```
❌ ERROR: H1 header ID doesn't match filename
         Filename ID: REQ-002
         H1 Header: # REQ-003: Connection Monitoring
```

**Cause**: H1 header has different ID than filename

**Fix**: Update H1 to match filename:
```markdown
# REQ-002: [HEALTH_CHECK_SERVICE] Connection Heartbeat Monitoring
```

---

### Mistake #4: Incomplete Upstream Chain

**Error**:
```
❌ ERROR: Incomplete upstream chain - missing: EARS BDD ADR
         Complete chain required: BRD → PRD → EARS → BDD → ADR → SYS
```

**Cause**: Missing required upstream artifact types in table

**Fix**: Add all 6 upstream types to Upstream Sources table

---

### Mistake #5: Broken Links

**Error**:
```
❌ ERROR: Broken link - file not found
         Link: ../../ADR/ADR-999_architecture.md
         Resolved: [project_root]/docs/ADR/ADR-999_architecture.md
```

**Cause**: Referenced file doesn't exist

**Fix**:
1. Verify file path is correct
2. Create missing document if needed
3. Update link to existing document

---

### Mistake #6: Missing Resource Tag (Template 2.0)

**Error**:
```
❌ ERROR: Template 2.0 requires [RESOURCE_INSTANCE] tag in H1
         Current H1: # REQ-002: Connection Monitoring
```

**Cause**: Template 2.0 requires resource classification tag

**Fix**:
```markdown
# REQ-002: [HEALTH_CHECK_SERVICE] Connection Heartbeat Monitoring
```

---

### Mistake #7: SPEC-Ready Score Without Content

**Warning**:
```
⚠️  WARNING: SPEC-Ready ≥90% but no Protocol/ABC class in section 3
⚠️  WARNING: SPEC-Ready ≥90% but no Pydantic/dataclass models in section 4
```

**Cause**: Claimed SPEC-Ready score but missing implementation code

**Fix**: Add code examples to sections 3-6 or reduce score to match completeness

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 3.0.1 | 2025-11-18 | Updated CHECK 2 to require all 11 Document Control fields, CHECK 10 to enforce template version 3.0 only (no legacy versions), enhanced CHECK 13 with project-specific resource tag guidance, corrected Validation Tiers Summary to split CHECK 3, updated Quick Fix Matrix | System Architect |
| 3.0.0 | 2025-11-18 | Initial validation rules for v3.0 script with cumulative tagging, filename validation, resource tags, link resolution | System Architect |

---

---

**Maintained By**: System Architect, Quality Assurance Team
**Review Frequency**: Updated with script and template enhancements
**Support**: See [REQ-TEMPLATE-V3.md](REQ-TEMPLATE-V3.md) for comprehensive template guidance
**Related Documents**:
- [REQ-TEMPLATE-V3.md](REQ-TEMPLATE-V3.md) - Current template (v3.0)
- [README.md](README.md) - REQ directory guide with creation steps
- [archived/REQ-TEMPLATE-UNIFIED-ARCHIVED.md](archived/REQ-TEMPLATE-UNIFIED-ARCHIVED.md) - Archived template (v3.0.2)
