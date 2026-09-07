# EARS Generation Pattern — SDD v3.2

## Pattern: PRD Capabilities → EARS Statements

Each PRD core capability maps to one or more EARS requirements, classified by pattern:

| PRD Capability | Maps To | Pattern |
|---------------|---------|---------|
| User-initiated action | event_driven | WHEN-THE-SHALL-WITHIN |
| Continuous monitoring | state_driven | WHILE-THE-SHALL-WITHIN |
| Error handling | unwanted_behavior | IF-THE-SHALL-WITHIN |
| Global invariants | ubiquitous | THE-SHALL |

## Prohibited Qualifiers (replace with quantified targets)

| Prohibited | Replacement |
|-----------|-------------|
| "real-time" | "WITHIN 60 seconds" or "p50 < 100ms, p95 < 300ms" |
| "immediate" / "immediately" | "WITHIN 30 seconds" or specific duration |
| "continuously" | "at each [event]" or specify periodicity |
| "fast" / "quickly" | Specify exact latency numbers (p50/p95/p99) |
| "near X" | "within 0.0Y of X" or explicit tolerance |

## Structural Rules

1. **No compound WHEN with AND** — Split into atomic requirements. "WHEN A AND B" becomes two separate WHEN requirements.

2. **No nested IF inside SHALL** — Each conditional path is a separate requirement. "SHALL escalate IF counter >= 3" becomes a separate IF-THE-SHALL.

3. **WITHIN must reference a specific event** — No orphaned reference points. "WITHIN 5 minutes" must be "WITHIN 5 minutes of [event]."

4. **IF/WITHIN must reference the same event** — Don't mix trigger and reference. "IF 3 failures... WITHIN 30 minutes of first failure" is wrong. Fix to "WITHIN 5 minutes of third failure."

5. **No subjective criteria** — Replace "acceptable", "reasonable", "significant". "assignment risk is unacceptable" becomes "ITM by >= 1% of underlying price."

6. **Atomicity**: One testable concept per requirement. If a WHEN clause lists 3+ alternatives via OR, split into separate atomic requirements.

7. **Quantify interval ranges**: "every 15-25 min" must specify configurable parameter or fixed value.

## State Machine Pattern

Every EARS document that touches operational modes MUST include a state_machine section:

```yaml
state_machine:
  description: 'Agent operational modes and transition rules.'
  states:
    AUTONOMOUS:
      description: Normal operation
      transitions:
        - to: WARNING
          trigger: Data staleness detected per thresholds
        - to: HALTED
          trigger: Critical dependency failure (3 consecutive failures)
    WARNING:
      description: Degraded — decisions suppressed, monitoring continues
      transitions:
        - to: AUTONOMOUS
          trigger: Recovery conditions met for 2 consecutive check windows
        - to: HALTED
          trigger: Failure escalates
    HALTED:
      description: All operations stopped
      transitions:
        - to: MANUAL
          trigger: Auto-escalates on HALTED entry
    MANUAL:
      description: Operator control — dashboard with one-click approvals
      transitions:
        - to: RECONCILING
          trigger: Operator initiates recovery sequence
    RECONCILING:
      description: State reconciliation with broker/external systems
      transitions:
        - to: AUTONOMOUS
          trigger: Reconciliation complete, broker API health passes 3 probes
        - to: MANUAL
          trigger: Unreconcilable state found (operator decides)
```

## Benchmarks-First Strategy

For EARS (and any SDD layer with 9+ documents):

1. Generate 2 benchmark documents from the strongest upstream sources
2. Validate both with sdd_validate
3. Review with 4 personas in parallel (requirements-specialist, technical-lead, qa-lead, chaos-engineer)
4. Remediate findings
5. Once pattern validated, batch-generate remaining 7 using execute_code

## Batch EARS Generation — Python Pattern

```python
import subprocess, yaml, hashlib, re

from sdd_doc_lint import compute_element_hash  # # Single source: governance/ID_NAMING_STANDARDS.md. Never re-derive the hash here.

def make_id(doc_type, doc_num, section_num, desc):
    h = compute_element_hash(f"{doc_num:02d}", f"{section_num:02d}", desc, "")[:4]
    return f"{doc_type}.{doc_num:02d}.{section_num:02d}.{h}"

def postprocess_yaml(yaml_str):
    """Quote values starting with > < comparison operators."""
    lines = yaml_str.split('\n')
    out = []
    for line in lines:
        if ':' in line and not line.strip().startswith('#'):
            idx = line.index(':')
            val = line[idx+1:].strip()
            if val and val[0] in '><':
                prefix = line[:idx+1]
                out.append(f'{prefix} "{val}"')
                continue
        out.append(line)
    return '\n'.join(out)

# Map PRD capabilities to EARS requirements
# event-driven: WHEN [trigger], THE [component] SHALL [action] WITHIN [constraint]
# state-driven:  WHILE [state], THE [component] SHALL [behavior] WITHIN [context]
# unwanted:      IF [error], THE [component] SHALL [recovery] WITHIN [timing]
# ubiquitous:    THE [component] SHALL [invariant] for [scope]
```

## Dual-WITHIN Pitfall — Atomicity Violation (TradeGent CC 2026-05-14)

A single EARS requirement with two WITHIN clauses violates atomicity. Each distinct timing
target must be a separate requirement. This is a common generation error when a PRD capability
describes two modes with different freshness targets (e.g., streaming vs snapshot).

```yaml
# WRONG — two WITHIN in one requirement (caught at review)
statement: |
  WHEN the Strategy Engine requests quote data, THE Internal API SHALL return
  quote stream WITHIN 1 second in streaming mode, WITHIN 30 seconds in snapshot mode.

# RIGHT — split into two atomic requirements
- name: Stream Real-Time Quotes in Streaming Mode
  statement: |
    WHEN the Strategy Engine requests streaming quote data, THE Internal API SHALL
    return quote stream WITHIN 1 second of broker event.
- name: Query Quote Snapshot on Demand
  statement: |
    WHEN the Strategy Engine requests a quote snapshot, THE Internal API SHALL
    return most recent values WITHIN 30 seconds of broker snapshot timestamp.
```

**Detection rule**: grep for `WITHIN.*WITHIN` in EARS statements. Any match is a structural violation.
Also applies to: dual thresholds in one requirement, dual state transitions, OR-branched behavior
with different timing constraints.
