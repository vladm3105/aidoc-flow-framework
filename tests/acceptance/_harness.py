"""Shared harness for per-layer acceptance tests (deterministic tier)."""

import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import ARTIFACTS, plugin_bundle_root, template_path

FIXTURES_ROOT = Path(__file__).resolve().parent / "fixtures"


def fixtures_for(layer_index: int, kind: str) -> Path:
    """Return the fixture directory for `valid` or `broken` per 1-indexed layer."""
    layer_name = ARTIFACTS[layer_index - 1].lower()
    folder = f"layer_{layer_index:02d}_{layer_name}"
    return FIXTURES_ROOT / folder / kind


def template_sections(name: str, subtype: str | None = None) -> list[str]:
    """Return required section keys from <TYPE>-TEMPLATE.yaml, in order.

    Honors two template-side optional/conditional flags introduced by
    CLEANUP-PR-D (PRD ``component_decomposition``) and CLEANUP-PR-E
    (IPLAN sub-types):

    * ``_required: false`` — unconditionally optional; excluded.
    * ``_required_when_subtype: [list]`` — required only when ``subtype``
      is in the list. When ``subtype`` is None, sections gated by subtype
      are excluded (matches the BRD/PRD/EARS/BDD/ADR/SPEC/TDD case where
      templates don't use the marker).

    The legacy ``required: False`` (no underscore) is honored too, with
    the same semantics as the underscore-prefixed form.
    """
    with template_path(name).open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    out: list[str] = []
    for key, value in data.items():
        if not isinstance(value, dict) or key == "metadata":
            continue
        if value.get("_required") is False:
            continue
        gated = value.get("_required_when_subtype")
        if isinstance(gated, list):
            if subtype is None or subtype not in gated:
                continue
        if value.get("required") is False:
            continue
        out.append(key)
    return out


def subtype_of(golden: Path) -> str:
    """Read ``document_control.subtype`` from a golden; default ``combined``.

    IPLAN sub-types per CLEANUP-PR-E item 17. Goldens authored before the
    sub-type system may omit the field; the template documents
    ``combined`` as the backward-compat default. Honored here so legacy
    goldens lint correctly without a fixture rewrite.

    YAML goldens may carry an optional ``---``-fenced frontmatter block;
    ``document_control`` lives in the body after the closing fence. This
    helper strips an optional frontmatter before parsing so the body's
    top-level keys are visible.
    """
    if golden.suffix == ".yaml":
        text = golden.read_text(encoding="utf-8")
        lines = text.splitlines()
        if lines and lines[0].strip() == "---":
            for i in range(1, len(lines)):
                if lines[i].strip() == "---":
                    text = "\n".join(lines[i + 1 :])
                    break
        data = yaml.safe_load(text) or {}
        dc = data.get("document_control") or {}
        return str(dc.get("subtype") or "combined")
    # .md goldens: no subtype slot; treat as "combined" by default.
    return "combined"


def run_lint(target: Path) -> tuple[int, list[dict]]:
    """Run sdd_doc_lint in JSON mode (Task 1.3) and return (returncode, findings).

    Re-raises with diagnostics on JSON decode failure rather than silently
    returning empty findings (which would hide linter bugs).
    """
    result = subprocess.run(
        [sys.executable, "-m", "sdd_doc_lint", str(target), "--format=json"],
        env={"PYTHONPATH": str(plugin_bundle_root()), "PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        findings = json.loads(result.stdout or "[]")
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"sdd_doc_lint produced non-JSON output (exit {result.returncode}):\n"
            f"--- STDOUT ---\n{result.stdout!r}\n"
            f"--- STDERR ---\n{result.stderr!r}"
        ) from exc
    return result.returncode, findings


def headings(artifact: Path) -> list[str]:
    """Return canonical section identifiers from an artifact.

    For .md / .feature: H2 headings normalized like sdd_doc_lint does.
    For .yaml: top-level keys from the body (excluding `_*` and `metadata`).
      Tolerates an optional `---` frontmatter fence — the body after the
      closing fence is parsed as YAML for its top-level keys. Required
      because some YAML goldens carry a `doc_id`-bearing frontmatter for
      TRACE-RES-001 indexing.
    """
    text = artifact.read_text(encoding="utf-8")
    if artifact.suffix in {".md", ".feature"}:
        out = []
        for line in text.splitlines():
            if line.startswith("## "):
                raw = line.lstrip("# ").strip().lower()
                out.append(re.sub(r"[^a-z0-9]+", "_", raw).strip("_"))
        return out
    if artifact.suffix == ".yaml":
        # Strip an optional frontmatter block (--- ... ---) so the body's
        # top-level YAML keys are visible. Goldens that don't use the fence
        # are unaffected (the whole file IS the body).
        lines = text.splitlines()
        if lines and lines[0].strip() == "---":
            for i in range(1, len(lines)):
                if lines[i].strip() == "---":
                    text = "\n".join(lines[i + 1 :])
                    break
        data = yaml.safe_load(text) or {}
        return [k for k in data if not k.startswith("_") and k != "metadata"]
    return []


class LayerHarness:
    """Mix-in providing the four per-layer acceptance assertions.

    Subclasses set `LAYER_INDEX` (1-8) and `LAYER_NAME` (e.g. "BRD") and inherit
    from both `unittest.TestCase` AND this mix-in.
    """

    LAYER_INDEX: int  # subclass sets this
    LAYER_NAME: str  # subclass sets this

    def assert_golden_passes_lint(self, golden: Path):
        rc, findings = run_lint(golden.parent)
        self.assertEqual(
            rc,
            0,  # type: ignore
            f"golden {golden.name} lint failed:\n{findings}",
        )
        self.assertEqual(
            [],
            findings,  # type: ignore
            f"golden {golden.name} emitted findings:\n{findings}",
        )

    def assert_broken_fixture_emits_expected_codes(self, broken_dir: Path):
        for codes_file in broken_dir.glob("*_drift_codes.yaml"):
            with codes_file.open(encoding="utf-8") as fh:
                manifest = yaml.safe_load(fh)
            fixture = broken_dir / manifest["file"]
            # Lint the directory containing the fixture so the linter scopes correctly.
            _, findings = run_lint(fixture.parent)
            emitted_codes = {f["code"] for f in findings}
            for expected in manifest["expected_findings"]:
                code = expected["code"]
                self.assertIn(
                    code,
                    emitted_codes,  # type: ignore
                    f"{fixture.name}: missing expected {code}; emitted: {emitted_codes}",
                )

    def assert_template_sections_present_in_golden(self, golden: Path):
        # Pass the golden's subtype so `_required_when_subtype:` sections
        # (CLEANUP-PR-E item 17, IPLAN) are filtered correctly. Layers
        # whose templates don't use the marker are unaffected by the value.
        expected = template_sections(self.LAYER_NAME, subtype=subtype_of(golden))
        present = set(headings(golden))
        missing = [s for s in expected if s not in present]
        self.assertFalse(
            missing,  # type: ignore
            f"{golden.name}: missing template sections {missing}\npresent: {sorted(present)}",
        )

    def assert_cumulative_upstream_tags_resolve(self, golden: Path):
        """For layer index N > 1, every @brd/@prd/... reference resolves.

        Tag format rules:
          BRD, PRD, EARS, BDD       — element refs in DOT form: TYPE.NN.SS.xxxx
          ADR, SPEC                 — refs allowed in either DOT or DASH form
          TDD                       — refs allowed in either DOT or DASH form
          IPLAN                     — accepts dash-or-dot; never appears upstream in practice
        """
        if self.LAYER_INDEX == 1:
            return  # BRD has no upstream
        text = golden.read_text(encoding="utf-8")
        DOT_ONLY = {"BRD", "PRD", "EARS", "BDD"}
        for upstream_idx in range(1, self.LAYER_INDEX):
            upstream_name = ARTIFACTS[upstream_idx - 1]
            tag = f"@{upstream_name.lower()}:"
            dot = rf"{tag}\s+{upstream_name}\.\d+\.\d+\.[a-f0-9]{{4,8}}"
            dash = rf"{tag}\s+{upstream_name}-\d+"
            pattern = dot if upstream_name in DOT_ONLY else rf"(?:{dot})|(?:{dash})"
            self.assertRegex(
                text,
                pattern,  # type: ignore
                f"{golden.name}: no {tag} reference matching {pattern}",
            )
