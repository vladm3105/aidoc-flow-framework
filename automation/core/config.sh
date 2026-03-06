#!/usr/bin/env bash
# =============================================================================
# config.sh — Automation Framework Config Loader
# =============================================================================
# Purpose: Load configuration for all automation pipelines.
#          Precedence: env vars > project .env > automation.yaml defaults
#
# Usage:   source config.sh   (sourced by other scripts, not executed directly)
# =============================================================================

# Only run once per shell session
[[ -n "${_AUTOMATION_CONFIG_LOADED:-}" ]] && return 0
_AUTOMATION_CONFIG_LOADED=1  # No export — guard is per-shell only, not for subprocesses

# Use a private variable so we don't overwrite the calling script's SCRIPT_DIR
_CONFIG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUTOMATION_ROOT="$(dirname "$_CONFIG_DIR")"

# =============================================================================
# Load project .env (if exists at git root or current directory)
# =============================================================================
_load_env_file() {
  local env_file="$1"
  if [[ -f "$env_file" ]]; then
    # Only export lines that are VAR=VALUE (skip comments and blank lines)
    while IFS= read -r line || [[ -n "$line" ]]; do
      [[ "$line" =~ ^#.*$ || -z "$line" ]] && continue
      if [[ "$line" =~ ^([A-Za-z_][A-Za-z0-9_]*)=(.*)$ ]]; then
        local key="${BASH_REMATCH[1]}"
        local val="${BASH_REMATCH[2]}"
        # Don't override if already set in environment
        [[ -z "${!key+x}" ]] && export "$key"="$val"
      fi
    done < "$env_file"
  fi
}

# Load automation framework config .env (ONLY from this framework's config dir)
# Do NOT auto-load from project git roots — that causes cross-contamination.
# Projects should set env vars explicitly in their shell or CI pipeline.
_load_env_file "$AUTOMATION_ROOT/config/.env"

# =============================================================================
# Load automation.yaml defaults (parse with yq if available, else use grep)
# =============================================================================
AUTOMATION_YAML="$AUTOMATION_ROOT/config/automation.yaml"

_yaml_get() {
  local key="$1"
  local default="$2"
  if command -v yq &>/dev/null && [[ -f "$AUTOMATION_YAML" ]]; then
    local val
    val=$(yq ".$key" "$AUTOMATION_YAML" 2>/dev/null || true)
    [[ -z "$val" || "$val" == "null" ]] && echo "$default" || echo "$val"
  else
    echo "$default"
  fi
}

# =============================================================================
# Set defaults (env vars take precedence over yaml, yaml over hardcoded default)
# =============================================================================

# AI Agent configuration
export AI_AGENT="${AI_AGENT:-$(_yaml_get 'ai_agent' 'claude')}"
export AI_MODEL="${AI_MODEL:-$(_yaml_get 'ai_model' '')}"
export AI_TIMEOUT="${AI_TIMEOUT:-$(_yaml_get 'ai_timeout' '120')}"

# Pipeline behaviour
export DRY_RUN="${DRY_RUN:-$(_yaml_get 'dry_run' 'false')}"
export AUTO_APPLY_ENABLED="${AUTO_APPLY_ENABLED:-$(_yaml_get 'auto_apply.enabled' 'true')}"
export AUTO_APPLY_COMMIT="${AUTO_APPLY_COMMIT:-$(_yaml_get 'auto_apply.commit' 'true')}"

# GitHub integration
export GH_REPO="${GH_REPO:-$(_yaml_get 'github.repo' '')}"
export GH_PROJECT="${GH_PROJECT:-$(_yaml_get 'github.project' '')}"
export GH_LABEL_REMEDIATION="${GH_LABEL_REMEDIATION:-council:remediation}"
export GH_LABEL_SOURCE="${GH_LABEL_SOURCE:-source:council}"

# Knowledge Base (graceful if not running)
export KB_ENABLED="${KB_ENABLED:-$(_yaml_get 'knowledge_base.enabled' 'false')}"
export KB_RAG_ENABLED="${KB_RAG_ENABLED:-$(_yaml_get 'knowledge_base.rag' 'false')}"
export KB_GRAPH_ENABLED="${KB_GRAPH_ENABLED:-$(_yaml_get 'knowledge_base.graph' 'false')}"

# ai_exec.sh path (absolute — always points to automation/core/ai_exec.sh)
export AI_EXEC_SH="$_CONFIG_DIR/ai_exec.sh"
