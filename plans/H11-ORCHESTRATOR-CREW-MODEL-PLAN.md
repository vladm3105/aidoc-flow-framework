# H11-ORCHESTRATOR-CREW-MODEL Plan (H-11) — modernize the sdd-orchestrator skill from the v3.2 "15 parallel personas + Lite/Standard/Full depth" model to the current weighted-crew + per-lens-playbook + single-path-adaptive model

| Field          | Value                                       |
| -------------- | ------------------------------------------- |
| Task           | H-11 (sdd-orchestrator crew-model modernization) |
| Type           | fix (doc/behavior accuracy)                 |
| Status         | READY — 2026-07-06 (Pass 2 = 3 independent agents, Pass 3 independent fresh-context, Pass 4 self) |
| Depends on     | none (independent)                          |
| Feeds          | the Hermes `sdd-orchestrator` skill accurately represents the current review + flow model |
| Version impact | **Hermes PATCH** (`0.7.0 → 0.7.1`; skill `2.0.0 → 2.1.0`). **No framework change** — docs corrected to match already-shipped engine behavior. No GATE-SPEC, no re-vendor. |

## Objective

The `sdd-orchestrator` agent-skill describes the **v3.2-era review + flow model** the
engine abandoned. The load-bearing anachronisms (grounded by a dispatched inventory +
3-agent review) are:

- **`SKILL.md`** — frontmatter (`:3`) + Overview (`:19`) claim "15 specialized review
  personas dispatched as parallel subagents"; a UCX→Hermes persona-skill-name mapping
  table (`:73`) + creation/review persona-assignment tables (`:444-529`) built on a flat
  15-persona pool; a **superseded chairperson scoring formula** ("8-category weighted
  deductions", `:555`) — the engine computes a **weighted average of crew lens_scores**
  (`review_scoring.py`); a **wrong BRD "All 15 required sections" list** (`:471`) — the
  current `BRD-TEMPLATE.yaml` has different sections (a creation persona following it
  would fail the schema); scattered "4 personas" counts (`:303`, `:534`) that contradict
  the 5-lens crews; and stale `/opt/data/ucx_framework/.venv` MCP-config paths (`:870`,
  `:1164`) a user would copy-paste.
- **Two LOADED governance files** carry a stale **behavioral** depth-tier model
  (Lite/Standard/Full) the framework abandoned for the single-path adaptive loop:
  `governance/GOVERNANCE_RULES.md:140` (§7 Depth Model) and — worse —
  `references/governance-load-protocol.md:58`, which `SKILL.md:26` designates the
  **primary mandatory load** ("skip = governance violation"). An agent following it
  selects a depth tier the engine no longer implements.

The current model: the closed **weighted-crew** set in `framework/governance/REVIEW_CREWS.yaml`
(9 per-layer crews of ~5-6 lenses, weights → weighted-average readiness) with
**per-(layer,lens) playbook injection** (`REVIEW_TEAM.md` §Playbooks / LAYER-PLAYBOOKS-001,
`:229`), over the single-path adaptive loop (MVP → PROD → New MVP). This plan corrects the
files that would **mislead a user/agent**; it does NOT hand-modernize the 72-file
inherited governance boilerplate (cosmetic version strings) or the orphaned vendored
`references/` framework-doc copies (a separate D-0013 decision).

## Scope

**In (behavior-correcting must-fixes):**

- **`SKILL.md` persona model:** frontmatter (`:3`) + Overview (`:19`) → the weighted-crew
  - playbook model (keep the parallel-dispatch statement — the engine does fan out). The
  UCX→Hermes 15-persona mapping (`:73-92`) + creation/review assignment tables
  (`:444-529`) → point at `REVIEW_CREWS.yaml` as **the authority for all 9 crews + weights**
  and show **one illustrative crew** (BRD `{architect:30, business_analyst:30, auditor:20,
  chaos_engineer:12, security_engineer:8}`) as the shape — do **not** copy all nine
  weighted crews into the skill (avoids the second-source-of-truth drift, Pass-2 F2). Add a
  cross-link to **LAYER-PLAYBOOKS-001** (`REVIEW_TEAM.md` §Playbooks) + the per-lens
  playbooks at `framework/playbooks/<NN>_<LAYER>/`.
- **`SKILL.md` scoring formula (`:555-560`):** replace the "8-category weighted deduction"
  chairperson formula with the current model — **weighted average of the crew's
  `lens_score`s (per-layer weights), then capped by unresolved P0/P1**
  (`review_scoring.py`). Keep the `≥90` gate threshold (still correct).
- **`SKILL.md` BRD sections (`:471`):** replace the wrong "All 15 required sections" list
  with the current `framework/layers/01_BRD/BRD-TEMPLATE.yaml` top-level sections (or point
  at the template as the authority rather than enumerate — avoids re-drift).
- **`SKILL.md` persona counts (`:303`, `:534`):** the "4-persona" prose → the 5-lens crew
  (these would contradict the corrected crew tables — the plan's own rewrite creates the
  contradiction if left).
- **`SKILL.md` version framing (`:44/707/883/963/1070/1173`) + MCP paths (`:870`, `:1164`):**
  drop "SDD v3.2" → version-agnostic ("the SDD flow"/`framework/`, not a re-pinned version);
  fix the two MCP-config blocks' stale `/opt/data/ucx_framework/.venv` path.
- **Two loaded governance files (Pass-2 F1):** `governance/GOVERNANCE_RULES.md:140` §7 +
  `references/governance-load-protocol.md:58` — replace the Lite/Standard/Full depth-tier
  model with the current single-path adaptive loop (all 8 layers required per
  NECESSARY-UPSTREAM-001; CHG overlay). These are LOADED (behavioral), not boilerplate.
- Bump skill `version: 2.1.0` (`:4`); Hermes `0.7.0 → 0.7.1`; Hermes + root CHANGELOG;
  D-0052 → **D-0053** (D-0052 was taken by H-14 PR 2); close H-11 in `HERMES-BACKLOG.md`
  (+ carve the 3 deferred follow-ups); HANDOFF.

**Out of scope (deferred — with rationale):**

- **The ~25-file "SDD v3.2" string residue across the 72-file inherited `governance/`
  scaffold + non-loaded `references/`/`root-docs/`.** Cosmetic version-string churn; only 3
  `governance/` files + the 1 primary reference are loaded (the depth-tier ones are pulled
  IN above); the rest carry a stale baseline string but no behavioral error. One-line
  backlog follow-up (optional bulk sweep).
- **The stale hand-vendored `references/` framework-doc copies** (`ucx-readme.md`,
  `doc-governance-core.md`, `id-naming-standards.md`, `layer-registry.yaml`,
  `data-consistency-report.json`) — a D-0013 delete-vs-resync decision; separate follow-up.
- **Element-ID SHA-256 algorithm (`SKILL.md:473`, `:661`, `:1177`)** — states IDs are
  `SHA256`-derived; per D-0040/`PROV01` element IDs are LLM-generated stable strings, NOT
  content-hashes. **Framework-gated** (the rehash is PROVISIONAL-IDS-002, blocked on a
  framework decision) → backlog follow-up, not an inline fix.
- **UCC/UCR/UCRem phase-header branding** (`:444`, `:508`, `:564`) — the phases
  (creation/review/remediation) still exist under new names; legacy UCX branding, not
  behavior-breaking. Cheap to sweep while the file is open (optional), else defer.
- **The sibling `sdd-review-personas` skill** — same pre-crew model; its own item.

## Approach / Design (D-0053)

### Point-at-authority, don't copy (Pass-2 F2)

The one internal-consistency trap is duplicating `REVIEW_CREWS.yaml` weights into the
skill: that creates a second source of truth that drifts. The skill instead **points at
`REVIEW_CREWS.yaml` as the authority** for every crew + weight and shows **one illustrative
BRD crew** as the shape. Same principle for the BRD section list (point at
`BRD-TEMPLATE.yaml`) and the version (point at `framework/VERSION`, don't re-pin `0.33.0`).
This is the D-0006 engine-agnostic-single-source principle applied to a consuming skill.

### The loaded governance depth-tier (Pass-2 F1)

`SKILL.md:26` makes `references/governance-load-protocol.md` a mandatory load and `:34-36`
fallback-loads 3 `governance/` files. The primary-load protocol file plus one of those three
fallback files (`GOVERNANCE_RULES.md`) carry the Lite/Standard/Full depth table — the
exact v3.2 `sdd_depth` model H-11's origin says the framework abandoned (grep of
`framework/governance/*.md` finds no Lite/Standard/Full; the only lifecycle model is
MVP→PROD→New MVP). A loaded file instructing an agent to pick a non-existent depth tier is
the same behavioral-inaccuracy class this plan fixes in `SKILL.md` — so those two edits are
in scope; the non-loaded governance boilerplate is not.

### Versioning

No `framework/` change — the skill consumes the governance docs; only skill + governance
prose is corrected to match already-shipped engine behavior → **Hermes PATCH** `0.7.0 →
0.7.1` (Pass-2 F3: the backward-compat text is "prose-only, engine unchanged" → PATCH, not
MINOR); skill `2.1.0` (substantive content rewrite + new playbook cross-link).

### Backward-compatibility

Prose-only; the skill's tool invocations + flow are unchanged (the review is already
crew-based + adaptive in the engine — the docs were stale, not the engine). No consumer
breaks.

## File structure

### Modified

| Path | Change |
| ---- | ------ |
| `platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/SKILL.md` | persona model + scoring formula + BRD sections + persona counts + MCP paths + v3.2 tags → current model (point-at-authority); `version: 2.1.0` |
| `.../sdd-orchestrator/governance/GOVERNANCE_RULES.md` | §7 Depth Model (`:140`) → single-path adaptive loop |
| `.../sdd-orchestrator/references/governance-load-protocol.md` | depth-tier table (`:58`) → single-path adaptive loop |
| `platforms/hermes/VERSION` (→ `0.7.1`) + Hermes CHANGELOG + root CHANGELOG | version + entries |
| `plans/DECISIONS.md` (D-0053) / `plans/HERMES-BACKLOG.md` (H-11 closed + 3 follow-ups) / `plans/HANDOFF.md` | docs |

## Implementation sequence

### Task 1: SKILL.md — [SKILL]

- Rewrite frontmatter/Overview; persona tables → point-at-`REVIEW_CREWS.yaml` + one
  illustrative crew + playbook cross-link; scoring formula → weighted-average; BRD sections
  → point-at-template; persona counts → 5-lens; MCP paths fixed; v3.2 → version-agnostic;
  bump `version`.

### Task 2: loaded governance depth-tier — [SKILL]

- `GOVERNANCE_RULES.md:140` + `governance-load-protocol.md:58` depth-tier → single-path
  adaptive loop.

### Task 3: version + docs

- Hermes `0.7.1`; both CHANGELOGs; D-0053; close H-11 + carve the 3 deferred follow-ups
  (governance-string sweep; vendored-copy delete-vs-resync; element-ID rehash); HANDOFF.

## Verification

| #  | Check | Expected | Maps to |
| -- | ----- | -------- | ------- |
| V1 | grep `SKILL.md` for the persona-model phrasing ("15 specialized review personas", "15 expert persona subagents", "dispatch personas as parallel subagents") | absent (scoped to persona phrasing — NOT bare "15", which false-positives on "15 required sections"/"7 to 15 scenarios") | persona model |
| V2 | grep `SKILL.md` for `v3.2` | absent (version-agnostic) | version sweep |
| V3 | `SKILL.md` references `REVIEW_CREWS.yaml` as authority + LAYER-PLAYBOOKS-001 + `framework/playbooks/` + one illustrative crew | present | crew model |
| V4 | `SKILL.md` scoring section | describes weighted-average-of-lens_scores (not "8-category deductions"); `≥90` gate retained | scoring fix |
| V5 | `SKILL.md` BRD-sections + persona-counts | point at `BRD-TEMPLATE.yaml`; "5-lens" not "4-persona" | section/count fixes |
| V6 | grep `SKILL.md` for `/opt/data/ucx_framework` | absent (MCP paths fixed) | path fix |
| V7 | grep the 2 governance files for `Lite`/`Standard`/`Full` depth table | absent (single-path model) | Pass-2 F1 |
| V8 | `SKILL.md` `version:` = `2.1.0`; `platforms/hermes/VERSION` = `0.7.1` | bumped | version |
| V9 | `python -m pytest platforms/hermes/tests -q` + `tests/conformance -q` | green (prose-only) | no regression |

## Docs to update

- [ ] `platforms/hermes/CHANGELOG.md` — `[0.7.1]`
- [ ] root `CHANGELOG.md` — Hermes `0.7.0 → 0.7.1`
- [ ] `plans/DECISIONS.md` — D-0053 (scope: SKILL.md + 2 loaded governance files; the rest deferred)
- [ ] `plans/HERMES-BACKLOG.md` — H-11 closed; add "governance/ v3.2 string sweep", "references/ vendored-copy delete-vs-resync", "element-ID rehash (PROVISIONAL-IDS-002)" follow-ups
- [ ] `plans/HANDOFF.md` — arc progress

## Risks

| #  | Risk | Likelihood | Mitigation |
| -- | ---- | ---------- | ---------- |
| R1 | Crew weights in SKILL.md drift from `REVIEW_CREWS.yaml` | low | point-at-authority + one illustrative crew (not a copy of all 9) — resolves the drift class (Pass-2 F2); V3 |
| R2 | Removing the UCX→Hermes persona mapping breaks a real dispatch | low | verified (Pass-2): `platforms/hermes/src/` never consumes the hyphenated skill-names; the runtime is `REVIEW_CREWS` lens names — the mapping is inert v3.2 doc |
| R3 | Scope creep into the 72-file governance tree | low | only the 2 LOADED depth-tier files are in scope; the boilerplate sweep + vendored-copy decision + element-ID rehash are parked backlog follow-ups |
| R4 | The plan's own table rewrite introduces a fresh contradiction with un-fixed prose counts | med | Pass-3 F3 caught this; the persona-count prose (`:303`,`:534`) is pulled INTO scope so the corrected table + prose agree |
| R5 | Hermes PATCH vs MINOR | low | prose-only doc-accuracy, engine unchanged → PATCH (Pass-2 F3) |

## Claim ledger

| #  | Claim | Symbol | Citation |
| -- | ----- | ------ | -------- |
| 1  | Frontmatter "15 specialized review personas dispatched as parallel subagents" | `15 specialized review personas` | platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/SKILL.md:3 |
| 2  | Overview repeats the v3.2/15-persona model | `15 expert persona subagents` | platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/SKILL.md:19 |
| 3  | UCX→Hermes persona-skill-name mapping table | `Persona Name Mapping` | platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/SKILL.md:73 |
| 4  | Skill `version: 2.0.0` (→ `2.1.0`) | `version: 2.0.0` | platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/SKILL.md:4 |
| 5  | Superseded "8-category" chairperson scoring formula | `Category-weighted scoring with 8 categories` | platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/SKILL.md:555 |
| 6  | Wrong BRD "All 15 required sections" list | `All 15 required sections present` | platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/SKILL.md:471 |
| 7  | Stale MCP-config path `/opt/data/ucx_framework/.venv` | `/opt/data/ucx_framework/.venv` | platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/SKILL.md:870 |
| 8  | The primary-load governance file carries the Lite/Standard/Full depth model | `Lite` | platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/references/governance-load-protocol.md:58 |
| 9  | `GOVERNANCE_RULES.md` §7 carries the depth model too | `Depth Model` | platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/governance/GOVERNANCE_RULES.md:140 |
| 10 | `governance-load-protocol.md` is the primary mandatory load | `governance-load-protocol` | platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/SKILL.md:26 |
| 11 | Current model: `REVIEW_CREWS.yaml` per-layer weighted crews | `crews:` | framework/governance/REVIEW_CREWS.yaml:46 |
| 12 | BRD review crew weights (illustrative + V3 spot-check) | `architect: 30, business_analyst: 30` | framework/governance/REVIEW_CREWS.yaml:51 |
| 13 | Current scoring is weighted-average-of-lens_scores | `weighted average` | platforms/hermes/src/mcp_server/review/review_scoring.py:7 |
| 14 | LAYER-PLAYBOOKS §Playbooks + playbooks path | `## Playbooks` | framework/governance/REVIEW_TEAM.md:229 |
| 15 | Current Hermes version is `0.7.0` (→ `0.7.1` PATCH) | `0.7.0` | platforms/hermes/VERSION:1 |
| 16 | Most recent project decision is D-0052 → next free is D-0053 | `D-0052` | plans/DECISIONS.md:13 |
| 17 | H-11 is the open backlog entry | `### H-11` | plans/HERMES-BACKLOG.md:386 |

## Review log

### Pass 1 — 2026-07-05 — self-review (initial "one-file" scope; superseded)

Scoped H-11 to `SKILL.md` persona-model + version sweep, deferring everything else. The
3-agent review (Pass 2) showed that scope was too small in specific behavioral places.

### Pass 2 — 2026-07-05 — independent (3-agent parallel per OPS-0067)

Citations **0 inaccuracies**; premise confirmed (the mapping is inert v3.2 doc — the
runtime uses `REVIEW_CREWS` lens names; the engine runs weighted crews + playbook
injection). Findings folded:

- **[LB] Loaded governance depth-tier residue.** `GOVERNANCE_RULES.md:140` + the
  **primary-load** `governance-load-protocol.md:58` carry the Lite/Standard/Full depth
  model the framework abandoned — behavioral, not cosmetic. → Pulled the **2 loaded files**
  into scope (the 72-file boilerplate stays deferred).
- **[LB] Crew-weights copy-vs-point contradiction.** Scope said "embed the crews+weights";
  R1 said "point, don't duplicate"; V4 verified a copy. → Resolved to **point-at-authority +
  one illustrative crew**; V3/V-checks aligned.
- **[MINOR] MINOR vs PATCH.** Backward-compat is "prose-only, engine unchanged" → **PATCH**
  `0.7.1`.
- **[LB×5, completeness] SKILL.md gaps the one-file scope missed:** wrong BRD "All 15
  required sections" (`:471`); superseded "8-category" scoring formula (`:555`);
  contradictory "4-persona" counts (`:303`,`:534` — the table rewrite would create a fresh
  contradiction); stale `/opt/data/ucx_framework/.venv` MCP paths (`:870`,`:1164`). → all
  **pulled into the SKILL.md edit** (the file is open anyway). Element-ID SHA-256
  (`:473`,`:661`,`:1177`) is **framework-gated** (PROVISIONAL-IDS-002) → backlog follow-up.
- **Advisory:** scope V1 to persona phrasing (bare "15" false-positives on "15 required
  sections"/"7 to 15 scenarios") — done. UCC/UCR/UCRem branding = optional/defer.

### Pass 3 — 2026-07-06 — independent (fresh-context adversarial re-review of the reshaped plan)

All 17 citations re-verified exact (symbol + advisory line). Internal consistency clean
(version-impact / Scope / File table / V1-V9 / ledger all agree). D-0053 confirmed free,
D-0052 taken. **Scope framing validated at source:** `SKILL.md:34-36` fallback-loads 3
`governance/` files (`GOVERNANCE_RULES.md`, `DEFINITION_OF_DONE.md`,
`DEVELOPMENT_WORKFLOW_GUIDE.md`) + the primary `references/governance-load-protocol.md`; a
grep confirmed the depth-tier table lives ONLY in `GOVERNANCE_RULES.md:140` +
`governance-load-protocol.md:58` — the exact 2 files in scope — so no LOADED behavioral file
is deferred and nothing speculative is in scope. Framework-agnostic boundary clean (every
edit target under `platforms/hermes/` or `plans/`; the `framework/` refs are read-as-authority,
not edited → no GATE-SPEC). One NIT (ambiguous "two of those" antecedent in the Approach §) —
folded. **Verdict: sound, ready to implement as written.**

### Pass 4 — 2026-07-06 — self-review (re-validate the Pass-2 fold)

Re-validated the expanded scope for internal consistency: the persona-count prose fix
(`:303`/`:534`) now agrees with the corrected crew guidance (no fresh contradiction — R4);
point-at-authority (crews, BRD sections, version) uniformly avoids second-source drift
(R1); the 2 loaded governance files close the behavioral depth-tier gap while the 72-file
boilerplate + vendored copies + element-ID rehash stay parked as 3 backlog follow-ups;
PATCH matches the prose-only backward-compat. D-0052→D-0053 (D-0052 taken by H-14 PR 2). V1
scoped to persona phrasing. No new gaps.

**Result:** ready
