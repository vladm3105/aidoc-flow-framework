# IPLAN ↔ Iplanic Integration — DEFERRED

**Status:** Deferred until iplanic stabilizes (out of `*-draft` schema versions).
**Decided:** 2026-06-01
**Trigger to revive:** Iplanic ships a non-draft (1.x stable) `iplan-document.schema.json`.

## Why deferred

[Iplanic](https://github.com/vladm3105/aidoc-flow-iplanic) is intended to be a
hosted control plane that manages IPLANs created by this framework — importing,
validating, dispatching to remote executors, and recording evidence. As of this
note, iplanic ships:

- A schema baseline marked `schema_version: "1.2-draft"` across every template.
- Internally consistent contract tests (~27, schema-introspection only).
- **No runtime, no API, no validation code, no working import pipeline** (per
  `iplanic/docs/PROJECT_GUIDE.md`).

Coupling a framework release (today: 0.11.0) to a deliberately pre-stable
upstream contract creates release-coordination risk for no immediate benefit:
no IPLAN today actually flows through iplanic. The framework's IPLAN at
Layer 8 (`framework/framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml`) remains
the source of truth for authoring and is consumed by human + AI implementers
directly.

When iplanic stabilizes, the integration is a small adapter (~400 LOC) on the
framework side. No changes to iplanic's contract are needed; iplanic's role
is downstream consumer.

## What was explored (don't re-derive)

A full integration plan was drafted and gap-reviewed. Key findings worth
preserving so a future revival doesn't repeat the mistakes:

### Schema mismatches discovered against `iplanic/schemas/iplan-document.schema.json` (1.2-draft)

| # | Adapter behavior | Why it failed |
|---|---|---|
| 1 | Emitted `metadata.canonical_hash` | Iplanic doesn't declare this field; `additionalProperties: false` rejects it. Iplanic computes its own hash on import. |
| 2 | `_normalize_status` shared between `files[]` and `todos[]` outputs | Iplanic uses different enums for these: `files[].status ∈ {Not Started, In Progress, Partial, Done, Skipped}` vs `todos[].status ∈ {Not Started, Queued, Running, Blocked, Completed, Failed, Cancelled}`. The shared function emitted `"In Progress"` for TODOs, which is invalid. Must split into per-context normalizers. |
| 3 | `_framework_version()` used `parents[3]/framework/VERSION` | Real path is `parents[2]/framework/VERSION`. Adapter threw on first call. |
| 4 | Mapped `"In Progress" → "Review"` for document status | Semantically wrong — `Review` means "under review", not "actively being worked on". Both `Draft` and `In Progress` should map to `Draft`; only `Completed → Approved`. |
| 5 | `target_files[].action` hardcoded `"create"` | Should derive from file status: NOT_STARTED→create, IN_PROGRESS→modify, DONE→verify. |
| 6 | TODO `type` hardcoded `"create"`/`"edit"` from status | Should derive from file path (tests/ → `test`, .md → `document`, otherwise create/edit). |
| 7 | Empty `commands.execute.items` violates `minItems: 1` | Adapter must enforce non-empty implementation/validation commands at entry, or refuse to adapt. |
| 8 | Empty `executor_work.todos[]` when `file_manifest.files` empty violates `minItems: 1` | Validate `file_manifest.files` non-empty at adapter entry. |
| 9 | `handoff.blockers` aggregated from sessions could become list-of-list | Use `_normalize_refs` defensively. |
| 10 | `build_intent` defaulted to bracket-placeholder strings (`"[not specified]"`) | Passes schema (`minLength: 1`) but produces auditable garbage. Adapter should `raise ValueError` instead. |

### Sequencing trap

Adding an optional `scope:` section to `IPLAN-TEMPLATE.yaml` (with `_size_target: 200`) BEFORE landing a `STRUCT01 _required: false` honor breaks STRUCT01 for every existing IPLAN. Either bundle atomically or land the STRUCT01 change first.

### Tautological tests

The drafted test for `_required: false` exercised an IPLAN body whose template
didn't yet declare the section — so STRUCT01 had nothing to fire on regardless
of the patch. Future test must inject a fake template with the override into a
tmp dir + point `registry` at it, so the new code path is actually exercised.

## What a future revival should look like

When iplanic ships `1.0` (or `2.0`, non-draft):

1. **Dry-run spike** (half-day): write `to_iplanic()` against the fixed schema
   directly; iterate until `jsonschema.Draft202012Validator(schema).validate(to_iplanic(golden))`
   passes for the layer-8 golden. No new plan until this works.
2. **Then plan around the working code** — derive the task list from what the
   spike actually does, not from theoretical mappings.
3. **Architectural shape** that's still right (don't re-debate):
   - One-way adapter, framework → iplanic. Never reverse.
   - Vendor iplanic schema with pinned SHA + provenance file.
   - Add ~5 universally-useful optional fields to framework IPLAN template
     (`document_control.{summary, problem, outcome, non_goals}` + optional `scope:` section).
     These improve plan-authoring quality even without iplanic.
   - STRUCT01 must honor `_required: false` per-section override.
   - Adapter lives at `framework/tools/iplan_export/`, ships with the framework
     (iplanic consumes the framework as a dep, not vice versa).
   - Round-trip test: every committed framework IPLAN → adapter → schema-validate
     against vendored iplanic schema. Gates every PR.
   - Snapshot regression test (mask non-deterministic fields:
     `created_at`, `updated_at`, any hash).
4. **Estimated effort when iplanic stable**: ~3-5 days end-to-end (vs. weeks
   today, because the schema field shapes will be fixed).

## What NOT to do in the meantime

- **Do not** start adding iplanic-shaped fields to the framework template
  speculatively (`source_framework_version`, `lineage.upstream.{brd,prd,...}_references`).
  Iplanic field names are still in flux.
- **Do not** vendor the draft schema into the framework. It will move.
- **Do not** add a "preview" or "experimental" adapter behind a feature flag.
  Half-done integrations rot.

## What CAN be done independently (if value emerges)

If `document_control.{summary, problem, outcome, non_goals}` + optional `scope:`
section turn out to be useful for plan-authoring quality on their own — i.e.
authors want to express intent + scope formally regardless of iplanic — those
can ship as a minor framework bump (0.11.x → 0.12.0) with zero iplanic coupling.
This is a separate decision, not part of this deferral.

## References

- Iplanic project: <https://github.com/vladm3105/aidoc-flow-iplanic>
- Iplanic schema this gap analysis was based on: pinned in iplanic main as of
  commit `4536e02` (2026-05-31).
- Framework IPLAN source of truth: `framework/layers/08_IPLAN/IPLAN-TEMPLATE.yaml`.
- Framework spec at deferral time: 0.11.0 (post PR #40 + #42 merge).
