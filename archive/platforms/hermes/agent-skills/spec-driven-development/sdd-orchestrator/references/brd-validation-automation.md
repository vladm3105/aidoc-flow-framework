# BRD Validation, Generation & Element ID Assignment (Python Automation)

## When to Use

When you need to: (A) generate a new BRD YAML from scratch programmatically,
or (B) validate and assign element IDs to existing BRD files.

## Phase 0: Programmatic BRD Generation from Scratch

When generating a single BRD that doesn't come from a source rulebook (no extraction needed),
build the complete document as a Python dict, serialize with `yaml.dump()`, post-process for
comparison operators, and write in one shot.

### Step 1: Element ID Helper

```python
import hashlib

from sdd_doc_lint import compute_element_hash  # # Single source: governance/ID_NAMING_STANDARDS.md. Never re-derive the hash here.

def hash4(doc_id, section_id, title, desc=""):
    """4-char element-ID hash — delegates to the canonical implementation."""
    return compute_element_hash(doc_id, section_id, title, desc)[:4]

def eid(section, title, desc=""):
    """Generate BRD.NN.SS.xxxx element ID. Section can be int or string."""
    if isinstance(section, int):
        sec_str = f"{section:02d}"
    else:
        sec_str = str(section)  # handles non-numeric sections like 'diag'
    return f"BRD.{doc_num}.{sec_str}.{hash4(f'{doc_num}:{sec_str}:{title}:{desc}')}"
```

**Pitfall**: `section` parameter may be non-numeric (e.g., `"diag"` for the diagrams registry).
The helper MUST handle both `int` and `str` — using `f"{section:02d}"` on a string will raise
`ValueError: Unknown format code 'd'`. Use `isinstance` check.

### Step 2: Build Document as Dict

```python
import datetime
ts = datetime.datetime.now().isoformat()
doc_num = "10"  # BRD-10

doc = {
    "id": f"BRD-{doc_num}",
    "title": "Your BRD Title",
    "metadata": { ... },  # Copy from BRD-TEMPLATE.yaml
    "document_control": {
        "project_name": "...",
        "version": "1.0",
        "status": "Draft",
        "date_created": ts,
        ...
    },
    # ... all 18 sections populated with content ...
    "functional_requirements": {
        "priority_definitions": { ... },
        "requirements": [
            {
                "id": eid(7, "fr01_title", "Description"),
                "title": "FR Title",
                "capability": "...",
                "priority": "P1",
                "complexity": {"rating": "3/5", "rationale": "..."},
                "business_needs": [...],
                "business_rules": [...],
                "acceptance_criteria": {
                    "items": [
                        {"id": eid(7, "ac_name"), "criterion": "...", "target": "..."}
                    ]
                },
                "related_requirements": {"references": [...]}
            }
        ]
    },
    "adr_topics": {
        "topics": [
            {"id": eid(8, "adr_topic"), "category": "Architecture", "title": "...", ...}
        ]
    },
    # ... continue through appendix ...
}
```

### Step 3: Serialize, Post-Process, Write

```python
import yaml, re

yaml_text = yaml.dump(doc, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120)

# Quote values starting with >=, <=, >, < (YAML chomping indicator collision)
lines = yaml_text.split('\n')
quoted = []
for line in lines:
    m = re.match(r'^(\s+)(\w[\w\s]*):\s*(>=|<=|>|<)(.+)$', line)
    if m:
        indent, key, op, rest = m.groups()
        if not rest.startswith("'") and not rest.startswith('"'):
            line = f"{indent}{key}: '{op}{rest}'"
    quoted.append(line)

final_yaml = '\n'.join(quoted) + '\n'

with open(output_path, 'w') as f:
    f.write(final_yaml)

# Verify
import subprocess
r = subprocess.run(["python3", "-c", f"import yaml; yaml.safe_load(open('{output_path}'))"],
                   capture_output=True, text=True)
assert r.returncode == 0, f"YAML invalid: {r.stderr}"
```

### Step 4: UCX Validate

After generation, run `sdd_validate` via MCP — never claim "validated" from `yaml.safe_load()` alone.

```
mcp_sdd_lifecycle_sdd_validate(doc_type="brd", document="path/to/BRD-NN.yaml", layer="01_BRD")
```

## Phase 1: Structural Validation (for existing BRDs)

Use `subprocess.run(["cat", path])` to get clean content — `read_file()` inside
execute_code returns line-numbered output that breaks YAML parsers.

```python
import yaml, subprocess, re

CANONICAL_SECTIONS = [
    "id", "title", "metadata", "document_control", "executive_summary",
    "diagrams", "introduction", "business_objectives", "project_scope",
    "stakeholders", "functional_requirements", "adr_topics",
    "quality_expectations", "constraints_and_assumptions",
    "acceptance_criteria", "risk_management", "approval",
    "traceability", "glossary", "appendix"
]

for brd_id, filename in [("BRD-01", "BRD-01.yaml"), ...]:
    path = f"/opt/data/tradegent_covered_calls/01_BRD/{filename}"
    r = subprocess.run(["cat", path], capture_output=True, text=True)
    doc = yaml.safe_load(r.stdout)

    present = set(doc.keys())
    missing = [k for k in CANONICAL_SECTIONS if k not in present]

    if missing:
        print(f"❌ {brd_id} MISSING: {missing}")
    else:
        print(f"✅ {brd_id}: all 20 canonical sections present")

    # Check server header
    server = doc["metadata"]["validation"]["server"]
    needs_fix = (server != "ucx_hermes")

    # Scan for legacy IDs
    for line in r.stdout.splitlines():
        for pat in ["REQ-001", "NFR-001", "SYS-0", "CTR-0", "TSPEC-", "TASK-0"]:
            if pat in line:
                print(f"  LEGACY ID: {pat}")

    # Count FRs and ADR topics
    fr_count = len(doc.get("functional_requirements", {}).get("requirements", []))
    adr_count = len(doc.get("adr_topics", {}).get("topics", []))
    print(f"  FRs: {fr_count}, ADR topics: {adr_count}")
```

## Phase 2: Element ID Assignment

Generate element-ID hashes via the canonical generator, assign to elements
across all sections, rewrite YAML, and post-process to quote comparison operators.

```python
import yaml, hashlib, re, subprocess

from sdd_doc_lint import compute_element_hash  # # Single source: governance/ID_NAMING_STANDARDS.md. Never re-derive the hash here.

def generate_hash(doc_id, section_id, title, description=""):
    """4-char element-ID hash. Delegates — do NOT re-implement the normalization:
    this function previously stripped spaces, used lower() not casefold(), skipped
    NFC and truncated at 200, so it disagreed with the verifier on five of six steps."""
    return compute_element_hash(doc_id, section_id, title, description)[:4]

# Load document
doc = yaml.safe_load(r.stdout)
doc_num = brd_id_str.split("-")[1]

# Sections to process — assign IDs to every element in:
#   business_objectives.goals          → BRD.NN.04.xxxx
#   business_objectives.success_metrics → BRD.NN.04.xxxx
#   functional_requirements.requirements → BRD.NN.07.xxxx
#   functional_requirements.requirements[].acceptance_criteria.items → BRD.NN.07.xxxx
#   adr_topics.topics                  → BRD.NN.08.xxxx
#   constraints_and_assumptions.constraints.items → BRD.NN.10.xxxx
#   constraints_and_assumptions.assumptions.items → BRD.NN.10.xxxx
#   risk_management.risks             → BRD.NN.12.xxxx
#   diagrams.id                       → BRD.NN.diagrams.xxxx

# For each section, iterate items and generate IDs:
for goal in doc["business_objectives"]["goals"]:
    hid = generate_hash(doc_num, "04", goal["statement"], goal.get("target", ""))
    goal["id"] = f"BRD.{doc_num}.04.{hid}"

# ... repeat for all sections ...

# Rewrite with post-processing
new_yaml = yaml.dump(doc, default_flow_style=False, sort_keys=False, allow_unicode=True, width=200)

# Quote values starting with >=, <=, >, <
import io
fixed_lines = []
for line in new_yaml.split('\n'):
    m = re.match(r'^(\s+)(\w[\w\s]*):\s*(>=|<=|>|<)(.*)', line)
    if m:
        indent, key, op, rest = m.groups()
        if not rest.strip().startswith('"') and not rest.strip().startswith("'"):
            line = f'{indent}{key}: "{op}{rest.strip()}"'
    fixed_lines.append(line)

with open(path, 'w') as f:
    f.write('\n'.join(fixed_lines))

# Verify
yaml.safe_load('\n'.join(fixed_lines))
```

## Phase 3: Post-Rewrite Integrity Checks

```python
# Count IDs by section
for line in lines:
    m = re.search(r'BRD\.\d{2}\.\w+\.([a-f0-9]{4})', line)
    ...

# Check for duplicate hashes
all_hashes = [h for lst in ids.values() for h in lst]
dupes = [h for h in all_hashes if all_hashes.count(h) > 1]

# Verify server header
assert doc["metadata"]["validation"]["server"] == "ucx_hermes"
```

## Pitfalls

- **Do NOT use `read_file()` inside execute_code** — returns line-numbered output (`1|content`). Use `subprocess.run(["cat", path])` instead.
- **Programmatic parsing ≠ UCX validation.** `yaml.safe_load()` checks syntax and key presence, but `sdd_validate` (via `mcp_sdd_lifecycle_sdd_validate`) enforces cross-section rules, phase consistency, C4 compliance, and metadata limits. Documents must be tagged **PARSED (pending sdd_validate)** until UCX confirms zero errors.
- **Check for hash collisions** — the 4-char prefix has ~1/65K collision rate; extend BOTH colliding IDs to 8 chars (`--length 8`). Scan for duplicates before writing.
- **`yaml.dump()` width** — set `width=200` to avoid auto-line-wrapping long values (which breaks quoted comparison operators).
- **Keep existing IDs** — if an element already has a real hash (not `xxxx`), do NOT overwrite it. Preserve stability.
- **`cwd` alone does NOT set `PYTHONPATH`** for stdio MCP servers. If the server imports sibling modules, add `env: {PYTHONPATH: "/path/to/src"}` to the Hermes `mcp_servers` config.
