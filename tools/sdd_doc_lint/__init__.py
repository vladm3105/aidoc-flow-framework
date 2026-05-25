"""sdd_doc_lint — deterministic structural check for SDD instance documents.

The platform-tier implementation of the framework's `on_author` / `pre_merge`
trigger-point check (see `framework/governance/REVIEW_REMEDIATION_FLOW.md`). It
runs the *structural* subset of a review — ID/tag forms, required upstream tags,
`@threshold:` format, EARS grammar, placeholder leakage — driven by
`framework/registry/LAYER_REGISTRY.yaml`. The semantic readiness score stays the
LLM `-audit` skill; this is the fast, repeatable gate beneath it.

Text-based on purpose: the checks work on an instance document whether it is
authored as Markdown or YAML.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

import yaml

_REGISTRY_REL = Path("framework") / "registry" / "LAYER_REGISTRY.yaml"


def find_registry(start: Path | None = None) -> Path:
    """Locate ``framework/registry/LAYER_REGISTRY.yaml`` without assuming the
    package's location, so a vendored copy works from any platform.

    Order: ``$SDD_REGISTRY`` → search upward from the CWD → search upward from
    this module → the canonical repo layout (``parents[2]``).
    """
    env = os.environ.get("SDD_REGISTRY")
    if env:
        return Path(env)
    seeds = [start or Path.cwd(), Path(__file__).resolve().parent]
    for seed in seeds:
        for base in [seed, *seed.resolve().parents]:
            candidate = base / _REGISTRY_REL
            if candidate.is_file():
                return candidate
    return Path(__file__).resolve().parents[2] / _REGISTRY_REL


LAYER_TAGS = ("brd", "prd", "ears", "bdd", "adr", "spec", "tdd", "iplan")

_TAG = re.compile(r"@(" + "|".join(LAYER_TAGS) + r")\s*:\s*([^\s|]+)")
_THRESHOLD = re.compile(r"@threshold:\s*([^\s|]+)")
_THEN_CONNECTIVE = re.compile(r"THEN\s*\[")
_PLACEHOLDERS = [
    re.compile(r"\bTBD\b"),
    re.compile(r"\bTODO\b"),
    re.compile(r"\bFIXME\b"),
    re.compile(r"\b[A-Z]{2,8}-XXX\b"),
    re.compile(r"\bXX+\b"),
]
# Candidate IDs whose prefix is a known artifact (avoids flagging unrelated tokens).
_KNOWN = "BRD|PRD|EARS|BDD|ADR|SPEC|TDD|IPLAN"
_DOC_ID = re.compile(rf"\b({_KNOWN})-([A-Za-z0-9]+)\b")
_ELEM_ID = re.compile(rf"\b({_KNOWN})((?:\.[A-Za-z0-9]+)+)\b")


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    code: str
    message: str
    severity: str = "error"

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: [{self.severity.upper()} {self.code}] {self.message}"


def _load_registry(registry: Path | None = None):
    registry = registry or find_registry()
    data = yaml.safe_load(registry.read_text(encoding="utf-8"))
    layers = {layer["artifact"]: layer for layer in data["layers"]}
    pats = data["id_patterns"]
    return layers, re.compile(pats["document"]), re.compile(pats["element"])


def detect_layer(path: Path, layers: dict) -> str | None:
    """Return the artifact code for an SDD instance doc, or None if not one."""
    parts = [p.upper() for p in path.parts]
    # docs/0N_<ARTIFACT>/...
    for part in parts:
        m = re.fullmatch(r"\d{2}_([A-Z]+)", part)
        if m and m.group(1) in layers:
            return m.group(1)
    # filename prefix <ARTIFACT>-NN_...
    m = re.match(rf"({_KNOWN})-", path.name.upper())
    if m and m.group(1) in layers:
        return m.group(1)
    return None


def lint_text(text: str, artifact: str, rel: str, layers, doc_re, elem_re) -> list[Finding]:
    findings: list[Finding] = []
    lines = text.splitlines()
    seen_tags: set[str] = set()

    for i, line in enumerate(lines, 1):
        # Trace tags: collect which upstream layers are referenced + validate the id form.
        for m in _TAG.finditer(line):
            seen_tags.add(m.group(1))
            val = m.group(2)
            if not (doc_re.match(val) or elem_re.match(val)):
                findings.append(
                    Finding(rel, i, "ID01", f"malformed trace-tag id '@{m.group(1)}: {val}'")
                )
        # Threshold tags: TYPE.NUM.key dotted form. Record their spans so the
        # element-id scan below does not mistake a threshold key for an element id.
        threshold_spans = []
        for m in _THRESHOLD.finditer(line):
            threshold_spans.append(m.span(1))
            val = m.group(1)
            if not re.match(r"^[A-Z]+\.[A-Za-z0-9]+(?:\.[A-Za-z0-9]+)+$", val):
                findings.append(
                    Finding(rel, i, "TH01", f"malformed @threshold: '{val}' (want TYPE.NN.key)")
                )

        def _in_threshold(span):
            return any(s[0] <= span[0] and span[1] <= s[1] for s in threshold_spans)

        # Inline document IDs (TYPE-NN) of known artifacts must match the doc form.
        for m in _DOC_ID.finditer(line):
            tok = m.group(0)
            if not doc_re.match(tok):
                findings.append(Finding(rel, i, "ID02", f"malformed document id '{tok}'"))
        # Inline element IDs (TYPE.a.b.c…) of known artifacts must match the element form.
        for m in _ELEM_ID.finditer(line):
            tok = m.group(0)
            if _in_threshold(m.span()):
                continue  # a threshold key, not an element id
            if tok.count(".") >= 3 and not elem_re.match(tok):
                findings.append(Finding(rel, i, "ID03", f"malformed element id '{tok}'"))
        # Placeholder leakage.
        for pat in _PLACEHOLDERS:
            if pat.search(line):
                findings.append(
                    Finding(
                        rel, i, "PH01", f"placeholder/unfilled token: '{pat.search(line).group(0)}'"
                    )
                )
        # EARS grammar: no THEN-connective.
        if artifact == "EARS" and _THEN_CONNECTIVE.search(line):
            findings.append(
                Finding(
                    rel,
                    i,
                    "EARS01",
                    "EARS uses 'THE … SHALL …', not a 'THEN [response]' connective",
                )
            )

    # Required upstream tags present (document-level, reported at line 0).
    required = layers[artifact].get("required_tags", []) or []
    for tag in required:
        if tag not in seen_tags:
            findings.append(
                Finding(
                    rel,
                    0,
                    "TAG01",
                    f"{artifact} requires upstream tag '@{tag}:' (cumulative traceability)",
                )
            )
    return findings


def lint_file(path: Path, layers, doc_re, elem_re) -> list[Finding]:
    artifact = detect_layer(path, layers)
    if artifact is None:
        return []
    try:
        rel = path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        rel = path.as_posix()
    return lint_text(path.read_text(encoding="utf-8"), artifact, rel, layers, doc_re, elem_re)


def lint_path(target: Path, registry: Path | None = None) -> list[Finding]:
    """Lint a file or recurse a directory; returns all findings."""
    layers, doc_re, elem_re = _load_registry(registry)
    findings: list[Finding] = []
    if target.is_dir():
        for p in sorted(target.rglob("*")):
            if p.is_file() and p.suffix.lower() in (".md", ".yaml", ".yml"):
                findings.extend(lint_file(p, layers, doc_re, elem_re))
    elif target.is_file():
        findings.extend(lint_file(target, layers, doc_re, elem_re))
    return findings
