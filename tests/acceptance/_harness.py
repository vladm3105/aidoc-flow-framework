"""Shared harness for per-layer acceptance tests (deterministic tier)."""

import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import ARTIFACTS, plugin_bundle_root, template_path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from sdd_doc_lint.trace_graph import ELEM_FORM

FIXTURES_ROOT = Path(__file__).resolve().parent / "fixtures"

#: Manifests of KNOWN, accepted lint warnings per lint target — deliberately
#: OUTSIDE `fixtures/`. A manifest inside the fixture tree is ingested by the
#: linter as an artifact when it lands in a `NN_LAYER/` directory, and
#: `live/_live_harness.py:stage_upstreams_into` copies every item of a `valid/`
#: dir into exactly such a directory. See ACCEPTANCE-TIER-DRIFT-UNTRACKED plan D1.
EXPECTED_WARNINGS_ROOT = Path(__file__).resolve().parent / "expected_warnings"


def load_layer_document(path: Path) -> dict:
    """Parse a fixture's YAML body, tolerating a frontmatter block.

    A `.yaml` layer artifact may carry a terminated ``---`` frontmatter fence
    (carrying ``doc_id``, which is what makes it visible to ``build_edge_graph``)
    followed by the document body. That is **two YAML documents in one stream**,
    so a bare ``yaml.safe_load`` raises ``ComposerError`` on it — the trap
    recorded in ``CLAUDE.md`` § "Acceptance harness".

    Strips the frontmatter block, then loads the body. Files with no fence load
    unchanged, so this is safe for every shape a fixture currently takes.

    Extracted from the two copies that already existed in this module
    (``golden_subtype`` and ``template_sections``' golden reader) rather than
    written fresh — they had the logic and the per-layer tests did not, which is
    why repairing a fixture's fence broke four of them.
    """
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                text = "\n".join(lines[i + 1 :])
                break
    return yaml.safe_load(text) or {}


def _manifest_path(target: Path) -> Path:
    """Return the manifest file for a lint target (may not exist)."""
    rel = target.resolve().relative_to(FIXTURES_ROOT.resolve()).as_posix()
    return EXPECTED_WARNINGS_ROOT / f"{rel.replace('/', '__')}.yaml"


def _finding_ref(finding: dict) -> str:
    """Return the per-code discriminator that identifies WHICH finding this is.

    Counts alone cannot detect substitution: ACC01/COV02 report against the host
    document, so re-pairing one element while orphaning another leaves the count
    unchanged. The discriminator is per-code because the codes expose different
    machine-readable handles:

    * ``ACC01`` / ``COV02`` — the element ID, taken as the single-quoted token
      and then VALIDATED with the canonical ``ELEM_FORM``. Two steps, because
      ``ELEM_FORM`` is fully anchored and cannot *search* a message.
    * ``REFGRAN01`` — the cited tag; its message carries no element ID at all,
      only a literal ``TYPE.NN.SS.xxxx`` placeholder.

    A code exposing neither raises rather than silently degrading to a countable
    blob: an un-pinnable rule must be handled deliberately.
    """
    message = finding["message"]
    for token in re.findall(r"'([^']+)'", message):
        if ELEM_FORM.match(token):
            return token
    tag = re.search(r"@(\w+):\s*([A-Z]+-\d+)", message)
    if tag:
        return f"@{tag.group(1)}: {tag.group(2)}"
    raise AssertionError(
        f"cannot derive a stable discriminator for {finding['code']} in "
        f"{finding['file']}: {message!r}. Extend _finding_ref() deliberately — "
        "do not fall back to counting, which cannot detect substitution."
    )


def _finding_key(finding: dict, target: Path) -> tuple[str, str, str]:
    """Return ``(code, target-relative file, ref)`` for a linter finding.

    The linter reports ``file`` relative to CWD, or absolute when the target is
    outside CWD (`sdd_doc_lint/__init__.py` ``_collect``). Neither is stable, so
    normalize to target-relative before comparing against a committed manifest.
    """
    emitted = Path(finding["file"])
    resolved = (Path.cwd() / emitted).resolve()
    try:
        rel = resolved.relative_to(target.resolve()).as_posix()
    except ValueError as exc:
        # Reachable, not hypothetical: the coverage/granularity rules report
        # `rel_by_doc.get(host, host)`, which is a BARE DOC ID (e.g. "BDD-01")
        # when the host is absent from the path map. The raw ValueError names a
        # path that does not exist and mentions neither the code nor the cause.
        raise AssertionError(
            f"{finding['code']}: cannot place {finding['file']!r} inside "
            f"{target}. The linter reports a bare doc id rather than a path when "
            "a cited host document is missing from the corpus — add the host to "
            "the fixture, or extend _finding_key() to handle doc-id references."
        ) from exc
    return (finding["code"], rel, _finding_ref(finding))


def expected_warnings(target: Path) -> dict[tuple[str, str, str], int]:
    """Return the accepted-warning multiset for a lint target.

    No manifest → empty multiset, which reproduces the historical
    "zero findings" contract exactly for every target that has none.
    """
    path = _manifest_path(target)
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    declared = str(data.get("target", "")).strip()
    derived = target.resolve().relative_to(FIXTURES_ROOT.resolve()).as_posix()
    # Explicit raises, NOT `assert`: these validate COMMITTED DATA, not a test
    # outcome, and `python -O` strips assert statements — which would let a
    # manifest with a mismatched target, a missing reason, or duplicate keys load
    # silently. `-O` must not weaken a data contract.
    if declared != derived:
        raise ValueError(
            f"{path.name}: `target: {declared}` does not match the target its "
            f"filename encodes ({derived}) — a renamed manifest must not silently "
            "pin a different directory"
        )
    out: dict[tuple[str, str, str], int] = {}
    for entry in data.get("expected_warnings") or []:
        key = (entry["code"], entry["file"], entry["ref"])
        if key in out:
            raise ValueError(f"{path.name}: duplicate entry {key} — use `count:` for multiplicity")
        if not str(entry.get("reason", "")).strip():
            raise ValueError(
                f"{path.name}: {key} has no `reason`. Every pinned warning must "
                "state what would clear it, or the manifest becomes an excuse list"
            )
        out[key] = int(entry["count"])
    return out


def assert_no_orphan_manifests(case) -> None:
    """Every manifest must name a lint target that exists.

    Bidirectional matching makes a STALE ENTRY fail, but nothing makes a stale
    FILE fail: a manifest orphaned by a fixture rename would sit forever pinning
    warnings nothing emits. This closes that gap at the file level.
    """
    for path in sorted(EXPECTED_WARNINGS_ROOT.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        target = FIXTURES_ROOT / str(data.get("target", "")).strip()
        case.assertTrue(
            target.is_dir(),
            f"{path.name}: `target: {data.get('target')}` is not a directory — "
            "orphaned by a fixture rename? Delete the manifest or fix the target",
        )


def assert_lint_matches_manifest(case, target: Path) -> None:
    """Assert a lint target is gate-clean and emits exactly its pinned warnings.

    Three assertions, in this order:

    1. ``rc == 0`` FIRST — a registry-unavailable exit produces empty stdout,
       which would otherwise surface as the nonsense "every entry is stale".
    2. zero ``error`` findings — the framework's own gate.
    3. the ``warning`` multiset equals the manifest's, BOTH directions. A new
       warning fails (drift); a pinned warning that no longer fires also fails
       (the manifest must shrink), so it cannot rot into an excuse list.
    """
    rc, findings = run_lint(target)
    case.assertEqual(rc, 0, f"{target.name}: lint exited {rc}:\n{findings}")

    errors = [f for f in findings if f["severity"] == "error"]
    case.assertEqual([], errors, f"{target.name}: lint errors:\n{errors}")

    # A finding at any OTHER severity would be gated by neither check — the error
    # assertion filters `== "error"` and the multiset filters `== "warning"`, so a
    # third value falls through both and a whole new rule could ship unnoticed.
    # That is precisely the failure this contract exists to prevent, one severity
    # string to the left. The plan's Pass 4 relied on "the linter emits only error
    # and warning"; this asserts it instead of assuming it.
    unhandled = sorted({f["severity"] for f in findings} - {"error", "warning"})
    case.assertEqual(
        [],
        unhandled,
        f"{target.name}: findings at unhandled severity {unhandled} are neither "
        "gated as errors nor pinned as warnings. Decide which they are and extend "
        "this contract — do not let them fall through.",
    )

    actual: dict[tuple[str, str, str], int] = {}
    for finding in findings:
        if finding["severity"] != "warning":
            continue
        key = _finding_key(finding, target)
        actual[key] = actual.get(key, 0) + 1

    expected = expected_warnings(target)
    if actual != expected:
        new = {k: v for k, v in actual.items() if expected.get(k) != v}
        gone = {k: v for k, v in expected.items() if actual.get(k) != v}
        case.fail(
            f"{target.name}: emitted warnings do not match "
            f"{_manifest_path(target).name}.\n"
            f"  unpinned / changed count (new drift — fix the fixture, or pin it "
            f"with a reason): {new or '{}'}\n"
            f"  pinned but not emitted (stale — delete the manifest entry): "
            f"{gone or '{}'}"
        )


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
        """The golden's directory must be gate-clean and emit only pinned warnings.

        Delegates to the module-level `assert_lint_matches_manifest` so
        `test_fullpath.py` — which does not inherit this mix-in — enforces the
        identical contract.
        """
        assert_lint_matches_manifest(self, golden.parent)

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
