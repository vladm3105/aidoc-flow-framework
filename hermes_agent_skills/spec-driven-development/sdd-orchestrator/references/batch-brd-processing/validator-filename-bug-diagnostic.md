# UCX sdd_validate Filename Heuristic Bug Diagnostic

## Symptom

A YAML BRD file fails validation with:
- Error: "Missing or invalid YAML frontmatter"
- Pass log: "Requires YAML data (skipped for MD)"
- Generated fix file: `*_validated.yaml` (validator's own re-serialization)

The `*_validated.yaml` file also fails with the same error.

## Diagnostic Steps

### Step 1: Verify YAML is structurally valid

```python
import yaml
with open("BRD-08_performance_review_cadence.yaml") as f:
    doc = yaml.safe_load(f)
print("YAML: OK")
print(f"Frontmatter type: {type(doc)}")
```

If this passes — the YAML is valid. The issue is validator type detection.

### Step 2: Compare bytes against a passing file

```python
import subprocess

# Compare first 5 lines
for path in ["BRD-07_market_state_thesis_monitor.yaml", "BRD-08_performance_review_cadence.yaml"]:
    r = subprocess.run(["head", "-5", path], capture_output=True, text=True)
    print(f"=== {path} ===")
    print(r.stdout)
```

If frontmatter is identical — confirmed validator issue, not content issue.

### Step 3: Check raw bytes at file start

```python
with open("BRD-08_performance_review_cadence.yaml", "rb") as f:
    raw = f.read(100)
print(raw.hex())
# Look for: BOM (EF BB BF), null bytes (00), wrong encoding markers
# Valid YAML starts with: `id:` = 69 64 3a 0a or `---` = 2d 2d 2d 0a
```

### Step 4: Rename and re-validate

```bash
cp BRD-08_performance_review_cadence.yaml BRD-08.yaml
# Run sdd_validate on BRD-08.yaml
```

If BRD-08.yaml passes (0 errors, 0 warnings) with identical content —
**confirmed filename heuristic bug.**

## Known Trigger Patterns

The validator appears to misclassify filenames with:
- Long descriptive suffixes (`_performance_review_cadence`)
- Multiple underscore-separated words
- Certain keywords (`review`, `performance`, `cadence`)

Short canonical names (`BRD-NN.yaml`) consistently pass.

## Evidence from TradeGent CC Session

| Filename | Result |
|---|---|
| `BRD-07_market_state_thesis_monitor.yaml` | PASS |
| `BRD-08_performance_review_cadence.yaml` | FAIL ("skipped for MD") |
| `BRD-08.yaml` (identical content, renamed from above) | PASS |
| `BRD-09_portfolio_operating_system.yaml` | PASS |

Byte-level comparison confirmed: identical structure, identical frontmatter,
identical YAML type. Only filename differed.

## Workaround

1. Rename failing file to short canonical form: `BRD-NN.yaml`
2. Validate — should now pass
3. Document the rename in CHANGELOG with the bug entry
4. Plan to rename back to descriptive form once validator is fixed

## Long-term Fix

Report to UCX framework maintainers with:
1. Failing filename + passing filename (identical content)
2. Validator version (from sdd_validate output)
3. Reproduction: any BRD with the pattern `_performance_review_cadence.yaml`

## Status Marking

When this bug is encountered, mark the BRD as:

```
Status: VALIDATED (workaround: renamed from {old_name} to BRD-NN.yaml
due to UCX sdd_validate filename heuristic bug — content identical,
byte-level comparison confirms structural validity)
```

Do NOT mark as "CONTENT COMPLETE" or skip validation. The workaround IS a
validation path — just with a temporary filename change.
