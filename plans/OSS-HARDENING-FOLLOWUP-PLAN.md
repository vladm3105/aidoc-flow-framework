# OSS Hardening Follow-up Plan

**Goal:** Close the OSS/security-hardening gaps (F1–F5) surfaced while preparing
the sibling `iplan-runner` for public release (its `PLAN-018`), now applied to
the **already-public** `aidoc-flow-framework`.

**Context:** This repo is already public (MIT, forks + stars exist). These are
incremental improvements; **F3 (local-path leaks) is the only live issue** — it
is both information disclosure and, for `.mcp.json` / agent-skill config
examples, functional breakage for anyone who clones. Because the repo is public
with forks, **history rewriting is out of scope** (disruptive, and the leaks are
local filesystem paths, not credentials); remediation fixes the working tree and
adds a guard against recurrence.

**Origin:** Findings F1–F5 in `iplan-runner/plans/PLAN-018_oss-public-migration.md`
("Framework-side improvements"). This plan is their remediation.

---

| Field      | Value |
|------------|-------|
| Status     | PLANNED - 2026-06-14 |
| Depends on | none (independent of `iplan-runner` PLAN-018) |
| Scope      | repo hygiene + CI hardening only — no contract/`framework/` or runtime code changes |

## Findings → tasks

| # | Finding | Evidence | Task |
|---|---------|----------|------|
| F3 | 60 tracked files leak `/opt/data/…` / `/home/<user>/…`; `.mcp.json` + agent-skill `SKILL.md` examples hardcode a local venv (leak **and** breakage) | `.mcp.json:4,6`; `platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/SKILL.md:870` | T1, T2, T3 |
| F1 | All GitHub Actions are tag-pinned (`@v6`/`@v4`), not SHA-pinned | `.github/workflows/codeql.yml:24` (`actions/checkout@v6`) | T4 |
| F2 | No `CODE_OF_CONDUCT.md` | absent at repo root | T5 |
| F4 | README has no status/license/version badges | `README.md:1` (no badge lines) | T6 |
| F5 | dependabot covers `platforms/hermes` + `tests/conformance` + actions only | `.github/dependabot.yml` | T7 (likely N/A — see task) |

## Scope

**In:** F1–F5 remediation on the working tree + a recurrence guard.

**Out:**

1. Rewriting public git history (forks/stars make it disruptive; leaks are paths,
   not secrets). Residue stays in history; an optional `git filter-repo`/BFG pass
   can be a separate, coordinated decision later.
2. Any change to the `framework/` contract, `platforms/*/src`, conformance
   vectors, or engine behaviour.

## Step sequence

### T1 — F3a: fix the leaks that are also broken config (HIGH)

These hardcode `/opt/data/ucx_framework/.venv/...`, so they leak the maintainer's
layout AND fail for any cloner.

- [ ] `.mcp.json` (`:4` command, `:6` cwd) — this is machine-specific and should
  not be a committed, hardcoded absolute path. Replace with a portable form
  (`python` on PATH + repo-relative `cwd`), or remove `.mcp.json` from VCS, add
  it to `.gitignore`, and commit a `.mcp.json.example` with placeholders.
- [ ] Agent-skill / integration docs that embed `command:
  "/opt/data/ucx_framework/.venv/bin/python"` → genericize to `python` /
  `<repo>/...` placeholders. Confirmed locations:
  `platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/SKILL.md:870,1164`
  and `platforms/hermes/docs/HERMES_INTEGRATION.md` (multiple: lines
  87/151/152/155/158/193/219 — invocation + MCP-config examples). These are
  copy-paste runnable instructions, so the absolute path is functional breakage,
  not just a leak.
- [ ] Commit: `fix(config): remove hardcoded local venv paths from .mcp.json + skill examples`

### T2 — F3b: scrub remaining doc/historical path leaks

- [ ] Genericize the remaining `/opt/data/` and `/home/<user>/` occurrences to
  placeholders (`<repo>/…`, `<workspace>/…`). Inventory (verify with the gate in
  T3): ~60 files total — `platforms/**` (~34, mostly agent-skill docs +
  `CHANGELOG.md` meta-references), `plans/**` (~24), `CHANGELOG.md`. Many `plans/`
  and `CHANGELOG` hits are meta-references *describing* earlier path cleanups;
  genericize the literal paths, keep any deliberately-illustrative placeholder
  (e.g. `/opt/data/my_project`) only if clearly marked as an example.
- [ ] Commit: `docs: genericize local absolute paths (info-disclosure cleanup)`

### T3 — F3c: recurrence guard

- [ ] Add a pre-commit hook + CI check rejecting newly-introduced absolute
  `/opt/data/` or `/home/<user>/` paths in tracked files (a `grep` gate; allowlist
  any intentional illustrative placeholder via an inline marker). Wire into
  `.pre-commit-config.yaml` and a workflow step.
- [ ] Commit: `ci: guard against committing local absolute paths`

### T4 — F1: SHA-pin GitHub Actions

- [ ] Pin every `uses:` across the 8 workflows to a full commit SHA with a
  `# vX.Y.Z` comment: `actions/checkout@v6`, `actions/setup-python@v6`,
  `actions/labeler@v6`, `github/codeql-action/init@v4`,
  `github/codeql-action/analyze@v4`. (Consider enabling Dependabot
  `github-actions` SHA updates, already configured, to keep them current.)
- [ ] Commit: `ci: pin GitHub Actions to commit SHAs (supply-chain hardening)`

### T5 — F2: CODE_OF_CONDUCT.md

- [ ] Add Contributor Covenant v2.1. `SECURITY.md` uses **GitHub private
  vulnerability reporting** (no published email), so set the CoC enforcement
  contact to the repo's private-reporting URL
  (`https://github.com/vladm3105/aidoc-flow-framework/security/advisories/new`) or
  the maintainer handle `@vladm3105` — pick one concrete value, do not leave a
  placeholder.
- [ ] Commit: `docs: add CODE_OF_CONDUCT (Contributor Covenant)`

### T6 — F4: README badges

- [ ] Add CI, license (MIT), and `framework/VERSION` badges near the top of
  `README.md`.
- [ ] Commit: `docs: add README status/license badges`

### T7 — F5: dependabot coverage (verify first; likely N/A)

- [ ] Check whether `platforms/claude-code-plugin` has a dependency manifest
  (`pyproject.toml`/`requirements*.txt`/`package.json`). Top-level has **none**,
  so a `pip` dependabot entry likely does **not** apply. If a manifest exists in
  a subdir, add the matching `package-ecosystem` + `directory` entry to
  `.github/dependabot.yml`; otherwise record F5 as **N/A** (the framework's only
  Python deps — `platforms/hermes`, `tests/conformance` — are already covered).
- [ ] Commit (if applicable): `ci: extend dependabot to claude-code-plugin`

## Verification

```bash
# F3: no local absolute paths remain (allow marked illustrative placeholders only)
! git grep -nE '/opt/data/|/home/[a-z]+/' -- . ':!plans/OSS-HARDENING-FOLLOWUP-PLAN.md'
# F1: no tag-pinned actions remain
! grep -rnE 'uses: [^#]+@v[0-9]+\s*$' .github/workflows
# F2/F4: files/badges present
test -f CODE_OF_CONDUCT.md && grep -qiE 'shields\.io|!\[' README.md
# repo still builds/tests green
python -m pytest -q   # or the repo's conformance entrypoint
pre-commit run --all-files
```

## Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Removing `.mcp.json` breaks the maintainer's local MCP wiring | Provide `.mcp.json.example`; document the portable form; `.gitignore` the real file |
| R2 | History still contains the leaked paths after T1–T2 | Documented as accepted residual (paths, not secrets); optional coordinated `filter-repo` later — out of scope here |
| R3 | Mass path genericization edits a skill doc whose path is load-bearing for an example | T2 keeps clearly-marked illustrative placeholders; T3 gate + `pre-commit run` catches breakage |
| R4 | SHA-pins go stale | Dependabot `github-actions` (already configured) raises bumps |

## Evidence ledger

| # | Claim | Symbol | Citation |
|---|-------|--------|----------|
| 1 | `.mcp.json` hardcodes a local venv path | `/opt/data/ucx_framework/.venv/bin/python` | .mcp.json:4 |
| 2 | Agent-skill example embeds the same local venv | `command: "/opt/data/ucx_framework/.venv/bin/python"` | platforms/hermes/agent-skills/spec-driven-development/sdd-orchestrator/SKILL.md:870 |
| 3 | Actions are tag-pinned, not SHA-pinned | `uses: actions/checkout@v6` | .github/workflows/codeql.yml:24 |
| 4 | dependabot covers hermes + conformance + actions only | `directory: "/platforms/hermes"` | .github/dependabot.yml:5 |
| 5 | Second platform is `claude-code-plugin` (not a Python `claude` engine) | `platforms/claude-code-plugin/` | platforms/claude-code-plugin/CHANGELOG.md:8 |

## Review log

### Pass 1 - 2026-06-14 - author

- Verified F1/F2/F4 and the F3 file count (60) against the repo; corrected F5
  from "add platforms/claude" to "claude-code-plugin, likely N/A (no Python
  manifest)"; split F3 into config-breakage (T1) vs doc cleanup (T2) + guard (T3).

### Pass 2 - 2026-06-14 - independent (general-purpose Agent, fresh context)

Confirmed accurate: F3 file count (60: 34 platforms, 24 plans, `.mcp.json`,
`CHANGELOG.md`), README clean of leaks, F1 (8 workflows, 5 tag-pinned actions),
F2/F4 gaps, **F5 N/A** (no manifest under `claude-code-plugin`; only hermes +
conformance have manifests, both already covered), and no missing high-value
OSS/security gap (placeholder `ghp_xxxx` in docs are illustrative, SECURITY.md
adequate, LICENSE present). Findings folded in:

- **[SHOULD] T1 wrong/incomplete file list.** `GITHUB_WORKFLOWS.md` has no venv
  leak; the real broken-config leaks are `SKILL.md:870,1164` and
  `HERMES_INTEGRATION.md` (lines 87/151/152/155/158/193/219). **Fixed.**
- **[SHOULD] T5 had no resolvable CoC contact** (SECURITY.md uses GitHub private
  reporting, no email). **Fixed:** specify the private-reporting URL or
  `@vladm3105`.
- **[NIT] Evidence row 5 line number wrong.** **Fixed** to
  `claude-code-plugin/CHANGELOG.md:8`.

**Result: ready** — no further load-bearing findings; F5 confirmed N/A.
