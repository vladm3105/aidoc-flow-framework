# P1-T2 Plan — Extract Layer Templates into `framework/layers/`

| Field      | Value                                      |
|------------|--------------------------------------------|
| Task       | P1-T2                                      |
| Depends on | P1-T1 audit, D-0005 (index templates), D-0006 (v0.1.0) |
| Status     | PLANNED — 2026-05-18T18:15:00Z             |
| Feeds      | P1-T3 (registry), P1-T5 (conformance)      |

## Objective

Populate `framework/layers/` with the 8 engine-agnostic layer specs extracted
from `legacy/ucx_flow_v3/`: each layer's authoring **template**, its **README**,
and a new per-layer **index template** (D-0005). All Hermes/MCP- and
Claude-Code-specific content removed so the result is engine-neutral.

## Scope

**In:** `framework/layers/01_BRD … 08_IPLAN/`, three files per layer.
**Out:** `LAYER_REGISTRY.yaml` (P1-T3); governance docs + root README (P1-T4);
conformance suite (P1-T5); `framework/VERSION` (P1-T6).

## Source → target map (per layer `0N_TYPE`)

| Source (`legacy/ucx_flow_v3/`) | Target (`framework/layers/`) | Action |
|--------------------------------|------------------------------|--------|
| `0N_TYPE/TYPE-TEMPLATE.yaml` | `0N_TYPE/TYPE-TEMPLATE.yaml` | copy + neutralize |
| `0N_TYPE/README.md` | `0N_TYPE/README.md` | copy + strip |
| `0N_TYPE/TYPE-00_index.{md,yaml}` | `0N_TYPE/TYPE-00_index.TEMPLATE.{md,yaml}` | rebuild as template |

24 files total (8 templates, 8 READMEs, 8 index templates).

## Transformation rules

### A — Templates (`*-TEMPLATE.yaml`)

- **A1.** Remove `metadata.validation.tool` (`sdd_validate`) and `.server`
  (`ucx_hermes`). Rewrite its `_guidance` to engine-neutral wording: validation
  = structural check + readiness score (quality gate) + preflight + cross-doc
  consistency, performed by *the platform's conformance tooling*. Applies to
  BRD, PRD, EARS, BDD, ADR (5 templates).
- **A2.** Header comment `_guidance — … ignored by MCP tools` →
  `… ignored by validators`. All 8 templates.
- **A3.** BRD `cross_section_rules.description: "Machine-enforced by
  sdd_validate (ucx_hermes)"` → `"Machine-enforced cross-section rules"`.
- **A4.** IPLAN template — neutralize `stateless MCP executor` phrasing →
  `stateless executor` / `AI agent session`.
- **A5.** SPEC, TDD templates — no engine refs; apply A2 + A7 only.
- **A6.** Do **not** change: `schema_version`, `layer`, C4 `_guidance` layer
  content, content sections, ID formats, `last_updated`.
- **A7.** Neutralize legacy version strings (every template carries 1–3):
  drop `# Version: 3.2` header lines; `SDD v3.2` / `SDD v3` → `SDD` (the
  methodology name stays; the legacy version qualifier goes — the framework
  version stream is `framework/VERSION`, P1-T6, per D-0006).

### B — Layer READMEs (`README.md`)

- **B1.** Layers 01–05: delete the `## Template Sync Rule` and
  `## MCP Tools (ucx_hermes)` sections in full (heading + body), leaving
  surrounding sections intact.
- **B2.** Layer 08 IPLAN: neutralize `stateless MCP executor` phrasing.
- **B3.** All: rewrite path refs `ucx_flow_v3/` → `framework/layers/`; repoint
  cross-layer and registry links to the new structure.
- **B4.** Layers 06, 07: copy, apply B3 only (no engine sections present).
- **B5.** BRD README: drop the `## Archive` section (references a
  `BRD_v1_archive/` dir that does not exist in `framework/`).

### C — Index templates (new — D-0005)

- **C1.** Layers 01–07: `TYPE-00_index.TEMPLATE.md`, modeled on the legacy
  `*-00_index.md` structure, **stripped of**: Hermes "Quick Start" MCP commands;
  project-instance taxonomy (e.g. BRD's F1–F7 / D1–D7 module list →
  generic placeholder note); instance statistics. **Kept**: layer position,
  empty registry table skeleton, allocation rules, quick links.
- **C2.** Layer 08: `IPLAN-00_index.TEMPLATE.yaml` — the legacy
  `IPLAN-00_index.yaml` is already a skeleton (`plans: []`, `backlog: []`);
  copy, drop the `SDD v3.2` version header line, keep structure.
- **C3.** `.TEMPLATE.` infix distinguishes the spec template from instance
  index files a project would create.

## Step sequence

1. Create `framework/layers/01_BRD … 08_IPLAN/` (8 dirs).
2. Per layer: copy + neutralize template (A); copy + strip README (B);
   build index template (C).
3. **Verify** (see below).
4. **Land:** commit; tick P1-T2 in `MIGRATION_TODO.md`; update `CHANGELOG.md`,
   `HANDOFF.md`.

## Verification

- Every `*.yaml` under `framework/layers/` parses: `python3 -c "import yaml,glob;
  [yaml.safe_load(open(f)) for f in glob.glob('framework/layers/**/*.yaml',
  recursive=True)]"`.
- `grep -riE 'hermes|mcp|sdd_[a-z]|ucx_' framework/layers/` → **empty**.
- `grep -rn 'ucx_flow_v3' framework/layers/` → **empty**.
- File count: 24 files across 8 dirs.
- Spot-read 2 templates + 2 READMEs to confirm no orphaned headings / no
  over-stripping of agnostic content.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Surgical edits corrupt large YAML (BRD 975 lines) | YAML parse check in Verify |
| R2 | README section removal orphans adjacent headings | review surrounding structure per edit |
| R3 | Internal links break after move | grep for `ucx_flow_v3` / old relative paths |
| R4 | Over-stripping removes agnostic content | only the 4 identified engine-specific patterns are removed; everything else copied verbatim |
| R5 | Index `.md` frontmatter goes stale | keep frontmatter; mark `document_type` as the index *template* |

## Review log

### Pass 1 — 2026-05-18T18:15:00Z

Self-review findings, folded into the plan above:

- **G1.** P1-T1 audit classed templates as cleanly AGNOSTIC; planning scan
  found a Hermes-bound `metadata.validation` block in 5 templates. → Added A1/A3.
- **G2.** Audit classed `*-00_index.*` as pure INSTANCE; inspection shows they
  are template-shaped (IPLAN index is already a skeleton). → C1/C2 build them
  as proper templates rather than discarding the structure.
- **G3.** BRD README `## Archive` points at a non-existent dir. → Added B5.
- **G4.** A `framework/layers/README.md` overview is **out of scope** here —
  deferred to P1-T4 framework-root assembly.
- **G5.** Confirmed `last_updated` in templates is left untouched (A6) — the
  spec version stream is `framework/VERSION`, not per-template dates.

### Pass 2 — 2026-05-18T18:30:00Z

Re-read the hardened plan as the workflow requires. Findings:

- **G6 (real — fixed).** Every template embeds legacy version strings
  (`# Version: 3.2`, `SDD v3.2`, `SDD v3`) — 16 occurrences across 8 files.
  The plan was silent; leaving them contradicts D-0006 (framework versions
  independently from `0.1.0`). → Added rule **A7**.
- **G7 (checked — not an issue).** Verified the layer READMEs contain no
  cross-doc markdown links to registry/governance files, and their only
  `ucx_flow_v3/` path references sit entirely inside the engine sections that
  B1 deletes. B3's link-rewriting is therefore mostly moot; B3 is kept only as
  a post-edit safety grep.
- **G8 (noted — out of scope).** `ID_NAMING_STANDARDS.md` has no entry for the
  `*-00_index.TEMPLATE.*` naming. Flagged for P1-T4 (governance extraction);
  not a P1-T2 change.

No open blockers. Ready to implement on approval.
