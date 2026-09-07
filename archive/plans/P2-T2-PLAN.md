# P2-T2 Plan — Hermes port-verbatim

| Field      | Value                                |
|------------|--------------------------------------|
| Task       | P2-T2                                |
| Depends on | P2-T0 audit, P2-T1 design (D-0013)   |
| Status     | DONE — 2026-05-20T09:10:00Z          |
| Feeds      | P2-T3 (port-with-repoint)            |

## Objective

Execute the **verbatim copy** of all no-coupling content from
`legacy/ucx_hermes/` into `platforms/hermes/`, per P2-T0 audit §5 and P2-T1
design Q5. Five source paths, **64 files total**, copied byte-identical to
their target paths. Verbatim means *byte-identical*: no edits, no
reformatting, no token rewrites. P2-T2 is straightforward unblocked work
and feeds P2-T3 (the port-with-repoint pass, where actual rewrites happen).

## Scope

**In** — the five paths classified `port-verbatim` by audit §5 (no
framework-coupling detected by initial grep + the §3b verify re-grep):

| Source (`legacy/ucx_hermes/`) | Target (`platforms/hermes/`) | Files |
|-------------------------------|-------------------------------|-------|
| `examples/` | `examples/` | 1 |
| `prompts/` (incl. `prompts/templates/`) | `prompts/` | 46 |
| `skills/layer_aliases/` | `skills/layer_aliases/` | 1 |
| `skills/personas/` | `skills/personas/` | 15 |
| `skills/persona_mappings.yaml` | `skills/persona_mappings.yaml` | 1 |
| **Total** | | **64** |

**Out:**

- **Content edits** — verbatim is byte-identical; any rewriting belongs in
  P2-T3 (port-with-repoint) or a follow-up that re-classifies the path.
- **Other paths** — `pyproject.toml`, `src/`, `tests/`, `docs/`,
  `skills/README.md`, `skills/hermes/` are all P2-T3 (port-with-repoint).
- **Dropped paths** — `templates/` (D-0013) and `docs/migration/` (audit
  §5) must remain absent from `platforms/hermes/`.
- **`platforms/hermes/README.md`** updates — left for P2-T5/T6.
- **`pyproject.toml`, VERSION, FRAMEWORK_SPEC_VERSION** — P2-T3 / P2-T4.

## Approach

For each source path:

1. Recursive copy (`cp -r`) preserving directory structure to the
   corresponding target under `platforms/hermes/`. No `cp -a`-style
   permission/timestamp preservation needed — git tracks content, not
   metadata.
2. After all copies, run a **fresh re-grep** for `ucx_flow|UCX_FLOW` on the
   copied targets. The audit's port-verbatim classification was based on an
   initial grep; the verify gate must independently confirm.
3. Run `diff -r <source> <target>` per path — proves byte-identical copy
   (stronger than a file-count check; would catch e.g. CRLF mangling).
4. Spot-check that the **dropped** paths are absent.
5. Confirm conformance suite still 25/25 — the suite scans only
   `framework/` (verified in P2-T0), so this is a sanity check, not a
   constraint.

## Step sequence

1. Confirm `platforms/hermes/` exists (it does — currently
   `README.md`-only).
2. Create `platforms/hermes/skills/` if not present.
3. Copy `examples/`, `prompts/`, `skills/layer_aliases/`,
   `skills/personas/`, `skills/persona_mappings.yaml` to their target paths
   (5 invocations, ordered for clarity).
4. Re-grep verify (step 2 in Approach).
5. `diff -r` verify per path (step 3 in Approach).
6. Conformance suite verify.
7. **Verify** (see Verification).
8. **Land** — single commit (one logical change: "feat(hermes): port
   verbatim content (P2-T2)"); update `plans/HANDOFF.md`; tick P2-T2 in
   `plans/MIGRATION_TODO.md`. No `CHANGELOG.md` entry yet — Hermes is
   incomplete until P2-T6 closes Phase 2.

## Verification

- **All five target paths exist** under `platforms/hermes/` at their
  expected locations.
- **Byte-identical:** `diff -r legacy/ucx_hermes/<p> platforms/hermes/<p>`
  prints nothing for each of the five paths.
- **File counts:** 64 files total under the copied paths
  (`find platforms/hermes/{examples,prompts,skills/layer_aliases,skills/personas} -type f | wc -l` = 63;
  plus `platforms/hermes/skills/persona_mappings.yaml` = 1).
- **No coupling slipped in:**
  `grep -rE 'ucx_flow|UCX_FLOW' platforms/hermes/examples platforms/hermes/prompts platforms/hermes/skills/layer_aliases platforms/hermes/skills/personas platforms/hermes/skills/persona_mappings.yaml`
  returns zero. (If non-zero, the path's verbatim classification is wrong —
  escalate, do **not** rewrite.)
- **Dropped paths absent:** `platforms/hermes/templates/` does **not**
  exist; `platforms/hermes/docs/migration/` does **not** exist (the
  latter is moot here — `docs/` is P2-T3 — but worth the check after
  P2-T3 runs).
- **Port-with-repoint paths absent (not yet copied):**
  `platforms/hermes/{src,tests,docs}/` do not exist;
  `platforms/hermes/skills/{README.md,hermes/}` do not exist;
  `platforms/hermes/pyproject.toml` does not exist.
- **Conformance suite:** 25/25 green. (Sanity check — should be unaffected
  since `_spec.py` scans only `framework/`.)
- **List-completeness (P2-T0 Pass 3 lesson):** the five copied paths match
  audit §5's port-verbatim rows 1:1 — no port-verbatim path missed; no
  port-with-repoint path included.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | A "port-verbatim" path contains framework coupling missed by P2-T0's grep | Fresh re-grep on each copied target (Approach §2); any hit escalates back to the audit — do **not** silently rewrite the content in P2-T2. |
| R2 | Hidden / dotfiles in the source paths missed by `cp -r` | Recon confirmed **no dotfiles** under the five paths. `diff -r` would catch any missed file regardless. |
| R3 | Copy method drifts content (e.g. line-ending conversion on a different OS, symlink dereferencing) | Use `cp -r` only; `diff -r` is the byte-identical gate. |
| R4 | Conformance suite breaks on new content under `platforms/hermes/` | The suite's `_spec.py` scans only `framework/` — confirmed in P2-T0 — but the suite is re-run as a sanity check (verify step). |
| R5 | An overzealous P2-T2 also touches port-with-repoint paths "while we're here" | Scope locked to the five paths; verify clause explicitly checks that `src/`, `tests/`, `docs/`, `skills/README.md`, `skills/hermes/`, `pyproject.toml` are **absent** at end of P2-T2. |
| R6 | The commit accidentally pulls in unrelated working-tree changes | `git status` review before commit; stage only the new `platforms/hermes/**` paths + the two tracker file edits. |

## Review log

### Pass 1 — 2026-05-20T09:00:00Z

- **G1.** P2-T0 Pass 3 retro lesson — explicit list-completeness in verify.
  Applied: the verify clause checks both the *expected-present* paths
  (5 copied targets) and the *expected-absent* paths (dropped + not-yet-
  copied), 1:1 against audit §5.
- **G2.** Hidden / dotfiles: recon already confirmed none in the source
  paths — risk R2 reduced from "blocker" to "double-check". `diff -r`
  catches it anyway.
- **G3.** The "verbatim" claim depends on the audit's grep. Reused the
  fresh-grep verify gate that caught prose coupling in P2-T0 implementation
  — same discipline.
- **G4.** README.md and pyproject.toml are explicitly out — keeps P2-T2
  focused. Phase-2-close work belongs to P2-T6.

### Pass 2 — 2026-05-20T09:02:00Z

- **G5.** List-completeness re-confirmed: the five paths match audit §5's
  port-verbatim rows exactly (`examples/`, `prompts/`,
  `skills/layer_aliases/`, `skills/personas/`, `skills/persona_mappings.yaml`).
  No port-verbatim path missing; no port-with-repoint path accidentally
  pulled in.
- **G6.** Risk R4 re-checked: `tests/conformance/_spec.py` defines
  `FRAMEWORK = REPO_ROOT / "framework"`. The suite never reaches into
  `platforms/`. Adding content there cannot regress the suite. Sanity
  check is still warranted.
- **G7.** Byte-identical: file-count was a weak proxy in the first draft;
  upgraded the verify to `diff -r` per path. Catches CRLF mangling,
  permission drift on copy, accidental edits, anything. Stronger gate.
- **G8.** R5 (scope creep into rewrite) is real — easy to "fix" a stray
  `ucx_hermes` mention while copying. The verify clause makes the rewrite
  paths explicitly off-limits.
- **G9.** No new blockers. Ready to implement on approval.

## Implementation note (2026-05-20T09:10:00Z)

Executed. All five paths copied (64 files) and all seven verify gates
green on the first pass: `diff -r` byte-identical on every path; fresh
grep for `ucx_flow|UCX_FLOW` on the copied targets returns zero; file
counts 64/64; all seven expected-absent paths (`templates/`, `src/`,
`tests/`, `docs/`, `skills/hermes/`, `skills/README.md`, `pyproject.toml`)
remain absent; conformance suite 25/25; list-completeness 1:1 with audit
§5. No content was rewritten in P2-T2 — scope held.
