"""Lint-catalog agreement guard (#715).

``framework/governance/LINT_RULES.md`` is the single source of truth for lint
rule IDs. This guard keeps it and the linters in sync, both directions:

* every ID the linters' ``CODES`` registries own (``CHG-L001``–``L015``,
  ``BGF-00``–``07``) appears in the catalog, and
* every catalogued table-row ID is grounded: emitted by ``sdd_doc_lint/``
  sources, an ``Alias of`` an emitted ID, or marked ``Reserved``.

Reserved rows are documented contracts with no machine check yet — the marker
is what stops a new unimplemented ID from slipping in unnoticed, and what
stops a reader from mistaking documentation for enforcement.
"""

import importlib.util
import re
import unittest

from _spec import FRAMEWORK, REPO_ROOT

CHG_LINT = REPO_ROOT / "sdd_doc_lint" / "chg_lint.py"
BUGFIX_LINT = REPO_ROOT / "sdd_doc_lint" / "bugfix_lint.py"
CATALOG = FRAMEWORK / "governance" / "LINT_RULES.md"
IMPL_DIRS = (REPO_ROOT / "sdd_doc_lint", REPO_ROOT / "hooks")

_ROW_ID = re.compile(r"^\| `([A-Z0-9][A-Z0-9-]*)` \|", re.MULTILINE)
_ID_TOKEN = re.compile(r"`([A-Z]{2,}(?:-[A-Z0-9]+)+|[A-Z]+[0-9]{2,}[A-Z0-9-]*)`")


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _catalog_text():
    return CATALOG.read_text(encoding="utf-8")


def _row_map():
    rows = {}
    for line in _catalog_text().splitlines():
        m = _ROW_ID.match(line)
        if m:
            rows.setdefault(m.group(1), line)
    return rows


def _impl_text():
    parts = []
    for base in IMPL_DIRS:
        for path in sorted(base.glob("*.py" if base.name != "hooks" else "*.sh")):
            if "__pycache__" in str(path) or "/tests/" in str(path):
                continue
            parts.append(path.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parts)


class LintCatalogAgreement(unittest.TestCase):
    def test_chg_codes_catalogued(self):
        """Every CHG-L ID the linter owns appears in LINT_RULES.md."""
        module = _load("chg_lint", CHG_LINT)
        self.assertEqual(
            set(module.CODES),
            {f"CHG-L{i:03d}" for i in range(1, 16)},
            "chg_lint owns exactly CHG-L001–L015",
        )
        catalog = _catalog_text()
        for code in sorted(module.CODES):
            with self.subTest(code=code):
                self.assertIn(f"`{code}`", catalog, f"{code} emitted but absent from LINT_RULES.md")

    def test_bgf_codes_catalogued(self):
        """Every BGF ID the bugfix linter owns appears in LINT_RULES.md."""
        module = _load("bugfix_lint", BUGFIX_LINT)
        self.assertEqual(
            set(module.CODES),
            {f"BGF-{i:02d}" for i in range(8)},
            "bugfix_lint owns exactly BGF-00–07",
        )
        catalog = _catalog_text()
        for code in sorted(module.CODES):
            with self.subTest(code=code):
                self.assertIn(f"`{code}`", catalog, f"{code} emitted but absent from LINT_RULES.md")

    def test_catalog_rows_grounded(self):
        """Every catalogued row ID is emitted, aliased, or reserved (#715)."""
        chg = _load("chg_lint", CHG_LINT)
        bgf = _load("bugfix_lint", BUGFIX_LINT)
        owned = set(chg.CODES) | set(bgf.CODES)
        impl = _impl_text()
        rows = _row_map()
        self.assertTrue(rows, "no rule rows parsed from LINT_RULES.md")
        for row_id, row in sorted(rows.items()):
            with self.subTest(row=row_id):
                if "reserved" in row.lower():
                    continue
                if row_id in owned or row_id in impl:
                    continue
                aliases = [t for t in _ID_TOKEN.findall(row) if t != row_id and t in impl]
                owned_aliases = [t for t in _ID_TOKEN.findall(row) if t != row_id and t in owned]
                self.assertTrue(
                    aliases or owned_aliases,
                    f"`{row_id}` catalogued but neither emitted, aliased to an "
                    "emitted ID, nor marked Reserved",
                )

    def test_reserved_rows_stay_marked(self):
        """The 18 known-unimplemented IDs keep their Reserved marker."""
        expected = (
            {f"TDD-SYNC-{c}" for c in "ABCDE"}
            | {"EVAL-001", "EVAL-002", "EVAL-003"}
            | {"EVAL-COV-001", "EVAL-COV-002", "EVAL-COV-003"}
            | {"IPLAN01", "REG01"}
            | {"GOV-008", "GOV-009", "GOV-010", "GOV-013", "GOV-015"}
        )
        rows = _row_map()
        for row_id in sorted(expected):
            with self.subTest(row=row_id):
                self.assertIn(row_id, rows, f"`{row_id}` vanished from the catalog")
                self.assertIn(
                    "reserved",
                    rows[row_id].lower(),
                    f"`{row_id}` lost its Reserved marker — implement a check "
                    "for it or keep it marked",
                )
