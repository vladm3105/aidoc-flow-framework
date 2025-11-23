#!/bin/bash
# Bulk Metadata Addition Script for AI Dev Flow Framework
#
# Adds YAML frontmatter metadata to markdown files based on templates
# Usage: ./bulk_add_metadata.sh [file_pattern] [template_type]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if file already has frontmatter
has_frontmatter() {
    local file="$1"
    head -n 1 "$file" | grep -q "^---$"
}

# Extract existing frontmatter
extract_frontmatter() {
    local file="$1"
    if has_frontmatter "$file"; then
        sed -n '/^---$/,/^---$/p' "$file"
    fi
}

# Remove existing frontmatter
remove_frontmatter() {
    local file="$1"
    if has_frontmatter "$file"; then
        sed -i '1{/^---$/,/^---$/d;}' "$file"
    fi
}

# Add metadata to skill file
add_skill_metadata() {
    local file="$1"
    local skill_name=$(basename "$(dirname "$file")")
    local temp_file="${file}.tmp"

    # Extract description from existing content
    local description=$(grep -m 1 "^description:" "$file" 2>/dev/null | sed 's/description: //' || echo "")

    cat > "$temp_file" <<EOF
---
name: $skill_name
description: ${description:-"Skill description"}
tags:
  - sdd-workflow
  - shared-architecture
  - documentation-skill
custom_fields:
  layer: 0
  artifact_type: UNKNOWN
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  skill_category: core-workflow
  upstream_artifacts: []
  downstream_artifacts: []
---

EOF

    # Append original content (without old frontmatter if exists)
    remove_frontmatter "$file"
    cat "$file" >> "$temp_file"
    mv "$temp_file" "$file"

    log_success "Added metadata to skill: $skill_name"
}

# Add metadata to guide file
add_guide_metadata() {
    local file="$1"
    local filename=$(basename "$file" .md)
    local temp_file="${file}.tmp"

    # Derive title from filename
    local title=$(echo "$filename" | sed 's/_/ /g' | sed 's/\b\(.\)/\u\1/g')

    cat > "$temp_file" <<EOF
---
title: "$title"
tags:
  - framework-guide
  - shared-architecture
custom_fields:
  document_type: guide
  priority: shared
  development_status: active
  applies_to: []
  version: "1.0"
---

EOF

    # Append original content (without old frontmatter if exists)
    remove_frontmatter "$file"
    cat "$file" >> "$temp_file"
    mv "$temp_file" "$file"

    log_success "Added metadata to guide: $filename"
}

# Add metadata to index file
add_index_metadata() {
    local file="$1"
    local filename=$(basename "$file")
    local temp_file="${file}.tmp"

    # Extract artifact type from filename (e.g., BRD-000_index.md -> BRD)
    local artifact_type=$(echo "$filename" | sed 's/-000.*//' | tr '[:lower:]' '[:upper:]')
    local layer=$(get_layer_for_artifact "$artifact_type")

    cat > "$temp_file" <<EOF
---
title: "$artifact_type-000: $artifact_type Index"
tags:
  - index-document
  - layer-$layer-artifact
  - shared-architecture
custom_fields:
  document_type: index
  artifact_type: $artifact_type
  layer: $layer
  priority: shared
---

EOF

    # Append original content (without old frontmatter if exists)
    remove_frontmatter "$file"
    cat "$file" >> "$temp_file"
    mv "$temp_file" "$file"

    log_success "Added metadata to index: $artifact_type"
}

# Add metadata to template file
add_template_metadata() {
    local file="$1"
    local filename=$(basename "$file")
    local temp_file="${file}.tmp"

    cat > "$temp_file" <<EOF
---
# Example metadata - customize for your document
title: "Document Title"
tags:
  - feature-doc
  - ai-agent-primary
  - recommended-approach
custom_fields:
  architecture_approach: ai-agent-based
  priority: primary
  development_status: active
---

EOF

    # Append original content (without old frontmatter if exists)
    remove_frontmatter "$file"
    cat "$file" >> "$temp_file"
    mv "$temp_file" "$file"

    log_success "Added example metadata to template: $filename"
}

# Get layer number for artifact type
get_layer_for_artifact() {
    local artifact="$1"
    case "$artifact" in
        BRD) echo "1" ;;
        PRD) echo "2" ;;
        EARS) echo "3" ;;
        BDD) echo "4" ;;
        ADR) echo "5" ;;
        SYS) echo "6" ;;
        REQ) echo "7" ;;
        IMPL) echo "8" ;;
        CTR) echo "9" ;;
        SPEC) echo "10" ;;
        TASKS) echo "11" ;;
        IPLAN) echo "12" ;;
        *) echo "0" ;;
    esac
}

# Determine file type and add appropriate metadata
process_file() {
    local file="$1"
    local force="$2"

    if has_frontmatter "$file" && [ "$force" != "force" ]; then
        log_warning "Skipping $file (already has frontmatter, use --force to overwrite)"
        return
    fi

    if [[ "$file" == *"/SKILL.md" ]]; then
        add_skill_metadata "$file"
    elif [[ "$file" == *"index.md" ]]; then
        add_index_metadata "$file"
    elif [[ "$file" == *"TEMPLATE"* ]]; then
        add_template_metadata "$file"
    elif [[ "$file" == *"GUIDE.md" ]] || [[ "$file" == *"RULES.md" ]] || [[ "$file" == *"STANDARDS.md" ]]; then
        add_guide_metadata "$file"
    else
        log_info "Unknown file type: $file (manual metadata required)"
    fi
}

# Main execution
main() {
    local pattern="${1:-.}"
    local force=""

    if [ "$2" == "--force" ] || [ "$2" == "-f" ]; then
        force="force"
    fi

    log_info "Processing files matching: $pattern"

    if [ -f "$pattern" ]; then
        # Single file
        process_file "$pattern" "$force"
    elif [ -d "$pattern" ]; then
        # Directory - process all .md files
        while IFS= read -r -d '' file; do
            process_file "$file" "$force"
        done < <(find "$pattern" -name "*.md" -type f -print0)
    else
        # Pattern matching
        while IFS= read -r -d '' file; do
            process_file "$file" "$force"
        done < <(find "$ROOT_DIR" -path "$pattern" -type f -print0)
    fi

    log_success "Bulk metadata addition complete"
}

# Show usage
usage() {
    cat <<EOF
Usage: $0 [OPTIONS] [PATH]

Add YAML frontmatter metadata to markdown files.

OPTIONS:
    -f, --force     Overwrite existing frontmatter
    -h, --help      Show this help message

PATH:
    File, directory, or pattern to process (default: current directory)

EXAMPLES:
    $0                              # Process all .md files in current directory
    $0 ai_dev_flow/                 # Process all .md files in ai_dev_flow/
    $0 .claude/skills/*/SKILL.md    # Process all SKILL.md files
    $0 file.md                      # Process single file
    $0 -f file.md                   # Force overwrite existing frontmatter

EOF
}

# Parse arguments
if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    usage
    exit 0
fi

main "$@"
