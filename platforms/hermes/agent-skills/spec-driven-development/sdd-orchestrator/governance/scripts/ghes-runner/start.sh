#!/bin/bash
set -euo pipefail

# 
# GHES Self-Hosted Runner — Entrypoint
# Registers with GHES, runs jobs, deregisters on stop
# 

: "${GHES_URL:?GHES_URL is required (e.g. https://{GITHUB_HOST})}"
: "${GHES_ORG:={GITHUB_ORG}}"
: "${GHES_REPO:={REPO_NAME}}"
: "${RUNNER_NAME:=$(hostname)}"
: "${RUNNER_LABELS:=ubuntu-latest}"
: "${RUNNER_SCOPE:=repo}"
: "${RUNNER_EPHEMERAL:=false}"

# GHES_PAT can be a classic PAT (ghp_*) or OAuth token (gho_*).
# If not set, falls back to gh auth token.
if [ -z "${GHES_PAT:-}" ]; then
    GHES_PAT=$(GH_HOST="${GHES_URL#https://}" gh auth token 2>/dev/null || true)
    if [ -z "${GHES_PAT}" ]; then
        echo "ERROR: GHES_PAT not set and gh auth token unavailable."
        exit 1
    fi
    echo ">> Using token from gh auth."
fi

RUNNER_DIR="/home/runner/actions-runner"

#  Deregister on shutdown 
cleanup() {
    echo ">> Received shutdown signal — removing runner..."
    cd "${RUNNER_DIR}"
    if [ -f ".runner" ]; then
        ./config.sh remove --token "${REG_TOKEN}" 2>/dev/null || true
    fi
    echo ">> Runner deregistered."
}
trap cleanup SIGTERM SIGINT EXIT

#  Get registration token 
echo ">> Requesting registration token from GHES..."
if [ "${RUNNER_SCOPE}" = "org" ]; then
    API_PATH="orgs/${GHES_ORG}/actions/runners/registration-token"
else
    API_PATH="repos/${GHES_ORG}/${GHES_REPO}/actions/runners/registration-token"
fi

# Try gh api first (handles OAuth tokens on GHES), fall back to curl
if command -v gh &>/dev/null; then
    REG_TOKEN=$(GH_HOST="${GHES_URL#https://}" gh api -X POST "${API_PATH}" --jq '.token' 2>/dev/null || true)
fi
if [ -z "${REG_TOKEN:-}" ] || [ "${REG_TOKEN}" = "null" ]; then
    REG_TOKEN=$(curl -sS -X POST \
        -H "Authorization: token ${GHES_PAT}" \
        -H "Accept: application/vnd.github+json" \
        "${GHES_URL}/api/v3/${API_PATH}" \
        | jq -r '.token')
fi

if [ -z "${REG_TOKEN}" ] || [ "${REG_TOKEN}" = "null" ]; then
    echo "ERROR: Failed to get registration token. Check GHES_PAT permissions."
    echo "  Required scopes: repo (repo-level) or admin:org (org-level)"
    exit 1
fi
echo ">> Registration token obtained."

#  Configure runner 
echo ">> Configuring runner: ${RUNNER_NAME}"
EXTRA_ARGS=""
if [ "${RUNNER_EPHEMERAL}" = "true" ]; then
    EXTRA_ARGS="--ephemeral"
fi

cd "${RUNNER_DIR}"

if [ "${RUNNER_SCOPE}" = "org" ]; then
    CONFIG_URL="${GHES_URL}/${GHES_ORG}"
else
    CONFIG_URL="${GHES_URL}/${GHES_ORG}/${GHES_REPO}"
fi

./config.sh \
    --url "${CONFIG_URL}" \
    --token "${REG_TOKEN}" \
    --name "${RUNNER_NAME}" \
    --labels "${RUNNER_LABELS}" \
    --work "_work" \
    --replace \
    --unattended \
    ${EXTRA_ARGS}

echo ">> Runner configured. Starting..."

#  Run 
./run.sh
