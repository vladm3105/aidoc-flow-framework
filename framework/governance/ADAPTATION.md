# Project Adaptation Surface

## Document Control

| Field | Value |
|-------|-------|
| Version | 1.1 |
| Status | Approved |
| Last Updated | 2026-10-07 |
| Author | Framework Maintainer |
| Framework Version | 0.88.4 |


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

## 4. The surface (v1 — fifteen knobs)

The authoritative definitions, types, and consumer roles live in
`ADAPTATION_SURFACE.yaml`. This section is the rationale.

Consumer roles are engine-agnostic: **authoring** (creating an artifact),
**audit** (running a quality gate), **traceability** (checking cross-references),
**scaffolding** (creating the project structure). Each engine maps its own tools
to these roles.

### 4.1 `active_layers`

Which of the 10 layers are in play for this project. A project may disable only
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

### 4.5 `review_mode`

Selects review/remediation depth: `team` runs the multi-persona review crew;
`single_pass` runs a single agent applying every lens in one context. **Never
weakens the gate** — the deterministic structural floor plus the
no-unresolved-P0/P1 rule holds in either mode; `single_pass` trades reviewer
diversity for cost, not rigor. The framework default is `team` at gates and
`single_pass` at write-time. See `REVIEW_TEAM.md` for the crew mechanics.

Honored by: **authoring** and **audit**.

### 4.6 `quality_loop_max_iterations`

The default cap on review→remediate cycles before the saga transitions to
`ESCALATED` (see `REVIEW_REMEDIATION_FLOW.md` §"Iteration cap"). Range
1–10; a value outside the range is treated as malformed and falls back to the
default (`3`). An engine reading it from the profile must handle
missing-file / missing-field / malformed-value by falling back to the default.
This bounds the loop; it does not weaken any gate.

Honored by: **audit**.

### 4.7 `ci_bindings`

Where a consuming project pins the platform mechanics
`CI_AUTONOMOUS_PR_STANDARD.md` points at: verification-tier latency ceilings
(Invariant 2), required checks and branch policy (Invariant 3), runners,
workflows, and the integration branch. Values are platform-specific and opaque
to the framework — a ceiling is a duration in whatever form the platform reads,
a branch policy is the platform's own rule object. Unset keys fall through to
framework defaults per the precedence chain in §2. **Never weakens a gate** —
ceilings keep the static < integration < promotion ordering, and required
checks still report conclusively on every merge request per Invariant 3.
Projects adopting `CI_AUTONOMOUS_PR_STANDARD.md` populate this knob; without
it each consumer invents its own profile shape for the same bindings.

Honored by: **scaffolding** (wires the project's CI surface from the pinned
values).

### 4.8 `exec_max_files`

How many distinct files one execution task may create or modify. Without a
standard knob each engine invents its own blast-radius limit and profiles are
not portable. Range 1–100 (`8` default); out-of-range values are malformed
and fall back to the default. A cap only — it never widens any gate.

Honored by: **authoring** and **audit**.

### 4.9 `exec_max_diff_lines`

How large one execution task's diff may grow (added-plus-removed lines).
Range 1–10000 (`600` default); out-of-range values are malformed and fall
back to the default. A cap only — it never widens any gate.

Honored by: **authoring** and **audit**.

### 4.10 `exec_protected_paths`

Repository-relative path prefixes an execution task must never write (e.g.
`framework/archive/`, `.git/`). Non-string or blank entries are ignored; the
list is **additive to engine built-ins only** — listing a path never
unprotects anything. Default `[]` (no project-level additions). This bounds
the blast radius; it does not weaken any gate.

Honored by: **authoring** and **audit**.

### 4.11 `exec_test_timeout_s`

Per-test-command wall-clock ceiling in seconds. Range 30–3600 (`300`
default); out-of-range values are malformed and fall back to the default.
A ceiling only — it never weakens any gate.

Honored by: **audit**.

### 4.12 `exec_max_attempts`

How many patch→verify cycles an execution task runs before it stops
retrying. The saga lifecycle already bounds *review* loops
(`quality_loop_max_iterations` → `ESCALATED`); this is the matching
bound for *execution* attempts, which otherwise retry unboundedly. Range
1–10 (`3` default, mirroring the review-loop cap); out-of-range values are
malformed and fall back to the default. This bounds the loop; it does not
weaken any gate.

Honored by: **authoring** and **audit**.

### 4.13 `exec_token_budget`

Total model-token budget per execution task, retries included — without it
cyclic retry compacts context monotonically across attempts and cost is
unbounded. Range 10000–2000000 (`200000` default); out-of-range values are
malformed and fall back to the default. A budget only — it never widens any
gate.

Honored by: **authoring** and **audit**.

### 4.14 `exec_wall_clock_budget_s`

Total wall-clock budget in seconds per execution task, retries included.
Range 60–14400 (`1800` default); out-of-range values are malformed and fall
back to the default. A budget only — it never widens any gate.

Honored by: **authoring** and **audit**.

### 4.15 `exec_failure_summary_lines`

Fixed size in lines of the failure summary carried across retries, so
retried context stays compact instead of accumulating full logs. Range
5–200 (`30` default); out-of-range values are malformed and fall back to the
default.

Honored by: **authoring** and **audit**.

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

### 5.1 Live policy updates (validate-then-swap)

§5 and §6 describe the profile at a single instant. A long-lived engine
(agent runtimes, daemon-backed authoring loops) MAY additionally pick up
profile edits without a restart — by polling or by watching the profile
file — under this discipline:

- **Validate, then atomically swap.** On observing a change, parse and
  validate the candidate profile *off to the side* (known knobs only,
  constraints hold, `schema_version` matches a surface the engine
  understands). Only a fully valid candidate replaces the active
  policy, in one atomic swap. The engine never runs on a half-parsed
  policy.
- **Schema-versioned policy.** The active policy always records the
  `schema_version` it was validated against (the same field §6
  describes). A candidate targeting a surface version the engine does
  not understand is rejected as invalid input.
- **Keep last-good.** Any invalid candidate — missing file mid-write,
  malformed value, unrecognized `schema_version` — is discarded and
  the engine keeps serving the last-good policy. Load-time fallback
  (§4 knob constraints, `ADAPTATION_SURFACE.yaml` defaults) is
  unchanged: this section adds the live-update dimension only and
  alters no load-time semantics.

Polling/watching is engine-local and out of framework scope; the
contract above governs only what an engine does with what it reads.

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
governance rule, or the registry) is routed through **change management** (CHG)
via the **GATE-SPEC** meta gate (`chg/gates/GATE-SPEC_FRAMEWORK.md`); a change to
an **engine's own authoring guidance** is an ordinary platform review.

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

## 10. Project overrides (`.aidoc/project/`)

A project may place files in `.aidoc/project/` using the same directory
structure as `framework/`. When an engine reads a template, rule, or
playbook, it checks `.aidoc/project/` first. If the file exists, it
replaces the framework version. If not, the framework version applies.

### Override structure

```
.aidoc/project/
├── layers/                    # template overrides
│   └── 06_SPEC/
│       └── SPEC-TEMPLATE.yaml
├── governance/                # rule overrides
│   ├── DOC_GOVERNANCE_CORE.md
│   └── ...
└── playbooks/                 # playbook overrides
    └── 01_BRD/
        └── auditor.md
```

### Discovery rule

1. Check `.aidoc/project/{same-path}` first
2. If the file exists there, use it (project override)
3. If not, fall back to `.aidoc/framework/{same-path}` (shared framework)

This is the same pattern as software: project-local config overrides
global defaults (e.g., `.eslintrc` vs `node_modules/.eslintrc`).

### Constraints

- **Project-local only.** Overrides live in the consuming project, never
  in the shared `framework/` directory.
- **Same structure.** Override files must mirror the framework's directory
  structure and filename exactly. An engine matches by path, not by content.
- **No weakened checks.** A project override may not weaken a blocking
  quality gate. It may only add sections, tighten thresholds, or customize
  wording.
- **Versioned.** Project overrides are committed alongside `profile.yaml`
  and carry the `framework_version` they were authored against.

### Symlink convention

`.aidoc/framework/` is a symlink to the shared framework directory. The
canonical path is declared in `profile.yaml` as `framework_path`.

New files use `.aidoc/framework/` as the canonical path. The root `framework/`
symlink has been removed — all references must use `.aidoc/framework/`.

## 11. Enforcement adaptation (mandatory for all consuming projects)

When adapting the framework, consuming projects MUST propagate these enforcement mechanisms:

| Step | What | Required |
|------|------|----------|
| 1 | Add governance gate to project CLAUDE.md (§3.4 — NON-NEGOTIABLE) | Yes |
| 2 | Add session-start verification checklist (10 items, before any code work) | Yes |
| 3 | Add §3.4.1 CHG post-creation validation to project DOC_GOVERNANCE_CORE.md | Yes |
| 4 | Install framework hooks (ch-gate-check.sh in hooks.json PreCommit) | Yes |
| 5 | Verify enforcement works (test: say "build" → agent stops at gate) | Yes |

These steps ensure defense-in-depth: CLAUDE.md (prompt-level), hooks (tool-level),
skills (process-level), and DOC_GOVERNANCE_CORE.md (documentation-level) all enforce
the CHG gate independently.
