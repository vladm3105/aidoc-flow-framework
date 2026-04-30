#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

INPUT_ROOT="${1:-ai_dev_ssd_flow/07_REQ}"
if [[ "${INPUT_ROOT}" = /* ]]; then
	REQ_ROOT="${INPUT_ROOT}"
else
	REQ_ROOT="${REPO_ROOT}/${INPUT_ROOT}"
fi

bash "${SCRIPT_DIR}/validate_req_quality_score.sh" "${REQ_ROOT}"
