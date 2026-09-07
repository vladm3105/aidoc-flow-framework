"""Prompt-hygiene helpers shared by every review-prompt builder.

`strip_author_self_claim` implements the `REVIEW_TEAM.md` §"Strip author self-claim"
MUST (CLEANUP-PR-B item 9): remove author self-assessment score lines from the
artifact body **before it reaches any review lens** — in `team` mode AND
`single_pass` mode. Applied at the shared builder (`runner.run_project_review_build`)
so every caller (saga branches/aggregate, MCP `prompt_only`, CLI `single_pass`) is
covered at one chokepoint. In-prompt only; the on-disk artifact keeps the fields.
"""

from __future__ import annotations

import re
from dataclasses import replace

from mcp_server.prompts import SourceSection

# Matches an assignment line whose key ends `_ready_score`/`_score` or is literally
# `readiness_score`/`audit_score` (REVIEW_TEAM.md canonical list). Consumes the whole
# line incl. its trailing newline; `[ \t]` (not `\s`) so it can't span across lines.
_SELF_CLAIM_RE = re.compile(
    r"^[ \t]*(?:[a-z0-9_]*_(?:ready_)?score|readiness_score|audit_score)[ \t]*[:=].*$\n?",
    re.IGNORECASE | re.MULTILINE,
)


def strip_author_self_claim(sections: list[SourceSection]) -> list[SourceSection]:
    """Redact author self-assessment score lines from each section body (in-prompt
    only; the on-disk artifact keeps them). Anchor-effect fix — a lens must not see
    the author's own score. Non-matching content is preserved verbatim; idempotent."""
    stripped: list[SourceSection] = []
    for section in sections:
        new_content = _SELF_CLAIM_RE.sub("", section.content)
        stripped.append(
            section if new_content == section.content else replace(section, content=new_content)
        )
    return stripped
