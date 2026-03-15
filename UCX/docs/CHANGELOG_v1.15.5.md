# CHANGELOG v1.15.5 - Persona Prompts as Default Review Mode

**Release Date**: 2026-03-14

## Overview

This release changes the default review mode from unified prompt to persona prompts, providing better review quality out of the box.

## Breaking Changes

**Default Mode Changed**: `ucx review` now uses persona prompts mode by default.

| Aspect | Before (v1.15.4) | After (v1.15.5) |
|--------|------------------|-----------------|
| Default mode | Unified prompt | Persona prompts |
| Large doc handling | Auto-switch to persona | Already using persona |
| Flag for unified | N/A (was default) | `--unified` or `-u` |

## Rationale

Testing showed that persona prompts mode produces significantly better results:

| Metric | Unified Prompt | Persona Prompts |
|--------|----------------|-----------------|
| Response tokens | ~500 (truncated) | ~25,000 (complete) |
| Findings detail | Summary only | Structured per-persona |
| Score accuracy | Often 0 (incomplete) | Full category-weighted |
| Large doc support | Poor | Excellent |

## Migration

**No code changes required.** Existing scripts using `ucx review` will automatically use the better persona prompts mode.

To explicitly use unified mode (for small documents or faster reviews):
```bash
ucx review brd docs/01_BRD/BRD-01 --unified
ucx review brd docs/01_BRD/BRD-01 -u
```

The `--persona` flag is kept for backwards compatibility but is now a no-op.

## Files Modified

| File | Changes |
|------|---------|
| `ucx/cli/main.py` | Changed default mode, updated help text |
| `ucx/version.py` | Updated to v1.15.5 |

## Usage

```bash
# Default: persona prompts mode (recommended)
ucx review brd docs/01_BRD/BRD-01

# Explicit unified mode (faster, less detailed)
ucx review brd docs/01_BRD/BRD-01 --unified
```
