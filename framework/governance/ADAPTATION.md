# Project Adaptation Surface

Engine-agnostic specification of **how a consuming project may adapt the SDD
flow to its own needs without forking the framework**. It defines a *closed*,
declarative set of preferences ("knobs") that a project declares once; any
conforming engine reads them when authoring and auditing artifacts.

The machine-readable companion is `ADAPTATION_SURFACE.yaml` — the authoritative
list of knobs, constraints, and the mandatory/skippable layer split. This
document is the human-readable contract; the YAML is what tools and the
conformance suite parse.

## 1. Principles

- **Closed surface.** Only the knobs enumerated in `ADAPTATION_SURFACE.yaml`
  are honored. An engine ignores any unknown or out-of-surface key. Adding a
  knob is itself a framework-spec change.
- **Declarative, not behavioral.** A profile supplies *data* — a switch, a
  bound, a term. It never carries logic and never rewrites how a skill works.
  This keeps the surface safe to honor on untrusted project input.
- **Project-local.** Adaptation lives in the consuming project, never in this
  spec. The framework ships only this contract; it ships no project profile.
- **Never weakens a check.** No knob may relax a blocking quality gate. Where a
  knob touches a threshold it may only make it *stricter* (see §4.3).
- **Reproducible.** The input an engine reads at runtime is fully
  version-controlled, so the same project audits identically on any machine and
  in CI (see §3).

## 2. The profile

A project declares its adaptation in a profile file:

```
.aidoc/profile.yaml          # the project profile (version-controlled)
```

Minimal shape:

```yaml
schema_version: "1.0.0"      # the ADAPTATION_SURFACE.yaml schema it targets
active_layers: [BRD, PRD, EARS, SPEC, TDD, IPLAN]
section_toggles:
  ADR: { security: on }
audit_threshold:
  ADR: 95
glossary:
  "user": "account holder"
```

Every key must resolve to a knob in `ADAPTATION_SURFACE.yaml`. An absent profile
means "framework defaults" — adaptation is purely additive.

## 3. Scopes and reproducibility

Two scopes are supported, but only one is read at runtime:

- **Project profile — `.aidoc/profile.yaml`** — the single input an engine reads
  when authoring or auditing. Version-controlled, so audits are reproducible in
  CI (which has no developer home directory).
- **User-global seed — `~/.aidoc/profile.yaml`** — an *authoring-time* seed
  expressing a developer's house preferences across all their projects. It is
  **not** a runtime input. When a project profile is created or refreshed, the
  seed is merged in (the project value wins on conflict) and the result is
  **materialized** into the committed `.aidoc/profile.yaml`.

Effective precedence is therefore `framework defaults < user-global seed <
project`, with the merge performed at authoring time so the runtime input stays
version-controlled. A project value that overrides the seed for the same knob is
a deliberate per-project deviation and is recorded as a learning (see the
knowledge-extraction overlay).

## 4. The surface (v1 — four knobs)

The authoritative definitions, types, and consumer roles live in
`ADAPTATION_SURFACE.yaml`. This section is the rationale.

Consumer roles are engine-agnostic: **authoring** (creating an artifact),
**audit** (running a quality gate), **traceability** (checking cross-references),
**scaffolding** (creating the project structure). Each engine maps its own tools
to these roles.

### 4.1 `active_layers`

Which of the 8 layers are in play for this project. A project may disable only
layers in the **skippable** set (`ADAPTATION_SURFACE.yaml: layers.skippable`,
v1 = `BDD`, `ADR`); the **mandatory** layers that anchor the intent → plan
spine cannot be disabled.

**Cascade rule.** Disabling a skippable layer removes it from the required
upstream tags and the `can_reference` set of every downstream layer, so the
chain stays internally consistent. Example: disabling `ADR` means `SPEC` no
longer requires an `adr` tag and the audit does not flag its absence.

Honored by: **scaffolding** (scaffolds only active layers), **traceability** and
**audit** (never demand a reference to, or flag the absence of, a disabled
layer).

### 4.2 `section_toggles`

Per-layer on/off switches for the template's **declared-optional** sections
only. Required sections are not toggleable — turning a required section off is
out of surface and ignored.

Honored by: **authoring** (omits/includes the section) and **audit** (a
toggled-off optional section is not a finding; a missing *required* section
still is).

### 4.3 `audit_threshold`

The layer-audit quality-gate score (the framework default is the value each
layer's audit defines). **Raise-only:** a project may set the threshold equal to
or higher than the framework default — making the gate *stricter* — never lower.
A value below the default is out of surface and ignored. This preserves the
"never weakens a check" principle.

Honored by: **audit**.

### 4.4 `glossary`

Preferred-term substitutions (`default term → project term`). **Mechanics:**
applied to **generated prose only**. Audits do **not** enforce terminology in
v1 — a glossary is a convenience, not a gate. This is the one knob a user-global
seed commonly carries.

Honored by: **authoring**.

## 5. How an engine consults the profile

The framework ships no runtime code; an engine honors the profile by
instruction, not by execution. Each adapting tool declares which knobs it honors
and, before applying defaults, merges the project profile and applies only those
knobs. The canonical instruction:

> Before applying defaults, read the project profile (`.aidoc/profile.yaml`).
> Honor only the knobs this tool declares; ignore any unknown or out-of-surface
> key, and any value that violates a knob's constraint (e.g. a lowered
> `audit_threshold`).

An engine that cannot find a profile proceeds with framework defaults.

## 6. Versioning

`ADAPTATION_SURFACE.yaml` carries a `schema_version`; a project profile records
the `schema_version` it targets. Changing the surface (adding, renaming, or
removing a knob, or changing the mandatory/skippable split) is a framework-spec
change and moves `framework/VERSION` accordingly.

## 7. Learnings log (raw signal for promotion)

A project may keep a learnings log alongside its profile:

```
.aidoc/learnings.md
```

Each entry records one observed deviation from a framework default — the raw
signal a later, **on-demand** knowledge-extraction step mines to decide whether a
local adaptation deserves promoting into the framework. Entry shape (one YAML
list item per learning):

```yaml
- ts: 2026-05-23T16:40:00Z      # ISO 8601 UTC
  layer: EARS                    # layer name | "utility:<name>" | "cross"
  knob: section_toggles.security # surface path, or "none" (not yet a knob)
  default: <framework default>
  chosen: <value the project used>
  rationale: <why the deviation>
  recurrence: 1                  # bumped when the same (layer, knob, chosen) recurs
  scope: project                 # project | user-global
  conflict: false                # true if the project overrode the user-global seed
```

**Capture is best-effort** — entries are appended when a profile override is
applied or a correction is made; `recurrence` *weights* generalizability, it does
not decide it.

**Promotion routes by owner.** A change to the framework **spec** (a template, a
governance rule, or the registry) is routed through **change management** (CHG);
a change to an **engine's own authoring guidance** is an ordinary platform
review. Spec-level promotion additionally depends on the CHG spec-change gate,
which is not yet built.

## 8. Conformance

The suite asserts, against `ADAPTATION_SURFACE.yaml`:

- the surface parses and is a closed set;
- every knob a tool declares is in the surface;
- the `audit_threshold` constraint is raise-only;
- no project profile or learnings file is committed under `framework/`;
- this document and the surface YAML carry no engine-specific tokens.

## 9. Out of scope (v1)

- `id_format` as a knob — deferred pending an `ID_NAMING_STANDARDS.md` review to
  enumerate genuinely project-selectable conventions; the narrow-surface
  principle favors not inventing options.
- **Spec-level** promotion (the CHG path in §7) — deferred until the CHG
  spec-change gate is built. Until then the extraction step still drafts
  spec-level proposals, but they cannot be run through a gate; engine-level
  guidance promotion (ordinary platform review) is unaffected.
