---
title: "ICON Integration Workflow"
tags:
  - framework-guide
  - implementation-contract
  - shared-architecture
  - active
custom_fields:
  artifact_type: Guide
  development_status: active
---

# ICON Integration Workflow

## Purpose

Standardized workflow for creating Implementation Contracts (ICON) with mandatory validation gates to prevent the 91% error rate observed in manual creation.

## Overview

ICON creation is an **8-file atomic operation** requiring updates across:
1. ICON-XXX.md (contract definition)
2. Provider TASKS-XXX.md (section 8.1)
3. N × Consumer TASKS-YYY.md (section 8.2)
4. docs/ICON/README.md (active contracts table)

**Critical Rule**: All 8 files must be updated in a single commit. Partial updates create orphaned contracts.

## Pre-Creation Phase

### Step 1: Dependency Analysis (Provider TASKS)

**Location**: Provider TASKS file (e.g., `docs/TASKS/TASKS-XXX.md`)

**Required sections**:
- Section 3.2: Downstream Dependencies (identifies consumers)
- Section 8.1: Provided Contracts (will add @icon tag here)

**Validation**:
```bash
# Check if provider TASKS has dependencies identified
grep -A 10 "### 3.2 Downstream Dependencies" docs/TASKS/TASKS-XXX.md

# Should show list of consuming TASKS
# Example output:
# - TASKS-02: Heartbeat Monitoring (health checks)
# - TASKS-03: Reconnection Service (retry logic)
```

**Decision Gate**: If section 3.2 is empty, STOP. Complete dependency analysis first.

### Step 2: Consumer Identification

**Objective**: Count exact number of consumer TASKS

**Method 1: Manual Analysis**:
- Read provider TASKS section 3.2
- List all TASKS-YYY entries
- Count = N consumers

**Method 2: Automated (after TASKS files have placeholder tags)**:
```bash
# If TASKS files already mention the planned ICON
grep -r "@icon: ICON-XXX" docs/TASKS/ | wc -l
```

**Output**: Consumer count = N (must be > 0)

**Decision Gate**: If N = 0, STOP. ICON not needed (no consumers).

### Step 3: Pre-Flight Validation Script

**Command**:
```bash
./scripts/preflight_icon_creation.sh ICON-XXX TASKS-XXX
```

**Checks performed**:
1. Provider TASKS-XXX.md exists
2. Provider TASKS has section 3.2 with ≥1 dependency
3. Consumer count N calculated
4. No self-reference (TASKS-XXX not in consumer list)
5. No existing ICON-XXX.md in docs/ICON/

**Output (success)**:
```
✓ Provider TASKS found: docs/TASKS/TASKS-XXX.md
✓ Consumer count: N TASKS
✓ No self-reference detected
✓ No duplicate ICON-XXX found
✓ All pre-flight checks passed

Proceed with ICON-XXX creation.
Consumer count for frontmatter: N
```

**Output (failure)**:
```
✗ Provider TASKS missing section 3.2
✗ Self-reference detected: TASKS-XXX in consumer list

Pre-flight FAILED. Fix TASKS files before creating ICON.
See ICON_ERROR_RECOVERY.md for guidance.
```

**Decision Gate**: Exit code must be 0 to proceed.

## Creation Phase

### Step 4: Create ICON File

**Command**:
```bash
cp docs_flow_framework/ai_dev_flow/ICON/ICON-TEMPLATE.md \
   docs/ICON/ICON-XXX_descriptive_name.md
```

**Edit frontmatter**:
```yaml
---
title: "ICON-XXX: [Contract Name]"
tags:
  - implementation-contract
  - layer-11-artifact
  - shared-architecture
  - active  # Set to "draft" initially
custom_fields:
  layer: 11
  artifact_type: ICON
  contract_type: Protocol Interface  # or Exception Hierarchy, State Machine, Data Model, DI Interface
  provider_tasks: TASKS-XXX
  consumer_count: N  # Use value from pre-flight script
  development_status: draft  # Do not set to "active" yet
---
```

**Complete sections 1-10** using template guidance:
1. Document Control (metadata table)
2. Contract Overview (purpose, scope, provider, consumers)
3. Contract Definition (Protocol/Exception/State/Model code)
4. Performance Requirements (if applicable)
5. Provider Requirements (implementation obligations)
6. Consumer Requirements (usage obligations, mock template)
7. Change Management (versioning strategy)
8. Testing Requirements (provider/consumer/protocol tests)
9. Traceability (upstream artifacts, tags)
10. Validation Checklist

### Step 5: Post-Creation Validation Script

**Command**:
```bash
./scripts/validate_icon_complete.sh ICON-XXX
```

**Checks performed**:
1. YAML frontmatter present (9 required fields)
2. All 10 sections present
3. Consumer count in frontmatter matches grep results
4. Performance requirements present (if contract_type = Protocol or State Machine)
5. Mock implementation template present (if contract_type = Protocol)
6. Exception hierarchy complete (if contract_type = Exception Hierarchy)

**Output (success)**:
```
✓ YAML frontmatter complete (9/9 fields)
✓ All sections present (10/10)
✓ Consumer count matches: N (frontmatter) = N (grep)
✓ Performance requirements documented
✓ Mock implementation template provided
✓ All post-creation checks passed

Proceed with TASKS integration.
```

**Decision Gate**: Exit code must be 0 to proceed.

## Integration Phase

### Step 6: Update Provider TASKS (Section 8.1)

**File**: Provider TASKS-XXX.md

**Add/update section 8.1**:
```markdown
## 8. Implementation Contracts

### 8.1 Provided Contracts

This TASKS provides the following implementation contracts for consumer TASKS:

**ICON-XXX: ContractName** (`docs/ICON/ICON-XXX_descriptive_name.md`)
- **Contract Type**: Protocol Interface
- **Consumers**: N TASKS (TASKS-02, TASKS-03, ...)
- **Purpose**: [One sentence describing contract purpose]
- **Key Interfaces**: `InterfaceName` protocol with X methods

@icon: ICON-XXX:ContractName
@icon-role: provider

**Implementation Location**: `src/module/file.py`
```

**Do NOT add section 8.2** (provider does not consume its own contract)

### Step 7: Update Consumer TASKS (Section 8.2)

**Files**: N × Consumer TASKS-YYY.md

**For each consumer**, add/update section 8.2:
```markdown
## 8. Implementation Contracts

### 8.2 Consumed Contracts

This TASKS consumes the following implementation contracts:

**ICON-XXX: ContractName** (`docs/ICON/ICON-XXX_descriptive_name.md`)
- **Provider**: TASKS-XXX
- **Contract Type**: Protocol Interface
- **Usage**: [One sentence describing how this TASKS uses the contract]
- **Integration Point**: Constructor dependency injection

@icon: ICON-XXX:ContractName
@icon-role: consumer

**Usage Example**:
```python
def __init__(self, connector: ServiceConnector):
    self.connector = connector
```
\`\`\`
```

**Repeat for all N consumers**

### Step 8: Update README

**File**: `docs/ICON/README.md`

**Add row to "Active Contracts" table**:
```markdown
| ICON-XXX | ContractName | Protocol Interface | TASKS-XXX | N | Active |
```

## Validation Phase

### Step 9: Integration Validation Script

**Command**:
```bash
./scripts/validate_icon_integration.sh ICON-XXX
```

**Checks performed**:
1. Provider TASKS has @icon tag in section 8.1
2. N consumer TASKS have @icon tags in section 8.2
3. README.md active contracts table includes ICON-XXX
4. Bidirectional traceability: ICON → TASKS → ICON

**Output (success)**:
```
✓ Provider TASKS-XXX has @icon tag (section 8.1)
✓ Consumer TASKS-02 has @icon tag (section 8.2)
✓ Consumer TASKS-03 has @icon tag (section 8.2)
✓ ... (N consumers verified)
✓ README.md includes ICON-XXX in active contracts
✓ Bidirectional traceability complete

Integration validation PASSED.
Proceed with activation.
```

**Decision Gate**: Exit code must be 0 to activate.

### Step 10: Activate Contract

**Edit ICON-XXX.md frontmatter**:
```yaml
custom_fields:
  development_status: active  # Change from "draft" to "active"
```

**Commit all 8 files atomically**:
```bash
git add docs/ICON/ICON-XXX_descriptive_name.md
git add docs/TASKS/TASKS-XXX.md  # Provider
git add docs/TASKS/TASKS-02.md  # Consumer 1
git add docs/TASKS/TASKS-03.md  # Consumer 2
# ... (add all N consumers)
git add docs/ICON/README.md

git commit -m "Add ICON-XXX: ContractName with N consumers

- Created ICON-XXX contract definition
- Updated provider TASKS-XXX section 8.1
- Updated N consumer TASKS sections 8.2
- Updated README.md active contracts table
- All validation scripts passed"
```

## Error Recovery

### Scenario 1: Pre-Flight Script Fails

**Error**: Provider TASKS missing section 3.2

**Fix**:
1. Open provider TASKS-XXX.md
2. Add section 3.2 with downstream dependencies list
3. Re-run pre-flight script

**Error**: Self-reference detected (TASKS-XXX in consumer list)

**Fix**:
1. Remove TASKS-XXX from section 3.2 dependencies
2. Provider never consumes its own contract
3. Re-run pre-flight script

### Scenario 2: Post-Creation Script Fails

**Error**: Consumer count mismatch (frontmatter ≠ grep)

**Fix**:
```bash
# Re-calculate correct count
actual_count=$(grep -r "@icon: ICON-XXX" docs/TASKS/ | wc -l)

# Update frontmatter
# Change: consumer_count: [old_value]
# To:     consumer_count: $actual_count
```

**Error**: Missing section X

**Fix**:
1. Open ICON-TEMPLATE.md
2. Copy section X template
3. Paste into ICON-XXX.md at correct location
4. Fill in content using similar ICON as reference

### Scenario 3: Integration Script Fails

**Error**: Consumer TASKS-YYY missing @icon tag

**Fix**:
1. Open TASKS-YYY.md
2. Add section 8.2 (if missing)
3. Add @icon tag: `@icon: ICON-XXX:ContractName`
4. Add @icon-role tag: `@icon-role: consumer`
5. Re-run integration script

**Error**: README.md not updated

**Fix**:
1. Open docs/ICON/README.md
2. Find "Active Contracts" table
3. Add row: `| ICON-XXX | ContractName | ... |`
4. Re-run integration script

### Scenario 4: Orphaned ICON (0 consumers)

**Symptoms**:
- ICON file exists in docs/ICON/
- grep shows 0 @icon tags in TASKS files
- README.md missing ICON-XXX entry

**Fix** (Complete integration):
1. Identify correct consumer TASKS from contract purpose
2. Run integration phase (steps 6-9)
3. Or delete ICON if truly not needed

**Prevention**: Always run pre-flight script first

### Scenario 5: Consumer Count Inflation

**Symptoms**:
- Frontmatter shows consumer_count: 20
- grep shows 3 actual references

**Fix**:
```bash
# Get accurate count
grep -r "@icon: ICON-XXX" docs/TASKS/ | wc -l
# Output: 3

# Update ICON-XXX.md frontmatter
# Change: consumer_count: 20
# To:     consumer_count: 3
```

**Prevention**: Use grep, not manual counting

### Scenario 6: Self-Reference Anti-Pattern

**Symptoms**:
- Provider TASKS-XXX has both section 8.1 AND 8.2
- Section 8.2 references ICON-XXX (own contract)

**Fix**:
1. Open TASKS-XXX.md
2. Remove section 8.2 entirely
3. Keep only section 8.1 (provider role)

**Prevention**: Pre-flight script detects this

### Scenario 7: Missing YAML Frontmatter

**Symptoms**:
- ICON file starts with `# ICON-XXX:` (no frontmatter)
- Post-creation script fails

**Fix**:
1. Open ICON-TEMPLATE.md
2. Copy lines 1-15 (YAML frontmatter)
3. Paste at top of ICON-XXX.md
4. Update fields (title, provider_tasks, consumer_count)

**Prevention**: Always use `cp ICON-TEMPLATE.md` to create new ICON

## Success Metrics

**ICON Health Dashboard**:
```bash
# Run all validation scripts on all ICONs
./scripts/validate_all_icons.sh

# Output:
# ICON-01: ✓ PASS (8 consumers, complete integration)
# ICON-03: ✓ PASS (8 consumers, complete integration)
# ICON-005: ✗ FAIL (consumer count mismatch: 6 declared, 2 actual)
# ICON-007: ✗ FAIL (orphaned: 0 TASKS references)
# ...
# Summary: 6/11 PASS (55% health rate)
```

**Target Metrics**:
- ICON health rate: ≥95% (≤5% with validation failures)
- Consumer count accuracy: 100% (grep = frontmatter)
- Orphaned ICON rate: 0% (all have ≥1 consumer)
- Self-reference rate: 0% (providers don't consume own contracts)

## References

- [ICON_CREATION_RULES.md](./ICON_CREATION_RULES.md) - Detailed creation rules
- [ICON-TEMPLATE.md](./ICON-TEMPLATE.md) - Contract template with all sections
- [ICON_ERROR_RECOVERY.md](./ICON_ERROR_RECOVERY.md) - Error recovery procedures
- [IMPLEMENTATION_CONTRACTS_GUIDE.md](../TASKS/IMPLEMENTATION_CONTRACTS_GUIDE.md) - Strategic guidance
