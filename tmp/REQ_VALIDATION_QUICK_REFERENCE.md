# REQ Validation Quick Reference Guide

---

## 1. Validation Scripts at a Glance

### Execution Matrix

| Script | Use Case | Command | Pass/Fail |
|--------|----------|---------|-----------|
| `validate_requirement_ids.py` | Check ID format + duplicate detection | `python validate_requirement_ids.py --directory REQ/` | 0=pass, 1=fail |
| `validate_req_spec_readiness.py` | Score SPEC-generation readiness | `python validate_req_spec_readiness.py --directory REQ/` | 0=pass, 1=fail |
| `validate_tags_against_docs.py` | Verify cumulative tagging hierarchy | `python validate_tags_against_docs.py --source REQ/ --docs ai_dev_flow/ --validate-cumulative` | 0=pass, 1=fail |
| `validate_traceability_matrix.py` | Check matrix consistency | `python validate_traceability_matrix.py --matrix REQ/matrix.md --input REQ/ --strict` | 0=pass, 1=fail |
| `validate_documentation_paths.py` | Find broken links | `python validate_documentation_paths.py --root ai_dev_flow/ --strict` | 0=pass, 1=fail |
| `generate_traceability_matrix.py` | Create matrix from scratch | `python generate_traceability_matrix.py --type REQ --input REQ/ --output matrix.md` | 0=pass, 1=fail |
| `update_traceability_matrix.py` | Sync existing matrix | `python update_traceability_matrix.py --matrix matrix.md --input REQ/ --dry-run` | 0=pass, 1=fail |

---

## 2. REQ Document Requirements

### Mandatory Structure (V2 Template - 12 Sections)

```
✅ ALWAYS REQUIRED:
   1. Description
   2. Document Control (Status, Version, Priority, Category, etc.)
   3. Interface Specifications (Protocol or ABC class)
   4. Data Schemas (JSON Schema OR Pydantic OR SQLAlchemy)
   5. Error Handling (Exception catalog with recovery strategies)
   6. Configuration (YAML examples + Pydantic validation)
   7. Non-Functional Requirements (Performance, Reliability, Security)
   8. Implementation Guidance (Algorithms, patterns, DI)
   9. Acceptance Criteria (AC-001, AC-002, ... with measurable outcomes)
   10. Verification Methods (BDD, unit tests, integration tests, performance tests)
   11. Traceability (@brd, @prd, @ears, @bdd, @adr, @sys tags + upstream/downstream)
   12. Change History (Version history table)

❌ CRITICAL = Sections 3-6 (must exist for SPEC-readiness)
⚠️  WARNINGS = Sections 1, 2, 7-12 (best practice)
```

### File Naming & Location

```
Format:        REQ-NNN_descriptive_slug.md
Pattern:       REQ-[001-999 or 1000+]_[lowercase_underscore_slug]
Location:      REQ/{category}/{subcategory}/REQ-NNN_slug.md
Examples:
   ✅ REQ/api/av/REQ-001_alpha_vantage_integration.md
   ✅ REQ/api/ib/REQ-002_ib_gateway_integration.md
   ✅ REQ/risk/lim/REQ-003_position_limit_enforcement.md
   ❌ REQ/REQ_integration.md (no ID)
   ❌ REQ/REQ-01_integration.md (2 digits instead of 3)
   ❌ REQ/REQ-001-Integration.md (wrong case in slug)
```

### Document Control Minimum Fields

```
| Field | Type | Example |
|-------|------|---------|
| Status | Draft/Review/Approved/Implemented/Verified/Retired | Approved |
| Version | Semantic | 2.0.1 |
| Priority | Critical/High/Medium/Low | High |
| Category | Functional/Non-Functional/Security/Performance | Functional |
| Source Document | Reference to upstream | PRD-003, SYS-008 |
| Verification Method | BDD/Spec/Unit/Integration/Contract | BDD |
| SPEC-Ready Score | 0-100% | 95% |
```

---

## 3. SPEC-Readiness Scoring

### Scoring Breakdown (100 Points Total)

```
SECTION PRESENCE (60 points):
  ✅ Section 3: Interface Specifications         +10pts (Protocol or ABC)
  ✅ Section 4: Data Schemas                    +10pts (≥2 of: JSON, Pydantic, SQLAlchemy)
  ✅ Section 5: Error Handling                  +10pts (Exception catalog table)
  ✅ Section 6: Configuration                   +10pts (YAML examples)
  ✅ Section 7: Non-Functional Requirements     +10pts (Quantified targets)
  ✅ No Placeholders                            +10pts (NO [TODO], [PLACEHOLDER], ...)

QUALITY CHECKS (40 points):
  ✅ Type Annotations                           +10pts (≥3 annotated functions)
  ✅ Error Recovery                             +10pts (≥2 strategies: retry, fallback, circuit breaker)
  ✅ Concrete Examples                          +10pts (≥10 domain-specific indicators)
  ✅ State Machines                             +10pts (Mermaid diagrams for workflows)

PASSING THRESHOLD: ≥90% (default, configurable)
```

### Quick Scoring Checklist

```
Section 3 (Interface Specs):
  ☑ Has Protocol class OR ABC class?
  ☑ Methods have type annotations?
  ☑ Docstrings explain parameters/returns/raises?
  
Section 4 (Data Schemas):
  ☑ JSON Schema definition present?
  ☑ Pydantic model with validators?
  ☑ Database schema (SQLAlchemy) OR just 2 above OK?
  
Section 5 (Error Handling):
  ☑ Exception catalog table with columns:
     - Exception Type | HTTP Code | Retry? | Recovery Strategy
     
Section 6 (Configuration):
  ☑ YAML config example present?
  ☑ Environment variables table?
  ☑ Pydantic/Dataclass config validation?
  
Section 7 (NFRs):
  ☑ Performance targets (p50, p95, p99)?
  ☑ Reliability targets (uptime %, error rate)?
  ☑ Security requirements (encryption, auth)?
  
Quality:
  ☑ ≥3 type-annotated functions visible?
  ☑ Retry policies mentioned?
  ☑ Real examples (AAPL, 182.50, user_id, etc)?
  ☑ Mermaid state diagram for complex flows?
  
Placeholders:
  ☑ NO [PLACEHOLDER], [TODO], [TBD] found?
  ☑ NO <insert X>, <fill in> found?
  ☑ NO bare ellipsis (...) in code?
```

---

## 4. Cumulative Tagging (Traceability)

### Tag Format & Requirements for REQ (Layer 7)

```
MANDATORY TAGS (6 required for REQ documents):

@brd: BRD-NNN[:REQUIREMENT-ID]
   └─ Example: @brd: BRD-001:FR-030

@prd: PRD-NNN[:REQUIREMENT-ID]
   └─ Example: @prd: PRD-003:FEATURE-002

@ears: EARS-NNN[:STATEMENT-ID]
   └─ Example: @ears: EARS-001:EVENT-003

@bdd: BDD-NNN[:SCENARIO-ID]
   └─ Example: @bdd: BDD-003:scenario-realtime-quote

@adr: ADR-NNN[(:ASPECT)]
   └─ Example: @adr: ADR-033

@sys: SYS-NNN[:SECTION-ID]
   └─ Example: @sys: SYS-008:PERF-001

PLACEMENT: Section 11 (Traceability) or top of document

EXAMPLE BLOCK:
────────────────────────────────────────────────────
@brd: BRD-001:FR-030
@prd: PRD-003:FEATURE-002
@ears: EARS-001:EVENT-003
@bdd: BDD-003:scenario-realtime-quote
@adr: ADR-033
@sys: SYS-008:PERF-001
────────────────────────────────────────────────────

VALIDATION:
  ✓ Document BRD-001 exists
  ✓ Requirement FR-030 exists within BRD-001
  ✓ All 6 tags present
  ✓ Tags in correct order (upstream → downstream)
```

---

## 5. Common Validation Failures & Fixes

### ID & Format Issues

```
❌ FAIL: Invalid filename format: REQ_api_integration.md

   CAUSE: Missing ID prefix
   FIX:   Rename to REQ-001_api_integration.md
   CHECK: python validate_requirement_ids.py --req-file REQ-001_api_integration.md

─────────────────────────────────────────────────────

❌ FAIL: Duplicate REQ-ID: REQ-001 found in multiple files

   CAUSE: Two files use same ID
   FILES: REQ/api/REQ-001_integration.md
          REQ/auth/REQ-001_access.md
   FIX:   Renumber second file to REQ-004_access.md
   CHECK: python validate_requirement_ids.py --directory REQ/

─────────────────────────────────────────────────────

❌ FAIL: Missing critical V2 sections: 3, 4, 5, 6

   CAUSE: Template sections not present
   FIX:   Copy from REQ-TEMPLATE.md Sections 3-6
   CHECK: python validate_requirement_ids.py --req-file REQ-001.md --check-v2-sections
```

### SPEC-Readiness Issues

```
❌ FAIL [60%]: REQ-001_integration.md

   ERRORS:
   ❌ Missing Section 3: Interface Specifications
      FIX: Add code block with Protocol or ABC:
      
      ### 3.1 Protocol Definition
      ```python
      from typing import Protocol
      class ExternalAPIClient(Protocol):
          async def connect(self, credentials) -> ConnectionResult: ...
          async def fetch_data(self, request) -> DataResponse: ...
      ```

   ❌ Missing Section 4 quality (only 1/3 schema types)
      FIX: Add Pydantic model:
      
      ### 4.2 Pydantic Models
      ```python
      class QuoteResponse(BaseModel):
          symbol: str
          price: float
          timestamp: datetime
      ```

   WARNINGS:
   ⚠️  No state machine diagrams
      FIX: Add Mermaid diagram in Section 5:
      
      ```mermaid
      stateDiagram-v2
          [*] --> Disconnected
          Disconnected --> Connecting: connect()
          Connecting --> Connected: success
      ```

   AFTER FIXES: Score ≈90-100% ✅ PASS
```

### Traceability Issues

```
❌ FAIL: REQ-001 missing tag: @sys

   TAGS FOUND: @brd, @prd, @ears, @bdd, @adr
   MISSING:    @sys
   FIX:        Add to Section 11 Traceability:
               @sys: SYS-008:PERF-001

─────────────────────────────────────────────────────

❌ FAIL: @adr references non-existent ADR-099

   FIX: Verify ADR-099 exists in ai_dev_flow/ADR/
        If not, update to valid ADR:
        @adr: ADR-033
        
   VERIFY: ls ai_dev_flow/ADR/ADR-033_*

─────────────────────────────────────────────────────

❌ FAIL: @bdd references non-existent scenario

   REFERENCED: BDD-003:scenario-realtime-quote
   FIX: Check BDD file for scenario name:
        grep -n "Scenario:" ai_dev_flow/BDD/BDD-003_*.feature
        
   UPDATE: If scenario named differently:
           @bdd: BDD-003:scenario-quote-fetch
```

### Path & Link Issues

```
❌ FAIL: Broken link with space in path

   PATH:   (.. /REQ-TEMPLATE.md)
   ISSUE:  Space after (..)
   FIX:    (../REQ-TEMPLATE.md)
   
   VERIFY: python validate_documentation_paths.py --strict

─────────────────────────────────────────────────────

❌ FAIL: Referenced file not found

   LINK:    [REQ Template](../../REQ/REQ-TEMPLATE.md)
   ISSUE:   Path resolves incorrectly
   ACTUAL:  ai_dev_flow/REQ-TEMPLATE.md (one level up)
   FIX:     [REQ Template](../REQ-TEMPLATE.md)
   
   VERIFY: python validate_documentation_paths.py --root ai_dev_flow/

─────────────────────────────────────────────────────

❌ FAIL: Case mismatch

   FOUND:   'req-001.md'
   ACTUAL:  'REQ-001_integration.md'
   FIX:     Update link: ../REQ-001_integration.md
   
   VERIFY: Exact case match in filesystem
```

---

## 6. Validation Command Cheat Sheet

### Single File Validation

```bash
# Check ID format only
python validate_requirement_ids.py --req-file REQ/api/REQ-001.md

# Check ID format + V2 template sections
python validate_requirement_ids.py --req-file REQ/api/REQ-001.md --check-v2-sections

# Check SPEC-readiness score
python validate_req_spec_readiness.py --req-file REQ/api/REQ-001.md --min-score 90
```

### Directory Validation

```bash
# Validate all REQ files (IDs + structure)
python validate_requirement_ids.py --directory REQ/ --check-v2-sections

# Validate SPEC-readiness for all
python validate_req_spec_readiness.py --directory REQ/ --min-score 90

# Validate all paths in framework
python validate_documentation_paths.py --root ai_dev_flow/ --strict

# Validate tags
python validate_tags_against_docs.py --source REQ/ --docs ai_dev_flow/ --validate-cumulative
```

### Matrix Operations

```bash
# Generate fresh matrix
python generate_traceability_matrix.py --type REQ --input REQ/ --output REQ/matrix.md

# Preview updates (dry-run)
python update_traceability_matrix.py --matrix REQ/matrix.md --input REQ/ --dry-run

# Apply updates with changelog
python update_traceability_matrix.py --matrix REQ/matrix.md --input REQ/ --changelog updates.md

# Validate matrix consistency
python validate_traceability_matrix.py --matrix REQ/matrix.md --input REQ/ --strict
```

### Complete Validation Suite

```bash
#!/bin/bash
# Validate all aspects of REQ directory

set -e
cd ai_dev_flow

echo "=== Step 1: ID Validation ==="
python scripts/validate_requirement_ids.py --directory REQ/ --check-v2-sections

echo "=== Step 2: SPEC-Readiness Check ==="
python scripts/validate_req_spec_readiness.py --directory REQ/ --min-score 90

echo "=== Step 3: Traceability Matrix ==="
python scripts/validate_traceability_matrix.py --matrix REQ/REQ-000_TRACEABILITY_MATRIX-TEMPLATE.md --input REQ/ --strict

echo "=== Step 4: Tag Validation ==="
python scripts/validate_tags_against_docs.py --source REQ/ --docs . --validate-cumulative

echo "=== Step 5: Path Integrity ==="
python scripts/validate_documentation_paths.py --root . --strict

echo "✅ All validations passed!"
```

---

## 7. Pre-Commit Hook Setup

```bash
#!/bin/bash
# Save as: .git/hooks/pre-commit
# Make executable: chmod +x .git/hooks/pre-commit

echo "🔍 Validating REQ documents..."

FAILED=0

# Check REQ files only if they were modified
if git diff --cached --name-only | grep -q "ai_dev_flow/REQ/"; then
    
    if ! python ai_dev_flow/scripts/validate_requirement_ids.py \
         --directory ai_dev_flow/REQ/ --check-v2-sections; then
        echo "❌ ID validation failed"
        FAILED=1
    fi
    
    if ! python ai_dev_flow/scripts/validate_req_spec_readiness.py \
         --directory ai_dev_flow/REQ/ --min-score 85; then
        echo "❌ SPEC-readiness check failed"
        FAILED=1
    fi
fi

if [ $FAILED -eq 1 ]; then
    echo "❌ Pre-commit validation failed. Fix issues and retry."
    exit 1
fi

echo "✅ Pre-commit validation passed!"
exit 0
```

---

## 8. Troubleshooting Matrix

| Symptom | Root Cause | Diagnosis | Solution |
|---------|-----------|-----------|----------|
| "REQ-NNN not found" | Wrong layer/directory | `find . -name "REQ-NNN*"` | Check file exists, correct path |
| Script fails silently | Python version <3.7 | `python --version` | Upgrade to 3.7+ |
| "Permission denied" | Script not executable | `ls -la script.py` | `chmod +x script.py` |
| Matrix counts mismatch | New/deleted files | `git status` | Run `update_traceability_matrix.py` |
| Tags not validating | Wrong format | Read tag examples | Fix to `@type: DOC-NNN:ID` |
| SPEC score <90% | Missing sections | Check warning list | Copy sections from template |
| Broken links persist | Path still wrong | Run validation script | Fix path syntax |

---

## 9. Performance Characteristics

| Operation | Scale | Time |
|-----------|-------|------|
| Validate single file | 1 file | <100ms |
| Validate directory | 50 files | <1s |
| Generate matrix | 50 docs | <2s |
| Validate large framework | 500 files | <5s |

**Memory**: <50MB for all operations
**Dependencies**: Python 3.7+ only (no pip installs)

---

## 10. Integration Examples

### GitHub Actions (on every push/PR)

```yaml
- name: Validate REQ Documents
  run: |
    python ai_dev_flow/scripts/validate_requirement_ids.py --directory ai_dev_flow/REQ/ --check-v2-sections
    python ai_dev_flow/scripts/validate_req_spec_readiness.py --directory ai_dev_flow/REQ/ --min-score 90
```

### Jenkins Pipeline

```groovy
stage('Validate REQ') {
    steps {
        sh 'python ai_dev_flow/scripts/validate_requirement_ids.py --directory ai_dev_flow/REQ/ --check-v2-sections'
        sh 'python ai_dev_flow/scripts/validate_req_spec_readiness.py --directory ai_dev_flow/REQ/ --min-score 90'
    }
}
```

### GitLab CI

```yaml
validate_req:
  stage: test
  script:
    - python ai_dev_flow/scripts/validate_requirement_ids.py --directory ai_dev_flow/REQ/ --check-v2-sections
    - python ai_dev_flow/scripts/validate_req_spec_readiness.py --directory ai_dev_flow/REQ/ --min-score 90
```

---

**Last Updated**: 2025-11-19  
**Template Version**: V2 (12 sections, SPEC-ready)  
**Layer**: 7 of 16-layer SDD workflow  
**Default Threshold**: 90% SPEC-readiness

