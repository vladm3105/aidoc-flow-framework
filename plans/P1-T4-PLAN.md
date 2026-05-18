# P1-T4 Plan — Extract Governance Docs + CHG Overlay into `framework/governance/`

| Field      | Value                                      |
|------------|--------------------------------------------|
| Task       | P1-T4                                      |
| Depends on | P1-T1 audit, D-0005, D-0006, P1-T2 (G8)    |
| Status     | PLANNED — 2026-05-18T20:00:00Z             |
| Feeds      | P1-T5 (conformance suite)                  |

## Objective

Populate `framework/governance/` with the engine-agnostic governance standards
and the CHG (change-management) overlay extracted from `legacy/ucx_flow_v3/`.
CHG is spec-only here — extracted for completeness, not enforced (re-introduced
post-Phase 5 per ROADMAP CHG-D1/D2).

## Scope

**In:** 5 governance docs, the CHG overlay (README, template, index template,
7 gates, 2 companion templates), and short `framework/governance/README.md` +
`chg/`-level orientation — 18 files.
**Out:** the 4 framework-root methodology docs (`SPEC_DRIVEN_DEVELOPMENT_GUIDE`,
`QUICK_REFERENCE`, `AI_ASSISTANT_RULES`, `TESTING_STRATEGY_TDD`) and the
framework root README — **no task owns these** (see G3); conformance suite
(P1-T5); `framework/VERSION` (P1-T6).

## Source → target map

| Source (`legacy/ucx_flow_v3/`) | Target (`framework/governance/`) | Action |
|--------------------------------|----------------------------------|--------|
| `DOC_GOVERNANCE_CORE.md` | `DOC_GOVERNANCE_CORE.md` | copy + T1 |
| `ID_NAMING_STANDARDS.md` | `ID_NAMING_STANDARDS.md` | copy + T1 + T4 |
| `TRACEABILITY.md` | `TRACEABILITY.md` | copy + T1 |
| `DIAGRAM_STANDARDS.md` | `DIAGRAM_STANDARDS.md` | copy + T1 + T2 |
| `THRESHOLD_NAMING_RULES.md` | `THRESHOLD_NAMING_RULES.md` | copy verbatim (scan: clean) |
| `CHG/README.md` | `chg/README.md` | copy + T1 |
| `CHG/CHG-TEMPLATE.yaml` | `chg/CHG-TEMPLATE.yaml` | copy + T1 + T3 |
| `CHG/CHG-00_index.md` | `chg/CHG-00_index.TEMPLATE.md` | rebuild as template (T5) |
| `CHG/gates/*.md` (×7) | `chg/gates/*.md` | copy + T1 |
| `CHG/templates/*.md` (×2) | `chg/templates/*.md` | copy + T1 |
| — | `README.md` (new) | write — governance overview |

## Transformation rules

- **T1 — version strings.** Drop `SDD v3.2` / `v3.2` / `(v3.2)` qualifiers
  → `SDD`; neutralize headings (`## v3.2 Governance Baseline` →
  `## Governance Baseline`, `v3.2 Standard` → `Standard`). **Remove the
  `framework_version: "3.2"` custom-field line** from CHG `.md` frontmatter and
  any `Framework: SDD v3.2 …` template lines — the spec version lives only in
  `framework/VERSION` (D-0006).
- **T2 — DIAGRAM_STANDARDS.** Remove the `.claude/skills/...SKILL.md` cross-ref
  lines; neutralize the Claude-Code skill names `mermaid-gen` / `charts-flow`
  (in tables, "Related Skills", "Enforcement") to platform-neutral wording
  ("the platform's diagram-generation tooling"). Keep the Mermaid-only standard.
- **T3 — CHG-TEMPLATE.yaml.** `ignored by MCP tools` → `ignored by validators`;
  `[How verified — test, review, MCP tool]` → `… validation tool`.
- **T4 — ID_NAMING_STANDARDS (G8).** Add a File-Naming entry for the index
  template: `{TYPE}-00_index.TEMPLATE.{md,yaml}`.
- **T5 — CHG index.** Rebuild `CHG-00_index.md` as `CHG-00_index.TEMPLATE.md`:
  empty registry skeleton, no instance rows, `.TEMPLATE.` infix (consistent
  with D-0005).
- **T6 — copy verbatim.** `THRESHOLD_NAMING_RULES.md` (scan: no engine tokens,
  no version strings).

`framework/governance/README.md`: ~1 paragraph — what the governance docs
cover; that CHG is spec-only / deferred until post-Phase 5.

## Step sequence

1. Create `framework/governance/` and `framework/governance/chg/{gates,templates}/`.
2. Copy + transform each file per the map.
3. Write `framework/governance/README.md`.
4. **Verify** (see below).
5. **Land:** commit; tick P1-T4 in `MIGRATION_TODO.md`; update `CHANGELOG.md`,
   `HANDOFF.md`; record the G3 follow-up task.

## Verification

Patterns dry-run against the legacy source during planning (scan calibrated):

- Every `*.yaml` under `framework/governance/` parses.
- `grep -riE 'hermes|ucx_|\.claude/' framework/governance/` → **empty**.
- `grep -rE 'sdd_(validate|create|score|consistency|preflight|next_action|review|remediate)' framework/governance/` → **empty**.
- `grep -rniE '\bmcp\b' framework/governance/` → **empty**.
- `grep -riE 'mermaid-gen|charts-flow' framework/governance/` → **empty**
  *(explicit — these bare Claude-Code skill names are NOT caught by the
  `.claude/` grep; without this check a real engine reference would slip
  through — a false-negative guard).*
- `grep -rniE 'sdd v3|v3\.[0-9]|framework_version' framework/governance/` →
  **empty** *(`v3\.[0-9]` needs a literal `v3.`; `C4-L3`, `dfd-l3`, `GATE-03`
  do not match — confirmed against legacy).*
- CHG `.md` frontmatter still valid after `framework_version` removal
  (spot-parse the `---` blocks).
- File count: 18.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Broad version-string edits corrupt CHG `.md` frontmatter | spot-parse frontmatter blocks in Verify |
| R2 | DIAGRAM_STANDARDS skill-neutralization over-strips the Mermaid standard | touch only skill-name/path refs; keep the rule body |
| R3 | Bare `mermaid-gen`/`charts-flow` names slip past the `.claude/` grep | explicit name grep in Verify |
| R4 | The 4 root methodology docs are stranded with no owning task | G3 — recommend a new tracked task P1-T7 |

## Review log

> ≥2 passes required before implementation (see `CLAUDE.md`). Each pass also
> cross-checks the Verification section against the transformation rules.

### Pass 1 — 2026-05-18T20:05:00Z

- **G1.** `mermaid-gen` / `charts-flow` appear as bare skill-name references in
  DIAGRAM_STANDARDS, not only as `.claude/skills/...` paths. An engine grep on
  `.claude/` alone would miss them — a false negative. → T2 neutralizes the
  bare names; Verification adds an explicit `mermaid-gen|charts-flow` grep.
- **G2.** CHG `.md` files carry a `framework_version: "3.2"` frontmatter field.
  Neutralizing the *string* is not enough — the field must be removed (D-0006:
  version lives only in `framework/VERSION`). → T1 makes removal explicit; R1
  guards frontmatter validity.
- **G3.** The 4 root methodology docs + framework root README are extracted by
  no P1 task. → Scoped OUT of P1-T4 (which is governance + CHG by definition);
  recorded as a follow-up — recommend adding **P1-T7 (framework root assembly)**
  to `MIGRATION_TODO.md`.
- **G4.** P1-T1 audit marked `CHG-00_index.md` INSTANCE/drop, but D-0005's
  logic (index format is a conformance concern) applies to CHG too. →
  T5 rebuilds it as `CHG-00_index.TEMPLATE.md`.

### Pass 2 — 2026-05-18T20:10:00Z

Re-read the hardened plan; cross-checked Verification vs transformation rules:

- **Verification audit.** `v3\.[0-9]` — confirmed no false positive against
  legacy: `C4-L3`/`dfd-l3`/`GATE-03`/`L3` lack a literal `v3.`. The added
  `mermaid-gen|charts-flow` grep closes the false-negative gap from G1. The
  `framework_version` token in the version grep catches any missed CHG field.
- **G5 (noted).** DIAGRAM_STANDARDS ends with a cross-ref to
  `SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` (a root doc not placed until the proposed
  P1-T7). The link will be dead until then — point it at the intended path
  `../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md` and accept the temporary gap, same as
  the P1-T2 cross-doc links.
- No new blockers. Ready to implement on approval.
