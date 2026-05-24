# P2-T8 Plan — Drop skill's templates duplication; rewire to `framework/layers/`

| Field      | Value                                |
|------------|--------------------------------------|
| Task       | P2-T8                                |
| Depends on | D-0013, P2-T7 (skill ported), P2-T3 (Hermes runtime ported) |
| Status     | DONE — 2026-05-20T13:55:00Z          |
| Feeds      | P2-T5 (verify), P2-T6 (close)        |

## Objective

Delete the 8 layer-template YAMLs at
`platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/templates/`
— they duplicate (with drifted engine hardcodes) the authoritative
`framework/layers/<NN>_<X>/<X>-TEMPLATE.yaml` set. Rewire the **25 prose
references** in the skill (17 in `SKILL.md`, 8 in
`references/sdd-workflow-quickstart.md`) to point at the framework paths
instead. After this task, the skill carries no template duplication and
its documentation directs readers at the single source of truth, fully
closing D-0013 for the agent-skills package.

## Audit — current state (planning recon)

**Files to delete (8 YAMLs in `sdd-orchestrator/templates/`):**

| Skill path | Framework counterpart | Drift |
|------------|----------------------|------:|
| `01_BRD-TEMPLATE.yaml` (975 lines) | `framework/layers/01_BRD/BRD-TEMPLATE.yaml` (975 lines) | engine hardcodes (`server: ucx_hermes`, `tool: sdd_validate`, `SDD v3` label) |
| `02_PRD-TEMPLATE.yaml` (604 lines) | `framework/layers/02_PRD/PRD-TEMPLATE.yaml` (603 lines) | same |
| `03_EARS-TEMPLATE.yaml` (373 lines) | `framework/layers/03_EARS/EARS-TEMPLATE.yaml` (373 lines) | same |
| `04_BDD-TEMPLATE.yaml` (366 lines) | `framework/layers/04_BDD/BDD-TEMPLATE.yaml` (364 lines) | same |
| `05_ADR-TEMPLATE.yaml` (446 lines) | `framework/layers/05_ADR/ADR-TEMPLATE.yaml` (444 lines) | same |
| `06_SPEC-TEMPLATE.yaml` (189 lines) | `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml` (188 lines) | same |
| `07_TDD-TEMPLATE.yaml` (266 lines) | `framework/layers/07_TDD/TDD-TEMPLATE.yaml` (265 lines) | same |
| `08_IPLAN-TEMPLATE.yaml` (164 lines) | `framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml` (163 lines) | engine hardcode + vendor-named agents (`[Claude \| Gemini \| Codex \| etc.]`) |

The drift is the platform/engine specificity that D-0013 explicitly excluded
from documents ("the framework being engine-agnostic means platform-specific
content shouldn't be in the template at all — it's a runtime concern"). Framework versions are the engine-agnostic single source of truth.

**Reference inventory (25 lines, 2 files):**

`SKILL.md` (17 lines):

- Lines 683–690: 8-item bulleted list of `templates/0N_TYPE-TEMPLATE.yaml`.
- Line 692: `skill_view(name='sdd-orchestrator', file_path='templates/NN_TYPE-TEMPLATE.yaml')` API-call example — needs both the path **and** the loading mechanism rewritten (`skill_view` only sees files inside the skill; framework files are outside).
- Lines 696–703: 8-row table with `templates/0N_TYPE-TEMPLATE.yaml` paths.

`references/sdd-workflow-quickstart.md` (8 lines):

- Lines 13–20: 8-row table with `templates/0N_TYPE-TEMPLATE.yaml` paths.

**Out of P2-T8 scope (related but disjoint):**

- `sdd-orchestrator/governance/templates/` — different directory, not a
  layer-template duplication; holds pre-commit configs and QA bridge docs
  (some already reference `framework/layers/`). Untouched.
- `SKILL.md` line 153 (`governance/templates/PROJECT_KICKOFF_PLAN-TEMPLATE.md`)
  — `governance/templates/`, untouched.
- `SKILL.md` line 1132 — already carries the D-0013 deprecation note. No edit.
- `SKILL.md` lines 195–197 — describes legacy vs framework template
  locations as a comparison; the framework line (196) is already correct,
  the project/MCP lines (195/197) are illustrative-historical (G13).
  Leave verbatim.
- `references/ucx-readme.md` line 126 — `│ └── templates/` is a tree-
  diagram of the *legacy ucx_hermes/* layout (historical illustration);
  not a current reference. Leave verbatim.
- P2-T9 (MCP scaffold runtime rewire to `framework/layers/`) — strictly
  the MCP server code path; no overlap with this skill-package work.

## Scope

**In:**

- Delete 8 YAMLs at `platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/templates/0N_TYPE-TEMPLATE.yaml`.
- Delete the now-empty `templates/` directory (the dir itself, not just its contents).
- Rewire **17 lines in `SKILL.md`** and **8 lines in `sdd-workflow-quickstart.md`** from skill-relative `templates/0N_TYPE-TEMPLATE.yaml` to framework-relative `framework/layers/0N_TYPE/TYPE-TEMPLATE.yaml`.
- Update `SKILL.md:692`'s `skill_view`-based loading example to a direct-read instruction (the file is no longer inside the skill, so `skill_view` doesn't apply).
- Confirm via diff-check that framework counterparts contain all
  engine-agnostic content from the skill copies (no substantive content
  is lost by the deletion). Drift items (`server: ucx_hermes`, etc.)
  are **intentionally** discarded per D-0013.

**Out:**

- Any change to `sdd-orchestrator/governance/templates/` (different
  artifact set, not subject to D-0013).
- Any change to `SKILL.md` lines 153, 195–197, 1132 (already correct
  or historical illustration).
- Any change to `references/ucx-readme.md` (legacy tree-diagram).
- P2-T9 (MCP scaffold runtime) — separate task, disjoint file set.
- New behavior / new content. Deletes + path renames only.

## Approach

### 1. Delete-by-`git rm`

```
git rm platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/templates/0{1..8}_*-TEMPLATE.yaml
```

Then verify the directory is empty and remove it:

```
rmdir platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/templates
```

`git rm` (over plain `rm`) keeps the deletion intent visible in the
commit. Bash brace expansion `0{1..8}_*` matches the 8 files exactly
(verified during recon: `ls templates/` shows nothing else).

### 2. Path-rewrite rule

Both reference files use the same skill-relative pattern. The rule:

| Pattern in skill | New pattern |
|---|---|
| `templates/01_BRD-TEMPLATE.yaml` | `framework/layers/01_BRD/BRD-TEMPLATE.yaml` |
| `templates/02_PRD-TEMPLATE.yaml` | `framework/layers/02_PRD/PRD-TEMPLATE.yaml` |
| `templates/03_EARS-TEMPLATE.yaml` | `framework/layers/03_EARS/EARS-TEMPLATE.yaml` |
| `templates/04_BDD-TEMPLATE.yaml` | `framework/layers/04_BDD/BDD-TEMPLATE.yaml` |
| `templates/05_ADR-TEMPLATE.yaml` | `framework/layers/05_ADR/ADR-TEMPLATE.yaml` |
| `templates/06_SPEC-TEMPLATE.yaml` | `framework/layers/06_SPEC/SPEC-TEMPLATE.yaml` |
| `templates/07_TDD-TEMPLATE.yaml` | `framework/layers/07_TDD/TDD-TEMPLATE.yaml` |
| `templates/08_IPLAN-TEMPLATE.yaml` | `framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml` |

The structural change is two-fold:

1. **Path prefix:** `templates/` → `framework/layers/0N_TYPE/`.
2. **Basename:** `0N_TYPE-TEMPLATE.yaml` → `TYPE-TEMPLATE.yaml` (drop
   the `0N_` prefix — the framework's per-layer-dir layout makes the
   number redundant in the filename).

Apply via 8 sed expressions (one per layer) rather than a single regex:

```
sed -i -E \
  -e 's|templates/01_BRD-TEMPLATE\.yaml|framework/layers/01_BRD/BRD-TEMPLATE.yaml|g' \
  -e 's|templates/02_PRD-TEMPLATE\.yaml|framework/layers/02_PRD/PRD-TEMPLATE.yaml|g' \
  -e 's|templates/03_EARS-TEMPLATE\.yaml|framework/layers/03_EARS/EARS-TEMPLATE.yaml|g' \
  -e 's|templates/04_BDD-TEMPLATE\.yaml|framework/layers/04_BDD/BDD-TEMPLATE.yaml|g' \
  -e 's|templates/05_ADR-TEMPLATE\.yaml|framework/layers/05_ADR/ADR-TEMPLATE.yaml|g' \
  -e 's|templates/06_SPEC-TEMPLATE\.yaml|framework/layers/06_SPEC/SPEC-TEMPLATE.yaml|g' \
  -e 's|templates/07_TDD-TEMPLATE\.yaml|framework/layers/07_TDD/TDD-TEMPLATE.yaml|g' \
  -e 's|templates/08_IPLAN-TEMPLATE\.yaml|framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml|g' \
  platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/SKILL.md \
  platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/references/sdd-workflow-quickstart.md
```

Word-boundary regex isn't needed here — the full skill-relative path is
specific enough to never collide. Pipe (`|`) is the sed delimiter
(slashes in paths). Eight pinned expressions over one regex avoids the
G-3 trap (a generic `\bNN_TYPE\b` pattern would have to know NN-TYPE
pairings — easier to enumerate).

The `templates/NN_TYPE-TEMPLATE.yaml` placeholder on `SKILL.md:692` is
**not** in the 8-pattern set (it's a meta-placeholder, not a real
filename). Handle as a separate scoped Edit (see §3).

### 3. `SKILL.md:692` — loading-mechanism rewrite

Current:

```
Load the appropriate template with `skill_view(name='sdd-orchestrator', file_path='templates/NN_TYPE-TEMPLATE.yaml')` before beginning creation or review.
```

New (preferred):

```
Load the appropriate template from `framework/layers/<NN>_<TYPE>/<TYPE>-TEMPLATE.yaml` in the repository (e.g. `framework/layers/01_BRD/BRD-TEMPLATE.yaml`). Use the standard file-read mechanism — `skill_view` does **not** apply since templates live outside the skill (D-0013).
```

Single targeted Edit, not sed — the rewrite is structural, not a
substring swap.

### 4. Content-equivalence check (no substantive content lost)

Before deleting any file, confirm that the framework counterpart
contains all engine-agnostic semantic content from the skill copy.
For each of the 8 pairs:

```
diff <(grep -v -E 'server:|tool: sdd_validate|ucx_hermes|SDD v3' <skill-file>) \
     <(grep -v -E 'server:|tool: sdd_validate|ucx_hermes|SDD v3' <fwk-file>) \
  | head -20
```

This isn't a byte-equivalence proof — small phrasing differences are
expected (the framework templates are post-extraction edits). The check
is a **judgment-supporting diff**: any large delta (>50 lines, or new
semantic blocks) flags a content-loss risk that warrants a manual
review of the framework template before delete. Recon already inspected
the 01_BRD / 02_PRD / 08_IPLAN diffs and confirmed the deltas are all
engine-hardcode-removal + minor phrasing.

If the check flags substantive content in a skill template that the
framework counterpart lacks: stop, capture the delta, decide whether to
**(a)** port the missing content into the framework template (P1-T2
correction) before deleting, or **(b)** classify the missing content as
intentionally engine-specific and dropped per D-0013. Do not silently
delete content that turns out to be unique.

## Step sequence

1. **Pre-flight:** capture pre-delete grep snapshot for verify.

   ```
   grep -rnE 'templates/0[1-8]_(BRD|PRD|EARS|BDD|ADR|SPEC|TDD|IPLAN)-TEMPLATE\.yaml|templates/NN_TYPE-TEMPLATE\.yaml' \
     platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/ \
     > /tmp/p2t8-pregrep.txt
   wc -l /tmp/p2t8-pregrep.txt  # expect 26 (25 references + 1 placeholder)
   ```

2. **Content-equivalence check** (Approach §4) for all 8 pairs. Halt on
   any substantive delta; otherwise proceed.
3. **Delete** the 8 YAMLs via `git rm`; `rmdir` the empty parent.
4. **Path-rewrite** sed (Approach §2) across the 2 reference files.
5. **Loading-mechanism rewrite** (Approach §3) — single Edit on
   `SKILL.md:692`.
6. **Verify** (see below).
7. **Land** — single commit
   `refactor(hermes-skill): drop layer template duplication; rewire to framework/layers/ (P2-T8)`;
   update `plans/HANDOFF.md`; tick P2-T8 in `plans/MIGRATION_TODO.md`.
   Push to working branch. No `CHANGELOG.md` entry yet — Phase 2
   closes at P2-T6.

## Verification

- **Templates dir gone:**
  `test ! -d platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/templates && echo "ok"`
  prints `ok`.
- **Files gone:** `git ls-files platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/templates/` returns empty.
- **No remaining skill-relative template references:**
  `grep -rnE 'templates/0[1-8]_(BRD|PRD|EARS|BDD|ADR|SPEC|TDD|IPLAN)-TEMPLATE\.yaml|templates/NN_TYPE-TEMPLATE\.yaml' \
    platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/`
  returns **zero** (down from 26).
- **All 8 framework paths now present in the rewired files:**
  for each layer L in `01_BRD 02_PRD 03_EARS 04_BDD 05_ADR 06_SPEC 07_TDD 08_IPLAN`,
  `grep -c "framework/layers/$L/.*-TEMPLATE\.yaml" platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/SKILL.md`
  returns **>= 2** (the bullet list + the table; 17 lines total / 8 layers
  ≈ 2.125 per layer on average — bullets + table rows pair up).
- **`sdd-workflow-quickstart.md`** has all 8 framework paths after sed.
- **`SKILL.md:692` no longer mentions `skill_view`:**
  `grep -c skill_view platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/SKILL.md`
  returns **0**. (Confirmed by recon: line 692 is the **only**
  `skill_view` mention in `SKILL.md`.)
- **D-0013 conformance for skill:** no platform-local template
  duplication anywhere under `platforms/hermes/agent-skills/`:
  `find platforms/hermes/agent-skills -name '*-TEMPLATE.yaml' -not -path '*/governance/*' | wc -l`
  returns **0**. (The `governance/templates/` subdir holds non-layer
  artifacts — pre-commit configs, QA-bridge docs — and is correctly
  excluded.)
- **No regression in untouched lines:**
  - `SKILL.md` line 153 (`governance/templates/PROJECT_KICKOFF_PLAN-TEMPLATE.md`) still present.
  - `SKILL.md` line 1132 (D-0013 note) still present and unmodified.
  - `references/ucx-readme.md:126` tree-diagram untouched.
- **Conformance suite:** 25/25 (sanity — the suite scans only
  `framework/`, unaffected).
- **`ucx_flow|UCX_FLOW` hits across the skill remain at 0** (per P2-T7
  the skill was already zeroed — sanity check that nothing slipped in).
- **Scope-completeness:** the post-edit file set diffs from the
  pre-edit set only at the 8 deleted files + the 2 edited reference
  files. `git status --short` lists exactly those 10 paths (plus the
  `plans/` tracker updates and this plan).

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | A framework template is missing semantic content that the skill template carries (content loss on delete). | Approach §4 content-equivalence check before delete; halt on substantive delta. Recon confirmed the 3 inspected diffs are all engine-hardcode + minor phrasing. |
| R2 | A skill consumer (not just `SKILL.md`) reads `templates/0N_TYPE-TEMPLATE.yaml` at runtime via the Claude Code `skill_view` API and would break. | Recon confirmed only **2 files** carry the skill-relative path (`SKILL.md`, `sdd-workflow-quickstart.md`); no `scripts/` code references the path. The `skill_view` call format on `SKILL.md:692` is an *example for users*, not a runtime call. |
| R3 | The `governance/templates/` subdir gets caught up by an over-broad delete or grep. | Approach §1 deletes by enumerated filenames (`0{1..8}_*-TEMPLATE.yaml`), not `templates/*`. The verify gate explicitly excludes `governance/templates/` from the D-0013 conformance check (`-not -path '*/governance/*'`). |
| R4 | The sed pipe delimiter `\|` collides with content (file path containing `\|`). | None of the 8 file paths contain pipes; verified by `grep` on the pre-port snapshot. |
| R5 | The loading-mechanism rewrite on `SKILL.md:692` confuses readers (they expect a `skill_view` example). | The replacement explicitly explains *why* `skill_view` doesn't apply (templates live outside the skill, D-0013). Reader gets the actionable instruction + the rationale. |
| R6 | A future sub-typing of layers (e.g. `06_SPEC/CSPEC/CSPEC-TEMPLATE.yaml`) would need a different path format — the new references are too specific. | Out of scope (post-v1.0 per D-0012 R2). The current 8-layer flat model is the v1 framework; this task ports the references to match what exists today. Future sub-typing can re-rewire when it arrives. |
| R7 | Scope creep — pull in P2-T9 (MCP scaffold runtime) "while we're here". | Scope locked to the 8 file deletes + 2 reference-file edits. R5-style discipline from P2-T3. P2-T9's edit set is entirely under `platforms/hermes/src/` — zero file overlap with this plan. |
| R8 | The 8-pattern sed misses the `templates/NN_TYPE-TEMPLATE.yaml` placeholder on `SKILL.md:692`. | Intentional: that line is handled by §3 (structural rewrite, not substring swap). Verify gate explicitly checks `skill_view` is gone. |
| R9 | The "files to delete" count doesn't match the verify "down from 26" baseline (if a hidden reference exists). | Pre-flight Step 1 captures the *actual* baseline to `/tmp/p2t8-pregrep.txt`. Verify gate compares against the captured count, not the planning estimate. If the real count differs, halt and review. |

## Review log

### Pass 1 — 2026-05-20T13:25:00Z

- **G1. P2-T3 G18 lesson (cross-check `Out:` against design downstream).**
  P2-T1 Q3 explicitly enumerated "drop platform templates" and the skill
  package as the target. Confirmed that P2-T8 covers that downstream item
  for the **skill** specifically; P2-T9 covers it for the **MCP server**.
  No design downstream is left unscoped.
- **G2. Content-equivalence is a gate, not an afterthought.** R1
  motivated promoting the diff-check from "informal sanity" to a Step 2
  pre-condition. Halt-on-substantive-delta is explicit.
- **G3. The 8-pattern sed over a generic regex.** A generic
  `\b(0[1-8])_(BRD|PRD|EARS|BDD|ADR|SPEC|TDD|IPLAN)-TEMPLATE\.yaml\b →
  framework/layers/\1/\2-TEMPLATE.yaml` is tempting but couples the
  pattern to a NN-TYPE pairing the regex doesn't actually enforce
  (a typo like `02_BRD` would silently rewrite to nonsense). Eight
  pinned expressions are verbose but trivially auditable. Kept.
- **G4. `skill_view` loading-mechanism semantics.** Recon confirmed
  `skill_view` is a Claude-skill-package-internal file accessor; it
  cannot read files outside the skill. Once templates move to
  `framework/layers/`, the line **must** change from API to
  filesystem-path instruction, not just have the path replaced. Step §3
  handles that as a separate Edit. Without this, line 692 would
  document an API call that fails at runtime.
- **G5. Verify gate symmetry.** Each delete operation has a verify
  (templates dir gone, 0 skill-relative refs); each rewrite has a verify
  (8 framework paths present, `skill_view` gone). Each *non*-edit
  (untouched lines) also has a verify (lines 153, 1132 still present,
  ucx-readme.md untouched). Symmetric coverage.
- **G6. The D-0013 conformance verify line.** A coarse
  `find platforms/hermes/agent-skills -name '*-TEMPLATE.yaml' | wc -l`
  would catch the layer-template case but also catch the
  `governance/templates/` non-layer artifacts. Filter
  `-not -path '*/governance/*'` keeps the gate honest. Verified by hand
  that no other directory under `agent-skills/` has `*-TEMPLATE.yaml`
  files matching the layer pattern.
- **G7. P2-T7 G11 (deletion is cleaner than deprecation notes).**
  Bias toward `git rm` over "leave the files with a deprecation header".
  The previous skill port (P2-T7) already deleted 6 D-0013-obsolete
  sync files; this task continues that pattern.
- **G8. Pre-grep snapshot for reproducibility (P2-T3 G14 lesson).**
  Step 1 captures `/tmp/p2t8-pregrep.txt` before any change; verify
  references the captured count, not the planning estimate.
- **G9. Scope discipline against P2-T9.** R7 enumerates the boundary
  explicitly because both tasks are D-0013 reconciliations and easy to
  confuse. The 0 file overlap is a clean separator: this task only
  touches `agent-skills/spec-driven-development/sdd-orchestrator/`;
  P2-T9 only touches `platforms/hermes/src/`.
- **G10. List-completeness (P2-T0 Pass 3 lesson).** The 25-line
  reference inventory was built by exact grep, then validated against
  the two-file edit set. Verify gate ensures the post-edit set matches
  the post-edit expectations file-by-file.

### Pass 2 — 2026-05-20T13:40:00Z

- **G11. Pre-grep estimate "26 lines" — recheck.** Pass 1 wrote
  "expect 26 (25 references + 1 placeholder)". On re-count:
  `SKILL.md` has 8 list items (683–690) + 8 table rows (696–703) =
  16, plus the `templates/NN_TYPE-TEMPLATE.yaml` placeholder on 692 =
  **17**. `sdd-workflow-quickstart.md` has 8 table rows = **8**.
  Total **25** lines. The "26" was off-by-one — the placeholder is
  **inside the 17, not on top of it**. Corrected the pre-flight `wc -l`
  expectation to **25**. (R9's tolerance for mismatch means a wrong
  estimate doesn't break the plan — the captured baseline is the
  truth.)
- **G12. `references/sdd-workflow-quickstart.md` may have headings or
  other context that reference templates more loosely.** Re-grep with
  loose pattern (`templates/`) to check: only the 8 table rows hit; no
  prose paragraph elsewhere references the templates by skill-relative
  path. Confirmed scope.
- **G13. Symmetry with P2-T9 — could merging save work?** Considered.
  Net: P2-T8 touches `agent-skills/.../sdd-orchestrator/` (0 file
  overlap with P2-T9's `src/mcp_server/`); P2-T9 also requires test-
  fixture updates, which is more code-shaped work than P2-T8's prose-
  shaped work. Merging would dilute the commit message and complicate
  rollback. Keep separate.
- **G14. Risk R5 — does the user lose any information by removing
  `skill_view`?** No: the replacement (a) names the framework path
  pattern, (b) provides a concrete example, (c) explains why
  `skill_view` doesn't apply. Reader has more context, not less.
- **G15. Idempotency check.** If a re-run hit the sed mid-state (e.g.
  some lines already rewritten), do the patterns still match?
  Patterns target `templates/0N_TYPE-TEMPLATE.yaml`; post-rewrite text
  reads `framework/layers/0N_TYPE/TYPE-TEMPLATE.yaml`. Patterns don't
  match the post-rewrite text — safe to re-run, no double-rewrites,
  no corruption.
- **G16. No new findings on Approach / Step sequence / Verification.**
  Plan is internally consistent. Ready to present on approval.

### Pass 3 — 2026-05-20T13:55:00Z (retrospective)

Status: DONE. One verify-gate calibration error recorded.

- **G17. Verify gate V6 was too coarse — recon claim was wrong.** Pass 1
  / Pass 2 wrote V6 as "`skill_view` count = 0 in `SKILL.md`" on the
  premise that line 692 was the **only** `skill_view` mention. That
  claim was an over-confident recon — the actual count is **6**: line
  26 (reads `references/governance-load-protocol.md`), lines 33–35
  (read three governance `.md` files), line 692 (the rewritten line
  itself, mentioning `skill_view` *as the API that doesn't apply*),
  and line 796 (prose mentioning `skill_view` alongside other read
  mechanisms). All 5 other uses are **correct** — they read files
  *inside* the skill, which is exactly what `skill_view` does. Only
  the templates use was wrong (templates are now outside the skill).
  Correcting V6: the right check is
  `grep "skill_view.*templates/" → 0`, not `grep skill_view → 0`.
  Verified post-implementation: zero `skill_view` calls reference
  `templates/`. Gate passes.
- **Lesson:** when a verify gate counts the disappearance of an API
  use, scope the grep to the *combination* of API + the thing that's
  going away, not the API alone. Otherwise the gate misclassifies
  unrelated valid uses as failures.

## Implementation note (2026-05-20T13:55:00Z)

Executed. All 9 verify gates green (after V6 correction):

- **Pre-flight:** 25 references across 2 files captured to
  `/tmp/p2t8-pregrep.txt`. Matches plan estimate exactly.
- **Content-equivalence:** filtered-diff line counts per layer pair
  were 2 / 8 / 10 / 12 / 15 / 15 / 21 / 28 — all well below the 50-line
  halt threshold. Spot-check of 01_BRD (largest delta) confirmed all
  deltas were engine-hardcode-removal + minor phrasing. No substantive
  content lost.
- **Deletions:** 8 YAMLs removed via `git rm`; the empty parent dir
  was auto-removed by `git rm` (no `rmdir` needed).
- **Path rewrite:** 8-pattern sed cleared the 24 enumerated layer
  references (16 in `SKILL.md` + 8 in `sdd-workflow-quickstart.md`);
  the line-692 placeholder handled separately by structural Edit.
- **Verify gates:** templates dir absent; zero skill-relative template
  refs; all 8 framework paths present in both reference files (with
  expected mention frequency 1 in quickstart and 2-3 in SKILL.md);
  zero `skill_view(... templates/...)` calls (G17 calibration); D-0013
  conformance (no platform-local layer templates anywhere under
  `agent-skills/`); untouched lines (153, 1132) intact; conformance
  suite 25/25; zero `ucx_flow|UCX_FLOW` hits in skill.
- **Scope-completeness:** `git status --short` lists exactly the 10
  expected paths (8 D + 2 M) plus the plan file — no scope leak.
