#!/bin/bash
# Setup script for AI PR Review labels
#
# Creates the required GitHub labels for the AI PR review workflow.
# Run this once per repository to set up the labeling system.
#
# Usage:
#   ./scripts/setup-ai-pr-review-labels.sh [OWNER/REPO]
#
# If OWNER/REPO is not provided, uses the current repository.
#
# Prerequisites:
#   - gh CLI authenticated
#   - Repository admin access

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Determine repository
if [ -n "${1:-}" ]; then
    REPO="$1"
else
    # Try to get from git remote
    REPO=$(gh repo view --json nameWithOwner -q '.nameWithOwner' 2>/dev/null || echo "")
    if [ -z "$REPO" ]; then
        log_error "Could not determine repository. Please provide OWNER/REPO as argument."
        exit 1
    fi
fi

log_info "Setting up AI PR Review labels for: $REPO"

# Function to create or update a label
create_label() {
    local name="$1"
    local color="$2"
    local description="$3"

    # Check if label exists
    if gh label view "$name" --repo "$REPO" &>/dev/null; then
        log_info "Label '$name' already exists, updating..."
        gh label edit "$name" \
            --repo "$REPO" \
            --color "$color" \
            --description "$description" 2>/dev/null || true
    else
        log_info "Creating label: $name"
        gh label create "$name" \
            --repo "$REPO" \
            --color "$color" \
            --description "$description"
    fi
}

# AI PR Review labels
log_info "Creating AI PR Review labels..."

create_label "ai:review-passed" "0E8A16" "AI review passed - no critical/medium findings"
create_label "ai:review-failed" "D93F0B" "AI review found critical/medium issues"
create_label "skip-ai-review" "CCCCCC" "Skip automated AI review on this PR"

# AI Issue labels (for governance workflow)
log_info "Creating AI Issue labels..."

create_label "ai:ready" "0052CC" "Ready for AI agent to work on"
create_label "ai:in-progress" "FBCA04" "AI agent actively working"
create_label "ai:review-requested" "5319E7" "AI work complete, human review requested"

# CHG labels (SDD-Full change management)
log_info "Creating CHG labels (SDD-Full only)..."

create_label "chg:pending" "F9A825" "CHG document awaiting approval"
create_label "chg:approved" "43A047" "CHG document approved"
create_label "chg:rejected" "D32F2F" "CHG document rejected"

log_info "Label setup complete!"

# Verify labels
log_info "Verifying labels..."
echo ""
echo "Labels created/updated:"
gh label list --repo "$REPO" | grep -E "^ai:|^skip-ai" || true
echo ""
log_info "Setup complete. AI PR Review workflow is ready to use."
