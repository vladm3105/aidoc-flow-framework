# P2-T0 Plan — Phase 2 audit & task breakdown

| Field      | Value                                |
|------------|--------------------------------------|
| Task       | P2-T0                                |
| Depends on | Phase 1 complete (`v0.2.0`, `framework/v0.1.0`) |
| Status     | PLANNED — 2026-05-19T13:55:00Z       |
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

## Provisional task breakdown (replaced after audit)

These are candidate downstream tasks shown for shape only — they **will**
change after step 7 of the audit. Do not treat as committed.

- **P2-T1** — Resolve `ucx_hermes` ↔ `mcp_ucx` and define the final
  `platforms/hermes/` layout (one tree or two sub-packages?).
- **P2-T2** — Port-verbatim content: copy directories that don't reference
  the framework into their target paths.
- **P2-T3** — Port-with-repoint: copy directories that reference the
  framework, rewiring all coupling sites to `framework/`.
- **P2-T4** — Declare `framework_spec_version` in the platform manifest
  (mechanism per P2-T1 design).
- **P2-T5** — Make Hermes pass the conformance suite (`tests/conformance/`)
  — fix any platform-side gaps surfaced by the audit.
- **P2-T6** — Phase 2 close: changelog `[0.3.0]`, milestone tag `v0.3.0`,
  platform tag `hermes/v0.1.0`. Tag policy per `docs/TAGGING.md`.

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
