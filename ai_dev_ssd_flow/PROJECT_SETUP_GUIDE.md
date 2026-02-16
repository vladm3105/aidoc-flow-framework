---
title: "Project Setup Guide"
tags:
  - framework-guide
  - shared-architecture
custom_fields:
  document_type: guide
  priority: shared
  development_status: active
---

# Project Setup Guide

**Version**: 1.1
**Purpose**: Master initialization guide for AI Assistants to set up new projects
**Target**: AI coding assistants (see AI_TOOL_OPTIMIZATION_GUIDE.md for tool-specific notes)
**Status**: Production

---

## Quick Start Overview

This guide walks AI Assistants through initializing a brand new project using the AI Dev Flow framework. Follow these steps in order.

### 🚀 Using the project-init Skill (Recommended)

For users of AI coding assistants: If your assistant provides a project initialization capability (e.g., a `project-init` skill), use it to automate this guide. See AI_TOOL_OPTIMIZATION_GUIDE.md for tool-specific tips.

```
User: "Initialize new project"
AI Assistant: Uses project-init skill
    → Runs domain selection questionnaire
    → Creates all folders automatically
    → Applies domain configuration
    → Runs contract decision questionnaire
    → Initializes index files
    → Validates setup
    → Hands off to doc-flow skill
```

**To use the skill**:
1. Invoke: your assistant’s project initialization command (e.g., `project-init`)
2. Follow the interactive prompts
3. After completion, use `doc-flow` skill for workflow execution

**Manual Setup**: If not using the skill, follow the 8 steps below manually.

---

## Setup Steps

### Step 1: Domain Selection (REQUIRED FIRST)

**AI Assistant Action**: Run [DOMAIN_SELECTION_QUESTIONNAIRE.md](./DOMAIN_SELECTION_QUESTIONNAIRE.md)

```
User is prompted with:
"What is the purpose and focus of this new project?"

Options:
1. Financial Services (DEFAULT)
2. Software/SaaS
3. Healthcare
4. E-commerce
5. IoT
6. Other/Generic
```

**Output**: Domain selected, configuration file loaded

**Example**:
```
✓ Domain selected: Financial Services
✓ Loading configuration: FINANCIAL_DOMAIN_CONFIG.md
✓ Domain-specific REQ subdirectories will be created on-demand during document generation
```

---

### Step 1.5: Workflow Selection (REQUIRED)

**AI Assistant Action**: Determine if this is a Standard or MVP project.

```
User is prompted with:
"Is this a full enterprise project or a rapid Minimum Viable Product (MVP)?"

 Options:
1. Standard Flow (Full templates, 15 layers, strict validation) - Recommended for Enterprise
2. MVP Track (Streamlined templates, faster setup, "Good Enough" validation) - Recommended for Startups/Prototypes
```

**If MVP Track Selected**:
- Use **MVP Templates** (`*-MVP-TEMPLATE.md`) instead of full templates.
- Follow schedule in [MVP_WORKFLOW_GUIDE.md](./MVP_WORKFLOW_GUIDE.md).
- Skip to Step 2.

---

### Step 2: Folder Structure Creation (REQUIRED SECOND)

**AI Assistant Action**: Create complete directory structure BEFORE creating any documents

**IMPORTANT**: Ensure project root directory exists first:
```bash
# Create project root directory if it doesn't exist
mkdir -p /opt/data/project_name
cd /opt/data/project_name
```

**Commands**:
```bash
# Core 15-layer architecture artifact directories (BRD through TASKS)
mkdir -p docs/BRD docs/PRD docs/EARS docs/BDD docs/ADR docs/SYS docs/REQ docs/CTR docs/SPEC docs/TSPEC docs/TASKS

# NOTE: REQ and CTR subdirectories are created on-demand by doc-req and doc-ctr skills
# when documents are generated. This ensures folders match actual project needs.

# Support directories
mkdir -p scripts
mkdir -p work_plans
```

Note: `work_plans/` is an optional helper directory for scratch operational notes.

**Validation**:
```bash
ls -la docs/  # Verify 11 artifact directories created (BRD through TASKS)
ls -la work_plans/  # Verify work_plans directory
```

**Output**: Complete folder structure ready

---

### Step 3: Template Copying

**AI Assistant Action**: Copy framework templates to project

**Commands**:
```bash
# Point to the framework checkout (adjust for your environment)
FRAMEWORK_ROOT=/path/to/ai_dev_flow

# Create ai_dev_flow directory for framework templates
mkdir -p ai_dev_flow

# Copy all templates into your project ai_dev_flow/ directory
cp -r "$FRAMEWORK_ROOT"/* ai_dev_flow/

# Copy validation scripts
mkdir -p scripts
cp "$FRAMEWORK_ROOT/scripts"/*.py scripts/
```

**Directory Purpose**:
- `ai_dev_flow/` = Framework templates (MVP defaults: `*-MVP-TEMPLATE.*`; full templates archived)
- `docs/` = Project documentation (BRD-01.md, PRD-01.md, etc.)

**Action for MVP Track**:
- When creating `BRD-01`, `PRD-01`, etc., use the `*-MVP-TEMPLATE.md` source files.
- See [MVP_WORKFLOW_GUIDE.md](./MVP_WORKFLOW_GUIDE.md) for details.

---

### Step 4: Domain Configuration Application

**AI Assistant Action**: Apply domain-specific placeholder replacements

**Financial Services Example**:
```bash
find docs/ -type f -name "*.md" -exec sed -i \
  -e 's/\[RESOURCE_COLLECTION\]/collection/g' \
  -e 's/\[RESOURCE_ITEM\]/Position/g' \
  -e 's/\[USER_ROLE\]/Trader/g' \
  {} +
```

**Output**: Templates customized with domain terminology

---

### Step 5: Contract Decision (REQUIRED)

**AI Assistant Action**: Run [CONTRACT_DECISION_QUESTIONNAIRE.md](./CONTRACT_DECISION_QUESTIONNAIRE.md)

```
User is prompted with:
"Does this project require API contracts or interface definitions?"

Options:
1. REST/GraphQL APIs
2. Event Schemas
3. Data Contracts
4. RPC/gRPC
5. WebSocket APIs
6. File Formats
7. None - Internal logic only
8. Unsure
```

**Output**: Workflow determined

- **With CTR**: `REQ → CTR → SPEC → TSPEC → TASKS`
- **Without CTR**: `REQ → SPEC → TSPEC → TASKS`

---

### Step 6: Index File Initialization

**AI Assistant Action**: Create index files for each document type

**Commands**:
```bash
# Create index files
touch docs/01_BRD/BRD-00_index.md
touch docs/02_PRD/PRD-00_index.md
touch docs/03_EARS/EARS-00_index.md
# Create a BDD suite folder and index file (per suite)
mkdir -p docs/04_BDD/BDD-NN_{slug}
touch docs/04_BDD/BDD-NN_{slug}/BDD-NN.0_index.md
touch docs/05_ADR/ADR-00_index.md
touch docs/06_SYS/SYS-00_index.md
touch docs/07_REQ/REQ-00_index.md
touch docs/08_CTR/CTR-00_index.md
  touch docs/09_SPEC/SPEC-00_index.yaml
  touch docs/11_TASKS/TASKS-00_index.md

```

**Output**: All index files created

---

### Step 7: Validation

**AI Assistant Action**: Verify setup complete

**Validation Commands**:
```bash
# Verify directory structure
ls -laR docs/

# Verify index files
ls docs/*/index.* || ls docs/*/*_index.*

# Verify scripts
ls scripts/*.py
```

**Success Criteria**:
- All 10 artifact directories exist (BRD through TASKS)
- Domain-specific subdirectories exist
- All index files created
- Validation scripts present
- work_plans directory exists (for /save-plan command output)

---

### Step 8: Project Ready

**AI Assistant Confirmation**:
```
═══════════════════════════════════════════════════════════
              PROJECT INITIALIZATION COMPLETE
═══════════════════════════════════════════════════════════

✓ Domain: Financial Services
✓ Folders: Created (13 artifact directories + domain subdirectories)
✓ Templates: Copied and customized
✓ Contracts: Included (CTR layer active)
✓ Index Files: Initialized
✓ Scripts: Ready

Workflow: 15-layer architecture: BRD → PRD → EARS → BDD → ADR → SYS → REQ → [CTR] → SPEC → TSPEC → TASKS → Code → Tests → Deployment (brackets indicate optional layers)

Next Steps:
1. Use `doc-flow` skill to begin workflow execution (recommended)
2. Or manually review [PROJECT_KICKOFF_TASKS.md](./PROJECT_KICKOFF_TASKS.md) for Day 1-7 tasks
3. Start with BRD-01 (Business Requirements Document)
4. Follow 15-layer architecture sequentially

═══════════════════════════════════════════════════════════
```

---

## Document Creation Rules

### Quality Enforcement Protocol

**Objective**: Create high-quality, consistent project documents through rigorous validation

**Core Principles**:

1. **Use Appropriate Skills**: Invoke `doc-{doc_type}` skill for AI-powered document generation
2. **Immediate Validation**: Validate each document immediately after creation
3. **Fix Before Proceeding**: Fix all errors before starting next document
4. **Comprehensive Review**: Perform final review of all documents in phase before proceeding
5. **Zero Tolerance**: Do not start next document type until all errors and warnings resolved
6. **No Quick Fixes**: Review everything carefully and individually
7. **Quality Gate**: Pass all validations without errors/warnings before next phase
8. **Update Execution Plan**: Update project execution plan in `work_plans/` after each phase completion

### Document Generation Workflow

#### Phase Execution Process

```text
For each document type in workflow sequence:
  1. Generate document using doc-{type} skill
  2. Run automated validation
  3. Run manual validation checks
  4. Fix all errors (no exceptions)
  5. Fix all warnings (no exceptions)
  6. Re-validate until clean
  7. Mark document as complete

After all documents of type created:
  8. Final phase review
  9. Cross-document consistency check
  10. Upstream document validation
  11. Fix all inconsistencies
  12. Execute additional checks as needed
  13. Quality gate approval
  14. Update project execution plan in work_plans/
  15. Proceed to next document type
```

#### Per-Document Validation Sequence

```bash
# 1. Generate document
# Use: doc-brd, doc-prd, doc-req, etc.

# 2. Automated validation (framework scripts)
./07_REQ/scripts/validate_req_template.sh docs/07_REQ/REQ-01_example.md
python scripts/validate_metadata.py docs/07_REQ/REQ-01_example.md

# 3. Manual validation checklist
# - Verify YAML frontmatter structure
# - Check traceability tags (@brd, @prd, @ears, etc.)
# - Validate naming conventions (ID_NAMING_STANDARDS.md)
# - Confirm acceptance criteria format
# - Review verification methods

# 4. Fix errors (mandatory)
# Address all validation errors before proceeding

# 5. Re-validate
# Repeat validation until error-free
```

#### Phase-Level Validation Sequence

```bash
# After all documents of type created

# 1. Cross-document consistency
grep -r "@prd: PRD-" docs/07_REQ/*.md | sort | uniq
# Verify all PRD references exist

# 2. Upstream validation
# Verify all upstream dependencies valid
# Example: All @prd tags in REQ files point to existing PRD-XXX

# 3. Inconsistency detection
python scripts/trace_check.py --type REQ
# Check bidirectional traceability

# 4. Additional checks
# - Duplicate REQ-ID detection
# - Orphaned requirements
# - Missing acceptance criteria
# - Invalid priority values

# 5. Quality gate approval
# All documents pass all checks

# 6. Update project execution plan
# Edit work_plans/{project}-init_REVISED_{date}.md
# Document completed phase, issues encountered, next steps
```

### Project Execution Plan Update Protocol

**Purpose**: Maintain living documentation of project initialization progress in `work_plans/` directory.

**What is the Project Execution Plan**:
- Located in: `work_plans/` directory
- Naming: `{project-name}-project-init_YYYYMMDD.md` or `{project-name}-project-init_REVISED_YYYYMMDD.md`
- Purpose: Track project initialization and documentation creation workflow
- Created by: `/save-plan` command or manually during project setup

**Plan Contents**:
- Current progress summary with completion status
- Completed milestones by layer (BRD, PRD, REQ, etc.)
- Known issues and their priority
- Next steps and ready-to-proceed actions
- Objective and key principles
- Execution steps with validation gates
- Update log tracking changes over time

**Update Triggers**:
- Phase completion (all BRD, all PRD, all REQ, etc.)
- Significant scope changes (>5 documents modified or major changes)
- Architecture decisions (ADR created that affects workflow)
- Contract additions/removals (CTR layer added/removed)
- Major validation failures requiring rework
- Domain configuration changes
- Workflow sequence adjustments

**Update Format Example**:

```markdown
# Implementation Plan - Project Name Initialization (REVISED)

**Created**: 2025-12-01T00:00:00 (Revised with Validation Gates)
**Last Updated**: 2025-12-01T00:00:00
**Status**: IN PROGRESS - Layer 1 (BRD) Complete, Ready for Layer 2 (PRD)

---

## Current Progress Summary (2025-12-01T00:00:00)

### ✅ Completed Milestones

**Layer 1: Business Requirements Documents (BRD)**
- **Status**: ✅ COMPLETE (100% compliance, 70/70 checks passed)
- **Documents Created**: 5 MVP BRDs (BRD-01 through BRD-05)
- **Creation Method**: doc-brd skill (AI-powered generation)
- **Validation Method**: Dual-layer (automated script + manual review)
- **Template Compliance**: 100%
- **Pass Rate**: 100%

**MVP BRD Documents**:
1. ✅ BRD-01: Platform Overview (Platform BRD)
2. ✅ BRD-02: Content Ingestion (Feature BRD)
3. ✅ BRD-03: Analysis Engine (Feature BRD)
4. ✅ BRD-04: Reporting System (Feature BRD)
5. ✅ BRD-05: REST API (Feature BRD)

### ⚠️ Known Issues

**BRD-01 Structural Inconsistencies** (P2 Priority - Not Blocking):
- Missing YAML frontmatter with `brd_type: platform` field
- Different table format causing grep pattern failures
- Content is complete and correct (manually validated)
- Impact: Low (formatting/parsing only, not content)

### 🎯 Next Steps

**Immediate Actions** (Optional):
1. Update BRD-00_index.md with all 5 created BRDs
2. Fix BRD-01 structural issues (YAML frontmatter, table format)
3. Create BRD-00_TRACEABILITY_MATRIX.md

**Ready to Proceed**:
- Layer 2: PRD creation (5 PRD documents: PRD-01 through PRD-005)
- Stakeholder review and approval of BRD documents

---

## Objective

Initialize the project with 15-layer SDD documentation structure using STRICT framework templates, creation rules, and validation gates.

## Key Principles

1. **Template-First**: Use only framework templates
2. **Creation Rules Compliance**: Follow CREATION_RULES.md
3. **Validation Gates**: Run validation scripts after each document type
4. **Fix-Before-Proceed**: Fix ALL issues before next type
5. **No Shortcuts**: Never skip validation
```

**AI Assistant Responsibility**:
- Update execution plan after completing each document type phase
- Document actual outcomes vs planned outcomes
- Track issues encountered and resolutions applied
- Maintain plan accuracy throughout project lifecycle

### Validation Rules by Document Type

#### BRD (Business Requirements)

**Required Elements**:
- YAML frontmatter with required fields
- Business objectives defined
- Stakeholders identified
- Success metrics specified
- No technical implementation details (business language only)

**Validation Commands**:
```bash
# Automated validation
python scripts/validate_metadata.py docs/01_BRD/BRD-01_*.md

# Manual checks
# - Business language (not technical)
# - Measurable success criteria
# - Stakeholder sign-off section
# - Financial analysis (ROI, NPV, payback period)
```

#### PRD (Product Requirements)

**Required Elements**:
- All BRD objectives addressed
- Features defined with priorities
- User stories included
- Acceptance criteria per feature
- Traceability to BRD (@brd tags)

**Validation Commands**:
```bash
# Automated validation
python scripts/validate_metadata.py docs/02_PRD/PRD-01_*.md

# Cross-reference check
grep "@brd:" docs/02_PRD/*.md | cut -d: -f2 | sort | uniq
ls docs/01_BRD/BRD-*.md
# Verify all @brd references exist
```

#### REQ (Atomic Requirements)

**Required Elements**:
- REQ v3.0 12-section format
- Unique REQ-ID per requirement
- Priority: MUST/SHOULD/MAY
- Acceptance criteria (5-part format recommended)
- Traceability tags (@prd, @brd, @ears)
- Verification methods specified
- SPEC-readiness scoring

**Validation Commands**:
```bash
# Primary validation
./07_REQ/scripts/validate_req_template.sh docs/07_REQ/REQ-01_*.md

# Duplicate detection
grep -h "^## REQ-" docs/07_REQ/*.md | sort | uniq -d
# Output should be empty (no duplicates)

# Traceability check
python scripts/trace_check.py --type REQ --strict
```

#### SPEC (Technical Specifications)

**Required Elements**:
- YAML format required
- Implementation details complete
- Technology stack specified
- API contracts defined (if applicable)
- Traceability to REQ (@req tags)
- Test strategy included

**Validation Commands**:
```bash
# YAML syntax validation
python -c "import yaml; yaml.safe_load(open('docs/09_SPEC/SPEC-01_*.yaml'))"

# Schema validation
python scripts/validate_spec_schema.py docs/09_SPEC/SPEC-01_*.yaml

# REQ coverage check
grep "@req:" docs/09_SPEC/*.yaml | cut -d: -f2 | sort | uniq
# Verify all requirements covered
```

#### TASKS (Task Breakdown)

**Required Elements**:
- Tasks derived from SPEC
- Dependencies mapped
- Acceptance criteria per task
- Implementation contracts (if parallel work required)
- Traceability to SPEC (@spec tags)
- Estimated complexity (1-5 scale)

**Validation Commands**:
```bash
# Dependency validation
python scripts/validate_task_dependencies.py docs/11_TASKS/TASKS-01_*.md

# Contract verification: Check TASKS Section 7-8 for implementation contracts
```

### Error Resolution Protocol

#### Error Categories

1. **Critical Errors** (Must fix immediately):
   - Missing required sections
   - Invalid YAML syntax
   - Duplicate IDs
   - Broken traceability references
   - Missing acceptance criteria
   - Failed automated validation scripts

2. **Warnings** (Must fix before phase completion):
   - Inconsistent formatting
   - Incomplete traceability
   - Missing verification methods
   - Unclear acceptance criteria
   - Incomplete metadata

3. **Style Issues** (Fix during final review):
   - Markdown formatting inconsistencies
   - Heading hierarchy issues
   - Link formatting
   - Table alignment

#### Resolution Process

**For Each Error**:
```text
1. Identify error type and location (file:line)
2. Read relevant framework standards
3. Apply fix according to standards
4. Re-validate immediately
5. Document fix in commit message
6. Proceed to next error

DO NOT:
- Batch fix multiple errors without validation
- Apply quick fixes without understanding root cause
- Skip validation after fixing
- Proceed with warnings unresolved
- Use placeholder values or "TODO" comments
```

### Phase Completion Checklist

**Before Starting Next Document Type**:

```text
☐ All documents of current type created
☐ All automated validations pass (0 errors)
☐ All manual checks completed
☐ All warnings resolved
☐ Cross-document consistency verified
☐ Upstream traceability validated
☐ Downstream references checked
☐ Phase review completed
☐ Project execution plan (work_plans/) updated with phase outcomes
☐ Quality gate approved
☐ Git commit with validation summary
```

### Common Validation Failures

#### Duplicate REQ-IDs

```bash
# Detection
grep -h "^## REQ-" docs/07_REQ/*.md | sort | uniq -d

# Resolution
# 1. Manually review duplicates
# 2. Assign unique IDs following ID_NAMING_STANDARDS.md
# 3. Update traceability references
# 4. Re-validate
```

#### Broken Traceability

```bash
# Detection
python scripts/trace_check.py --strict

# Resolution
# 1. Add missing @tag references
# 2. Verify upstream documents exist
# 3. Update traceability matrix
# 4. Re-validate bidirectional links
```

#### Invalid YAML Frontmatter

```bash
# Detection
python scripts/validate_metadata.py docs/07_REQ/*.md

# Resolution
# 1. Fix YAML syntax errors (indentation, quotes)
# 2. Add missing required fields
# 3. Validate tag taxonomy compliance
# 4. Re-validate
```

#### Missing Acceptance Criteria

```bash
# Detection
grep -L "Acceptance Criteria" docs/07_REQ/*.md

# Resolution
# 1. Add acceptance criteria section
# 2. Use 5-part format (Given/When/Then/And/Verify)
# 3. Include measurable outcomes
# 4. Link to verification methods
```

### Quality Metrics

**Target Quality Scores**:
- Validation pass rate: 100%
- Traceability coverage: 100%
- Acceptance criteria completeness: 100%
- Duplicate ID rate: 0%
- Broken reference rate: 0%

**Measurement Commands**:
```bash
# Generate quality report
python scripts/quality_metrics.py --phase REQ

# Expected output:
# Total documents: 45
# Validation passes: 45/45 (100%)
# Traceability coverage: 45/45 (100%)
# Acceptance criteria: 45/45 (100%)
# Duplicate IDs: 0
# Broken references: 0
# Quality gate: PASS ✓
```

### Integration with Workflow

**Document Creation Sequence**:
```text
BRD Phase:
  Generate BRD-01 → Validate → Fix → Complete
  Generate BRD-02 → Validate → Fix → Complete
  ...
  Phase Review → Quality Gate → Update work_plans/ → Proceed to PRD

PRD Phase:
  Generate PRD-01 → Validate → Fix → Complete
  Generate PRD-02 → Validate → Fix → Complete
  ...
  Phase Review → Verify BRD traceability → Quality Gate → Update work_plans/ → Proceed to EARS

REQ Phase:
  Generate REQ-01 → Validate → Fix → Complete
  Generate REQ-02 → Validate → Fix → Complete
  ...
  Phase Review → Verify 02_PRD/EARS traceability → Quality Gate → Update work_plans/ → Proceed to SPEC

SPEC Phase:
  Generate SPEC-01 → Validate → Fix → Complete
  ...
  Phase Review → Verify REQ coverage → Quality Gate → Update work_plans/ → Proceed to TASKS

TASKS Phase:
  Generate TASKS-01 → Validate → Fix → Complete
  ...
  Phase Review → Quality Gate → Update work_plans/ → Ready for implementation
```

### AI Assistant Responsibilities

**During Document Creation**:
1. Use appropriate doc-{type} skill
2. Execute validation immediately after generation
3. Report validation results to user
4. Fix errors before asking to proceed
5. Request user approval only after passing validation
6. Maintain quality metrics throughout session
7. Update project execution plan after each phase

**Validation Reporting Format**:
```text
Document: REQ-01_example.md
Status: Created

Validation Results:
✓ YAML frontmatter valid
✓ REQ-ID unique (REQ-032)
✓ Priority specified (MUST)
✓ Acceptance criteria complete (5-part format)
✓ Traceability tags present (@prd: PRD.01.07.01, @ears: EARS.01.24.01)
✓ Verification methods defined
✓ Metadata compliant

Automated Checks:
✓ validate_req_template.sh: PASS
✓ validate_metadata.py: PASS

Status: Ready for review ✓
```

**Error Reporting Format**:
```text
Document: REQ-02_example.md
Status: Created

Validation Results:
✗ ERROR: Duplicate REQ-ID (REQ-032 already exists)
✗ ERROR: Missing acceptance criteria section
⚠ WARNING: Incomplete traceability (@prd tag missing)

Automated Checks:
✗ validate_req_template.sh: FAIL (2 errors, 1 warning)

Status: Requires fixes before proceeding

Fixes Required:
1. Assign unique REQ-ID (next available: REQ-046)
2. Add acceptance criteria section with 5-part format
3. Add @prd traceability tag

Next Action: Fix errors and re-validate
```

**Project Execution Plan Update Duties**:
- Update `work_plans/{project}-init_REVISED_{date}.md` after each phase
- Document completion status, validation results, issues encountered
- Update "Current Progress Summary" section
- Add to "Completed Milestones" with metrics
- Document any "Known Issues" discovered
- Update "Next Steps" with immediate actions
- Maintain accurate status header

---

## Complete Example: Enterprise Service Platform

### Initialization Transcript

```
User: "Initialize new project"

AI Assistant: Running domain selection questionnaire...

═══════════════════════════════════════════════════════════
What is the purpose and focus of this new project?
1. Financial Services (DEFAULT)
2. Software/SaaS
3. Healthcare
4. E-commerce
5. IoT
6. Other/Generic
═══════════════════════════════════════════════════════════

User: [Enter] (selects default: Financial Services)

AI Assistant:
✓ Domain selected: Financial Services
✓ Loading configuration: FINANCIAL_DOMAIN_CONFIG.md
✓ Domain-specific subdirectories: risk, operations, data, compliance, ml

Creating folder structure...
✓ Created: docs/01_BRD/
✓ Created: docs/02_PRD/
✓ Created: docs/03_EARS/
✓ Created: docs/04_BDD/
✓ Created: docs/05_ADR/
✓ Created: docs/06_SYS/
✓ Created: docs/07_REQ/
✓ Created: docs/08_CTR/
✓ Created: docs/09_SPEC/
✓ Created: docs/11_TASKS/

✓ Created: docs/07_REQ/api/
✓ Created: docs/07_REQ/auth/
✓ Created: docs/07_REQ/data/
✓ Created: docs/07_REQ/risk/
✓ Created: docs/07_REQ/operations/
✓ Created: docs/07_REQ/collection/
✓ Created: docs/07_REQ/compliance/
✓ Created: docs/07_REQ/ml/

✓ Created: scripts/
✓ Created: work_plans/

Copying templates...
✓ Templates copied from framework

Applying Financial Services domain configuration...
✓ [RESOURCE_COLLECTION] → collection
✓ [RESOURCE_ITEM] → Position
✓ [USER_ROLE] → Trader
✓ [REGULATORY_REQUIREMENT] → regulatory Rule 15c3-5

Running contract decision questionnaire...

═══════════════════════════════════════════════════════════
Does this project require API contracts or interface definitions?
1. REST/GraphQL APIs
2. Event Schemas
3. Data Contracts
7. None - Internal logic only
═══════════════════════════════════════════════════════════

User: "1,2" (REST APIs and Event Schemas)

AI Assistant:
✓ Contracts needed
✓ Contract types: REST/GraphQL APIs (OpenAPI), Event Schemas (AsyncAPI)
✓ Workflow: REQ → CTR → SPEC → TSPEC → TASKS

Initializing index files...
✓ All index files created

Validation...
✓ All directories verified
✓ All index files verified
✓ Scripts ready

═══════════════════════════════════════════════════════════
              PROJECT INITIALIZATION COMPLETE
═══════════════════════════════════════════════════════════

Project Ready!

Next: Review PROJECT_KICKOFF_TASKS.md for Day 1-7 action plan
```

---

## Troubleshooting

### Error: Directory Already Exists

**Issue**: `mkdir: cannot create directory 'docs': File exists`

**Resolution**:
- This is expected if project already initialized
- Skip folder creation step
- Verify existing structure: `ls -la docs/`

---

### Error: Permission Denied

**Issue**: `mkdir: cannot create directory: Permission denied`

**Resolution**:
- Check current working directory permissions
- Ensure write access to parent directory
- Use absolute paths if needed

---

### Error: Template Not Found

**Issue**: `cp: cannot stat "$FRAMEWORK_ROOT"/*: No such file or directory`

**Resolution**:
- Verify framework path
- Check if framework is installed
- Use alternative path if framework location differs

---

## Quick Reference Commands

### Initialize Project (All Steps)

```bash
# Step 1: Domain Selection (interactive)
# AI Assistant runs DOMAIN_SELECTION_QUESTIONNAIRE.md

# Step 2: Create Folders
mkdir -p docs/{BRD,PRD,EARS,BDD,ADR,SYS,REQ,CTR,SPEC,TASKS}
mkdir -p scripts work_plans
# NOTE: 07_REQ/CTR subdirectories created on-demand by doc-req/doc-ctr skills

# Step 3: Copy Templates
FRAMEWORK_ROOT=/path/to/ai_dev_flow
mkdir -p ai_dev_flow
cp -r "$FRAMEWORK_ROOT"/* ai_dev_flow/
cp "$FRAMEWORK_ROOT/scripts"/*.py scripts/

# Step 4: Apply Domain Config
# Run placeholder replacement based on domain selection

# Step 5: Contract Decision (interactive)
# AI Assistant runs CONTRACT_DECISION_QUESTIONNAIRE.md

# Step 6: Initialize Index Files
for type in BRD PRD EARS BDD ADR SYS REQ CTR SPEC TASKS; do
  touch docs/$type/*_index.*
done

# Step 7: Validate
ls -laR docs/
```

---

## Relationship to project-init Skill

### For AI coding assistants

**Best Practice**: Use the **`project-init` skill** which automates this entire guide:

**Skill Location**: `/opt/data/docs_flow_framework/.claude/skills/project-init/SKILL.md`

**What the skill does**:

1. References this guide (PROJECT_SETUP_GUIDE.md) as authoritative source
2. Automates all 8 steps interactively
3. Provides user-friendly prompts and confirmations
4. Handles errors and validation
5. Hands off to `doc-flow` skill upon completion

**When to use skill vs manual**:

- ✅ **Use skill**: For standard project initialization (recommended)
- ✅ **Use manual**: For custom setups, debugging, or understanding the process

### Workflow Integration

```text
project-init skill (automates this guide)
         ↓
PROJECT_SETUP_GUIDE.md (8 steps)
         ↓
Project Initialized ✅
         ↓
doc-flow skill (workflow execution)
         ↓
PROJECT_KICKOFF_TASKS.md (Day 1-7)
```

---

## References

- [AI_ASSISTANT_RULES.md](./AI_ASSISTANT_RULES.md) - Core execution rules
- [DOMAIN_SELECTION_QUESTIONNAIRE.md](./DOMAIN_SELECTION_QUESTIONNAIRE.md) - Step 1 guidance
- [CONTRACT_DECISION_QUESTIONNAIRE.md](./CONTRACT_DECISION_QUESTIONNAIRE.md) - Step 5 guidance
- [PROJECT_KICKOFF_TASKS.md](./PROJECT_KICKOFF_TASKS.md) - Day 1-7 tasks
- [FINANCIAL_DOMAIN_CONFIG.md](./FINANCIAL_DOMAIN_CONFIG.md) - Financial domain config
- [SOFTWARE_DOMAIN_CONFIG.md](./SOFTWARE_DOMAIN_CONFIG.md) - Software/SaaS config
- [GENERIC_DOMAIN_CONFIG.md](./GENERIC_DOMAIN_CONFIG.md) - Generic config

### Related Skills

- Use your assistant’s project initialization capability (e.g., `project-init`) to automate this guide
- **doc-flow** skill - Workflow execution after initialization

---

## End of Project Setup Guide
