# Verified Anthropic CLI commands

> Source verification deferred — confirm against current docs before relying on
> these commands in CI. Update this file (and tests/smoke/install-from-marketplace.sh)
> whenever the verified syntax changes.

## Install Claude Code CLI (canonical)

```
npm install -g @anthropic-ai/claude-code
```

(Alternative: `curl -fsSL https://claude.ai/install.sh | bash` — verify before use.)

## Install plugin from a local bundle (preferred for smoke)

```
claude --plugin-dir <path-to-bundle> ...
```

This works against any local checkout of the plugin (e.g. the framework's bundled
copy at `framework/platforms/claude-code-plugin/`) and requires no marketplace
endpoint. It is the path scripts/test-plugin.sh already uses today.

## Install plugin from a marketplace URL (manual today)

Marketplace install syntax depends on the Claude Code CLI version. Verify with
`claude plugin --help` before automating. The post-deploy smoke workflow today
uses workflow_dispatch with a tarball URL plus the `--plugin-dir <unpacked>` form
as a fallback so it remains automatable irrespective of marketplace UX.

## Verification log

| Date | Channel | Verified | Notes |
|------|---------|----------|-------|
| —    | —       | —        | Pending verification — see Task 8.0 |
