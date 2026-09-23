# Test Environment & Prerequisites

## Required tools

| Tool | Version | Used by |
|------|---------|---------|
| Python | ≥3.11 (CI pins 3.12) | All Python tests |
| bash | ≥5.0 | Harness scripts |
| git | ≥2.30 | All tests |

## Python dependencies

Pin file: `tests/conformance/requirements.txt`

Install:

```bash
pip install -r tests/conformance/requirements.txt
```

## Disk layout

- Single repository, no submodules.
- Tests run from the repository root (not from `framework/`).

## Network

- All suites run fully offline (PyYAML + jsonschema from the pin file).

## Local-only setup

```bash
git clone <repo>
pip install -r tests/conformance/requirements.txt
python3 -m unittest discover -s tests/conformance
```
