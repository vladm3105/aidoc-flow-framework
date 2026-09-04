"""GD-26 — a Draft IPLAN's §5 ``session_handoff.sessions`` is EMPTY.

``IPLAN-TEMPLATE.yaml`` §5 shipped a worked example asserting a session had
already run — a date, an agent and ``action: created`` on a file not on disk —
while the plugin's authoring skill instructed *seeding* that block at Draft. An
agent copying the example produced a Draft IPLAN recording history that never
happened (#621). It is #601 one section up, and the two engines contradicted
each other on it.

**The Draft rule reads the PARSED YAML value, never a comment.** That is GD-25's
central lesson, inherited verbatim: a guard checking only an enum comment would
have passed ``2943bf3b``, the commit that shipped #601.

**Why §5 is empty when §6 is seeded**, since the asymmetry looks like an
inconsistency until you see it: §6 ``code_inventory`` seeds one entry per §2
``file_manifest`` path, so its seed is **derived** from a set known at Draft —
which is exactly what makes an empty §6 indistinguishable from an executor that
never wrote its entries back. Nobody knows the future *sessions*, so a §5 seed
would be **fabricated**, and it would contradict
``document_control.session_count: 0``.

**No bundle-identity assertion here.** ``test_iplan_code_inventory_lifecycle``'s
``test_the_vendored_bundle_matches_the_spec`` already byte-compares this exact
file, and its own docstring says it adds no coverage; a second copy would be
duplication, not defence.

Whitespace is normalized before every scan and the skill glob reaches
``doc-iplan*/**/*.md`` rather than top-level ``SKILL.md`` — both are
``test_iplan_code_inventory_lifecycle``'s recorded findings, and
``test_no_inprompt_hashing.py`` is this repo's standing example of a guard that
scanned less than its name implied.
"""

from __future__ import annotations

import re
import unittest

import yaml
from _spec import FRAMEWORK, REPO_ROOT

IPLAN_TEMPLATE = FRAMEWORK / "layers" / "08_IPLAN" / "IPLAN-TEMPLATE.yaml"
IPLAN_README = FRAMEWORK / "layers" / "08_IPLAN" / "README.md"
GOVERNANCE_DECISIONS = FRAMEWORK / "governance" / "DECISIONS.md"
PLUGIN_SKILLS = REPO_ROOT / "platforms" / "claude-code-plugin" / "skills"
HERMES = REPO_ROOT / "platforms" / "hermes"

IPLAN_SKILL_GLOB = "doc-iplan*/**/*.md"
IPLAN_SKILL_DIRS = "doc-iplan*"
EXPECTED_IPLAN_SKILLS = 4
#: Measured on `main` before GD-26's edits, and again after. A sum, not a floor.
MEASURED_CODE_INVENTORY_SENTENCES = 7
#: Seed-carrier sentences whose match is exempt. All four are correct and local:
#: the fixer's phase-1 row, and four in the other engine's creation prompt (its
#: `Initialize … (sessions: [])`, its retrospective clause, its Draft carve-out and
#: its "initialized (empty sessions array)" criterion). A rise means a region
#: stopped being scanned.
MEASURED_EXEMPT_CARRIER_SENTENCES = 5

#: The Hermes surfaces that state the Draft shape or an IPLAN *creation* rule.
#: ``sdd-orchestrator`` is here because its "For IPLAN creation, enforce:" block
#: required carrying *previous session state* — #621's defect on Platform A,
#: which is why "the other engine was already right" was retracted.
HERMES_CREATION_SURFACES = (
    HERMES / "prompts" / "templates" / "creation" / "UCC_PROMPT_IPLAN.md",
    HERMES / "agent-skills" / "spec-driven-development" / "sdd-orchestrator" / "SKILL.md",
)

#: The §5 carrier ONLY — plural ``sessions`` or the section name. Deliberately NOT
#: the singular ``session:``, which is §6 ``code_inventory``'s per-entry key: the
#: first draft matched it and flagged ``code_inventory` seeded `planned` … (`session:
#: null`)``, a CORRECT GD-25 instruction. Flagging the sanctioned text of a sibling
#: decision is how a guard teaches the next author to mangle right prose.
_CARRIER = r"(?:\bsessions\b|\bsession[ _]handoff\b)"

#: The seed verbs. `initiali[sz]e` is load-bearing rather than decorative: BOTH
#: Platform-A surfaces already say "Initialize with empty sessions array", so
#: "Initialize the sessions array with one entry" is the likeliest regression
#: wording on that engine and the first draft's verb set walked straight past it.
_SEED_VERB = (
    r"\b(?:seed(?:s|ed|ing)?|populate(?:s|d)?|populating|prefill(?:s|ed|ing)?|"
    r"pre-fill(?:s|ed|ing)?|pre-populate(?:s|d)?|initiali[sz]e[sd]?|initiali[sz]ing|"
    r"stub(?:s|bed|bing)?)\b"
)

#: An instruction to SEED / POPULATE a session at authoring time, in either word
#: order. ``sessions`` and the seed verb within one clause is the defect shape;
#: an *append* instruction is correct and must not match, which is why the verb
#: set excludes "append".
_SEEDED_SESSION = re.compile(
    # seed-verb ... §5 carrier, either order
    _SEED_VERB
    + r"[^.]{0,60}?"
    + _CARRIER
    + r"|"
    + _CARRIER
    + r"[^.]{0,60}?"
    + _SEED_VERB
    # the verb-less form: a creation-time rule to carry prior state forward.
    # `sdd-orchestrator/SKILL.md` said "Session handoff: previous session state"
    # under "For IPLAN creation, enforce:" — #621's defect with no seed verb in it.
    + r"|\bprevious session state\b",
    re.IGNORECASE,
)

#: ⚠️ RETROSPECTIVE ATTRIBUTION IS CORRECT TEXT AND MUST NOT MATCH. "populated
#: during implementation sessions", "appended by each session", "written per
#: session" all say WHO fills the block — a later session — which is precisely
#: the rule GD-26 ratifies. The first draft of this guard fired on Hermes'
#: ``UCC_PROMPT_IPLAN.md`` for exactly that sentence. A guard that reds on the
#: sanctioned replacement forces the author to mangle correct prose to get
#: green: the failure ``test_adr_alternatives_optionality.py`` records, where
#: ``cost/fit`` was a substring of its own fix.
#: ADJACENCY IS LOAD-BEARING. A first draft allowed 40 characters between the
#: preposition and ``session``, which let ``doc-iplan``'s step 9 escape through
#: ``per `file_manifest` path (`session: null`` — a YAML key, not a session doing
#: work. The exemption must require the noun to FOLLOW the preposition directly.
_RETROSPECTIVE = re.compile(
    r"\b(?:during|by|per|after)\s+"
    r"(?:implementation\s+|each\s+|every\s+|a\s+|the\s+|one\s+)?sessions?\b"
    r"|\bappend(?:s|ed|ing)?\b",
    re.IGNORECASE,
)

#: A sentence that FORBIDS the seed is the sanctioned replacement text, and the
#: authoring, audit and fixer skills are exactly where it belongs. Without this
#: exemption the guard reds on the next correct edit — the failure mode
#: ``test_adr_alternatives_optionality.py`` records as review-killed.
_PROHIBITION = re.compile(
    r"\b(?:never|not|no longer|reject|forbid|must not|cannot|rather than|instead of|"
    r"do not|without)\b",
    re.IGNORECASE,
)


#: Seeding the EMPTY list is the ratified rule, not the defect — the defect is
#: seeding *content*. Without this the guard forbids the very sentence the fix
#: has to write ("seed `session_handoff` with `sessions: []`"), which would force
#: the prohibition wording into `doc-iplan-fixer`'s Fix-Phases table and disarm
#: GD-25's guards over all ~1,900 characters of it (see GD25GuardIsNotDisarmed).
_EMPTY_LIST = re.compile(
    r"sessions:\s*\[\s*\]"
    # ...and the PROSE form of the same rule. Adding `initiali[sz]e` to the verb
    # set made this necessary: the other engine's own correct success criterion
    # reads "Session handoff section initialized (empty sessions array)", with no
    # brackets anywhere, and the literal-only pattern flagged it.
    r"|empty\s+sessions?\s+array"
    r"|sessions?\s+array\s*\(\s*empty\s*\)",
    re.IGNORECASE,
)


#: How far from the match an exemption still counts as evidence ABOUT that match.
#: `_normalize` collapses a markdown table into ONE "sentence" — measured at 1,922
#: characters for `doc-iplan-fixer`'s Fix-Phases table — so a sentence-wide
#: exemption is not a carve-out, it is a hole the width of the table. Mutation
#: testing landed a full seed-a-session instruction in that table and it shipped
#: green, exempted by a `sessions: []` 1,500 characters away that this change had
#: itself put there. An exemption token that far from the carrier is not evidence
#: about the carrier.
_EXEMPTION_WINDOW = 80


def _exempt(sentence: str, match: re.Match) -> bool:
    """Is this MATCH exempt — judged on its own neighbourhood, not the sentence?

    `_PROHIBITION` stays sentence-wide: a sentence that forbids the seed is
    sanctioned replacement text wherever the clause sits. The other two are
    windowed, because they are claims about the carrier rather than about the
    author's intent.
    """
    if _PROHIBITION.search(sentence):
        return True
    lo = max(0, match.start() - _EXEMPTION_WINDOW)
    hi = min(len(sentence), match.end() + _EXEMPTION_WINDOW)
    window = sentence[lo:hi]
    return bool(_RETROSPECTIVE.search(window) or _EMPTY_LIST.search(window))


def _normalize(text: str) -> str:
    """Collapse every whitespace run to one space, so a rule survives reflow."""
    return re.sub(r"\s+", " ", text)


def _units(text: str) -> list[str]:
    """Scan units for the negative rule: a table ROW or a list ITEM is its own unit.

    ``_sentences`` inherits the sibling guard's tokenizer, and that tokenizer is
    the hazard: ``_normalize`` collapses ``doc-iplan-fixer``'s Fix-Phases table
    into ONE 1,922-character "sentence", so an exemption anywhere in the table
    covers every row of it. Mutation testing put a seed-a-session instruction in
    that table and it shipped green — twice, once even with an 80-character
    exemption window, because the adversarial row sat next to the legitimate
    ``sessions: []``.

    Splitting on row and bullet boundaries BEFORE normalizing removes the class
    rather than narrowing it: a markdown row cannot borrow its neighbour's
    exemption, because it is no longer in the same unit. Wrapped prose still
    joins, so the reflow finding that shaped the sibling guard still holds.
    """
    units: list[str] = []
    buf: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        is_marker = line.startswith(("|", "- ", "* ", "+ ")) or re.match(r"^\d+[.)]\s", line)
        if is_marker or not line:
            if buf:
                units.append(" ".join(buf))
                buf = []
            if is_marker:
                units.append(line)
            continue
        buf.append(line)
    if buf:
        units.append(" ".join(buf))
    out: list[str] = []
    for unit in units:
        out.extend(_sentences(unit))
    return out


def _sentences(text: str) -> list[str]:
    """Split on terminal punctuation.

    NOTE the `\\n` alternation that ``test_iplan_code_inventory_lifecycle``'s
    copy carries is deliberately absent: ``_normalize`` runs first, so no
    newline survives to split on. Writing it here would be dead code that reads
    like a bound — the misreading that nearly shipped a disarmed guard (#621
    plan, R2b).
    """
    return [s for s in re.split(r"(?<=[.!?])\s+", _normalize(text)) if s.strip()]


def _unit_at(body: str, index: int) -> str:
    """The bullet, table row or sentence containing ``index``.

    Bounded by a list marker or a table cell delimiter — NOT by sentence, because
    a carve-out legitimately follows the rule as a second sentence in the same cell.
    Tight enough to defeat a decoy in a neighbouring bullet 373 characters away.
    """
    starts = [body.rfind(t, 0, index) for t in ("- [ ]", "- ", "| ")]
    lo = max([x for x in starts if x != -1], default=0)
    ends = [body.find(t, index + 1) for t in ("- [ ]", "\n- ", " |")]
    hi = min([x for x in ends if x != -1], default=len(body))
    return body[lo : max(hi, index + 1)]


class DraftSessionsAreEmpty(unittest.TestCase):
    """The shipped §5 value, read as parsed YAML."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.source = IPLAN_TEMPLATE.read_text(encoding="utf-8")
        cls.template = yaml.safe_load(cls.source)
        cls.handoff = cls.template["session_handoff"]

    def test_sessions_is_an_empty_list(self) -> None:
        """The rule, read from the parsed value — not from a comment."""
        self.assertIn(
            "sessions",
            self.handoff,
            "§5 lost its `sessions:` carrier — GD-26 empties it, it does not remove it",
        )
        self.assertEqual(
            self.handoff["sessions"],
            [],
            "a Draft IPLAN carries `sessions: []` (GD-26/#621). A populated worked "
            "example here is copied verbatim by authoring agents and fabricates a "
            "session that never ran — #601 one section up",
        )

    def test_the_section_key_set_is_exactly_this(self) -> None:
        """GD-26 claims "no key is added and none is removed" — an ALLOWLIST claim,
        so assert the set. A sampled denylist let a mutation add a section-level
        `last_session_state: "…action: created"` and stay green, which is #621's
        defect wearing a different key name."""
        self.assertEqual(
            set(self.handoff),
            {"_size_target", "_required_when_subtype", "_guidance", "sessions"},
            "§5's key set changed. GD-26 adds no key and removes none; the "
            "per-session record stays per-session, inside `sessions[]`",
        )

    def test_guidance_states_the_draft_rule(self) -> None:
        guidance = _normalize(self.handoff["_guidance"]).lower()
        for phrase in ("empty at draft", "`sessions: []`"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, guidance)

    def test_guidance_explains_the_asymmetry_with_section_6(self) -> None:
        """Without the reason, a later reader "repairs" §5 into §6's seeded shape."""
        guidance = _normalize(self.handoff["_guidance"]).lower()
        for phrase in ("code_inventory", "derived", "fabricat"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, guidance)

    def test_guidance_carries_the_append_shape(self) -> None:
        """GD-24: an example overrides the prose beside it. Deleting the worked
        entry outright would leave an executor no shape to append, so it moves
        into the guidance labelled as an append — never a Draft value."""
        guidance = _normalize(self.handoff["_guidance"])
        self.assertRegex(
            guidance,
            r"(?i)append",
            "the guidance must label the worked entry as what a session APPENDS",
        )
        for key in ("date:", "agent:", "files_touched:", "next_session_directive:"):
            with self.subTest(key=key):
                self.assertIn(key, guidance)

    def test_the_action_enum_survives_the_move(self) -> None:
        """``test_iplan_code_inventory_lifecycle`` asserts exactly ONE ``action:``
        enum line over this file's raw source and holds it to two values. Moving
        the worked entry into a block scalar keeps that line — with its comment —
        so the sibling guard stays green. Pinned here because the enum now lives
        only inside `_guidance`, where a careless trim would silently drop it."""
        actions = re.findall(r"^\s*action:\s*\S+\s*#\s*(.*?)\s*$", self.source, re.MULTILINE)
        self.assertEqual(
            len(actions),
            1,
            f"expected exactly one `action:` enum line, found {actions}",
        )
        self.assertEqual([v.strip() for v in actions[0].split("|")], ["created", "modified"])


class LayerReadmeStatesTheRule(unittest.TestCase):
    def test_readme_describes_the_empty_draft(self) -> None:
        readme = _normalize(IPLAN_README.read_text(encoding="utf-8")).lower()
        self.assertIn("`sessions: []`", readme)
        self.assertRegex(
            readme,
            r"draft[^.]{0,120}?`sessions: \[\]`|`sessions: \[\]`[^.]{0,120}?draft",
            "the layer README must tie the empty list to the Draft state",
        )


class PlatformSurfacesAgree(unittest.TestCase):
    """Both engines state the same rule. #621's premise was that they did not."""

    def _skill_docs(self):
        return sorted(PLUGIN_SKILLS.glob(IPLAN_SKILL_GLOB))

    def test_every_iplan_skill_is_scanned(self) -> None:
        dirs = sorted(p.name for p in PLUGIN_SKILLS.glob(IPLAN_SKILL_DIRS) if p.is_dir())
        self.assertEqual(
            len(dirs),
            EXPECTED_IPLAN_SKILLS,
            f"expected {EXPECTED_IPLAN_SKILLS} doc-iplan* skills, found {dirs} — update "
            "EXPECTED_IPLAN_SKILLS deliberately, so a new skill cannot escape the rules below",
        )
        self.assertTrue(self._skill_docs(), "the markdown glob matched nothing")

    def test_no_surface_instructs_seeding_a_session(self) -> None:
        """The negative. Covers BOTH engines: #621's live disagreement was that
        Platform B seeded while Platform A did not."""
        docs = [(d, d.relative_to(PLUGIN_SKILLS)) for d in self._skill_docs()]
        docs += [(h, h.relative_to(REPO_ROOT)) for h in HERMES_CREATION_SURFACES]
        for doc, rel in docs:
            for sentence in _units(doc.read_text(encoding="utf-8")):
                if "session" not in sentence.lower():
                    continue
                match = _SEEDED_SESSION.search(sentence)
                if not match or _exempt(sentence, match):
                    continue
                with self.subTest(doc=str(rel)):
                    self.fail(
                        f"{rel} instructs seeding/populating a session at authoring "
                        f"time: {sentence!r} — a Draft carries `sessions: []` (GD-26/#621)"
                    )

    def test_every_iplan_skill_states_the_empty_draft(self) -> None:
        """The positive half. A negative rule proves only that a surface stopped
        saying the old thing; GD-26 claims all four say the new one."""
        for skill in sorted(PLUGIN_SKILLS.glob(f"{IPLAN_SKILL_DIRS}/SKILL.md")):
            with self.subTest(skill=skill.parent.name):
                body = _normalize(skill.read_text(encoding="utf-8"))
                self.assertIn(
                    "`sessions: []`",
                    body,
                    f"{skill.parent.name} never states the empty Draft handoff — GD-26 "
                    f"says all {EXPECTED_IPLAN_SKILLS} IPLAN skills move with the template",
                )

    def test_hermes_creation_surfaces_state_the_empty_draft(self) -> None:
        for doc in HERMES_CREATION_SURFACES:
            with self.subTest(doc=doc.name):
                body = _normalize(doc.read_text(encoding="utf-8")).lower()
                self.assertRegex(
                    body,
                    r"empty sessions array|`sessions: \[\]`|sessions array \(empty\)",
                    f"{doc.name} must state the empty-at-Draft handoff; #621's premise "
                    "was that the two engines disagreed about it",
                )


class NonEmptySectionRuleIsDraftAware(unittest.TestCase):
    """Three surfaces demand every required section be non-empty/populated. With
    `sessions: []` now the correct Draft value of one, each needs the carve-out —
    otherwise an auditor fails an IPLAN the author was told to write, which is the
    failure GD-25 explicitly designed against. The plan found this repair had
    reached ONE of the three."""

    SURFACES = (
        (PLUGIN_SKILLS / "doc-iplan-audit" / "SKILL.md", "present and non-empty"),
        (PLUGIN_SKILLS / "doc-iplan" / "SKILL.md", "present and non-empty"),
        (
            HERMES / "prompts" / "templates" / "creation" / "UCC_PROMPT_IPLAN.md",
            "present and populated",
        ),
    )

    def test_each_non_empty_rule_carries_the_draft_carve_out(self) -> None:
        for path, marker in self.SURFACES:
            rel = path.relative_to(REPO_ROOT)
            body = _normalize(path.read_text(encoding="utf-8"))
            with self.subTest(surface=str(rel)):
                self.assertIn(
                    marker,
                    body,
                    f"{rel} no longer states '{marker}' — if the rule moved, move this "
                    "pin with it rather than deleting the coverage",
                )
                # Bound to the marker's OWN unit. A 400-character window let an
                # unrelated checklist bullet 373 characters away ("Session Handoff
                # present — `sessions: []` at Draft") satisfy this for
                # `doc-iplan/SKILL.md`, so deleting that file's actual carve-out
                # stayed green. Every occurrence is checked, not only the first.
                found = [m.start() for m in re.finditer(re.escape(marker), body)]
                self.assertTrue(found, f"{rel}: marker vanished")
                for index in found:
                    unit = _unit_at(body, index)
                    self.assertRegex(
                        unit,
                        r"`sessions: \[\]`",
                        f"{rel}'s '{marker}' rule has no Draft carve-out in its own "
                        "bullet. A Draft's `session_handoff` carrying `sessions: []` "
                        "satisfies it; without this an auditor fails what the author "
                        "was told to write",
                    )


class GD25GuardIsNotDisarmed(unittest.TestCase):
    """⚠️ Adding a *correct* prohibition sentence to a doc-iplan skill can silently
    DISARM ``test_iplan_code_inventory_lifecycle``'s two negative rules.

    ``_PROHIBITION`` there is applied per-**sentence**, and its ``_normalize``
    collapses a markdown table with no ``.``+whitespace into ONE sentence —
    ``doc-iplan-fixer``'s Fix-Phases table is a single ~1,900-character
    "sentence" carrying ``code_inventory`` twice. One exemption word anywhere in
    it exempts the whole table, and the suite stays green *because nothing
    happened*.

    Measured on ``main`` before GD-26's edits: 7 ``code_inventory``-bearing
    sentences across the four skills, **0** exempt. This pins that.
    """

    def test_no_code_inventory_sentence_is_prohibition_exempt(self) -> None:
        from test_iplan_code_inventory_lifecycle import (  # noqa: PLC0415
            _PROHIBITION as GD25_PROHIBITION,
        )
        from test_iplan_code_inventory_lifecycle import (  # noqa: PLC0415
            _sentences as gd25_sentences,
        )

        exempt: list[str] = []
        total = 0
        for skill in sorted(PLUGIN_SKILLS.glob(f"{IPLAN_SKILL_DIRS}/SKILL.md")):
            for sentence in gd25_sentences(skill.read_text(encoding="utf-8")):
                if "code_inventory" not in sentence:
                    continue
                total += 1
                if GD25_PROHIBITION.search(sentence):
                    exempt.append(f"{skill.parent.name}: {sentence[:120]}…")
        self.assertEqual(
            total,
            MEASURED_CODE_INVENTORY_SENTENCES,
            f"expected {MEASURED_CODE_INVENTORY_SENTENCES} `code_inventory`-bearing "
            f"sentences across the {EXPECTED_IPLAN_SKILLS} IPLAN skills, found {total}. "
            "A floor of one-per-skill is satisfied by `doc-iplan` alone, so it pins "
            "nothing; re-measure and update this constant deliberately",
        )
        self.assertEqual(
            exempt,
            [],
            "a `code_inventory` sentence is now exempt from GD-25's negative rules "
            "via its per-sentence `_PROHIBITION` escape, so those rules no longer "
            "scan it. Give each prohibition clause its own sentence, terminated by "
            f"`.` + whitespace. Offenders: {exempt}",
        )


class GD26GuardIsNotDisarmed(unittest.TestCase):
    """This guard installs the SAME hazard it polices for GD-25, so it polices it
    for itself too.

    ``test_no_surface_instructs_seeding_a_session`` skips a match when an
    exemption fires. `_normalize` collapses ``doc-iplan-fixer``'s Fix-Phases table
    into ONE 1,922-character "sentence", and THIS change put ``sessions: []`` into
    that table — which, before `_exempt` was windowed, made the whole table
    permanently exempt. Mutation testing dropped a full seed-a-session instruction
    into it and the suite stayed green.

    Windowing fixes that instance. This pins the CLASS: any sentence carrying the
    §5 carrier whose match is exempt is counted, and the count is a measured
    constant. A new exemption then has to be made deliberately, not inherited from
    a token 1,500 characters away.
    """

    def test_exempt_carrier_sentences_match_the_measured_baseline(self) -> None:
        exempt: list[str] = []
        docs = list(PLUGIN_SKILLS.glob(IPLAN_SKILL_GLOB)) + list(HERMES_CREATION_SURFACES)
        for doc in sorted(docs):
            for sentence in _units(doc.read_text(encoding="utf-8")):
                match = _SEEDED_SESSION.search(sentence)
                if match and _exempt(sentence, match):
                    exempt.append(
                        f"{doc.name}: {sentence[max(0, match.start() - 40) : match.end() + 40]}"
                    )
        self.assertEqual(
            len(exempt),
            MEASURED_EXEMPT_CARRIER_SENTENCES,
            "the number of exempted seed-carrier sentences moved. Each one is a "
            "region the negative rule no longer scans, so a rise must be a "
            "deliberate re-measurement rather than a side effect. Found:\n  " + "\n  ".join(exempt),
        )


class DecisionIsRecorded(unittest.TestCase):
    def test_gd_26_records_the_decision(self) -> None:
        """A heading is not a decision: assert the body carries the rule."""
        decisions = GOVERNANCE_DECISIONS.read_text(encoding="utf-8")
        self.assertRegex(
            decisions,
            r"(?m)^## GD-26 [-—] ",
            "a §5 Draft-shape change is a governance decision; GD-26 records it",
        )
        # Drop the remainder of the heading LINE before reading the body. The
        # heading itself contains "derived", so the assertion below was satisfied
        # by the heading alone — the exact thing this method's docstring denies.
        after = decisions.split("## GD-26")[1].split("\n", 1)[1]
        body = _normalize(after.split("\n## GD-25")[0])
        self.assertIn("`sessions: []`", body)
        self.assertRegex(
            body,
            r"(?i)derived",
            "GD-26 must state WHY §6 is seeded and §5 is not, or a later reader "
            "re-derives §5 into §6's shape",
        )
        self.assertRegex(
            body,
            r"(?i)session_count",
            "GD-26 must record that a seeded session contradicts "
            "`document_control.session_count: 0`",
        )


if __name__ == "__main__":
    unittest.main()
