#!/usr/bin/env bash
# =============================================================================
# ai_exec.sh — Agent-Agnostic AI Execution Adapter (Wrapper)
# =============================================================================
# Purpose: Thin wrapper that validates args and calls ai_exec.py for execution.
#
# Usage:   ai_exec.sh <prompt_file> [options]
#
# Engines (via run_review.sh extracted from YAML):
#   engine: cmd      - Execute cmd string with prompt piped to stdin
#   engine: litellm  - Call LiteLLM/OpenAI-compatible API via Python
#
# Options:
#   --engine <type>           Engine type: "cmd" or "litellm" (required)
#   --cmd "<command>"         CLI command to execute (for engine: cmd)
#   --model <model>           Model name
#   --temperature <f>         Sampling temperature
#   --max-tokens <int>        Max output tokens
#   --api-base <url>          Base URL for API
#   --api-key-env <name>      Env var name holding API key
#   --timeout <seconds>       Execution timeout (default: 120)
#   --system-prompt-file <f>  Shared context file (cached by API)
#
# Prompt Caching:
#   When --system-prompt-file is provided:
#   - System message = shared context (cached by OpenAI/Anthropic)
#   - User message = persona-specific prompt (from prompt_file)
#
# Environment Variables (available for cmd string expansion):
#   $P_MODEL, $P_TEMP, $P_MAX_TOKENS, $P_TOP_K
#
# Output:  stdout (raw LLM response text)
# Exit:    0=success, 1=agent error, 2=config error, 3=timeout
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="${SCRIPT_DIR}/ai_exec.py"

# Validate Python script exists
if [[ ! -f "$PYTHON_SCRIPT" ]]; then
  echo "[ai_exec] ERROR: Python script not found: $PYTHON_SCRIPT" >&2
  exit 2
fi

# Export environment variables that cmd engine may need
export P_MODEL="${P_MODEL:-}"
export P_TEMP="${P_TEMP:-}"
export P_MAX_TOKENS="${P_MAX_TOKENS:-}"
export P_TOP_K="${P_TOP_K:-}"

# Pass all arguments to Python script
exec python3 "$PYTHON_SCRIPT" "$@"
