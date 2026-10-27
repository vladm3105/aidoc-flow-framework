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
KIND=""
KIND_SPECIFIED=0
SHARED="$SCRIPT_DIR"

usage() {
  cat <<EOF
Usage: $(basename "$0") --target <path> [options]

Options:
  --target <path>       Target repository directory (required)
  --kind <pin|symlink>  Deployment kind (default: pin)
  --shared <path>       Shared framework location for symlink (default: $SCRIPT_DIR)
  --dry-run             Preview operations without mutating disk
  --force               Allow re-deploying same version or non-destructive reinstall
  --yes                 Confirm operations non-interactively
  --no-stack-policy     Skip scaffolding stack-policy.yaml
  --no-adr              Skip scaffolding docs/sdd/05_ADR/ADR-00_index.yaml
  --no-agents           Skip scaffolding AGENTS.md
  --no-blueprints       Skip scaffolding .aidoc/project/governance/ blueprints
  --no-precommit        Skip scaffolding .pre-commit-config.yaml
  --author <name>       Set author name for scaffolded docs
  --canon-sha <sha>     Verify canon commit SHA
  -h, --help            Show this help message
EOF
  exit 1
}

EXTRA_ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET="${2:-}"; shift 2 ;;
    --kind) KIND="${2:-}"; KIND_SPECIFIED=1; shift 2 ;;
    --shared) SHARED="${2:-}"; shift 2 ;;
    --dry-run) EXTRA_ARGS+=("--dry-run"); shift ;;
    --force) EXTRA_ARGS+=("--force"); shift ;;
    --yes) EXTRA_ARGS+=("--yes"); shift ;;
    --no-stack-policy) EXTRA_ARGS+=("--no-stack-policy"); shift ;;
    --no-adr) EXTRA_ARGS+=("--no-adr"); shift ;;
    --no-agents) EXTRA_ARGS+=("--no-agents"); shift ;;
    --no-blueprints) EXTRA_ARGS+=("--no-blueprints"); shift ;;
    --no-precommit) EXTRA_ARGS+=("--no-precommit"); shift ;;
    --author) [[ $# -ge 2 ]] || { echo "ERROR: --author needs a value" >&2; exit 1; }; EXTRA_ARGS+=("--author" "$2"); shift 2 ;;
    --canon-sha) [[ $# -ge 2 ]] || { echo "ERROR: --canon-sha needs a value" >&2; exit 1; }; EXTRA_ARGS+=("--canon-sha" "$2"); shift 2 ;;
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
  if [[ "$KIND_SPECIFIED" -eq 0 ]]; then
    KIND="pin"
  fi
  if [[ "$KIND" == "symlink" ]]; then
    echo "WARNING: '--kind symlink' is deprecated and raw filesystem symlinks in version control" >&2
    echo "         are strictly forbidden per docs/AIDOC_WORKSTATION_STANDARD.md:341." >&2
    echo "         Consider using '--kind pin' or Git submodule instead." >&2
  fi
  echo "==> Fresh install: deploying .aidoc on $TARGET (version: $VERSION, kind: $KIND)"
  INSTALL_ARGS=("$TARGET" "--kind" "$KIND")
  if [[ "$KIND" == "symlink" ]]; then
    INSTALL_ARGS+=("--shared" "$SHARED")
  else
    INSTALL_ARGS+=("--canon-dir" "$SCRIPT_DIR")
  fi
  "${SCRIPT_DIR}/framework/scripts/install.sh" "${INSTALL_ARGS[@]}" "${EXTRA_ARGS[@]}"
else
  echo "==> Brownfield upgrade: re-adopting framework on $TARGET (version: $VERSION)"
  UPGRADE_ARGS=("$TARGET" "--to" "$VERSION")
  if [[ "$KIND_SPECIFIED" -eq 1 ]]; then
    UPGRADE_ARGS+=("--kind" "$KIND")
    if [[ "$KIND" == "symlink" ]]; then
      echo "WARNING: '--kind symlink' is deprecated and raw filesystem symlinks in version control" >&2
      echo "         are strictly forbidden per docs/AIDOC_WORKSTATION_STANDARD.md:341." >&2
      UPGRADE_ARGS+=("--shared" "$SHARED")
    else
      UPGRADE_ARGS+=("--canon-dir" "$SCRIPT_DIR")
    fi
  else
    # Auto-detect argument pairing to match upgrade.sh's detected kind
    if [[ -L "$TARGET/.aidoc/framework" ]]; then
      UPGRADE_ARGS+=("--shared" "$SHARED")
    else
      UPGRADE_ARGS+=("--canon-dir" "$SCRIPT_DIR")
    fi
  fi
  "${SCRIPT_DIR}/framework/scripts/upgrade.sh" "${UPGRADE_ARGS[@]}" "${EXTRA_ARGS[@]}"
fi
