# P4-T3 Plan — CI workflows

| Field      | Value                                |
|------------|--------------------------------------|
| Task       | P4-T3                                |
| Depends on | P4-T1 design (Q3), P4-T2 (suite at 31) |
| Status     | DONE (pending workflow file relocation by user) — 2026-05-21T02:15:00Z |
| Feeds      | P4-T5 (verify + close)               |

## Objective

Author the three greenfield GitHub Actions workflows per P4-T1 Q3:
`.github/workflows/conformance.yml` (shared 31-test suite),
`hermes.yml` (Hermes' 447-test pytest), `plugin.yml` (plugin smoke
check: manifest validity + coupling sweep). All on `ubuntu-latest`
with Python 3.12 via `actions/setup-python@v5`. No carry-over from
the legacy 28-workflow set parked in
`legacy/github-workflows-disabled/`.

## Scope

**In:**

1. **`.github/workflows/conformance.yml`** — runs the framework
   conformance suite on push/PR to any branch.
2. **`.github/workflows/hermes.yml`** — runs Hermes' own pytest
   suite on push/PR touching `platforms/hermes/**` or `framework/**`
   (the latter because Hermes consumes the framework spec; a framework
   change should re-validate Hermes).
3. **`.github/workflows/plugin.yml`** — smoke-checks the plugin:
   manifest validity (`python -m json.tool`) + coupling sweep
   (zero `ucx_flow|UCX_FLOW|ucx_hermes` hits) on push/PR touching
   `platforms/claude-code-plugin/**`.
4. **Local smoke** — run the test commands locally (where possible)
   to confirm they work before committing.
5. **YAML syntax validation** — parse each workflow file with
   PyYAML to catch syntax errors before push.

**Out:**

- Triggering an actual GitHub Actions run. The in-container
  session can't observe a real CI invocation; CI green-status
  comes from a real PR after the workflows are pushed.
- Release automation, deploy workflows, dependency-update bots
  beyond Dependabot (already configured at `.github/dependabot.yml`).
- Self-hosted runners. P4-T1 Q3 confirmed `ubuntu-latest`.
- Conditional skip / advanced matrix builds. Single-OS,
  single-Python-version is sufficient for v1 CI.

## Approach

### 1. `conformance.yml`

```yaml
name: Conformance

on:
  push:
  pull_request:

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  conformance:
    name: Framework + platform conformance
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install conformance suite dependencies
        run: pip install -r tests/conformance/requirements.txt

      - name: Run conformance suite
        run: python -m unittest discover -s tests/conformance -v
```

### 2. `hermes.yml`

```yaml
name: Hermes platform

on:
  push:
    paths:
      - 'platforms/hermes/**'
      - 'framework/**'
      - '.github/workflows/hermes.yml'
  pull_request:
    paths:
      - 'platforms/hermes/**'
      - 'framework/**'
      - '.github/workflows/hermes.yml'

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test:
    name: Hermes pytest
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install Hermes dependencies
        working-directory: platforms/hermes
        run: |
          pip install -e .
          pip install pytest

      - name: Run Hermes test suite
        working-directory: platforms/hermes
        env:
          PYTHONPATH: src
        run: python -m pytest tests/ -v
```

### 3. `plugin.yml`

```yaml
name: Claude Code plugin

on:
  push:
    paths:
      - 'platforms/claude-code-plugin/**'
      - '.github/workflows/plugin.yml'
  pull_request:
    paths:
      - 'platforms/claude-code-plugin/**'
      - '.github/workflows/plugin.yml'

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  smoke:
    name: Plugin smoke checks
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate plugin manifest is JSON
        run: python -m json.tool < platforms/claude-code-plugin/.claude-plugin/plugin.json

      - name: Coupling sweep — no Hermes references in plugin runtime
        run: |
          if grep -rEln 'ucx_flow|UCX_FLOW|ucx_hermes' \
               platforms/claude-code-plugin/.claude-plugin \
               platforms/claude-code-plugin/commands \
               platforms/claude-code-plugin/agents 2>/dev/null; then
            echo "::error::Found forbidden Hermes-engine tokens in plugin runtime"
            exit 1
          fi
          echo "ok: no forbidden tokens"

      - name: Plugin structural sanity
        run: |
          dirs=$(find platforms/claude-code-plugin/skills -mindepth 1 -maxdepth 1 -type d | wc -l)
          if [ "$dirs" -lt 100 ]; then
            echo "::error::Plugin skill count $dirs is suspiciously low (expected ~142)"
            exit 1
          fi
          echo "ok: $dirs skill dirs"
```

### 4. Local smoke tests

Before commit:

```sh
# YAML syntax validation (all three workflows):
for f in .github/workflows/{conformance,hermes,plugin}.yml; do
  python -c "import yaml; yaml.safe_load(open('$f'))" && echo "ok: $f"
done

# conformance.yml's commands:
pip install -r tests/conformance/requirements.txt 2>/dev/null
python -m unittest discover -s tests/conformance -v 2>&1 | tail -3

# plugin.yml's commands (manifest + sweep + structural):
python -m json.tool < platforms/claude-code-plugin/.claude-plugin/plugin.json > /dev/null && echo "manifest ok"
grep -rEln 'ucx_flow|UCX_FLOW|ucx_hermes' \
  platforms/claude-code-plugin/.claude-plugin \
  platforms/claude-code-plugin/commands \
  platforms/claude-code-plugin/agents 2>/dev/null || echo "sweep ok"
find platforms/claude-code-plugin/skills -mindepth 1 -maxdepth 1 -type d | wc -l
```

`hermes.yml`'s pytest run requires Python 3.12 + venv; local
smoke is **not strictly required** (we've already run it during
P2-T9 / P3-T4 and got 447/447). Re-running here is optional.

### 5. Design notes

- **No matrix builds.** Single Python 3.12, single ubuntu-latest.
  Multi-version matrices are a post-v1 nice-to-have.
- **`concurrency` block** cancels in-progress runs on rebase
  (matches the legacy CI pattern that *was* worth keeping).
- **`permissions: contents: read`** — minimal permissions; no
  write needed (these are read-only checks).
- **`paths:` filters** scope hermes.yml and plugin.yml to relevant
  changes only — saves CI minutes; doesn't gate framework-only
  changes on platform tests they can't break.
- **`conformance.yml` has no `paths:` filter** — it's the canonical
  spec contract; every push should re-validate.

## Step sequence

1. **Pre-flight YAML setup.** Confirm PyYAML available
   (`tests/conformance/requirements.txt` already includes it; if
   not installed locally, `pip install pyyaml`).
2. **Create `.github/workflows/` directory.**
3. **Write three workflow files** per §Approach.
4. **Local smoke** (§Approach.4): YAML parsing + conformance run +
   plugin checks.
5. **Verify** (see below).
6. **Land** — single commit
   `ci: add greenfield workflows for conformance + Hermes + plugin (P4-T3)`;
   update `plans/HANDOFF.md`; tick P4-T3 in
   `plans/MIGRATION_TODO.md`. Push.

## Verification

- **V1. All three workflow files present:**
  `ls .github/workflows/` returns `conformance.yml`, `hermes.yml`,
  `plugin.yml` (3 files).
- **V2. Each is valid YAML:**
  `python -c "import yaml; [yaml.safe_load(open(f)) for f in ['.github/workflows/conformance.yml','.github/workflows/hermes.yml','.github/workflows/plugin.yml']]; print('ok')"`
  prints `ok`.
- **V3. Each declares `runs-on: ubuntu-latest`:**
  `grep -c 'runs-on: ubuntu-latest' .github/workflows/*.yml`
  returns 3 (one per file).
- **V4. Each declares Python 3.12 (where applicable):**
  conformance.yml + hermes.yml use `actions/setup-python@v5` with
  `python-version: '3.12'`. plugin.yml uses Python implicitly
  (only `python -m json.tool`) — defaults to system Python on the
  runner (3.10+).
- **V5. conformance suite command works locally:**
  `python -m unittest discover -s tests/conformance` returns
  `Ran 31 tests in <X>s, OK`.
- **V6. plugin smoke commands work locally:**
  - `python -m json.tool < platforms/claude-code-plugin/.claude-plugin/plugin.json`
    exits 0.
  - Coupling sweep returns no hits in the scoped directories.
  - Structural check returns 142 skill dirs.
- **V7. No code changes outside `.github/workflows/`:**
  `git diff --stat HEAD -- :^.github/workflows/ :^plans/` empty.
- **V8. Concurrency block present** in all three (prevents
  duplicate parallel runs on rebase).

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | A YAML syntax error slips in (indentation, missing quotes). | V2 verify gate parses with `yaml.safe_load`; halt before push if any fails. |
| R2 | `actions/setup-python@v5` major version pin breaks if v6 ships breaking changes. | Pinned to `@v5` (major version). GitHub follows SemVer for actions; minor / patch updates are safe within v5. If v6 ships, a single-line edit updates all three workflows. |
| R3 | `paths:` filter on hermes.yml / plugin.yml doesn't trigger on framework changes that affect them. | `hermes.yml` includes `framework/**` in its paths; `plugin.yml` does not (per design — plugin is declarative, doesn't import framework at runtime). If framework changes that *should* trigger plugin re-validation surface, add `framework/**` to plugin.yml later. |
| R4 | The plugin coupling-sweep `grep -E` shell syntax differs between local sh and GitHub Actions ubuntu-latest. | Both use `bash` (GitHub Actions default shell on ubuntu-latest); `grep -E` is GNU grep. Identical behavior. Verified by local smoke. |
| R5 | `pip install -e .` for Hermes fails on the runner (missing system deps). | Hermes' dependencies are pure Python (`mcp[cli]`, `pydantic`, `PyYAML`, `python-dotenv`). No system-level deps required. Per Hermes' `pyproject.toml`. |
| R6 | The conformance suite's working directory matters. | `python -m unittest discover -s tests/conformance` works from repo root (the `-s` arg is path-relative); CI checks out to `$GITHUB_WORKSPACE` which is repo root by default. |
| R7 | We can't actually verify CI passes from inside the in-container session. | Verify gates are static (YAML valid, commands work locally). Real CI green status comes from the next PR / push after merge. Acceptable per P4-T0 audit §3 — CI is greenfield and shipped for use, not real-time-validated in this task. |
| R8 | `::error::` GitHub Actions log syntax in plugin.yml — does it actually annotate the PR? | GitHub Actions parses `::error::` lines into PR check-run annotations. Validated by GitHub docs; will work on any modern runner. |

## Review log

### Pass 1 — 2026-05-21T01:45:00Z

- **G1. P4-T1 Q3 design honored throughout.** `ubuntu-latest`,
  Python 3.12, `actions/setup-python@v5`, no carry-over from
  legacy.
- **G2. `paths:` filters scope hermes + plugin to relevant
  changes.** Conformance suite (the contract) runs on every push;
  per-platform suites trigger only when their platform changes.
- **G3. `framework/**` triggers hermes.yml** — framework changes
  invalidate Hermes' consumption of it. Plugin doesn't need this
  trigger (declarative, doesn't import framework at runtime).
- **G4. `concurrency` blocks cancel duplicates** — the one pattern
  from legacy CI worth keeping.
- **G5. Permissions minimal — `contents: read`** only. No write
  needed. Defensive against compromised actions.
- **G6. Plugin smoke is light** — manifest valid + coupling sweep
  + structural. Doesn't try to invoke skills (would need a Claude
  Code runtime).
- **G7. Hermes smoke uses `pip install -e .`** to honor
  `pyproject.toml`'s deps list. Plus `pip install pytest`
  because pytest isn't in Hermes' runtime deps (only dev deps,
  if any).
- **G8. Workflow YAML uses `actions/checkout@v4`** — current
  stable major version.
- **G9. No matrix builds / multi-Python / multi-OS in v1 CI.**
  Single config; matrix expansion is post-v1.

### Pass 2 — 2026-05-21T01:55:00Z

- **G10. paths filter on workflow file itself.** Both hermes.yml
  and plugin.yml include `.github/workflows/<name>.yml` in their
  paths — so editing the workflow re-runs the workflow (catches
  workflow-level regressions). Standard pattern.
- **G11. Hermes pytest count assertion.** Workflow runs
  `pytest tests/ -v` and exits non-zero on any failure. Doesn't
  hardcode an expected count (447) — that's brittle as tests are
  added / removed. Trust pytest's exit code.
- **G12. Plugin's `find ... | wc -l < 100` threshold.** Currently
  142 skills; 100 is a loose floor. Catches catastrophic
  destruction (e.g. an accidental `rm -rf skills/*` that landed in
  a PR), not subtle removals. Tighter check would be brittle. Loose
  is right for a smoke gate.
- **G13. Hermes' `working-directory:` runs from the platform dir.**
  Two steps need it (install + test). DRY would be a job-level
  `defaults: { run: { working-directory: ... } }`; explicit per-
  step is more readable for a 3-step job.
- **G14. Plugin manifest is a single file — JSON parse covers
  validity.** Doesn't validate schema (no public schema URL per
  P3-T1 Q1). Schema validation would require either a custom
  validator or an external tool; not worth it for v1.
- **G15. No new findings.** Plan is internally consistent; verify
  gates are observable. Ready to present on approval.

## Implementation note (2026-05-21T02:05:00Z)

Executed. All 8 verify gates green; no implementation-time findings.

- **V1 files present:** `conformance.yml`, `hermes.yml`, `plugin.yml`.
- **V2 YAML valid:** all 3 parse via `yaml.safe_load`.
- **V3 `runs-on: ubuntu-latest`** in all 3.
- **V4 Python 3.12 via setup-python@v5** in conformance.yml +
  hermes.yml (plugin.yml uses runner default Python for
  `json.tool`).
- **V5 conformance suite locally:** `Ran 31 tests in 0.289s, OK`.
- **V6 plugin smoke locally:** manifest valid; coupling sweep
  returns 0 hits; 142 skill dirs.
- **V7 scope discipline:** only `.github/workflows/` and
  `plans/P4-T3-PLAN.md` modified.
- **V8 concurrency block** present in all 3.

CI is shipped. Real green status will surface on the next push /
PR run after this commit lands. P4-T0 audit §3 already
acknowledged that in-container can't observe a real CI run; this is
expected and not a verify failure.

If a workflow fails on the first real run, the responsible fix is
in a follow-up commit (or in P4-T5 verify if it surfaces during
phase close), not by weakening the workflow.

### Implementation-time discovery — in-container workflow-push restriction

The push of `.github/workflows/*.yml` was **rejected** by the
in-container git proxy with:

```
! [remote rejected] claude/multi-platform-migration-AamWB ->
  claude/multi-platform-migration-AamWB
  (refusing to allow a GitHub App to create or update workflow
  `.github/workflows/conformance.yml` without `workflows` permission)
```

Fifth in-container permission restriction (after the three
`refs/tags/*` 403s at P1-T8 / P2-T6 / P3-T5, all the same root cause:
the GitHub App credentials the container uses are scoped narrower
than a normal user push). Different shape (this rejects the *branch*
push outright when it contains workflow file additions, not just
the tag refs), same workaround: do the operation from a local clone
with normal credentials.

**Resolution:**

The three workflow files are staged at
`plans/workflows-pending/{conformance,hermes,plugin}.yml` for
inspection / transit. The user moves them into place from a local
clone:

```sh
# In a local clone with normal GitHub credentials:
git fetch origin claude/multi-platform-migration-AamWB
git checkout claude/multi-platform-migration-AamWB
git pull --ff-only

mkdir -p .github/workflows
git mv plans/workflows-pending/conformance.yml .github/workflows/conformance.yml
git mv plans/workflows-pending/hermes.yml      .github/workflows/hermes.yml
git mv plans/workflows-pending/plugin.yml      .github/workflows/plugin.yml
rmdir plans/workflows-pending

git commit -m "ci: install P4-T3 workflows at .github/workflows/

Moves the three CI workflows from plans/workflows-pending/ to their
runtime location at .github/workflows/. The in-container session
couldn't push workflow files directly (GitHub App credentials lack
the 'workflows' permission); content was prepared in-container and
this commit completes the install."

git push origin claude/multi-platform-migration-AamWB
```

After the push, the workflows fire on the next push or PR. Verify
via `gh run list` or the Actions tab.

### Lesson for future planning

The in-container restriction set is now:
- `refs/tags/*` pushes (HTTP 403; 3 occurrences).
- `.github/workflows/**` file additions / edits (rejected with
  "refusing to allow GitHub App without workflows permission";
  1 occurrence, now).

Any future task that touches either category should bake the
local-clone workaround into the plan from the outset. Documented
in `docs/TAGGING.md` for tags; should be added there for
workflows too (P4-T4 or P4-T5 housekeeping).
