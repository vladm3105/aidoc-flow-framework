"""Deterministic acceptance: _id_coordinator helpers work against committed goldens.

The smoke block exercises extract_elements + element_id so the helpers don't rot.
It does NOT reach write_registry(), which has no caller anywhere in the repo:
strict cross-layer ID closure is still deferred (see PLUGIN-TEST-SUITE-REVIEW.md
F2), because downstream goldens reference placeholder upstream IDs that don't
reproduce the upstream's actual element hashes.

The parity block below is NOT a smoke test — it is the guard that keeps
``element_hash()`` a delegation to the canonical ``compute_element_hash()``
instead of a second implementation of the ID_NAMING_STANDARDS transform
(IDCOORD-SECOND-HASH-IMPL, #351).
"""

import hashlib
import sys
import tempfile
import unicodedata
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _harness import FIXTURES_ROOT, fixtures_for, headings
from _id_coordinator import element_hash, element_id, extract_elements

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "conformance"))
from _spec import ARTIFACTS

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from sdd_doc_lint import compute_element_hash

#: Inputs chosen so each row exercises at least one step of the normalization
#: transform (ID_NAMING_STANDARDS "Normalization transform"): NFC → casefold →
#: strip to ``[a-z0-9 ]`` → collapse whitespace → trim → first 100 chars. A row
#: whose raw and normalized forms coincide would pass under any hash function and
#: so proves nothing; every row here differs pre/post transform.
PARITY_CASES = [
    ("casefold", "BRD-01", "07", "User Login", "Users Authenticate"),
    ("punctuation", "BRD-01", "07", "User Login (P1)", "Users authenticate; then land."),
    # Explicit escapes, NOT a literal precomposed character: "e" + U+0301
    # COMBINING ACUTE. This is the ONLY row exercising the NFC step, and it does
    # so only while the text stays decomposed. An editor or formatter that
    # precomposed a literal here would silently drop NFC coverage to zero with
    # every test still green — the row's casefold difference alone satisfies the
    # exercise-check below. Escapes cannot be normalized away in source, and
    # test_nfc_case_is_decomposed fails loudly if it happens regardless.
    ("nfc", "PRD-02", "03", "Caf\u0065\u0301 mode", "S\u0065\u0301lection d\u0065\u0301faut"),
    ("whitespace_runs", "EARS-01", "04", "Ubiquitous\t\trule", "When  X   then  Y"),
    ("leading_trailing", "BDD-01", "05", "  Scenario name  ", "\n Given a user \t"),
    ("truncation", "ADR-01", "02", "d" * 140, "e" * 250),
    ("all_steps", "SPEC-01", "06", "  API: /v1/Users — LIST  ", "Returns\tthe   User List."),
    ("empty_description", "TDD-01", "01", "Unit test", ""),
]


class ElementHashParityTests(unittest.TestCase):
    """``element_hash()`` must BE the canonical hash, not resemble it."""

    def test_element_hash_matches_canonical_prefix(self):
        for label, doc_id, section_id, title, description in PARITY_CASES:
            with self.subTest(case=label):
                self.assertEqual(
                    element_hash(doc_id, section_id, title, description),
                    compute_element_hash(doc_id, section_id, title, description)[:4],
                    f"{label}: _id_coordinator.element_hash diverged from "
                    "sdd_doc_lint.compute_element_hash",
                )

    def test_nfc_case_is_decomposed(self):
        """The NFC row must stay decomposed or it stops testing the NFC step.

        Only this row exercises NFC. If its text were precomposed, the row would
        still pass every other assertion in this file — including the
        exercise-check below, which its casefold difference satisfies on its own.
        Coverage of one normative transform step would vanish silently, which is
        the same failure mode that let the original divergence hide.
        """
        (case,) = [c for c in PARITY_CASES if c[0] == "nfc"]
        _, _, _, title, description = case
        for field in (title, description):
            self.assertFalse(
                unicodedata.is_normalized("NFC", field),
                f"{field!r} is already NFC-normalized — the nfc parity case no "
                "longer exercises the NFC step; restore the \\u0065\\u0301 escapes",
            )

    def test_parity_cases_actually_exercise_the_transform(self):
        """Guard the guard: every case must differ from its un-normalized form.

        If a case hashed the same with and without the transform, its parity
        assertion would hold under a wrong implementation too.
        """
        for label, doc_id, section_id, title, description in PARITY_CASES:
            with self.subTest(case=label):
                raw = f"{doc_id}:{section_id}:{title}:{description}"
                unnormalized = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:4]
                self.assertNotEqual(
                    unnormalized,
                    compute_element_hash(doc_id, section_id, title, description)[:4],
                    f"{label}: normalized and un-normalized hashes coincide — "
                    "this case cannot detect a missing transform",
                )


class IdCoordinatorSmokeTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)

    def test_element_hash_is_deterministic(self):
        a = element_hash("BRD-01", "project_scope", "Scope", "In: A; Out: B")
        b = element_hash("BRD-01", "project_scope", "Scope", "In: A; Out: B")
        self.assertEqual(a, b)
        self.assertEqual(len(a), 4)
        self.assertRegex(a, r"^[0-9a-f]{4}$")

    def test_element_id_format(self):
        eid = element_id("BRD", 1, "project_scope", "Scope", "desc")
        self.assertRegex(eid, r"^BRD\.01\.project_scope\.[0-9a-f]{4}$")

    def test_element_hash_changes_with_inputs(self):
        a = element_hash("BRD-01", "s", "t", "d")
        b = element_hash("BRD-01", "s", "t", "DIFFERENT")
        self.assertNotEqual(a, b)

    def test_extract_elements_runs_on_each_layer_golden(self):
        """Smoke: extract_elements() must not raise for any committed golden.

        Returns a list (possibly empty) of dicts with the documented keys.
        Empty is acceptable here — many goldens use ## H2 sections without
        ### H3 sub-elements, which extract_elements treats as zero elements.
        """
        for idx, name in enumerate(ARTIFACTS, start=1):
            with self.subTest(layer=name):
                valid_dir = fixtures_for(idx, "valid")
                goldens = list(valid_dir.glob(f"{name}-01_golden.*"))
                self.assertEqual(
                    len(goldens), 1, f"expected 1 golden for {name}, got {len(goldens)}"
                )
                elements = extract_elements(goldens[0])
                self.assertIsInstance(elements, list)
                for elem in elements:
                    self.assertIn("section_id", elem)
                    self.assertIn("title", elem)
                    self.assertIn("description", elem)
                    self.assertIn("element_id", elem)
                    self.assertRegex(elem["element_id"], rf"^{name}\.\d+\.\w+\.[0-9a-f]{{4}}$")

    def test_extract_elements_runs_on_every_fullpath_golden(self):
        """Regression: multi-document YAML goldens must not crash the extractor.

        The layer-tier test above walks ``layer_NN_<name>/valid/`` only, which is
        why the ``ComposerError`` on the three ``fullpath/golden_chain`` YAML
        goldens — each carrying a ``---`` frontmatter fence plus a body, i.e. two
        YAML documents — stayed invisible. Walking ``fullpath/`` closes that gap.

        Three FURTHER multi-document goldens sit under ``layer_07_tdd/valid/`` and
        ``layer_08_iplan/valid/`` as upstream companions; the per-layer glob above
        (``{name}-01_golden.*``) does not reach them. Not a second code path —
        there is one extractor, exercised here — but do not read "3
        multi-document goldens" as a count of the whole fixture tree.
        """
        # Scoped to goldens: an rglob over every .md/.yaml would also count
        # `*_drift_codes.yaml` manifests, so adding a broken fixture the
        # documented way would fail this for reasons unrelated to element IDs.
        artifacts = sorted((FIXTURES_ROOT / "fullpath").rglob("*_golden.*"))
        self.assertEqual(len(artifacts), 16, "fullpath golden set changed shape")
        multi_doc_seen = 0
        for artifact in artifacts:
            with self.subTest(artifact=str(artifact.relative_to(FIXTURES_ROOT))):
                elements = extract_elements(artifact)
                self.assertIsInstance(elements, list)
                for elem in elements:
                    self.assertIn("section_id", elem)
                    self.assertIn("title", elem)
                    self.assertIn("description", elem)
                    self.assertRegex(elem["element_id"], r"^[A-Z]+\.\d+\.\w+\.[0-9a-f]{4}$")
                if artifact.suffix != ".yaml":
                    continue
                # Body sections per _harness.headings(), which strips the
                # optional frontmatter fence independently of the extractor.
                # NB: this holds under a key-union merge too, because today's
                # frontmatter is only `doc_id` (scalar) + `metadata` (filtered).
                # The case that actually discriminates is synthesised in
                # test_frontmatter_dict_is_not_walked_as_a_section.
                body_sections = set(headings(artifact))
                for elem in elements:
                    self.assertIn(elem["section_id"], body_sections)
                # A *leading* `---` is only a document-start marker; what
                # crashed safe_load is a second document, i.e. a closing
                # frontmatter fence. Count documents rather than guessing
                # from the first line.
                documents = list(yaml.safe_load_all(artifact.read_text(encoding="utf-8")))
                if len(documents) > 1:
                    multi_doc_seen += 1
                    self.assertGreater(
                        len(elements),
                        0,
                        f"{artifact.name}: multi-document golden yielded no "
                        "elements — the body document was not parsed",
                    )
        # >= rather than ==: this exists to prove the regression scenario is
        # actually present in the corpus, so zero must fail. Adding a fourth
        # multi-document golden is a good change and must not fail.
        self.assertGreaterEqual(
            multi_doc_seen, 3, "expected >= 3 multi-document YAML goldens under fullpath/"
        )

    def test_frontmatter_keys_are_not_walked_as_sections(self):
        """Elements come from the body document only, never the frontmatter.

        **The committed corpus cannot test this**, which is the whole reason it
        is synthesised. Today's frontmatter is `doc_id` (scalar → skipped) plus
        `metadata` (filtered by name), and the one first-class frontmatter block
        the spec defines — `reuse:` (D-0041, TRACEABILITY.md:141) — is a flat
        dict of scalars, so it mints nothing either. Over that corpus,
        last-document-wins and a key-union merge are indistinguishable; both pass
        every other test in this file.

        The shape that separates them is a frontmatter key whose value is a
        mapping of mappings (or a list of mappings) — the extractor's own
        criterion for a section worth walking. No current frontmatter has that
        shape; this pins the contract before one does.
        """
        artifact = Path(self.tmpdir.name) / "SPEC-01_golden.yaml"
        artifact.write_text(
            "---\n"
            "doc_id: SPEC-01\n"
            "metadata:\n"
            "  artifact_id: SPEC-01\n"
            "overrides:\n"
            "  authservice:\n"
            "    title: Overridden component\n"
            "    description: Frontmatter, so it must never become an element\n"
            "---\n"
            "\n"
            "interfaces:\n"
            "  - name: AuthService\n"
            "    description: Issues tokens\n",
            encoding="utf-8",
        )
        sections = {elem["section_id"] for elem in extract_elements(artifact)}
        self.assertEqual(
            sections,
            {"interfaces"},
            "frontmatter keys leaked into the section namespace — extract_elements "
            "must take the body document, not merge the two key sets",
        )

    def test_registry_path_present(self):
        registry = FIXTURES_ROOT / "fullpath" / "ID_REGISTRY.yaml"
        self.assertTrue(registry.exists(), "ID_REGISTRY.yaml missing")


if __name__ == "__main__":
    unittest.main()
