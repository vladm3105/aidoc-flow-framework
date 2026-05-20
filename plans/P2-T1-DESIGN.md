# P2-T1 Design — Hermes platform

| Field      | Value                                |
|------------|--------------------------------------|
| Task       | P2-T1                                |
| Produced by| P2-T1 (`plans/P2-T1-PLAN.md`)        |
| Date       | 2026-05-19T14:50:00Z                 |
| Feeds      | P2-T2, P2-T3, P2-T4                  |

## Summary

Five design choices resolved before any code moves:

| Q | Question | Choice |
|---|----------|--------|
| Q1 | Python module / package name | Keep `mcp_server` import path; rename **distribution** to `hermes-server` |
| Q2 | `framework_spec_version` declaration | Two plain-text files: `platforms/hermes/VERSION` + `platforms/hermes/FRAMEWORK_SPEC_VERSION` |
| Q3 | `templates/` overlap | **Drop platform templates**; consume `framework/layers/*/*-TEMPLATE.yaml` at runtime (D-0013) |
| Q4 | Distribution script entry | `hermes-mcp = "mcp_server.server:main_sync"` |
| Q5 | Target `platforms/hermes/` layout | Mirror legacy minus dropped paths; add the two VERSION files at top |

The single non-obvious choice — Q3 — is also recorded as D-0013 in
`plans/DECISIONS.md`. No cross-question conflicts surfaced.

## Q1 — Python module / package name

**Options:**
1. Keep `mcp_server` import path; rename distribution to `hermes-server`.
2. Rename import path to `hermes_mcp` (`platforms/hermes/src/hermes_mcp/`); rename distribution.
3. Rename to `aidocflow_hermes` / `aidocflow.hermes`.

**Input gathered:** `platforms/claude-code-plugin/` is a **Claude Code plugin**
— JS + Markdown + `.claude-plugin/plugin.json` (per `docs/REPO_STRUCTURE.md`
and ROADMAP Phase 3). It ships **no Python package**, so there is **no
Python import collision** to design around. The collision risk Q1 was
originally built on does not exist.

**Chosen:** Option 1 — keep `mcp_server` as the import path; change only
the **distribution name** (in `pyproject.toml`) to `hermes-server`.

**Rationale:** With no Platform B Python package to collide with, the
distinct-distribution-name approach gets full identity (the *project*
identifies as `hermes-server`) at **zero import churn** in `src/` and
`tests/`. Every option > 1 would force renaming dozens to hundreds of
imports across the codebase for no functional gain. Minimal-churn wins on
all criteria.

**Downstream implications:**
- **P2-T3 `pyproject.toml`:** `[project] name = "hermes-server"`.
- **P2-T3 src/ + tests/:** zero import edits required.
- Future-proofing: if a *third* MCP platform later wants to ship a
  `mcp_server` package, the distinct distribution name (`hermes-server`)
  still distinguishes them. Import-time collision is then a separate (and
  cleanly-addressable) Phase-N concern, not P2-T1's problem.

## Q2 — `framework_spec_version` declaration mechanism

**Options:**
1. Two plain-text files: `platforms/hermes/VERSION` + `platforms/hermes/FRAMEWORK_SPEC_VERSION`.
2. Single key in `pyproject.toml`: `[tool.hermes] framework_spec_version = "0.1.0"`.
3. YAML manifest: `platforms/hermes/manifest.yaml`.

**Chosen:** Option 1 — two plain-text files, each a single bare SemVer line.

**Rationale:** Mirrors `framework/VERSION` exactly (D-0006 / D-0009 — "bare
SemVer; `v` is added by the tag, not stored in the file"). Greppable,
machine-readable in any language, no parser dependency, no schema-version
churn. Option 2 couples spec conformance to a Python-only build artifact
(future non-Python platforms would need a different mechanism). Option 3
adds a YAML schema for a single value. KISS wins.

**Downstream implications:**
- **P2-T4** creates:
  - `platforms/hermes/VERSION` — the platform's own SemVer (initial value
    `0.1.0`, per the platform tag namespace in `docs/TAGGING.md`).
  - `platforms/hermes/FRAMEWORK_SPEC_VERSION` — the spec version Hermes
    claims to conform to (initial value `0.1.0`, matching
    `framework/VERSION`).
- **Phase 4** conformance test (when added): assert
  `platforms/<name>/FRAMEWORK_SPEC_VERSION` exists, is a bare SemVer, and
  matches `framework/VERSION`. Phase 4 — not P2-T4.

## Q3 — `templates/` overlap

**Inputs gathered:**
- `framework/layers/<NN>_<X>/` ships **`<X>-TEMPLATE.yaml`** for all 8
  layers (BRD, PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN). Confirmed by
  directory listing.
- Framework templates are **engine-agnostic**: `grep -nE
  'ucx_hermes|mcp_ucx|server:|sdd_validate'` against
  `framework/layers/01_BRD/BRD-TEMPLATE.yaml` returns **zero**.
- Hermes templates (`legacy/ucx_hermes/templates/*-TEMPLATE.yaml`) are
  near-identical (975 vs 978 lines for BRD) but **embed engine hardcodes**:
  `server: ucx_hermes`, "All validation runs through ucx_hermes MCP tools",
  etc. (audit §3b prose-level coupling).
- `legacy/ucx_hermes/templates/` also ships **`BRD-MD-TEMPLATE.md`** — a
  markdown variant with no framework equivalent. Single file.

So the YAMLs aren't two artifacts that happen to share names — **they are
the same artifact, with platform-specific drift**, and the framework already
holds the engine-agnostic source of truth.

**Options:**
1. Drop platform templates entirely; consume `framework/layers/` at runtime.
2. Keep platform copies; require the platform to update them whenever the
   framework's change.
3. Keep platform copies as a thin override layer (engine-specific patch on
   top of framework).

**Chosen:** Option 1 — `platforms/hermes/templates/` does **not** exist.
The platform's runtime template-loader reads from
`framework/layers/<NN>_<X>/<X>-TEMPLATE.yaml`.

**Rationale:** The framework being engine-agnostic means platform-specific
content (`server: ucx_hermes`) **shouldn't be in the template at all** —
it's a runtime concern, not a document concern. Option 2 creates a
guaranteed drift problem (we just confirmed the legacy copies have drifted
by exactly that block). Option 3 adds an override layer to solve a problem
that shouldn't exist if the runtime stops requiring engine-named fields.
This is the architecturally correct answer, and the audit's §3b prose
coupling in `templates/*.yaml` simply evaporates — those files don't get
copied at all.

**The `BRD-MD-TEMPLATE.md` exception:** one Hermes-only template (markdown
BRD variant) has no framework equivalent. P2-T3 investigation:

- If any platform code references it → port the single file to
  `platforms/hermes/skills/<consumer>/` (wherever it's actually used) or
  to a new `platforms/hermes/runtime-templates/` if the runtime path
  needs one.
- If unused → drop.
- Either way: it does **not** justify keeping the whole `templates/`
  directory.

**Downstream implications:**
- **P2-T3:** do **not** copy `legacy/ucx_hermes/templates/` to
  `platforms/hermes/templates/`. Investigate `BRD-MD-TEMPLATE.md` usage;
  port-or-drop based on the answer.
- **P2-T3 (code repoint):** `src/mcp_server/utils/template_naming.py`,
  `src/mcp_server/skills/scaffold.py`, and any other template-path code
  must read from `framework/layers/<NN>_<X>/` instead of any local
  `templates/` directory. May require a small extension of the runtime
  loader (path-by-layer-number, not flat-name).
- **Engine-name fields:** the platform's validation/runtime must stop
  *requiring* `server: ucx_hermes`-style fields in templates, since the
  framework's templates don't carry them. If the legacy code reads
  `template['metadata']['validation']['server']` for any logic, that
  logic moves to platform-side config in P2-T3.
- **Recorded as D-0013** in `plans/DECISIONS.md`.

## Q4 — Distribution script entry

**Options:**
1. `hermes-mcp = "mcp_server.server:main_sync"`
2. `mcp-hermes = "mcp_server.server:main_sync"`
3. Keep legacy `mcp-ucx`.

**Chosen:** Option 1 — `hermes-mcp`.

**Rationale:** Identifies the platform first (`hermes`-…), the protocol
second (`-mcp`). Reads naturally ("the Hermes MCP server"). Option 2 reads
backwards (the protocol isn't the identity). Option 3 inherits the legacy
project's name and is misleading. Collision with the (now-frozen)
`legacy/mcp_ucx/` script doesn't matter — legacy isn't installable from
this repo.

**Downstream implications:**
- **P2-T3 `pyproject.toml`:**
  ```toml
  [project.scripts]
  hermes-mcp = "mcp_server.server:main_sync"
  ```
- Docs / READMEs / install instructions reference `hermes-mcp` going
  forward (cleaned up in P2-T3 as part of the docs port).
- `.mcp.json` (P2-T3): the command name in the MCP config points at the
  new entry.

## Q5 — Target `platforms/hermes/` layout

**Options:**
1. Mirror legacy structure (`src/`, `tests/`, `skills/`, `docs/`,
   `examples/`, `prompts/`, `pyproject.toml`) minus the paths the audit
   dropped (`templates/` per Q3, `docs/migration/`).
2. Restructure (e.g. flatten `src/mcp_server/` directly under
   `platforms/hermes/src/` — drop the inner package dir).
3. Hybrid (mirror but rename some dirs).

**Chosen:** Option 1 — mirror legacy layout, with the audit-driven removals
and the two VERSION files added at the top.

Concrete layout (top two levels):

```
platforms/hermes/
├── VERSION                       # platform SemVer (0.1.0 initial)
├── FRAMEWORK_SPEC_VERSION        # spec conformance (0.1.0 initial)
├── pyproject.toml                # name = "hermes-server"; scripts.hermes-mcp
├── README.md
├── src/
│   └── mcp_server/               # unchanged import path
├── tests/
│   ├── contract/
│   ├── integration/
│   └── unit/
├── skills/
│   ├── README.md
│   ├── hermes/                   # platform-specific skills (port-with-repoint)
│   ├── layer_aliases/
│   ├── personas/
│   └── persona_mappings.yaml
├── docs/
│   ├── CHANGELOG/
│   ├── architecture/
│   ├── plans/
│   ├── policies/
│   └── specs/                    # NOT docs/migration/ — dropped
├── examples/
└── prompts/
```

**Excluded** from the target tree (by P2-T0 audit / P2-T1 design):
`templates/` (Q3), `docs/migration/` (P2-T0 audit §5).

**Rationale:** Minimal churn, predictable for anyone who knows the legacy
layout, no surprise renames. The two added files (VERSION,
FRAMEWORK_SPEC_VERSION) are the only structural additions and they live at
the conventional top.

**Downstream implications:**
- **P2-T2** copy targets: `examples/`, `prompts/`, `skills/layer_aliases/`,
  `skills/personas/`, `persona_mappings.yaml` map to identical paths under
  `platforms/hermes/`.
- **P2-T3** copy targets: `pyproject.toml`, `src/`, `tests/`, `docs/` (less
  `docs/migration/`), `skills/README.md`, `skills/hermes/` map to identical
  paths.
- **P2-T4:** the two VERSION files land at top.

## Cross-question conflicts

None. Specifically checked:

- Q3 (drop `templates/`) × Q5 (layout) — accommodated; `templates/` absent
  from the target tree.
- Q1 (keep `mcp_server` import) × Q4 (`hermes-mcp` script entry) —
  compatible; the script targets `mcp_server.server:main_sync`.
- Q2 (top-level VERSION files) × Q5 (top-level layout) — both at
  `platforms/hermes/`'s top; no contest.
- Q1 (distribution `hermes-server`) × Q4 (script `hermes-mcp`) — distinct
  identifiers, no collision.

## Deferred items

The plan's scope locked in five questions. Items surfaced during evaluation
that aren't yet resolved:

1. **`BRD-MD-TEMPLATE.md` placement** — investigation deferred to **P2-T3**
   (port-or-drop based on whether platform code references it). The
   *category* — single-file exception — is decided here; the *destination*
   needs the call-site check.
2. **Runtime template-loader extension** — the platform's template loader
   currently expects a flat `templates/` directory; under Q3 it must read
   from per-layer dirs in `framework/layers/`. The extension itself is
   **P2-T3 code work**, not a P2-T1 design question — but flagged here so
   P2-T3 doesn't treat it as a surprise.
3. **Validation field `server: ucx_hermes`** — code that requires this
   field at runtime needs the dependency removed (per Q3 rationale). Also
   P2-T3 code work, flagged here.

These are implementation tasks for P2-T3, not new design questions.

## Verify (against the plan's gate)

- **All five questions covered** (list-completeness check, lesson from
  P2-T0 Pass 3): Q1 ✓ Q2 ✓ Q3 ✓ Q4 ✓ Q5 ✓.
- Each section carries options / chosen / rationale / downstream
  implications.
- **Q1** — names both the import path (`mcp_server`) and the distribution
  name (`hermes-server`); confirms no Platform B Python collision via
  inspection of `platforms/claude-code-plugin/`.
- **Q2** — chosen approach is concretely implementable in P2-T4 against
  `framework/VERSION` (two `cat`-able files).
- **Q3** — names what happens to **each** template file: the 8 YAMLs are
  dropped (consume from framework); the lone `BRD-MD-TEMPLATE.md` has its
  deferral rule recorded (P2-T3 investigates and ports-or-drops).
- **Q4** — `hermes-mcp` doesn't collide with anything installable from the
  new repo (legacy `mcp-ucx` is frozen and not installed).
- **Q5** — the target layout is sketched as a path tree, top two levels.
- Cross-question conflicts: explicitly checked, none.
- **D-0013** recorded for Q3 (the architecturally non-obvious choice).
- **No code or files moved by P2-T1** — `git status` shows only `plans/`
  and `plans/DECISIONS.md` edits.
