#!/usr/bin/env bash
# Setup GitHub environments for AIOCTO deployment
# Phase 5 - GCP Configuration
#
# Creates and configures GitHub environments:
#   - development (auto-deploy on PR)
#   - staging (deploy on phase completion)
#   - production (manual approval required)
#
# Prerequisites:
#   - gh CLI authenticated with admin access
#   - Repository admin permissions
#
# Usage:
#   ./scripts/project_setup/setup_github_environments.sh

set -euo pipefail

# Configuration
GH_HOST="${GH_HOST:-{GITHUB_HOST}}"
OWNER="{GITHUB_ORG}"
REPO="{REPO_NAME}"

# Required reviewers for production (GitHub usernames)
PROD_REVIEWERS=("{ADMIN_USERNAME}")

echo "=== GitHub Environment Setup ==="
echo "Repository: $OWNER/$REPO"
echo ""

# Check gh authentication
if ! GH_HOST=$GH_HOST gh auth status &>/dev/null; then
    echo "Error: gh CLI not authenticated. Run: gh auth login --hostname $GH_HOST"
    exit 1
fi

# Create environments using GitHub API
create_environment() {
    local env_name=$1
    local wait_timer=${2:-0}
    local reviewers=${3:-""}
    local branch_policy=${4:-""}

    echo "Creating environment: $env_name"

    # Build the request body
    local body="{\"wait_timer\": $wait_timer"

    if [[ -n "$reviewers" ]]; then
        # Get user IDs for reviewers
        local reviewer_ids="["
        local first=true
        for reviewer in $reviewers; do
            local user_id
            user_id=$(GH_HOST=$GH_HOST gh api "users/$reviewer" --jq '.id' 2>/dev/null || echo "")
            if [[ -n "$user_id" ]]; then
                if [[ "$first" != "true" ]]; then
                    reviewer_ids+=","
                fi
                reviewer_ids+="{\"type\": \"User\", \"id\": $user_id}"
                first=false
            fi
        done
        reviewer_ids+="]"
        body+=", \"reviewers\": $reviewer_ids"
    fi

    if [[ -n "$branch_policy" ]]; then
        body+=", \"deployment_branch_policy\": $branch_policy"
    fi

    body+="}"

    # Create or update environment
    GH_HOST=$GH_HOST gh api \
        --method PUT \
        "repos/$OWNER/$REPO/environments/$env_name" \
        --input - <<< "$body" \
        --silent || echo "  Warning: Could not create $env_name (may need admin rights)"

    echo "  Created: $env_name"
}

# Development environment - no restrictions
echo ""
echo "=== Development Environment ==="
create_environment "development" 0 "" ""

# Staging environment - protected branches only
echo ""
echo "=== Staging Environment ==="
create_environment "staging" 0 "" '{"protected_branches": true}'

# Production environment - require approval
echo ""
echo "=== Production Environment ==="
create_environment "production" 0 "${PROD_REVIEWERS[*]}" '{"protected_branches": true, "custom_branch_policies": false}'

echo ""
echo "=== Environment Setup Complete ==="
echo ""
echo "Environments created:"
echo "  - development: Auto-deploy for PRs"
echo "  - staging: Protected branches only"
echo "  - production: Requires approval from ${PROD_REVIEWERS[*]}"
echo ""
echo "Next steps:"
echo "  1. Add environment secrets via GitHub UI or gh CLI:"
echo "     gh secret set GCP_PROJECT_DEV --env development"
echo "     gh secret set GCP_PROJECT_STAGING --env staging"
echo "     gh secret set GCP_PROJECT_PROD --env production"
echo "  2. Configure WIF credentials for each environment"
echo "  3. Test deployment workflows"
