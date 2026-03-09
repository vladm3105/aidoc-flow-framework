# UCX vs Claude Skills Feature Comparison

**Document ID**: UCX-COMPARISON-001
**Date**: 2026-03-09 (Updated)
**Status**: Full Parity Achieved

---

## Executive Summary

This document compares features between the UCX (Unified Context) Framework and the Claude Skills system (e.g., `doc-brd-autopilot`). Following the Python migration (v1.1.0), UCX now has full feature parity with Claude Skills.

---

## Feature Comparison Matrix

| Feature | Claude Skills | UCX | Status |
|---------|--------------|-----|--------|
| **Document Creation** | `doc-brd`, `doc-prd`, etc. | `ucx create` | PARITY |
| **Document Review** | `doc-brd-audit` | `ucx review` | PARITY |
| **Document Remediation** | `doc-brd-fixer` | `ucx remediate` | PARITY |
| **Full Autopilot Cycle** | `doc-brd-autopilot` | `ucx autopilot` | PARITY |
| **Multi-Persona Authoring** | Per skill | Skill injection | PARITY |
| **Validation Integration** | `doc-*-validator` | `ucx validate` | PARITY |
| **Template Loading** | From skill | `--template` option | PARITY |
| **Upstream Artifact Support** | `--upstream` | `--from-upstream` | PARITY |
| **Reference Document Loading** | `--ref` | `--from-ref` | PARITY |
| **Drift Monitoring** | `.drift_cache.json` | `DriftMonitor` class | PARITY |
| **Smart Document Detection** | Auto-detect action | `UCXAutopilot` | PARITY |
| **IPLAN Input Support** | `--iplan` option | `--from-iplan` | PARITY |
| **Multi-Document Batch** | Chunked by 3 | `BatchProcessor` | PARITY |
| **Confidence Gate** | `manual-required` check | Fix confidence levels | PARITY |
| **PRD-Ready Scoring** | Score >= 90% check | `min_score` config | PARITY |
| **Multi-Provider LLM** | Anthropic only | LiteLLM (any provider) | **UCX ADVANTAGE** |

---

## UCX Advantages Over Claude Skills

### 1. Multi-Provider LLM Support

UCX uses LiteLLM for access to multiple providers:

```bash
# Anthropic (default)
UCX_MODEL=opus ucx review brd docs/01_BRD/BRD-01.md

# OpenAI
UCX_MODEL="openai/gpt-4o" ucx review brd docs/01_BRD/BRD-01.md

# Local Ollama (free)
UCX_MODEL="ollama/llama3" UCX_API_BASE="http://localhost:11434" ucx review brd docs/01_BRD/BRD-01.md
```

### 2. Python API

UCX provides a full Python API for programmatic use:

```python
from ucx import UCXAutopilot, UCXConfig

config = UCXConfig(model="opus", max_iterations=3, min_score=90)
pilot = UCXAutopilot(config)

result = pilot.run(
    doc_type="brd",
    target=Path("docs/01_BRD/BRD-01"),
    from_ref=Path("docs/00_REF/"),
)
```

### 3. MCP Server

UCX can run as an MCP server for integration with other tools:

```bash
ucx serve --transport http --port 8765
```

### 4. Observability

UCX includes OpenTelemetry instrumentation for tracing and metrics.

---

## Implementation Mapping

| Claude Skill | UCX CLI | UCX Python API |
|--------------|---------|----------------|
| `/doc-brd` | `ucx create brd` | `UCCPhase.create("brd", ...)` |
| `/doc-brd-audit` | `ucx review brd` | `UCRPhase.review("brd", ...)` |
| `/doc-brd-fixer` | `ucx remediate brd` | `UCRemPhase.generate_fixes(...)` |
| `/doc-brd-autopilot` | `ucx autopilot brd` | `UCXAutopilot.run("brd", ...)` |
| `/doc-brd-validator` | `ucx validate brd` | Built into `UCRPhase` |

---

## Migration Guide

### From Shell Scripts to CLI

Old (deprecated):
```bash
./run_ucc.sh brd ./docs/01_BRD/ --from-ref ./docs/00_REF/
./run_ucr.sh brd ./docs/01_BRD/
./run_ucrem.sh ./docs/01_BRD/BRD_UCR_REVIEW.md ./docs/01_BRD/
```

New:
```bash
ucx create brd docs/01_BRD/BRD-01 --from-ref docs/00_REF/
ucx review brd docs/01_BRD/BRD-01.md
ucx remediate brd docs/01_BRD/BRD-01.md --review-report docs/01_BRD/BRD_UCR_REVIEW.md
```

### From Claude Skills to UCX CLI

Old:
```bash
/doc-brd-autopilot BRD-01 --from-ref ./docs/00_REF/
```

New:
```bash
ucx autopilot brd docs/01_BRD/BRD-01 --from-ref docs/00_REF/ --max-iterations 3
```

---

## Feature Implementation Details

### Drift Monitoring

```python
from ucx.core.drift import DriftMonitor
from pathlib import Path

monitor = DriftMonitor()
has_drift, changed_files = monitor.check(
    target=Path("docs/01_BRD/BRD-01"),
    upstream=Path("docs/00_REF/"),
)
```

### Batch Processing

```python
from ucx.core.batch import BatchProcessor

processor = BatchProcessor(config, batch_size=3)
results = await processor.process([
    ("brd", Path("docs/01_BRD/BRD-01")),
    ("brd", Path("docs/01_BRD/BRD-02")),
    ("brd", Path("docs/01_BRD/BRD-03")),
])
```

### Checkpointing

```python
from ucx.core.checkpoint import CheckpointManager

checkpoint = CheckpointManager(checkpoint_dir=Path("./checkpoints"))
# Automatic resume on failure
```

---

## See Also

- [README.md](../README.md) - Package overview
- [SKILL_INDEX.md](../SKILL_INDEX.md) - Complete skill mapping
- [HOW_TO_USE.md](HOW_TO_USE.md) - Usage guide
