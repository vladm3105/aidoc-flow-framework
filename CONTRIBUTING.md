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

## How to add a test, a skill, a lint check

See [`tests/CONTRIBUTING.md`](tests/CONTRIBUTING.md) (test-suite contribution guidance).

## How to add a governance file or change a framework spec section

The framework spec is GATE-SPEC governed. Any change under `framework/` (the spec subtree) requires bumping `framework/VERSION` and going through the conformance suite. See [`docs/PROJECT.md`](docs/PROJECT.md) §6 (Change Management).

## Reporting bugs and security issues

- Functional bugs: <https://github.com/vladm3105/aidoc-flow-framework/issues>
- Security vulnerabilities: see [`SECURITY.md`](SECURITY.md) for the disclosure protocol.

## License

MIT (see [`LICENSE`](LICENSE)).
