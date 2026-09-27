"""Conformance: ``framework/`` carries no engine-specific or stale tokens.

The spec must stay engine-agnostic — no platform names, MCP references, or
Claude Code skill names — and must not re-introduce version strings that the
migration deliberately neutralized.

This module scans ``framework/`` only. It must never scan ``tests/``, which
contains these token strings as literal search patterns.
"""

import re
import unittest

from _spec import FRAMEWORK, framework_files

# Engine-specific tokens that must not leak into the engine-agnostic spec.
# The SDD-tool pattern is verb-specific on purpose: the agnostic registry
# field `sdd_layer` must NOT be flagged.
ENGINE_TOKENS = [
    re.compile(r"hermes", re.IGNORECASE),
    re.compile(r"ucx_", re.IGNORECASE),
    re.compile(r"\.claude/"),
    re.compile(r"\bmcp\b", re.IGNORECASE),
    re.compile(r"mermaid-gen", re.IGNORECASE),
    re.compile(r"charts-flow", re.IGNORECASE),
    re.compile(
        r"sdd_(?:validate|create|score_validate|consistency|"
        r"preflight|next_action|review|remediate)",
        re.IGNORECASE,
    ),
    re.compile(r"\bplugin\b", re.IGNORECASE),
    re.compile(r"\bSKILL(?:\.md)?\b"),
    re.compile(
        r"\bdoc-(?:brd|prd|ears|bdd|adr|spec|tdd|iplan|chg|validator|ref|flow|naming"
        r"|autopilot|audit|fixer)\b",
        re.IGNORECASE,
    ),
]

# Allowlisted occurrences of engine tokens in framework/ (e.g. meta-governance or explicit illustrations)
ALLOWLISTED_TOKENS = {
    # Sanctioned Platform-B illustration in AIDOC.md
    ("docs/AIDOC.md", "plugin"),
    ("docs/AIDOC.md", "doc-"),
    ("docs/AIDOC.md", "doc-validator"),
    ("docs/AIDOC.md", "doc-ref"),
    ("docs/AIDOC.md", "doc-<layer>-autopilot"),
    ("docs/AIDOC.md", "doc-<layer>-audit"),
    ("docs/AIDOC.md", "doc-<layer>-fixer"),
    # GD-06 decision record naming neutralized tokens
    ("governance/DECISIONS.md", "plugin"),
    ("governance/DECISIONS.md", "skill"),
    ("governance/DECISIONS.md", "doc-"),
    ("governance/DECISIONS.md", "doc-*"),
    # Registry acceptance harness commentary note
    ("registry/LAYER_REGISTRY.yaml", "plugin"),
}

# `framework_version` is banned everywhere — the spec version lives in
# `framework/VERSION` (D-0006), not in per-file frontmatter.
FRAMEWORK_VERSION = re.compile(r"framework_version")

# Stale "SDD v3.x" version claims are banned — EXCEPT on the registry's
# sanctioned `derived_from:` provenance field, which intentionally records
# the historical origin of the spec.
SDD_V3 = re.compile(r"SDD v3", re.IGNORECASE)


def _lines(path):
    return enumerate(path.read_text(encoding="utf-8").splitlines(), start=1)


class EngineTokenHygiene(unittest.TestCase):
    def test_no_engine_tokens(self):
        violations = []
        for path in framework_files():
            rel = str(path.relative_to(FRAMEWORK))
            for lineno, line in _lines(path):
                for pattern in ENGINE_TOKENS:
                    if pattern.search(line):
                        # Check allowlist
                        allowlisted = False
                        for allow_path, allow_token in ALLOWLISTED_TOKENS:
                            if rel == allow_path and allow_token.lower() in line.lower():
                                allowlisted = True
                                break
                        # Owned skills surface (0.62.0): framework/skills/ ships
                        # the skill contract itself, so the SKILL filename token
                        # is the contract, not engine leakage. Other engine
                        # tokens remain banned there.
                        if not allowlisted and rel.startswith("skills/"):
                            if pattern.pattern.startswith(r"\bSKILL"):
                                allowlisted = True
                        if not allowlisted:
                            violations.append(f"{rel}:{lineno}: {line.strip()}")
        self.assertEqual(violations, [], f"engine tokens in framework/: {violations}")


class VersionStringHygiene(unittest.TestCase):
    def test_all_version_pins_equal_framework_version(self):
        """Every swept-form pin equals `framework/VERSION` exactly (#689).

        Replaces the retired skip-stub: `test_sync_version_refs.py` only
        asserts membership in OLD_VERSIONS (weaker), so a stale pin sails
        through. Scope mirrors `hooks/sync-version-refs.sh` (live tree only —
        `framework_files()` already excludes the frozen `archive/` snapshots).
        """
        current = (FRAMEWORK / "VERSION").read_text(encoding="utf-8").strip()
        forms = (
            re.compile(r'framework_spec_version: "(\d+\.\d+\.\d+)"'),
            re.compile(r'framework_version: "(\d+\.\d+\.\d+)"'),
            re.compile(r"\| Framework Version \| (\d+\.\d+\.\d+) \|"),
        )
        stale = []
        for path in framework_files():
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            rel = path.relative_to(FRAMEWORK)
            for pattern in forms:
                for version in pattern.findall(text):
                    if version != current:
                        stale.append(f"{rel}: {version} != {current}")
        self.assertEqual(stale, [], f"stale version pins: {stale}")

    def test_no_stale_sdd_v3_strings(self):
        violations = []
        for path in framework_files():
            for lineno, line in _lines(path):
                if SDD_V3.search(line) and "derived_from" not in line:
                    rel = path.relative_to(FRAMEWORK)
                    violations.append(f"{rel}:{lineno}: {line.strip()}")
        self.assertEqual(violations, [], f"stale SDD v3 strings: {violations}")


if __name__ == "__main__":
    unittest.main()
