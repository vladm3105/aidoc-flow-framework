#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

INPUT_ROOT="${1:-docs/01_BRD}"
if [[ "${INPUT_ROOT}" = /* ]]; then
	BRD_ROOT="${INPUT_ROOT}"
else
	BRD_ROOT="${REPO_ROOT}/${INPUT_ROOT}"
fi

python3 "${REPO_ROOT}/ai_dev_ssd_flow/scripts/detect_legacy_element_ids.py" "${BRD_ROOT}" --summary
