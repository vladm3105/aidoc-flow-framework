# Phase 3 Audit — Claude Code plugin

| Field      | Value                                |
|------------|--------------------------------------|
| Audit of   | `.claude/` (repo root)               |
| Target     | `platforms/claude-code-plugin/`      |
| Produced by| P3-T0                                |
| Date       | 2026-05-20T18:00:00Z                 |

## Summary

Phase 3's source is **`.claude/` at the repo root** — the active skill
loader the in-container session uses today. 191 files total: 149
skills (129 `doc-*` + 20 non-doc), 1 agent, 1 command, 3 hooks,
2 settings files. Per `docs/REPO_STRUCTURE.md`, `.claude/` ports to
`platforms/claude-code-plugin/` in Phase 3 but **stays at root until
Phase 5 cutover** — root is active for migration, the plugin is the
user-facing distribution. The decision is therefore **copy + divergence**:
root stays in dev-time service, plugin gets a curated user-facing
subset.

Framework coupling is **modest, single-class, and uniform**: 30 files
carry `{project_root}/ai_dev_flow/...` placeholder paths that reference
the framework dir under its **old** name. They all need a uniform
sed-rewrite (`ai_dev_flow` → `framework`). No `ucx_flow_v3` / `ucx_hermes`
hits — the skills were never coupled to Hermes.

`legacy/mcp_ucx`-style predecessor noise doesn't exist here. Phase 3 is
simpler in shape than Phase 2 (estimated 5 tasks vs the 9 P2 needed).

## 1. Inventory

### `.claude/` — 191 files

```
.claude/
├── settings.json           1 file  (dev-time hooks config — drop from plugin)
├── settings.local.json     1 file  (dev-time, gitignored — drop)
├── agents/                 1 file  (requirements-analyst.md)
├── commands/               1 file  (save-plan.md)
├── hooks/                  3 files (migration hooks — drop from plugin)
└── skills/               184 files (149 skill dirs + 22 root files + 13 misc)
    ├── doc-*/            129 skill dirs (the doc workflow engine)
    ├── (non-doc)/         20 skill dirs (mixed scope)
    └── (root files)       22 files (READMEs + *_quickref.md)
```

### `.claude/skills/` breakdown

**129 `doc-*` skills** — the SDD workflow engine, organized by SDD layer:

- **Layer 1–8 artifact skills** (8 × ~6 variants each: `doc-<X>`,
  `doc-<X>-audit`, `doc-<X>-autopilot`, `doc-<X>-fixer`,
  `doc-<X>-reviewer`, `doc-<X>-validator`) across BRD, PRD, EARS,
  BDD, ADR, SYS, REQ, SPEC (= 48 skills approx).
- **Subtype skills** for SPEC subtypes (CSPEC, DSPEC, UXSPEC, RISKSPEC,
  PROCSPEC) and TSPEC subtypes (UTEST, ITEST, STEST, FTEST, PTEST,
  SECTEST) — each with the same variant set.
- **Orchestrator skills** — `doc-flow` (the workflow orchestrator),
  `doc-naming`, `doc-validator`, `doc-review`, `doc-ref`.
- **CTR / TSPEC / TASKS** — the cross-layer artifact skills.

**20 non-`doc-*` skills** — mixed scope; per-skill in/out judgement
deferred to P3-T1:

| Skill | Initial classification |
|-------|------------------------|
| `doc-flow` (already counted above) | core orchestrator — IN |
| `skill-recommender` | recommends doc-* skills — IN |
| `trace-check` | traces SDD artifacts — IN |
| `workflow-optimizer` | optimizes doc-flow sequence — IN |
| `quality-advisor` | quality monitor for SDD — IN |
| `context-analyzer` | analyzes project for SDD setup — IN |
| `mermaid-gen` | generates diagrams referenced by SDD — IN |
| `charts-flow` | mermaid architecture diagrams — IN |
| `adr-roadmap` | ADR-based phased roadmaps — IN |
| `project-init` | initialize SDD projects — IN |
| `project-mngt` | PM artifacts atop SDD — IN |
| `code-review` | code review skill — borderline (used by SDD?) |
| `refactor-flow` | code refactor — borderline |
| `test-automation` | test plans — borderline (TSPEC-adjacent) |
| `security-audit` | security review — borderline |
| `contract-tester` | API contract testing — borderline (CTR-adjacent) |
| `analytics-flow` | data analysis workflow — borderline |
| `devops-flow` | devops practices — borderline |
| `ai-pr-review` | AI PR review — borderline |
| `google-adk` | Google ADK dev — likely OUT (vendor-specific) |
| `n8n` | n8n automation — likely OUT (unrelated to SDD) |

12 "IN" + 6 "borderline" + 2 "OUT" — final calls in P3-T1.

**22 root files under `.claude/skills/`** — sit outside any skill
directory. Mostly `*_quickref.md` quick-reference docs and umbrella
READMEs (`doc-brd-skills-readme.md` etc.). Initial read: **port-with-
repoint** (the same `ai_dev_flow` placeholder issue), pending P3-T1
confirmation they're skill-scope (not just dev-time scaffolding).

### `.claude/agents/` and `.claude/commands/`

| File | Class | Notes |
|------|-------|-------|
| `agents/requirements-analyst.md` | port-verbatim | SDD requirements agent — clearly plugin-scope. |
| `commands/save-plan.md` | needs P3-T1 review | A "save current plan" command; may be dev-time-only (this migration uses plans/), or user-facing for SDD plan capture. |

### `.claude/hooks/`

| Hook | Class | Notes |
|------|-------|-------|
| `plan-review-gate.sh` | **drop** | Migration-only: warns when a staged `plans/PX-T*.md` file has < 2 review passes. Tied to the development workflow, not user-facing SDD. |
| `pre-compact-snapshot.sh` | **drop** | Migration-only: snapshots pre-compaction state on the working branch. |
| `session-start-handoff.sh` | **drop** | Migration-only: injects `plans/HANDOFF.md` at session start. |

All three are *this project's* dev-time hooks, not Claude Code plugin
lifecycle hooks. Shipping them in the plugin would force users into
the migration's review/handoff discipline. **Drop wholesale**; if the
plugin needs its own hooks later, they're a separate add.

### `.claude/settings*.json`

| File | Class | Notes |
|------|-------|-------|
| `settings.json` | **drop** | Configures the migration `plan-review-gate.sh` hook + tool allowlist for the in-container session. Not plugin runtime. |
| `settings.local.json` | **drop** | `gitignore`d local overrides. Not in the repo. |

## 2. Relationship — `.claude/` (root) ↔ `platforms/claude-code-plugin/` (target)

`.claude/` at the repo root is the **active loader** Claude Code reads
when running this in-container session. Removing or moving it during
P3 would break the session's own skill set mid-flight. The plugin
target at `platforms/claude-code-plugin/` is the **user-facing
distribution** that ships independently.

The two trees serve different roles and have different lifetimes:

| | Root `.claude/` | Plugin target |
|---|----------------|---------------|
| Audience | Dev session (this migration) | End users / installers |
| Active until | Phase 5 cutover | Indefinite |
| Scope | Whatever the migration session needs | Curated, user-facing |
| Hooks | Migration hygiene | Plugin lifecycle (if any) |
| Settings | Dev-time tool allowlist | Manifest-driven |

**Decision: copy-with-divergence.** P3 copies the in-scope subset
from `.claude/` to `platforms/claude-code-plugin/` (skills, agents,
in-scope commands). Root `.claude/` stays as-is, scoped to the
migration. At Phase 5 cutover, root `.claude/` is removed; the plugin
becomes the single source.

No sync mechanism is needed during Phase 3+4 — the plugin diverges
from root at the moment of copy, and any updates to a skill the user
wants in both places are made twice (a Phase-5 problem, not a
Phase-3 problem). The Phase-2 lesson (D-0013, single-source-of-truth)
applies here once Phase 5 removes the duplication.

## 3. Framework coupling

A fresh grep of `.claude/` enumerates the entire coupling surface:

| Pattern | Files with hit | Class |
|---------|---------------:|-------|
| `ucx_flow\|UCX_FLOW\|ucx_hermes` | **0** | — |
| `ai_dev_flow` (placeholder) | **30** | **rewire** — current-behavior reference to the framework dir under its old name |
| `/opt/data` (excluding `/opt/data/ucx_framework`) | **3** | preserve (G13 illustration paths in tutorials) |
| `/opt/data/ucx_framework` | **1** (`project-mngt/SKILL.md`) | **rewire** — current-behavior reference; map to repo-relative `framework/` |
| `{project_root}` placeholder | 17 | mostly co-occur with `ai_dev_flow` — same rewire pass |
| `framework/layers\|framework/registry\|framework/governance` | **0** | — (skills don't reference framework by its new name yet) |

### 3a. The `ai_dev_flow` rewire (30 files)

Examples from `doc-brd-skills-readme.md`:

```
- [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md]({project_root}/ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md)
- [ID_NAMING_STANDARDS.md]({project_root}/ai_dev_flow/ID_NAMING_STANDARDS.md)
- [ADR-TEMPLATE.md]({project_root}/ai_dev_flow/ADR/ADR-TEMPLATE.md)
```

These all reference files now under `framework/` in the new layout
(`framework/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md`,
`framework/governance/ID_NAMING_STANDARDS.md`,
`framework/layers/05_ADR/ADR-TEMPLATE.yaml`, etc.).

Rewire shape — uniform word-boundary regex (P2-T7 G12 lesson):

```
sed -i -E 's/\bai_dev_flow\b/framework/g' <30 files>
```

After the sed, some references will need sub-path adjustments
(`framework/ID_NAMING_STANDARDS.md` → `framework/governance/ID_NAMING_STANDARDS.md`)
analogous to P2-T3's follow-up edits. The 30-file set + the
sub-path map is P3-T2 implementation work; the audit's job is to
flag the size and shape.

### 3b. The `/opt/data/ucx_framework` rewire (1 file)

`project-mngt/SKILL.md:46` reads:

```
`/opt/data/ucx_framework/ai_dev_flow/ID_NAMING_STANDARDS.md`
```

This is a **current-behavior framework reference** (not an illustration
of a user's local path), per the same logic that P2-T7 used for
`/opt/data/ucx_framework/...` lines. Rewire to repo-relative
`framework/governance/ID_NAMING_STANDARDS.md`.

### 3c. The 3 illustration `/opt/data/...` paths (preserve)

| File | Path | Why preserve |
|------|------|--------------|
| `doc-req-autopilot/SKILL.md:312` | `/opt/data/trading_nexus_v4.2/.../docs/07_REQ/REQ-01_f1_iam/` | Tutorial reference to a user's local project. |
| `project-init/SKILL.md:149` | `/opt/data/my_project` | User-project placeholder. |
| `project-mngt/SKILL.md:46` | `/opt/data/ucx_framework/ai_dev_flow/ID_NAMING_STANDARDS.md` | (this is the §3b rewire — counted there, not here) |

Net: 2 illustration paths preserved verbatim per G13.

### Verify gate for P3-T2

After the port + rewires:

- `grep -rE 'ucx_flow|UCX_FLOW|ucx_hermes' platforms/claude-code-plugin/` returns **zero**.
- `grep -rE '\bai_dev_flow\b' platforms/claude-code-plugin/` returns **zero**.
- `/opt/data/ucx_framework` returns zero.
- `/opt/data` returns hits only in the 2 illustration files
  (set-membership check).

## 4. Conformance gap

The current 25-test conformance suite at `tests/conformance/` scans
**only `framework/`** (P2-T0 confirmed this). It makes no assertion
about platforms — same conformance gap as Hermes faced in Phase 2.

Phase 3's obligations against the suite:

1. **Do not modify `framework/`.** Structural; the plugin lives under
   `platforms/claude-code-plugin/`.
2. **Declare `framework_spec_version`** per D-0009 / P2-T1 Q2.
   Mechanism: two plain-text VERSION files at platform top —
   `platforms/claude-code-plugin/VERSION` (`0.1.0`) and
   `platforms/claude-code-plugin/FRAMEWORK_SPEC_VERSION` (matching
   `framework/VERSION`). Identical to Hermes' P2-T3 mechanism.
3. **Pass the suite** — automatic, since the platform doesn't modify
   `framework/`.

Platform-level conformance checks ("every `platforms/<name>/`
declares `framework_spec_version`", "no platform writes to
`framework/`", "every plugin skill references a known framework
layer") are still Phase 4 work.

## 5. Classification matrix

Top-level paths under `.claude/`:

| Path | Files | Class | Note |
|------|------:|-------|------|
| `agents/requirements-analyst.md` | 1 | **port-verbatim** | Plugin-scope SDD agent. |
| `commands/save-plan.md` | 1 | **defer to P3-T1** | Borderline dev-time vs user-facing. |
| `hooks/plan-review-gate.sh` | 1 | **drop** | Migration-only dev-time hook. |
| `hooks/pre-compact-snapshot.sh` | 1 | **drop** | Migration-only. |
| `hooks/session-start-handoff.sh` | 1 | **drop** | Migration-only. |
| `settings.json` | 1 | **drop** | Migration tool allowlist. |
| `settings.local.json` | 1 | **drop** | Gitignored local overrides. |
| `skills/doc-*` | 129 dirs | **port-with-repoint** | Core engine; ~30 files of the 184 carry `ai_dev_flow` placeholders to rewire. |
| `skills/<non-doc>` | 20 dirs | **defer to P3-T1** | Per-skill in/out per §1 initial classification. |
| `skills/*.md` (22 root files) | 22 | **port-with-repoint (likely)** | `_quickref.md` + READMEs; same coupling rewire as the doc-* skills. |
| **— plugin-side adds —** | | | |
| `.claude-plugin/plugin.json` | 1 | **add** | Plugin manifest. Schema TBD by P3-T1. |
| `VERSION` | 1 | **add** | Initial `0.1.0` per `docs/TAGGING.md`. |
| `FRAMEWORK_SPEC_VERSION` | 1 | **add** | `0.1.0` matching `framework/VERSION`. |
| `CHANGELOG.md` | 1 | **add** | Platform changelog; first entry at P3-T5 close. |
| `README.md` | 1 | **expand** | Already exists as placeholder; expand at P3-T3. |

**Coverage check:** every top-level `.claude/` path appears above
plus 5 plugin-side adds. The 22 root files under `.claude/skills/`
are explicitly accounted for (avoiding the P2-T0 §5b miss).

## 6. Open questions (for P3-T1 design)

1. **Plugin manifest schema.** `.claude-plugin/plugin.json` is the
   user-facing manifest, but its required schema isn't documented in
   the repo. P3-T1 must consult Claude Code's external plugin docs
   and define the minimal required fields (name, version,
   description, dependencies, skill/agent registration). May need
   web research.

2. **Non-doc-skill scope.** The 20 non-`doc-*` skills split into
   "clearly IN" (12), "borderline" (6), "OUT" (2). Resolve each
   borderline case: `code-review`, `refactor-flow`, `test-automation`,
   `security-audit`, `contract-tester`, `analytics-flow`,
   `devops-flow`, `ai-pr-review`. Criteria: does the skill participate
   in the SDD workflow or is it general-purpose? P3-T1 lists each
   with a chosen disposition.

3. **`save-plan` command.** Port to plugin (user-facing "save my SDD
   plan" command) or drop (migration-only `plans/` workflow)?
   Read the command's body to decide.

4. **22 root files under `.claude/skills/`.** `*_quickref.md` + the
   umbrella READMEs — are these plugin scope (loaded as skill
   index docs) or `.claude/`-internal dev scaffolding? P3-T1 confirms.

5. **Plugin name in the manifest.** `aidoc-flow` (matches project),
   `aidoc-flow-doc-skills`, `doc-flow` (matches the orchestrator
   skill), or a new name? Affects the user's install command.

6. **Copy strategy.** Single-pass `cp -r` from `.claude/<subset>` →
   `platforms/claude-code-plugin/<subset>`, or a more selective
   per-skill copy? Bias to `cp -r` per the P2-T2 pattern.

7. **Plugin lifecycle hooks.** Will the plugin ship any hooks of its
   own (separate from the dropped migration hooks), or is it
   declarative-only (skills + agents + commands)? Default: no hooks
   in the initial release.

## 7. Verify (against the plan's gate)

- All 191 files in `.claude/` classified across §5; 22 root files
  in `.claude/skills/` enumerated separately to avoid the P2-T0 §5b
  miss.
- `.claude/` ↔ plugin relationship named: **copy with divergence**,
  root stays until Phase 5.
- Framework-coupling list complete — 1 class (`ai_dev_flow`
  placeholder), 30 files, uniform rewire shape; 1 outlier file with
  `/opt/data/ucx_framework`; 2 illustration paths preserved per G13.
- Conformance gap stated identically to Hermes' — D-0009 mechanism
  (two VERSION files), no `framework/` change.
- Open questions list ≥ 5 (canonical Phase-N count).
- No code or files moved by this audit — `git status` shows only
  `plans/` edits.
