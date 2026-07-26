"""Conformance: the element-ID hash contract has ONE source, and every mandating layer states it.

D-0062 (PROVISIONAL-IDS-002 Phase 1) made a six-step **normalization transform**
normative for element-ID hash inputs and made
`governance/ID_NAMING_STANDARDS.md` its single source. Within the framework spec
that change originally reached exactly one surface (`BRD-TEMPLATE.yaml`); four
layer templates and three layer READMEs went on publishing the *pre*-normalization
input string, so anyone following a layer template computed a different hash than
`compute_element_hash()` does for the same content. TDD, meanwhile, published no
element-ID contract at all despite being one of six layers that MUST carry
element IDs.

This guard locks the shape of the fix (ELEMENT-ID-LAYER-CONTRACT-001, #343/#344):

  1. no file under `framework/layers/**` publishes the raw pre-normalization
     input string — the `norm()` form or nothing;
  2. each of the six element-ID-mandating layer templates declares the four
     `id_standard` keys AND cross-references `ID_NAMING_STANDARDS.md` rather
     than re-specifying the algorithm;
  3. each of the six mandating layer READMEs has an `## Element IDs` section;
  4. no template re-introduces `placeholder:` (#352 — the key matched neither of
     its two possible meanings, had no consumer, and was deleted).

**Scope is `framework/layers/**` only.** The 19 plugin/Hermes authoring surfaces
that also state a hash input are owned by #342 and are NOT covered here — a green
run of this file does not mean the repo is free of the drift class. #342 must add
its own lock.

The pairs below are a hardcoded list, deliberately NOT a glob: a glob sweeps in
`*-MVP-TEMPLATE.yaml`, `*-00_index.TEMPLATE.*`, and the `06_SPEC` / `08_IPLAN`
main templates + READMEs — the two documented element-ID exemptions
(`ID_NAMING_STANDARDS.md`), which correctly carry none of this.
"""

import unittest

from _spec import FRAMEWORK

# The six layers that MUST carry element IDs (ID_NAMING_STANDARDS.md).
# SPEC (06) and IPLAN (08) are the two documented exemptions and are excluded.
MANDATING_LAYERS = (
    ("01_BRD", "BRD-TEMPLATE.yaml"),
    ("02_PRD", "PRD-TEMPLATE.yaml"),
    ("03_EARS", "EARS-TEMPLATE.yaml"),
    ("04_BDD", "BDD-TEMPLATE.yaml"),
    ("05_ADR", "ADR-TEMPLATE.yaml"),
    ("07_TDD", "TDD-TEMPLATE.yaml"),
)

# The pre-normalization hash input. Its presence anywhere under framework/layers/
# means that surface disagrees with ID_NAMING_STANDARDS.md for any title or
# description containing uppercase or punctuation — i.e. nearly all of them.
RAW_INPUT = "{doc_id}:{section_id}:{title}:{description}"

# Keys every mandating layer template must declare. `placeholder` is deliberately
# absent: it was deleted in #352.
REQUIRED_ID_KEYS = (
    "format:",
    "hash_algorithm:",
    "hash_length:",
    "max_hash_length:",
)

AUTHORITY = "ID_NAMING_STANDARDS.md"


class ElementIdLayerContract(unittest.TestCase):
    def test_no_layer_surface_publishes_the_raw_hash_input(self):
        """The single-source property: layers cross-reference, never re-specify."""
        offenders = []
        for path in sorted(FRAMEWORK.glob("layers/**/*")):
            if not path.is_file() or path.suffix not in (".md", ".yaml"):
                continue
            text = path.read_text(encoding="utf-8")
            for lineno, line in enumerate(text.splitlines(), 1):
                if RAW_INPUT in line:
                    rel = path.relative_to(FRAMEWORK.parent)
                    offenders.append(f"{rel}:{lineno}")
        self.assertEqual(
            offenders,
            [],
            "these layer surfaces publish the PRE-normalization hash input "
            f"{RAW_INPUT!r}, which disagrees with governance/ID_NAMING_STANDARDS.md "
            "for any title/description with uppercase or punctuation. Delete the "
            "re-specified algorithm and cross-reference the standard instead "
            f"(see BRD-TEMPLATE.yaml for the pattern): {offenders}",
        )

    def test_mandating_templates_declare_the_id_keys_and_cite_the_authority(self):
        for layer, template in MANDATING_LAYERS:
            path = FRAMEWORK / "layers" / layer / template
            with self.subTest(layer=layer):
                self.assertTrue(path.is_file(), f"{path} is missing")
                text = path.read_text(encoding="utf-8")
                self.assertIn(
                    "id_standard:",
                    text,
                    f"{layer}/{template} declares no id_standard block, but {layer} "
                    "is one of the six layers that MUST carry element IDs",
                )
                for key in REQUIRED_ID_KEYS:
                    self.assertIn(
                        key,
                        text,
                        f"{layer}/{template} id_standard is missing {key!r}",
                    )
                self.assertIn(
                    AUTHORITY,
                    text,
                    f"{layer}/{template} does not cross-reference {AUTHORITY}; the "
                    "hash algorithm has exactly one source and each layer must "
                    "point at it rather than restate it",
                )

    def test_mandating_readmes_have_an_element_ids_section(self):
        for layer, _template in MANDATING_LAYERS:
            path = FRAMEWORK / "layers" / layer / "README.md"
            with self.subTest(layer=layer):
                self.assertTrue(path.is_file(), f"{path} is missing")
                text = path.read_text(encoding="utf-8")
                self.assertIn(
                    "## Element IDs",
                    text,
                    f"{layer}/README.md has no '## Element IDs' section, but {layer} "
                    "is one of the six layers that MUST carry element IDs. Its five "
                    "siblings each document the format and cite the standard.",
                )

    def test_no_template_reintroduces_the_placeholder_key(self):
        """#352 — `placeholder` matched neither possible meaning and had no consumer."""
        offenders = []
        for layer, template in MANDATING_LAYERS:
            path = FRAMEWORK / "layers" / layer / template
            if not path.is_file():
                continue
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if line.strip().startswith("placeholder:"):
                    offenders.append(f"{layer}/{template}:{lineno}")
        self.assertEqual(
            offenders,
            [],
            "the `placeholder` id_standard key was deleted in #352: it declared "
            '"0000" while every template body uses `.xxxx`, matched neither the '
            "template-notation nor the produced-document-provisional meaning, was "
            "defined nowhere in framework/governance/, and had no code consumer. "
            f"Do not re-introduce it: {offenders}",
        )


if __name__ == "__main__":
    unittest.main()
