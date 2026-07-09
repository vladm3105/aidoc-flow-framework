"""Conformance: plugin release docs and marketplace metadata match VERSION files."""

import json
import re
import unittest

from _spec import REPO_ROOT, framework_version

PLUGIN = REPO_ROOT / "platforms" / "claude-code-plugin"
PLUGIN_VERSION = PLUGIN / "VERSION"
PLUGIN_FSV = PLUGIN / "FRAMEWORK_SPEC_VERSION"
PLUGIN_README = PLUGIN / "README.md"
SKILL_AUTHORING = PLUGIN / "docs" / "SKILL_AUTHORING.md"
MARKETPLACE = REPO_ROOT / ".claude-plugin" / "marketplace.json"
ROOT_README = REPO_ROOT / "README.md"
PARITY_DOC = REPO_ROOT / "docs" / "PARITY.md"
TAGGING_DOC = REPO_ROOT / "docs" / "TAGGING.md"
PLUGIN_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "plugin.yml"
SIBLING_SKILL_REF = re.compile(r"\.\./([^/\s`]+)/SKILL\.md")
FRONTMATTER = re.compile(r"\A---\r?\n(?P<body>.*?)\r?\n---\r?\n", re.DOTALL)
ALLOWED_SKILL_CATEGORIES = {
    "automation-workflow",
    "core-workflow",
    "quality-assurance",
    "utility",
}

# Skills retained as deprecation stubs in v0.4.0. They are scheduled for
# removal in v0.5.0 and carry ``deprecated: true`` in their frontmatter.
DEPRECATED_SKILLS = {
    "doc-review",
    "trace-check",
}

EXPECTED_SKILLS = {
    # Layer families: base + autopilot + audit + fixer.
    *{
        f"doc-{layer}{suffix}"
        for layer in ("brd", "prd", "ears", "bdd", "adr", "spec", "tdd", "iplan")
        for suffix in ("", "-autopilot", "-audit", "-fixer")
    },
    # CHG governance overlay.
    "doc-chg",
    "doc-chg-autopilot",
    "doc-chg-audit",
    "doc-chg-fixer",
    # Utilities.
    "doc-flow",
    "doc-naming",
    "doc-ref",
    "doc-validator",
    "review-team",
    "project-init",
    "project-adopt",
    "project-profile",
    "knowledge-extractor",
    "gate-check",
    "charts-flow",
    "adr-roadmap",
    "quality-advisor",
    "security-audit",
    # Deprecated stubs (retained as redirects in v0.4.0).
    *DEPRECATED_SKILLS,
}


def _plugin_version() -> str:
    return PLUGIN_VERSION.read_text(encoding="utf-8").strip()


def _plugin_framework_spec_version() -> str:
    return PLUGIN_FSV.read_text(encoding="utf-8").strip()


def _frontmatter_field(path, field):
    match = FRONTMATTER.search(path.read_text(encoding="utf-8"))
    if not match:
        return None

    field_match = re.search(
        rf'(?m)^\s*{re.escape(field)}:\s*(?:"([^"]+)"|([^\s#]+))\s*(?:#.*)?$',
        match.group("body"),
    )
    if not field_match:
        return None
    return field_match.group(1) or field_match.group(2)


class PluginReleaseMetadata(unittest.TestCase):
    def test_plugin_readme_versions_match_declarations(self):
        version = _plugin_version()
        fsv = _plugin_framework_spec_version()
        text = PLUGIN_README.read_text(encoding="utf-8")

        self.assertIn(f"$ cat VERSION\n{version}", text)
        self.assertIn(f"$ cat FRAMEWORK_SPEC_VERSION\n{fsv}", text)
        self.assertIn(f"framework spec `{fsv}`", text)
        self.assertNotRegex(text, r"framework spec `0\.(?:[0-9])\.")

    def test_skill_authoring_defaults_match_declarations(self):
        version = _plugin_version()
        fsv = _plugin_framework_spec_version()
        text = SKILL_AUTHORING.read_text(encoding="utf-8")

        self.assertIn(f'version: "{version}"', text)
        self.assertIn(f'framework_spec_version: "{fsv}"', text)
        self.assertIn(f"currently `{version}`", text)

    def test_marketplace_version_matches_plugin_version(self):
        data = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
        plugins = data.get("plugins", [])
        entry = next((item for item in plugins if item.get("name") == "aidoc-flow"), None)
        self.assertIsNotNone(entry, "marketplace.json must list aidoc-flow")
        self.assertEqual(entry.get("version"), _plugin_version())

    def test_root_readme_plugin_release_matches_plugin_version(self):
        text = ROOT_README.read_text(encoding="utf-8")
        tag = f"claude-code-plugin/v{_plugin_version()}"
        self.assertIn(tag, text)

    def test_parity_doc_matches_plugin_release_inventory(self):
        text = PARITY_DOC.read_text(encoding="utf-8")
        self.assertIn(f"claude-code-plugin/v{_plugin_version()}", text)
        # v0.4.0 ships 52 skills total: 50 canonical active + 2 deprecated stubs.
        self.assertIn("52 (50 active + 2 deprecated)", text)
        self.assertNotIn("**54 skills** total", text)

    def test_tagging_doc_lists_current_plugin_release(self):
        text = TAGGING_DOC.read_text(encoding="utf-8")
        self.assertIn(f"claude-code-plugin/v{_plugin_version()}", text)
        # v0.4.0 ships 52 skills total: 50 canonical active + 2 deprecated stubs.
        self.assertIn("52 (50 active + 2 deprecated)", text)

    def test_framework_spec_declaration_matches_framework_version(self):
        # The plugin's FRAMEWORK_SPEC_VERSION must match the framework spec.
        # Bumped 0.15.1 → 0.15.2 for the framework/README.md Layout fix (PATCH:
        # doc clarification; any framework/** change trips GATE-SPEC-E005).
        self.assertEqual(_plugin_framework_spec_version(), framework_version())
        self.assertEqual(_plugin_framework_spec_version(), "0.35.2")

    def test_skill_inventory_matches_canonical_release_set(self):
        actual = {path.parent.name for path in (PLUGIN / "skills").glob("*/SKILL.md")}
        self.assertEqual(actual, EXPECTED_SKILLS)
        # 50 active canonical + 2 deprecated stubs = 52.
        self.assertEqual(len(actual), 52)

    def test_skill_metadata_versions_match_plugin_declarations(self):
        version = _plugin_version()
        fsv = _plugin_framework_spec_version()
        mismatches = []

        for path in sorted((PLUGIN / "skills").glob("*/SKILL.md")):
            actual_version = _frontmatter_field(path, "version")
            actual_fsv = _frontmatter_field(path, "framework_spec_version")
            if actual_version != version:
                mismatches.append(f"{path.relative_to(PLUGIN)} version={actual_version!r}")
            if actual_fsv != fsv:
                mismatches.append(
                    f"{path.relative_to(PLUGIN)} framework_spec_version={actual_fsv!r}"
                )

        self.assertFalse(
            mismatches,
            "skill metadata version drift:\n  " + "\n  ".join(mismatches[:50]),
        )

    def test_skill_categories_match_authoring_contract(self):
        bad_categories = []

        for path in sorted((PLUGIN / "skills").glob("*/SKILL.md")):
            category = _frontmatter_field(path, "skill_category")
            deprecated = _frontmatter_field(path, "deprecated")
            # Deprecated stub skills may omit or override the standard
            # category enum, but if they declare one it still must be allowed.
            if deprecated == "true" and category is None:
                continue
            if category not in ALLOWED_SKILL_CATEGORIES:
                bad_categories.append(f"{path.relative_to(PLUGIN)} skill_category={category!r}")

        self.assertFalse(
            bad_categories,
            "skill categories outside authoring contract:\n  " + "\n  ".join(bad_categories[:50]),
        )

    def test_deprecated_skills_carry_replacement_metadata(self):
        """Every deprecated stub must declare its replacement explicitly."""
        for name in DEPRECATED_SKILLS:
            skill_md = PLUGIN / "skills" / name / "SKILL.md"
            self.assertTrue(skill_md.exists(), f"missing deprecated stub: {name}")
            deprecated = _frontmatter_field(skill_md, "deprecated")
            replacement = _frontmatter_field(skill_md, "replacement")
            self.assertEqual(
                deprecated,
                "true",
                f"{name}: deprecated stub must declare deprecated: true",
            )
            self.assertIsNotNone(
                replacement,
                f"{name}: deprecated stub must declare replacement",
            )

    def test_plugin_workflow_checks_canonical_skill_count(self):
        text = PLUGIN_WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("-name SKILL.md", text)
        # v0.4.0: 50 canonical active + 2 deprecated stubs = 52.
        self.assertIn('"$skills" -ne 52', text)
        self.assertIn("canonical set of 52", text)

    def test_skill_cross_references_target_canonical_skills(self):
        bad_refs = []
        for path in sorted((PLUGIN / "skills").rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            for match in SIBLING_SKILL_REF.finditer(text):
                target = match.group(1)
                if "<" in target or ">" in target:
                    continue
                if target not in EXPECTED_SKILLS:
                    line = text.count("\n", 0, match.start()) + 1
                    bad_refs.append(f"{path.relative_to(PLUGIN)}:{line}: {target}")

        self.assertFalse(
            bad_refs,
            "skill references outside the canonical release set:\n  " + "\n  ".join(bad_refs[:25]),
        )


if __name__ == "__main__":
    unittest.main()
