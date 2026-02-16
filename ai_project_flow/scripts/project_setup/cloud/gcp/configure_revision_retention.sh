#!/usr/bin/env bash
# Configure Cloud Run revision retention policy
# Phase 5 - GCP Configuration (IPLAN-010)
#
# This script configures Cloud Run services to retain only the last N revisions,
# reducing storage costs and cleanup overhead.
#
# Prerequisites:
#   - gcloud CLI authenticated with appropriate permissions
#   - Cloud Run Admin API enabled
#
# Usage:
#   ./scripts/project_setup/gcp/configure_revision_retention.sh [--project PROJECT_ID] [--region REGION] [--keep N]

set -euo pipefail

# Defaults
PROJECT_ID="${GCP_PROJECT:-}"
REGION="${GCP_REGION:-{GCP_REGION}}"
KEEP_REVISIONS=10
SERVICES=("{PROJECT_PREFIX}-{SERVICE_NAME}")

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
        --keep)
            KEEP_REVISIONS="$2"
            shift 2
            ;;
        --service)
            SERVICES+=("$2")
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [--project PROJECT_ID] [--region REGION] [--keep N] [--service NAME]"
            echo ""
            echo "Configures Cloud Run revision retention:"
            echo "  --project  GCP project ID (or set GCP_PROJECT env var)"
            echo "  --region   GCP region (default: {GCP_REGION})"
            echo "  --keep     Number of revisions to keep (default: 10)"
            echo "  --service  Service name (can be repeated; default: {PROJECT_PREFIX}-{SERVICE_NAME})"
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

echo "=== Cloud Run Revision Retention Configuration ==="
echo "Project:         $PROJECT_ID"
echo "Region:          $REGION"
echo "Keep revisions:  $KEEP_REVISIONS"
echo ""

cleanup_old_revisions() {
    local service=$1

    echo "Processing service: $service"

    # Check if service exists
    if ! gcloud run services describe "$service" \
        --project="$PROJECT_ID" \
        --region="$REGION" \
        --format="value(name)" 2>/dev/null; then
        echo "  Service $service not found, skipping."
        return 0
    fi

    # Get all revisions sorted by creation time (newest first)
    local revisions
    revisions=$(gcloud run revisions list \
        --service="$service" \
        --project="$PROJECT_ID" \
        --region="$REGION" \
        --format="value(name)" \
        --sort-by="~metadata.creationTimestamp" 2>/dev/null)

    if [[ -z "$revisions" ]]; then
        echo "  No revisions found."
        return 0
    fi

    # Count revisions
    local count=0
    local deleted=0

    while IFS= read -r revision; do
        ((count++))

        if [[ $count -gt $KEEP_REVISIONS ]]; then
            echo "  Deleting old revision: $revision"
            if gcloud run revisions delete "$revision" \
                --project="$PROJECT_ID" \
                --region="$REGION" \
                --quiet 2>/dev/null; then
                ((deleted++))
            else
                echo "    Warning: Failed to delete $revision (may be in use)"
            fi
        fi
    done <<< "$revisions"

    echo "  Retained: $KEEP_REVISIONS, Deleted: $deleted, Total was: $count"
}

# Process each service
for service in "${SERVICES[@]}"; do
    cleanup_old_revisions "$service"
    echo ""
done

echo "=== Retention Configuration Complete ==="
echo ""
echo "Note: This is a one-time cleanup. For automated cleanup, the"
echo "deploy-staging.yml workflow includes revision retention logic."
