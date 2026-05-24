# P3-T3 Plan — Plugin scaffold

| Field      | Value                                |
|------------|--------------------------------------|
| Task       | P3-T3                                |
| Depends on | P3-T1 design, P3-T2 content port     |
| Status     | DONE — 2026-05-20T21:10:00Z          |
| Feeds      | P3-T4 (verify), P3-T5 (close)        |

## Objective

Scaffold the four files the plugin needs that `.claude/` didn't carry:
`.claude-plugin/plugin.json` (minimal manifest), `VERSION`,
`FRAMEWORK_SPEC_VERSION`, and an expanded `README.md` (replacing the
Phase 0 placeholder). After this task, `platforms/claude-code-plugin/`
is structurally complete and ready for the P3-T4 verify gate.

## Audit refresh — two findings from P3-T3 recon

### Finding 1 — git config identity mismatch (P3-T1 Q1 correction)

P3-T1 Q1 said "manifest author block populated from
`git config user.name` at P3-T3". Recon reveals the in-container git
config is `Claude / noreply@anthropic.com` — the agent session's
identity, not the repo owner's. Using these values would falsely
attribute the plugin to "Claude". **Correction:** omit the author
block entirely. The manifest's `repository` URL
(`https://github.com/vladm3105/aidoc-flow-framework`) already
identifies ownership.

### Finding 2 — Hermes has no platform-level `CHANGELOG.md`

Recon: `platforms/hermes/CHANGELOG.md` does not exist. P3-T1 Q-list
implicitly assumed CHANGELOG would be a P3-T3 deliverable (project-
level `CHANGELOG.md` prose mentions "each platform keeps its own
changelog at `platforms/<name>/CHANGELOG.md`"). Hermes departed
from that prose in P2-T3 without explicit decision; the precedent is
**no platform changelog**. Following Hermes' precedent here:
**skip `CHANGELOG.md` from P3-T3 scope**. If per-platform changelogs
land later, they retrofit symmetrically across both platforms (a
post-Phase-3 cleanup task).

Both corrections are minor adjustments to P3-T1 design, not design
reversals. Recorded here so the plan's scope is consistent with what
ships.

## Scope

**In:**

1. **`.claude-plugin/plugin.json`** — minimal manifest per P3-T1 Q1
   (minus the author block per Finding 1):

   ```json
   {
     "name": "aidoc-flow",
     "description": "AI-Driven Specification-Driven Development (SDD) workflow — skills, agents, and commands for the 8-layer doc flow (BRD → IPLAN). Consumes the aidoc-flow framework spec.",
     "version": "0.1.0",
     "license": "MIT",
     "repository": "https://github.com/vladm3105/aidoc-flow-framework",
     "homepage": "https://github.com/vladm3105/aidoc-flow-framework",
     "keywords": ["sdd", "spec-driven-development", "documentation", "brd", "prd", "ears", "bdd", "adr", "iplan"]
   }
   ```

2. **`VERSION`** — single line `0.1.0\n`. Mirrors `framework/VERSION`
   and `platforms/hermes/VERSION` byte-for-byte (6 bytes).
3. **`FRAMEWORK_SPEC_VERSION`** — single line `0.1.0\n`. Identical to
   `framework/VERSION` (verified by `diff` in P3-T4).
4. **`README.md`** — populated, replacing the Phase 0 placeholder.
   Mirror the structure of `platforms/hermes/README.md` (which is
   itself still the Phase-0-placeholder style as of P2-T5 — Hermes
   didn't expand its README either; that's a deferred symmetric task
   for both platforms). For P3-T3, write a usable plugin README that
   covers: what the plugin is, how to install it, how to use the
   skills, where to find the framework spec, version + spec-conformance
   declaration, and a pointer to the project's `ROADMAP.md` and
   `CHANGELOG.md`.

**Out:**

- `CHANGELOG.md` — per Finding 2, skip to match Hermes precedent.
- Hooks — P3-T1 Q7 decided no hooks in v0.1.0.
- Author block — per Finding 1.
- License file at repo root — P3-T1 §Deferred R1 flagged this as a
  follow-up; not in P3-T3 scope. Manifest declares `"license": "MIT"`
  as a placeholder string; project-level `LICENSE` file is a separate
  add.
- Any modification to `skills/`, `agents/`, `commands/` content —
  P3-T2 is the content port; T3 only adds new top-level files.
- Any modification to other platforms or `framework/`.

## Approach

### 1. Create `.claude-plugin/plugin.json`

```sh
mkdir -p platforms/claude-code-plugin/.claude-plugin
# write file via Write tool with the JSON body above
```

Validate by parsing:

```sh
python -m json.tool < platforms/claude-code-plugin/.claude-plugin/plugin.json > /dev/null && echo "ok: valid JSON"
```

### 2. Write the two VERSION files

```sh
echo "0.1.0" > platforms/claude-code-plugin/VERSION
echo "0.1.0" > platforms/claude-code-plugin/FRAMEWORK_SPEC_VERSION
```

Both files: 6 bytes (`0.1.0\n`). Match `framework/VERSION` exactly.

### 3. Replace `README.md` with a populated version

Structure mirrors Hermes' README skeleton but with substantive
content (Hermes' README is itself still placeholder-style; both will
be expanded symmetrically at a later cleanup task, or the plugin's
expanded README sets a precedent for a Hermes follow-up).

The new README covers:

- One-paragraph what-this-is
- Install via Claude Code's plugin manager
- Use — quick-start invocation patterns (`/aidoc-flow:doc-brd-autopilot`,
  `/aidoc-flow:doc-flow`, etc.)
- Skill catalogue summary (8 layers + meta + non-doc)
- Conformance: declares framework spec version; points at the shared
  conformance suite
- The `field | value` info table (matches Hermes' format)
- Pointers to ROADMAP, CHANGELOG (project-level), framework spec

## Step sequence

1. **Create the `.claude-plugin/` directory** and write `plugin.json`.
2. **Validate the JSON** via `python -m json.tool`.
3. **Write `VERSION` and `FRAMEWORK_SPEC_VERSION`** as single-line
   `0.1.0\n` files.
4. **Replace `README.md`** with the populated content (Write tool —
   it already exists, must Read first).
5. **Verify** (see below).
6. **Land** — single commit
   `feat(plugin): scaffold .claude-plugin/plugin.json + VERSION files + populated README (P3-T3)`;
   update `plans/HANDOFF.md`; tick P3-T3 in
   `plans/MIGRATION_TODO.md`. Push.

## Verification

- **V1. Manifest exists and is valid JSON:**
  `python -m json.tool < platforms/claude-code-plugin/.claude-plugin/plugin.json > /dev/null`
  exits 0.
- **V2. Manifest field set:** the keys are exactly `{name, description,
  version, license, repository, homepage, keywords}` — no `author`,
  no superfluous fields. `python -c "import json; d=json.load(open('platforms/claude-code-plugin/.claude-plugin/plugin.json')); print(sorted(d.keys()))"`
  prints the expected list.
- **V3. Manifest name == plugin identity:** `name` field is
  `"aidoc-flow"` (matches P3-T1 Q5).
- **V4. Manifest version matches VERSION file:** `name field == "0.1.0"
  == cat VERSION`.
- **V5. VERSION + FRAMEWORK_SPEC_VERSION are correct:**
  - `cat platforms/claude-code-plugin/VERSION` prints `0.1.0`.
  - `diff platforms/claude-code-plugin/FRAMEWORK_SPEC_VERSION framework/VERSION`
    prints nothing.
  - Both files are 6 bytes:
    `wc -c platforms/claude-code-plugin/{VERSION,FRAMEWORK_SPEC_VERSION}`
    reports 6 each.
- **V6. README is populated (not placeholder):**
  - `grep -c 'PLACEHOLDER' platforms/claude-code-plugin/README.md` returns 0.
  - `wc -l platforms/claude-code-plugin/README.md` > 30 (placeholder was 30 lines; expanded version substantially longer).
- **V7. Top-level structure complete:**
  `ls platforms/claude-code-plugin/` lists exactly:
  `.claude-plugin`, `FRAMEWORK_SPEC_VERSION`, `README.md`, `VERSION`,
  `agents`, `commands`, `skills`. (7 entries; no `CHANGELOG.md`, no
  `hooks/`.)
- **V8. No code changes outside plugin:**
  `git diff --stat HEAD -- framework/ platforms/hermes/` empty.
- **V9. Conformance suite still 25/25** (sanity).
- **V10. Plugin still has the P3-T2 content intact:**
  - `find platforms/claude-code-plugin/skills -mindepth 1 -maxdepth 1 -type d | wc -l` = 142.
  - `find platforms/claude-code-plugin/skills -maxdepth 1 -type f | wc -l` = 19.
  - `grep -rE '\bai_dev_flow\b' platforms/claude-code-plugin/` returns 0 (Step §2 doesn't re-introduce coupling).

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Manifest JSON is syntactically invalid (trailing comma, unquoted key). | V1 verify gate parses the file with `python -m json.tool`; fails fast on syntax errors. |
| R2 | `name` field collides with another Claude Code plugin in a user's setup. | `aidoc-flow` was chosen specifically to be unique (P3-T1 Q5). No collision in this repo; collision in a user's setup is the user's choice to resolve. |
| R3 | Auto-discovery doesn't see the skills because the manifest claims a `name` that doesn't match the directory. | Claude Code's auto-discovery uses the file path (`skills/<name>/SKILL.md`), not the plugin's manifest name. Confirmed via claude-code-guide agent during P3-T1. |
| R4 | `VERSION` files contain a `v` prefix (against convention). | `echo "0.1.0"` writes `0.1.0\n` without prefix. Matches `framework/VERSION` and `platforms/hermes/VERSION` (D-0006, D-0009 convention). |
| R5 | README expansion sneaks in claims about features that aren't actually shipped (e.g. lifecycle hooks, CLI commands beyond the one `save-plan`). | README is reviewed against the actual plugin content during writing: 144 skills, 1 agent, 1 command, no hooks. Anything beyond gets cut. |
| R6 | README references a `LICENSE` file at repo root that doesn't exist. | Don't link to a missing file. Mention "MIT" in the README info table but no link. P3-T1 §Deferred R1 tracks the LICENSE work item. |
| R7 | The "Hermes precedent" for no platform CHANGELOG is itself a Phase 2 oversight; ideally both platforms would have one. | Acknowledged in Finding 2. Following the precedent for symmetry; a future cleanup task can retrofit both platforms together. |
| R8 | `git config user.name` returning `Claude` was unexpected. The P3-T1 design implicitly assumed it would return the repo owner. | Finding 1 documents the correction (omit author block). The misuse risk is real for any future task that templates on git config — flag in the lesson section. |

## Review log

### Pass 1 — 2026-05-20T20:50:00Z

- **G1. Author block correction (Finding 1).** P3-T1 said
  "populated from `git config user.name` at P3-T3"; recon shows the
  in-container config is the session's identity (`Claude`), not the
  repo owner. Omitting the author block is the cleanest fix and
  consistent with the Hermes pyproject precedent (Hermes ships no
  `[project.authors]` either). Manifest stays minimal.
- **G2. CHANGELOG correction (Finding 2).** Hermes has no platform-
  level changelog despite the project-level prose suggesting one.
  Following the precedent for symmetry. If/when CHANGELOG retrofits
  arrive, they happen for both platforms together.
- **G3. README expansion — but not over-expansion.** R5 sets the
  guardrail: don't claim features the plugin doesn't ship. The README
  describes what auto-discovery makes available (144 skills,
  1 agent, 1 command), not aspirational state.
- **G4. Manifest field-set verify (V2).** Set-membership over field
  count — catches both missing fields and superfluous fields. P2-T3
  / P2-T8 G13 lesson applies here.
- **G5. License-file deferral (R6).** No `LICENSE` at repo root; the
  manifest declares `"license": "MIT"` as a placeholder. The README
  mentions "MIT" but does NOT link to a missing file. P3-T1
  §Deferred R1 tracks the work item.
- **G6. Symmetry with Hermes top-level structure.** Plugin top will
  carry: `VERSION`, `FRAMEWORK_SPEC_VERSION`, `README.md`,
  `.claude-plugin/`, plus `skills/`, `agents/`, `commands/`. Hermes
  top carries: `VERSION`, `FRAMEWORK_SPEC_VERSION`, `README.md`,
  `pyproject.toml`, plus `src/`, `tests/`, `docs/`, `examples/`,
  `prompts/`, `skills/`, `agents/` (via `agent-skills/`). Different
  shapes per platform; common parts match (V7).
- **G7. The `.claude-plugin/` directory exists only after this task.**
  Currently absent. Step 1 creates it; verify gate (V7) confirms its
  presence.
- **G8. Conformance suite sanity (V9).** No expected change — the
  suite scans only `framework/`. Run for hygiene.
- **G9. List-completeness for V7.** The 7 expected entries match
  P3-T1 Q5/Q6 expectations exactly. The 22-entry `git ls-tree` view
  would include the nested `.claude-plugin/plugin.json`; V7 uses
  `ls -la` at the platform top, so only the 7 top-level entries.

### Pass 2 — 2026-05-20T21:00:00Z

- **G10. R8 - `git config user.name` returning `Claude` is a
  recurring failure mode.** P3-T1 design assumed it would yield the
  repo owner. Future tasks templating on git config should check the
  value first rather than blind-trusting it. **Lesson:** templated
  identity fields need a sanity check against the repo URL/owner.
  Not a P3-T3 fix; a process note for future plan-writing.
- **G11. README structure — what to actually include?** Drafted the
  outline in §Approach.3. Re-reading Hermes' README placeholder: it
  carries only the info table + the 4-bullet target layout. Hermes'
  README is itself underbaked. P3-T3 will write a more substantive
  plugin README; if it sets a useful precedent, a follow-up can
  expand Hermes' README symmetrically. Recorded in R7 as the
  symmetry-cleanup work item.
- **G12. Idempotency.** Step 1 creates `.claude-plugin/`; second run
  would `mkdir -p` no-op. Step 2 truncates the VERSION files
  (`echo > file` overwrites); content is identical, so re-runnable.
  Step 4 (README replace) similar — Write tool overwrites; no
  partial state.
- **G13. JSON validation via `python -m json.tool`.** Standard library,
  available in any Python 3+. No `jq` dependency needed.
- **G14. No new findings.** Plan is internally consistent. Ready to
  present on approval.

## Implementation note (2026-05-20T21:10:00Z)

Executed. All 11 verify gates green (V7 needed `ls -A` to include the
hidden `.claude-plugin/` directory — minor implementation correction,
not a substantive issue).

- **V1 JSON validity:** `python -m json.tool` parses without error.
- **V2 field set:** exactly `['description', 'homepage', 'keywords',
  'license', 'name', 'repository', 'version']` — no `author`, no
  superfluous fields, matches the Q1+Finding 1 design.
- **V3 manifest name:** `"aidoc-flow"`.
- **V4 manifest version == VERSION file:** both `0.1.0`.
- **V5 VERSION + FRAMEWORK_SPEC_VERSION:** both 6 bytes (`0.1.0\n`);
  `diff platforms/claude-code-plugin/FRAMEWORK_SPEC_VERSION
  framework/VERSION` prints nothing (identical).
- **V6 README populated:** 82 lines (placeholder was 27), zero
  `PLACEHOLDER` markers.
- **V7 top-level structure (`ls -A`):** exactly 7 entries —
  `.claude-plugin`, `FRAMEWORK_SPEC_VERSION`, `README.md`, `VERSION`,
  `agents`, `commands`, `skills`. No `CHANGELOG.md`, no `hooks/`.
- **V8 no code changes outside plugin:** empty diff.
- **V9 conformance suite:** 25/25.
- **V10 plugin content intact:** 142 skill dirs, 19 root files, 0
  `ai_dev_flow` hits.
- **V11 manifest visual sanity:** content matches Q1's design
  verbatim modulo Finding 1 (omitted author block).

The README is substantially expanded from the placeholder (27 → 82
lines) and covers: what's inside (table of skills/agents/commands
with counts), install pointer, use (slash-prefix invocation
examples), framework spec conformance with VERSION cat output, the
platform info table, and the relationship to the Hermes platform.

Hermes' own README is still in the Phase-0-placeholder style (27
lines, no real user-facing content). P3-T3 sets a precedent for a
substantive platform README; a future symmetry task can expand
Hermes' README using P3-T3's structure. Flagged as a post-Phase-3
cleanup item (Risk R7).
