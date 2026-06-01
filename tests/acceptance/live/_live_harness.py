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


import tempfile  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _harness import fixtures_for, headings, run_lint, template_sections  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "conformance"))
from _spec import ARTIFACTS  # noqa: E402

LAYER_OUT_EXT = {
    1: ".md",
    2: ".md",
    3: ".md",
    4: ".md",
    5: ".md",
    6: ".yaml",
    7: ".yaml",
    8: ".yaml",
}


def stage_upstreams_into(workspace: Path, layer_index: int) -> None:
    """Copy every layer 1..N-1 golden into <workspace>/docs/<NN>_<TYPE>/."""
    for upstream_idx in range(1, layer_index):
        upstream_name = ARTIFACTS[upstream_idx - 1]
        src = fixtures_for(upstream_idx, "valid")
        dst = workspace / "docs" / f"{upstream_idx:02d}_{upstream_name}"
        dst.mkdir(parents=True, exist_ok=True)
        for item in src.iterdir():
            if item.is_dir():
                shutil.copytree(item, dst / item.name, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dst / item.name)


def assert_live_layer_conformant(
    testcase,
    layer_index: int,
    prompt: str,
    timeout: int = 420,
    test_id: str | None = None,
) -> None:
    """Stage upstreams, invoke `claude -p`, assert artifact passes structural checks."""
    layer_name = ARTIFACTS[layer_index - 1]
    ext = LAYER_OUT_EXT[layer_index]
    if test_id is None:
        method = getattr(testcase, "_testMethodName", "unknown")
        test_id = f"T3L.{layer_name.lower()}.{method}"
    with tempfile.TemporaryDirectory() as td:
        ws = Path(td)
        stage_upstreams_into(ws, layer_index)
        (ws / "docs" / f"{layer_index:02d}_{layer_name}").mkdir(parents=True, exist_ok=True)
        invoke_skill(prompt, cwd=ws, timeout=timeout, test_id=test_id)

        candidates = list(
            (ws / "docs" / f"{layer_index:02d}_{layer_name}").rglob(f"{layer_name}-01*{ext}")
        )
        testcase.assertTrue(candidates, f"no {layer_name}-01{ext} emitted")
        artifact = candidates[0]

        present = set(headings(artifact))
        missing = [s for s in template_sections(layer_name) if s not in present]
        testcase.assertFalse(missing, f"live {layer_name} missing sections: {missing}")

        rc, findings = run_lint(artifact.parent)
        testcase.assertEqual(rc, 0, f"sdd_doc_lint failed:\n{findings}")
