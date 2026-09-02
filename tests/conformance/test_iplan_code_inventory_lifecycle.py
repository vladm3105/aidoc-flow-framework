"""Conformance: IPLAN ``code_inventory`` carries a three-value lifecycle, is
seeded ``planned`` at Draft, and states that vocabulary consistently everywhere
it appears (GD-25).

Guards the fix for #601. The template's §6 example read ``status: created`` with
``session: 1`` — the only worked example of the carrier — so agents generating a
Draft IPLAN copied it and claimed files existed that had never been written. The
first repair (``2943bf3b``, pushed straight to ``main``) appended ``planned`` to
the enum comment and nothing else, which left the §2 passage that *explains* this
carrier's vocabulary asserting ``created | modified`` while the ``status:`` key
below it declared three values. That contradiction is why this guard exists, so
its first job is to hold every in-file statement of the vocabulary to one value
set.

**Why the seed rule reads the parsed YAML, not the comment.** The enum lives in a
``#`` comment, which nothing parses; the *example entries* are what an authoring
agent copies. A guard checking only the comment would have passed ``2943bf3b`` —
the exact change that shipped the defect. So the entries are loaded with
``yaml.safe_load`` and every one must be in the Draft state, with paths matching
§2's ``file_manifest``, because "one entry per manifest path" is a rule an example
teaches only by demonstrating it.

**Why the platform rules are both negative AND positive.** The first draft
asserted only that no ``doc-iplan*`` skill instructs an *empty* inventory.
Mutation testing killed that shape on four counts, each of which this repo has
been bitten by before:

* the retired instruction re-entered by word order ("leave ``code_inventory``
  empty"), because the pattern was modifier-then-key — verbatim the
  order-directionality bug ``test_adr_alternatives_optionality.py`` records as
  review-killed one release earlier;
* a *correct* prohibition ("Reject an empty ``code_inventory``") reddened the
  check, the sibling guard's other recorded flaw — so a negation exemption is
  required, not optional;
* a skill could instruct ``status: created`` in a Draft seed and stay green: the
  rule banned the previous wrong instruction, not the class of wrong instruction;
* and deleting a skill's seed instruction outright stayed green, because a
  negative can only prove a surface does not say the old thing. Every claim GD-25
  makes about the four skills needs the positive.

Whitespace is normalized before every scan, because the live instruction in
``doc-iplan/SKILL.md`` was split across a line break — the shape that once let
``test_no_inprompt_hashing.py`` pass a live reintroduction. Expected fragments are
built from ``LIFECYCLE`` rather than hardcoded, so a meaning-preserving reword of
the punctuation around them cannot red a required context.
"""

from __future__ import annotations

import re
import unittest

import yaml
from _spec import FRAMEWORK, REPO_ROOT

IPLAN_TEMPLATE = FRAMEWORK / "layers" / "08_IPLAN" / "IPLAN-TEMPLATE.yaml"
IPLAN_README = FRAMEWORK / "layers" / "08_IPLAN" / "README.md"
GOVERNANCE_DECISIONS = FRAMEWORK / "governance" / "DECISIONS.md"
PLUGIN_BUNDLE_TEMPLATE = (
    REPO_ROOT
    / "platforms"
    / "claude-code-plugin"
    / "framework"
    / "layers"
    / "08_IPLAN"
    / "IPLAN-TEMPLATE.yaml"
)
PLUGIN_SKILLS = REPO_ROOT / "platforms" / "claude-code-plugin" / "skills"

#: The ratified vocabulary, in lifecycle order. Every expected fragment below is
#: built from this tuple; nothing restates it as a literal.
LIFECYCLE = ("planned", "created", "modified")
VOCABULARY = " | ".join(LIFECYCLE)

#: Every markdown file under a skill that authors, drives, audits or repairs an
#: IPLAN. ``**/*.md`` rather than ``SKILL.md``: a reference file beside a skill is
#: read by the same agent, and ``test_no_inprompt_hashing.py`` is this repo's
#: standing example of a guard that scanned less than its name implied.
IPLAN_SKILL_GLOB = "doc-iplan*/**/*.md"
#: Skills that must each carry the positive seed instruction.
IPLAN_SKILL_DIRS = "doc-iplan*"
EXPECTED_IPLAN_SKILLS = 4

#: The retired instruction, in EITHER order — "empty `code_inventory`" and
#: "`code_inventory` … empty" are the same defect. ``no`` is excluded from the
#: modifier set: it appears in ordinary correct prose ("no requirement that…"),
#: and the empty-list form is caught by its own literal below.
_EMPTY_INVENTORY = re.compile(
    r"\b(?:empty|blank)\b[^.]{0,40}?`?code_inventory`?"
    r"|`?code_inventory`?[^.]{0,40}?\b(?:empty|blank)\b"
    r"|code_inventory[^.]{0,20}?files:\s*\[\s*\]",
    re.IGNORECASE,
)

#: A sentence that FORBIDS the empty inventory is the sanctioned replacement
#: text, and the audit and fixer skills are exactly where it belongs. Without
#: this exemption the guard reds on the next correct edit — the failure mode
#: ``test_adr_alternatives_optionality.py`` records as review-killed.
_PROHIBITION = re.compile(
    r"\b(?:never|not|no longer|reject|forbid|must not|cannot|rather than|instead of)\b",
    re.IGNORECASE,
)

#: A Draft seed instruction that names a built status is #601 at the surface an
#: agent actually reads: the template can be right while the skill overrides it.
_DRAFT_BUILT_STATUS = re.compile(
    r"\b(?:status:\s*)?(?:created|modified)\b[^.]{0,60}?\b(?:draft|seed(?:s|ed|ing)?)\b"
    r"|\b(?:draft|seed(?:s|ed|ing)?)\b[^.]{0,60}?\bstatus:\s*(?:created|modified)\b",
    re.IGNORECASE,
)


def _normalize(text: str) -> str:
    """Collapse every whitespace run to one space, so a rule survives reflow."""
    return re.sub(r"\s+", " ", text)


def _sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+|\n", _normalize(text)) if s.strip()]


def _entry_status_lines(source: str) -> list[tuple[str, str | None]]:
    """``(value, enum-comment)`` for each ``status:`` line under ``files:``.

    Scoped to the entry list, not the whole block: ``_guidance`` is a literal
    scalar that may legitimately quote an entry's shape, and counting that as a
    second declaration would send a reader to the entries when the prose is what
    changed.
    """
    lines = source.splitlines()
    opener = re.compile(r"^ {2}code_inventory:")
    start = next((i for i, ln in enumerate(lines) if opener.match(ln)), None)
    if start is None:
        raise AssertionError(
            "no `  code_inventory:` key in the IPLAN template — the block was "
            "renamed or re-indented, and every rule in this module is scoped to it"
        )
    found: list[tuple[str, str | None]] = []
    in_files = False
    for line in lines[start + 1 :]:
        if line.strip() and len(line) - len(line.lstrip(" ")) <= 2:
            break
        if re.match(r"^ {4}files:", line):
            in_files = True
            continue
        if in_files:
            match = re.match(r"^\s*status:\s*(\S+)\s*(?:#\s*(.*?))?\s*$", line)
            if match:
                found.append((match.group(1), match.group(2)))
    return found


class CodeInventoryLifecycle(unittest.TestCase):
    """The vocabulary, the Draft seed, and the three in-file statements."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.source = IPLAN_TEMPLATE.read_text(encoding="utf-8")
        cls.doc = yaml.safe_load(cls.source)
        cls.inventory = cls.doc["traceability"]["code_inventory"]
        cls.manifest = cls.doc["file_manifest"]

    def test_enum_comment_declares_the_three_values_in_lifecycle_order(self) -> None:
        enums = [c for _, c in _entry_status_lines(self.source) if c]
        self.assertEqual(
            len(enums),
            1,
            "the code_inventory status vocabulary must be declared on exactly one "
            f"entry's `status:` comment; found {len(enums)}: {enums}",
        )
        self.assertEqual(
            [v.strip() for v in enums[0].split("|")],
            list(LIFECYCLE),
            f"the enum comment must read `{VOCABULARY}`, in lifecycle order — a "
            "reader takes the first value as the default",
        )

    def test_every_example_entry_is_in_the_draft_state(self) -> None:
        files = self.inventory["files"]
        self.assertGreaterEqual(len(files), 1, "code_inventory needs worked entries")
        for entry in files:
            with self.subTest(path=entry.get("path")):
                for key in ("path", "status", "session", "verified"):
                    self.assertIn(
                        key,
                        entry,
                        f"a code_inventory entry must carry `{key}` — the Draft seed "
                        "rule names all four, so a missing one is a template defect",
                    )
                self.assertEqual(
                    entry["status"],
                    "planned",
                    "a template is a Draft IPLAN, so every worked entry must show the "
                    "Draft state — an example showing `created` is the #601 defect, "
                    "because agents copy the example, not the prose",
                )
                self.assertIsNone(
                    entry["session"],
                    "`session` names the session that created or modified the file; "
                    "a planned file has none",
                )
                self.assertIs(
                    entry["verified"],
                    False,
                    "`verified` means tests pass + lint clean, and is a bool — "
                    "nothing planned has been verified",
                )

    def test_one_entry_per_file_manifest_path(self) -> None:
        self.assertEqual(
            [f["path"] for f in self.inventory["files"]],
            [f["path"] for f in self.manifest["files"]],
            "the Draft seed is one code_inventory entry per file_manifest path, in "
            "manifest order; the example must demonstrate it, because a rule stated "
            "only in prose beside a shorter example teaches the shorter example",
        )

    def test_all_three_in_file_statements_name_the_same_values(self) -> None:
        """#609 item 2: two of them disagreed for two days and nothing parsed either.

        The third — ``_guidance``'s own lifecycle list — sits directly above the
        entries and is the copy a reader meets first.
        """
        normalized = _normalize(self.source)
        anchor = "`traceability.code_inventory.files[].status`"
        self.assertIn(anchor, normalized, "the §2 carrier note no longer names §6's key")
        window = normalized.split(anchor, 1)[1][:200]
        # Punctuation-agnostic on purpose: an earlier draft pinned the em-dashes
        # around the vocabulary, so rewriting `(a different vocabulary — X —` as
        # `(a different vocabulary: X,` reddened a required context for no
        # semantic change. Assert the value set, not the prose around it.
        self.assertIn(
            f"`{VOCABULARY}`",
            window,
            "the §2 passage that explains this carrier restates its vocabulary within "
            f"200 characters of the key; it must name `{VOCABULARY}` — the same values "
            f"the `status:` key declares. Window was: {window!r}",
        )
        guidance = _normalize(self.inventory["_guidance"])
        for value in LIFECYCLE:
            with self.subTest(value=value):
                self.assertRegex(
                    guidance,
                    rf"\b{value}\s+—",
                    f"`{value}` is missing from the _guidance lifecycle list — that "
                    "list is the third in-file statement of the vocabulary and the "
                    "one a reader meets first",
                )

    def test_guidance_states_the_draft_seed_and_forbids_the_empty_block(self) -> None:
        guidance = _normalize(self.inventory["_guidance"]).lower()
        for phrase in ("one entry per", "file_manifest", "session: null", "manifest order"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, guidance)
        self.assertRegex(
            guidance,
            r"empty `code_inventory` is not the draft state",
            "the guidance must say what the Draft state is NOT — two plugin skills "
            "instructed the opposite before GD-25",
        )

    def test_guidance_scopes_the_seed_rule_to_a_subtype_carrying_a_manifest(self) -> None:
        """``deploy`` requires no ``file_manifest``, so the rule is unsatisfiable there."""
        guidance = _normalize(self.inventory["_guidance"]).lower()
        self.assertIn("deploy", guidance)
        subtypes = _normalize(self.doc["document_control"]["_guidance"]).lower()
        self.assertIn(
            "file_manifest + execution_commands not required",
            subtypes,
            "the deploy carve-out above is derived from document_control's subtype "
            "table; if that table changed, the carve-out is stale",
        )

    def test_planned_must_not_survive_a_session(self) -> None:
        self.assertRegex(
            _normalize(self.inventory["_guidance"]),
            r"`planned` MUST\s+NOT survive a session",
            "the lifecycle is only a contract if the transition is mandatory; without "
            "this, `planned` becomes the new permanent stale value `created` used to be",
        )

    def test_the_sibling_action_carrier_is_not_extended(self) -> None:
        """GD-25 states this as a decision; a stated non-decision with no guard is
        exactly the shape that produced #609."""
        actions = re.findall(r"^\s*action:\s*\S+\s*#\s*(.*?)\s*$", self.source, re.MULTILINE)
        self.assertEqual(len(actions), 1, f"expected one `action:` enum, found {actions}")
        self.assertEqual(
            [v.strip() for v in actions[0].split("|")],
            ["created", "modified"],
            "`session_handoff.sessions[].files_touched[].action` records what a session "
            "did to a file; `planned` there is a contradiction in terms (GD-25)",
        )


class PlatformSurfacesAgree(unittest.TestCase):
    """Every ``doc-iplan*`` surface states the seed, and none re-teaches the empty
    block or a built status at Draft."""

    def _skill_docs(self):
        return sorted(PLUGIN_SKILLS.glob(IPLAN_SKILL_GLOB))

    def test_the_vendored_bundle_matches_the_spec(self) -> None:
        """Restates ``test_plugin_framework_bundle.py``'s byte-identity coverage for
        this one file, so a drift failure names the carrier rather than a path. It
        adds no coverage: the bundle guard already caught ``2943bf3b``'s drift."""
        self.assertEqual(
            PLUGIN_BUNDLE_TEMPLATE.read_text(encoding="utf-8"),
            IPLAN_TEMPLATE.read_text(encoding="utf-8"),
            "the plugin's vendored IPLAN template drifted from framework/ — run "
            "`bash tools/sync-plugin-framework.sh`",
        )

    def test_every_iplan_skill_is_scanned(self) -> None:
        dirs = sorted(p.name for p in PLUGIN_SKILLS.glob(IPLAN_SKILL_DIRS) if p.is_dir())
        self.assertEqual(
            len(dirs),
            EXPECTED_IPLAN_SKILLS,
            f"expected {EXPECTED_IPLAN_SKILLS} doc-iplan* skills, found {dirs} — update "
            "EXPECTED_IPLAN_SKILLS deliberately, so a new skill cannot escape the rules "
            "below silently",
        )
        self.assertTrue(self._skill_docs(), "the markdown glob matched nothing")

    def test_no_skill_instructs_an_empty_code_inventory(self) -> None:
        for doc in self._skill_docs():
            rel = doc.relative_to(PLUGIN_SKILLS)
            for sentence in _sentences(doc.read_text(encoding="utf-8")):
                match = _EMPTY_INVENTORY.search(sentence)
                if not match or _PROHIBITION.search(sentence):
                    continue
                with self.subTest(doc=str(rel)):
                    self.fail(
                        f"{rel} instructs an empty code_inventory: {sentence!r} — "
                        "GD-25 seeds it `planned` instead"
                    )

    def test_no_skill_ties_a_built_status_to_a_draft_seed(self) -> None:
        """The template can be correct while the skill overrides it — which is the
        surface an authoring agent actually reads."""
        for doc in self._skill_docs():
            rel = doc.relative_to(PLUGIN_SKILLS)
            for sentence in _sentences(doc.read_text(encoding="utf-8")):
                if "code_inventory" not in sentence:
                    continue
                match = _DRAFT_BUILT_STATUS.search(sentence)
                if not match or _PROHIBITION.search(sentence):
                    continue
                with self.subTest(doc=str(rel)):
                    self.fail(
                        f"{rel} seeds a Draft code_inventory with a built status: "
                        f"{sentence!r} — a Draft carries `planned` (GD-25/#601)"
                    )

    def test_every_iplan_skill_states_the_planned_seed(self) -> None:
        """The positive half. A negative rule proves only that a surface stopped
        saying the old thing; GD-25 claims all four say the new one."""
        for skill in sorted(PLUGIN_SKILLS.glob(f"{IPLAN_SKILL_DIRS}/SKILL.md")):
            with self.subTest(skill=skill.parent.name):
                body = _normalize(skill.read_text(encoding="utf-8"))
                self.assertRegex(
                    body,
                    r"`?planned`?",
                    f"{skill.parent.name} never mentions `planned` — GD-25 says all "
                    f"{EXPECTED_IPLAN_SKILLS} IPLAN skills move with the template",
                )
                self.assertRegex(
                    body,
                    r"code_inventory[^.]{0,120}?planned|planned[^.]{0,120}?code_inventory",
                    f"{skill.parent.name} mentions `planned` but not in connection with "
                    "`code_inventory` — the seed instruction is what GD-25 claims shipped",
                )

    def test_the_layer_readme_describes_the_seed(self) -> None:
        readme = _normalize(IPLAN_README.read_text(encoding="utf-8")).lower()
        for phrase in ("seeded `planned`", "one entry per `file_manifest` path"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, readme)


class DecisionIsRecorded(unittest.TestCase):
    def test_gd_25_records_the_decision(self) -> None:
        """A heading is not a decision: assert the body carries the rule."""
        decisions = GOVERNANCE_DECISIONS.read_text(encoding="utf-8")
        self.assertRegex(
            decisions,
            r"(?m)^## GD-25 [-—] ",
            "a spec vocabulary change is a governance decision; GD-25 records it",
        )
        body = _normalize(decisions.split("## GD-25")[1].split("\n## GD-24")[0])
        for value in LIFECYCLE:
            with self.subTest(value=value):
                self.assertIn(value, body)
        self.assertRegex(
            body,
            r"(?i)one entry per §2 `file_manifest` path",
            "GD-25 must state the Draft-seed rule, not merely that a value was added",
        )


if __name__ == "__main__":
    unittest.main()
