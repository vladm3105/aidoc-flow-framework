#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

if [[ "${ENABLE_CLAUDE_SKILL_HOOK:-0}" != "1" ]]; then
  echo "[SKIP] Claude skill hook disabled. Set ENABLE_CLAUDE_SKILL_HOOK=1 to enable manual skill audit."
  exit 0
fi

if ! command -v claude >/dev/null 2>&1; then
  echo "[ERROR] Claude CLI not found in PATH; cannot run skill audit hook."
  exit 1
fi

REPORT_DIR="${REPO_ROOT}/tmp/skill_hook_reports"
mkdir -p "${REPORT_DIR}"

failed=0
for file_path in "$@"; do
  if [[ "$file_path" = /* ]]; then
    resolved_file_path="$file_path"
  else
    resolved_file_path="${REPO_ROOT}/${file_path}"
  fi

  if [[ ! -f "$resolved_file_path" ]]; then
    continue
  fi

  base_name="$(basename "$resolved_file_path" .md)"
  report_file="${REPORT_DIR}/${base_name}.doc-prd-audit.txt"

  echo "[INFO] Skill audit: /doc-prd-audit ${resolved_file_path}"
  if ! timeout 120 claude -p "/doc-prd-audit ${resolved_file_path}" --output-format text >"${report_file}" 2>&1; then
    echo "[ERROR] Skill audit failed for ${resolved_file_path} (see ${report_file})"
    failed=1
  fi
done

if [[ "$failed" -ne 0 ]]; then
  exit 1
fi

echo "[PASS] Claude skill audit completed for PRD files."
