# P2-T0 Plan — Phase 2 audit & task breakdown

| Field      | Value                                |
|------------|--------------------------------------|
| Task       | P2-T0                                |
| Depends on | Phase 1 complete (`v0.2.0`, `framework/v0.1.0`) |
| Status     | DONE — 2026-05-19T14:15:00Z          |
| Feeds      | P2-T1 … P2-Tn (Hermes re-homing tasks defined here) |

## Objective

Map Phase 2 on paper before any code moves. The legacy Hermes platform lives
in **two** trees — `legacy/ucx_hermes/` (280 files) and `legacy/mcp_ucx/`
(255 files) — each with its own `pyproject.toml`, `src/`, `skills/`,
`templates/`, and `tests/`. Their relationship is unaudited, and many files
reference paths (`ucx_flow`, `framework/`) that mean different things in the
new layout. The target `platforms/hermes/` is empty except for its
`README.md`.

P2-T0 produces:

1. **`plans/P2-AUDIT-hermes.md`** — an audit doc inventorying both trees,
   resolving their relationship, mapping framework coupling, and classifying
   every top-level path as port-verbatim / port-with-repoint / drop / defer.
2. **A concrete P2-T1…P2-Tn task breakdown** appended to this plan, with
   inputs and outputs for each task.
3. **A conformance-gap statement** — exactly what Hermes must declare and
   change to satisfy the 25-test conformance suite at `tests/conformance/`.

P2-T0 is **paper only**; no code or files move.

## Scope

**In:**
- Inventory both legacy trees by directory and file type.
- Resolve the `ucx_hermes` ↔ `mcp_ucx` relationship (separate roles? library +
  server? overlap?). This is the highest-risk unknown.
- Identify framework-coupling sites (references to old paths, legacy registry,
  legacy layer locations) that need repointing post-copy.
- Determine the conformance gap: enumerate what assertions the conformance
  suite makes about platforms, and what Hermes must add to declare
  `framework_spec_version` (D-0009) and pass.
- Classify every top-level dir under both trees:
  `port-verbatim` | `port-with-repoint` | `drop` | `defer`.
- Output: `plans/P2-AUDIT-hermes.md` + P2-Tx breakdown.

**Out:**
- Any actual copy, move, or code change (later P2-T*).
- Conformance suite extension or new tests (Phase 4).
- Platform B (Claude Code plugin) — Phase 3.

## Approach

1. **Inventory.** File counts by type and key directories for both trees; read
   each `pyproject.toml` and any top-level README to capture stated role.
2. **Relationship.** Sample-read each tree's `src/` to confirm role; check
   import boundaries (does `ucx_hermes` import `mcp_ucx`?). Document one of:
   *separate roles* / *library + server* / *renamed duplicate* / *overlap*.
3. **Framework coupling.** Grep both trees for `ucx_flow`, legacy registry
   paths, hard-coded `legacy/` references, layer locations; list every
   coupling site with its file path.
4. **Conformance gap.** Read each `tests/conformance/*` module to enumerate
   exactly what the suite asserts about a platform (entry points, manifest
   files, declared `framework_spec_version`, etc.). State the gap.
5. **Classification.** Walk each top-level dir of both trees; tag each as
   `port-verbatim` / `port-with-repoint` / `drop` / `defer`. Justify each tag
   in one line.
6. **Write `plans/P2-AUDIT-hermes.md`** with sections: Inventory · Relationship
   · Framework coupling · Conformance gap · Classification matrix · Open
   questions.
7. **Draft P2-T1…P2-Tn** in this plan's "Provisional task breakdown" section
   (replace the provisional list with the audit-confirmed one).

## Step sequence

1. Inventory `legacy/ucx_hermes/` and `legacy/mcp_ucx/`.
2. Resolve the two-package relationship.
3. Build the framework-coupling map.
4. Enumerate conformance assertions about platforms; derive the gap.
5. Classify every top-level dir.
6. Write `plans/P2-AUDIT-hermes.md`.
7. Replace the provisional task breakdown with the audit-confirmed one.
8. **Verify** (see below).
9. **Land** — commit the audit + plan update; update `HANDOFF.md`,
   `MIGRATION_TODO.md` (add the P2-Tx items), `ROADMAP.md` if scope clarifies.

## Verification

- `plans/P2-AUDIT-hermes.md` exists and covers **all 535 files** — every
  top-level directory of each tree appears in the classification matrix.
- The two-package relationship is named (one of the four options above).
- The framework-coupling list is complete (a fresh grep against the same
  patterns returns nothing not already in the list).
- The conformance-gap section names every assertion the existing suite makes
  about a platform and what Hermes lacks for each.
- This plan's "Task breakdown" lists P2-T1…P2-Tn, each with a one-line scope
  and explicit input (legacy paths) → output (`platforms/hermes/<path>`).
- **No code or files moved** in P2-T0 — the diff is paper only.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | `ucx_hermes` and `mcp_ucx` overlap / one absorbs the other → bad target layout | Audit resolves the relationship as step 2, before any classification. |
| R2 | Framework-coupling site missed → Hermes won't pass conformance after copy | Explicit grep + classification matrix; fresh grep at verify step must return only listed sites. |
| R3 | Audit grows into doing the actual port → scope creep | Plan is paper-only; verify clause forbids file moves; "every change reviewed in two passes" gate also catches drift. |
| R4 | `framework_spec_version` declaration mechanism not yet defined in the registry | The conformance suite enforces it (D-0009, P1-T6); if the *mechanism* is undefined, surface as an open question in the audit and resolve in P2-T1 design, not in P2-T0. |
| R5 | Provisional P2-Tx list locks in shape that the audit then contradicts | The list is labelled *provisional* and explicitly replaced after step 5; the audit, not this plan, is the source of truth. |

## Task breakdown (audit-confirmed)

Replaces the provisional list. Source of truth is `plans/P2-AUDIT-hermes.md`;
the `ucx_hermes` ↔ `mcp_ucx` question is resolved (predecessor/successor;
`mcp_ucx` out of scope, see audit §2). Phase 2 input is the 280 files of
`legacy/ucx_hermes/`.

- **P2-T1 — Design.** Resolve the five open questions in audit §6:
  Python module name (avoid `mcp_server` collision); `framework_spec_version`
  declaration mechanism (recommendation: `platforms/hermes/VERSION` +
  `platforms/hermes/FRAMEWORK_SPEC_VERSION`); `templates/` overlap with
  `framework/layers/*-TEMPLATE.md`; distribution script entry name; document
  the target `platforms/hermes/` layout. Output: a short design doc
  (`plans/P2-T1-DESIGN.md`) plus updated D-0013 if any choice is non-obvious.
- **P2-T2 — Port-verbatim.** Copy the no-coupling content into
  `platforms/hermes/` as-is: `examples/`, `prompts/`, `skills/layer_aliases/`,
  `skills/personas/`, and `skills/persona_mappings.yaml`. No content edits.
- **P2-T3 — Port-with-repoint (now incorporates P2-T4 spec-version declaration).**
  Copy `pyproject.toml`, `src/`, `tests/`, and `docs/` (excluding
  `docs/migration/`, dropped) into `platforms/hermes/`. Copy
  `skills/README.md` and `skills/hermes/` into `platforms/hermes/skills/`.
  The three legacy-root-level files from §5b are **ported via P2-T7** (the
  `hermes_agent_skills` package on main carries byte-identical copies);
  P2-T3 does **not** double-port them. **Do not copy `templates/`** —
  dropped per D-0013. Apply the design from P2-T1 (Q1 `hermes-server`
  distribution + keep `mcp_server` import; Q4 `hermes-mcp` script entry)
  in the `pyproject.toml` edit. Rewire **both** classes of framework
  coupling from audit §3: the 4 code-level files (§3a) with targeted edits
  **and** the prose-level set (§3b: 5 `skills/` markdown files; the
  `templates/` rows of §3b are moot post-D-0013) via word-boundary regex
  sed (G12 lesson). **Also add `platforms/hermes/VERSION` (`0.1.0`) and
  `platforms/hermes/FRAMEWORK_SPEC_VERSION` (matching `framework/VERSION` =
  `0.1.0`)** — formerly P2-T4, folded in here. Update `.mcp.json` to point
  at the new Hermes path. Verify gate (G13 lesson): a fresh
  `grep -rE 'ucx_flow|UCX_FLOW' platforms/hermes/` returns zero;
  `/opt/data` illustration paths in tutorials remain.
- ~~**P2-T4** — folded into P2-T3 (2026-05-20T10:45:00Z).~~
- **P2-T5 — Verify.** Run `tests/conformance/` — all 25 tests still green
  (no `framework/` change). Run Hermes' own test suite
  (`platforms/hermes/tests/`) against the repointed paths.
  Cross-platform sweep: `grep -rE 'ucx_flow|UCX_FLOW' platforms/hermes/`
  returns zero; `VERSION` and `FRAMEWORK_SPEC_VERSION` files exist and
  match `framework/VERSION`.
- **P2-T6 — Phase 2 close.** Cut `CHANGELOG.md [0.3.0]`; mark Phase 2
  complete in `ROADMAP.md`; create milestone tag `v0.3.0` and platform tag
  `hermes/v0.1.0` (annotated, per `docs/TAGGING.md`). Tag publication
  expected to need the same local-clone workaround as P1-T8 (in-container
  git proxy still 403s on `refs/tags/*`).
- **P2-T8 — Drop skill's template duplication (D-0013 conformance).**
  Remove the 8 layer YAMLs at
  `platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/templates/0N_TYPE-TEMPLATE.yaml`
  and rewire the skill's runtime / documentation references to read from
  `framework/layers/<NN>_<X>/<X>-TEMPLATE.yaml` per D-0013. Verify gate:
  `find platforms/hermes/agent-skills/.../sdd-orchestrator/templates/`
  returns nothing (or directory is gone); a sample skill invocation
  (manual or test) resolves a template from `framework/layers/`.
  Added 2026-05-20T10:45:00Z (follow-up flag from P2-T7).

## Implementation note (2026-05-19T14:15:00Z)

Executed. Recon found `mcp_ucx` and `ucx_hermes` are not siblings but
predecessor/successor (confirmed by the in-tree migration doc), which
collapsed the highest-risk unknown R1 and shrank Phase 2 input from 535 to
280 files. The user directive "use ucx_hermes" aligned with that finding.
The audit (`plans/P2-AUDIT-hermes.md`) classifies every top-level path,
identifies four framework-coupling sites for rewiring (`src/mcp_server/`
under `skills/`, `validation/`, `utils/`, `creation/`), and pins the
conformance gap honestly: the current 25-test suite asserts only on
`framework/`, so Phase 2's suite gate is "don't break it"; platform-level
tests are a Phase 4 concern. No code or files were moved by P2-T0.

## Review log

### Pass 1 — 2026-05-19T13:58:00Z

- **G1.** The `ucx_hermes` / `mcp_ucx` relationship is the highest-risk
  unknown. Plan must resolve it *before* any classification, since a wrong
  guess corrupts the target layout. → Step 2 explicitly resolves it; R1.
- **G2.** Conformance-gap can't be guessed from `framework_spec_version`
  alone; the suite at `tests/conformance/` makes its own assertions about
  platforms. Plan must read those tests, not infer. → Approach step 4 says
  exactly that; verify clause requires enumerating every assertion.
- **G3.** Both the audit doc *and* the P2-Tx breakdown must come out of
  P2-T0; leaving the breakdown for a later task would re-do the work. →
  Both are in scope; verify clause requires both.
- **G4.** The provisional task list risks becoming load-bearing. → Labelled
  provisional and explicitly replaced after step 5; R5.

### Pass 2 — 2026-05-19T14:00:00Z

- **G5.** Verify clause counts 535 files — confirmed against recon
  (280 + 255). Every top-level dir must appear in the matrix; that's the
  honest completeness check.
- **G6.** Audit doc filename `plans/P2-AUDIT-hermes.md` mirrors
  `plans/P1-AUDIT-ucx_flow_v3.md` — consistent.
- **G7.** R4 framework-spec-version mechanism — re-checked: P1-T6 / D-0009
  introduced the convention but the *platform-side declaration mechanism*
  (manifest file? key in `pyproject.toml`? a dedicated `VERSION` file?)
  isn't fixed. Correctly deferred to P2-T1 design, with the audit surfacing
  it as an open question.
- **G8.** "Paper only" gate is explicit in scope, verify, and R3 — three
  layers of guard. Sufficient.
- No new blockers. Ready to implement on approval.

### Pass 3 — 2026-05-19T14:30:00Z (retrospective)

Added after implementation, to record what the verify step caught that the
pre-implementation reviews didn't. Status stays DONE.

- **G9.** Pass 2 cleared the plan without explicitly auditing the
  framework-coupling list for *completeness*. The initial draft of audit
  §3 enumerated 4 code-level sites; the verify-time fresh `grep` found
  prose-level sites in `skills/hermes/*` and `templates/*` that the draft
  had missed. The audit was corrected (§3a code-level / §3b prose-level
  split) and P2-T3's description updated accordingly. The gap existed
  because the reviews asked "is the plan well-structured?" but not "is the
  *content list* it produces likely to be exhaustive?" Future audit-style
  plans (e.g. P3-T0 if Phase 3 needs one): include an explicit
  list-completeness pass — "for every enumeration the plan claims to
  produce, what classes of items might the first draft omit?" — alongside
  the structural review.

### Pass 4 — 2026-05-20T09:25:00Z (retrospective)

Added after P2-T2 verbatim copy and a user-flagged review of legacy
root-level coverage. Status stays DONE on P2-T0 itself; the audit gains
§5b, and P2-T3's scope extends accordingly.

- **G10.** A *second* audit gap surfaced — this time at the **scope**
  level, not the enumeration-within-scope level (G9). The plan scoped the
  audit to the two named subdirectories (`legacy/ucx_hermes/`,
  `legacy/mcp_ucx/`) and never asked whether `legacy/` root files might be
  Hermes-relevant. Three were
  (`HERMES_UCX_RUNTIME_ENVIRONMENT.md`,
  `MULTI_PROJECT_QUICK_REFERENCE.md`,
  `MULTI_PROJECT_SETUP_GUIDE.md`); the user surfaced the first by name,
  and a directory listing surfaced the other two. Four root-level files
  classified `drop`/`out of scope`. The audit was corrected with §5b.
- **Lesson for future audit-style plans:** the review must also ask **"is
  the *scope* of the audit complete?"** — not only "is the enumeration
  within scope likely exhaustive?" (G9). Concretely, for any migration
  audit: enumerate every file at the root of the source tree
  (`find <source> -maxdepth 1 -type f`) and classify each, even when the
  scope is described in terms of named subdirectories. The scope question
  is upstream of the enumeration question; G9 catches the latter, G10
  catches the former.
