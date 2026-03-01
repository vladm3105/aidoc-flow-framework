#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

INPUT_ROOT="${1:-ai_dev_ssd_flow/02_PRD}"
if [[ "${INPUT_ROOT}" = /* ]]; then
	PRD_ROOT="${INPUT_ROOT}"
else
	PRD_ROOT="${REPO_ROOT}/${INPUT_ROOT}"
fi

python3 "${REPO_ROOT}/ai_dev_ssd_flow/scripts/detect_legacy_prd_element_ids.py" "${PRD_ROOT}" --summary
