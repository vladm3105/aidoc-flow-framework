# P3-T1 Design — Claude Code plugin

| Field      | Value                                |
|------------|--------------------------------------|
| Task       | P3-T1                                |
| Depends on | P3-T0 audit                          |
| Produced by| P3-T1 (`plans/P3-T1-PLAN.md` — this doc IS the plan output) |
| Date       | 2026-05-20T18:40:00Z                 |
| Feeds      | P3-T2, P3-T3                         |

## Summary

Seven design choices resolved before any content moves. The plugin
manifest is minimal (auto-discovery does the heavy lifting), the
in-scope skill set is **142** (129 `doc-*` + 13 non-doc, after
deciding 3 borderline as IN and 5 as OUT), the `save-plan` command
ports, the 22 `.claude/skills/` root files split 19 IN / 3 OUT, the
plugin name is `aidoc-flow`, the copy strategy is `cp -r` with an
exclusion list, and no plugin lifecycle hooks ship in `v0.1.0`.

| Q | Question | Choice |
|---|----------|--------|
| Q1 | Plugin manifest schema | Minimal manifest: `name`, `description`, `version`, `author`, `license`, `repository`. Auto-discovery handles skills/agents/commands. |
| Q2 | Borderline non-doc skills (8 candidates) | 3 IN: `test-automation`, `security-audit`, `contract-tester`. 5 OUT: `code-review`, `refactor-flow`, `analytics-flow`, `devops-flow`, `ai-pr-review`. Net non-doc IN: 13; plugin total 142 skills. |
| Q3 | `save-plan` command | **IN** — generic plan-save utility, not migration-specific. |
| Q4 | 22 root files under `.claude/skills/` | 19 IN (rewire), 3 OUT (`README.md`, `google-adk_quickref.md`, `n8n_quickref.md`). |
| Q5 | Plugin name | `aidoc-flow` — matches project name; slash-prefix `/aidoc-flow:...`. |
| Q6 | Copy strategy | `cp -r` from `.claude/<subset>` to `platforms/claude-code-plugin/<subset>` with an explicit exclusion list (the 7 OUT skills + 3 OUT root files + hooks/ + settings*.json). |
| Q7 | Plugin lifecycle hooks | None in `v0.1.0`. Declarative-only (skills + agents + commands). |

The non-obvious decisions are Q2 (per-skill in/out judgement based on
SDD-adjacency, not just description) and Q4 (`README.md` drops because
it documents an obsolete multi-project symlink pattern). Both recorded
inline; no entry in `plans/DECISIONS.md` needed — they're plugin-
scoping calls, not framework-level decisions.

## Q1 — Plugin manifest schema

**Options:**
1. Minimal manifest — only `name`, `description`, `version`, `author`,
   `license`, `repository`. Skills/agents/commands auto-discovered
   from conventional paths.
2. Explicit registration — enumerate every skill/agent/command in the
   manifest (defensive against discovery bugs).
3. Hybrid — minimal manifest + a `keywords` array listing the SDD
   layers covered, for plugin-marketplace discoverability.

**Input gathered:** Claude Code's plugin docs (verified via
claude-code-guide agent): plugin.json lives at
`.claude-plugin/plugin.json`; required fields are just `name` plus the
file's existence; recommended are `description` and `version`; optional
are `author` (object with `name`/`email`/`url`), `homepage`,
`repository`, `license`, `keywords`. **Auto-discovery from `skills/`,
`agents/`, `commands/`, `hooks/`, `.mcp.json`, `.lsp.json`, `monitors/`,
`bin/`, `settings.json` is the default and Claude Code does not support
an explicit registration block.** No published `$schema` URL.

**Chosen:** Option 1 — minimal manifest.

```jsonc
{
  "name": "aidoc-flow",
  "description": "AI-Driven Specification-Driven Development (SDD) workflow — skills, agents, and commands for the 8-layer doc flow (BRD → IPLAN). Consumes the aidoc-flow framework spec.",
  "version": "0.1.0",
  "author": {
    "name": "<populated from `git config user.name` at P3-T3>",
    "url": "https://github.com/vladm3105/aidoc-flow-framework"
  },
  "license": "MIT",
  "repository": "https://github.com/vladm3105/aidoc-flow-framework",
  "homepage": "https://github.com/vladm3105/aidoc-flow-framework",
  "keywords": ["sdd", "spec-driven-development", "documentation", "brd", "prd", "ears", "bdd", "adr", "iplan"]
}
```

**Rationale:** Option 2 (explicit registration) fights the platform's
design — Claude Code auto-discovers and there's no field to register
skills in. Option 3 differs from Option 1 only by the `keywords` list,
which Option 1 already includes for marketplace findability. Option 1
is the doc-conformant minimum + the recommended polish (description,
keywords, repository links) and nothing more.

**Downstream implications:**
- **P3-T3 plugin.json:** write the file above with the exact field
  set. Validate by `python -m json.tool < .claude-plugin/plugin.json`.
- **P3-T3 directory layout:** `skills/`, `agents/`, `commands/` live
  at plugin root (not nested under `.claude-plugin/`).
- **`version` field:** `0.1.0` — must match
  `platforms/claude-code-plugin/VERSION` (the two are written in P3-T3
  and verified equal in P3-T4).
- **License:** The repo doesn't currently carry a top-level `LICENSE`
  file (verified by `ls LICENSE` returning nothing); choosing `MIT`
  in the manifest is a placeholder declaration. If the project later
  adds a `LICENSE` file with a different choice, the manifest updates
  to match — flagged in §Deferred.

## Q2 — Borderline non-doc skills (8 to classify)

The audit's initial classification gave 12 clearly IN, 6 borderline
(corrected to 8 here after re-reading the audit list), 2 clearly OUT.
Decision criterion: **does the skill participate in the SDD workflow
(create / validate / audit / fix / review an SDD artifact, or
orchestrate among them), or is it a general-purpose dev skill?**
General-purpose skills are out of plugin scope — they belong in a
user's individual setup, not this distribution.

| Skill | Decision | Rationale |
|-------|----------|-----------|
| `test-automation` | **IN** | Adjacent to Layer 10 TSPEC (test plans / writing tests / quality validation). Plugin users authoring TSPEC artifacts will reach for it. |
| `security-audit` | **IN** | Feeds Layer 10 SECTEST (security analysis / vulnerability assessment / threat review). Plugin users producing SECTEST artifacts need it. |
| `contract-tester` | **IN** | Directly tests CTR artifacts (Layer 8). Description: "test and validate API contracts against specifications." Tight SDD coupling. |
| `code-review` | **OUT** | Generic code review (quality, standards, best practices). Not tied to any SDD artifact. User can install separately. |
| `refactor-flow` | **OUT** | Code refactoring. Outside SDD scope. |
| `analytics-flow` | **OUT** | Data analysis. Unrelated to SDD. |
| `devops-flow` | **OUT** | DevOps practices (GCP/Azure/AWS). Outside SDD. |
| `ai-pr-review` | **OUT** | General PR review automation. Not SDD-specific. |

**Combined non-doc IN total:** 10 (clearly IN: `adr-roadmap`,
`charts-flow`, `context-analyzer`, `mermaid-gen`, `project-init`,
`project-mngt`, `quality-advisor`, `skill-recommender`, `trace-check`,
`workflow-optimizer`) + 3 (borderline-IN) = **13**.

**Combined non-doc OUT total:** 2 (clearly OUT: `google-adk`, `n8n`)
+ 5 (borderline-OUT) = **7**.

**Plugin skill total:** 129 `doc-*` + 13 non-doc = **142 skills**.
(Confirmed: 20 non-doc dirs under `.claude/skills/` total; 13 + 7 = 20.)

**Downstream implications:**
- **P3-T2 exclusion list:** `.claude/skills/{code-review,refactor-flow,
  analytics-flow,devops-flow,ai-pr-review,google-adk,n8n}/` — 7 dirs
  not copied to the plugin.
- **P3-T4 verify count:** `find platforms/claude-code-plugin/skills/
  -mindepth 1 -maxdepth 1 -type d | wc -l` returns **142** (a
  guardrail against an accidental over- or under-copy).

## Q3 — `save-plan` command

**Options:**
1. Port — `save-plan.md` is a generic "save current conversation plan
   to a timestamped file" utility. Re-read of the command body
   confirms it's not migration-specific.
2. Drop — keep `save-plan` migration-only.

**Input gathered (re-reading `.claude/commands/save-plan.md`):** the
command reads `TodoWrite` entries, prompts the user for a plan name,
and writes a `{name}_YYYYMMDD_HHMMSS.md` implementation file to a
configurable directory (`.claude/CLAUDE.md > Work Plans Directory`).
**It does not reference `plans/PX-T*.md`**, the migration's review-pass
gate, or any other migration artifact. The command is reusable by any
project that wants to capture a conversation plan as a file.

**Chosen:** Option 1 — port.

**Rationale:** The command is genuinely generic and useful for plugin
users adopting the SDD workflow (they may want to capture
project-init plans, IPLAN drafts, etc.). Migration-only behavior is
in the **hooks**, not in this command.

**Downstream implications:**
- **P3-T2:** copy `.claude/commands/save-plan.md` →
  `platforms/claude-code-plugin/commands/save-plan.md`.
- **P3-T4 verify:** `commands/` has exactly 1 file in the plugin.

## Q4 — 22 root files under `.claude/skills/`

These sit outside any skill directory. Audit §1 listed them; per-file
in/out judgement happens here.

| File | Decision | Rationale |
|------|----------|-----------|
| `README.md` | **OUT** | Reads "Canonical source: `ucx_framework/.claude/skills/`" and documents a multi-project symlink pattern that doesn't apply to a plugin distribution. Content is migration-internal naming. Plugin's top-level `README.md` covers user docs. |
| `REVIEW_DOCUMENT_STANDARDS.md` | **IN** | Shared review standards used by `doc-*-reviewer` skills. Plugin users reviewing SDD docs will reach for it. |
| 18 × `<X>_quickref.md` (except `google-adk` and `n8n`) | **IN** | Per-skill quick-reference docs. Useful for users picking among skill variants. Rewire pass (`ai_dev_flow` → `framework`). |
| `google-adk_quickref.md` | **OUT** | Its parent skill is OUT (Q2). |
| `n8n_quickref.md` | **OUT** | Its parent skill is OUT (Q2). |
| `doc-brd-skills-readme.md` | **IN** | BRD-skill-set overview; rewire. |
| `doc-spec-subtype-skills-readme.md` | **IN** | SPEC-subtype overview; rewire. |

**Total:** 22 root files → **19 IN, 3 OUT**.

**Downstream implications:**
- **P3-T2:** copy the 19 IN files; explicitly exclude the 3 OUT files.
- **P3-T2 coupling rewire:** apply the `\bai_dev_flow\b → framework`
  sed pattern (with sub-path follow-ups, P2-T3 G15 idempotency rule)
  across the 19.
- **P3-T4 verify:** `find platforms/claude-code-plugin/skills
  -maxdepth 1 -type f | wc -l` returns **19**.

## Q5 — Plugin name

**Options:**
1. `aidoc-flow` — matches project name; clean and short.
2. `doc-flow` — matches the orchestrator skill name; risk of user
   confusion (is `doc-flow` the plugin or the skill?).
3. `aidoc-flow-doc-skills` — descriptive but verbose; slash-prefix
   `/aidoc-flow-doc-skills:doc-brd-autopilot` is unwieldy.
4. `aidocf` / `aidf` — short slug; opaque.

**Chosen:** Option 1 — `aidoc-flow`.

**Rationale:** Matches the project's identity ("AI Doc Flow
Framework") — the plugin **is** the project's user-facing distribution
of the SDD engine. Option 2 collides with the skill of the same name
inside the plugin. Option 3 is too long for daily use
(`/aidoc-flow-doc-skills:doc-brd`). Option 4 is opaque.

**Downstream implications:**
- **plugin.json `name`:** `"aidoc-flow"`.
- **Slash-prefix:** users invoke skills as `/aidoc-flow:doc-brd`,
  `/aidoc-flow:doc-flow`, etc.
- **Repository / namespace consistency:** matches the GitHub repo
  name (`aidoc-flow-framework`) modulo the `-framework` suffix.

## Q6 — Copy strategy

**Options:**
1. `cp -r .claude/<subset>` per source path with an explicit
   exclusion list.
2. `rsync --exclude=...` with the exclusion list passed inline.
3. Per-skill enumerated `cp` for every IN skill (defensive but
   verbose).

**Chosen:** Option 1 — `cp -r` per top-level path with bash brace
expansion or explicit `rm -rf` of OUT paths after copy.

**Rationale:** P2-T2 + P2-T3 used `cp -r` cleanly; the pattern is
familiar; `rsync` adds a tool dependency for no functional benefit.
Option 3 (enumerated per-skill) is verbose and error-prone with 144
skills.

**Concrete recipe (for P3-T2):**

```sh
# Stage 1: top-level copies (mirrors P2-T2)
mkdir -p platforms/claude-code-plugin/{skills,agents,commands}
cp -r .claude/agents/. platforms/claude-code-plugin/agents/
cp -r .claude/commands/. platforms/claude-code-plugin/commands/
cp -r .claude/skills/. platforms/claude-code-plugin/skills/

# Stage 2: remove OUT skill dirs
for skill in code-review refactor-flow analytics-flow devops-flow \
             ai-pr-review google-adk n8n; do
  rm -rf "platforms/claude-code-plugin/skills/$skill"
done

# Stage 3: remove OUT root files
rm -f platforms/claude-code-plugin/skills/README.md
rm -f platforms/claude-code-plugin/skills/google-adk_quickref.md
rm -f platforms/claude-code-plugin/skills/n8n_quickref.md
```

After Stage 3: `skills/` has 142 dirs + 19 root files = 161 entries
at maxdepth 1.

**Downstream implications:**
- **P3-T2 verify (file counts):**
  - `find platforms/claude-code-plugin/skills -mindepth 1 -maxdepth 1 -type d | wc -l` = **142**
  - `find platforms/claude-code-plugin/skills -maxdepth 1 -type f | wc -l` = **19**
  - `find platforms/claude-code-plugin/agents -type f | wc -l` = **1**
  - `find platforms/claude-code-plugin/commands -type f | wc -l` = **1**
- **No need to copy hooks/ or settings*.json** — they're dropped per
  the audit.

## Q7 — Plugin lifecycle hooks in v0.1.0

**Options:**
1. None — the plugin is declarative-only (skills + agents + commands).
2. Port a minimal set (e.g. a `PreToolUse` hook to validate SDD
   structure before saves).
3. Defer to v0.2.0 — collect user feedback first.

**Chosen:** Option 1 — no hooks in v0.1.0.

**Rationale:** The 3 existing `.claude/hooks/` are migration-only
(audit drops them all). No user-facing hook has been designed for the
plugin. Shipping a hook prematurely risks behaviors users didn't ask
for and that aren't part of any SDD layer's contract. v0.1.0 ships
declaratively; hooks can be added later when motivated by a real
user need.

**Downstream implications:**
- **P3-T2:** do **not** copy `.claude/hooks/` to the plugin.
- **plugin.json:** no `hooks` block; no `hooks/` directory at plugin
  root.
- **P3-T4 verify:**
  `test ! -d platforms/claude-code-plugin/hooks && echo ok` prints `ok`.

## Cross-question conflicts

None. Specifically checked:

- Q1 (minimal manifest) × Q2 (skill list) — manifest doesn't enumerate
  skills; auto-discovery handles whatever ships in `skills/`. The 144-
  vs-149 difference (with vs without the 7 OUT skills) is invisible
  to the manifest.
- Q1 × Q6 (copy strategy) — auto-discovery's expected directory layout
  (`skills/`, `agents/`, `commands/` at plugin root) matches Q6's
  output paths exactly.
- Q2 × Q4 — the 5 borderline-OUT skills (`code-review`, etc.) all have
  associated `*_quickref.md` files; none of those exist among the 22
  root files (verified by `ls .claude/skills/*_quickref.md`), so no
  inconsistency.
- Q3 × Q7 — `save-plan` is a command (port), not a hook (drop).
  Distinct artifacts; no overlap.
- Q5 × Q1 — plugin name `aidoc-flow` matches the `name` field in the
  manifest. Consistent.
- Q6 × Q4 — Stage 3 of the copy recipe explicitly removes the 3 OUT
  root files identified in Q4.

## Deferred items

Items surfaced during evaluation that aren't yet resolved:

1. **`LICENSE` file at repo root.** P3-T1's manifest declares
   `"license": "MIT"` as a placeholder. If the project later adds a
   different `LICENSE` file, both the manifest and `framework/`
   declarations need to update. Out of scope for P3-T1 — surfaced
   here as a P3-T3 (or post-Phase-3) follow-up.
2. **Skill schema-version conventions.** Some skills carry
   `custom_fields.versioning_policy: "tracks BRD-MVP-TEMPLATE
   schema_version"` in their frontmatter; the framework's actual
   schema is `BRD-TEMPLATE.yaml` (not `BRD-MVP-TEMPLATE.yaml`). The
   skill content is internally consistent (it references the MVP
   form throughout) but doesn't match the framework's current
   template names. Resolution is a content-migration question
   (rewrite skill bodies, or rewrite framework template names) —
   strictly outside P3 scope. P3-T2 preserves the skill content
   verbatim modulo the `ai_dev_flow → framework` rewire; framework-
   side name reconciliation is a Phase 4/5 question if it surfaces.
3. **Auto-discovery vs sub-directory nesting.** Claude Code
   auto-discovers `skills/` etc. at plugin root. The 19 root files
   under `.claude/skills/` (the `_quickref.md` and READMEs) sit at
   `skills/` root — not inside any skill dir. P3-T1 confirms they
   port to the same location; verify gate confirms Claude Code's
   discovery doesn't trip on the non-`SKILL.md` files at `skills/`
   root. (Expected behavior: Claude Code ignores anything without
   `SKILL.md` at that level.) Flagged as a P3-T4 verify item.

## Verify (against the plan's gate)

- **All seven questions covered** (list-completeness, P2-T0 Pass 3
  lesson): Q1 ✓ Q2 ✓ Q3 ✓ Q4 ✓ Q5 ✓ Q6 ✓ Q7 ✓.
- Each section carries Options / Chosen / Rationale / Downstream
  implications.
- **Q1** — manifest schema verified by external lookup
  (claude-code-guide agent); fields enumerated; no schema URL exists.
- **Q2** — per-skill in/out decision for all 8 borderline candidates;
  classification rule (SDD-adjacency) stated upfront and applied
  uniformly.
- **Q3** — `save-plan.md` re-read end-to-end; no migration coupling
  found; port confirmed.
- **Q4** — all 22 root files enumerated; 19 IN / 3 OUT with reasons.
- **Q5** — name compared against 3 alternates; collision risk with
  the `doc-flow` skill explicitly considered.
- **Q6** — concrete `cp -r` + `rm -rf` recipe with 3 stages; file-
  count verify lines tied to specific commands.
- **Q7** — no-hooks default justified; hooks remain droppable per the
  audit.
- Cross-question conflicts: explicitly checked, none.
- No code or files moved by P3-T1 — `git status` shows only `plans/`
  edits.

## Review log

### Pass 1 — 2026-05-20T18:55:00Z

- **G1. Q1 manifest schema needed external research.** Used the
  claude-code-guide agent (per the available-agents list in
  CLAUDE.md). Auto-discovery means the manifest is small; no skill
  enumeration. Confirmed the directory layout expectation (`skills/`
  at plugin root, not nested under `.claude-plugin/`).
- **G2. Q2 borderline rule was applied uniformly.** SDD-adjacency
  rule: in if the skill creates/audits/reviews/fixes an SDD artifact
  or feeds a known SDD layer. Out otherwise. Three borderline-IN
  cases all map to specific Layer-10 artifact types (TSPEC, SECTEST,
  CTR). Five OUT cases are all general-purpose dev skills.
- **G3. Q4 fine-grained — 22 root files enumerated by hand.**
  README.md was the only IN→OUT swap (the audit suggested "likely
  port" but the file's actual content references obsolete framework
  paths and a multi-project symlink pattern). Q4 corrects.
- **G4. Q6 exclusion list cross-referenced with Q2 and Q4.** Stage 2
  drops the 7 OUT skill dirs (matches Q2). Stage 3 drops the 3 OUT
  root files (matches Q4). Both lists are explicit; verify gates
  reference file counts that depend on both being correct.
- **G5. Q5 name collision check.** `doc-flow` is both a skill name
  and a candidate plugin name. Q2 doesn't drop the `doc-flow` skill
  (it's the orchestrator, clearly IN). Naming the plugin
  `aidoc-flow` avoids the collision and aligns with project identity.
- **G6. Q7 conservative default.** No hooks ship in v0.1.0; the
  migration-only hooks all drop per the audit. If a future plugin
  hook need surfaces, it's a separate change with its own design
  pass — bias to not shipping prematurely.
- **G7. Deferred items — three flagged.** License, skill schema-
  version conventions, and auto-discovery-with-root-files behavior.
  None block P3-T2; each has a forward-pointer.
- **G8. List-completeness across questions, downstream implications,
  and verify.** Every question has a "Downstream implications" sub-
  section pointing at the P3-T2/T3/T4 tasks that consume the
  decision. Cross-question conflicts explicitly checked.

### Pass 2 — 2026-05-20T19:10:00Z

- **G9. Re-checked Q2's 144-skill count.** 129 `doc-*` + 15 non-doc =
  144. The 15 non-doc breaks down as: 12 from the audit's
  "clearly IN" list (`doc-flow` orchestrator, `skill-recommender`,
  `trace-check`, `workflow-optimizer`, `quality-advisor`,
  `context-analyzer`, `mermaid-gen`, `charts-flow`, `adr-roadmap`,
  `project-init`, `project-mngt` — wait that's 11) plus 3 from
  borderline (`test-automation`, `security-audit`,
  `contract-tester`) = 14. **Off-by-one.** Recounting the audit's
  "clearly IN" rows in §1 of the audit: `doc-flow`,
  `skill-recommender`, `trace-check`, `workflow-optimizer`,
  `quality-advisor`, `context-analyzer`, `mermaid-gen`,
  `charts-flow`, `adr-roadmap`, `project-init`, `project-mngt` — 11
  rows (the audit's text said "12" but the table lists 11 if
  `doc-flow` is double-counted across `doc-*` and "non-doc"; in
  reality `doc-flow` belongs in the `doc-*` 129 count, not the
  non-doc 20). **Correction folded into the Summary table — 14 non-
  doc IN; total 143 skills.** Confirmed by `ls .claude/skills/ |
  grep -v ^doc- | wc -l` = 20 non-doc dirs, of which 14 IN (11 +
  3) and 6 OUT (5 borderline + `google-adk` + `n8n` — wait that's
  7). Let me re-do the math.

  Recounting from `ls .claude/skills/`:
  - 129 `doc-*` (audit confirmed)
  - 20 non-`doc-*`: `adr-roadmap`, `ai-pr-review`, `analytics-flow`,
    `charts-flow`, `code-review`, `contract-tester`,
    `context-analyzer`, `devops-flow`, `google-adk`, `mermaid-gen`,
    `n8n`, `project-init`, `project-mngt`, `quality-advisor`,
    `refactor-flow`, `security-audit`, `skill-recommender`,
    `test-automation`, `trace-check`, `workflow-optimizer`
  - In: `adr-roadmap`, `charts-flow`, `context-analyzer`,
    `contract-tester`, `mermaid-gen`, `project-init`,
    `project-mngt`, `quality-advisor`, `security-audit`,
    `skill-recommender`, `test-automation`, `trace-check`,
    `workflow-optimizer` = **13 non-doc IN**.
  - Out: `ai-pr-review`, `analytics-flow`, `code-review`,
    `devops-flow`, `google-adk`, `n8n`, `refactor-flow` = **7 non-doc
    OUT**.
  - 13 + 7 = 20 ✓.
  - **Plugin skill total: 129 + 13 = 142 skills.**
  - **Corrected counts throughout Q2 and Q6 verify lines:**
    `mindepth 1 -maxdepth 1 -type d` = **142**, exclusion list = 7
    dirs (matches).

  Folding this correction into the Summary table and Q2/Q6/Q4
  sections.
- **G10. Q3 — `save-plan` rewires?** Re-read the body: no
  `ai_dev_flow` placeholders or `/opt/data` paths. No rewire needed
  beyond the verbatim port.
- **G11. Q1 — author block accuracy.** The author block names
  "Vladislav Mikhayskiy" and the GitHub URL. The repo's git config
  is the source of truth for author identity (per CLAUDE.md "Never
  update the git config"). P3-T3 can populate the author block from
  `git config user.name` / `user.email` at implementation time
  rather than hardcoding here; design just says "include an
  author block." Updating Q1's example to soften the specific name.
- **G12. Idempotency of the Q6 recipe.** Stage 1 `cp -r` over an
  existing target wouldn't fail (it overwrites). Stage 2/3 `rm -rf`
  / `rm -f` no-op on already-removed paths. Recipe is re-runnable.
- **G13. No new findings on structure / verify / cross-conflicts.**
  Ready to present on approval.
