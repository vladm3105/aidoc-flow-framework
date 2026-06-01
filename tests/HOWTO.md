# How to Use the Test Suite

Quick paths for common workflows. For strategy, see
`plans/PLUGIN-TEST-SUITE-PLAN.md`. For per-test detail, see `SCENARIOS.md`.

## Common workflows

### "Run everything deterministic before I push"

```bash
bash tests/scripts/test-plugin.sh --suite=pre-deploy
```

Runs Tiers 1, 2, 3 (det), 4 (det), 5. Under 5 min on a laptop.

### "Run just one layer"

```bash
bash tests/scripts/test-layer.sh brd          # or prd, ears, bdd, adr, spec, tdd, iplan
```

### "Run the full BRD → IPLAN chain"

```bash
bash tests/scripts/test-fullpath.sh            # deterministic
bash tests/scripts/test-fullpath.sh --live     # include live autopilot chain (expensive)
```

### "Include live LLM probes"

Append `--live` to any suite. Requires `claude` CLI on PATH and authenticated.

### "Run the LLM code reviewer on my diff"

```bash
REVIEW=1 bash tests/scripts/test-plugin.sh --suite=review
```

### "Run the marketplace pre-deploy gate locally"

```bash
LIVE=1 bash tests/scripts/test-plugin.sh --suite=pre-deploy --live
```

This is what `release.yml` runs in CI.

## Selecting a single test class

```bash
cd framework
python3 -m unittest tests.acceptance.deterministic.test_layer_brd.LayerBrdTests -v
```

## Re-running only failed tests (after CI failure)

```bash
cd framework
python3 -m unittest tests.acceptance.deterministic.test_fullpath.FullpathChainTests.test_forward_tag_closure -v
```

## Environment variables

| Variable | Effect |
|----------|--------|
| `LIVE=1` | Enables live LLM tier (claude -p) |
| `REVIEW=1` | Enables LLM code-reviewer tier |
| `MARKETPLACE_URL` | Required for post-deploy smoke |
| `BASE_REF` | Base ref for LLM reviewer diff (default `origin/main`) |
| `MAX_DIFF_BYTES` | Cap on diff size piped to reviewer (default 262144) |
