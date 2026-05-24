# P2-T3 Plan — Hermes port-with-repoint

| Field      | Value                                |
|------------|--------------------------------------|
| Task       | P2-T3                                |
| Depends on | P2-T0 audit, P2-T1 design (Q1, Q4, D-0013), P2-T2 (verbatim copy done), P2-T7 (agent-skills already ported, §5b updated) |
| Status     | DONE — 2026-05-20T12:50:00Z          |
| Feeds      | P2-T8 (templates-in-skill drop), P2-T5 (verify), P2-T6 (close) |

## Objective

Copy the **remaining 200 files** of `legacy/ucx_hermes/` (everything classified
`port-with-repoint` by audit §5) into `platforms/hermes/` and rewire **all**
framework-coupling references from `ucx_flow_v3` to `framework/` — both the
code-level constants the running MCP server depends on and the prose / test
references that document or assert them. Apply P2-T1's design choices in
`pyproject.toml` (Q1 `hermes-server` distribution, Q4 `hermes-mcp` script);
add the two VERSION files (folded in from P2-T4); update root `.mcp.json` to
the new platform path. After this task, `platforms/hermes/` carries the
complete Hermes runtime, the conformance suite is still green, and a fresh
`grep -rE 'ucx_flow|UCX_FLOW' platforms/hermes/` returns zero on
current-behavior content.

## Audit refresh — §3 / §5 coverage correction (Pass 1 finding G1)

Recon during planning uncovered three audit-gap files the original P2-T0
§3a/§3b coupling list missed. Resolving as part of this plan (analogous to
P2-T7's §5b correction):

| Class | File | Hits | Origin gap |
|-------|------|------|------------|
| §3a code-mirror — **tests** | `tests/unit/test_scaffold_init.py` | 6 | Tests assert against the §3a code paths but were not enumerated. |
| §3a code-mirror — **tests** | `tests/unit/test_validation_runner.py` | 2 | Same. |
| §3a code-mirror — **tests** | `tests/integration/test_creation_profile_contracts_integration.py` | 1 | Same. |

These 3 test files **must** be rewired alongside the §3a code files —
otherwise the ported test suite would assert against the old `ucx_flow_v3/`
constants. Treat them as **§3a-extension** (mandatory runtime/test rewire),
not §3b prose.

Separately, `docs/` was outside §3a/§3b entirely. Recon shows **17 docs/
files** (~131 hits) containing `ucx_flow_v3`. Per the P2-T7 G13 lesson
(historical / illustrative refs are preserved; current-behavior refs are
rewritten), classify as follows — final per-file judgment lives in
Approach §4:

| Cluster | Files | Disposition |
|---------|-------|-------------|
| **Historical — keep as-is** | `docs/CHANGELOG/CHANGELOG_v{1.11.0,1.16.0,2.0.0}.md`, `docs/ROADMAP.md` (the `v1.22.0` retrospective block, lines 587–601), `docs/plans/PLAN-014_checklist.md`, `docs/plans/PLAN-014_3segment_element_id_migration.md`, `docs/plans/PLAN-016_checklist.md`, `docs/plans/PLAN-016_cross_section_validation.md`, `docs/plans/PLAN-018_yaml_parity_and_api_consistency.md`, `docs/plans/PLAN-021_sdd_reporting_naming_standard.md`, `docs/plans/PLAN-026_persona_management_tools.md` | These describe past work / completed migrations / version history. Rewriting would falsify history. **Preserve verbatim.** |
| **Current behavior — rewrite** | `docs/HERMES_INTEGRATION.md`, `docs/architecture/MCP_OPERATIONAL_FLOWS.md`, `docs/architecture/MCP_UNIFIED_CONTEXT_FRAMEWORK.md`, `docs/architecture/MCP_RUNTIME_ARCHITECTURE.md`, `docs/architecture/MCP_PERSONA_DESIGN_GUIDE.md`, `docs/specs/SPEC-003_mcp_creation_validation_profile_contracts.md` | Describe the runtime / spec as it stands. Rewrite per the path-map. |

A second audit-refresh step inside this plan (Step 7) lands the
correction back into `plans/P2-AUDIT-hermes.md` so future readers see one
authoritative scope.

## Scope

**In:**

- Copy 7 source paths from `legacy/ucx_hermes/` to `platforms/hermes/`,
  byte-identical *except* for the targeted edits in Approach §3–§4:

  | Source | Target | Files |
  |--------|--------|------:|
  | `pyproject.toml` | `pyproject.toml` | 1 |
  | `src/` | `src/` | 63 |
  | `tests/` | `tests/` | 47 |
  | `docs/` excluding `docs/migration/` | `docs/` | 80 |
  | `skills/README.md` | `skills/README.md` | 1 |
  | `skills/hermes/` | `skills/hermes/` | 8 |
  | **Total** | | **200** |

- Edit `pyproject.toml` per P2-T1 Q1 (`name = "hermes-server"`,
  `version = "0.1.0"` — new lineage per P2-T6 rationale) and Q4
  (`[project.scripts] hermes-mcp = "mcp_server.server:main_sync"`).
  Keep the `mcp_server` import path and `packages = ["src/mcp_server"]`.
- Rewire **§3a-extension** (4 code + 3 test = 7 files, 19 hits) — full
  path-map rewrite per Approach §3.
- Rewire **§3b skills prose** (5 files, 6 hits) — same path-map.
- Rewire **current-behavior docs cluster** (6 files, ~14 hits) per the
  audit-refresh classification — same path-map.
- Add `platforms/hermes/VERSION` (single line `0.1.0`) and
  `platforms/hermes/FRAMEWORK_SPEC_VERSION` (single line `0.1.0`,
  matching `framework/VERSION`). **Folded in from former P2-T4.**
- Update root `.mcp.json`: change `cwd` from
  `/opt/data/ucx_framework/legacy/ucx_hermes/src` to
  `/opt/data/ucx_framework/platforms/hermes/src` (path-prefix only —
  user's local Python interpreter path is illustrative per G13, kept).
- Update `plans/P2-AUDIT-hermes.md`: §3a renamed "§3a code + tests"
  with the 3 test files added; §3b unchanged structurally but a footnote
  records the docs split; new §3c "Documentation cluster" added with
  the historical-vs-current classification from this plan.

**Out:**

- Copy of `legacy/ucx_hermes/templates/` — **dropped** per D-0013 (no
  target directory created).
- Copy of `legacy/ucx_hermes/docs/migration/` — **dropped** per audit §5
  (1 file, `MIGRATION_FROM_MCP_UCX.md`).
- Re-port of the 3 legacy-root docs (`HERMES_UCX_RUNTIME_ENVIRONMENT.md`,
  `MULTI_PROJECT_QUICK_REFERENCE.md`, `MULTI_PROJECT_SETUP_GUIDE.md`) —
  already carried by P2-T7 under `platforms/hermes/agent-skills/.../root-docs/`.
- Drop of the skill's `sdd-orchestrator/templates/0N_TYPE-TEMPLATE.yaml`
  duplication — **P2-T8** handles that (different file set, different
  rewire target).
- Conformance suite extension to platform-level checks (Phase 4).
- Behavior changes: no logic edits, no refactors. Edits are limited to
  the path-map and the two pyproject keys.

## Approach

### 1. Copy strategy

Use `cp -r` for each of the 7 source paths into `platforms/hermes/`,
**except** `docs/migration/` which is skipped (P2-T2 used the same
mechanic for the verbatim set). For `docs/`, use a two-step pattern that
makes the omission explicit:

```
mkdir -p platforms/hermes/docs
cp -r legacy/ucx_hermes/docs/* platforms/hermes/docs/
rm -rf platforms/hermes/docs/migration
```

Rationale for the post-copy delete over a `--exclude` rsync: plain `cp`
is already in use by P2-T2; the delete is one line and trivially
auditable; avoids introducing a new tool dependency.

### 2. `pyproject.toml` edits

After copying the legacy file to `platforms/hermes/pyproject.toml`, apply
**three** scoped edits with the `Edit` tool (not sed — risk of corruption
on a TOML structure):

| Key | Legacy value | New value | Source |
|-----|-------------|-----------|--------|
| `[project] name` | `ucx-hermes-server` | `hermes-server` | P2-T1 Q1 |
| `[project] version` | `2.0.0` | `0.1.0` | P2-T6 — fresh `hermes/v0.1.0` lineage; legacy 2.0.0 stops at the audit boundary |
| `[project.scripts]` (key) | `mcp-ucx` | `hermes-mcp` | P2-T1 Q4 |

`description`, `requires-python`, `dependencies`,
`[project.optional-dependencies]`, `[build-system]`,
`[tool.hatch.build.targets.wheel] packages` — all unchanged. The `packages
= ["src/mcp_server"]` line stays as-is (Q1 keeps the import path).

### 3. Path-map for `ucx_flow_v3` rewires (§3a-extension + §3b skills + §3c current-behavior docs)

Apply via `sed -i -E 's/\bucx_flow_v3\b/framework/g' <file>` per file —
**word-boundary regex**, per the P2-T7 G12 lesson — covers both
`ucx_flow_v3/` and bare-name forms (`"ucx_flow_v3"`, `$DIR/ucx_flow_v3`).
After the sed, spot-check that any compound references resolve correctly:

| Pattern after `s/\bucx_flow_v3\b/framework/g` | Action |
|---|---|
| `framework/LAYER_REGISTRY.yaml` | Further edit → `framework/registry/LAYER_REGISTRY.yaml` (registry was extracted into a sub-dir in P1-T3). One occurrence: `src/mcp_server/creation/profile_contracts.py:68`, mirrored in `tests/integration/test_creation_profile_contracts_integration.py:66`. |
| `framework/01_BRD/` (and `02_PRD/`, etc.) in docstring at `src/mcp_server/utils/template_naming.py:17` | Further edit → `framework/layers/01_BRD/` (layers were re-rooted into `framework/layers/` in P1-T2). |
| `framework` (bare, in code as `repo_root / "framework"`) | Correct as-is — points at the framework root. (4 of the §3a hits.) |
| `framework` in prose / test setup paths (e.g. `tmp_path / "framework"` in `test_scaffold_init.py`) | Correct as-is. |

Total file set the sed runs against:

- **7 §3a-extension files** — `src/mcp_server/{skills/scaffold,validation/runner,utils/template_naming,creation/profile_contracts}.py`; `tests/{unit/test_scaffold_init,unit/test_validation_runner,integration/test_creation_profile_contracts_integration}.py`.
- **5 §3b skills files** — `skills/README.md`; `skills/hermes/{README,ucx-kb-maintenance/KB_GENERAL_RULES,ucx-kb-context/SKILL,ucx-sdd-bridge/SKILL}.md`.
- **6 §3c current-behavior docs** — `docs/HERMES_INTEGRATION.md`; `docs/architecture/{MCP_OPERATIONAL_FLOWS,MCP_UNIFIED_CONTEXT_FRAMEWORK,MCP_RUNTIME_ARCHITECTURE,MCP_PERSONA_DESIGN_GUIDE}.md`; `docs/specs/SPEC-003_mcp_creation_validation_profile_contracts.md`.

**Total:** 18 files edited by sed; 4 of those receive a follow-up
sub-path edit (`registry/`, `layers/`).

### 4. Historical docs cluster — preserved verbatim (G13)

The 11 docs files classified "historical" in the audit refresh are
copied byte-identical and **not** sed'd:

- `docs/CHANGELOG/CHANGELOG_v{1.11.0,1.16.0,2.0.0}.md` — version history.
- `docs/ROADMAP.md` — the `v1.22.0` retrospective block is history;
  no rewrite even though it mentions `ucx_flow_v3`.
- `docs/plans/PLAN-014_checklist.md`, `PLAN-014_3segment_element_id_migration.md`,
  `PLAN-016_checklist.md`, `PLAN-016_cross_section_validation.md`,
  `PLAN-018_yaml_parity_and_api_consistency.md`,
  `PLAN-021_sdd_reporting_naming_standard.md`,
  `PLAN-026_persona_management_tools.md` — completed migration plans;
  rewriting their `ucx_flow_v3` mentions would falsify history.

The verify gate (below) is calibrated to allow non-zero
`ucx_flow|UCX_FLOW` hits **only** in this 11-file whitelist.

### 5. VERSION files (formerly P2-T4)

Create two single-line plain-text files at `platforms/hermes/` top:

- `VERSION` → `0.1.0\n` (matches the initial platform tag `hermes/v0.1.0` per `docs/TAGGING.md`).
- `FRAMEWORK_SPEC_VERSION` → `0.1.0\n` (must match `framework/VERSION`).

Both bare SemVer, trailing newline, no `v` prefix — mirrors `framework/VERSION`'s convention (D-0006, D-0009).

### 6. `.mcp.json` repoint

Single edit: the `cwd` field. Old:

```
"cwd": "/opt/data/ucx_framework/legacy/ucx_hermes/src"
```

New:

```
"cwd": "/opt/data/ucx_framework/platforms/hermes/src"
```

The Python interpreter path (`/opt/data/ucx_framework/.venv/bin/python`)
is illustrative — left as-is per G13.

### 7. Audit refresh

After all edits land, update `plans/P2-AUDIT-hermes.md`:

- §3a heading: "Code-level (4 files, 6 lines — mandatory runtime rewire)"
  → "Code-level + tests (7 files, 19 lines — mandatory runtime rewire)";
  add the 3 test files to its table; add a Pass 5 retro note pointing
  here.
- §3b: leave structurally as-is; add a one-line footnote indicating that
  docs/ coupling was discovered separately and is documented in §3c.
- §3c (new): "Documentation cluster — historical vs current" — the
  classification table from this plan, the historical-keep whitelist,
  and the G13 rationale.

## Step sequence

1. **Pre-flight:** confirm `platforms/hermes/` exists (does — P2-T2 +
   P2-T7 contents present); confirm `legacy/ucx_hermes/` unchanged
   (`git status` clean for that path).
2. **Copy 7 source paths** per Approach §1, including the
   `docs/migration/` delete.
3. **Confirm file count:** `find platforms/hermes/{src,tests,docs,skills/hermes,skills/README.md,pyproject.toml} -type f | wc -l` == **200**; `find platforms/hermes/docs/migration -type f 2>/dev/null | wc -l` == **0**; `find platforms/hermes/templates -type f 2>/dev/null | wc -l` == **0**.
4. **`pyproject.toml` edits** (3 keys via Edit tool — Approach §2).
5. **Path-map sed** across the 18 edit-list files (Approach §3); apply
   the 4 follow-up sub-path edits.
6. **VERSION files** created (Approach §5).
7. **`.mcp.json`** edited (Approach §6).
8. **Audit refresh** applied to `plans/P2-AUDIT-hermes.md` (Approach §7).
9. **Verify** (see below).
10. **Land** — single commit
    `feat(hermes): port-with-repoint src/tests/docs/skills + pyproject + VERSION (P2-T3)`;
    update `plans/HANDOFF.md`; tick P2-T3 in `plans/MIGRATION_TODO.md`.
    Push to working branch. No `CHANGELOG.md` entry yet — Phase 2 closes
    at P2-T6.

## Verification

- **File count: 200 + 2** new files under the 7 in-scope target paths,
  plus `VERSION` and `FRAMEWORK_SPEC_VERSION` at top:
  `find platforms/hermes/{src,tests,docs,skills/README.md,skills/hermes,pyproject.toml,VERSION,FRAMEWORK_SPEC_VERSION} -type f | wc -l` = **202**.
- **Dropped paths absent:** `platforms/hermes/templates/` and
  `platforms/hermes/docs/migration/` do not exist.
- **`pyproject.toml`:**
  - `grep '^name = "hermes-server"' platforms/hermes/pyproject.toml` matches.
  - `grep '^version = "0.1.0"' platforms/hermes/pyproject.toml` matches.
  - `grep '^hermes-mcp =' platforms/hermes/pyproject.toml` matches.
  - `grep 'ucx-hermes-server\|mcp-ucx' platforms/hermes/pyproject.toml` returns zero.
- **Coupling — current-behavior content:**
  `grep -rE 'ucx_flow|UCX_FLOW' platforms/hermes/src platforms/hermes/tests platforms/hermes/skills platforms/hermes/pyproject.toml`
  returns **zero**.
- **Coupling — docs whitelist tolerance (G13):**
  - `grep -rE 'ucx_flow|UCX_FLOW' platforms/hermes/docs -l | sort` matches **exactly** the 11-file historical whitelist (Approach §4). No more, no fewer.
  - `grep -rE 'ucx_flow|UCX_FLOW' platforms/hermes/docs/HERMES_INTEGRATION.md platforms/hermes/docs/architecture platforms/hermes/docs/specs` returns zero.
- **Sub-path correctness:**
  - `grep -nE 'framework/LAYER_REGISTRY\.yaml' platforms/hermes/src platforms/hermes/tests` returns zero (must have been further-edited to `framework/registry/LAYER_REGISTRY.yaml`).
  - `grep -nE 'framework/registry/LAYER_REGISTRY\.yaml' platforms/hermes/src/mcp_server/creation/profile_contracts.py` matches.
  - `grep -nE 'framework/layers/01_BRD' platforms/hermes/src/mcp_server/utils/template_naming.py` matches.
- **VERSION files:**
  - `cat platforms/hermes/VERSION` prints `0.1.0`.
  - `diff platforms/hermes/FRAMEWORK_SPEC_VERSION framework/VERSION` prints nothing.
- **`.mcp.json`:**
  - `grep 'platforms/hermes/src' .mcp.json` matches.
  - `grep 'legacy/ucx_hermes' .mcp.json` returns zero.
- **Conformance suite:** all 25 tests still pass (`pytest tests/conformance/`).
  The suite scans only `framework/`, so it is a sanity check.
- **Hermes' own test suite:** `cd platforms/hermes && python -m pytest tests/` runs and passes (modulo any pre-existing flaky tests in legacy — record any deltas as a P2-T5 follow-up rather than fix here).
- **Audit refresh landed:** `grep -n '^### 3a' plans/P2-AUDIT-hermes.md` shows the renamed heading; `grep -n '^### 3c' plans/P2-AUDIT-hermes.md` shows the new section.
- **List-completeness (P2-T0 Pass 3 lesson):** the 7 source paths in
  Scope match audit §5's port-with-repoint rows 1:1; no port-with-repoint
  path missed; no port-verbatim or dropped path included.
- **Scope-completeness (P2-T0 Pass 4 / P2-T7 Pass 2 lesson):** after the
  port,
  `grep -rE 'ucx_flow|UCX_FLOW' legacy/ucx_hermes/ | cut -d: -f1 | sort -u`
  returns the same 29 files this plan accounts for (4 §3a code + 3 tests
  - 5 §3b skills + 6 §3c current-docs + 11 historical-docs whitelist +
  the `pyproject.toml` re-grep target). No new file appearing implies a
  scope leak; differing count blocks the commit.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Blind `sed -i` across all docs files corrupts historical content (the original concern that motivated G13). | Approach §3 limits sed to the 18-file edit-list **only**. The 11 historical-whitelist files are never sed'd. Verify gate checks the whitelist by exact set membership, not by hit count. |
| R2 | A file we tagged "historical" actually contains a current-behavior reference that should be rewritten. | The historical cluster is bounded: CHANGELOG files describe past versions by construction; PLAN-* checklists were closed completed plans. If implementation discovers a current-behavior ref in a historical file, stop the commit, reclassify, and rerun the verify gate. Do **not** silently rewrite. |
| R3 | The `sed` word-boundary regex misses an esoteric form (e.g. `ucx_flow_v3.LAYER_REGISTRY`, `UCX_FLOW_V3`). | Verify gate's coverage list is computed against the full pre-port grep, not against the edit-list — any escapee shows up as either a hit in a current-behavior file (fails verify) or as a new file in the post-port whitelist (fails set-membership check). |
| R4 | Hermes' own test suite has pre-existing failures unrelated to the port (e.g. requires `litellm` optional dep, hits a network during contract tests). | Verify clause allows recording deltas as a P2-T5 follow-up rather than blocking the commit. Document any failures in the commit message + HANDOFF; don't paper over. |
| R5 | `pyproject.toml` edit breaks `pip install -e .` because the package layout doesn't match the new distribution name. | `[tool.hatch.build.targets.wheel] packages = ["src/mcp_server"]` and the `mcp_server` import path are both untouched (Q1 design). A renamed *distribution* doesn't affect import discovery. Smoke-check by running `python -c "import mcp_server"` from inside `platforms/hermes/`. |
| R6 | The audit-refresh update to `plans/P2-AUDIT-hermes.md` ships partial / inconsistent (e.g. §3a updated but §3c forgotten). | Step 8 of the sequence is an explicit deliverable. Verify gate checks both headings exist. |
| R7 | `.mcp.json` repoint breaks an active dev session because `legacy/ucx_hermes/src` was being used as `cwd` in someone's running MCP server. | The current `.mcp.json` already points at legacy (committed before P2-T2); changing it now is the expected next step. The local Python interpreter path is preserved — no user-environment churn. Document the change in the commit message. |
| R8 | `pyproject.toml` `version = "0.1.0"` collides with the `framework/VERSION` of the same value (and with `hermes_agent_skills`'s prior version, if any). | The platform-tag namespace (`hermes/v0.1.0`) and the framework tag namespace (`framework/v0.1.0`) are explicitly disjoint per `docs/TAGGING.md`. SemVer reuse across namespaces is allowed and intentional. |
| R9 | Scope creep — pull in P2-T8 (skill's templates drop) "while we're here" because both touch `platforms/hermes/`. | Scope locked to the 7 source paths from audit §5's port-with-repoint set + the 2 VERSION files + `.mcp.json` + audit doc. P2-T8 touches `platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/templates/` — entirely outside this plan's edit set; trivial to keep separate. |

## Review log

> Per `CLAUDE.md` § Development workflow: at least two ISO-stamped passes
> before this plan may be presented or implemented.

### Pass 1 — 2026-05-20T11:35:00Z

- **G1. Audit gap — test files.** Recon found that
  `tests/unit/test_scaffold_init.py` (6 hits),
  `tests/unit/test_validation_runner.py` (2 hits), and
  `tests/integration/test_creation_profile_contracts_integration.py`
  (1 hit) all reference `ucx_flow_v3`. The audit's §3a enumerated only
  the production code paths. Folded these into Scope as
  "§3a-extension" and into the path-map; Step 7 lands the audit doc
  correction.
- **G2. Audit gap — docs cluster.** Recon also surfaced **17 docs/
  files** with `ucx_flow_v3` (~131 hits). §3b prose was limited to
  `skills/` + `templates/`. Applying P2-T7 G13: 11 are
  historical (PLAN-014, PLAN-016, PLAN-018, PLAN-021, PLAN-026
  completed plans + 3 CHANGELOG files + ROADMAP retrospective block)
  and **must not** be rewritten; 6 are current-behavior
  (`HERMES_INTEGRATION.md`, 4 architecture docs, SPEC-003) and **must**
  be rewritten. Verify gate calibrated against the historical whitelist
  by exact set membership, not count tolerance — catches both
  whitelist-bleed (a historical file got rewritten) and scope-leak
  (a new file appeared with hits).
- **G3. Word-boundary regex (P2-T7 G12).** Path-map uses
  `\bucx_flow_v3\b` over slash-prefix sed — catches bare-name forms
  (`"ucx_flow_v3"`, `$DIR/ucx_flow_v3`, `tmp_path / "ucx_flow_v3"`)
  that slash-prefix would miss. Specific case: every hit in
  `test_scaffold_init.py` is the bare-name form
  (`tmp_path / "ucx_flow_v3"`); slash-prefix sed would clear zero.
- **G4. Sub-path follow-up edits.** Naïve global sed would produce
  `framework/LAYER_REGISTRY.yaml` (broken — registry was sub-rooted in
  P1-T3) and `framework/01_BRD/` (broken — layers were sub-rooted in
  P1-T2). Approach §3 enumerates the 4 follow-up edits to land the
  correct sub-paths. Verify gate checks the post-edit values, not just
  zero `ucx_flow_v3` hits.
- **G5. pyproject.toml edit risk.** Listed `Edit` (not sed) for the 3
  pyproject keys — sed on TOML is brittle (quoting, table boundaries).
  Three scoped Edit calls keep the change auditable in the tool log.
- **G6. Scope discipline.** Listed the 9 things this plan does **not**
  touch (templates/ drop, migration/ drop, agent-skills already done,
  P2-T8, conformance extension, behavior changes). R9 makes "don't
  drag P2-T8 in" explicit because the two tasks both touch
  `platforms/hermes/` and are tempting to bundle.
- **G7. List-completeness.** Verification reuses the P2-T0 Pass 3
  pattern: scope matches audit §5's port-with-repoint rows 1:1, and
  scope-completeness recheck against the full pre-port grep catches
  any file the plan forgot to enumerate.
- **G8. The `\b` boundary in sed `-E`.** Confirmed `sed -E` honors
  `\b` on Linux (GNU sed). If portability becomes a concern (e.g. on
  macOS BSD sed), the implementation can switch to
  `[^[:alnum:]_]ucx_flow_v3[^[:alnum:]_]` — but this container ships
  GNU sed.
- **G9. The `.mcp.json` interpreter path.** Kept the
  `/opt/data/ucx_framework/.venv/bin/python` value — that's the
  user's local Python install path (G13 illustrative).
  Only `cwd` changes.
- **G10. Conformance suite expectation.** Reaffirmed against
  `tests/conformance/_spec.py` reading `framework/` only: this port
  cannot affect the suite. Sanity check is in the verify list for
  hygiene, not as a real gate.
- **G11. Version-bump rationale.** Pinned `version = "0.1.0"` (not
  `2.0.0` from legacy) — rationale documented inline in §2; lineage
  resets at the audit boundary because Hermes is shipping as a new
  platform under a new tag namespace.
- **G12. Hermes test suite as soft gate.** R4 makes pre-existing
  failures a P2-T5 follow-up rather than blocking the commit. Bias is
  toward shipping the port and surfacing legacy fragility separately,
  not toward fixing legacy bugs under cover of a port commit.

### Pass 2 — 2026-05-20T11:50:00Z

- **G13. Whitelist set-membership check stronger than a count.** Re-read
  Pass 1; the verify line that uses "exactly these 11 filenames" was
  worth double-checking. Confirmed it catches three failure modes a
  count-only check would miss: (a) a historical file silently rewritten
  (member missing → wrong list); (b) a scope-leak file gaining hits
  (extra member → wrong list); (c) a typo in the whitelist when the
  plan was authored (membership doesn't match expected). Kept.
- **G14. Pre-port grep reproducibility.** The scope-completeness check
  in verify compares against "the full pre-port grep". To make this
  reproducible, the implementation captures the grep output to
  `/tmp/p2t3-pregrep.txt` before any edits — folded the note into
  Step 1 of the sequence.
- **G15. Follow-up edits idempotency.** The 4 sub-path follow-up edits
  (e.g. `framework/LAYER_REGISTRY.yaml` → `framework/registry/...`)
  need to be order-stable: if the sed has already run, the follow-up
  edits must still match. Confirmed all four targets uniquely match
  the post-sed form, and none of them match a pre-sed substring that
  could fire twice (e.g. `framework/01_BRD/` doesn't pre-exist anywhere
  in the source — the docstring originally said `ucx_flow_v3/01_BRD/`).
  No idempotency issue.
- **G16. Risk R8 cross-check.** Re-read `docs/TAGGING.md` namespace
  rules in head. Framework tag `framework/v0.1.0` and platform tag
  `hermes/v0.1.0` are explicitly disjoint; same SemVer across
  namespaces is the documented norm, not a clash. R8 confirmed
  non-blocking.
- **G17. No new findings on Approach / Step sequence / Verification.**
  The plan is internally consistent and the verify gates are
  symmetric with the edit rules (no edit rule lacks a verify; no
  verify checks an output no edit rule produces). Ready to present
  on approval.

### Pass 3 — 2026-05-20T12:50:00Z (retrospective)

Recording one implementation-time plan contradiction and the user
decision that resolved it. Status: DONE.

- **G18. Plan contradiction: "no logic edits" vs P2-T1 Q3 downstream.**
  Implementation completed the port mechanics cleanly (all 13 V1-V13
  verify gates green; conformance 25/25). The optional V10 (Hermes' own
  test suite) surfaced 50 / 447 failures, **all** tracing to one root
  cause: `src/mcp_server/skills/scaffold.py:CANONICAL_SCAFFOLD_MAPPINGS`
  still references `platforms/hermes/templates/` for the
  scaffold-from-canonical operation, but D-0013 dropped that directory.
  This is precisely the P2-T1 Q3 downstream that the design doc flagged:

  > "the platform's template loader currently expects a flat `templates/`
  > directory; under Q3 it must read from per-layer dirs in
  > `framework/layers/`. The extension itself is **P2-T3 code work**,
  > not a P2-T1 design question — but flagged here so P2-T3 doesn't
  > treat it as a surprise."

  The P2-T3 plan above wrote "**Out:** Behavior changes: no logic edits,
  no refactors. Edits are limited to the path-map and the two pyproject
  keys." Those two statements directly contradicted each other. Pass 1
  / Pass 2 should have caught it (G11 lesson from P2-T7: "Don't write
  both [conflicting things] without reconciling them").

  Resolution: surfaced via `AskUserQuestion`; user chose **defer to a
  new P2-T9 task**. P2-T3 ships the port mechanics; P2-T9 will rewire
  the scaffold runtime to `framework/layers/<NN>_<X>/`. The 50 failing
  tests are documented as expected fallout of the D-0013 architectural
  gap, not regressions caused by the port itself.

- **Lesson for future port plans:** when a prior design doc enumerates
  downstream code work, the plan that consumes that design must either
  (a) include that work in scope, or (b) explicitly defer it to a named
  follow-up task with rationale. A blanket "no logic edits" out-scope
  clause is too coarse when the design has already flagged required
  logic edits — review passes need to cross-check `Out:` clauses
  against upstream design `Downstream implications:` sections.

## Implementation note (2026-05-20T12:50:00Z)

Executed. Port mechanics clean on the first pass:

- **Counts:** 200 ported + 2 VERSION files = 202; all 7 source paths
  copied; `templates/` and `docs/migration/` absent at target.
- **pyproject.toml:** 3 keys edited (`name`, `version`, script entry);
  zero legacy markers remain.
- **Coupling:** `grep -rE 'ucx_flow|UCX_FLOW'` on current-behavior
  content (`src/`, `tests/`, `skills/`, `pyproject.toml`) returns
  **zero**. Docs whitelist matches **exactly** the 11 expected
  historical files (set membership check passed).
- **Sub-paths:** `framework/registry/LAYER_REGISTRY.yaml` (×2),
  `framework/layers/01_BRD/` (×1) all correctly landed by the 3
  follow-up Edit calls (note: plan said "4 follow-up edits" — recon
  actually showed 3; the 4th was a planning-time miscount, not an
  edit gap).
- **VERSION files:** both `0.1.0`; `FRAMEWORK_SPEC_VERSION` diff'd
  identical to `framework/VERSION`.
- **`.mcp.json`:** `cwd` repointed to `platforms/hermes/src`; legacy
  refs zero. Python interpreter path kept (G13 illustrative).
- **Audit refresh:** §3a renamed to "Code-level + tests" with the 3
  test files appended; new §3c "Documentation cluster" added with the
  6-current / 11-historical classification.
- **Conformance suite:** 25/25 (all subtests pass; 0.46s).
- **Hermes' own suite (V10):** 397 / 447 pass. 50 failures — all
  D-0013 scaffold contract gap (G18 above). Deferred to P2-T9.
- **Scope-completeness recheck:** `legacy/ucx_hermes/` in-scope paths
  still have hits in exactly 29 files (matches pre-port snapshot at
  `/tmp/p2t3-pregrep.txt`) — no scope leak.
