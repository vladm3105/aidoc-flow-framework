"""Conformance: no platform authoring surface instructs in-prompt SHA-256 (#342).

The platform-side counterpart to `test_element_id_layer_contract.py`, which locks
the same property over `framework/layers/**` and whose docstring says explicitly
that it does NOT cover these files.

**Why this is a defect and not a style nit.** `plans/PROVISIONAL-IDS-002-PLAN.md`
ruled that real hashes come from a deterministic tool pass, "not from prompting",
because an LLM cannot compute SHA-256 reliably. An authoring surface that says
"take the first 4 hex of SHA256(...)" therefore asks the engine to do something it
cannot do correctly, and the emitted ID passes `ELEM_FORM` regardless — so nothing
fails, and the wrong ID ships. A founder-run agent hit exactly this, found no
callable, and wrote its own ad-hoc hash script.

What replaced the instruction (founder decision, 2026-07-26):

  * **BRD** — the one layer with a defined field-extraction boundary — surfaces
    CALL the generator: `python -m sdd_doc_lint.rehash --compute`.
  * **PRD / EARS / BDD / ADR / TDD** — no defined boundary, so there is nothing
    correct to pass a generator. Surfaces instruct a **stable opaque 4-hex
    identifier**, distinct within its section, and say the hash form is the
    canonicalization TARGET produced by a tool pass. No `id_state: provisional`:
    canonicalization cannot run for these layers yet, so a provisional mark could
    never be discharged and would raise a permanent, un-clearable `PROV01`.

This guard locks the *negative* property only — that no surface tells an engine to
hash. It cannot verify that what replaced the instruction is correct; that is what
review is for. Stated plainly so a green run is not over-read, mirroring the scope
honesty of the framework-side lock.
"""

import re
import unittest

from _spec import REPO_ROOT

PLUGIN_SKILLS = REPO_ROOT / "platforms" / "claude-code-plugin" / "skills"
HERMES_PROMPTS = REPO_ROOT / "platforms" / "hermes" / "prompts" / "templates"
HERMES_REFERENCES = (
    REPO_ROOT
    / "platforms"
    / "hermes"
    / "agent-skills"
    / "spec-driven-development"
    / "sdd-orchestrator"
    / "references"
)

# An instruction to derive an element ID by hashing. Deliberately narrow: it must
# match the *derivation* forms the 19 surfaces used, not every mention of SHA-256.
INSTRUCTION = re.compile(
    r"""(
          hex\s+of\s+SHA-?256      # "first 4 hex of SHA256"
        | SHA-?256\s*\(            # "SHA256(key)"
        | SHA-?256\s+of\b          # "SHA256 of the case content"
        | SHA-?256\s*,\s*first     # "(SHA256, first 4 hex ...)"
        | \d\s*-\s*char\s+SHA-?256 # "4-char SHA256"
        | SHA-?256\s+\d+\s*-\s*char
    )""",
    re.IGNORECASE | re.VERBOSE,
)

# A clause telling the author NOT to hash is the fix, not the defect — but it must
# be REMOVED from the line before testing, never used to skip the whole line.
#
# Markdownlint reflows these surfaces into single long lines, so the corrected
# text and any future reintroduction land on the SAME line. A line-scoped "skip if
# a negation appears anywhere" check would then suppress the very regression this
# guard exists to catch. A mutation test proved exactly that: reintroducing
# "first 4 hex of SHA256" next to the negation passed a line-scoped version.
#
# So: excise the negation clause, then see whether an instruction still remains.
# The clause ENDS at its own SHA-256 mention — a trailing `[^.;]*` would swallow a
# reintroduced instruction sitting after the negation on the same reflowed line.
NEGATION_CLAUSE = re.compile(
    r"(do\s+\*{0,2}not\*{0,2}|never)\s+(compute|re-?derive)[^.;]{0,40}?SHA-?256",
    re.IGNORECASE,
)

# Genuine non-element-ID uses. Each needs a reason, not just a path.
ALLOWED = {
    # Webhook signing algorithms in a worked BRD example — domain content about
    # partner integrations, nothing to do with element IDs.
    "HMAC-SHA256",
}


# Dated session records are HISTORY, not authoring surfaces: they record what an
# agent did on a given day. Rewriting one to satisfy a present-day rule would
# falsify the record — the same principle that forbids hand-editing example
# artifacts and freezes the `legacy/` archive. They are excluded by name (a
# `*-session-YYYY-MM-DD.md` shape), never by silently narrowing the glob, so the
# exemption is visible and a NEW live reference cannot slip through with it.
_SESSION_RECORD = re.compile(r"-session-\d{4}-\d{2}-\d{2}\.md$")


def _surfaces():
    """Every authoring/fixing surface that could carry the instruction."""
    yield from sorted(PLUGIN_SKILLS.glob("doc-*/SKILL.md"))
    yield from sorted(HERMES_PROMPTS.glob("*/*.md"))
    # Loaded references ship runnable code an agent is pointed at, so they count
    # as authoring surfaces even though they are not prompts.
    for path in sorted(HERMES_REFERENCES.glob("*.md")):
        if _SESSION_RECORD.search(path.name):
            continue
        yield path


class NoInPromptHashing(unittest.TestCase):
    def test_no_surface_instructs_the_engine_to_compute_sha256(self):
        offenders = []
        for path in _surfaces():
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                # Excise negation clauses first, then test what remains.
                probe = NEGATION_CLAUSE.sub("", line)
                if not INSTRUCTION.search(probe):
                    continue
                if any(tok in probe for tok in ALLOWED):
                    continue
                rel = path.relative_to(REPO_ROOT)
                offenders.append(f"{rel}:{lineno}: {line.strip()[:90]}")
        self.assertEqual(
            offenders,
            [],
            "these authoring surfaces instruct the engine to compute SHA-256 in-prompt, "
            "which no LLM does reliably and which PROVISIONAL-IDS-002 already ruled out. "
            "BRD surfaces should CALL `rehash --compute`; the other five layers should "
            "emit a stable opaque 4-hex identifier and cite "
            "governance/ID_NAMING_STANDARDS.md as the authority:\n  " + "\n  ".join(offenders),
        )

    def test_the_guard_would_catch_a_regression(self):
        """The pattern must actually match the form the surfaces used.

        A negative-property guard that matches nothing is indistinguishable from a
        passing one, so assert it fires on the exact strings this change removed.
        """
        for sample in (
            "hash = first 4 hex of SHA256(`{doc_id}:{section_id}`)",
            "ID = `BRD.{doc_id}.{section_id}.<first 4 hex of SHA256(key)>`",
            "first 4 hex of SHA256 of the case content",
            "| xxxx | Content hash (SHA256, first 4 hex) |",
            '"""4-char SHA256 hex from text"""',
        ):
            with self.subTest(sample=sample[:40]):
                self.assertTrue(INSTRUCTION.search(sample), f"guard missed: {sample}")

    def test_the_guard_does_not_fire_on_legitimate_mentions(self):
        for sample in (
            "- Per-partner webhook specifications (HMAC-SHA256 vs SHA512)",
            "Do **not** compute SHA-256 in this prompt — call the generator.",
            "never compute SHA256 by hand; canonicalization is a tool pass",
        ):
            with self.subTest(sample=sample[:40]):
                probe = NEGATION_CLAUSE.sub("", sample)
                fired = INSTRUCTION.search(probe) and not any(t in probe for t in ALLOWED)
                self.assertFalse(fired, f"false positive on: {sample}")

    def test_a_negation_does_not_mask_a_reintroduction_on_the_same_line(self):
        """The hole a mutation test found: markdownlint reflows these surfaces into
        single long lines, so a corrected sentence and a reintroduced instruction
        share one line. Excising the negation clause must leave the instruction
        visible, or the guard silently stops guarding."""
        line = (
            "Emit a stable identifier. Do **not** compute SHA-256 in this prompt — "
            "hash = first 4 hex of SHA256 of the content."
        )
        probe = NEGATION_CLAUSE.sub("", line)
        self.assertTrue(
            INSTRUCTION.search(probe),
            "a reintroduced instruction was masked by a negation on the same line",
        )


if __name__ == "__main__":
    unittest.main()
