# DOC-CHECK Plan — automated document + PR review gates

| Field      | Value                          |
|------------|--------------------------------|
| Task       | DOC-CHECK                      |
| Depends on | framework spec `0.6.0`; the per-layer `-audit`/`-fixer` skills + Hermes validation runtime (both exist) |
| Status     | PLANNED — 2026-05-25 (awaiting decisions D1–D5) |
| Feeds      | a deterministic review gate that fires on document write (#1) and on PRs (#2), both platforms |

## Objective

The flow already has **review** (`doc-<layer>-audit`, Hermes `UCR_*`) and
**remediation** (`doc-<layer>-fixer`, Hermes `UCRem_*`) plus the readiness/CHG
gates. What it lacks is **automated triggering**: nothing fires a check when a
document is written (#1) or when a PR changes documents (#2). This task adds that
triggering for a *consuming project* — a deterministic structural gate that runs
automatically — while leaving the semantic ≥90 readiness audit as the LLM
skill layer on top.

## Background — what exists vs. what's missing

| Capability | Plugin | Hermes | Framework |
|------------|--------|--------|-----------|
| Review (semantic) | `doc-<layer>-audit` skills | `UCR_*` prompts + `sdd-review-personas` | readiness gate ≥90; CHG gates |
| Remediation | `doc-<layer>-fixer` skills | `UCRem_*` prompts | — |
| **Deterministic doc validator** | **none** | `src/mcp_server/validation/*` + scoring CLI | registry + templates (the rules' source of truth) |
| **Write-time trigger (#1)** | **none** (no plugin hooks) | MCP validate/score tool (on-demand) | — |
| **PR/CI trigger (#2)** | **none** | **none** | `spec_gate.py` gates the *framework*, not instance docs |

Two facts shape the design:

1. **Consumer-facing.** This repo ships the framework + platforms; it holds **no
   SDD instance documents**. The hook + CI are things a *consuming project*
   installs; in this repo they're developed and tested against **fixtures**.
2. **Deterministic vs LLM.** Hooks (shell) and CI (Actions) are deterministic;
   the `-audit` skills are LLM reasoning. So #1/#2 enforce a **structural** gate
   (scriptable) and *defer to / nudge* the LLM audit for the semantic score.

## Scope

**In:**

- A shared, engine-agnostic, **stdlib** doc-linter (the deterministic backbone).
- **#1** — a Claude Code **PostToolUse hook** shipped in the plugin: on a write to
  `docs/<NN>_<X>/**`, run the linter on the touched file, print findings, and
  nudge the agent to run the matching `doc-<layer>-audit`. Advisory (never blocks
  the edit).
- **#2** — a reusable **GitHub Actions workflow** that runs the linter over the
  changed `docs/**` on PRs and fails / comments on structural violations.
  Shipped as a consumer template + self-tested in this repo against fixtures.
- **Both platforms:** the linter is engine-agnostic; the plugin wires the hook;
  Hermes reuses the linter for CI parity (its server-side validator already
  covers the on-demand #1 case).
- Fixtures: a small set of valid + intentionally-broken sample docs to test the
  linter, the hook, and the CI gate in this repo.

**Out (deferred / not in scope):**

- Re-implementing the **semantic ≥90 readiness score** deterministically — that
  stays the LLM `-audit` skill. The linter is structural only.
- Running the LLM audit *inside* CI (would need a Claude API key + cost +
  nondeterminism) — explicitly out; #2 is the deterministic gate.
- Converging Hermes' existing `mcp_server/validation` onto the shared linter
  (a larger refactor; flagged as a possible follow-up under D1).
- Auto-applying the `-fixer` from a hook (remediation stays a deliberate,
  reviewed step; the hook only *surfaces* findings + suggests the fixer).

## Decisions (recommendations — pending confirmation)

- **D1 — Build vs reuse the validator.** Options: (A) extract Hermes' validation
  core into a shared lib and have both consume it (clean but a big refactor of a
  working server); (B) **build a fresh minimal stdlib linter** for the structural
  subset, framework-registry-driven, no deps; (C) shell the plugin/CI out to the
  Hermes Python validator (couples the no-MCP plugin to the Hermes server —
  rejected). **Recommend B** for v1: engine-agnostic, no-deps, fast, keeps the
  plugin independent; the registry + templates are the shared source of truth, so
  divergence from Hermes' rules is bounded. Converging (A) is a later option.
- **D2 — Where the linter lives.** **Recommend `tools/sdd_doc_lint/`** (shared,
  sibling to `tests/`, like `tests/chg/spec_gate.py` is shared CI tooling) — not
  under `framework/` (ships no runtime) and not in the conformance suite (which
  validates the framework itself, not instance docs).
- **D3 — Severity.** **Recommend:** CI (#2) **blocks** on structural violations
  (deterministic, fair to hard-gate); the plugin hook (#1) is **advisory** —
  prints findings + nudges the audit, never blocks the user's write. The semantic
  ≥90 gate stays a human/LLM decision, not auto-enforced.
- **D4 — v1 check set.** Start with high-value deterministic checks: document/
  element **ID forms** (`TYPE-NN`, `TYPE.NN.SS.xxxx`), **required template
  sections** present (per the layer template), **cumulative upstream tag** count
  per layer (registry `required_tags`), **`@threshold:` tag format**, **EARS
  pattern grammar** (5 patterns, `THE…SHALL`, no `THEN` — reuses #4b), **broken
  intra-doc links / placeholder `TBD`/`PRD-XXX` leakage**. Defer anything needing
  semantic judgment to the `-audit` skill.
- **D5 — Fixtures + consumer delivery.** Add `tools/sdd_doc_lint/fixtures/`
  (valid + broken samples) tested by a new conformance/tool test; ship the CI
  workflow as `platforms/*/templates/` (or a documented snippet) for consumers to
  copy, since this repo has no `docs/` tree to gate directly.

## Approach

### Phase 1 — the shared linter (`tools/sdd_doc_lint/`)

Stdlib Python CLI: `python -m sdd_doc_lint <path-or-dir>`. Reads
`framework/registry/LAYER_REGISTRY.yaml` + the layer templates to know each
layer's required tags / sections / ID forms. Emits findings (file:line, code,
message) and a non-zero exit on error-level findings. Pure structural (D4 set).
Unit-tested against the D5 fixtures.

### Phase 2 — #1 plugin write-time hook

Add a `hooks/` dir + a `hooks` block to the plugin manifest: a **PostToolUse**
hook matching `Write|Edit` on `docs/<NN>_<X>/**`, running the linter on the file
and emitting an advisory message (findings + "run `/aidoc-flow:doc-<layer>-audit`
for the full readiness check"). Non-blocking. Documented in the plugin README +
`SKILL_AUTHORING`/hooks doc.

### Phase 3 — #2 PR/CI gate

A reusable workflow `doc-review.yml` (path-filtered to `docs/**`) that runs the
linter over the PR's changed docs and annotates/fails on violations. Self-tested
in this repo by running it against the D5 fixtures (a `docs-fixtures/` path) so
CI exercises it even though the repo has no real `docs/` tree. Shipped as a
consumer-copyable template for both platforms.

### Phase 4 — Hermes parity + docs

Hermes already validates on-demand server-side (#1 analog). Add a thin CLI/use
note so Hermes-based projects can run the same `doc-review.yml` (via the shared
linter) for #2 parity. Document the review→remediation→gate loop pointer in
`docs/PARITY.md`. (Converging Hermes' validator onto the shared linter is the
deferred D1-A follow-up.)

## Step sequence

1. **Confirm D1–D5.**
2. Phase 1: linter + fixtures + unit test → green.
3. Phase 2: plugin hook + manifest + docs; manual-test the hook fires advisory.
4. Phase 3: `doc-review.yml` + fixture self-test.
5. Phase 4: Hermes parity note + PARITY pointer.
6. **Verify** (below); **land** per phase (conventional commits); update
   `CHANGELOG.md` (project-level — tooling) + plugin/Hermes changelogs as touched.
   No framework spec change ⇒ no GATE-SPEC bump (unless we add the optional
   flow-loop doc — see Risks R5).

## Verification

- `python -m sdd_doc_lint tools/sdd_doc_lint/fixtures/valid/` exits 0;
  `.../broken/` exits non-zero with the expected codes.
- New tool unit test green; full conformance suite still green (49).
- Plugin hook: writing a fixture doc in a scratch project surfaces the advisory
  (manual check; document the manual test since hooks need a live session).
- `doc-review.yml` run against fixtures: passes on valid, fails on broken.
- `pre-commit run --all-files` clean; no engine tokens in the (engine-agnostic)
  linter; the plugin hook references no Hermes/Python-server dependency.

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Over-engineering — rebuilding the LLM audit deterministically | Hard line: linter = structural subset only (D4); semantic score stays the `-audit` skill. Phase-gated. |
| R2 | Duplication with Hermes' validator | Accept bounded duplication for v1 (B); both read the same registry/templates; converging (D1-A) is a later option. |
| R3 | Hook fires too aggressively / annoys (false-positive, cost) | Advisory only (D3), path-scoped to `docs/<NN>_<X>/**`, structural-only so it's fast + deterministic; user can disable in settings. |
| R4 | This repo has no `docs/` to gate → CI gate looks untested | D5 fixtures + a self-test job exercise the linter and workflow in-repo. |
| R5 | Should the framework spec model the loop? | Optional: a small engine-agnostic "review→remediation→gate loop" note in `framework/` would be a GATE-SPEC change (bump). Flagged as a decision, default **out** to keep this a tooling/platform change. |
| R6 | Plugin manifest hook schema correctness | Verify the Claude Code plugin `hooks` schema (PostToolUse matcher) against current docs before wiring; keep the hook script POSIX-portable. |

## Review log

> ≥2 passes before implementation (CLAUDE.md). Each pass re-reads the whole
> plan, lists findings, folds fixes back above; stop when a pass finds nothing.

### Pass 1 — 2026-05-25

- **Original draft conflated "run the audit" with the hook.** Corrected the core
  premise: hooks/CI are deterministic and cannot run the LLM audit, so the design
  centers on a deterministic structural linter with the audit as an advisory
  nudge / separate semantic layer (Background fact 2; D3; R1).
- **Missed that the repo has no instance docs.** Added the consumer-facing framing
  - fixtures (Background fact 1; D5; R4) so #1/#2 are testable here.
- **Plugin-Hermes coupling trap.** Rejected shelling the plugin out to Hermes'
  Python validator (D1-C); the plugin is the no-MCP platform and must stay
  independent — hence a shared stdlib linter (D1-B).
- **Hermes was nearly double-counted.** Clarified Hermes already covers the
  on-demand #1 via its server validator; its increment is CI parity, not a new
  validator (Phase 4).

### Pass 2 — 2026-05-25

- **Severity asymmetry made explicit.** CI blocks (deterministic, fair); the
  write-time hook never blocks (advisory) — folded into D3 + R3 so the two
  triggers aren't held to the same bar.
- **Scope discipline.** Re-confirmed the linter is structural-only and phased;
  the semantic ≥90 score and any Hermes-validator convergence are explicitly
  out / deferred (Scope-Out; R1/R2). Prevents the linter from sprawling into a
  re-implementation of the audits.
- **Framework-spec neutrality.** Confirmed this is tooling/platform work with no
  `framework/` edit (no GATE-SPEC bump) unless the optional flow-loop doc (R5) is
  adopted — kept default-out.
- No further findings — implementable pending D1–D5 confirmation.
