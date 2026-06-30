"""Conformance: the 8 layer index/registry templates lint clean of structural errors.

`sdd_doc_lint` exempts index/registry docs (`<TYPE>-00_index`) from the
instance-doc structural checks — STRUCT01 (required sections) and the
trace-resolution skip. That exemption must fire for the *real* templates, not just
a synthetic fixture: the templates declare `artifact_type` under `custom_fields`
(some with a bare value) and the IPLAN registry is a `.yaml` with no `---`
frontmatter, so an exemption keyed only on top-level `artifact_type` silently
missed all 8 — a consumer copying a template into `docs/` then hit STRUCT01 errors.

This guard lints each real index template and asserts:
  * zero STRUCT01 (the exemption fires), and
  * zero `-INDEX`-token ID02 (the `<X>-INDEX` artifact-type marker is not itself
    reported as a malformed document id).

Regression for STRUCT01-INDEX-EXEMPTION (D-0043). It would FAIL on `main` before
the fix (STRUCT01 nonzero on every template).
"""

import sys
import unittest

from _spec import FRAMEWORK, REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "tools"))

from sdd_doc_lint import find_registry, lint_path  # noqa: E402

_REGISTRY = FRAMEWORK / "registry" / "LAYER_REGISTRY.yaml"


def _index_templates():
    """The 8 layer index/registry templates (`<TYPE>-00_index.TEMPLATE.{md,yaml}`)."""
    found = sorted(FRAMEWORK.glob("layers/0*/[A-Z]*-00_index.TEMPLATE.*"))
    return found


class IndexTemplateLint(unittest.TestCase):
    def test_all_eight_index_templates_present(self):
        templates = _index_templates()
        self.assertEqual(
            len(templates),
            8,
            f"expected 8 layer index templates, found {[p.name for p in templates]}",
        )

    def test_index_templates_emit_no_struct01_or_index_id02(self):
        registry = _REGISTRY if _REGISTRY.is_file() else find_registry()
        for template in _index_templates():
            with self.subTest(template=template.name):
                findings = lint_path(template, registry=registry)
                struct01 = [f for f in findings if f.code == "STRUCT01"]
                self.assertEqual(
                    struct01,
                    [],
                    f"{template.name}: index doc must be STRUCT01-exempt; got "
                    f"{[f.message for f in struct01]}",
                )
                index_id02 = [f for f in findings if f.code == "ID02" and "-INDEX'" in f.message]
                self.assertEqual(
                    index_id02,
                    [],
                    f"{template.name}: the -INDEX artifact-type marker must not be "
                    f"flagged as a malformed document id; got "
                    f"{[f.message for f in index_id02]}",
                )


if __name__ == "__main__":
    unittest.main()
