#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

INPUT_ROOT="${1:-ucx_flow_v3/04_BDD}"
if [[ "${INPUT_ROOT}" = /* ]]; then
	BDD_ROOT="${INPUT_ROOT}"
else
	BDD_ROOT="${REPO_ROOT}/${INPUT_ROOT}"
fi

python3 "${SCRIPT_DIR}/calculate_bdd_adr_ready_score.py" "${BDD_ROOT}"
