#!/usr/bin/env bash
#
# setup-environments.sh - Configure GitHub Environments and Secrets
#
# Usage:
#   ./setup-environments.sh
#
# Prerequisites:
#   - GCP projects and WIF configured (run setup-projects.sh, setup-wif.sh first)
#   - GitHub CLI (gh) installed and authenticated to GHES
#   - Repository admin permissions
#
# This script configures:
#   - GitHub environments (development, staging, production)
#   - Environment protection rules
#   - Repository and environment secrets

set -euo pipefail

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
readonly GITHUB_HOST="{GITHUB_HOST}"
readonly GITHUB_ORG="{GITHUB_ORG}"
readonly GITHUB_REPO="{REPO_NAME}"
readonly REPO="${GITHUB_ORG}/${GITHUB_REPO}"

readonly PROJECT_PREFIX="{PROJECT_PREFIX}"
readonly DEV_PROJECT="${PROJECT_PREFIX}-dev"
readonly STAGING_PROJECT="${PROJECT_PREFIX}-staging"
readonly PROD_PROJECT="${PROJECT_PREFIX}-prod"

# Required reviewers for production (GitHub usernames)
readonly PROD_REVIEWERS="{CODEOWNER_1},{CODEOWNER_2}"

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
log_info() { echo "[INFO] $*"; }
log_warn() { echo "[WARN] $*" >&2; }
log_error() { echo "[ERROR] $*" >&2; }

# -----------------------------------------------------------------------------
# Validation
# -----------------------------------------------------------------------------
validate_prerequisites() {
  log_info "Validating prerequisites..."

  if ! command -v gh &>/dev/null; then
    log_error "GitHub CLI (gh) not found. Install: https://cli.github.com/"
    exit 1
  fi

  # Check authentication
  if ! GH_HOST="$GITHUB_HOST" gh auth status &>/dev/null; then
    log_error "Not authenticated to $GITHUB_HOST"
    log_info "Run: GH_HOST=$GITHUB_HOST gh auth login"
    exit 1
  fi

  log_info "Prerequisites validated"
}

# -----------------------------------------------------------------------------
# Create GitHub Environment
# -----------------------------------------------------------------------------
create_environment() {
  local env_name="$1"
  local wait_timer="${2:-0}"
  local reviewers="${3:-}"

  log_info "Creating environment: $env_name"

  # Create environment via API
  local payload="{}"

  if [[ "$wait_timer" -gt 0 ]]; then
    payload=$(jq -n --argjson timer "$wait_timer" '{wait_timer: $timer}')
  fi

  GH_HOST="$GITHUB_HOST" gh api \
    --method PUT \
    "/repos/${REPO}/environments/${env_name}" \
    --input - <<< "$payload" || {
      log_warn "Environment $env_name may already exist or API error"
    }

  # Configure protection rules if reviewers specified
  if [[ -n "$reviewers" ]]; then
    log_info "Configuring protection rules for $env_name"

    # Get reviewer user IDs
    local reviewer_ids=()
    IFS=',' read -ra reviewer_names <<< "$reviewers"

    for username in "${reviewer_names[@]}"; do
      local user_id
      user_id=$(GH_HOST="$GITHUB_HOST" gh api "/users/${username}" --jq '.id' 2>/dev/null) || {
        log_warn "Could not find user: $username"
        continue
      }
      reviewer_ids+=("$user_id")
    done

    if [[ ${#reviewer_ids[@]} -gt 0 ]]; then
      # Build reviewers array
      local reviewers_json="["
      for i in "${!reviewer_ids[@]}"; do
        if [[ $i -gt 0 ]]; then reviewers_json+=","; fi
        reviewers_json+="{\"type\":\"User\",\"id\":${reviewer_ids[$i]}}"
      done
      reviewers_json+="]"

      # Update environment protection rules
      GH_HOST="$GITHUB_HOST" gh api \
        --method PUT \
        "/repos/${REPO}/environments/${env_name}" \
        -f "reviewers=${reviewers_json}" \
        -f "wait_timer=${wait_timer}" || {
          log_warn "Could not set reviewers for $env_name"
        }
    fi
  fi
}

# -----------------------------------------------------------------------------
# Set Repository Secret
# -----------------------------------------------------------------------------
set_repo_secret() {
  local secret_name="$1"
  local secret_value="$2"

  log_info "Setting repository secret: $secret_name"

  echo -n "$secret_value" | GH_HOST="$GITHUB_HOST" gh secret set "$secret_name" \
    --repo "$REPO" || {
      log_error "Failed to set secret: $secret_name"
      return 1
    }
}

# -----------------------------------------------------------------------------
# Set Environment Secret
# -----------------------------------------------------------------------------
set_env_secret() {
  local env_name="$1"
  local secret_name="$2"
  local secret_value="$3"

  log_info "Setting environment secret: $env_name/$secret_name"

  echo -n "$secret_value" | GH_HOST="$GITHUB_HOST" gh secret set "$secret_name" \
    --repo "$REPO" \
    --env "$env_name" || {
      log_error "Failed to set secret: $env_name/$secret_name"
      return 1
    }
}

# -----------------------------------------------------------------------------
# Get WIF Provider
# -----------------------------------------------------------------------------
get_wif_provider() {
  local project_id="$1"

  local project_number
  project_number=$(gcloud projects describe "$project_id" --format='value(projectNumber)' 2>/dev/null) || {
    log_warn "Could not get project number for $project_id"
    echo "PLACEHOLDER_WIF_PROVIDER"
    return
  }

  echo "projects/${project_number}/locations/global/workloadIdentityPools/github-pool/providers/{WIF_PROVIDER_NAME}"
}

# -----------------------------------------------------------------------------
# Interactive Secret Setup
# -----------------------------------------------------------------------------
setup_secrets_interactive() {
  log_info ""
  log_info "Setting up secrets..."
  log_info "====================="
  log_info ""

  # Check if we can auto-detect WIF providers
  local can_auto_detect=false
  if command -v gcloud &>/dev/null; then
    can_auto_detect=true
  fi

  if [[ "$can_auto_detect" == "true" ]]; then
    log_info "Auto-detecting WIF configuration from GCP..."

    # Get WIF providers
    local wif_dev wif_staging wif_prod
    wif_dev=$(get_wif_provider "$DEV_PROJECT")
    wif_staging=$(get_wif_provider "$STAGING_PROJECT")
    wif_prod=$(get_wif_provider "$PROD_PROJECT")

    # Repository-level secrets (shared WIF provider)
    set_repo_secret "WIF_PROVIDER" "$wif_dev"

    # Environment secrets
    set_env_secret "development" "GCP_PROJECT_DEV" "$DEV_PROJECT"
    set_env_secret "development" "WIF_SA_EMAIL_DEV" "${PROJECT_PREFIX}-dev-sa@${DEV_PROJECT}.iam.gserviceaccount.com"

    set_env_secret "staging" "GCP_PROJECT_STAGING" "$STAGING_PROJECT"
    set_env_secret "staging" "WIF_SA_EMAIL_STAGING" "${PROJECT_PREFIX}-staging-sa@${STAGING_PROJECT}.iam.gserviceaccount.com"
    set_env_secret "staging" "GCP_PROJECT_DEV" "$DEV_PROJECT"  # For pulling from dev registry

    set_env_secret "production" "GCP_PROJECT_PROD" "$PROD_PROJECT"
    set_env_secret "production" "WIF_SA_EMAIL_PROD" "${PROJECT_PREFIX}-prod-sa@${PROD_PROJECT}.iam.gserviceaccount.com"
    set_env_secret "production" "GCP_PROJECT_STAGING" "$STAGING_PROJECT"  # For pulling from staging registry

  else
    log_warn "gcloud CLI not available - cannot auto-detect WIF configuration"
    log_info ""
    log_info "Please set the following secrets manually:"
    log_info ""

    cat <<EOF
Repository Secrets:
  GH_HOST=$GITHUB_HOST gh secret set WIF_PROVIDER --repo $REPO

Environment Secrets (development):
  GH_HOST=$GITHUB_HOST gh secret set GCP_PROJECT_DEV --env development --repo $REPO
  GH_HOST=$GITHUB_HOST gh secret set WIF_SA_EMAIL_DEV --env development --repo $REPO

Environment Secrets (staging):
  GH_HOST=$GITHUB_HOST gh secret set GCP_PROJECT_STAGING --env staging --repo $REPO
  GH_HOST=$GITHUB_HOST gh secret set WIF_SA_EMAIL_STAGING --env staging --repo $REPO

Environment Secrets (production):
  GH_HOST=$GITHUB_HOST gh secret set GCP_PROJECT_PROD --env production --repo $REPO
  GH_HOST=$GITHUB_HOST gh secret set WIF_SA_EMAIL_PROD --env production --repo $REPO
EOF
  fi
}

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
print_summary() {
  log_info ""
  log_info "======================================="
  log_info "GitHub Environment Setup Complete!"
  log_info "======================================="
  log_info ""

  cat <<EOF
Environments configured:

  development:
    - Auto-deploy on merge to main
    - No approval required
    - Wait timer: 0 minutes

  staging:
    - Triggered after dev deployment succeeds
    - No approval required
    - Wait timer: 5 minutes

  production:
    - Manual workflow_dispatch only
    - Required reviewers: ${PROD_REVIEWERS}
    - Wait timer: 10 minutes
    - Deployment window: Mon-Thu 10am-4pm EST

Verify configuration:
  GH_HOST=$GITHUB_HOST gh api /repos/${REPO}/environments

Test deployment:
  GH_HOST=$GITHUB_HOST gh workflow run deploy-dev.yml
EOF
}

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
main() {
  log_info "AI Cost Monitoring - GitHub Environment Setup"
  log_info "=============================================="

  validate_prerequisites

  # Create environments
  create_environment "development" 0 ""
  create_environment "staging" 5 ""
  create_environment "production" 10 "$PROD_REVIEWERS"

  # Setup secrets
  setup_secrets_interactive

  # Print summary
  print_summary
}

main "$@"
