"""Conformance: the document-level-permitted set is ``{SPEC, IPLAN}`` everywhere it is stated.

GD-03 ratified that an ``@<layer>:`` trace citation to an element-declaring
layer MUST be element-level, which leaves SPEC and IPLAN as the only layers a
trace citation may name at document level. That proposition is stated in four
places and, until this module, measured in none — between 2026-06-27 and
2026-08-23 two of the statements said the opposite and nothing noticed (#531).

See ``DocumentLevelPermittedParity`` for what is and is not covered.
"""

from __future__ import annotations

import hashlib
import re
import sys
import textwrap
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
    body = tag_syntax_rows(text)
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


def _joined_bullet(text: str, anchor: str) -> str | None:
    """The bullet containing ``anchor``, joined across its continuation lines.

    Physical-line scoping was a measured false positive in the *benign*
    direction, which is the expensive one: ``TRACEABILITY.md``'s granularity
    bullet is a single 743-character line in a file whose next-longest line is
    103 and whose body wraps at ~95, so it is an outlier that a reflow or a
    copy-edit is likely to wrap. Reproduced at widths 80, 95 and 100 — every one
    made the permit anchor ``Unparseable``, i.e. the conformance hook (a
    *required* context) failing on text that is still correct.

    ``_bullets`` has always joined continuations for ``ID_NAMING_STANDARDS.md``;
    this is the same rule, applied to the one surface that lacked it. It is
    deliberately more permissive than ``_bullets`` about indentation: a wrap
    written without a two-space continuation indent is still a wrap.
    """
    lines = text.splitlines()
    start = next((i for i, ln in enumerate(lines) if anchor in ln), None)
    if start is None:
        return None
    bullet = lines[start].rstrip()
    for line in lines[start + 1 :]:
        stripped = line.strip()
        # A blank line, a sibling bullet or a heading ends the bullet. Anything
        # else non-blank is a continuation of it.
        # A bare "#" is not a heading — CommonMark requires a following space — and
        # the anchored bullet contains the literal `#502`, so a narrow reflow starts
        # a continuation line with it. Treating that as a heading ended the join and
        # made the surface Unparseable; measured at width 48.
        if not stripped or re.match(r"^(?:[-*+]\s|#{1,6}\s|\d+\.\s)", stripped):
            break
        bullet += " " + stripped
    return bullet


def tag_syntax_rows(text: str) -> list:
    """The data rows of the granularity table — the first pipe table only."""
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
    return body


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
    for sentence in _sentences(bullet):
        for phrase in _PERMIT:
            index = sentence.find(phrase)
            if index != -1:
                return sentence[:index]
    return bullet


# Markers that make a fragment a *contrast* rather than a grant. Without them the
# clarification "(unlike `@adr:` and `@tdd:`, which must be element-level)" reads
# as permitting ADR and TDD; with them, ", as are `@adr:` and `@tdd:` citations"
# still reads as the grant it is. Both directions are locked in ``MutationLocks``.
# Deliberately NOT "must be" or "never": both are modal rather than negative, so
# "as must be `@adr:` and `@tdd:` citations" — a grant — was read as a forbid and
# skipped. Every marker here entails element-level, which is the actual contrast.
_FORBID_MARKERS = ("element-level", "unlike", "whereas", "as opposed to")

# A clause introducing an EXAMPLE or a cross-reference names layers without
# claiming anything about them. Without this, moving the live bullet's own
# "(e.g. TDD citing `SPEC-01`, …)" after the predicate — a meaning-preserving
# copy-edit — reported correct text as Unparseable, naming TDD.
_EXAMPLE_MARKERS = ("e.g.", "i.e.", "cf.", "see ")


_ABBREVIATIONS = ("e.g.", "i.e.", "cf.", "et al.", "vs.")


def _sentences(text: str) -> list:
    r"""Sentence split that does not break inside a common abbreviation.

    ``re.split(r"(?<=\.)\s+", …)`` breaks after "e.g.", which silently halves
    the live "Design & realization layers" bullet and put its own example into
    what the tail rule treats as a separate statement. Guarded by a placeholder
    swap rather than a lookbehind, because Python requires fixed-width lookbehind
    and these abbreviations differ in length.
    """
    guarded = text
    for index, abbreviation in enumerate(_ABBREVIATIONS):
        guarded = guarded.replace(abbreviation, f"\x00{index}\x00")
    return [
        re.sub(r"\x00(\d+)\x00", lambda m: _ABBREVIATIONS[int(m.group(1))], sentence)
        for sentence in re.split(r"(?<=\.)\s+", guarded)
    ]


def _has_forbid_marker(fragment: str) -> bool:
    lowered = fragment.lower()
    return any(marker in lowered for marker in _FORBID_MARKERS)


def _stray_layers(bullet: str, granted: set) -> set:
    """Layers a permitting bullet names AFTER its permit phrase and does not forbid.

    ``_permit_subject`` truncates at the permit phrase because the phrase is a
    predicate, so its subject precedes it. That is right for the subject and
    blind to a **trailing conjunction**: appending ", as are ``@adr:`` and
    ``@tdd:`` citations" to the ``@spec:``/``@iplan:`` bullet grants two
    element-declaring layers document-level citation — verbatim the GD-13 drift
    — and an earlier draft returned ``{SPEC, IPLAN}`` for it, reporting the
    drift as correct.

    The tail cannot simply be read for layer names: the live text names SPEC and
    IPLAN again in a cross-reference ("see the SPEC §5 / IPLAN §4 exemption"),
    and the *other* permitting bullet's forbid sentence names TDD and ADR in a
    counter-example. So the rule is **new** names only — a tail may restate what
    the bullet granted, never introduce a layer — and fragments carrying a
    forbid marker are skipped. A survivor is reported ``Unparseable``, not
    silently dropped: a construction this parser cannot classify is not the same
    claim as "permits nothing".
    """
    sentences = _sentences(bullet)
    tail: list = []
    for index, sentence in enumerate(sentences):
        for phrase in _PERMIT:
            at = sentence.find(phrase)
            if at != -1:
                tail = [sentence[at + len(phrase) :], *sentences[index + 1 :]]
                break
        if tail:
            break

    stray: set = set()
    for position, sentence in enumerate(tail):
        # A *later* sentence carrying a forbid marker is a forbid statement and
        # is skipped whole — that is the shape of the live "Design & realization
        # layers" bullet's second sentence. The permit sentence's own tail
        # (position 0) is split finer, because its contrast lives in a clause.
        if position and _has_forbid_marker(sentence):
            continue
        for clause in re.split(r"[(),;—]", sentence):
            if _has_forbid_marker(clause):
                continue
            if any(marker in clause.lower() for marker in _EXAMPLE_MARKERS):
                continue
            stray |= {m.group(1) for m in _LAYER.finditer(clause)}
            stray |= {m.group(1).upper() for m in _TAG.finditer(clause)}
    return stray - granted


def _permits(bullet: str) -> bool:
    if _EXEMPTION in bullet:
        return False
    return any(phrase in bullet for phrase in _PERMIT)


def id_naming_section(text: str) -> str:
    start = text.find("### Reference granularity")
    if start == -1:
        raise Unparseable("ID_NAMING_STANDARDS.md: no '### Reference granularity' heading")
    rest = text[start + 1 :]
    end = rest.find("\n### ")
    return rest if end == -1 else rest[:end]


def id_naming_bullets(text: str) -> list:
    section = id_naming_section(text)
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
        stray = _stray_layers(bullet, found)
        if stray:
            # See ``_stray_layers``. Reported rather than answered, because the
            # answer would be a set that omits a layer the text just granted.
            raise Unparseable(
                "ID_NAMING_STANDARDS.md: a permitting bullet names "
                f"{sorted(stray)} after its permit phrase, outside any "
                "element-level or contrast clause, so whether it grants them "
                f"document-level citation cannot be read: {bullet[:120]!r}"
            )
        permitted |= found
    if not permitted:
        raise Unparseable("ID_NAMING_STANDARDS.md: no permitting bullet named any layer")
    return permitted


_TRACEABILITY_ANCHOR = "Reference Granularity Principle"
# The lazy run is forbidden from crossing a ``document-level`` occurrence. Without
# that guard it absorbs arbitrary prose — including a second, unmodelled grant —
# into the permit clause's own match span, which the role check then reads as
# "accounted for". Measured: a grant planted inside the clause's subject returned
# {SPEC, IPLAN}. Locked by ``test_a_grant_inside_the_permit_clause_is_unparseable``.
_TRACEABILITY_PERMIT = re.compile(
    r"citing\s+(?:(?!document-level)[^()])*?\(([^)]*)\)\s+at document-level", re.IGNORECASE
)

# Every role a "document-level" phrase is allowed to play in that bullet, as a
# pattern that must **contain** the occurrence it accounts for.
#
# Substrings-in-a-window were the first design and were defeated two ways, both
# reproduced against the live text and both now locked in ``MutationLocks``:
# a new claim that *reuses* a role's own wording ("`@adr:` and `@tdd:` may
# likewise be cited at document-level") matched the bare "at document-level"
# string, and a new claim merely *near* a legitimate one ("Citing a
# document-level ID, though ADR document-level cites are fine, (e.g. `BDD-01`)")
# fell inside its ±40-character window. Both returned {SPEC, IPLAN} — genuinely
# wrong text reported as correct. Containment has neither failure mode: an
# occurrence is accounted for only by a match that spans it.
_TRACEABILITY_ROLE_PATTERNS = (
    # the permit clause — the anchor itself, so it accounts for its own occurrence
    _TRACEABILITY_PERMIT,
    # the forbid counter-example
    re.compile(r"Citing\s+a\s+\*{0,2}document-level\*{0,2}\s+ID", re.IGNORECASE),
    # the self-tag / forward-pointer carve-out
    re.compile(
        r"are\s+\*{0,2}document-level\*{0,2}\s+and\s+(?:\w+\s+)?(?:exempt|are\s+\*\*not\*\*)",
        re.IGNORECASE,
    ),
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
    bullet = _joined_bullet(text, _TRACEABILITY_ANCHOR)
    if bullet is None:
        raise Unparseable(f"TRACEABILITY.md: no '{_TRACEABILITY_ANCHOR}' bullet")

    accounted = [
        match.span()
        for pattern in _TRACEABILITY_ROLE_PATTERNS
        for match in pattern.finditer(bullet)
    ]
    unmodelled = []
    for occurrence in re.finditer(r"document-level", bullet):
        if not any(
            start <= occurrence.start() and occurrence.end() <= end for start, end in accounted
        ):
            unmodelled.append(
                bullet[max(0, occurrence.start() - 40) : occurrence.end() + 40].strip()
            )
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


def anchored_region(name: str, text: str) -> str:
    """The exact span of prose each extractor reads, whitespace-normalised.

    Normalisation is whitespace-only, so a reflow or an indent change does not
    move the digest — those are the edits the extractors are already tolerant
    of. Every other edit does move it, which is the point.
    """
    if name == "ID_NAMING_STANDARDS.md":
        region = id_naming_section(text)
    elif name == "TAG_SYNTAX.md":
        region = "\n".join(tag_syntax_rows(text))
    elif name == "TRACEABILITY.md":
        region = _joined_bullet(text, _TRACEABILITY_ANCHOR) or ""
        if not region:
            raise Unparseable(f"TRACEABILITY.md: no '{_TRACEABILITY_ANCHOR}' bullet")
    else:  # pragma: no cover - guarded by test_every_surface_is_pinned
        raise KeyError(name)
    return re.sub(r"\s+", " ", region).strip()


# Digest of each anchored region as it stands today. See ``AnchoredProseIsPinned``
# for why these exist and what to do when one fails; the failure message carries
# the new digest, so regenerating is a copy, never a computation.
PINNED_REGIONS = {
    "ID_NAMING_STANDARDS.md": "7749a042461518610a32edc839530502f7b3bede690eeff8e9b5f168ffcfae51",  # pragma: allowlist secret
    "TAG_SYNTAX.md": "914e3577d0d195f2ecff54ad1d448a12ee9c8a0e205ac4d10edb53b78de60cd1",  # pragma: allowlist secret
    "TRACEABILITY.md": "65cb30a43a0a11f2aae69914b131397c38a68afbf63414d52c44a97f1d8a8590",  # pragma: allowlist secret
}


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

       **Fifteen** such constructions have been found across **three**
       adversarial rounds — 3, then 5, then 7 — and the trend is the point, not
       the fifteen. Rounds 2 and 3 each ran against a form of this module that
       had been pushed for merge, and each found governance text granting ADR
       and TDD document-level citation, the GD-13 drift verbatim, reported as
       **correct**. Round 3 also found four benign edits reported as drift,
       including moving the live bullet's own example after its predicate.

       **So the extractors are no longer the only guard, and scope limit 2 is
       narrower than it was.** ``AnchoredProseIsPinned`` pins each anchored
       region by digest, and a digest cannot be defeated by phrasing — a
       re-drift cannot pass unnoticed however it is worded. What remains
       phrasing-dependent is only which *message* you get: a construction an
       extractor models is reported as a wrong set, and one it does not is
       reported as changed prose to re-read. One such construction is known and
       kept as a live assertion rather than a footnote (a later sentence that
       both grants and contrasts; splitting it finer false-positives on the
       live "Design & realization layers" bullet, so markers cannot separate
       them).

       The counts above are asserted by ``DocumentedCountsAreReal``, because
       they were narrated wrongly three times before they were derived.

    3. *Reach — two, not six.* This module reaches **two** of the six surfaces
       GD-13 corrected. The other four were
       ``playbooks/{05_ADR,07_TDD}/auditor.md``,
       ``layers/08_IPLAN/IPLAN-TEMPLATE.yaml`` and
       ``platforms/claude-code-plugin/agents/requirements-analyst.md``, none of
       which this module reads.

       An earlier form of GD-13's successor sentence claimed such a guard
       "would have caught all six", and an earlier form of *this* docstring
       recorded that as a live defect. **It is not one:**
       ``framework/governance/DECISIONS.md`` already states "would catch **two**
       of the six above, not all six", and GD-18 item 3 records the correction
       as landed. Both were true at this branch's merge base, so the claim is
       stated here as the plain fact it is rather than as a finding against
       another document.

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

    # ----------------------------------------------------------------------
    # Review-2 locks. Each of the four below is a construction that the first
    # merged form of this module got wrong on the LIVE text, reproduced before
    # being folded. Three grant ADR/TDD document-level citation — verbatim the
    # GD-13 drift this guard exists to catch — and were reported as correct;
    # the fourth reddened a required check on text that was right.
    # ----------------------------------------------------------------------

    def test_a_trailing_conjunction_grant_is_not_silently_dropped(self):
        """The grant arrives AFTER the permit phrase, as a conjunction.

        ``_permit_subject`` truncates at the permit phrase because the phrase is
        a predicate — correct for the subject, blind to a tail. Measured:
        this returned ``{SPEC, IPLAN}``, i.e. the guard passing on text that
        grants two element-declaring layers document-level citation.

        Note this is the *symmetric* case of
        ``test_a_correct_clarification_naming_upstream_tags_is_not_a_permission``
        above: that one locks the false-positive direction of the same tail, and
        having only it is what left this direction open.
        """
        mutant = self._mutate(
            "ID_NAMING_STANDARDS.md",
            "- `@spec:` and `@iplan:` citations are **document-level**",
            "- `@spec:` and `@iplan:` citations are **document-level**, "
            "as are `@adr:` and `@tdd:` citations",
        )
        with self.assertRaises(Unparseable) as caught:
            extract_id_naming(mutant)
        # Not merely "it raised": a parse that broke for an unrelated reason
        # would satisfy assertRaises while detecting nothing (D2). The message
        # must name the layers the mutant granted.
        self.assertIn("ADR", str(caught.exception))
        self.assertIn("TDD", str(caught.exception))

    def test_a_second_sentence_grant_is_not_silently_dropped(self):
        """The same grant as its own sentence, which sentence-scoping alone misses."""
        mutant = self._mutate(
            "ID_NAMING_STANDARDS.md",
            "- `@spec:` and `@iplan:` citations are **document-level**",
            "- `@spec:` and `@iplan:` citations are **document-level**. "
            "So are `@adr:` and `@tdd:` citations.",
        )
        with self.assertRaises(Unparseable) as caught:
            extract_id_naming(mutant)
        self.assertIn("ADR", str(caught.exception))
        self.assertIn("TDD", str(caught.exception))

    def test_a_grant_reusing_a_modelled_roles_wording_is_unparseable(self):
        """A new claim phrased in an existing role's own words.

        The first form of the role check tested for the bare substring
        ``"at document-level"`` anywhere in a ±40-character window, so a claim
        that *reused* that wording accounted for itself. Measured: returned
        ``{SPEC, IPLAN}``. Containment has no such failure mode.
        """
        mutant = self._mutate(
            "TRACEABILITY.md",
            "Self-tags and downstream forward-pointers are document-level and exempt (GD-03).",
            "`@adr:` and `@tdd:` may likewise be cited at document-level. "
            "Self-tags and downstream forward-pointers are document-level and exempt (GD-03).",
        )
        with self.assertRaises(Unparseable) as caught:
            extract_traceability(mutant)
        # The unmodelled-role path specifically — not a broken permit anchor,
        # which would raise for a reason that is not a detection (D2).
        self.assertIn("modelled roles", str(caught.exception))

    def test_a_grant_adjacent_to_a_modelled_role_is_unparseable(self):
        """A new claim that is merely NEAR a legitimate one.

        The second defeat of the window design, and independent of the first:
        this phrasing reuses no role string, it simply lands inside the forbid
        counter-example's window. Measured: returned ``{SPEC, IPLAN}``.
        """
        mutant = self._mutate(
            "TRACEABILITY.md",
            "Citing a document-level ID (e.g. `BDD-01`)",
            "Citing a document-level ID, though ADR document-level cites are fine, (e.g. `BDD-01`)",
        )
        with self.assertRaises(Unparseable) as caught:
            extract_traceability(mutant)
        self.assertIn("modelled roles", str(caught.exception))

    def test_a_rewrapped_bullet_is_still_readable(self):
        """The false-positive direction: a benign reflow must not redden a required check.

        The bullet is a ~740-character line in a file whose next-longest is 103,
        so it is exactly the line a reflow touches. Physical-line scoping made
        **every** wrap width ``Unparseable`` — the conformance hook failing on
        correct text, which sends the author to fix a rule that is not wrong.

        ``break_on_hyphens=False`` models a real wrap: splitting ``document-``
        from ``level`` would corrupt the rendered prose, so no reflow a
        contributor would actually run does it. Both continuation-indent styles
        are covered because the guard must not depend on one.
        """
        text = (GOVERNANCE / "TRACEABILITY.md").read_text(encoding="utf-8")
        self.assertIn(_TRACEABILITY_ANCHOR, text)
        for indent in ("  ", ""):
            for width in (72, 80, 95, 120):
                with self.subTest(indent=len(indent), width=width):
                    wrapped = []
                    for line in text.splitlines():
                        if _TRACEABILITY_ANCHOR in line:
                            wrapped.extend(
                                textwrap.wrap(
                                    line,
                                    width,
                                    subsequent_indent=indent,
                                    break_on_hyphens=False,
                                    break_long_words=False,
                                )
                            )
                        else:
                            wrapped.append(line)
                    self.assertEqual(
                        extract_traceability("\n".join(wrapped)),
                        set(EXPECTED_PERMITTED),
                    )


class MutationLocksRoundThree(unittest.TestCase):
    """Round three's mutants. Same contract as ``MutationLocks``: applied to the
    live text, existence-guarded, and each reproduced before its fix was written.

    Two grants the guard reported as **correct**, and four benign edits it
    reported as drift. The split matters: a phrasing classifier fails in both
    directions, and only the second direction is visible without an adversary.
    """

    def _mutate(self, name: str, old: str, new: str) -> str:
        text = (GOVERNANCE / name).read_text(encoding="utf-8")
        self.assertIn(old, text, f"{name}: mutation target no longer present — rewrite this mutant")
        return text.replace(old, new, 1)

    def test_a_grant_inside_the_permit_clause_is_unparseable(self):
        """The permit clause's own lazy run absorbed an unmodelled grant.

        ``[^()]*?`` is unbounded, so a grant planted in the clause's *subject*
        was swallowed into the clause's match span — and containment then read
        it as accounted for. The role check was thereby defeated by the one
        pattern that is not short and anchored. Measured: ``{SPEC, IPLAN}``.
        """
        mutant = self._mutate(
            "TRACEABILITY.md",
            "citing the element-ID-exempt layers (SPEC, IPLAN) at document-level",
            "citing the element-ID-exempt layers, and `@adr:`/`@tdd:` refs which are "
            "equally document-level, (SPEC, IPLAN) at document-level",
        )
        with self.assertRaises(Unparseable) as caught:
            extract_traceability(mutant)
        self.assertIn("modelled roles", str(caught.exception))

    def test_a_modal_grant_is_not_read_as_a_forbid(self):
        """``must be`` is modality, not negation.

        ``must be document-level`` is a grant and ``must be element-level`` is a
        forbid; a bare ``must be`` marker cannot tell them apart, and treating
        it as a forbid skipped the clause. Two words from a mutant already
        locked in ``MutationLocks``. Measured: ``{SPEC, IPLAN}``.
        """
        mutant = self._mutate(
            "ID_NAMING_STANDARDS.md",
            "- `@spec:` and `@iplan:` citations are **document-level**",
            "- `@spec:` and `@iplan:` citations are **document-level**, "
            "as must be `@adr:` and `@tdd:` citations",
        )
        with self.assertRaises(Unparseable) as caught:
            extract_id_naming(mutant)
        self.assertIn("ADR", str(caught.exception))
        self.assertIn("TDD", str(caught.exception))

    def test_moving_the_live_example_after_the_predicate_stays_correct(self):
        """A meaning-preserving reorder of the bullet's OWN example.

        Nothing says the example must precede the predicate — the ordering is
        incidental. Moving it after put ``TDD`` in the tail, and the stray rule
        called correct text drift, naming TDD. The expensive direction.
        """
        mutant = self._mutate(
            "ID_NAMING_STANDARDS.md",
            "citing an upstream design doc as an architectural unit or provenance "
            "(e.g. TDD citing `SPEC-01`, IPLAN citing `SPEC-01`) is **document-level permitted**",
            "citing an upstream design doc as an architectural unit or provenance "
            "is **document-level permitted** (e.g. TDD citing `SPEC-01`, IPLAN citing `SPEC-01`)",
        )
        self.assertEqual(extract_id_naming(mutant), set(EXPECTED_PERMITTED))

    def test_an_adverb_in_the_exemption_clause_stays_correct(self):
        """One inserted word must not redden a required check."""
        mutant = self._mutate(
            "TRACEABILITY.md",
            "are document-level and exempt",
            "are document-level and therefore exempt",
        )
        self.assertEqual(extract_traceability(mutant), set(EXPECTED_PERMITTED))

    def test_bolding_the_term_stays_correct(self):
        """Converging on the sibling file's house style must not fail.

        ``ID_NAMING_STANDARDS.md`` already bolds the term in both its permitting
        bullets, so bolding it in ``TRACEABILITY.md`` is a contributor making the
        two governance files agree — and it made the role patterns miss.
        """
        mutant = self._mutate(
            "TRACEABILITY.md",
            "are document-level and exempt",
            "are **document-level** and exempt",
        )
        self.assertEqual(extract_traceability(mutant), set(EXPECTED_PERMITTED))

    def test_a_narrow_reflow_starting_a_line_with_an_issue_ref_stays_correct(self):
        """``#502`` is not a heading, and the bullet contains it.

        CommonMark requires a space after ``#``. Treating a bare ``#`` as a
        heading ended the continuation join at a line starting ``#502):**``,
        which any reflow narrower than ~53 columns produces. This repo's own
        ``CLAUDE.md`` records ``#NNN``-at-line-start as a live markdownlint
        hazard, so the token class is not hypothetical here.
        """
        text = (GOVERNANCE / "TRACEABILITY.md").read_text(encoding="utf-8")
        self.assertIn("#502", text, "the issue reference this mutant needs is gone")
        for width in (44, 48, 52):
            with self.subTest(width=width):
                wrapped = []
                for line in text.splitlines():
                    if _TRACEABILITY_ANCHOR in line:
                        wrapped.extend(
                            textwrap.wrap(
                                line, width, break_on_hyphens=False, break_long_words=False
                            )
                        )
                    else:
                        wrapped.append(line)
                self.assertEqual(extract_traceability("\n".join(wrapped)), set(EXPECTED_PERMITTED))


class DocumentedCountsAreReal(unittest.TestCase):
    """The counts this module's prose states are asserted against the code.

    Not pedantry: the review-round counts in this module's docstring, in
    ``CHANGELOG.md`` and in ``plans/DECISIONS.md`` D-0079 were **wrong three
    separate times** while this guard was being built — narrated from memory
    rather than derived, and each wrong count read as authoritative. A number
    that appears in four documents needs one executable source.

    If a round finds more constructions, update the number here **and** in the
    four prose surfaces named in the failure message. That is the point: the
    test makes the prose edit non-optional.
    """

    ROUND_LOCKS = {1: 3, 2: 5, 3: 7}
    PROSE_SURFACES = (
        "this module's class docstring, scope limit 2",
        "CHANGELOG.md, the #531 entry",
        "plans/DECISIONS.md, D-0079 items 7-8",
        "plans/REFGRAN-GUARD-001-PLAN.md, Pass 6-7",
    )

    def test_round_three_locks_match_the_documented_count(self):
        """Round 3 = the locks in ``MutationLocksRoundThree`` + the pin-only one.

        The pin-only construction is the phrasing no extractor models, asserted
        live in ``AnchoredProseIsPinned.test_a_grant_no_extractor_models_still_fails``.
        """
        locked = len([m for m in dir(MutationLocksRoundThree) if m.startswith("test_")])
        pin_only = 1
        self.assertEqual(
            locked + pin_only,
            self.ROUND_LOCKS[3],
            "round-3 construction count changed; update ROUND_LOCKS and then "
            + "; ".join(self.PROSE_SURFACES),
        )

    def test_total_constructions_match_the_documented_total(self):
        self.assertEqual(
            sum(self.ROUND_LOCKS.values()),
            15,
            "the total this module's prose states is stale; update it in "
            + "; ".join(self.PROSE_SURFACES),
        )


class AnchoredProseIsPinned(unittest.TestCase):
    """The anchored regions are pinned by digest, so no re-drift can be silent.

    **Why this exists, stated plainly: the extractors above cannot be trusted to
    be exhaustive, and three rounds of review are the evidence.** Each round
    was adversarial, each constructed governance text that genuinely grants an
    element-declaring layer document-level citation, and each found phrasings
    the previous round's extractor reported as **correct** — 3, then 5, then 7.
    A classifier built from permit phrases and forbid markers is doing natural
    language, and its known-closed phrasing set has never been its coverage.

    One phrasing is still open and is not closable that way: a later sentence
    that both grants and contrasts ("So are ``@adr:`` and ``@tdd:`` citations,
    unlike ``@ears:``") is skipped whole, because splitting it finer
    false-positives on the live "Design & realization layers" bullet, whose
    forbid sentence names TDD and ADR in a counter-example. Marker-based
    classification has no answer there.

    So the guard stops relying on classification for the direction that matters.
    A digest cannot be defeated by phrasing: **any** change to the prose these
    extractors read moves it, so a re-drift cannot pass unnoticed regardless of
    how it is worded. The extractors keep their job — proving the *current*
    pinned text states ``{SPEC, IPLAN}`` — and stop carrying the burden of
    proving that no future wording could.

    **The false positives are the feature.** Normalisation is whitespace-only,
    so reflows and re-indents pass; every other edit fails, with a message that
    names the region, prints the set still extracted, and gives the new digest
    to paste. That is not "fix a rule that is not wrong" — it is "a normative
    statement that drifted unnoticed for two months has changed; confirm it
    still means ``{SPEC, IPLAN}`` and say so." Updating a pin is a two-line
    diff a reviewer can actually check.

    **Do not regenerate a pin to make CI green.** Read the region, confirm the
    document-level-permitted set is still exactly ``{SPEC, IPLAN}``, and only
    then paste the digest — the whole value of this test is the pause.
    """

    def test_every_surface_is_pinned(self):
        """The pin set and the extractor set stay in step.

        Without this, adding a fourth surface to ``SURFACES`` would leave it
        unpinned and the pin suite would still be green — a guard that grows a
        hole exactly when it grows a surface.
        """
        self.assertEqual(set(PINNED_REGIONS), set(SURFACES))

    def test_anchored_regions_match_their_pins(self):
        for name in sorted(PINNED_REGIONS):
            with self.subTest(surface=name):
                text = (GOVERNANCE / name).read_text(encoding="utf-8")
                region = anchored_region(name, text)
                digest = hashlib.sha256(region.encode("utf-8")).hexdigest()
                if digest == PINNED_REGIONS[name]:
                    continue
                try:
                    reads_as = sorted(SURFACES[name](text))
                except Unparseable as exc:
                    reads_as = f"UNREADABLE — {exc}"
                self.fail(
                    f"{name}: the anchored granularity prose changed.\n"
                    f"  It now reads as document-level-permitted: {reads_as}\n"
                    f"  (it must be {sorted(EXPECTED_PERMITTED)})\n"
                    "  If that is still correct, this is a wording change: confirm it, "
                    "then update PINNED_REGIONS to\n"
                    f'    "{name}": "{digest}",\n'
                    "  and say in the PR that you re-read the region. Never repin to go green."
                )

    def test_a_grant_no_extractor_models_still_fails(self):
        """The phrasing the extractors provably cannot classify is caught here.

        ``extract_id_naming`` returns ``{SPEC, IPLAN}`` for this mutant — the
        one open false negative, kept as a *live* assertion so the claim stays
        honest — and the pin catches it anyway. This is the test that makes the
        digest load-bearing rather than decorative.
        """
        text = (GOVERNANCE / "ID_NAMING_STANDARDS.md").read_text(encoding="utf-8")
        target = "- `@spec:` and `@iplan:` citations are **document-level**"
        self.assertIn(target, text, "mutation target no longer present — rewrite this mutant")
        mutant = text.replace(
            target,
            target + ". So are `@adr:` and `@tdd:` citations, unlike `@ears:`.",
            1,
        )
        self.assertEqual(
            extract_id_naming(mutant),
            set(EXPECTED_PERMITTED),
            "the extractor now classifies this phrasing — good; rewrite this test "
            "against the next one it cannot, or drop it and say why",
        )
        self.assertNotEqual(
            hashlib.sha256(
                anchored_region("ID_NAMING_STANDARDS.md", mutant).encode("utf-8")
            ).hexdigest(),
            PINNED_REGIONS["ID_NAMING_STANDARDS.md"],
            "the pin did not move, so it does not close what the extractor misses",
        )

    def test_a_reflow_does_not_move_a_pin(self):
        """Whitespace-only normalisation, asserted rather than assumed.

        If a re-indent moved the digest, every reflow would demand a repin and
        the pin would train reviewers to regenerate without reading — which is
        the one failure mode that makes this test worthless.
        """
        for name in sorted(PINNED_REGIONS):
            with self.subTest(surface=name):
                text = (GOVERNANCE / name).read_text(encoding="utf-8")
                # Only what a reflow actually touches: continuation indent and
                # trailing whitespace. Re-indenting headings, table rows or
                # bullet starts is corruption, not a reflow, and would break the
                # anchors rather than testing normalisation.
                reflowed = "\n".join(
                    "      " + line.strip() + " " if line[:1].isspace() and line.strip() else line
                    for line in text.splitlines()
                )
                self.assertNotEqual(reflowed, text, "the reflow changed nothing")
                self.assertEqual(
                    anchored_region(name, text),
                    anchored_region(name, reflowed),
                )


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
