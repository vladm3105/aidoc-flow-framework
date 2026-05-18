#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

usage() {
  cat <<'EOF'
PRD validation wrapper (tiered)

Usage:
  ./validate_prd_wrapper.sh [PRD_ROOT] [--docs-root PATH] [--skip-advisory] [--advisory-strict]

Tiers:
  Tier 1 (CORE, blocking):
    - PRD standardized element type code validation
    - PRD structural validation
    - PRD quality gate validation

  Tier 2 (ADVISORY, non-blocking by default):
    - metadata validation
    - link validation
    - forward reference validation
    - diagram consistency validation

Options:
  PRD_ROOT          PRD directory to validate (default: docs/02_PRD)
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

PRD_ROOT_INPUT="docs/02_PRD"
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
      PRD_ROOT_INPUT="$1"
      shift
      ;;
  esac
done

PRD_ROOT="$(resolve_path "${PRD_ROOT_INPUT}")"
if [[ ! -d "${PRD_ROOT}" ]]; then
  echo "[ERROR] PRD root not found: ${PRD_ROOT}"
  exit 2
fi

if [[ -n "${DOCS_ROOT_INPUT}" ]]; then
  DOCS_ROOT="$(resolve_path "${DOCS_ROOT_INPUT}")"
elif [[ "$(basename "${PRD_ROOT}")" == "02_PRD" ]]; then
  DOCS_ROOT="$(dirname "${PRD_ROOT}")"
else
  DOCS_ROOT="${REPO_ROOT}/docs"
fi

CORE_FAIL=0
CORE_WARN=0
ADVISORY_FAIL=0

is_section_based_prd_root() {
  local root="$1"
  find "$root" -type f -name 'PRD-*.0_*.md' -o -type f -name 'PRD-*.0_index.md' 2>/dev/null | grep -q .
}

run_core() {
  local label="$1"
  shift
  echo "[CORE] ${label}"
  set +e
  "$@"
  local rc=$?
  set -e

  # Validator exit codes: 0=pass, 1=warnings only, 2=errors
  case "$rc" in
    0)
      echo "[PASS] ${label}"
      ;;
    1)
      echo "[WARN] ${label} (warnings present)"
      CORE_WARN=$((CORE_WARN + 1))
      ;;
    *)
      echo "[FAIL] ${label}"
      CORE_FAIL=1
      ;;
  esac
}

run_quality_core() {
  local label="$1"
  shift
  echo "[CORE] ${label}"
  set +e
  "$@"
  local rc=$?
  set -e

  # Quality gate exit codes: 0=pass, 1=warnings only, 2=errors
  case "$rc" in
    0)
      echo "[PASS] ${label}"
      ;;
    1)
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
echo "PRD Validation Wrapper"
echo "=========================================="
echo "PRD root:  ${PRD_ROOT}"
echo "Docs root: ${DOCS_ROOT}"
echo ""

run_core "PRD standardized element type codes" \
  python3 "${REPO_ROOT}/ucx_flow_v3/scripts/validate_prd_standardized_element_codes.py" "${PRD_ROOT}"

if is_section_based_prd_root "${PRD_ROOT}"; then
  echo "[CORE] PRD structural validator"
  echo "[PASS] PRD structural validator (section-based PRD root detected; monolithic structural validator skipped)"
else
  run_core "PRD structural validator" \
    python3 "${SCRIPT_DIR}/validate_prd.py" "${PRD_ROOT}"
fi

run_quality_core "PRD quality gate" \
  bash "${SCRIPT_DIR}/validate_prd_quality_score.sh" "${PRD_ROOT}"

if [[ "${SKIP_ADVISORY}" -eq 0 ]]; then
  echo ""
  run_advisory "Metadata validation" \
    python3 "${REPO_ROOT}/ucx_flow_v3/scripts/validate_metadata.py" "${PRD_ROOT}" --strict

  run_advisory "Link validation" \
    python3 "${REPO_ROOT}/ucx_flow_v3/scripts/validate_links.py" --docs-dir "${PRD_ROOT}"

  run_advisory "Forward reference validation" \
    python3 "${REPO_ROOT}/ucx_flow_v3/scripts/validate_forward_references.py" "${PRD_ROOT}"

  run_advisory "Diagram consistency validation" \
    python3 "${REPO_ROOT}/ucx_flow_v3/scripts/validate_diagram_consistency.py" "${PRD_ROOT}"
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
