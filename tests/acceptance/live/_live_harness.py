"""Live tier harness — skipped unless LIVE=1 in env."""

import json
import os
import shutil
import subprocess
import sys
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "conformance"))
from _spec import plugin_bundle_root

LIVE_ENABLED = os.environ.get("LIVE") == "1"
HAS_CLAUDE = shutil.which("claude") is not None

skipUnlessLive = unittest.skipUnless(
    LIVE_ENABLED and HAS_CLAUDE,
    "live tier disabled (set LIVE=1 and ensure `claude` CLI is on PATH)",
)


TOKEN_LEDGER = Path(os.environ.get("TOKEN_LEDGER", "tmp/token-ledger.json"))


def _append_ledger(test_id: str, prompt_chars: int, response_chars: int, elapsed_s: float) -> None:
    TOKEN_LEDGER.parent.mkdir(parents=True, exist_ok=True)
    ledger: list[dict] = []
    if TOKEN_LEDGER.exists():
        try:
            ledger = json.loads(TOKEN_LEDGER.read_text(encoding="utf-8")) or []
        except json.JSONDecodeError:
            ledger = []
    ledger.append(
        {
            "test_id": test_id,
            "approx_input_tokens": prompt_chars // 4,
            "approx_output_tokens": response_chars // 4,
            "elapsed_s": round(elapsed_s, 2),
        }
    )
    TOKEN_LEDGER.write_text(json.dumps(ledger, indent=2), encoding="utf-8")


def invoke_skill(prompt: str, cwd: Path, timeout: int = 300, test_id: str = "unknown") -> str:
    """Invoke a /aidoc-flow:* command via `claude -p` and return stdout."""
    start = time.monotonic()
    result = subprocess.run(
        [
            "claude",
            "--plugin-dir",
            str(plugin_bundle_root()),
            "--dangerously-skip-permissions",
            "-p",
            prompt,
        ],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    elapsed = time.monotonic() - start
    _append_ledger(
        test_id, prompt_chars=len(prompt), response_chars=len(result.stdout), elapsed_s=elapsed
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude -p exit {result.returncode}:\n{result.stderr}")
    return result.stdout
