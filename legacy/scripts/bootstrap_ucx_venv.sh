#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
FRAMEWORK_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
VENV_DIR="${FRAMEWORK_ROOT}/.venv"
WITH_KB=false
REQUIRE_PYTHON_VERSION=""

if command -v python3.12 >/dev/null 2>&1; then
  PYTHON_BIN="python3.12"
else
  PYTHON_BIN="python3"
fi

usage() {
  cat <<'EOF'
Usage: scripts/bootstrap_ucx_venv.sh [options]

Create/update shared UCX virtual environment at /opt/data/ucx_framework/.venv.

Options:
  --framework-root PATH  Override framework root (default: script parent directory)
  --venv PATH            Override virtual environment path
  --python BIN           Python binary to use (default: python3.12, fallback python3)
  --with-kb              Install optional ucx_kb runtime dependencies and validate import
  --require-python-version VER  Require exact Python version (e.g., 3.12.13)
  -h, --help             Show this help message
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --framework-root)
      FRAMEWORK_ROOT="$2"
      shift 2
      ;;
    --venv)
      VENV_DIR="$2"
      shift 2
      ;;
    --python)
      PYTHON_BIN="$2"
      shift 2
      ;;
    --with-kb)
      WITH_KB=true
      shift
      ;;
    --require-python-version)
      REQUIRE_PYTHON_VERSION="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "Python binary not found: ${PYTHON_BIN}" >&2
  exit 2
fi

if [[ ! -d "${FRAMEWORK_ROOT}" ]]; then
  echo "Framework root not found: ${FRAMEWORK_ROOT}" >&2
  exit 2
fi

if [[ ! -d "${FRAMEWORK_ROOT}/ucx_hermes" ]]; then
  echo "ucx_hermes directory missing under framework root: ${FRAMEWORK_ROOT}" >&2
  exit 2
fi

"${PYTHON_BIN}" - <<'PY'
import sys

if sys.version_info < (3, 12):
    raise SystemExit("Python 3.12+ is required for ucx_hermes")
PY

if [[ -n "${REQUIRE_PYTHON_VERSION}" ]]; then
  "${PYTHON_BIN}" - <<PY
import platform

required = "${REQUIRE_PYTHON_VERSION}"
actual = platform.python_version()
if actual != required:
    raise SystemExit(f"Python {required} is required (found {actual})")
PY
fi

echo "[ucx-bootstrap] framework root: ${FRAMEWORK_ROOT}"
echo "[ucx-bootstrap] virtual environment: ${VENV_DIR}"
echo "[ucx-bootstrap] python: ${PYTHON_BIN}"
if [[ -n "${REQUIRE_PYTHON_VERSION}" ]]; then
  echo "[ucx-bootstrap] required python version: ${REQUIRE_PYTHON_VERSION}"
fi

"${PYTHON_BIN}" -m venv "${VENV_DIR}"
"${VENV_DIR}/bin/python" -m pip install --upgrade pip setuptools wheel
"${VENV_DIR}/bin/pip" install -e "${FRAMEWORK_ROOT}/ucx_hermes[api]"

if [[ "${WITH_KB}" == "true" ]]; then
  "${VENV_DIR}/bin/pip" install -U psycopg neo4j fastapi uvicorn python-dotenv pyyaml requests tenacity ratelimit mcp
fi

"${VENV_DIR}/bin/python" --version
"${VENV_DIR}/bin/python" -c "import mcp_server; print('ucx_hermes ok')"

if [[ "${WITH_KB}" == "true" ]]; then
  PYTHONPATH="${FRAMEWORK_ROOT}" "${VENV_DIR}/bin/python" -c "import ucx_kb; print('ucx_kb ok')"
fi

echo "[ucx-bootstrap] complete"
