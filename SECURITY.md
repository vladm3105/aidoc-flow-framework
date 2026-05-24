# Security Policy

## Supported versions

This is a specification + tooling project (an engine-agnostic `framework/` spec
plus two platforms). Security fixes are applied to the latest release line.

| Component | Supported |
|-----------|-----------|
| Latest project release (`v1.x`) | ✅ |
| `framework/` spec — latest (`0.3.x`) | ✅ |
| Platforms — latest tagged release | ✅ |
| Older / pre-cutover (`< v1.0`, archive branch) | ❌ |

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
and the shared `tests/` tooling. The `legacy/` archive is **out of scope**
(frozen pre-migration content).

## Automated security checks

This repository runs, in CI and via pre-commit:

- **CodeQL** — static analysis (code scanning) for Python.
- **bandit** — Python security linter (SAST).
- **detect-secrets** + **detect-private-key** — secret scanning.
- **pip-audit** — dependency vulnerability scanning.
- **Dependabot** — dependency update PRs and security alerts.

GitHub-native **secret scanning + push protection** and **Dependabot alerts**
are enabled in the repository's security settings.
