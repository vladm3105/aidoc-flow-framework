"""CLI-based AI client that wraps shell commands for CLI agents."""

import datetime
import json
import os
import re
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Optional, TypedDict

from ucx.ai.base import BaseAIClient
from ucx.exceptions import AIClientError
from ucx.utils.logging import (
    get_logger,
    log_cli_command,
    log_cli_result,
    log_ai_request,
    log_ai_response,
)


class CLIToolConfig(TypedDict, total=False):
    command: str
    base_args: list[str]
    system_prompt_flag: Optional[str]
    model_flag: Optional[str]
    input_method: str
    supports_files: bool
    timeout_default: int
    supports_web_search: bool
    allowed_tools_flag: str


class CLIClient(BaseAIClient):
    """
    AI client that invokes CLI agents via shell commands.

    Supports Claude CLI, Codex CLI, Gemini CLI, and other command-line AI tools.
    Handles long prompts via file-based input for reliability.

    Example:
        >>> client = CLIClient(cli_tool="claude")
        >>> response = client.generate("Analyze this document...")

        >>> # Or use Gemini CLI
        >>> client = CLIClient(cli_tool="gemini")

        >>> # Or use Codex CLI
        >>> client = CLIClient(cli_tool="codex", model="gpt-5-codex")
    """

    # Supported CLI tools and their command patterns
    CLI_TOOLS: dict[str, CLIToolConfig] = {
        "claude": {
            "command": "claude",
            "base_args": ["-p", "--dangerously-skip-permissions"],  # -p for print mode, skip permission prompts
            "system_prompt_flag": "--system-prompt",
            "model_flag": "--model",
            "allowed_tools_flag": "--allowedTools",  # For enabling web search
            "input_method": "stdin",  # stdin for reliability with long prompts
            "supports_files": True,
            "supports_web_search": True,  # Claude CLI supports web search via --allowedTools
            "timeout_default": 600,  # Claude CLI can take time for complex prompts
        },
        "gemini": {
            "command": "gemini",
            "base_args": [],
            "system_prompt_flag": None,
            "model_flag": None,
            "input_method": "stdin",
            "supports_files": False,
            "supports_web_search": False,
            "timeout_default": 300,
        },
        "codex": {
            "command": "codex",
            "base_args": ["exec", "-"],
            "system_prompt_flag": None,
            "model_flag": "-m",
            "input_method": "stdin",
            "supports_files": False,
            "supports_web_search": False,
            "timeout_default": 600,
        },
        "ollama": {
            "command": "ollama",
            "base_args": ["run"],
            "system_prompt_flag": None,
            "model_flag": None,  # Model is part of command for ollama
            "input_method": "stdin",
            "supports_files": False,
            "supports_web_search": False,
            "timeout_default": 300,
        },
        "aider": {
            "command": "aider",
            "base_args": ["--message"],
            "system_prompt_flag": None,
            "model_flag": "--model",
            "input_method": "arg",
            "supports_files": True,
            "supports_web_search": False,
            "timeout_default": 300,
        },
    }

    # Model aliases for Claude CLI
    MODEL_ALIASES = {
        "opus": "opus",
        "sonnet": "sonnet",
        "haiku": "haiku",
    }

    # Threshold for using file-based input (characters)
    LONG_PROMPT_THRESHOLD = 10000

    # Common quota/usage-limit phrases surfaced by CLI tools.
    # Covers Anthropic (claude), Google (gemini), OpenAI/Codex, and generic HTTP 429.
    QUOTA_HINT_PATTERNS = [
        "out of extra usage",
        "rate limit",
        "rate_limit",            # OpenAI/Codex JSON field
        "quota",
        "usage limit",
        "too many requests",
        "insufficient_quota",    # OpenAI quota exhausted
        "resource_exhausted",    # Gemini gRPC status
        "overloaded_error",      # Anthropic claude overloaded
        "429",                   # HTTP Too Many Requests
    ]

    # Minimal prompt for the budget/rate-limit probe (Phase 1).
    # Uses only a handful of tokens so cost is negligible.
    BUDGET_CHECK_PROMPT = "Return ONLY: OK"
    BUDGET_CHECK_EXPECTED = "OK"
    # Shorter timeout for the budget probe; a non-responsive tool fails fast.
    BUDGET_CHECK_TIMEOUT = 30  # seconds

    # Per-tool lightweight version/list command used in Phase 2 (capability check).
    # These commands must not invoke the LLM — they only verify the binary/daemon.
    CAPABILITY_CHECKS: dict[str, list[str]] = {
        "claude": ["claude", "--version"],
        "gemini": ["gemini", "--version"],
        "codex": ["codex", "--version"],
        "ollama": ["ollama", "--version"],
        "aider": ["aider", "--version"],
    }

    # Install hints shown when a binary is not found during capability check.
    INSTALL_HINTS: dict[str, str] = {
        "claude": "npm install -g @anthropic-ai/claude-code",
        "gemini": "npm install -g @google/gemini-cli",
        "codex": "npm install -g @openai/codex",
        "ollama": "https://ollama.ai",
        "aider": "pip install aider-chat",
    }

    # Strong signals that a CLI returned an error message instead of model output.
    RESPONSE_ERROR_PREFIXES = [
        "error:",
        "fatal:",
        "exception:",
        "traceback (most recent call last):",
        "usage:",
        "invalid api key",
        "authentication failed",
        "permission denied",
        "command not found",
    ]

    RESPONSE_ERROR_TERMS = [
        "rate limit",
        "quota",
        "too many requests",
        "unauthorized",
        "forbidden",
        "permission denied",
        "invalid api key",
        "authentication failed",
        "try '--help'",
        "failed to",
        "not found",
        "network error",
        "timed out",
    ]

    PREFLIGHT_PROMPT = (
        "Availability check. Return ONLY the current UTC date in YYYY-MM-DD format. "
        "No prose, no markdown, no explanation."
    )

    def __init__(
        self,
        cli_tool: str = "claude",
        model: Optional[str] = None,
        timeout: Optional[int] = None,
        working_dir: Optional[Path] = None,
        env_vars: Optional[dict] = None,
        enable_web_search: bool = False,
    ):
        """
        Initialize CLI client.

        Args:
            cli_tool: CLI tool to use (claude, codex, gemini, ollama, aider)
            model: Model override (opus, sonnet, haiku for Claude; model name for Ollama)
            timeout: Command timeout in seconds (uses tool default if not set)
            working_dir: Working directory for command execution
            env_vars: Additional environment variables
            enable_web_search: Enable web search for deeper analysis (Claude CLI only)
        """
        super().__init__(model=model or cli_tool)
        self.cli_tool = cli_tool.lower()
        self.working_dir = working_dir
        self.env_vars = env_vars or {}
        self.enable_web_search = enable_web_search
        self.logger = get_logger("ucx.ai.cli")

        if self.cli_tool not in self.CLI_TOOLS:
            raise AIClientError(
                f"Unsupported CLI tool: {cli_tool}. "
                f"Supported: {list(self.CLI_TOOLS.keys())}"
            )

        self.tool_config: CLIToolConfig = self.CLI_TOOLS[self.cli_tool]
        self.timeout = timeout or self.tool_config["timeout_default"]

        # Resolve model alias
        self._resolved_model: Optional[str]
        if model and model.lower() in self.MODEL_ALIASES:
            self._resolved_model = self.MODEL_ALIASES[model.lower()]
        else:
            self._resolved_model = model

        # Validate web search support
        if enable_web_search and not self.tool_config["supports_web_search"]:
            self.logger.warning(
                f"Web search requested but {cli_tool} does not support it. Ignoring."
            )
            self.enable_web_search = False

        self.logger.debug(
            f"Initialized CLIClient: tool={self.cli_tool} model={self._resolved_model} "
            f"timeout={self.timeout}s web_search={self.enable_web_search}"
        )

    def generate(
        self,
        prompt: str,
        *,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs,
    ) -> str:
        """
        Generate response using CLI tool.

        Handles long prompts via file-based input for reliability.

        Args:
            prompt: The prompt to send to the CLI tool
            system_prompt: Optional system prompt (passed via flag if supported)
            max_tokens: Ignored for CLI tools
            temperature: Ignored for CLI tools
            **kwargs: Additional arguments passed to subprocess

        Returns:
            Generated text response

        Raises:
            AIClientError: If CLI execution fails
        """
        prompt_len = len(prompt)
        prompt_tokens = self.count_tokens(prompt)

        self.logger.info(
            f"Generate request: tool={self.cli_tool} prompt_chars={prompt_len} "
            f"prompt_tokens={prompt_tokens} has_system_prompt={system_prompt is not None}"
        )

        # Log AI request
        log_ai_request(
            provider=f"cli:{self.cli_tool}",
            model=self._resolved_model or self.cli_tool,
            prompt_tokens=prompt_tokens,
            operation="generate",
        )

        start_time = time.perf_counter()

        try:
            self._run_availability_preflight(**kwargs)

            # For long prompts, use file-based input
            if prompt_len > self.LONG_PROMPT_THRESHOLD:
                self.logger.debug(
                    f"Using file-based input for long prompt ({prompt_len} chars > {self.LONG_PROMPT_THRESHOLD})"
                )
                result = self._execute_with_file_input(prompt, system_prompt, **kwargs)
            else:
                result = self._execute_cli(prompt, system_prompt, **kwargs)

            embedded_error = self._detect_embedded_cli_error(result)
            if embedded_error is not None:
                duration_ms = (time.perf_counter() - start_time) * 1000
                log_ai_response(
                    provider=f"cli:{self.cli_tool}",
                    model=self._resolved_model or self.cli_tool,
                    response_tokens=0,
                    duration_ms=duration_ms,
                    success=False,
                )
                self.logger.error(
                    "CLI returned error-like text payload with exit code 0: %s",
                    embedded_error,
                )
                raise AIClientError(
                    "CLI returned an error-like text response instead of model output: "
                    f"{embedded_error}",
                    model=self.cli_tool,
                )

            duration_ms = (time.perf_counter() - start_time) * 1000
            response_tokens = self.count_tokens(result)

            # Log AI response
            log_ai_response(
                provider=f"cli:{self.cli_tool}",
                model=self._resolved_model or self.cli_tool,
                response_tokens=response_tokens,
                duration_ms=duration_ms,
                success=True,
            )

            self.logger.info(
                f"Generate complete: response_chars={len(result)} "
                f"response_tokens={response_tokens} duration_ms={duration_ms:.0f}"
            )

            return result

        except subprocess.TimeoutExpired:
            duration_ms = (time.perf_counter() - start_time) * 1000
            log_ai_response(
                provider=f"cli:{self.cli_tool}",
                model=self._resolved_model or self.cli_tool,
                response_tokens=0,
                duration_ms=duration_ms,
                success=False,
            )
            self.logger.error(f"CLI command timed out after {self.timeout}s")
            raise AIClientError(
                f"CLI command timed out after {self.timeout}s. "
                f"Consider increasing timeout for long documents.",
                model=self.cli_tool,
            )
        except AIClientError:
            raise
        except subprocess.CalledProcessError as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            log_ai_response(
                provider=f"cli:{self.cli_tool}",
                model=self._resolved_model or self.cli_tool,
                response_tokens=0,
                duration_ms=duration_ms,
                success=False,
            )
            # Some CLI tools emit fatal messages to stdout (not stderr).
            stderr_msg = (e.stderr or "").strip()
            stdout_msg = (e.output or "").strip()
            raw_error_text = "\n".join(part for part in [stderr_msg, stdout_msg] if part).strip()

            if raw_error_text:
                error_msg = raw_error_text[:1000]
            else:
                error_msg = "No error output"

            lower_error = raw_error_text.lower()
            if any(pattern in lower_error for pattern in self.QUOTA_HINT_PATTERNS):
                guidance = (
                    "Usage quota or rate limit detected. "
                    "Choose another model/backend and retry "
                    "(example: --cli-tool gemini --model gemini-2.5-pro)."
                )
                error_msg = f"{error_msg}\n{guidance}" if error_msg != "No error output" else guidance

            self.logger.error(f"CLI command failed: exit_code={e.returncode} error={error_msg}")
            raise AIClientError(
                f"CLI command failed with exit code {e.returncode}: {error_msg}",
                model=self.cli_tool,
            )
        except FileNotFoundError:
            self.logger.error(f"CLI tool not found: {self.tool_config['command']}")
            raise AIClientError(
                f"CLI tool not found: {self.tool_config['command']}. "
                f"Make sure {self.cli_tool} is installed and in PATH.",
                model=self.cli_tool,
            )
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            self.logger.exception(f"CLI execution error: {e}")
            raise AIClientError(
                f"CLI execution error: {str(e)}",
                model=self.cli_tool,
            )

    def _run_availability_preflight(self, **kwargs) -> None:
        """
        Run a 3-phase preflight before every LLM generation call.

        Phase 1 – Budget / rate-limit check
            Send a minimal ``BUDGET_CHECK_PROMPT`` with a short timeout.
            Detect quota / rate-limit signals in the response text or process
            error output.  For Ollama (local daemon) the check is replaced by
            ``ollama list`` to confirm the service and requested model are
            available — Ollama has no API rate limits.
            Result: ``"ok"`` | ``"quota_exceeded"`` | ``"no_response"``

        Phase 2 – Capability check  (runs ONLY when Phase 1 → ``"no_response"``)
            Execute the tool's lightweight version / list command (no LLM call)
            to determine whether the binary / daemon is installed.  This lets us
            give the user an actionable message:
            * Binary missing  → install hint
            * Binary present  → service/network issue

        Phase 3 – Date probe  (runs ONLY when Phase 1 → ``"ok"``)
            Ask the model for the current UTC date.  A mismatch means the model
            is not responding coherently (wrong context, stale state, etc.).
        """
        # ── Phase 1: Budget / rate-limit check ─────────────────────────────
        self.logger.debug("Preflight Phase 1: budget/rate-limit check (%s)", self.cli_tool)
        budget_result = self._run_budget_check(**kwargs)

        if budget_result == "quota_exceeded":
            raise AIClientError(
                f"Usage quota or rate limit detected for {self.cli_tool}. "
                "Choose another model/backend and retry "
                "(example: --cli-tool gemini --model gemini-2.5-pro).",
                model=self.cli_tool,
            )

        if budget_result == "no_response":
            # ── Phase 2: Capability check ───────────────────────────────────
            self.logger.debug(
                "Preflight Phase 2: capability check (%s)", self.cli_tool
            )
            cap_ok, cap_message = self._run_capability_check()
            if not cap_ok:
                raise AIClientError(
                    f"LLM capability check failed for {self.cli_tool}: {cap_message}",
                    model=self.cli_tool,
                )
            # Tool is installed but produced no response → service/network issue
            raise AIClientError(
                f"LLM budget/rate-limit check: no response from {self.cli_tool} "
                f"(tool is present: {cap_message}). "
                "Possible causes: network issue, service outage, or extreme rate limiting. "
                "Try another backend: --cli-tool gemini --model gemini-2.5-pro",
                model=self.cli_tool,
            )

        # ── Phase 3: Date probe ─────────────────────────────────────────────
        self.logger.debug("Preflight Phase 3: date probe (%s)", self.cli_tool)
        expected_utc_date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
        response = self._execute_cli(self.PREFLIGHT_PROMPT, system_prompt=None, **kwargs).strip()

        embedded_error = self._detect_embedded_cli_error(response)
        if embedded_error is not None:
            raise AIClientError(
                "LLM availability preflight failed: CLI returned error-like text response: "
                f"{embedded_error}",
                model=self.cli_tool,
            )

        detected_date = self._extract_iso_date(response)
        if detected_date != expected_utc_date:
            raise AIClientError(
                "LLM availability preflight failed: date probe mismatch. "
                f"Expected UTC date {expected_utc_date}, got '{response}'.",
                model=self.cli_tool,
            )

        self.logger.debug(
            "LLM preflight passed: expected_utc_date=%s detected_date=%s",
            expected_utc_date,
            detected_date,
        )

    def _run_budget_check(self, **kwargs) -> str:
        """
        Phase 1: Send a minimal prompt to detect quota / rate-limit issues early.

        For Ollama (local daemon) this is replaced by an ``ollama list`` probe
        that confirms the service and the requested model are available; Ollama
        has no API rate limits.

        For all other CLI tools the method executes
        ``BUDGET_CHECK_PROMPT`` ("Return ONLY: OK") with
        ``BUDGET_CHECK_TIMEOUT`` seconds and inspects the output.

        Returns:
            ``"ok"``             – Tool is responsive and within quota.
            ``"quota_exceeded"`` – Quota or rate-limit signal detected.
            ``"no_response"``    – No output (timeout, empty, binary error).
        """
        if self.cli_tool == "ollama":
            return self._run_ollama_budget_check()

        try:
            self.logger.debug(
                "Budget check: sending minimal prompt to %s (timeout=%ss)",
                self.cli_tool,
                self.BUDGET_CHECK_TIMEOUT,
            )
            response = self._execute_cli(
                self.BUDGET_CHECK_PROMPT,
                system_prompt=None,
                timeout_override=self.BUDGET_CHECK_TIMEOUT,
            ).strip()

            if not response:
                self.logger.debug("Budget check: empty response from %s", self.cli_tool)
                return "no_response"

            lower = response.lower()
            if any(p in lower for p in self.QUOTA_HINT_PATTERNS):
                self.logger.warning(
                    "Budget check: quota/rate-limit signal in response from %s: %.80s",
                    self.cli_tool,
                    response,
                )
                return "quota_exceeded"

            self.logger.debug("Budget check: OK for %s", self.cli_tool)
            return "ok"

        except subprocess.TimeoutExpired:
            self.logger.warning(
                "Budget check: timed out after %ss for %s",
                self.BUDGET_CHECK_TIMEOUT,
                self.cli_tool,
            )
            return "no_response"

        except subprocess.CalledProcessError as e:
            error_text = ((e.stderr or "") + (e.output or "")).lower()
            if any(p in error_text for p in self.QUOTA_HINT_PATTERNS):
                self.logger.warning(
                    "Budget check: quota/rate-limit in error output for %s: %.120s",
                    self.cli_tool,
                    error_text[:120],
                )
                return "quota_exceeded"
            self.logger.debug(
                "Budget check: CalledProcessError for %s (no_response)", self.cli_tool
            )
            return "no_response"

        except FileNotFoundError:
            self.logger.debug("Budget check: binary not found for %s", self.cli_tool)
            return "no_response"

        except AIClientError as exc:
            if any(p in str(exc).lower() for p in self.QUOTA_HINT_PATTERNS):
                return "quota_exceeded"
            return "no_response"

        except Exception as exc:
            self.logger.debug(
                "Budget check: unexpected error for %s: %s", self.cli_tool, exc
            )
            return "no_response"

    def _run_ollama_budget_check(self) -> str:
        """
        Ollama-specific Phase 1 check: verify service health and model availability.

        Runs ``ollama list`` (instant, no LLM call) to confirm the daemon is
        reachable and the requested model has been pulled.  Ollama is a local
        service with no API quota or rate limits.

        Returns:
            ``"ok"``          – Daemon running and model found in the list.
            ``"no_response"`` – Daemon not running or model not pulled.
        """
        model_name = self._resolved_model or self.cli_tool
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10,
                env={**os.environ, **self.env_vars},
            )
            if result.returncode != 0:
                self.logger.debug(
                    "Ollama list returned exit code %d", result.returncode
                )
                return "no_response"

            if model_name and model_name not in result.stdout:
                self.logger.warning(
                    "Ollama model '%s' not found in 'ollama list'. "
                    "Pull it first: ollama pull %s",
                    model_name,
                    model_name,
                )
                return "no_response"

            self.logger.debug(
                "Ollama service OK, model '%s' available", model_name
            )
            return "ok"

        except subprocess.TimeoutExpired:
            self.logger.warning("ollama list timed out; daemon may not be running")
            return "no_response"
        except FileNotFoundError:
            self.logger.debug("ollama binary not found in PATH")
            return "no_response"
        except Exception as exc:
            self.logger.debug("Ollama budget check error: %s", exc)
            return "no_response"

    def _run_capability_check(self) -> tuple[bool, str]:
        """
        Phase 2: Verify the tool binary is installed and responds to a lightweight
        version / list command.  Called only when Phase 1 returns ``"no_response"``.

        Returns:
            ``(True,  version_line)`` – Binary found and responsive.
            ``(False, error_msg)``    – Binary missing, crashed, or timed out.
        """
        cmd = self.CAPABILITY_CHECKS.get(self.cli_tool)
        if not cmd:
            return True, f"no capability check defined for {self.cli_tool}"

        try:
            env = {**os.environ, **self.env_vars}
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
                env=env,
            )
            combined = (result.stdout + result.stderr).strip()
            first_line = combined.splitlines()[0][:100] if combined else ""

            if result.returncode != 0:
                self.logger.debug(
                    "Capability check for %s returned exit code %d: %s",
                    self.cli_tool,
                    result.returncode,
                    first_line,
                )
                return False, (
                    f"{cmd[0]} returned exit code {result.returncode}: {first_line}"
                )

            self.logger.debug(
                "Capability check OK for %s: %s", self.cli_tool, first_line
            )
            return True, first_line

        except subprocess.TimeoutExpired:
            return False, f"{cmd[0]} capability check timed out after 10s"

        except FileNotFoundError:
            hint = self.INSTALL_HINTS.get(self.cli_tool, f"install {self.cli_tool}")
            return False, f"{cmd[0]} not found in PATH. Install: {hint}"

        except Exception as exc:
            return False, f"{cmd[0]} capability check error: {exc}"

    def _extract_iso_date(self, text: str) -> Optional[str]:
        """Extract first ISO date token from response text."""
        match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", text)
        return match.group(1) if match else None

    def _detect_embedded_cli_error(self, response_text: str) -> Optional[str]:
        """Detect plain-text CLI/tool errors that can arrive with exit code 0."""
        text = (response_text or "").strip()
        if not text:
            return "empty response"

        # Parse JSON-style error payloads if present.
        if text.startswith("{") and text.endswith("}"):
            try:
                payload = json.loads(text)
                if isinstance(payload, dict):
                    value = payload.get("error") or payload.get("errors")
                    if value:
                        return str(value)[:300]
            except Exception:
                pass

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        first_line = lines[0].lower() if lines else ""

        if any(first_line.startswith(prefix) for prefix in self.RESPONSE_ERROR_PREFIXES):
            return lines[0][:300] if lines else "error-like prefix"

        # Avoid false positives for valid markdown documents (headings/frontmatter).
        looks_like_markdown_doc = bool(
            re.search(r"(?m)^#\s+\S", text)
            or re.search(r"(?m)^##\s+\S", text)
            or text.startswith("---\n")
        )

        lowered = text.lower()
        term_hits = sum(1 for term in self.RESPONSE_ERROR_TERMS if term in lowered)

        if not looks_like_markdown_doc and len(text) <= 5000 and term_hits >= 2:
            return lines[0][:300] if lines else text[:300]

        return None

    def _execute_cli(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        timeout_override: Optional[int] = None,
        **kwargs,
    ) -> str:
        """Execute CLI command with stdin input.

        Args:
            prompt: Text to send via stdin.
            system_prompt: Optional system prompt passed via flag.
            timeout_override: Override ``self.timeout`` for this call only.
                Used by the budget-check probe which uses a shorter timeout.
            **kwargs: Ignored; retained for forward-compatibility.
        """
        command = self._build_command(system_prompt=system_prompt)
        codex_last_message_path: Optional[Path] = None

        # Codex CLI prints execution metadata to stdout; capture only the final
        # assistant message to keep generated documents clean.
        if self.cli_tool == "codex":
            with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
                codex_last_message_path = Path(f.name)
            command.extend(["--output-last-message", str(codex_last_message_path)])

        # Log command
        log_cli_command(command, self.timeout)
        self.logger.debug(f"Executing command: {' '.join(command)}")

        # Prepare environment
        env = os.environ.copy()
        env.update(self.env_vars)

        start_time = time.perf_counter()

        try:
            # Execute command with prompt via stdin
            effective_timeout = (
                timeout_override if timeout_override is not None else self.timeout
            )
            result = subprocess.run(
                command,
                input=prompt,
                capture_output=True,
                text=True,
                timeout=effective_timeout,
                cwd=self.working_dir,
                env=env,
            )

            duration_s = time.perf_counter() - start_time

            # Log result
            log_cli_result(
                command=command[0],
                returncode=result.returncode,
                duration_s=duration_s,
                output_len=len(result.stdout),
            )

            if result.returncode != 0:
                self.logger.warning(f"CLI stderr: {result.stderr[:500] if result.stderr else 'empty'}")
                raise subprocess.CalledProcessError(
                    result.returncode,
                    command,
                    output=result.stdout,
                    stderr=result.stderr,
                )

            if self.cli_tool == "codex" and codex_last_message_path and codex_last_message_path.exists():
                codex_message = codex_last_message_path.read_text(encoding="utf-8").strip()
                if codex_message:
                    return codex_message

            return result.stdout.strip()
        finally:
            if codex_last_message_path:
                codex_last_message_path.unlink(missing_ok=True)

    def _execute_with_file_input(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> str:
        """Execute CLI command with file-based input for long prompts."""
        # Create temp file with prompt content
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".md",
            delete=False,
            encoding="utf-8",
        ) as f:
            f.write(prompt)
            temp_path = Path(f.name)

        self.logger.debug(f"Created temp file for prompt: {temp_path}")

        try:
            command = self._build_command(system_prompt=system_prompt)
            codex_last_message_path: Optional[Path] = None

            if self.cli_tool == "codex":
                with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
                    codex_last_message_path = Path(f.name)
                command.extend(["--output-last-message", str(codex_last_message_path)])

            # Log command
            log_cli_command(command, self.timeout)
            self.logger.debug(f"Executing command with file input: {' '.join(command)}")

            env = os.environ.copy()
            env.update(self.env_vars)

            start_time = time.perf_counter()

            try:
                # Read file content and pass via stdin
                with open(temp_path, "r", encoding="utf-8") as f:
                    result = subprocess.run(
                        command,
                        input=f.read(),
                        capture_output=True,
                        text=True,
                        timeout=self.timeout,
                        cwd=self.working_dir,
                        env=env,
                    )

                duration_s = time.perf_counter() - start_time

                # Log result
                log_cli_result(
                    command=command[0],
                    returncode=result.returncode,
                    duration_s=duration_s,
                    output_len=len(result.stdout),
                )

                if result.returncode != 0:
                    self.logger.warning(f"CLI stderr: {result.stderr[:500] if result.stderr else 'empty'}")
                    raise subprocess.CalledProcessError(
                        result.returncode,
                        command,
                        output=result.stdout,
                        stderr=result.stderr,
                    )

                if self.cli_tool == "codex" and codex_last_message_path and codex_last_message_path.exists():
                    codex_message = codex_last_message_path.read_text(encoding="utf-8").strip()
                    if codex_message:
                        return codex_message

                return result.stdout.strip()
            finally:
                if codex_last_message_path:
                    codex_last_message_path.unlink(missing_ok=True)

        finally:
            # Clean up temp file
            temp_path.unlink(missing_ok=True)
            self.logger.debug(f"Cleaned up temp file: {temp_path}")

    def _build_command(
        self,
        system_prompt: Optional[str] = None,
    ) -> list[str]:
        """Build command list for subprocess."""
        command = [self.tool_config["command"]]
        command.extend(self.tool_config["base_args"])

        # Handle model specification
        if self._resolved_model:
            if self.cli_tool == "claude" and self.tool_config["model_flag"]:
                # Only add model flag if it's a recognized alias (opus, sonnet, haiku)
                if self._resolved_model in self.MODEL_ALIASES.values():
                    command.extend([self.tool_config["model_flag"], self._resolved_model])
            elif self.cli_tool == "ollama":
                # For ollama, model is part of command: ollama run <model>
                command = ["ollama", "run", self._resolved_model]
            elif self.tool_config["model_flag"]:
                command.extend([self.tool_config["model_flag"], self._resolved_model])

        # Add system prompt if supported
        if system_prompt and self.tool_config["system_prompt_flag"]:
            command.extend([self.tool_config["system_prompt_flag"], system_prompt])

        # Add web search capability if enabled (Claude CLI only)
        if self.enable_web_search and self.tool_config["allowed_tools_flag"]:
            command.extend([self.tool_config["allowed_tools_flag"], "WebSearch"])
            self.logger.debug("Web search enabled via --allowedTools WebSearch")

        return command

    def generate_with_context(
        self,
        prompt: str,
        context_files: list[Path],
        *,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Generate response with file context.

        Embeds file contents into the prompt for CLI tools.

        Args:
            prompt: The prompt to send
            context_files: Paths to files to include as context
            system_prompt: Optional system prompt
            **kwargs: Additional arguments

        Returns:
            Generated text response
        """
        self.logger.info(f"Generate with context: {len(context_files)} files")

        # Build combined prompt with file contents
        parts = [prompt, "\n\n---\n\n# Context Files\n"]

        for file_path in context_files:
            if file_path.exists():
                content = file_path.read_text(encoding="utf-8")
                parts.append(f"\n## File: {file_path.name}\n\n```\n{content}\n```\n")
                self.logger.debug(f"Added context file: {file_path.name} ({len(content)} chars)")

        full_prompt = "".join(parts)

        return self.generate(
            full_prompt,
            system_prompt=system_prompt,
            **kwargs,
        )

    @classmethod
    def is_available(cls, cli_tool: str) -> bool:
        """Check if a CLI tool is available in PATH."""
        if cli_tool.lower() not in cls.CLI_TOOLS:
            return False

        command = cls.CLI_TOOLS[cli_tool.lower()]["command"]

        try:
            result = subprocess.run(
                ["which", command],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except Exception:
            return False

    @classmethod
    def available_tools(cls) -> list[str]:
        """Return list of available CLI tools."""
        return [tool for tool in cls.CLI_TOOLS if cls.is_available(tool)]

    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for CLI tools.

        Uses a simple approximation since CLI tools don't expose tokenizers.
        Approximation: ~4 characters per token (conservative estimate).

        Args:
            text: Text to count

        Returns:
            Estimated number of tokens
        """
        return len(text) // 4 + 1
