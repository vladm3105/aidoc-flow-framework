#!/usr/bin/env bash
# =============================================================================
# ai_exec.sh — Agent-Agnostic AI Execution Adapter
# =============================================================================
# Purpose: Single entry point for calling any AI agent from pipeline scripts.
#          All pipelines call this instead of claude/opencode/codex directly.
#
# Usage:   ai_exec.sh <prompt_file> [options]
#
# Options:
#   --cmd "<shell command>"  Execute a raw CLI command (prompt piped via stdin)
#                            Example: --cmd "claude -p --model claude-3-7-sonnet"
#   --model <model>          Override model name (for API engines)
#   --timeout <seconds>      Execution timeout
#   --temperature <float>    Sampling temperature (API engines only)
#   --top-k <int>            Top-K sampling (API engines only)
#   --max-tokens <int>       Max output tokens (API engines only)
#   --api-base <url>         Base URL for OpenAI-compatible APIs
#   --api-key-env <name>     Name of env var holding the API key
#
# Env:     AI_AGENT   = claude (default) | opencode | codex | cline | ollama | openai-api | litellm
#          AI_MODEL   = model name within the agent (e.g. claude-sonnet-4)
#          AI_TIMEOUT = max seconds to wait (default: 120)
# Output:  stdout (raw LLM response text)
# Exit:    0=success, 1=agent error, 2=config error, 3=timeout
# =============================================================================

set -euo pipefail

PROMPT_FILE="${1:-}"
shift || true

# Parse optional flags
OVERRIDE_CMD=""
OVERRIDE_MODEL=""
OVERRIDE_TIMEOUT=""
OVERRIDE_TEMPERATURE=""
OVERRIDE_TOP_K=""
OVERRIDE_MAX_TOKENS=""
OVERRIDE_API_BASE=""
OVERRIDE_API_KEY_ENV=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --cmd)         OVERRIDE_CMD="$2";         shift 2 ;;
    --model)       OVERRIDE_MODEL="$2";       shift 2 ;;
    --timeout)     OVERRIDE_TIMEOUT="$2";     shift 2 ;;
    --temperature) OVERRIDE_TEMPERATURE="$2"; shift 2 ;;
    --top-k)       OVERRIDE_TOP_K="$2";       shift 2 ;;
    --max-tokens)  OVERRIDE_MAX_TOKENS="$2";  shift 2 ;;
    --api-base)    OVERRIDE_API_BASE="$2";    shift 2 ;;
    --api-key-env) OVERRIDE_API_KEY_ENV="$2"; shift 2 ;;
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

  # ---------------------------------------------------------------------------
  # Raw CLI command dispatch (highest priority)
  # If --cmd is provided, execute it directly with prompt piped to stdin.
  # This bypasses the engine table entirely for maximum CLI flexibility.
  # Example YAML: cmd: "claude -p --model claude-3-7-sonnet"
  # ---------------------------------------------------------------------------
  if [[ -n "$OVERRIDE_CMD" ]]; then
    bash -c "$OVERRIDE_CMD" < "$prompt_file"
    return $?
  fi

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
    openai-api|litellm)
      local model="${AI_MODEL:-gpt-4o}"
      local base_url="${OVERRIDE_API_BASE:-${OPENAI_BASE_URL:-https://api.openai.com/v1}}"
      
      # Securely resolve API key from requested .env variable name, falling back to OPENAI_API_KEY
      local target_env_var="${OVERRIDE_API_KEY_ENV:-OPENAI_API_KEY}"
      local api_key="${!target_env_var:-}"
      
      if [[ -z "$api_key" ]]; then
        echo "[ai_exec] ERROR: Environment variable '$target_env_var' is not set for openai-api/litellm agent" >&2
        exit 2
      fi
      
      local prompt_content
      prompt_content=$(cat "$prompt_file")
      
      # Optional JSON Parameters
      local temperature="${OVERRIDE_TEMPERATURE:-0.3}"
      
      # Construct curl JSON payload dynamically using jq
      local jq_script='{model: $model, messages: [{role:"user", content: $content}], temperature: ($temp | tonumber)}'
      if [[ -n "$OVERRIDE_MAX_TOKENS" && -n "$OVERRIDE_TOP_K" ]]; then
        jq_script='{model: $model, messages: [{role:"user", content: $content}], temperature: ($temp | tonumber), max_tokens: ($max_tokens | tonumber), top_k: ($top_k | tonumber)}'
      elif [[ -n "$OVERRIDE_MAX_TOKENS" ]]; then
        jq_script='{model: $model, messages: [{role:"user", content: $content}], temperature: ($temp | tonumber), max_tokens: ($max_tokens | tonumber)}'
      elif [[ -n "$OVERRIDE_TOP_K" ]]; then
        jq_script='{model: $model, messages: [{role:"user", content: $content}], temperature: ($temp | tonumber), top_k: ($top_k | tonumber)}'
      fi

      curl -s -f -X POST "${base_url}/chat/completions" \
        -H "Authorization: Bearer ${api_key}" \
        -H "Content-Type: application/json" \
        -d "$(jq -n \
          --arg model "$model" \
          --arg content "$prompt_content" \
          --arg temp "$temperature" \
          --arg max_tokens "${OVERRIDE_MAX_TOKENS:-""}" \
          --arg top_k "${OVERRIDE_TOP_K:-""}" \
          "$jq_script")" \
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
