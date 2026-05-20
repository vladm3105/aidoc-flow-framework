# P3-T0 Plan — Phase 3 audit & task breakdown

| Field      | Value                                |
|------------|--------------------------------------|
| Task       | P3-T0                                |
| Depends on | Phase 2 complete (`v0.3.0`, `hermes/v0.1.0`) |
| Status     | DONE — 2026-05-20T18:35:00Z          |
| Feeds      | P3-T1 … P3-Tn (Claude Code plugin tasks defined here) |

## Objective

Map Phase 3 on paper before any content moves. The Claude Code plugin's
source content lives at the **repo-root `.claude/` directory** — the
active skill loader the in-container session uses today. Per
`docs/REPO_STRUCTURE.md` it ports to `platforms/claude-code-plugin/`
in Phase 3, but the relationship (move vs copy vs cutover semantics)
and the in-scope subset (some non-doc skills look migration-specific)
need explicit resolution before any work starts.

P3-T0 produces:

1. **`plans/P3-AUDIT-claude-code-plugin.md`** — an audit doc
   inventorying `.claude/`, resolving its relationship to the plugin
   target, mapping framework coupling, and classifying every top-level
   path as port-verbatim / port-with-repoint / drop / defer.
2. **A concrete P3-T1…P3-Tn task breakdown** appended to this plan,
   with inputs and outputs for each task.
3. **A conformance-gap statement** — what the plugin must declare and
   change to satisfy the 25-test framework conformance suite (the
   suite scans `framework/`, so the gap is the platform-side
   declaration mechanism).

P3-T0 is **paper only**; no content moves and no manifest is created.

## Scope

**In:**
- Inventory `.claude/` by directory and file type (191 files total
  during recon).
- Resolve the `.claude/` ↔ `platforms/claude-code-plugin/` relationship:
  move (clean cutover; breaks in-container session's own skills),
  copy with sync (interim duplication), or copy-and-divergence
  (root stays migration-flavored, plugin is user-facing).
- Identify framework-coupling sites — references to `ucx_flow_v3`,
  `ai_dev_flow/`, framework paths, or illustration `/opt/data/...`
  paths that distinguish "rewire" from "leave verbatim".
- Determine the conformance gap: what does the plugin declare to
  satisfy D-0009 (`framework_spec_version`)?
- Classify every top-level path under `.claude/` and decide what
  needs to be **added** (plugin manifest, VERSION files) that doesn't
  exist in `.claude/`.
- Output: `plans/P3-AUDIT-claude-code-plugin.md` + the P3-Tx
  breakdown below.

**Out:**
- Any actual copy or content edit (later P3-T*).
- The plugin manifest schema decision — that's a P3-T1 design question.
- Specific non-doc-skill in/out judgement — surfaced here as an open
  question; resolved in P3-T1.
- Conformance suite extension (Phase 4).
- Phase 5 cutover — when root `.claude/` is removed.

## Approach

1. **Inventory.** `find .claude/ -maxdepth 2 -type d` and per-subdir
   file counts. Already executed during planning recon.
2. **Coupling sweep.** Grep `.claude/` for `ucx_flow|UCX_FLOW`,
   `ucx_hermes`, `ai_dev_flow`, `framework/layers`, `/opt/data`.
   Record per-file hit counts; classify any hit as
   current-behavior-rewire vs historical-illustrative per the
   G13 lesson.
3. **Relationship resolution.** Compare `.claude/` (active loader)
   vs `platforms/claude-code-plugin/` (distribution target) by role
   and lifetime; recommend the move/copy/sync mechanic.
4. **Classification matrix.** Per top-level `.claude/` path:
   port-verbatim, port-with-repoint, drop, or defer; with a one-line
   rationale.
5. **Adds.** Enumerate the files the plugin needs that `.claude/`
   doesn't carry (manifest, VERSION files, CHANGELOG, possibly
   expanded README).
6. **Open questions.** What design choices P3-T1 must resolve before
   any port runs.
7. **Task breakdown.** Define P3-T1…P3-Tn with concrete deliverables
   and verify gates.

## Step sequence

1. Recon (done during planning).
2. Write `plans/P3-AUDIT-claude-code-plugin.md` per §Approach.
3. Append the P3-T1…P3-Tn task breakdown to this plan.
4. **Verify** (see below).
5. **Land** — single commit
   `docs: P3-T0 phase-3 audit + task breakdown (paper-only)`; update
   `plans/HANDOFF.md`; tick P3-T0 in `plans/MIGRATION_TODO.md`.
   Push to working branch.

## Verification

- **Paper-only.** `git status` shows changes only under `plans/` (no
  edits to `framework/`, `platforms/`, or `.claude/`).
- **Inventory completeness.** Every top-level path in
  `.claude/{skills,agents,commands,hooks,settings*.json}` appears in
  the audit's classification matrix.
- **Coupling scan reproducible.** The audit cites a coupling-sweep
  command whose output is captured (per-file hit counts), and the
  matrix decisions reference that output.
- **Open-questions completeness.** At least the canonical 5 questions
  for a Phase-N design (per the P2-T1 pattern) appear in the audit's
  §6: scope subset, manifest schema, version mechanism, copy
  semantics, naming.
- **Task breakdown self-contained.** Each P3-T1…P3-Tn task has a
  one-paragraph statement of inputs/outputs and a verify gate.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Audit misses a non-`.claude/` source content blob (e.g. `legacy/ai_dev_ssd_flow_v2/` carries earlier skill versions worth porting). | Cross-check vs `docs/REPO_STRUCTURE.md` legacy→target mapping: `legacy/ai_dev_ssd_flow_v2/` is classified "dropped (superseded by `framework/`)". The audit confirms no Phase-3-relevant content under `legacy/` other than the root-doc context inherited at Phase 2. |
| R2 | The move-vs-copy decision affects whether the in-container session continues to work after the port (root `.claude/` removal would break this session's own skill loading). | Resolved in audit §2 with a clear mechanic; the conservative answer (copy + root stays until Phase 5 cutover) is the default unless a strong reason emerges. |
| R3 | A non-doc skill in `.claude/skills/` is migration-specific (used by this dev workflow) and shouldn't ship in the user-facing plugin. | Audit §5 lists each non-doc skill explicitly and tags candidates; P3-T1 design makes the final in/out call per skill. Defer rather than decide here. |
| R4 | `.claude/hooks/` look like dev-time hooks (plan-review-gate, pre-compact-snapshot, session-start-handoff). Shipping them in the plugin would force users into the migration workflow. | Audit classifies hooks as drop-from-plugin per their migration-only purpose; rationale recorded. Plugin lifecycle hooks (if any) would be a fresh add in P3-T2/T3. |
| R5 | The doc-* skills reference framework artifacts by placeholder path (`{project_root}/ai_dev_flow/...`) that doesn't map to the new `framework/` layout. | Audit §3 records this as coupling that needs rewire in P3-T*; the size of the rewire (number of files, lines) is part of the audit output and informs P3-T1 design. |
| R6 | The plugin manifest schema isn't documented anywhere in the repo; need to consult Claude Code's external docs. | P3-T1 design surfaces this as an open question; the audit doesn't presume a schema. |

## Review log

### Pass 1 — 2026-05-20T18:05:00Z

- **G1. Paper-only constraint matches the P2-T0 pattern.** Verify
  gate checks `git status` for no edits to `framework/`,
  `platforms/`, or `.claude/`. Mirrors P2-T0.
- **G2. The move-vs-copy question is the highest-risk unknown.**
  Pulled into audit §2 as a primary decision, not a sub-bullet.
  R2 explicitly handles the conservative default.
- **G3. Non-doc skill in/out is deferred to P3-T1, not decided here.**
  The audit lists each; the design pass decides. Mirrors P2-T1 Q3
  ("which template artifacts are dropped").
- **G4. Coupling sweep needs to use the audit-sweep idiom
  (whitelist if historical, rewire if current).** P2-T7 G13 + P2-T3
  §3c carried this lesson. Audit §3 must surface both kinds.
- **G5. The conformance gap is small** (the suite scans only
  `framework/`). For Phase 3 the gap is the platform-side
  declaration mechanism — same as Hermes (`VERSION` +
  `FRAMEWORK_SPEC_VERSION`, D-0009).
- **G6. The plugin manifest is a NEW artifact** the source doesn't
  carry. Audit §5b enumerates what the plugin needs that `.claude/`
  doesn't have, in addition to the inventoried ports.
- **G7. Recon already done; audit body is the deliverable.** No
  separate recon step required at implementation time — Step 1 is
  marked done during planning.

### Pass 2 — 2026-05-20T18:20:00Z

- **G8. List-completeness (P2-T0 Pass 3 lesson) — every top-level
  `.claude/` entry must appear in §5.** Recon enumerated:
  `skills/`, `agents/`, `commands/`, `hooks/`, `settings.json`,
  `settings.local.json`. Audit §5 will cover all 6.
- **G9. Scope-completeness (P2-T0 Pass 4 lesson) — anything outside
  `.claude/` that could be plugin-source must be considered.**
  Cross-checked: `legacy/ai_dev_ssd_flow_v2/` is dropped; `.mcp.json`
  is Hermes-only; no other plugin-source content surfaced.
- **G10. Open questions for P3-T1 — anchor the count.** P2-T1
  resolved 5 questions; P3-T1 will likely have a similar count
  (manifest, scope subset, version mechanism, naming, copy
  semantics). Audit §6 lists them upfront so P3-T1 doesn't
  reinvent its own scope.
- **G11. No new findings.** Plan is internally consistent and the
  verify gates are observable. Ready to present on approval.

## Phase 3 task breakdown (resolved here, executed P3-T1..P3-T5)

After the audit (this task), Phase 3 unfolds as five sub-tasks. The
shape mirrors P2 but simpler — coupling is near-zero, no separate
"verbatim port" + "port-with-repoint" split. Numbering preserves the
P2 convention (T0 audit, T5 verify, T6 close); intermediate tasks
fold work that P2 spread across T1-T4 + T7-T9.

- **P3-T1 — Design.** Resolve the 5–7 open questions surfaced by the
  audit (manifest schema, scope subset of non-doc skills, version
  mechanism, naming, copy semantics, etc.). Output:
  `plans/P3-T1-DESIGN.md` recording each decision with rationale.
  Mirrors P2-T1's shape.
- **P3-T2 — Port content.** Copy the in-scope contents from
  `.claude/` to `platforms/claude-code-plugin/` per the P3-T1
  decisions: `skills/` (the in-scope subset), `agents/`, `commands/`.
  Apply any coupling rewires identified by audit §3
  (`{project_root}/ai_dev_flow/...` → `framework/...` for the
  current-behavior subset; preserve illustration paths per G13).
  Mirrors P2-T2 + P2-T3 combined (one-step since coupling is small).
- **P3-T3 — Plugin scaffold.** Create `.claude-plugin/plugin.json`
  (manifest per P3-T1's schema decision), `VERSION` (`0.1.0`),
  `FRAMEWORK_SPEC_VERSION` (matching `framework/VERSION`), and
  expand `platforms/claude-code-plugin/README.md` from placeholder
  to populated. Mirrors P2-T3's pyproject + VERSION work.
- **P3-T4 — Verify.** Conformance suite still 25/25; coupling sweep
  on `platforms/claude-code-plugin/` returns zero (or matches the
  P3-T2 whitelist if a G13-style historical set emerges); plugin
  manifest validates against Claude Code's schema (if the schema
  is accessible); per-skill content equivalence check vs root
  `.claude/` (no semantic drift on the copy). Mirrors P2-T5.
- **P3-T5 — Close.** Cut `CHANGELOG.md [0.4.0]`; mark Phase 3 in
  `ROADMAP.md`; create annotated tags `v0.4.0` (milestone) and
  `claude-code-plugin/v0.1.0` (platform). Anticipate the in-container
  tag-push 403; bake the local-clone workaround into the plan.
  Mirrors P2-T6.

The shape is 5 tasks (P3-T1..T5), where P2 needed 9 (P2-T0..T9 inc.
the implementation-discovered T7..T9). Justified by:
- Single-source-of-truth content (`.claude/`) — no `mcp_ucx`-style
  predecessor to disambiguate.
- Near-zero framework coupling — no `ucx_flow_v3` runtime constants
  to rewire.
- Declarative artifact (no Python package, no test suite to repoint).

If implementation surfaces unexpected complexity (e.g. P3-T2 finds
substantial coupling), the breakdown can grow; the audit's job is to
make this estimate honest.
