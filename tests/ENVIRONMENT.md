# Test Environment & Prerequisites

## Required tools

| Tool | Version | Used by |
|------|---------|---------|
| Python | ≥3.11 | All Python tests |
| bash | ≥5.0 | Harness scripts |
| git | ≥2.30 | All tests |
| Claude Code CLI | latest | Tier 1 (validate), Tier 3-live, Tier 4-live, Tier 7 |
| Anthropic API key | active | Live tiers (env: ANTHROPIC_API_KEY) |

## Python dependencies

Pin file: `framework/tests/conformance/requirements.txt`

Install:

```bash
pip install -r framework/tests/conformance/requirements.txt
```

## Disk layout

- The framework is a git submodule under `aidoc-flow/framework/`.
- The plugin bundle lives at `framework/platforms/claude-code-plugin/`.
- Tests must be run from `framework/` (not parent `aidoc-flow/`).

## Network

- Tiers 1–6 (det) run fully offline.
- Tiers 3-live, 4-live, 8 require outbound HTTPS to api.anthropic.com.
- Tier 7 requires HTTPS to the marketplace URL.

## Secrets

- `ANTHROPIC_API_KEY`: must be set for live tiers; in GitHub Actions pulled from
  `secrets.ANTHROPIC_API_KEY`. Never committed.
- `MARKETPLACE_URL`: input to post-deploy workflow.

## Local-only setup

```bash
git clone --recurse-submodules <repo>
cd aidoc-flow
pip install -r framework/tests/conformance/requirements.txt
# Install Claude Code CLI (see tests/smoke/COMMANDS.md for verified command)
claude --version
```
