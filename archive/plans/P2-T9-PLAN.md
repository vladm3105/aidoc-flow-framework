# P2-T9 Plan — Rewire MCP scaffold runtime to `framework/layers/`

| Field      | Value                                |
|------------|--------------------------------------|
| Task       | P2-T9                                |
| Depends on | D-0013, P2-T3 (Hermes runtime ported), P2-T8 (skill templates dropped) |
| Status     | DONE — 2026-05-20T15:30:00Z          |
| Feeds      | P2-T5 (verify — closes the 50-failure gap), P2-T6 (close) |

## Objective

Close the D-0013 architectural gap surfaced by P2-T3: the MCP server's
`scaffold_project_ucx` function still expects a flat
`platforms/hermes/templates/` directory (dropped by D-0013) and reads
layer templates from `framework/` directly (which has the layer dirs
one level deeper, at `framework/layers/<NN>_<X>/`, per P1-T2). After
this task, `scaffold_project_ucx` consumes the framework's per-layer
layout cleanly, the 50 deferred Hermes test failures from P2-T3's V10
all pass, and Phase 2 verify (P2-T5) is unblocked.

## Audit — two bugs, single root cause

P2-T3's V10 ran the Hermes test suite and produced **50 / 447
failures**, all sharing the same stack-trace head:

```
File "src/mcp_server/skills/scaffold.py", line 193, in scaffold_project_ucx
    raise FileNotFoundError(f"Missing canonical scaffold source: {source_path}")
FileNotFoundError: Missing canonical scaffold source: <repo>/platforms/hermes/templates
```

Recon shows two coupled bugs:

### Bug A — `CANONICAL_SCAFFOLD_MAPPINGS[6]` points at the dropped `templates/`

`scaffold.py:9-17`:

```python
CANONICAL_SCAFFOLD_MAPPINGS: tuple[tuple[Path, Path], ...] = (
    (Path("skills/personas"), Path("UCX/skills/personas")),
    (Path("skills/persona_mappings.yaml"), Path("UCX/skills/persona_mappings.yaml")),
    (Path("skills/layer_aliases"), Path("UCX/skills/layer_aliases")),
    (Path("prompts/templates/creation"), Path("UCX/prompts/templates/creation")),
    (Path("prompts/templates/review"), Path("UCX/prompts/templates/review")),
    (Path("prompts/templates/remediation"), Path("UCX/prompts/templates/remediation")),
    (Path("templates"), Path("UCX/templates")),     # ← row 7 / index 6
)
```

The 7th row copies `<platform>/templates/` → `<user-project>/UCX/templates/`
— a flat scaffold of layer templates into the user's project. Pre-D-0013
the platform's `templates/` held 8 flat YAMLs (`BRD-MVP-TEMPLATE.md`,
`PRD-TEMPLATE.yaml`, etc.); P2-T3 dropped that directory per D-0013, so
`source_path.exists()` returns False and the scaffold fails fast at
line 193.

### Bug B — `_default_ssd_root()` returns `framework/` but layers live at `framework/layers/`

`scaffold.py:69-78`:

```python
def _default_ssd_root() -> Path:
    repo_root = _default_repo_root()
    v3_root = repo_root / "framework"
    if v3_root.exists():
        return v3_root
    return repo_root / "framework"
```

`_copy_ssd_layer_assets` (line 140) iterates `ssd_root.iterdir()` looking
for `\d{2}_[A-Z]+` directory names. With `ssd_root = <repo>/framework/`,
that scan finds **zero** layer dirs because the real layout is
`framework/layers/01_BRD/`, `framework/layers/02_PRD/`, etc. — one level
deeper (P1-T2 nested them under `layers/` to leave room for `registry/`,
`governance/`, `VERSION`, methodology docs at the framework root).

The function compounds the bug by checking `v3_root.exists()` and then
returning the same `framework` path in both branches — the condition has
no effect. The variable name `v3_root` is also a stale `ucx_flow_v3`
artifact (P2-T3's path-map only rewrote `ucx_flow_v3` tokens; the local
variable name kept `v3_` because the substring isn't in the regex).

Bug B doesn't show up in P2-T3's V10 because Bug A short-circuits before
the SSD scan. Once Bug A is fixed, Bug B would surface as
`Missing authoritative SSD source: <repo>/framework` (the suite would
still fail). Both must land in the same commit.

### Why the scaffold-init tests (with explicit `ssd_root`) also failed

`test_scaffold_init.py` calls `scaffold_project_ucx(...,
ssd_root=tmp_path / "framework", canonical_root=tmp_path / "canonical")`
— explicit values. Bug B doesn't bite because `_default_ssd_root` isn't
called. **Bug A** still bites because `_create_canonical_scaffold` does
create `templates/` in the fixture (test line 21), and so the runtime
finds the directory; but the fixture also writes a single flat file
`templates/BRD-MVP-TEMPLATE.md`, and the post-scaffold assertion
(test line 54) verifies it landed in the project. Once we remove the
`templates/` row from `CANONICAL_SCAFFOLD_MAPPINGS`, the fixture's
`templates/` dir is orphaned and the assertion at line 54 is wrong —
both need updating. The other 5 tests in `test_scaffold_init.py` don't
make assertions about flat templates and will keep passing.

The 1 test in `test_validation_runner.py` and the 9 tests in
`test_remediation_runner.py` all call `main(["init", ...])` which runs
the real scaffold with default roots — they hit **both** bugs.

## Scope

**In:**

- Remove `(Path("templates"), Path("UCX/templates"))` from
  `CANONICAL_SCAFFOLD_MAPPINGS` (Bug A).
- Rewrite `_default_ssd_root()` to return `<repo>/framework/layers/`
  cleanly, rename the stale `v3_root` local to `layers_root`, and drop
  the no-op `exists()` branch (Bug B).
- Update `test_scaffold_init.py:_create_canonical_scaffold` — remove
  the `templates/` mkdir (line 21) and the `templates/BRD-MVP-TEMPLATE.md`
  write (line 29).
- Update `test_scaffold_init.py:test_scaffold_project_ucx_creates_expected_files`
  — remove the assertion that `UCX/templates/BRD-MVP-TEMPLATE.md` exists
  (line 54). The other two assertions in that test
  (`UCX/templates/layers/01_BRD/BRD-MVP-TEMPLATE.yaml`,
  `UCX/templates/layers/01_BRD/BRD_MVP_SCHEMA.yaml`) verify
  `_copy_ssd_layer_assets` and stay.
- Verify the 50 deferred Hermes failures all pass post-fix.

**Out:**

- `_REQUIRED_SUBDIRS` in `project_ucx_loader.py:25-33` — keep the
  `Path("templates")` entry. After this fix, scaffold creates
  `UCX/templates/layers/<NN>_<X>/`, which implies `UCX/templates/`
  exists as the parent. `validate_project_ucx_root` will still find the
  directory and pass. **No edit needed.** A future cleanup might
  consolidate `templates/` + `templates/layers` into one entry, but
  that's a refactor unrelated to D-0013.
- Other `templates/` mentions in `tool_registry.py:348` (prompt
  template path documentation), `project_ucx_loader.py:28-30` (prompts
  templates) — those refer to **prompt** templates, not **layer**
  templates. Different artifact, different directory, not subject to
  D-0013. Untouched.
- Test fixtures in `test_prompt_context_builder.py` that create
  `UCX/templates/` paths manually — those simulate a scaffolded
  project for prompt-context tests; they don't go through
  `scaffold_project_ucx`, so the fix here doesn't change their
  behavior.
- Conformance suite extension (still Phase 4).
- Behavior beyond D-0013 closure (e.g. discovery / templates schema
  validation / etc.).

## Approach

### 1. `scaffold.py` edits — two scoped changes

**Edit 1.** Delete the `templates/` row from `CANONICAL_SCAFFOLD_MAPPINGS`:

```diff
 CANONICAL_SCAFFOLD_MAPPINGS: tuple[tuple[Path, Path], ...] = (
     (Path("skills/personas"), Path("UCX/skills/personas")),
     (Path("skills/persona_mappings.yaml"), Path("UCX/skills/persona_mappings.yaml")),
     (Path("skills/layer_aliases"), Path("UCX/skills/layer_aliases")),
     (Path("prompts/templates/creation"), Path("UCX/prompts/templates/creation")),
     (Path("prompts/templates/review"), Path("UCX/prompts/templates/review")),
     (Path("prompts/templates/remediation"), Path("UCX/prompts/templates/remediation")),
-    (Path("templates"), Path("UCX/templates")),
 )
```

**Edit 2.** Rewrite `_default_ssd_root()` cleanly:

```diff
 def _default_ssd_root() -> Path:
-    repo_root = _default_repo_root()
-    v3_root = repo_root / "framework"
-    if v3_root.exists():
-        return v3_root
-    return repo_root / "framework"
+    return _default_repo_root() / "framework" / "layers"
```

The new body is a single expression. The `exists()` check in the old
body was a no-op (both branches returned the same path); replacing it
with a direct return removes dead code. The `framework/layers` path is
the canonical layer-template root per P1-T2 / D-0013.

### 2. `test_scaffold_init.py` edits — minimal-touch

**Edit 3.** Remove the `templates/` fixture lines in
`_create_canonical_scaffold`:

```diff
     (root / "prompts/templates/remediation").mkdir(parents=True, exist_ok=True)
-    (root / "templates").mkdir(parents=True, exist_ok=True)

     (root / "skills/personas/architect.md").write_text("architect persona", encoding="utf-8")
     ...
     (root / "prompts/templates/remediation/base.md").write_text("remediate", encoding="utf-8")
-    (root / "templates/BRD-MVP-TEMPLATE.md").write_text("brd template", encoding="utf-8")
```

**Edit 4.** Remove the orphaned assertion at line 54:

```diff
     assert (project_root / "UCX/prompts/templates/review/base.md").exists()
-    assert (project_root / "UCX/templates/BRD-MVP-TEMPLATE.md").exists()
     assert (project_root / "UCX/templates/layers/01_BRD/BRD-MVP-TEMPLATE.yaml").exists()
```

No other test in `test_scaffold_init.py` references `UCX/templates/<X>-TEMPLATE.md`
or `templates/BRD-MVP-TEMPLATE.md` — verified by grep during planning.

### 3. Verify against real framework layout

After the edits, the runtime path with real defaults is:

- `canonical_root = platforms/hermes/` (from `_default_canonical_root`)
- 6 mappings copy from `platforms/hermes/{skills,prompts/templates/*}` →
  user-project `UCX/...`. All 6 source paths exist (verified during
  recon).
- `ssd_root = framework/layers` (new). `_copy_ssd_layer_assets`
  iterates `framework/layers/iterdir()`, matches the 8 layer dirs
  (`01_BRD`..`08_IPLAN`), and copies `-TEMPLATE`-named files from each
  into `<project>/UCX/templates/layers/<NN>_<X>/`.

The framework's per-layer files (recon: `framework/layers/01_BRD/`
contains `BRD-00_index.TEMPLATE.md`, `BRD-TEMPLATE.yaml`, `README.md`)
include the substring `-TEMPLATE` only in the 2 template files
(`BRD-00_index.TEMPLATE.md`, `BRD-TEMPLATE.yaml`). The runtime filter
(`"-TEMPLATE" in name or endswith("_MVP_SCHEMA.yaml")`) selects exactly
those two and skips `README.md`. Correct behavior for the new layout.

### 4. No CANONICAL_SCAFFOLD_MAPPINGS index reshuffle concerns

Removing the last row of the 7-tuple keeps the other 6 in their original
positional indices. No call-site of `CANONICAL_SCAFFOLD_MAPPINGS` uses
positional access (`[6]`) — verified by grep. The tuple is consumed by
the `for ... in CANONICAL_SCAFFOLD_MAPPINGS` loop in
`scaffold_project_ucx`, which doesn't care about ordering. Safe drop.

## Step sequence

1. **Pre-flight:** capture the current failure count baseline.

   ```
   cd platforms/hermes
   PYTHONPATH=src /tmp/hermes-venv/bin/python -m pytest tests/ -q 2>&1 | tail -2
   ```

   Expect: `50 failed, 397 passed` (matches P2-T3 V10).
2. **Edit 1** — remove `templates/` row from `CANONICAL_SCAFFOLD_MAPPINGS`.
3. **Edit 2** — rewrite `_default_ssd_root()`.
4. **Edit 3** — remove `templates/` fixture lines from
   `_create_canonical_scaffold`.
5. **Edit 4** — remove the orphaned assertion at test line 54.
6. **Verify** (see below).
7. **Land** — single commit
   `fix(hermes): rewire scaffold runtime to framework/layers/ (P2-T9, closes D-0013 for MCP server)`;
   update `plans/HANDOFF.md`; tick P2-T9 in `plans/MIGRATION_TODO.md`.
   Push to working branch.

## Verification

- **Hermes test suite passes fully:** all 447 tests green.
  `PYTHONPATH=src /tmp/hermes-venv/bin/python -m pytest tests/ -q` reports
  `447 passed` (or `397 + 50 = 447` — the 50 deferred failures are gone
  and no new failures introduced).
- **Conformance suite still 25/25.**
- **No new `ucx_flow|UCX_FLOW` hits:** zero in `platforms/hermes/src`,
  `platforms/hermes/tests` (sanity — the rename of `v3_root` to
  `layers_root` reduces this by one residual variable-name hit but
  doesn't introduce any).
- **No new `templates/` row in `CANONICAL_SCAFFOLD_MAPPINGS`:**
  `grep -c '"templates"' platforms/hermes/src/mcp_server/skills/scaffold.py`
  returns **0**.
- **`_default_ssd_root` returns the right path:** one-liner check

  ```
  cd platforms/hermes
  PYTHONPATH=src /tmp/hermes-venv/bin/python -c \
    "from mcp_server.skills.scaffold import _default_ssd_root; \
     p = _default_ssd_root(); print(p); print(p.exists()); \
     print(sorted(d.name for d in p.iterdir() if d.is_dir()))"
  ```

  prints `<repo>/framework/layers`, `True`, and the 8 layer dirs.
- **End-to-end smoke (manual):**
  `PYTHONPATH=src /tmp/hermes-venv/bin/python -c \
    "import tempfile, pathlib; from mcp_server.skills.scaffold import scaffold_project_ucx; \
     d = pathlib.Path(tempfile.mkdtemp()); \
     r = scaffold_project_ucx(project_root=d); \
     print('created:', len(r.created_paths)); \
     print('skipped:', len(r.skipped_paths))"`
  exits 0 and reports a non-zero `created` count (proof the full
  scaffold runs cleanly against real defaults).
- **No regression to `project_ucx_loader`:** the `_REQUIRED_SUBDIRS`
  containing `Path("templates")` still succeeds against the new
  scaffold output because `UCX/templates/layers/<NN>_<X>/` implies the
  `UCX/templates/` parent dir. Verified by the smoke test above: the
  smoke-tested temp project has both `UCX/templates/` (auto-created as
  parent) and `UCX/templates/layers/01_BRD/` (created by
  `_copy_ssd_layer_assets`).

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Removing the `templates/` row breaks an external caller that relied on the flat scaffold (e.g. an MCP client tool that expects `UCX/templates/<X>-MVP-TEMPLATE.md` to exist). | The platform's own tests are the contract; no in-repo caller relies on the flat layout (verified by grep for `UCX/templates/[A-Z]+-`). External clients haven't existed yet — Phase 2 is the platform's first ship. Document the change in the commit message; surface in P2-T6 CHANGELOG entry. |
| R2 | `_default_ssd_root` rewrite changes behavior for an explicit-`ssd_root` test caller that passed `tmp_path / "framework"` (the test's flat layer layout). | `_default_ssd_root` is only consulted when `ssd_root is None` in `scaffold_project_ucx`. Tests that pass `ssd_root` explicitly are unaffected. Verified by reading the function flow. |
| R3 | A layer in `framework/layers/` happens to contain a file whose name includes `-TEMPLATE` but isn't intended as a runtime template (e.g. a draft). | Filter at `scaffold.py:145` already gates with `"-TEMPLATE" in name`; matches the framework's `BRD-TEMPLATE.yaml` and `BRD-00_index.TEMPLATE.md` patterns. If a future framework file uses `-TEMPLATE` in a non-template name, that's a framework hygiene issue, not a scaffold-runtime issue. |
| R4 | Other src/ paths reference `platforms/hermes/templates/` and would still try to read it. | Recon scan showed only 3 references: scaffold.py (this fix), project_ucx_loader.py (user-project `<UCX>/templates/`, not platform `templates/` — different), tool_registry.py (prompt templates description, unrelated). No other scan-affected code. |
| R5 | The `test_remediation_runner.py` 9 failures aren't actually about scaffold — they were classified by stack trace, but maybe some have a second root cause. | Verify gate explicitly counts post-fix failures; if ≠ 0, halt and re-diagnose. The plan's success criterion is `447 passed`, not "50 specific failures gone". |
| R6 | The variable-name rename `v3_root` → `layers_root` is cosmetic and could be dropped to minimize diff. | Kept because it removes the only remaining `v3_` residual in `scaffold.py`, restores name accuracy (the path is the layers root, not a "v3" root), and the diff is 1 line. P2-T7 G12 lesson: don't leave stale stub names around. |
| R7 | The smoke-test step writes a tempdir but doesn't clean up. | Acceptable — the dir is in `tempfile.mkdtemp()` and ephemeral. Test hygiene; not a verify-gate concern. |
| R8 | A second runtime call path computes templates locations independently and still expects `platforms/hermes/templates/`. | Verified by full-repo grep during recon (search 1 ran `grep -rE 'platforms/hermes/templates'` against `src/`; zero hits other than the scaffold row we're removing). |

## Review log

### Pass 1 — 2026-05-20T14:40:00Z

- **G1. Two bugs, one root cause — both must land together.** Pass 1
  identified Bug B as a latent failure mode that would surface only
  after Bug A is fixed; if I only fix Bug A, the test suite still
  fails on the next line. Step sequence makes both Edit 1 and Edit 2
  mandatory before verify.
- **G2. Test-fixture orphan after Edit 1.** Removing
  `CANONICAL_SCAFFOLD_MAPPINGS[6]` orphans the fixture's `templates/`
  dir and the line-54 assertion. Caught by reading the test +
  the runtime contract together (Edits 3 + 4). The other 5 tests in
  `test_scaffold_init.py` don't make assertions about flat templates;
  verified by reading every assertion in the file.
- **G3. `_REQUIRED_SUBDIRS` looks unaffected — confirmed via the
  smoke-test.** The post-fix scaffold creates
  `<UCX>/templates/layers/<NN>_<X>/`, which auto-creates the parent
  `<UCX>/templates/`. The `validate_project_ucx_root` check passes
  trivially. No `project_ucx_loader.py` edit needed.
- **G4. The `v3_root` variable name is a stale residual.** P2-T3's
  path-map rewrote `ucx_flow_v3` tokens but didn't touch shorter
  forms like `v3_`. Edit 2 cleans it up. The rename is cosmetic but
  removes 1 of the last `v3` mentions in `src/`.
- **G5. Smoke test as verify (not just unit-test suite).** Unit tests
  pass explicit `ssd_root` / `canonical_root` and don't exercise
  `_default_ssd_root`. The smoke-test step uses defaults — only way
  to prove Bug B is gone end-to-end with the real framework layout.
- **G6. No `CANONICAL_SCAFFOLD_MAPPINGS[6]` callers anywhere.**
  Grepped for positional indexing of the tuple; none found. Safe to
  drop the row.
- **G7. The `exists()` no-op branch.** The old code
  `if v3_root.exists(): return v3_root; return repo_root / "framework"`
  returns the same path either way. Looks like a forgotten halfway-
  refactor (e.g. the `else` branch used to return something else and
  got "simplified" to the same path). Removing it is the right cleanup.
- **G8. Verify gate symmetry (P2-T8 G17 lesson).** Each edit has a
  matching verify: Edit 1 → "no `templates` row in mapping"; Edit 2
  → `_default_ssd_root` returns `framework/layers`; Edit 3+4 → test
  suite passes. Smoke test catches end-to-end behavior that unit-test
  passes alone can't prove.
- **G9. Scope discipline.** R4 enumerates the 3 src files that
  reference `templates/`; only scaffold.py is in scope. P2-T8's R7
  (scope creep) reaffirmed: the prompt-templates rows
  (`prompts/templates/...`) are unrelated and stay.
- **G10. Risk R5 — 9 remediation-runner failures might have a hidden
  second root cause.** Plan acknowledges the unknown and the verify
  gate requires zero failures, not "50 specific tests fixed". If R5
  fires, the implementation halts and we re-plan rather than
  papering over.

### Pass 2 — 2026-05-20T14:55:00Z

- **G11. Filter compatibility with framework layer files.**
  Re-checked `_copy_ssd_layer_assets:145` filter: accepts files with
  `"-TEMPLATE"` substring OR ending in `_MVP_SCHEMA.yaml`. Framework
  files in `framework/layers/01_BRD/` are `BRD-00_index.TEMPLATE.md`
  (matches), `BRD-TEMPLATE.yaml` (matches), `README.md` (excluded).
  Filter behaves correctly for the new layout.
- **G12. Names matter: `BRD-MVP-TEMPLATE.yaml` (test) vs
  `BRD-TEMPLATE.yaml` (framework).** The unit test fixture uses
  `BRD-MVP-TEMPLATE.yaml` while the real framework ships
  `BRD-TEMPLATE.yaml`. Both contain `-TEMPLATE`, so both pass the
  filter. The test asserts the MVP filename because that's what the
  fixture writes — not what the framework ships. Tests stay correct.
- **G13. Idempotency of edits.** Re-running Edits 1+2 on the post-fix
  file would no-op (Edit 1: row already absent; Edit 2: body already
  the one-liner). Edits 3+4 likewise. Safe to re-apply.
- **G14. R6 cosmetic-rename trade-off.** Could leave `v3_root` as-is
  and minimize diff. Decided to rename: 1 line cost, removes a stale
  name, aligns with the project's broader "no `ucx_flow_v3` /
  `v3` residuals" hygiene. Kept the rename in scope.
- **G15. No new findings.** Plan is internally consistent and the
  verify gates cover each edit; ready to present on approval.

### Pass 3 — 2026-05-20T15:30:00Z (retrospective)

Status: DONE. Two implementation-time scope discoveries.

- **G16. `_default_repo_root` was off by one — `parents[4]` vs
  `parents[5]`.** Plan scoped Edit 2 to `_default_ssd_root` only.
  Implementation revealed that `_default_repo_root` ALSO used the
  legacy `parents[4]` count — which pointed at `legacy/` pre-isolation
  but now points at `platforms/` (one level too shallow). With
  Edit 2 returning `_default_repo_root() / "framework/layers"`, the
  bug surfaced as `platforms/framework/layers` (non-existent path).
  Fix: changed `_default_repo_root` to `parents[5]`. The recon during
  planning saw both functions but missed that the depth changed when
  the file moved from `legacy/ucx_hermes/...` to `platforms/hermes/...`
  (same source-relative depth, but `parents[4]` meaning shifted from
  `legacy/` to `platforms/`). **Lesson:** when porting files between
  different directory layouts, audit every `parents[N]` and
  `parents[__file__]`-relative path computation; the count is brittle
  to layout changes. Should have been caught in P2-T3's path-map but
  P2-T3's sed didn't cover integer literals.

- **G17. `validation/runner.py:_resolve_canonical_template_root` had
  the same two bugs.** Plan classified this file as out of scope —
  but with scaffold fixed, smoke tests then surfaced two further
  failures (`test_validate_ears_directory_flow_passes...`,
  `test_main_validate_without_out_uses_document_dir`) tracing to
  `runner.py:155-161`. Same shape: `parents[4]` (should be `[5]`)
  and `/ "framework"` (should be `/ "framework/layers"` to match the
  framework's per-layer layout) — but also a third issue, the
  project-local override path was `project_root / "framework"`
  (sed-rewritten from `ucx_flow_v3`), which never matched after
  scaffold because scaffold installs templates at
  `<project>/UCX/templates/layers/`, not `<project>/framework/`.
  Plan-vs-reality contradiction: the scope's "Out" clause excluded
  `runner.py` on the assumption that scaffold was the only path-
  computer. Wrong — by the same G18 lesson from P2-T3, the "no logic
  edits" Out-clause needed to cross-check the actual code search,
  not just the symptoms in V10. The fix extended to a 3-stage
  precedence chain: `<project>/framework/<NN>_<X>/` override (preserves
  the test fixture's deliberate override semantic), then
  `<project>/UCX/templates/layers/<NN>_<X>/` (scaffold output), then
  `<repo>/framework/layers/` (canonical). The test
  `test_run_project_validation_build_fails_on_missing_required_section`
  exercises override precedence — would have failed without the
  override-first ordering.

- **Lessons for future runtime-path rewires:**
  - Audit **every** `parents[N]` call when files move between
    directory layouts. `parents[N]` is brittle and the count's
    meaning shifts with each path-level change. Better long-term:
    consolidate path resolution into one helper module so the magic
    number is in one place.
  - When fixing a path computer in one module, **grep the codebase
    for the same idiom** (`parents[\d+]`, hardcoded path joins) —
    duplicates are likely. Don't treat the first hit as the only
    one.
  - When test fixtures write to multiple paths to exercise
    precedence, the runtime's path-resolution order is part of the
    contract. Surface the precedence in the fix even if it requires
    additional fallback stages.

## Implementation note (2026-05-20T15:30:00Z)

Executed. Final state: **all 447 Hermes tests pass** (up from 397/447
at start; 50 failures from P2-T3 V10 all resolved). Conformance suite
25/25 unchanged.

Files edited (5 spots across 3 files):

- `platforms/hermes/src/mcp_server/skills/scaffold.py`:
  - Removed `(Path("templates"), Path("UCX/templates"))` from
    `CANONICAL_SCAFFOLD_MAPPINGS` (Bug A).
  - Rewrote `_default_ssd_root()` to a one-liner returning
    `framework/layers` (Bug B).
  - **Plus G16:** updated `_default_repo_root()` from `parents[4]` to
    `parents[5]` so the repo root resolves correctly under the new
    `platforms/hermes/...` layout. Added clarifying comments to both
    `_default_canonical_root` and `_default_repo_root`.
- `platforms/hermes/src/mcp_server/validation/runner.py`:
  - **Plus G17:** rewrote `_resolve_canonical_template_root` as a
    3-stage precedence chain: `<project>/framework/<NN>_<X>/`
    (override) → `<project>/UCX/templates/layers/<NN>_<X>/` (scaffold
    output) → `<repo>/framework/layers/` (canonical, via
    `parents[5]`).
- `platforms/hermes/tests/unit/test_scaffold_init.py`:
  - Removed orphaned `templates/` fixture lines (mkdir + write) in
    `_create_canonical_scaffold` (Edits 3a + 3b).
  - Removed orphaned `UCX/templates/BRD-MVP-TEMPLATE.md` assertion
    in `test_scaffold_project_ucx_creates_expected_files` (Edit 4).

Verify gates (all green):

- **V1.** `CANONICAL_SCAFFOLD_MAPPINGS` no longer has the `templates`
  row.
- **V2.** `_default_ssd_root()` returns
  `<repo>/framework/layers/`; `.exists() == True`; iterdir yields the
  8 expected layer dirs.
- **V3.** Smoke test scaffolds 71 files into a temp project; both
  `UCX/templates/` and `UCX/templates/layers/01_BRD/BRD-TEMPLATE.yaml`
  land correctly. `_REQUIRED_SUBDIRS` check passes implicitly (parent
  dir exists via the layers sub-dir creation).
- **V4.** Conformance suite 25/25.
- **V5.** Hermes test suite 447/447 (was 397/447).
- **Sanity:** zero `platforms/framework/` references; zero
  `ucx_flow|UCX_FLOW` hits in `src/` or `tests/`.

P2-T3 V10's deferred failures are now closed; Phase 2 verify (P2-T5)
no longer has a failing-suite gate to worry about.
