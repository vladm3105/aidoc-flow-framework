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
]

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
            for lineno, line in _lines(path):
                for pattern in ENGINE_TOKENS:
                    if pattern.search(line):
                        rel = path.relative_to(FRAMEWORK)
                        violations.append(f"{rel}:{lineno}: {line.strip()}")
        self.assertEqual(violations, [], f"engine tokens in framework/: {violations}")


class VersionStringHygiene(unittest.TestCase):
    def test_no_framework_version_field(self):
        violations = []
        for path in framework_files():
            for lineno, line in _lines(path):
                if FRAMEWORK_VERSION.search(line):
                    violations.append(f"{path.relative_to(FRAMEWORK)}:{lineno}")
        self.assertEqual(violations, [], f"framework_version in framework/: {violations}")

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
