"""Conformance: every version a CHANGELOG documents as released must actually
have been a value of its stream's ``VERSION`` file (#617, D-0078).

**The defect this catches is a phantom version, not a missing tag.** D-0078:

    ``framework/VERSION`` moved ``0.41.3 → 0.43.0`` in one commit. Spec ``0.42.0``
    was **never a value of the file**, yet ``CHANGELOG.md`` documents a
    ``0.41.3 → 0.42.0`` release and GD-14 is ratified against it.

That is a documented release that never existed in the tree, and D-0078 records
the standing consequence that ``GATE-SPEC`` cannot see it: ``E001``–``E008`` are
all diff-local, so nothing checks that a superseded version was ever published.
This module is that check.

**Why it is not a tag-currency check.** An earlier framing of #617 proposed
comparing shipped versions against cut tags. Measured, 77 of 89 framework
versions are untagged, and ``docs/TAGGING.md`` declares the tag-cut lag *"a known
backlog"* — so such a check would emit dozens of findings against a sanctioned
state. Tags are deliberately out of scope here.

**Two accepted phantoms exist and are named below.** Both are permanent by
decision: D-0078 chose to correct forward rather than rewrite a published record,
and release tags are immutable once pushed. The guard therefore documents them
and fails on any *new* one.

**Three authoring details are load-bearing, each because review caught the
opposite choice failing:**

* Release versions are read from **heading lines only**. An unanchored scan of
  the file body turns a narrative sentence ("Planned next: Framework Spec
  ``0.49.0 → 0.50.0``") into a phantom and reddens a required context on correct
  work — and ``CHANGELOG.md`` is written in exactly that long-prose style.
* The framework changelog has used **three** heading forms over its life
  (backticked transition, unbackticked transition, and ``## [0.21.2] — Framework
  Spec — …``). A pattern matching only the current one measured 22 of 48 and left
  the older forms as a green corridor for a new phantom, while the
  "did the pattern match anything?" canary stayed satisfied by the 22.
* The history walk passes ``--full-history``. Default ``git log`` simplification
  prunes a TREESAME side at each merge — 42 of 131 commits here — so a value that
  existed only on the pruned side reads as a phantom. That losing shape has
  already occurred: D-0082 records three PRs each claiming ``0.45.0``.
"""

from __future__ import annotations

import functools
import re
import subprocess
import unittest

import yaml
from _spec import REPO_ROOT, platform_dirs

_SEMVER = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")
_HEADING = re.compile(r"^\#{2,3} .*$", re.MULTILINE)


def _framework_releases(text: str) -> set[str]:
    """Every version named on a ``Framework Spec`` heading, both sides of a transition.

    Taking *every* SemVer in the segment rather than one capture group covers all
    three historical heading forms at once, and closes the case where a version
    appears only as the ``from`` side of a transition it never reached.

    **Scoped to the ``Framework Spec`` segment, because 14 of the 55 headings are
    combined** — ``… Framework Spec 0.15.0 → 0.15.1 + Plugin 0.10.2 → 0.11.0``.
    Reading the whole line attributes the *plugin's* versions to the framework
    stream; that produced a false phantom (``0.10.2``) on correct history, and the
    other 13 were hidden only by the coincidence that those plugin versions
    happen to also be real framework values. Streams are separated by ``+``.
    """
    releases: set[str] = set()
    for line in _HEADING.findall(text):
        for segment in line.split("+"):
            if "Framework Spec" in segment:
                releases.update(_SEMVER.findall(segment))
    return releases


def _leading_version_releases(text: str) -> set[str]:
    """Platform changelogs: the version that opens the heading (``## [0.25.0] - …``)."""
    return set(re.findall(r"^\#\# \[?([0-9]+\.[0-9]+\.[0-9]+)", text, re.MULTILINE))


#: (stream, VERSION path, CHANGELOG path, extractor).
STREAMS = (
    ("framework", "framework/VERSION", "CHANGELOG.md", _framework_releases),
    (
        "claude-code-plugin",
        "platforms/claude-code-plugin/VERSION",  # pragma: allowlist secret
        "platforms/claude-code-plugin/CHANGELOG.md",
        _leading_version_releases,
    ),
    (
        "hermes",
        "platforms/hermes/VERSION",
        "platforms/hermes/CHANGELOG.md",
        _leading_version_releases,
    ),
)

#: Phantoms that already shipped and are permanent by decision. Each entry needs
#: the reason, because an unexplained allowlist entry is indistinguishable from a
#: silenced defect — and this is the file a future session will read to decide
#: whether a new phantom may join them. The answer is no: both of these are
#: immutable, whereas a new phantom is still fixable at the PR that introduces it.
ACCEPTED_PHANTOMS = {
    (
        "framework",
        "0.42.0",
    ): "D-0078 (#558) — spec 0.42.0 is documented and GD-14 is ratified against it, "
    "but VERSION jumped 0.41.3 → 0.43.0. The founder chose to correct forward in the "
    "next real release rather than rewrite a published CHANGELOG entry.",
    (
        "hermes",
        "0.1.1",
    ): "D-0086 (#617) — hermes/v0.1.1 was cut as a release tag on a commit whose "
    "platforms/hermes/VERSION reads 0.1.0 (not a predates-the-file artifact: the file "
    "existed a day earlier holding 0.1.0). Worse than the framework case, because "
    "docs/TAGGING.md makes release tags immutable so it cannot be corrected in place.",
}


def _git(*args: str) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=False
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout


def _cannot_measure() -> str | None:
    """Why history is unreadable here, or ``None`` when it is readable.

    Covers both degraded contexts the same way: a shallow CI checkout, and a
    source export with no ``.git`` at all (the suite is documented as the runnable
    contract a platform consumer executes, so that is a real context). Neither may
    raise — an ERROR here would be indistinguishable from a real defect.
    """
    try:
        if _git("rev-parse", "--is-inside-work-tree").strip() != "true":
            return "not a git work tree"
        if _git("rev-parse", "--is-shallow-repository").strip() == "true":
            return "shallow clone"
    except (RuntimeError, OSError) as exc:
        return f"git unavailable ({exc})"
    return None


@functools.cache
def _version_values(path: str) -> frozenset[str]:
    """Every distinct value ``path`` has held across HEAD's full history.

    ``HEAD``, never a branch name: on a PR the checkout is a detached merge ref
    and ``main`` may not exist locally. ``--full-history`` for the reason in the
    module docstring.
    """
    values: set[str] = set()
    for sha in _git("log", "--full-history", "--format=%H", "HEAD", "--", path).split():
        blob = subprocess.run(
            ["git", "show", f"{sha}:{path}"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if blob.returncode == 0 and blob.stdout.strip():
            values.add(blob.stdout.strip())
    return frozenset(values)


def _declared(stream_spec) -> set[str]:
    _, _, changelog_path, extractor = stream_spec
    return extractor((REPO_ROOT / changelog_path).read_text("utf-8"))


class DeepCheckoutIsConfigured(unittest.TestCase):
    """At least one runner of this suite must have full history.

    The suite runs in **three** CI places with different, and partly unownable,
    checkout depths: ``conformance.yml`` and ``chg-gate.yml`` (both ours, both
    deep — but ``chg-gate`` is ``pull_request``-only, so it covers no ``push``
    run), and the reusable ``pre-commit`` workflow, whose checkout belongs to the
    canon repo and sets no depth at all. ``actions/checkout`` defaults to
    ``fetch-depth: 1``, so the phantom check cannot measure anything in a shallow
    clone.

    Failing on shallow would redden a **required** context we do not configure.
    Skipping silently would be the false all-clear this repo has been bitten by.
    So the history-dependent tests skip when history is unreadable, and this
    assertion — which needs no history, and therefore runs everywhere — guarantees
    the blocking runner is configured deep.
    """

    WORKFLOW = REPO_ROOT / ".github" / "workflows" / "conformance.yml"
    JOB = "conformance"

    def test_conformance_job_fetches_full_history(self):
        workflow = yaml.safe_load(self.WORKFLOW.read_text("utf-8"))
        self.assertIn(
            self.JOB,
            workflow["jobs"],
            f"conformance.yml declares no {self.JOB!r} job — this guard no longer knows "
            "which job runs the suite",
        )
        # Scoped to the job that runs the suite: an unrelated job in the same file
        # may legitimately use a shallow checkout.
        steps = [
            step
            for step in (workflow["jobs"][self.JOB].get("steps") or [])
            if str(step.get("uses", "")).startswith("actions/checkout")
        ]
        self.assertTrue(steps, f"the {self.JOB!r} job has no actions/checkout step")
        for step in steps:
            self.assertEqual(
                # `or {}` not a default: an emptied `with:` block parses as None,
                # which would raise AttributeError and report as an ERROR — losing the
                # actionable message at exactly the moment it is needed.
                str((step.get("with") or {}).get("fetch-depth")),
                "0",
                f"the {self.JOB!r} job's checkout does not set `fetch-depth: 0`, so the "
                "suite's only deep runner on `push` became shallow and "
                "test_no_undocumented_phantom_release now measures nothing "
                "(see .github/workflows/chg-gate.yml for the same setting)",
            )


class StreamCoverage(unittest.TestCase):
    """A stream removed from ``STREAMS`` is a silent narrowing, not a failure."""

    def test_every_platform_is_covered(self):
        covered = {s[0] for s in STREAMS} - {"framework"}
        on_disk = {p.name for p in platform_dirs()}
        self.assertEqual(
            covered,
            on_disk,
            f"STREAMS covers {sorted(covered)} but platforms/ holds {sorted(on_disk)} — an "
            "uncovered stream can ship a phantom release with the suite green",
        )

    def test_framework_headings_all_yield_a_version(self):
        """The canary with teeth.

        ``assertTrue(declared)`` cannot catch a *new* heading form: the 22 entries
        in the current form keep it satisfied forever. This asserts instead that
        every heading claiming to be a Framework Spec release parses — so a fourth
        form fails the moment it is introduced, rather than opening a green
        corridor for a phantom written in it.
        """
        text = (REPO_ROOT / "CHANGELOG.md").read_text("utf-8")
        for line in _HEADING.findall(text):
            if "Framework Spec" in line:
                with self.subTest(heading=line[:70]):
                    self.assertTrue(
                        _SEMVER.findall(line),
                        "a 'Framework Spec' heading names no version, so this heading form "
                        "is invisible to the phantom check",
                    )


class GitHistoryAvailable(unittest.TestCase):
    def setUp(self):
        reason = _cannot_measure()
        if reason:
            self.skipTest(f"{reason} — guaranteed elsewhere by DeepCheckoutIsConfigured")

    def test_version_history_covers_every_documented_release(self):
        """The precondition the phantom check needs, stated as the bar.

        A `> 1` bar passed on a two-commit clone and then let the phantom check
        emit a wall of false findings telling the author to fix correct work.
        """
        for spec in STREAMS:
            stream, version_path = spec[0], spec[1]
            with self.subTest(stream=stream):
                self.assertGreaterEqual(
                    len(_version_values(version_path)),
                    len(_declared(spec)) - len(ACCEPTED_PHANTOMS),
                    f"{version_path} holds fewer historical values than {spec[2]} documents "
                    "releases — history is truncated, and the phantom check below would "
                    "report correct work as defective",
                )


class ReleaseRecordIntegrity(unittest.TestCase):
    def setUp(self):
        reason = _cannot_measure()
        if reason:
            self.skipTest(f"{reason} — guaranteed elsewhere by DeepCheckoutIsConfigured")

    def test_no_undocumented_phantom_release(self):
        """Every documented release existed; anything else is named and cited."""
        for spec in STREAMS:
            stream, version_path, changelog_path = spec[0], spec[1], spec[2]
            with self.subTest(stream=stream):
                declared = _declared(spec)
                self.assertTrue(
                    declared,
                    f"{changelog_path} yielded no release versions — the heading form changed "
                    "and this guard silently stopped measuring the stream",
                )
                phantoms = declared - _version_values(version_path)
                unexplained = sorted(p for p in phantoms if (stream, p) not in ACCEPTED_PHANTOMS)
                self.assertEqual(
                    unexplained,
                    [],
                    f"{changelog_path} documents {unexplained} as released, but "
                    f"{version_path} never held those values. A release that exists only in "
                    "the changelog is the D-0078 phantom (#558): the version cannot be tagged "
                    "without putting a tag on a commit that contradicts it. Fix the version "
                    "bump or the entry in THIS PR — it is cheap now and permanent later.",
                )

    def test_accepted_phantoms_are_still_real(self):
        """An allowlist outliving its defect quietly licenses the next one."""
        for (stream, version), reason in ACCEPTED_PHANTOMS.items():
            with self.subTest(stream=stream, version=version):
                spec = next(s for s in STREAMS if s[0] == stream)
                self.assertIn(
                    version,
                    _declared(spec) - _version_values(spec[1]),
                    f"{stream} {version} is allowlisted as an accepted phantom but is no longer "
                    "one — drop the entry rather than leaving it to excuse a future phantom",
                )
                self.assertGreater(len(reason), 80, "an allowlist entry needs its reason")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
