# AI Assistant Execution Rules

**Version**: 1.0
**Purpose**: Core rules for AI Coding Assistants executing AI Dev Flow framework
**Target Tools**: Claude AI, Claude Code, Gemini CLI, GitHub Copilot, Cursor, Windsurf
**Status**: Production

---

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
1. Financial Services (default - trading, banking, insurance, portfolio management)
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
# Core 10-layer directory structure
mkdir -p docs/brds
mkdir -p docs/prd
mkdir -p docs/ears
mkdir -p docs/bbds
mkdir -p docs/adrs
mkdir -p docs/sys
mkdir -p docs/reqs
mkdir -p docs/impl_plans
mkdir -p docs/contracts
mkdir -p docs/specs
mkdir -p docs/ai_tasks

# Requirements subdirectories (domain-agnostic structure)
mkdir -p docs/reqs/api
mkdir -p docs/reqs/auth
mkdir -p docs/reqs/data
mkdir -p docs/reqs/core
mkdir -p docs/reqs/integration
mkdir -p docs/reqs/monitoring
mkdir -p docs/reqs/reporting
mkdir -p docs/reqs/security
mkdir -p docs/reqs/ui

# Domain-specific subdirectories (add based on domain selection)
# For Financial Services:
mkdir -p docs/reqs/risk
mkdir -p docs/reqs/trading
mkdir -p docs/reqs/portfolio
mkdir -p docs/reqs/compliance

# For Healthcare:
mkdir -p docs/reqs/patient
mkdir -p docs/reqs/clinical
mkdir -p docs/reqs/ehr

# For E-commerce:
mkdir -p docs/reqs/catalog
mkdir -p docs/reqs/cart
mkdir -p docs/reqs/order
mkdir -p docs/reqs/payment

# For Software/SaaS:
mkdir -p docs/reqs/tenant
mkdir -p docs/reqs/subscription
mkdir -p docs/reqs/billing

# Scripts directory
mkdir -p scripts

# Root documentation
mkdir -p .
```

### Domain-Specific Extensions

**Financial Services** (add these):
```bash
mkdir -p docs/reqs/risk
mkdir -p docs/reqs/trading
mkdir -p docs/reqs/portfolio
mkdir -p docs/reqs/compliance
mkdir -p docs/reqs/ml
```

**Software/SaaS** (add these):
```bash
mkdir -p docs/reqs/tenant
mkdir -p docs/reqs/subscription
mkdir -p docs/reqs/billing
mkdir -p docs/reqs/workspace
```

**Healthcare** (add these):
```bash
mkdir -p docs/reqs/patient
mkdir -p docs/reqs/clinical
mkdir -p docs/reqs/ehr
mkdir -p docs/reqs/hipaa
```

**E-commerce** (add these):
```bash
mkdir -p docs/reqs/catalog
mkdir -p docs/reqs/cart
mkdir -p docs/reqs/order
mkdir -p docs/reqs/payment
mkdir -p docs/reqs/inventory
```

**IoT** (add these):
```bash
mkdir -p docs/reqs/device
mkdir -p docs/reqs/telemetry
mkdir -p docs/reqs/firmware
mkdir -p docs/reqs/edge
```

### Validation

After folder creation, AI Assistant **MUST** verify:

```bash
# Verify directory structure
ls -la docs/

# Expected output should include all 11 directories:
# brds, prd, ears, bbds, adrs, sys, reqs, impl_plans, contracts, specs, ai_tasks

# Verify requirements subdirectories
ls -la docs/reqs/

# Expected output should include domain-specific subdirectories
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
[RESOURCE_COLLECTION] → Portfolio
[RESOURCE_ITEM] → Position
[RESOURCE_ACTION] → Trade Execution
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
sed -i 's/\[RESOURCE_COLLECTION\]/Portfolio/g' docs/reqs/REQ-001_example.md
sed -i 's/\[RESOURCE_ITEM\]/Position/g' docs/reqs/REQ-001_example.md
# ... apply all domain mappings
```

Or use domain-aware template generation when creating documents.

---

## Rule 4: Template Copying and Initialization

### Copy Framework Templates

```bash
# Copy all templates from framework to project
cp /opt/data/docs_flow_framework/ai_dev_flow/docs_templates/brds/* docs/brds/
cp /opt/data/docs_flow_framework/ai_dev_flow/docs_templates/prd/* docs/prd/
cp /opt/data/docs_flow_framework/ai_dev_flow/docs_templates/ears/* docs/ears/
cp /opt/data/docs_flow_framework/ai_dev_flow/docs_templates/bbds/* docs/bbds/
cp /opt/data/docs_flow_framework/ai_dev_flow/docs_templates/adrs/* docs/adrs/
cp /opt/data/docs_flow_framework/ai_dev_flow/docs_templates/sys/* docs/sys/
cp /opt/data/docs_flow_framework/ai_dev_flow/docs_templates/reqs/* docs/reqs/
cp /opt/data/docs_flow_framework/ai_dev_flow/docs_templates/impl_plans/* docs/impl_plans/
cp /opt/data/docs_flow_framework/ai_dev_flow/docs_templates/contracts/* docs/contracts/
cp /opt/data/docs_flow_framework/ai_dev_flow/docs_templates/specs/* docs/specs/
cp /opt/data/docs_flow_framework/ai_dev_flow/docs_templates/ai_tasks/* docs/ai_tasks/

# Copy validation scripts
cp /opt/data/docs_flow_framework/ai_dev_flow/scripts/*.py scripts/
```

### Initialize Index Files

AI Assistant **MUST** create index files for each document type:

```bash
# Create index files
touch docs/brds/BRD-000_index.md
touch docs/prd/PRD-000_index.md
touch docs/ears/EARS-000_index.md
touch docs/bbds/BDD-000_index.feature
touch docs/adrs/ADR-000_index.md
touch docs/sys/SYS-000_index.md
touch docs/reqs/REQ-000_index.md
touch docs/impl_plans/IMPL-000_index.md
touch docs/contracts/CTR-000_index.md
touch docs/specs/SPEC-000_index.yaml
touch docs/ai_tasks/TASKS-000_index.md
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
| {TYPE}-001 | [First Document Title](../path/to/doc.md) | Draft | High | YYYY-MM-DD | YYYY-MM-DD |

---

## Next Available ID

**Next ID**: {TYPE}-001

**ID Assignment Rules**:
- Sequential numbering (001-999, then 1000+)
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

### ID Naming Standards

AI Assistant **MUST** follow these rules when creating documents:

#### Format
```
{TYPE}-{NNN}_{descriptive_slug}.{ext}
```

or for sub-documents:
```
{TYPE}-{NNN}-{YY}_{descriptive_slug}.{ext}
```

#### Components
- **{TYPE}**: Document type (BRD, PRD, REQ, ADR, CTR, SPEC, TASKS, etc.)
- **{NNN}**: Sequential number (001-999, then 1000+)
- **{YY}**: Sub-document number (01-99, then 100+) - optional
- **{descriptive_slug}**: Lowercase, underscores, describes content
- **{ext}**: File extension (.md, .yaml, .feature)

#### Examples
```
REQ-001_position_limit_enforcement.md
ADR-005_database_selection.md
CTR-012_market_data_api.md
CTR-012_market_data_api.yaml  (dual-file contract)
SPEC-023_risk_calculator.yaml
TASKS-023_implement_risk_calculator.md
REQ-042-01_authentication_methods.md  (sub-document)
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
touch docs/contracts/CTR-012_market_data_api.md
touch docs/contracts/CTR-012_market_data_api.yaml
```

**Matching slug requirement**: `market_data_api` must be identical in both filenames.

---

## Rule 7: Traceability Link Format

### Markdown Link Standard

AI Assistant **MUST** use this format for all document references:

```markdown
[{TYPE}-{ID}](../path/to/document.md#{TYPE}-{ID})
```

#### Examples
```markdown
[REQ-003](../reqs/risk/REQ-003_position_limit.md#REQ-003)
[ADR-005](../adrs/ADR-005_database_selection.md#ADR-005)
[CTR-012](../contracts/CTR-012_market_data_api.md#CTR-012)
[SPEC-023](../specs/SPEC-023_risk_calculator.yaml#SPEC-023)
```

### Section 7: Traceability

Every document **MUST** include Section 7 with:

1. **Upstream Sources** - Documents driving this artifact
2. **Downstream Artifacts** - Documents/code derived from this
3. **Primary Anchor/ID** - Main identifier for this document
4. **Code Paths** - Implementation locations (if applicable)

### Example Section 7

```markdown
## 7. Traceability

### Upstream Sources
| Source | Type | Reference |
|--------|------|-----------|
| [BRD-001](../brds/BRD-001_trading_platform.md#BRD-001) | Business Requirements | Risk management objectives |
| [PRD-002](../prd/PRD-002_risk_controls.md#PRD-002) | Product Requirements | Position limit feature |
| [ADR-008](../adrs/ADR-008_risk_architecture.md#ADR-008) | Architecture Decision | Real-time limit enforcement |

### Downstream Artifacts
| Artifact | Type | Reference |
|----------|------|-----------|
| [SPEC-023](../specs/SPEC-023_risk_calculator.yaml#SPEC-023) | Technical Specification | Implementation spec |
| [TASKS-023](../ai_tasks/TASKS-023_risk_calculator.md#TASKS-023) | Implementation Tasks | AI generation tasks |
| [BDD-015](../bbds/BDD-015_position_limits.feature#BDD-015) | BDD Scenarios | Acceptance tests |

### Primary Anchor/ID
- **REQ-003**: Position limit enforcement requirement

### Code Paths
- `src/risk/position_limiter.py::PositionLimiter.enforce_limit()`
- `tests/risk/test_position_limits.py::test_hard_limit_enforcement()`
```

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
python scripts/check_broken_references.py

# Validate requirement IDs (after documents created)
python scripts/validate_requirement_ids.py

# Generate traceability matrix (after documents created)
python scripts/generate_traceability_matrix.py --type REQ --input docs/reqs/ --output docs/TRACEABILITY_MATRIX_REQ.md
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
| "Missing Section 7" | Incomplete template | Add traceability section |
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
6. **Add Section 7** (traceability with upstream/downstream)
7. **Add anchor** at top: `<a id="{TYPE}-{ID}"></a>`
8. **Save file** with correct naming
9. **Update index file** with new entry
10. **Validate links** (run validation script)

### Template Section Requirements

AI Assistant **MUST** complete these sections in every document:

- **Document Control Table**: Status, version, priority, dates
- **Context/Purpose**: Why this document exists
- **Main Content**: Domain-specific requirements/specifications
- **Acceptance Criteria**: Measurable, testable conditions (for REQ)
- **Dependencies**: Prerequisites and constraints
- **Risks**: Potential issues and mitigations
- **Section 7: Traceability**: Complete upstream/downstream tables
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
  - Upstream section: [REQ-023](../reqs/risk/REQ-023_risk_calculator.md#REQ-023)

Step 3: Update REQ-023
  - Downstream section: [SPEC-023](../specs/SPEC-023_risk_calculator.yaml#SPEC-023)

Step 4: Create TASKS-023_implement_risk_calculator.md
  - Upstream section: [SPEC-023](../specs/SPEC-023_risk_calculator.yaml#SPEC-023)

Step 5: Update SPEC-023 and REQ-023
  - Add TASKS-023 to downstream sections

Step 6: Validate
  - Run check_broken_references.py
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
REQ-042-01_authentication_methods.md
REQ-042-02_password_policies.md
REQ-042-03_mfa_requirements.md
REQ-042-04_session_management.md
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
# PURPOSE: Enforce position limits per REQ-023 acceptance criteria
class PositionLimiter:
    """
    Position limit enforcement per [REQ-023](../docs/reqs/risk/REQ-023_position_limit.md).

    Architecture: [ADR-008](../docs/adrs/ADR-008_risk_architecture.md) - Real-time enforcement
    Acceptance Tests: [BDD-015](../docs/bbds/BDD-015_position_limits.feature)
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
# TEST: Position limit enforcement per acceptance criteria
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

## Summary: Execution Checklist

AI Assistant **MUST** complete this checklist for every new project:

- [ ] **Step 1**: Ask domain selection question
- [ ] **Step 2**: Create complete folder structure (all 11+ directories)
- [ ] **Step 3**: Load domain configuration file
- [ ] **Step 4**: Copy templates with domain placeholder replacement
- [ ] **Step 5**: Run contract decision questionnaire
- [ ] **Step 6**: Initialize all index files ({TYPE}-000_index.{ext})
- [ ] **Step 7**: Validate folder structure (ls -laR docs/)
- [ ] **Step 8**: Begin document creation following kickoff tasks
- [ ] **Step 9**: Maintain traceability (Section 7 in all documents)
- [ ] **Step 10**: Run validation scripts after each document
- [ ] **Step 11**: Generate code with traceability comments
- [ ] **Step 12**: Create tests matching BDD scenarios
- [ ] **Step 13**: Generate traceability matrices
- [ ] **Step 14**: Final validation before marking project setup complete

---

## Tool Integration Examples

### Claude Code Example

```markdown
User: "Initialize new financial services trading platform project"

Claude Code:
1. Domain Selection: "Financial Services (default) detected. Loading FINANCIAL_DOMAIN_CONFIG.md"
2. Folder Creation: "Creating 10-layer structure + finance subdirectories..."
   [Runs mkdir commands]
3. Validation: "Verifying structure... ✓ All directories created"
4. Template Setup: "Copying templates and applying financial domain placeholders..."
5. Contract Decision: "Running contract questionnaire..."
   User response: "Yes - REST API for market data"
   Action: "Including CTR layer in workflow"
6. Index Initialization: "Creating index files for all document types... ✓ Complete"
7. Ready: "Project initialized. Ready to create BRD-001. Next: Define business objectives."
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
6. Status: "✓ Project ready. Starting with BRD-001..."
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
- [TOOL_OPTIMIZATION_GUIDE.md](./TOOL_OPTIMIZATION_GUIDE.md) - AI tool selection

---

**End of AI Assistant Execution Rules**
