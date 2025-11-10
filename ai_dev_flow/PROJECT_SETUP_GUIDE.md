# Project Setup Guide

**Version**: 1.1
**Purpose**: Master initialization guide for AI Assistants to set up new projects
**Target**: AI Coding Assistants (Claude AI, Claude Code, Gemini CLI, GitHub Copilot)
**Status**: Production

---

## Quick Start Overview

This guide walks AI Assistants through initializing a brand new project using the AI Dev Flow framework. Follow these steps in order.

### 🚀 Using the project-init Skill (Recommended)

**For Claude Code Users**: The easiest way to initialize a new project is to use the **`project-init` skill**, which automates this entire guide:

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
1. Invoke: `project-init` skill (in Claude Code)
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
✓ Domain-specific subdirectories: risk, trading, portfolio, compliance, ml
```

---

### Step 2: Folder Structure Creation (REQUIRED SECOND)

**AI Assistant Action**: Create complete directory structure BEFORE creating any documents

**Commands**:
```bash
# Core 10-layer directory structure (ALL PROJECTS)
mkdir -p docs/BRD docs/PRD docs/EARS docs/BDD docs/ADR docs/SYS docs/REQ docs/IMPL docs/CONTRACTS docs/SPEC docs/TASKS

# Standard requirements subdirectories (ALL PROJECTS)
mkdir -p docs/REQ/api docs/REQ/auth docs/REQ/data docs/REQ/core docs/REQ/integration docs/REQ/monitoring docs/REQ/reporting docs/REQ/security docs/REQ/ui

# Domain-specific subdirectories (based on Step 1 selection)
# Financial Services:
mkdir -p docs/REQ/risk docs/REQ/trading docs/REQ/portfolio docs/REQ/compliance docs/REQ/ml

# Software/SaaS:
mkdir -p docs/REQ/tenant docs/REQ/subscription docs/REQ/billing docs/REQ/workspace

# Support directories
mkdir -p scripts
mkdir -p work_plans
```

**Validation**:
```bash
ls -la docs/  # Verify 11 directories created
ls -la docs/REQ/  # Verify subdirectories
ls -la work_plans/  # Verify work_plans directory
```

**Output**: Complete folder structure ready

---

### Step 3: Template Copying

**AI Assistant Action**: Copy framework templates to project

**Commands**:
```bash
# Copy all templates
cp -r /opt/data/docs_flow_framework/ai_dev_flow/docs_templates/* docs/

# Copy validation scripts
cp /opt/data/docs_flow_framework/ai_dev_flow/scripts/*.py scripts/
```

---

### Step 4: Domain Configuration Application

**AI Assistant Action**: Apply domain-specific placeholder replacements

**Financial Services Example**:
```bash
find docs/ -type f -name "*.md" -exec sed -i \
  -e 's/\[RESOURCE_COLLECTION\]/Portfolio/g' \
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

- **With CTR**: `REQ → IMPL → CTR → SPEC → TASKS`
- **Without CTR**: `REQ → IMPL → SPEC → TASKS`

---

### Step 6: Index File Initialization

**AI Assistant Action**: Create index files for each document type

**Commands**:
```bash
# Create index files
touch docs/BRD/BRD-000_index.md
touch docs/PRD/PRD-000_index.md
touch docs/EARS/EARS-000_index.md
touch docs/BDD/BDD-000_index.feature
touch docs/ADR/ADR-000_index.md
touch docs/SYS/SYS-000_index.md
touch docs/REQ/REQ-000_index.md
touch docs/IMPL/IMPL-000_index.md
touch docs/CONTRACTS/CTR-000_index.md
touch docs/SPEC/SPEC-000_index.yaml
touch docs/TASKS/TASKS-000_index.md
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
- All 11 core directories exist
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
✓ Folders: Created (11 core + domain subdirectories)
✓ Templates: Copied and customized
✓ Contracts: Included (CTR layer active)
✓ Index Files: Initialized
✓ Scripts: Ready

Workflow: BRD → PRD → EARS → BDD → ADR → SYS → REQ → IMPL → CTR → SPEC → TASKS → Code

Next Steps:
1. Use `doc-flow` skill to begin workflow execution (recommended)
2. Or manually review [PROJECT_KICKOFF_TASKS.md](./PROJECT_KICKOFF_TASKS.md) for Day 1-7 tasks
3. Start with BRD-001 (Business Requirements Document)
4. Follow 10-layer workflow sequentially

═══════════════════════════════════════════════════════════
```

---

## Complete Example: Financial Services Trading Platform

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
✓ Domain-specific subdirectories: risk, trading, portfolio, compliance, ml

Creating folder structure...
✓ Created: docs/BRD/
✓ Created: docs/PRD/
✓ Created: docs/EARS/
✓ Created: docs/BDD/
✓ Created: docs/ADR/
✓ Created: docs/SYS/
✓ Created: docs/REQ/
✓ Created: docs/IMPL/
✓ Created: docs/CONTRACTS/
✓ Created: docs/SPEC/
✓ Created: docs/TASKS/

✓ Created: docs/REQ/api/
✓ Created: docs/REQ/auth/
✓ Created: docs/REQ/data/
✓ Created: docs/REQ/risk/
✓ Created: docs/REQ/trading/
✓ Created: docs/REQ/portfolio/
✓ Created: docs/REQ/compliance/
✓ Created: docs/REQ/ml/

✓ Created: scripts/
✓ Created: work_plans/

Copying templates...
✓ Templates copied from framework

Applying Financial Services domain configuration...
✓ [RESOURCE_COLLECTION] → Portfolio
✓ [RESOURCE_ITEM] → Position
✓ [USER_ROLE] → Trader
✓ [REGULATORY_REQUIREMENT] → SEC Rule 15c3-5

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
✓ Workflow: REQ → IMPL → CTR → SPEC → TASKS

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

**Issue**: `cp: cannot stat '/opt/data/docs_flow_framework/ai_dev_flow/docs_templates/*': No such file or directory`

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
mkdir -p docs/{BRD,PRD,EARS,BDD,ADR,SYS,REQ,IMPL,CONTRACTS,SPEC,TASKS}
mkdir -p docs/REQ/{api,auth,data,core,integration,monitoring,reporting,security,ui}
mkdir -p scripts work_plans
# Add domain-specific subdirectories based on Step 1

# Step 3: Copy Templates
cp -r /opt/data/docs_flow_framework/ai_dev_flow/docs_templates/* docs/
cp /opt/data/docs_flow_framework/ai_dev_flow/scripts/*.py scripts/

# Step 4: Apply Domain Config
# Run placeholder replacement based on domain selection

# Step 5: Contract Decision (interactive)
# AI Assistant runs CONTRACT_DECISION_QUESTIONNAIRE.md

# Step 6: Initialize Index Files
for type in BRD PRD EARS BDD ADR SYS REQ IMPL CONTRACTS SPEC TASKS; do
  touch docs/$type/*_index.*
done

# Step 7: Validate
ls -laR docs/
```

---

## Relationship to project-init Skill

### For AI Assistants in Claude Code

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

- **project-init** skill - Automates this guide (Claude Code)
- **doc-flow** skill - Workflow execution after initialization

---

## End of Project Setup Guide
