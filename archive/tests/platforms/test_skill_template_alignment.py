"""Conformance: Claude Code plugin skills align with the canonical layer
templates.

Catches the drift class that produced the `doc-flow` confabulation incident
(skills describing sections that do not exist in the template, audit checklists
declaring hard-coded counts that drift away from the template). The template
is the single source of truth (D-0013); skills that reference structure must
align with it.

Checks per layer (BRD/PRD/EARS/BDD/ADR/SPEC/TDD/IPLAN):

1. The audit skill (``doc-<layer>-audit/SKILL.md``) defers to the template:
   it must contain the explicit "Load <TYPE>-TEMPLATE.yaml and enumerate" block
   and **must not** declare a hard-coded section count of the form
   ``all N template sections`` or ``all N required sections``.

2. The creation skill (``doc-<layer>/SKILL.md``) declares a section count in
   its ``### Required structure (N …)`` heading that matches the template's
   own ``# Section N:`` numbering.

3. The creation skill's numbered section list references only template keys —
   no phantom sections (e.g. ``User Stories`` in BRD before this fix).
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml
from _spec import FRAMEWORK, PLATFORMS_ROOT, registry_layers

PLUGIN_SKILLS = PLATFORMS_ROOT / "claude-code-plugin" / "skills"

# The convention is: template top-level YAML keys that are not header
# metadata are sections.
_HEADER_KEYS = {"id", "title", "metadata", "version", "schema_version", "description", "layer"}

# Words that commonly appear in a section title and a creation skill's list
# but are also generic English — stop-words for the "references only template
# keys" check.
_STOPWORDS = {
    "a",
    "an",
    "and",
    "the",
    "of",
    "to",
    "in",
    "for",
    "with",
    "or",
    "on",
    "at",
    "incl",
    "incl.",
    "from",
    "by",
    "as",
    "this",
    "that",
    "see",
    "per",
}


def _normalise(token: str) -> str:
    return re.sub(r"[^a-z0-9]", "", token.lower())


def _template_sections(template_path: Path) -> dict[str, dict]:
    """Return {key: section_body} for every top-level mapping that is not a
    metadata header key."""
    with template_path.open(encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    return {k: v for k, v in doc.items() if k not in _HEADER_KEYS and isinstance(v, dict)}


def _template_numbered_count(template_path: Path) -> int:
    """Count the template's own ``# Section N: …`` comment headers."""
    text = template_path.read_text(encoding="utf-8")
    return len(re.findall(r"^# Section \d+:", text, flags=re.MULTILINE))


def _required_structure_count(skill_path: Path) -> int | None:
    text = skill_path.read_text(encoding="utf-8")
    m = re.search(r"### Required structure \((\d+)\b", text)
    return int(m.group(1)) if m else None


def _required_structure_block(skill_path: Path) -> str:
    """The text from `### Required structure` up to the next `###` heading."""
    text = skill_path.read_text(encoding="utf-8")
    m = re.search(
        r"### Required structure[^\n]*\n(.*?)(?=^###\s|\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    return m.group(1) if m else ""


def _skill_section_titles(block: str) -> list[str]:
    """Extract bolded or numbered section titles from a Required-structure
    block. Returns the raw title strings (e.g. ``Functional Requirements``).
    """
    titles: list[str] = []
    # Bold list items: `1. **Title** — …`
    titles += re.findall(r"\d+\.\s+\*\*([^*]+)\*\*", block)
    # Inline-dotted list items: `2. Title (incl. …) · 3. Title …`
    for piece in re.split(r"·", block):
        m = re.match(r"\s*\d+\.\s+([^(·\n]+)", piece)
        if m:
            titles.append(m.group(1).strip().rstrip("."))
    # De-dup, preserve order.
    seen, out = set(), []
    for t in titles:
        n = _normalise(t)
        if n and n not in seen:
            seen.add(n)
            out.append(t.strip())
    return out


class AuditSkillsDeferToTemplate(unittest.TestCase):
    """Each ``doc-<layer>-audit`` SKILL.md loads the template at runtime and
    does not hard-code a brittle section count."""

    def test_template_enumeration_block_present(self):
        for layer in registry_layers():
            artifact = layer["artifact"]
            skill = PLUGIN_SKILLS / f"doc-{artifact.lower()}-audit" / "SKILL.md"
            with self.subTest(layer=artifact):
                self.assertTrue(skill.is_file(), f"missing {skill}")
                body = skill.read_text(encoding="utf-8")
                self.assertIn(
                    "Template-conformance enumeration",
                    body,
                    f"{skill.name} is missing the explicit template-enumeration"
                    " block — the auditor will not know to load the template",
                )
                self.assertIn(
                    f"{artifact}-TEMPLATE.yaml",
                    body,
                    f"{skill.name} must reference {artifact}-TEMPLATE.yaml in"
                    " the enumeration block",
                )

    def test_no_hardcoded_section_count(self):
        pattern = re.compile(
            r"all\s+\d+\s+(?:required\s+)?(?:template\s+)?sections",
            re.IGNORECASE,
        )
        for layer in registry_layers():
            artifact = layer["artifact"]
            skill = PLUGIN_SKILLS / f"doc-{artifact.lower()}-audit" / "SKILL.md"
            with self.subTest(layer=artifact):
                body = skill.read_text(encoding="utf-8")
                hits = pattern.findall(body)
                self.assertFalse(
                    hits,
                    f"{skill.name} still hard-codes a section count "
                    f"({hits!r}); audit skills must defer to the template "
                    "enumeration",
                )


class CreationSkillsMatchTemplate(unittest.TestCase):
    """Each ``doc-<layer>`` SKILL.md's ``Required structure`` count matches
    the template's own ``# Section N:`` numbered count, and its section list
    contains only real template keys (no phantoms)."""

    def test_required_structure_count_matches_template(self):
        for layer in registry_layers():
            artifact = layer["artifact"]
            skill = PLUGIN_SKILLS / f"doc-{artifact.lower()}" / "SKILL.md"
            template = FRAMEWORK / layer["folder"] / layer["template"]
            with self.subTest(layer=artifact):
                self.assertTrue(skill.is_file(), f"missing {skill}")
                self.assertTrue(template.is_file(), f"missing {template}")
                skill_count = _required_structure_count(skill)
                self.assertIsNotNone(
                    skill_count,
                    f"{skill.name} is missing a `### Required structure (N …)` heading",
                )
                template_count = _template_numbered_count(template)
                self.assertEqual(
                    skill_count,
                    template_count,
                    f"{skill.name} declares {skill_count} sections but "
                    f"{template.name} numbers {template_count} via "
                    "`# Section N:` comments — the template is the source of "
                    "truth (D-0013)",
                )

    def test_required_structure_section_list_uses_only_template_keys(self):
        for layer in registry_layers():
            artifact = layer["artifact"]
            skill = PLUGIN_SKILLS / f"doc-{artifact.lower()}" / "SKILL.md"
            template = FRAMEWORK / layer["folder"] / layer["template"]
            with self.subTest(layer=artifact):
                block = _required_structure_block(skill)
                titles = _skill_section_titles(block)
                template_keys = {_normalise(k) for k in _template_sections(template).keys()}
                # Heuristic: a non-phantom title must share at least one
                # significant token with **some** template key (treating each
                # template key as a single normalised string for substring
                # comparison). Genuine phantoms (e.g. "User Stories" in a BRD
                # whose template has no `user_stories` key) share no token
                # with any key.
                phantoms = []
                for title in titles:
                    tokens = [
                        _normalise(t) for t in title.split() if t and t.lower() not in _STOPWORDS
                    ]
                    if not tokens:
                        continue
                    if any(any(tok and tok in key for tok in tokens) for key in template_keys):
                        continue
                    phantoms.append(title)
                self.assertFalse(
                    phantoms,
                    f"{skill.name} section list contains titles with no "
                    f"matching template key: {phantoms}. The template is the "
                    "source of truth — remove phantom sections from the skill"
                    " or add them to the template.",
                )


if __name__ == "__main__":
    unittest.main()
