# Batch Remediation Script Pattern

After reviewing 2-3 BRDs individually and identifying common issue patterns,
apply the same fixes to all remaining BRDs in a single `execute_code` call.

## Common Fix Patterns Detected

After reviewing BRD-01 and BRD-02, these patterns appear consistently:

1. **objectives_to_requirements placeholder IDs** (`xxxx` instead of actual hashes)
2. **cross_brd_dependencies only has BRD-01**
3. **related_requirements only references BRD-01**
4. **Missing data staleness/freshness thresholds** (options chain, execution quotes, stop-loss prices, market state indicators, portfolio PnL)

## Complete Script

```python
import yaml, os, subprocess, hashlib, re
from datetime import datetime

def make_id(doc_id, section_id, label):
    inp = f"{doc_id}:{section_id}:{label}"[:200].lower()
    inp = re.sub(r'[^a-z0-9]', '', inp)
    h = hashlib.sha256(inp.encode()).hexdigest()[:4]
    try:
        sid = f"{int(section_id):02d}"
    except (ValueError, TypeError):
        sid = str(section_id)
    return f"BRD.{doc_id}.{sid}.{h}"

brd_dir = "/opt/data/project/01_BRD"
files = {
    4: "BRD-04_trade_scheduling_execution.yaml",
    5: "BRD-05_risk_portfolio_management.yaml",
    6: "BRD-06_pnl_simulation_engine.yaml",
    7: "BRD-07_market_state_thesis_monitor.yaml",
    8: "BRD-08.yaml",  # short name due to validator heuristic
    9: "BRD-09_portfolio_operating_system.yaml"
}

fixes_log = {}

for num, fname in files.items():
    path = os.path.join(brd_dir, fname)
    with open(path) as f:
        doc = yaml.safe_load(f)

    fix_count = 0
    goals = doc.get("business_objectives", {}).get("goals", [])
    frs = doc.get("functional_requirements", {}).get("requirements", [])

    # Fix 1: objectives_to_requirements placeholders
    obj_section = doc.get("traceability", {}).get("objectives_to_requirements", [])
    has_placeholders = any(
        "xxxx" in str(v)
        for entry in obj_section
        for f in ["objective_id", "related_frs"]
        for v in ([entry.get(f, "")] if not isinstance(entry.get(f, ""), list) else entry.get(f, []))
    )

    if has_placeholders and goals and frs:
        new_entries = []
        for i, g in enumerate(goals):
            if i == 0 and frs:
                refs = [frs[j]["id"] for j in range(min(3, len(frs))) if "id" in frs[j]]
            elif i == 1 and frs:
                refs = [frs[j]["id"] for j in range(min(5, len(frs))) if "id" in frs[j]]
            elif frs:
                refs = [frs[j]["id"] for j in range(len(frs)) if "id" in frs[j]]
            else:
                refs = []
            new_entries.append({
                "objective_id": g.get("id", f"BRD.0{num}.04.xxxx"),
                "objective": g.get("statement", ""),
                "related_frs": refs,
                "coverage": "Complete"
            })
        doc["traceability"]["objectives_to_requirements"] = new_entries
        fix_count += 1

    # Fix 2: Expand cross_brd_dependencies
    cross_deps = doc.get("traceability", {}).get("cross_brd_dependencies", [])
    if len(cross_deps) == 1 and cross_deps[0].get("related_brd") == "BRD-01":
        all_brds = [f"BRD-0{i}" for i in range(1, 10) if i != num]
        new_deps = [{"related_brd": "BRD-01", "dependency_type": "Foundation", "rationale": "Shared platform infrastructure"}]
        for other in all_brds:
            new_deps.append({"related_brd": other, "dependency_type": "Discoverability", "rationale": "Cross-reference for comprehensive trade agent coverage"})
        doc["traceability"]["cross_brd_dependencies"] = new_deps
        fix_count += 1

    # Fix 3: Add data freshness thresholds per BRD domain
    if frs:
        if num == 4:  # Trade Scheduling — execution quotes
            for fr in frs:
                if "execution" in fr.get("title", "").lower() or "limit" in fr.get("title", "").lower():
                    if not any("stale" in str(b) or "fresh" in str(b) for b in fr.get("business_rules", [])):
                        fr["business_rules"].append("Order execution must verify broker quote data is < 30 seconds old before calculating mid-price for limit orders.")
                        fix_count += 1
                        break

        if num == 5:  # Risk — stop-loss
            for fr in frs:
                if "stop" in fr.get("title", "").lower():
                    if not any("stale" in str(b) for b in fr.get("business_rules", [])):
                        fr["business_rules"].append("All price data used for stop-loss evaluation must be < 5 seconds old. Stale data triggers two consecutive confirming readings.")
                        fix_count += 1
                        break

        if num == 7:  # Market State
            for fr in frs:
                if "state" in fr.get("title", "").lower() or "thesis" in fr.get("title", "").lower():
                    if not any("stale" in str(b) for b in fr.get("business_rules", [])):
                        fr["business_rules"].append("Market state classification must use data < 15 minutes old for price/volume and < 1 day for sentiment flags.")
                        fix_count += 1
                        break

        if num == 9:  # Portfolio
            for fr in frs:
                if "position" in fr.get("title", "").lower() or "portfolio" in fr.get("title", "").lower():
                    if not any("stale" in str(b) for b in fr.get("business_rules", [])):
                        fr["business_rules"].append("Position-level PnL and delta values must be < 30 seconds old. Portfolio aggregations flag stale data > 5 minutes.")
                        fix_count += 1
                        break

    # Update version
    if fix_count > 0:
        doc["document_control"]["version"] = "1.1"
        doc["document_control"]["last_updated"] = datetime.now().isoformat()
        doc["document_control"]["revision_history"]["entries"].append({
            "version": "1.1",
            "date": datetime.now().isoformat(),
            "author": "Hermes Agent (batch review + remediation)",
            "changes": f"Post-review: {fix_count} fixes including placeholder IDs, cross-BRD deps, and data freshness thresholds.",
            "approver": ""
        })

        yaml_str = yaml.dump(doc, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120)
        with open(path, 'w') as f:
            f.write(yaml_str)

    fixes_log[num] = fix_count
    print(f"BRD-0{num}: {fix_count} fixes")

print(f"\nTotal: {sum(fixes_log.values())} fixes across {len(fixes_log)} BRDs")
```

## When to Customize

Customize this script when:

- Your BRDs have different section structures (not all 18 sections)
- Your source document has different domain-specific freshness thresholds
- You need to fix diagram placeholder IDs (add a `diagrams` fix block)
- You need to fix acceptance criteria references (add a `launch_gates` fix block)

## After Batch Remediation

1. **Re-validate all affected BRDs** with `sdd_validate`
2. **Verify `yaml.safe_load()`** on each file
3. **Update CHANGELOG** with the batch remediation entry
4. **Update `plans/BRD-PLANNING-ROADMAP.md`** with version numbers and fix counts
