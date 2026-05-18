#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

INPUT_ROOT="${1:-ucx_flow_v3/07_REQ}"
MIN_SCORE="${2:-90}"

if [[ "${INPUT_ROOT}" = /* ]]; then
	REQ_ROOT="${INPUT_ROOT}"
else
	REQ_ROOT="${REPO_ROOT}/${INPUT_ROOT}"
fi

if [[ ! -d "${REQ_ROOT}" ]]; then
	echo "[FAIL] REQ root not found: ${REQ_ROOT}" >&2
	exit 2
fi

mapfile -t REQ_FILES < <(
	find "${REQ_ROOT}" -type f -name 'REQ-*.md' \
		! -name 'REQ-00_*' \
		! -name '*TEMPLATE*' \
		! -name '*.A_audit_report*' \
		! -name '*.R_review_report*' \
		! -name '*.F_fix_report*' \
		! -name '*.V_validation_report*' \
		| sort
)

if [[ ${#REQ_FILES[@]} -eq 0 ]]; then
	echo "[SKIP] No REQ files found in ${REQ_ROOT}"
	exit 0
fi

for req_file in "${REQ_FILES[@]}"; do
	python3 "${SCRIPT_DIR}/validate_req_spec_readiness.py" --req-file "${req_file}" --min-score "${MIN_SCORE}"
done
