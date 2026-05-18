# P1-T3 Plan — Extract `LAYER_REGISTRY.yaml` into `framework/registry/`

| Field      | Value                                      |
|------------|--------------------------------------------|
| Task       | P1-T3                                      |
| Depends on | P1-T2 (`framework/layers/`), D-0006 (v0.1.0) |
| Status     | PLANNED — 2026-05-18T19:20:00Z             |
| Feeds      | P1-T5 (conformance suite), P1-T6 (`framework/VERSION`) |

## Objective

Move the layer registry — the machine-readable single source of truth for the
8-layer model (layer order, traceability dependency graph, C4 mapping, ID
patterns) — into `framework/registry/` as an engine-neutral artifact. The
registry is the authoritative core both platforms validate against; templates
and prose docs defer to it.

## Scope

**In:** `framework/registry/LAYER_REGISTRY.yaml` (copied + neutralized) and a
short `framework/registry/README.md` stating the registry's authoritative role.
**Out:** deep semantic validation of the registry (P1-T5 conformance suite);
`framework/VERSION` (P1-T6); governance docs (P1-T4).

## Approach

Source: `legacy/ucx_flow_v3/LAYER_REGISTRY.yaml` (233 lines). Copy to
`framework/registry/LAYER_REGISTRY.yaml`, then apply:

- **T1 — header.** `# SDD v3 Layer Registry` → `# SDD Layer Registry`; drop the
  `# Version: 3.2` and `# Last Updated:` comment lines; keep the
  `# Single source of truth …` line.
- **T2 — version field.** Drop the standalone `version: "3.2"` key. The spec
  version lives only in `framework/VERSION` (D-0006, P1-T6) — one source.
- **T3 — `metadata.framework`.** `"Specification-Driven Development (SDD) v3 —
  Streamlined"` → `"Specification-Driven Development (SDD)"`. Add
  `derived_from: "SDD v3.2"` for provenance (consistent with D-0006).
- **T4 — changelog.** Drop the entire `metadata.changelog:` block (legacy
  v3.0–3.2 history; this also removes the lone engine reference, a "Stateless
  MCP executor" line, that sits inside it).
- **T5 — `folder:` paths.** `01_BRD/` → `layers/01_BRD/` (… ×8) — paths are
  relative to the `framework/` root. Add a one-line comment in the registry
  stating that convention.
- **T6 — C4 comment.** `SDD v3.2 layers` → `SDD layers`.
- **T7 — keep verbatim.** `layers[].template` (bare filenames), `id_patterns`,
  `c4_mapping` (including the agnostic field names `sdd_layer` / `sdd_layers`),
  `layer_groups`, and `metadata.{total_layers,maintainer,template_policy}`.

`framework/registry/README.md`: ~1 paragraph — the registry is the
authoritative machine-readable definition of the layer model; templates,
READMEs, and the conformance suite defer to it; paths are framework-root-relative.

## Step sequence

1. Create `framework/registry/`; copy the registry file in; apply T1–T7.
2. Write `framework/registry/README.md`.
3. **Verify** (see below).
4. **Land:** commit; tick P1-T3 in `MIGRATION_TODO.md`; update `CHANGELOG.md`,
   `HANDOFF.md`.

## Verification

- `framework/registry/LAYER_REGISTRY.yaml` parses (`python3 -c "import yaml; …"`).
- `grep -riE 'hermes|ucx_|\bmcp\b' framework/registry/` → **empty**.
- `grep -rE 'sdd_(validate|create|score|consistency|preflight|next_action|review|remediate)' framework/registry/` → **empty**. *(Precise engine-tool pattern — `sdd_layer`/`sdd_layers` are agnostic field names and are intentionally NOT matched; a broad `sdd_[a-z]` grep would mis-flag them.)*
- `grep -rniE 'sdd v3|version: *.?3\.[0-9]' framework/registry/` → **empty**.
- Path cross-check: for each of the 8 `layers[]`, `framework/<folder><template>`
  resolves to a real file under `framework/layers/`.
- `total_layers` equals the count of `layers:` entries (8).

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | A broad `sdd_[a-z]` engine grep mis-flags the agnostic `sdd_layer` field | verification uses the precise engine-tool name pattern instead |
| R2 | `folder:` path convention ambiguous (relative to registry vs framework root) | chose framework-root-relative; documented in-file; path cross-check confirms it resolves |
| R3 | Dropping the `version` field may surprise a future validator | none expects it yet; P1-T5 is designed against this registry; `framework/VERSION` is canonical |

## Review log

> ≥2 passes required before implementation (see `CLAUDE.md` § Development workflow).

### Pass 1 — 2026-05-18T19:25:00Z

Re-read the plan against the legacy file scan. Findings, folded in above:

- **G1.** Planning scan showed the legacy registry uses `sdd_layer:` /
  `sdd_layers:` field names in `c4_mapping`. The P1-T2-style broad grep
  `sdd_[a-z]` would mis-flag these agnostic fields as engine references. →
  Verification rewritten to a precise engine-tool-name pattern (R1).
- **G2.** `folder:` paths were ambiguous after the move into `layers/`. →
  T5 fixed to framework-root-relative + an in-file comment documenting it.
- **G3.** D-0006 attaches `derived_from: "SDD v3.2"` provenance to the spec;
  the registry should carry it too. → Added to T3.

### Pass 2 — 2026-05-18T19:30:00Z

Re-read the hardened plan. Findings:

- **G4 (resolved in plan).** Confirmed dropping `metadata.changelog` leaves
  `metadata:` structurally valid (remaining keys: `framework`, `derived_from`,
  `total_layers`, `maintainer`, `template_policy`) and removes the only
  in-file engine reference — no separate engine-token edit needed.
- **G5 (scoped out, noted).** Deep semantic checks (layer `number` 1–8 dense,
  `downstream` chain consistency, `required_tags` monotonic) belong to the
  P1-T5 conformance suite, not P1-T3. P1-T3 verification stays at parse +
  engine-clean + path-resolution + `total_layers`. Recorded so P1-T5 picks
  it up.
- No new blockers. Ready to implement.
