#!/usr/bin/env python3
"""Shared prerequisites for the sdd_doc_lint CLIs (extracted under #668).

Both `chg_lint.py` and `bugfix_lint.py` run in two modes — `python -m
sdd_doc_lint.<name>` (package mode, repo root on `sys.path`) and
`python sdd_doc_lint/<name>.py` (script mode, only `sdd_doc_lint/` on
`sys.path`) — so importers use the dual-mode form:

    try:
        from sdd_doc_lint._common import load_yaml_file, yaml
    except ImportError:
        from _common import load_yaml_file, yaml

Deliberately NOT shared: `bugfix_lint._load` keeps its error-dict
convention (`__io_error__` / `__parse_error__`), which the BGF-00 path
consumes — collapsing it onto `(data, error)` tuples would change
reported messages.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install with: pip install pyyaml", file=sys.stderr)
    raise SystemExit(3)


def load_yaml_file(path: Path | str) -> tuple[Any | None, str | None]:
    """Read + parse a YAML file.

    Returns `(data, None)` on success, `(None, error_message)` on I/O or
    parse failure. Message shapes match the former inline loader in
    `chg_lint.lint_chg` exactly (`File not found: …` / `YAML parse error: …`).
    """
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError:
        return None, f"File not found: {path}"
    try:
        return yaml.safe_load(text), None
    except yaml.YAMLError as e:
        return None, f"YAML parse error: {e}"
