"""Conformance: every layer skill (creation + audit) references the canonical
authoring-style governance doc, and the doc itself exists.

The framework adopted a token-efficient authoring style (governance principle
7, `framework/governance/AUTHORING_STYLE.md`) so that documents stay precise
and complete without inflating the token cost of authoring/audit/review across
a large corpus. This test prevents the rule from being forgotten when new
skills are added: every doc-<layer>/SKILL.md and doc-<layer>-audit/SKILL.md
must cite `AUTHORING_STYLE.md` in its authority/prerequisite list, and the
audit skills must additionally carry the style-check block.
"""

from __future__ import annotations

import unittest

from _spec import FRAMEWORK, PLATFORMS_ROOT, registry_layers

STYLE_DOC = FRAMEWORK / "governance" / "AUTHORING_STYLE.md"
PLUGIN_SKILLS = PLATFORMS_ROOT / "claude-code-plugin" / "skills"


class AuthoringStyleDoc(unittest.TestCase):
    def test_style_doc_present(self):
        self.assertTrue(
            STYLE_DOC.is_file(),
            f"missing canonical authoring-style doc at {STYLE_DOC}",
        )

    def test_style_doc_referenced_from_governance_core(self):
        core = (FRAMEWORK / "governance" / "DOC_GOVERNANCE_CORE.md").read_text(encoding="utf-8")
        self.assertIn(
            "AUTHORING_STYLE.md",
            core,
            "DOC_GOVERNANCE_CORE.md must cite AUTHORING_STYLE.md so it is part"
            " of the canonical governance set",
        )


class CreationSkillsCiteStyleDoc(unittest.TestCase):
    """Every doc-<layer> SKILL.md must reference AUTHORING_STYLE.md so the
    author loads it before writing."""

    def test_each_creation_skill_references_style(self):
        for layer in registry_layers():
            artifact = layer["artifact"]
            skill = PLUGIN_SKILLS / f"doc-{artifact.lower()}" / "SKILL.md"
            with self.subTest(layer=artifact):
                self.assertTrue(skill.is_file(), f"missing {skill}")
                body = skill.read_text(encoding="utf-8")
                self.assertIn(
                    "AUTHORING_STYLE.md",
                    body,
                    f"{skill.name} must reference AUTHORING_STYLE.md in its"
                    " Prerequisites/authority list so authors load it before"
                    " writing",
                )


class AuditSkillsCiteStyleAndCheckIt(unittest.TestCase):
    """Every doc-<layer>-audit SKILL.md must reference AUTHORING_STYLE.md in
    its Authority line AND carry the style-check block in its Structural
    Checklist."""

    def test_each_audit_skill_references_style(self):
        for layer in registry_layers():
            artifact = layer["artifact"]
            skill = PLUGIN_SKILLS / f"doc-{artifact.lower()}-audit" / "SKILL.md"
            with self.subTest(layer=artifact):
                self.assertTrue(skill.is_file(), f"missing {skill}")
                body = skill.read_text(encoding="utf-8")
                self.assertIn(
                    "AUTHORING_STYLE.md",
                    body,
                    f"{skill.name} must reference AUTHORING_STYLE.md in its"
                    " Authority line so the auditor loads it",
                )

    def test_each_audit_skill_has_style_check_block(self):
        for layer in registry_layers():
            artifact = layer["artifact"]
            skill = PLUGIN_SKILLS / f"doc-{artifact.lower()}-audit" / "SKILL.md"
            with self.subTest(layer=artifact):
                body = skill.read_text(encoding="utf-8")
                self.assertIn(
                    "Authoring-style check",
                    body,
                    f"{skill.name} must carry the Authoring-style check block"
                    " (Tier 2 → Tier 1 at threshold) in the Structural"
                    " Checklist",
                )


class ChgFamilyCitesStyleDoc(unittest.TestCase):
    """The CHG family (`doc-chg`, `doc-chg-audit`, `doc-chg-fixer`,
    `doc-chg-autopilot`) is a governance overlay alongside the 8 layer
    families and must apply the same authoring-style rule (AS5)."""

    CHG_SKILLS = ("doc-chg", "doc-chg-audit", "doc-chg-fixer", "doc-chg-autopilot")

    def test_every_chg_skill_references_style(self):
        for name in self.CHG_SKILLS:
            skill = PLUGIN_SKILLS / name / "SKILL.md"
            with self.subTest(skill=name):
                self.assertTrue(skill.is_file(), f"missing {skill}")
                self.assertIn(
                    "AUTHORING_STYLE.md",
                    skill.read_text(encoding="utf-8"),
                    f"{name}/SKILL.md must reference AUTHORING_STYLE.md",
                )

    def test_chg_audit_carries_style_check_block(self):
        skill = PLUGIN_SKILLS / "doc-chg-audit" / "SKILL.md"
        self.assertIn(
            "Authoring-style check",
            skill.read_text(encoding="utf-8"),
            "doc-chg-audit must carry the Authoring-style check block in the Structural Checklist",
        )


if __name__ == "__main__":
    unittest.main()
