# P5-T2 Plan — Remove `legacy/`

| Field      | Value                                |
|------------|--------------------------------------|
| Task       | P5-T2                                |
| Depends on | P5-T0 audit, P5-T1 design, D-0014; archive branch `legacy-ucx-v3.2-read-only` (protected) |
| Status     | DONE — 2026-05-21T07:20:00Z          |
| Feeds      | P5-T4 (docs), P5-T5 (verify), P5-T6 (cutover) |

## Objective

Remove the in-tree `legacy/` directory (~2276 files, 28M) from the
working branch. This is the archive-then-clean cleanup of D-0014:
the pristine pre-migration project is already preserved in the
protected `legacy-ucx-v3.2-read-only` branch, so the working-branch
copy is redundant and is removed to produce a clean shipped project.

**Destructive.** Gated on: (a) the archive branch existing +
protected (precondition — met); (b) no surviving-tree **runtime**
dependency on `legacy/` (pre-flight check); (c) **explicit user
confirmation** before the `git rm` runs.

## Scope

**In:**
- `git rm -r legacy/` on the working branch — removes the entire
  `legacy/` tree.
- Verify the removal: `legacy/` absent; conformance 31/31; Hermes
  suite unaffected; no dangling **runtime** reference; archive
  branch still holds the content.

**Out:**
- Root `.claude/` removal — that's P5-T3 (separate, sequenced late).
- Any rewrite of plan docs that cite `legacy/<path>` — those become
  pointers-to-history (content in the archive branch); acceptable
  per P5-T1 Q5. Not edited here.
- `main` operations — P5-T6.
- Doc finalization (README/REPO_STRUCTURE legacy references) — P5-T4.

## Approach

### 1. Pre-flight (read-only, before the destructive step)

- **Archive precondition:** confirm `origin/legacy-ucx-v3.2-read-only`
  exists and contains the legacy trees + the pre-migration root
  (re-confirm; already verified at D-0014 restore).
- **Runtime-dependency sweep:** confirm nothing in the surviving
  tree reads `legacy/` at runtime. Distinguish:
  - **Runtime** references (code/config that resolves a `legacy/`
    path) — must be **zero**. (P5-T0 §1: framework/ + tests/ +
    .mcp.json clean.)
  - **Documentary** references (CHANGELOGs, plan prose, the known
    plugin stale-refs) — allowed; become pointers-to-history.
- **Working-tree cleanliness:** `git status` clean except expected.

### 2. The removal

```sh
git rm -r legacy/
```

Single scoped command. Removes only `legacy/`.

### 3. Post-removal verify (see Verification)

## Step sequence

1. **Pre-flight checks** (Approach §1) — read-only.
2. **⛔ CONFIRMATION GATE** — present the pre-flight results +
   the exact `git rm` command; **do not proceed without explicit
   user go-ahead.**
3. **`git rm -r legacy/`**.
4. **Verify** (below).
5. **Land** — single commit
   `chore: remove in-tree legacy/ (archived as legacy-ucx-v3.2-read-only) (P5-T2)`;
   update `plans/HANDOFF.md`; tick P5-T2 in `plans/MIGRATION_TODO.md`.
   Push.

## Verification

- **V1. `legacy/` gone:** `test ! -d legacy && echo ok`; `git ls-files
  legacy/ | wc -l` == 0.
- **V2. Conformance suite:** `python3 -m unittest discover -s
  tests/conformance` → 31 passed (legacy removal cannot affect it —
  scans `framework/` only — but run as sanity).
- **V3. Hermes suite unaffected:** re-run if venv available
  (`447 passed` expected); else assert by reasoning (Hermes
  references `framework/` + `tmp_path`, never `legacy/` — verified
  P2-T9). Record which.
- **V4. No dangling runtime reference:** re-grep the surviving tree
  for `legacy/` — remaining hits are documentary only (CHANGELOGs,
  plan prose, plugin stale-refs); zero runtime/config hits.
- **V5. Archive intact:** `git ls-remote origin
  legacy-ucx-v3.2-read-only` returns the protected branch; its
  content unchanged (the removal is only on the working branch).
- **V6. Scope discipline:** `git status` / `git diff --cached
  --stat` shows **only** `legacy/` deletions (~2276 files) — no
  other path touched.
- **V7. Plugin smoke unaffected:** manifest valid; plugin skill
  count unchanged (142).

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | A surviving-tree file resolves a `legacy/` path at runtime; removal breaks it. | Pre-flight runtime-dependency sweep (Approach §1); P5-T0 §1 already found framework/ + tests/ + .mcp.json clean. Any runtime hit halts the removal. |
| R2 | The archive branch is incomplete → content actually lost. | Pre-flight re-confirms the archive holds all 7 legacy trees + the pre-migration root (verified at D-0014 restore: 2732 files, superset). The removal touches only the working branch; the protected archive is untouched. Plus git history retains the working-branch `legacy/`. |
| R3 | Plan docs citing `legacy/<path>` dangle after removal. | Expected + accepted (P5-T1 Q5): they're historical provenance; content is one `git checkout legacy-ucx-v3.2-read-only` away. Not edited in P5-T2. |
| R4 | `git rm -r legacy/` accidentally catches more than `legacy/`. | The path arg is exactly `legacy/`. V6 confirms only `legacy/` deletions in the staged diff before commit. |
| R5 | The conformance suite or a platform test imports from `legacy/`. | conformance `_spec.py` roots at `framework/`; Hermes tests use `framework/` + `tmp_path`; plugin is declarative. None reference `legacy/`. V2/V3 confirm post-removal. |
| R6 | Large deletion commit is hard to review. | It's a single mechanical `git rm -r legacy/`; the diff is all deletions under one path. V6's stat confirms the scope. |
| R7 | Removal runs without explicit confirmation. | Step 2 is a hard CONFIRMATION GATE; P5-T2 does not `git rm` until the user says go. |

## Review log

### Pass 1 — 2026-05-21T06:55:00Z

- **G1. Destructive — explicit confirmation gate (Step 2).** The
  removal does not run on plan approval alone; the user must
  confirm after seeing the pre-flight results. Honors the
  commitment made when Phase 5 was scoped.
- **G2. Archive precondition is the safety net.** The pristine
  pre-migration project is in the protected `legacy-ucx-v3.2-read-only`
  branch (D-0014, verified). Removal is lossless — the working-branch
  `legacy/` is a redundant copy.
- **G3. Runtime vs documentary references (V4).** The sweep
  distinguishes them: runtime hits must be zero (would break);
  documentary hits (CHANGELOGs, plan prose, plugin stale-refs) are
  allowed and become pointers-to-history. P5-T0 §1 already
  established framework/ + tests/ + .mcp.json are clean.
- **G4. Scope discipline (V6).** `git rm -r legacy/` is path-scoped;
  the staged-diff stat confirms only `legacy/` before commit. Guards
  against an over-broad removal.
- **G5. Conformance/Hermes unaffected (V2/V3).** The suites root at
  `framework/` / `tmp_path`, never `legacy/`. Run as sanity; record
  Hermes-suite result or the reasoning if the venv is gone.
- **G6. plans/ docs not edited (R3).** Per P5-T1 Q5, the historical
  plan docs that cite `legacy/` stay as-is (provenance); the content
  is recoverable from the archive branch.

### Pass 2 — 2026-05-21T07:05:00Z

- **G7. `.mcp.json` re-check.** P5-T0 confirmed `.mcp.json` cwd is
  `platforms/hermes/src` (no `legacy/`). The pre-flight re-greps it
  to be certain before removal.
- **G8. The 1 documentary `legacy/` hit in plugin skills**
  (`doc-brd-autopilot/SKILL.md`, found at P5-T0) — it's part of the
  known ~150 stale-refs set (PARITY.md), not a runtime path. After
  removal it dangles slightly more; already slated for post-v1.0
  content cleanup. Not a blocker.
- **G9. Hermes CHANGELOG mentions `legacy/ucx_hermes`** — that's
  migration history in `platforms/hermes/CHANGELOG.md` (P4-T4);
  stays accurate as history. Documentary, allowed.
- **G10. Re-confirm archive immutability at execution.** V5 checks
  the archive branch still resolves on the remote post-removal
  (the removal is working-branch-only; the protected archive can't
  be affected, but verify).
- **G11. No new findings.** Plan is internally consistent; the
  confirmation gate is explicit. Ready to run the pre-flight, then
  request go-ahead.

## Implementation note (2026-05-21T07:20:00Z)

Executed after explicit user confirmation. `git rm -r legacy/`
removed **2276 tracked files** (645,145 line-deletions). All verify
gates green:

- **V1.** `git ls-files legacy/` == 0 (git-clean removal). The
  `legacy/` directory **lingers on disk** only because of **11
  git-ignored `legacy/tmp/` scratch files** (format-review reports +
  update scripts the pre-migration project never tracked). These are
  gitignored → not in the repo, not in history, not in the archive
  branch → **won't propagate to the new `main`** (a fresh clone has
  no `legacy/`). Left in place on disk (container-local cruft;
  harmless; not unilaterally `rm -rf`'d given the user's
  preserve-legacy caution — though they exist nowhere in git).
- **V2.** Conformance suite 31/31.
- **V3.** Hermes suite **447/447** (venv was available).
- **V4.** Zero `legacy/` references in the surviving runtime tree
  (`framework/`, `tests/`, `platforms/*/src`+manifest, `.mcp.json`).
- **V5.** Archive branch `legacy-ucx-v3.2-read-only` intact on the
  remote at `491e8db` (the removal was working-branch-only).
- **V6.** Scope clean — the staged diff is **only** `legacy/`
  deletions (2276 files); no other path touched.
- **V7.** Plugin smoke unaffected (142 skill dirs; manifest valid).

The legacy content remains fully recoverable from the protected
`legacy-ucx-v3.2-read-only` branch + git history. Documentary
`legacy/` references in `README.md`, `docs/REPO_STRUCTURE.md`,
`CLAUDE.md` are reconciled in P5-T4; those in CHANGELOGs / ROADMAP /
STARTUP_HANDOFF / the plugin stale-ref stay as historical prose.
