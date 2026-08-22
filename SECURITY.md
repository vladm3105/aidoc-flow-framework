# Security Policy

## Supported versions

This is a specification + tooling project (an engine-agnostic `framework/` spec
plus two platforms). The project, the spec, and each platform are versioned and
released independently (`docs/PROJECT.md` §2), and each carries its own
`VERSION` file.

Security fixes land on `main` and ship in the next release of each affected
stream; they are not backported to earlier releases. Report against `main`, or
against whatever build you are running — including an untagged one. Both
platforms currently ship ahead of their newest tag, because the tag-cut is a
known backlog (`docs/TAGGING.md`), so the version you have may have no tag at
all.

| Component | Supported |
|-----------|-----------|
| `main` | ✅ — fixes land here first |
| The most recent release of each stream | ✅ — fixed on `main`, shipped in that stream's next release |
| Anything older, pre-cutover project releases (`< v1.0`) included, and branch `legacy-ucx-v3.2-read-only` | ❌ |

## Reporting a vulnerability

**Please do not open a public issue, PR, or discussion for security
vulnerabilities** — that would disclose the issue before a fix is available.

Instead, use **GitHub's private vulnerability reporting**:

1. Go to the repository's **Security** tab.
2. Choose **Report a vulnerability** (Privately report a security
   vulnerability).
3. Describe the issue, affected component/path, reproduction steps, and impact.

This opens a private advisory visible only to the maintainers.

### What to expect

- **Acknowledgement:** within 5 business days.
- **Assessment + triage:** we confirm, assess severity, and agree on a fix
  timeline with you.
- **Disclosure:** coordinated — we publish an advisory (crediting you, if you
  wish) once a fix is released.

## Scope

In scope: the `framework/` spec tooling, the Hermes MCP server
(`platforms/hermes/`), the Claude Code plugin (`platforms/claude-code-plugin/`),
the shared tooling in `tools/` (the SDD linter, the saga driver and the sync
scripts among others), the shared `tests/` tooling, and this repository's own automation
(`.github/workflows/`, `scripts/`) — workflow definitions and hook scripts
both execute, and some workflows run on a self-hosted runner pool.

Out of scope: `legacy/`, a parking area for plugin skills pulled from the
shipped surface — nothing under it is discovered or shipped — and the
pre-migration archive branch
`legacy-ucx-v3.2-read-only`.

## Automated security checks

**Only three of the checks below can block a merge:** `bandit`,
`detect-secrets` and `detect-private-key`. They run in the `pre-commit` job,
which is a required status check on `main`
(`call / Lint / format / security hooks`). Everything else reports without
gating: a red advisory check leaves a pull request warned but mergeable, and
maintainers triage those findings by hand. The one control that stops a change
before it lands is GitHub's secret-scanning push protection, described at the
end of this section.

**Configured in `.github/workflows/`**, run in CI only:

- **CodeQL** — code scanning for `actions` and `python` (`codeql.yml`).
- **semgrep** — SAST (`sast-scan.yml`).
- **osv-scanner** — dependency vulnerability scanning across the repository's
  manifests (`dep-scan.yml`).
- **gitleaks** — secret scanning over the **full git commit history**, not the
  working tree (`secret-scan.yml`); suppressions live in `.gitleaks.toml`.
- **trivy config** — IaC / misconfiguration scanning (`trivy-scan.yml`).

On a pull request from a branch of this repository, each reports both as its
own workflow check and as a code-scanning check run built from uploaded SARIF
(CodeQL produces one workflow check per language, so three in total). **On a
pull request from a fork, `sast-scan`, `dep-scan` and `trivy-scan` do not run
at all, and no code-scanning check is produced** — expect fewer checks there,
not a broken pipeline.

Only the workflow check reflects `fail-on-findings`, which `sast-scan`,
`dep-scan` and `trivy-scan` set to `false`: a finding does not turn those jobs
red, though a toolchain failure still can. `secret-scan` does fail its job on a
finding, and `codeql` has no findings gate at all.

**Configured in `.pre-commit-config.yaml`**, run on `git commit` and again in
CI, where `pre-commit.yml` runs the same hooks over the whole tree (see also [`CONTRIBUTING.md`](CONTRIBUTING.md#secret-scanning--where-each-pass-runs)):

- **bandit** — Python security linter, scoped to `platforms/hermes/src/` and
  `tests/`.
- **detect-secrets** (baselined in `.secrets.baseline`) +
  **detect-private-key** — secret scanning.

`pip-audit` is configured in that file but runs in neither place: it declares
`stages: [manual]`, so it scans `tests/conformance/requirements.txt` only when
invoked explicitly.

A repository-wide `exclude:` hides `legacy/`, `framework/` and the plugin's
vendored copy of the spec from **every** hook in that file, both secret
scanners included. Secrets under those paths are covered instead by
`secret-scan.yml`, which scans the full history and is not subject to the
exclude.

**Configured in the repository's security settings**, outside any file here:
**secret scanning with push protection**, which rejects a push containing a
recognised provider token outright — scanning for non-provider and custom
patterns is not enabled, so it does not catch every secret — and
**Dependabot**, which raises security alerts and dependency-update pull
requests.
