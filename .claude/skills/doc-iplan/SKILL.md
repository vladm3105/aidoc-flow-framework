---
name: "doc-iplan: Create Implementation Plans (Layer 12)"
name: doc-iplan
description: Create Implementation Plans (IPLAN) - Layer 12 artifact converting TASKS into session-based bash command execution plans
tags:
  - sdd-workflow
  - layer-12-artifact
  - shared-architecture
custom_fields:
  layer: 12
  artifact_type: IPLAN
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  skill_category: core-workflow
  upstream_artifacts: [BRD,PRD,EARS,BDD,ADR,SYS,REQ,IMPL,CTR,SPEC,TASKS]
  downstream_artifacts: [Code]
---

# doc-iplan

## Purpose

Create **Implementation Plans (IPLAN)** - Layer 12 artifact in the SDD workflow that converts TASKS into session-based, executable bash command sequences for implementation.

**Layer**: 12

**Upstream**: BRD (Layer 1), PRD (Layer 2), EARS (Layer 3), BDD (Layer 4), ADR (Layer 5), SYS (Layer 6), REQ (Layer 7), IMPL (Layer 8), CTR (Layer 9), SPEC (Layer 10), TASKS (Layer 11)

**Downstream Artifacts**: Code (Layer 13)

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


Before creating IPLAN, read:

1. **Shared Standards**: `.claude/skills/doc-flow/SHARED_CONTENT.md`
2. **Upstream TASKS**: Read task breakdown (PRIMARY SOURCE)
3. **Template**: `ai_dev_flow/IPLAN/IPLAN-TEMPLATE.md`
4. **Creation Rules**: `ai_dev_flow/IPLAN/IPLAN_CREATION_RULES.md`
5. **Validation Rules**: `ai_dev_flow/IPLAN/IPLAN_VALIDATION_RULES.md`
6. **Validation Script**: `ai_dev_flow/scripts/validate_iplan.sh`
7. **IPLAN Conventions**: ID_NAMING_STANDARDS.md (as of 2025-11-26)

## When to Use This Skill

Use `doc-iplan` when:
- Have completed BRD through TASKS (Layers 1-11)
- Ready to convert tasks to executable bash commands
- Preparing for implementation session
- Need step-by-step execution plan
- You are at Layer 12 of the SDD workflow

## IPLAN-Specific Guidance

### 1. File Naming Convention

**Format**: `IPLAN-NNN_{descriptive_slug}.md`

**Components**:
- **IPLAN-NNN**: Sequential 3-digit ID (e.g., IPLAN-001, IPLAN-002)
- **descriptive_slug**: Short lowercase description with underscores (e.g., gateway_connection, trade_validation)

**Examples**:
- `IPLAN-001_gateway_connection.md`
- `IPLAN-002_trade_validation.md`
- `IPLAN-003_market_data_streaming.md`

**Filename Validation**:
```bash
# Validate filename format
filename="IPLAN-001_gateway_connection.md"
if [[ ! $filename =~ ^IPLAN-[0-9]{3,4}_[a-z0-9_]+\.md$ ]]; then
  echo "ERROR: Invalid format. Must be IPLAN-NNN_{slug}.md"
  exit 1
fi
```

**Tag Format**: `@iplan: IPLAN-001` (use ID only, not full filename)

### 1.1 Required Frontmatter Structure

**CRITICAL**: Every IPLAN file MUST include this frontmatter structure with the `tags:` section:

```yaml
---
tags:
  - implementation-plan
  - layer-12-artifact
  - active
name: "IPLAN-NNN: [Descriptive Task/Feature Name]"
layer: 12
artifact_type: IPLAN
parent_tasks: TASKS-NNN
dependencies: []
status: ready
created: YYYY-MM-DD
estimated_effort_hours: NN
# Layer 12 Cumulative Traceability Tags
traceability:
  brd: "BRD-NNN" or null
  prd: "PRD-NNN" or null
  ears: "EARS-NNN" or null
  bdd: "BDD-NNN" or null
  adr: "ADR-NNN" or null
  sys: "SYS-NNN"
  req: "REQ-NNN"
  spec: "SPEC-NNN"
  tasks: "TASKS-NNN"
---
```

**MANDATORY TAGS**:
- `implementation-plan` - Identifies document type
- `layer-12-artifact` - **REQUIRED** for validation (validation will FAIL without this)
- `active` - Document status

**Validation will reject files missing `layer-12-artifact` tag.**

### 2. Session-Based Execution Plan

**Purpose**: Convert TASKS into executable bash command sequences

**Format**:
```markdown
## Execution Plan

### Session 1: Project Setup (Estimated: 1.5 hours)

**Tasks**: TASK-001-001, TASK-001-002

**Commands**:
```bash
# TASK-001-001: Initialize Project Structure
mkdir -p src/controllers src/services src/repositories src/models
mkdir -p tests/unit tests/integration
touch src/controllers/data_validation_controller.py
touch src/services/data_validator.py
touch src/repositories/data_repository.py
touch src/models/data_request.py
touch src/__init__.py

# Verify structure created
ls -R src/

# TASK-001-002: Set Up Development Environment
cat > requirements.txt <<EOF
fastapi==0.104.1
pydantic==2.5.0
sqlalchemy==2.0.23
pytest==7.4.3
pytest-cov==4.1.0
EOF

cat > pyproject.toml <<EOF
[project]
name = "data-validator"
version = "1.0.0"
requires-python = ">=3.11"
EOF

# Install dependencies
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Verify installation
pip list | grep fastapi
```

**Validation**:
```bash
# Verify all files created
test -f src/controllers/data_validation_controller.py && echo "✓ Controller file exists"
test -f src/services/data_validator.py && echo "✓ Service file exists"

# Verify dependencies installed
python -c "import fastapi; print(f'✓ FastAPI {fastapi.__version__} installed')"
```

**Rollback** (if needed):
```bash
rm -rf src/ tests/ requirements.txt pyproject.toml .venv
```
```

### 3. Required Sections

**Document Control** (MANDATORY - First section before all numbered sections)

**Core Sections**:
1. **Overview**: Session-based execution summary
2. **Prerequisites**: What must be ready before starting
3. **Execution Plan**: Session-by-session commands (primary content)
4. **Validation Commands**: How to verify each session
5. **Rollback Procedures**: How to undo if needed
6. **Notes and Warnings**: Important considerations
7. **Traceability**: Section 7 format with cumulative tags

### 4. Session Organization

**Typical Sessions**:

1. **Session 1: Project Setup** (infrastructure)
2. **Session 2: Data Models** (schemas, Pydantic models)
3. **Session 3: Business Logic** (services, algorithms)
4. **Session 4: API Layer** (controllers, routing)
5. **Session 5: Error Handling** (middleware, error codes)
6. **Session 6: Configuration** (env vars, settings)
7. **Session 7: Testing** (unit, integration tests)
8. **Session 8: Deployment** (Docker, CI/CD)

**Each Session Includes**:
- Tasks covered (TASK IDs)
- Bash commands (executable)
- Validation commands
- Rollback procedure

### 5. Command Format

**Bash Commands**:
- Must be executable (copy-paste ready)
- Include comments explaining each step
- Use heredocs for multi-line files
- Include error checking

**Example**:
```bash
# Create FastAPI controller
cat > src/controllers/data_validation_controller.py <<'EOF'
from fastapi import APIRouter, HTTPException
from src.models.data_request import DataRequest, ValidationResponse
from src.services.data_validator import validate_data_request

router = APIRouter()

@router.post("/api/v1/data/validate", response_model=ValidationResponse)
async def validate_data(record: DataRequest):
    """Validate data record endpoint"""
    try:
        result = await validate_data_request(record)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
EOF

# Verify file created and syntax valid
test -f src/controllers/data_validation_controller.py || exit 1
python -m py_compile src/controllers/data_validation_controller.py
```

### 6. Validation Commands

**After Each Session**: Provide commands to verify success

**Format**:
```markdown
**Validation**:
```bash
# Verify files exist
test -f src/controllers/data_validation_controller.py && echo "✓ Controller created"
test -f src/services/data_validator.py && echo "✓ Service created"

# Verify syntax valid
python -m py_compile src/controllers/*.py
python -m py_compile src/services/*.py

# Run unit tests
pytest tests/unit/ -v

# Check test coverage
pytest tests/unit/ --cov=src --cov-report=term-missing
```
```

### 7. Rollback Procedures

**For Each Session**: Provide commands to undo changes

**Format**:
```markdown
**Rollback** (if needed):
```bash
# Remove created files
rm -f src/controllers/data_validation_controller.py
rm -f src/services/data_validator.py

# Reset git (if committed)
git reset --hard HEAD~1
```
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

**Layer 12 (IPLAN)**: Must include tags from Layers 1-11

**Tag Count**: 9-11 tags (minimum 9, maximum 11)

**Minimum (IMPL and CTR skipped)**:
```markdown
## Traceability

**Required Tags** (Cumulative Tagging Hierarchy - Layer 12):
```markdown
@brd: BRD.001.003
@prd: PRD.001.002
@ears: EARS.001.001
@bdd: BDD.001.001
@adr: ADR-033, ADR-045
@sys: SYS.001.001
@req: REQ.001.001
@spec: SPEC-001
@tasks: TASKS.001.001
```

**Maximum (IMPL and CTR included)**:
```markdown
@brd: BRD.001.003
@prd: PRD.001.002
@ears: EARS.001.001
@bdd: BDD.001.001
@adr: ADR-033, ADR-045
@sys: SYS.001.001
@req: REQ.001.001
@impl: IMPL.001.001
@ctr: CTR-001
@spec: SPEC-001
@tasks: TASKS.001.001
```

## Upstream/Downstream Artifacts

**Upstream Sources**:
- **BRD** (Layer 1) - Business requirements
- **PRD** (Layer 2) - Product features
- **EARS** (Layer 3) - Formal requirements
- **BDD** (Layer 4) - Test scenarios
- **ADR** (Layer 5) - Architecture decisions
- **SYS** (Layer 6) - System requirements
- **REQ** (Layer 7) - Atomic requirements
- **IMPL** (Layer 8) - Implementation approach (optional)
- **CTR** (Layer 9) - Data contracts (optional)
- **SPEC** (Layer 10) - Technical specifications
- **TASKS** (Layer 11) - Task breakdown (PRIMARY SOURCE)

**Downstream Artifacts**:
- **Code** (Layer 13) - Implementation

**Same-Type Document Relationships** (conditional):
- `@related-iplan: IPLAN-NNN` - IPLANs sharing session context
- `@depends-iplan: IPLAN-NNN` - IPLAN that must be completed first

## Creation Process

### Step 1: Read Upstream TASKS

Read TASKS (Layer 11) - task breakdown to convert to commands.

### Step 2: Reserve ID Number

Check `docs/IPLAN/` for next available ID number.

### Step 3: Create IPLAN File

**Location**: `docs/IPLAN/IPLAN-NNN_{slug}.md` (template available at `ai_dev_flow/IPLAN/`)

**Example**: `docs/IPLAN/IPLAN-001_data_validation.md`

### Step 4: Fill Document Control Section

Complete metadata and Document Revision History table.

### Step 5: Write Overview

Summarize session-based execution approach.

### Step 6: Define Prerequisites

List what must be ready before starting (database, credentials, etc.).

### Step 7: Create Session-by-Session Execution Plan

For each session:
1. List tasks covered (TASK IDs)
2. Write executable bash commands
3. Add comments explaining each step
4. Include error checking

### Step 8: Add Validation Commands

For each session, provide commands to verify success.

### Step 9: Add Rollback Procedures

For each session, provide commands to undo changes.

### Step 10: Document Notes and Warnings

Important considerations, potential issues.

### Step 11: Add Cumulative Tags

Include all 9-11 upstream tags (@brd through @tasks).

### Step 12: Create/Update Traceability Matrix

**MANDATORY**: Update `docs/IPLAN/IPLAN-000_TRACEABILITY_MATRIX.md`

### Step 13: Validate IPLAN

```bash
ai_dev_flow/scripts/validate_iplan.sh docs/IPLAN/IPLAN-001_*.md

python ai_dev_flow/scripts/validate_tags_against_docs.py --artifact IPLAN-001 --expected-layers brd,prd,ears,bdd,adr,sys,req,impl,ctr,spec,tasks --strict

# Test bash commands (dry-run)
bash -n docs/IPLAN/IPLAN-001_*.md  # syntax check
```

### Step 14: Commit Changes

Commit IPLAN file and traceability matrix.

## Validation

### Automated Validation

```bash
# Quality gates
scripts/validate_quality_gates.sh docs/IPLAN/IPLAN-001_*.md

# IPLAN format validation
ai_dev_flow/scripts/validate_iplan.sh docs/IPLAN/IPLAN-001_*.md

# Cumulative tagging
python ai_dev_flow/scripts/validate_tags_against_docs.py \
  --artifact IPLAN-001 \
  --expected-layers brd,prd,ears,bdd,adr,sys,req,impl,ctr,spec,tasks \
  --strict

# Bash syntax check
bash -n docs/IPLAN/IPLAN-001_*.md
```

### Manual Checklist

- [ ] File naming follows IPLAN-NNN_{slug}.md format
- [ ] Document Control section at top
- [ ] Overview explains session-based approach
- [ ] Prerequisites listed (database, credentials, etc.)
- [ ] Execution Plan organized into sessions
- [ ] Each session lists covered TASK IDs
- [ ] Bash commands are executable (copy-paste ready)
- [ ] Comments explain each command
- [ ] Validation commands provided for each session
- [ ] Rollback procedures provided for each session
- [ ] Notes and Warnings documented
- [ ] Cumulative tags: @brd through @tasks (9-11 tags) included
- [ ] Traceability matrix updated
- [ ] Bash syntax valid (bash -n passes)

## Common Pitfalls

1. **Non-executable commands**: Commands must be copy-paste ready
2. **Missing validation**: Each session needs validation commands
3. **No rollback**: Must provide undo procedures
4. **Wrong file naming**: Must use IPLAN-NNN_{slug}.md format
5. **Missing cumulative tags**: Layer 12 must include all 9-11 upstream tags
6. **No error checking**: Commands should check for errors

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
python ai_dev_flow/scripts/validate_cross_document.py --document docs/IPLAN/IPLAN-NNN_slug.md --auto-fix

# Layer validation (Phase 2) - run when all IPLAN documents complete
python ai_dev_flow/scripts/validate_cross_document.py --layer IPLAN --auto-fix
```

### Layer-Specific Upstream Requirements

| This Layer | Required Upstream Tags | Count |
|------------|------------------------|-------|
| IPLAN (Layer 12) | @brd, @prd, @ears, @bdd, @adr, @sys, @req, @spec, @tasks (+ @impl, @ctr if created) | 9-11 tags |

### Auto-Fix Actions (No Confirmation Required)

| Issue | Fix Action |
|-------|------------|
| Missing upstream tag | Add with upstream document reference |
| Invalid tag format | Correct to TYPE.NNN.NNN format |
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

After creating IPLAN, proceed to:

**Code Implementation** (Layer 13)

Execute the IPLAN session-by-session to implement the code.

## Reference Documents

For supplementary documentation related to IPLAN artifacts:
- **Format**: `IPLAN-REF-NNN_{slug}.md`
- **Skill**: Use `doc-ref` skill
- **Validation**: Minimal (non-blocking)
- **Examples**: Session execution guides, environment setup guides

## Related Resources

- **Template**: `ai_dev_flow/IPLAN/IPLAN-TEMPLATE.md` (primary authority)
- **IPLAN Creation Rules**: `ai_dev_flow/IPLAN/IPLAN_CREATION_RULES.md`
- **IPLAN Validation Rules**: `ai_dev_flow/IPLAN/IPLAN_VALIDATION_RULES.md`
- **IPLAN README**: `ai_dev_flow/IPLAN/README.md`
- **ID Naming Standards**: `ai_dev_flow/ID_NAMING_STANDARDS.md`
- **Shared Standards**: `.claude/skills/doc-flow/SHARED_CONTENT.md`

## Quick Reference

**IPLAN Purpose**: Convert TASKS into session-based bash command execution plans

**Layer**: 12

**Tags Required**: @brd through @tasks (9-11 tags)

**Format**: Session-based execution plan with bash commands

**IPLAN-Ready Score**: ≥90% target for implementation readiness

**File Naming**: `IPLAN-NNN_{slug}.md`

**Tag Format**: `@iplan: IPLAN-001` (use ID only, not full filename)

**Key Sections**:
- Prerequisites
- Execution Plan (session-by-session)
- Validation Commands
- Rollback Procedures
- Notes and Warnings

**Session Structure**:
- Tasks covered (TASK IDs)
- Executable bash commands
- Validation commands
- Rollback procedure

**Next**: Code Implementation (Layer 13)
