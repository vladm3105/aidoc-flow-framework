# UCX v1.18.0 - Layer Action Handoff System

## Problem Statement

BRD reviews flag technical/product details as P0/P1 errors, incorrectly penalizing BRD scores. These items belong in downstream layers.

**Solution**: Capture out-of-scope items as **ACTIONS** (0 score impact) that handoff to appropriate downstream layers.

---

## Scope

### Target Layers (Immediate Downstream from BRD)

| Layer | Document | Handoff Purpose |
|-------|----------|-----------------|
| **L2 PRD** | Product Requirements | Feature details, user stories, acceptance criteria |
| **L3 EARS** | Formal Requirements | Structured requirement syntax |
| **L4 BDD** | Test Scenarios | Behavior specifications, Gherkin scenarios |
| **L5 ADR** | Architecture Decisions | Technical decisions, trade-offs |
| **L8 CTR** | Data Contracts | API schemas, interface definitions |

**NOT in BRD→Handoff scope**: SPEC (L9) is too far downstream. SPEC receives handoffs from ADR/CTR, not directly from BRD.

### Action Types

| Type | v1.18.0 | Purpose |
|------|---------|---------|
| `HANDOFF` | ✅ Implemented | Transfer requirement to downstream layer |
| `INFORM` | 🔜 Reserved | Context sharing, no action required |
| `REVIEW` | 🔜 Reserved | Needs human review before processing |
| `DEFER` | 🔜 Reserved | Out of current scope, future consideration |

Scripts are designed to accept all types; only HANDOFF is used in v1.18.0.

### Personas

**All review personas** can create actions when they identify out-of-scope items:
- Architect, Auditor, Tech Lead, Strategist, Chaos Engineer, Operator
- Integration Lead, Product Owner, Business Analyst, QA Lead, Fact Checker

Each persona creates actions for items outside BRD scope that their expertise identifies.

### Scripts
- `extract_actions.py` - Extract and filter actions (supports all types)
- `validate_actions.py` - Validate action format (supports all types)

---

## Action Format

```
<!-- UCX-ACTION-START -->
ACTION_ID: ACT-{8-char-hex}
TYPE: HANDOFF
TARGET: {PRD|EARS|BDD|ADR|CTR}
PRIORITY: {P0|P1|P2}
SOURCE: {BRD_ID} Section {X.X}
PERSONA: {PERSONA_NAME}
CONTEXT: {Business context from BRD that triggers this need}
REQUIREMENT: {What downstream doc should specify}
<!-- UCX-ACTION-END -->
```

### Field Definitions

| Field | Required | Description |
|-------|----------|-------------|
| `ACTION_ID` | Yes | Unique handle: `ACT-7f3a2b1c` (8-char hex, LLM-generated) |
| `TYPE` | Yes | Action type: HANDOFF (v1.18.0), future: INFORM, REVIEW, DEFER |
| `TARGET` | Yes | Downstream doc: PRD, EARS, BDD, ADR, CTR |
| `PRIORITY` | Yes | Suggested priority for target layer |
| `SOURCE` | Yes | BRD ID and section reference |
| `PERSONA` | Yes | Persona that generated this action |
| `CONTEXT` | Yes | Business requirement from BRD |
| `REQUIREMENT` | Yes | What to specify in downstream doc |

**Note**: ACTION_ID is just a tracking handle for LLM-to-LLM handoff. The real content is in TARGET, CONTEXT, and REQUIREMENT fields.

### Examples

**Product Feature → PRD**
```
<!-- UCX-ACTION-START -->
ACTION_ID: ACT-3f7a2c1b
TYPE: HANDOFF
TARGET: PRD
PRIORITY: P1
SOURCE: BRD-01 Section 4.2
PERSONA: PRODUCT_OWNER
CONTEXT: BRD states "senders need transaction status visibility"
REQUIREMENT: Define user stories for transaction tracking feature with acceptance criteria
<!-- UCX-ACTION-END -->
```

**Architecture Decision → ADR**
```
<!-- UCX-ACTION-START -->
ACTION_ID: ACT-8d4e6f2a
TYPE: HANDOFF
TARGET: ADR
PRIORITY: P0
SOURCE: BRD-01 Section 10.2
PERSONA: ARCHITECT
CONTEXT: BRD states "platform must survive Asterium outage"
REQUIREMENT: Document failover architecture decision (active-passive vs active-active)
<!-- UCX-ACTION-END -->
```

**Test Scenario → BDD**
```
<!-- UCX-ACTION-START -->
ACTION_ID: ACT-1b9c5e3d
TYPE: HANDOFF
TARGET: BDD
PRIORITY: P1
SOURCE: BRD-01 Section 6.3
PERSONA: QA_LEAD
CONTEXT: BRD states "KYC Level 1 users limited to $300/day"
REQUIREMENT: Define Gherkin scenarios for KYC limit enforcement
<!-- UCX-ACTION-END -->
```

**API Contract → CTR**
```
<!-- UCX-ACTION-START -->
ACTION_ID: ACT-5a2f8c4e
TYPE: HANDOFF
TARGET: CTR
PRIORITY: P1
SOURCE: BRD-01 Section 6.5
PERSONA: INTEGRATION_LEAD
CONTEXT: BRD states "must integrate with Paynet for UZS disbursement"
REQUIREMENT: Define Paynet API contract with request/response schemas
<!-- UCX-ACTION-END -->
```

**Formal Requirement → EARS**
```
<!-- UCX-ACTION-START -->
ACTION_ID: ACT-9e1d7b6c
TYPE: HANDOFF
TARGET: EARS
PRIORITY: P1
SOURCE: BRD-01 Section 6.1
PERSONA: BUSINESS_ANALYST
CONTEXT: BRD states "transaction must complete within 30 seconds"
REQUIREMENT: Formalize as EARS requirement with preconditions and success criteria
<!-- UCX-ACTION-END -->
```

---

## Implementation Plan

### Phase 1: Update Review Prompt

**File**: `docs/UCX/review/UCR_PROMPT_BRD_PROJECT.md`

#### 1.1 Add Action System Section (after Layer Scope Enforcement)

```markdown
## ACTION Handoff System (v1.18.0)

When a finding is OUT OF BRD SCOPE but valuable for downstream documents:

1. **DO NOT flag as P0/P1/P2** (no BRD score penalty)
2. **CREATE an ACTION** to handoff to appropriate layer

### Target Layers

| Target | Layer | Handoff When BRD Mentions |
|--------|-------|---------------------------|
| PRD | L2 | Feature details, user stories, UI requirements |
| EARS | L3 | Requirements needing formal structure |
| BDD | L4 | Testable behaviors, acceptance scenarios |
| ADR | L5 | Architecture decisions, technical trade-offs |
| CTR | L8 | API contracts, interface definitions |

**NOT BRD→Handoff**: SPEC (L9) receives from ADR/CTR, not BRD.

### Action Format

\`\`\`
<!-- UCX-ACTION-START -->
ACTION_ID: ACT-{8-char-hex}
TYPE: HANDOFF
TARGET: {PRD|EARS|BDD|ADR|CTR}
PRIORITY: {P0|P1|P2}
SOURCE: {BRD_ID} Section {X.X}
PERSONA: {YOUR_PERSONA_NAME}
CONTEXT: {Business context from BRD}
REQUIREMENT: {What downstream doc should specify}
<!-- UCX-ACTION-END -->
\`\`\`

Generate a unique 8-character hex string for ACTION_ID (e.g., `ACT-7f3a2b1c`).

### When to Create Actions

Any persona can create an action when they identify an item that:
- Is OUT OF BRD SCOPE (belongs in downstream layer)
- Has value for downstream document creators
- Would otherwise be flagged as a finding

### Deduplication

If multiple personas identify same requirement for same target:
- Create ONE action with highest priority
- List personas comma-separated in PERSONA field
```

#### 1.2 Add to Each Persona Section

Add this block to ALL persona sections (Architect, Auditor, Tech Lead, etc.):

```markdown
**OUT OF BRD SCOPE - CREATE ACTION instead of P0/P1/P2**:

When you identify items that belong in downstream layers, create an ACTION:
- Feature/product details → TARGET: PRD
- Formal requirements → TARGET: EARS
- Test scenarios/behaviors → TARGET: BDD
- Architecture decisions → TARGET: ADR
- API contracts/schemas → TARGET: CTR

Do NOT flag these as P0/P1/P2 findings. Create ACTION with TYPE: HANDOFF.
```

#### 1.3 Add Actions Manifest to Chairperson

```markdown
## DOWNSTREAM LAYER ACTIONS

<!-- UCX-ACTIONS-MANIFEST-START -->
### Actions Summary
| Target | Count | Priority Breakdown |
|--------|-------|-------------------|
| PRD | [N] | P0:[N] P1:[N] P2:[N] |
| EARS | [N] | P0:[N] P1:[N] P2:[N] |
| BDD | [N] | P0:[N] P1:[N] P2:[N] |
| ADR | [N] | P0:[N] P1:[N] P2:[N] |
| CTR | [N] | P0:[N] P1:[N] P2:[N] |
| **Total** | [N] | |

### Actions Table
| ACTION_ID | Type | Target | Priority | Source | Requirement |
|-----------|------|--------|----------|--------|-------------|
| ACT-3f7a2c1b | HANDOFF | PRD | P1 | 4.2 | Define transaction tracking user stories |
| ACT-8d4e6f2a | HANDOFF | ADR | P0 | 10.2 | Document failover architecture |
| ACT-5a2f8c4e | HANDOFF | CTR | P1 | 6.5 | Define Paynet API contract |
<!-- UCX-ACTIONS-MANIFEST-END -->

**NOTE**: Actions do NOT affect BRD score. They are handoffs to downstream layers.
```

#### 1.4 Update Score Calculation

```markdown
**PRD-Ready Score Calculation**:

Score = 100 - (P0 × 10) - (P1 × 3) - (P2 × 1)
        ↑ ACTIONS DO NOT AFFECT SCORE

| Finding Type | Count | Points | Impact |
|--------------|-------|--------|--------|
| P0 Critical | [N] | -10 each | -[N] |
| P1 High | [N] | -3 each | -[N] |
| P2 Medium | [N] | -1 each | -[N] |
| **ACTIONS** | [N] | 0 each | **0** |
| **Total** | | | **-[N]** |

**Final Score**: [100 - deduction]
```

---

### Phase 2: Create Scripts

#### 2.1 Action Extraction Script

**File**: `UCX/scripts/extract_actions.py`

```python
#!/usr/bin/env python3
"""
Extract UCX actions from BRD review reports.

Usage:
    python extract_actions.py <report.md> [options]

Options:
    --target PRD|EARS|BDD|ADR|CTR    Filter by target layer
    --type HANDOFF|INFORM|REVIEW|DEFER    Filter by action type
    --priority P0|P1|P2    Filter by priority
    --format json|md|csv|summary    Output format (default: json)
    --output FILE    Write to file instead of stdout

Examples:
    python extract_actions.py BRD-01.UCR_review.md --format summary
    python extract_actions.py BRD-01.UCR_review.md --target ADR --format md
    python extract_actions.py BRD-01.UCR_review.md --type HANDOFF --format json
"""

import re
import json
import argparse
import sys
from pathlib import Path
from dataclasses import dataclass, asdict

@dataclass
class Action:
    action_id: str
    action_type: str
    target: str
    priority: str
    source: str
    persona: str
    context: str
    requirement: str

# Simple pattern: ACT-{8-char-hex}
ACTION_PATTERN = re.compile(
    r'<!-- UCX-ACTION-START -->\s*'
    r'ACTION_ID:\s*(?P<action_id>ACT-[a-f0-9]{6,10})\s*'
    r'TYPE:\s*(?P<action_type>\w+)\s*'
    r'TARGET:\s*(?P<target>\w+)\s*'
    r'PRIORITY:\s*(?P<priority>P[012])\s*'
    r'SOURCE:\s*(?P<source>[^\n]+)\s*'
    r'PERSONA:\s*(?P<persona>[^\n]+)\s*'
    r'CONTEXT:\s*(?P<context>[^\n]+)\s*'
    r'REQUIREMENT:\s*(?P<requirement>[^\n]+)\s*'
    r'<!-- UCX-ACTION-END -->',
    re.MULTILINE
)

# Configurable valid values (easy to extend)
VALID_TYPES = {'HANDOFF', 'INFORM', 'REVIEW', 'DEFER'}
VALID_TARGETS = {'PRD', 'EARS', 'BDD', 'ADR', 'CTR'}
VALID_PRIORITIES = {'P0', 'P1', 'P2'}

def extract_actions(content: str) -> list[Action]:
    """Extract actions from review report."""
    actions = []
    for match in ACTION_PATTERN.finditer(content):
        actions.append(Action(**match.groupdict()))
    return actions

def filter_actions(actions: list[Action],
                   target: str = None,
                   action_type: str = None,
                   priority: str = None) -> list[Action]:
    """Filter actions by criteria."""
    result = actions
    if target:
        result = [a for a in result if a.target.upper() == target.upper()]
    if action_type:
        result = [a for a in result if a.action_type.upper() == action_type.upper()]
    if priority:
        result = [a for a in result if a.priority.upper() == priority.upper()]
    return result

def output_json(actions: list[Action]) -> str:
    return json.dumps([asdict(a) for a in actions], indent=2)

def output_csv(actions: list[Action]) -> str:
    if not actions:
        return "action_id,type,target,priority,source,persona,context,requirement"
    header = "action_id,type,target,priority,source,persona,context,requirement"
    rows = []
    for a in actions:
        # Escape quotes in context and requirement
        ctx = a.context.replace('"', '""')
        req = a.requirement.replace('"', '""')
        row = f'{a.action_id},{a.action_type},{a.target},{a.priority},"{a.source}",{a.persona},"{ctx}","{req}"'
        rows.append(row)
    return header + "\n" + "\n".join(rows)

def output_md(actions: list[Action]) -> str:
    if not actions:
        return "No actions found."
    lines = [
        "| Action ID | Type | Target | Priority | Source | Requirement |",
        "|-----------|------|--------|----------|--------|-------------|"
    ]
    for a in actions:
        req = a.requirement[:50] + "..." if len(a.requirement) > 50 else a.requirement
        lines.append(f"| {a.action_id} | {a.action_type} | {a.target} | {a.priority} | {a.source} | {req} |")
    return "\n".join(lines)

def output_summary(actions: list[Action]) -> str:
    """Output summary statistics."""
    if not actions:
        return "No actions found."

    by_type = {}
    by_target = {}
    by_priority = {}

    for a in actions:
        by_type[a.action_type] = by_type.get(a.action_type, 0) + 1
        by_target[a.target] = by_target.get(a.target, 0) + 1
        by_priority[a.priority] = by_priority.get(a.priority, 0) + 1

    lines = [
        f"Total Actions: {len(actions)}",
        "",
        "By Type:",
        *[f"  {k}: {v}" for k, v in sorted(by_type.items())],
        "",
        "By Target:",
        *[f"  {k}: {v}" for k, v in sorted(by_target.items())],
        "",
        "By Priority:",
        *[f"  {k}: {v}" for k, v in sorted(by_priority.items())],
    ]
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(
        description="Extract UCX actions from BRD review reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python extract_actions.py report.md --format summary
  python extract_actions.py report.md --target ADR --format md
  python extract_actions.py report.md --type HANDOFF -o actions.json
        """
    )
    parser.add_argument("report", help="Path to UCR review report")
    parser.add_argument("--target", choices=list(VALID_TARGETS),
                        help="Filter by target layer")
    parser.add_argument("--type", dest="action_type", choices=list(VALID_TYPES),
                        help="Filter by action type")
    parser.add_argument("--priority", choices=list(VALID_PRIORITIES),
                        help="Filter by priority")
    parser.add_argument("--format", choices=["json", "csv", "md", "summary"],
                        default="json", help="Output format")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    args = parser.parse_args()

    report_path = Path(args.report)
    if not report_path.exists():
        print(f"Error: File not found: {report_path}", file=sys.stderr)
        sys.exit(1)

    content = report_path.read_text()
    actions = extract_actions(content)
    actions = filter_actions(actions, args.target, args.action_type, args.priority)

    formatters = {
        'json': output_json,
        'csv': output_csv,
        'md': output_md,
        'summary': output_summary
    }
    result = formatters[args.format](actions)

    if args.output:
        Path(args.output).write_text(result)
        print(f"Written {len(actions)} actions to {args.output}")
    else:
        print(result)

if __name__ == "__main__":
    main()
```

#### 2.2 Action Validation Script

**File**: `UCX/scripts/validate_actions.py`

```python
#!/usr/bin/env python3
"""
Validate UCX action format in BRD review reports.

Usage:
    python validate_actions.py <report.md> [--strict]

Options:
    --strict    Fail on warnings (unknown types/targets still allowed but warned)

Examples:
    python validate_actions.py BRD-01.UCR_review.md
    python validate_actions.py BRD-01.UCR_review.md --strict
"""

import re
import sys
from pathlib import Path

# Known values (extensible - unknown values generate warnings, not errors)
KNOWN_TYPES = {'HANDOFF', 'INFORM', 'REVIEW', 'DEFER'}
KNOWN_TARGETS = {'PRD', 'EARS', 'BDD', 'ADR', 'CTR'}
KNOWN_PRIORITIES = {'P0', 'P1', 'P2'}

# Required fields
REQUIRED_FIELDS = ['ACTION_ID', 'TYPE', 'TARGET', 'PRIORITY', 'SOURCE', 'PERSONA', 'CONTEXT', 'REQUIREMENT']

def validate_actions(content: str) -> tuple[list, list]:
    """
    Validate actions and return (errors, warnings).
    Errors: Missing fields, malformed format
    Warnings: Unknown types/targets (allows future extension)
    """
    errors = []
    warnings = []

    # Find all action blocks
    pattern = r'<!-- UCX-ACTION-START -->(.*?)<!-- UCX-ACTION-END -->'
    for match in re.finditer(pattern, content, re.DOTALL):
        block = match.group(1)
        line_num = content[:match.start()].count('\n') + 1

        # Extract ACTION_ID for error reporting
        id_match = re.search(r'ACTION_ID:\s*(ACT-[a-f0-9]+)', block)
        action_id = id_match.group(1) if id_match else "UNKNOWN"

        # Check required fields
        for field in REQUIRED_FIELDS:
            if f'{field}:' not in block:
                errors.append((line_num, action_id, f"Missing required field: {field}"))

        # Validate ACTION_ID format (simple: ACT-{hex})
        if id_match:
            if not re.match(r'ACT-[a-f0-9]{6,10}$', action_id):
                errors.append((line_num, action_id,
                    "Invalid ACTION_ID format. Expected: ACT-{6-10 hex chars} (e.g., ACT-7f3a2b1c)"))

        # Check TYPE (warn if unknown, don't error - allows future types)
        type_match = re.search(r'TYPE:\s*(\w+)', block)
        if type_match:
            action_type = type_match.group(1).upper()
            if action_type not in KNOWN_TYPES:
                warnings.append((line_num, action_id,
                    f"Unknown TYPE: {action_type}. Known types: {KNOWN_TYPES}"))

        # Check TARGET (warn if unknown - allows future targets)
        target_match = re.search(r'TARGET:\s*(\w+)', block)
        if target_match:
            target = target_match.group(1).upper()
            if target not in KNOWN_TARGETS:
                warnings.append((line_num, action_id,
                    f"Unknown TARGET: {target}. Known targets: {KNOWN_TARGETS}"))

        # Validate PRIORITY (error if invalid - strict set)
        priority_match = re.search(r'PRIORITY:\s*(P[012])', block)
        if not priority_match and 'PRIORITY:' in block:
            errors.append((line_num, action_id,
                f"Invalid PRIORITY format. Must be: {KNOWN_PRIORITIES}"))

    # Check for unmatched markers
    start_count = content.count('<!-- UCX-ACTION-START -->')
    end_count = content.count('<!-- UCX-ACTION-END -->')
    if start_count != end_count:
        errors.append((0, "GLOBAL",
            f"Unmatched markers: {start_count} starts, {end_count} ends"))

    return errors, warnings

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Validate UCX action format")
    parser.add_argument("report", help="Path to UCR review report")
    parser.add_argument("--strict", action="store_true",
                        help="Treat warnings as errors")
    args = parser.parse_args()

    report_path = Path(args.report)
    if not report_path.exists():
        print(f"Error: File not found: {report_path}")
        sys.exit(1)

    content = report_path.read_text()
    errors, warnings = validate_actions(content)

    # Count actions
    action_count = content.count('<!-- UCX-ACTION-START -->')

    # Print results
    if errors:
        print(f"ERRORS ({len(errors)}):")
        for line_num, action_id, msg in errors:
            print(f"  Line {line_num} [{action_id}]: {msg}")
        print()

    if warnings:
        print(f"WARNINGS ({len(warnings)}):")
        for line_num, action_id, msg in warnings:
            print(f"  Line {line_num} [{action_id}]: {msg}")
        print()

    # Determine exit status
    if errors:
        print(f"VALIDATION FAILED: {len(errors)} errors in {action_count} actions")
        sys.exit(1)
    elif warnings and args.strict:
        print(f"VALIDATION FAILED (strict): {len(warnings)} warnings in {action_count} actions")
        sys.exit(1)
    else:
        status = f" ({len(warnings)} warnings)" if warnings else ""
        print(f"✓ VALIDATION PASSED: {action_count} actions{status}")
        sys.exit(0)

if __name__ == "__main__":
    main()
```

---

### Phase 3: Version Bump

**File**: `UCX/ucx/version.py`
```python
__version__ = "1.18.0"
```

---

### Phase 4: Documentation Updates

#### 4.1 Changelog

**File**: `UCX/docs/CHANGELOG.md`

Add entry for v1.18.0:

```markdown
## [1.18.0] - 2026-03-XX

### Added
- **Layer Action Handoff System**: Capture out-of-scope items as ACTIONS that handoff to downstream layers (PRD, EARS, BDD, ADR, CTR) without penalizing BRD score
- New scripts: `extract_actions.py` and `validate_actions.py` for action processing
- ACTION format with fields: ACTION_ID, TYPE, TARGET, PRIORITY, SOURCE, PERSONA, CONTEXT, REQUIREMENT
- Actions Manifest section in Chairperson output
- Support for future action types (INFORM, REVIEW, DEFER) - currently only HANDOFF implemented

### Changed
- Updated all review personas to create ACTIONS for out-of-scope items instead of P0/P1/P2 findings
- Score calculation explicitly excludes ACTIONS (0 score impact)

### Fixed
- BRD scores no longer penalized for technical/product details that belong in downstream layers
```

#### 4.2 README Update

**File**: `UCX/README.md`

Add section under Features:

```markdown
### Layer Action Handoff (v1.18.0)

UCX review automatically identifies items that belong in downstream layers and creates structured ACTIONS for handoff:

| Target | Layer | Purpose |
|--------|-------|---------|
| PRD | L2 | Feature details, user stories |
| EARS | L3 | Formal requirement syntax |
| BDD | L4 | Test scenarios |
| ADR | L5 | Architecture decisions |
| CTR | L8 | API contracts |

Actions do NOT affect BRD score - they are handoffs, not findings.

**Extract actions:**
\`\`\`bash
python scripts/extract_actions.py report.md --target ADR --format md
\`\`\`

**Validate actions:**
\`\`\`bash
python scripts/validate_actions.py report.md
\`\`\`
```

#### 4.3 Roadmap Update

**File**: `UCX/docs/ROADMAP.md`

Update roadmap:

```markdown
## Completed

### v1.18.0 - Layer Action Handoff
- [x] ACTION format for downstream layer handoffs
- [x] HANDOFF action type
- [x] extract_actions.py script
- [x] validate_actions.py script
- [x] All personas can create actions
- [x] Actions excluded from BRD score

## Planned

### v1.19.0 - Action Types Expansion (if needed)
- [ ] INFORM action type - context sharing
- [ ] REVIEW action type - human review required
- [ ] DEFER action type - future scope
- [ ] Action lifecycle tracking (STATUS field)
- [ ] Bidirectional traceability (@action tags)

### v1.20.0 - Downstream Integration (if needed)
- [ ] PRD autopilot reads BRD actions
- [ ] ADR autopilot reads BRD actions
- [ ] Action resolution tracking
```

#### 4.4 User Guide Update

**File**: `UCX/docs/USER_GUIDE.md`

Add section:

```markdown
## Working with Actions

### What are Actions?

Actions are structured handoffs from BRD review to downstream layers. When a reviewer identifies something outside BRD scope (e.g., technical implementation detail), they create an ACTION instead of a P0/P1/P2 finding.

**Key points:**
- Actions do NOT affect BRD score
- Actions target specific downstream documents (PRD, EARS, BDD, ADR, CTR)
- Actions have suggested priority for the target layer

### Action Format

\`\`\`
<!-- UCX-ACTION-START -->
ACTION_ID: ACT-7f3a2b1c
TYPE: HANDOFF
TARGET: ADR
PRIORITY: P0
SOURCE: BRD-01 Section 10.2
PERSONA: ARCHITECT
CONTEXT: BRD states "platform must survive partner outage"
REQUIREMENT: Document failover architecture decision
<!-- UCX-ACTION-END -->
\`\`\`

### Extracting Actions

\`\`\`bash
# Get summary of all actions
python scripts/extract_actions.py report.md --format summary

# Extract ADR-targeted actions as markdown
python scripts/extract_actions.py report.md --target ADR --format md

# Extract as JSON for processing
python scripts/extract_actions.py report.md --target PRD --format json -o prd_actions.json
\`\`\`

### Validating Actions

\`\`\`bash
# Basic validation
python scripts/validate_actions.py report.md

# Strict mode (warnings = errors)
python scripts/validate_actions.py report.md --strict
\`\`\`
```

---

## Files to Modify

| File | Changes | Priority |
|------|---------|----------|
| `docs/UCX/review/UCR_PROMPT_BRD_PROJECT.md` | Add action system, update all personas, update scoring | P0 |
| `UCX/scripts/extract_actions.py` | New script (~130 lines) | P0 |
| `UCX/scripts/validate_actions.py` | New script (~100 lines) | P0 |
| `UCX/ucx/version.py` | Version bump | P0 |
| `UCX/docs/CHANGELOG.md` | Add v1.18.0 entry | P1 |
| `UCX/README.md` | Add Layer Action Handoff section | P1 |
| `UCX/docs/ROADMAP.md` | Update completed/planned sections | P1 |
| `UCX/docs/USER_GUIDE.md` | Add Working with Actions section | P1 |

**Total: 8 files**

---

## Implementation Order

| Step | Phase | Task | Effort |
|------|-------|------|--------|
| 1 | 1 | Add Action System section to prompt | 20 min |
| 2 | 1 | Add action instruction block to all persona sections | 30 min |
| 3 | 1 | Add Actions Manifest to Chairperson | 15 min |
| 4 | 1 | Update score calculation | 10 min |
| 5 | 2 | Create extract_actions.py | 30 min |
| 6 | 2 | Create validate_actions.py | 25 min |
| 7 | 3 | Version bump | 5 min |
| 8 | 4 | Update CHANGELOG.md | 10 min |
| 9 | 4 | Update README.md | 10 min |
| 10 | 4 | Update ROADMAP.md | 10 min |
| 11 | 4 | Update USER_GUIDE.md | 15 min |
| 12 | - | Test with BRD-01 review | 20 min |

**Total: ~3.5 hours**

---

## Verification

```bash
# 1. Run review with updated prompt
source .envrc && ucx review brd docs/01_BRD/BRD-01/

# 2. Validate action format
python UCX/scripts/validate_actions.py BRD-01.UCR_review_report.md
# Expected: "✓ VALIDATION PASSED: N actions"

# 3. Get summary
python UCX/scripts/extract_actions.py BRD-01.UCR_review_report.md --format summary

# 4. Extract by target
python UCX/scripts/extract_actions.py BRD-01.UCR_review_report.md --target ADR --format md

# 5. Extract by type (ready for future types)
python UCX/scripts/extract_actions.py BRD-01.UCR_review_report.md --type HANDOFF --format json

# 6. Verify BRD score improved (out-of-scope items no longer penalize)
```

---

## Extension Points (Future-Ready)

### Adding New Action Types

1. Add to `KNOWN_TYPES` in both scripts
2. Document in prompt
3. No structural changes needed

### Adding New Target Layers

1. Add to `KNOWN_TARGETS` in both scripts
2. Add to prompt's target table
3. No structural changes needed

### Scripts Accept Unknown Values

- Unknown TYPE: Warning (not error) → allows gradual rollout
- Unknown TARGET: Warning (not error) → allows new layers
- `--strict` flag to enforce known values only

---

## Layer Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  BRD (L1) - Business Requirements                               │
│  ├── FINDINGS: P0/P1/P2 (affect score)                         │
│  └── ACTIONS: TYPE=HANDOFF (0 score impact)                    │
│              │                                                  │
│              ├──→ PRD (L2): Feature details, user stories      │
│              ├──→ EARS (L3): Formal requirement syntax         │
│              ├──→ BDD (L4): Test scenarios, Gherkin            │
│              ├──→ ADR (L5): Architecture decisions             │
│              └──→ CTR (L8): API contracts, schemas             │
│                                                                 │
│  NOT in BRD→Handoff: SPEC (L9) receives from ADR/CTR          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Success Criteria

1. **BRD scores increase** - Out-of-scope items no longer penalize BRD
2. **Actions captured** - All personas can create actions for downstream layers
3. **Validation passes** - All actions have correct format
4. **Extraction works** - Filter by target, type, priority
5. **Future-ready** - Scripts accept new types/targets with warnings

---

## Rollback

If issues occur:
1. Revert prompt changes → Actions won't be generated
2. Remove scripts → No impact on existing functionality
3. Existing reviews remain valid
4. No breaking changes
