"""Conformance: the ADR ``alternatives`` block grades a named disqualifying
factor, and treats ``estimated_cost`` / ``fit`` as optional dimensions (GD-24).

Guards the fix for #602. The template used to mandate a cost estimate and a fit
rating on **every** alternative (``_antipatterns``: "FAIL: no cost estimate per
alternative"), while the normative authoring lens —
``framework/playbooks/05_ADR/architect.md`` check C2 — grades only that the
rejection reason names *the concrete factor that disqualified the option*, with
cost as one example beside latency, complexity and vendor lock-in. Authors
resolved the contradiction the way the template told them to: by inventing a
dollar figure for decisions that have no cost dimension, and by restating an
analysis that already existed elsewhere.

**Why the mandate rule is a normalized sentence scan, not a literal blocklist.**
The first draft of this guard listed the exact retired phrasings. Review killed
it on three counts, each of which this repo has been bitten by before: the
literals missed the live defect in ``doc-adr/SKILL.md`` (which said "cost, fit",
not "cost/fit"); one literal was a substring of the *sanctioned* replacement
text, held apart only by a capital letter, so lowercasing a correct line would
have reddened a required check; and a line break inside a phrase defeats any
literal, which is exactly how ``test_no_inprompt_hashing.py`` once passed a live
reintroduction. The rule below normalizes whitespace, splits into sentences, and
fails a sentence that ties a per-option quantifier to ``estimated_cost``/``fit``
without exempting it — so it survives rewording and reflow, and it reads the
*meaning* rather than one past edit's words.
"""

import re
import unittest

import yaml
from _spec import FRAMEWORK, REPO_ROOT

ADR_TEMPLATE = FRAMEWORK / "layers" / "05_ADR" / "ADR-TEMPLATE.yaml"
ARCHITECT_LENS = FRAMEWORK / "playbooks" / "05_ADR" / "architect.md"
TAG_SYNTAX = FRAMEWORK / "governance" / "TAG_SYNTAX.md"
GOVERNANCE_DECISIONS = FRAMEWORK / "governance" / "DECISIONS.md"

#: The retired template antipattern. Restoring it verbatim re-opens #602; the
#: sentence rule below catches the reworded restorations it cannot.
RETIRED_TEMPLATE_ANTIPATTERN = "no cost estimate per alternative"

#: A per-option quantifier, and one of the now-optional dimensions, co-occurring
#: in one sentence — in EITHER order. Order-directionality was a real bug in the
#: first version of this rule: written as quantifier-then-field, it missed both
#: "cost and fit required on each option" and "lacks estimated_cost … on each
#: option", which is exactly the reworded restoration the rule exists to catch.
#: Bare "cost" is deliberately excluded from the dimension set: the
#: rejection-reason sentence legitimately names cost as one example factor, and
#: matching it there would fail correct text.
_QUANTIFIER = re.compile(r"\b(each|every|all)\b|\bper[- ]option\b", re.IGNORECASE)
_DIMENSION = re.compile(
    r"estimated_cost|\bcost\s*/\s*fit\b|\bfit\b|\bcost\b\W+\bfit\b", re.IGNORECASE
)
#: Words that mark a sentence as *granting* the option rather than demanding it.
_EXEMPT = re.compile(r"\boptional\b|\bomit\b|\bconditional\b|\bwhere the decision\b", re.IGNORECASE)


def _sentences(text: str) -> list[str]:
    """Whitespace-normalized sentences, so a line break cannot hide a mandate."""
    return [s for s in re.split(r"(?<=[.;:])\s+", re.sub(r"\s+", " ", text)) if s.strip()]


def _mandating(text: str) -> list[str]:
    return [
        s
        for s in _sentences(text)
        if _QUANTIFIER.search(s) and _DIMENSION.search(s) and not _EXEMPT.search(s)
    ]


def _c2_block(text: str) -> str:
    """The body of architect.md check C2 alone.

    Scoping matters: ``disqualified it`` also appears in the lens's reasoning
    frame, so a whole-file search stays green while C2's actual requirement is
    deleted. Raises if C2 stops existing in the declared form, which is itself
    the assertion.
    """
    parts = re.split(r"^\*\*(C\d+) — ", text, flags=re.MULTILINE)
    blocks = dict(zip(parts[1::2], parts[2::2]))
    if "C2" not in blocks:
        raise AssertionError("architect.md declares no '**C2 — ' check — the template cites it")
    return blocks["C2"]


def _alternatives():
    return yaml.safe_load(ADR_TEMPLATE.read_text(encoding="utf-8"))["alternatives"]


class AlternativesTemplate(unittest.TestCase):
    """The `considered` block cites the seed and records a decision per option.

    Rewritten CLEANUP-001: the section stopped re-surveying (`options` with
    `pros`/`cons`/`estimated_cost`/`fit`/`rejection_reason`/`prior_analysis`)
    and now cites the seed (`considered` with `source: @seed:` + `decision:`).
    The #602-era assertions (per-option cost mandate, prior_analysis affordance)
    test a shape the template no longer has; what remains is the C2 agreement:
    ≥2 rejected alternatives, each with a decision rationale, a seed source,
    and guidance that defers analysis to the seed.
    """

    def setUp(self):
        self.alternatives = _alternatives()
        # Template key renamed `options` → `considered` when the section stopped
        # re-surveying and started citing the seed (CLEANUP-001: the rename
        # shipped without updating this guard).
        self.options = self.alternatives.get("options", self.alternatives.get("considered"))
        for opt in self.options:
            self.assertIsInstance(opt, dict, f"alternatives option is not a mapping: {opt!r}")

    def test_every_rejected_option_carries_a_decision(self):
        """architect.md C2 — each alternative names its fate and reason."""
        for opt in self.options:
            if opt.get("selected"):
                continue
            with self.subTest(option=opt.get("name")):
                decision = opt.get("decision") or opt.get("rejection_reason") or ""
                self.assertTrue(
                    decision,
                    f"non-selected option {opt.get('name')!r} carries no decision — "
                    "architect.md C2 grades exactly this",
                )

    def test_every_option_cites_its_source(self):
        """The seed-citation shape: no option without a source."""
        for opt in self.options:
            with self.subTest(option=opt.get("name")):
                self.assertTrue(
                    opt.get("source"),
                    f"option {opt.get('name')!r} carries no source — the section "
                    "cites the seed instead of re-surveying it",
                )

    def test_option_count_matches_what_the_lens_grades(self):
        """C2 needs ≥2 alternatives *beside* the chosen path; ``options`` includes it.

        The template's example block is the schema as far as an authoring agent is
        concerned, so a 2-entry example teaches a shape the lens P1s.
        """
        rejected = [o for o in self.options if not o.get("selected")]
        selected = [o for o in self.options if o.get("selected")]
        self.assertEqual(
            len(selected), 1, "the example block must show exactly one selected option"
        )
        self.assertGreaterEqual(
            len(rejected),
            2,
            "the example block shows fewer than 2 non-selected alternatives — architect.md C2 "
            "fails a single alternative, so the template would teach a shape the lens rejects",
        )

    def test_one_option_demonstrates_the_whole_shape(self):
        """The load-bearing assertion: seed-citation has to be *shown*, on one option.

        A rejected option carrying both `source` and `decision` is the worked
        example that teaches the shape. (Supersedes the #602-era demonstration
        of omitted cost/fit + prior_analysis, which tested the retired shape.)
        """
        demo = [
            o
            for o in self.options
            if not o.get("selected") and o.get("source") and o.get("decision")
        ]
        self.assertTrue(
            demo,
            "no rejected option demonstrates the seed-citation shape (source + decision) — "
            "without one worked example the template teaches nothing",
        )

    def test_guidance_defers_analysis_to_the_seed(self):
        """The regression vector the original defect actually used, re-aimed.

        `_guidance` once mandated per-option cost/fit; now it must keep saying
        the full analysis lives in the seed. A token check cannot tell a block
        that grants the deferral from one that revokes it.
        """
        guidance = self.alternatives["_guidance"]
        self.assertIn(
            "seed",
            guidance.lower(),
            "alternatives._guidance no longer defers analysis to the seed",
        )
        for sentence in _mandating(guidance):
            self.fail(
                f"alternatives._guidance re-mandates a per-option dimension: {sentence!r} "
                "— #602 / GD-24 make estimated_cost and fit optional"
            )

    def test_guidance_names_the_seed_source(self):
        guidance = self.alternatives["_guidance"]
        self.assertIn(
            "source",
            guidance.lower(),
            "alternatives._guidance never tells options to cite their source",
        )

    def test_antipatterns_forbid_duplicating_seed_analysis(self):
        joined = " ".join(self.alternatives["_antipatterns"])
        self.assertIn(
            "seed",
            joined.lower(),
            "_antipatterns no longer flags duplicating seed analysis — the failure "
            "the section exists to prevent",
        )
        for sentence in _mandating(joined):
            self.fail(
                f"_antipatterns re-mandates a per-option dimension: {sentence!r} — see #602 / GD-24"
            )
        self.assertNotIn(
            RETIRED_TEMPLATE_ANTIPATTERN,
            joined.lower(),
            f"_antipatterns restored the retired per-option cost mandate "
            f"({RETIRED_TEMPLATE_ANTIPATTERN!r}) — see #602 / GD-24",
        )

    def test_no_option_re_surveys_with_pros_cons(self):
        """The new shape forbids what the old shape required."""
        for opt in self.options:
            with self.subTest(option=opt.get("name")):
                for field in ("pros", "cons", "estimated_cost", "fit"):
                    self.assertNotIn(
                        field,
                        opt,
                        f"option {opt.get('name')!r} carries {field!r} — analysis "
                        "belongs in the seed, not the ADR",
                    )

    def test_seed_source_is_cited_not_resurveyed(self):
        """The affordance that lets an author cite the seed, not restate it."""
        guidance = self.alternatives["_guidance"]
        self.assertIn("seed", guidance.lower(), "the seed is undocumented")
        self.assertNotRegex(
            re.sub(r"\s+", " ", guidance),
            r"pros.*cons.*estimated cost.*fit rating",
            "the guidance reinstates the retired re-survey mandate",
        )


class SeedTagPremise(unittest.TestCase):
    """GD-24 declines `@seed:` on the ground that no such form is registered.

    If a future change registers one, the ADR guidance and GD-24 both become
    wrong — silently, since nothing else reads that premise.
    """

    def test_no_seed_tag_is_registered(self):
        self.assertNotIn(
            "@seed:",
            TAG_SYNTAX.read_text(encoding="utf-8"),
            "TAG_SYNTAX.md now registers an @seed: form — GD-24's declining rationale and "
            "ADR-TEMPLATE.yaml's alternatives guidance both need revisiting",
        )

    def test_gd24_is_recorded(self):
        self.assertIn(
            "## GD-24",
            GOVERNANCE_DECISIONS.read_text(encoding="utf-8"),
            "GD-24 is missing from framework/governance/DECISIONS.md — this module cites it "
            "in every failure message",
        )


class ArchitectLensAgreement(unittest.TestCase):
    def setUp(self):
        self.c2 = _c2_block(ARCHITECT_LENS.read_text(encoding="utf-8"))

    def test_c2_still_grades_the_named_factor(self):
        """The template now defers to C2; a silent C2 rewrite would strand it."""
        self.assertIn(
            "disqualified it",
            self.c2,
            "architect.md C2 no longer requires a rationale naming the factor that "
            "disqualified the option — ADR-TEMPLATE.yaml's alternatives guidance cites it",
        )

    def test_c2_grades_a_named_disqualifying_factor(self):
        """Both halves, or the template and the lens disagree.

        C2 grades a rationale naming the concrete disqualifying factor; the
        template's `decision: "Rejected — [one-line reason]"` is that rationale
        in seed-citation form. Without the factor requirement, the citation
        becomes a way to say nothing.
        """
        self.assertIn(
            "disqualified it",
            self.c2,
            "architect.md C2 no longer requires a rationale naming the factor that "
            "disqualified the option — ADR-TEMPLATE.yaml's alternatives guidance cites it",
        )
        self.assertRegex(
            re.sub(r"\s+", " ", self.c2),
            r"stub rationale",
            "architect.md C2 no longer fails a stub rationale — the citation becomes "
            "a way to say nothing",
        )

    def test_c2_does_not_reinstate_cost_as_a_required_field(self):
        for sentence in _mandating(self.c2):
            self.fail(f"architect.md C2 re-mandates a per-option dimension: {sentence!r}")


class PluginSkillAgreement(unittest.TestCase):
    """Retired with the platforms (CLEANUP-001): no doc-adr* skills exist."""

    def test_platform_skills_are_gone(self):
        self.assertFalse(
            (REPO_ROOT / "platforms").exists(),
            "platforms/ is back — resurrect the per-option mandate scan with it",
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
