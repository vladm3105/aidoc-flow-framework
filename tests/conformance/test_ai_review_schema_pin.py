"""Conformance: the ai-review config's ``$schema`` tag tracks its caller's pin.

`.github/ai-review/config.json` declares a **machine-read** canon pin — the
`$schema` URL names a `ci/vX.Y.Z` tag — and **no tool in the toolchain repairs
or reports it**:

* ``install/install.sh --repin`` rewrites ``uses:`` lines only, so a canon bump
  moves the caller and leaves the config behind.
* canon marks this file ``safe_to_replace: false`` in
  `aidoc-flow-ci install/templates/manifest.json`, so ``--update --non-interactive``
  (and any no-TTY run) keeps the local copy. An *interactive* ``--update`` does
  prompt to replace it — with canon's whole template body, which would discard
  this repo's local policy blocks. Answer keep.
* ``sync/check-pin-currency.sh`` walks ``.github/workflows/`` only — on both its
  local and its fleet path — so this pin is outside its scan by construction.

Regression cover: **#606** — the config sat at ``ci/v2.16.0`` while
`.github/workflows/ai-review.yml` had been carried across the v3 major boundary
to ``ci/v3.0.0`` by Dependabot. Latent rather than live (the reusable resolves policy from
`trust_config_repo`, not from this file), but the stale pin breaks exactly the
path the file exists for: pointing `trust_config_repo` at this repo.

ANCHOR: `ai-review.yml`, because this config is its namesake and its is the
``version == 2`` assertion the config's own ``_note`` cites. `composition.yml`
also reads this file — canon's `composition.yml` fetches it from this repo by
API (the FT-6 path) — at its own, currently different, tag. It is deliberately
not the anchor; do not "fix" the pin toward it.

The invariant is an **equality between two files**, not a currency check
against canon's latest — a caller deliberately held back a major must be able
to hold its schema back with it. So a future canon bump is free to move both,
and is not free to move one.

ACCEPTED SHAPES, deliberately narrow. Only ``ci/vMAJOR.MINOR.PATCH`` (no
prerelease suffix) and only the plain ``owner/repo/<ref>/path`` raw URL form
(not ``refs/tags/``). A SHA-pinned caller carrying canon's own
``@<40hex> # ci/vX.Y.Z`` comment is likewise refused — no call site in this repo
uses that shape today, and refusal is a loud failure, not a silent pass.
**Widening either regex requires taking `test_the_matchers_reject_non_pins`
with it**, or the guard starts accepting a non-pin (``main``, a fork) on both
sides and equality is satisfied by a state that is not a pin at all.
"""

from __future__ import annotations

import json
import re
import unittest

import yaml
from _spec import REPO_ROOT

CONFIG = REPO_ROOT / ".github" / "ai-review" / "config.json"
CALLER = REPO_ROOT / ".github" / "workflows" / "ai-review.yml"
CONFIG_REL = CONFIG.relative_to(REPO_ROOT)
CALLER_REL = CALLER.relative_to(REPO_ROOT)

# `…/aidoc-flow-ci/ci/v3.0.0/schemas/ai-review-config-v2.schema.json`
SCHEMA_URL = re.compile(
    r"^https://raw\.githubusercontent\.com/vladm3105/aidoc-flow-ci/"
    r"(?P<tag>ci/v\d+\.\d+\.\d+)/schemas/(?P<file>[\w.-]+\.schema\.json)$"
)
# `vladm3105/aidoc-flow-ci/.github/workflows/ai-review.yml@ci/v3.0.0`
USES = re.compile(
    r"^vladm3105/aidoc-flow-ci/\.github/workflows/ai-review\.yml@(?P<tag>ci/v\d+\.\d+\.\d+)$"
)

# Non-pins the matchers must refuse. Each is a state that would otherwise let
# the equality assertion pass while the pin is gone: a floating ref, a fork, or
# a different reusable at a coincidentally equal tag.
REJECTED_SCHEMA_URLS = (
    "https://raw.githubusercontent.com/vladm3105/aidoc-flow-ci/main/schemas/ai-review-config-v2.schema.json",
    "https://raw.githubusercontent.com/acme/aidoc-flow-ci/ci/v3.0.0/schemas/ai-review-config-v2.schema.json",
    "https://raw.githubusercontent.com/vladm3105/aidoc-flow-ci/ci/v3.0/schemas/ai-review-config-v2.schema.json",
)
REJECTED_USES = (
    "vladm3105/aidoc-flow-ci/.github/workflows/ai-review.yml@main",
    "acme/aidoc-flow-ci/.github/workflows/ai-review.yml@ci/v3.0.0",
    "vladm3105/aidoc-flow-ci/.github/workflows/composition.yml@ci/v3.0.0",
)


class AiReviewSchemaPinTracksCaller(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads(CONFIG.read_text(encoding="utf-8"))
        cls.workflow = yaml.safe_load(CALLER.read_text(encoding="utf-8"))

    def _schema_match(self):
        """Extracted, not asserted-through: a missing `$schema` or a URL shape
        this test cannot parse must FAIL here rather than compare None to None
        further down and pass vacuously."""
        url = self.config.get("$schema")
        self.assertIsNotNone(
            url, f"{CONFIG_REL} declares no $schema — the pin this module guards is gone"
        )
        match = SCHEMA_URL.match(url)
        self.assertIsNotNone(
            match,
            f"$schema is not a recognizable canon schema URL: {url!r} — this guard accepts "
            "only a ci/vX.Y.Z tag in the plain raw-URL form; see the module docstring",
        )
        return match

    def _caller_tag(self) -> str:
        uses = self.workflow.get("jobs", {}).get("call", {}).get("uses")
        self.assertIsNotNone(uses, f"{CALLER_REL} has no jobs.call.uses — re-point this guard")
        match = USES.match(uses)
        self.assertIsNotNone(
            match,
            f"jobs.call.uses is not a recognizable canon pin: {uses!r} — this guard accepts "
            "only @ci/vX.Y.Z, not a SHA pin or a floating ref; see the module docstring",
        )
        return match.group("tag")

    def test_schema_tag_equals_caller_tag(self):
        """#606: the two parted across a major boundary — the config two majors
        behind canon, one behind its own caller — with nothing to report it."""
        schema_tag = self._schema_match().group("tag")
        caller_tag = self._caller_tag()
        self.assertEqual(
            schema_tag,
            caller_tag,
            f"{CONFIG_REL} pins its $schema at {schema_tag} while {CALLER_REL} calls "
            f"{caller_tag}. Move both in one commit — no --repin or --update repairs this URL.",
        )

    def test_schema_url_names_the_declared_version(self):
        """The relational half of the guard, and the reason tag-equality alone
        is not enough: equality is satisfiable by pointing the URL at any file
        under `schemas/`. Derived from the declared version rather than
        hardcoded, so a future contract bump cannot be "fixed" by editing two
        constants in lockstep while the coupling goes on untested."""
        version = self.config.get("version")
        self.assertEqual(
            self._schema_match().group("file"),
            f"ai-review-config-v{version}.schema.json",
            f'config declares "version": {version!r} but its $schema names a different contract file',
        )

    def test_declared_version_is_supported_by_canon(self):
        """Currency, not relation — a separate invariant from the test above,
        and it fails for a different reason. Canon asserts `version == 2`
        before reading any field (CI-0014), inside the block it marks
        `>>> CI0014-SCHEMA-ASSERT >>>` — cited by marker rather than line
        number, because that block occurs twice per reusable (trust job and
        review job) and moves every release. A config declaring anything else
        hard-fails ai-review rather than becoming authoritative. Bump this only
        when canon raises SUPPORTED."""
        self.assertEqual(
            self.config.get("version"),
            2,
            "config declares a schema version canon does not support (canon: SUPPORTED=2)",
        )

    def test_the_matchers_reject_non_pins(self):
        """Guards the guard: these two regexes ARE the detector, and the live
        files matching them proves nothing about what they refuse. Without
        this, broadening either one — the obvious edit when accommodating a SHA
        pin or a `refs/tags/` URL — leaves both assertions above green while
        `main` starts reading as a "tag" on both sides."""
        for url in REJECTED_SCHEMA_URLS:
            with self.subTest(schema=url):
                self.assertIsNone(SCHEMA_URL.match(url), f"SCHEMA_URL accepts a non-pin: {url}")
        for uses in REJECTED_USES:
            with self.subTest(uses=uses):
                self.assertIsNone(USES.match(uses), f"USES accepts a non-pin: {uses}")


if __name__ == "__main__":
    unittest.main()
