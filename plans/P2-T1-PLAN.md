# P2-T1 Plan — Hermes platform design

| Field      | Value                                |
|------------|--------------------------------------|
| Task       | P2-T1                                |
| Depends on | P2-T0 (`plans/P2-AUDIT-hermes.md`)   |
| Status     | DONE — 2026-05-19T14:50:00Z          |
| Feeds      | P2-T2 (verbatim copy), P2-T3 (repoint copy), P2-T4 (spec-version declaration) |

## Objective

Make the **five concrete design choices** identified in P2-T0's audit §6
before any code moves. Each choice gates a downstream task — the module
name and target layout shape P2-T2/T3's copy; the `framework_spec_version`
mechanism shapes P2-T4; the templates-overlap question shapes how
`templates/` is ported in P2-T3; the script entry shapes the new
`pyproject.toml`. The deliverable is **`plans/P2-T1-DESIGN.md`** — one
section per question with options considered, the chosen option, a brief
rationale, and any downstream implications. Non-obvious choices are also
recorded as `D-0013…` in `plans/DECISIONS.md`.

P2-T1 is **paper only** — no code or files move. P2-T2 begins the copy work.

## Scope

**In** — exactly the five questions from audit §6, no more:

1. **Python module / package name** — avoid `mcp_server` collision with any
   future platform; choose import path + distribution name.
2. **`framework_spec_version` declaration mechanism** — where Hermes declares
   the spec version it conforms to (file? `pyproject.toml` key? manifest?).
3. **`templates/` overlap** — relationship between
   `ucx_hermes/templates/*-TEMPLATE.yaml` (runtime YAML) and
   `framework/layers/*/*-TEMPLATE.md` (framework's MD index templates).
4. **Distribution script entry** — replacement for the stale
   `scripts.mcp-ucx = "mcp_server.server:main_sync"`.
5. **Target `platforms/hermes/` layout** — mirror the legacy tree shape or
   restructure?

**Out:**
- Any file moves, code edits, or `.mcp.json` repoints (those start in P2-T2).
- New conformance tests (Phase 4).
- Platform B (Claude Code plugin) design — Phase 3.
- New design questions beyond the five above. If a sixth appears during
  evaluation, it is logged in the design doc's "Deferred" section, not
  resolved here.

## Approach

For each question:

1. **List candidates** — 2–4 realistic options.
2. **State criteria** — collision risk, simplicity, alignment with framework
   conventions (D-0006/D-0009), churn cost in downstream tasks, future-proofing.
3. **Pick one** — choose the option that best satisfies the criteria, with a
   short rationale.
4. **State implications** — which downstream task is affected and how.

Two questions need extra input gathering before evaluation:

- **Q1 (module name)** — examine `platforms/claude-code-plugin/` (if present)
  to see whether Platform B uses Python at all. Per the project description
  the plugin is JS/Markdown/Claude-native (no Python), which would
  *eliminate the collision risk Q1 is built on* and could make
  "minimal churn — keep `mcp_server` import, change distribution name only"
  the clean answer.
- **Q3 (templates overlap)** — compare structures, not full content: do the
  ucx_hermes runtime YAMLs match the framework's index-template MDs in
  purpose, or are they orthogonal artifacts that just share layer names?
  Time-boxed; deeper detail deferred to P2-T3 if not decisive here.

The other three (Q2, Q4, Q5) are short-form choices that should resolve in
a paragraph each.

## Step sequence

1. Gather inputs for Q1 and Q3 (see Approach §1 and §2 above).
2. For each of the five questions, evaluate options together (not serially)
   so cross-question conflicts surface — e.g. Q5 layout interacting with Q2
   mechanism.
3. Write `plans/P2-T1-DESIGN.md` with the per-question sections.
4. If any choice is non-obvious or load-bearing, record a `D-0013…` entry
   in `plans/DECISIONS.md`.
5. **Verify** (see below).
6. **Land** — commit; update `plans/HANDOFF.md`, tick P2-T1 in
   `plans/MIGRATION_TODO.md`; design doc unblocks P2-T2.

## Verification

- `plans/P2-T1-DESIGN.md` exists and contains **all five** question
  sections — explicit list-completeness check (lesson from P2-T0 Pass 3
  retrospective).
- Each section carries: (a) options considered, (b) chosen option,
  (c) one-paragraph rationale, (d) downstream implications.
- **Q1** (module name) — the choice names both the *import path* and the
  *distribution name*, and confirms no conflict with whatever
  `platforms/claude-code-plugin/` is expected to be.
- **Q2** (declaration mechanism) — the chosen approach is concretely
  implementable in P2-T4 against `framework/VERSION` (D-0009).
- **Q3** (templates) — the choice names what happens to **each** of the
  ~10 YAML files in `ucx_hermes/templates/` (kept / dropped / regenerated /
  deferred-with-decision-rule).
- **Q4** (script entry) — the chosen name doesn't collide with the legacy
  `mcp-ucx` script while the legacy tree still ships in `legacy/`.
- **Q5** (layout) — the chosen layout is sketched as a path tree, top two
  levels, so P2-T3 has an unambiguous copy target.
- Any cross-question conflict surfaced and resolved (or explicitly noted).
- No code or files moved — `git status` shows only `plans/` (and possibly
  `DECISIONS.md`) changes.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Q3 (templates overlap) requires deeper inspection than expected → P2-T1 grows | Time-box: compare structure and purpose, not full content; defer specifics to P2-T3 if needed and record the deferral rule explicitly. |
| R2 | Q1 module name choice forces import-path rewrites across `src/` and `tests/` — bigger than the audit implied | The plan explicitly considers churn cost; "minimal churn — keep `mcp_server` import path, change distribution name only" is a named candidate. Picking it costs ~0 churn. |
| R3 | Choices are made in isolation; a downstream conflict surfaces (e.g. Q5 layout breaks Q2 mechanism) | Step 2 evaluates the five questions together, not serially; verify clause requires an explicit "no cross-question conflicts" check. |
| R4 | Design becomes a forum for second-guessing the audit; new questions sprout | Scope locks in the five audit-listed questions only; any sixth goes into the design doc's "Deferred" section, not into P2-T1's resolution loop. |
| R5 | Decisions don't get recorded as `D-0013` entries because they "feel obvious" — context lost across sessions | Step 4 makes the `D-0013…` decision-log step explicit; "feels obvious" is not a stop condition. |

## Review log

### Pass 1 — 2026-05-19T14:38:00Z

- **G1.** Q3 (templates overlap) is the highest-effort question and most
  likely to expand. → Mitigated by R1 + a time-box; if not decisive,
  deferral rule is recorded, not silently dropped.
- **G2.** Lesson from P2-T0 Pass 3 (G9) — Pass 2 didn't audit
  list-completeness; verify caught it. Applying it here: verify clause
  explicitly checks "all five questions covered" as the first item.
- **G3.** Q1 module-name decision has cross-platform implications not
  visible from `ucx_hermes` alone. The plan looks at `platforms/claude-code-plugin/`
  before deciding. → Approach §1 names that input gathering as step 1.
- **G4.** The plan must describe *how* to decide, not pre-decide. → It
  describes candidates and criteria; the design doc seals choices. Named
  candidates (e.g. "minimal churn" for Q1) are noted to ground the criteria,
  not to settle the answer.

### Pass 2 — 2026-05-19T14:40:00Z

- **G5.** Verify clause covers downstream implications — Q1 → imports,
  Q3 → per-file template handling, Q2 → P2-T4 implementability, Q5 → P2-T3
  copy target, Q4 → no legacy collision. Each downstream task has at least
  one verify line tying back to its question. Sufficient.
- **G6.** R2's "minimal churn" candidate borders on pre-deciding. Re-checked:
  it's listed as *a candidate to weigh*, not as the chosen answer; the design
  doc still must justify whatever it picks. Acceptable.
- **G7.** List-completeness pass (G2) executed: the five questions match
  audit §6 1:1; no questions added; no questions silently dropped.
- **G8.** Cross-question conflict guard (R3) is in approach step 2 *and*
  the verify clause — two layers of guard. Good.
- **G9.** Decision-log step (R5) — re-confirmed step 4 makes
  `DECISIONS.md` updates a normal part of the task, not an afterthought.
- No new blockers. Ready to implement on approval.

## Implementation note (2026-05-19T14:50:00Z)

Executed. Q1's input-gathering eliminated its premise — `platforms/claude-code-plugin/`
is JS+Markdown with no Python package, so the import-collision risk Q1 was
designed around doesn't exist; the answer collapsed to minimal-churn
(distribution rename only). Q3's input-gathering produced the substantive
finding of the task: the framework already ships engine-agnostic
`<X>-TEMPLATE.yaml` for all 8 layers, and the Hermes copies have already
drifted by exactly the engine-named block. **D-0013** captures the
resulting "single source of truth" decision; the audit's §3b prose-coupling
in `templates/*.yaml` evaporates because those files aren't copied at all.
Q2/Q4/Q5 resolved short-form per the audit recommendations. No
cross-question conflicts. Design committed to `plans/P2-T1-DESIGN.md`. No
code or files moved.
