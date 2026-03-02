#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

INPUT_ROOT="${1:-ai_dev_ssd_flow}"
if [[ "${INPUT_ROOT}" = /* ]]; then
	DOCS_ROOT="${INPUT_ROOT}"
else
	DOCS_ROOT="${REPO_ROOT}/${INPUT_ROOT}"
fi

if [[ ! -d "${DOCS_ROOT}" ]]; then
	echo "[ERROR] Metadata scope hook: root not found: ${DOCS_ROOT}"
	exit 2
fi

extract_frontmatter() {
	local file_path="$1"
	awk '
		NR == 1 && $0 == "---" { in_fm=1; next }
		in_fm && $0 == "---" { exit }
		in_fm { print }
	' "$file_path"
}

extract_value() {
	local frontmatter="$1"
	local key="$2"
	printf '%s\n' "$frontmatter" \
		| sed -n -E "s/^[[:space:]]*${key}:[[:space:]]*\"?([^\"#]+)\"?.*$/\1/p" \
		| head -n1 \
		| xargs
}

eligible=0
templates=0
drafts=0
other_status=0
errors=0

changed="$(git -C "${REPO_ROOT}" diff --cached --name-only --diff-filter=ACMRTUXB || true)"

if [[ -z "${changed}" ]]; then
	echo "[PASS] Metadata scope hook: no staged files."
	exit 0
fi

while IFS= read -r rel; do
	[[ -z "${rel}" ]] && continue
	abs="${REPO_ROOT}/${rel}"

	[[ -f "${abs}" ]] || continue
	[[ "${abs}" == *.md ]] || continue

	case "${abs}" in
		"${DOCS_ROOT}/"01_BRD/*|"${DOCS_ROOT}/"02_PRD/*|"${DOCS_ROOT}/"03_EARS/*|"${DOCS_ROOT}/"04_BDD/*|"${DOCS_ROOT}/"05_ADR/*|"${DOCS_ROOT}/"06_SYS/*|"${DOCS_ROOT}/"07_REQ/*|"${DOCS_ROOT}/"08_CTR/*|"${DOCS_ROOT}/"09_SPEC/*|"${DOCS_ROOT}/"10_TSPEC/*|"${DOCS_ROOT}/"11_TASKS/*)
			;;
		*)
			continue
			;;
	esac

	frontmatter="$(extract_frontmatter "${abs}")"
	[[ -n "${frontmatter}" ]] || continue

	document_type="$(extract_value "${frontmatter}" "document_type")"
	status="$(extract_value "${frontmatter}" "status")"
	if [[ -z "${status}" ]]; then
		status="$(extract_value "${frontmatter}" "development_status")"
	fi

	if [[ "${document_type}" == "template" ]]; then
		templates=$((templates + 1))
		continue
	fi

	if [[ -z "${status}" ]]; then
		echo "[ERROR] Missing custom_fields.status in instance document: ${rel}"
		errors=$((errors + 1))
		continue
	fi

	case "${status}" in
		development|production)
			eligible=$((eligible + 1))
			;;
		draft)
			drafts=$((drafts + 1))
			;;
		*)
			other_status=$((other_status + 1))
			;;
	esac
done <<< "${changed}"

if [[ ${errors} -gt 0 ]]; then
	echo "[FAIL] Metadata scope hook: ${errors} staged instance document(s) missing status."
	exit 2
fi

echo "[PASS] Metadata scope hook: eligible=${eligible}, templates=${templates}, drafts=${drafts}, other_status=${other_status}"
exit 0
