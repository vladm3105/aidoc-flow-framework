#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

usage() {
	cat <<'EOF'
Usage:
  sdd_layer_quality_matrix_hook.sh [DOCS_ROOT] [--changed-only]

Modes:
  default/full  Run all configured SDD layer validators (BRD..TASKS)
  --changed-only Run validators only for layers touched by staged files

DOCS_ROOT:
  Path to docs root containing 01_BRD..11_TASKS.
  If omitted: defaults to docs/.

Important:
  This hook validates project artifacts only.
  Framework/template library roots (e.g. ucx_flow_v3/) are not valid DOCS_ROOT values.
EOF
}

resolve_default_root() {
	echo "docs"
}

INPUT_ROOT=""
CHANGED_ONLY=0

while [[ $# -gt 0 ]]; do
	case "$1" in
		--changed-only)
			CHANGED_ONLY=1
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
			if [[ -z "${INPUT_ROOT}" ]]; then
				INPUT_ROOT="$1"
			else
				echo "[ERROR] Unexpected extra positional argument: $1"
				usage
				exit 2
			fi
			shift
			;;
	esac
done

if [[ -z "${INPUT_ROOT}" ]]; then
	INPUT_ROOT="$(resolve_default_root)"
fi

if [[ "${INPUT_ROOT}" = /* ]]; then
	DOCS_ROOT="${INPUT_ROOT}"
else
	DOCS_ROOT="${REPO_ROOT}/${INPUT_ROOT}"
fi

if [[ ! -d "${DOCS_ROOT}" ]]; then
	echo "[ERROR] Docs root not found: ${DOCS_ROOT}"
	exit 2
fi

if [[ ! -d "${DOCS_ROOT}/01_BRD" && ! -d "${DOCS_ROOT}/02_PRD" ]]; then
	echo "[ERROR] Invalid DOCS_ROOT: ${DOCS_ROOT}"
	echo "[ERROR] Expected layer directories (e.g., 01_BRD, 02_PRD) under DOCS_ROOT."
	exit 2
fi

declare -A LAYER_PATHS=(
	[BRD]="${DOCS_ROOT}/01_BRD"
	[PRD]="${DOCS_ROOT}/02_PRD"
	[EARS]="${DOCS_ROOT}/03_EARS"
	[BDD]="${DOCS_ROOT}/04_BDD"
	[ADR]="${DOCS_ROOT}/05_ADR"
	[SYS]="${DOCS_ROOT}/06_SYS"
	[REQ]="${DOCS_ROOT}/07_REQ"
	[CTR]="${DOCS_ROOT}/08_CTR"
	[SPEC]="${DOCS_ROOT}/09_SPEC"
	[TSPEC]="${DOCS_ROOT}/10_TSPEC"
	[TASKS]="${DOCS_ROOT}/11_TASKS"
)

declare -a ALL_LAYERS=(BRD PRD EARS BDD ADR SYS REQ CTR SPEC TSPEC TASKS)
declare -a TARGET_LAYERS=()
declare -A BRD_CHANGED_MODULES=()
declare -A PRD_CHANGED_MODULES=()
declare -A TASKS_CHANGED_FILES=()

extract_frontmatter() {
	local file_path="$1"
	awk '
		NR == 1 && $0 == "---" { in_fm=1; next }
		in_fm && $0 == "---" { exit }
		in_fm { print }
	' "$file_path"
}

extract_frontmatter_value() {
	local frontmatter="$1"
	local key="$2"
	printf '%s\n' "$frontmatter" \
		| sed -n -E "s/^[[:space:]]*${key}:[[:space:]]*\"?([^\"#]+)\"?.*$/\1/p" \
		| head -n1 \
		| xargs
}

should_enforce_file() {
	local file_path="$1"

	[[ -f "$file_path" ]] || return 1
	[[ "$file_path" == *.md ]] || return 1

	local frontmatter
	frontmatter="$(extract_frontmatter "$file_path")"
	[[ -n "$frontmatter" ]] || return 1

	local document_type
	document_type="$(extract_frontmatter_value "$frontmatter" "document_type")"
	if [[ "$document_type" == "template" ]]; then
		return 1
	fi

	local status
	status="$(extract_frontmatter_value "$frontmatter" "status")"
	if [[ -z "$status" ]]; then
		status="$(extract_frontmatter_value "$frontmatter" "development_status")"
	fi

	case "$status" in
		development|production)
			return 0
			;;
		*)
			return 1
			;;
	esac
}

record_module_change() {
	local abs="$1"
	local layer="$2"
	local module_prefix="$3"

	local layer_root="${LAYER_PATHS[${layer}]}"
	local rel="${abs#${layer_root}/}"
	local module="${rel%%/*}"

	if [[ "${module}" == ${module_prefix}* ]]; then
		if [[ "${layer}" == "BRD" ]]; then
			BRD_CHANGED_MODULES["${layer_root}/${module}"]=1
		else
			PRD_CHANGED_MODULES["${layer_root}/${module}"]=1
		fi
	fi
}

collect_changed_layers() {
	declare -A seen=()
	local changed
	changed="$(git -C "${REPO_ROOT}" diff --cached --name-only --diff-filter=ACMRTUXB || true)"

	if [[ -z "${changed}" ]]; then
		return 0
	fi

	while IFS= read -r rel; do
		[[ -z "${rel}" ]] && continue
		local abs
		abs="${REPO_ROOT}/${rel}"

		if ! should_enforce_file "${abs}"; then
			continue
		fi

		if [[ "${abs}" == "${LAYER_PATHS[BRD]}/"* ]]; then
			seen[BRD]=1
			record_module_change "${abs}" BRD "BRD-"
		fi
		if [[ "${abs}" == "${LAYER_PATHS[PRD]}/"* ]]; then
			seen[PRD]=1
			record_module_change "${abs}" PRD "PRD-"
		fi
		if [[ "${abs}" == "${LAYER_PATHS[EARS]}/"* ]]; then seen[EARS]=1; fi
		if [[ "${abs}" == "${LAYER_PATHS[BDD]}/"* ]]; then seen[BDD]=1; fi
		if [[ "${abs}" == "${LAYER_PATHS[ADR]}/"* ]]; then seen[ADR]=1; fi
		if [[ "${abs}" == "${LAYER_PATHS[SYS]}/"* ]]; then seen[SYS]=1; fi
		if [[ "${abs}" == "${LAYER_PATHS[REQ]}/"* ]]; then seen[REQ]=1; fi
		if [[ "${abs}" == "${LAYER_PATHS[CTR]}/"* ]]; then seen[CTR]=1; fi
		if [[ "${abs}" == "${LAYER_PATHS[SPEC]}/"* ]]; then seen[SPEC]=1; fi
		if [[ "${abs}" == "${LAYER_PATHS[TSPEC]}/"* ]]; then seen[TSPEC]=1; fi
		if [[ "${abs}" == "${LAYER_PATHS[TASKS]}/"* ]]; then
			seen[TASKS]=1
			if [[ "${abs}" == *.md && "$(basename "${abs}")" == TASKS-* ]]; then
				TASKS_CHANGED_FILES["${abs}"]=1
			fi
		fi
	done <<< "${changed}"

	for layer in "${ALL_LAYERS[@]}"; do
		if [[ -n "${seen[${layer}]:-}" ]]; then
			TARGET_LAYERS+=("${layer}")
		fi
	done
}

run_layer() {
	local layer="$1"
	echo "[LAYER] ${layer}"

	case "${layer}" in
		BRD)
			if [[ ${CHANGED_ONLY} -eq 1 && ${#BRD_CHANGED_MODULES[@]} -gt 0 ]]; then
				for module_dir in "${!BRD_CHANGED_MODULES[@]}"; do
					echo "  [TARGET] ${module_dir}"
					bash "${REPO_ROOT}/ucx_flow_v3/01_BRD/scripts/validate_brd_wrapper.sh" "${module_dir}" --skip-advisory
				done
			else
				bash "${REPO_ROOT}/ucx_flow_v3/01_BRD/scripts/validate_brd_wrapper.sh" "${LAYER_PATHS[BRD]}" --skip-advisory
			fi
			;;
		PRD)
			if [[ ${CHANGED_ONLY} -eq 1 && ${#PRD_CHANGED_MODULES[@]} -gt 0 ]]; then
				for module_dir in "${!PRD_CHANGED_MODULES[@]}"; do
					echo "  [TARGET] ${module_dir}"
					bash "${REPO_ROOT}/ucx_flow_v3/02_PRD/scripts/validate_prd_wrapper.sh" "${module_dir}" --skip-advisory
				done
			else
				bash "${REPO_ROOT}/ucx_flow_v3/02_PRD/scripts/validate_prd_wrapper.sh" "${LAYER_PATHS[PRD]}" --skip-advisory
			fi
			;;
		EARS)
			python3 "${REPO_ROOT}/ucx_flow_v3/03_EARS/scripts/validate_ears.py" --path "${LAYER_PATHS[EARS]}"
			;;
		BDD)
			python3 "${REPO_ROOT}/ucx_flow_v3/04_BDD/scripts/validate_bdd.py" "${LAYER_PATHS[BDD]}"
			;;
		ADR)
			python3 "${REPO_ROOT}/ucx_flow_v3/05_ADR/scripts/validate_adr.py" "${LAYER_PATHS[ADR]}"
			;;
		SYS)
			python3 "${REPO_ROOT}/ucx_flow_v3/06_SYS/scripts/validate_sys.py" "${LAYER_PATHS[SYS]}"
			;;
		REQ)
			bash "${REPO_ROOT}/ucx_flow_v3/07_REQ/scripts/validate_all.sh" --directory "${LAYER_PATHS[REQ]}"
			;;
		CTR)
			bash "${REPO_ROOT}/ucx_flow_v3/08_CTR/scripts/validate_ctr_all.sh" --directory "${LAYER_PATHS[CTR]}"
			;;
		SPEC)
			bash "${REPO_ROOT}/ucx_flow_v3/09_SPEC/scripts/validate_all_spec.sh" --directory "${LAYER_PATHS[SPEC]}"
			;;
		TSPEC)
			bash "${REPO_ROOT}/ucx_flow_v3/10_TSPEC/scripts/validate_all_tspec.sh" "${LAYER_PATHS[TSPEC]}"
			;;
		TASKS)
			local tasks_found=0
			if [[ ${CHANGED_ONLY} -eq 1 && ${#TASKS_CHANGED_FILES[@]} -gt 0 ]]; then
				for tasks_file in "${!TASKS_CHANGED_FILES[@]}"; do
					[[ -f "${tasks_file}" ]] || continue
					tasks_found=1
					echo "  [TARGET] ${tasks_file}"
					bash "${REPO_ROOT}/ucx_flow_v3/11_TASKS/scripts/validate_tasks.sh" "${tasks_file}"
				done
			else
				while IFS= read -r tasks_file; do
					[[ -z "${tasks_file}" ]] && continue
					tasks_found=1
					bash "${REPO_ROOT}/ucx_flow_v3/11_TASKS/scripts/validate_tasks.sh" "${tasks_file}"
				done < <(find "${LAYER_PATHS[TASKS]}" -type f -name 'TASKS-*.md' 2>/dev/null | sort)
			fi

			if [[ ${tasks_found} -eq 0 ]]; then
				echo "[WARN] No TASKS files found under ${LAYER_PATHS[TASKS]}"
			fi
			;;
		*)
			echo "[ERROR] Unknown layer: ${layer}"
			return 2
			;;
	esac
}

if [[ ${CHANGED_ONLY} -eq 1 ]]; then
	collect_changed_layers
	if [[ ${#TARGET_LAYERS[@]} -eq 0 ]]; then
		echo "[PASS] No staged instance docs with status development/production detected under ${DOCS_ROOT}; skipping matrix."
		exit 0
	fi
else
	for layer in "${ALL_LAYERS[@]}"; do
		TARGET_LAYERS+=("${layer}")
	done
fi

echo "=========================================="
echo "SDD Layer Quality Matrix"
echo "=========================================="
echo "Docs root: ${DOCS_ROOT}"
echo "Mode:      $([[ ${CHANGED_ONLY} -eq 1 ]] && echo "changed-only" || echo "full")"
echo "Layers:    ${TARGET_LAYERS[*]}"

status=0
for layer in "${TARGET_LAYERS[@]}"; do
	if [[ ! -d "${LAYER_PATHS[${layer}]}" ]]; then
		echo "[WARN] ${layer} directory not found: ${LAYER_PATHS[${layer}]}"
		continue
	fi

	if ! run_layer "${layer}"; then
		status=2
	fi
done

if [[ ${status} -ne 0 ]]; then
	echo "[FAIL] SDD layer quality matrix checks reported validation failures."
	exit ${status}
fi

echo "[PASS] SDD layer quality matrix checks completed (${#TARGET_LAYERS[@]} layer(s))."
