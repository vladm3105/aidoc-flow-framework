#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

INPUT_ROOT="${1:-ai_dev_ssd_flow/05_ADR}"
if [[ "${INPUT_ROOT}" = /* ]]; then
	ADR_ROOT="${INPUT_ROOT}"
else
	ADR_ROOT="${REPO_ROOT}/${INPUT_ROOT}"
fi

bash "${SCRIPT_DIR}/validate_adr_quality_score.sh" "${ADR_ROOT}"
