#!/bin/bash
# Setup hybrid shared/custom resources for a project
# Part of AI Dev Flow Framework multi-project architecture

set -e

PROJECT_DIR=$1
INCLUDE_GITHUB=$2  # Optional: pass "--with-github" to include .github symlink
FRAMEWORK_DIR="/opt/data/ucx_framework"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

if [ -z "$PROJECT_DIR" ]; then
    echo -e "${RED}Error: Project directory required${NC}"
    echo "Usage: $0 /opt/data/project_name [--with-github]"
    echo ""
    echo "Options:"
    echo "  --with-github    Also symlink .github/ (workflows, issue templates, etc.)"
    exit 1
fi

if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}Error: Project directory does not exist: $PROJECT_DIR${NC}"
    exit 1
fi

if [ ! -d "$FRAMEWORK_DIR" ]; then
    echo -e "${RED}Error: Framework directory not found: $FRAMEWORK_DIR${NC}"
    exit 1
fi

echo -e "${GREEN}Setting up hybrid resources for: $PROJECT_DIR${NC}"
echo ""

# Create .claude directory structure
mkdir -p "$PROJECT_DIR/.claude"
mkdir -p "$PROJECT_DIR/.claude/custom_skills"
mkdir -p "$PROJECT_DIR/.claude/custom_commands"
mkdir -p "$PROJECT_DIR/.claude/custom_agents"

# Backup existing resources if not symlinks
backup_if_needed() {
    local target=$1
    local name=$(basename "$target")

    if [ -d "$target" ] && [ ! -L "$target" ]; then
        local backup="${target}.backup_$(date +%Y%m%d_%H%M%S)"
        echo -e "${YELLOW}  Backing up existing $name -> ${backup}${NC}"
        mv "$target" "$backup"
    elif [ -L "$target" ]; then
        echo -e "  Removing old symlink: $name"
        rm "$target"
    fi
}

# Setup symlinks for shared resources
echo "Setting up shared resource symlinks..."

if [ -d "$FRAMEWORK_DIR/.claude/skills" ]; then
    backup_if_needed "$PROJECT_DIR/.claude/skills"
    ln -sf "$FRAMEWORK_DIR/.claude/skills" "$PROJECT_DIR/.claude/skills"
    echo -e "${GREEN}  ✓ Skills linked${NC}"
else
    echo -e "${YELLOW}  ⚠ Framework skills directory not found${NC}"
fi

if [ -d "$FRAMEWORK_DIR/.claude/commands" ]; then
    backup_if_needed "$PROJECT_DIR/.claude/commands"
    ln -sf "$FRAMEWORK_DIR/.claude/commands" "$PROJECT_DIR/.claude/commands"
    echo -e "${GREEN}  ✓ Commands linked${NC}"
else
    echo -e "${YELLOW}  ⚠ Framework commands directory not found (optional)${NC}"
fi

if [ -d "$FRAMEWORK_DIR/.claude/agents" ]; then
    backup_if_needed "$PROJECT_DIR/.claude/agents"
    ln -sf "$FRAMEWORK_DIR/.claude/agents" "$PROJECT_DIR/.claude/agents"
    echo -e "${GREEN}  ✓ Agents linked${NC}"
else
    echo -e "${YELLOW}  ⚠ Framework agents directory not found (optional)${NC}"
fi

echo ""
echo "Setting up template symlinks..."

# Setup template symlinks (BOTH frameworks)
mkdir -p "$PROJECT_DIR/.templates"

# SDD Framework templates
backup_if_needed "$PROJECT_DIR/.templates/ucx_flow_v3"
ln -sf "$FRAMEWORK_DIR/ucx_flow_v3" "$PROJECT_DIR/.templates/ucx_flow_v3"
echo -e "${GREEN}  ✓ SDD templates linked (ucx_flow_v3)${NC}"

# Issues Flow templates
backup_if_needed "$PROJECT_DIR/.templates/ai_project_issues_flow"
ln -sf "$FRAMEWORK_DIR/ai_project_issues_flow" "$PROJECT_DIR/.templates/ai_project_issues_flow"
echo -e "${GREEN}  ✓ Issues Flow templates linked (ai_project_issues_flow)${NC}"

# Optional: Setup .github symlink for CI/CD workflows
if [ "$INCLUDE_GITHUB" = "--with-github" ]; then
    echo ""
    echo "Setting up GitHub workflows symlink..."

    if [ -d "$FRAMEWORK_DIR/.github" ]; then
        backup_if_needed "$PROJECT_DIR/.github"
        ln -sf "$FRAMEWORK_DIR/.github" "$PROJECT_DIR/.github"
        WORKFLOW_COUNT=$(find "$PROJECT_DIR/.github/workflows" -name "*.yml" 2>/dev/null | wc -l)
        TEMPLATE_COUNT=$(find "$PROJECT_DIR/.github/ISSUE_TEMPLATE" -name "*.md" 2>/dev/null | wc -l)
        echo -e "${GREEN}  ✓ GitHub linked ($WORKFLOW_COUNT workflows, $TEMPLATE_COUNT issue templates)${NC}"
    else
        echo -e "${YELLOW}  ⚠ Framework .github directory not found${NC}"
    fi
fi

echo ""
echo "Setting up validation script symlinks..."

# Setup validation script symlinks
mkdir -p "$PROJECT_DIR/scripts"
backup_if_needed "$PROJECT_DIR/scripts/validate"
ln -sf "$FRAMEWORK_DIR/scripts" "$PROJECT_DIR/scripts/validate"
echo -e "${GREEN}  ✓ Validation scripts linked${NC}"

echo ""
echo "Configuring .gitignore..."

# Create .gitignore entries
GITIGNORE="$PROJECT_DIR/.gitignore"
touch "$GITIGNORE"

# Add entries if not present
add_gitignore_entry() {
    local entry=$1
    if ! grep -qxF "$entry" "$GITIGNORE"; then
        echo "$entry" >> "$GITIGNORE"
    fi
}

# Exclude symlinked resources
add_gitignore_entry ".claude/skills"
add_gitignore_entry ".claude/commands"
add_gitignore_entry ".claude/agents"
add_gitignore_entry ".templates/ucx_flow_v3"
add_gitignore_entry ".templates/ai_project_issues_flow"
add_gitignore_entry "scripts/validate"

# Add .github if included
if [ "$INCLUDE_GITHUB" = "--with-github" ]; then
    add_gitignore_entry ".github"
fi
add_gitignore_entry ""
add_gitignore_entry "# Keep project-specific Claude resources"
add_gitignore_entry "!.claude/custom_skills/"
add_gitignore_entry "!.claude/custom_commands/"
add_gitignore_entry "!.claude/custom_agents/"
add_gitignore_entry "!.claude/settings.local.json"
add_gitignore_entry "!.claude/CLAUDE.md"

echo -e "${GREEN}  ✓ .gitignore configured${NC}"

# Create placeholder README in custom directories
cat > "$PROJECT_DIR/.claude/custom_skills/README.md" << 'EOF'
# Project-Specific Skills

Place project-specific Claude skills in this directory.

## Structure

```
custom_skills/
└── my-skill/
    └── SKILL.md
```

## Usage

Skills in this directory are only available to this project and are
committed to version control (unlike shared skills which are symlinked).

## Example

See framework documentation for skill creation guidelines:
/opt/data/ucx_framework/.claude/skills/
EOF

echo ""
echo "Verifying setup..."
echo ""

# Verify setup
echo "Shared resources (symlinks):"
ls -la "$PROJECT_DIR/.claude/" | grep "^l" || echo "  (none found)"
echo ""
echo "Custom resources (directories):"
ls -la "$PROJECT_DIR/.claude/" | grep "^d" | grep custom || echo "  (none found)"
echo ""
echo "Template access:"
if [ -L "$PROJECT_DIR/.templates/ucx_flow_v3" ]; then
    SDD_COUNT=$(find "$PROJECT_DIR/.templates/ucx_flow_v3" -name "*-TEMPLATE.yaml" -o -name "*-TEMPLATE.md" 2>/dev/null | wc -l)
    echo -e "${GREEN}  ✓ SDD: $SDD_COUNT templates accessible${NC}"
else
    echo -e "${RED}  ✗ SDD template symlink not found${NC}"
fi
if [ -L "$PROJECT_DIR/.templates/ai_project_issues_flow" ]; then
    ISSUES_COUNT=$(find "$PROJECT_DIR/.templates/ai_project_issues_flow" -name "*.md" 2>/dev/null | wc -l)
    echo -e "${GREEN}  ✓ Issues Flow: $ISSUES_COUNT docs accessible${NC}"
else
    echo -e "${RED}  ✗ Issues Flow template symlink not found${NC}"
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}Setup complete for: $(basename "$PROJECT_DIR")${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Available resources:"
echo "  • Shared skills: .claude/skills/ (symlink)"
echo "  • Custom skills: .claude/custom_skills/ (tracked)"
echo "  • SDD Templates: .templates/ucx_flow_v3/ (v3 chain)"
echo "  • Issues Flow: .templates/ai_project_issues_flow/ (governance)"
echo "  • Validation: scripts/validate/ (symlink)"
if [ "$INCLUDE_GITHUB" = "--with-github" ]; then
    echo "  • GitHub CI/CD: .github/ (20 workflows, 10 issue templates)"
fi
echo ""
echo "Next steps:"
echo "  1. Review .gitignore entries"
echo "  2. Create project-specific skills in .claude/custom_skills/"
echo "  3. Configure .claude/settings.local.json"
echo "  4. Optional: Create .claude/CLAUDE.md for project context"
if [ "$INCLUDE_GITHUB" != "--with-github" ]; then
    echo "  5. Optional: Re-run with --with-github to add CI/CD workflows"
fi
echo ""
echo "Framework Selection:"
echo "  • Large projects (months-years): Use ucx_flow_v3"
echo "  • Small projects (1-6 months): Use ai_project_issues_flow"
echo ""
