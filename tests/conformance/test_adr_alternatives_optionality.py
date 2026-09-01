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
PLUGIN_SKILLS = REPO_ROOT / "platforms" / "claude-code-plugin" / "skills"

#: Every plugin skill that authors, drives or audits an ADR. Globbed rather than
#: listed: a new ``doc-adr-*`` skill inherits the rule instead of silently
#: escaping it, which is how ``doc-adr-fixer`` — the surface that writes patches
#: *into* ADRs — was outside the first draft's hardcoded roster.
ADR_SKILL_GLOB = "doc-adr*/SKILL.md"
EXPECTED_ADR_SKILLS = 4

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
    def setUp(self):
        self.alternatives = _alternatives()
        self.options = self.alternatives["options"]
        for opt in self.options:
            self.assertIsInstance(opt, dict, f"alternatives option is not a mapping: {opt!r}")

    def test_every_rejected_option_carries_a_rejection_reason(self):
        """architect.md C2 — the one thing the section genuinely requires."""
        for opt in self.options:
            if opt.get("selected"):
                continue
            with self.subTest(option=opt.get("name")):
                reason = opt.get("rejection_reason") or ""
                self.assertTrue(
                    reason,
                    f"non-selected option {opt.get('name')!r} carries no rejection_reason "
                    "— architect.md C2 grades exactly this",
                )
                # The placeholder must keep *saying* what C2 grades. A revert to a
                # bare "[Why not selected]" is the stub rationale C2 fails, and the
                # template would be teaching it.
                self.assertIn(
                    "concrete disqualifying factor",
                    reason,
                    f"the rejection_reason placeholder on {opt.get('name')!r} no longer tells "
                    "the author to name the concrete disqualifying factor",
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
        """The load-bearing assertion: optionality has to be *shown*, on one option.

        Prose calling a field optional beside three examples that all carry it
        teaches the mandate. Requiring the demonstration to be a rejected option
        that also cites ``prior_analysis`` stops it decomposing into two half
        examples, or being satisfied by an appended filler entry.
        """
        demo = [
            o
            for o in self.options
            if not o.get("selected")
            and "estimated_cost" not in o
            and "fit" not in o
            and o.get("rejection_reason")
            and o.get("prior_analysis")
        ]
        self.assertTrue(
            demo,
            "no option demonstrates the complete GD-24 shape (rejected, estimated_cost and fit "
            "both omitted, an existing survey cited in prior_analysis rather than restated) — "
            "without one worked example the template teaches the mandate #602 removed",
        )

    def test_guidance_never_mandates_a_per_option_dimension(self):
        """The regression vector the original defect actually used.

        ``_guidance`` is where "Each must have pros, cons, estimated cost, and fit
        rating" lived. A token check ("does OPTIONAL appear anywhere?") cannot tell
        a block that grants the option from one that revokes it.
        """
        for sentence in _mandating(self.alternatives["_guidance"]):
            self.fail(
                f"alternatives._guidance re-mandates a per-option dimension: {sentence!r} "
                "— #602 / GD-24 make estimated_cost and fit optional"
            )

    def test_guidance_grants_the_optionality_by_name(self):
        guidance = self.alternatives["_guidance"]
        for field in ("estimated_cost", "fit"):
            with self.subTest(field=field):
                granted = [s for s in _sentences(guidance) if field in s and _EXEMPT.search(s)]
                self.assertTrue(
                    granted,
                    f"alternatives._guidance never says {field!r} may be omitted",
                )

    def test_antipatterns_grade_the_named_factor_not_the_cost_field(self):
        joined = " ".join(self.alternatives["_antipatterns"])
        self.assertIn(
            "concrete disqualifying factor",
            joined.lower(),
            "_antipatterns does not flag a rejection reason that names no concrete "
            "factor — the failure architect.md C2 actually grades",
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

    def test_prior_analysis_is_offered_and_bounded(self):
        """The affordance that lets an author cite an existing survey, not restate it."""
        self.assertTrue(
            any("prior_analysis" in opt for opt in self.options),
            "no option demonstrates prior_analysis — authors have no worked example",
        )
        guidance = self.alternatives["_guidance"]
        self.assertIn("prior_analysis", guidance, "prior_analysis is undocumented")
        self.assertRegex(
            re.sub(r"\s+", " ", guidance),
            r"prior_analysis[^.]{0,120}(PROSE|prose)",
            "the guidance no longer says prior_analysis is prose",
        )
        self.assertRegex(
            re.sub(r"\s+", " ", guidance),
            r"NO `@`-tag|no `@`-tag|carries NO @-tag",
            "the guidance no longer forbids an @-tag inside prior_analysis — the linter's tag "
            "scanner is document-global, so one written there becomes a real trace edge",
        )

    def test_no_option_writes_a_trace_tag_in_prior_analysis(self):
        """Guard the template's own example against the leak it warns about."""
        for opt in self.options:
            with self.subTest(option=opt.get("name")):
                self.assertNotRegex(
                    str(opt.get("prior_analysis", "")),
                    r"@(brd|prd|ears|bdd|adr|spec|tdd|iplan)\s*:",
                    "prior_analysis carries an @-tag; the linter reads it as lineage",
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

    def test_c2_admits_a_cited_survey_without_opening_a_loophole(self):
        """Both halves, or the template and the lens disagree.

        Without the first, an author who follows the template — compress the
        rationale, cite the survey — takes a P1 for doing so. Without the second,
        the compression becomes a way to say nothing.
        """
        self.assertIn(
            "prior_analysis",
            self.c2,
            "architect.md C2 does not admit the template's prior_analysis citation — "
            "an ADR authored to the template would take a P1 for doing so",
        )
        self.assertRegex(
            re.sub(r"\s+", " ", self.c2),
            r"citation[^.]{0,80}named factor[^.]{0,40}stub",
            "architect.md C2 no longer closes the citation loophole (a citation naming no "
            "factor is still a stub) — the compression becomes a way to say nothing",
        )

    def test_c2_does_not_reinstate_cost_as_a_required_field(self):
        for sentence in _mandating(self.c2):
            self.fail(f"architect.md C2 re-mandates a per-option dimension: {sentence!r}")


class PluginSkillAgreement(unittest.TestCase):
    def setUp(self):
        self.skills = sorted(PLUGIN_SKILLS.glob(ADR_SKILL_GLOB))

    def test_roster_is_complete(self):
        self.assertEqual(
            len(self.skills),
            EXPECTED_ADR_SKILLS,
            f"the doc-adr* skill roster changed ({[s.parent.name for s in self.skills]}) — "
            "review the per-option mandate rule against the new surface, then update the count",
        )

    def test_no_adr_skill_mandates_a_per_option_dimension(self):
        for skill in self.skills:
            text = skill.read_text(encoding="utf-8")
            for sentence in _mandating(text):
                with self.subTest(skill=skill.parent.name):
                    self.fail(
                        f"{skill.relative_to(REPO_ROOT)} mandates a per-option dimension: "
                        f"{sentence!r} — it contradicts ADR-TEMPLATE.yaml (#602 / GD-24)"
                    )

    def test_audit_skill_grades_the_named_factor(self):
        text = (PLUGIN_SKILLS / "doc-adr-audit" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn(
            "disqualifying factor",
            text,
            "doc-adr-audit no longer grades the named disqualifying factor — an ADR "
            "authored to the current template would fail an audit it should pass",
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
