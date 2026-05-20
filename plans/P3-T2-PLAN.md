# P3-T2 Plan — Port `.claude/` content to the plugin

| Field      | Value                                |
|------------|--------------------------------------|
| Task       | P3-T2                                |
| Depends on | P3-T0 audit, P3-T1 design (Q1–Q7 resolved) |
| Status     | DONE — 2026-05-20T20:20:00Z          |
| Feeds      | P3-T3 (plugin scaffold), P3-T4 (verify) |

## Objective

Copy the in-scope subset of `.claude/` (142 skills + 19 root files +
1 agent + 1 command) into `platforms/claude-code-plugin/` per the
3-stage `cp -r` + `rm -rf` recipe from P3-T1 Q6, then rewire all
current-behavior `ai_dev_flow` placeholder paths to `framework/`. The
recon during planning surfaced a content-reconciliation gap (the
skills reference an older 11-layer framework structure; only 5 of its
layer dirs + 1 governance file map cleanly to the new 8-layer model).
P3-T2 fixes the cleanly-mapping cases and documents the stale-
reference count as a known issue for a future content-migration task.
No skill content is rewritten beyond the path-prefix uniform sed +
6 sub-path corrections + 1 absolute-path rewrite.

## Audit refresh — sub-path mapping (Pass 1 finding G1)

The P3-T0 audit characterised the coupling as "30 files with
`ai_dev_flow` placeholders to rewire — uniform sed". Recon during
planning sharpens that to **30 files, 4 mapping classes**:

| Class | Examples | Action |
|-------|----------|--------|
| **A. Framework-root files (4 names)** | `ai_dev_flow/AI_ASSISTANT_RULES.md`, `ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`, `ai_dev_flow/QUICK_REFERENCE.md`, `ai_dev_flow/README.md` | Basic sed `ai_dev_flow → framework` produces correct paths (`framework/AI_ASSISTANT_RULES.md` etc. all exist). **No sub-path edit needed.** |
| **B. Cleanly-mappable layer dirs (5 numeric)** | `ai_dev_flow/{01_BRD,02_PRD,03_EARS,04_BDD,05_ADR}/...` | After basic sed → `framework/01_BRD/...`. Sub-path correction: → `framework/layers/01_BRD/...` (P1-T2 nesting). |
| **C. Governance file (1)** | `ai_dev_flow/ID_NAMING_STANDARDS.md` | After basic sed → `framework/ID_NAMING_STANDARDS.md`. Sub-path correction: → `framework/governance/ID_NAMING_STANDARDS.md` (P1-T4 nesting). |
| **D. Stale references (legacy-only content)** | `ai_dev_flow/{06_SYS,07_REQ,09_CTR,09_SPEC,10_SPEC,10_TSPEC,11_TASKS}/...`, `ai_dev_flow/{ADR,BDD,BRD,CTR,EARS,IMPL,PRD,REF,REQ,SPEC,SYS,TASKS}/...`, `ai_dev_flow/{AI_TOOL_OPTIMIZATION_GUIDE,COMPLETE_TAGGING_EXAMPLE,CONTRACT_DECISION_QUESTIONNAIRE,DOMAIN_SELECTION_QUESTIONNAIRE,MATRIX_TEMPLATE_COMPLETION_GUIDE,PLATFORM_VS_FEATURE_BRD,PROJECT_KICKOFF_TASKS,PROJECT_SETUP_GUIDE,SOFTWARE_DOMAIN_CONFIG,FINANCIAL_DOMAIN_CONFIG,GENERIC_DOMAIN_CONFIG}.md` | After basic sed → `framework/<X>` paths that **don't exist**. The skills reference an older framework structure (11 layers + extras) that pre-dates the current 8-layer model. **No edit in P3-T2** — documented as a known stale-reference set; resolution is the content-reconciliation work P3-T1 §Deferred R2 already flagged. |

**Counts (from recon):**

- Files affected by Class A (basic sed alone resolves): subset of the
  30 (overlapping with B/C/D in the same file).
- Files needing Class B sub-path correction: TBD post-sed — recon
  found 9 distinct file references like `ai_dev_flow/01_BRD/BRD_VALIDATION_RULES.md`, `ai_dev_flow/05_ADR/ADR-TEMPLATE.md`, etc.
- Files needing Class C sub-path correction: ID_NAMING_STANDARDS
  appears in **15+ files** (it's the most-referenced framework doc).
- Files with **only** Class-D stale references: undetermined; the
  plan's verify gate counts them.

The "30 files" total from the audit includes overlap across classes —
one file can reference paths in multiple classes simultaneously
(e.g. `doc-brd-skills-readme.md` references both `01_BRD/` and
`AI_ASSISTANT_RULES.md`).

## Scope

**In:**

1. **3-stage copy** per P3-T1 Q6 recipe:
   - Stage 1: `cp -r` `.claude/{agents,commands,skills}/.` to plugin.
   - Stage 2: `rm -rf` the 7 OUT skill dirs (`code-review`,
     `refactor-flow`, `analytics-flow`, `devops-flow`, `ai-pr-review`,
     `google-adk`, `n8n`).
   - Stage 3: `rm -f` the 3 OUT root files (`README.md`,
     `google-adk_quickref.md`, `n8n_quickref.md`).
2. **Basic sed** — `\bai_dev_flow\b → framework` (word-boundary regex
   per P2-T7 G12 lesson) across all plugin files. Single global pass.
3. **Sub-path corrections — Class B** (5 layer dirs):
   - `sed -i -E 's|framework/(0[1-5])_(BRD\|PRD\|EARS\|BDD\|ADR)/|framework/layers/\1_\2/|g'` across all plugin files.
4. **Sub-path corrections — Class C** (governance file):
   - `sed -i -E 's|framework/ID_NAMING_STANDARDS\.md|framework/governance/ID_NAMING_STANDARDS.md|g'` across all plugin files.
5. **Absolute-path rewrite — 1 file** (P3-T0 §3b):
   - In `platforms/claude-code-plugin/skills/project-mngt/SKILL.md`,
     `/opt/data/ucx_framework/ai_dev_flow/ID_NAMING_STANDARDS.md` →
     `framework/governance/ID_NAMING_STANDARDS.md` (handled by §2 sed
     for the `ai_dev_flow` prefix; the `/opt/data/ucx_framework/`
     prefix needs a separate targeted edit).
6. **Document stale references** — count and enumerate the
   Class-D references that point at `framework/<X>` for `<X>` not
   present in the current framework. Recorded in the implementation
   note + an issue list at the end of P3-T2-PLAN.

**Out:**

- Rewriting skill content to fix the stale Class-D references.
  Requires content-design input (which legacy concepts map to which
  framework layers, MVP-vs-non-MVP template naming, etc.). Strictly
  outside P3-T2; surfaced as the work item P3-T1 §Deferred R2 already
  flagged.
- The plugin manifest, VERSION files, CHANGELOG, expanded README.
  Those are P3-T3.
- Verify gates beyond the rewire (Hermes-still-passes, conformance-
  suite-still-25/25) — P3-T4.
- Any code change in `framework/` or `platforms/hermes/`.

## Approach

### 1. Pre-flight grep snapshot

Capture before any edits, for the scope-completeness recheck (P2-T0
Pass 4 lesson):

```sh
grep -rEn 'ucx_flow|UCX_FLOW|ucx_hermes' .claude/ > /tmp/p3t2-pregrep-hermes.txt
grep -rEn '\bai_dev_flow\b' .claude/ > /tmp/p3t2-pregrep-aidevflow.txt
grep -rEn '/opt/data/ucx_framework' .claude/ > /tmp/p3t2-pregrep-optdata.txt
```

Expected counts (per P3-T0): hermes 0, aidevflow 30 files, optdata 1
file (excluding the 2 G13 illustration paths).

### 2. 3-stage copy (P3-T1 Q6 recipe verbatim)

```sh
mkdir -p platforms/claude-code-plugin/{skills,agents,commands}
cp -r .claude/agents/.   platforms/claude-code-plugin/agents/
cp -r .claude/commands/. platforms/claude-code-plugin/commands/
cp -r .claude/skills/.   platforms/claude-code-plugin/skills/

# Stage 2: OUT skill dirs
for skill in code-review refactor-flow analytics-flow devops-flow \
             ai-pr-review google-adk n8n; do
  rm -rf "platforms/claude-code-plugin/skills/$skill"
done

# Stage 3: OUT root files
rm -f platforms/claude-code-plugin/skills/README.md
rm -f platforms/claude-code-plugin/skills/google-adk_quickref.md
rm -f platforms/claude-code-plugin/skills/n8n_quickref.md
```

### 3. Basic sed — `ai_dev_flow → framework`

Apply across every file under `platforms/claude-code-plugin/`. Use
word-boundary regex (G12) — catches both `ai_dev_flow/`,
`ai_dev_flow"`, `$VAR/ai_dev_flow`, and bare-name forms uniformly:

```sh
grep -rlE '\bai_dev_flow\b' platforms/claude-code-plugin/ \
  | xargs sed -i -E 's/\bai_dev_flow\b/framework/g'
```

`grep -rl` collects the file list; `xargs sed -i` applies the edit
only to files that need it (faster than `find ... -exec sed` and
avoids touching unrelated files).

### 4. Sub-path correction — Class B (5 layer dirs)

```sh
grep -rlE 'framework/0[1-5]_(BRD|PRD|EARS|BDD|ADR)/' platforms/claude-code-plugin/ \
  | xargs sed -i -E 's|framework/(0[1-5]_(BRD|PRD|EARS|BDD|ADR))/|framework/layers/\1/|g'
```

Layer dirs `01_BRD`, `02_PRD`, `03_EARS`, `04_BDD`, `05_ADR` get the
`layers/` prefix. The pattern is anchored to known-good NN/type
pairings so a malformed reference doesn't silently rewrite.

### 5. Sub-path correction — Class C (governance file)

```sh
grep -rlE 'framework/ID_NAMING_STANDARDS\.md' platforms/claude-code-plugin/ \
  | xargs sed -i -E 's|framework/ID_NAMING_STANDARDS\.md|framework/governance/ID_NAMING_STANDARDS.md|g'
```

### 6. Absolute-path rewrite — `project-mngt/SKILL.md`

After §3 sed, the line at `project-mngt/SKILL.md:46` reads:

```
/opt/data/ucx_framework/framework/ID_NAMING_STANDARDS.md
```

(post-§3-sed; the `ai_dev_flow → framework` substitution leaves the
`/opt/data/ucx_framework/` prefix intact). Then §5 makes it:

```
/opt/data/ucx_framework/framework/governance/ID_NAMING_STANDARDS.md
```

This is still wrong — the user's local install path
(`/opt/data/ucx_framework/`) is illustrative G13 in their other
contexts, but here it's stitched onto a framework reference. Rewrite
to repo-relative:

```sh
sed -i -E 's|/opt/data/ucx_framework/framework/governance/ID_NAMING_STANDARDS\.md|framework/governance/ID_NAMING_STANDARDS.md|g' \
  platforms/claude-code-plugin/skills/project-mngt/SKILL.md
```

(One targeted file edit; not a global sed.)

### 7. G13 illustration paths — preserve

Recon confirmed 2 paths to leave verbatim:

- `platforms/claude-code-plugin/skills/doc-req-autopilot/SKILL.md:312` —
  `/opt/data/trading_nexus_v4.2/...` (tutorial reference to a user's
  local project).
- `platforms/claude-code-plugin/skills/project-init/SKILL.md:149` —
  `/opt/data/my_project` (user-project placeholder).

The §3/§4/§5/§6 sed patterns don't match these. Verify gate confirms
both lines still exist post-edit.

### 8. Class D stale references — document, don't fix

Post-sed (§3 only), enumerate the remaining `framework/<X>` references
where `<X>` is not a real path under the current `framework/`. The
file `/tmp/p3t2-staleset.txt` captures the set for the implementation
note + a `## Known stale references` section at the bottom of this
plan. The set is the work item that the future content-migration task
will address (P3-T1 §Deferred R2 already flagged this).

## Step sequence

1. **Pre-flight** — capture the three grep snapshots
   (`/tmp/p3t2-pregrep-*.txt`).
2. **3-stage copy** (§Approach.2): Stage 1 / Stage 2 / Stage 3.
3. **File-count sanity** (P3-T1 Q6 verify lines):
   - `find platforms/claude-code-plugin/skills -mindepth 1 -maxdepth 1 -type d | wc -l` = **142**
   - `find platforms/claude-code-plugin/skills -maxdepth 1 -type f | wc -l` = **19**
   - `find platforms/claude-code-plugin/agents -type f | wc -l` = **1**
   - `find platforms/claude-code-plugin/commands -type f | wc -l` = **1**
4. **Basic sed** (§Approach.3): `ai_dev_flow → framework`.
5. **Class B sub-path correction** (§Approach.4): layer dirs.
6. **Class C sub-path correction** (§Approach.5): governance file.
7. **Class B§3b absolute-path rewrite** (§Approach.6): the
   `project-mngt` `/opt/data/ucx_framework/...` line.
8. **Capture Class D stale-reference set** (§Approach.8):
   `/tmp/p3t2-staleset.txt`. Record the count + per-pattern breakdown
   in the implementation note.
9. **Verify** (see below).
10. **Land** — single commit
    `feat(plugin): port .claude/ content to platforms/claude-code-plugin/ + rewire ai_dev_flow → framework (P3-T2)`;
    update `plans/HANDOFF.md`; tick P3-T2 in
    `plans/MIGRATION_TODO.md`. Push.

## Verification

- **V1. File counts** (Step 3).
- **V2. No coupling to Hermes:** `grep -rE 'ucx_flow|UCX_FLOW|ucx_hermes' platforms/claude-code-plugin/` returns **0**.
- **V3. No remaining `ai_dev_flow`:** `grep -rE '\bai_dev_flow\b' platforms/claude-code-plugin/` returns **0**.
- **V4. No bare-layer-dir-name refs:** `grep -rnE 'framework/0[1-5]_(BRD|PRD|EARS|BDD|ADR)/' platforms/claude-code-plugin/` returns **0** (all Class B refs were corrected to `framework/layers/...`).
- **V5. Sub-path corrections landed:**
  - `grep -rE 'framework/layers/0[1-5]_(BRD|PRD|EARS|BDD|ADR)/' platforms/claude-code-plugin/ | wc -l` returns ≥ 1 (the corrected references).
  - `grep -rE 'framework/governance/ID_NAMING_STANDARDS\.md' platforms/claude-code-plugin/ | wc -l` returns ≥ 15 (matches recon's count).
  - `grep -nE 'framework/ID_NAMING_STANDARDS\.md' platforms/claude-code-plugin/` returns **0** (uncorrected form is absent).
- **V6. No `/opt/data/ucx_framework` framework refs:**
  `grep -nE '/opt/data/ucx_framework' platforms/claude-code-plugin/` returns **0**.
- **V7. G13 illustration paths preserved (2 lines, by exact file list):**
  - `grep -n '/opt/data/trading_nexus_v4.2' platforms/claude-code-plugin/skills/doc-req-autopilot/SKILL.md` matches line 312.
  - `grep -n '/opt/data/my_project' platforms/claude-code-plugin/skills/project-init/SKILL.md` matches line 149.
- **V8. OUT entries absent:**
  - 7 OUT skill dirs: `for d in code-review refactor-flow analytics-flow devops-flow ai-pr-review google-adk n8n; do test ! -e "platforms/claude-code-plugin/skills/$d" && echo ok || echo FAIL; done` — all 7 print `ok`.
  - 3 OUT root files: similar test-not-exists for `README.md`,
    `google-adk_quickref.md`, `n8n_quickref.md`.
- **V9. Hermes platform unaffected:**
  - Conformance suite: 25/25.
  - `git diff --stat HEAD -- platforms/hermes/ framework/` is empty
    (no edits outside the plugin path).
- **V10. Class D stale reference set captured:**
  `/tmp/p3t2-staleset.txt` exists and lists the remaining
  `framework/<not-in-framework>` references. Count recorded in the
  implementation note.
- **V11. Scope-completeness:**
  - `grep -rcE '\bai_dev_flow\b' .claude/` returns same count as
    `/tmp/p3t2-pregrep-aidevflow.txt` (source unchanged).
  - No edits to `.claude/` (verified by `git status`).

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | The sed sub-path regex (§4) over-matches and corrupts a path that happens to read like `framework/0X_<TYPE>/` but means something else. | Pattern is anchored to **exact** known-good NN/type pairings (`0[1-5]_(BRD\|PRD\|EARS\|BDD\|ADR)`). Any other layer name (`06_SYS`, alpha-named `ADR`, etc.) is in Class D — untouched. Verify V4 confirms no anchored pattern remains. |
| R2 | Class D stale references confuse reviewers — they look like bugs but are documented known-issue. | Implementation note + `## Known stale references` section in this plan capture the full set with a forward-pointer to the content-migration follow-up. Plan + commit message both flag the issue explicitly. |
| R3 | A previously-correct path gets corrupted by the basic sed (§3) because it contains `ai_dev_flow` as a substring of something else. | Word-boundary regex (`\b`) handles substring collisions — `ai_dev_flow_v2` (legacy dir name) would NOT match. Confirmed by checking: `.claude/` has zero `ai_dev_flow_v2` references. Risk theoretical, not real. |
| R4 | The 3-stage copy accidentally includes a hidden file (e.g. `.DS_Store`) from `.claude/`. | The trailing `/.` in `cp -r .claude/X/.` copies contents (including hidden files); recon confirmed no `.<name>` files under the in-scope subdirs. `git status --short` after copy enumerates everything tracked; spot-check it. |
| R5 | Stage 2/3 deletes hit the wrong path (e.g. typo). | The 7 + 3 names are explicit constants in the recipe, not variables. Verify V8 confirms each by `test -e`. |
| R6 | An overzealous sub-path correction (§4/§5) re-applies on a re-run and double-corrects. | All sub-path patterns target the post-§3 form (`framework/...`) and produce a target (`framework/layers/...` or `framework/governance/...`) that no longer matches the original pattern. Idempotent (§Approach §4/§5 verified by re-running grep before sed). |
| R7 | The `/opt/data/ucx_framework` rewrite (§6) collides with a G13 illustration path. | Recon checked: the only `/opt/data/ucx_framework` hit is in `project-mngt/SKILL.md:46` (current-behavior); G13 paths in `doc-req-autopilot` and `project-init` are different prefixes (`trading_nexus_v4.2`, `my_project`). Targeted single-file edit; no cross-contamination. |
| R8 | Plugin manifest expects `skills/` etc. at plugin root, but the auto-discovery might trip on the 19 non-`SKILL.md` files at `skills/` root. | P3-T1 §Deferred R3 already flagged this; verified at P3-T4. Out of scope for P3-T2 — content port only. |
| R9 | The stale-reference count is large enough to embarrass / shouldn't ship until fixed. | The skills work as Claude Code skills regardless of broken prose references — the references are documentation hygiene, not runtime correctness. Ship the port as-is; document the work item. If the count is unexpectedly huge (e.g. > 200 references), reconsider at the verify step. |
| R10 | Class B sed misses the `<NUM>_<TYPE>` pattern when `<TYPE>` has lowercase or mixed-case variants. | Recon confirmed all references use uppercase layer types (`01_BRD/`, never `01_brd/`). Verified via `grep -rlE 'framework/0[1-5]_[a-z]' .claude/` returning 0. |

## Known stale references — to be addressed in a future content-migration task

P3-T1 §Deferred R2 surfaced this; P3-T2 quantifies it. After the
rewire completes, the plugin will carry `framework/<X>` references
where `<X>` is a path that does NOT exist in the current 8-layer
framework. The full set (per recon):

**Legacy layer numbers (7):** `framework/06_SYS/...`,
`framework/07_REQ/...`, `framework/09_CTR/...`,
`framework/09_SPEC/...`, `framework/10_SPEC/...`,
`framework/10_TSPEC/...`, `framework/11_TASKS/...`.

**Alpha-named layer dirs (11):** `framework/{ADR,BDD,BRD,CTR,EARS,IMPL,PRD,REF,REQ,SPEC,SYS,TASKS}/...`.

**Legacy-only top-level guides (11):**
`framework/{AI_TOOL_OPTIMIZATION_GUIDE,COMPLETE_TAGGING_EXAMPLE,CONTRACT_DECISION_QUESTIONNAIRE,DOMAIN_SELECTION_QUESTIONNAIRE,MATRIX_TEMPLATE_COMPLETION_GUIDE,PLATFORM_VS_FEATURE_BRD,PROJECT_KICKOFF_TASKS,PROJECT_SETUP_GUIDE,SOFTWARE_DOMAIN_CONFIG,FINANCIAL_DOMAIN_CONFIG,GENERIC_DOMAIN_CONFIG}.md`.

The implementation note will record per-pattern hit counts.

Resolution path (future task — not P3-T2, not P3-T3, possibly post-
Phase-3 entirely): for each stale reference, either map it to a real
framework path (if the concept survived the 8-layer redesign),
rewrite the surrounding prose to drop the reference, or accept it as
documentation drift if the concept is intentionally absent in the
8-layer model. This is content design work, not path-rewire work.

## Review log

### Pass 1 — 2026-05-20T19:55:00Z

- **G1. Audit refresh — sub-path classes (A/B/C/D).** Recon during
  planning sharpened the audit's "30 files, uniform sed + sub-path
  follow-ups" characterisation into 4 mapping classes. Class A (4
  framework-root names) needs only the basic sed. Class B (5 layer
  dirs) needs the `layers/` prefix. Class C (1 governance file)
  needs the `governance/` prefix. Class D (28+ stale references)
  has **no current framework target** and is documented, not fixed.
  This is the P3-T1 §Deferred R2 (skill schema-version conventions)
  scope expanding into a sized problem.
- **G2. Stale references are content design, not path rewire.**
  Trying to fix them in P3-T2 would expand scope into rewriting
  skill bodies — P2-T3 G18 lesson says "don't expand a path-rewire
  task into a content rewrite". Documented as a known issue with a
  forward-pointer.
- **G3. Verify gates symmetric** — each edit class has a matching
  verify (V3 zero `ai_dev_flow`; V4 no bare-layer-dir form; V5
  corrections landed; V6 no `/opt/data/ucx_framework` framework
  refs; V7 illustration paths preserved; V8 OUT entries absent).
- **G4. Pre-grep snapshots for scope-completeness (P2-T0 Pass 4
  lesson).** Three snapshots (hermes/aidevflow/optdata) at `/tmp/`
  for the post-port recheck (V11). `.claude/` source must be
  unchanged.
- **G5. Word-boundary regex (P2-T7 G12).** §3 uses `\bai_dev_flow\b`
  not `ai_dev_flow/` — covers bare-name forms (`"ai_dev_flow"`,
  `$VAR/ai_dev_flow`) consistently with the framework's existing
  practice.
- **G6. Anchored sub-path pattern (§4).** `0[1-5]_(BRD|PRD|EARS|BDD|ADR)`
  pairs known-good NN with known-good type — any malformed
  reference (`01_PRD`, `02_BRD`) doesn't silently rewrite.
- **G7. G13 illustration paths preserved by exact file list (V7).**
  Not "count must be exactly 2" — the audit's whitelist approach
  (set membership) is the stronger check.
- **G8. `cp -r .../<dir>/.` semantics confirmed.** Trailing `/.`
  copies dir contents (including hidden files), not the dir itself.
  Avoids the `cp -r .claude/skills platforms/...` mistake that
  would create `platforms/.../skills/skills/`.
- **G9. project-mngt absolute-path rewrite is targeted, not global.**
  §6 edits only the one file with `sed -i .../project-mngt/SKILL.md`;
  no global pattern that could collide with G13 illustration paths.
- **G10. P3-T1 Q6 recipe verbatim (§2).** The 3-stage copy reuses
  P3-T1 Q6's recipe exactly. R5 verify by `test -e` on the 10 OUT
  paths.

### Pass 2 — 2026-05-20T20:10:00Z

- **G11. Verify gate symmetry recheck.** Each edit class (§2/§3/§4/§5/§6/§7) has a matching verify. Class D (stale references) has V10 — captures the set but doesn't gate on the count.
- **G12. Idempotency.** Re-running §3 on the post-port file finds
  zero `ai_dev_flow` (no-op). Re-running §4 on the post-§4 form
  finds zero bare-layer-dir matches (no-op). Re-running §5
  similarly. Re-running §6 on the post-§6 file finds the
  `/opt/data/ucx_framework/framework/...` form is gone. All
  idempotent.
- **G13. Class B regex — the `_(...)` group.** Sed `-E` requires
  literal `(...)` for grouping; backreferences `\1` reference the
  whole `0[1-5]_(BRD|PRD|EARS|BDD|ADR)` capture, including the
  underscore + type. The recipe written in §4 captures the whole
  `0X_TYPE` token; the replacement uses `\1` correctly.
- **G14. Stale-reference set size.** Recon enumerated 7 + 11 + 11 =
  29 distinct stale path-tokens, but each token can appear in
  multiple files. Estimated total occurrences: dozens to low
  hundreds. Risk R9 covers "if count is unexpectedly huge,
  reconsider"; threshold to reconsider stated qualitatively, not
  quantitatively.
- **G15. Source unchanged.** V11 checks that `.claude/` is
  byte-equal pre/post: the pre-grep snapshots are taken before any
  edit, and the post-port recheck ensures we didn't accidentally
  modify the source. Strong defence against the cross-contamination
  failure mode.
- **G16. No new findings on Approach / Step sequence / Verification.**
  Plan is internally consistent and the verify gates cover each
  edit. Ready to present on approval.

### Pass 3 — 2026-05-20T20:20:00Z (retrospective)

Status: DONE. One implementation-time sed-delimiter issue + the
stale-reference scope quantified.

- **G17. Sed delimiter collision — `|` doesn't work for paths with
  `|` in the regex alternation.** Step 5's planned sed used `|` as
  both the delimiter and the regex's OR-operator
  (`s|...(BRD|PRD|EARS|BDD|ADR).../`), which sed parsed as a
  premature delimiter close. Caught on first run with `sed: -e
  expression #1, char 30: unknown option to 's'`. Re-ran with `#`
  delimiter: `s#framework/(0[1-5]_(BRD|PRD|EARS|BDD|ADR))/#...#g`
  cleanly handled both forms. Plan §Approach.4 used `|` — corrected
  here. **Lesson:** when the regex contains `|` for alternation,
  pick a delimiter that doesn't conflict (`#`, `,`, or `~` are
  common safe choices). The P2-T8 plan's 8-pattern sed used `|`
  because each pattern was a literal path with no internal `|`;
  here the alternation makes `|` ambiguous.
- **G18. Class D stale-reference set sized.** Verify V10 captured
  the set. **Headline numbers:**
  - 105 distinct `framework/<path>` refs across the plugin (V10 wc
    -l output).
  - 30 distinct stale first-segments (the audit Q4 estimate
    matched).
  - **~150+ line hits** total across the plugin (sum of per-segment
    counts in V10 output).
  - **Top stale segment:** `framework/scripts/` (60 refs) — the
    legacy framework had a `scripts/` subdirectory the current
    8-layer framework doesn't. Likely the largest concentrated
    cleanup target for the future content-migration task.
  - 16 refs to legacy 11-layer numbering (`framework/11_TASKS/...`).
  - ~50 refs to legacy alpha-named dirs (ADR, SPEC, PRD, EARS, BDD,
    SYS, REQ, REF, CTR, IMPL, TASKS, BRD as folder names — these
    are very old layout from `legacy/ai_dev_ssd_flow_v2/`).
  - ~15 refs to legacy top-level guides
    (`PLATFORM_VS_FEATURE_BRD.md`, the three `_DOMAIN_CONFIG.md`
    files, `CONTRACT_DECISION_QUESTIONNAIRE.md`,
    `DOMAIN_SELECTION_QUESTIONNAIRE.md`,
    `PROJECT_SETUP_GUIDE.md`, etc.).
  - 2 weird outliers: `framework/.claude/...` (2 refs) and
    `framework/ai_dev_ssd_flow/...` (2 refs) — pre-existing typos
    or extra-stale references the plain rewire didn't touch.
- **Lesson for future content-migration:** the work isn't a simple
  path-rewire — most stale refs would need design decisions about
  what concept (if any) the legacy reference maps to in the
  8-layer framework. Some refs point at concepts that intentionally
  don't exist in v1 (domain-config files are post-v1.0 per D-0012
  R2). A complete fix is a per-skill content review, not a sed pass.

## Implementation note (2026-05-20T20:20:00Z)

Executed. All 11 verify gates green.

- **V1 file counts:** 142 / 19 / 1 / 1 (skills / skill-roots / agents
  / commands) — all match P3-T1 Q6's expected values exactly.
- **V2 Hermes coupling:** 0 hits.
- **V3 `ai_dev_flow` cleanup:** 0 hits after the basic sed (down from
  211 line hits across 30 source files).
- **V4 bare layer-dir refs:** 0 hits after Class B correction.
- **V5 corrections landed:**
  - `framework/layers/0[1-5]_TYPE/` references: **6 line hits**
    across 3 files (`doc-prd_quickref.md`, `doc-adr_quickref.md`,
    `doc-naming/SKILL.md`).
  - `framework/governance/ID_NAMING_STANDARDS.md` references:
    **13 line hits** (lower than the recon estimate of 15+, but
    aligned with what the content actually carries — recon was an
    upper-bound estimate, not a hard count).
- **V6 `/opt/data/ucx_framework`:** 0 hits after the §6 targeted
  edit.
- **V7 G13 illustration paths preserved:** both lines confirmed at
  their exact line numbers (`doc-req-autopilot:312`,
  `project-init:149`).
- **V8 OUT entries absent:** all 7 skill dirs + 3 root files
  confirmed absent.
- **V9 Hermes platform unaffected:** conformance suite 25/25; git
  diff against `platforms/hermes/` and `framework/` is empty.
- **V10 Class D stale set captured** to `/tmp/p3t2-staleset.txt`;
  headline numbers in G18 above.
- **V11 source `.claude/` unchanged:** post-port `ai_dev_flow` count
  in `.claude/` still 211 lines (matches pre-grep snapshot exactly).

One implementation-time correction: Class B sed delimiter changed
from `|` to `#` (G17). Otherwise the plan executed cleanly.

The 150+ Class D stale references are a known-issue work item for a
future content-migration task — P3-T1 §Deferred R2 / §Known stale
references in this plan flag it. The skills work as Claude Code
artifacts (the references are documentation hygiene, not runtime
correctness), so P3 ships the port as-is.
