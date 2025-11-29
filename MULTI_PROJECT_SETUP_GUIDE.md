# Multi-Project Framework Setup Guide

**Purpose**: Configuration patterns for sharing AI Dev Flow Framework resources across multiple projects

**Scope**: Claude Code skills, commands, agents, templates, and validation scripts

**Last Updated**: 2025-11-13

> **Note**: Examples in this guide use placeholder project paths like `${PROJECT_PATH}/` for illustration purposes. Replace these with your actual project paths (e.g., `${PROJECT_PATH}` or `/path/to/your/project/`).

---

## Architecture Overview

### Centralized Framework Pattern

```
/opt/data/
├── docs_flow_framework/          # Central framework repository
│   ├── ai_dev_flow/              # Document templates
│   ├── scripts/                  # Validation and automation tools
│   └── .claude/
│       ├── skills/               # Shared skills (15+)
│       ├── commands/             # Shared slash commands
│       └── agents/               # Shared agent configurations
│
└── projects/
    ├── project_a/                # Individual projects
    │   ├── docs/                 # Project artifacts (BRD, ADR, etc.)
    │   ├── src/                  # Source code
    │   ├── .templates/           # Symlink → framework templates
    │   └── .claude/
    │       ├── skills/           # Symlink → shared skills
    │       ├── commands/         # Symlink → shared commands
    │       ├── agents/           # Symlink → shared agents
    │       ├── custom_skills/    # Project-specific skills
    │       └── settings.local.json  # Project configuration
    │
    └── project_b/
        └── [same structure]
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
| **Templates** | `.templates/ai_dev_flow/` | N/A | Symlink only |
| **Scripts** | `scripts/validate/` | `scripts/` | Both available |

---

## Setup Procedures

### 1. Framework Prerequisites

**Verify framework structure:**
```bash
ls -la /opt/data/docs_flow_framework/.claude/
# Expected: skills/, commands/, agents/

ls -la /opt/data/docs_flow_framework/ai_dev_flow/
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

# Setup template symlinks
mkdir -p "$PROJECT_DIR/.templates"
backup_if_needed "$PROJECT_DIR/.templates/ai_dev_flow"
ln -sf "$FRAMEWORK_DIR/ai_dev_flow" "$PROJECT_DIR/.templates/ai_dev_flow"

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
```

**Note**: This script creates symlinks for shared resources only. To complete the project setup with documentation folders (`docs/`) and implementation plans folder (`work_plans/`), use:

```bash
# Recommended: Use project-init skill
cd /opt/data/project_name
# In Claude Code: /skill project-init

# OR manually create folder structure
mkdir -p docs/{BRD,PRD,EARS,BDD,ADR,SYS,REQ,IMPL,CTR,SPEC,TASKS,IPLAN}
mkdir -p docs/REQ/{api,auth,data,core,integration,monitoring,reporting,security,ui}
mkdir -p work_plans
mkdir -p scripts
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
- Initializes all 13 artifact directories (BRD through IPLAN)
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

# Setup one project
/opt/data/docs_flow_framework/scripts/setup_project_hybrid.sh ${PROJECT_PATH}
```

### 4. Bulk Project Setup

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

### Complete Project Layout

```
/opt/data/project_name/
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
├── .templates/
│   └── ai_dev_flow/                 # Symlink → framework templates
│
├── docs/                            # Project artifacts (auto-created by project-init)
│   ├── BRD/
│   ├── PRD/
│   ├── ADR/
│   ├── REQ/
│   └── generated/
│       └── matrices/
│
├── work_plans/                      # Implementation plans (auto-created by project-init)
│   └── IPLAN-001_*.md
│
├── scripts/
│   ├── validate/                    # Symlink → framework scripts
│   └── project_specific.sh          # Project scripts
│
├── src/                             # Source code
├── tests/                           # Tests
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
**Templates**: .templates/ai_dev_flow/
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
# Shared framework resources (symlinks - do not commit)
.claude/skills
.claude/commands
.claude/agents
.templates/
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
# Edit framework template
vim /opt/data/docs_flow_framework/ai_dev_flow/BRD/BRD-TEMPLATE.md

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

# Verify template access
ls -la ${PROJECT_PATH}/.templates/ai_dev_flow/BRD/
# Should list template files
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

### Use Case 1: Greenfield Project

**Scenario**: Starting new project with framework

```bash
# 1. Create project root directory
mkdir -p /opt/data/new_project

# 2. Setup hybrid resources (symlinks only)
/opt/data/docs_flow_framework/scripts/setup_project_hybrid.sh /opt/data/new_project

# 3. Create project structure (docs, work_plans, src, tests)
cd /opt/data/new_project
# Use /skill project-init for full structure
# OR manually:
mkdir -p docs/{BRD,PRD,EARS,BDD,ADR,SYS,REQ,IMPL,CTR,SPEC,TASKS,IPLAN}
mkdir -p work_plans
mkdir -p src tests

# 4. Result: Complete project setup with framework access
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
- [Specification-Driven Development Guide](./ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md) - SDD workflow
- [ID Naming Standards](./ai_dev_flow/ID_NAMING_STANDARDS.md) - Document naming conventions
- [Traceability Setup](./ai_dev_flow/TRACEABILITY_SETUP.md) - Tag-based traceability

### External Resources

- Claude Code Skills Documentation: https://docs.claude.com/claude-code/skills
- Symlink best practices: `man ln`
- Git symlink handling: https://git-scm.com/docs/git-add#_symbolic_links

---

## Changelog

### Version 1.0 (2025-11-13)

- Initial hybrid approach documentation
- Setup script for shared/custom resource pattern
- Migration procedures from copied skills
- Validation and troubleshooting guides
- Use cases and rollback procedures

---

**Maintained by**: Framework Administrator
**Contact**: See framework repository for issues and contributions
