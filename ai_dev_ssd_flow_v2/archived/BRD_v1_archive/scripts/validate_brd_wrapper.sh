#!/usr/bin/env bash
# =============================================================================
# DEPRECATED: This script is deprecated as of UCX v1.9.0.
#
# Migration: Use `ucx validate brd <path> --tier1-only` instead.
# Removal: This script will be removed in UCX v2.0.0.
#
# See: /opt/data/docs_flow_framework/UCX/docs/QUICK_START.md
# =============================================================================

echo "WARNING: This script is deprecated. Use 'ucx validate brd <path>' instead." >&2
echo "         Will be removed in UCX v2.0.0." >&2

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

usage() {
  cat <<'EOF'
BRD validation wrapper (tiered)

Usage:
  ./validate_brd_wrapper.sh [BRD_ROOT] [--docs-root PATH] [--skip-advisory] [--advisory-strict]

Tiers:
  Tier 1 (CORE, blocking):
    - standardized element codes
    - BRD structural validation
    - BRD quality gate validation

  Tier 2 (ADVISORY, non-blocking by default):
    - metadata validation
    - link validation
    - forward reference validation
    - diagram consistency validation

Options:
  BRD_ROOT          BRD directory to validate (default: docs/01_BRD)
  --docs-root PATH  Explicit docs root path for advisory tools
  --skip-advisory   Run only core checks
  --advisory-strict Treat advisory failures as blocking
  -h, --help        Show this help
EOF
}

resolve_path() {
  local input_path="$1"
  if [[ "${input_path}" = /* ]]; then
    echo "${input_path}"
  else
    echo "${REPO_ROOT}/${input_path}"
  fi
}

BRD_ROOT_INPUT="docs/01_BRD"
DOCS_ROOT_INPUT=""
SKIP_ADVISORY=0
ADVISORY_STRICT=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --docs-root)
      DOCS_ROOT_INPUT="$2"
      shift 2
      ;;
    --skip-advisory)
      SKIP_ADVISORY=1
      shift
      ;;
    --advisory-strict)
      ADVISORY_STRICT=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --*)
      echo "[ERROR] Unknown option: $1"
      usage
      exit 2
      ;;
    *)
      BRD_ROOT_INPUT="$1"
      shift
      ;;
  esac
done

BRD_ROOT="$(resolve_path "${BRD_ROOT_INPUT}")"
if [[ ! -d "${BRD_ROOT}" ]]; then
  echo "[ERROR] BRD root not found: ${BRD_ROOT}"
  exit 2
fi

if [[ -n "${DOCS_ROOT_INPUT}" ]]; then
  DOCS_ROOT="$(resolve_path "${DOCS_ROOT_INPUT}")"
elif [[ "$(basename "${BRD_ROOT}")" == "01_BRD" ]]; then
  DOCS_ROOT="$(dirname "${BRD_ROOT}")"
else
  DOCS_ROOT="${REPO_ROOT}/docs"
fi

CORE_FAIL=0
CORE_WARN=0
ADVISORY_FAIL=0

is_section_based_brd_root() {
  local root="$1"
  find "$root" -type f -name 'BRD-*.0_*.md' -o -type f -name 'BRD-*.0_index.md' 2>/dev/null | grep -q .
}

run_core() {
  local label="$1"
  shift
  echo "[CORE] ${label}"
  if ! "$@"; then
    echo "[FAIL] ${label}"
    CORE_FAIL=1
  else
    echo "[PASS] ${label}"
  fi
}

run_quality_core() {
  local label="$1"
  shift
  echo "[CORE] ${label}"
  set +e
  "$@"
  local rc=$?
  set -e

  case "$rc" in
    0)
      echo "[PASS] ${label}"
      ;;
    2)
      echo "[WARN] ${label} (warnings present)"
      CORE_WARN=$((CORE_WARN + 1))
      ;;
    *)
      echo "[FAIL] ${label}"
      CORE_FAIL=1
      ;;
  esac
}

run_advisory() {
  local label="$1"
  shift
  echo "[ADVISORY] ${label}"
  set +e
  "$@"
  local rc=$?
  set -e

  if [[ "$rc" -ne 0 ]]; then
    echo "[WARN] ${label} (exit ${rc})"
    ADVISORY_FAIL=$((ADVISORY_FAIL + 1))
  else
    echo "[PASS] ${label}"
  fi
}

echo "=========================================="
echo "BRD Validation Wrapper"
echo "=========================================="
echo "BRD root:  ${BRD_ROOT}"
echo "Docs root: ${DOCS_ROOT}"
echo ""

run_core "Standardized element codes" \
  python3 "${REPO_ROOT}/ucx_flow_v3/scripts/validate_standardized_element_codes.py" "${BRD_ROOT}" --strict

if is_section_based_brd_root "${BRD_ROOT}"; then
  echo "[CORE] BRD structural validator"
  echo "[PASS] BRD structural validator (section-based BRD root detected; monolithic structural validator skipped)"
else
  run_core "BRD structural validator" \
    python3 "${SCRIPT_DIR}/validate_brd.py" "${BRD_ROOT}" --strict
fi

run_quality_core "BRD quality gate" \
  bash "${SCRIPT_DIR}/validate_brd_quality_score.sh" "${BRD_ROOT}"

if [[ "${SKIP_ADVISORY}" -eq 0 ]]; then
  echo ""
  run_advisory "Metadata validation" \
    python3 "${REPO_ROOT}/ucx_flow_v3/scripts/validate_metadata.py" "${BRD_ROOT}" --strict

  run_advisory "Link validation" \
    python3 "${REPO_ROOT}/ucx_flow_v3/scripts/validate_links.py" --docs-dir "${BRD_ROOT}"

  run_advisory "Forward reference validation" \
    python3 "${REPO_ROOT}/ucx_flow_v3/scripts/validate_forward_references.py" "${BRD_ROOT}"

  run_advisory "Diagram consistency validation" \
    python3 "${REPO_ROOT}/ucx_flow_v3/scripts/validate_diagram_consistency.py" "${BRD_ROOT}"
fi

echo ""
echo "=========================================="
echo "Wrapper Summary"
echo "=========================================="
echo "Core failures:      ${CORE_FAIL}"
echo "Core warnings:      ${CORE_WARN}"
echo "Advisory failures:  ${ADVISORY_FAIL}"

if [[ "${CORE_FAIL}" -ne 0 ]]; then
  echo "[FAIL] Tier 1 core checks failed (blocking)."
  exit 2
fi

if [[ "${ADVISORY_STRICT}" -eq 1 && "${ADVISORY_FAIL}" -ne 0 ]]; then
  echo "[FAIL] Advisory checks failed under --advisory-strict."
  exit 1
fi

if [[ "${CORE_WARN}" -ne 0 || "${ADVISORY_FAIL}" -ne 0 ]]; then
  echo "[PASS] Core checks passed; non-blocking findings remain in warnings/advisory tier."
else
  echo "[PASS] All checks passed."
fi

exit 0
