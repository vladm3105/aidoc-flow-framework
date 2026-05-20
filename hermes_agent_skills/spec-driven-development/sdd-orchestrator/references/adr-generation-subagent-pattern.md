# ADR Generation Subagent Pattern — Timeout & Pre-Extraction

## Problem: ADR Subagents Consistently Time Out at 600s

ADR generation via `delegate_task` subagents hits a hard 600s wall-clock timeout.
The subagent must read 4-6 upstream files (BDD, EARS, PRD, BRD = ~15-30KB each),
the ADR-TEMPLATE.yaml (~15KB), and a reference ADR (~30-70KB) — 100-300KB total.

Observed pattern (TradeGent CC, 2026-05-12):
- Subagent spends 200-400s reading files
- Then writes the YAML via write_file (success)
- Then the LLM call for the summary text exceeds the 600s timeout
- Result: subagent shows "timeout" but the file WAS written correctly

## Timeout ≠ Failure (Critical Rule)

After any ADR subagent timeout, verify disk state BEFORE re-dispatching:

```python
import os, datetime, yaml

path = "/opt/data/tradegent_covered_calls/05_ADR/ADR-NN.yaml"
if os.path.exists(path):
    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(path))
    sz = os.path.getsize(path)
    with open(path) as f:
        data = yaml.safe_load(f)
    sections = len(data)
    kc = len(data.get("decision", {}).get("key_components", []))
    print(f"ADR-NN: {sz//1024}KB, {sections} sections, {kc} components, mtime={mtime}")
else:
    print("ADR-NN: NOT WRITTEN — re-dispatch needed")
```

If the file exists with 13-15 sections and yaml.safe_load() succeeds:
**The fix was applied. Do not re-dispatch.** The timeout was on summary generation only.

If the file does NOT exist or has <5 sections:
**Re-dispatch is needed.** The subagent never reached write_file.

## Mitigation: Pre-Extracted Upstream Data

For ADRs that require complex upstream context, pre-extract the BDD/EARS data
into the subagent prompt instead of having the subagent read files:

```python
# Pre-extract BDD scenario summary
import yaml
bdd_path = f"/opt/data/tradegent_covered_calls/04_BDD/BDD-0{num}.yaml"
with open(bdd_path) as f:
    data = yaml.safe_load(f)

ss = data.get("scenario_structure", {}).get("scenarios", {})
scenario_summary = []
for stype in ["success", "error", "recovery", "audit"]:
    for s in ss.get(stype, []):
        scenario_summary.append(
            f"[{stype.upper()}] {s.get('id','')}: {s.get('name','')} ({s.get('priority','')})"
        )

# Pass scenario_summary, feature name, and description in the subagent prompt
# Subagent then only needs to read ADR-TEMPLATE.yaml + reference ADR
# No need to read BDD/EARS/PRD/BRD files
```

This reduces subagent file-reading time from 200-400s to 50-100s.

## Batch Size

`delegate_task` enforces `max_concurrent_children=3`. For ADR generation:
- Phase 1: 2 benchmarks (ADR-01 + ADR-07) — one dispatch
- Phase 2: 7 remaining engines — 3 dispatches (3+3+1)
- Phase 3: 10 cross-cutting — 4 dispatches (3+3+3+1)

Cross-cutting ADRs tend to be shorter (no engine-specific detail needed)
but still benefit from pre-extracted BDD context about which findings they unblock.

## Verification Checklist After Each Phase

- [ ] All expected files exist on disk
- [ ] All files parse with yaml.safe_load()
- [ ] All files have 13-15 top-level sections
- [ ] Each file's decision.key_components has >=3 entries
- [ ] File sizes are in the 30-70KB range (not 0-5KB stubs)
- [ ] Mermaid diagrams present in architecture_flow section
- [ ] 2-3 alternatives listed with rejection reasons
