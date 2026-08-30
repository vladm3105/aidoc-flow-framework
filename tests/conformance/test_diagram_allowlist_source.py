"""Conformance: DG02's allowlist comes from the registry, and the registry is read.

`LAYER_REGISTRY.yaml` carries `c4_mapping[*].diagram_tags` and the registry's own
README calls itself the single source of truth — but **no code read that field**.
`DG02`'s real authority was a literal in `tools/sdd_doc_lint`, making the diagram
vocabulary a five-surface statement with the executable one last (#552).

That is the third instance of one shape this session: #565 (`extensions` is the
normative instance-format field and no linter reads it) and #531 (a granularity
rule stated in four places, executable in one). The pattern is a
machine-readable field that *looks* authoritative and is consumed by nothing.

`_diagram_allowed()` now reads the registry, with the literal kept only as a
fallback for an unreadable registry — the direction that fails safe, since an
empty allowlist makes `DG02` **reject** rather than accept.
"""

from __future__ import annotations

import sys
import unittest

import yaml
from _spec import FRAMEWORK, REGISTRY_PATH, REPO_ROOT

sys.path.insert(0, str(REPO_ROOT / "tools"))
from sdd_doc_lint import _DIAGRAM_ALLOWED, _check_diagram_level, _diagram_allowed  # noqa: E402

LAYERS = ("BRD", "PRD", "EARS", "BDD", "ADR", "SPEC", "TDD", "IPLAN")


class DiagramAllowlistComesFromTheRegistry(unittest.TestCase):
    def test_the_registry_declares_diagram_tags(self):
        """Guards the guard: with the field gone, every assertion below is vacuous.

        PER LAYER, deliberately. An `any(...)` over the whole mapping is satisfied
        for all eight layers by a single surviving entry, so a `c4_mapping` entry
        that stops naming its layer falls silently back to the in-code literal in
        `_diagram_allowed` — which is exactly the #552 state this module exists to
        prevent, reappearing invisibly to the module. Caught on OPS-0065 round 4.
        """
        data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
        mapping = data.get("c4_mapping")
        self.assertIsInstance(mapping, dict, "LAYER_REGISTRY.yaml lost its c4_mapping block")
        named = {
            artifact
            for e in mapping.values()
            if isinstance(e, dict) and "diagram_tags" in e
            for artifact in (e.get("artifacts") or ([e["artifact"]] if e.get("artifact") else []))
        }
        for layer in LAYERS:
            with self.subTest(layer=layer):
                self.assertIn(
                    layer,
                    named,
                    f"no c4_mapping entry declaring diagram_tags names {layer} — "
                    "DG02 would silently fall back to the in-code literal for it",
                )

    def test_every_layer_resolves_through_the_registry(self):
        for layer in LAYERS:
            with self.subTest(layer=layer):
                self.assertIsInstance(_diagram_allowed(layer), set)

    def test_registry_and_fallback_agree(self):
        """The consolidation invariant, and the reason this was safe to land.

        `sequence-*` is excluded from the comparison because `_DIAGRAM_SEQUENCE`
        allows it on **every** layer regardless of the allowlist — PRD's registry
        entry lists `sequence-sync`, which the literal omits, and the two are
        therefore equivalent in effect rather than identical in content.

        A divergence here is not automatically a defect: it means the registry
        and the fallback disagree, and whoever changed one must say which is
        right. Failing is how that decision gets made deliberately.
        """
        for layer in LAYERS:
            with self.subTest(layer=layer):
                from_registry = {
                    t for t in _diagram_allowed(layer) if not t.startswith("sequence-")
                }
                self.assertEqual(
                    from_registry,
                    _DIAGRAM_ALLOWED.get(layer, set()),
                    f"{layer}: registry diagram_tags and the in-code fallback disagree",
                )

    def test_the_value_actually_comes_from_the_registry_content(self):
        """Kills the mutant every other test in this module survives.

        Every assertion below/above compares `_diagram_allowed` against
        `_DIAGRAM_ALLOWED` -- the in-code literal -- so a `_diagram_allowed`
        that ignored the registry entirely and returned that literal would pass
        all of them. Measured: it does. That is the exact defect #552/GD-22
        claims to remove, so the module could not test its own thesis.

        This binds the return value to registry *content* by writing a registry
        whose `diagram_tags` deliberately DIFFER from the literal. It can only
        pass if the file was read and parsed.
        """
        import tempfile
        from pathlib import Path

        data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
        # c4_mapping is keyed by C4 LEVEL ("context", "container", ...), and each
        # entry names its SDD artifact -- so find BRD's entry rather than
        # indexing by artifact name, which raises KeyError.
        entry = next(
            (
                e
                for e in data["c4_mapping"].values()
                if isinstance(e, dict)
                and "BRD" in (e.get("artifacts") or ([e["artifact"]] if e.get("artifact") else []))
            ),
            None,
        )
        self.assertIsNotNone(
            entry, "no c4_mapping entry names BRD — the registry stopped declaring it"
        )
        entry["diagram_tags"] = ["@diagram: c4-l9", "@diagram: dfd-l9"]
        with tempfile.TemporaryDirectory() as td:
            alt = Path(td) / "LAYER_REGISTRY.yaml"
            alt.write_text(yaml.safe_dump(data), encoding="utf-8")
            got = _diagram_allowed("BRD", alt)
        self.assertEqual(
            {"c4-l9", "dfd-l9"},
            got,
            "`_diagram_allowed` did not read the registry it was handed -- it is "
            "returning the in-code literal, which is the defect GD-22 removes",
        )
        self.assertNotEqual(
            _DIAGRAM_ALLOWED["BRD"],
            got,
            "the fixture must differ from the literal or this assertion is vacuous",
        )

    def test_an_unreadable_registry_fails_closed(self):
        """Falls back to the literal, never to 'allow everything'.

        An allowlist that widens on error is the dangerous direction: DG02 would
        stop rejecting and the failure would be invisible.
        """
        from pathlib import Path

        self.assertEqual(
            _diagram_allowed("BRD", Path("/nonexistent/LAYER_REGISTRY.yaml")),
            _DIAGRAM_ALLOWED["BRD"],
        )


class Dg02VerdictTable(unittest.TestCase):
    """GD-22's behavioural claim, pinned.

    `_DIAGRAM_UNIVERSAL` is the entire executable content of GD-22, and it shipped
    with no conformance coverage: the tests above cover the *registry sourcing*
    half (#552) and never exercise `state-*` / `flow-*`. Both `DECISIONS.md` and
    the CHANGELOG present a four-row verdict table as "verified rather than
    asserted" — a one-time manual measurement with no regression guard behind it.
    Mutating `_DIAGRAM_UNIVERSAL` to `^(state|flow|c4)-` would have shipped green.
    Added on OPS-0065 review of the 0.47.0 combine.

    Asserts the CLASSIFICATION (does DG02 fire?) rather than a finding count, so
    a row cannot pass because the tag stopped being recognised as a tag at all.
    """

    #: (tag, artifact, should_be_rejected) — the table as published.
    CASES = (
        ("c4-l3", "EARS", True),
        ("c4-l3", "BRD", True),
        ("c4-l1", "BRD", False),
        ("state-lifecycle", "EARS", False),
        ("flow-approval", "EARS", False),
        ("sequence-sync", "EARS", False),
        ("bogus-kind", "EARS", True),
    )

    def _dg02(self, tag: str, artifact: str):
        return [
            f
            for f in _check_diagram_level(f"@diagram: {tag}\n", artifact, "X-01.md")
            if f.code == "DG02"
        ]

    def test_the_published_verdict_table_holds(self):
        for tag, artifact, rejected in self.CASES:
            with self.subTest(tag=tag, artifact=artifact):
                found = self._dg02(tag, artifact)
                self.assertEqual(
                    rejected,
                    bool(found),
                    f"{tag} on {artifact}: expected "
                    f"{'rejected' if rejected else 'accepted'}, got the opposite",
                )

    def test_a_universal_kind_is_accepted_on_every_layer(self):
        """The GD-22 claim proper: non-C4 kinds are layer-independent."""
        for artifact in LAYERS:
            for tag in ("state-lifecycle", "flow-approval"):
                with self.subTest(artifact=artifact, tag=tag):
                    self.assertEqual(
                        [],
                        self._dg02(tag, artifact),
                        f"{tag} rejected on {artifact} — GD-22 makes non-C4 kinds "
                        "valid on EVERY layer",
                    )

    def test_the_new_ears_and_bdd_slots_lint_clean_on_their_own_templates(self):
        """GD-22's other published claim: zero DG02 findings on the template itself."""
        for artifact, folder in (("EARS", "03_EARS"), ("BDD", "04_BDD")):
            path = FRAMEWORK / "layers" / folder / f"{artifact}-TEMPLATE.yaml"
            with self.subTest(artifact=artifact):
                self.assertIn("diagram:", path.read_text(encoding="utf-8"))
                self.assertEqual(
                    [],
                    [
                        f
                        for f in _check_diagram_level(
                            path.read_text(encoding="utf-8"), artifact, path.name
                        )
                        if f.code == "DG02"
                    ],
                )


class RegistryReachesLintPath(unittest.TestCase):
    """The `registry=` argument must actually reach `DG02`, not just `_diagram_allowed`.

    `DiagramAllowlistComesFromTheRegistry` above calls `_diagram_allowed` and
    `_check_diagram_level` **directly**, always passing a registry explicitly. The
    change #552 had to make was the WIRING — threading `registry` through
    `lint_text`'s call to `_check_diagram_level` — and no test goes through
    `lint_path`, the only caller that carries it.

    Measured on OPS-0065 round 4: dropping that argument SURVIVED the whole
    conformance tier. It is not an equivalent mutant — with it dropped, a
    caller-supplied registry is silently ignored and `find_registry()` (CWD-upward
    search, or `$SDD_REGISTRY`) wins instead.
    """

    _DOC = "---\ndoc_id: BRD-01\nartifact_type: BRD\n---\n\n@diagram: c4-l3\n"

    def _dg02_with(self, registry) -> set:
        import tempfile
        from pathlib import Path

        from sdd_doc_lint import lint_path

        with tempfile.TemporaryDirectory() as tmp:
            doc = Path(tmp) / "BRD-01.md"
            doc.write_text(self._DOC, encoding="utf-8")
            return {f.code for f in lint_path(doc, registry=registry) if f.code == "DG02"}

    def test_a_caller_supplied_registry_changes_the_dg02_verdict(self):
        import tempfile
        from pathlib import Path

        data = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
        entry = next(
            (
                e
                for e in data["c4_mapping"].values()
                if isinstance(e, dict)
                and "BRD" in (e.get("artifacts") or ([e["artifact"]] if e.get("artifact") else []))
            ),
            None,
        )
        self.assertIsNotNone(
            entry, "no c4_mapping entry names BRD — the registry stopped declaring it"
        )
        # Widen BRD to admit c4-l3, which the shipped registry rejects.
        entry["diagram_tags"] = ["@diagram: c4-l3"]

        with tempfile.TemporaryDirectory() as tmp:
            alt = Path(tmp) / "LAYER_REGISTRY.yaml"
            alt.write_text(yaml.safe_dump(data), encoding="utf-8")
            # Templates resolve relative to the registry; link the real tree so
            # STRUCT01 stays quiet and DG02 is the only thing under test.
            (Path(tmp) / "layers").symlink_to(FRAMEWORK / "layers")
            widened = self._dg02_with(alt)

        self.assertEqual(
            set(),
            widened,
            "a caller-supplied registry that ADMITS c4-l3 on BRD still produced DG02 — "
            "`registry` is not reaching `_check_diagram_level` through `lint_path`",
        )
        self.assertEqual(
            {"DG02"},
            self._dg02_with(None),
            "the shipped registry must still reject c4-l3 on BRD, or the assertion "
            "above passes for the wrong reason",
        )


if __name__ == "__main__":
    unittest.main()
