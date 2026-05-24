# UCX `sdd_remediate` Content Limitations

## What the tool does vs. what it does NOT do

`sdd_remediate` is a **structural/schema fixer** — it scans YAML files for:

- Placeholder tokens (`xxxx`, `TBD` without explanation)
- Invalid element ID formats (wrong hash length, wrong segment count)
- Missing required sections

It does **NOT** perform semantic content authoring:

- Adding new scenarios to `scenario_structure.scenarios`
- Rewriting boilerplate Gherkin into domain-specific language
- Generating missing success/error/recovery/audit/edge/performance blocks
- Applying narrative recommendations from markdown review reports (UCREM, chairperson manifest)

## Reproduction: TradeGent CC BDD-02, 2026-05-08

### Before remediation

```
BDD-02.yaml: 7 scenarios (suc:4, err:2, recovery:1)
```

### UCREM report claims

```
"BDD-02: was 7 → now 15 scenarios"
"+3 Gate scenarios, +1 audit logging, +1 data-source recovery"
"+7 total new scenarios; 9 existing rewritten"
```

### What `sdd_remediate` actually produced

```
$ sdd_remediate(document=BDD-02.yaml, remediation_report=UCREM-REPORT.md)
→ findings: 2 tier2 (placeholder tokens, element_id format)
→ derived copy: BDD-02_remediate_v2.yaml
→ applied_changes: "none (copy-only deterministic baseline)"
→ md5sum(source) == md5sum(derived) — byte-for-byte identical
→ scenarios in derived copy: still 7
```

### What subagent dispatch actually produced (same session, 2026-05-08)

```
delegate_task(tasks=[bdd-02-fixer, bdd-04-fixer, bdd-05-fixer])
→ BDD-02 rewritten from 7 → 12 scenarios (suc:7, err:2, rec:2, audit:1)
→ BDD-04 rewritten from 7 → 12 scenarios
→ BDD-05 rewritten from 7 → 11 scenarios
→ All files: md5 changed, yaml.safe_load() verified, sdd_validate PASS 0/0
```

The markdown report described 58 content-level findings. `sdd_remediate` ignored all of them because they require semantic authoring, not structural repair.

### Subagent dispatch concurrency

`delegate_task` enforces `max_concurrent_children=3`. For 7 docs, split into three batches:

- Batch 1: BDD-02, BDD-04, BDD-05
- Batch 2: BDD-06, BDD-07, BDD-08
- Batch 3: BDD-09 (or pair with a lightweight doc)
Each fixer subagent reads the upstream EARS, the original BDD, and a per-document fix list, then writes the complete rewritten YAML back to the original path.

### Timeout ≠ failure (critical edge case)

Subagent timeout at 600s does NOT mean the fix wasn't applied. At TradeGent CC:

- BDD-05 fixer timed out at 600s (3 times) but the file WAS written with 11 scenarios
- The subagent wrote the YAML to disk via write_file, then the LLM call for the summary text exceeded the timeout
- Verification rule: after any timeout, check `os.path.getmtime()` and `yaml.safe_load()` on the target file. If mtime advanced AND scenario count increased → fix applied. Only re-dispatch if the file is unchanged from pre-remediation state.
- All 3 BDD-05 timeout attempts produced the same final file (11 scenarios) — the subagent did its work before timing out on the summary generation.

## Why markdown reports don't work with `sdd_remediate`

`sdd_remediate` expects a **structured JSON remediation report** with machine-actionable fields:

```json
{
  "findings": [
    {
      "finding_id": "P0-...",
      "recommended_action": "add_scenario",
      "target_path": "scenario_structure.scenarios.success",
      "patch": { ... }
    }
  ]
}
```

A narrative markdown synthesis (UCREM report, chairperson manifest) is prose — it says "add Gate 3 scenario" but does not provide the YAML block, the ID, the Gherkin steps, or the trace tags. `sdd_remediate` cannot parse prose instructions.

## Correct content-remediation path

### Option A: Scripted Python patching

1. Parse chairperson manifest into a per-document fix list
2. Write a Python script (via `execute_code`) that:
   - Reads the original YAML
   - Appends new scenario dicts to the correct `scenario_structure.scenarios.*` lists
   - Generates proper `BDD.NN.SS.xxxx` IDs with SHA256 truncated to 4 chars
   - Updates metadata counts (`total_sections`, `last_updated`)
   - Writes the modified YAML back
3. Verify with `yaml.safe_load()` + scenario count diff
4. Run `sdd_validate` for structural confirmation only

### Option B: Subagent dispatch (for Gherkin authoring)

1. Send each BDD's original YAML + the per-document fix list to `delegate_task`
2. Subagent produces a complete rewritten YAML as text output
3. Agent writes the text back to the original path
4. Verify with `yaml.safe_load()` + `sdd_validate`

### Verification step (mandatory)

After ANY remediation, verify actual disk state:

```bash
# Count scenarios in the file
grep -c "^    - id:" BDD-NN.yaml   # naive — better: yaml.safe_load count
# Check file modification time
ls -la --time-style=full-iso BDD-NN.yaml
# Compare md5 with source (if derived copy was made)
md5sum BDD-NN.yaml out/BDD-NN_remediate_v*.yaml
```

## Rule

**Never claim remediation is "applied" based solely on a remediation report narrative. Always verify the YAML files on disk with `yaml.safe_load()` or `grep`/`wc`. A report saying "fixed" is not evidence — the file is.**
