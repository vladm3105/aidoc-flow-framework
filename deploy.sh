#!/usr/bin/env bash
# deploy.sh — Unified deployment & upgrade entrypoint for aidoc-flow-framework.
# Usage:
#   ./deploy.sh --target <target-repo-dir> [--kind pin|symlink] [--shared <path>] [--dry-run] [--force] [--yes]
#
# Idempotently detects whether the target is an initial install or a live upgrade:
#   - If <target>/.aidoc does not exist (or lacks framework link/pin): runs framework/scripts/install.sh
#   - If <target>/.aidoc exists: runs framework/scripts/upgrade.sh to the current canon VERSION

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION="$(tr -d '[:space:]' < "$SCRIPT_DIR/framework/VERSION")"

TARGET=""
KIND="symlink"
SHARED="$SCRIPT_DIR"
DRY_RUN=0
FORCE=0
YES=0

usage() {
  cat <<EOF
Usage: $(basename "$0") --target <path> [options]

Options:
  --target <path>       Target repository directory (required)
  --kind <pin|symlink>  Deployment kind (default: symlink)
  --shared <path>       Shared framework location for symlink (default: $SCRIPT_DIR)
  --dry-run             Preview operations without mutating disk
  --force               Allow re-deploying same version or non-destructive reinstall
  --yes                 Confirm operations non-interactively
  -h, --help            Show this help message
EOF
  exit 1
}

EXTRA_ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET="${2:-}"; shift 2 ;;
    --kind) KIND="${2:-}"; shift 2 ;;
    --shared) SHARED="${2:-}"; shift 2 ;;
    --dry-run) DRY_RUN=1; EXTRA_ARGS+=("--dry-run"); shift ;;
    --force) FORCE=1; EXTRA_ARGS+=("--force"); shift ;;
    --yes) YES=1; EXTRA_ARGS+=("--yes"); shift ;;
    -h|--help) usage ;;
    *) echo "ERROR: Unknown option: $1" >&2; usage ;;
  esac
done

if [[ -z "$TARGET" ]]; then
  echo "ERROR: --target is required." >&2
  usage
fi

if [[ ! -d "$TARGET" ]]; then
  echo "ERROR: Target directory '$TARGET' does not exist." >&2
  exit 1
fi

TARGET="$(cd "$TARGET" && pwd)"

if [[ ! -e "$TARGET/.aidoc/framework" && ! -L "$TARGET/.aidoc/framework" ]]; then
  echo "==> Fresh install: deploying .aidoc on $TARGET (version: $VERSION, kind: $KIND)"
  INSTALL_ARGS=("$TARGET" "--kind" "$KIND")
  if [[ "$KIND" == "symlink" ]]; then
    INSTALL_ARGS+=("--shared" "$SHARED")
  else
    INSTALL_ARGS+=("--canon-dir" "$SCRIPT_DIR")
  fi
  "${SCRIPT_DIR}/framework/scripts/install.sh" "${INSTALL_ARGS[@]}" "${EXTRA_ARGS[@]}"
else
  echo "==> Brownfield upgrade: re-adopting framework on $TARGET (version: $VERSION, kind: $KIND)"
  UPGRADE_ARGS=("$TARGET" "--to" "$VERSION" "--kind" "$KIND")
  if [[ "$KIND" == "symlink" ]]; then
    UPGRADE_ARGS+=("--shared" "$SHARED")
  else
    UPGRADE_ARGS+=("--canon-dir" "$SCRIPT_DIR")
  fi
  "${SCRIPT_DIR}/framework/scripts/upgrade.sh" "${UPGRADE_ARGS[@]}" "${EXTRA_ARGS[@]}"
fi
