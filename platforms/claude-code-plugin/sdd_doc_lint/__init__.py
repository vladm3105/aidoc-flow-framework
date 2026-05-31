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
    # STY03 — document body over the +50% target (blocking).
    target = _DOC_TARGET_WORDS.get(artifact)
    if target is not None:
        words = sum(len(line.split()) for line in body)
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
    """STRUCT01: every required <TYPE>-TEMPLATE.yaml section must appear as a ## heading."""
    findings: list[Finding] = []
    if not artifact:
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
    findings.extend(_check_id_uniqueness(corpus))
    findings.extend(_check_cascade(corpus))
    findings.extend(_check_staleness(corpus, _framework_version(registry or find_registry())))
    return findings
