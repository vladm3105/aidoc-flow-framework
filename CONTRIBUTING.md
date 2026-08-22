# Contributing to AI Doc Flow Framework

Thanks for considering a contribution. This project follows a conformance-gated workflow: every PR must pass the conformance test suite and the relevant platform tests.

## Quick start

```bash
git clone https://github.com/vladm3105/aidoc-flow-framework
cd aidoc-flow-framework
pip install pre-commit && pre-commit install
```

## Project layout

See [`docs/REPO_STRUCTURE.md`](docs/REPO_STRUCTURE.md) for the full layout. The two surfaces:

- `framework/` — engine-agnostic SDD specification (the contract).
- `platforms/` — platform implementations (Hermes MCP server, Claude Code plugin).

## Before you push

```bash
# Conformance (framework spec invariants)
cd tests/conformance && python3 -m unittest discover -q

# Unit + per-layer + packaging + release (all tiers)
cd .. && python3 -m unittest discover -s unit -q
python3 -m unittest discover -s acceptance/deterministic -q
python3 -m unittest discover -s packaging -q
python3 -m unittest discover -s release -q
```

## Documentation discipline — update docs of record per PR

**Every PR must keep the documents-of-record in sync with the change it ships.** Do not let a separate "doc-refresh" PR be the catch-up mechanism (PR #98 was that catch-up; the rule below prevents recurrence).

Two pre-commit hooks automate the discipline:

| Hook | Script | What it does |
|---|---|---|
| `sync-version-refs` | `scripts/sync-version-refs.sh` | **Mechanical auto-sync.** When a `VERSION` file changes, propagates the new version string into every doc-of-record that quotes it (`plugin.json`, `marketplace.json`, 52 × SKILL.md frontmatter, READMEs, PARITY.md current-state row, …). Re-stages on its own; idempotent. Silent on commits that don't bump a version. |
| `check-docs-updated` | `scripts/check-docs-updated.sh` | **Semantic reminder.** Runs on every commit. When the staged change touches code/spec/skills but no document-of-record, prints a checklist of likely-stale docs. **Warning only — never blocks the commit.** Authors decide whether to update or proceed (false-positive friendly). |

Together they handle: mechanical sync is invisible (just commit; the right files update); semantic reminder surfaces the prose-authoring docs (CHANGELOG entry, ROADMAP bullet, handoff narrative, Hermes-backlog entry) that the author must write themselves.

### Documents of record — what to update for which change

| Change category | Mandatory updates (same PR) | Mechanical (auto-synced) | Semantic (you author) |
|---|---|---|---|
| **Framework spec** (`framework/**`) | `framework/VERSION` bump if structural; `framework/governance/DECISIONS.md` if a decision is recorded; repo-root `CHANGELOG.md` `[Unreleased]`; `ROADMAP.md` "Recently shipped" if user-visible | CLAUDE.md current-state line; README.md Status block; docs/PARITY.md row | DECISIONS entry; CHANGELOG entry; ROADMAP bullet |
| **Platform change** (`platforms/<name>/**`) | `platforms/<name>/CHANGELOG.md` `[Unreleased]`; `platforms/<name>/VERSION` if bumping; `docs/PARITY.md` (release only); `docs/TAGGING.md` (release only) | plugin.json; marketplace.json; 52 × SKILL.md frontmatter; READMEs; PARITY current-state | CHANGELOG entry; new TAGGING row (on release) |
| **User-visible policy/rule** | `CLAUDE.md` §"Durable conventions"; auto-memory entry; `README.md` if status-line affected | — | rule prose; memory note |
| **Platform follow-on / defect discovered** | Open GitHub issue with label `platform: <name>` | — | issue reproduction, blast radius, fix shape |
| **Session milestone reached** | `plans/HANDOFF.md` prepend new current-state header | — | handoff narrative (PRs landed, next item) |
| **New advisory (warning) lint rule** | the affected manifests under `tests/acceptance/expected_warnings/` — the rule fires on the acceptance fixtures and reddens the tier until each new warning is pinned with a `reason` (or the fixture is cleared) | — | `reason` prose naming what would clear each pinned warning |
| **Trivial / typo / internal refactor** | (none) | — | — |

If your change spans categories, do all the updates. The hooks above flag misses on commit; an explicit checklist in your PR description naming the touched docs helps reviewers.

### When the warning hook fires

`check-docs-updated` prints a WARNING when:

- Any of `framework/**`, `platforms/**/{skills,agents,scripts,tools}/**`, `platforms/**/VERSION`, `tools/**` is staged
- AND no doc-of-record (`CHANGELOG.md`, `README.md`, `ROADMAP.md`, `CLAUDE.md`, `plans/HANDOFF.md`, `docs/PARITY.md`, `docs/TAGGING.md`, `docs/PROJECT.md`, `framework/governance/DECISIONS.md`, `platforms/*/CHANGELOG.md`) is staged

Common false positives (warning is correct to ignore):

- Typo / comment-only fix
- Test-only change with no production-behavior impact
- Internal refactor that's invisible to users

The hook exits 0 regardless — it's a reminder, not a gate. If your change genuinely needs no doc update, commit and move on.

## How to add a test, a skill, a lint check

See [`tests/CONTRIBUTING.md`](tests/CONTRIBUTING.md) (test-suite contribution guidance).

**Adding an advisory (warning-severity) lint rule?** It will fire on the
acceptance fixtures, and the deterministic acceptance tier is a **required
check**, so it blocks every merge until you update the affected manifests under
`tests/acceptance/expected_warnings/` **in the same PR**. That is deliberate: the
tier previously asserted zero findings of any severity, so each new advisory rule
silently reddened it (`REFGRAN01`, then `ACC01`). Pin the new warnings with a
`reason`, or clear the fixtures. See
[`tests/acceptance/README.md`](tests/acceptance/README.md#accepted-warnings-expected_warnings).

## How to add a governance file or change a framework spec section

The framework spec is GATE-SPEC governed. Any change under `framework/` (the spec subtree) requires bumping `framework/VERSION` and going through the conformance suite. See [`docs/PROJECT.md`](docs/PROJECT.md) §6 (Change Management).

## Secret scanning — where each pass runs

| Stage | Tool | Scope | Config |
|---|---|---|---|
| `pre-commit` (local) | `detect-secrets` | staged files | `.secrets.baseline` |
| CI (`pre-commit.yml`) | `detect-secrets`, `detect-private-key` | full tree (`--all-files`) | `.secrets.baseline`, `.pre-commit-config.yaml` |
| CI (`secret-scan.yml`) | `gitleaks` | **full git history** (`gitleaks git`, canon `ci/v2.x`) | `.gitleaks.toml` |

There is deliberately **no local gitleaks hook** ([#348](https://github.com/vladm3105/aidoc-flow-framework/issues/348)): the upstream hook builds gitleaks from source and needs Go ≥ 1.21, and the failure lands in hook installation, aborting the commit before any other hook runs. Because CI scans history rather than the working tree, a clean local tree can still fail the gate — validate a suspected finding with `git log -p` / `git grep` over history, and record justified suppressions in `.gitleaks.toml`. See [`SECURITY.md`](SECURITY.md) for full details on automated security checks.

## Reporting bugs and security issues

- Functional bugs: <https://github.com/vladm3105/aidoc-flow-framework/issues>
- Security vulnerabilities: see [`SECURITY.md`](SECURITY.md) for the disclosure protocol.

## License

MIT (see [`LICENSE`](LICENSE)).
