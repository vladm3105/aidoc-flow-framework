# YAML Patch Indentation Auto-Fix

## Problem

When inserting new YAML list items via string-based `patch` operations (e.g., adding a new `business_rule` to a `functional_requirements` block), the inserted line often ends up at column 0 instead of the required indentation level. This produces:

```
while parsing a block mapping
expected <block end>, but found '-'
  in "<file>", line N, column 1:
    - 'New business rule ...'
```

The `-` at column 0 breaks the YAML structure because it appears to start a new top-level key when it should be a child item of the current mapping.

## Root Cause

When constructing replacement strings for `patch` operations, the new lines must include the same leading whitespace as the lines they're replacing. If the old string is at 4-space indent but the new string omits that indent, the patch tool inserts the replacement verbatim at column 0.

Common culprits:
- Adding a new list item to `business_rules` (should be indented 4 spaces)
- Adding a new constraint or assumption (should be indented 2 spaces under `items:`)
- Adding a new acceptance criterion (should be indented 6 spaces under `items:`)

## Auto-Fix Script

Run this after any patch-heavy editing session to detect and fix unindented list items:

```python
import subprocess, yaml

path = "/path/to/document.yaml"
r = subprocess.run(["cat", path], capture_output=True, text=True)
content = r.stdout

lines = content.split('\n')
fixed = []
for i, line in enumerate(lines):
    # Detect: line starts with "- '" at column 0, previous line is indented
    if line.startswith("- '") and i > 30:
        prev = lines[i-1] if i > 0 else ""
        if prev.startswith("    ") or prev.startswith("      "):
            # This is likely a business rule / list item that should be indented
            line = "    " + line
            print(f"Fixed indentation at line {i+1}")
    fixed.append(line)

content = '\n'.join(fixed)

# Verify
try:
    yaml.safe_load(content)
    print("YAML valid after fix")
    with open(path, 'w') as f:
        f.write(content)
except yaml.YAMLError as e:
    print(f"Still broken: {e}")
```

## Prevention

When using `patch` for YAML modifications, always include the correct leading whitespace in both the `old_string` and `new_string`. If inserting a new item at the same level, match the whitespace of surrounding items exactly.

### Correct pattern:

```python
# Adding a business rule at 4-space indent
old = (
    "    - 'Existing business rule'\n"
    "    acceptance_criteria:"
)
new = (
    "    - 'Existing business rule'\n"
    "    - 'New business rule with correct 4-space indentation'\n"
    "    acceptance_criteria:"
)
```

### Wrong pattern:

```python
# Missing leading spaces in new line
old = "    - 'Existing business rule'\n    acceptance_criteria:"
new = "    - 'Existing business rule'\n- 'New rule'\n    acceptance_criteria:"
#                                         ^ no indent — will break YAML
```

## Alternative: Full Rewrite

When making multiple edits to the same section, it's often safer to rebuild the entire section via `execute_code` rather than chaining multiple `patch` calls. Read the file, modify the Python dict representation with `yaml.load()`/`yaml.dump()`, and write back — indentation is handled automatically by the YAML library.
