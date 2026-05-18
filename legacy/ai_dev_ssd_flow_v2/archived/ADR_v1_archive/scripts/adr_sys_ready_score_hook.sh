#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

INPUT_ROOT="${1:-ucx_flow_v3/05_ADR}"
if [[ "${INPUT_ROOT}" = /* ]]; then
	ADR_ROOT="${INPUT_ROOT}"
else
	ADR_ROOT="${REPO_ROOT}/${INPUT_ROOT}"
fi

python3 "${SCRIPT_DIR}/calculate_adr_sys_ready_score.py" "${ADR_ROOT}"
