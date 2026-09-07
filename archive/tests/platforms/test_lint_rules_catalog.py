"""Conformance: every rule ID the reference linter can emit is documented in the
spec's lint-rule catalog (``framework/governance/LINT_RULES.md``).

The catalog is the normative list of deterministic lint rules so a user (or a
second platform) can look up any code the linter prints. This guard extracts the
rule codes emitted by ``sdd_doc_lint`` (the ``Finding(...)`` code argument and
``code=`` keyword) and asserts each appears as a catalog row (FRWK-REVIEW-002 D2).
"""

import ast
import re
import unittest

from _spec import REPO_ROOT

LINT_SRC = REPO_ROOT / "tools" / "sdd_doc_lint"
CATALOG = REPO_ROOT / "framework" / "governance" / "LINT_RULES.md"

# A rule ID: uppercase letters/digits, optional hyphenated segments
# (e.g. TH01, COV02, BDD-SCHEMA-001, TH-RES-001).
_RULE_ID = re.compile(r"^[A-Z]{2,}(?:-[A-Z]+)*-?\d{2,3}$|^[A-Z]{2,}\d{2}$")


def _emitted_codes() -> set[str]:
    """AST-enumerate every rule code the linter emits: the 3rd positional
    argument of ``Finding(...)`` and any ``code="..."`` keyword. Walking the AST
    (rather than a line heuristic) catches codes on a continuation line — the
    line-based approach silently missed `PH01` (FRWK-REVIEW-002 D2 / L1)."""
    codes: set[str] = set()

    def _add(node: ast.AST) -> None:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if _RULE_ID.match(node.value):
                codes.add(node.value)

    for py in LINT_SRC.glob("*.py"):
        tree = ast.parse(py.read_text(encoding="utf-8"))
        for call in ast.walk(tree):
            if not isinstance(call, ast.Call):
                continue
            func = call.func
            name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
            if name == "Finding" and len(call.args) >= 3:
                _add(call.args[2])
            for kw in call.keywords:
                if kw.arg == "code":
                    _add(kw.value)
    return codes


class LintRulesCatalog(unittest.TestCase):
    def test_catalog_exists(self):
        self.assertTrue(CATALOG.is_file(), "framework/governance/LINT_RULES.md is missing")

    def test_every_emitted_rule_is_catalogued(self):
        catalog_text = CATALOG.read_text(encoding="utf-8")
        catalogued = set(re.findall(r"`([A-Z][A-Z0-9-]+)`", catalog_text))
        missing = sorted(c for c in _emitted_codes() if c not in catalogued)
        self.assertEqual(
            missing,
            [],
            f"lint rule IDs emitted by sdd_doc_lint but absent from LINT_RULES.md: {missing}",
        )
