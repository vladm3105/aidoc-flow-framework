# Multi-Project Setup - Quick Reference

**Quick commands for managing AI Dev Flow Framework across multiple projects**

---

## Setup New Project

```bash
# Setup hybrid shared/custom resources
/opt/data/docs_flow_framework/scripts/setup_project_hybrid.sh /opt/data/project_name

# What it does:
# ✓ Creates .claude/custom_skills/, custom_commands/, custom_agents/
# ✓ Symlinks .claude/skills/ → framework
# ✓ Symlinks .claude/commands/ → framework
# ✓ Symlinks .claude/agents/ → framework
# ✓ Symlinks .templates/ai_dev_flow/ → framework
# ✓ Symlinks scripts/validate/ → framework scripts
# ✓ Configures .gitignore
#
# IMPORTANT: This creates symlinks only
# To complete project setup (create docs/, work_plans/, etc.):
# → Use: /skill project-init (recommended)
# → OR manually: mkdir -p docs/{BRD,PRD,...} work_plans scripts
```

---

## Setup Multiple Projects

```bash
# Batch setup
for PROJECT in ibmcp b_local trading techtrend; do
    /opt/data/docs_flow_framework/scripts/setup_project_hybrid.sh /opt/data/$PROJECT
done
```

---

## Directory Structure After Setup

```
/opt/data/project_name/
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
├── .templates/
│   └── ai_dev_flow/         → /opt/data/docs_flow_framework/ai_dev_flow/
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
# View templates
ls /opt/data/docs_flow_framework/ai_dev_flow/

# Template directories:
# BRD/, PRD/, EARS/, BDD/, ADR/, SYS/, REQ/,
# IMPL/, CTR/, SPEC/, TASKS/, IPLAN/
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
# Edit in framework
vim /opt/data/docs_flow_framework/ai_dev_flow/REQ/REQ-TEMPLATE.md

# Changes immediately available to ALL projects
```

---

## Migration: Custom → Shared

```bash
# If custom skill becomes useful across projects:

# 1. Copy to framework
cp -r /opt/data/project_a/.claude/custom_skills/useful-skill \
      /opt/data/docs_flow_framework/.claude/skills/

# 2. Remove from project custom
rm -rf /opt/data/project_a/.claude/custom_skills/useful-skill

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
ls -la /opt/data/project_name/.templates/ai_dev_flow/BRD/
# Should list: BRD-template.md, BRD-template-2.md, etc.
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
mkdir /opt/data/ibmcp/.claude/custom_skills/ib-specific
vim /opt/data/ibmcp/.claude/custom_skills/ib-specific/SKILL.md

# 2. Commit to project repo
git add .claude/custom_skills/ib-specific/
git commit -m "Add IB-specific skill"

# 3. Only available in this project
```

### Pattern 3: Template Usage

```bash
# 1. Access template via symlink
cat /opt/data/project_name/.templates/ai_dev_flow/BRD/BRD-template.md

# 2. Copy to project docs
cp .templates/ai_dev_flow/BRD/BRD-template.md \
   docs/BRD/BRD-001_my_requirements.md

# 3. Edit project copy
vim docs/BRD/BRD-001_my_requirements.md
```

---

## Resources

**Full Documentation**: `/opt/data/docs_flow_framework/MULTI_PROJECT_SETUP_GUIDE.md`

**Framework Root**: `/opt/data/docs_flow_framework/`

**Setup Script**: `/opt/data/docs_flow_framework/scripts/setup_project_hybrid.sh`

**Skills Catalog**: `/opt/data/docs_flow_framework/.claude/skills/README.md`

---

**Quick Reference Version**: 1.0 (2025-11-13)
