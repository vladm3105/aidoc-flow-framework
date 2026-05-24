#!/bin/bash
set -euo pipefail

#
# GHES Self-Hosted Runner — Local Setup Script
# Registers and starts a persistent runner on the host
#
# Usage: ./setup-local-runner.sh [start|stop|status|remove]
#
# Prerequisites:
#   - gh CLI authenticated to {GITHUB_HOST}
#   - 64-bit Linux (x86_64)
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNNER_DIR="${SCRIPT_DIR}/runner-local"
RUNNER_VERSION="2.311.0"
GHES_HOST="{GITHUB_HOST}"
GHES_ORG="{GITHUB_ORG}"
GHES_REPO="{REPO_NAME}"
RUNNER_NAME="local-{PROJECT_PREFIX}-01"
RUNNER_LABELS="ubuntu-latest"
PID_FILE="${RUNNER_DIR}/runner.pid"
LOG_FILE="${RUNNER_DIR}/runner.log"

#  Helper functions
info()  { echo ">> $*"; }
error() { echo "ERROR: $*" >&2; exit 1; }

get_reg_token() {
    GH_HOST="${GHES_HOST}" gh api -X POST \
        "/repos/${GHES_ORG}/${GHES_REPO}/actions/runners/registration-token" \
        --jq '.token' 2>/dev/null
}

#  Commands
cmd_start() {
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        info "Runner already running (PID $(cat "$PID_FILE"))"
        return 0
    fi

    # Download runner if not present
    if [ ! -f "${RUNNER_DIR}/config.sh" ]; then
        info "Downloading Actions runner v${RUNNER_VERSION}..."
        mkdir -p "${RUNNER_DIR}"
        curl -fsSL -o "${RUNNER_DIR}/actions-runner.tar.gz" \
            "https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz"
        tar xzf "${RUNNER_DIR}/actions-runner.tar.gz" -C "${RUNNER_DIR}"
        rm "${RUNNER_DIR}/actions-runner.tar.gz"
        info "Runner binary extracted."
    fi

    # Configure if not already configured
    if [ ! -f "${RUNNER_DIR}/.runner" ]; then
        info "Getting registration token..."
        REG_TOKEN=$(get_reg_token)
        if [ -z "$REG_TOKEN" ] || [ "$REG_TOKEN" = "null" ]; then
            error "Failed to get registration token. Ensure gh is authenticated to ${GHES_HOST} with repo scope."
        fi

        info "Configuring runner: ${RUNNER_NAME}"
        cd "${RUNNER_DIR}"
        ./config.sh \
            --url "https://${GHES_HOST}/${GHES_ORG}/${GHES_REPO}" \
            --token "${REG_TOKEN}" \
            --name "${RUNNER_NAME}" \
            --labels "${RUNNER_LABELS}" \
            --work "_work" \
            --replace \
            --unattended
        info "Runner configured."
    fi

    # Start runner
    info "Starting runner..."
    cd "${RUNNER_DIR}"
    nohup ./run.sh > "${LOG_FILE}" 2>&1 &
    echo $! > "${PID_FILE}"
    sleep 2

    if kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        info "Runner started (PID $(cat "$PID_FILE"))"
        info "Log: ${LOG_FILE}"
        tail -5 "${LOG_FILE}"
    else
        error "Runner failed to start. Check ${LOG_FILE}"
    fi
}

cmd_stop() {
    if [ ! -f "$PID_FILE" ]; then
        info "No PID file found — runner not running."
        return 0
    fi

    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        info "Stopping runner (PID $PID)..."
        kill "$PID"
        sleep 2
        if kill -0 "$PID" 2>/dev/null; then
            kill -9 "$PID"
        fi
        info "Runner stopped."
    else
        info "Runner not running (stale PID file)."
    fi
    rm -f "$PID_FILE"
}

cmd_status() {
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        info "Runner is RUNNING (PID $(cat "$PID_FILE"))"
        tail -3 "${LOG_FILE}" 2>/dev/null
    else
        info "Runner is NOT running."
    fi

    # Check GHES registration
    info "Checking GHES registration..."
    GH_HOST="${GHES_HOST}" gh api \
        "/repos/${GHES_ORG}/${GHES_REPO}/actions/runners" \
        --jq '.runners[] | "  \(.name): \(.status) [\(.labels | map(.name) | join(", "))]"' 2>/dev/null \
        || info "Could not query GHES runners API."
}

cmd_remove() {
    cmd_stop

    if [ -f "${RUNNER_DIR}/.runner" ]; then
        info "Getting removal token..."
        REG_TOKEN=$(get_reg_token)
        cd "${RUNNER_DIR}"
        ./config.sh remove --token "${REG_TOKEN}" 2>/dev/null || true
        info "Runner deregistered from GHES."
    fi

    info "To remove runner files: rm -rf ${RUNNER_DIR}"
}

#  Main
ACTION="${1:-start}"

case "$ACTION" in
    start)  cmd_start ;;
    stop)   cmd_stop ;;
    status) cmd_status ;;
    remove) cmd_remove ;;
    *)      echo "Usage: $0 [start|stop|status|remove]"; exit 1 ;;
esac
