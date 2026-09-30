# How to Use the Test Suite

Quick paths for common workflows. All commands run from the repository root.
For per-suite detail, see `tests/README.md` and `tests/acceptance/README.md`.

## Common workflows

### "Run everything deterministic before I push"

```bash
python3 -m unittest discover -s tests/unit
python3 -m unittest discover -s sdd_doc_lint/tests
python3 -m unittest discover -s tests/conformance
python3 -m unittest discover -s tests/acceptance/deterministic
```

### "Run just one layer"

```bash
bash tests/scripts/test-layer.sh brd          # or prd, ears, bdd, adr, spec, tdd, iplan
```

### "Run the full BRD → IPLAN chain"

```bash
bash tests/scripts/test-fullpath.sh            # deterministic
```

## Selecting a single test class

```bash
python3 -m unittest tests.acceptance.deterministic.test_layer_brd.LayerBrdTests -v
```

## Re-running only failed tests (after CI failure)

```bash
python3 -m unittest tests.acceptance.deterministic.test_fullpath.FullpathChainTests.test_forward_tag_closure -v
```
