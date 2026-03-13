# Multi-Project Framework Setup Guide

**Purpose**: Configuration patterns for sharing AI Dev Flow Framework resources across multiple projects

**Scope**: Claude Code skills, commands, agents, templates, and validation scripts

**Last Updated**: 2026-03-12T00:00:00

> **Note**: Examples in this guide use placeholder project paths like `${PROJECT_PATH}/` for illustration purposes. Replace these with your actual project paths (e.g., `${PROJECT_PATH}` or `/path/to/your/project/`).

---

## SDD Depth Selection

This repository provides a **unified SDD framework** with scalable depth:

| Depth | Layers | Best For |
|:------|:-------|:---------|
| **SDD-Lite** | REF → BRD-MVP → PRD-MVP → TASKS | MVPs, prototypes, solo + AI, 1-3 months |
| **SDD-Standard** | + EARS, ADR, SYS, REQ | Production apps, small teams, 3-6 months |
| **SDD-Full** | All 15 layers + 4-Gate CHG | Enterprise, regulated, multi-team, 6+ months |

### Key Directories

| Directory | Purpose |
|:----------|:--------|
| `ai_dev_ssd_flow/` | Layer documentation and templates (BRD, PRD, EARS, ADR, etc.) |
| `governance/` | Project governance, setup guides, scripts, CI/CD templates |
| `governance/shared/` | Shared governance (PR review, branching, releases) |
| `project_knowledge/` | Standalone RAG + Graph knowledge base package |
| `framework_rags/` | Shared RAG tools and reference utilities |

**See**: [governance/SDD_DEPTH_GUIDE.md](./governance/SDD_DEPTH_GUIDE.md) for detailed layer mappings.

---

## Architecture Overview

### Centralized Framework Pattern

```
/opt/data/
├── docs_flow_framework/              # Central framework repository
│   ├── UCX/                          # Unified CLI (Python package)
│   │   ├── ucx/                      # Source code
│   │   │   ├── cli/                  # CLI commands
│   │   │   ├── validators/           # Document validators
│   │   │   │   ├── brd/              # BRD validator (complete)
│   │   │   │   └── common/           # Shared validation utilities
│   │   │   └── api/                  # Review/remediation API
│   │   ├── bin/                      # CLI entry points
│   │   └── docs/                     # UCX documentation
│   │
│   ├── ai_dev_ssd_flow/              # SDD templates (12 layers)
│   │   ├── 01_BRD/                   # Business Requirements
│   │   ├── 02_PRD/                   # Product Requirements
│   │   ├── ...                       # (layers 03-11)
│   │   └── AUTOPILOT/                # Automation scripts
│   │
│   ├── governance/                   # SDD governance templates
│   │   ├── governance/               # PROJECT_PLAN, rules
│   │   ├── templates/                # README, CLAUDE.md
│   │   ├── .github/                  # Workflows, issue templates
│   │   └── docs/                     # ADRs, QA docs
│   │
│   ├── scripts/                      # Validation and automation tools
│   │   └── ucx-validate.sh           # UCX wrapper for all layers
│   ├── project_knowledge/            # Standalone RAG + Graph + MCP package
│   ├── framework_rags/               # Shared rag_tools and reference services
│   ├── .venv/                        # Shared Python virtual environment
│   └── .claude/
│       ├── skills/                   # Shared skills (50+)
│       ├── commands/                 # Shared slash commands
│       └── agents/                   # Shared agent configurations
│
└── projects/
    ├── project_a/                    # Individual projects
    │   ├── .envrc                    # direnv: PYTHONPATH, venv activation
    │   ├── docs/                     # Project artifacts (BRD, ADR, etc.)
    │   ├── src/                      # Source code
    │   ├── ai_dev_flow/              # Symlink → SDD templates (optional)
    │   ├── .templates/
    │   │   ├── ai_dev_ssd_flow/      # Symlink → SDD templates
    │   │   └── governance/           # Symlink → SDD governance
    │   └── .claude/
    │       ├── skills/               # Symlink → shared skills
    │       ├── commands/             # Symlink → shared commands
    │       ├── agents/               # Symlink → shared agents
    │       ├── custom_skills/        # Project-specific skills
    │       └── settings.local.json   # Project configuration
    │
    └── project_b/
        └── [same structure]
```

---

## UCX Framework Integration (Development Mode)

UCX is the unified CLI for document creation, review, and remediation. During active development, use **PYTHONPATH** instead of pip install to always have the latest version.

### Integration Options

| Approach | Up-to-date | Version Control | Best For |
|----------|------------|-----------------|----------|
| **PYTHONPATH + direnv** | ✅ Always | ❌ No pinning | Active development (recommended) |
| **Pip Editable Install** | ✅ Always | ❌ No pinning | Stable development |
| **Pip Install (release)** | ⚠️ On update | ✅ Semver | Production use |

### Option 1: direnv (Recommended for Development)

Create `.envrc` in your project root:

```bash
# /opt/data/your_project/.envrc

# Framework root
export FRAMEWORK_ROOT="/opt/data/docs_flow_framework"

# Add UCX to Python path (no pip install needed)
export PYTHONPATH="$FRAMEWORK_ROOT/UCX:$PYTHONPATH"

# Add UCX bin to PATH for CLI commands
export PATH="$FRAMEWORK_ROOT/UCX/bin:$PATH"

# Use framework's shared virtual environment
source "$FRAMEWORK_ROOT/.venv/bin/activate"

# UCX project root (for config discovery)
export UCX_PROJECT_ROOT="$PWD"
```

Enable for your project:

```bash
cd /opt/data/your_project
direnv allow
```

**Verification**:

```bash
# Test UCX import (no install required)
python -c "from ucx.cli import main; print('UCX available')"

# Test UCX CLI
ucx --version

# Test UCX validate
ucx validate brd docs/01_BRD/ --tier1-only
```

### Option 2: Shell Profile (Global)

Add to `~/.bashrc` or `~/.zshrc`:

```bash
# Framework paths (global availability)
export FRAMEWORK_ROOT="/opt/data/docs_flow_framework"
export PYTHONPATH="$FRAMEWORK_ROOT/UCX:$PYTHONPATH"
export PATH="$FRAMEWORK_ROOT/UCX/bin:$PATH"

# Alias to activate framework venv
alias fw='source $FRAMEWORK_ROOT/.venv/bin/activate'
```

### Option 3: Project Wrapper Script

Create a project-local UCX wrapper:

```bash
#!/bin/bash
# /opt/data/your_project/bin/ucx

FRAMEWORK_ROOT="/opt/data/docs_flow_framework"
PYTHONPATH="$FRAMEWORK_ROOT/UCX:$PYTHONPATH" \
  "$FRAMEWORK_ROOT/.venv/bin/python" -m ucx.cli "$@"
```

Make executable:

```bash
chmod +x /opt/data/your_project/bin/ucx
```

### UCX Commands Available

Once configured, all UCX commands work without installation:

```bash
# Document validation (non-AI)
ucx validate brd docs/01_BRD/BRD-01/ --tier1-only

# AI-powered review
ucx review brd docs/01_BRD/BRD-01/

# AI-powered remediation
ucx remediate docs/01_BRD/BRD-01/

# Scan review report (v1.11.0+)
ucx scan docs/01_BRD/BRD-01.UCR_review_report_v001.md

# List available validators
ucx validate --help
```

### UCX v1.12.0 Category-Weighted Scoring

UCX v1.12.0 introduces category-weighted scoring for more accurate document quality assessment.

**Scoring Categories**:
| Category | ID | Weight | Max Deduction |
|----------|-----|--------|---------------|
| functional | CAT-01 | 25% | -25 |
| quality | CAT-02 | 15% | -15 |
| compliance | CAT-03 | 20% | -20 |
| constraints | CAT-04 | 10% | -10 |
| integration | CAT-05 | 10% | -10 |
| acceptance | CAT-06 | 10% | -10 |
| risk | CAT-07 | 5% | -5 |
| architecture | CAT-08 | 5% | -5 |

**Formula**:
```
raw_deduction = (P0 × 10) + (P1 × 3) + (P2 × 1)
capped_deduction = min(raw_deduction, max_deduction)
weighted_deduction = capped_deduction × category_weight
final_score = 100 - sum(weighted_deduction for each category)
```

**Thresholds**:
| Score | Status | Action |
|-------|--------|--------|
| ≥85 | PASS | PRD-Ready |
| 70-84 | WARN | Needs review |
| <70 | FAIL | Not ready |

**See**: `/opt/data/docs_flow_framework/UCX/docs/scoring/SCORING_GUIDE.md` for complete documentation.

### Project-Specific UCX Configuration (v1.12.0+)

For domain-specific reviews, create project UCX files:

```bash
# Create UCX directory structure
mkdir -p /opt/data/project_name/docs/UCX/{skills,review,creation,remediation}

# Required files for BRD review:
# docs/UCX/skills/           # Domain-specific persona skills
# docs/UCX/review/           # UCR review prompts
# docs/UCX/README.md         # Project UCX configuration
```

**Project UCX Structure** (example from b-local):
```
docs/UCX/
├── README.md                     # Project UCX config (version, commands)
├── skills/                       # Domain-specific persona skills
│   ├── architect.md              # Architecture focus areas
│   ├── auditor.md                # Compliance requirements
│   ├── chairperson.md            # Score calculation, manifest format
│   ├── integration_lead.md       # Partner integrations
│   └── ...                       # Other personas
├── review/
│   ├── UCR_PROMPT_BRD_PROJECT.md # BRD review prompt (all personas)
│   └── UCR_PROMPT_PRD_PROJECT.md # PRD review prompt (all personas)
├── creation/
│   └── UCC_PROMPT_BRD_PROJECT.md # BRD creation prompt
└── remediation/
    └── UCRem_PROMPT_BRD_PROJECT.md # BRD remediation prompt
```

**Key v1.12.0 Requirements**:
1. **Category Tagging**: Chairperson must assign `[CAT:xxx]` tags to findings
2. **Category Summary Table**: Manifest includes per-category scoring breakdown
3. **Weighted Score**: Use category-weighted formula (not legacy 100-P0×10-P1×3-P2×1)
4. **Version Reference**: Set `Requires UCX Framework v1.12.0+` in README.md

**Reference Implementation**: `/opt/data/b-local/b-local-docs/docs/UCX/`

### Pre-commit with UCX (No Install)

Configure pre-commit to use framework UCX:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: ucx-brd-validate
        name: UCX BRD Validation (Tier 1)
        entry: bash -c 'source /opt/data/docs_flow_framework/.venv/bin/activate && PYTHONPATH=/opt/data/docs_flow_framework/UCX:$PYTHONPATH ucx validate brd docs/01_BRD --tier1-only'
        language: system
        files: ^docs/01_BRD/.*\.md$
        stages: [pre-commit]
```

Or use the framework wrapper script:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: ucx-brd-validate
        name: UCX BRD Validation (Tier 1)
        entry: /opt/data/docs_flow_framework/scripts/ucx-validate.sh brd docs/01_BRD --tier1-only
        language: system
        files: ^docs/01_BRD/.*\.md$
        stages: [pre-commit]
```

---

## Hybrid Approach: Shared + Custom Resources

### Principle

Projects use **symlinks** for shared framework resources while maintaining dedicated directories for project-specific customizations.

### Resource Categories

| Resource Type | Shared (Symlink) | Custom (Local) | Discovery Priority |
|---------------|------------------|----------------|-------------------|
| **Skills** | `.claude/skills/` | `.claude/custom_skills/` | Both merged |
| **Commands** | `.claude/commands/` | `.claude/custom_commands/` | Both merged |
| **Agents** | `.claude/agents/` | `.claude/custom_agents/` | Both merged |
| **SDD Templates** | `.templates/ai_dev_ssd_flow/` | N/A | Symlink only |
| **Issues Templates** | `.templates/governance/` | N/A | Symlink only |
| **GitHub CI/CD** | `.github/` (--with-github) | N/A | Optional symlink |
| **Scripts** | `scripts/validate/` | `scripts/` | Both available |
| **Git Hooks Config** | `.pre-commit-config.yaml` (symlink to `pre-commit-config.project.yaml`) | N/A | Symlink per project profile |

---

## Setup Procedures

### 0. Project Knowledge Base Setup (Optional, Shared Runtime)

Use when the project needs retrieval and graph-backed context:

Choose one mode:

- **File-only mode**
    - Store and manage knowledge as files only.
    - No database services, no MCP runtime required.
    - Use this as the default for lightweight/MVP workflows.

- **Indexed mode (RAG + Graph + MCP)**
    - Ingest files into PostgreSQL (`pgvector`) and Neo4j.
    - Enable semantic retrieval and graph relationship queries.
    - Use when the project requires reusable knowledge context across runs.

```bash
cd /opt/data/docs_flow_framework/project_knowledge

# Configure env
cp .env.example .env

# Start PostgreSQL+pgvector and Neo4j
docker compose -f docker-compose.db.yml --env-file .env up -d

# Start MCP server
python -m project_knowledge.mcp.server

# Optional: ingest docs
python project_knowledge/orchestrator.py /path/to/docs --pattern "*.yaml"
```

Core docs:
- `project_knowledge/README.md`
- `project_knowledge/mcp/README.md`

---

### 1. Framework Prerequisites

**Verify framework structure:**
```bash
ls -la /opt/data/docs_flow_framework/.claude/
# Expected: skills/, commands/, agents/

ls -la /opt/data/docs_flow_framework/ai_dev_ssd_flow/
# Expected: BRD/, PRD/, ADR/, REQ/, etc.
```

### 2. Project Setup Script

**Location**: `/opt/data/docs_flow_framework/scripts/setup_project_hybrid.sh`

```bash
#!/bin/bash
# Setup hybrid shared/custom resources for a project

set -e

PROJECT_DIR=$1
FRAMEWORK_DIR="/opt/data/docs_flow_framework"

if [ -z "$PROJECT_DIR" ]; then
    echo "Usage: $0 /opt/data/project_name"
    exit 1
fi

if [ ! -d "$PROJECT_DIR" ]; then
    echo "Error: Project directory does not exist: $PROJECT_DIR"
    exit 1
fi

echo "Setting up hybrid resources for: $PROJECT_DIR"

# Create .claude directory structure
mkdir -p "$PROJECT_DIR/.claude"
mkdir -p "$PROJECT_DIR/.claude/custom_skills"
mkdir -p "$PROJECT_DIR/.claude/custom_commands"
mkdir -p "$PROJECT_DIR/.claude/custom_agents"

# Backup existing resources if not symlinks
backup_if_needed() {
    local target=$1
    if [ -d "$target" ] && [ ! -L "$target" ]; then
        echo "Backing up existing: $target"
        mv "$target" "${target}.backup_$(date +%Y%m%d_%H%M%S)"
    elif [ -L "$target" ]; then
        rm "$target"
    fi
}

# Setup symlinks for shared resources
backup_if_needed "$PROJECT_DIR/.claude/skills"
backup_if_needed "$PROJECT_DIR/.claude/commands"
backup_if_needed "$PROJECT_DIR/.claude/agents"

ln -sf "$FRAMEWORK_DIR/.claude/skills" "$PROJECT_DIR/.claude/skills"
ln -sf "$FRAMEWORK_DIR/.claude/commands" "$PROJECT_DIR/.claude/commands"
ln -sf "$FRAMEWORK_DIR/.claude/agents" "$PROJECT_DIR/.claude/agents"

# Setup template symlinks (BOTH frameworks)
mkdir -p "$PROJECT_DIR/.templates"
backup_if_needed "$PROJECT_DIR/.templates/ai_dev_ssd_flow"
backup_if_needed "$PROJECT_DIR/.templates/governance"
ln -sf "$FRAMEWORK_DIR/ai_dev_ssd_flow" "$PROJECT_DIR/.templates/ai_dev_ssd_flow"
ln -sf "$FRAMEWORK_DIR/governance" "$PROJECT_DIR/.templates/governance"

# Setup validation script symlinks
mkdir -p "$PROJECT_DIR/scripts"
backup_if_needed "$PROJECT_DIR/scripts/validate"
ln -sf "$FRAMEWORK_DIR/scripts" "$PROJECT_DIR/scripts/validate"

# Create .gitignore entries
GITIGNORE="$PROJECT_DIR/.gitignore"
if [ -f "$GITIGNORE" ]; then
    # Add entries if not present
    grep -q "^.claude/skills$" "$GITIGNORE" || echo ".claude/skills" >> "$GITIGNORE"
    grep -q "^.claude/commands$" "$GITIGNORE" || echo ".claude/commands" >> "$GITIGNORE"
    grep -q "^.claude/agents$" "$GITIGNORE" || echo ".claude/agents" >> "$GITIGNORE"
    grep -q "^.templates/$" "$GITIGNORE" || echo ".templates/" >> "$GITIGNORE"
    grep -q "^scripts/validate$" "$GITIGNORE" || echo "scripts/validate" >> "$GITIGNORE"

    # Ensure custom resources are tracked
    grep -q "^!.claude/custom_skills/$" "$GITIGNORE" || echo "!.claude/custom_skills/" >> "$GITIGNORE"
    grep -q "^!.claude/custom_commands/$" "$GITIGNORE" || echo "!.claude/custom_commands/" >> "$GITIGNORE"
    grep -q "^!.claude/settings.local.json$" "$GITIGNORE" || echo "!.claude/settings.local.json" >> "$GITIGNORE"
fi

# Create .envrc for direnv (UCX without pip install)
if [ ! -f "$PROJECT_DIR/.envrc" ]; then
    cat > "$PROJECT_DIR/.envrc" << 'ENVRC'
# Framework root
export FRAMEWORK_ROOT="/opt/data/docs_flow_framework"

# Add UCX to Python path (no pip install needed)
export PYTHONPATH="$FRAMEWORK_ROOT/UCX:$PYTHONPATH"

# Add UCX bin to PATH
export PATH="$FRAMEWORK_ROOT/UCX/bin:$PATH"

# Use framework's shared virtual environment
source "$FRAMEWORK_ROOT/.venv/bin/activate"

# UCX project root (for config discovery)
export UCX_PROJECT_ROOT="$PWD"
ENVRC
    echo "Created .envrc for UCX integration"
fi

# Add .envrc to .gitignore if not present
if [ -f "$GITIGNORE" ]; then
    grep -q "^.envrc$" "$GITIGNORE" || echo ".envrc" >> "$GITIGNORE"
fi

# Verify setup
echo ""
echo "✓ Setup complete. Verifying structure..."
echo ""
echo "Shared resources (symlinks):"
ls -la "$PROJECT_DIR/.claude/" | grep "^l"
echo ""
echo "Custom resources (directories):"
ls -la "$PROJECT_DIR/.claude/" | grep "^d" | grep custom
echo ""
echo "Template access:"
ls -la "$PROJECT_DIR/.templates/"
echo ""
echo "UCX integration (.envrc):"
if [ -f "$PROJECT_DIR/.envrc" ]; then
    echo "  ✓ .envrc created - run 'direnv allow' to activate"
else
    echo "  ⚠ .envrc not created"
fi
```

**Note**: This script creates symlinks for shared resources only. To complete the project setup with documentation folders (`docs/`) and implementation plans folder (`work_plans/`), use:

```bash
# Recommended: Use project-init skill
cd /opt/data/project_name
# In Claude Code: /skill project-init

# OR manually create folder structure
mkdir -p docs/{BRD,PRD,EARS,BDD,ADR,SYS,REQ,IMPL,CTR,SPEC,TASKS}
mkdir -p docs/REQ/{api,auth,data,core,integration,monitoring,reporting,security,ui}
mkdir -p work_plans
mkdir -p scripts

# Setup AI Expert Board
mkdir -p docs/AI_EXPERTS
cp /opt/data/docs_flow_framework/ai_dev_ssd_flow/AI_EXPERTS/review.template.yaml docs/AI_EXPERTS/review.yaml
# Edit docs/AI_EXPERTS/review.yaml to configure the 7 personas for your specific domain.
# Note: The AI Experts team should be created during a new project initialization, or manually on demand later.
# INTEGRATION LEAD (Persona 7): Requires an INTEGRATION_MATRIX.md to work optimally.
#   If missing, the audit script falls back to scanning sibling documents in the same layer
#   for context. This ensures the expert is useful from Day 1 of a project.
```

### 3. Shared Git Hook Library (Symlinked `.pre-commit-config.yaml`)

Use a framework-maintained hook profile and symlink project-level `.pre-commit-config.yaml` to avoid manual mirroring across repositories.

**Framework library location (current profile):**
- `docs_flow_framework/ai_dev_ssd_flow/scripts/pre_commit_hooks/library/pre-commit-config.project.yaml`

**Project symlink example (any project):**

```bash
cd /opt/data/<project-repo>

# Replace local config with symlink to shared library profile
rm -f .pre-commit-config.yaml
ln -s ../../docs_flow_framework/ai_dev_ssd_flow/scripts/pre_commit_hooks/library/pre-commit-config.project.yaml .pre-commit-config.yaml

# Verify target
ls -l .pre-commit-config.yaml
```

**Operational constraints:**
- Symlink target is path-dependent; it requires sibling repo layout under `/opt/data/`.
- If the framework repo path changes, recreate the symlink with the updated relative or absolute target.
- For CI/clones without this shared filesystem layout, use copied config or generate the symlink during bootstrap.

For current `b-local-docs`, `<project-repo>` is `b-local/b-local-docs`.

**Validation:**

```bash
cd /opt/data/<project-repo>
python3 - <<'PY'
import yaml
from pathlib import Path
p = Path('.pre-commit-config.yaml')
print('resolved_to:', p.resolve())
yaml.safe_load(p.read_text())
print('yaml_ok')
PY
```

### 3. Setup Script vs Project-Init Skill

**`setup_project_hybrid.sh`** (Lightweight):
- Creates `.claude/` directory structure
- Creates symlinks to framework skills/agents/commands
- Ideal for: Adding framework to existing projects
- Does NOT create: `docs/` or `work_plans/` directories

**`/skill project-init`** (Full Structure):
- Creates complete documentation structure (`docs/`)
- Creates `work_plans/` directory
- Initializes all 12 artifact directories (BRD through TASKS)
- Ideal for: Starting new projects from scratch
- Includes: Domain selection, contract decision, template customization

**Decision Matrix**:

| Use Case | Recommended Tool |
|----------|------------------|
| Adding framework to existing project | `setup_project_hybrid.sh` |
| Starting brand new project | `/skill project-init` |
| Need docs/ folder structure | `/skill project-init` |
| Only need skills/commands access | `setup_project_hybrid.sh` |

### 4. Single Project Setup

```bash
# Make script executable
chmod +x /opt/data/docs_flow_framework/scripts/setup_project_hybrid.sh

# Setup one project (basic - templates and skills)
/opt/data/docs_flow_framework/scripts/setup_project_hybrid.sh ${PROJECT_PATH}

# Setup with GitHub CI/CD workflows (20 workflows + issue templates)
/opt/data/docs_flow_framework/scripts/setup_project_hybrid.sh ${PROJECT_PATH} --with-github
```

### 5. Bulk Project Setup

```bash
# Setup all projects at once
for PROJECT in [PROJECT_A] [PROJECT_B] [PROJECT_C]; do
    if [ -d "/opt/data/$PROJECT" ]; then
        echo "Setting up: $PROJECT"
        /opt/data/docs_flow_framework/scripts/setup_project_hybrid.sh "/opt/data/$PROJECT"
    fi
done
```

---

## Directory Structure Details

### GitHub CI/CD Resources (--with-github)

When using `--with-github`, the following resources are symlinked:

**Workflows (20)**:

| Category | Workflows |
|----------|-----------|
| **CI/CD** | ci.yml, deploy-dev.yml, deploy-staging.yml, deploy-prod.yml |
| **AI Review** | ai-review.yml, agent-dispatch.yml |
| **Issue Creation** | create-bug-issue.yml, create-deployment-issue.yml, create-qa-testing-issue.yml |
| **Phase Management** | phase-transition.yml, check-phase-completion.yml, check-all-phases-dev.yml |
| **QA** | execute-qa-testing.yml |
| **Project Mgmt** | auto-add-to-project.yml, issue-label-sync.yml, pr-merge-cleanup.yml |
| **Operations** | release.yml, rollback-prod.yml |
| **SDD** | mvp-docs-generation.yml, test-pipeline.yml |

**Issue Templates (10)**: architecture_proposal, bug_report, cost_analysis, development_issue, feature_request, infra_task, mcp_server, research_task, security_report

**Config Files**: CODEOWNERS, dependabot.yml, labeler.yml, PULL_REQUEST_TEMPLATE.md

### Complete Project Layout

```
/opt/data/project_name/
├── .envrc                           # direnv config (UCX PYTHONPATH, venv)
├── .claude/
│   ├── skills/                      # Symlink → framework shared skills
│   ├── commands/                    # Symlink → framework shared commands
│   ├── agents/                      # Symlink → framework shared agents
│   ├── custom_skills/               # Project-specific skills
│   │   └── example_skill/
│   │       └── SKILL.md
│   ├── custom_commands/             # Project-specific commands
│   │   └── project_command.md
│   ├── custom_agents/               # Project-specific agents
│   │   └── project_agent.json
│   ├── settings.local.json          # Project configuration
│   └── CLAUDE.md                    # Project instructions (optional)
│
├── .github/                         # Optional: with --with-github flag
│   ├── workflows/                   # 20 CI/CD workflows
│   ├── ISSUE_TEMPLATE/              # 10 issue templates
│   ├── CODEOWNERS
│   ├── dependabot.yml
│   ├── labeler.yml
│   └── PULL_REQUEST_TEMPLATE.md
│
├── .templates/
│   ├── ai_dev_ssd_flow/             # Symlink → SDD templates (12 layers)
│   └── governance/                  # Symlink → SDD governance templates
│
├── ai_dev_flow/                     # Optional: Symlink → SDD templates (convenience)
│
├── docs/                            # Project artifacts (auto-created by project-init)
│   ├── 01_BRD/
│   ├── 02_PRD/
│   ├── 05_ADR/
│   ├── 07_REQ/
│   └── generated/
│       └── matrices/
│
├── work_plans/                      # Implementation plans (auto-created by project-init)
│   └── PLAN-001_*.md
│
├── scripts/
│   ├── validate/                    # Symlink → framework scripts
│   └── project_specific.sh          # Project scripts
│
├── src/                             # Source code
├── tests/                           # Test suite (aligned with TSPEC L10)
│   ├── unit/                        # UTEST - Unit tests
│   ├── integration/                 # ITEST - Integration tests
│   ├── smoke/                       # STEST - Smoke tests
│   └── functional/                  # FTEST - Functional tests
└── .gitignore                       # Exclude symlinks, include custom
```

---

## Resource Discovery Behavior

### Skills Discovery

Claude Code searches multiple locations and merges results:

```
Priority 1: .claude/custom_skills/     # Project-specific (highest)
Priority 2: .claude/skills/            # Shared framework
```

**Example:**
- Framework skill: `.claude/skills/doc-flow/` → Available
- Custom skill: `.claude/custom_skills/ib-api-helper/` → Available
- Both accessible via `/skill` command

### Commands Discovery

```
Priority 1: .claude/custom_commands/   # Project-specific
Priority 2: .claude/commands/          # Shared framework
```

**Example:**
- Framework command: `/save-plan` → Available
- Custom command: `/ib-connect` → Available

### Agents Discovery

```
Priority 1: .claude/custom_agents/     # Project-specific
Priority 2: .claude/agents/            # Shared framework
```

---

## Creating Custom Resources

### Custom Skill Example

**Location**: `${PROJECT_PATH}/.claude/custom_skills/project-helper/SKILL.md`

```markdown
# Custom Project Skill

**Purpose**: Project-specific data connection and validation utilities

**Scope**: Project-specific skill for [PROJECT_NAME]

## Prompt

You are a project specialist...

[Skill content]
```

**Access:**
```bash
# Available only in this project
/skill project-helper
```

### Custom Command Example

**Location**: `${PROJECT_PATH}/.claude/custom_commands/service-connect.md`

```markdown
Test service connection and report status with diagnostics
```

**Access:**
```bash
# Available only in this project
/service-connect
```

### Custom Agent Example

**Location**: `${PROJECT_PATH}/.claude/custom_agents/service_tester.json`

```json
{
  "name": "service_tester",
  "description": "Test service connections",
  "systemPrompt": "You are a service testing specialist..."
}
```

---

## Configuration Management

### Project Settings

**Location**: `/opt/data/project_name/.claude/settings.local.json`

```json
{
  "workingDirectory": "${PROJECT_PATH}",
  "docFlowPath": "docs/",
  "workPlansPath": "work_plans/",
  "frameworkPath": "/opt/data/docs_flow_framework",
  "projectType": "mcp_server",
  "traceabilityEnabled": true
}
```

### Project Instructions

**Location**: `/opt/data/project_name/.claude/CLAUDE.md` (optional)

```markdown
# Project: [PROJECT_NAME]

**Active Framework**: /opt/data/docs_flow_framework
**Templates**: .templates/ai_dev_ssd_flow/
**Work Plans**: work_plans/

## Project-Specific Rules

- Follow project-specific terminology
- Document all API method signatures
- Include error codes in documentation

## Active Documents

- BRD-001: Core project functionality
- BRD-002: Data processing features
- ADR-001: Implementation technology decision
```

---

## Version Control Configuration

### .gitignore Template

Add to each project's `.gitignore`:

```gitignore
# Environment configuration (machine-specific paths)
.envrc

# Shared framework resources (symlinks - do not commit)
.claude/skills
.claude/commands
.claude/agents
.templates/ai_dev_ssd_flow
.templates/governance
ai_dev_flow
scripts/validate

# Keep project-specific resources (commit these)
!.claude/custom_skills/
!.claude/custom_commands/
!.claude/custom_agents/
!.claude/settings.local.json
!.claude/CLAUDE.md

# Keep actual documentation artifacts
!docs/
!work_plans/
!scripts/*.sh
!scripts/*.py
```

### Framework .gitignore

Add to `/opt/data/docs_flow_framework/.gitignore`:

```gitignore
# Framework should commit its resources
# Nothing to ignore for shared resources
```

---

## Maintenance Procedures

### Updating Shared Skills

```bash
# Edit framework skill
vim /opt/data/docs_flow_framework/.claude/skills/doc-flow/SKILL.md

# Changes immediately available to all projects (symlinks)
# No sync required
```

### Updating Framework Templates

```bash
# Edit SDD framework template
vim /opt/data/docs_flow_framework/ai_dev_ssd_flow/01_BRD/BRD-MVP-TEMPLATE.md

# Edit SDD governance framework template
vim /opt/data/docs_flow_framework/governance/PROJECT_PLAN.md

# Changes immediately available to all projects
```

### Adding New Framework Skills

```bash
# Create new skill in framework
mkdir /opt/data/docs_flow_framework/.claude/skills/new-skill
vim /opt/data/docs_flow_framework/.claude/skills/new-skill/SKILL.md

# Automatically available to all projects via symlink
```

### Migrating Custom Skill to Shared

```bash
# If a project-specific skill proves useful across projects:

# 1. Copy from project to framework
cp -r ${PROJECT_PATH}/.claude/custom_skills/useful-skill \
      /opt/data/docs_flow_framework/.claude/skills/

# 2. Remove from project custom
rm -rf ${PROJECT_PATH}/.claude/custom_skills/useful-skill

# 3. Now available to all projects via shared symlink
```

---

## Validation and Testing

### Verify Setup

```bash
# Check symlinks are valid
ls -la ${PROJECT_PATH}/.claude/
# Should show: skills -> /opt/data/docs_flow_framework/.claude/skills

# Test skill discovery
cd ${PROJECT_PATH}
# In Claude Code session:
# /skill doc-flow  # Should work (shared)
# /skill ib-api-helper  # Should work (custom, if exists)

# Verify SDD template access
ls -la ${PROJECT_PATH}/.templates/ai_dev_ssd_flow/01_BRD/
# Should list: BRD-MVP-TEMPLATE.md, etc.

# Verify SDD governance template access
ls -la ${PROJECT_PATH}/.templates/governance/
# Should list: PROJECT_PLAN.md, GOVERNANCE_RULES.md, etc.
```

### Troubleshooting

**Issue: Symlink broken**
```bash
# Check target exists
ls -la /opt/data/docs_flow_framework/.claude/skills/
# If missing, framework not properly set up

# Recreate symlink
cd /opt/data/project_name/.claude
rm skills
ln -s /opt/data/docs_flow_framework/.claude/skills skills
```

**Issue: Custom skill not discovered**
```bash
# Verify directory structure
ls -la /opt/data/project_name/.claude/custom_skills/skill_name/
# Must contain SKILL.md

# Check file permissions
chmod 644 /opt/data/project_name/.claude/custom_skills/skill_name/SKILL.md
```

---

## Migration from Copied Skills

### Assessment

```bash
# Identify projects with copied skills
for PROJECT in /opt/data/*/; do
    if [ -d "$PROJECT/.claude/skills" ] && [ ! -L "$PROJECT/.claude/skills" ]; then
        echo "Has copied skills: $PROJECT"
        du -sh "$PROJECT/.claude/skills"
    fi
done
```

### Migration Steps

```bash
# For each project with copied skills:

# 1. Backup existing skills
cd /opt/data/project_name/.claude
mv skills skills.backup_20251113

# 2. Identify project-specific skills
diff -r skills.backup_20251113 /opt/data/docs_flow_framework/.claude/skills
# Any differences = project-specific

# 3. Extract project-specific skills
mkdir custom_skills
mv skills.backup_20251113/project_specific_skill custom_skills/

# 4. Create symlink to shared
ln -s /opt/data/docs_flow_framework/.claude/skills skills

# 5. Test
# Verify both shared and custom skills are accessible

# 6. Remove backup after verification
rm -rf skills.backup_20251113
```

---

## Performance Considerations

### Symlink Performance

- **Read operations**: Identical to direct files (kernel-level resolution)
- **Write operations**: Not applicable (read-only usage)
- **Discovery overhead**: Negligible (<1ms for directory traversal)
- **Network impact**: Zero (local filesystem only)

### Storage Savings

**Before** (copied skills):
- 5 projects × 50MB skills = 250MB total

**After** (symlinked skills):
- 1 framework × 50MB skills = 50MB total
- 5 projects × 1KB symlinks = 5KB total
- **Total savings**: 200MB (80% reduction)

---

## Security Considerations

### Access Control

**Framework directory**:
- Permissions: `755` (read/execute for all users)
- Ownership: Controlled by framework maintainer
- Modification: Requires write access to framework

**Project directories**:
- Permissions: `755` for shared symlinks
- Permissions: `755` for custom resources
- Ownership: Project-specific

### Isolation

**Symlinks provide read-only access**:
- Projects cannot modify shared framework resources
- Framework changes require explicit access to framework directory
- Custom resources remain project-isolated

---

## Use Cases

### Use Case 1: Greenfield Project (SDD)

**Scenario**: Starting new large project with full SDD methodology

```bash
# 1. Create project root directory
mkdir -p /opt/data/new_project

# 2. Setup hybrid resources (symlinks to BOTH frameworks)
/opt/data/docs_flow_framework/scripts/setup_project_hybrid.sh /opt/data/new_project

# 3. Create SDD project structure (docs, work_plans, src, tests)
cd /opt/data/new_project
# Use /skill project-init for full structure
# OR manually:
mkdir -p docs/{BRD,PRD,EARS,BDD,ADR,SYS,REQ,IMPL,CTR,SPEC,TASKS}
mkdir -p work_plans
mkdir -p src tests

# 4. Result: Complete project setup with SDD framework access
# Access templates: .templates/ai_dev_ssd_flow/
```

### Use Case 1b: Greenfield Project (SDD governance)

**Scenario**: Starting new small-medium project with lightweight governance

```bash
# 1. Create project root directory
mkdir -p /opt/data/new_project

# 2. Setup hybrid resources (symlinks to BOTH frameworks)
/opt/data/docs_flow_framework/scripts/setup_project_hybrid.sh /opt/data/new_project

# 3. Copy SDD governance structure
cd /opt/data/new_project
cp -r .templates/governance/.github .
cp .templates/governance/PROJECT_PLAN.md docs/
cp .templates/governance/GOVERNANCE_RULES.md docs/
mkdir -p docs/adr docs/qa

# 4. Result: Project with CI/CD and governance templates
# Access templates: .templates/governance/
```

### Use Case 2: Existing Project Migration

**Scenario**: Project has copied skills, needs to migrate

```bash
# 1. Backup existing
cd /opt/data/existing_project/.claude
cp -r skills skills.backup

# 2. Run setup (handles migration)
/opt/data/docs_flow_framework/scripts/setup_project_hybrid.sh /opt/data/existing_project

# 3. Extract custom skills
# [Manual step: identify and move project-specific skills]
```

### Use Case 3: Framework Skill Development

**Scenario**: Developing new skill that will be shared

```bash
# 1. Create in framework (not project)
mkdir /opt/data/docs_flow_framework/.claude/skills/new-feature
vim /opt/data/docs_flow_framework/.claude/skills/new-feature/SKILL.md

# 2. Test in any project (immediately available via symlink)
cd ${PROJECT_PATH}
# Use /skill new-feature

# 3. Iterate (edit framework skill, test in project)
```

### Use Case 4: Project-Specific Skill

**Scenario**: Skill relevant only to one project

```bash
# 1. Create in project custom directory
mkdir ${PROJECT_PATH}/.claude/custom_skills/project-validator
vim ${PROJECT_PATH}/.claude/custom_skills/project-validator/SKILL.md

# 2. Commit to project repository
cd ${PROJECT_PATH}
git add .claude/custom_skills/project-validator/
git commit -m "Add project-specific validation skill"

# 3. Not available in other projects (intentionally isolated)
```

---

## Rollback Procedures

### Revert to Copied Skills

If symlink approach proves problematic:

```bash
# 1. Copy framework skills to project
cp -r /opt/data/docs_flow_framework/.claude/skills /opt/data/project_name/.claude/skills.new

# 2. Remove symlink
rm /opt/data/project_name/.claude/skills

# 3. Rename copied skills
mv /opt/data/project_name/.claude/skills.new /opt/data/project_name/.claude/skills

# 4. Update .gitignore (remove symlink exclusion)
# Now commit skills directory
```

---

## References

### Related Documentation

- [AI Dev Flow Framework README](./README.md) - Framework overview

**SDD Framework (ai_dev_ssd_flow)**:
- [SDD Methodology Guide](./ai_dev_ssd_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - 12-layer workflow
- [ID Naming Standards](./ai_dev_ssd_flow/ID_NAMING_STANDARDS.md) - Document naming conventions
- [Traceability Setup](./ai_dev_ssd_flow/TRACEABILITY_SETUP.md) - Tag-based traceability

**SDD Governance Framework (governance)**:
- [SDD governance README](./governance/README.md) - Lightweight governance overview
- [Setup Guide](./governance/SETUP_GUIDE.md) - Quick start
- [Governance Rules](./governance/GOVERNANCE_RULES.md) - Operational rules

### External Resources

- Claude Code Skills Documentation: https://docs.claude.com/claude-code/skills
- Symlink best practices: `man ln`
- Git symlink handling: https://git-scm.com/docs/git-add#_symbolic_links

---

## Changelog

### Version 2.3 (2026-03-12)

- **UCX v1.12.0 Category-Weighted Scoring**: Added documentation for new scoring system
  - 8 scoring categories with per-category weights and caps
  - Category tagging with `[CAT:xxx]` format
  - Per-category deduction caps to prevent runaway scores
  - Updated thresholds: PASS (≥85), WARN (70-84), FAIL (<70)
- **Project-Specific UCX Configuration**: Added section for setting up project UCX files
  - Directory structure for skills, prompts, and remediation
  - Key v1.12.0 requirements for category tagging
  - Reference to b-local implementation example
- Added `ucx scan` command to UCX commands documentation

### Version 2.2 (2026-03-11)

- **UCX Framework Integration**: Added comprehensive section for UCX development mode
  - PYTHONPATH-based integration (no pip install required)
  - direnv `.envrc` configuration for automatic environment setup
  - Pre-commit hook configuration with UCX
  - Three integration options: direnv, shell profile, wrapper script
- Updated architecture diagram to include UCX package structure
- Updated setup script to auto-generate `.envrc` file
- Updated project layout to include `.envrc` and `ai_dev_flow/` symlink
- Added UCX CLI commands documentation

### Version 2.1 (2026-02-17T00:00:00)

- **Dual Framework Support**: Added `governance` alongside `ai_dev_ssd_flow`
- Updated setup script to symlink BOTH framework template directories
- Added framework selection decision matrix
- Added Use Case 1b for SDD governance greenfield projects
- Updated directory structure diagrams to show both templates
- Updated .gitignore patterns for dual framework symlinks
- Updated all template path references to use numbered layer directories

### Version 2.0 (2026-02-07T00:00:00)

- Updated for Autopilot v6.0 integration
- Added TSPEC (Layer 10) test specification support
- Added TDD workflow mode references
- Added CHG change management integration
- Updated project structure with tests/ directory
- Added Autopilot v6.0 quick start section to quick reference

### Version 1.0 (2025-11-13T00:00:00)

- Initial hybrid approach documentation
- Setup script for shared/custom resource pattern
- Migration procedures from copied skills
- Validation and troubleshooting guides
- Use cases and rollback procedures

---

**Maintained by**: Framework Administrator
**Contact**: See framework repository for issues and contributions
