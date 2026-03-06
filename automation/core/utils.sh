#!/usr/bin/env bash
# =============================================================================
# utils.sh — Shared Utilities for Automation Pipelines
# =============================================================================
# Usage: source utils.sh   (sourced by other scripts)
# =============================================================================

[[ -n "${_AUTOMATION_UTILS_LOADED:-}" ]] && return 0
_AUTOMATION_UTILS_LOADED=1  # No export — guard is per-shell only, not for subprocesses

# =============================================================================
# Logging
# =============================================================================
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; NC='\033[0m'

log_info()    { echo -e "${BLUE}[INFO]${NC}    $*"; }
log_ok()      { echo -e "${GREEN}[OK]${NC}      $*"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC}    $*" >&2; }
log_error()   { echo -e "${RED}[ERROR]${NC}   $*" >&2; }
log_step()    { echo -e "\n${CYAN}▶ $*${NC}"; }
log_dry()     { echo -e "${YELLOW}[DRY-RUN]${NC} $*"; }

die() { log_error "$*"; exit 1; }

# =============================================================================
# Dry-run guard — prefix commands with this to skip in dry-run mode
# =============================================================================
# Usage: run_or_dry git commit -m "..."
run_or_dry() {
  if [[ "${DRY_RUN:-false}" == "true" ]]; then
    log_dry "Would run: $*"
  else
    "$@"
  fi
}

# =============================================================================
# JSON helpers (requires jq)
# =============================================================================
require_jq() {
  command -v jq &>/dev/null || die "jq is required but not installed. Run: apt-get install jq"
}

json_get() {
  local json="$1" key="$2" default="${3:-}"
  local val
  val=$(echo "$json" | jq -r "$key" 2>/dev/null || echo "")
  [[ -z "$val" || "$val" == "null" ]] && echo "$default" || echo "$val"
}

json_length() {
  local json="$1"
  echo "$json" | jq 'length' 2>/dev/null || echo "0"
}

# Validate JSON array from file
assert_valid_json_array() {
  local file="$1"
  if ! jq -e '. | type == "array"' "$file" &>/dev/null; then
    die "Expected a JSON array in file: $file"
  fi
}

# =============================================================================
# Git helpers
# =============================================================================
git_root() {
  git rev-parse --show-toplevel 2>/dev/null || die "Not inside a git repository"
}

git_current_branch() {
  git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown"
}

git_commit_if_changes() {
  local msg="$1"
  shift
  local files=("$@")
  if git diff --quiet "${files[@]}" 2>/dev/null && git diff --cached --quiet "${files[@]}" 2>/dev/null; then
    log_info "No changes to commit for: ${files[*]}"
    return 0
  fi
  run_or_dry git add "${files[@]}"
  run_or_dry git commit --no-verify -m "$msg"
  log_ok "Committed: $msg"
}

# =============================================================================
# File helpers
# =============================================================================
require_file() {
  local f="$1"
  [[ -f "$f" ]] || die "Required file not found: $f"
}

require_cmd() {
  local cmd="$1"
  command -v "$cmd" &>/dev/null || die "Required command not found: $cmd (install it first)"
}

tmp_file() {
  local prefix="${1:-automation}"
  mktemp "/tmp/${prefix}.XXXXXX"
}

cleanup_on_exit() {
  local files=("$@")
  # shellcheck disable=SC2064
  trap "rm -f ${files[*]}" EXIT
}

# =============================================================================
# Priority helpers
# =============================================================================
priority_label() {
  case "${1^^}" in
    P0) echo "priority:P0" ;;
    P1) echo "priority:P1" ;;
    P2) echo "priority:P2" ;;
    P3) echo "priority:P3" ;;
    *)  echo "priority:P2" ;;  # default to P2 if unknown
  esac
}

priority_lifecycle_label() {
  case "${1^^}" in
    P0) echo "ai:ready" ;;       # immediate AI pickup
    P1) echo "ai:backlog" ;;     # sprint planning
    P2) echo "ai:backlog" ;;
    *)  echo "ai:backlog" ;;
  esac
}

# =============================================================================
# Action type classifier (used by 03_auto_apply.sh)
# =============================================================================
is_auto_applicable() {
  local action_type="${1:-}"
  case "$action_type" in
    frontmatter_tag|section_add|matrix_row|tag_correction|dependency_add)
      return 0 ;;  # structural — safe to auto-apply
    *)
      return 1 ;;  # content/architecture — send to GitHub Issues
  esac
}
