"""sdd_doc_lint — deterministic structural check for SDD instance documents.

CANONICAL SOURCE: tools/sdd_doc_lint/__init__.py (edit here).
Vendored byte-identical mirrors at platforms/claude-code-plugin/sdd_doc_lint/
and platforms/hermes/sdd_doc_lint/ are produced by
tools/sdd_doc_lint/sync-vendored.sh — DO NOT EDIT the vendored copies; any
direct edit there is overwritten on the next sync run. (CLEANUP-PR-A item 3.)

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

# Shared @-tag trace primitives (CFB-PR-2 DD-1). The forward coverage engine
# reuses the SAME token→doc reduction, layer order, and `@`-tag regex as the
# backward walker so the two directions of the trace graph agree byte-for-byte.
# Package-relative import → resolves in the canonical tree and in every vendored
# copy (the submodule is carried by sync-vendored.sh).
from .trace_graph import LAYER_INDEX as _LAYER_INDEX
from .trace_graph import TAG as _TRACE_TAG
from .trace_graph import doc_id_from_token

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

# AS3 — authoring-style check (governance/AUTHORING_STYLE.md).
# Banned-phrase regexes. Tuned for low false-positive rate: only patterns whose
# fix is mechanical and unambiguous. Less-clear-cut superlatives (robust,
# powerful, comprehensive, optimal, best) are left to LLM Tier-2 review.
_STYLE_BANNED = [
    (re.compile(r"\bin order to\b", re.IGNORECASE), "filler — use 'to'"),
    (re.compile(r"\bthe fact that\b", re.IGNORECASE), "filler — drop"),
    (re.compile(r"\bit should be noted that\b", re.IGNORECASE), "filler — drop"),
    (re.compile(r"\bplease note\b", re.IGNORECASE), "filler — drop"),
    (re.compile(r"\bas a matter of fact\b", re.IGNORECASE), "filler — drop"),
    (re.compile(r"\bsimply\b", re.IGNORECASE), "ease-of-use claim"),
    (re.compile(r"\beasily\b", re.IGNORECASE), "ease-of-use claim"),
    (re.compile(r"\bstraightforwardly\b", re.IGNORECASE), "ease-of-use claim"),
    (re.compile(r"\bamazing\b", re.IGNORECASE), "superlative"),
    (re.compile(r"\bseamless(?:ly)?\b", re.IGNORECASE), "superlative"),
    (re.compile(r"\bcutting[- ]edge\b", re.IGNORECASE), "superlative"),
    (re.compile(r"\bstate[- ]of[- ]the[- ]art\b", re.IGNORECASE), "superlative"),
    (re.compile(r"\bwill be able to\b", re.IGNORECASE), "future-oriented promise"),
    (re.compile(r"\byou'?ll be able to\b", re.IGNORECASE), "future-oriented promise"),
]

# AS3 — per-section / per-document size targets. Defaults from
# AUTHORING_STYLE.md; "blocking" threshold = +50% over default. AS2: each
# template section can declare a `_size_target: <words>` key to override.
_SECTION_TARGET_WORDS = 200
_SECTION_BLOCKING_WORDS = 300  # 200 × 1.5
_BLOCKING_FACTOR = 1.5
_DOC_TARGET_WORDS = {
    "BRD": 3000,
    "PRD": 3000,
    "EARS": 1500,
    "BDD": 1500,
    "ADR": 1500,
    "SPEC": 1500,
    "TDD": 1500,
    "IPLAN": 1500,
}
# Sections that legitimately carry mostly tabular metadata; exempt from the
# section-size warning.
_SIZE_EXEMPT_HEADINGS = {"document control", "traceability", "glossary", "revision history"}

_FRONTMATTER_FENCE = re.compile(r"^---\s*$")
_SECTION_HEADING = re.compile(r"^## +(.+?)\s*$")
_HEADING_NUMBER_PREFIX = re.compile(r"^\d+(?:\.\d+)*\.?\s*")
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
    section: str | None = None

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: [{self.severity.upper()} {self.code}] {self.message}"


def _load_registry(registry: Path | None = None):
    registry = registry or find_registry()
    data = yaml.safe_load(registry.read_text(encoding="utf-8"))
    layers = {layer["artifact"]: layer for layer in data["layers"]}
    pats = data["id_patterns"]
    return layers, re.compile(pats["document"]), re.compile(pats["element"])


# CLEANUP-PR-C item 12: threshold pattern matches
# `TYPE.NN.<lowercase_category>(.<lowercase_subkey>)+` — at minimum 4 dotted
# segments, optionally more for nested subkeys (e.g.
# `PRD.01.auth.attempts.max` is 5 segments). Lowercase category
# distinguishes thresholds from 4-segment hex-hash element IDs (which use
# digits in the section_id position). Mirrors `id_patterns.threshold` in
# `framework/registry/LAYER_REGISTRY.yaml`; kept in sync there via the
# spec contract. Stricter than the pre-0.18.0 inline pattern (which
# permitted mixed-case categories) but accepts N-segment subkeys.
_THRESHOLD_FORM = re.compile(r"^[A-Z]+\.\d{2,}\.[a-z_]+(?:\.[a-z0-9_]+)+$")


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


def _split_frontmatter(lines: list[str]) -> tuple[list[str], list[str]]:
    """Return (frontmatter_lines, body_lines). Frontmatter is the YAML fenced
    by ``---`` at the top; body is everything after the closing fence (or the
    whole file if no frontmatter is present)."""
    if not lines or not _FRONTMATTER_FENCE.match(lines[0]):
        return [], lines
    for i in range(1, len(lines)):
        if _FRONTMATTER_FENCE.match(lines[i]):
            return lines[1:i], lines[i + 1 :]
    return [], lines


def _section_word_counts(body: list[str]) -> list[tuple[str, int, int]]:
    """Return [(heading, start_line_in_body, word_count), ...] for each
    ``## …`` section in the body. Word count excludes the heading line and any
    code-fenced blocks (``` … ```).
    """
    sections: list[tuple[str, int, int]] = []
    current_head: str | None = None
    current_start = 0
    current_words = 0
    in_fence = False
    for i, raw in enumerate(body):
        if raw.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        head = _SECTION_HEADING.match(raw)
        if head:
            if current_head is not None:
                sections.append((current_head, current_start, current_words))
            current_head = head.group(1)
            current_start = i + 1
            current_words = 0
            continue
        if current_head is not None:
            current_words += len(raw.split())
    if current_head is not None:
        sections.append((current_head, current_start, current_words))
    return sections


def _parse_doc_control(body: list[str]) -> tuple[int | None, dict[str, str], dict[str, str] | None]:
    """Locate the Document Control section in a markdown body and return
    ``(section_line, dc_table, latest_revision)`` where ``dc_table`` maps the
    Document Control key-value table's first column (lowercase) to its second
    column, and ``latest_revision`` is the first data row of the
    revision-history table (header Version|Date|Author|Change). Either may be
    empty if not found.
    """
    dc_idx = None
    for i, line in enumerate(body):
        if line.strip().lower().rstrip(":") == "## document control":
            dc_idx = i
            break
    if dc_idx is None:
        return None, {}, None
    dc_table: dict[str, str] = {}
    rev_latest: dict[str, str] | None = None
    j = dc_idx + 1
    while j < len(body):
        line = body[j].rstrip()
        if line.startswith("## ") and "Document Control" not in line:
            break
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 4 and cells[0].lower() == "version" and cells[1].lower() == "date":
                # revision-history header → next non-separator data row
                k = j + 1
                while k < len(body):
                    row = body[k].rstrip()
                    if not row.startswith("|"):
                        break
                    row_cells = [c.strip() for c in row.strip("|").split("|")]
                    sep_chars = set("".join(row_cells))
                    if sep_chars and sep_chars <= set("-: "):
                        k += 1
                        continue
                    if len(row_cells) >= 2:
                        rev_latest = {"version": row_cells[0], "date": row_cells[1]}
                        break
                    k += 1
                j = k + 1
                continue
            if len(cells) >= 2:
                key = cells[0].lower()
                val = cells[1]
                if key and key != "field" and set(key) - set("-: "):
                    dc_table[key] = val
        j += 1
    return dc_idx, dc_table, rev_latest


def _check_frontmatter_consistency(text: str, rel: str) -> list[Finding]:
    """AS8 — frontmatter ↔ Document Control ↔ revision-history consistency.
    Compares ``status``, ``version``, ``last_updated`` across the three
    parallel statements of artifact identity. Single finding code FM01.
    """
    findings: list[Finding] = []
    lines = text.splitlines()
    fm_lines, body = _split_frontmatter(lines)
    if not fm_lines:
        return findings
    try:
        fm = yaml.safe_load("\n".join(fm_lines)) or {}
    except yaml.YAMLError:
        return findings
    if not isinstance(fm, dict):
        return findings
    dc_idx, dc_table, rev = _parse_doc_control(body)
    if dc_idx is None:
        return findings
    body_offset = len(fm_lines) + 2  # both --- fences
    anchor = body_offset + dc_idx + 1

    def _emit(message: str) -> None:
        findings.append(Finding(rel, anchor, "FM01", message, severity="error"))

    def _norm(v: object) -> str:
        return str(v).strip().strip('"').strip("'") if v is not None else ""

    fm_status = _norm(fm.get("status"))
    dc_status = dc_table.get("status", "").strip()
    if fm_status and dc_status and fm_status != dc_status:
        _emit(f"frontmatter status='{fm_status}' ≠ Document Control Status='{dc_status}'")

    fm_version = _norm(fm.get("version"))
    dc_version = dc_table.get("version", "").strip()
    if fm_version and dc_version and fm_version != dc_version:
        _emit(f"frontmatter version='{fm_version}' ≠ Document Control Version='{dc_version}'")

    if rev:
        if fm_version and rev["version"] and fm_version != rev["version"]:
            _emit(
                f"frontmatter version='{fm_version}' ≠ latest revision-history "
                f"version='{rev['version']}'"
            )
        fm_last_updated = _norm(fm.get("last_updated"))
        if fm_last_updated and rev["date"] and fm_last_updated != rev["date"]:
            _emit(
                f"frontmatter last_updated='{fm_last_updated}' ≠ latest revision-history "
                f"date='{rev['date']}'"
            )

    return findings


def _normalise_heading(heading: str) -> str:
    """Convert a markdown heading to a candidate template-key form.

    Examples:
      '3. Introduction'             -> 'introduction'
      'Document Control'            -> 'document_control'
      '7.2 Architecture Decisions'  -> 'architecture_decisions'
      'Constraints & Assumptions'   -> 'constraints_and_assumptions'
    """
    h = _HEADING_NUMBER_PREFIX.sub("", heading.strip()).lower()
    h = h.replace("&", "and")
    return re.sub(r"[^a-z0-9]+", "_", h).strip("_")


def _load_section_targets(artifact: str, registry: Path | None = None) -> dict[str, int]:
    """Return ``{section_key: _size_target}`` from the layer's TEMPLATE.yaml.
    Returns ``{}`` when the template cannot be loaded — callers fall back to
    the flat default.
    """
    try:
        registry = registry or find_registry()
        layer_folder = next(
            entry["folder"]
            for entry in yaml.safe_load(registry.read_text(encoding="utf-8"))["layers"]
            if entry["artifact"] == artifact
        )
    except (OSError, StopIteration, KeyError, yaml.YAMLError):
        return {}
    tpl = registry.parent.parent / layer_folder / f"{artifact}-TEMPLATE.yaml"
    try:
        doc = yaml.safe_load(tpl.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return {}
    if not isinstance(doc, dict):
        return {}
    out: dict[str, int] = {}
    for key, body in doc.items():
        if isinstance(body, dict) and isinstance(body.get("_size_target"), int):
            # CLEANUP-PR-D item 15: respect `_required: false` markers
            # (e.g. PRD's component_decomposition is OPTIONAL — present
            # only when downstream cites @threshold). Sections marked
            # `_required: false` are excluded from STRUCT01 enforcement
            # but still get STY02 size-budget enforcement.
            if body.get("_required") is False:
                continue
            # CLEANUP-PR-F: sections marked `_required_when_subtype: [...]`
            # are conditionally required based on the artifact's
            # `document_control.subtype` value (per CLEANUP-PR-E item 17).
            # The corpus-level lint cannot determine the artifact's
            # subtype without parsing every instance doc; defer the
            # subtype-aware required-section check to the layer's
            # `doc-<layer>-audit` SKILL (which does parse the artifact).
            if isinstance(body.get("_required_when_subtype"), list):
                continue
            out[key] = body["_size_target"]
    return out


def _check_style(
    text: str, artifact: str, rel: str, body_offset: int, *, registry: Path | None = None
) -> list[Finding]:
    """AS3 — authoring-style check. Banned phrases (per-line warning),
    oversized section body (warning), oversized whole-document body (error
    only when over by ≥50% — the AUTHORING_STYLE.md blocking threshold)."""
    findings: list[Finding] = []
    lines = text.splitlines()
    _, body = _split_frontmatter(lines)
    # STY01 — banned phrases (per-line). Scan body only so frontmatter YAML
    # keys (e.g. `simply: true`) don't trip.
    for offset, raw in enumerate(body):
        # Skip headings and table separator lines.
        if raw.lstrip().startswith("#") or set(raw.strip()) <= set("|-: "):
            continue
        for pat, label in _STYLE_BANNED:
            m = pat.search(raw)
            if m:
                findings.append(
                    Finding(
                        rel,
                        body_offset + offset + 1,
                        "STY01",
                        f"authoring-style: {label} ('{m.group(0)}')",
                        severity="warning",
                    )
                )
    # STY02 — section body over the +50% blocking threshold. Per-section
    # target comes from the template's `_size_target` (AS2); falls back to
    # the flat 200-word default when no template entry matches.
    section_targets = _load_section_targets(artifact, registry)
    for heading, start, words in _section_word_counts(body):
        if heading.strip().lower() in _SIZE_EXEMPT_HEADINGS:
            continue
        key = _normalise_heading(heading)
        target = section_targets.get(key, _SECTION_TARGET_WORDS)
        blocking = int(target * _BLOCKING_FACTOR)
        if words > blocking:
            findings.append(
                Finding(
                    rel,
                    body_offset + start,
                    "STY02",
                    f"section '{heading}' is {words} words; target ≤{target}"
                    f" (blocking >{blocking})",
                    severity="warning",
                )
            )
    # STY03 — document body over the +50% target (blocking). Word count
    # excludes code-fenced blocks (``` … ```), mirroring STY02 / AS3. BDD
    # bodies are mostly fenced Gherkin and the doc-bdd skill allows ~50k
    # tokens of it before a split; counting fences here would block any real
    # BDD suite far below that allowance.
    target = _DOC_TARGET_WORDS.get(artifact)
    if target is not None:
        words = 0
        in_fence = False
        for line in body:
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            words += len(line.split())
        if words > target * 3 // 2:
            findings.append(
                Finding(
                    rel,
                    body_offset,
                    "STY03",
                    f"document body is {words} words; {artifact} target ≤{target}"
                    f" (blocking >{target * 3 // 2})",
                    severity="error",
                )
            )
    return findings


def lint_text(
    text: str,
    artifact: str,
    rel: str,
    layers,
    doc_re,
    elem_re,
    *,
    registry: Path | None = None,
) -> list[Finding]:
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
        # Threshold tags: TYPE.NN.<category>.<key> dotted form. Record their
        # spans so the element-id scan below does not mistake a threshold key
        # for an element id. CLEANUP-PR-C item 12 — uses the strict pattern
        # matching `id_patterns.threshold` in LAYER_REGISTRY.yaml.
        threshold_spans = []
        for m in _THRESHOLD.finditer(line):
            threshold_spans.append(m.span(1))
            val = m.group(1)
            if not _THRESHOLD_FORM.match(val):
                findings.append(
                    Finding(
                        rel,
                        i,
                        "TH01",
                        f"malformed @threshold: '{val}' "
                        "(want TYPE.NN.<category>.<key> with lowercase category)",
                    )
                )
        # CLEANUP-PR-D item 15: `full_id:` lines declare threshold keys
        # in PRD `component_decomposition` sections. Exempt the declared
        # value from the element-id scan (the key is a threshold, not an
        # element id).
        for m in re.finditer(
            r"full_id:\s*[\"\']?(PRD\.\d+\.[a-z_]+(?:\.[a-z0-9_]+)+)[\"\']?", line
        ):
            threshold_spans.append(m.span(1))

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
    # AS3 — authoring-style check (banned phrases + size targets).
    findings.extend(_check_style(text, artifact, rel, body_offset=0, registry=registry))
    # AS8 — frontmatter ↔ Document Control ↔ revision-history consistency.
    findings.extend(_check_frontmatter_consistency(text, rel))
    # AS10 — @diagram tag level cascade vs DIAGRAM_STANDARDS.md.
    findings.extend(_check_diagram_level(text, artifact, rel))
    # STRUCT01 — required template sections present.
    findings.extend(_check_required_template_sections(rel, text, artifact, registry))
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


_THRESHOLD_PARSED = re.compile(r"@threshold:\s*([A-Z]+)\.([0-9]+)\.([A-Za-z0-9_.]+)")
_THRESHOLD_VALUE = re.compile(r"(\d+(?:\.\d+)?)\s*(ms|s|min|h|%|MB|GB|KB|req/s|rpm)\b")

# AS10 — @diagram level cascade per framework/governance/DIAGRAM_STANDARDS.md.
# Per-layer allowed diagram-tag types: each artifact may only carry the level
# associated with its own layer (BRD=L1, PRD=L2, SPEC=L3); ADR has no C4/DFD
# level (decision bridge). 'sequence-*' tags are allowed on every layer.
_DIAGRAM_TAG = re.compile(r"@diagram:\s*([a-z][a-z0-9]*(?:-[a-z0-9]+)+)")
_DIAGRAM_ALLOWED = {
    "BRD": {"c4-l1", "dfd-l1"},
    "PRD": {"c4-l2", "dfd-l2"},
    "EARS": set(),
    "BDD": set(),
    "ADR": set(),
    "SPEC": {"c4-l3", "dfd-l3"},
    "TDD": set(),
    "IPLAN": set(),
}
_DIAGRAM_SEQUENCE = re.compile(r"^sequence-(sync|async|error|[a-z0-9-]+)$")


def _check_diagram_level(text: str, artifact: str, rel: str) -> list[Finding]:
    """AS10 — verify each ``@diagram: <type>`` tag uses a type permitted on
    this artifact's layer (per ``framework/governance/DIAGRAM_STANDARDS.md``).
    ``sequence-*`` tags are universally allowed; C4/DFD tags must match the
    layer's level (BRD→L1, PRD→L2, SPEC→L3); ADR has no C4/DFD level.
    """
    findings: list[Finding] = []
    allowed = _DIAGRAM_ALLOWED.get(artifact, set())
    for i, line in enumerate(text.splitlines(), 1):
        for m in _DIAGRAM_TAG.finditer(line):
            tag = m.group(1)
            if _DIAGRAM_SEQUENCE.match(tag):
                continue
            if tag in allowed:
                continue
            # If the artifact has no allowed C4/DFD level but a c4/dfd tag is
            # present, that is also a mismatch.
            findings.append(
                Finding(
                    rel,
                    i,
                    "DG02",
                    f"@diagram '{tag}' is not valid for layer {artifact}"
                    + (
                        f" (expected {sorted(allowed)})"
                        if allowed
                        else " (no C4/DFD level on this layer)"
                    ),
                    severity="error",
                )
            )
    return findings


_ELEM_DEF_BULLET = re.compile(
    r"^\s*-\s+\*\*([A-Z]+\.[0-9]+\.[A-Za-z0-9]+\.[a-z0-9]+)\*\*", re.MULTILINE
)
_ELEM_DEF_HEADING = re.compile(
    r"^#{2,4}\s+([A-Z]+\.[0-9]+\.[A-Za-z0-9]+\.[a-z0-9]+)\b", re.MULTILINE
)
_ELEM_DEF_YAML = re.compile(
    r"^\s*[-]?\s*id:\s*[\"']?([A-Z]+\.[0-9]+\.[A-Za-z0-9]+\.[a-z0-9]+)[\"']?", re.MULTILINE
)


# --- Heading-context FR scanner (CFB-PR-2 DD-3) ---------------------------------
# The forward-coverage engine gates only *functional requirements*. R-a/R-b make
# "scope by YAML path" impossible (the body is flat regex; authored artifacts are
# markdown prose) and the bare `.07.` ordinal ambiguous (§7 mixes FR definitions
# and an acceptance-criteria sub-block under the same ordinal). So an FR is
# identified structurally: a definition bullet under a `## … Functional
# Requirements` heading, before that section's `Acceptance criteria:` label line.

#: An FR definition bullet: ``- **<ID> — <Title>** …``. Captures the element id
#: only — the discriminators for "gated FR" are the heading context + the
#: acceptance-criteria boundary (DD-3), NOT the band, so a bullet that is
#: missing its band still classifies as an FR (DD-4's rule can then flag it).
#: The em-dash is accepted as em (—), en (–), or hyphen (-) for author leniency.
_FR_BULLET = re.compile(r"^\s*-\s+\*\*([A-Z]+\.[0-9]+\.[0-9]+\.[a-f0-9]+)\s+[—–-]\s+[^*]+\*\*")
#: The leading parenthetical band token on an FR bullet, e.g. the ``P1`` in
#: ``** (P1, anonymous public): …``. Matched on the bullet's first line only;
#: the first token suffices even when the parenthetical wraps to the next line
#: (corpus ``882c``: ``(P1, internal / privileged — Service-Owner\n  role)``).
_FR_BAND = re.compile(r"\*\*\s*\(\s*([^\s,)]+)")
#: The plain prose label that ends the FR definition sub-block and opens the
#: acceptance-criteria sub-block (a label line, NOT a `##` heading — R-b).
_ACCEPTANCE_LABEL = re.compile(r"^\s*Acceptance\s+criteria:\s*$", re.IGNORECASE)
#: The normalised heading key that opens the gated FR section.
_FR_SECTION_KEY = "functional_requirements"


@dataclass(frozen=True)
class FRElement:
    """A gated functional-requirement element (CFB-PR-2 DD-3).

    ``band`` is the raw leading parenthetical token on the FR bullet
    (e.g. ``"P1"``, ``"Future"``), or ``None`` when the bullet carries no
    parenthetical. DD-4's band rule validates it against ``priority_definitions``
    and treats ``Future`` as the deferral signal. ``line`` is 1-based and points
    at the FR bullet.
    """

    elem_id: str
    line: int
    band: str | None


def scan_fr_elements(text: str) -> list[FRElement]:
    """Return the gated functional-requirement elements declared in ``text``.

    An element id is a gated FR iff its line is (a) under a ``## … Functional
    Requirements`` heading, (b) before that section's ``Acceptance criteria:``
    label line, and (c) authored as an FR *definition bullet*
    ``- **<ID> — <Title>** …``. Prose citations of element ids inside the
    section and the §7 acceptance-criteria sub-block elements are NOT gated
    (the former lack the bullet form; the latter fall after the boundary).

    Reuses the level-2 ``_SECTION_HEADING`` mechanism so a new ``##`` heading
    ends the FR section. Pure structural scan — no YAML, no registry.
    """
    out: list[FRElement] = []
    in_fr_section = False
    past_acceptance = False
    for i, line in enumerate(text.splitlines(), 1):
        head = _SECTION_HEADING.match(line)
        if head:
            in_fr_section = _normalise_heading(head.group(1)) == _FR_SECTION_KEY
            past_acceptance = False
            continue
        if not in_fr_section:
            continue
        if _ACCEPTANCE_LABEL.match(line):
            past_acceptance = True
            continue
        if past_acceptance:
            continue
        m = _FR_BULLET.match(line)
        if m:
            band_m = _FR_BAND.search(line)
            out.append(
                FRElement(elem_id=m.group(1), line=i, band=band_m.group(1) if band_m else None)
            )
    return out


def _check_id_uniqueness(corpus: list[tuple[str, str]]) -> list[Finding]:
    """AS11 — element-ID hash integrity (definition uniqueness).

    Each element ID ``TYPE.NN.SS.xxxx`` carries a 4-hex-char SHA256-prefix of
    its ``{doc_id}:{section_id}:{title}:{description}`` content. A canonical
    invariant is that any given hash defines **one** element — so the same ID
    must not be *defined* in two different files (citations via
    ``@<lower>:`` tags are fine; only standalone definitions count).

    A definition matches one of three shapes:
      ``- **ID** — …``                        (markdown bullet)
      ``## ID …`` / ``### ID …`` etc.         (markdown heading)
      ``  - id: "ID"`` or ``id: ID``          (YAML key)
    """
    by_id: dict[str, list[tuple[str, int]]] = {}
    for rel, text in corpus:
        for pattern in (_ELEM_DEF_BULLET, _ELEM_DEF_HEADING, _ELEM_DEF_YAML):
            for m in pattern.finditer(text):
                eid = m.group(1)
                line = text[: m.start()].count("\n") + 1
                by_id.setdefault(eid, []).append((rel, line))
    findings: list[Finding] = []
    for eid, locs in by_id.items():
        if len(locs) > 1:
            paths = "; ".join(f"{p}:{ln}" for p, ln in locs)
            for rel, line in locs:
                findings.append(
                    Finding(
                        rel,
                        line,
                        "HASH01",
                        f"element id '{eid}' is defined in {len(locs)} places — each "
                        f"4-hex hash must identify exactly one element ({paths})",
                        severity="error",
                    )
                )
    return findings


_DOC_ID_FROM_ELEMENT = re.compile(r"^([A-Z]+)\.([0-9]+)\.")


def _framework_version(registry_path: Path) -> str | None:
    """Read ``framework/VERSION`` co-located with the registry. Returns None
    if the file isn't readable (so the staleness check no-ops gracefully)."""
    version_file = registry_path.parent.parent / "VERSION"
    try:
        return version_file.read_text(encoding="utf-8").strip()
    except OSError:
        return None


def _parse_minor(v: str) -> tuple[int, int]:
    parts = v.strip().split(".")
    try:
        return int(parts[0]), int(parts[1])
    except (ValueError, IndexError):
        return 0, 0


def _check_staleness(corpus: list[tuple[str, str]], framework_version: str | None) -> list[Finding]:
    """AS9 — staleness detection.

    Approved artifacts must carry a ``last_audited_spec`` frontmatter field
    naming the ``framework/VERSION`` they were audited against. When that
    field is missing OR has a smaller major.minor than the current
    ``framework/VERSION``, the artifact's approval is potentially stale —
    the spec has grown since the audit. Warning-only; recommends re-audit.
    """
    if not framework_version:
        return []
    current = _parse_minor(framework_version)
    findings: list[Finding] = []
    for rel, text in corpus:
        fm = _extract_frontmatter(text)
        if not fm:
            continue
        status = str(fm.get("status", "")).strip()
        if status != "Approved":
            continue
        raw_last = fm.get("last_audited_spec")
        if not raw_last:
            findings.append(
                Finding(
                    rel,
                    1,
                    "STALE01",
                    f"status=Approved but no last_audited_spec frontmatter field — "
                    f'add `last_audited_spec: "{framework_version}"` after re-audit',
                    severity="warning",
                )
            )
            continue
        last = str(raw_last).strip().strip('"').strip("'")
        if _parse_minor(last) < current:
            findings.append(
                Finding(
                    rel,
                    1,
                    "STALE01",
                    f"last_audited_spec={last} < current framework/VERSION={framework_version}"
                    f" — re-audit before relying on the Approved status",
                    severity="warning",
                )
            )
    return findings


def _extract_frontmatter(text: str) -> dict | None:
    lines = text.splitlines()
    fm_lines, _ = _split_frontmatter(lines)
    if not fm_lines:
        return None
    try:
        fm = yaml.safe_load("\n".join(fm_lines))
    except yaml.YAMLError:
        return None
    return fm if isinstance(fm, dict) else None


def _check_cascade(corpus: list[tuple[str, str]]) -> list[Finding]:
    """AS12 — ``deliverable_type`` / ``brd_type`` cascade.

    Each artifact downstream of a BRD inherits the BRD's ``deliverable_type``
    (code / document / ux / risk / process) unchanged. ``brd_type`` (platform /
    feature) cascades the same way. Audit skills require this in prose;
    sdd_doc_lint enforces it deterministically.

    Algorithm:
      1. Walk corpus; build ``brd_meta[doc_id]`` = ``{deliverable_type,
         brd_type}`` for every BRD found.
      2. For each non-BRD artifact, find its first ``@brd:`` reference in
         frontmatter or body; resolve the BRD-NN doc ID; look up brd_meta;
         compare ``deliverable_type``.
      3. Emit CSC01 on mismatch.
    """
    brd_meta: dict[str, dict[str, str]] = {}
    non_brd: list[tuple[str, str, dict, str | None]] = []

    for rel, text in corpus:
        fm = _extract_frontmatter(text)
        if not fm:
            continue
        doc_id = str(fm.get("doc_id") or "").strip().strip('"').strip("'")
        artifact_type = str(fm.get("artifact_type") or "").strip()
        if not doc_id:
            continue
        if artifact_type == "BRD":
            brd_meta[doc_id] = {
                "deliverable_type": str(fm.get("deliverable_type", "")).strip(),
                "brd_type": str(fm.get("brd_type", "")).strip(),
            }
            continue
        # Find @brd: BRD.NN.SS.xxxx reference (frontmatter tags or body).
        brd_ref: str | None = None
        for m in _TAG.finditer(text):
            if m.group(1) == "brd":
                em = _DOC_ID_FROM_ELEMENT.match(m.group(2))
                if em and em.group(1) == "BRD":
                    brd_ref = f"BRD-{em.group(2).zfill(2)}"
                    break
        non_brd.append((rel, doc_id, fm, brd_ref))

    findings: list[Finding] = []
    for rel, doc_id, fm, brd_ref in non_brd:
        if not brd_ref or brd_ref not in brd_meta:
            continue
        parent = brd_meta[brd_ref]
        child_dt = str(fm.get("deliverable_type", "")).strip()
        if parent["deliverable_type"] and child_dt and child_dt != parent["deliverable_type"]:
            findings.append(
                Finding(
                    rel,
                    1,
                    "CSC01",
                    f"{doc_id} deliverable_type='{child_dt}' ≠ parent {brd_ref} "
                    f"deliverable_type='{parent['deliverable_type']}'",
                    severity="error",
                )
            )
        # brd_type only meaningful on PRD (which inherits it from the
        # parent BRD); ADRs and below normally do not declare it.
        child_bt = str(fm.get("brd_type", "")).strip()
        if parent["brd_type"] and child_bt and child_bt != parent["brd_type"]:
            findings.append(
                Finding(
                    rel,
                    1,
                    "CSC01",
                    f"{doc_id} brd_type='{child_bt}' ≠ parent {brd_ref} "
                    f"brd_type='{parent['brd_type']}'",
                    severity="error",
                )
            )
    return findings


def _check_required_template_sections(
    rel: str,
    text: str,
    artifact: str | None,
    registry: Path | None,
) -> list[Finding]:
    """STRUCT01: every required <TYPE>-TEMPLATE.yaml section must appear as a ## heading.

    Frontmatter `artifact_type` overrides the path-inferred artifact when the
    document declares an `<X>-INDEX` variant (e.g. `BRD-INDEX` for
    `BRD-00_index.md`). Index docs have their own template
    (`<X>-NN_index.TEMPLATE.md`) and intentionally diverge from the standard
    `<X>-TEMPLATE.yaml` section set; applying the standard template's
    required-sections check to an index would produce spurious STRUCT01
    findings.
    """
    findings: list[Finding] = []
    if not artifact:
        return findings
    fm = _extract_frontmatter(text)
    if fm:
        declared = str(fm.get("artifact_type") or "").strip()
        if declared.endswith("-INDEX"):
            return findings
    targets = _load_section_targets(artifact, registry)
    if not targets:
        return findings
    _, body = _split_frontmatter(text.splitlines())
    # _section_word_counts() already returns only ## (level-2) headings.
    present = {_normalise_heading(h) for h, _start, _wc in _section_word_counts(body)}
    for key in targets:
        if key not in present:
            findings.append(
                Finding(
                    code="STRUCT01",
                    severity="error",
                    path=rel,
                    line=1,
                    section=key,
                    message=f"missing required section: {key}",
                )
            )
    return findings


def _check_threshold_consistency(corpus: list[tuple[str, str]]) -> list[Finding]:
    """AS7 — corpus-level: when the same threshold key suffix (the part after
    ``TYPE.NN.``) is referenced in ≥ 2 artifacts with different inline numeric
    values, flag drift. Values are read from the same line as the
    ``@threshold:`` reference or the previous line (the canonical "X under N
    ms\\nTracked as @threshold: …" pattern). Warning-only; deterministic.
    """
    by_suffix: dict[str, dict[str, list[tuple[str, int]]]] = {}
    for rel, text in corpus:
        lines = text.splitlines()
        for i, line in enumerate(lines, 1):
            m = _THRESHOLD_PARSED.search(line)
            if not m:
                continue
            suffix = m.group(3)
            ctx_prev = lines[i - 2] if i >= 2 else ""
            ctx = ctx_prev + " " + line
            vm = _THRESHOLD_VALUE.search(ctx)
            if vm:
                value = f"{vm.group(1)} {vm.group(2)}"
                by_suffix.setdefault(suffix, {}).setdefault(value, []).append((rel, i))
    findings: list[Finding] = []
    for suffix, values in by_suffix.items():
        if len(values) > 1:
            sample = ", ".join(sorted(values.keys()))
            for value, locs in values.items():
                for rel, line in locs:
                    findings.append(
                        Finding(
                            rel,
                            line,
                            "TH02",
                            f"threshold suffix '{suffix}' = {value} here; corpus has [{sample}]",
                            severity="warning",
                        )
                    )
    return findings


# --- Bidirectional element edge-graph (CFB-PR-2 DD-1 / R-c) --------------------
# `_check_trace_resolution` computes the citation adjacency per-line and
# discards it; forward coverage needs it retained. `build_edge_graph` keeps
# every UPSTREAM `@<layer>:` citation as a `TraceEdge`, so forward
# (cited→citers) and backward (citer→cited) adjacency both derive from one
# structure. The graph is NET-NEW: today's `element_index` is a declaration
# presence map that excludes downstream citations, so this adjacency does not
# exist yet.


@dataclass(frozen=True)
class TraceEdge:
    """One UPSTREAM `@<layer>:` citation: ``citer_doc`` (downstream) cites
    ``cited_token`` (an element id or doc id), whose host doc is ``cited_doc``.
    ``line`` is 1-based in ``citer_doc``."""

    citer_doc: str
    citer_layer: str
    cited_token: str
    cited_doc: str
    line: int


@dataclass(frozen=True)
class EdgeGraph:
    """Corpus-wide upstream-citation adjacency (CFB-PR-2 DD-1).

    ``element_host`` maps each element id to its *declaring* host doc
    (citations excluded — R-c). ``doc_layer`` maps doc id → artifact code.
    ``edges`` is every upstream citation edge.
    """

    element_host: dict[str, str]
    doc_layer: dict[str, str]
    edges: tuple[TraceEdge, ...]

    def citers_of(self, token: str) -> set[str]:
        """Doc ids that cite ``token`` (an element id or doc id) directly."""
        return {e.citer_doc for e in self.edges if e.cited_token == token}

    def citers_of_doc(self, doc_id: str) -> set[str]:
        """Doc ids that cite ANY element of ``doc_id`` (or the doc id itself)."""
        return {e.citer_doc for e in self.edges if e.cited_doc == doc_id}

    def citers_in_layer(self, token: str, layer: str) -> set[str]:
        """``citers_of(token)`` restricted to citers in the given layer."""
        return {
            e.citer_doc for e in self.edges if e.cited_token == token and e.citer_layer == layer
        }


def _artifact_code(fm: dict | None) -> str:
    """Artifact code from frontmatter — ``artifact_type`` if present (keeping a
    trailing ``-INDEX`` marker so callers can skip index docs), else the prefix
    of ``doc_id``."""
    if not fm:
        return ""
    code = str(fm.get("artifact_type") or "").strip().upper()
    if code:
        return code
    doc_id = str(fm.get("doc_id") or "").strip().strip('"').strip("'")
    m = re.match(r"^([A-Z]+)-", doc_id)
    return m.group(1) if m else ""


def build_edge_graph(corpus: list[tuple[str, str]]) -> EdgeGraph:
    """Build the net-new bidirectional element edge-graph (CFB-PR-2 DD-1 / R-c).

    Retains every UPSTREAM `@<layer>:` citation. An edge is recorded only when
    the cited token is strictly upstream of the citer (``cited_layer <
    citer_layer``) — matching `_check_trace_resolution`'s strictly-downstream
    skip (TRACE-RES-FIXUP-001 Fix 1); same-layer sibling lineage is kept,
    self-references are dropped. Index docs (``*-INDEX``) emit no edges.
    Multi-`@brd` pipe lines yield one edge per tag (DD-8, via the shared regex).
    """
    element_host: dict[str, str] = {}
    doc_layer: dict[str, str] = {}
    docs: list[tuple[str, str]] = []  # (doc_id, text) for docs with a doc_id
    for _rel, text in corpus:
        fm = _extract_frontmatter(text)
        doc_id = ""
        if fm:
            doc_id = str(fm.get("doc_id") or "").strip().strip('"').strip("'")
        if not doc_id:
            continue
        doc_layer[doc_id] = _artifact_code(fm)
        docs.append((doc_id, text))
        # Element declarations live only in their host doc (R-c: a cited element
        # in a downstream doc must not declare itself).
        for m in _ELEM_ID.finditer(text):
            elem = m.group(0)
            parts = elem.split(".")
            if len(parts) >= 2 and f"{parts[0]}-{parts[1]}" == doc_id:
                element_host.setdefault(elem, doc_id)

    edges: list[TraceEdge] = []
    for doc_id, text in docs:
        citer_code = doc_layer.get(doc_id, "")
        if citer_code.endswith("-INDEX"):
            continue  # index docs intentionally carry no real lineage
        citer_n = _LAYER_INDEX.get(citer_code, 0)
        for i, line in enumerate(text.splitlines(), 1):
            for m in _TRACE_TAG.finditer(line):
                value = m.group(2)
                cited_doc = doc_id_from_token(value)
                if cited_doc is None or cited_doc == doc_id:
                    continue  # malformed value, or a self-reference (no lineage)
                cited_n = _LAYER_INDEX.get(cited_doc.split("-", 1)[0], 0)
                # Strictly-downstream forward references are not upstream edges.
                if citer_n and cited_n and cited_n > citer_n:
                    continue
                edges.append(TraceEdge(doc_id, citer_code, value, cited_doc, i))
    return EdgeGraph(element_host, doc_layer, tuple(edges))


def _check_trace_resolution(
    corpus: list[tuple[str, str]],
    layers: dict,
    doc_re: re.Pattern,
    elem_re: re.Pattern,
) -> list[Finding]:
    """TRACE-RES-001 — every emitted UPSTREAM ``@<layer>: <ID>`` tag in
    the corpus resolves on disk (the target document exists AND the cited
    element ID is present in that document).

    Backs the framework's necessary-upstream contract
    (NECESSARY-UPSTREAM-001): the structural floor enforces resolution
    uniformly at every layer regardless of whether the layer carries an
    auditor lens.

    Skipped:
      * Index documents (frontmatter ``artifact_type: <X>-INDEX``) — they
        intentionally carry no trace tags.
      * Placeholder / malformed tag values — covered by PH01 / ID01.
      * Downstream tags (tags whose layer-number is greater than the
        artifact's own layer-number). The necessary-upstream contract is
        about UPSTREAM lineage; downstream pointers are informational
        forward references that may point at layers the cascade hasn't
        produced yet. Per TRACE-RES-FIXUP-001 Fix 1.
        Self-tags (same layer as artifact, doc_id matches artifact's own
        doc_id) resolve naturally via doc_index — no explicit skip needed.
        Sibling references (same layer, different doc_id) still resolve
        against doc_index — they are real upstream lineage within a layer.
    """
    # Map artifact code → layer number for upstream/downstream comparison.
    layer_number = {code: layer["number"] for code, layer in layers.items()}

    doc_index: dict[str, str] = {}
    element_index: dict[str, str] = {}
    for rel, text in corpus:
        fm = _extract_frontmatter(text)
        doc_id = ""
        if fm:
            doc_id = str(fm.get("doc_id") or "").strip().strip('"').strip("'")
        if not doc_id:
            continue
        doc_index[doc_id] = text
        # Element IDs are added to the index only when declared in their own
        # host document (citations in downstream docs are excluded so they
        # cannot resolve themselves).
        for m in _ELEM_ID.finditer(text):
            elem = m.group(0)
            if not elem_re.match(elem):
                continue
            parts = elem.split(".")
            if len(parts) >= 2:
                host = f"{parts[0]}-{parts[1]}"
                if host == doc_id:
                    element_index.setdefault(elem, doc_id)

    findings: list[Finding] = []
    for rel, text in corpus:
        fm = _extract_frontmatter(text)
        if fm and str(fm.get("artifact_type") or "").strip().endswith("-INDEX"):
            continue
        # Derive artifact's own layer-number for downstream-skip comparison.
        artifact_code = ""
        if fm:
            artifact_code = str(fm.get("artifact_type") or "").strip().upper()
        if not artifact_code:
            doc_id_str = str(fm.get("doc_id") or "").strip().strip('"').strip("'") if fm else ""
            m_pfx = re.match(r"^([A-Z]+)-", doc_id_str)
            if m_pfx:
                artifact_code = m_pfx.group(1)
        my_layer_n = layer_number.get(artifact_code, 0)

        for i, line in enumerate(text.splitlines(), 1):
            for m in _TAG.finditer(line):
                tag_layer = m.group(1).upper()
                tag_layer_n = layer_number.get(tag_layer, 0)
                # Skip downstream tags: forward pointers to layers below the
                # artifact's own layer. Per TRACE-RES-FIXUP-001 Fix 1.
                if my_layer_n and tag_layer_n and tag_layer_n > my_layer_n:
                    continue
                value = m.group(2)
                if not (doc_re.match(value) or elem_re.match(value)):
                    continue
                if doc_re.match(value):
                    if value not in doc_index:
                        findings.append(
                            Finding(
                                rel,
                                i,
                                "TRACE-RES-001",
                                f"trace tag '@{m.group(1)}: {value}' "
                                f"references unknown document "
                                f"(no corpus member has doc_id '{value}')",
                            )
                        )
                else:
                    if value not in element_index:
                        head = value.split(".", 2)
                        host_doc = (
                            f"{head[0]}-{head[1]}"
                            if len(head) >= 2 and head[1].isdigit()
                            else "<unknown>"
                        )
                        host_status = (
                            "host document missing"
                            if host_doc not in doc_index
                            else "element id not declared in host document"
                        )
                        findings.append(
                            Finding(
                                rel,
                                i,
                                "TRACE-RES-001",
                                f"trace tag '@{m.group(1)}: {value}' "
                                f"unresolvable ({host_status}; expected host "
                                f"'{host_doc}')",
                            )
                        )
    return findings


def lint_path(target: Path, registry: Path | None = None) -> list[Finding]:
    """Lint a file or recurse a directory; returns all findings."""
    layers, doc_re, elem_re = _load_registry(registry)
    findings: list[Finding] = []
    corpus: list[tuple[str, str]] = []  # (rel_path, text) — for corpus-level passes

    def _collect(p: Path):
        artifact = detect_layer(p, layers)
        if artifact is None:
            return
        try:
            rel = p.resolve().relative_to(Path.cwd().resolve()).as_posix()
        except ValueError:
            rel = p.as_posix()
        text = p.read_text(encoding="utf-8")
        corpus.append((rel, text))
        findings.extend(lint_text(text, artifact, rel, layers, doc_re, elem_re, registry=registry))

    if target.is_dir():
        for p in sorted(target.rglob("*")):
            if p.is_file() and p.suffix.lower() in (".md", ".yaml", ".yml"):
                _collect(p)
    elif target.is_file():
        _collect(target)

    findings.extend(_check_threshold_consistency(corpus))
    findings.extend(_check_threshold_resolution(corpus))
    findings.extend(_check_id_uniqueness(corpus))
    findings.extend(_check_cascade(corpus))
    findings.extend(_check_staleness(corpus, _framework_version(registry or find_registry())))
    findings.extend(_check_trace_resolution(corpus, layers, doc_re, elem_re))
    return findings


def _check_threshold_resolution(corpus: list[tuple[str, str]]) -> list[Finding]:
    """TH-RES-001 (CLEANUP-PR-D item 16) — every downstream ``@threshold:
    PRD.NN.<category>.<key>`` citation MUST resolve to a `full_id` entry
    in the host PRD's `component_decomposition.components[].thresholds[]`
    section.

    The check is **citation-driven**: it scans for `@threshold:` citations
    only; PRDs with no downstream threshold-cites pass the gate
    automatically (the `component_decomposition` section is OPTIONAL per
    PRD template).

    Severity policy:
      - PRD has NO `component_decomposition` section AND downstream cites
        a threshold to that PRD → P2 finding on the host PRD
        ("component_decomposition section missing; downstream cites
        @threshold").
      - PRD has the section BUT the cited threshold's full_id isn't in
        it → P1 finding on the citing artifact ("@threshold: <full_id>
        unresolved; not declared in PRD-NN").
    """
    import yaml as _yaml  # local alias avoids shadowing in caller

    findings: list[Finding] = []

    # 1. Collect every @threshold: PRD.NN.<cat>.<key> citation by host PRD.
    cite_re = re.compile(r"@threshold:\s*(PRD)\.(\d+)\.([a-z_]+(?:\.[a-z0-9_]+)+)")
    citations: dict[tuple[str, str], list[tuple[str, int]]] = {}
    # key: (PRD-id, full_id_after_PRD.NN.); value: list of (citing_rel, line)
    for rel, text in corpus:
        # Skip the PRDs themselves — citations only count from downstream.
        if "/02_PRD/" in rel:
            continue
        for i, line in enumerate(text.splitlines(), start=1):
            for m in cite_re.finditer(line):
                prd_id = f"PRD-{m.group(2).zfill(2)}"
                full_id = f"PRD.{m.group(2)}.{m.group(3)}"
                citations.setdefault((prd_id, full_id), []).append((rel, i))

    if not citations:
        return findings

    # 2. Index each PRD's declared thresholds.
    declared: dict[str, set[str]] = {}  # prd_id -> set of full_ids
    has_section: dict[str, bool] = {}
    for rel, text in corpus:
        if "/02_PRD/" not in rel:
            continue
        m = re.search(r"PRD-(\d+)", Path(rel).name)
        if not m:
            continue
        prd_id = f"PRD-{m.group(1).zfill(2)}"
        # The PRD may be markdown (with embedded YAML frontmatter or a YAML
        # ## Component Decomposition section); to keep the rule simple, look
        # for the `component_decomposition` key + harvest `full_id:` values.
        if "component_decomposition" not in text:
            has_section[prd_id] = False
            continue
        has_section[prd_id] = True
        declared.setdefault(prd_id, set())
        # Harvest `full_id: PRD.NN.x.y` entries verbatim. Robust to either
        # YAML or markdown surface; we just want the value.
        for m2 in re.finditer(r"full_id:\s*[\"']?(PRD\.\d+\.[a-z_]+(?:\.[a-z0-9_]+)+)[\"']?", text):
            declared[prd_id].add(m2.group(1))

    # 3. Emit findings. Group by PRD so the "missing section" case emits
    # ONCE per PRD (not once per cited threshold), avoiding noise.
    missing_section_thresholds: dict[str, list[str]] = {}
    for (prd_id, full_id), cites in citations.items():
        if not has_section.get(prd_id):
            missing_section_thresholds.setdefault(prd_id, []).append(full_id)
            continue
        if full_id not in declared.get(prd_id, set()):
            # Severity P1 — section exists but threshold key not declared.
            for citing_rel, line in cites:
                findings.append(
                    Finding(
                        citing_rel,
                        line,
                        "TH-RES-001",
                        f"@threshold: {full_id} unresolved; not declared in {prd_id}'s "
                        f"component_decomposition section",
                        severity="error",
                    )
                )
    # Emit one P2 advisory per PRD missing the section.
    for prd_id, thresholds in missing_section_thresholds.items():
        prd_rel = next(
            (
                rel
                for rel, _ in corpus
                if f"/02_PRD/{prd_id}" in rel or Path(rel).name.startswith(prd_id)
            ),
            prd_id,
        )
        examples = ", ".join(sorted(set(thresholds))[:3])
        findings.append(
            Finding(
                str(prd_rel),
                1,
                "TH-RES-001",
                f"{prd_id} missing `component_decomposition` section; "
                f"{len(set(thresholds))} downstream @threshold citation(s) "
                f"cannot resolve (e.g. {examples})",
                severity="error",
            )
        )

    return findings
