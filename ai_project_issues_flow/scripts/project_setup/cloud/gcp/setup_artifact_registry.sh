#!/usr/bin/env bash
# Setup Artifact Registry repositories for AIOCTO environments
# Phase 5 - GCP Configuration
#
# Prerequisites:
#   - gcloud CLI authenticated with appropriate permissions
#   - Artifact Registry API enabled
#
# Usage:
#   ./scripts/project_setup/gcp/setup_artifact_registry.sh [--project PROJECT_ID] [--region REGION]

set -euo pipefail

# Defaults
PROJECT_ID="${GCP_PROJECT:-}"
REGION="${GCP_REGION:-{GCP_REGION}}"
REPOS=("{GCP_PROJECT_DEV}" "{GCP_PROJECT_STAGING}" "{GCP_PROJECT_PROD}")

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --project)
            PROJECT_ID="$2"
            shift 2
            ;;
        --region)
            REGION="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [--project PROJECT_ID] [--region REGION]"
            echo ""
            echo "Creates Artifact Registry repositories for {PROJECT_PREFIX} environments:"
            echo "  - {GCP_PROJECT_DEV} (development)"
            echo "  - {GCP_PROJECT_STAGING} (staging)"
            echo "  - {GCP_PROJECT_PROD} (production)"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [[ -z "$PROJECT_ID" ]]; then
    echo "Error: PROJECT_ID not set. Use --project or set GCP_PROJECT env var."
    exit 1
fi

echo "=== AIOCTO Artifact Registry Setup ==="
echo "Project: $PROJECT_ID"
echo "Region:  $REGION"
echo ""

# Enable Artifact Registry API
echo "Enabling Artifact Registry API..."
gcloud services enable artifactregistry.googleapis.com --project="$PROJECT_ID" --quiet

# Create repositories
for REPO in "${REPOS[@]}"; do
    echo ""
    echo "Creating repository: $REPO"

    if gcloud artifacts repositories describe "$REPO" \
        --project="$PROJECT_ID" \
        --location="$REGION" \
        --format="value(name)" 2>/dev/null; then
        echo "  Repository $REPO already exists, skipping."
    else
        gcloud artifacts repositories create "$REPO" \
            --project="$PROJECT_ID" \
            --location="$REGION" \
            --repository-format=docker \
            --description="AIOCTO Docker images for ${REPO#{PROJECT_PREFIX}-} environment" \
            --labels="environment=${REPO#{PROJECT_PREFIX}-},project={PROJECT_PREFIX}"
        echo "  Created $REPO"
    fi
done

# Configure repository cleanup policies
echo ""
echo "Configuring cleanup policies..."
for REPO in "${REPOS[@]}"; do
    # Keep last 10 versions per tag, delete untagged after 7 days
    cat > /tmp/cleanup-policy-${REPO}.json <<EOF
{
  "cleanupPolicies": [
    {
      "id": "keep-minimum-versions",
      "action": "KEEP",
      "condition": {
        "tagState": "TAGGED",
        "versionNamePrefixes": ["phase-", "v"]
      },
      "mostRecentVersions": {
        "keepCount": 10
      }
    },
    {
      "id": "delete-old-untagged",
      "action": "DELETE",
      "condition": {
        "tagState": "UNTAGGED",
        "olderThan": "7d"
      }
    }
  ]
}
EOF

    gcloud artifacts repositories set-cleanup-policies "$REPO" \
        --project="$PROJECT_ID" \
        --location="$REGION" \
        --policy=/tmp/cleanup-policy-${REPO}.json \
        --quiet 2>/dev/null || echo "  Cleanup policy for $REPO: API not available or already set"

    rm -f /tmp/cleanup-policy-${REPO}.json
done

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Docker push commands:"
for REPO in "${REPOS[@]}"; do
    echo "  docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/IMAGE:TAG"
done
echo ""
echo "Configure docker auth:"
echo "  gcloud auth configure-docker ${REGION}-docker.pkg.dev"
