---
title: "ICON Error Recovery Procedures"
tags:
  - framework-guide
  - implementation-contract
  - troubleshooting
  - active
custom_fields:
  artifact_type: Guide
  development_status: active
---

# ICON Error Recovery Procedures

## Purpose

Comprehensive recovery procedures for the 7 most common ICON creation errors, based on analysis of 91% error rate in initial contract creation.

## Error Classification

| Error Type | Frequency | Severity | Recovery Time |
|------------|-----------|----------|---------------|
| Orphaned ICON | 36% (4/11) | High | 30 min |
| Consumer Count Mismatch | 73% (8/11) | Medium | 5 min |
| Self-Reference | 18% (2/11) | Medium | 10 min |
| Missing YAML | 9% (1/11) | Low | 5 min |
| Incomplete Sections | 45% (5/11) | Medium | 20 min |
| Wrong Contract Type | 9% (1/11) | Low | 15 min |
| Missing Performance Reqs | 18% (2/11) | Low | 10 min |

## Recovery Procedures

### §2.1 Orphaned ICON Recovery

**Symptoms**:
- ICON-XXX.md exists in docs/ICON/
- `grep -r "@icon: ICON-XXX" docs/TASKS/` returns 0 results
- README.md does not list ICON-XXX
- development_status may be "active" (incorrectly)

**Root Cause**: ICON created without completing integration phase (steps 6-8 of workflow)

**Impact**:
- Broken bidirectional traceability
- Consumer code cannot discover contract
- Integration debt accumulation

**Recovery Steps**:

1. **Identify Intended Consumers**:
   ```bash
   # Read ICON file to understand purpose
   grep "### Consumers" docs/ICON/ICON-XXX_*.md

   # Should show consumer list like:
   # | TASKS-002 | Heartbeat Monitoring | Health check operations |
   ```

2. **Verify Consumer TASKS Exist**:
   ```bash
   # Check if listed TASKS files exist
   ls docs/TASKS/TASKS-002.md docs/TASKS/TASKS-003.md
   ```

3. **Update Provider TASKS** (if missing section 8.1):
   - Open provider TASKS file
   - Add section 8.1 with @icon tag (see ICON_INTEGRATION_WORKFLOW.md §6)

4. **Update Consumer TASKS** (add section 8.2 to each):
   ```bash
   # For each consumer TASKS-YYY:
   # Add section 8.2 with @icon tag
   # See ICON_INTEGRATION_WORKFLOW.md §7
   ```

5. **Update README.md**:
   - Add row to active contracts table

6. **Validate Integration**:
   ```bash
   ./scripts/validate_icon_integration.sh ICON-XXX
   # Must show: ✓ All checks passed
   ```

7. **Update Development Status** (if needed):
   - If all validations pass, set `development_status: active`
   - If validations fail, set `development_status: draft` until fixed

**Prevention**: Always run pre-flight script before creating ICON

**Estimated Time**: 30 minutes (5 min per consumer TASKS + validation)

### §2.2 Consumer Count Mismatch Recovery

**Symptoms**:
- Frontmatter shows `consumer_count: N`
- `grep -r "@icon: ICON-XXX" docs/TASKS/ | wc -l` shows different number M
- N ≠ M (usually N > M, indicating inflation)

**Root Cause**: Manual counting instead of grep-based validation

**Impact**:
- Inaccurate dependency tracking
- Misleading contract scope
- Consumer discovery failures

**Recovery Steps**:

1. **Calculate Accurate Count**:
   ```bash
   actual_count=$(grep -r "@icon: ICON-XXX" docs/TASKS/ | wc -l)
   echo "Actual consumer count: $actual_count"
   ```

2. **List Actual Consumers**:
   ```bash
   grep -r "@icon: ICON-XXX" docs/TASKS/ | cut -d: -f1 | sort -u
   # Shows list of TASKS files with @icon tags
   ```

3. **Update ICON Frontmatter**:
   ```yaml
   # Change:
   consumer_count: N  # Old incorrect value

   # To:
   consumer_count: M  # Use $actual_count from step 1
   ```

4. **Update Consumer List Table** (if exists in ICON):
   - Section 2: Contract Overview → Consumers table
   - Verify table rows match grep results
   - Remove phantom consumers
   - Add missing consumers

5. **Validate**:
   ```bash
   ./scripts/validate_icon_complete.sh ICON-XXX
   # Should show: ✓ Consumer count matches
   ```

**Prevention**: Use grep command in step 5 of creation workflow

**Estimated Time**: 5 minutes

### §2.3 Self-Reference Anti-Pattern Recovery

**Symptoms**:
- Provider TASKS-XXX has BOTH section 8.1 AND section 8.2
- Section 8.2 includes @icon tag for ICON-XXX (own contract)
- Conceptual error: provider consuming its own interface

**Root Cause**: Misunderstanding of provider/consumer roles

**Impact**:
- Circular dependency confusion
- Consumer count inflation
- Architectural inconsistency

**Recovery Steps**:

1. **Identify Self-Reference**:
   ```bash
   # Check if provider TASKS has section 8.2
   grep -A 5 "### 8.2 Consumed Contracts" docs/TASKS/TASKS-XXX.md
   ```

2. **Remove Section 8.2**:
   - Open provider TASKS-XXX.md
   - Delete entire section 8.2 (including heading and content)
   - Keep section 8.1 (provider role) unchanged

3. **Update Consumer Count**:
   ```bash
   # Re-calculate without self-reference
   new_count=$(grep -r "@icon: ICON-XXX" docs/TASKS/ | grep -v "TASKS-XXX" | wc -l)
   ```

4. **Update ICON Frontmatter**:
   ```yaml
   consumer_count: [new_count]  # Use value from step 3
   ```

5. **Update Consumer List** (in ICON file):
   - Remove TASKS-XXX from consumers table
   - Should only list downstream consumers

6. **Validate**:
   ```bash
   ./scripts/validate_icon_integration.sh ICON-XXX
   # Should show: ✓ No self-reference detected
   ```

**Prevention**: Pre-flight script detects self-references

**Estimated Time**: 10 minutes

### §2.4 Missing YAML Frontmatter Recovery

**Symptoms**:
- ICON file starts with `# ICON-XXX:` (no YAML block at top)
- Post-creation validation script fails with "YAML frontmatter missing"
- Metadata fields not parseable

**Root Cause**: Manual file creation instead of using ICON-TEMPLATE.md

**Impact**:
- Automation scripts cannot parse metadata
- Contract not discoverable by tooling
- Inconsistent documentation structure

**Recovery Steps**:

1. **Copy YAML Template**:
   ```bash
   # Extract frontmatter from template
   head -n 15 docs_flow_framework/ai_dev_flow/ICON/ICON-TEMPLATE.md > /tmp/frontmatter.yaml
   ```

2. **Prepend to ICON File**:
   ```bash
   # Create temporary file with frontmatter + existing content
   cat /tmp/frontmatter.yaml docs/ICON/ICON-XXX_*.md > /tmp/icon_fixed.md
   mv /tmp/icon_fixed.md docs/ICON/ICON-XXX_*.md
   ```

3. **Update Frontmatter Fields**:
   - Open ICON file in editor
   - Update `title` field
   - Update `provider_tasks` field
   - Update `consumer_count` field (use grep)
   - Update `contract_type` field
   - Keep other fields as defaults

4. **Validate YAML Syntax**:
   ```bash
   # Check YAML is valid
   python3 -c "import yaml; yaml.safe_load(open('docs/ICON/ICON-XXX_*.md').read().split('---')[1])"
   # No output = valid YAML
   ```

5. **Validate Complete**:
   ```bash
   ./scripts/validate_icon_complete.sh ICON-XXX
   # Should show: ✓ YAML frontmatter complete
   ```

**Prevention**: Always use `cp ICON-TEMPLATE.md` for new contracts

**Estimated Time**: 5 minutes

### §2.5 Incomplete Sections Recovery

**Symptoms**:
- ICON file has < 10 numbered sections
- Common missing sections: 4 (Performance), 6 (Consumer Requirements), 8 (Testing)
- Post-creation validation shows "Section X missing"

**Root Cause**: Skipped sections during creation, incomplete template usage

**Impact**:
- Incomplete contract specification
- Consumer implementation gaps
- Testing strategy undefined

**Recovery Steps**:

1. **Identify Missing Sections**:
   ```bash
   ./scripts/validate_icon_complete.sh ICON-XXX --show-missing
   # Output: Missing sections: 4, 6, 8
   ```

2. **Open ICON-TEMPLATE.md for Reference**:
   - Find missing section numbers in template
   - Copy section template (heading + content structure)

3. **Add Missing Sections** (for each):

   **Example: Section 4 (Performance Requirements)**
   ```markdown
   ## Performance Requirements

   | Operation | p50 Latency | p95 Latency | p99 Latency |
   |-----------|-------------|-------------|-------------|
   | `method_name()` | < Xms | < Yms | < Zms |

   **Measurement Method**: [Describe benchmarking approach]
   **Target Environment**: [Specify hardware/OS requirements]
   ```

   **Example: Section 6 (Consumer Requirements)**
   ```markdown
   ## Consumer Requirements

   ### Usage Obligations

   **Consumer TASKS MUST**:
   1. Accept ProtocolName protocol type in constructors
   2. Handle all specified exceptions
   3. Check preconditions before operations
   4. Implement callbacks for state changes
   5. Use dependency injection for testing

   ### Mock Implementation Template

   ```python
   class MockProtocolName:
       """Mock ProtocolName for unit tests."""
       # ... (copy from similar ICON like ICON-001)
   ```
   \`\`\`

   **Example: Section 8 (Testing Requirements)**
   ```markdown
   ## Testing Requirements

   ### Provider Tests

   **Required Coverage**:
   - Unit tests: ≥95%
   - Integration tests: ≥85%
   - Protocol conformance tests: 100%

   **Test Categories**:
   1. [Operation category 1]
   2. [Operation category 2]

   ### Consumer Tests

   **Required Coverage**:
   - Mock-based unit tests: ≥95%
   - Integration tests with real provider: ≥85%

   **Test Categories**:
   1. Mock usage patterns
   2. Exception handling for all error types
   ```

4. **Find Similar ICON for Content Examples**:
   ```bash
   # Find ICONs with same contract_type
   grep "contract_type: Protocol Interface" docs/ICON/ICON-*.md
   # Use one as content reference
   ```

5. **Validate Complete**:
   ```bash
   ./scripts/validate_icon_complete.sh ICON-XXX
   # Should show: ✓ All sections present (10/10)
   ```

**Prevention**: Use ICON-TEMPLATE.md checklist during creation

**Estimated Time**: 20 minutes (depends on number of missing sections)

### §2.6 Wrong Contract Type Recovery

**Symptoms**:
- Frontmatter shows `contract_type: Protocol Interface`
- But content defines exception hierarchy (or vice versa)
- Type mismatch between metadata and implementation

**Root Cause**: Incorrect type selection during creation

**Impact**:
- Consumer expectations mismatch
- Wrong template sections used
- Testing strategy misalignment

**Recovery Steps**:

1. **Analyze Contract Content**:
   ```bash
   # Check for protocol definition
   grep "class.*Protocol" docs/ICON/ICON-XXX_*.md

   # Check for exception hierarchy
   grep "class.*Exception" docs/ICON/ICON-XXX_*.md

   # Check for state machine
   grep "class.*State.*Enum" docs/ICON/ICON-XXX_*.md
   ```

2. **Determine Correct Type**:
   | Content Pattern | Correct Type |
   |-----------------|--------------|
   | `class X(Protocol)` | Protocol Interface |
   | `class X(Exception)` | Exception Hierarchy |
   | `class X(Enum)` + transitions | State Machine Contract |
   | `class X(BaseModel)` | Data Model (Pydantic) |
   | `class X(ABC)` | Dependency Injection Interface |

3. **Update Frontmatter**:
   ```yaml
   custom_fields:
     contract_type: [Correct Type]  # Update to match content
   ```

4. **Review Section Requirements**:
   - **Protocol Interface**: Requires section 4 (Performance), 6 (Mock template)
   - **Exception Hierarchy**: Requires retry semantics, error codes
   - **State Machine**: Requires transition rules, validation
   - **Data Model**: Requires field validation, serialization
   - **DI Interface**: Requires ABC methods, injection examples

5. **Add Missing Type-Specific Sections** (if needed):
   - Use ICON-TEMPLATE.md guidance for contract type
   - Reference similar ICON for examples

6. **Validate**:
   ```bash
   ./scripts/validate_icon_complete.sh ICON-XXX
   # Should show: ✓ Contract type requirements met
   ```

**Prevention**: Review contract type table before creation

**Estimated Time**: 15 minutes

### §2.7 Missing Performance Requirements Recovery

**Symptoms**:
- `contract_type: Protocol Interface` or `State Machine Contract`
- No section 4 (Performance Requirements)
- Post-creation validation shows "Performance requirements missing"

**Root Cause**: Skipped optional section that's mandatory for certain types

**Impact**:
- No latency SLAs defined
- Consumer performance expectations unclear
- Benchmarking strategy undefined

**Recovery Steps**:

1. **Verify Type Requires Performance Section**:
   | Contract Type | Requires Performance? |
   |---------------|----------------------|
   | Protocol Interface | Yes (method latencies) |
   | State Machine | Yes (transition times) |
   | Exception Hierarchy | No |
   | Data Model | No |
   | DI Interface | No |

2. **Add Section 4** (if required):
   ```markdown
   ## Performance Requirements

   | Operation | p50 Latency | p95 Latency | p99 Latency |
   |-----------|-------------|-------------|-------------|
   | `connect()` | < 500ms | < 2000ms | < 5000ms |
   | `disconnect()` | < 100ms | < 500ms | < 1000ms |
   | `state` property | < 0.01ms | < 0.1ms | < 1ms |

   **Measurement Method**: pytest-benchmark with 1000 iterations
   **Target Environment**: Python 3.11, Linux x86_64, 4 CPU cores
   **Baseline**: Measured on development machine (adjust for production)
   ```

3. **Reference Similar ICON**:
   - ICON-001: Protocol latencies (connect/disconnect)
   - ICON-005: State machine transitions
   - ICON-006: Monitoring intervals

4. **Define Realistic Targets**:
   - Use existing benchmarks if available
   - Or define targets based on consumer needs
   - Include measurement methodology

5. **Validate**:
   ```bash
   ./scripts/validate_icon_complete.sh ICON-XXX
   # Should show: ✓ Performance requirements documented
   ```

**Prevention**: Check contract type requirements table during creation

**Estimated Time**: 10 minutes

## Batch Recovery

### Fixing Multiple ICONs

**Scenario**: Multiple ICONs created with same error pattern

**Strategy**: Use script-based batch recovery

**Example: Fix All Consumer Count Mismatches**:
```bash
#!/bin/bash
# fix_consumer_counts.sh

for icon_file in docs/ICON/ICON-*.md; do
    icon_id=$(basename "$icon_file" | cut -d_ -f1)

    # Get declared count from frontmatter
    declared=$(grep "consumer_count:" "$icon_file" | awk '{print $2}')

    # Get actual count from grep
    actual=$(grep -r "@icon: $icon_id" docs/TASKS/ | wc -l)

    if [ "$declared" -ne "$actual" ]; then
        echo "Fixing $icon_id: $declared → $actual"

        # Update frontmatter
        sed -i "s/consumer_count: $declared/consumer_count: $actual/" "$icon_file"
    fi
done

echo "Batch fix complete. Run validation:"
echo "./scripts/validate_all_icons.sh"
```

**Example: Fix All Orphaned ICONs**:
```bash
#!/bin/bash
# fix_orphaned_icons.sh

for icon_file in docs/ICON/ICON-*.md; do
    icon_id=$(basename "$icon_file" | cut -d_ -f1)

    # Check if orphaned
    ref_count=$(grep -r "@icon: $icon_id" docs/TASKS/ | wc -l)

    if [ "$ref_count" -eq 0 ]; then
        echo "Orphaned ICON detected: $icon_id"

        # Set to draft status
        sed -i 's/development_status: active/development_status: draft/' "$icon_file"

        echo "Set $icon_id to draft. Manual integration required."
        echo "See ICON_INTEGRATION_WORKFLOW.md steps 6-9"
    fi
done
```

## Prevention Checklist

Before marking ICON as `development_status: active`, verify:

- [ ] Pre-flight validation passed (`preflight_icon_creation.sh`)
- [ ] Post-creation validation passed (`validate_icon_complete.sh`)
- [ ] Integration validation passed (`validate_icon_integration.sh`)
- [ ] All 10 sections present and complete
- [ ] Consumer count matches grep results exactly
- [ ] No self-references detected
- [ ] Provider TASKS has section 8.1
- [ ] All N consumer TASKS have section 8.2
- [ ] README.md updated
- [ ] Atomic commit includes all 8 files

## Support

**For errors not covered here**:
1. Check [ICON_INTEGRATION_WORKFLOW.md](./ICON_INTEGRATION_WORKFLOW.md) for process guidance
2. Check [ICON_CREATION_RULES.md](./ICON_CREATION_RULES.md) for rules reference
3. Review similar ICON files for examples
4. Ask for assistance with specific error details

**Common Support Requests**:
- "How to find consumers?" → See §2.1 step 1
- "Consumer count keeps changing" → Use grep, not manual count (§2.2)
- "Provider consuming own contract?" → Remove section 8.2 (§2.3)
- "Which sections are mandatory?" → See ICON-TEMPLATE.md checklist
