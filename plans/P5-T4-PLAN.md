# P5-T4 Plan — Finalize project docs

| Field      | Value                                |
|------------|--------------------------------------|
| Task       | P5-T4                                |
| Depends on | P5-T1 design (Q5, Q6), P5-T2 (legacy/ removed), D-0014 |
| Status     | DONE — 2026-05-21T08:05:00Z          |
| Feeds      | P5-T3 (remove root .claude/), P5-T5 (verify), P5-T6 (close) |

## Objective

Finalize the four project front-matter / memory docs from
migration-in-progress to as-built post-migration state:
`README.md`, `docs/REPO_STRUCTURE.md`, `docs/PROJECT.md`, and a
rewrite of `CLAUDE.md` (P5-T1 Q6). Reconcile every "legacy
removed/archived at cutover" reference to name the protected
`legacy-ucx-v3.2-read-only` archive branch (D-0014). `ROADMAP.md`
Phase-5-complete status marking is deferred to **P5-T6** (the close)
to avoid double-handling.

## Scope

**In:**
1. **`README.md`** — drop the "Phase 0 / planning" status + the
   "Migration in progress" section; drop `legacy/` from the
   architecture diagram (removed in P5-T2); update the platform
   matrix to released/available; refresh the Documentation list
   (drop `legacy/README.md`; add `docs/PARITY.md`, `docs/TAGGING.md`);
   add a "Pre-migration history" pointer to the archive branch.
2. **`docs/REPO_STRUCTURE.md`** — flip the status banner from
   "PLANNED target" to "as-built (post-migration)"; reconcile the
   legacy footer (legacy/ removed from the tree + archived as the
   branch; `.claude/` ported to the plugin). Keep the Legacy →
   Target mapping table as the historical record of where content
   went.
3. **`docs/PROJECT.md`** — reconcile the migration-era branching
   note (§3) + the §4 cutover milestone wording ("legacy archived")
   to name the archive branch; light touch elsewhere (versioning /
   conformance / CHG sections stay accurate).
4. **`CLAUDE.md`** — rewrite from migration-in-progress to slim
   post-migration project memory (P5-T1 Q6).

**Out:**
- `ROADMAP.md` Phase-5 status marking + the `[1.0.0]` changelog —
  **P5-T6** (close).
- Root `.claude/` removal — **P5-T3** (next; this task does not
  remove it). P5-T4 docs avoid depending on root `.claude/` existing
  but do not assert it's already gone.
- Plan docs that cite `legacy/<path>` — historical provenance, left
  as-is (P5-T1 Q5).
- Any code change.

## Approach

### 1. README.md

Rewrite as the project's permanent front page (no migration framing):
- **Status line** → drop "early restructure (Phase 0 — planning)";
  replace with a one-line "delivered" framing (multi-platform
  framework; cutover at `v1.0.0`).
- **Architecture diagram** → remove the `legacy/` line; show
  `framework/` + `platforms/{hermes,claude-code-plugin}/` +
  `tests/conformance/`.
- **Platforms matrix** → status column: Hermes "MCP server —
  `hermes/v0.1.0`"; plugin "Native Claude Code — `claude-code-plugin/v0.1.0`".
- **Documentation list** → drop `legacy/README.md`; add
  `docs/PARITY.md` (platform comparison) + `docs/TAGGING.md`.
- **Replace "Migration in progress"** with **"Pre-migration history"**:
  the original `ucx_framework` (v0.20.4) is preserved on the
  protected `legacy-ucx-v3.2-read-only` branch; the migration record
  lives in `plans/`.

### 2. docs/REPO_STRUCTURE.md

- **Status banner** → "Status: as-built (post-migration). The
  repository converged to this layout at the Phase 5 cutover."
- **Footer reconciliation** → replace the "Content is copied out of
  `legacy/` … `legacy/` is removed at/after the Phase 5 cutover.
  `.claude/` stays at repo root …" paragraph with: legacy content
  was extracted in Phases 1–3; the `legacy/` tree was **removed**
  at cutover (P5-T2) and the pristine pre-migration project is
  preserved on the protected `legacy-ucx-v3.2-read-only` branch; the
  root `.claude/` skill set was ported into the plugin (Phase 3) and
  the root loader is removed at cutover.
- **Mapping table** → keep as the historical "where content went"
  record (it documents the migration; still accurate).

### 3. docs/PROJECT.md

- **§3** → the "`main` is protected for the duration of the
  migration … until the Phase 5 cutover" note: keep as the
  migration-era policy but add that at cutover the new project
  replaces `main` and the pre-migration `main` is preserved as the
  `legacy-ucx-v3.2-read-only` branch.
- **§4 milestone table** → "Cutover | 5 | `v1.0.0` | New project
  replaces `main`; legacy archived" → "… legacy archived as the
  `legacy-ucx-v3.2-read-only` branch."
- Leave §2 (versioning), §5 (conformance), §6 (CHG) as-is — accurate.

### 4. CLAUDE.md rewrite (P5-T1 Q6)

New slim post-migration project memory. **Keep:**
- What the project is (one engine-agnostic `framework/` spec + two
  independent platforms).
- Where things are (framework, platforms, tests/conformance, docs,
  plans).
- Durable conventions: the framework spec is the contract; both
  platforms declare `FRAMEWORK_SPEC_VERSION`; the conformance suite
  must stay green; tagging policy (`docs/TAGGING.md`); the
  plan→review→implement→verify→land workflow as **guidance**.
- Pointer to `legacy-ucx-v3.2-read-only` for pre-migration history.

**Drop:** migration-phase tracking ("Phase 1 — Framework Spec
Extraction"), "mid-restructure", "Legacy is frozen / copy-don't-move"
(legacy is gone from the tree), working-branch rule, "`main` is
locked" (cutover supersedes it), legacy-CI note.

`CLAUDE.md` is a **root file** (not under `.claude/`) → survives the
P5-T3 `.claude/` removal.

## Step sequence

1. **README.md** edits (§1).
2. **docs/REPO_STRUCTURE.md** edits (§2).
3. **docs/PROJECT.md** edits (§3).
4. **CLAUDE.md** rewrite (§4).
5. **Verify** (below).
6. **Land** — single commit
   `docs: P5-T4 finalize project docs — as-built + legacy→archive-branch reconciliation`;
   update `plans/HANDOFF.md`; tick P5-T4 in `plans/MIGRATION_TODO.md`.
   Push.

## Verification

- **V1. README** — no "Phase 0" / "planning" / "Migration in
  progress" stale strings; no `legacy/` in the architecture diagram;
  contains a `legacy-ucx-v3.2-read-only` pointer.
- **V2. REPO_STRUCTURE** — status banner says "as-built"; footer
  names the archive branch; no "legacy/ is removed at/after the
  cutover" future-tense language.
- **V3. PROJECT** — §4 cutover row names the archive branch.
- **V4. CLAUDE.md** — no "Phase 1 — Framework Spec Extraction" /
  "mid-restructure" / "Legacy is frozen" / "main is locked" strings;
  contains the durable-conventions content + the archive-branch
  pointer.
- **V5. Conformance suite** — 31/31 (docs don't affect it; sanity).
- **V6. No runtime `legacy/` reference reintroduced** — the four
  edited docs may *mention* `legacy-ucx-v3.2-read-only` (the branch)
  but introduce no `legacy/` *path* runtime dependency.
- **V7. Scope** — `git diff --stat` shows only the 4 docs + the 2
  trackers; no code, no other files.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | P5-T4 docs assert root `.claude/` is already removed, but P5-T3 (its removal) runs next. | Docs avoid present-tense "root .claude/ has been removed"; phrase the loader as "ported into the plugin; removed at cutover" (the cutover completes across P5-T3+T6). P5-T5 verifies final alignment. |
| R2 | README/PROJECT version claims go stale (e.g. claiming v1.0.0 before P5-T6 ships it). | Avoid hard "v1.0.0 released" claims; describe the delivered structure + platform versions (`hermes/v0.1.0`, `claude-code-plugin/v0.1.0`) which are real now. P5-T6 handles the v1.0.0 milestone. |
| R3 | Over-aggressive CLAUDE.md rewrite drops a still-relevant rule (e.g. the conformance-green gate). | The rewrite explicitly keeps the durable conventions list; only migration-era rules are dropped. Pass-2 cross-checks the kept set. |
| R4 | The Legacy→Target mapping table reads as still-active. | Reframe its intro as a historical record ("where the pre-migration content went"); the table content is accurate provenance. |
| R5 | A doc edit breaks an internal markdown link. | Edits don't move files; relative links (`docs/`, `framework/`, `plans/`) stay valid. `legacy/README.md` link in README is removed (the file is gone). |

## Review log

### Pass 1 — 2026-05-21T07:45:00Z

- **G1. Scope = the 4 front-matter docs.** ROADMAP Phase-5 marking
  is P5-T6 (the close), not P5-T4 — avoids two tasks both editing
  ROADMAP's Phase 5 row. P5-T4 reconciles the *wording* of legacy
  removal in README/REPO_STRUCTURE/PROJECT/CLAUDE.md.
- **G2. Sequencing vs P5-T3 (R1).** P5-T4 runs before the root
  `.claude/` removal. Docs describe the loader as "ported to the
  plugin; removed at cutover" (true across P5-T3+T6) rather than
  asserting present-tense removal. Keeps docs accurate at commit
  time and after P5-T3.
- **G3. No premature v1.0.0 claims (R2).** Describe what's real now
  (the delivered structure + the platform `v0.1.0` releases). The
  `v1.0.0` milestone is P5-T6.
- **G4. CLAUDE.md keep/drop list explicit (R3).** Keep durable
  conventions (contract, conformance-green, tagging, workflow-as-
  guidance, handoff); drop migration-era rules (phases, legacy-
  frozen, working-branch, main-lock).
- **G5. Legacy→Target table kept as history (R4).** It's the
  provenance record of where pre-migration content landed —
  valuable, accurate, reframed as historical.
- **G6. Archive-branch pointer in all four docs.** README,
  REPO_STRUCTURE, PROJECT, CLAUDE.md each point at
  `legacy-ucx-v3.2-read-only` for pre-migration history — consistent
  cross-referencing.

### Pass 2 — 2026-05-21T07:55:00Z

- **G7. `docs/PROJECT.md` §1 "ucx_hermes" parenthetical.** Minor —
  "(ucx_hermes)" as Hermes' engine label is a legacy name. Leave it
  (it's accurate as the platform's origin/import path) or soften;
  not worth a risky edit. Decided: leave (out of scope creep).
- **G8. README "Platforms" status wording.** Use the platform tag
  names (`hermes/v0.1.0`, `claude-code-plugin/v0.1.0`) which are
  published + accurate, rather than phase references ("re-homed in
  Phase 2"). Forward-looking and stable.
- **G9. CLAUDE.md workflow guidance — hook is gone after P5-T3.**
  The `plan-review-gate.sh` hook is removed with `.claude/` in
  P5-T3, so the two-pass review can't be *hook-enforced* post-
  cutover. The rewritten CLAUDE.md presents it as a **convention/
  guidance**, not a hook-enforced gate. Consistent with P5-T1 G11.
- **G10. V6 guards against reintroducing a `legacy/` path dep.**
  The docs reference the *branch* `legacy-ucx-v3.2-read-only` (fine)
  but must not reintroduce a `legacy/`-*path* runtime reference. V6
  checks.
- **G11. No new findings.** Plan internally consistent; doc-only,
  no destructive ops. Ready to execute.

## Implementation note (2026-05-21T08:05:00Z)

Executed. Four docs finalized; all 7 verify gates green.

- **README.md** — dropped the "Phase 0 / planning" status + the
  "Migration in progress" section; removed `legacy/` from the
  architecture diagram; platform matrix → `hermes/v0.1.0` /
  `claude-code-plugin/v0.1.0`; Documentation list refreshed (added
  PARITY + TAGGING; dropped `legacy/README.md`); new "Pre-migration
  history" section points at `legacy-ucx-v3.2-read-only`. (V1's one
  "Phase 0" hit is the benign ROADMAP-description line, not stale
  framing.)
- **docs/REPO_STRUCTURE.md** — status banner → "as-built
  (post-migration)"; Legacy→Target mapping reframed as a historical
  record; footer reconciled (legacy/ removed at P5-T2 + archived;
  root `.claude/` ported to the plugin + removed at cutover).
- **docs/PROJECT.md** — §3 reconciled (pre-migration `main`
  preserved as the archive branch; `main` force-updated at cutover);
  §4 cutover milestone now names the archive branch.
- **CLAUDE.md** — rewritten to slim post-migration project memory:
  dropped migration-phase tracking / "Legacy is frozen" /
  working-branch / "main is locked" / legacy-CI; kept the durable
  conventions (framework-is-the-contract, conformance-green,
  D-0013, tagging, versioning streams), the workflow as **guidance**,
  session-handoff, where-things-are; added the archive-branch
  pointer. It's a root file → survives the P5-T3 `.claude/` removal.
- Conformance 31/31; scope = the 4 docs + trackers only.

The remaining `legacy/` path mentions are confined to
REPO_STRUCTURE's historical mapping table ("was under `legacy/`") —
intentional provenance, not runtime references.
