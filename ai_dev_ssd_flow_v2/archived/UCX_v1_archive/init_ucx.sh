#!/usr/bin/env bash
# =============================================================================
# init_ucx.sh — Initialize UCX for a Project
# =============================================================================
# Sets up the UCX directory structure for a project with symlinks to the
# framework and project-specific override directories.
#
# Usage:
#   ./init_ucx.sh [project_ucx_dir]
#
# Examples:
#   ./init_ucx.sh                           # Creates ./docs/UCX/
#   ./init_ucx.sh /opt/data/myproject/UCX   # Creates at specified path
#
# =============================================================================

set -euo pipefail

# =============================================================================
# Configuration
# =============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRAMEWORK_UCX="${FRAMEWORK_UCX:-$SCRIPT_DIR}"
PROJECT_UCX="${1:-./docs/UCX}"

echo "════════════════════════════════════════════════════════════"
echo "  UCX Project Initialization"
echo "════════════════════════════════════════════════════════════"
echo "  Framework: $FRAMEWORK_UCX"
echo "  Project:   $PROJECT_UCX"
echo "════════════════════════════════════════════════════════════"
echo ""

# =============================================================================
# Create directory structure
# =============================================================================
echo "Creating directory structure..."

mkdir -p "$PROJECT_UCX/creation"
mkdir -p "$PROJECT_UCX/review"
mkdir -p "$PROJECT_UCX/remediation"

# =============================================================================
# Create symlinks to framework
# =============================================================================
echo "Creating symlinks to framework..."

# Skills symlink
if [[ ! -e "$PROJECT_UCX/skills" ]]; then
    ln -sf "$FRAMEWORK_UCX/skills" "$PROJECT_UCX/skills"
    echo "  ✓ skills -> $FRAMEWORK_UCX/skills"
fi

# Creation symlinks
if [[ ! -e "$PROJECT_UCX/creation/run_ucc.sh" ]]; then
    ln -sf "$FRAMEWORK_UCX/creation/run_ucc.sh" "$PROJECT_UCX/creation/run_ucc.sh"
    echo "  ✓ creation/run_ucc.sh"
fi

if [[ ! -e "$PROJECT_UCX/creation/UCC_PERSONAS.md" ]]; then
    ln -sf "$FRAMEWORK_UCX/creation/UCC_PERSONAS.md" "$PROJECT_UCX/creation/UCC_PERSONAS.md"
    echo "  ✓ creation/UCC_PERSONAS.md"
fi

if [[ ! -e "$PROJECT_UCX/creation/UCC_OUTPUT_SCHEMA.md" ]]; then
    ln -sf "$FRAMEWORK_UCX/creation/UCC_OUTPUT_SCHEMA.md" "$PROJECT_UCX/creation/UCC_OUTPUT_SCHEMA.md"
    echo "  ✓ creation/UCC_OUTPUT_SCHEMA.md"
fi

# Review symlinks
if [[ ! -e "$PROJECT_UCX/review/run_ucr.sh" ]]; then
    ln -sf "$FRAMEWORK_UCX/review/run_ucr.sh" "$PROJECT_UCX/review/run_ucr.sh"
    echo "  ✓ review/run_ucr.sh"
fi

if [[ ! -e "$PROJECT_UCX/review/UCR_OUTPUT_TEMPLATE.md" ]]; then
    ln -sf "$FRAMEWORK_UCX/review/UCR_OUTPUT_TEMPLATE.md" "$PROJECT_UCX/review/UCR_OUTPUT_TEMPLATE.md"
    echo "  ✓ review/UCR_OUTPUT_TEMPLATE.md"
fi

if [[ ! -e "$PROJECT_UCX/review/UCR_OUTPUT_UNIFIED.md" ]]; then
    ln -sf "$FRAMEWORK_UCX/review/UCR_OUTPUT_UNIFIED.md" "$PROJECT_UCX/review/UCR_OUTPUT_UNIFIED.md"
    echo "  ✓ review/UCR_OUTPUT_UNIFIED.md"
fi

# Remediation symlinks
if [[ ! -e "$PROJECT_UCX/remediation/run_ucrem.sh" ]]; then
    ln -sf "$FRAMEWORK_UCX/remediation/run_ucrem.sh" "$PROJECT_UCX/remediation/run_ucrem.sh"
    echo "  ✓ remediation/run_ucrem.sh"
fi

if [[ ! -e "$PROJECT_UCX/remediation/UCRem_PERSONAS.md" ]]; then
    ln -sf "$FRAMEWORK_UCX/remediation/UCRem_PERSONAS.md" "$PROJECT_UCX/remediation/UCRem_PERSONAS.md"
    echo "  ✓ remediation/UCRem_PERSONAS.md"
fi

if [[ ! -e "$PROJECT_UCX/remediation/UCRem_REPORT_SCHEMA.md" ]]; then
    ln -sf "$FRAMEWORK_UCX/remediation/UCRem_REPORT_SCHEMA.md" "$PROJECT_UCX/remediation/UCRem_REPORT_SCHEMA.md"
    echo "  ✓ remediation/UCRem_REPORT_SCHEMA.md"
fi

if [[ ! -e "$PROJECT_UCX/remediation/UCRem_REPORT_TEMPLATE.md" ]]; then
    ln -sf "$FRAMEWORK_UCX/remediation/UCRem_REPORT_TEMPLATE.md" "$PROJECT_UCX/remediation/UCRem_REPORT_TEMPLATE.md"
    echo "  ✓ remediation/UCRem_REPORT_TEMPLATE.md"
fi

# =============================================================================
# Create README
# =============================================================================
if [[ ! -e "$PROJECT_UCX/README.md" ]]; then
    cat > "$PROJECT_UCX/README.md" << 'EOF'
# UCX (Unified Context) - Project Configuration

This directory contains project-specific UCX configuration and prompts.

## Structure

```
UCX/
├── README.md                 # This file
├── skills -> framework       # Symlink to framework persona skills
│
├── creation/                 # UCC (Unified Context Creation)
│   ├── run_ucc.sh -> fw      # Symlink to framework runner
│   ├── UCC_PERSONAS.md -> fw # Symlink to framework personas
│   └── UCC_PROMPT_*_PROJECT.md  # Project-specific prompts (optional)
│
├── review/                   # UCR (Unified Context Review)
│   ├── run_ucr.sh -> fw      # Symlink to framework runner
│   └── UCR_PROMPT_*_PROJECT.md  # Project-specific prompts (optional)
│
└── remediation/              # UCRem (Unified Context Remediation)
    ├── run_ucrem.sh -> fw    # Symlink to framework runner
    └── UCRem_PROMPT_*_PROJECT.md  # Project-specific prompts (optional)
```

## Project-Specific Customization

To customize UCX for this project:

1. **Add domain context**: Create `*_PROJECT.md` prompts with project-specific
   terminology, compliance requirements, or technical constraints.

2. **Override prompts**: Copy a framework prompt and modify it. The runners
   automatically prefer `*_PROJECT.md` files over framework defaults.

## Usage

### Create a document
```bash
./creation/run_ucc.sh <doc_type> <output_path> [options]
```

### Review a document
```bash
./review/run_ucr.sh <doc_type> <document_path> [output_file]
```

### Generate fix proposals
```bash
./remediation/run_ucrem.sh <review_report> <document_path>
```

## Framework Location

Framework UCX: /opt/data/docs_flow_framework/ucx_flow_v3/UCX
EOF
    echo "  ✓ README.md"
fi

# =============================================================================
# Summary
# =============================================================================
echo ""
echo "════════════════════════════════════════════════════════════"
echo "  UCX Initialized Successfully"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Project UCX directory: $PROJECT_UCX"
echo ""
echo "Next steps:"
echo "  1. Add project-specific prompts (optional):"
echo "     - $PROJECT_UCX/creation/UCC_PROMPT_BRD_PROJECT.md"
echo "     - $PROJECT_UCX/review/UCR_PROMPT_BRD_PROJECT.md"
echo ""
echo "  2. Run your first UCR review:"
echo "     $PROJECT_UCX/review/run_ucr.sh brd docs/01_BRD/"
echo ""
echo "════════════════════════════════════════════════════════════"
