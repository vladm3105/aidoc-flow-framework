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

**What you get:**

- Templates + schemas for every layer.
- Cumulative `@upstream:` traceability tags from BRD all the way to code.
- Deterministic lint (`sdd_doc_lint`) for structural correctness.
- Conformance-tested outputs across both platforms.

**Use it when** you want AI-assisted development backed by a verifiable
specification trail, not ad-hoc prompts that produce inconsistent or
hard-to-audit output.

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
| **Claude Code plugin** | Native Claude Code (skills / agents / commands) | `claude-code-plugin/v0.10.1` (`platforms/claude-code-plugin/`) |

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
**post-cutover development** — latest project release `v1.1.0`, framework spec
`0.13.0`. The Claude Code plugin (`platforms/claude-code-plugin/`) is currently a **pre-1.0 preview** (v0.6.2); APIs and surfaces may change before 1.0. The framework spec is at `0.13.0`. Post-v1.0 work to date:

- the project adaptation overlay (`framework/governance/ADAPTATION.md` + the closed-knob `ADAPTATION_SURFACE.yaml`);
- the **GATE-SPEC** change-management gate (`framework/governance/chg/`);
- the **review-team** model (multi-persona crews + scoring/conflict policy — `framework/governance/REVIEW_TEAM.md` / `REVIEW_CREWS.yaml`);
- the **C4 + DFD + sequence** diagram standards (`framework/governance/DIAGRAM_STANDARDS.md`);
- the **token-efficient authoring** governance (`framework/governance/AUTHORING_STYLE.md`) wired into every layer's `_size_target` and into every audit skill;
- the **`.aidoc/` provenance tier** — committed audit/review/remediation/validation/security/quality reports (`framework/docs/AIDOC.md`);
- the **pre-deployment acceptance test suite** (`tests/scripts/test-acceptance.sh` + [`tests/ACCEPTANCE.md`](tests/ACCEPTANCE.md)) that drives every active plugin surface element (50 skills + 11 agents + 1 command + 1 hook) against a named example's seed as the release gate, with resume on interrupt, partial-execution flags (`--element`, `--from-layer`, `--to-layer`, `--dry-run`), and `--promote` to commit the produced chain;
- the **`adversary` lens partition** (CHAOS-SEC-SPLIT-001, framework `0.12.0`) — split into `chaos_engineer` (reliability/NFR/failure-mode) + `security_engineer` (threat-model/security-controls) with per-layer crew weight redistribution in `REVIEW_CREWS.yaml`;
- the **review-saga lifecycle promoted to spec** (SAGA-PARITY-001 Phase 1, framework `0.13.0`) — `REVIEW_SAGA.md` + `saga.schema.json` codify the engine-agnostic state machine + journal schema + break-circuit policy that both platforms align to;
- the **plugin BRD saga driver** (SAGA-PARITY-001 Phase 2 + Amendment 1, plugin `0.6.1`) — `tools/saga_driver.py` (Python stdlib-only) replaces cooperative-enforcement SKILL-prompt loop with preemptive script-driven enforcement; vendored alongside the framework bundle in the plugin distribution;
- the **content sub-checks** (REVIEW-CALIBRATION-001, plugin `0.6.2`) — A1 cell-actionability + A2 assumption-capture + A3 cross-section pointer-validity (auditor) + BA1 acceptance-criterion testability (business_analyst) + SE1 deferred-decision safety (security_engineer), applied uniformly across all 8 layer audit SKILLs;
- the **plugin-first development sequencing** (2026-06-06) — features land on the plugin first; Hermes follow-on batches per [`plans/HERMES-BACKLOG.md`](plans/HERMES-BACKLOG.md);
- pre-commit + CI security tooling (CodeQL, bandit, detect-secrets, pip-audit, gitleaks, Dependabot).

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
