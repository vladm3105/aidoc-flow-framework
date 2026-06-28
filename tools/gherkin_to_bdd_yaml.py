#!/usr/bin/env python3
"""gherkin_to_bdd_yaml — one-time migration transcoder (YAML-BDD-SCHEMA D-6).

Parse a BDD doc's embedded Gherkin (``​```gherkin`` fences) into the structured
YAML scenario model (plan §Schema) and rewrite §2 Feature Definition + §3
Scenario Structure to carry ``​```yaml`` blocks instead.

**ID stability is the contract (Pass-2 LB-2):** each scenario's existing
``@scenario-id:`` value is copied **verbatim** into the YAML ``id:`` field — the
content hash is never recomputed — so every downstream ``@bdd:`` citation keeps
resolving. ``name``/steps are carried for fidelity but are not what stabilises
the ID.

Lossy only on cosmetics: ``#`` comments are lifted into ``spec_trace:`` (for
``# spec_trace:`` lines) / ``notes:`` (everything else); exact whitespace is not
preserved. Pure stdlib + PyYAML (already a linter dependency).

This is the parser/emitter engine + a CLI. The engine
(``parse_gherkin_feature`` / ``render_scenarios_yaml``) is what the unit tests
exercise; the CLI ``transcode_markdown`` does the §2/§3 in-place rewrite for the
corpus migration (PR-3).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

# --- Gherkin token patterns ---------------------------------------------------
_SCENARIO_ID = re.compile(r"@scenario-id:\s*(BDD\.\d+\.\d+\.[a-z0-9]+)")
_SCENARIO_TYPE = re.compile(r"@scenario-type:\s*([a-z]+)")
_PRIORITY = re.compile(r"@(p\d-[a-z]+)")
_EARS = re.compile(r"@ears:\s*(EARS\.\d+\.\d+\.[a-z0-9]+)")
_STEP = re.compile(r"^\s*(Given|When|Then|And|But)\s+(.*\S)\s*$")
_SCENARIO = re.compile(r"^\s*(Scenario Outline|Scenario):\s*(.*\S)\s*$")
_SPEC_TRACE_C = re.compile(r"^\s*#\s*spec_trace:\s*(.*\S)\s*$")
_COMMENT = re.compile(r"^\s*#\s*(.*\S)\s*$")
_EXAMPLES = re.compile(r"^\s*Examples:\s*$")
_TABLE_ROW = re.compile(r"^\s*\|(.+)\|\s*$")
_PHASE = {"Given": "given", "When": "when", "Then": "then"}


def _table_cells(line: str) -> list[str]:
    return [c.strip() for c in _TABLE_ROW.match(line).group(1).split("|")]


def parse_gherkin_feature(gherkin: str) -> dict:
    """Parse one Gherkin feature block into the YAML scenario model.

    Returns ``{"feature": {...}, "scenarios": [...]}``. Scenario IDs are taken
    verbatim from ``@scenario-id:`` (never recomputed).
    """
    feature: dict = {}
    scenarios: list[dict] = []
    pending_tags: list[str] = []  # raw tag-line text awaiting the next Scenario
    desc_lines: list[str] = []
    cur: dict | None = None
    phase: str | None = None
    in_examples = False
    ex_headers: list[str] | None = None
    section = "preamble"  # preamble | feature | background | scenario

    def flush_scenario() -> None:
        nonlocal cur
        if cur is not None:
            scenarios.append(cur)
            cur = None

    for raw in gherkin.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue

        if line.lstrip().startswith("Feature:"):
            feature["name"] = line.split("Feature:", 1)[1].strip()
            # feature-level tags (no element @ears per D-3): keep runner tags only
            runner = [t for t in pending_tags if not t.startswith(("@ears", "@bdd"))]
            if runner:
                feature["tags"] = runner
            pending_tags = []
            section = "feature"
            continue

        if line.lstrip().startswith("Background:"):
            flush_scenario()
            feature.setdefault("background", {"steps": []})
            section = "background"
            phase = None
            continue

        m_scn = _SCENARIO.match(line)
        if m_scn:
            flush_scenario()
            cur = {
                "id": _first(_SCENARIO_ID, pending_tags),
                "name": m_scn.group(2),
                "type": _first(_SCENARIO_TYPE, pending_tags) or "success",
                "priority": _first(_PRIORITY, pending_tags) or "p2-medium",
                "ears": _all(_EARS, pending_tags),
            }
            if m_scn.group(1) == "Scenario Outline":
                cur["outline"] = True
            pending_tags = []
            section = "scenario"
            phase = None
            in_examples = False
            ex_headers = None
            continue

        if _TAGLINE_OK(line) and section in ("preamble", "feature", "scenario", "background"):
            # A tag line precedes a Feature/Scenario. Buffer raw tag tokens.
            if line.lstrip().startswith("@"):
                pending_tags.extend(line.split())  # one entry per @-token
                continue

        # Example tables (scenario outline).
        if cur is not None and _EXAMPLES.match(line):
            in_examples = True
            cur["examples"] = {"headers": [], "rows": []}
            continue
        if cur is not None and in_examples and _TABLE_ROW.match(line):
            cells = _table_cells(line)
            if ex_headers is None:
                ex_headers = cells
                cur["examples"]["headers"] = cells
            else:
                cur["examples"]["rows"].append(cells)
            continue

        # Comments → spec_trace / notes (scenario scope).
        if cur is not None and _SPEC_TRACE_C.match(line):
            cur.setdefault("spec_trace", []).append(_SPEC_TRACE_C.match(line).group(1))
            continue
        if cur is not None and _COMMENT.match(line):
            cur.setdefault("notes", []).append(_COMMENT.match(line).group(1))
            continue

        # Steps.
        m_step = _STEP.match(line)
        if m_step:
            kw, text = m_step.group(1), m_step.group(2)
            if kw in _PHASE:
                phase = _PHASE[kw]
            if section == "background":
                feature["background"]["steps"].append(text)
            elif cur is not None and phase:
                cur.setdefault(phase, []).append(text)
            continue

        # Feature narrative (As a / I want / So that).
        if section == "feature":
            desc_lines.append(line.strip())

    flush_scenario()
    if desc_lines:
        feature["description"] = "\n".join(desc_lines)
    return {"feature": feature, "scenarios": scenarios}


def _TAGLINE_OK(line: str) -> bool:
    return line.lstrip().startswith("@")


def _first(pat: re.Pattern, tags: list[str]) -> str | None:
    for t in tags:
        m = pat.search(t)
        if m:
            return m.group(1)
    return None


def _all(pat: re.Pattern, tags: list[str]) -> list[str]:
    out: list[str] = []
    for t in tags:
        out.extend(m.group(1) for m in pat.finditer(t))
    return out


def render_scenarios_yaml(scenarios: list[dict]) -> str:
    """Deterministic YAML for the ``scenarios:`` block (field order preserved)."""
    return yaml.safe_dump({"scenarios": scenarios}, sort_keys=False, allow_unicode=True, width=100)


def render_feature_yaml(feature: dict) -> str:
    return yaml.safe_dump({"feature": feature}, sort_keys=False, allow_unicode=True, width=100)


def transcode_markdown(md_text: str) -> str:
    """Rewrite a BDD doc's ``​```gherkin`` block(s) into ``​```yaml`` feature +
    scenarios blocks. Non-Gherkin content is preserved verbatim."""
    fence = re.compile(r"```gherkin\n(.*?)\n```", re.DOTALL)
    blocks = fence.findall(md_text)
    if not blocks:
        return md_text
    parsed = parse_gherkin_feature("\n\n".join(blocks))
    feature_yaml = "```yaml\n" + render_feature_yaml(parsed["feature"]) + "```"
    scenarios_yaml = "```yaml\n" + render_scenarios_yaml(parsed["scenarios"]) + "```"

    first = True

    def _replace(_m: re.Match) -> str:
        nonlocal first
        if first:
            first = False
            return feature_yaml + "\n\n" + scenarios_yaml
        return ""  # subsequent gherkin blocks folded into the first

    return fence.sub(_replace, md_text)


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print("usage: gherkin_to_bdd_yaml.py <BDD-NN.md> [--in-place]", file=sys.stderr)
        return 2
    path = Path(args[0])
    out = transcode_markdown(path.read_text(encoding="utf-8"))
    if "--in-place" in args:
        path.write_text(out, encoding="utf-8")
    else:
        sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
