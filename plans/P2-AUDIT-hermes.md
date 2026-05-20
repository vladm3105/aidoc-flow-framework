# Phase 2 Audit — Hermes platform

| Field      | Value                                |
|------------|--------------------------------------|
| Audit of   | `legacy/ucx_hermes/`, `legacy/mcp_ucx/` |
| Target     | `platforms/hermes/`                  |
| Produced by| P2-T0                                |
| Date       | 2026-05-19T14:15:00Z                 |

## Summary

Phase 2's input shrinks from the assumed 535 files to **280 files in
`legacy/ucx_hermes/`**. `legacy/mcp_ucx/` is the deprecated **predecessor**
of `ucx_hermes` (confirmed by the in-tree migration doc at
`legacy/ucx_hermes/docs/migration/MIGRATION_FROM_MCP_UCX.md`) and is fully out
of scope — it stays frozen in `legacy/`. Per the user directive ("use
ucx_hermes"), the entire `mcp_ucx` tree is classified **drop (whole tree)**.

The remaining 280 files port into `platforms/hermes/` with **four
framework-coupling sites** to rewire to `framework/`. The current 25-test
conformance suite asserts only on `framework/`; it makes no assertion about
platforms today, so the Phase 2 obligation is small: don't break the suite,
repoint the coupling sites, and declare `framework_spec_version` (mechanism
defined in P2-T1).

## 1. Inventory

### `legacy/ucx_hermes/` — 280 files, in scope

```
docs/        — CHANGELOG, architecture, migration, plans, policies, specs
examples/    — usage examples
prompts/     — MCP prompts (+ templates/)
skills/      — README.md, hermes/, layer_aliases/, personas/, persona_mappings.yaml
src/         — mcp_server package (18 sub-modules)
templates/   — layer template YAMLs (BRD/PRD/EARS/BDD/ADR/SPEC/TDD/IPLAN-TEMPLATE.yaml) + archive/
tests/       — contract/, integration/, unit/
pyproject.toml — name "ucx-hermes-server", version 2.0.0, scripts.mcp-ucx
```

`src/mcp_server/` modules: `cleanup`, `cli`, `consistency`, `core`,
`creation`, `executor`, `link_validation`, `models`, `preflight`,
`prescreening`, `prompts`, `remediation`, `reporting`, `review`, `scan`,
`scoring`, `skills`, `utils`, `validation`.

### `legacy/mcp_ucx/` — 255 files, **out of scope**

Same shape as `ucx_hermes` (mirror dirs), pyproject `name = "mcp-ucx-server"`,
version **0.1.0** in pyproject but described as **v1.22.0 (frozen,
deprecated)** in the migration doc.

### `platforms/hermes/` — currently empty

`README.md` only (1 file, 722 bytes — scaffolded).

### `legacy/` — root-level files (added 2026-05-20T09:25:00Z — see §5b)

Seven files at `legacy/` root, three of them Hermes-relevant. Initial Pass
1/2 scoped the audit to the two named subdirectories and missed these.
Classified in §5b.

## 2. Relationship — `ucx_hermes` ↔ `mcp_ucx` (R1 resolved)

**`mcp_ucx` is the deprecated predecessor; `ucx_hermes` is the canonical
successor.** Direct quote from
`legacy/ucx_hermes/docs/migration/MIGRATION_FROM_MCP_UCX.md`:

> The `mcp_ucx/` directory is **deprecated** and **frozen at v1.22.0**. All
> active MCP code, tests, docs, templates, prompts, and skills now live in
> `ucx_hermes/`.

Substantive differences (per the migration doc):

| Concern | `mcp_ucx` (deprecated) | `ucx_hermes` (active) |
|---------|------------------------|------------------------|
| AI executor delegation | Silent auto-rewrite via stateless agents | Removed from document-critical paths; returns structured reports/prompts only |
| Validation safety | Conditional AI fix path inside `sdd_validate` | 100% deterministic; fix path returns report text, does not execute |
| Hermes integration | None | Bridge skill + integration doc + explicit safety contract |

Cross-import check: `mcp_ucx` does **not** import from `ucx_hermes`, and
`ucx_hermes` does not import `mcp_ucx` (only docs reference the old name).
There is no library/server split — they're the same project at two evolution
points.

**Conclusion:** Phase 2 ports `ucx_hermes` only. `mcp_ucx` stays frozen
under `legacy/` and is archived at Phase 5 with the rest of legacy.

## 3. Framework coupling

Two classes — **both must be rewired in P2-T3**. The verify re-grep on the
initial audit caught prose-level coupling that an earlier pass missed; the
list below is the corrected, complete set.

### 3a. Code-level (4 files, 6 lines — mandatory runtime rewire)

Path constants used by the running MCP server. Wrong values break behaviour.

| File | Lines | Current reference | Target |
|------|-------|-------------------|--------|
| `src/mcp_server/skills/scaffold.py` | 75, 78 | `repo_root / "ucx_flow_v3"` | `repo_root / "framework"` (or `framework/layers/`) |
| `src/mcp_server/validation/runner.py` | 156, 161 | `project_root / "ucx_flow_v3"`, `framework_root / "ucx_flow_v3"` | `framework/` |
| `src/mcp_server/utils/template_naming.py` | 17 | docstring: `ucx_flow_v3/01_BRD/` | docstring → `framework/layers/01_BRD/` |
| `src/mcp_server/creation/profile_contracts.py` | 68 | `registry_source: str = "ucx_flow_v3/LAYER_REGISTRY.yaml"` | `framework/registry/LAYER_REGISTRY.yaml` |

### 3b. Prose-level (skills + templates — documentation accuracy)

Markdown bodies and YAML comment headers reference `ucx_flow_v3` by name.
They don't affect runtime, but the platform's docs and template headers
would be inaccurate after the port. Rewire in the same P2-T3 pass.

| File | Kind |
|------|------|
| `skills/README.md` | table mention (line 20) |
| `skills/hermes/README.md` | prose (line 40) |
| `skills/hermes/ucx-kb-maintenance/KB_GENERAL_RULES.md` | prose (line 5) |
| `skills/hermes/ucx-kb-context/SKILL.md` | prose (line 26) |
| `skills/hermes/ucx-sdd-bridge/SKILL.md` | prose (lines 48, 50, 137) |
| `templates/README.md` | prose + paths (lines 4, 50, 54, 100) |
| `templates/{BRD,PRD,EARS,BDD,ADR,SPEC,TDD,IPLAN}-TEMPLATE.yaml` | comment header (`# v3 changes from ucx_flow_v3:`) — present on each layer template |

**Verify gate for P2-T3:** a fresh `grep -rE 'ucx_flow|UCX_FLOW'
platforms/hermes/` after the port returns **zero**.

**Note (post-D-0013):** `templates/` is dropped entirely; the platform
consumes `framework/layers/`. The `templates/`-prefixed entries above
remain listed for audit completeness but are not rewired in P2-T3 because
those files are not copied. P2-T3's effective prose-level rewire covers
the 5 `skills/` markdown files and the new §5b files.

## 4. Conformance gap

The current 25-test suite at `tests/conformance/` asserts only on
`framework/` — `_spec.py` defines `FRAMEWORK = REPO_ROOT / "framework"` and
every test loads from there. **No existing test makes any assertion about a
platform.**

Hermes' Phase 2 obligations against the suite are therefore:

1. **Do not modify `framework/`** — Hermes lives under `platforms/hermes/`, so
   this is structural, not a code constraint.
2. **Declare `framework_spec_version`** per D-0009 / docs/TAGGING.md. The
   *mechanism* (where the declaration lives) is not yet fixed — see Open
   Questions below; resolved in **P2-T1**.
3. **Repoint the 4 coupling sites** from §3 in P2-T3.

Platform-level conformance tests (e.g. "every `platforms/<name>/` declares a
`framework_spec_version`", "no platform writes to `framework/`") are **not
in the current suite**. They are deferred to **Phase 4 — Conformance &
Independence**, which is when both platforms are formally verified. Phase 2's
suite-pass gate is the existing 25 tests continuing to pass.

## 5. Classification matrix

### `legacy/mcp_ucx/` (whole tree)

| Path | Files | Class | Note |
|------|-------|-------|------|
| `legacy/mcp_ucx/**` | 255 | **drop** | Deprecated predecessor; frozen in `legacy/`, archived at Phase 5. |

### `legacy/ucx_hermes/` — per top-level path

| Path | Files | Class | Note |
|------|-------|-------|------|
| `pyproject.toml` | 1 | **port-with-repoint** | Rename package; revisit `scripts.mcp-ucx` entry; review deps. Target name decided in P2-T1. |
| `src/mcp_server/` | ~100 | **port-with-repoint** | Copy verbatim; rewire 4 framework-coupling sites to `framework/`. |
| `tests/` | ~50 | **port-with-repoint** | Three subdirs (contract/, integration/, unit/) — copy; fix any path constants that referenced `ucx_flow_v3`. |
| `docs/CHANGELOG/` | — | **port-with-repoint** | Becomes the platform's CHANGELOG. Reset version line per P2-T6 (`hermes/v0.1.0` is fresh; the legacy 2.0.0 lineage stops here). |
| `docs/architecture/` | — | **port-with-repoint** | Update any `ucx_flow_v3` path references. |
| `docs/plans/` | — | **port-with-repoint** | Update path references. |
| `docs/policies/` | — | **port-with-repoint** | Update path references. |
| `docs/specs/` | — | **port-with-repoint** | Update path references. |
| `docs/migration/` | — | **drop** | Migration-from-mcp_ucx doc; obsolete in the new layout (mcp_ucx is archived at Phase 5). |
| `examples/` | — | **port-verbatim** | Usage examples; no framework coupling detected. |
| `prompts/` | — | **port-verbatim** | MCP prompt files; no `ucx_flow` references detected. |
| `skills/README.md` | 1 | **port-with-repoint** | Prose ref at line 20 (§3b). |
| `skills/hermes/` | 5 skills | **port-with-repoint** | Hermes-specific skills (`ucx-github-deploy-governance`, `ucx-github-governance`, `ucx-kb-context`, `ucx-kb-maintenance`, `ucx-sdd-bridge`); prose refs in 4 of 5 (§3b). |
| `skills/layer_aliases/` | — | **port-verbatim** | Alias map; no `ucx_flow` references detected. |
| `skills/personas/` + `persona_mappings.yaml` | — | **port-verbatim** | Persona definitions; no `ucx_flow` references detected. |
| `templates/` | ~10 YAML + archive/ | **drop (D-0013)** | Resolved in P2-T1 Q3: framework already ships engine-agnostic `*-TEMPLATE.yaml` for all 8 layers (`framework/layers/<NN>_<X>/`). Platforms consume from there. Platform's `templates/` dropped entirely. |

**Coverage:** `mcp_ucx/` (255, dropped wholesale) + ucx_hermes top-level
paths above = all 535 files accounted for; classified `port-verbatim` |
`port-with-repoint` | `drop` | `defer` per the plan's verify clause.
**See §5b for the legacy-root-level-files correction added 2026-05-20.**

### 5b. Legacy root-level files (audit-scope gap correction, 2026-05-20T09:25:00Z)

Pass 1/2 of P2-T0 scoped the audit to the two named subdirectories
(`legacy/ucx_hermes/`, `legacy/mcp_ucx/`). It did not consider files at
`legacy/` root. Seven exist; three are Hermes-relevant and were missed
until the user surfaced `HERMES_UCX_RUNTIME_ENVIRONMENT.md`. Classification:

| File | Class | Target / Disposition |
|------|-------|---------------------|
| `legacy/HERMES_UCX_RUNTIME_ENVIRONMENT.md` | **ported via P2-T7** | The user-added skill package on main carries a byte-identical copy at `hermes_agent_skills/spec-driven-development/sdd-orchestrator/root-docs/`. P2-T7 lands it at `platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/root-docs/RUNTIME_ENVIRONMENT_OR_LIKE.md`. P2-T3 does **not** double-port from `legacy/`. |
| `legacy/MULTI_PROJECT_QUICK_REFERENCE.md` | **ported via P2-T7** | Same — byte-identical copy ported via P2-T7. |
| `legacy/MULTI_PROJECT_SETUP_GUIDE.md` | **ported via P2-T7** | Same — byte-identical copy ported via P2-T7. |
| `legacy/pyproject.toml` | **drop** | Legacy top-level workspace project file; new repo has per-platform `pyproject.toml`s, no top-level one. |
| `legacy/pytest.ini` | **drop** | Legacy top-level pytest config; each platform carries its own. |
| `legacy/requirements-test.txt` | **drop** | Legacy top-level test deps; each platform carries its own. |
| `legacy/README.md` | **out of scope** | Stays in `legacy/`; explicitly marks the dir as frozen. |

**Effect on P2-T3 scope:** add the three port-with-repoint root-level files
(`HERMES_UCX_RUNTIME_ENVIRONMENT.md`, `MULTI_PROJECT_QUICK_REFERENCE.md`,
`MULTI_PROJECT_SETUP_GUIDE.md`) to the copy + prose-rewire set. Exact
target subpaths within `platforms/hermes/docs/` decided by P2-T3 by content
fit (architecture/ vs docs/ root vs policies/).

**Effect on file accounting:** Phase 2 input is now 280 (ucx_hermes) +
3 (legacy root) = **283 files** to port. The 4 drop / out-of-scope
root-level files are recorded but require no action.

## 6. Open questions (for P2-T1 design)

1. **Python module / package name.** `ucx_hermes` ships `src/mcp_server/`
   (import path `mcp_server`). If a future platform also needs an
   `mcp_server` name, they'll collide on install. Decide:
   `platforms/hermes/src/hermes_mcp/` or keep `mcp_server` with a unique
   distribution name (`hermes-server`). Affects every import in `src/` and
   `tests/`.

2. **`framework_spec_version` declaration mechanism.** D-0009 mandates that
   platforms declare which spec version they conform to, but the mechanism
   is not fixed. Candidates:
   - `platforms/hermes/VERSION` (platform's own SemVer per docs/TAGGING.md)
     **plus** `platforms/hermes/FRAMEWORK_SPEC_VERSION` (single line, bare
     SemVer matching `framework/VERSION`).
   - A key in `pyproject.toml` (e.g. `[tool.hermes] framework_spec_version =
     "0.1.0"`).
   - A YAML manifest (`platforms/hermes/manifest.yaml`).
   Recommendation: two plain-text VERSION files (mirrors framework/VERSION
   pattern; easiest to grep and machine-read).

3. **`templates/` overlap.** `ucx_hermes/templates/` holds runtime YAML
   templates the MCP server consumes (BRD-TEMPLATE.yaml, PRD-TEMPLATE.yaml,
   …). `framework/layers/*/` holds the framework's *index templates* in
   markdown (e.g. `BRD-00_index.TEMPLATE.md`). Different artifacts, same
   names. Decide: keep both (platform owns its runtime templates), drop the
   platform's templates in favour of generating from the framework, or
   restructure. Affects P2-T3 directly.

4. **Distribution script entry.** Both legacy `pyproject.toml` files declare
   `scripts.mcp-ucx = "mcp_server.server:main_sync"`. The CLI name `mcp-ucx`
   carries the old project's name; decide whether the platform ships
   `mcp-hermes` (or similar) instead.

5. **Conformance suite extension to platform-level checks.** Not in scope for
   Phase 2 — deferred to Phase 4 — but worth noting that the audit's
   conformance-gap (§4) implies a future test like "every `platforms/*/`
   carries a `FRAMEWORK_SPEC_VERSION` that matches `framework/VERSION`."

## 7. Verify (against the plan's gate)

- All 535 + 7 = 542 files classified across the audited scope: 255
  (mcp_ucx, drop wholesale) + ucx_hermes per-dir matrix (every top-level
  path) + 7 legacy-root files (§5b, added post-implementation).
- `ucx_hermes ↔ mcp_ucx` relationship named: **renamed/superseded**
  (predecessor frozen).
- Framework-coupling list complete — 4 code-level files (§3a) + the
  prose-level set in §3b. Fresh `grep -rE 'ucx_flow|UCX_FLOW' legacy/ucx_hermes`
  returns only files listed in §3a/§3b (the initial draft listed only the
  code-level set; the verify pass caught the prose-level files and §3b
  records them).
- Conformance gap stated against the actual `tests/conformance/_spec.py` and
  the existing 6 test modules; the framework conformance suite (25 tests)
  runs green during this audit — confirming the audit moved no files.
- No code or files moved by this audit (`git status` shows only `plans/`
  and `docs/`-style edits).
- **§5b correction (2026-05-20):** legacy root-level files audited;
  3 Hermes-relevant files added to P2-T3 scope; 4 root-level files
  classified drop / out-of-scope. P2-T0-PLAN Pass 4 retrospective records
  the scope-completeness lesson.
