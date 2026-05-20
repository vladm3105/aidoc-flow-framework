# YAML Quoting Rules for SDD Documents

## The Problem

SDD documents (BRD, PRD, EARS, BDD, ADR, SPEC, TDD, IPLAN) are YAML files.
Many fields contain comparison operators: `target: >=90%`, `criterion: >25% gap`,
`metric: <=3x debt`. YAML's parser interprets `>`, `<`, `>=`, `<=` as block
scalar chomping indicators when they appear at the start of a value.

## What Breaks

| Pattern | Example | Error |
|---------|---------|-------|
| `target: >=X` | `target: >=90% of candidates` | `YAMLError: expected chomping` |
| `target: <=X` | `target: <=3x net debt` | Same |
| `criterion: >X` | `criterion: >25% single-day gap` | Same |
| `metric: <X` | `metric: <15 min staleness` | Same |
| Multi-line with `>=` inside parens | `- Gate 3: (beat rate >=60%)\n  remaining` | `YAMLError: could not find expected ':'` |

## The Fix

### Rule 1: Quote any bare value starting with comparison operators

```yaml
# WRONG
target: >=90% of candidates

# RIGHT
target: '>=90% of candidates remain qualified at next quarterly re-screen'
```

### Rule 2: Collapse multi-line items with inline operators into single quoted string

```yaml
# WRONG
- Gate 3: Fundamental health check (FCF positive, net debt/EBITDA <=3x, revenue >=5%,
  beat rate >=60%)

# RIGHT
- 'Gate 3: Fundamental health check (FCF positive, net debt/EBITDA <=3x, revenue >=5%, beat rate >=60%)'
```

### Rule 3: Post-process after yaml.dump()

When generating SDD documents via Python, use this post-processing pattern:

```python
import yaml, re

raw = yaml.dump(brd_dict, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120)
lines = raw.split('\n')
for i, line in enumerate(lines):
    stripped = line.lstrip()
    for prefix in ['target: ', 'criterion: ', 'metric: ']:
        if stripped.startswith(prefix):
            val = stripped[len(prefix):].strip()
            if val and val[0] in '><=':
                indent = line[:len(line) - len(stripped)]
                lines[i] = f"{indent}{prefix}'{val}'"
output = '\n'.join(lines)

# Verify
yaml.safe_load(output)  # must not raise
with open(path, 'w') as f:
    f.write(output)
```

## Field Names Known to Trigger This

- `target` (in goals, success_metrics, acceptance_criteria, success_criteria)
- `criterion` (in acceptance_criteria)
- `metric` (in success_metrics, non_functional_requirements)
- Any business_rules entry starting with a number+comparison

## Verification

After writing any SDD YAML file, always run:

```bash
python3 -c "import yaml; yaml.safe_load(open('01_BRD/BRD-NN_doc.yaml'))" && echo VALID || echo BROKEN
```

If BROKEN, scan for unquoted `>=`, `<=`, `>`, `<` at value start positions.

## Programmatic YAML Patching — Indentation Preservation

When using Python string replacement (`content.replace(old, new)`) to insert
new list items into YAML files, the replacement text MUST preserve the exact
indentation of the surrounding list. This is the single most common failure mode
in programmatic YAML editing.

**Example — inserting a new business rule into a BRD:**

```python
# WRONG — new rule at column 0 breaks YAML structure
old = "- 'Detect stale position data: ...'"
new = "- 'Detect stale position data: ...'\n- 'Position data sanity check: ...'"

# RIGHT — new rule indented to match surrounding list (4 spaces here)
old = "- 'Detect stale position data: ...'"
new = "- 'Detect stale position data: ...'\n    - 'Position data sanity check: ...'"
```

**Detection**: `yaml.safe_load()` fails with `expected <block end>, but found '-'`.

**Heuristic fix** (runnable in execute_code):
```python
lines = content.split('\n')
fixed = []
for i, line in enumerate(lines):
    if line.startswith("- '") and i > 30:  # skip early metadata
        prev = lines[i-1] if i > 0 else ""
        if prev.startswith("    ") or prev.startswith("      "):
            line = "    " + line  # indent to match surrounding list
    fixed.append(line)
content = '\n'.join(fixed)
```

This hit 3 times during BRD-10 remediation. Always verify replacement indentation
against surrounding context before writing.
