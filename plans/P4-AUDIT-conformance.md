# Phase 4 Audit — Conformance & Independence

| Field      | Value                                |
|------------|--------------------------------------|
| Audit of   | current state vs Phase 4 exit conditions |
| Targets    | `tests/conformance/`, `.github/workflows/`, both platforms |
| Produced by| P4-T0                                |
| Date       | 2026-05-20T23:30:00Z                 |

## Summary

Phase 4 closes the gaps the prior phases deferred. Unlike P2/P3, there
is **no source-content port** — both platforms exist, both pass the
framework's 25-test conformance suite, both declare
`FRAMEWORK_SPEC_VERSION = 0.1.0`. The work is **mechanical** and
**bounded**:

1. **Conformance gap:** the suite's documented "Platform-conformance
   contract" has **4 bullets**; **0 are implemented**. 3 are
   statically testable in-repo today; 1 requires runtime exercise
   (deferred).
2. **CI gap:** `.github/workflows/` is empty. Need 3 minimal workflows
   (conformance, Hermes tests, plugin smoke).
3. **CHANGELOG gap:** both platforms lack `platforms/<name>/CHANGELOG.md`.
   Symmetric retrofit needed.
4. **README gap:** Hermes README is still Phase-0 placeholder (27
   lines). Should mirror the populated 82-line plugin README.
5. **LICENSE gap:** no repo-root `LICENSE` file. Plugin manifest
   declares `"license": "MIT"` as a placeholder.
6. **Parity report:** no `docs/PARITY.md` exists. Need to document
   feature gaps between Hermes and the plugin.

Plus carried-known-issues from P3 (skill schema-version naming, ~150
stale `framework/<X>` refs in plugin) — those are **content-design
questions**, scoped out of Phase 4 (resolution post-Phase-3 cleanup
or post-v1.0).

## 1. Inventory — current state

### `tests/conformance/`

```
25 tests across 5 modules:
  test_governance.py    (framework/governance/ + chg/)
  test_layers.py        (framework/layers/0N_X/)
  test_registry.py      (framework/registry/LAYER_REGISTRY.yaml)
  test_root.py          (framework/ top-level files)
  test_spec_hygiene.py  (no engine tokens in framework/)
  test_version.py       (framework/VERSION format)
```

All scan **only `framework/`** (`_spec.py` defines `FRAMEWORK =
REPO_ROOT / "framework"`). **No test asserts against any platform**
today.

### `tests/conformance/README.md` — Platform-conformance contract

Written at P1-T5; documents what Phase 4 must implement:

> A platform (Hermes, the Claude Code plugin) conforms to the
> framework when:
>
> - **PC1.** it declares the `framework_spec_version` it implements
>   (see `framework/VERSION`);
> - **PC2.** every artifact it generates validates against the
>   matching layer template in `framework/layers/` and the
>   `id_patterns` in the registry;
> - **PC3.** it enforces the traceability rules the registry encodes
>   (`required_tags`, `can_reference`, `downstream`);
> - **PC4.** it carries no expectation of the other platform's
>   engine.

Counts: **4 bullets, 0 implemented.**

### `.github/`

```
.github/
├── CODEOWNERS
├── ISSUE_TEMPLATE/
├── PULL_REQUEST_TEMPLATE.md
├── dependabot.yml
├── labeler.yml
└── templates/
```

**No `workflows/` directory.** Legacy `legacy/github-workflows-disabled/`
holds 28 frozen workflow files from the pre-migration project
(disabled at P1-T0 per `CLAUDE.md` Rules).

### Platforms

| | Hermes | Plugin |
|---|--------|--------|
| `VERSION` | `0.1.0` ✓ | `0.1.0` ✓ |
| `FRAMEWORK_SPEC_VERSION` | `0.1.0` ✓ | `0.1.0` ✓ |
| `README.md` | placeholder (27 lines) | populated (82 lines) ✓ |
| `CHANGELOG.md` | absent | absent |
| Own test suite | 447 tests ✓ | none (declarative) |
| Manifest | `pyproject.toml` | `.claude-plugin/plugin.json` ✓ |
| Coupling sweep | green ✓ | green ✓ |

### Repo root

| | State |
|---|---|
| `LICENSE` | absent (plugin manifest declares MIT placeholder) |
| `docs/PARITY.md` | absent |

## 2. Conformance gap — per-bullet assessment

For each platform-conformance contract bullet, classify as:
**STATIC** (testable from inside the repo via file/spec inspection)
or **RUNTIME** (requires executing a platform to verify).

### PC1 — `framework_spec_version` declaration

**STATIC.** Each platform declares via
`platforms/<name>/FRAMEWORK_SPEC_VERSION`. Test must assert:

- Every `platforms/<name>/` has a `FRAMEWORK_SPEC_VERSION` file.
- Each file is a bare SemVer string (no `v` prefix, no trailing
  whitespace beyond `\n`).
- Each value equals `framework/VERSION` (currently `0.1.0`).
- Each `platforms/<name>/VERSION` exists (the platform's own
  SemVer) — separate file, same shape.

**Implementable today.** New module:
`tests/conformance/platforms/test_version_declaration.py`.

### PC2 — Generated-artifact validation

**RUNTIME.** "Every artifact it generates validates" requires
*executing* the platform's generator and checking the output. The
test would need to:

1. Invoke a platform's BRD-generation skill / tool with a known
   input.
2. Parse the output.
3. Validate it against the registry's `id_patterns` and the layer
   template.

Hermes has 447 unit + integration tests that exercise its
validation paths internally; the plugin is declarative (no
test harness ships with the skills). Cross-platform "every
generated artifact validates" is **out of static-test scope**.

**Deferred.** Each platform's own test suite (Hermes' pytest,
plugin's future smoke checks) is the runtime exercise. The
shared conformance suite cannot static-test this.

### PC3 — Traceability rule enforcement

**RUNTIME** (same reasoning as PC2). The registry encodes
`required_tags`, `can_reference`, `downstream`; whether a platform
*enforces* those rules at validation time is observable only by
running its validator.

**Deferred** to per-platform runtime exercise.

### PC4 — No expectation of the other platform's engine

**STATIC.** Each platform's source must not reference the other's
engine. Test must assert:

- `platforms/hermes/` contains no `aidoc-flow` / `claude-plugin` /
  `skill_view` references (plugin-engine tokens).
- `platforms/claude-code-plugin/` contains no `hermes` /
  `mcp_server` / `sdd_validate` / `pyproject.toml` references
  (Hermes-engine tokens).

Tightening note: legacy / historical text **inside docs/** may
mention the other platform's name (e.g. plugin README mentions
Hermes explicitly, by design). The test must scope to **runtime-
significant** files (`src/`, `skills/<skill>/SKILL.md`, manifest,
not README narrative). Per-platform allow-list of files where
cross-references are intentional.

**Implementable today.** New module:
`tests/conformance/platforms/test_engine_isolation.py`.

### Summary

| Bullet | Implementation in P4-T2 |
|--------|------------------------|
| PC1 — `framework_spec_version` declaration | **Yes** (3–4 assertions) |
| PC2 — Generated-artifact validation | **No** — deferred to runtime exercise |
| PC3 — Traceability rule enforcement | **No** — deferred to runtime exercise |
| PC4 — Engine isolation | **Yes** (per-platform allow-list grep) |

Plus a **structural completeness check** (every `platforms/<name>/`
declares both `VERSION` and `FRAMEWORK_SPEC_VERSION`; no platform
writes to `framework/`) added as a 5th test.

Expected test count after P4-T2: **25 + 3 to 5 = 28 to 30 tests**.

## 3. CI gap

`.github/workflows/` is empty. Need a minimal greenfield set:

| Workflow | Trigger | Job |
|----------|---------|-----|
| `conformance.yml` | push / PR to any branch | Run `python3 -m unittest discover -s tests/conformance` |
| `hermes.yml` | push / PR touching `platforms/hermes/` | Run Hermes' own pytest in a Python 3.12 venv |
| `plugin.yml` | push / PR touching `platforms/claude-code-plugin/` | Lint `plugin.json` (`python -m json.tool`) + coupling sweep (`grep -r 'ucx_flow\|ucx_hermes' returns 0`) |

Legacy `legacy/github-workflows-disabled/` is a 28-workflow set
that's deeply coupled to the pre-migration project's structure (BRD
template validators, multi-phase checkers, AI PR review bots).
**Don't port any of it** — greenfield is cleaner. Reusable patterns,
if any, can be cherry-picked after Phase 5 cutover.

Minimal CI is sufficient for Phase 4. Richer CI (auto-deploy, release
automation) is post-v1.0.

## 4. Deferred-items roll-up

Items flagged "deferred" across P1/P2/P3 plans, classified for
Phase 4:

| Source | Item | Phase 4 in-scope? |
|--------|------|------------------|
| P2-T3 carried | per-platform CHANGELOG (Hermes) | **Yes — P4-T4** |
| P3-T1 §Deferred R1 | `LICENSE` file at repo root | **Yes — P4-T4** |
| P3-T1 §Deferred R2 | skill schema-version naming (`BRD-MVP-TEMPLATE` vs `BRD-TEMPLATE`) | **No** — content-design question; defer post-v1.0 |
| P3-T1 §Deferred R3 | auto-discovery against non-`SKILL.md` files at `skills/` root | **No** — already verified by P3-T4 G20; no action needed |
| P3-T2 G18 carried | ~150 Class D stale `framework/<X>` refs in plugin skills | **No** — per-skill content-migration task; defer post-v1.0 |
| P3-T3 Finding 2 | per-platform CHANGELOG (plugin) | **Yes — P4-T4** |
| P3-T3 R7 | expand Hermes README symmetrically with plugin README | **Yes — P4-T4** |
| P3-T4 G18 lesson | future port plans add `find -type l` to audit recon | **No** — lesson recorded; no Phase 4 action |
| P2-T1 §Deferred (5) | conformance-suite extension to platform-level checks | **Yes — P4-T2** |
| P2-T6 R4 (and P3-T5 R4) | `LICENSE` declared "MIT" in manifest as placeholder | **Yes — P4-T4** (covered by LICENSE work) |

**5 items in Phase 4 scope; 4 deferred (3 content-design / 1 already-done).**

## 5. Parity report scope

`docs/PARITY.md` documents **feature gaps between Hermes and the
plugin** for users choosing between them.

### Comparison framework

**Primary dimension:** the 8 SDD layers (BRD → IPLAN).
**Secondary dimension:** workflow operations
(`create`, `audit`, `validate`, `review`, `fix`, `autopilot`).

For each (layer × operation) cell, mark:

- **H** if Hermes provides it
- **P** if the plugin provides it
- **HP** if both
- **—** if neither

Plus a freeform "platform-specific extras" section for things only
one platform has:

- Hermes-only: MCP-server runtime, conformance-suite-extension
  hooks, scaffold runtime, etc.
- Plugin-only: skill auto-discovery, slash-command UX,
  `requirements-analyst` subagent, `save-plan` command.

### Scope guardrails

- Static comparison — don't run the platforms; observe their
  declared coverage by inspection of `platforms/hermes/skills/`
  vs `platforms/claude-code-plugin/skills/` and the skills' own
  frontmatter.
- ~1-page report — not a comprehensive feature wishlist.
- Updated only when a platform ships a structurally different
  capability (not every patch).

## 6. Open questions (for P4-T1 design)

1. **Test-module naming / placement.** New tests live at
   `tests/conformance/platforms/test_*.py` (sub-package) or flat at
   `tests/conformance/test_platform_*.py`? Affects suite organization.

2. **Per-platform allow-list for PC4 engine isolation.** Which
   files in `platforms/hermes/` are allowed to mention "plugin" /
   "claude" tokens (probably docs/ + README), and vice versa? P4-T1
   defines the exact allow-list.

3. **CI runner — `ubuntu-latest` or `self-hosted`?** Legacy used
   `self-hosted`; greenfield should use `ubuntu-latest` (no
   infra dependency). Confirm.

4. **CHANGELOG retrofit content.** P4-T0 audit (G10 in
   P4-T0-PLAN) recommends the minimal-honest variant: each
   platform's `[0.1.0]` mirrors the project-level `[0.3.0]` /
   `[0.4.0]` content scoped to that platform. Confirm posture.

5. **Hermes README expansion — full mirror or extract-from-
   project-level-README?** Full mirror = duplicate skill counts +
   table + use examples for Hermes. Extract = shorter, pointer-
   heavy. Plugin README mirrored the populated pattern; symmetric
   answer is "full mirror" for Hermes.

6. **LICENSE choice.** Plugin manifest declares MIT placeholder.
   Confirm MIT (and add `LICENSE` to repo root) or change to
   Apache 2.0 / GPL / etc. Project-level decision.

7. **Tag a new `framework/v0.X.Y` if PC1+PC4 tests are added?**
   Conformance tests don't change `framework/` itself; spec
   version stays `0.1.0`. **No** new framework tag in Phase 4.
   Confirmed; not strictly an open question.

## 7. Verify (against the plan's gate)

- All 4 platform-conformance contract bullets enumerated in §2
  with PC1-PC4 IDs.
- CI gap stated (no `.github/workflows/`) with the 3-workflow
  minimal CI sketch.
- Deferred-items roll-up complete: 5 in-scope + 4 deferred = 9
  items (cross-checked against P1/P2/P3 plan §Deferred sections).
- Parity report scope statement with comparison framework
  (layers × operations).
- Open-questions list = 6 (above the canonical 4 minimum).
- No code or files moved (`git status` shows only `plans/`).
