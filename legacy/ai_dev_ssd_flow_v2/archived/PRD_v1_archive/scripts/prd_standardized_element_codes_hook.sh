#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

INPUT_ROOT="${1:-ucx_flow_v3/02_PRD}"
if [[ "${INPUT_ROOT}" = /* ]]; then
	PRD_ROOT="${INPUT_ROOT}"
else
	PRD_ROOT="${REPO_ROOT}/${INPUT_ROOT}"
fi

python3 "${REPO_ROOT}/ucx_flow_v3/scripts/validate_prd_standardized_element_codes.py" "${PRD_ROOT}" --strict
