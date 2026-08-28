"""Conformance: instance format has ONE normative source, and no spec surface contradicts it.

GD-15 (spec 0.43.0) made YAML the mandatory instance format for layers 1-8 and, in the same
entry, declined to adopt the frontmatter contract that makes an instance legible to any rule.
GD-17 (INSTANCE-FORMAT-SSOT-001) resolves the resulting incoherence: `LAYER_REGISTRY.yaml`
`extensions` is the sole *authority* for instance format, every other carrier states its value
in-layer and cross-references the registry (GD-09 rule 2), and the mandate takes normative
effect on a testable outcome rather than a component list.

This guard locks the negative property: **no file under the framework spec tree names an
AUTHORED layer instance whose extension is absent from that layer's `extensions`.** The
distinction matters: GD-15 sanctions Markdown as an optional *rendering* of an instance, and
`extensions` governs the authored source, not every legitimate reference to a rendering. That is
why exemption 2 exists rather than being a violation.

Two exemptions, both load-bearing:

1. **Index docs, exempted at the MENTION level, not the file level.** The registry header's
   `Index templates:` block sanctions `.md` index docs for layers 01-07 (cited by name, not by
   line: an EFFECTIVE CONDITION block was inserted above it and shifted the numbers once already). Seven such mentions sit inside index files; two
   more sit in non-index files (`BRD-TEMPLATE.yaml`, `ID_NAMING_STANDARDS.md`). A file-level
   exemption -- e.g. reusing the linter's `_is_index_doc`, which tests the document being linted
   -- catches only the seven and false-positives on the other two.
2. **`governance/DECISIONS.md`.** Its `IPLAN-01.md` mention describes the real corpus artifact
   inside a ratified GD-16 measurement. Flagging it would demand rewriting a decision record.

**Scope is the framework spec tree only** (`REPO_ROOT/framework`), NOT a `framework/**` glob:
`platforms/claude-code-plugin/framework/` is a vendored mirror, and including it doubles every
figure and reports violations that the vendoring step -- not this guard -- resolves. Platform
authoring surfaces state their own filenames and are out of scope here; they must add their own
lock (the same caveat GD-09 recorded for its guard).
"""

from __future__ import annotations

import re
import unittest

from _spec import FRAMEWORK, load_registry

#: Eight registry artifact names, a hyphen, then two digits or the literal ``NN``, an optional
#: slug, then the extension. The digits are required: a loose ``(BRD|...)-[^\s]*\.md`` matches
#: ~14 non-instance documents under the spec tree (``IPLAN-ECOSYSTEM.md``, ``IPLAN-STANDARD.md``,
#: ``IPLAN-TDDREF-001-PLAN.md``, ...) and makes the count meaningless.
_INSTANCE_TOKEN = re.compile(
    r"\b(BRD|PRD|EARS|BDD|ADR|SPEC|TDD|IPLAN)-(NN|\d{2})([_A-Za-z0-9{}*-]*)\.(md|yaml)\b"
)

#: Ratified decision records describe artifacts as they are, not as the spec mandates.
_EXEMPT_FILES = {"governance/DECISIONS.md"}


def _allowed_extensions() -> dict[str, set[str]]:
    return {layer["artifact"]: set(layer["extensions"]) for layer in load_registry()["layers"]}


def _is_index_mention(nn: str, slug: str) -> bool:
    """Exemption 1, at the mention level: ``<TYPE>-00_index*`` wherever it appears."""
    return nn == "00" and "index" in slug


def scan_violations(*, exempt_index: bool = True, exempt_decisions: bool = True) -> list[str]:
    allowed = _allowed_extensions()
    out: list[str] = []
    for path in sorted(FRAMEWORK.rglob("*")):
        if not path.is_file() or path.suffix not in (".md", ".yaml"):
            continue
        rel = path.relative_to(FRAMEWORK).as_posix()
        if exempt_decisions and rel in _EXEMPT_FILES:
            continue
        for lineno, line in enumerate(path.read_text("utf-8").splitlines(), 1):
            for match in _INSTANCE_TOKEN.finditer(line):
                artifact, nn, slug, ext = match.groups()
                # No TEMPLATE guard here, deliberately: the slug class excludes ``.``, so
                # ``BRD-00_index.TEMPLATE.md`` cannot match _INSTANCE_TOKEN at all. A guard
                # would be unreachable today and would silently exempt a whole class if the
                # slug class were ever loosened to admit ``.``.
                assert "TEMPLATE" not in match.group(0), (
                    f"regex loosened to admit TEMPLATE filenames: {match.group(0)!r} — "
                    "decide explicitly how templates are handled before relaxing the slug class"
                )
                if exempt_index and _is_index_mention(nn, slug):
                    continue
                if f".{ext}" not in allowed[artifact]:
                    out.append(
                        f"{rel}:{lineno} {match.group(0)} (allows {sorted(allowed[artifact])})"
                    )
    return out


class InstanceFormatSingleSource(unittest.TestCase):
    def test_no_surface_contradicts_the_registry(self):
        violations = scan_violations()
        self.assertEqual(
            [],
            violations,
            "a framework spec surface names a layer instance whose extension is absent from "
            "that layer's `extensions`; the registry is the sole authority (GD-17):\n  "
            + "\n  ".join(violations),
        )

    def test_index_exemption_is_mention_level_not_file_level(self):
        """Mutation guard for exemption 1.

        Removing it must surface the nine sanctioned index mentions. Seven sit inside index
        files and two do not, so a count of seven would mean a file-level exemption had been
        substituted -- the defect this test exists to prevent.
        """
        without = scan_violations(exempt_index=False)
        baseline = scan_violations()
        surfaced = len(without) - len(baseline)
        self.assertEqual(
            9,
            surfaced,
            "removing the index exemption should surface exactly 9 sanctioned index mentions "
            f"(7 inside index files + 2 outside); got {surfaced}. A result of 7 means the "
            "exemption was implemented at the file level.",
        )

    def test_decisions_exemption_is_live(self):
        """Mutation guard for exemption 2.

        Asserts the *classification* — that removing the exemption surfaces mentions and that
        every one of them is in ``DECISIONS.md`` — rather than an exact count. The count is not
        stable: a decision record legitimately accumulates descriptive references to artifacts
        as new entries are ratified (GD-16 and GD-17 each name ``IPLAN-01.md``), so a hardcoded
        total would break on a future entry that is entirely correct.
        """
        baseline = scan_violations()
        without = scan_violations(exempt_decisions=False)
        surfaced = [v for v in without if v not in baseline]
        self.assertTrue(
            surfaced,
            "removing the DECISIONS.md exemption surfaced nothing, so the exemption is not "
            "being applied and the mutation guard is inert.",
        )
        self.assertTrue(
            all(v.startswith("governance/DECISIONS.md:") for v in surfaced),
            f"the DECISIONS.md exemption should affect only that file; got: {surfaced}",
        )


if __name__ == "__main__":
    unittest.main()
