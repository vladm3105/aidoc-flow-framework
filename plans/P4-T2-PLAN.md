# P4-T2 Plan — Platform conformance tests

| Field      | Value                                |
|------------|--------------------------------------|
| Task       | P4-T2                                |
| Depends on | P4-T0 audit, P4-T1 design (Q1, Q2)   |
| Status     | DONE — 2026-05-21T01:20:00Z          |
| Feeds      | P4-T3 (CI workflows consume the new tests), P4-T5 (verify) |

## Objective

Implement the platform-conformance contract bullets that are
statically testable in-repo today: **PC1** (every platform declares
`FRAMEWORK_SPEC_VERSION` matching `framework/VERSION`) and **PC4**
(neither platform's runtime-significant surface references the
other's engine). Tests live in the new `tests/conformance/platforms/`
sub-package per P4-T1 Q1; PC4 scopes by runtime-significant directory
per P4-T1 Q2. Suite grows 25 → 31 test methods.

## Scope

**In:**

1. **Extend `tests/conformance/_spec.py`** with platform helpers:
   `PLATFORMS_ROOT`, `platform_dirs()`, `platform_version_file()`,
   `platform_framework_spec_version_file()`, `framework_version()`.
2. **Create `tests/conformance/platforms/__init__.py`** — empty
   marker for the sub-package.
3. **Create `tests/conformance/platforms/test_version_declaration.py`** —
   4 test methods covering PC1 + structural completeness:
   - `test_every_platform_has_VERSION_file`
   - `test_every_platform_has_FRAMEWORK_SPEC_VERSION_file`
   - `test_version_files_are_bare_semver`
   - `test_FRAMEWORK_SPEC_VERSION_matches_framework_VERSION`
4. **Create `tests/conformance/platforms/test_engine_isolation.py`** —
   2 test methods covering PC4:
   - `test_hermes_does_not_reference_plugin_engine`
   - `test_plugin_does_not_reference_hermes_engine`

**Out:**

- PC2 (artifact validation) + PC3 (traceability enforcement) — both
  require runtime exercise; deferred per P4-T0 §2.
- CI workflow authoring (P4-T3).
- Any platform code change (none needed; this task only adds tests).
- `tests/conformance/README.md` update — the contract is already
  documented there; "Phase 4 implements PC1+PC4" can be a P4-T5
  closing-note edit, not a P4-T2 deliverable.

## Approach

### 1. `_spec.py` extension

Add at the bottom of `tests/conformance/_spec.py` (keep existing
helpers untouched):

```python
PLATFORMS_ROOT = REPO_ROOT / "platforms"


def platform_dirs() -> list[Path]:
    """Return every direct subdirectory of platforms/ (sorted)."""
    return sorted(p for p in PLATFORMS_ROOT.iterdir() if p.is_dir())


def platform_version_file(platform: Path) -> Path:
    return platform / "VERSION"


def platform_framework_spec_version_file(platform: Path) -> Path:
    return platform / "FRAMEWORK_SPEC_VERSION"


def framework_version() -> str:
    """Return the bare-SemVer string from framework/VERSION."""
    return (FRAMEWORK / "VERSION").read_text(encoding="utf-8").strip()
```

### 2. `test_version_declaration.py` — PC1 + structural

```python
"""Conformance: every platform declares FRAMEWORK_SPEC_VERSION
matching framework/VERSION (PC1) and the SemVer file shape (D-0009)."""

import re
import unittest

from .._spec import (
    framework_version,
    platform_dirs,
    platform_framework_spec_version_file,
    platform_version_file,
)

BARE_SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


class PlatformVersionDeclarationTests(unittest.TestCase):
    def test_every_platform_has_VERSION_file(self):
        for platform in platform_dirs():
            with self.subTest(platform=platform.name):
                f = platform_version_file(platform)
                self.assertTrue(f.is_file(), f"{f} missing")

    def test_every_platform_has_FRAMEWORK_SPEC_VERSION_file(self):
        for platform in platform_dirs():
            with self.subTest(platform=platform.name):
                f = platform_framework_spec_version_file(platform)
                self.assertTrue(f.is_file(), f"{f} missing")

    def test_version_files_are_bare_semver(self):
        for platform in platform_dirs():
            for getter in (platform_version_file, platform_framework_spec_version_file):
                f = getter(platform)
                with self.subTest(platform=platform.name, file=f.name):
                    self.assertTrue(f.is_file(), f"{f} missing")
                    body = f.read_text(encoding="utf-8").strip()
                    self.assertRegex(body, BARE_SEMVER, f"{f}: not bare SemVer")

    def test_FRAMEWORK_SPEC_VERSION_matches_framework_VERSION(self):
        fwk = framework_version()
        for platform in platform_dirs():
            with self.subTest(platform=platform.name):
                f = platform_framework_spec_version_file(platform)
                declared = f.read_text(encoding="utf-8").strip()
                self.assertEqual(
                    declared, fwk,
                    f"{platform.name} declares spec {declared!r}; "
                    f"framework/VERSION is {fwk!r}",
                )
```

### 3. `test_engine_isolation.py` — PC4

```python
"""Conformance: neither platform's runtime-significant surface
references the other's engine (PC4). Scope: runtime files only;
docs / READMEs / skill prose are documentary and allowed."""

import re
import unittest

from .._spec import PLATFORMS_ROOT

# Forbidden tokens per platform — case-insensitive substring match.
HERMES_FORBIDDEN = (
    "claude-plugin",
    "claude_plugin",
    ".claude-plugin/",
    "skill_view",
    "aidoc-flow:",
)
PLUGIN_FORBIDDEN = (
    "mcp_server",
    "sdd_validate",
    "hermes-server",
    "mcp-ucx",
)

# Runtime-significant scopes per platform (relative to its own root).
HERMES_SCOPE = (
    "src",
    "pyproject.toml",
)
PLUGIN_SCOPE = (
    ".claude-plugin",
    "commands",
    "agents",
)


def _violations(platform_root, scopes, forbidden):
    """Yield (file, line_no, line) for any forbidden-token hit."""
    patterns = re.compile(
        "|".join(re.escape(tok) for tok in forbidden),
        re.IGNORECASE,
    )
    for scope in scopes:
        path = platform_root / scope
        if not path.exists():
            continue
        files = [path] if path.is_file() else [p for p in path.rglob("*") if p.is_file()]
        for file in files:
            try:
                lines = file.read_text(encoding="utf-8").splitlines()
            except (UnicodeDecodeError, PermissionError):
                continue
            for i, line in enumerate(lines, start=1):
                if patterns.search(line):
                    yield (file, i, line)


class PlatformEngineIsolationTests(unittest.TestCase):
    def test_hermes_does_not_reference_plugin_engine(self):
        hermes = PLATFORMS_ROOT / "hermes"
        if not hermes.exists():
            self.skipTest("hermes platform absent")
        hits = list(_violations(hermes, HERMES_SCOPE, HERMES_FORBIDDEN))
        self.assertEqual(
            hits, [],
            "Hermes runtime surface references plugin engine:\n  " +
            "\n  ".join(f"{f}:{n}: {line}" for f, n, line in hits),
        )

    def test_plugin_does_not_reference_hermes_engine(self):
        plugin = PLATFORMS_ROOT / "claude-code-plugin"
        if not plugin.exists():
            self.skipTest("claude-code-plugin platform absent")
        hits = list(_violations(plugin, PLUGIN_SCOPE, PLUGIN_FORBIDDEN))
        self.assertEqual(
            hits, [],
            "Plugin runtime surface references Hermes engine:\n  " +
            "\n  ".join(f"{f}:{n}: {line}" for f, n, line in hits),
        )
```

### 4. Smoke-test design

Before committing, run the suite locally to confirm:
- All 31 test methods discovered (25 existing + 6 new).
- All 31 pass (subTests too).
- No spurious skip / error / unexpected behavior.

If a PC4 forbidden-token test fails, **don't weaken the test** —
investigate the offending file (the verify gate from
`tests/conformance/README.md` says "never weaken a check to make it
pass"). The likely failure modes: (a) a real cross-engine leak (rare —
P3-T4 G20 confirmed none), (b) a forbidden-token false positive on
an unexpected match (e.g. `mcp_server` appearing as a substring of an
unrelated identifier). Either way, escalate before adjusting.

## Step sequence

1. Read current `_spec.py` (already known from recon).
2. **Edit `_spec.py`** with the platform helpers (Step §1).
3. **Create `tests/conformance/platforms/__init__.py`** (empty).
4. **Create `test_version_declaration.py`** (Step §2).
5. **Create `test_engine_isolation.py`** (Step §3).
6. **Run the suite:** `python3 -m unittest discover -s tests/conformance -v`.
   Expect 31 test methods, all passing.
7. **Verify** (see below).
8. **Land** — single commit
   `feat(conformance): add platform-level tests — PC1 declaration + PC4 engine isolation (P4-T2)`;
   update `plans/HANDOFF.md`; tick P4-T2 in
   `plans/MIGRATION_TODO.md`. Push.

## Verification

- **V1. Test discovery:** `python3 -m unittest discover -s tests/conformance -v 2>&1 | grep -c '^test_'`
  returns ≥ 31 (existing 25 + new 6).
- **V2. Suite passes:** suite exit code 0; output reports
  `OK` with the expected test method count.
- **V3. New tests are in the sub-package:**
  `find tests/conformance/platforms -name 'test_*.py' | wc -l` = 2.
- **V4. `_spec.py` extension is additive:** existing helpers
  (`load_registry`, `registry_layers`, `framework_files`,
  `REPO_ROOT`, `FRAMEWORK`, `REGISTRY_PATH`, `ARTIFACTS`) unchanged.
  `git diff tests/conformance/_spec.py` shows only additions at
  the end of the file.
- **V5. PC1 actual values:** both platforms declare `0.1.0`
  matching `framework/VERSION = 0.1.0` — exercised by
  `test_FRAMEWORK_SPEC_VERSION_matches_framework_VERSION` passing.
- **V6. PC4 actual hits:** zero forbidden-token hits in either
  platform's runtime scope — exercised by both
  `test_*_does_not_reference_*_engine` passing.
- **V7. No code change outside `tests/`:**
  `git diff --stat HEAD -- framework/ platforms/` is empty.
- **V8. README.md unchanged:** `tests/conformance/README.md` is not
  edited in P4-T2 (its prose is already accurate about Phase 4
  intent; P4-T5 may add a "PC1+PC4 now implemented" note).

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | A PC4 forbidden token has a substring collision in unrelated content. | Forbidden tokens chosen to be distinctive (`claude-plugin`, `mcp_server`, `sdd_validate`). Case-insensitive `re.escape` join — no regex meta-character surprises. If a collision surfaces, the failure prints file/line/content, making investigation fast. |
| R2 | A platform genuinely needs to reference the other's engine for legitimate documentary purposes inside a runtime-scope directory. | None today (verified by recon). If a future need arises, the test gives a clear failure with file/line; the maintainer either adds a structural exception (e.g. an inline annotation the test skips) or moves the documentary content out of the runtime scope. Per-file allow-lists are explicitly out of design (P4-T1 Q2). |
| R3 | `unittest discover` doesn't recurse into the sub-package. | Stdlib `unittest` recurses through sub-packages by default when given `-s tests/conformance`. The `__init__.py` marker is the standard recurse trigger. Verified by V1. |
| R4 | Imports `from .._spec import ...` (relative) fail if the suite is run from the wrong working directory. | Existing test modules use `from _spec import ...` (top-level package context). The sub-package needs `from .._spec import ...` which only works if `tests/conformance/__init__.py` exists. **Check first** — if it doesn't, add one (empty marker). If unittest discovery struggles, fall back to absolute import via `sys.path` manipulation (less clean but bulletproof). |
| R5 | The test count `31` is one off because subTests inflate the count or because I miscounted. | V1's `grep -c '^test_'` counts actual test methods (the lines `unittest` prints in verbose mode). If it's 30 or 32, the implementation note records the actual number; no need to gate exactly on 31. |
| R6 | Adding `_spec.py` helpers breaks an existing test's import. | The additions are at the *end* of `_spec.py`; existing test imports (`from _spec import REPO_ROOT, FRAMEWORK, ...`) are unaffected. V4 confirms additive-only. |
| R7 | Plugin `commands/save-plan.md` content triggers a forbidden-token false positive. | Recon during P3-T4 confirmed `save-plan.md` is clean of `mcp_server` / `sdd_validate` / `hermes-server` / `mcp-ucx` (it mentions `TodoWrite`, `CLAUDE.md`, `plans/` only). Re-confirmed during planning. |

## Review log

### Pass 1 — 2026-05-21T01:00:00Z

- **G1. `_spec.py` extension is additive.** Existing helpers
  unchanged; new ones bolt on at the end. V4 enforces.
- **G2. Sub-package import idiom.** Test modules use
  `from .._spec import ...` (relative). Needs both
  `tests/conformance/__init__.py` and `tests/conformance/platforms/__init__.py`
  as marker files. **Check `tests/conformance/__init__.py`
  existence first; if absent, add as well (empty).** R4 mitigates.
- **G3. PC1 covers existence + format + value match.** Three
  distinct test methods because each failure mode points at a
  different fix:
  - "missing file" → P3-T3 / P2-T3 retrofit.
  - "not bare SemVer" → file content edit.
  - "value mismatch" → either platform out of sync with framework,
    or a planned version bump in flight.
- **G4. PC4 uses case-insensitive `re.escape` join.** Safe over
  arbitrary strings. Failure prints file/line/content for
  diagnosability.
- **G5. PC4 in-scope directories are minimal.** Hermes: 2 paths
  (`src/`, `pyproject.toml`); plugin: 3 paths (`.claude-plugin/`,
  `commands/`, `agents/`). Anything else is documentary.
- **G6. R1 forbidden-token collision possibilities.** Re-checked
  each token:
  - `claude-plugin` — distinctive; only the plugin package would
    use it.
  - `claude_plugin` — underscore variant; same.
  - `.claude-plugin/` — path; distinctive.
  - `skill_view` — Claude Code internal API; no Hermes code would
    legitimately reference it.
  - `aidoc-flow:` — the plugin's slash-prefix; trailing colon
    distinguishes from the project name "aidoc-flow" (which Hermes
    docs may reference, and which is out of runtime scope anyway).
  - `mcp_server` — Hermes' Python module name; the plugin has no
    reason to reference it.
  - `sdd_validate` — Hermes MCP tool name.
  - `hermes-server` — Hermes distribution name.
  - `mcp-ucx` — Hermes' legacy script entry.
- **G7. Test naming.** Methods use uppercase artifact names
  (`VERSION`, `FRAMEWORK_SPEC_VERSION`) to match the file names
  they assert about. Reads naturally in test output.
- **G8. Suite count expectation.** Existing 25 + new 6 = 31. The
  README's "25 tests" line will need a bump at P4-T5 close. Not a
  P4-T2 task.

### Pass 2 — 2026-05-21T01:10:00Z

- **G9. `re.escape` over the OR of forbidden tokens.** The
  `_violations` helper builds `re.compile(
  "|".join(re.escape(tok) for tok in forbidden), re.IGNORECASE)`.
  Each token is escaped (handles `.` in `.claude-plugin/`); the
  OR joins; flag adds case-insensitivity. Reviewed mentally:
  pattern for Hermes = `claude\-plugin|claude_plugin|\.claude\-plugin/|skill_view|aidoc\-flow:`.
  Hyphens get escaped (harmless inside non-character-class
  context); slashes pass through. Works.
- **G10. Edge case — a binary file in `src/` would crash
  `read_text`.** `_violations` catches `UnicodeDecodeError` and
  `PermissionError` and skips. Hermes `src/` is all `.py` files
  (Python source); plugin scopes are `.json` and `.md`. No
  binary files expected; defensive catch is hygiene.
- **G11. Edge case — a `pyproject.toml` declaring an MCP dep
  legitimately references `mcp[cli]`.** Wait — does Hermes'
  pyproject.toml mention `mcp_server`? Re-check: the dependency
  is `mcp[cli]>=1.0.0`, NOT `mcp_server`. The string `mcp_server`
  is in `[tool.hatch.build.targets.wheel] packages = ["src/mcp_server"]`
  — Hermes' OWN package, which is correctly in Hermes' own
  pyproject. The PLUGIN's forbidden list contains `mcp_server`
  (forbidden in the plugin), not Hermes' own list. So no
  conflict. ✓
- **G12. Plugin `commands/` — only `save-plan.md`.** Already
  verified clean of Hermes engine tokens. ✓
- **G13. Plugin `agents/` — only `requirements-analyst.md`.**
  Need to verify it's clean too. Will check during execution; if
  not, the test will fail loudly with file/line.
- **G14. No new findings.** Plan is internally consistent.
  Ready to present on approval.

## Implementation note (2026-05-21T01:20:00Z)

Executed. All 8 verify gates green.

- **V1 test discovery:** new sub-package recognized by
  `unittest discover`; the 6 new test methods appear in `-v` output
  alongside the 25 existing.
- **V2 suite passes:** `python3 -m unittest discover -s tests/conformance`
  reports `Ran 31 tests in 0.253s, OK` (up from 25). All 31 pass on
  first run; no skips or errors.
- **V3 new tests in sub-package:** `tests/conformance/platforms/`
  carries `__init__.py`, `test_version_declaration.py` (4 tests),
  `test_engine_isolation.py` (2 tests).
- **V4 `_spec.py` extension is additive:** `git diff` shows only
  trailing additions (`PLATFORMS_ROOT`, `platform_dirs`,
  `platform_version_file`, `platform_framework_spec_version_file`,
  `framework_version`); existing helpers untouched.
- **V5 PC1 actual values:** both platforms declare `0.1.0`;
  `test_FRAMEWORK_SPEC_VERSION_matches_framework_VERSION` passes
  (subTest per platform).
- **V6 PC4 actual hits:** zero forbidden-token hits in either
  platform's runtime scope; both engine-isolation tests pass.
- **V7 no changes outside `tests/`:** `git diff --stat HEAD --
  framework/ platforms/` empty.
- **V8 README.md unchanged:** `tests/conformance/README.md` untouched
  (P4-T5 will update the prose to reflect "PC1+PC4 implemented").

One implementation-time correction: the initial Edit on `_spec.py`
failed silently because I hadn't Read the file first; suite
discovered the new modules but their imports failed
(`ImportError: cannot import name 'PLATFORMS_ROOT' from '_spec'`).
Re-Read + re-Edit landed cleanly. Lesson: the Edit tool's
read-before-edit requirement is a real guardrail — if a verify step
shows an unexpected ImportError after a "successful" Edit, suspect
silent failure.

Test count delta: planned 28-30; actual **+6 = 31**. The plan's
range was an underestimate; the implementation's 4 + 2 method
split matches the design.
