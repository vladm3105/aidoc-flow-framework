#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

INPUT_ROOT="${1:-ai_dev_ssd_flow/04_BDD}"
if [[ "${INPUT_ROOT}" = /* ]]; then
	BDD_ROOT="${INPUT_ROOT}"
else
	BDD_ROOT="${REPO_ROOT}/${INPUT_ROOT}"
fi

bash "${SCRIPT_DIR}/validate_bdd_quality_score.sh" "${BDD_ROOT}"
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

INPUT_ROOT="${1:-ai_dev_ssd_flow/04_BDD}"
if [[ "${INPUT_ROOT}" = /* ]]; then
	BDD_ROOT="${INPUT_ROOT}"
else
	BDD_ROOT="${REPO_ROOT}/${INPUT_ROOT}"
fi

bash "${SCRIPT_DIR}/validate_bdd_quality_score.sh" "${BDD_ROOT}"
