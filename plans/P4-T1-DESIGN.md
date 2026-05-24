# P4-T1 Design — Conformance & Independence

| Field      | Value                                |
|------------|--------------------------------------|
| Task       | P4-T1                                |
| Depends on | P4-T0 audit                          |
| Produced by| P4-T1 (this doc IS the plan output)  |
| Date       | 2026-05-21T00:05:00Z                 |
| Feeds      | P4-T2, P4-T3, P4-T4                  |

## Summary

Six design choices resolved before any test, workflow, or retrofit
lands. Conformance tests live in a new `tests/conformance/platforms/`
sub-package; PC4 engine-isolation scopes by **runtime-significant
directory** (not by file type or per-file allow-list); CI runs on
`ubuntu-latest`; CHANGELOG retrofit is **minimal-honest** (each
platform's `[0.1.0]` mirrors the corresponding project-level release
scoped to that platform); Hermes README is **full mirror** of P3-T3's
plugin README structure; LICENSE is **MIT** (matches plugin manifest
placeholder, simplest, permissive for any future commercial use).

| Q | Question | Choice |
|---|----------|--------|
| Q1 | Test-module placement | New sub-package `tests/conformance/platforms/test_*.py`; both platforms in one module per concern (one module asserts version declaration for both platforms). |
| Q2 | PC4 engine-isolation scope | By **runtime-significant directory** (`src/`, `pyproject.toml`, `.claude-plugin/`). Docs / READMEs / skills' SKILL.md prose may reference the other platform for documentary purposes. |
| Q3 | CI runner | `ubuntu-latest` for all three workflows. No `self-hosted` dependency. |
| Q4 | CHANGELOG retrofit posture | **Minimal-honest**: each platform's `[0.1.0]` mirrors the corresponding project release scoped to that platform (plugin gets project `[0.4.0]` scope, Hermes gets project `[0.3.0]` scope). |
| Q5 | Hermes README structure | Full mirror of P3-T3 plugin README — info table, install/use, conformance section, relationship-to-the-other-platform paragraph. |
| Q6 | LICENSE choice | **MIT** — matches plugin manifest placeholder. |

Plus an implicit Q7 (do we bump `framework/VERSION`?): **no.** Phase 4
adds enforcement of the existing spec, not changes to it. Framework
stays at `v0.1.0`.

## Q1 — Test-module placement

**Options:**

1. Sub-package `tests/conformance/platforms/test_*.py` — both
   platforms asserted from one module per concern.
2. Flat at `tests/conformance/test_platform_*.py` — same
   structure, but no sub-package directory.
3. Per-platform sub-package `tests/conformance/platforms/hermes/`
   + `.../claude-code-plugin/` — separate test modules per platform.

**Chosen:** Option 1.

**Rationale:** Existing suite structure (`test_governance.py`,
`test_layers.py`, etc.) is "one module per concern", and the
platform-conformance tests follow the same pattern: PC1 (version
declaration) asserts symmetric structure across all platforms;
splitting into per-platform files would duplicate code. The sub-
package separates framework-level concerns (`tests/conformance/test_*.py`)
from platform-level (`tests/conformance/platforms/test_*.py`)
visually.

Option 2 muddles the visual separation; Option 3 fragments tests
that share assertion logic.

**Downstream implications:**

+ **P4-T2 file layout:**

  ```
  tests/conformance/
  ├── _spec.py
  ├── test_*.py           (5 existing framework-level modules)
  └── platforms/
      ├── __init__.py
      ├── test_version_declaration.py  (PC1 + structural completeness)
      └── test_engine_isolation.py     (PC4)
  ```

+ **`_spec.py` extension:** add helpers `platforms_root()`,
  `platform_dirs()`, `platform_version_file(name)`, etc. — single
  source of truth for path resolution.
+ **`unittest discover`** automatically picks up the sub-package
  (the `-s tests/conformance` argument recurses).
+ **Test count delta:** +3 to +5 tests (PC1 declaration check,
  PC1 value match, PC4 hermes-to-plugin, PC4 plugin-to-hermes,
  structural-completeness). Suite goes 25 → 28-30.

## Q2 — PC4 engine-isolation scope

**Options:**

1. **By directory:** scan only `platforms/<name>/src/`,
   `pyproject.toml`, `.claude-plugin/` — the runtime-significant
   surface. Skills/agents/docs prose is out of scope.
2. **By file type:** scan `*.py`, `*.json`, `*.toml`; allow
   `*.md`.
3. **Per-file allow-list:** enumerate every file where cross-
   references are intentional; flag anything else.

**Input gathered (recon):**

Hermes mentioning plugin tokens:

+ `agent-skills/.../sdd-orchestrator/SKILL.md:40,1132` —
  references "aidoc-flow migration" (the project name), not a
  plugin-engine reference per se.

Plugin mentioning Hermes tokens:

+ `README.md:75` — deliberate "Relationship to Hermes" paragraph
  (P3-T3 design); documentary, by design.
+ `doc-naming/SKILL.md:122` — example user-document filename
  `BRD-01_ib_stock_options_mcp_server.md` (a name a user might
  pick); not a runtime reference.

All current cross-engine mentions are documentary or incidental.
None point at the other engine as a runtime dependency.

**Chosen:** Option 1 (scope by runtime-significant directory).

**Rationale:** Option 2 would catch the README's deliberate
documentary section as a false positive. Option 3 over-engineers
for the maintenance cost (a per-file allow-list churns whenever
docs change). Option 1 catches the meaningful leak ("Hermes' Python
source code imports something plugin-specific" — never OK) without
false positives on prose.

**Concrete forbidden-tokens specification:**

| Platform | Forbidden tokens (case-insensitive) | Scope |
|----------|-------------------------------------|-------|
| Hermes (`platforms/hermes/`) | `claude-plugin`, `claude_plugin`, `\.claude-plugin/`, `skill_view`, `aidoc-flow:` (the plugin's slash prefix) | `src/**`, `pyproject.toml` |
| Plugin (`platforms/claude-code-plugin/`) | `mcp_server`, `sdd_validate`, `hermes-server`, `mcp-ucx` | `.claude-plugin/`, `commands/**`, `agents/**` |

`README.md` and `docs/` are out of scope per the documentary-allow
rule. `skills/**/SKILL.md` is out of scope for prose-tolerance —
skills are markdown bodies executed as Claude instructions, not
runtime code; documentary references are accepted.

**Downstream implications:**

+ **P4-T2 `test_engine_isolation.py`:** two test methods (one per
  platform's forbidden-token check), iterating the in-scope
  directory list, asserting zero hits.
+ **Future-proofing:** if a new forbidden token surfaces post-
  Phase-4, add to the constants module without changing test
  logic.

## Q3 — CI runner

**Chosen:** `ubuntu-latest`.

**Rationale:** Legacy `legacy/github-workflows-disabled/ci.yml` uses
`self-hosted` — that requires GitHub Actions runners the user
maintains. Greenfield CI should use GitHub-provided runners
(`ubuntu-latest`) so workflows run out of the box with no infra
setup. Faster onboarding; lower op cost; matches the "shippable
plugin" + "shippable Hermes" framing.

**Downstream implications:**

+ **P4-T3 workflows:** all three jobs declare `runs-on:
  ubuntu-latest`.
+ **Python version:** Hermes requires `>=3.12`; CI uses
  `actions/setup-python@v5` with `python-version: '3.12'`.
+ **No carry-over** from legacy workflows (R5 of P4-T0).

## Q4 — CHANGELOG retrofit posture

**Options:**

1. **Minimal-honest:** each platform's `[0.1.0]` mirrors the
   corresponding project-level release scoped to that platform's
   content.
2. **Project-pointer:** each platform's CHANGELOG is a stub
   pointing at project-level for details.
3. **Detailed:** rewrite from scratch for each platform.

**Chosen:** Option 1 (minimal-honest).

**Rationale:** Option 2 risks broken-link drift and forces users
to context-switch between two files for one platform's history.
Option 3 is content design work — out of mechanical-Phase-4
scope. Option 1 is the right hand-off shape: a user who only cares
about Hermes can read `platforms/hermes/CHANGELOG.md` end-to-end
and understand its history; same for the plugin.

**Concrete content:**

+ **`platforms/hermes/CHANGELOG.md`:**
  + `## [0.1.0] — 2026-05-20` — mirrors project `[0.3.0]` Hermes-
    specific content (the "Added / Changed / Removed" rows that
    pertain to `platforms/hermes/`). Cross-reference to project-
    level `CHANGELOG.md` and `plans/P2-T*-PLAN.md` for full audit
    trail.

+ **`platforms/claude-code-plugin/CHANGELOG.md`:**
  + `## [0.1.0] — 2026-05-20` — mirrors project `[0.4.0]`
    plugin-specific content. Cross-reference to project-level
    `CHANGELOG.md` and `plans/P3-T*-PLAN.md`.

Both files: open with the Keep-a-Changelog preamble, then a
single `[0.1.0]` entry, then a footer pointing at the project-
level changelog for cross-platform / framework changes.

**Downstream implications:**

+ **P4-T4 files created:** two new `CHANGELOG.md` files (one per
  platform), each ~30-50 lines.
+ **No retro-tag** for `[0.1.0]` — both platforms already have
  `hermes/v0.1.0` and `claude-code-plugin/v0.1.0` tags; the
  CHANGELOG just documents what's in those tagged commits.
+ **Phase 4 itself** is not in either platform's `[0.1.0]` —
  Phase 4 happens *after* both platforms' first releases. If
  Phase 4 changes anything platform-specific, that's a future
  `[0.1.1]` (or `[0.2.0]`).

## Q5 — Hermes README structure

**Chosen:** Full mirror of P3-T3 plugin README structure.

**Rationale:** P3-T3 set the pattern: substantive user-facing
README with info table, install pointer, use examples, conformance
section, relationship-to-other-platform paragraph. Hermes' current
27-line placeholder doesn't serve users. Mirroring achieves
symmetry; the two READMEs feel like sibling deliveries of the
same project.

**Content outline (mirrors plugin README §):**

1. One-paragraph "what this is" — Hermes is the MCP-server delivery
   of the AI Doc Flow framework.
2. **What's inside** table — `src/mcp_server/` modules, the
   447-test suite, agent-skills package, prompts, skills.
3. **Install** — `pip install hermes-server` (when published) +
   `.mcp.json` config snippet.
4. **Use** — invoking `hermes-mcp` from a Claude Code session;
   pointer to the MCP tools the server exposes.
5. **Framework spec conformance** — `cat VERSION` + `cat
   FRAMEWORK_SPEC_VERSION` snippet; declares `0.1.0` against
   `framework/v0.1.0`.
6. **Platform info table** — engine, version, conforms-to, license,
   repository.
7. **Relationship to the Claude Code plugin** — symmetric with the
   plugin README's Hermes section.

**Downstream implications:**

+ **P4-T4** writes the new `platforms/hermes/README.md` (~80
  lines, vs 27 placeholder).
+ **No content drift risk** — the structure mirrors plugin README
  exactly; updates to one set the pattern for the other.

## Q6 — LICENSE choice

**Options:**

1. **MIT** — matches plugin manifest placeholder; most permissive;
   minimal copyleft surface.
2. **Apache 2.0** — adds patent grant + contributor agreement;
   corporate-friendly.
3. **GPL-3** — copyleft; ensures derivatives stay open.

**Chosen:** **MIT.**

**Rationale:**

+ Plugin manifest already declares `"license": "MIT"` (P3-T3); a
  different choice creates a manifest-vs-LICENSE inconsistency.
+ MIT supports both open-source community adoption (low friction)
  and any future commercial / hosted use (no copyleft).
+ Apache 2.0's patent grant is valuable but adds complexity not
  warranted at v1.
+ GPL-3 forecloses commercial relicensing options that the
  STARTUP_HANDOFF surfaces as potential paths.

**Downstream implications:**

+ **P4-T4 creates** `LICENSE` at repo root with the standard MIT
  text + `Copyright (c) 2026 vladm3105` (matches the repo owner).
+ **Plugin manifest** already correct; no edit needed.
+ **Hermes pyproject.toml** doesn't declare a license today;
  P4-T4 adds `license = "MIT"` for symmetry (single-line edit).

## Q7 — `framework/VERSION` bump?

**Chosen:** **No.**

**Rationale:** Phase 4 adds enforcement (tests) of the existing
spec, not changes to the spec itself. `framework/` is byte-
unchanged. The `framework/v0.1.0` tag still points at the
authoritative spec commit. **No new `framework/v0.X.Y` tag in
Phase 4.**

This was an implicit question from the P4-T0 audit; confirmed here
for the record.

## Cross-question conflicts

None. Specifically checked:

+ Q1 (sub-package) × Q2 (forbidden tokens) — tests share the
  `_spec.py` helpers; sub-package import path
  (`from .._spec import ...`) works in standard `unittest`
  discovery.
+ Q2 (PC4 scope) × Q5 (Hermes README mirror) — README's
  "Relationship to plugin" section is in `README.md`, out of PC4
  forbidden-token scope. Safe.
+ Q3 (`ubuntu-latest`) × Hermes' `requires-python = ">=3.12"` —
  `actions/setup-python@v5` provides 3.12 on `ubuntu-latest`.
  Compatible.
+ Q4 (CHANGELOG content scoped to platform) × Q5 (README
  structure) — distinct files; no overlap.
+ Q6 (MIT) × plugin manifest (MIT placeholder) — match.

## Deferred items

1. **Hermes `pyproject.toml` license declaration.** Q6 includes a
   single-line `license = "MIT"` edit; if MIT changes later (e.g.
   commercial license + open-source dual-license), both `LICENSE`
   and `pyproject.toml` update together. Tracked as a low-priority
   follow-up.
2. **CHANGELOG retrofit for Phase 4 changes** to each platform.
   If P4-T2/T3/T4 touches platform content (probably not —
   conformance tests live in `tests/`, CI lives in `.github/`),
   that's the platforms' `[0.1.1]` entries. Defer until Phase 4
   actually surfaces such changes.
3. **PC4 forbidden-token list maintenance.** As new engine
   features land (e.g. a future MCP method or plugin command),
   the forbidden-token list may need an update. Tracked as a
   per-release review item.

## Verify (against the plan's gate)

+ **All six questions covered** (list-completeness, P2-T0 Pass 3
  lesson): Q1 ✓ Q2 ✓ Q3 ✓ Q4 ✓ Q5 ✓ Q6 ✓. Plus implicit Q7
  ✓ (no framework bump).
+ Each section carries Options / Chosen / Rationale / Downstream
  implications.
+ **Q1** — file layout sketched; test count delta predicted (+3
  to +5).
+ **Q2** — concrete forbidden-token tables per platform; allow-
  list rule (runtime-significant directories) stated.
+ **Q3** — runner choice + Python version + carry-over policy
  (none).
+ **Q4** — concrete mirror posture; both files structured the
  same way; tag-vs-CHANGELOG alignment confirmed.
+ **Q5** — content outline matches P3-T3 plugin README structure.
+ **Q6** — LICENSE choice + tribute / copyright line + manifest
  consistency check.
+ Cross-question conflicts: explicitly checked, none.
+ Deferred items list: 3 (one per question class).
+ No code or files moved by P4-T1 — `git status` shows only
  `plans/` edits.

## Review log

### Pass 1 — 2026-05-21T00:20:00Z

+ **G1. Q1 sub-package mirrors `_spec.py`'s existing helper
  pattern.** Adding helpers (`platforms_root()`, etc.) to
  `_spec.py` keeps path-resolution in one place — consistent with
  how the existing tests use `_spec.FRAMEWORK`.
+ **G2. Q2 — directory-scoped not file-type-scoped.** The plugin
  README's "Relationship to Hermes" paragraph (P3-T3 by design)
  would fire on file-type scoping. Directory scoping avoids that
  false positive.
+ **G3. Q2 — forbidden-token tables are bidirectional.** Each
  platform has its own list of forbidden tokens (the other's
  engine identifiers). Tests are symmetric: 2 methods, one per
  direction.
+ **G4. Q2 in-scope directory list — minimal.** Hermes:
  `src/`, `pyproject.toml` (runtime). Plugin: `.claude-plugin/`,
  `commands/`, `agents/` (manifest + executable artifacts). NOT
  `skills/` — skill bodies are prose; documentary references OK.
+ **G5. Q3 — `ubuntu-latest` chosen for greenfield clarity.**
  Legacy `self-hosted` requires the user's CI runner pool. Out
  of the box, `ubuntu-latest` works for anyone forking the repo.
+ **G6. Q4 — minimal-honest means "mirror the project-level
  scope, don't invent new content".** Each platform CHANGELOG
  cites the project-level entry as the authoritative full
  record.
+ **G7. Q5 — full mirror, not extraction.** Hermes README needs
  the same substantive user-facing content as the plugin's. The
  extraction option would force users to context-switch.
+ **G8. Q6 — MIT consistent with plugin manifest.** A mismatch
  (LICENSE = Apache, manifest = MIT) would be a real bug.
+ **G9. Q7 — explicit no-bump for framework.** P4 doesn't change
  the spec; only enforces it.

### Pass 2 — 2026-05-21T00:35:00Z

+ **G10. Test-module file naming convention.** Sub-package
  modules use `test_version_declaration.py` + `test_engine_isolation.py`
  — names describe *what* is tested, not *which platform*. Both
  modules assert across all platforms. Consistent with the
  existing top-level naming (`test_governance.py` covers all
  governance, not a specific module).
+ **G11. PC4 case-insensitivity.** The forbidden-token spec
  notes case-insensitive matching. Important because `Hermes` /
  `hermes` / `HERMES` could all appear. Test uses Python's
  `re.IGNORECASE`.
+ **G12. `commands/` in plugin scope — is `save-plan.md` at
  risk?** Re-checked: `save-plan.md` mentions `TodoWrite`,
  `CLAUDE.md`, plans/ — no Hermes engine tokens. Clean.
+ **G13. Hermes `agent-skills/` — should it be in PC4 scope?**
  Recon showed `sdd-orchestrator/SKILL.md` mentions "aidoc-flow
  migration". Not an engine reference (the project's name, not
  the plugin engine). If we added `agent-skills/` to scope, we'd
  generate a false positive. Confirmed exclusion.
+ **G14. License copyright line.** Standard MIT `Copyright (c)
  YYYY <name>` line. Use `vladm3105` as the copyright holder
  (matches the GitHub repo owner). Cleaner than `Vladislav
  Mikhayskiy` (avoids the Finding 1 misattribution risk from
  P3-T3 — git config returns `Claude` not the owner; here we
  derive from the repo URL).
+ **G15. No new findings on Approach / Step sequence /
  Verification.** Plan is internally consistent and the verify
  gates are observable. Ready to present on approval.
