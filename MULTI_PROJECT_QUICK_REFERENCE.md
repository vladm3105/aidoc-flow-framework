# Multi-Project Setup - Quick Reference

**Quick commands for managing AI Dev Flow Framework across multiple projects**

---

## SDD Depth Options

| Depth | Use Case | Layers |
|:------|:---------|:-------|
| **SDD-Lite** | MVPs, prototypes, solo + AI | REF → BRD-MVP → PRD-MVP → TASKS |
| **SDD-Standard** | Production apps, small teams | + EARS, ADR, SYS, REQ |
| **SDD-Full** | Enterprise, regulated, multi-team | All 15 layers + 4-Gate CHG |

---

## Project Knowledge Base (RAG + Graph)

Use the standalone package in this framework:

### Option A: File-only mode (no DB runtime)

Use direct file workflows when retrieval/indexing is not required.

```bash
# Keep knowledge in docs/ (or project-specific folders)
# Use regular file search/read workflows
# No project_knowledge DB or MCP startup required
```

### Option B: Indexed mode (RAG + Graph + MCP)

Use this mode when you need semantic retrieval, graph context, and reusable knowledge tools.

Optional alternative: use `framework_rags` as a shared RAG runtime instead of built-in project RAG when needed (see `framework_rags/README.md`).

```bash
cd /opt/data/docs_flow_framework/project_knowledge

# 1) Configure environment
cp .env.example .env

# 2) Start databases
docker compose -f docker-compose.db.yml --env-file .env up -d

# 3) Start MCP server
python -m project_knowledge.mcp.server

# 4) Ingest documents
python project_knowledge/orchestrator.py /path/to/docs --pattern "*.yaml"

# 5) Run pilot validation
python project_knowledge/scripts/pilot_validate.py
```

---

## Setup New Project

```bash
# Setup hybrid shared/custom resources (BOTH frameworks)
/opt/data/docs_flow_framework/scripts/setup_project_hybrid.sh /opt/data/project_name

# With GitHub CI/CD workflows and issue templates
/opt/data/docs_flow_framework/scripts/setup_project_hybrid.sh /opt/data/project_name --with-github

# What it does:
# ✓ Creates .claude/custom_skills/, custom_commands/, custom_agents/
# ✓ Symlinks .claude/skills/ → framework
# ✓ Symlinks .claude/commands/ → framework
# ✓ Symlinks .claude/agents/ → framework
# ✓ Symlinks .templates/ai_dev_ssd_flow/ → SDD layer templates (15 layers)
# ✓ Symlinks .templates/governance/ → SDD governance templates
# ✓ Symlinks scripts/validate/ → framework scripts
# ✓ Configures .gitignore
#
# With --with-github flag:
# ✓ Symlinks .github/ → framework (20 workflows, 10 issue templates)
#
# IMPORTANT: This creates symlinks only
# To complete project setup (create docs/, work_plans/, etc.):
# → Use: /skill project-init (recommended)
# → OR manually: mkdir -p docs/{BRD,PRD,...} work_plans scripts
#
# Initialize AI Expert Board:
# → mkdir -p docs/AI_EXPERTS
# → Copy ai_dev_ssd_flow/AI_EXPERTS/review.template.yaml to docs/AI_EXPERTS/review.yaml
# → This team should be created during new project initialization or manually on demand later.
```

---

## Setup Multiple Projects

```bash
# Batch setup
for PROJECT in [PROJECT_A] [PROJECT_B] [PROJECT_C]; do
    /opt/data/docs_flow_framework/scripts/setup_project_hybrid.sh /opt/data/$PROJECT
done
```

---

## UCX Framework (Development Mode)

UCX is the unified CLI for document creation, review, and remediation. Use PYTHONPATH instead of pip install during development.

### Quick Setup with direnv

```bash
# Create .envrc in your project
cat > /opt/data/project_name/.envrc << 'EOF'
export FRAMEWORK_ROOT="/opt/data/docs_flow_framework"
export PYTHONPATH="$FRAMEWORK_ROOT/UCX:$PYTHONPATH"
export PATH="$FRAMEWORK_ROOT/UCX/bin:$PATH"
source "$FRAMEWORK_ROOT/.venv/bin/activate"
export UCX_PROJECT_ROOT="$PWD"
EOF

# Enable direnv
cd /opt/data/project_name
direnv allow
```

### UCX Commands

```bash
# Validate BRD (non-AI, fast)
ucx validate brd docs/01_BRD/ --tier1-only

# AI-powered review
ucx review brd docs/01_BRD/BRD-01/

# AI-powered remediation
ucx remediate docs/01_BRD/BRD-01/

# Scan review report (v1.11.0+)
ucx scan docs/01_BRD/BRD-01.UCR_review_report_v001.md

# Check version
ucx --version
```

### UCX v1.12.0 Category-Weighted Scoring

| Category | Weight | Max Deduction |
|----------|--------|---------------|
| functional | 25% | -25 |
| compliance | 20% | -20 |
| quality | 15% | -15 |
| constraints | 10% | -10 |
| integration | 10% | -10 |
| acceptance | 10% | -10 |
| risk | 5% | -5 |
| architecture | 5% | -5 |

**Thresholds**: PASS (≥85), WARN (70-84), FAIL (<70)

**Category Tags**: Chairperson assigns `[CAT:xxx]` to each finding

### Project-Specific UCX Setup (v1.12.0)

```bash
# Create project UCX structure
mkdir -p docs/UCX/{skills,review,creation,remediation}

# Required for domain-specific reviews:
# docs/UCX/skills/*.md        # Persona skills (architect, auditor, etc.)
# docs/UCX/review/*.md        # UCR review prompts
# docs/UCX/README.md          # Project config (version, commands)

# Key v1.12.0 requirements:
# - Chairperson assigns [CAT:xxx] tags to findings
# - Category Summary table in manifest
# - Use category-weighted scoring formula
```

**Reference**: `/opt/data/b-local/b-local-docs/docs/UCX/`

### Pre-commit with UCX

```yaml
# .pre-commit-config.yaml
- id: ucx-brd-validate
  name: UCX BRD Validation
  entry: /opt/data/docs_flow_framework/scripts/ucx-validate.sh brd docs/01_BRD --tier1-only
  language: system
  files: ^docs/01_BRD/.*\.md$
```

---

## Directory Structure After Setup

```
/opt/data/project_name/
├── .envrc                   ✓ UCX environment (direnv)
├── .claude/
│   ├── skills/              → /opt/data/docs_flow_framework/.claude/skills/
│   ├── commands/            → /opt/data/docs_flow_framework/.claude/commands/
│   ├── agents/              → /opt/data/docs_flow_framework/.claude/agents/
│   ├── custom_skills/       ✓ Tracked in git
│   ├── custom_commands/     ✓ Tracked in git
│   ├── custom_agents/       ✓ Tracked in git
│   ├── settings.local.json  ✓ Tracked in git
│   └── CLAUDE.md            ✓ Tracked in git (optional)
│
├── .github/                 → /opt/data/docs_flow_framework/.github/ (with --with-github)
│   ├── workflows/           20 CI/CD workflows
│   ├── ISSUE_TEMPLATE/      10 issue templates
│   ├── CODEOWNERS
│   ├── dependabot.yml
│   └── PULL_REQUEST_TEMPLATE.md
│
├── .templates/
│   ├── ai_dev_ssd_flow/         → /opt/data/docs_flow_framework/ai_dev_ssd_flow/
│   └── governance/  → /opt/data/docs_flow_framework/governance/
│
├── scripts/
│   ├── validate/            → /opt/data/docs_flow_framework/scripts/
│   └── project_*.sh         ✓ Project-specific scripts
│
├── docs/                    ✓ Project documentation artifacts (auto-created by project-init)
├── work_plans/              ✓ Project implementation plans (auto-created by project-init)
└── src/                     ✓ Project source code
```

**Legend:**

- `→` Symlink (not tracked in git, created by setup_project_hybrid.sh)
- `✓` Tracked in git
- **Auto-created folders**: docs/, work_plans/ created by `/skill project-init`

---

## Creating Custom Resources

### Custom Skill

```bash
# Create directory
mkdir -p /opt/data/project_name/.claude/custom_skills/my-skill

# Create skill definition
cat > /opt/data/project_name/.claude/custom_skills/my-skill/SKILL.md << 'EOF'
# My Custom Skill

**Purpose**: Project-specific functionality

## Prompt

You are a specialist in...

[Skill content]
EOF

# Use in project
cd /opt/data/project_name
# In Claude Code: /skill my-skill
```

### Custom Command

```bash
# Create command
cat > /opt/data/project_name/.claude/custom_commands/my-command.md << 'EOF'
Execute project-specific workflow with validation and reporting
EOF

# Use in project
cd /opt/data/project_name
# In Claude Code: /my-command
```

---

## Accessing Resources

### Shared Skills (All Projects)

```bash
# View available shared skills
ls /opt/data/docs_flow_framework/.claude/skills/

# Example skills:
# - doc-flow: SDD workflow
# - trace-check: Traceability validation
# - project-init: Project initialization
# - mermaid-gen: Diagram generation
# - charts_flow: Architecture diagrams
```

### Templates (All Projects)

```bash
# View SDD templates (12 layers - large projects)
ls /opt/data/docs_flow_framework/ai_dev_ssd_flow/

# Template directories:
# 01_BRD/, 02_PRD/, 03_EARS/, 04_BDD/, 05_ADR/, 06_SYS/,
# 07_REQ/, 08_CTR/, 09_SPEC/, 10_TSPEC/, 11_TASKS/, AUTOPILOT/

# View SDD governance templates (lightweight - small projects)
ls /opt/data/docs_flow_framework/governance/

# Key directories:
# governance/ - PROJECT_PLAN, GOVERNANCE_RULES
# templates/ - README, CLAUDE.md, CONTRIBUTING
# .github/ - workflows, issue templates
# docs/ - ADRs, QA docs, core specs
```

### GitHub Workflows (with --with-github)

```bash
# Available workflows (20 total):
ls /opt/data/docs_flow_framework/.github/workflows/

# CI/CD: ci.yml, deploy-dev.yml, deploy-staging.yml, deploy-prod.yml
# AI Review: ai-review.yml, agent-dispatch.yml
# Issue Management: create-bug-issue.yml, create-deployment-issue.yml,
#                   create-qa-testing-issue.yml, issue-label-sync.yml
# Phase Management: phase-transition.yml, check-phase-completion.yml,
#                   check-all-phases-dev.yml
# QA: execute-qa-testing.yml
# Project: auto-add-to-project.yml, pr-merge-cleanup.yml
# Ops: release.yml, rollback-prod.yml
# SDD: mvp-docs-generation.yml, test-pipeline.yml
```

### Validation Scripts (All Projects)

```bash
# Run from any project
cd /opt/data/project_name

# Extract tags from code
python scripts/validate/extract_tags.py \
    --source src/ docs/ \
    --output docs/generated/tags.json

# Validate tags against documents
python scripts/validate/validate_tags_against_docs.py \
    --tags docs/generated/tags.json \
    --strict

# Generate traceability matrices
python scripts/validate/generate_traceability_matrices.py --auto
```

---

## Updating Framework Resources

### Update Shared Skill

```bash
# Edit in framework
vim /opt/data/docs_flow_framework/.claude/skills/doc-flow/SKILL.md

# Changes immediately available to ALL projects (via symlinks)
```

### Add New Shared Skill

```bash
# Create in framework
mkdir /opt/data/docs_flow_framework/.claude/skills/new-skill
vim /opt/data/docs_flow_framework/.claude/skills/new-skill/SKILL.md

# Automatically available to ALL projects
```

### Update Template

```bash
# Edit SDD template in framework
vim /opt/data/docs_flow_framework/ai_dev_ssd_flow/07_REQ/REQ-MVP-TEMPLATE.md

# Edit SDD governance template in framework
vim /opt/data/docs_flow_framework/governance/PROJECT_PLAN.md

# Changes immediately available to ALL projects
```

---

## Migration: Custom → Shared

```bash
# If custom skill becomes useful across projects:

# 1. Copy to framework
cp -r ${PROJECT_A_PATH}/.claude/custom_skills/useful-skill \
      /opt/data/docs_flow_framework/.claude/skills/

# 2. Remove from project custom
rm -rf ${PROJECT_A_PATH}/.claude/custom_skills/useful-skill

# 3. Now shared across all projects
```

---

## Verification

### Check Setup

```bash
# Verify symlinks
ls -la /opt/data/project_name/.claude/

# Expected output includes:
# skills -> /opt/data/docs_flow_framework/.claude/skills
# commands -> /opt/data/docs_flow_framework/.claude/commands
# agents -> /opt/data/docs_flow_framework/.claude/agents
```

### Test Skill Discovery

```bash
cd /opt/data/project_name

# In Claude Code session:
# /skill doc-flow        # Shared skill
# /skill my-skill        # Custom skill (if exists)
```

### Verify Template Access

```bash
# Verify SDD templates
ls -la /opt/data/project_name/.templates/ai_dev_ssd_flow/01_BRD/
# Should list: BRD-MVP-TEMPLATE.md, etc.

# Verify SDD governance templates
ls -la /opt/data/project_name/.templates/governance/
# Should list: PROJECT_PLAN.md, GOVERNANCE_RULES.md, etc.
```

---

## Troubleshooting

### Broken Symlink

```bash
# Check if target exists
ls -la /opt/data/docs_flow_framework/.claude/skills/

# Recreate symlink
cd /opt/data/project_name/.claude
rm skills
ln -s /opt/data/docs_flow_framework/.claude/skills skills
```

### Skill Not Found

```bash
# Verify skill exists in framework
ls /opt/data/docs_flow_framework/.claude/skills/skill-name/

# Verify skill has SKILL.md
cat /opt/data/docs_flow_framework/.claude/skills/skill-name/SKILL.md

# Check custom skills
ls /opt/data/project_name/.claude/custom_skills/
```

### Permission Issues

```bash
# Fix framework permissions
chmod -R 755 /opt/data/docs_flow_framework/.claude/skills/

# Fix custom permissions
chmod -R 755 /opt/data/project_name/.claude/custom_skills/
```

---

## Git Operations

### What to Commit

**DO commit:**

- `.claude/custom_skills/`
- `.claude/custom_commands/`
- `.claude/custom_agents/`
- `.claude/settings.local.json`
- `.claude/CLAUDE.md`
- `docs/` (project artifacts)
- `work_plans/` (project plans)
- `.gitignore`

**DO NOT commit:**

- `.claude/skills/` (symlink)
- `.claude/commands/` (symlink)
- `.claude/agents/` (symlink)
- `.templates/` (symlink)
- `scripts/validate/` (symlink)

### Clone Project Setup

```bash
# After cloning project
git clone <project-url> /opt/data/new_clone
cd /opt/data/new_clone

# Setup framework symlinks
/opt/data/docs_flow_framework/scripts/setup_project_hybrid.sh /opt/data/new_clone

# Symlinks recreated, custom resources already present from git
```

---

## Common Patterns

### Pattern 1: Framework Skill Development

```bash
# 1. Create skill in framework (not project)
mkdir /opt/data/docs_flow_framework/.claude/skills/new-feature
vim /opt/data/docs_flow_framework/.claude/skills/new-feature/SKILL.md

# 2. Test in any project (immediately available)
cd /opt/data/any_project
# Use: /skill new-feature

# 3. Iterate (edit framework, test in project)
```

### Pattern 2: Project-Specific Feature

```bash
# 1. Create in project custom
mkdir ${PROJECT_B_PATH}/.claude/custom_skills/project-specific
vim ${PROJECT_B_PATH}/.claude/custom_skills/project-specific/SKILL.md

# 2. Commit to project repo
git add .claude/custom_skills/project-specific/
git commit -m "Add project-specific skill"

# 3. Only available in this project
```

### Pattern 3: Template Usage (SDD Framework)

```bash
# 1. Access SDD template via symlink
cat /opt/data/project_name/.templates/ai_dev_ssd_flow/01_BRD/BRD-MVP-TEMPLATE.md

# 2. Copy to project docs
cp .templates/ai_dev_ssd_flow/01_BRD/BRD-MVP-TEMPLATE.md \
   docs/BRD/BRD-001_my_requirements.md

# 3. Edit project copy
vim docs/BRD/BRD-001_my_requirements.md
```

### Pattern 4: Template Usage (SDD governance)

```bash
# 1. Access SDD governance template via symlink
cat /opt/data/project_name/.templates/governance/PROJECT_PLAN.md

# 2. Copy governance docs to project
cp .templates/governance/PROJECT_PLAN.md \
   docs/PROJECT_PLAN.md

# 3. Copy GitHub workflows/templates
cp -r .templates/governance/.github/* .github/

# 4. Customize for project
vim docs/PROJECT_PLAN.md
```

---

## Resources

**Full Documentation**: `/opt/data/docs_flow_framework/MULTI_PROJECT_SETUP_GUIDE.md`

**Framework Root**: `/opt/data/docs_flow_framework/`

**Setup Script**: `/opt/data/docs_flow_framework/scripts/setup_project_hybrid.sh`

**Skills Catalog**: `/opt/data/docs_flow_framework/.claude/skills/README.md`

### Framework-Specific Documentation

| Framework | README | Key Docs |
|-----------|--------|----------|
| **ai_dev_ssd_flow** | `ai_dev_ssd_flow/README.md` | 12-layer SDD methodology |
| **governance** | `governance/README.md` | Governance, CI/CD, Issues |

---

## Autopilot v6.0 Quick Start

```bash
# Run MVP Autopilot with TDD mode
python3 ai_dev_ssd_flow/AUTOPILOT/scripts/mvp_autopilot.py \
  --root . \
  --intent "My MVP" \
  --slug my_mvp \
  --tdd-mode \
  --auto-fix \
  --report markdown

# Run with Change Management mode
python3 ai_dev_ssd_flow/AUTOPILOT/scripts/mvp_autopilot.py \
  --root . \
  --chg-mode \
  --chg-level L2 \
  --auto-fix

# Run validation only
python3 ai_dev_ssd_flow/AUTOPILOT/scripts/mvp_autopilot.py \
  --root . \
  --validate-gates
```

**Key v6.0 Features**:
- **TSPEC** (Layer 10): Test Specifications (UTEST, ITEST, STEST, FTEST)
- **TDD Mode**: Test-first development with Red→Green validation
- **CHG Integration**: 4-Gate change management system

---

**Quick Reference Version**: 2.4 (2026-03-12)
