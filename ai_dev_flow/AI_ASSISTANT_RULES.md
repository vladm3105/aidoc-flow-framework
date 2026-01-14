---
title: "AI Assistant Execution Rules"
tags:
  - framework-guide
  - shared-architecture
  - required-both-approaches
  - active
custom_fields:
  document_type: execution-rules
  priority: shared
  development_status: active
  applies_to: [project-initialization, ai-assistants]
  version: "1.0"
  target_tools: [Claude AI, Claude Code, Gemini CLI, GitHub Copilot, Cursor, Windsurf]
---

# AI Assistant Execution Rules

**Version**: 1.0
**Purpose**: Core rules for AI Coding Assistants executing AI Dev Flow framework
**Target Tools**: Claude AI, Claude Code, Gemini CLI, GitHub Copilot, Cursor, Windsurf
**Status**: Production

---

See also:
- AI Assistant Playbook (index): AI_ASSISTANT_PLAYBOOK.md
- Tool Optimization Guide (sizes, validation, style): AI_TOOL_OPTIMIZATION_GUIDE.md

> Path conventions: Examples below use a portable `docs/` root for new projects. In this repository, artifact folders live at the ai_dev_flow root (no `docs/` prefix). When running commands here, drop the `docs/` prefix. For details, see README → "Using This Repo".

## Assistant Output Style (All Tools)

- Use professional software development language (engineering tone).
- Avoid marketing or emotional language; be factual and concise.
- Be token‑efficient: prefer bullets, short paragraphs, and concrete commands.
- Output should be actionable: commands, file paths, code identifiers, checklists.
- Emoji policy: informational only; keep to a minimum (0–1 typical).
- Avoid redundancy and filler (no restating prompts, apologies, or small talk).

### Claude Code — Stricter Rules

- Keep responses compact and highly structured.
- Default to zero emoji; at most a single informational emoji for long summaries.
- Prefer diffs, code blocks, and validations over narrative text.
- Remove superfluous preambles; focus on steps, results, and next actions.

See also: AI_TOOL_OPTIMIZATION_GUIDE.md → “Style and Tone Guidelines”.

## Critical Execution Order

AI Coding Assistants **MUST** follow this sequence when initializing a new project:

1. **Domain Selection** → Ask user for project domain (Step 1)
2. **Folder Structure Creation** → Create all directories before any documents (Step 2)
3. **Domain Configuration** → Load and apply domain-specific settings (Step 3)
4. **Template Initialization** → Copy templates and replace placeholders (Step 4)
5. **Contract Decision** → Run contract questionnaire (Step 5)
6. **Index File Setup** → Initialize all index files (Step 6)
7. **Document Creation** → Begin generating project documents (Step 7)

---

## Rule 1: Domain Selection (FIRST STEP)

### Execution
At project initialization, AI Assistant **MUST** ask:

```
"What is the purpose and focus of this new project?"

Options:
1. Financial Services (default - trading, banking, insurance, collection management)
2. Software/SaaS (B2B/B2C software service, multi-tenant applications)
3. Healthcare (EMR, telemedicine, medical devices, patient management)
4. E-commerce (retail, marketplace, subscription services)
5. IoT (devices, sensors, industrial systems)
6. Other/Generic (internal tools, utilities, custom domain)
```

### Default Behavior
If user does not specify or says "default", use **Financial Services** configuration.

### Domain Config Mapping
| User Selection | Config File |
|----------------|-------------|
| Financial Services | `FINANCIAL_DOMAIN_CONFIG.md` |
| Software/SaaS | `SOFTWARE_DOMAIN_CONFIG.md` |
| Healthcare | Use `DOMAIN_ADAPTATION_GUIDE.md` (Healthcare section) |
| E-commerce | Use `DOMAIN_ADAPTATION_GUIDE.md` (E-commerce section) |
| IoT | Use `DOMAIN_ADAPTATION_GUIDE.md` (IoT section) |
| Other/Generic | `GENERIC_DOMAIN_CONFIG.md` |

### AI Action
1. Ask domain question
2. Record user response
3. Load corresponding domain configuration file
4. Proceed to Rule 2

---

## Rule 2: Folder Structure Creation (SECOND STEP)

### Critical Rule
**AI Assistant MUST create complete directory structure BEFORE creating any documents.**

### Why This Matters
- Prevents "file not found" errors
- Ensures index files can be initialized
- Enables proper document organization from start
- Validates project structure before content generation

### Execution Command

```bash
# Core 16-layer architecture (13 documentation artifacts + 3 execution layers)
mkdir -p docs/BRD
mkdir -p docs/PRD
mkdir -p docs/EARS
mkdir -p docs/BDD
mkdir -p docs/ADR
mkdir -p docs/SYS
mkdir -p docs/REQ
mkdir -p docs/IMPL
mkdir -p docs/CTR
mkdir -p docs/SPEC
mkdir -p docs/TASKS
mkdir -p docs/IPLAN
mkdir -p docs/ICON   # Optional (Implementation Contracts)

# Requirements subdirectories (domain-agnostic structure)
mkdir -p docs/07_REQ/api
mkdir -p docs/07_REQ/auth
mkdir -p docs/07_REQ/data
mkdir -p docs/07_REQ/core
mkdir -p docs/07_REQ/integration
mkdir -p docs/07_REQ/monitoring
mkdir -p docs/07_REQ/reporting
mkdir -p docs/07_REQ/security
mkdir -p docs/07_REQ/ui

# Domain-specific subdirectories (add based on domain selection)
# For Financial Services:
mkdir -p docs/07_REQ/risk
mkdir -p docs/07_REQ/trading
mkdir -p docs/07_REQ/collection
mkdir -p docs/07_REQ/compliance

# For Healthcare:
mkdir -p docs/07_REQ/patient
mkdir -p docs/07_REQ/clinical
mkdir -p docs/07_REQ/ehr

# For E-commerce:
mkdir -p docs/07_REQ/catalog
mkdir -p docs/07_REQ/cart
mkdir -p docs/07_REQ/order
mkdir -p docs/07_REQ/payment

# For Software/SaaS:
mkdir -p docs/07_REQ/tenant
mkdir -p docs/07_REQ/subscription
mkdir -p docs/07_REQ/billing

# Support directories
mkdir -p scripts
mkdir -p work_plans

# Root documentation (created by VCS init; no action required)
```

### Domain-Specific Extensions

**Financial Services** (add these):
```bash
mkdir -p docs/07_REQ/risk
mkdir -p docs/07_REQ/trading
mkdir -p docs/07_REQ/collection
mkdir -p docs/07_REQ/compliance
mkdir -p docs/07_REQ/ml
```

**Software/SaaS** (add these):
```bash
mkdir -p docs/07_REQ/tenant
mkdir -p docs/07_REQ/subscription
mkdir -p docs/07_REQ/billing
mkdir -p docs/07_REQ/workspace
```

**Healthcare** (add these):
```bash
mkdir -p docs/07_REQ/patient
mkdir -p docs/07_REQ/clinical
mkdir -p docs/07_REQ/ehr
mkdir -p docs/07_REQ/hipaa
```

**E-commerce** (add these):
```bash
mkdir -p docs/07_REQ/catalog
mkdir -p docs/07_REQ/cart
mkdir -p docs/07_REQ/order
mkdir -p docs/07_REQ/payment
mkdir -p docs/07_REQ/inventory
```

**IoT** (add these):
```bash
mkdir -p docs/07_REQ/device
mkdir -p docs/07_REQ/telemetry
mkdir -p docs/07_REQ/firmware
mkdir -p docs/07_REQ/edge
```

### Validation

After folder creation, AI Assistant **MUST** verify:

```bash
# Verify directory structure
ls -la docs/

# Expected to include at least 12 directories:
# BRD, PRD, EARS, BDD, ADR, SYS, REQ, IMPL, CTR, SPEC, TASKS, IPLAN
# Optional: ICON (if using implementation contracts)

# Verify requirements subdirectories
ls -la docs/07_REQ/

# Expected output should include domain-specific subdirectories

# Verify support directories
ls -la scripts/ work_plans/

# Expected: scripts/ and work_plans/ directories exist
```

### Error Handling

If folder creation fails:
1. Check parent directory permissions
2. Verify disk space availability
3. Report specific error to user
4. **STOP** execution until resolved (do not proceed to document creation)

---

## Rule 3: Domain Configuration Application

### Execution
After folder creation, AI Assistant **MUST**:

1. **Read** selected domain configuration file
2. **Extract** placeholder mappings
3. **Store** terminology for document generation
4. **Apply** domain-specific templates

### Placeholder Replacement Strategy

Domain configuration files contain mappings like:

```yaml
# Example from FINANCIAL_DOMAIN_CONFIG.md
[RESOURCE_COLLECTION] → collection
[RESOURCE_ITEM] → Position
[RESOURCE_ACTION] → operation execution
[EXTERNAL_DATA_PROVIDER] → Market Data Feed
[CALCULATION_ENGINE] → Greeks Calculator
```

AI Assistant **MUST**:
- Replace placeholders when copying templates
- Use domain terminology in generated documents
- Apply regulatory requirements from domain config
- Include domain-specific examples

### Application Method

```bash
# For each template file copied:
sed -i 's/\[RESOURCE_COLLECTION\]/collection/g' docs/07_REQ/REQ-01_example.md
sed -i 's/\[RESOURCE_ITEM\]/Position/g' docs/07_REQ/REQ-01_example.md
# ... apply all domain mappings
```

Or use domain-aware template generation when creating documents.

---

## Rule 4: Template Copying and Initialization

### Copy Framework Templates

```bash
# Point to the framework checkout (adjust for your environment)
FRAMEWORK_ROOT=/path/to/ai_dev_flow

# Copy templates by artifact type (portable example uses docs/)
cp -r "$FRAMEWORK_ROOT/BRD"/*   docs/01_BRD/
cp -r "$FRAMEWORK_ROOT/PRD"/*   docs/02_PRD/
cp -r "$FRAMEWORK_ROOT/EARS"/*  docs/03_EARS/
cp -r "$FRAMEWORK_ROOT/BDD"/*   docs/04_BDD/
cp -r "$FRAMEWORK_ROOT/ADR"/*   docs/05_ADR/
cp -r "$FRAMEWORK_ROOT/SYS"/*   docs/06_SYS/
cp -r "$FRAMEWORK_ROOT/REQ"/*   docs/07_REQ/
cp -r "$FRAMEWORK_ROOT/IMPL"/*  docs/08_IMPL/
cp -r "$FRAMEWORK_ROOT/CTR"/*   docs/09_CTR/
cp -r "$FRAMEWORK_ROOT/SPEC"/*  docs/10_SPEC/
cp -r "$FRAMEWORK_ROOT/TASKS"/* docs/11_TASKS/
cp -r "$FRAMEWORK_ROOT/ICON"/*  docs/ICON/ 2>/dev/null || true  # optional

# Copy validation scripts
mkdir -p scripts
cp "$FRAMEWORK_ROOT/scripts"/*.py scripts/
```

### Initialize Index Files

AI Assistant **MUST** create index files for each document type:

```bash
# Create index files
touch docs/01_BRD/BRD-00_index.md
touch docs/02_PRD/PRD-00_index.md
touch docs/03_EARS/EARS-00_index.md
touch docs/04_BDD/BDD-00_index.md
touch docs/05_ADR/ADR-00_index.md
touch docs/06_SYS/SYS-00_index.md
touch docs/07_REQ/REQ-00_index.md
touch docs/08_IMPL/IMPL-00_index.md
touch docs/09_CTR/CTR-00_index.md
touch docs/10_SPEC/SPEC-00_index.md
touch docs/11_TASKS/TASKS-00_index.md
touch docs/12_IPLAN/IPLAN-00_index.md
touch docs/ICON/ICON-00_index.md  # optional
```

### Index File Content Template

```markdown
# {TYPE} Index

**Purpose**: Master index of all {TYPE} documents in this project
**Status**: Active
**Last Updated**: {TIMESTAMP}

---

## Document Registry

| ID | Title | Status | Priority | Created | Last Modified |
|----|-------|--------|----------|---------|---------------|
| {TYPE}-01 | [First Document Title](../path/to/doc.md) | Draft | High | YYYY-MM-DD | YYYY-MM-DD |

---

## Next Available ID

**Next ID**: {TYPE}-01

**ID Assignment Rules**:
- Sequential numbering (01-99, then 100+)
- Never reuse IDs
- Stable once assigned
- Update this section when creating new documents

---

## Statistics

- **Total Documents**: 0
- **Draft**: 0
- **In Review**: 0
- **Approved**: 0
- **Deprecated**: 0
```

---

## Rule 5: Contract Decision Questionnaire

### Execution Trigger
After domain configuration and folder setup, AI Assistant **MUST** run contract decision questionnaire.

### Questionnaire File
Refer to `CONTRACT_DECISION_QUESTIONNAIRE.md` for complete questionnaire.

### Quick Decision Logic

AI Assistant asks:

```
"Does this project require API contracts or interface definitions?"

1. Yes - External APIs (REST/GraphQL)
2. Yes - Event schemas (pub/sub, message queues)
3. Yes - Data contracts (database schemas, data models shared between services)
4. No - Internal logic only
5. Unsure - Need guidance
```

### Decision Outcome

| Answer | Action |
|--------|--------|
| 1, 2, 3 (Yes) | Include CTR (contracts) layer in workflow |
| 4 (No) | Skip CTR layer, go directly IMPL → SPEC |
| 5 (Unsure) | Run full CONTRACT_DECISION_QUESTIONNAIRE.md |

### Workflow Adjustment

**With Contracts**:
```
REQ → IMPL → CTR → SPEC → TASKS → Code
```

**Without Contracts**:
```
REQ → IMPL → SPEC → TASKS → Code
```

---

## Rule 6: Document ID Management

### Scope: Documentation Artifacts Only

**CRITICAL**: ID naming standards apply ONLY to **documentation artifacts** in the SDD workflow. Source code files follow language-specific conventions.

#### ✅ Apply ID Standards To:
- Documentation in `docs/` directories: BRD, PRD, REQ, ADR, SPEC, CTR, IMPL, TASKS, EARS, SYS
- BDD feature files (`.feature`) in `tests/bdd/` or similar directories

#### ❌ Do NOT Apply ID Standards To:
- **Python source code** (`src/`, `[project_module]/`): Follow PEP 8 conventions
  - Modules: `snake_case.py`
  - Classes: `PascalCase`
  - Functions: `snake_case()`
- **Python test files** (`tests/`): Follow pytest conventions
  - Test modules: `test_*.py`
  - Test functions: `test_*()`
- **Other languages**: Follow language-specific style guides

### ID Naming Standards for Documentation

AI Assistant **MUST** follow these rules when creating **documentation** files:

#### Format
```
{TYPE}-{NN}_{descriptive_slug}.{ext}
```

or for sub-documents:
```
{TYPE}-{NN}-{YY}_{descriptive_slug}.{ext}
```

#### Components
- **{TYPE}**: Document type (BRD, PRD, REQ, ADR, CTR, SPEC, TASKS, etc.)
- **{NN}**: Sequential number (01-99, then 100+)
- **{YY}**: Sub-document number (01-99, then 100+) - optional
- **{descriptive_slug}**: Lowercase, underscores, describes content
- **{ext}**: File extension (.md, .yaml, .feature)

#### Examples
```
REQ-01_resource_limit_enforcement.md
ADR-005_database_selection.md
CTR-012_data_service_api.md
CTR-012_data_service_api.yaml  (dual-file contract)
SPEC-023_risk_calculator.yaml
TASKS-023_implement_risk_calculator.md
REQ-042.1_authentication_methods.md  (section file)
```

### ID Assignment Process

1. **Check index file** for next available ID
2. **Assign sequential ID** (never skip, never reuse)
3. **Create document** with proper naming
4. **Update index file** with new entry
5. **Mark ID as used** in index

### Dual-File Contracts

For CTR documents, AI Assistant **MUST** create both files:

```bash
# Create both markdown and YAML with matching slugs
touch docs/09_CTR/CTR-012_data_service_api.md
touch docs/09_CTR/CTR-012_data_service_api.yaml
```

**Matching slug requirement**: `data_service_api` must be identical in both filenames.

---

## Rule 7: Traceability Link Format

### Markdown Link Standard

AI Assistant **MUST** use this format for all document references:

```markdown
[{TYPE}-{ID}](../path/to/document.md#{TYPE}-{ID})
```

#### Examples
```markdown
# Nested folder structure (ALL TYPES - DEFAULT)
[BRD-01](../01_BRD/BRD-01/BRD-01.0_index.md#BRD-01)
[PRD-02](../02_PRD/PRD-02/PRD-02.0_index.md#PRD-02)
[ADR-005](../05_ADR/ADR-005/ADR-005.0_index.md#ADR-005)

# Flat structure (REQ, SPEC, CTR, etc.)
[REQ-03](../07_REQ/risk/REQ-03_resource_limit.md#REQ-03)
[CTR-012](../09_CTR/CTR-012_data_service_api.md#CTR-012)
[SPEC-023](../10_SPEC/SPEC-023_risk_calculator/SPEC-023_risk_calculator.yaml)
```

### Section 7: Traceability

Every document **MUST** include section 7 with:

1. **Upstream Sources** - Documents driving this artifact
2. **Downstream Artifacts** - Documents/code derived from this
3. **Primary Anchor/ID** - Main identifier for this document
4. **Code Paths** - Implementation locations (if applicable)

### Example section 7

```markdown
## 7. Traceability

### Upstream Sources
| Source | Type | Reference |
|--------|------|-----------|
| `@brd: BRD.01.01.01` | Business Requirements | Risk management objectives |
| `@prd: PRD.02.01.01` | Product Requirements | resource limit feature |
| `@adr: ADR-008` | Architecture Decision | Real-time limit enforcement |

### Downstream Artifacts
| Artifact | Type | Reference |
|----------|------|-----------|
| `@spec: SPEC-023` | Technical Specification | Implementation spec |
| `@tasks: TASKS.23.29.01` | Implementation Tasks | AI generation tasks |
| `@bdd: BDD.15.13.01` | BDD Scenarios | Acceptance tests |

### Primary Anchor/ID
- **REQ-03**: resource limit enforcement requirement

### Code Paths
- `src/risk/resource_limiter.py::PositionLimiter.enforce_limit()`
- `tests/risk/test_resource_limits.py::test_hard_limit_enforcement()`
```

---

## Rule 7.5: Mandatory Traceability Matrix Management

### Policy

**CRITICAL**: Traceability matrices are NOT optional. They are mandatory quality infrastructure for SDD workflow compliance.

### Enforcement

When creating ANY artifact document type:
- BRD, PRD, EARS, BDD, ADR, SYS, REQ, IMPL, CTR, SPEC, TASKS

You MUST:
1. Create or update the corresponding `[TYPE]-00_TRACEABILITY_MATRIX.md`
2. Add the new document to section 2 (Complete Inventory)
3. Document upstream sources in section 3
4. Document downstream artifacts in section 4 (even if "To Be Created")
5. Update status and completion percentage
6. Commit matrix in SAME commit as artifact

**No Exceptions**: This requirement has zero tolerance for non-compliance.

### Template Locations

All artifact types have traceability matrix templates:
```
ai_dev_flow/[TYPE]/[TYPE]-00_TRACEABILITY_MATRIX-TEMPLATE.md
```

### Validation Requirements

**Pre-Commit Checks**:
- [ ] Traceability matrix file exists for artifact type
- [ ] New document appears in matrix inventory (section 2)
- [ ] Upstream sources documented (section 3)
- [ ] Downstream artifacts documented (section 4)
- [ ] All references resolve correctly
- [ ] No orphaned artifacts (documents missing from matrix)

**Automated Validation**:
```bash
# Run validation script
python scripts/validate_traceability_matrix.py --type [TYPE] --strict

# Check coverage
python scripts/check_traceability_coverage.py --all
```

### Why This Is Critical

**Impact Analysis**: Determine what breaks when upstream requirements change
**Regulatory Compliance**: regulatory, FDA, ISO audits require complete traceability
**Quality Assurance**: Prevent orphaned requirements and missing implementations
**Change Management**: Understand ripple effects across entire workflow
**Automated Validation**: Enable pre-commit hooks and CI/CD quality gates

### Failure Modes If Matrix Missing

**Consequences**:
- ❌ Cannot determine impact of requirement changes
- ❌ Orphaned requirements (no implementation)
- ❌ Failed regulatory audits (incomplete audit trail)
- ❌ Manual validation required (expensive, error-prone)
- ❌ Pull requests rejected by automated checks
- ❌ Project delays due to quality gate failures

### Success Criteria

✅ 100% of artifacts tracked in matrices
✅ Zero orphaned documents
✅ All upstream/downstream links resolve
✅ Automated validation passes
✅ Audit-ready traceability at all times

---

## Rule 8: Tool-Specific Optimization

### Claude Code
- **Context**: 200K tokens (~600KB conversation)
- **File limit**: 50K tokens standard (200KB), 100K maximum (400KB)
- **Strategy**: Single comprehensive files, no artificial splitting
- **Read command**: Use `Read` tool for all file operations
- **Parallel operations**: Use multiple tool calls in single message

### Gemini CLI
- **Context**: 1M tokens (conversation total)
- **@ reference limit**: 10K tokens (40KB) max
- **Large file strategy**: Use file read tool, not `@` reference
- **Command**: `gemini read LARGE_FILE.md` instead of `@LARGE_FILE.md`
- **Workaround**: "Read and analyze LARGE_FILE.md..." in natural language

### GitHub Copilot
- **Optimal**: 10-30KB per file
- **Large file strategy**: Create companion summary files
- **Working set**: Maximum 10 files in Copilot Edits mode
- **Inline**: Best for small code snippets and completions

### Cursor / Windsurf
- **Context**: Similar to Claude Code
- **Strategy**: Leverage full context window for comprehensive docs
- **Parallel operations**: Supported

---

## Rule 9: Validation Commands

### AI Assistant MUST Run After Setup

```bash
# Validate directory structure
ls -laR docs/

# Verify index files exist
ls docs/*/index.*

# Check for broken references (after documents created)
python scripts/validate_links.py

# Validate requirement IDs (after documents created)
python scripts/validate_requirement_ids.py

# Generate traceability matrix (after documents created)
python scripts/generate_traceability_matrix.py --type REQ --input docs/07_REQ/ --output docs/TRACEABILITY_MATRIX_REQ.md
```

### Continuous Validation

AI Assistant should run validation:
- After creating each document
- Before marking task as complete
- When user requests validation
- Before generating code from SPEC

---

## Rule 10: Error Handling

### Common Errors and Resolutions

| Error | Cause | Resolution |
|-------|-------|------------|
| "Directory not found" | Skipped Rule 2 (folder creation) | Run folder creation commands |
| "File not found" | Incorrect relative path | Verify path from document location |
| "Broken reference" | Document doesn't exist or wrong ID | Check index file for correct ID |
| "Duplicate ID" | Reused ID from index | Assign next sequential ID |
| "Missing section 7" | Incomplete template | Add traceability section |
| "Slug mismatch" | CTR .md and .yaml different slugs | Rename to match |

### Error Reporting

AI Assistant **MUST**:
1. Report specific error message
2. Identify which rule was violated
3. Provide exact resolution steps
4. Re-run validation after fix
5. Confirm resolution before proceeding

---

## Rule 11: Document Creation Workflow

### Standard Document Creation Process

For each document, AI Assistant **MUST**:

1. **Check index** for next available ID
2. **Verify folder exists** (Rule 2 validation)
3. **Load template** for document type
4. **Apply domain config** (placeholder replacement)
5. **Fill all sections** (no empty placeholders)
6. **Add section 7** (traceability with upstream/downstream)
7. **Add anchor** at top: `<a id="{TYPE}-{ID}"></a>`
8. **Save file** with correct naming
9. **Update index file** with new entry
10. **Validate links** (run validation script)

### Template section Requirements

AI Assistant **MUST** complete these sections in every document:

- **Document Control Table**: Status, version, priority, dates
- **Context/Purpose**: Why this document exists
- **Main Content**: Domain-specific requirements/specifications
- **Acceptance Criteria**: Measurable, testable conditions (for REQ)
- **Dependencies**: Prerequisites and constraints
- **Risks**: Potential issues and mitigations
- **section 7: Traceability**: Complete upstream/downstream tables
- **Change History**: Version tracking

---

## Rule 12: Multi-Document Workflows

### When Creating Related Documents

AI Assistant **MUST** maintain bidirectional links:

1. **Create parent document first** (e.g., REQ)
2. **Add placeholder downstream links** (SPEC, TASKS to be created)
3. **Create child documents** (SPEC, TASKS)
4. **Add upstream links in children** (pointing back to REQ)
5. **Update parent downstream section** (replace placeholders with actual links)
6. **Validate bidirectional links** (run validation script)

### Example Workflow

```
Step 1: Create REQ-023_risk_calculator.md
  - Downstream section: "SPEC-023 (to be created)"

Step 2: Create SPEC-023_risk_calculator.yaml
  - Upstream section: [REQ-023](../07_REQ/risk/REQ-023_risk_calculator.md#REQ-023)

Step 3: Update REQ-023
  - Downstream section: [SPEC-023](../10_SPEC/SPEC-023_risk_calculator/SPEC-023_risk_calculator.yaml)

Step 4: Create TASKS-023_implement_risk_calculator.md
  - Upstream section: [SPEC-023](../10_SPEC/SPEC-023_risk_calculator/SPEC-023_risk_calculator.yaml)

Step 5: Update SPEC-023 and REQ-023
  - Add TASKS-023 to downstream sections

Step 6: Validate
  - Run validate_links.py
```

---

## Rule 13: Token Optimization

### Document Size Targets

AI Assistant **SHOULD** target these sizes:

| Document Type | Target Size | Max Size | Rationale |
|--------------|-------------|----------|-----------|
| BRD | 5-15KB | 50KB | Strategic overview |
| PRD | 10-30KB | 50KB | Feature descriptions |
| EARS | 5-10KB | 30KB | Measurable requirements only |
| BDD | 5-20KB | 50KB | Test scenarios |
| ADR | 3-8KB | 20KB | Decision record (one decision) |
| SYS | 10-25KB | 50KB | System specifications |
| REQ | 2-5KB | 10KB | **One atomic requirement per file** |
| IMPL | 10-30KB | 50KB | Project plan |
| CTR (.md) | 10-25KB | 50KB | Contract context |
| CTR (.yaml) | 5-15KB | 30KB | OpenAPI/AsyncAPI schema |
| SPEC | 15-40KB | 100KB | Complete technical spec |
| TASKS | 5-15KB | 30KB | Implementation steps |

### When to Split Documents

AI Assistant **MUST** split documents when:

1. **Single file exceeds 100KB (100K tokens)** - Hard limit
2. **REQ contains multiple concepts** - Split into one REQ per concept
3. **SPEC covers multiple independent modules** - Create one SPEC per module
4. **ADR documents multiple decisions** - Create one ADR per decision

### Splitting Strategy

Use sub-document numbering:

```
Original: REQ-042_authentication.md (too large, multiple concepts)

Split into:
REQ-042.1_authentication_methods.md
REQ-042.2_password_policies.md
REQ-042.3_mfa_requirements.md
REQ-042.4_session_management.md
```

---

## Rule 14: Code Generation from SPEC

### Pre-Generation Validation

Before generating code from SPEC, AI Assistant **MUST**:

1. **Verify SPEC completeness**:
   - All classes defined
   - All methods with signatures
   - All parameters with types
   - Return types specified
   - Error handling documented
   - Pre/post conditions clear

2. **Verify upstream traceability**:
   - REQ references present
   - ADR references present (if applicable)
   - BDD scenario references present
   - CTR references present (if interfaces)

3. **Verify downstream planning**:
   - TASKS document exists
   - Implementation steps clear
   - Test cases identified

### Code Generation Rules

AI Assistant **MUST** inject traceability comments:

```python
# TRACEABILITY: REQ-023, ADR-008, BDD-015
# SPEC: SPEC-023_risk_calculator.yaml
# PURPOSE: Enforce resource limits per REQ-023 acceptance criteria
class PositionLimiter:
    """
    resource limit enforcement per [REQ-023](../docs/07_REQ/risk/REQ-023_resource_limit.md).

    Architecture: [ADR-008](../docs/05_ADR/ADR-008_realtime_enforcement/ADR-008.0_realtime_enforcement_index.md) - Real-time enforcement
    Acceptance Tests: [BDD-015](../docs/04_BDD/BDD-015_resource_limits/BDD-015.1_resource_limits.feature)
    """

    def enforce_limit(self, position: Position) -> EnforcementResult:
        """
        REQ-023-AC1: Hard limit prevents position increases beyond threshold.
        REQ-023-AC2: Soft limit warns but allows within tolerance.
        """
        # Implementation per SPEC-023
        pass
```

### Test Generation Rules

AI Assistant **MUST** generate tests matching BDD scenarios:

```python
# TRACEABILITY: BDD-015, REQ-023
# TEST: resource limit enforcement per acceptance criteria
def test_hard_limit_enforcement():
    """
    BDD: BDD-015 Scenario "Hard limit prevents position increase"
    REQ: REQ-023-AC1 - Hard limit enforcement
    """
    # Given position at hard limit
    limiter = PositionLimiter(hard_limit=1000)
    position = Position(size=1000)

    # When attempting to increase
    result = limiter.enforce_limit(position.increase(100))

    # Then increase rejected
    assert result.allowed == False
    assert result.reason == "Hard limit exceeded"
```

---

## Rule 15: Framework Updates and Maintenance

### When to Update Framework

AI Assistant should suggest framework updates when:

1. **New domain emerges** - Create new domain config file
2. **Template improvements identified** - Update template files
3. **Validation script enhancements** - Update Python scripts
4. **ID naming conflicts** - Refine ID standards
5. **Tool optimization discovered** - Update tool-specific guidance

### Update Process

1. **Document issue** in framework repository
2. **Propose solution** with examples
3. **Update relevant files** (templates, configs, rules)
4. **Test with sample project**
5. **Update version numbers**
6. **Regenerate documentation**

---

## Rule 16: TASKS Implementation Workflow

### Development Plan Tracking (CRITICAL)

**Before ANY TASKS Implementation**: The Development Plan (`docs/DEVELOPMENT_PLAN.md`) is the **central command center** for organizing and tracking all TASKS across implementation phases.

**Mandatory Setup**:
1. Copy `TASKS/DEVELOPMENT_PLAN_TEMPLATE.md` to `docs/DEVELOPMENT_PLAN.md` at project start
2. Populate with all TASKS organized by phase and priority
3. Use YAML-based structure for machine-parsable tracking

**See**: `TASKS/DEVELOPMENT_PLAN_README.md` for complete documentation.

### Mandatory Workflow Rules

AI Assistant **MUST** enforce these rules for EVERY TASKS:

**Rule 3: Pre-Execution Verification** (BEFORE starting)
- Update `pre_check` status and checklist in Development Plan YAML
- Verify against REQ-NN and TASKS-NN
- Confirm architecture decisions
- Check for missing logic/fields
- Review upstream artifact consistency
- Confirm all dependencies available
- **Block implementation until all checklist items complete**

**Rule 2: Phase Tracker Update** (AFTER completing)
- Update TASKS status: `IN_PROGRESS` → `COMPLETED` in YAML
- Update IPLAN status to `COMPLETED` if applicable
- Mark `post_check` checklist items as complete
- **Required BEFORE moving to next TASKS**

**Rule 1: Session Log Update** (AFTER completing)
- Add entry to Development Plan Section 3 (Session Log)
- Include: date, TASKS ID, COMPLETED status, implementation summary
- Mark session log checklist items in YAML as complete
- **Required for audit trail and continuity**

### Execution Steps

1. **Verify Pre-Conditions**: Check Development Plan that TASKS is next in queue and `pre_check` complete
2. **Create IPLAN**: Generate `IPLAN-XX` breaking down TASKS into Phases (Domain, Logic, Service, Test)
3. **Update Task Artifact**: Maintain `task.md` with granular progress
4. **Execute & Verify**: TDD loop with `pytest`
5. **Update Development Plan**: 
   - Mark TASKS status as `COMPLETED` in YAML
   - Mark IPLAN status as `COMPLETED` in YAML
   - Complete `post_check` checklist in YAML
   - Add Session Log entry
6. **Document**: Update `walkthrough.md` with implementation summary

### Development Plan Structure

The Development Plan uses YAML blocks for each phase:

```yaml
phase_N_tasks:
  - id: TASKS-XX
    service_name: "[Service Name]"
    priority: P0
    workflow:
      pre_check:        # Rule 3: Verification before start
        status: COMPLETED
        checklist: [6 items: all must be true]
      tasks:            # Main implementation tracking
        status: COMPLETED
        iplan_id: IPLAN-XX
        iplan_status: COMPLETED
      post_check:       # Rules 1 & 2: Updates after completion
        status: COMPLETED
        checklist: [7 items: all must be true]
```

### Quality Gates

**Block IF**:
- `pre_check.status != COMPLETED` → Cannot start implementation
- `tasks.status == COMPLETED` AND `post_check.status != COMPLETED` → Cannot move to next TASKS
- Session Log missing entry for completed TASKS → Audit trail incomplete

---

## Rule 17: Change Management Protocol

### Trigger
When executing a major architectural pivot or technology switch (e.g., changing databases, replacing a framework), AI Assistant **MUST** follow the `CHANGE_MANAGEMENT_GUIDE.md`.

### Execution
1.  **Plan**: Create a dedicated `implementation_plan.md` section for the migration.
2.  **Archive**: Move obsolete artifacts to `docs/archive/vX_<reason>/`. **NEVER DELETE** significant planning documents.
3.  **Supersede**: Explicitly state in new documents which artifacts they replace.
4.  **Revalidate**: Perform structural validation on the new set of documents.

---

## Summary: Execution Checklist

AI Assistant **MUST** complete this checklist for every new project:

- [ ] **Step 1**: Ask domain selection question
- [ ] **Step 2**: Create complete folder structure (all 11+ directories)
- [ ] **Step 3**: Load domain configuration file
- [ ] **Step 4**: Copy templates with domain placeholder replacement
- [ ] **Step 5**: Run contract decision questionnaire
- [ ] **Step 6**: Initialize all index files ({TYPE}-00_index.{ext})
- [ ] **Step 7**: Validate folder structure (ls -laR docs/)
- [ ] **Step 8**: Begin document creation following kickoff tasks
- [ ] **Step 9**: Maintain traceability (section 7 in all documents)
- [ ] **Step 10**: Run validation scripts after each document
- [ ] **Step 11**: Generate code with traceability comments
- [ ] **Step 12**: Create tests matching BDD scenarios
- [ ] **Step 13**: Generate traceability matrices
- [ ] **Step 14**: Final validation before marking project setup complete
- [ ] **Step 15**: Implement TASKS using Phase-based workflow (IPLAN -> Code -> Verify)

---

## Tool Integration Examples

### Claude Code Example

```markdown
User: "Initialize new financial services trading platform project"

Claude Code:
1. Domain Selection: "Financial Services (default) detected. Loading FINANCIAL_DOMAIN_CONFIG.md"
2. Folder Creation: "Creating 16-layer architecture (13 artifact directories) + finance subdirectories..."
   [Runs mkdir commands]
3. Validation: "Verifying structure... ✓ All directories created"
4. Template Setup: "Copying templates and applying financial domain placeholders..."
5. Contract Decision: "Running contract questionnaire..."
   User response: "Yes - REST API for market data"
   Action: "Including CTR layer in workflow"
6. Index Initialization: "Creating index files for all document types... ✓ Complete"
7. Ready: "Project initialized. Ready to create BRD-01. Next: Define business objectives."
```

### Gemini CLI Example

```markdown
User: "Set up new SaaS project for multi-tenant collaboration platform"

Gemini CLI:
1. Domain: "Detected Software/SaaS domain. Loading SOFTWARE_DOMAIN_CONFIG.md"
2. Folders: "Creating structure..."
   [Executes mkdir -p commands]
3. Config: "Applying SaaS terminology: Tenant, Workspace, Subscription..."
4. Contracts: "Questionnaire: Does this require APIs?"
   User: "Yes - GraphQL API for workspace management"
   Action: "Including CTR layer"
5. Templates: "Initializing with SaaS examples..."
6. Status: "✓ Project ready. Starting with BRD-01..."
```

---

## Rule 10: Metadata Tagging for Dual-Architecture Projects

### Purpose

When projects support multiple architectural approaches (e.g., AI Agent-Based vs Traditional implementations), use YAML frontmatter metadata to:
- Indicate architectural priority (primary/recommended vs fallback/reference)
- Enable visual hierarchy in documentation sites
- Provide bidirectional cross-references between equivalent implementations
- Support filtering and querying by architecture approach

### When to Apply Metadata Tagging

**Use metadata tagging when:**
- ✅ Project supports dual/multiple architectural approaches
- ✅ Need to indicate recommendation between approaches
- ✅ Building documentation sites (Docusaurus, MkDocs)
- ✅ Require cross-referencing between equivalent implementations

**Do NOT use when:**
- ❌ Project has single architecture only
- ❌ All documents apply equally to all approaches

### Quick Reference Templates

**Primary (Recommended) Implementation:**
```yaml
---
title: "BRD-XXX: Feature Name"
tags:
  - feature-brd
  - ai-agent-primary
  - recommended-approach
custom_fields:
  architecture_approach: ai-agent-based
  priority: primary
  development_status: active
  agent_id: AGENT-XXX
  fallback_reference: BRD-YYY
---
```

**Fallback (Reference) Implementation:**
```yaml
---
title: "BRD-XXX: Feature Name"
tags:
  - feature-brd
  - traditional-fallback
  - reference-implementation
custom_fields:
  architecture_approach: traditional-8layer
  priority: fallback
  development_status: reference
  primary_alternative: BRD-YYY_name
---
```

**Shared Platform Requirements:**
```yaml
---
title: "BRD-XXX: Platform Feature"
tags:
  - platform-brd
  - shared-architecture
  - required-both-approaches
custom_fields:
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  implementation_differs: false
  primary_implementation: ai-agent-based
---
```

### Custom Admonitions

Add visual indicators for primary/fallback documents:

**Recommended Approach:**
```markdown
:::recommended Primary Implementation (AI Agent-Based)
**Architecture**: AI Agent-Based Platform (@adr: ADR-02)
**Priority**: ✅ Recommended approach
**Status**: Active development

**Fallback Alternative**: [@brd: BRD-YYY](./BRD-YYY_name.md)
:::
```

**Fallback Approach:**
```markdown
:::fallback Fallback Implementation (Traditional)
**Architecture**: Traditional Platform (@adr: ADR-01)
**Priority**: ⚠️ Fallback option (use only if primary not viable)
**Status**: Reference implementation

**Recommended Alternative**: [@brd: BRD-XXX](./BRD-XXX_name.md)
:::
```

### AI Assistant Actions

When creating documents for dual-architecture projects:

1. **Identify Document Type**: Determine if primary, fallback, or shared
2. **Apply Metadata Template**: Use appropriate template from above
3. **Add Custom Admonition**: For key documents (e.g., BRD-22, BRD-16)
4. **Create Bidirectional References**: Link primary ↔ fallback
5. **Validate**: Ensure YAML syntax correct, references exist

### Complete Reference

See [METADATA_TAGGING_GUIDE.md](./METADATA_TAGGING_GUIDE.md) for:
- Complete metadata structure standards
- Tag taxonomy
- Validation scripts
- Documentation site integration
- Migration guide
- Troubleshooting

---

## Rule 16: Cross-Document Consistency Validation (MANDATORY)

### Purpose

Ensure all documents maintain semantic consistency with their upstream sources through automated validation and auto-fix after every document creation or modification.

### Trigger

**Execute IMMEDIATELY after ANY document creation or modification** - no exceptions.

### Mandatory Actions

1. **Run cross-document validation**:
   ```bash
   python scripts/validate_cross_document.py --document {created_doc} --auto-fix
   ```

2. **Verify tag references**: All @tags must reference existing documents with valid requirement IDs

3. **Verify cumulative tag chain**: Tag count must match layer requirements per TRACEABILITY.md

4. **Auto-fix all issues**: ERROR and WARNING level issues fixed without user confirmation

5. **Re-validate until clean**: Loop until 0 errors and 0 warnings

6. **Mark as complete**: Only after validation passes

### Validation Loop

```
LOOP:
  1. Run: python scripts/validate_cross_document.py --document {doc} --auto-fix
  2. IF errors fixed: GOTO LOOP (re-validate)
  3. IF warnings fixed: GOTO LOOP (re-validate)
  4. IF unfixable issues: Log for manual review, continue
  5. IF clean: Mark VALIDATED, update traceability matrix
```

### Zero Tolerance Policy

**DO NOT proceed to next document until validation passes.** This is a blocking quality gate.

### Validation Codes

| Code | Description | Severity | Auto-Fix Action |
|------|-------------|----------|-----------------|
| XDOC-001 | Referenced requirement ID not found in upstream | ERROR | Remove reference + dependent content |
| XDOC-002 | Missing cumulative tag for layer | ERROR | Add tag with valid upstream ref |
| XDOC-003 | Upstream document file not found | ERROR | **REMOVE functionality requiring it** |
| XDOC-004 | Title mismatch with upstream | WARNING | Update title to match upstream |
| XDOC-005 | Referencing deprecated requirement | WARNING | Remove or suggest replacement |
| XDOC-006 | Tag format invalid | ERROR | Correct to TYPE.NN.TT.SS or TYPE-NN format |
| XDOC-007 | Gap in cumulative tag chain | ERROR | Add missing tags from chain |
| XDOC-008 | Broken internal link/anchor | ERROR | Fix path or remove link |
| XDOC-009 | Missing traceability section | ERROR | Add template section |
| XDOC-010 | Orphan requirement (no downstream) | WARNING | Annotate for review |

---

## Rule 17: Auto-Fix Policy

### Purpose

Define which issues are auto-fixed without user confirmation and which require manual review.

### Command Line Options

| Option | Description |
|--------|-------------|
| `--auto-fix` | Enable automatic fixing of issues |
| `--dry-run` | Preview changes without applying them |
| `--force-xdoc` | Skip confirmation for XDOC-003 tag removals |
| `--no-backup` | Do not create backup files before auto-fix |

### Auto-Fix WITHOUT Confirmation

The following issues are fixed automatically without prompting:

| Issue Code | Fix Action | Example |
|------------|------------|---------|
| XDOC-002 | Add missing cumulative tag | Add `@prd: PRD-01` for EARS layer |
| XDOC-005 | Replace deprecated reference | `@adr: ADR-03` → `@adr: null <!-- deprecated -->` |
| XDOC-006 | Correct tag format | `@brd: brd001` → `@brd: BRD-01` |
| XDOC-008 | Fix broken internal link | Recalculate correct path |
| XDOC-009 | Insert traceability section | Add Section 7 template |

### Requires Confirmation (XDOC-003)

**CRITICAL**: Reference to missing upstream document requires user confirmation:

```
WARNING: XDOC-003 - Removing reference to missing document: BRD-01
  File: REQ-001.md
  Tag:  @brd: BRD-01
Continue with removal? [y/N]:
```

**Bypass options:**
- `--force-xdoc`: Skip confirmation (use in CI/CD pipelines)
- `--dry-run`: Preview without prompting or applying changes

### Audit Trail

All XDOC-003 tag removals are logged to `tmp/validation_audit.json`:

```json
{
  "timestamp": "2025-12-29T14:30:00.000000",
  "file": "/path/to/document.md",
  "issue_code": "XDOC_003",
  "action": "removed_tag",
  "removed_content": "@brd: BRD-01",
  "backup_path": "/path/to/document.md.bak"
}
```

### Backup Strategy

Before ANY auto-fix (unless `--no-backup` specified):
1. Create `.bak` backup file: `{filename}.md.bak`
2. Apply fixes to original file
3. If validation passes: Delete backup
4. If errors remain: Keep backup for recovery

### Requires Manual Review (NOT Auto-Fixed)

| Issue Code | Reason | Action |
|------------|--------|--------|
| XDOC-001 | Missing required tag needs human input | Log: "Add required @tag reference" |
| XDOC-004 | Bidirectional mismatch needs review | Log: "Review bidirectional reference" |
| XDOC-007 | Optional tag is intentionally missing | Log: "Optional tag not present" |
| XDOC-010 | Duplicate may be intentional | Log: "Review duplicate references" |

### Strict Hierarchy Enforcement

**CRITICAL**: If upstream document is missing (XDOC-003), the fix action is:
1. **PROMPT** for user confirmation (unless `--force-xdoc`)
2. **REMOVE** the @tag reference to missing document
3. **LOG** removal to audit trail (`tmp/validation_audit.json`)
4. **DO NOT** create placeholder or phantom references

This enforces strict hierarchy - no orphan forward references allowed.

---

## Rule 18: Validation Phases

### Purpose

Define three validation phases that execute at different workflow stages.

### Phase 1: Per-Document Validation (Immediate)

**Trigger**: Immediately after creating or modifying any document

**Checks**:
- Format validation (YAML frontmatter, sections)
- Upstream reference existence (all @tags resolve)
- Cumulative tag completeness (layer requirements met)
- Internal link resolution (all paths valid)

**Command**:
```bash
python scripts/validate_cross_document.py --document {doc_path} --auto-fix
```

**Blocking**: YES - Cannot proceed until Phase 1 passes

### Phase 2: Per-Layer Validation (Layer Completion)

**Trigger**: When ALL documents of a layer type are created

**Checks**:
- Cross-document consistency within layer
- Orphan detection (documents with no downstream)
- Layer-wide coverage metrics
- Traceability matrix update

**Command**:
```bash
python scripts/validate_cross_document.py --layer {TYPE} --auto-fix
```

**Automatic Trigger Detection**:
- Track expected document count from project plan
- When count reached, automatically run Phase 2
- Block proceeding to next layer until Phase 2 passes

### Phase 3: Final Validation (Before Layer Transition)

**Trigger**: Before proceeding from one layer to the next in the workflow

**Checks**:
- Full traceability chain validation (all layers complete)
- Complete orphan detection across all documents
- Quality gate approval (all metrics ≥90%)
- Cumulative tag chain integrity

**Command**:
```bash
python scripts/validate_cross_document.py --all --auto-fix --strict
```

**Quality Gate Thresholds**:
- 100% upstream references resolved
- 0 broken links
- 0 missing cumulative tags
- 0 format errors
- ≤5% orphan requirements (warnings only)

### Phase Execution Summary

| Phase | Trigger | Scope | Blocking | Auto-Fix |
|-------|---------|-------|----------|----------|
| 1 | After each document | Single document | YES | YES |
| 2 | Layer completion | All docs in layer | YES | YES |
| 3 | Layer transition | All layers | YES | YES |

### Validation Report Output

After each validation phase, generate report:

```markdown
# Cross-Document Validation Report

**Document**: {doc_path}
**Timestamp**: {ISO timestamp}
**Phase**: {1|2|3}

## Fixes Applied

### ERRORS Fixed ({count})
| Code | Issue | Fix Applied |
|------|-------|-------------|

### WARNINGS Fixed ({count})
| Code | Issue | Fix Applied |
|------|-------|-------------|

## Remaining Issues ({count})
| Code | Severity | Issue | Action |
|------|----------|-------|--------|

## Summary
- Status: {PASSED|PASSED_WITH_WARNINGS|FAILED}
- Errors: {found} found, {fixed} fixed, {remaining} manual
- Warnings: {found} found, {fixed} fixed
```

---

## References

- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](./SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - Complete SDD methodology
- [DOMAIN_SELECTION_QUESTIONNAIRE.md](./DOMAIN_SELECTION_QUESTIONNAIRE.md) - Domain detection guide
- [CONTRACT_DECISION_QUESTIONNAIRE.md](./CONTRACT_DECISION_QUESTIONNAIRE.md) - Contract decision logic
- [FINANCIAL_DOMAIN_CONFIG.md](./FINANCIAL_DOMAIN_CONFIG.md) - Finance configuration
- [SOFTWARE_DOMAIN_CONFIG.md](./SOFTWARE_DOMAIN_CONFIG.md) - Software/SaaS configuration
- [GENERIC_DOMAIN_CONFIG.md](./GENERIC_DOMAIN_CONFIG.md) - Universal configuration
- [ID_NAMING_STANDARDS.md](./ID_NAMING_STANDARDS.md) - Document ID rules
- [TRACEABILITY.md](./TRACEABILITY.md) - Traceability guidelines
- [METADATA_TAGGING_GUIDE.md](./METADATA_TAGGING_GUIDE.md) - Dual-architecture metadata standards
- [AI_TOOL_OPTIMIZATION_GUIDE.md](./AI_TOOL_OPTIMIZATION_GUIDE.md) - AI tool selection

---

**End of AI Assistant Execution Rules**

---

## Product Appendix: AI‑Assisted Documentation Features (PRD Summary)

This appendix consolidates and supersedes the former `PRD-00_ai_assisted_documentation_features.md`. It specifies the product requirements that guide assistant behavior and UX for documentation generation within the AI Dev Flow.

### 1. Problem Statement

Current challenges in assisted documentation creation:
- Skill selection complexity (25+ skills; steep learning curve)
- Context loss across artifacts and sessions
- Quality inconsistency vs templates and validators
- Workflow friction choosing next steps across 16 layers

Business impact:
- Productivity loss (40–60% on skill/workflow overhead)
- Quality variance leading to traceability gaps
- Onboarding friction (2–4 weeks to proficiency)
- Rework (15–25% artifacts)

### 2. Goals

Primary (P0):
- G‑001: Automate skill recommendation (≥85% accuracy)
- G‑002: Intelligent context analysis (≥90% relevant context)
- G‑003: Proactive quality guidance (≥30% fewer validation failures)
- G‑004: Next‑step recommendations (≥50% less navigation time)

Secondary (P1):
- G‑005: Surface relevant existing artifacts (≥80% relevance)
- G‑006: Detect common anti‑patterns (≥70% detection)
- G‑007: Adaptive guidance by expertise level (≥4.0/5.0 satisfaction)

### 3. Non‑Goals
- Full automation of document creation (human review required)
- Replacement of existing doc‑* skills (augment, don’t replace)
- Cross‑project analysis (single project scope)
- Free‑form NL generation (prefer structured templates)
- Real‑time collaborative editing

### 4. User Needs

Personas and needs:
- Framework Beginner: clear guidance, auto skill selection, validation feedback
- Intermediate User: context awareness, workflow optimization, quality checks
- Power User: customization, batch operations, efficiency tools

Representative stories (abbrev.):
- Skill Recommendation: suggest 1–3 skills with confidence and rationale; override allowed
- Context Analysis: surface upstream artifacts and summarize context pre‑creation
- Quality Guidance: real‑time section completeness and anti‑pattern warnings
- Workflow Optimization: recommend downstream/parallel steps after completion

### 5. Product Features

- Skill Recommender: intent + project state → ranked skills with confidence/rationale
- Context Analyzer: scan structure/metadata/traceability → context model for sessions
- Quality Advisor: section completeness, anti‑patterns, cumulative tag checks, naming
- Workflow Optimizer: current position, downstream needs, parallel work, progress

### 6. KPIs

Performance: recommendation <500ms; context <2s/100 artifacts; quality check <100ms/section; workflow <300ms.

Adoption: feature adoption ≥80%; recommendation acceptance ≥70%; repeat usage ≥90%.

Quality: recommendation accuracy ≥85%; context relevance ≥90%; validation failures −30%; time‑to‑artifact −40%.

### 7. Architecture Topics → ADRs
- Context storage strategy (session vs persistent)
- Skill matching (rule‑based vs ML)
- Quality check integration (hooks vs inline)
- State management (file‑based vs in‑memory)

Traceability note: This appendix documents product intent within execution rules; formal ADRs/03_EARS/BDD remain separate artifacts at their respective layers.
