#!/bin/bash
# Setup hybrid shared/custom resources for a project
# Part of AI Dev Flow Framework multi-project architecture

set -e

PROJECT_DIR=$1
FRAMEWORK_DIR="/opt/data/docs_flow_framework"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

if [ -z "$PROJECT_DIR" ]; then
    echo -e "${RED}Error: Project directory required${NC}"
    echo "Usage: $0 /opt/data/project_name"
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

# Setup template symlinks
mkdir -p "$PROJECT_DIR/.templates"
backup_if_needed "$PROJECT_DIR/.templates/ai_dev_flow"
ln -sf "$FRAMEWORK_DIR/ai_dev_flow" "$PROJECT_DIR/.templates/ai_dev_flow"
echo -e "${GREEN}  ✓ Templates linked${NC}"

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
add_gitignore_entry ".templates/"
add_gitignore_entry "scripts/validate"
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
/opt/data/docs_flow_framework/.claude/skills/
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
if [ -L "$PROJECT_DIR/.templates/ai_dev_flow" ]; then
    TEMPLATE_COUNT=$(find "$PROJECT_DIR/.templates/ai_dev_flow" -name "*-TEMPLATE.md" -o -name "*-template.md" 2>/dev/null | wc -l)
    echo -e "${GREEN}  ✓ $TEMPLATE_COUNT templates accessible${NC}"
else
    echo -e "${RED}  ✗ Template symlink not found${NC}"
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
echo "  • Templates: .templates/ai_dev_flow/ (symlink)"
echo "  • Validation: scripts/validate/ (symlink)"
echo ""
echo "Next steps:"
echo "  1. Review .gitignore entries"
echo "  2. Create project-specific skills in .claude/custom_skills/"
echo "  3. Configure .claude/settings.local.json"
echo "  4. Optional: Create .claude/CLAUDE.md for project context"
echo ""
