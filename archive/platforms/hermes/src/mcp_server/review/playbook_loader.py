"""Per-(layer, lens) playbook loading for the review saga (HERMES-PARITY-PHASE-2).

The framework playbook contract (`framework/governance/REVIEW_TEAM.md` §Playbooks)
gives each review lens a layer-specific reasoning frame + a numbered evidence
checklist (`C1`..`Cn`) at `framework/playbooks/<NN>_<LAYER>/<lens>.md`. This module
resolves that file for a branch persona and parses its valid check ids.

Only framework **review-crew** lenses (per `REVIEW_CREWS.yaml`, after
`canonical_persona` aliasing) have playbooks. Non-crew branch personas — e.g.
`fact_checker` (an extra Hermes lens) and `chairperson` (→ `synthesizer`, the
reducer) — legitimately have none: they get no playbook and no citation floor,
NOT a `BRANCH_FAILED`. A missing file for a persona that IS a crew lens is an
error (`PlaybookMissing`), never a silent playbook-less prompt.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from mcp_server.review.review_scoring import canonical_persona, load_crew_weights

# Short layer name (REVIEW_CREWS.yaml key) -> playbook directory (framework/layers convention).
_LAYER_DIRS: dict[str, str] = {
    "BRD": "01_BRD",
    "PRD": "02_PRD",
    "EARS": "03_EARS",
    "BDD": "04_BDD",
    "ADR": "05_ADR",
    "SPEC": "06_SPEC",
    "TDD": "07_TDD",
    "IPLAN": "08_IPLAN",
    "CHG": "09_CHG",
}

# A `## Required evidence checks` row: `**C1 — ...`.
_CHECK_RE = re.compile(r"^\*\*(C\d+)\b", re.MULTILINE)


class PlaybookMissing(RuntimeError):
    """A crew lens's expected playbook file is absent."""


@dataclass(frozen=True)
class Playbook:
    layer_dir: str
    lens: str
    content: str
    check_ids: frozenset[str]
    path: Path


def _framework_playbooks_root() -> Path:
    # .../platforms/hermes/src/mcp_server/review/playbook_loader.py
    #   parents[5] == repository root  (same idiom as review_scoring._default_crews_path)
    return Path(__file__).resolve().parents[5] / "framework" / "playbooks"


def normalize_layer(layer: str | None) -> tuple[str, str]:
    """Return ``(short, layer_dir)`` — e.g. ``("BRD", "01_BRD")`` — from either the
    doc-type (``brd``) or the directory form (``01_BRD``)."""
    s = str(layer or "").strip()
    if len(s) > 3 and s[:2].isdigit() and s[2] == "_":
        return s.split("_", 1)[1].upper(), s
    short = s.upper()
    return short, _LAYER_DIRS.get(short, "")


def is_crew_lens(layer: str | None, persona: str, crews_path: Path | None = None) -> bool:
    """True iff ``persona`` (after aliasing) is a framework review-crew lens for ``layer``."""
    lens = canonical_persona(persona)
    short, _ = normalize_layer(layer)
    try:
        crew = load_crew_weights(short, crews_path)
    except KeyError:
        return False
    return lens in crew


@lru_cache(maxsize=64)
def _read_playbook(path_str: str) -> tuple[str, frozenset[str]]:
    path = Path(path_str)
    content = path.read_text(encoding="utf-8")
    return content, frozenset(_CHECK_RE.findall(content))


def load_playbook(
    layer: str | None, persona: str, crews_path: Path | None = None
) -> Playbook | None:
    """Resolve the playbook for a branch persona.

    Returns ``None`` for a non-crew persona (``fact_checker``/``chairperson``) — no
    playbook, no citation floor. Raises :class:`PlaybookMissing` if a persona that
    IS a crew lens has no playbook file.
    """
    if not is_crew_lens(layer, persona, crews_path):
        return None
    lens = canonical_persona(persona)
    _, layer_dir = normalize_layer(layer)
    path = _framework_playbooks_root() / layer_dir / f"{lens}.md"
    if not path.is_file():
        raise PlaybookMissing(f"playbook missing: {path}")
    content, check_ids = _read_playbook(str(path))
    return Playbook(layer_dir=layer_dir, lens=lens, content=content, check_ids=check_ids, path=path)
