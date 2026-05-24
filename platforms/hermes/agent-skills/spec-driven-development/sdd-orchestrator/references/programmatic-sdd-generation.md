# Programmatic SDD Document Generation

## When to Use

Generate a BRD, PRD, or other SDD YAML document programmatically via `execute_code` when:

- The document has 500+ lines with many element IDs that need content-based hashing
- You need deterministic hash generation (SHA256 first 4 chars) across many elements
- YAML quoting edge cases (comparison operators, special chars) would cause iterative write/fail cycles
- You're generating multiple documents from a common structure (batch)

## Core Pattern

```python
import hashlib, yaml, subprocess, datetime, re

def hash4(text):
    """Produce 4-char hex hash for element IDs."""
    clean = text.lower()[:100]
    return hashlib.sha256(clean.encode()).hexdigest()[:4]

def eid(section, title, desc=""):
    """Generate TYPE.NN.SS.xxxx element ID. Section can be int or string."""
    if isinstance(section, int):
        sec_str = f"{section:02d}"
    else:
        sec_str = str(section)
    return f"{doc_type}.{doc_id}.{sec_str}.{hash4(f'{doc_id}:{sec_str}:{title}:{desc}')}"
```

## Document Assembly

Build the document as a Python dict following the template structure:

```python
doc = {
    "id": "BRD-10",
    "title": "Document Title",
    "metadata": { ... },      # Schema version, layers, validation, C4 level, ID standard
    "document_control": { ... },  # Version, status, dates, revision_history
    "executive_summary": { ... },
    "diagrams": { ... },       # Required for PRD/BRD — must have items[]
    "introduction": { ... },
    "business_objectives": { ... },  # BRD only
    "project_scope": { ... },        # BRD only
    "stakeholders": { ... },
    "functional_requirements": {
        "priority_definitions": { "P1": "...", "P2": "..." },
        "requirements": [ ... ]       # BRD format
        # OR
        "core_capabilities": [ ... ]  # PRD format
    },
    "adr_topics": { ... },           # BRD only
    "quality_expectations": { ... },
    "constraints_and_assumptions": { ... },
    "acceptance_criteria": { ... },  # Different structure per layer
    "risk_management": { ... },
    "approval": { ... },
    "traceability": {
        "tags": [...],
        "cross_links": { "depends": [...], "discoverability": [...] },
        "upstream": { ... },
        "downstream_expected": [...],
        "health_score": { ... }
    },
    "glossary": { "terms": [...] },
    "appendix": { ... }              # BRD only
}
```

## Writing and Post-Processing

```python
# Dump YAML
yaml_text = yaml.dump(doc, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120)

# Post-process: quote values starting with >=, <=, >, <
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
```

## Verification

Always verify YAML validity immediately after writing:

```python
r = subprocess.run(["python3", "-c", f"import yaml; d=yaml.safe_load(open('{output_path}')); print('YAML valid')"], 
                   capture_output=True, text=True)
if r.returncode != 0:
    print(f"YAML ERROR: {r.stderr}")
```

## Layer-Specific Requirements

### BRD (Layer 1)

- 18 top-level sections (template says 15, UCX validator accepts more)
- Functional requirements use `requirements` list with `priority`, `complexity`, `business_needs`, `business_rules`, `acceptance_criteria`
- Include `adr_topics` with 7+ topics
- Include `appendix` with lifecycle and next_cycle_roadmap

### PRD (Layer 2)

- 15 top-level sections
- `diagrams` section REQUIRED — must have `items[]` with at least 1 diagram entry
- Functional requirements use `core_capabilities` with `brd_reference` hash links
- Include `user_stories` with roles + stories in "As a... I want... so that..." format
- Include `customer_facing_content` with positioning, key_messages, error_messages, success_messages
- Include `diagram_contract` with containers + data_flows
- User journey sequence diagram must include alt/else branches
- ADR topic elaboration in traceability section

## Quality Gate Checklist

Before calling generation complete, verify:

- [ ] YAML parses cleanly
- [ ] `sdd_validate` passes 0/0
- [ ] Element IDs use content hashes (not sequential numbers)
- [ ] BRD refs use hash-level `@brd: TYPE.NN.SS.xxxx` (not document-level `@brd: TYPE-NN`)
- [ ] Diagram contract populated with containers + data_flows (PRD)
- [ ] User journeys include alt/else error paths (PRD)
- [ ] Customer-facing error messages have actionable guidance (PRD)
- [ ] Traceability section has bidirectional cross-links

## Pitfalls

1. **read_file inside execute_code returns line-numbered output** — use `subprocess.run(["cat", path])` for clean YAML parsing
2. **Comparison operators at line start** — quote `>=`, `<=`, `>`, `<` after yaml.dump()
3. **Indentation errors from patch-based edits** — see `references/yaml-patch-indentation-fix.md`
4. **sdd_validate template interference** — template files with `id: ADR-NN` collide with parse stream; move them aside
5. **Filename heuristic bug** — long descriptive names like `BRD-08_performance_review_cadence.yaml` may be misclassified as Markdown; rename to `BRD-NN.yaml`
