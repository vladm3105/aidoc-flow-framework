#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

INPUT_ROOT="${1:-ucx_flow_v3/06_SYS}"
if [[ "${INPUT_ROOT}" = /* ]]; then
	SYS_ROOT="${INPUT_ROOT}"
else
	SYS_ROOT="${REPO_ROOT}/${INPUT_ROOT}"
fi

python3 "${SCRIPT_DIR}/validate_sys.py" "${SYS_ROOT}"
