"""Conformance: the document-level-permitted set is ``{SPEC, IPLAN}`` everywhere it is stated.

GD-03 ratified that an ``@<layer>:`` trace citation to an element-declaring
layer MUST be element-level, which leaves SPEC and IPLAN as the only layers a
trace citation may name at document level. That proposition is stated in four
places and, until this module, measured in none — between 2026-06-27 and
2026-08-23 two of the statements said the opposite and nothing noticed (#531).

See ``DocumentLevelPermittedParity`` for what is and is not covered.
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

from _spec import ARTIFACTS, FRAMEWORK, REPO_ROOT

# The linter constant is the authority, so it is imported rather than parsed out
# of the source: an import has no ``Unparseable`` failure mode, and it survives
# both a ``ruff-format`` reflow of the tuple and a type annotation on the
# assignment. Established pattern — see
# ``tests/conformance/platforms/test_realizing_layers_registry.py`` and
# ``tests/conformance/test_acceptance_pairing.py``.
sys.path.insert(0, str(REPO_ROOT / "tools"))
from sdd_doc_lint import _REFGRAN_ELEMENT_DECLARING  # noqa: E402

GOVERNANCE = FRAMEWORK / "governance"
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "refgran"

# Never a fresh literal: re-stating the layer list here would make this guard a
# fifth unguarded statement of it.
LAYERS = frozenset(ARTIFACTS)

EXPECTED_PERMITTED = frozenset({"SPEC", "IPLAN"})

_LAYER = re.compile(r"\b(BRD|PRD|EARS|BDD|ADR|SPEC|TDD|IPLAN)\b")
_TAG = re.compile(r"@(brd|prd|ears|bdd|adr|spec|tdd|iplan)\b")


class Unparseable(Exception):
    """A surface's anchor did not match, so no set could be read from it.

    Raised — never swallowed into an empty set. A failed parse and a surface
    stating the wrong set are different defects with opposite remedies, and an
    empty set silently reads as "no layer is document-level permitted", which no
    surface has ever said. Treating one as the other is how a regression fixture
    comes to stand as evidence of a detection that never happened.
    """


# --------------------------------------------------------------------------
# Extractors — one per prose surface. Each is anchored on the *permit* clause.
# --------------------------------------------------------------------------


def extract_tag_syntax(text: str) -> set:
    """The Form-cell-scoped read of ``TAG_SYNTAX.md``'s granularity table.

    Two scoping rules, and **both** were established by a mutation that the
    first draft of this extractor failed:

    * *Cell.* The element row's *Why* cell contains the word "document"
      ("functionality is defined in the element, not the document"), so a
      row-level read yields all eight layers on correct text.
    * *Table.* The file carries a **second** pipe table — the necessary-upstream
      tags at ``TAG_SYNTAX.md:87-95`` — and an extractor that collects every
      pipe row to EOF reads its rows too. Two of them already carry the string
      "doc-level" one cell away from the one this reads
      (``| TDD | … | @spec: SPEC-01 (doc-level — SPEC exempt) |``), so the
      benign margin is one cell wide. Measured: moving that parenthetical into
      the second cell makes a *file*-scoped extractor return
      ``{SPEC, IPLAN, TDD}`` and report correct text as drift.
    """
    lines = text.splitlines()
    header = next(
        (
            i
            for i, ln in enumerate(lines)
            if ln.startswith("|") and "Target layer" in ln and "Form" in ln
        ),
        None,
    )
    if header is None:
        raise Unparseable("TAG_SYNTAX.md: no '| Target layer | Form | Why |' table header")

    # Stop at the first non-pipe line: a GFM table ends at a blank line, so this
    # cannot run on into the next table.
    body = []
    for ln in lines[header + 1 :]:
        if not ln.startswith("|"):
            break
        if set(ln) <= set("|- :"):
            continue
        body.append(ln)
    if not body:
        raise Unparseable("TAG_SYNTAX.md: granularity table has no data rows")

    permitted: set = set()
    for row in body:
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if len(cells) < 2:
            raise Unparseable(f"TAG_SYNTAX.md: malformed table row: {row!r}")
        target, form = cells[0], cells[1]
        if "document" in form.lower():
            permitted |= {m.group(1) for m in _LAYER.finditer(target)}
    if not permitted:
        # The empty set is never an answer here. Rewording the Form cell from
        # "**document**" to "**doc**" would otherwise report
        # "set() != {SPEC, IPLAN}" under the disagreement message — the exact
        # inversion ``Unparseable`` exists to prevent, and the first draft of
        # this extractor shipped it while the other two guarded against it.
        raise Unparseable(
            "TAG_SYNTAX.md: granularity table names no document-level row "
            "(the Form cell no longer says 'document')"
        )
    return permitted


def _bullets(section: str) -> list:
    """Top-level ``- `` bullets, each joined across its continuation lines.

    Joining matters: the section is split by a ``**Derivable Principle:**``
    lead-in and a blank line, so a naive per-block split does not yield the
    six bullets the section actually has.
    """
    out: list = []
    for line in section.splitlines():
        if line.startswith("- "):
            out.append(line)
        elif out and line.strip() and (line.startswith("  ") or line.startswith("\t")):
            out[-1] += " " + line.strip()
    return out


# A bullet is read only if it explicitly *permits*. The whitelist, not a
# blacklist: a forbid-marker filter alone admits the BDD-carrier bullet, which
# names @ears/@bdd and permits nothing.
_PERMIT = (
    "document-level permitted",
    "are **document-level**",
    "is **document-level**",
)
_EXEMPTION = "**Self-tags**"
_SUBJECT = re.compile(r"^-\s+\*\*(.+?)\*\*")


def _permit_subject(bullet: str) -> str:
    """The text a permit phrase attaches to: its own sentence, up to the phrase.

    The permit phrase is a **predicate** ("… are **document-level**"), so the
    layers it grants are its grammatical subject and precede it. Reading the
    whole bullet — or even the whole sentence — instead was a measured false
    positive: appending the entirely correct clarification "(unlike ``@adr:``
    and ``@tdd:``, which must be element-level)" to the ``@spec:``/``@iplan:``
    bullet made the extractor return ``{SPEC, IPLAN, ADR, TDD}`` and report
    correct text as drift.

    Sentence-bounded first, so that a permit in one sentence cannot claim a
    subject from an earlier one. Returns the whole bullet when no permit phrase
    is present, which keeps the function total rather than empty — callers gate
    on ``_permits`` first.
    """
    for sentence in re.split(r"(?<=\.)\s+", bullet):
        for phrase in _PERMIT:
            index = sentence.find(phrase)
            if index != -1:
                return sentence[:index]
    return bullet


def _permits(bullet: str) -> bool:
    if _EXEMPTION in bullet:
        return False
    return any(phrase in bullet for phrase in _PERMIT)


def id_naming_bullets(text: str) -> list:
    start = text.find("### Reference granularity")
    if start == -1:
        raise Unparseable("ID_NAMING_STANDARDS.md: no '### Reference granularity' heading")
    rest = text[start + 1 :]
    end = rest.find("\n### ")
    section = rest if end == -1 else rest[:end]
    bullets = _bullets(section)
    if not bullets:
        raise Unparseable("ID_NAMING_STANDARDS.md: '### Reference granularity' has no bullets")
    return bullets


def extract_id_naming(text: str) -> set:
    """The permit-classified read of ``ID_NAMING_STANDARDS.md``'s bullets.

    **A permit phrase outranks a forbid marker in the same bullet**, and the
    names are then taken from the bullet's *bolded subject* plus its ``@tag``
    tokens — never from the bullet body.

    Both halves are load-bearing and both were established by mutation:

    * *Permit-over-forbid.* The "Design & realization layers" bullet carries a
      permit phrase **and** a forbid sentence ("Citing an element-declaring
      layer … remains element-level"), so a forbid-first classifier skips it.
      A re-drift adding ``ADR / TDD`` back to its bolded subject while leaving
      the forbid sentence intact survives forbid-first and is killed here.

      **Note precisely what does and does not establish this.** The *drift
      fixture* does not: its version of the bullet carries no forbid sentence
      at all (that sentence arrived with the #530 correction), so a forbid-first
      classifier reads the fixture correctly and passes the regression. The
      rule is established solely by
      ``MutationLocks.test_permit_outranks_forbid``, which runs **both**
      classifiers against the mutant and asserts they disagree. Before that
      lock existed the claim was narration: a forbid-first design passed every
      other test in this module.
    * *Subject, not body.* That same bullet's body names TDD and ADR in a
      counter-example ("a concrete test case in TDD, a decision in ADR"), so a
      body-wide read yields ``{SPEC, IPLAN, TDD, ADR}`` on **correct** text.
    """
    permitted: set = set()
    for bullet in id_naming_bullets(text):
        if not _permits(bullet):
            continue
        found: set = set()
        subject = _SUBJECT.match(bullet)
        if subject:
            found |= {m.group(1) for m in _LAYER.finditer(subject.group(1))}
        # Tags come from what the permit phrase attaches to — see
        # ``_permit_subject``. Reading them body-wide was a measured false
        # positive on correct text.
        found |= {m.group(1).upper() for m in _TAG.finditer(_permit_subject(bullet))}
        if not found:
            # A bullet that permits but names no layer where the parser looks
            # is not "permits nothing" — it is a bullet this parser cannot
            # read. Measured: moving the layer list out of the bolded subject
            # and into the body ("citing an upstream design doc (SPEC, IPLAN,
            # ADR or TDD) … is **document-level permitted**") is *genuinely
            # wrong text* that an earlier draft returned {SPEC, IPLAN} for,
            # because the emptied bullet contributed nothing and the other
            # permitting bullet supplied the correct-looking answer.
            raise Unparseable(
                "ID_NAMING_STANDARDS.md: a permitting bullet names no layer in "
                "its bolded subject or its permitting sentence, so its claim "
                f"cannot be read: {bullet[:120]!r}"
            )
        permitted |= found
    if not permitted:
        raise Unparseable("ID_NAMING_STANDARDS.md: no permitting bullet named any layer")
    return permitted


_TRACEABILITY_ANCHOR = "Reference Granularity Principle"
_TRACEABILITY_PERMIT = re.compile(r"citing\s+[^()]*?\(([^)]*)\)\s+at document-level", re.IGNORECASE)

# Every role a "document-level" phrase is allowed to play in that bullet. Any
# occurrence matching none of these is an unmodelled statement, and the parse is
# reported as unreadable rather than answered.
_TRACEABILITY_KNOWN_ROLES = (
    "at document-level",  # the permit clause — the anchor
    "a document-level ID",  # the forbid counter-example
    "are document-level and exempt",  # the self-tag / forward-pointer carve-out
)


def extract_traceability(text: str) -> set:
    """The permit-clause read of ``TRACEABILITY.md``'s one-sentence statement.

    Anchored on ``citing <subject> (<layers>) at document-level`` rather than on
    the subject wording. The subject is exactly what drifts — the pre-#530 text
    reads "citing design/decision units (…)" and the corrected text reads
    "citing the element-ID-exempt layers (…)" — so a subject anchor is
    ``Unparseable`` on the drift, and the regression fixture would then pass for
    the wrong reason. That was a real defect in this module's design, caught
    only when the fixture was run against it.

    **The bullet is also checked for unmodelled claims.** The permit clause
    alone is not the bullet's only opportunity to say something about
    document-level citation: appending "An ``@adr:`` or ``@tdd:``
    document-level citation is likewise acceptable." leaves the anchor matching
    exactly once and the extracted set unchanged, so the guard reported
    genuinely wrong text as correct. Every ``document-level`` occurrence must
    now play one of three known roles, and a fourth kind of statement makes the
    surface unreadable rather than silently ignored.

    Case-insensitive on ``citing`` because the most likely copy-edit to this
    five-line run-on bullet is splitting it into sentences, which capitalises
    it. Verified: neither other ``Citing`` on the line is followed by
    ``(…) at document-level``, in the live text or in the fixture, so the
    single-match requirement is unaffected.
    """
    bullet = next(
        (ln for ln in text.splitlines() if _TRACEABILITY_ANCHOR in ln),
        None,
    )
    if bullet is None:
        raise Unparseable(f"TRACEABILITY.md: no '{_TRACEABILITY_ANCHOR}' bullet")

    unmodelled = []
    for occurrence in re.finditer(r"document-level", bullet):
        window = bullet[max(0, occurrence.start() - 40) : occurrence.end() + 40]
        if not any(role in window for role in _TRACEABILITY_KNOWN_ROLES):
            unmodelled.append(window.strip())
    if unmodelled:
        raise Unparseable(
            "TRACEABILITY.md: the granularity bullet makes a document-level "
            "statement in none of the three modelled roles (permit clause, "
            f"forbid counter-example, exemption carve-out): {unmodelled!r}"
        )

    hits = _TRACEABILITY_PERMIT.findall(bullet)
    if len(hits) != 1:
        raise Unparseable(
            f"TRACEABILITY.md: expected exactly 1 'citing (…) at document-level' "
            f"permit clause, found {len(hits)}"
        )
    return {m.group(1) for m in _LAYER.finditer(hits[0])}


SURFACES = {
    "TAG_SYNTAX.md": extract_tag_syntax,
    "ID_NAMING_STANDARDS.md": extract_id_naming,
    "TRACEABILITY.md": extract_traceability,
}


def _token_only_prototype(text: str) -> set:
    """The discarded first design, kept as the **positive control** for D4/V6.

    It uses this module's own bullet anchor and permit classifier, and differs
    in one dimension only: it never reads the bolded subject. It missed the
    real drift, because the drifted bullet named its layers in a bolded subject
    with no ``@adr:``/``@tdd:`` token anywhere.

    (An earlier version of this docstring described a looser classifier —
    "tokens inside a bullet or sentence containing document-level" — and
    credited the prototype with killing "three synthetic mutants". Neither was
    true of the code: the first misdescribed ``_permits``, and those mutants
    were never shipped, so the claim was unverifiable narration. Both corrected
    rather than repeated.)

    A stub raising ``NotImplementedError`` would fail for a reason unrelated to
    detection — a green baseline with no information content, and a perfect kill
    rate against a control you built is a symptom rather than a result. This one
    fails the way the real mistake failed.
    """
    permitted: set = set()
    for bullet in id_naming_bullets(text):
        if not _permits(bullet):
            continue
        # The one and only difference from ``extract_id_naming``: no bolded
        # subject. Same section anchor, same permit classifier — so a failure
        # here isolates the bolded-subject rule and nothing else.
        permitted |= {m.group(1).upper() for m in _TAG.finditer(_permit_subject(bullet))}
    if not permitted:
        # The control carries the real extractor's empty-set guard too. Without
        # it the difference is *two*-dimensional, and the day this returns the
        # empty set for an unrelated reason the assertion that consumes it
        # blames the bolded-subject rule for a broken parse — the exact
        # conflation ``Unparseable`` exists to prevent.
        raise Unparseable("token-only control: no permitting bullet named any layer")
    return permitted


class DocumentLevelPermittedParity(unittest.TestCase):
    """Every surface that states the document-level-permitted set states ``{SPEC, IPLAN}``.

    Four surfaces carry the proposition and only one is executable:

    * ``tools/sdd_doc_lint/__init__.py`` ``_REFGRAN_ELEMENT_DECLARING`` — the
      authority, imported not parsed
    * ``framework/governance/ID_NAMING_STANDARDS.md`` §"Reference granularity" —
      GD-03's *named* authority
    * ``framework/governance/TAG_SYNTAX.md`` — a derived surface; its own header
      delegates granularity ownership to ``ID_NAMING_STANDARDS.md``, which is an
      argument for covering it, since a derived surface that disagrees is
      exactly the bug
    * ``framework/governance/TRACEABILITY.md`` — one dense prose sentence

    The comparison is over the **document-level-permitted** set, not its
    complement. The two look interchangeable and are not: ``TRACEABILITY.md``
    names EARS, BDD, ADR and TDD on the element-declaring side and omits BRD and
    PRD, so an element-declaring comparison reports a 4-of-6 mismatch on a
    **correct** file. Every surface states the document-level side completely.

    **Four scope limits, each established by measurement rather than assumed.**

    1. *Four surfaces, not the class.* A class-wide scan over the authoring
       surfaces (playbooks, layer templates, plugin skills and agents, Hermes
       prompts and ``agent-skills``) was measured and rejected: the token census
       returns 51 hits across 29 files, overwhelmingly **exempt** — self-tags,
       downstream forward-pointers, ``FAIL:``/``WRONG:`` counter-examples, and
       the layer templates' own self-tag declarations. An exemption model at
       that ratio is a heuristic that fails in one of two directions, both worse
       than no check: it false-positives on correct text and blocks CI, or it
       under-covers and then reads as complete.
       ``tests/conformance/platforms/test_no_inprompt_hashing.py`` is the
       in-repo instance of the second. Those surfaces are not unguarded in
       consequence, only unguarded *here* — ``REFGRAN01`` flags the artifacts
       they generate, which is how #486 was found, a downstream detector with
       regen latency.

    2. *Per recognised phrasing, not per document — and this is stronger than
       "per anchored region", which is how an earlier draft of this docstring
       put it.* The guard reads a **permit clause**, not a document. A
       contradicting sentence elsewhere in a guarded file passes, which matters
       because it is verbatim how GD-13 describes the original defect
       (``ID_NAMING_STANDARDS.md`` "contradicting the bullet immediately below
       it in the same file") — but so, in general, does a contradiction *inside
       the anchored region itself*, phrased in a way none of the three
       extractors models.

       Three such constructions were found in review and each is now closed by
       a lock in ``MutationLocks``: layers moved out of a bolded subject into
       the bullet body, a permitting bullet's forbid clause flipped, and an
       extra document-level claim appended to the ``TRACEABILITY.md`` bullet.
       They are closed **as specific phrasings**, not as a class. A fourth
       phrasing nobody has thought of is the standing residual risk here, and
       it is the reason the ``LAYER_REGISTRY.yaml`` alternative in limit 4 is
       the better design: a parsed set has no phrasings.

    3. *Reach.* ``framework/governance/DECISIONS.md`` GD-13 says a guard over
       these surfaces "would have caught all six". It would have caught **two**.
       The other four were ``playbooks/{05_ADR,07_TDD}/auditor.md``,
       ``layers/08_IPLAN/IPLAN-TEMPLATE.yaml`` and
       ``platforms/claude-code-plugin/agents/requirements-analyst.md``, none of
       which this module reads. The inherited claim is recorded here as wrong
       rather than repeated.

    4. *The better design is not this one.* Stating the set once in
       ``LAYER_REGISTRY.yaml`` — as ``realizing_layers`` and
       ``acceptance_layers`` already are — and checking the prose against the
       registry is the correct shape. It is rejected on cost only: a
       ``framework/**`` edit trips ``GATE-SPEC-E005`` and forces a
       ``framework/VERSION`` bump with its fanout and a founder grant.
    """

    def _read(self, name: str) -> str:
        return (GOVERNANCE / name).read_text(encoding="utf-8")

    def test_linter_constant_and_permitted_set_are_exact_complements(self):
        """The authority's complement is ``{SPEC, IPLAN}`` — asserted, not subtracted.

        Written as two set assertions rather than as ``LAYERS - declaring`` so
        that a layer added to one side and not the other fails here instead of
        vanishing into the arithmetic.
        """
        declaring = frozenset(_REFGRAN_ELEMENT_DECLARING)
        self.assertEqual(
            declaring | EXPECTED_PERMITTED,
            LAYERS,
            "element-declaring ∪ document-level-permitted must be all 8 layers",
        )
        self.assertEqual(
            declaring & EXPECTED_PERMITTED,
            frozenset(),
            "no layer may be both element-declaring and document-level permitted",
        )

    def test_live_surfaces_agree_with_the_authority(self):
        for name, extract in sorted(SURFACES.items()):
            with self.subTest(surface=name):
                try:
                    got = extract(self._read(name))
                except Unparseable as exc:
                    self.fail(f"{name}: the guard could not read this surface — {exc}")
                self.assertEqual(
                    got,
                    set(EXPECTED_PERMITTED),
                    f"{name} states a document-level-permitted set that disagrees with "
                    f"GD-03 and with tools/sdd_doc_lint _REFGRAN_ELEMENT_DECLARING",
                )

    def test_id_naming_bullet_shape_is_locked(self):
        """Six bullets, exactly two of them permitting.

        The shape is asserted, not only the result, so a seventh bullet forces a
        decision instead of silently joining a class.
        """
        bullets = id_naming_bullets(self._read("ID_NAMING_STANDARDS.md"))
        self.assertEqual(len(bullets), 6, "§Reference granularity bullet count changed")
        self.assertEqual(
            sum(1 for b in bullets if _permits(b)),
            2,
            "the number of *permitting* bullets changed — reclassify before editing",
        )


class Pre530DriftRegression(unittest.TestCase):
    """The guard detects the real pre-#530 drift, and the control confirms it is a detection.

    Fixtures are the drift verbatim at ``8dccc315^`` — see the fixture
    directory's ``README.md``. Synthetic mutants are not enough here: the first
    prototype killed three of them and missed the real drift, because a mutant
    written beside an extractor inherits the extractor's assumption about *how
    the rule is phrased*, so mutant and extractor agree and the mutant dies for
    the wrong reason.
    """

    EXPECTED_DRIFT = {
        "pre530_ID_NAMING_STANDARDS.md": (extract_id_naming, {"ADR", "SPEC", "TDD", "IPLAN"}),
        "pre530_TRACEABILITY.md": (extract_traceability, {"ADR", "SPEC", "TDD", "IPLAN"}),
        # Already correct at that revision — the negative control. It must stay
        # extractable *as correct*, or a guard that simply failed on everything
        # old would look like it worked.
        "pre530_TAG_SYNTAX.md": (extract_tag_syntax, {"SPEC", "IPLAN"}),
    }

    def test_guard_reads_the_pre_530_sets(self):
        for name, (extract, expected) in sorted(self.EXPECTED_DRIFT.items()):
            with self.subTest(fixture=name):
                text = (FIXTURES / name).read_text(encoding="utf-8")
                # Asserting the *set* — not merely that the guard failed. A
                # fixture that raises Unparseable is a broken parse, and the
                # fixture would then stand as evidence of a detection that never
                # happened. That is not hypothetical: it is what the first
                # TRACEABILITY.md anchor did (Pass 4).
                try:
                    got = extract(text)
                except Unparseable as exc:
                    self.fail(f"{name}: parse broke, so nothing was detected — {exc}")
                self.assertEqual(got, expected)

    def test_the_two_drifted_surfaces_would_have_failed_the_live_check(self):
        """Each drifted surface, run through its extractor, is not ``{SPEC, IPLAN}``.

        An earlier version of this test compared two module *constants* and
        never called an extractor — it passed with all three extractor bodies
        commented out. It is written against the extractor now, so it measures
        the thing its name claims.
        """
        for name in ("pre530_ID_NAMING_STANDARDS.md", "pre530_TRACEABILITY.md"):
            with self.subTest(fixture=name):
                extract, _ = self.EXPECTED_DRIFT[name]
                got = extract((FIXTURES / name).read_text(encoding="utf-8"))
                self.assertNotEqual(
                    got,
                    set(EXPECTED_PERMITTED),
                    f"{name} is the drift fixture; extracting {EXPECTED_PERMITTED} "
                    "from it would mean the guard cannot see the regression",
                )

    def test_the_discarded_token_only_prototype_misses_the_real_drift(self):
        """V6 — the positive control, measured rather than narrated.

        The prototype must **miss** ``ID_NAMING_STANDARDS.md``: the drifted
        bullet names ADR and TDD in a bolded subject with no ``@adr:``/``@tdd:``
        token, so a token-only read returns the correct-looking set. This is
        what makes the bolded-subject rule a measured requirement rather than an
        assertion in a docstring.
        """
        drifted = (FIXTURES / "pre530_ID_NAMING_STANDARDS.md").read_text(encoding="utf-8")
        self.assertEqual(
            _token_only_prototype(drifted),
            set(EXPECTED_PERMITTED),
            "the control no longer reproduces the original miss, so it is no "
            "longer evidence that the bolded-subject rule is required",
        )
        self.assertEqual(extract_id_naming(drifted), {"ADR", "SPEC", "TDD", "IPLAN"})


class MutationLocks(unittest.TestCase):
    """Every mutant this guard was measured against, shipped as a test.

    The module's own review established why this class has to exist: a mutation
    *run once* during development proves the guard worked that afternoon and
    locks nothing. The permit-over-forbid rule was justified in a docstring as
    "established by mutation" while **no shipped test distinguished it** — a
    forbid-first classifier passed every other test in this file, because the
    drift fixture's bullet has no forbid sentence (that sentence arrived with
    the #530 correction and exists only in the live text).

    Each mutant below is applied to the **live** governance text at run time, so
    these stay honest as those documents change. A mutant that stops applying
    fails loudly on the ``assertIn`` guard rather than passing vacuously.
    """

    def _mutate(self, name: str, old: str, new: str) -> str:
        text = (GOVERNANCE / name).read_text(encoding="utf-8")
        self.assertIn(old, text, f"{name}: mutation target no longer present — rewrite this mutant")
        return text.replace(old, new, 1)

    def test_permit_outranks_forbid(self):
        """The bullet re-drifts in its subject while keeping today's forbid sentence.

        This is the likeliest shape of a future re-drift, and it is the mutant
        that *justifies* permit-over-forbid rather than merely illustrating it:
        a forbid-first classifier skips the bullet and returns the correct-
        looking answer. Both classifiers are run here, so the comparison is the
        assertion.
        """
        mutant = self._mutate(
            "ID_NAMING_STANDARDS.md",
            "- **Design & realization layers (SPEC / IPLAN):**",
            "- **Design & realization layers (ADR / SPEC / TDD / IPLAN):**",
        )
        self.assertIn("remains element-level", mutant, "the forbid sentence must survive")

        def forbid_first(text: str) -> set:
            """The rejected classifier: skip any bullet carrying a forbid marker."""
            out: set = set()
            for bullet in id_naming_bullets(text):
                if _EXEMPTION in bullet or "remains element-level" in bullet:
                    continue
                if not any(phrase in bullet for phrase in _PERMIT):
                    continue
                subject = _SUBJECT.match(bullet)
                if subject:
                    out |= {m.group(1) for m in _LAYER.finditer(subject.group(1))}
                out |= {m.group(1).upper() for m in _TAG.finditer(_permit_subject(bullet))}
            return out

        self.assertEqual(
            forbid_first(mutant),
            set(EXPECTED_PERMITTED),
            "the mutant no longer survives forbid-first, so it no longer "
            "justifies the permit-over-forbid rule",
        )
        self.assertNotEqual(
            extract_id_naming(mutant),
            set(EXPECTED_PERMITTED),
            "permit-over-forbid must kill the mutant that forbid-first survives",
        )

    def test_layers_moved_out_of_the_bolded_subject_are_not_silently_dropped(self):
        """Genuinely wrong text whose layers sit in the body, not the subject.

        An earlier draft returned ``{SPEC, IPLAN}`` here: the emptied bullet
        contributed nothing and the *other* permitting bullet supplied the
        correct-looking answer. A permitting bullet naming no layer where the
        parser looks is now unreadable, not empty.
        """
        mutant = self._mutate(
            "ID_NAMING_STANDARDS.md",
            "- **Design & realization layers (SPEC / IPLAN):**",
            "- **Design & realization layers:** citing an upstream design doc "
            "(SPEC, IPLAN, ADR or TDD) as an architectural unit is "
            "**document-level permitted**. Formerly:",
        )
        with self.assertRaises(Unparseable):
            extract_id_naming(mutant)

    def test_a_correct_clarification_naming_upstream_tags_is_not_a_permission(self):
        """The false-positive direction: correct text must stay correct.

        Reading ``@tag`` tokens body-wide made this clarification — which
        *restates* the rule — read as granting ADR and TDD document-level
        citation, reddening CI on text that is right.
        """
        mutant = self._mutate(
            "ID_NAMING_STANDARDS.md",
            "- `@spec:` and `@iplan:` citations are **document-level**",
            "- `@spec:` and `@iplan:` citations are **document-level** "
            "(unlike `@adr:` and `@tdd:`, which must be element-level)",
        )
        self.assertEqual(extract_id_naming(mutant), set(EXPECTED_PERMITTED))

    def test_a_second_table_cannot_contribute_rows(self):
        """``TAG_SYNTAX.md`` carries a second pipe table 60 lines below the first.

        The benign margin is one cell wide: two of its rows already read
        ``@spec: SPEC-01`` **(doc-level — SPEC exempt)** in the third cell. A
        file-scoped extractor that read the second cell of those rows returned
        ``{SPEC, IPLAN, TDD}`` — a wrong layer set on correct text, which is the
        failure direction ``Unparseable`` cannot rescue.
        """
        mutant = self._mutate(
            "TAG_SYNTAX.md",
            "`@ears @bdd @adr @spec`",
            "`@ears @bdd @adr @spec` (@spec is document-level)",
        )
        self.assertEqual(extract_tag_syntax(mutant), set(EXPECTED_PERMITTED))

    def test_a_reworded_form_cell_is_unparseable_not_empty(self):
        """The empty set is never an answer — the third extractor learned it last."""
        mutant = self._mutate("TAG_SYNTAX.md", "**document** `TYPE-NN`", "**doc** `TYPE-NN`")
        with self.assertRaises(Unparseable):
            extract_tag_syntax(mutant)

    def test_an_extra_document_level_claim_is_unparseable(self):
        """A fourth kind of document-level statement is not silently ignored.

        The appended sentence leaves the permit anchor matching exactly once and
        the extracted set unchanged, so a permit-clause-only reading reported
        genuinely wrong text as correct.
        """
        mutant = self._mutate(
            "TRACEABILITY.md",
            "Self-tags and downstream forward-pointers are document-level and exempt (GD-03).",
            "An `@adr:` or `@tdd:` document-level citation is likewise acceptable. "
            "Self-tags and downstream forward-pointers are document-level and exempt (GD-03).",
        )
        with self.assertRaises(Unparseable):
            extract_traceability(mutant)


class UnparseableIsDistinctFromDisagreement(unittest.TestCase):
    """A broken parse reports as a broken parse and names no layer set.

    Its inverse is the dangerous one: a benign rewording of a *correct* surface
    yielding the empty set would redden CI with a message naming layers, sending
    the author to fix a rule that is not wrong.
    """

    def test_missing_heading_is_unparseable(self):
        text = (GOVERNANCE / "ID_NAMING_STANDARDS.md").read_text(encoding="utf-8")
        with self.assertRaises(Unparseable) as caught:
            extract_id_naming(text.replace("### Reference granularity", "### Something else"))
        self.assertIn("Reference granularity", str(caught.exception))
        self.assertNotIn("SPEC", str(caught.exception))

    def test_missing_table_header_is_unparseable(self):
        text = (GOVERNANCE / "TAG_SYNTAX.md").read_text(encoding="utf-8")
        with self.assertRaises(Unparseable):
            extract_tag_syntax(text.replace("| Target layer | Form | Why |", "| A | B | C |"))

    def test_missing_permit_clause_is_unparseable(self):
        text = (GOVERNANCE / "TRACEABILITY.md").read_text(encoding="utf-8")
        with self.assertRaises(Unparseable):
            extract_traceability(text.replace("at document-level", "at doc level"))


if __name__ == "__main__":
    unittest.main()
