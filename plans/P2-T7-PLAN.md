# P2-T7 Plan — Port `hermes_agent_skills/` (sdd-orchestrator + sdd-review-personas)

| Field      | Value                                |
|------------|--------------------------------------|
| Task       | P2-T7                                |
| Depends on | P2-T0 audit (§5b correction), P2-T1 design (D-0013) |
| Status     | PLANNED — 2026-05-20T09:50:00Z       |
| Feeds      | P2-T4 (declaration), P2-T5 (verify), P2-T6 (close) |

## Objective

Port the **187 files** of `hermes_agent_skills/spec-driven-development/`
from `origin/main` into **`platforms/hermes/agent-skills/spec-driven-development/`**
on the working branch, with framework-path coupling rewired to point at
`framework/`. This is a port-with-repoint task (analogous to P2-T3 but for
the user-added skill package on main rather than for `legacy/ucx_hermes/`).

These are the user's **canonical Hermes agent skills designed to consume the
aidoc-flow framework** — not legacy material. The repoint isn't legacy
salvage; it's correcting source-path references so the skills target the
framework at its new, canonical location (`framework/` in this repo)
instead of the legacy `ucx_flow_v3/` paths they were authored against.

The package contains two skills:
- `sdd-orchestrator/` (186 files) — SDD v3.2 orchestration engine with
  `governance/`, `references/`, `root-docs/`, `scripts/`.
- `sdd-review-personas/` (1 file, `SKILL.md`) — 15-persona review panel.

Source-side coupling: **185 `ucx_flow|UCX_FLOW` hits** across the tree,
plus `/opt/data/ucx_framework/...` absolute paths in `governance/` and
`references/`, and prose describing the legacy template-sync procedure
that D-0013 made obsolete.

## Scope

**In:**
- Port all 187 files from `origin/main:hermes_agent_skills/spec-driven-development/`
  to `platforms/hermes/agent-skills/spec-driven-development/`.
- Rewire all `ucx_flow_v3` references to the equivalent paths under
  `framework/`. Path-map rules in **Approach**.
- Rewrite the `/opt/data/ucx_framework/ucx_flow_v3` absolute-path mention
  in `sdd-orchestrator/SKILL.md` to a repo-relative `framework/` reference.
- Resolve duplication with audit §5b: the three `root-docs/*` files
  (`HERMES_UCX_RUNTIME_ENVIRONMENT.md`, `MULTI_PROJECT_QUICK_REFERENCE.md`,
  `MULTI_PROJECT_SETUP_GUIDE.md`) are byte-identical to the legacy-root
  copies and arrive in this port. **Update §5b** to mark those three as
  "ported via P2-T7" — they do **not** also need porting via P2-T3.
- Preserve file permissions on executable scripts (mode 100755 in main).
- Scope-completeness check (P2-T0 Pass 4 lesson): re-verify that no
  *other* Hermes-relevant content on `origin/main` is missed by this
  port. Specifically: `git diff --name-only --diff-filter=A HEAD origin/main`
  yields no Hermes-relevant paths outside `hermes_agent_skills/`.

**Out:**
- Behavior re-architecture of the template-sync workflow (D-0013
  obsoletes it). The skill's prose describing that workflow is updated to
  reflect D-0013, but no new behavior is implemented here — that's a
  follow-up if/when needed.
- Cherry-picking the commits — surgical `git checkout` from `origin/main`
  is preferred to avoid pulling unrelated files (tmp/, ucx_flow_v3/ at
  root, etc. — confirmed not Hermes-relevant).
- Conformance suite extension (Phase 4).

## Approach

1. **Bring files across** via:
   ```
   git checkout origin/main -- hermes_agent_skills/spec-driven-development/
   mkdir -p platforms/hermes/agent-skills/
   git mv hermes_agent_skills/spec-driven-development \
          platforms/hermes/agent-skills/spec-driven-development
   rmdir hermes_agent_skills  # source root was empty after the move
   ```
   `git mv` preserves the rename in history so reviewers can see the
   one-step relocation.

2. **Path repoint** — apply the following mapping (manual edit, not blind
   sed; many references are in prose where a global substitution could
   corrupt meaning):

   | Legacy path | New path |
   |-------------|----------|
   | `ucx_flow_v3/` | `framework/` |
   | `ucx_flow_v3/LAYER_REGISTRY.yaml` | `framework/registry/LAYER_REGISTRY.yaml` |
   | `ucx_flow_v3/DOC_GOVERNANCE_CORE.md` | `framework/governance/DOC_GOVERNANCE_CORE.md` |
   | `ucx_flow_v3/CHG/` | `framework/governance/chg/` |
   | `ucx_flow_v3/0N_TYPE/TYPE-TEMPLATE.yaml` | `framework/layers/0N_<X>/<X>-TEMPLATE.yaml` |
   | `/opt/data/ucx_framework/ucx_flow_v3/` | `framework/` (repo-relative) |
   | `/opt/data/ucx_framework/ucx_hermes/` | `platforms/hermes/` (repo-relative) |

3. **D-0013 reconciliation** — the orchestrator's `SKILL.md` describes a
   legacy template-sync procedure (`ucx_flow_v3/0N_TYPE/TYPE-TEMPLATE.yaml
   → templates/0N_TYPE-TEMPLATE.yaml`) plus references to a sync
   procedure doc and a sync script. D-0013 made this workflow obsolete —
   the platform now reads templates directly from `framework/layers/`.
   Action: replace the affected paragraphs in `SKILL.md` and
   `references/ucx-sdd-bridge/template-sync-procedure.md` with notes that
   the sync workflow is deprecated (D-0013); the script
   `scripts/ucx-sdd-bridge/sync-ucx-templates.sh` is also marked obsolete
   in its first comment line. Files are kept in place for now (history /
   future reference) but marked. **No behavioral changes.**

4. **§5b correction (audit update)** — mark the three `root-docs/*` files
   as "ported via P2-T7" in `plans/P2-AUDIT-hermes.md`. P2-T3's scope
   shrinks correspondingly (loses those three files from its
   port-with-repoint set).

## Step sequence

1. Verify source content unchanged (`git ls-tree -r origin/main -- 'hermes_agent_skills/**' | wc -l` == 187).
2. `git checkout` + `git mv` to bring files into target path.
3. Confirm file count at target: `find platforms/hermes/agent-skills/spec-driven-development -type f | wc -l` == 187.
4. Apply path-repoint rules (§Approach.2) across all files.
5. Apply D-0013 reconciliation (§Approach.3).
6. Update `plans/P2-AUDIT-hermes.md` §5b (§Approach.4); update P2-T3
   scope in `MIGRATION_TODO.md` and `P2-T0-PLAN.md` accordingly.
7. **Verify** (see below).
8. **Land** — single commit `feat(hermes): port agent-skills sdd-orchestrator + sdd-review-personas (P2-T7)`;
   update `plans/HANDOFF.md`; tick P2-T7 in `MIGRATION_TODO.md`.

## Verification

- **File count:** `find platforms/hermes/agent-skills/spec-driven-development -type f | wc -l` == **187**.
- **Coupling absent:** `grep -rE 'ucx_flow|UCX_FLOW' platforms/hermes/agent-skills/`
  returns **zero** (down from 185 hits at source).
- **Absolute paths absent:** `grep -rE '/opt/data/ucx_framework' platforms/hermes/agent-skills/`
  returns zero.
- **Executable bits preserved:** `find platforms/hermes/agent-skills -type f -perm -u+x | wc -l`
  matches the source count of `100755` files from `git ls-tree -r origin/main`.
- **§5b updated:** the three `root-docs/*` files marked "ported via P2-T7"
  in `plans/P2-AUDIT-hermes.md`; P2-T3 scope updated to drop them.
- **D-0013 reconciliation applied:** the obsolete template-sync paragraphs
  in `SKILL.md`, `references/ucx-sdd-bridge/template-sync-procedure.md`,
  and the sync script's header now carry a deprecation note pointing at
  D-0013.
- **Scope completeness (P2-T0 Pass 4 lesson):** rerun
  `git diff --name-only --diff-filter=A HEAD origin/main` after the port;
  the remaining entries are confirmed non-Hermes (tmp/, root-level
  ucx_flow_v3/ which is the un-isolated original now in legacy/, etc.).
- **List completeness (P2-T0 Pass 3 lesson):** both skills present —
  `platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/`
  and `.../sdd-review-personas/`. Top-level subdir count under
  `sdd-orchestrator/` matches the source (governance, references,
  root-docs, scripts).
- **Conformance suite:** 25/25 (sanity; `_spec.py` scans only `framework/`,
  so the suite is unaffected — but run anyway).

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Blind global sed over 185 hits corrupts prose (e.g. `ucx_flow_v3` appears in code-block paths that *describe* the legacy and shouldn't be rewritten) | Use targeted edits per the path-map rules; never `sed -i` across all files. Spot-check each file class (SKILL.md, governance/, references/). |
| R2 | D-0013 reconciliation expands into rewriting behavior, not just deprecation notes | Plan explicitly limits §Approach.3 to *prose marking* — no script rewrites. Behavioral changes belong to a follow-up task if/when needed. |
| R3 | Cherry-pick from main pulls extra files (commits touch unrelated paths) | Avoid cherry-pick; use `git checkout origin/main -- <path>` to pull only the named subtree. Verify with `git status` before commit. |
| R4 | Executable bits lost in the port (`cp` / `git checkout` may not preserve mode) | Verify with `find ... -perm -u+x` post-port; restore with `chmod +x` per the source `100755` list if any are lost. |
| R5 | Another Hermes-relevant content blob exists on main that I haven't surfaced | Step 1 of Verification: re-run the `git diff --diff-filter=A` scope-completeness check after the port. |
| R6 | The §5b correction is forgotten and the three `root-docs/*` files end up double-ported (in P2-T3 and in P2-T7) | §5b update is a verification line, not an afterthought. P2-T3's plan (when written) will inherit the corrected scope. |
| R7 | `git mv` of `hermes_agent_skills/spec-driven-development/` leaves the empty parent `hermes_agent_skills/` directory tracked | After `git mv`, `rmdir hermes_agent_skills` (or `git rm` if tracked). Verify `ls -la` shows no leftover. |

## Review log

### Pass 1 — 2026-05-20T09:52:00Z

- **G1.** P2-T0 Pass 3 lesson (list-completeness): verify clause checks
  *both* skills present with their expected subdir structure. Applied.
- **G2.** P2-T0 Pass 4 lesson (scope-completeness): verify clause re-runs
  the `git diff --diff-filter=A HEAD origin/main` check post-port, to
  confirm no other Hermes-relevant content on main is missed. Applied.
- **G3.** The 185 hits include code-block paths that *describe legacy
  behavior* and should not be silently rewritten. R1 mitigates with a
  no-blind-sed rule.
- **G4.** D-0013 ripple — the skill carries prose for a workflow D-0013
  made obsolete. Plan limits Approach.3 to deprecation notes, not
  behavior rewrites. R2.
- **G5.** §5b update is a real artifact of this task, not a comment in
  passing. Step 6 of the sequence makes it an explicit deliverable; R6
  guards it.

### Pass 2 — 2026-05-20T09:54:00Z

- **G6.** List-completeness re-confirmed: the 187 files map to the two
  skills 186 + 1; no skill missed; no path outside `hermes_agent_skills/`
  pulled in.
- **G7.** Scope-completeness re-confirmed: the only other paths newly on
  main are `tmp/` (review reports — not Hermes-related) and `ucx_flow_v3/`
  at root (the un-isolated original, already in `legacy/ucx_flow_v3/`
  on this branch). Captured in Out-of-scope.
- **G8.** R7 — git mv leaves an empty parent dir. Caught and handled
  with `rmdir`/`git rm`.
- **G9.** Executable bits — recon found mode-100755 files (e.g.
  `apply_doc_path_aliases.py`, `setup-iam-oidc.sh`, etc.). Verify step
  preserves them; R4 guards.
- **G10.** No new blockers. Ready to implement on approval.
