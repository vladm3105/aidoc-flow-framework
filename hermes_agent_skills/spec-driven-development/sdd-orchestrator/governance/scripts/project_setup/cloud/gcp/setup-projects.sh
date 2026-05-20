#!/usr/bin/env bash
#
# setup-projects.sh - Create and configure GCP projects for {PROJECT_PREFIX}
#
# Usage:
#   ./setup-projects.sh [--dry-run]
#
# Prerequisites:
#   - gcloud CLI installed and authenticated
#   - Billing account with permissions to link projects
#   - Organization admin permissions (or project creator role)
#
# This script creates three GCP projects:
#   - {GCP_PROJECT_DEV} (development)
#   - {GCP_PROJECT_STAGING} (pre-production)
#   - {GCP_PROJECT_PROD} (production)

set -euo pipefail

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_PREFIX="{PROJECT_PREFIX}"
readonly REGION="{GCP_REGION}"

# Project IDs - customize if needed
readonly DEV_PROJECT="${PROJECT_PREFIX}-dev"
readonly STAGING_PROJECT="${PROJECT_PREFIX}-staging"
readonly PROD_PROJECT="${PROJECT_PREFIX}-prod"

# Billing account - MUST be set
BILLING_ACCOUNT="${BILLING_ACCOUNT:-}"

# Organization (optional - leave empty for standalone projects)
ORGANIZATION_ID="${ORGANIZATION_ID:-}"

# Dry run mode
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
# Validation
# -----------------------------------------------------------------------------
validate_prerequisites() {
  log_info "Validating prerequisites..."

  if ! command -v gcloud &>/dev/null; then
    log_error "gcloud CLI not found. Install: https://cloud.google.com/sdk/docs/install"
    exit 1
  fi

  if [[ -z "$BILLING_ACCOUNT" ]]; then
    log_error "BILLING_ACCOUNT environment variable not set"
    log_info "List billing accounts: gcloud billing accounts list"
    exit 1
  fi

  # Verify billing account access
  if ! gcloud billing accounts describe "$BILLING_ACCOUNT" &>/dev/null; then
    log_error "Cannot access billing account: $BILLING_ACCOUNT"
    exit 1
  fi

  log_info "Prerequisites validated"
}

# -----------------------------------------------------------------------------
# Project Creation
# -----------------------------------------------------------------------------
create_project() {
  local project_id="$1"
  local display_name="$2"

  log_info "Creating project: $project_id"

  if gcloud projects describe "$project_id" &>/dev/null; then
    log_info "Project $project_id already exists, skipping creation"
    return 0
  fi

  local create_args=("projects" "create" "$project_id" "--name=$display_name")

  if [[ -n "$ORGANIZATION_ID" ]]; then
    create_args+=("--organization=$ORGANIZATION_ID")
  fi

  run_cmd gcloud "${create_args[@]}"

  # Link billing account
  log_info "Linking billing account to $project_id"
  run_cmd gcloud billing projects link "$project_id" \
    --billing-account="$BILLING_ACCOUNT"
}

# -----------------------------------------------------------------------------
# Enable APIs
# -----------------------------------------------------------------------------
enable_apis() {
  local project_id="$1"

  log_info "Enabling APIs for $project_id"

  local apis=(
    "run.googleapis.com"                  # Cloud Run
    "cloudbuild.googleapis.com"           # Cloud Build
    "artifactregistry.googleapis.com"     # Artifact Registry
    "containerregistry.googleapis.com"    # Container Registry
    "firestore.googleapis.com"            # Firestore
    "pubsub.googleapis.com"               # Pub/Sub
    "cloudfunctions.googleapis.com"       # Cloud Functions
    "cloudscheduler.googleapis.com"       # Cloud Scheduler
    "monitoring.googleapis.com"           # Cloud Monitoring
    "logging.googleapis.com"              # Cloud Logging
    "secretmanager.googleapis.com"        # Secret Manager
    "iam.googleapis.com"                  # IAM
    "iamcredentials.googleapis.com"       # IAM Credentials
    "sts.googleapis.com"                  # Security Token Service (WIF)
    "cloudresourcemanager.googleapis.com" # Resource Manager
    "billingbudgets.googleapis.com"       # Budget alerts
    "recommender.googleapis.com"          # Recommender (idle resources)
    "bigquery.googleapis.com"             # BigQuery (analytics)
  )

  for api in "${apis[@]}"; do
    log_info "  Enabling $api"
    run_cmd gcloud services enable "$api" --project="$project_id"
  done
}

# -----------------------------------------------------------------------------
# Create Service Accounts
# -----------------------------------------------------------------------------
create_service_accounts() {
  local project_id="$1"
  local env_name="$2"

  log_info "Creating service accounts for $project_id"

  local sa_name="${PROJECT_PREFIX}-${env_name}-sa"
  local sa_email="${sa_name}@${project_id}.iam.gserviceaccount.com"

  # Check if SA exists
  if gcloud iam service-accounts describe "$sa_email" --project="$project_id" &>/dev/null; then
    log_info "Service account $sa_name already exists"
    return 0
  fi

  run_cmd gcloud iam service-accounts create "$sa_name" \
    --project="$project_id" \
    --display-name="AI Cost Monitoring ${env_name} Service Account"

  # Grant roles
  local roles=(
    "roles/run.invoker"
    "roles/run.developer"
    "roles/datastore.user"
    "roles/pubsub.editor"
    "roles/logging.logWriter"
    "roles/monitoring.metricWriter"
    "roles/secretmanager.secretAccessor"
    "roles/bigquery.dataEditor"
    "roles/bigquery.jobUser"
  )

  for role in "${roles[@]}"; do
    log_info "  Granting $role to $sa_email"
    run_cmd gcloud projects add-iam-policy-binding "$project_id" \
      --member="serviceAccount:$sa_email" \
      --role="$role" \
      --condition=None
  done
}

# -----------------------------------------------------------------------------
# Configure Firestore
# -----------------------------------------------------------------------------
configure_firestore() {
  local project_id="$1"

  log_info "Configuring Firestore for $project_id"

  # Check if Firestore is already configured
  if gcloud firestore databases describe --project="$project_id" &>/dev/null 2>&1; then
    log_info "Firestore already configured for $project_id"
    return 0
  fi

  run_cmd gcloud firestore databases create \
    --project="$project_id" \
    --location="nam5" \
    --type="firestore-native"
}

# -----------------------------------------------------------------------------
# Create Budget Alerts
# -----------------------------------------------------------------------------
create_budget() {
  local project_id="$1"
  local budget_amount="$2"
  local display_name="$3"

  log_info "Creating budget alert for $project_id: \$${budget_amount}/month"

  # Budget creation requires billing API
  # This is a simplified version - use Terraform for production
  cat <<EOF
[MANUAL STEP] Create budget alert:
  gcloud billing budgets create \\
    --billing-account=${BILLING_ACCOUNT} \\
    --display-name="${display_name}" \\
    --budget-amount=${budget_amount}USD \\
    --filter-projects=projects/${project_id} \\
    --threshold-rule=percent=0.5,basis=CURRENT_SPEND \\
    --threshold-rule=percent=0.8,basis=CURRENT_SPEND \\
    --threshold-rule=percent=1.0,basis=CURRENT_SPEND
EOF
}

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
main() {
  log_info "AI Cost Monitoring - GCP Project Setup"
  log_info "======================================="

  validate_prerequisites

  if [[ "$DRY_RUN" == "--dry-run" ]]; then
    log_info "Running in DRY-RUN mode - no changes will be made"
  fi

  # Create projects
  create_project "$DEV_PROJECT" "AI Cost Monitoring - Development"
  create_project "$STAGING_PROJECT" "AI Cost Monitoring - Staging"
  create_project "$PROD_PROJECT" "AI Cost Monitoring - Production"

  # Enable APIs
  for project in "$DEV_PROJECT" "$STAGING_PROJECT" "$PROD_PROJECT"; do
    enable_apis "$project"
  done

  # Create service accounts
  create_service_accounts "$DEV_PROJECT" "dev"
  create_service_accounts "$STAGING_PROJECT" "staging"
  create_service_accounts "$PROD_PROJECT" "prod"

  # Configure Firestore
  for project in "$DEV_PROJECT" "$STAGING_PROJECT" "$PROD_PROJECT"; do
    configure_firestore "$project"
  done

  # Budget alerts
  create_budget "$DEV_PROJECT" "100" "AI Cost Monitoring Dev Budget"
  create_budget "$STAGING_PROJECT" "200" "AI Cost Monitoring Staging Budget"
  create_budget "$PROD_PROJECT" "2000" "AI Cost Monitoring Prod Budget"

  log_info ""
  log_info "======================================="
  log_info "Project setup complete!"
  log_info ""
  log_info "Projects created:"
  log_info "  - Development: $DEV_PROJECT"
  log_info "  - Staging:     $STAGING_PROJECT"
  log_info "  - Production:  $PROD_PROJECT"
  log_info ""
  log_info "Next steps:"
  log_info "  1. Run ./setup-wif.sh to configure Workload Identity Federation"
  log_info "  2. Run ./setup-environments.sh to configure GitHub environments"
  log_info "  3. Review and apply budget alerts (manual step above)"
}

main "$@"
