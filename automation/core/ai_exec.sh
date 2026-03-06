#!/usr/bin/env bash
# =============================================================================
# ai_exec.sh — Agent-Agnostic AI Execution Adapter
# =============================================================================
# Purpose: Single entry point for calling any AI agent from pipeline scripts.
#          All pipelines call this instead of claude/opencode/codex directly.
#
# Usage:   ai_exec.sh <prompt_file> [--model <model>] [--timeout <seconds>]
# Env:     AI_AGENT   = claude (default) | opencode | codex | cline | ollama | openai-api
#          AI_MODEL   = model name within the agent (e.g. claude-sonnet-4)
#          AI_TIMEOUT = max seconds to wait (default: 120)
# Output:  stdout (raw LLM response text)
# Exit:    0=success, 1=agent error, 2=config error, 3=timeout
# =============================================================================

set -euo pipefail

PROMPT_FILE="${1:-}"
shift || true

# Parse optional flags
OVERRIDE_MODEL=""
OVERRIDE_TIMEOUT=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --model)    OVERRIDE_MODEL="$2";   shift 2 ;;
    --timeout)  OVERRIDE_TIMEOUT="$2"; shift 2 ;;
    *) echo "[ai_exec] Unknown flag: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "$PROMPT_FILE" ]]; then
  echo "[ai_exec] ERROR: prompt file argument required" >&2
  echo "Usage: ai_exec.sh <prompt_file> [--model <model>] [--timeout <seconds>]" >&2
  exit 2
fi

if [[ ! -f "$PROMPT_FILE" ]]; then
  echo "[ai_exec] ERROR: prompt file not found: $PROMPT_FILE" >&2
  exit 2
fi

# Load config.sh if available (sets AI_AGENT, AI_MODEL, etc.)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$SCRIPT_DIR/config.sh" ]]; then
  # shellcheck source=config.sh
  source "$SCRIPT_DIR/config.sh"
fi

AI_AGENT="${AI_AGENT:-claude}"
AI_MODEL="${OVERRIDE_MODEL:-${AI_MODEL:-}}"
AI_TIMEOUT="${OVERRIDE_TIMEOUT:-${AI_TIMEOUT:-120}}"

# =============================================================================
# Agent dispatch
# =============================================================================
run_agent() {
  local prompt_file="$1"

  case "$AI_AGENT" in

    # -------------------------------------------------------------------------
    # Claude CLI (Anthropic)
    # https://docs.anthropic.com/claude/docs/claude-code
    # -------------------------------------------------------------------------
    claude)
      local args=("-p")
      [[ -n "$AI_MODEL" ]] && args+=("--model" "$AI_MODEL")
      claude "${args[@]}" < "$prompt_file"
      ;;

    # -------------------------------------------------------------------------
    # OpenCode CLI
    # https://github.com/opencode-ai/opencode
    # -------------------------------------------------------------------------
    opencode)
      local args=()
      [[ -n "$AI_MODEL" ]] && args+=("--model" "$AI_MODEL")
      opencode run "${args[@]}" < "$prompt_file"
      ;;

    # -------------------------------------------------------------------------
    # OpenAI Codex CLI
    # https://github.com/openai/codex
    # -------------------------------------------------------------------------
    codex)
      local args=("exec")
      [[ -n "$AI_MODEL" ]] && args+=("--model" "$AI_MODEL")
      codex "${args[@]}" < "$prompt_file"
      ;;

    # -------------------------------------------------------------------------
    # Cline (CLI mode)
    # https://github.com/cline/cline
    # -------------------------------------------------------------------------
    cline)
      local args=("--prompt" "$prompt_file")
      [[ -n "$AI_MODEL" ]] && args+=("--model" "$AI_MODEL")
      cline "${args[@]}"
      ;;

    # -------------------------------------------------------------------------
    # Ollama (local models)
    # https://ollama.ai
    # -------------------------------------------------------------------------
    ollama)
      local model="${AI_MODEL:-mistral}"
      ollama run "$model" < "$prompt_file"
      ;;

    # -------------------------------------------------------------------------
    # OpenAI-compatible REST API (fallback for any OpenAI-compatible endpoint)
    # -------------------------------------------------------------------------
    openai-api)
      local model="${AI_MODEL:-gpt-4o}"
      local base_url="${OPENAI_BASE_URL:-https://api.openai.com/v1}"
      local api_key="${OPENAI_API_KEY:-}"
      if [[ -z "$api_key" ]]; then
        echo "[ai_exec] ERROR: OPENAI_API_KEY not set for openai-api agent" >&2
        exit 2
      fi
      local prompt_content
      prompt_content=$(cat "$prompt_file")
      curl -s -f -X POST "${base_url}/chat/completions" \
        -H "Authorization: Bearer ${api_key}" \
        -H "Content-Type: application/json" \
        -d "$(jq -n \
          --arg model "$model" \
          --arg content "$prompt_content" \
          '{model: $model, messages: [{role:"user", content: $content}], temperature: 0.3}')" \
        | jq -r '.choices[0].message.content'
      ;;

    # -------------------------------------------------------------------------
    # Gemini CLI
    # https://ai.google.dev/gemini-api/docs/gemini-cli
    # -------------------------------------------------------------------------
    gemini)
      local args=()
      [[ -n "$AI_MODEL" ]] && args+=("--model" "$AI_MODEL")
      gemini "${args[@]}" < "$prompt_file"
      ;;

    *)
      echo "[ai_exec] ERROR: Unknown AI_AGENT='$AI_AGENT'" >&2
      echo "  Supported: claude, opencode, codex, cline, ollama, openai-api, gemini" >&2
      exit 2
      ;;
  esac
}

# =============================================================================
# Execute with timeout
# =============================================================================
if command -v timeout &>/dev/null; then
  timeout "$AI_TIMEOUT" bash -c "$(declare -f run_agent); run_agent '$PROMPT_FILE'"
  EXIT_CODE=$?
  if [[ $EXIT_CODE -eq 124 ]]; then
    echo "[ai_exec] ERROR: Agent timed out after ${AI_TIMEOUT}s (AI_AGENT=$AI_AGENT)" >&2
    exit 3
  fi
  exit $EXIT_CODE
else
  run_agent "$PROMPT_FILE"
fi
