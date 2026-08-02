"""Release: CHANGELOG.md has an entry for the current VERSION."""

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))
from _spec import FRAMEWORK

# CHANGELOG.md lives at the repo root, not inside framework/
CHANGELOG = FRAMEWORK.parent / "CHANGELOG.md"

PLACEHOLDER_TOKENS = ("TBD", "TODO:", "FILL IN")

_HEADING = re.compile(r"^(#{2,3})\s")
_FENCE_LINE = re.compile(r"^\s{0,3}(```|~~~)")
_INLINE_CODE = re.compile(r"`+[^`\n]+`+")


def strip_code(text: str) -> str:
    """Blank out fenced blocks and inline code spans, preserving line count.

    A token inside backticks is a *mention* of the literal, not an unfilled
    placeholder. Markdown already draws that distinction; the gate honours it
    rather than inventing an allow-marker.

    Scanned line-by-line rather than by a multi-line regex, because a regex
    pairs an *unterminated* fence with the next opening fence and blanks the
    prose between them — over-stripping hides real placeholders, which is the
    dangerous direction for a gate. A line scanner instead blanks an
    unterminated fence to end-of-file, which is how markdown renders it.

    Line count is preserved exactly — callers align indices against the
    original, so ``split("\\n")`` is used rather than ``splitlines()``, which
    would drop a trailing empty line and shift the tail.
    """
    out: list[str] = []
    fence: str | None = None
    for line in text.split("\n"):
        marker = _FENCE_LINE.match(line)
        if fence is None:
            if marker:
                fence = marker.group(1)
                out.append("")
            else:
                out.append(_INLINE_CODE.sub(" ", line))
            continue
        if marker and marker.group(1) == fence:
            fence = None
        out.append("")
    return "\n".join(out)


def placeholders_in(text: str) -> list[str]:
    """Return the placeholder tokens appearing in ``text`` as unfilled placeholders.

    A token counts when it is outside any code span and not embedded in a
    longer *word*. The boundary is alphanumeric-only on purpose: punctuation
    and hyphens do **not** exempt a token, so ``2026-08-TBD`` in a dated
    heading — the likeliest unfilled placeholder in a changelog — still fails,
    as do ``_TBD_`` and ``**TBD**``.

    That leaves exactly one way to name a token without tripping the gate:
    put it in backticks. Prose citing this gate's own backlog ID must write
    ``RELEASE-GATE-TBD-FALSE-POSITIVE`` in code formatting, which is the
    correct markdown treatment for an identifier regardless.
    """
    body = strip_code(text)
    found = []
    for token in PLACEHOLDER_TOKENS:
        # A token ending in punctuation (``TODO:``) needs no trailing boundary;
        # requiring one would miss ``TODO:write this``.
        trailing = r"(?![A-Za-z0-9])" if token[-1].isalnum() else ""
        if re.search(rf"(?<![A-Za-z0-9]){re.escape(token)}{trailing}", body):
            found.append(token)
    return found


def newest_entry(changelog: str) -> str:
    """Return the slice of ``changelog`` a release is publishing *now*.

    ``CHANGELOG.md`` is append-only: past entries are never rewritten, so a
    placeholder token in one is *history*, not an orphan. The literal ``TBD``
    at the time of writing sits inside a quoted historical commit message
    recording a past review that fixed such a placeholder — text that is
    correct and must not be edited.

    Scoping to ``## [Unreleased]`` does not help: this repo keeps every
    unreleased entry under that one heading (~2,700 lines of them), so the
    quoted text is inside it. The boundary that works is the *entry*::

        ## [Unreleased]                 <- start (first level-2 heading …
                                        …  with a body; an emptied one is
                                           skipped, see below)
        ### Fixed — … (2026-08-02)      <- the entry being published
        …body…
        ### Fixed — … (2026-08-01)      <- stop (second level-3 heading)

    Two shapes this has to survive, both of which occur in this workspace:

    * **A release cut empties ``## [Unreleased]``** and promotes the entry to
      its own level-2 section — ``platforms/claude-code-plugin/CHANGELOG.md``
      does this at its cuts. A section with no body is therefore skipped
      rather than returned, because returning it would scan nothing and pass
      vacuously.
    * **A section may carry no level-3 heading at all**, in which case the
      whole section is the entry.

    Headings are located in the *code-stripped* text so that a ``##`` line
    inside a fenced example cannot truncate the entry early and leave a real
    placeholder below it unscanned. Slicing then uses the original lines,
    which is sound because ``strip_code`` preserves line count.

    **Accepted limitations, stated rather than hidden.** Only the newest entry
    is scanned, so a single PR adding *two* level-3 entries has only the first
    checked; that matches this repo's one-entry-per-PR convention but nothing
    enforces it. And in the window after a release cut empties
    ``## [Unreleased]`` and before the next entry is written, the newest
    body-bearing section is a *released* one — append-only text that cannot be
    edited if it were ever to trip the gate.

    Raises ``ValueError`` when no level-2 section with a body exists — a
    placeholder gate that scanned nothing must fail, not silently pass.
    """
    lines = changelog.split("\n")
    scanned = strip_code(changelog).split("\n")
    headings = [(i, len(m[1])) for i, line in enumerate(scanned) if (m := _HEADING.match(line))]

    for start in [i for i, level in headings if level == 2]:
        section_end = next((i for i, level in headings if i > start and level == 2), len(lines))
        entries = [i for i, level in headings if start < i < section_end and level == 3]
        stop = entries[1] if len(entries) > 1 else section_end
        block = lines[start:stop]
        if any(line.strip() for line in block[1:]):
            return "\n".join(block)

    raise ValueError(
        "CHANGELOG.md has no level-2 section with a body; cannot locate the newest entry"
    )


class StripCodeTests(unittest.TestCase):
    def test_removes_inline_code_spans(self):
        self.assertNotIn("TBD", strip_code("the literal `TBD` is checked"))

    def test_removes_backtick_fenced_blocks(self):
        self.assertNotIn("TBD", strip_code("before\n```\nTBD\n```\nafter"))

    def test_removes_tilde_fenced_blocks(self):
        self.assertNotIn("TBD", strip_code("before\n~~~\nTBD\n~~~\nafter"))

    def test_a_tilde_line_does_not_close_a_backtick_fence(self):
        # The mismatched marker must stay inside the fence, so the TBD between
        # them is blanked and the prose after the real close survives.
        stripped = strip_code("```\n~~~\nTBD\n```\nafter")
        self.assertNotIn("TBD", stripped)
        self.assertIn("after", stripped)

    def test_a_fence_indented_up_to_three_spaces_is_still_a_fence(self):
        # CommonMark allows 0-3 spaces before a fence marker; the `\s{0,3}`
        # allowance in _FENCE_LINE is what honours that.
        self.assertNotIn("TBD", strip_code("intro\n   ```\n   TBD\n   ```\nafter"))

    def test_an_unterminated_fence_blanks_to_end_of_file(self):
        self.assertNotIn("TBD", strip_code("intro\n```\nTBD\nstill inside"))

    def test_preserves_line_count_exactly(self):
        # newest_entry aligns heading indices from the stripped text against
        # the original lines; a dropped trailing line would shift the tail.
        for src in ("a\n```\nTBD\n```\nb", "one `x` two", "```\nunterminated\n", "trailing\n"):
            with self.subTest(src=src):
                self.assertEqual(len(strip_code(src).split("\n")), len(src.split("\n")))

    def test_keeps_prose_outside_code(self):
        self.assertIn("TBD", strip_code("a bare TBD and a `quoted` one"))

    def test_does_not_over_strip_between_two_code_spans(self):
        # Guards the greedy-regex failure mode: `a` … TBD … `b` must not be
        # collapsed into one span, which would hide the placeholder between them.
        self.assertIn("TBD", strip_code("see `one` then TBD then `two`"))


class PlaceholdersInTests(unittest.TestCase):
    def test_the_vocabulary_is_exactly_these_three(self):
        # Asserted against literals, NOT by iterating PLACEHOLDER_TOKENS —
        # a test that loops the tuple it claims to pin agrees with any
        # truncation of it and pins nothing.
        self.assertEqual(PLACEHOLDER_TOKENS, ("TBD", "TODO:", "FILL IN"))

    def test_a_bare_tbd_is_a_placeholder(self):
        self.assertEqual(placeholders_in("- Version: TBD here"), ["TBD"])

    def test_a_bare_todo_is_a_placeholder(self):
        self.assertEqual(placeholders_in("- TODO: write the entry"), ["TODO:"])

    def test_a_todo_needs_no_trailing_boundary(self):
        self.assertEqual(placeholders_in("- TODO:write the entry"), ["TODO:"])

    def test_a_bare_fill_in_is_a_placeholder(self):
        self.assertEqual(placeholders_in("- Release date: FILL IN"), ["FILL IN"])

    def test_backticked_mentions_are_not_placeholders(self):
        self.assertEqual(placeholders_in("checks `TBD`, `TODO:` and `FILL IN`"), [])

    def test_a_fenced_mention_is_not_a_placeholder(self):
        self.assertEqual(placeholders_in("example:\n```\nTBD\n```\n"), [])

    def test_a_hyphenated_date_placeholder_still_fails(self):
        # The likeliest real placeholder in a changelog, and the reason the
        # boundary is alphanumeric-only rather than \w or [\w-].
        self.assertEqual(placeholders_in("## [0.25.0] — 2026-08-TBD"), ["TBD"])

    def test_emphasis_wrapping_does_not_exempt_a_token(self):
        for wrapped in ("_TBD_", "__TBD__", "*TBD*", "**TBD**", "(TBD)", '"TBD"', "TBD."):
            with self.subTest(wrapped=wrapped):
                self.assertEqual(placeholders_in(f"- Version: {wrapped}"), ["TBD"])

    def test_a_token_inside_a_longer_word_is_not_a_placeholder(self):
        self.assertEqual(placeholders_in("the TBDish approach and FILL INSIDE"), [])

    def test_a_token_preceded_by_a_letter_is_not_a_placeholder(self):
        # The LEADING boundary, which suffix-only cases above do not exercise.
        self.assertEqual(placeholders_in("the aTBD marker and xFILL IN"), [])

    def test_matching_is_case_sensitive(self):
        # Lowercasing the match would fire on ordinary prose: "fill in the form".
        self.assertEqual(placeholders_in("please fill in the form; tbd later"), [])

    def test_an_unbackticked_identifier_is_reported(self):
        # Consequence of the alphanumeric-only boundary, pinned so it is a
        # decision rather than a surprise: prose must backtick the ID.
        self.assertEqual(placeholders_in("closes RELEASE-GATE-TBD-FALSE-POSITIVE"), ["TBD"])
        self.assertEqual(placeholders_in("closes `RELEASE-GATE-TBD-FALSE-POSITIVE`"), [])

    def test_clean_text_yields_nothing(self):
        self.assertEqual(placeholders_in("nothing to declare"), [])


class NewestEntryTests(unittest.TestCase):
    """The slicing helper — the gate is only as good as its boundary."""

    CHANGELOG = "\n".join(
        [
            "# Changelog",
            "preamble PREAMBLE-MARK",  # above the first level-2 heading: out of scope
            "",
            "## [Unreleased]",
            "",
            "### Added — the entry being published (2026-08-02)",
            "",
            "- current body",
            "",
            "### Added — a previous entry STOP-MARK (2026-08-01)",
            "",
            "- historical body",
            "",
            "## [1.0.0] — 2026-05-21",
            "",
            "- released body",
        ]
    )

    def test_starts_at_the_first_level_2_heading(self):
        self.assertTrue(newest_entry(self.CHANGELOG).startswith("## [Unreleased]"))

    def test_includes_the_entry_being_published(self):
        self.assertIn("current body", newest_entry(self.CHANGELOG))

    def test_excludes_the_preceding_entry(self):
        self.assertNotIn("historical body", newest_entry(self.CHANGELOG))

    def test_excludes_the_stop_heading_line_itself(self):
        # Off-by-one guard: real entry headings quote their subject, so
        # including the boundary line would fail on the PREVIOUS entry's title.
        self.assertNotIn("STOP-MARK", newest_entry(self.CHANGELOG))

    def test_excludes_released_sections(self):
        self.assertNotIn("released body", newest_entry(self.CHANGELOG))

    def test_excludes_the_preamble(self):
        self.assertNotIn("PREAMBLE-MARK", newest_entry(self.CHANGELOG))

    def test_a_level_3_heading_above_the_first_level_2_does_not_become_the_start(self):
        stray = "### stray STRAY-MARK\n\n- stray body\n\n## [Unreleased]\n\n- real body\n"
        entry = newest_entry(stray)
        self.assertTrue(entry.startswith("## [Unreleased]"))
        self.assertNotIn("STRAY-MARK", entry)

    def test_a_level_1_heading_does_not_become_the_start(self):
        doc = "# Changelog TITLE-MARK\n\n## [Unreleased]\n\n- real body\n"
        self.assertNotIn("TITLE-MARK", newest_entry(doc))

    def test_a_level_4_heading_does_not_end_the_entry(self):
        doc = "## [Unreleased]\n\n### Added — entry\n\n#### detail\n\n- deep body\n"
        self.assertIn("deep body", newest_entry(doc))

    def test_a_heading_marker_needs_a_space(self):
        doc = "## [Unreleased]\n\n### Added — entry\n\n###NotAHeading\n\n- still mine\n"
        self.assertIn("still mine", newest_entry(doc))

    def test_a_heading_inside_a_fence_does_not_end_the_entry(self):
        # Without code-stripping the example heading truncates the slice and
        # the placeholder below it is never scanned — a silent false green.
        doc = (
            "## [Unreleased]\n\n### Added — entry\n\n"
            "```markdown\n### Added — example\n```\n\n- Version: TBD\n"
        )
        self.assertIn("TBD", newest_entry(doc))

    def test_a_sole_entry_runs_to_end_of_file(self):
        sole = "# Changelog\n\n## [Unreleased]\n\n### Added — only entry\n\n- body\n"
        self.assertIn("- body", newest_entry(sole))

    def test_an_entry_with_no_level_3_heading_stops_at_the_next_release(self):
        bare = "## [Unreleased]\n\n- loose body\n\n## [1.0.0]\n\n- released body\n"
        entry = newest_entry(bare)
        self.assertIn("loose body", entry)
        self.assertNotIn("released body", entry)

    def test_an_emptied_unreleased_section_is_skipped_not_returned(self):
        # The post-release-cut shape: platforms/claude-code-plugin/CHANGELOG.md
        # promotes the entry to a level-2 section and leaves [Unreleased] bare.
        # Returning the empty section would scan nothing and pass vacuously.
        cut = "## [Unreleased]\n\n## [0.25.0] — 2026-08-02\n\n### Added — the cut entry\n\n- body\n"
        entry = newest_entry(cut)
        self.assertTrue(entry.startswith("## [0.25.0]"))
        self.assertIn("- body", entry)

    def test_a_whitespace_only_section_counts_as_empty(self):
        # `line.strip()` is what makes this an empty section. Without it a
        # release cut that leaves an indented blank line behind returns the
        # bare [Unreleased] and the real entry below goes unscanned.
        cut = "## [Unreleased]\n\n   \n\n## [0.25.0]\n\n### Added\n\n- Version: TBD\n"
        entry = newest_entry(cut)
        self.assertTrue(entry.startswith("## [0.25.0]"))
        self.assertEqual(placeholders_in(entry), ["TBD"])

    def test_the_slice_is_original_text_not_code_stripped_text(self):
        # Headings are located in stripped text; the slice must come from the
        # original, or every code span in a published entry would be blanked.
        doc = "## [Unreleased]\n\n### Added — entry\n\n- see `inline code` here\n"
        self.assertIn("`inline code`", newest_entry(doc))

    def test_no_level_2_heading_raises_rather_than_scanning_nothing(self):
        with self.assertRaises(ValueError):
            newest_entry("# Changelog\n\nno sections here\n")

    def test_only_empty_level_2_sections_raises(self):
        with self.assertRaises(ValueError):
            newest_entry("## [Unreleased]\n\n## [1.0.0]\n")


class ChangelogEntryTests(unittest.TestCase):
    def test_changelog_exists(self):
        self.assertTrue(CHANGELOG.exists(), f"CHANGELOG.md missing at {CHANGELOG}")

    def test_changelog_has_entry_for_current_version(self):
        if not CHANGELOG.exists():
            self.skipTest("CHANGELOG.md not present")
        version = (FRAMEWORK / "VERSION").read_text(encoding="utf-8").strip()
        changelog = CHANGELOG.read_text(encoding="utf-8")
        # The current version's entry may appear in either form (RELEASE-CHANGELOG-
        # TEST-CONVENTION-GAP):
        #   * a released top-level heading — ``## [0.30.0]`` / ``## 0.30.0``; or
        #   * an ``## [Unreleased]`` subsection heading naming the version, the
        #     convention this repo uses — ``### Added — … framework spec X → 0.30.0``.
        # Match the version in any level-2/3 heading line, not just a bracketed
        # top-level one. The trailing lookahead avoids a prefix match (0.30.0 in
        # 0.30.01).
        #
        # Deliberately scans the WHOLE file: this is a presence check, and the
        # heading may be a released section far below the newest entry.
        pattern = rf"^#{{2,3}}\s+.*{re.escape(version)}(?![\d.])"
        self.assertRegex(
            changelog,
            re.compile(pattern, re.MULTILINE),
            f"CHANGELOG.md has no heading naming the current version {version} "
            f"(neither a released '## [{version}]' nor an '[Unreleased]' '### … {version}' entry)",
        )

    def test_no_placeholder_orphans(self):
        if not CHANGELOG.exists():
            self.skipTest("CHANGELOG.md not present")
        found = placeholders_in(newest_entry(CHANGELOG.read_text(encoding="utf-8")))
        self.assertEqual(
            found,
            [],
            f"the newest CHANGELOG.md entry contains unfilled placeholder(s) {found}. "
            "If the entry is *describing* a token rather than leaving one unfilled, "
            "wrap it in backticks — a bare occurrence reads as an unfilled placeholder.",
        )
