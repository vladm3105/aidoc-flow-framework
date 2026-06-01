# Verified Anthropic CLI commands

> Confirm against current Anthropic docs whenever the verification date is older
> than a release cycle. Update `tests/smoke/install-from-marketplace.sh` whenever
> verified syntax changes.

## Install Claude Code CLI (canonical)

```
npm install -g @anthropic-ai/claude-code
```

Source: <https://code.claude.com/docs/en/setup> (verified 2026-05-31).

## Install plugin from a local bundle (preferred for smoke)

```
claude --plugin-dir <path-to-bundle>
```

Loads a plugin directly from a local directory without requiring installation.
Accepts a directory or a `.zip` archive (requires Claude Code v2.1.128+). Local
plugins take precedence over installed marketplace plugins with the same name.
Multiple `--plugin-dir` flags may be passed.

Source: <https://code.claude.com/docs/en/plugins> (verified 2026-05-31).

This works against any local checkout (e.g. `framework/platforms/claude-code-plugin/`)
and requires no marketplace endpoint. It is the path `tests/scripts/test-plugin.sh`
uses today.

## Install plugin from a marketplace (current state)

The `claude plugin install` CLI subcommand exists and is the scriptable path:

```
claude plugin install <plugin>[@<marketplace-name>] [--scope user|project|local]
```

It expects a **plugin name** (optionally `name@marketplace`), not a URL — the
marketplace must be added first:

```
claude plugin marketplace add <path-or-url>
claude plugin install <plugin>@<marketplace-name>
```

For a local directory marketplace containing `.claude-plugin/marketplace.json`:

```
claude plugin marketplace add ./my-marketplace
claude plugin install <plugin>@<marketplace-name>
```

Sources:

- <https://code.claude.com/docs/en/plugins-reference> (verified 2026-05-31)
- <https://code.claude.com/docs/en/plugin-marketplaces> (verified 2026-05-31)
- <https://code.claude.com/docs/en/discover-plugins> (verified 2026-05-31)

An equivalent in-session slash form (`/plugin install <plugin>@<marketplace>`)
is documented but is interactive, not automatable from a smoke script.

## Verification log

| Date | Channel | Verified | Notes |
|------|---------|----------|-------|
| 2026-05-31 | context7 (`/websites/code_claude`) → <https://code.claude.com/docs/en/setup> | `npm install -g @anthropic-ai/claude-code` | Canonical install path. |
| 2026-05-31 | context7 (`/websites/code_claude`) → <https://code.claude.com/docs/en/plugins> | `claude --plugin-dir <path>` | Local-bundle path used by `tests/scripts/test-plugin.sh`. |
| 2026-05-31 | context7 (`/websites/code_claude`) → <https://code.claude.com/docs/en/plugins-reference> | `claude plugin install <plugin>[@<marketplace>]` | CLI subcommand; argument is plugin name, not a URL. |
| 2026-05-31 | context7 (`/websites/code_claude`) → <https://code.claude.com/docs/en/plugin-marketplaces> | `claude plugin marketplace add <path-or-url>` | Marketplace must be added before `install`. |
