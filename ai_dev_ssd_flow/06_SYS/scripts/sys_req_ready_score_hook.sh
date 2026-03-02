#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

INPUT_ROOT="${1:-ai_dev_ssd_flow/06_SYS}"
if [[ "${INPUT_ROOT}" = /* ]]; then
	SYS_ROOT="${INPUT_ROOT}"
else
	SYS_ROOT="${REPO_ROOT}/${INPUT_ROOT}"
fi

python3 "${SCRIPT_DIR}/calculate_sys_req_ready_score.py" "${SYS_ROOT}"
