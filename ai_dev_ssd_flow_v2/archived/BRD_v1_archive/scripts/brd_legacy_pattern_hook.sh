#!/usr/bin/env bash
# =============================================================================
# DEPRECATED: This script is deprecated as of UCX v1.9.0.
#
# Migration: Use `ucx validate brd <path>` instead (includes legacy detection).
# Removal: This script will be removed in UCX v2.0.0.
#
# See: /opt/data/docs_flow_framework/UCX/docs/QUICK_START.md
# =============================================================================

echo "WARNING: This script is deprecated. Use 'ucx validate brd <path>' instead." >&2
echo "         Will be removed in UCX v2.0.0." >&2

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

INPUT_ROOT="${1:-docs/01_BRD}"
if [[ "${INPUT_ROOT}" = /* ]]; then
	BRD_ROOT="${INPUT_ROOT}"
else
	BRD_ROOT="${REPO_ROOT}/${INPUT_ROOT}"
fi

python3 "${REPO_ROOT}/ucx_flow_v3/scripts/detect_legacy_element_ids.py" "${BRD_ROOT}" --summary
