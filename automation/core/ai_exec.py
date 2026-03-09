#!/usr/bin/env python3
"""
ai_exec.py — Agent-Agnostic AI Execution Adapter

Handles both cmd (CLI) and litellm (API) engine types for AI Expert Board.
Called by ai_exec.sh wrapper script.

Usage:
    python ai_exec.py <prompt_file> --engine <cmd|litellm> [options]

Engines:
    cmd      - Execute CLI command with prompt piped to stdin
    litellm  - Call OpenAI-compatible API directly

Options:
    --engine <type>           Engine type: "cmd" or "litellm" (required)
    --cmd "<command>"         CLI command to execute (for engine: cmd)
    --model <model>           Model name
    --temperature <f>         Sampling temperature
    --max-tokens <int>        Max output tokens
    --api-base <url>          Base URL for API
    --api-key-env <name>      Env var name holding API key
    --timeout <seconds>       Execution timeout (default: 120)
    --system-prompt-file <f>  Shared context file (cached by API)

Prompt Caching:
    When --system-prompt-file is provided:
    - System message = shared context (cached by OpenAI/Anthropic)
    - User message = persona-specific prompt (from prompt_file)

    This reduces token usage by ~80% for multi-agent reviews.

Exit codes:
    0 - Success
    1 - Agent/API error
    2 - Configuration error
    3 - Timeout
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

try:
    import httpx
except ImportError:
    httpx = None


def run_cmd_engine(
    prompt_file: Path,
    cmd: str,
    timeout: int,
    system_prompt_file: Path | None = None,
) -> str:
    """Execute CLI command with prompt piped to stdin."""
    if not cmd:
        print("[ai_exec] ERROR: engine=cmd requires --cmd parameter", file=sys.stderr)
        sys.exit(2)

    # Build full prompt: system context + user prompt
    prompt_parts = []
    if system_prompt_file and system_prompt_file.exists():
        prompt_parts.append(system_prompt_file.read_text(encoding="utf-8"))
        prompt_parts.append("\n\n--- PERSONA INSTRUCTIONS ---\n\n")
    prompt_parts.append(prompt_file.read_text(encoding="utf-8"))
    prompt_content = "".join(prompt_parts)

    # Execute command with prompt piped to stdin
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            input=prompt_content,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=os.environ,
        )
        if result.returncode != 0:
            print(f"[ai_exec] ERROR: Command failed with exit code {result.returncode}", file=sys.stderr)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            sys.exit(1)
        return result.stdout
    except subprocess.TimeoutExpired:
        print(f"[ai_exec] ERROR: Timed out after {timeout}s", file=sys.stderr)
        sys.exit(3)


def run_litellm_engine(
    prompt_file: Path,
    model: str,
    api_base: str,
    api_key_env: str,
    temperature: float,
    max_tokens: int | None,
    timeout: int,
    system_prompt_file: Path | None = None,
) -> str:
    """
    Call OpenAI-compatible API directly.

    Uses system/user message split for prompt caching:
    - System message: shared context (cached after first call)
    - User message: persona-specific instructions
    """
    # Resolve API key from environment variable
    api_key = os.environ.get(api_key_env, "")
    if not api_key:
        print(f"[ai_exec] ERROR: Environment variable '{api_key_env}' is not set", file=sys.stderr)
        sys.exit(2)

    # Build messages with caching optimization
    messages = []

    # System message (shared context - cached by OpenAI/Anthropic)
    if system_prompt_file and system_prompt_file.exists():
        system_content = system_prompt_file.read_text(encoding="utf-8")
        messages.append({"role": "system", "content": system_content})

    # User message (persona-specific prompt)
    user_content = prompt_file.read_text(encoding="utf-8")
    messages.append({"role": "user", "content": user_content})

    # Build request payload
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    if max_tokens:
        payload["max_tokens"] = max_tokens

    # Make API request
    url = f"{api_base.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        if httpx:
            # Use httpx if available (better for large payloads)
            with httpx.Client(timeout=timeout) as client:
                response = client.post(url, headers=headers, json=payload)

                if response.status_code != 200:
                    print(f"[ai_exec] ERROR: API returned HTTP {response.status_code}", file=sys.stderr)
                    print(response.text, file=sys.stderr)
                    sys.exit(1)

                response_data = response.json()
        else:
            # Fallback to urllib
            import urllib.request
            import urllib.error

            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    response_data = json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                error_body = e.read().decode("utf-8")
                print(f"[ai_exec] ERROR: API returned HTTP {e.code}", file=sys.stderr)
                print(error_body, file=sys.stderr)
                sys.exit(1)

        # Extract content from response
        return response_data["choices"][0]["message"]["content"]

    except Exception as e:
        if "timeout" in str(e).lower() or "timed out" in str(e).lower():
            print(f"[ai_exec] ERROR: Timed out after {timeout}s", file=sys.stderr)
            sys.exit(3)
        print(f"[ai_exec] ERROR: API request failed: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="AI Execution Adapter")
    parser.add_argument("prompt_file", type=Path, help="Path to prompt file (persona-specific)")
    parser.add_argument("--engine", required=True, choices=["cmd", "litellm"], help="Engine type")
    parser.add_argument("--cmd", default="", help="CLI command (for engine=cmd)")
    parser.add_argument("--model", default="gpt-4o", help="Model name")
    parser.add_argument("--temperature", type=float, default=0.3, help="Sampling temperature")
    parser.add_argument("--max-tokens", type=int, default=None, help="Max output tokens")
    parser.add_argument("--api-base", default="https://api.openai.com/v1", help="API base URL")
    parser.add_argument("--api-key-env", default="OPENAI_API_KEY", help="Env var name for API key")
    parser.add_argument("--timeout", type=int, default=120, help="Execution timeout in seconds")
    parser.add_argument(
        "--system-prompt-file",
        type=Path,
        default=None,
        help="Shared context file (system message, cached by API)",
    )
    # Ignored options (for compatibility)
    parser.add_argument("--top-k", type=int, default=None, help="(ignored)")

    args = parser.parse_args()

    # Validate prompt file
    if not args.prompt_file.exists():
        print(f"[ai_exec] ERROR: prompt file not found: {args.prompt_file}", file=sys.stderr)
        sys.exit(2)

    # Validate system prompt file if provided
    if args.system_prompt_file and not args.system_prompt_file.exists():
        print(f"[ai_exec] WARNING: system prompt file not found: {args.system_prompt_file}", file=sys.stderr)
        args.system_prompt_file = None

    # Dispatch to appropriate engine
    if args.engine == "cmd":
        output = run_cmd_engine(
            args.prompt_file,
            args.cmd,
            args.timeout,
            args.system_prompt_file,
        )
    else:  # litellm
        output = run_litellm_engine(
            args.prompt_file,
            args.model,
            args.api_base,
            args.api_key_env,
            args.temperature,
            args.max_tokens,
            args.timeout,
            args.system_prompt_file,
        )

    # Output result
    print(output)


if __name__ == "__main__":
    main()
