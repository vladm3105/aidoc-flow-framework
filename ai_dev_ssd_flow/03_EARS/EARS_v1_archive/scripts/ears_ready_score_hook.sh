#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

INPUT_ROOT="${1:-ai_dev_ssd_flow/03_EARS}"
if [[ "${INPUT_ROOT}" = /* ]]; then
	EARS_ROOT="${INPUT_ROOT}"
else
	EARS_ROOT="${REPO_ROOT}/${INPUT_ROOT}"
fi

python3 "${SCRIPT_DIR}/calculate_ears_ready_score.py" "${EARS_ROOT}"
