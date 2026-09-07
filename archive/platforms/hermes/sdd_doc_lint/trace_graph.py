"""Shared @-tag trace primitives — the single source of the parsing/locating
rules used by both the backward walker (`trace_walk.py`) and the forward
coverage engine (`sdd_coverage.py` / the `sdd_doc_lint` coverage gate).

Extracted from `trace_walk.py` per CFB-PR-2 DD-1 so the two directions of the
trace graph agree byte-for-byte on: the layer order, the `@`-tag regex, the
doc/element ID forms, and the token→doc-id / doc-id→path helpers.

Lives as a submodule of the `sdd_doc_lint` package (rather than a loose
`tools/` sibling) so the **vendored** linter copies — synced into each platform
by `sync-vendored.sh` — can import it via a package-relative path
(`from .trace_graph import …`) that resolves regardless of how the package was
placed on `sys.path`. The two unvendored `tools/` scripts (`trace_walk.py`,
`sdd_coverage.py`) reach it via `from sdd_doc_lint.trace_graph import …`.

Pure stdlib (`re` + `pathlib` only); no framework or third-party imports — the
module itself is importable standalone even where PyYAML is absent.
"""

from __future__ import annotations

import re
from pathlib import Path

#: The 8 SDD layers in chain order; index (1-based) gives the layer's depth.
KNOWN_LAYERS = ("BRD", "PRD", "EARS", "BDD", "ADR", "SPEC", "TDD", "IPLAN")
LAYER_INDEX = {name: i + 1 for i, name in enumerate(KNOWN_LAYERS)}

#: Every `@<layer>: <value>` token. The value capture terminates on whitespace, a
#: pipe, OR a quote. The pipe keeps a multi-tag line (`@brd: X | @brd: Z`) yielding
#: one match per tag (CFB-PR-2 DD-8); the quote-exclusion (LINT-TAG-QUOTE-001, issue
#: #542) stops a tag closing a quoted YAML scalar (`tdd_ref: "@tdd: TDD.01.04.aaaa"`)
#: from glomming the closing quote into the value — which failed the anchored
#: `ELEM_FORM` below and dropped the citation from the edge graph SILENTLY. Sibling of
#: the same exclusion on `_THRESHOLD` in `__init__.py`. Safe because a tag value is
#: always validated against `DOC_FORM`/`ELEM_FORM` (and the registry `id_patterns`),
#: none of which admit a quote.
TAG = re.compile(r"@(" + "|".join(t.lower() for t in KNOWN_LAYERS) + r")\s*:\s*([^\s|'\"]+)")

#: Document-level id, e.g. `BRD-01`.
DOC_FORM = re.compile(r"^([A-Z]+)-\d+$")
#: Element-level id, e.g. `BRD.01.07.6c3f` (4-hex content-hash slug).
ELEM_FORM = re.compile(r"^([A-Z]+)\.\d+\.\d+\.[a-f0-9]+$")


def doc_id_from_token(token: str) -> str | None:
    """Reduce an `@`-tag value to its host doc id (`TYPE-NN`).

    `BRD-01` → `BRD-01`; `BRD.01.07.6c3f` → `BRD-01`; anything else → `None`.
    """
    if DOC_FORM.match(token):
        return token
    if ELEM_FORM.match(token):
        prefix, _, rest = token.partition(".")
        first_segment = rest.split(".", 1)[0]
        return f"{prefix}-{first_segment}"
    return None


def locate_doc(doc_id: str, docs_root: Path) -> Path | None:
    """Resolve `TYPE-NN` to its file under `docs_root/NN_TYPE/` (`.md|.yaml|.yml`)."""
    m = DOC_FORM.match(doc_id)
    if not m:
        return None
    layer = m.group(1)
    layer_n = LAYER_INDEX.get(layer)
    if layer_n is None:
        return None
    folder = docs_root / f"{layer_n:02d}_{layer}"
    for ext in (".md", ".yaml", ".yml"):
        candidate = folder / f"{doc_id}{ext}"
        if candidate.is_file():
            return candidate
    return None


def emit_tags(text: str) -> list[str]:
    """Every `@`-tag VALUE token in `text` (multi-`@` pipe lines handled)."""
    return [m.group(2) for m in TAG.finditer(text)]
