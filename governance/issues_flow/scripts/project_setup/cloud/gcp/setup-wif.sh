#!/usr/bin/env bash
#
# setup-wif.sh - Configure Workload Identity Federation for GitHub Actions
#
# Usage:
#   ./setup-wif.sh [--dry-run]
#
# Prerequisites:
#   - GCP projects created (run setup-projects.sh first)
#   - gcloud CLI authenticated with project owner permissions
#
# This script configures:
#   - Workload Identity Pool for GitHub
#   - Workload Identity Provider for GitHub OIDC
#   - Service account bindings for WIF

set -euo pipefail

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
readonly PROJECT_PREFIX="{PROJECT_PREFIX}"
readonly POOL_NAME="github-pool"
readonly PROVIDER_NAME="{WIF_PROVIDER_NAME}"
readonly GITHUB_ORG="{GITHUB_ORG}"
readonly GITHUB_REPO="{REPO_NAME}"

# Projects
readonly DEV_PROJECT="${PROJECT_PREFIX}-dev"
readonly STAGING_PROJECT="${PROJECT_PREFIX}-staging"
readonly PROD_PROJECT="${PROJECT_PREFIX}-prod"

DRY_RUN="${1:-}"

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
log_info() { echo "[INFO] $*"; }
log_warn() { echo "[WARN] $*" >&2; }
log_error() { echo "[ERROR] $*" >&2; }

run_cmd() {
  if [[ "$DRY_RUN" == "--dry-run" ]]; then
    echo "[DRY-RUN] $*"
  else
    "$@"
  fi
}

# -----------------------------------------------------------------------------
# Create Workload Identity Pool
# -----------------------------------------------------------------------------
create_wif_pool() {
  local project_id="$1"

  log_info "Creating Workload Identity Pool in $project_id"

  local pool_id="${POOL_NAME}"

  # Check if pool exists
  if gcloud iam workload-identity-pools describe "$pool_id" \
    --project="$project_id" \
    --location="global" &>/dev/null 2>&1; then
    log_info "Pool $pool_id already exists"
    return 0
  fi

  run_cmd gcloud iam workload-identity-pools create "$pool_id" \
    --project="$project_id" \
    --location="global" \
    --display-name="GitHub Actions Pool" \
    --description="Workload Identity Pool for GitHub Actions CI/CD"
}

# -----------------------------------------------------------------------------
# Create Workload Identity Provider
# -----------------------------------------------------------------------------
create_wif_provider() {
  local project_id="$1"

  log_info "Creating Workload Identity Provider in $project_id"

  local provider_id="${PROVIDER_NAME}"
  local pool_id="${POOL_NAME}"

  # Check if provider exists
  if gcloud iam workload-identity-pools providers describe "$provider_id" \
    --workload-identity-pool="$pool_id" \
    --project="$project_id" \
    --location="global" &>/dev/null 2>&1; then
    log_info "Provider $provider_id already exists"
    return 0
  fi

  # GitHub OIDC configuration
  # Attribute mapping: extract repo, ref, actor from GitHub token
  run_cmd gcloud iam workload-identity-pools providers create-oidc "$provider_id" \
    --project="$project_id" \
    --location="global" \
    --workload-identity-pool="$pool_id" \
    --display-name="GitHub Provider" \
    --description="OIDC provider for GitHub Actions" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner,attribute.ref=assertion.ref" \
    --attribute-condition="assertion.repository_owner == '${GITHUB_ORG}'"
}

# -----------------------------------------------------------------------------
# Bind Service Account to WIF
# -----------------------------------------------------------------------------
bind_service_account() {
  local project_id="$1"
  local env_name="$2"

  log_info "Binding service account to WIF for $project_id"

  local sa_name="${PROJECT_PREFIX}-${env_name}-sa"
  local sa_email="${sa_name}@${project_id}.iam.gserviceaccount.com"
  local pool_name="projects/${project_id}/locations/global/workloadIdentityPools/${POOL_NAME}"

  # Principal set for the specific repository
  local principal="principalSet://iam.googleapis.com/${pool_name}/attribute.repository/${GITHUB_ORG}/${GITHUB_REPO}"

  # Allow the GitHub Actions workflow to impersonate the service account
  run_cmd gcloud iam service-accounts add-iam-policy-binding "$sa_email" \
    --project="$project_id" \
    --role="roles/iam.workloadIdentityUser" \
    --member="$principal"

  log_info "Bound $principal to $sa_email"
}

# -----------------------------------------------------------------------------
# Output Configuration
# -----------------------------------------------------------------------------
output_config() {
  local project_id="$1"
  local env_name="$2"

  local project_number
  project_number=$(gcloud projects describe "$project_id" --format='value(projectNumber)')

  local wif_provider="projects/${project_number}/locations/global/workloadIdentityPools/${POOL_NAME}/providers/${PROVIDER_NAME}"
  local sa_email="${PROJECT_PREFIX}-${env_name}-sa@${project_id}.iam.gserviceaccount.com"

  cat <<EOF

=== ${env_name^^} Environment Configuration ===

GitHub Secrets to configure:
  WIF_PROVIDER:         ${wif_provider}
  WIF_SA_EMAIL_${env_name^^}:  ${sa_email}
  GCP_PROJECT_${env_name^^}:   ${project_id}

EOF
}

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
main() {
  log_info "AI Cost Monitoring - WIF Setup"
  log_info "==============================="

  if [[ "$DRY_RUN" == "--dry-run" ]]; then
    log_info "Running in DRY-RUN mode"
  fi

  # Setup WIF for each environment
  for project_env in "$DEV_PROJECT:dev" "$STAGING_PROJECT:staging" "$PROD_PROJECT:prod"; do
    IFS=':' read -r project_id env_name <<< "$project_env"

    log_info ""
    log_info "Setting up WIF for $project_id ($env_name)"
    log_info "-------------------------------------------"

    create_wif_pool "$project_id"
    create_wif_provider "$project_id"
    bind_service_account "$project_id" "$env_name"
    output_config "$project_id" "$env_name"
  done

  log_info ""
  log_info "==============================="
  log_info "WIF setup complete!"
  log_info ""
  log_info "Next steps:"
  log_info "  1. Add the GitHub secrets listed above to your repository"
  log_info "  2. Configure GitHub environments (development, staging, production)"
  log_info "  3. Test with a workflow_dispatch trigger"
}

main "$@"
