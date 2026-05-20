#!/bin/bash
# Setup GCP prerequisites for the AI PR Review workflow (IPLAN-003 H1-H5).
#
# Creates: Vertex AI API enablement, WIF pool/provider, service account,
#          IAM bindings, and sets GitHub repo secrets.
#
# Prerequisites:
#   1. gcloud CLI installed and authenticated with sufficient permissions:
#      - roles/iam.workloadIdentityPoolAdmin (or roles/owner)
#      - roles/iam.serviceAccountAdmin
#      - roles/resourcemanager.projectIamAdmin
#      - roles/serviceusage.serviceUsageAdmin
#   2. gh CLI installed and authenticated to {GITHUB_HOST}
#   3. jq installed
#
# Usage:
#   ./scripts/project_setup/gcp/setup-ai-review-gcp.sh --project=my-gcp-project
#   ./scripts/project_setup/gcp/setup-ai-review-gcp.sh --project=my-gcp-project --dry-run
#   ./scripts/project_setup/gcp/setup-ai-review-gcp.sh --project=my-gcp-project --repo-scope=single
#   ./scripts/project_setup/gcp/setup-ai-review-gcp.sh --verify-only --project=my-gcp-project
#
# Reference:
#   - Docs: governance/AI_PR_Review/README.md
#   - ADR-002: docs/adr/002-gcp-only-first.md (WIF auth, no SA keys)
#   - ADR-009: docs/adr/009-ai-pr-review-custom-workflow.md

set -euo pipefail

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
readonly GHES_HOST="{GITHUB_HOST}"
readonly GHES_ORG="{GITHUB_ORG}"
readonly GHES_REPO="{REPO_NAME}"
readonly GHES_ISSUER="https://${GHES_HOST}/_services/token"

# All repos that use the reusable AI review workflow.
# Monorepo only - all components are in {REPO_NAME}.
readonly ALL_REPOS=(
    "{REPO_NAME}"
)

readonly SA_NAME="{PROJECT_PREFIX}-ai-reviewer"
readonly SA_DISPLAY="AI PR Review (GHES Actions)"
readonly SA_DESCRIPTION="Used by GitHub Actions ai-review.yml workflow to call Vertex AI"

readonly WIF_POOL="{WIF_POOL_NAME}"
readonly WIF_POOL_DISPLAY="GitHub Actions Pool"
readonly WIF_POOL_DESCRIPTION="WIF pool for GitHub Enterprise Server Actions"

readonly WIF_PROVIDER="{WIF_PROVIDER_NAME}"
readonly WIF_ATTR_MAPPING="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.actor=assertion.actor"
readonly WIF_ATTR_CONDITION="assertion.repository_owner == '${GHES_ORG}'"

readonly IAM_ROLE="roles/aiplatform.user"
readonly WIF_REGION="us-central1"

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
GCP_PROJECT_ID=""
DRY_RUN=false
VERIFY_ONLY=false
REPO_SCOPE="org"  # "org" or "single"
SKIP_SECRETS=false

# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'  # No Color

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
log_step()  { echo -e "\n${BLUE}[STEP]${NC} $1"; }
log_ok()    { echo -e "  ${GREEN}OK${NC}  $1"; }
log_skip()  { echo -e "  ${YELLOW}SKIP${NC} $1"; }
log_fail()  { echo -e "  ${RED}FAIL${NC} $1"; }
log_info()  { echo -e "  ${BLUE}INFO${NC} $1"; }
log_dry()   { echo -e "  ${YELLOW}DRY${NC}  $1"; }

die() { echo -e "${RED}Error:${NC} $1" >&2; exit 1; }

run_cmd() {
    # Execute a command or print it in dry-run mode.
    if $DRY_RUN; then
        log_dry "$*"
        return 0
    fi
    "$@"
}

check_tool() {
    if ! command -v "$1" &>/dev/null; then
        die "$1 is required but not installed."
    fi
}

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------
usage() {
    cat <<USAGE
Usage: $0 --project=<GCP_PROJECT_ID> [OPTIONS]

Required:
  --project=ID          GCP project ID

Options:
  --dry-run             Print commands without executing
  --verify-only         Only run verification checks (no changes)
  --repo-scope=SCOPE    WIF binding scope: "org" (default) or "single"
                        org    = all repos in ${GHES_ORG}
                        single = only ${GHES_ORG}/${GHES_REPO}
  --skip-secrets        Skip GitHub secret creation (H4-H5)
  -h, --help            Show this help

Examples:
  $0 --project=my-gcp-project
  $0 --project=my-gcp-project --dry-run
  $0 --project=my-gcp-project --repo-scope=single
  $0 --verify-only --project=my-gcp-project
USAGE
    exit 0
}

for arg in "$@"; do
    case $arg in
        --project=*)    GCP_PROJECT_ID="${arg#*=}" ;;
        --dry-run)      DRY_RUN=true ;;
        --verify-only)  VERIFY_ONLY=true ;;
        --repo-scope=*) REPO_SCOPE="${arg#*=}" ;;
        --skip-secrets) SKIP_SECRETS=true ;;
        -h|--help)      usage ;;
        *)              die "Unknown argument: $arg" ;;
    esac
done

[ -z "$GCP_PROJECT_ID" ] && die "--project is required. Run with -h for usage."
[[ "$REPO_SCOPE" != "org" && "$REPO_SCOPE" != "single" ]] && die "--repo-scope must be 'org' or 'single'"

SA_EMAIL="${SA_NAME}@${GCP_PROJECT_ID}.iam.gserviceaccount.com"

# ---------------------------------------------------------------------------
# Pre-flight checks
# ---------------------------------------------------------------------------
echo "============================================="
echo " AI PR Review — GCP Setup (IPLAN-003 H1-H5)"
echo "============================================="
echo ""
echo " Project:     $GCP_PROJECT_ID"
echo " SA:          $SA_EMAIL"
echo " WIF Pool:    $WIF_POOL"
echo " WIF Provider:$WIF_PROVIDER"
echo " Repo Scope:  $REPO_SCOPE"
echo " GHES Issuer: $GHES_ISSUER"
echo " Dry Run:     $DRY_RUN"
echo " Verify Only: $VERIFY_ONLY"
echo ""

check_tool gcloud
check_tool jq
if ! $SKIP_SECRETS; then
    check_tool gh
fi

# Verify gcloud auth
log_step "Pre-flight: verifying gcloud authentication"
ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null || true)
if [ -z "$ACTIVE_ACCOUNT" ]; then
    die "No active gcloud account. Run: gcloud auth login"
fi
log_ok "Authenticated as $ACTIVE_ACCOUNT"

# Verify project exists
gcloud projects describe "$GCP_PROJECT_ID" --format="value(projectId)" &>/dev/null \
    || die "Cannot access project $GCP_PROJECT_ID. Check permissions or project ID."
log_ok "Project $GCP_PROJECT_ID accessible"

# Get project number (needed for WIF provider resource name)
PROJECT_NUMBER=$(gcloud projects describe "$GCP_PROJECT_ID" --format="value(projectNumber)")
log_info "Project number: $PROJECT_NUMBER"

if $VERIFY_ONLY; then
    # Jump to verification
    echo ""
    echo "=== Verification Mode ==="
    echo ""
fi

# ---------------------------------------------------------------------------
# H1: Enable Vertex AI API
# ---------------------------------------------------------------------------
log_step "H1: Enable Vertex AI API"

API_ENABLED=$(gcloud services list --enabled \
    --filter="name:aiplatform.googleapis.com" \
    --project="$GCP_PROJECT_ID" \
    --format="value(name)" 2>/dev/null || true)

if [ "$API_ENABLED" = "aiplatform.googleapis.com" ]; then
    log_ok "aiplatform.googleapis.com already enabled"
elif $VERIFY_ONLY; then
    log_fail "aiplatform.googleapis.com is NOT enabled"
else
    run_cmd gcloud services enable aiplatform.googleapis.com --project="$GCP_PROJECT_ID"
    log_ok "aiplatform.googleapis.com enabled"
fi

# ---------------------------------------------------------------------------
# H2a: Create service account
# ---------------------------------------------------------------------------
log_step "H2a: Create service account ($SA_NAME)"

SA_EXISTS=$(gcloud iam service-accounts list \
    --filter="email:${SA_EMAIL}" \
    --project="$GCP_PROJECT_ID" \
    --format="value(email)" 2>/dev/null || true)

if [ "$SA_EXISTS" = "$SA_EMAIL" ]; then
    log_ok "Service account already exists: $SA_EMAIL"
elif $VERIFY_ONLY; then
    log_fail "Service account $SA_EMAIL does NOT exist"
else
    run_cmd gcloud iam service-accounts create "$SA_NAME" \
        --display-name="$SA_DISPLAY" \
        --description="$SA_DESCRIPTION" \
        --project="$GCP_PROJECT_ID"
    log_ok "Service account created: $SA_EMAIL"
fi

# ---------------------------------------------------------------------------
# H2b: Create Workload Identity Pool
# ---------------------------------------------------------------------------
log_step "H2b: Create Workload Identity Pool ($WIF_POOL)"

POOL_EXISTS=$(gcloud iam workload-identity-pools describe "$WIF_POOL" \
    --location="global" \
    --project="$GCP_PROJECT_ID" \
    --format="value(name)" 2>/dev/null || true)

if [ -n "$POOL_EXISTS" ]; then
    log_ok "WIF pool already exists: $WIF_POOL"
elif $VERIFY_ONLY; then
    log_fail "WIF pool $WIF_POOL does NOT exist"
else
    run_cmd gcloud iam workload-identity-pools create "$WIF_POOL" \
        --location="global" \
        --display-name="$WIF_POOL_DISPLAY" \
        --description="$WIF_POOL_DESCRIPTION" \
        --project="$GCP_PROJECT_ID"
    log_ok "WIF pool created: $WIF_POOL"
fi

# ---------------------------------------------------------------------------
# H2c: Create Workload Identity Provider (OIDC)
# ---------------------------------------------------------------------------
log_step "H2c: Create Workload Identity Provider ($WIF_PROVIDER)"

PROVIDER_EXISTS=$(gcloud iam workload-identity-pools providers describe "$WIF_PROVIDER" \
    --location="global" \
    --workload-identity-pool="$WIF_POOL" \
    --project="$GCP_PROJECT_ID" \
    --format="value(name)" 2>/dev/null || true)

if [ -n "$PROVIDER_EXISTS" ]; then
    log_ok "WIF provider already exists: $WIF_PROVIDER"
elif $VERIFY_ONLY; then
    log_fail "WIF provider $WIF_PROVIDER does NOT exist"
else
    run_cmd gcloud iam workload-identity-pools providers create-oidc "$WIF_PROVIDER" \
        --location="global" \
        --workload-identity-pool="$WIF_POOL" \
        --issuer-uri="$GHES_ISSUER" \
        --attribute-mapping="$WIF_ATTR_MAPPING" \
        --attribute-condition="$WIF_ATTR_CONDITION" \
        --project="$GCP_PROJECT_ID"
    log_ok "WIF provider created: $WIF_PROVIDER"
fi

# Get the full pool resource name for IAM binding
POOL_RESOURCE=$(gcloud iam workload-identity-pools describe "$WIF_POOL" \
    --location="global" \
    --project="$GCP_PROJECT_ID" \
    --format="value(name)" 2>/dev/null || true)

if [ -z "$POOL_RESOURCE" ] && ! $DRY_RUN; then
    log_fail "Cannot resolve pool resource name — pool may not exist yet"
fi

# ---------------------------------------------------------------------------
# H2d: IAM binding — allow provider to impersonate SA
# ---------------------------------------------------------------------------
log_step "H2d: Bind WIF provider → service account (scope: $REPO_SCOPE)"

if [ "$REPO_SCOPE" = "single" ]; then
    MEMBER="principalSet://iam.googleapis.com/${POOL_RESOURCE}/attribute.repository/${GHES_ORG}/${GHES_REPO}"
else
    MEMBER="principalSet://iam.googleapis.com/${POOL_RESOURCE}/attribute.repository_owner/${GHES_ORG}"
fi

if $VERIFY_ONLY; then
    # Check if binding exists
    BINDING_CHECK=$(gcloud iam service-accounts get-iam-policy "$SA_EMAIL" \
        --project="$GCP_PROJECT_ID" \
        --format=json 2>/dev/null | jq -r --arg m "$MEMBER" \
        '.bindings[]? | select(.role == "roles/iam.workloadIdentityUser") | .members[]? | select(. == $m)' 2>/dev/null || true)
    if [ -n "$BINDING_CHECK" ]; then
        log_ok "IAM binding exists: workloadIdentityUser for $REPO_SCOPE scope"
    else
        log_fail "IAM binding MISSING for $MEMBER"
    fi
else
    run_cmd gcloud iam service-accounts add-iam-policy-binding "$SA_EMAIL" \
        --role="roles/iam.workloadIdentityUser" \
        --member="$MEMBER" \
        --project="$GCP_PROJECT_ID"
    log_ok "IAM binding set: workloadIdentityUser ($REPO_SCOPE scope)"
fi

# ---------------------------------------------------------------------------
# H3: Grant Vertex AI User role to service account
# ---------------------------------------------------------------------------
log_step "H3: Grant $IAM_ROLE to service account"

if $VERIFY_ONLY; then
    ROLE_CHECK=$(gcloud projects get-iam-policy "$GCP_PROJECT_ID" \
        --flatten="bindings[].members" \
        --filter="bindings.members:serviceAccount:${SA_EMAIL} AND bindings.role:${IAM_ROLE}" \
        --format="value(bindings.role)" 2>/dev/null || true)
    if [ "$ROLE_CHECK" = "$IAM_ROLE" ]; then
        log_ok "$IAM_ROLE granted to $SA_EMAIL"
    else
        log_fail "$IAM_ROLE NOT granted to $SA_EMAIL"
    fi
else
    run_cmd gcloud projects add-iam-policy-binding "$GCP_PROJECT_ID" \
        --member="serviceAccount:${SA_EMAIL}" \
        --role="$IAM_ROLE" \
        --condition=None
    log_ok "$IAM_ROLE granted to $SA_EMAIL"
fi

# ---------------------------------------------------------------------------
# H4-H5: Set GitHub repo secrets (all repos)
# ---------------------------------------------------------------------------
if $SKIP_SECRETS; then
    log_step "H4-H5: Skipped (--skip-secrets)"
else
    export GH_HOST="$GHES_HOST"

    # Verify gh auth
    log_step "H4-H5: Set GitHub repo secrets (${#ALL_REPOS[@]} repos)"
    GH_AUTH=$(GH_HOST=$GHES_HOST gh auth status 2>&1 || true)
    if echo "$GH_AUTH" | grep -q "Logged in"; then
        log_ok "gh authenticated to $GHES_HOST"
    else
        die "gh not authenticated to $GHES_HOST. Run: GH_HOST=$GHES_HOST gh auth login"
    fi

    # Resolve WIF provider full resource name
    PROVIDER_RESOURCE=$(gcloud iam workload-identity-pools providers describe "$WIF_PROVIDER" \
        --location="global" \
        --workload-identity-pool="$WIF_POOL" \
        --project="$GCP_PROJECT_ID" \
        --format="value(name)" 2>/dev/null || true)

    if [ -z "$PROVIDER_RESOURCE" ] && ! $DRY_RUN; then
        log_fail "Cannot resolve provider resource name — run GCP steps first"
    fi

    # Push secrets to each repo
    SECRETS_OK=0
    SECRETS_FAIL=0
    for repo in "${ALL_REPOS[@]}"; do
        FULL_REPO="${GHES_ORG}/${repo}"
        log_info "--- ${repo} ---"

        # Check repo exists
        if ! $DRY_RUN; then
            REPO_CHECK=$(GH_HOST=$GHES_HOST gh repo view "$FULL_REPO" --json name --jq '.name' 2>/dev/null || true)
            if [ -z "$REPO_CHECK" ]; then
                log_skip "$repo — repo not found (will be created later)"
                continue
            fi
        fi

        if $VERIFY_ONLY; then
            SECRET_LIST=$(GH_HOST=$GHES_HOST gh secret list --repo "$FULL_REPO" 2>/dev/null || true)
            for secret_name in WIF_PROVIDER WIF_SA_EMAIL GCP_PROJECT_ID; do
                if echo "$SECRET_LIST" | grep -q "$secret_name"; then
                    log_ok "$repo: $secret_name exists"
                    ((SECRETS_OK++))
                else
                    log_fail "$repo: $secret_name MISSING"
                    ((SECRETS_FAIL++))
                fi
            done
        else
            for secret_name in WIF_PROVIDER WIF_SA_EMAIL GCP_PROJECT_ID; do
                case $secret_name in
                    WIF_PROVIDER)   secret_value="$PROVIDER_RESOURCE" ;;
                    WIF_SA_EMAIL)   secret_value="$SA_EMAIL" ;;
                    GCP_PROJECT_ID) secret_value="$GCP_PROJECT_ID" ;;
                esac

                if $DRY_RUN; then
                    log_dry "gh secret set $secret_name --repo $FULL_REPO"
                    ((SECRETS_OK++))
                else
                    if echo -n "$secret_value" | GH_HOST=$GHES_HOST gh secret set "$secret_name" \
                        --repo "$FULL_REPO" 2>/dev/null; then
                        log_ok "$repo: $secret_name set"
                        ((SECRETS_OK++))
                    else
                        log_fail "$repo: $secret_name failed"
                        ((SECRETS_FAIL++))
                    fi
                fi
            done
        fi
    done

    echo ""
    log_info "Secrets: $SECRETS_OK set, $SECRETS_FAIL failed"
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "============================================="
if $VERIFY_ONLY; then
    echo " Verification complete"
elif $DRY_RUN; then
    echo " Dry run complete — no changes made"
else
    echo " Setup complete"
fi
echo "============================================="
echo ""
echo " Service Account: $SA_EMAIL"
echo " WIF Pool:        projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$WIF_POOL"
echo " WIF Provider:    projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$WIF_POOL/providers/$WIF_PROVIDER"
echo " IAM Role:        $IAM_ROLE"
echo " Repo Scope:      $REPO_SCOPE"
echo ""

echo " Repos with secrets:"
for repo in "${ALL_REPOS[@]}"; do
    echo "   - ${GHES_ORG}/${repo}"
done
echo ""

if ! $VERIFY_ONLY && ! $DRY_RUN; then
    echo " Next steps:"
    echo "   1. Verify GHES OIDC is enabled:"
    echo "      GHES Admin -> Actions -> General -> OpenID Connect"
    echo "      Issuer URL: $GHES_ISSUER"
    echo ""
    echo "   2. Add caller workflow to each component repo:"
    echo "      .github/workflows/ai-review.yml (see ai-review-reusable.yml header)"
    echo ""
    echo "   3. Run verification:"
    echo "      $0 --verify-only --project=$GCP_PROJECT_ID"
    echo ""
    echo "   4. Test by opening a PR on ${GHES_ORG}/${GHES_REPO}"
    echo ""
fi
