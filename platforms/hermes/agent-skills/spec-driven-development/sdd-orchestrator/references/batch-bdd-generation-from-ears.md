# Batch BDD Generation from EARS — Complete Pattern

## Overview

Generates BDD acceptance scenario documents from EARS formal requirements using Python dict construction + safe YAML serialization. Proven on TradeGent CC (9 BDDs, ~100K chars, all validated 0/0).

## Core Function: build_bdd()

```python
import yaml, subprocess, hashlib, datetime

from sdd_doc_lint import compute_element_hash  # # Single source: governance/ID_NAMING_STANDARDS.md. Never re-derive the hash here.

def h(doc_id, section_id, title, desc=""):
    """4-char content-derived hash — delegates to the canonical implementation."""
    return compute_element_hash(doc_id, section_id, title, desc)[:4]

def build_bdd(doc_num, ears_id, ears_dict, title_suffix, feature_desc, extra_scenarios=None):
    reqs = ears_dict.get("requirements", {})

    event_driven = reqs.get("event_driven", [])
    state_driven = reqs.get("state_driven", [])
    unwanted = reqs.get("unwanted_behavior", [])
    ubiquitous = reqs.get("ubiquitous", [])
    all_reqs = event_driven + state_driven + unwanted + ubiquitous

    ears_refs = [f"@ears: {r['id']}" for r in all_reqs if 'id' in r]
    ears_control = ears_dict.get("document_control", {})
    ears_trace = ears_dict.get("traceability", {})
    prd_refs = ears_trace.get("upstream", {}).get("prd_references", [f"@prd: PRD.{doc_num}.09.xxxx"])
    brd_refs = ears_trace.get("upstream", {}).get("brd_references", [f"@brd: BRD.{doc_num}.07.xxxx"])

    success_scenarios = []
    error_scenarios = []
    recovery_scenarios = []

    # Event-driven → success scenarios (first 3-4)
    for r in event_driven[:3]:
        sid = r["id"]
        sname = r["name"]
        stmt = r.get("statement", "")
        when_part = stmt.split("WHEN ")[1].split(", THE")[0].strip() if "WHEN " in stmt else "the trigger condition is met"
        then_part = stmt.split("THE ")[1].split("WITHIN")[0].strip() if "THE " in stmt else "execute per specification"

        success_scenarios.append({
            "id": f"BDD.{doc_num}.03.{h([doc_num,'03',sname,stmt[:80]])}",
            "name": sname,
            "scenario_type": "success",
            "priority": "P1",
            "tags": ["@scenario-type:success", "@p1-high", f"@scenario-id:BDD.{doc_num}.03.{h([doc_num,'03',sname,stmt[:80]])}"],
            "given": ["the system is active and configured", f"preconditions for {sname} are met"],
            "when": [when_part],
            "then": [then_part, "the result SHALL be logged with all relevant parameters"],
            "ears_trace": f"@ears: {sid}",
            "spec_trace": [f"5 (Behavior — {sname.lower().replace(' ','_')})"]
        })

    # State-driven → success scenarios (first 2)
    for r in state_driven[:2]:
        sid = r["id"]
        sname = r["name"]
        success_scenarios.append({
            "id": f"BDD.{doc_num}.03.{h([doc_num,'03',sname,r.get('statement','')[:80]])}",
            "name": sname,
            "scenario_type": "success",
            "priority": "P1",
            "tags": ["@scenario-type:success", "@p1-high", f"@scenario-id:BDD.{doc_num}.03.{h([doc_num,'03',sname,r.get('statement','')[:80]])}"],
            "given": [f"preconditions for {sname} are active"],
            "when": ["the monitoring cycle executes"],
            "then": [f"the system SHALL {sname.lower()} per specification", "state SHALL be logged"],
            "ears_trace": f"@ears: {sid}",
            "spec_trace": [f"5 (Behavior — {sname.lower().replace(' ','_')})"]
        })

    # Unwanted behavior → error scenarios (first 2)
    for r in unwanted[:2]:
        sid = r["id"]
        sname = r["name"]
        error_scenarios.append({
            "id": f"BDD.{doc_num}.03.{h([doc_num,'03',sname,r.get('statement','')[:80]])}",
            "name": sname,
            "scenario_type": "error",
            "priority": "P1",
            "tags": ["@scenario-type:error", "@p1-high", f"@scenario-id:BDD.{doc_num}.03.{h([doc_num,'03',sname,r.get('statement','')[:80]])}"],
            "given": ["an error condition has occurred"],
            "when": [f"the condition matching {sname} is detected"],
            "then": ["the system SHALL handle the error per specification", "the operator SHALL be notified WITHIN 5 minutes", "the error SHALL be logged with details"],
            "ears_trace": f"@ears: {sid}",
            "spec_trace": [f"5 (Behavior — error_handling)", f"5 (Behavior — {sname.lower().replace(' ','_')})"]
        })

    # Recovery: at least 1 from last unwanted behavior
    if unwanted:
        r = unwanted[-1]
        recovery_scenarios.append({
            "id": f"BDD.{doc_num}.03.{h([doc_num,'03','Recovery',r.get('name','')])}",
            "name": f"Recovery from {r.get('name','Recovery')}",
            "scenario_type": "recovery",
            "priority": "P1",
            "tags": ["@scenario-type:recovery", "@p1-high", f"@scenario-id:BDD.{doc_num}.03.{h([doc_num,'03','Recovery',r.get('name','')])}"],
            "given": [f"a {r.get('name','')} condition has been resolved"],
            "when": ["the system performs recovery sequence"],
            "then": ["normal operation SHALL be restored", "recovery SHALL be logged with resolution details"],
            "ears_trace": f"@ears: {r['id']}",
            "spec_trace": ["5 (Behavior — recovery)", "5 (Behavior — state_transitions)"]
        })

    # Build full document with all required sections
    bdd = {
        "id": f"BDD-{doc_num}",
        "title": f"TradeGent CC — {title_suffix} Acceptance Scenarios",
        "metadata": { ... },  # standard metadata block
        "document_control": { ... },  # version, status, timestamps, revision history
        "feature_definition": { ... },  # feature_name, description, background steps
        "scenario_structure": {
            "scenarios": {
                "success": success_scenarios,
                "error": error_scenarios,
                "recovery": recovery_scenarios,
                "parameterized": [],
                "optional": []
            }
        },
        "traceability": { ... },  # upstream EARS/PRD/BRD refs, downstream ADR/TDD, health_score
        "glossary": { "terms": [...] }
    }
    return bdd
```

## Safe YAML Serialization

```python
def safe_yaml(doc):
    """Dump YAML and quote values starting with comparison operators."""
    raw = yaml.dump(doc, default_flow_style=False, sort_keys=False, allow_unicode=True, width=200)
    lines = raw.split('\n')
    fixed = []
    for line in lines:
        s2 = line.lstrip()
        if s2.startswith(('>=', '<=', '> ', '< ')) and ':' in line:
            parts = line.split(':', 1)
            if len(parts) == 2:
                val = parts[1].strip()
                if val and val[0] not in ("'", '"', "|", ">"):
                    line = f"{parts[0]}: '{val}'"
        fixed.append(line)
    return '\n'.join(fixed)
```

## Session Execution Pattern

```python
# 1. Load all EARS files with subprocess.run(["cat", path]) inside execute_code
#    (NOT read_file — that returns line-numbered output that breaks YAML parsing)

# 2. Generate all BDDs
bdd_files = {}
for num in ["02", "04", "05", "06", "07", "08", "09"]:
    ears_key = f"EARS-{num}"
    ears_dict = ears_data[ears_key]
    title, desc = titles[num]
    bdd = build_bdd(num, ears_key, ears_dict, title, desc)
    bdd_str = safe_yaml(bdd)
    yaml.safe_load(bdd_str)  # verify
    bdd_files[num] = bdd_str
    with open(f"/tmp/BDD-{num}.yaml", "w") as f:
        f.write(bdd_str)

# 3. Copy to project directory
# cp /tmp/BDD-*.yaml /opt/data/.../04_BDD/

# 4. Validate all at directory level
# sdd_validate(doc_type="bdd", document="04_BDD", layer="04_BDD")
```

## Review + Remediation Strategy

### Benchmarks First

Generate and fully review (5 personas) the umbrella (BDD-01) and core engine (BDD-03) before batch-generating the remaining 7. Benchmarks establish the pattern — batch documents inherit the learned structure.

### What to Fix at BDD Layer

- Missing EARS requirement coverage
- State machine transition gaps
- Gherkin syntax/executability issues
- Tag/priority mismatches, dead data columns
- Alert deduplication and idempotency scenarios

### What to Defer to ADR/SPEC

- OAuth token lifecycle, credential storage, regulatory hooks (architecture/interface)
- DST/market holiday, circuit breaker handling (system-level contracts)
- Concurrent failure, clock skew, cascading triggers (integration test definitions)

## Common Pitfalls

1. **read_file inside execute_code**: Returns line-numbered output. Use `subprocess.run(["cat", path])` instead for YAML parsing.
2. **yaml.safe_load() ≠ validation**: Only confirms YAML syntax. Run `sdd_validate` for structural/cross-section/template compliance.
3. **Tag/priority mismatch**: Scenarios tagged `@p0-critical` should have `priority: P0`, not `P1`. Fix in remediation.
4. **Dead data in parameterized scenarios**: Example table columns not referenced by `<placeholder>` in Given/When/Then steps are dead weight — remove them.
5. **Background over-constrains error paths**: Background steps run before every scenario. If Background says "market data is operational," stale-data error scenarios are logically contradictory. Keep Background minimal.
6. **Stuck-roll counter arithmetic**: Map counter values to EARS specification exactly. Counter=1 at first increment, escalate at counter=3. Verify the window-to-counter mapping across documents.
7. **Dividend flagging vs evaluation split**: EARS may define separate requirements for flagging (Tuesday) and ITM evaluation (Wednesday). Trace both requirements separately in the same scenario.
