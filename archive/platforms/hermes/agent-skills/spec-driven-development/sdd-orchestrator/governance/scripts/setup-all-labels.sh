#!/bin/bash
# Create all labels from LABEL_REGISTRY.yaml
# Usage: ./setup-all-labels.sh <owner> <repo>
#
# Prerequisites:
# - gh CLI authenticated
# - PyYAML installed (pip install pyyaml)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REGISTRY="${SCRIPT_DIR}/../github/LABEL_REGISTRY.yaml"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Parse arguments
if [ $# -lt 2 ]; then
    # Try to get from git remote
    REPO=$(gh repo view --json nameWithOwner -q '.nameWithOwner' 2>/dev/null || echo "")
    if [ -z "$REPO" ]; then
        log_error "Usage: $0 <owner> <repo>"
        log_error "Or run from within a git repository."
        exit 1
    fi
    OWNER=$(echo "$REPO" | cut -d'/' -f1)
    REPO_NAME=$(echo "$REPO" | cut -d'/' -f2)
else
    OWNER="$1"
    REPO_NAME="$2"
fi

FULL_REPO="${OWNER}/${REPO_NAME}"

log_info "Creating labels for ${FULL_REPO} from ${REGISTRY}"

# Check prerequisites
if ! command -v gh &>/dev/null; then
    log_error "gh CLI not found. Install from https://cli.github.com/"
    exit 1
fi

if ! python3 -c "import yaml" 2>/dev/null; then
    log_error "PyYAML not installed. Run: pip install pyyaml"
    exit 1
fi

if [ ! -f "$REGISTRY" ]; then
    log_error "Registry file not found: $REGISTRY"
    exit 1
fi

# Create labels using Python for YAML parsing
python3 << EOF
import yaml
import subprocess
import sys

with open("${REGISTRY}") as f:
    data = yaml.safe_load(f)

total = 0
created = 0
failed = 0

for category, labels in data.get("categories", {}).items():
    print(f"\n=== {category.upper()} ===")
    for label in labels:
        total += 1
        cmd = [
            "gh", "label", "create", label["name"],
            "--color", label["color"],
            "--description", label["description"],
            "--repo", "${FULL_REPO}",
            "--force"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓ {label['name']}")
            created += 1
        else:
            # Check if it's just a "label already exists" error
            if "already exists" in result.stderr.lower():
                print(f"  ↻ {label['name']} (updated)")
                created += 1
            else:
                print(f"  ✗ {label['name']}: {result.stderr.strip()}")
                failed += 1

print(f"\n=== Summary ===")
print(f"Total: {total}, Created/Updated: {created}, Failed: {failed}")
sys.exit(1 if failed > 0 else 0)
EOF

exit_code=$?

if [ $exit_code -eq 0 ]; then
    log_info "All labels created successfully!"
else
    log_warn "Some labels failed to create. Check output above."
fi

# Show final label list
echo ""
log_info "Current labels in ${FULL_REPO}:"
gh label list --repo "${FULL_REPO}" --limit 100 | sort

exit $exit_code
