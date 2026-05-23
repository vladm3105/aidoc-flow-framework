---
name: project-init
description: Initialize projects with AI Dev Flow framework using domain-aware setup
metadata:
  tags:
    - sdd-workflow
    - shared-architecture
  custom_fields:
    layer: null
    artifact_type: null
    architecture_approaches: [ai-agent-based, traditional-8layer]
    priority: shared
    development_status: active
    skill_category: utility
    upstream_artifacts: []
    downstream_artifacts: [BRD]
    framework_spec_version: 8-layer
    version: "1.0"
    last_updated: "2026-05-23"
    versioning_policy: "tracks skill behavior"
---

# project-init

## Purpose
Provide AI assistants with structured guidance for initializing brand new (greenfield) projects using the AI Dev Flow framework. This skill handles the one-time setup process that must occur BEFORE workflow execution begins.

**⚠️ CRITICAL**: This skill is for NEW PROJECT INITIALIZATION ONLY. For ongoing workflow execution on existing projects, use the `doc-flow` skill instead.

## When to Use This Skill

**Use project-init when:**
- Starting a brand new project from scratch (greenfield)
- No project folders exist yet
- Domain has not been selected
- Project structure needs to be initialized

**Do NOT use project-init when:**
- Project already has docs/ folder structure
- Domain is already configured
- Working on existing project
- → Use `doc-flow` skill instead for workflow execution

## Hand-off to doc-flow

After completing project initialization, AI Assistant **MUST** inform user:

```
✅ Project initialization complete!

Next: Use the `doc-flow` skill to begin workflow execution:
- Create BRD (Business Requirements)
- Create PRD (Product Requirements)
- Follow the 8-layer SDD flow (Layers 1-8) with 8 artifact directories (BRD through IPLAN): BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code
```

---

## Initialization Workflow (7 Steps)

### Step 0: Read Execution Rules

**File**: [AI_ASSISTANT_RULES.md]({project_root}/framework/AI_ASSISTANT_RULES.md)

**Purpose**: Understand core execution rules before starting

**Key Rules**:
1. Domain Selection FIRST
2. Create Folders BEFORE Documents
3. Apply Domain Configuration
4. Initialize Index Files
5. Validate Setup
6. Token Optimization
7. Tool-Specific Guidance

**Action**: AI Assistant reads this file to understand the core execution rules

---

### Step 1: Domain Selection (REQUIRED FIRST)

**File**: [DOMAIN_SELECTION_QUESTIONNAIRE.md]({project_root}/framework/DOMAIN_SELECTION_QUESTIONNAIRE.md)

**Purpose**: Determine project domain to load correct configuration

**AI Assistant Action**: Present questionnaire to user

```
═══════════════════════════════════════════════════════════
                 PROJECT DOMAIN SELECTION
═══════════════════════════════════════════════════════════

What is the purpose and focus of this new project?

Select one:

1. Financial Services (DEFAULT)
   - Trading platforms, banking, insurance, portfolio management
   - Regulatory: SEC, FINRA, SOX, Basel III, PCI-DSS

2. Software/SaaS
   - B2B/B2C software services, multi-tenant applications
   - Regulatory: SOC2, GDPR/CCPA, ISO 27001

3. Healthcare
   - EMR, telemedicine, medical devices, patient management
   - Regulatory: HIPAA, FDA, HITECH, 21 CFR Part 11

4. E-commerce
   - Retail, marketplace, subscription services
   - Regulatory: PCI-DSS, GDPR/CCPA, FTC

5. IoT (Internet of Things)
   - Connected devices, sensors, industrial systems
   - Regulatory: FCC, CE, UL/IEC, FDA (medical devices)

6. Other/Generic
   - Internal tools, utilities, custom domain
   - Regulatory: Company policies only

Enter selection (1-6) or press Enter for default (1):
```

**Output**: Domain selected, configuration file determined

**Domain Configuration Mapping**:
| Selection | Domain | Config File |
|-----------|--------|-------------|
| 1 or Enter | Financial Services | FINANCIAL_DOMAIN_CONFIG.md |
| 2 | Software/SaaS | SOFTWARE_DOMAIN_CONFIG.md |
| 3 | Healthcare | DOMAIN_ADAPTATION_GUIDE.md (Healthcare) |
| 4 | E-commerce | DOMAIN_ADAPTATION_GUIDE.md (E-commerce) |
| 5 | IoT | DOMAIN_ADAPTATION_GUIDE.md (IoT) |
| 6 | Other/Generic | GENERIC_DOMAIN_CONFIG.md |

---

### Step 2: Folder Structure Creation (REQUIRED SECOND)

**Rule**: AI Assistant **MUST** create complete directory structure BEFORE creating any documents.

**Why**: Prevents "file not found" errors, ensures proper organization

**IMPORTANT**: Ensure project root directory exists first:

```bash
# Create project root directory if it doesn't exist
mkdir -p {project_root}
cd {project_root}
```

> Replace `{project_root}` with your actual project path (e.g., `/opt/data/my_project`)

**Commands to Execute**:

```bash
# Core 8 artifact directories (BRD through IPLAN) — numbered per the 8-layer SDD flow
mkdir -p docs/01_BRD
mkdir -p docs/02_PRD
mkdir -p docs/03_EARS
mkdir -p docs/04_BDD
mkdir -p docs/05_ADR
mkdir -p docs/06_SPEC
mkdir -p docs/07_TDD
mkdir -p docs/08_IPLAN

# Temporary plans for bugfixes/corrections live under IPLAN
mkdir -p docs/08_IPLAN/tmp

# Work plans directory (for /save-plan command output)
mkdir -p plans
```

**Validation**:
```bash
ls -la docs/  # Verify 8 artifact directories created
ls -la plans/  # Verify plans directory
```

---

### Step 3: Load Domain Configuration

**Files**:
- [FINANCIAL_DOMAIN_CONFIG.md]({project_root}/framework/FINANCIAL_DOMAIN_CONFIG.md) - Default
- [SOFTWARE_DOMAIN_CONFIG.md]({project_root}/framework/SOFTWARE_DOMAIN_CONFIG.md)
- [GENERIC_DOMAIN_CONFIG.md]({project_root}/framework/GENERIC_DOMAIN_CONFIG.md)

**Purpose**: Apply domain-specific terminology and placeholders

**AI Assistant Action**:
1. Read selected domain configuration file
2. Extract placeholder mappings
3. Store terminology for document generation

**Example Mappings**:

**Financial Services**:
```
[RESOURCE_COLLECTION] → Portfolio
[RESOURCE_ITEM] → Position
[USER_ROLE] → Trader / Portfolio Manager
[TRANSACTION] → Trade
[REGULATORY_REQUIREMENT] → SEC Rule 15c3-5
```

**Software/SaaS**:
```
[RESOURCE_COLLECTION] → Workspace
[RESOURCE_ITEM] → Resource
[USER_ROLE] → Account Admin / Member
[TRANSACTION] → API Call
[REGULATORY_REQUIREMENT] → SOC2 Control
```

**Generic**:
```
[RESOURCE_COLLECTION] → Collection
[RESOURCE_ITEM] → Entity
[USER_ROLE] → User
[TRANSACTION] → Action
[REGULATORY_REQUIREMENT] → Company Policy
```

---

### Step 4: Template Copying (Optional)

**Purpose**: Copy framework templates to project (optional step)

**Commands**:
```bash
# Create framework directory for framework templates
mkdir -p framework

# Copy the layer templates (if framework templates exist)
cp -r {framework_root}/framework/layers framework/
```

**Directory Purpose**:
- `framework/` = Framework spec and layer templates (`layers/01_BRD/BRD-TEMPLATE.yaml`, etc.)
- `docs/` = Project documentation (`01_BRD/BRD-01.yaml`, `02_PRD/PRD-01.yaml`, etc.)

**Note**: This step is optional. Templates can also be referenced directly from the framework location. The framework is spec-only — validation is performed by the doc-* skills against the declarative checks in `framework/governance/` and each layer `README.md`, not by runtime scripts.

---

### Step 5: Index File Initialization + Document Control

**Purpose**: Create index files for each document type

**Document Control Requirements**:
All AI Dev Flow templates include a Document Control section with:
- Project metadata (name, version, date, owner, preparer, status)
- Document Revision History table
- Essential for traceability, change management, and regulatory compliance

**AI Assistant Must Emphasize**:
When creating documents from templates, users must complete the Document Control section with all required fields.

**Commands**:
```bash
# Create index files (Layers 1-7 use .md indices; IPLAN uses .yaml)
touch docs/01_BRD/BRD-00_index.md
touch docs/02_PRD/PRD-00_index.md
touch docs/03_EARS/EARS-00_index.md
touch docs/04_BDD/BDD-00_index.md
touch docs/05_ADR/ADR-00_index.md
touch docs/06_SPEC/SPEC-00_index.md
touch docs/07_TDD/TDD-00_index.md
touch docs/08_IPLAN/IPLAN-00_index.yaml
```

**Index File Purpose**:
- Track all documents of each type
- Provide next available ID
- Document registry with status

---

### Step 6: Validation

**Purpose**: Verify setup complete and correct

**Validation Commands**:
```bash
# Verify directory structure
ls -laR docs/

# Verify index files exist
ls docs/*/index.* || ls docs/*/*_index.*

# Expected: 8 artifact directories (BRD through IPLAN) + domain subdirectories
# Expected: 8 index files
```

**Success Criteria**:
- ✅ All 8 artifact directories exist (01_BRD, 02_PRD, 03_EARS, 04_BDD, 05_ADR, 06_SPEC, 07_TDD, 08_IPLAN)
- ✅ Domain-specific subdirectories exist (risk/, trading/, tenant/, etc.)
- ✅ All index files created
- ✅ All templates include Document Control sections
- ✅ plans directory exists (for /save-plan command)

**Error Handling**:
- If folders missing: Re-run Step 2
- If index files missing: Re-run Step 5
- If domain subdirs missing: Check Step 1 domain selection

---

### Step 7: Project Ready - Hand-off to doc-flow

**AI Assistant Confirmation Message**:

```
═══════════════════════════════════════════════════════════
              PROJECT INITIALIZATION COMPLETE
═══════════════════════════════════════════════════════════

✓ Domain: [Financial Services / Software/SaaS / etc.]
✓ Folders: Created (8 artifact directories + domain subdirectories)
✓ Domain Config: Applied ([PLACEHOLDERS] → [domain terms])
✓ Index Files: Initialized (8 files)
✓ Validation: Passed

Workflow Configuration:
BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code

═══════════════════════════════════════════════════════════
                      NEXT STEPS
═══════════════════════════════════════════════════════════

✅ Project structure ready for development!

Next: Use the `doc-flow` skill to begin workflow execution

Suggested first tasks:
- Create BRD (Business Requirements)
- Create PRD + EARS (Product Requirements)
- Create BDD + ADR (Acceptance Scenarios + Architecture)
- Create SPEC (Technical Specification)
- Create TDD (Test Definitions)
- Create IPLAN (Implementation Plan)

Invoke: doc-flow skill to start with BRD

═══════════════════════════════════════════════════════════
```

---

## Reference Files

All guidance files located in: `{project_root}/framework/`

### Core Guidance Files

1. **[AI_ASSISTANT_RULES.md]({project_root}/framework/AI_ASSISTANT_RULES.md)** - Core execution rules
2. **[DOMAIN_SELECTION_QUESTIONNAIRE.md]({project_root}/framework/DOMAIN_SELECTION_QUESTIONNAIRE.md)** - Domain selection
3. **[SPEC_DRIVEN_DEVELOPMENT_GUIDE.md]({project_root}/framework/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md)** - Master setup and methodology guide
4. **[QUICK_REFERENCE.md]({project_root}/framework/QUICK_REFERENCE.md)** - Quick reference card
5. **[LAYER_REGISTRY.yaml]({project_root}/framework/registry/LAYER_REGISTRY.yaml)** - Authoritative 8-layer definitions

### Domain Configuration Files

8. **[FINANCIAL_DOMAIN_CONFIG.md]({project_root}/framework/FINANCIAL_DOMAIN_CONFIG.md)** - Financial Services (DEFAULT)
9. **[SOFTWARE_DOMAIN_CONFIG.md]({project_root}/framework/SOFTWARE_DOMAIN_CONFIG.md)** - Software/SaaS
10. **[GENERIC_DOMAIN_CONFIG.md]({project_root}/framework/GENERIC_DOMAIN_CONFIG.md)** - Generic/Other

---

## Example Usage

### Example 1: Software Application Project

```
User: "Initialize new software application project"

AI Assistant (using project-init skill):

Step 1: Domain Selection
"What is the purpose and focus of this new project?"

User: "2" (Software/SaaS)

AI Assistant:
✓ Domain selected: Software/SaaS
✓ Loading configuration: SOFTWARE_DOMAIN_CONFIG.md
✓ Domain-specific subdirectories: tenant, subscription, billing, workspace

Step 2: Folder Creation
Creating the 8-layer SDD flow (8 artifact directories)...
✓ Created: docs/01_BRD/
✓ Created: docs/02_PRD/
✓ Created: docs/03_EARS/
✓ Created: docs/04_BDD/
✓ Created: docs/05_ADR/
✓ Created: docs/06_SPEC/
✓ Created: docs/07_TDD/
✓ Created: docs/08_IPLAN/
✓ Created: docs/08_IPLAN/tmp/
✓ Created: docs/06_SPEC/tenant/
✓ Created: docs/06_SPEC/subscription/
✓ Created: docs/06_SPEC/billing/
✓ Created: docs/06_SPEC/workspace/
✓ Created: plans/

Step 3: Domain Configuration
Applying Software/SaaS terminology:
✓ [RESOURCE_COLLECTION] → Workspace
✓ [RESOURCE_ITEM] → Resource
✓ [USER_ROLE] → Account Admin
✓ [REGULATORY_REQUIREMENT] → SOC2 Control

Step 5: Index Files
✓ All 8 index files created

Step 6: Validation
✓ All directories verified
✓ All index files verified

═══════════════════════════════════════════════════════════
              PROJECT INITIALIZATION COMPLETE
═══════════════════════════════════════════════════════════

✓ Domain: Software/SaaS
✓ Folders: Created (8 artifact directories + 4 SaaS subdirectories)
✓ Workflow: BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code

Next: Use `doc-flow` skill to begin workflow execution
Start with: BRD-01 (Business Requirements Document)

═══════════════════════════════════════════════════════════
```

---

### Example 2: Software/SaaS Multi-Tenant Platform

```
User: "Set up new SaaS project for team collaboration platform"

AI Assistant (using project-init skill):

Step 1: Domain Selection
User: "2" (Software/SaaS)

AI Assistant:
✓ Domain selected: Software/SaaS
✓ Loading configuration: SOFTWARE_DOMAIN_CONFIG.md
✓ Domain-specific subdirectories: tenant, subscription, billing, workspace

Step 2: Folder Creation
✓ All core directories created (01_BRD … 08_IPLAN)
✓ SaaS subdirectories created: tenant/, subscription/, billing/, workspace/
✓ Support directories created: plans/

Step 3: Domain Configuration
✓ [RESOURCE_COLLECTION] → Workspace
✓ [RESOURCE_ITEM] → Resource
✓ [USER_ROLE] → Account Admin
✓ [TRANSACTION] → API Call
✓ [REGULATORY_REQUIREMENT] → SOC2 Control

Step 5: Index Files
✓ All 8 index files created
✓ Workflow: BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code

Project Ready!
Next: Use `doc-flow` skill for BRD-01 creation
```

---

## Troubleshooting

### Issue: Directory Already Exists

**Error**: `mkdir: cannot create directory 'docs': File exists`

**Resolution**:
- Project may already be initialized
- Verify: `ls -la docs/`
- If folders exist, skip to doc-flow skill
- If folders incomplete, delete and re-run project-init

### Issue: Permission Denied

**Error**: `mkdir: cannot create directory: Permission denied`

**Resolution**:
- Check current working directory permissions
- Ensure write access to parent directory
- Use `pwd` to verify location

### Issue: Domain Unclear

**User says**: "I'm not sure which domain to choose"

**AI Assistant Action**:
Run follow-up questions from DOMAIN_SELECTION_QUESTIONNAIRE.md:
1. Does project involve financial transactions? → Financial Services
2. Multi-tenant SaaS application? → Software/SaaS
3. Handle patient health information? → Healthcare
4. Online store or marketplace? → E-commerce
5. Connected devices or sensors? → IoT
6. None of above? → Generic

---

## Tool Optimization Notes

### Claude Code
- File limit: 50K tokens (200KB) standard, 100K max
- Strategy: Single comprehensive files
- No artificial splitting needed

### Gemini CLI
- @ reference limit: 10K tokens (40KB)
- Large files: Use file read tool instead of `@`
- Command: `gemini read FILE.md`

### GitHub Copilot
- Optimal: 10-30KB per file
- Large files: Create companion summaries
- Working set: Max 10 files in Edits mode

---

## Related Skills

**After project-init completes, use:**
- **doc-flow** - Main workflow execution skill
  - Create BRD, PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN
  - Follow the 8-layer SDD flow (Layers 1-8: BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code)
  - Generate code from specifications

**Other complementary skills:**
- **mermaid-gen** - Generate Mermaid diagrams
- **charts-flow** - Create architecture diagrams
- **test-automation** - Test suite creation
- **code-review** - Code quality review
- **security-audit** - Security analysis

---

## Quick Reference

**When to use project-init:**
- ✅ Brand new project (no folders exist)
- ✅ Greenfield development
- ✅ Starting from scratch

**When to use doc-flow:**
- ✅ Project already initialized
- ✅ Folders exist (docs/01_BRD/, docs/02_PRD/, etc.)
- ✅ Workflow execution (creating BRD, PRD, SPEC, etc.)

**Workflow sequence:**
```
project-init (Day 0) → doc-flow (Day 1+) → other skills (as needed)
```

---

**End of project-init Skill**
