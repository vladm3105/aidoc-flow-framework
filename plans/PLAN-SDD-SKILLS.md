# SDD Layer + CHG Skillset — Plan

Closes #1032. Adds 13 engine-agnostic skills under `framework/skills/sdd-*`
(8 layer, 2 bridge, 3 governance) plus registry/readme index updates.

## Goal

Give every SDD layer (01–10) and the CHG governance surface a dispatchable,
engine-agnostic agent skill, closing the gap where templates and linters exist
but no skill routes an agent to them.

## Out of scope

- Existing 12 `framework/skills/` skills, `_shared/`, `.agents/skills/` ports: untouched.
- Private canon (`agents-skills-config`): untouched.
- One-line backlog: `sdd-eval` deep gate wiring; per-engine native mirrors.

## Approach

Build in `framework/skills/sdd-*` (`aidoc/skills/` resolves there via the
`aidoc -> framework` symlink; no folder creation needed). Each `SKILL.md` is
thin — trigger, inputs (layer `*-TEMPLATE.yaml` + `*-00_index`), steps
(author → lint → gate), next-skill handoff — using `<skills-root>` paths and
no engine names. Registry + readme index update in the same PR that adds the
skills. Vehicle DIR2C/F2/C1. Publish split: plan PR, then skills PR A
(governance+bridge, 5 skills), then skills PR B (layers, 8 skills).

## Steps

1. Live-validate + file issue (done: #1032, triage note posted, labels set).
2. Worktree `../aidoc-framework-1032`, branch `feature/1032-sdd-skills` (done).
3. This plan file → two review passes → plan PR → merge before any skill.
4. Complete the §3.4 checklist BEFORE writing the CHG. Then write the C1 CHG
   (no code steps, non-empty `decision:`, lifecycle attribution with `author`
   - `chg_ref`, `change_source: direct`, `sdd_lifecycle: []`) and run §3.4.1
   validation AFTER writing it, BEFORE committing. DIR2C/F2 is the vehicle:
   skills + registry/readme are docs/tooling with no product-behavior change,
   matching the DIR2C trigger row; SEED2C/SDD2C are rejected because no SDD
   cascade or new product chain is involved. Then write one scoped IPLAN
   (full 13-skill + registry + readme `file_manifest`, rollback, covering
   verification commands). `chg_lint` green. Version-bump protocol
   (GATE-SPEC-E005): (1) bump `framework/VERSION` to the next MINOR,
   (2) append the prior version to `OLD_VERSIONS` in
   `hooks/sync-version-refs.sh`, (3) run `bash hooks/sync-version-refs.sh`,
   (4) `ruff format` any touched Python, (5) verify via
   `python3 tests/chg/spec_gate.py --base origin/dev`. The CHG + IPLAN ride
   PR A; PR B is rebased onto merged A and references the same IPLAN for its
   file subset.
5. PR A: `sdd-chg-flow`, `sdd-chg-author`, `sdd-chg-triage`, `sdd-iplan`,
   `sdd-gates` + registry/readme.
6. PR B: `sdd-brd`, `sdd-prd`, `sdd-ears`, `sdd-bdd`, `sdd-adr`, `sdd-spec`,
   `sdd-tdd`, `sdd-eval` + registry/readme.
7. Watch checks per PR (`--required --watch`, CLEAN on current `headRefOid`);
   squash-merge; worktree remove BEFORE branch delete. Every push carries the
   OPS-0065 audit-trail phrase; never `--no-verify`; never push `main`. Run
   `bash framework/skills/_shared/scripts/check-skill-shadowing.sh` for the
   13 new names in each skills PR, and `check_plan.py` on this plan file in
   the plan PR.

## Claim ledger

| # | Claim | Symbol | Citation |
| --- | --- | --- | --- |
| 1 | Registry is the single owner of the skill list; `name` must match dir | `SKILL.md frontmatter` | framework/skills/SKILLS-REGISTRY.yaml:2 |
| 2 | Registry currently at version 1.0 / framework 0.96.14 | `version: "1.0"` | framework/skills/SKILLS-REGISTRY.yaml:3 |
| 3 | DIR2C = IPLAN→Code/Docs, `direct`, C1 CHG + scoped IPLAN, `sdd_lifecycle: []` | `DIR2C` | framework/governance/CHG_REQUEST_FLOWS.md:53 |
| 4 | DIR2C legacy alias is F2 | `DIR2C` $\leftrightarrow$ F2 | framework/governance/CHG_REQUEST_FLOWS.md:56 |
| 5 | Never push directly to `main`; changes via `dev` | `dev` | AGENTS.md:98 |
| 6 | Plans get two review cycles before the plan PR opens | `## Review log` | AGENTS.md:114 |
| 7 | Implementation begins only after the plan PR is merged | `plan PR` | AGENTS.md:117 |
| 8 | Push must carry the OPS-0065 audit-trail phrase | `Multi-agent self-review` | AGENTS.md:204 |
| 9 | `<skills-root>` is the `framework/skills/` directory | `<skills-root>` | framework/skills/README.md:30 |
| 10 | Layer chain is BRD→…→IPLAN→[Code]→EVAL | `01_BRD → 02_PRD` | framework/layers/README.md:21 |
| 11 | Layer 01 owns strategic business objectives | `01_BRD/` | framework/layers/README.md:28 |
| 12 | EVAL workflow standard exists for layer 10 | `# EVAL Workflow` | framework/layers/10_EVAL/EVAL_WORKFLOW_STANDARD.md:1 |
| 13 | `framework/VERSION` currently holds 0.96.14 | `0.96.14` | framework/VERSION:1 |
| 14 | Registry tracks `framework_version: "0.96.14"` | `framework_version: "0.96.14"` | framework/skills/SKILLS-REGISTRY.yaml:4 |

## Review log

### Pass 1: 2026-10-25T20:40:00Z (author self-validation)

- All 13 ledger citations verified against the live tree at `dev 21a46e7d6`.
- Destination corrected to `framework/skills/sdd-*` (review gap 1: earlier draft targeted `.agents/skills/`).
- Registry + readme updates added to PR A/B scope (review gap 2).
- Version-bump protocol defaulted to run (review gap 4).

### Pass 2: 2026-10-25T21:04:54Z (independent adversarial review)

- Independent read-only review (fresh-context subagent, 11 findings, verdict was FINDINGS ABOVE). Each finding re-validated live before folding:
  1. Plan filename `SDD-SKILLS-PLAN.md` invisible to `plan-gate.yml` + pre-commit hook (regex `(^|/)PLAN-[^/]*\.md$` requires a `PLAN-` prefix) — fixed by rename to `plans/PLAN-SDD-SKILLS.md`.
  2. Pass 2 was pending with no zero-findings statement — fixed by this entry.
  3. Pass 1 timestamp malformed (`2026-10-25T`) — fixed with a complete ISO stamp.
  4. §3.4 checklist unnamed in Step 4 — added explicitly with §3.4.1 validation.
  5. Version-bump protocol lossy — spelled out GATE-SPEC-E005 five steps with `ruff format` and `--base origin/dev`.
  6. `change_source: direct` / `sdd_lifecycle: []` unstated (CHG-L013 risk); DIR2C-vs-SEED2C unjustified — both fixed in Step 4.
  7. CHG/IPLAN landing PR and A→B sequencing unstated — CHG + IPLAN ride PR A, PR B rebases onto merged A.
  8. One IPLAN or two ambiguous — declared: one IPLAN, full manifest, riding PR A; PR B references it for its subset.
  9. PR B skill names shorthand — all eight full names listed.
  10. Shadowing check + `check_plan.py` runs missing — added to Step 7.
  11. Ledger row 2 half-anchored (`framework_version` on line 4) — added row 14.
- Step 1/2 state confirmed before plan PR: #1032 OPEN with triage note + labels; worktree clean at `dev 21a46e7d6`.
- Pass 1 patches re-validated: destination `framework/skills/sdd-*`, registry + readme scope, bump-by-default all hold.
- **Result:** ready — no new findings.
