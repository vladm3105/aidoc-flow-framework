# AI Doc Flow Framework

**AI Doc Flow Framework** is a structured workflow for
**Specification-Driven Development (SDD)** with AI coding assistants. It
guides a project through an 8-layer documentation chain — from business
intent down to executable implementation plans — so AI tools read, audit,
and act on a verifiable spec rather than ad-hoc prompts.

```text
BRD  →  PRD  →  EARS  →  BDD  →  ADR  →  SPEC  →  TDD  →  IPLAN  →  Code
business  product  formal  executable  decision  component  test    impl
intent    reqs     reqs    scenarios   record    contract   suite   plan
```

Each layer has its own template, contract, and quality gate. The framework
owns the engine-agnostic specification; two independent platforms (Hermes
MCP server, Claude Code plugin) each implement it. Both pass the same
conformance suite.

## The problem

Driving AI assistants from free-form prompts carries three recurring costs.
Output varies between runs, because the prompt is not retained as a reviewable
artifact. There is no recorded link from a business requirement to the code that
implements it, so checking or auditing the result means re-reading everything.
And nothing measures whether a step is complete enough to build on — "it looked
right" is the only gate.

Specification-Driven Development replaces the free-form prompt with a fixed
chain of documents. Each of the eight layers has a defined template, a set of
required references to the layers above it, and a numeric quality gate that must
be met before the next layer is generated. Each step is therefore reproducible
(it is a committed artifact), traceable (each element cites the upstream
elements it derives from), and checkable (each layer is scored against a rubric
and structurally linted).

## What the framework provides

- **Eight layered artifacts** — BRD, PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN. Each
  is a document type with a defined template and schema; a layer may reference
  only the layers before it.
- **Cumulative traceability** — `@upstream:` tags link every element to the
  elements it derives from, from business intent down to code. Broken or missing
  links are detectable, not silent.
- **Per-layer quality gates** — each layer is scored against a rubric; downstream
  generation is gated on a minimum score, so an underspecified layer is caught
  before it propagates.
- **Multi-persona review** — each layer is reviewed from a defined set of lenses
  (for example architecture, security, traceability) with weighted scoring and a
  recorded verdict (`framework/governance/REVIEW_TEAM.md`).
- **Deterministic structural lint** — `sdd_doc_lint` checks required sections, ID
  formats, and reference resolution the same way on every run.
- **Committed provenance** — the `.aidoc/` tier keeps audit, review, remediation,
  validation, and security records beside the output, so "how was this produced?"
  is answerable without a re-run.
- **Two engines, one contract** — the specification is engine-agnostic; a Hermes
  MCP server and a Claude Code plugin each implement it, and both pass the same
  conformance suite.

## Spec-driven vs. ad-hoc prompting

| Dimension | Ad-hoc prompting | This framework |
|-----------|------------------|----------------|
| Reproducibility | Output varies per run; the prompt is not kept as an artifact | Each layer is a committed document generated from a fixed template |
| Traceability | No recorded link from requirement to code | `@upstream:` tags link every element to the ones it derives from |
| Review | Re-read the whole output to judge it | Each layer is scored against a rubric before the next is generated |
| Audit trail | None unless added by hand | `.aidoc/` keeps audit, review, and remediation records beside the output |
| Structural correctness | Checked manually | `sdd_doc_lint` checks it deterministically |

## When to use it

Use the framework when outputs must stay consistent and auditable as work scales
across a team or over time — where "it passed review" needs to mean something
traceable to a spec, not a one-off prompt that happened to look right. For a
single throwaway script, the layered chain is more structure than the task
needs.

## Architecture

```
framework/                  Engine-agnostic specification (the shared contract)
platforms/
  hermes/                   Platform A — Hermes AI (MCP-server engine)
  claude-code-plugin/       Platform B — Claude Code plugin (native engine)
tests/
  conformance/              Shared suite both platforms must pass
```

The `framework/` spec defines the 8-layer SDD flow
(BRD → PRD → EARS → BDD → ADR → SPEC → TDD → IPLAN → Code), schemas, templates,
and governance. Each platform is an independent implementation of that spec —
they share the specification and nothing else, and both pass the same
conformance suite at `tests/conformance/`.

## Platforms

| Platform | Engine | Release |
|----------|--------|---------|
| **Hermes AI** | MCP server | `hermes/v0.3.0` (`platforms/hermes/`) |
| **Claude Code plugin** | Native Claude Code (skills / agents / commands) | `claude-code-plugin/v0.12.0` (`platforms/claude-code-plugin/`) |

See [`docs/PARITY.md`](docs/PARITY.md) for the capability comparison and a
"which platform should I use?" guide.

### Install the Claude Code plugin

This repo doubles as a plugin marketplace (`.claude-plugin/marketplace.json`).
From Claude Code:

```
/plugin marketplace add vladm3105/aidoc-flow-framework
/plugin install aidoc-flow@aidoc-flow-framework
```

## Status

The migration is complete (cutover shipped as `v1.0.0`); the project is now in
**post-cutover development** (latest project release `v1.1.0`), tracking
framework spec `0.16.0`. The Claude Code plugin is a **pre-1.0 preview** — APIs
and surfaces may change before 1.0. Platform release versions are in the
[Platforms](#platforms) table above.

Post-v1.0 development — delivered and planned — is tracked in
[`ROADMAP.md`](ROADMAP.md); per-release detail is in
[`CHANGELOG.md`](CHANGELOG.md). Development lands on the Claude Code plugin
first, with Hermes follow-on batches per
[`plans/HERMES-BACKLOG.md`](plans/HERMES-BACKLOG.md).

## Contributing

Enable the pre-commit hooks before committing:

```sh
pip install pre-commit && pre-commit install
```

See `.pre-commit-config.yaml` for the hook set and [`SECURITY.md`](SECURITY.md)
for the vulnerability-reporting policy.

## Documentation

- `ROADMAP.md` — delivery plan and post-v1.0 work (migration complete at `v1.0.0`).
- `CHANGELOG.md` — project-level changelog.
- `SECURITY.md` — security policy and vulnerability reporting.
- `docs/REPO_STRUCTURE.md` — repository layout (as-built).
- `docs/PROJECT.md` — versioning, branching, milestones, conformance, change management.
- `docs/TAGGING.md` — git-tag policy (release + bookmark tags).
- `docs/PARITY.md` — Hermes ↔ plugin capability comparison.
- `framework/README.md` — the engine-agnostic SDD specification.
- [`framework/docs/AIDOC.md`](framework/docs/AIDOC.md) — the `.aidoc/` provenance tier (third committed documentation tier).
- [`tests/ACCEPTANCE.md`](tests/ACCEPTANCE.md) — pre-deployment acceptance-test methodology (driver, log layout, schema, `--promote`, phase definitions, partial-execution flags, CI integration).
- [`tests/README.md`](tests/README.md) — tiered test-suite navigation hub.
- [`plans/ACCEPTANCE-SUITE-HISTORY.md`](plans/ACCEPTANCE-SUITE-HISTORY.md) — per-PR implementation timeline + design evolution + lessons learned for the acceptance suite.
- [`docs/STARTUP_HANDOFF.md`](docs/STARTUP_HANDOFF.md) — historical session brief from the Phase-3/4 migration period.

## Pre-migration history

This project was migrated from the pre-migration `ucx_framework` (v0.20.4)
into the multi-platform structure above. The **pristine pre-migration project**
is preserved on the protected, read-only branch
**`legacy-ucx-v3.2-read-only`** (`git checkout legacy-ucx-v3.2-read-only`).
The full migration record — per-task plans, audits, verify records, and the
decision log — lives under `plans/`.
