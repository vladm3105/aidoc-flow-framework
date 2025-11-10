# EARS (Easy Approach to Requirements Syntax)

## Overview

EARS files capture requirements in a structured, precise format that transforms high-level product requirements into clear, testable statements. EARS uses the **WHEN-THE-SHALL-WITHIN** syntax to ensure every requirement is measurable and implementation-ready.

## Purpose

EARS serves as the crucial translation layer between:
- **Upstream**: Product Requirements Documents (PRDs) 
- **Downstream**: Atomic Requirements (REQs), Architecture Decisions (ADRs), and Technical Specifications

## [RESOURCE_INSTANCE - e.g., database connection, workflow instance] in Development Workflow
```
BRD (Business Requirements Document): High-level business needs
        ↓
PRD (Product Requirements Document): User needs and features
        ↓
EARS (Easy Approach to Requirements Syntax): Atomic, measurable requirements using WHEN/THEN format, Requirements Expressions). All work traces back to formal technical requirements (WHEN-THE-SHALL-WITHIN format), AI generated structured requirement formatAI transforms interfaces as code specification
        ↓
BDD (Behavior-Driven Development). Business + Dev + Test AI generates acceptance scenarios 
        ↓
ADR (Architecture Decisions Requirements)
        ↓
SYS (System Requirements). Technical interpretation of business requirements  
        ↓
REQ (Atomic Requirements) 
        ↓
SPEC (Technical Implementation)  ← )  
        ↓
TASKS (Implementation Plans)
        ↓
Code (src/{module_name}/) ← AI generates Python
        ↓
Tests (tests/{suit_name}) ← AI generates test suites
        ↓
Validation ← AI runs BDD tests
        ↓
Human Review ← HUMAN reviews architecture only
        ↓
Production-Ready Code 
                     
```

## Statement Types

### Event-Driven Requirements
Define system behavior in response to specific events:

```markdown
WHEN [triggering condition] THE [system] SHALL [response action] WITHIN [timeframe]
```

**Example:**
```markdown
WHEN the [DATA_ANALYSIS - e.g., user behavior analysis, trend detection] Agent requests historical data, the client SHALL retrieve data from [EXTERNAL_DATA_PROVIDER - e.g., Weather API, Stock Data API] and cache the response with endpoint-appropriate TTL.
```

### State-Driven Requirements
Define behavior based on system states:

```markdown
WHILE [state condition] THE [system] SHALL [behavior] WITHIN [constraint]
```

**Example:**
```markdown
WHILE [EXTERNAL_DATA_PROVIDER - e.g., Weather API, Stock Data API] is degraded, the client SHALL use the last valid cached response if freshness SLA is met.
```

### Unwanted Behavior Requirements
Define behaviors to avoid (negative requirements):

```markdown
IF [problem condition] THE [system] SHALL [preventive action] WITHIN [timeframe]
```

**Example:**
```markdown
IF rate limits are exceeded, the client SHALL queue or throttle requests per token bucket policy and return a clear 429 error with retry-after guidance to callers.
```

### Ubiquitous Requirements
Define system-wide constraints and quality attributes:

```markdown
THE [system] SHALL [requirement] WITHIN [constraint]
```

**Examples:**
```markdown
THE client SHALL normalize responses to the internal schema used by [EXTERNAL_SERVICE_GATEWAY] to enable seamless failover.

THE client SHALL complete requests within 2 seconds p95 for supported endpoints.
```

## File Structure

### Header with Traceability Tags

All EARS files start with traceability tags linking to related artifacts:

```markdown
@requirement:[REQ-NNN](../reqs/.../REQ-NNN_...md#REQ-NNN)
@adr:[ADR-NNN](../adrs/ADR-NNN_...md#ADR-NNN)
@prd:[PRD-NNN](../prd/PRD-NNN_...md)
@sys:[SYS-NNN](../sys/SYS-NNN_...md)
@spec:[SPEC-NNN](../specs/.../SPEC-NNN_...yaml)
@bdd:[BDD-NNN:scenarios](../bbds/BDD-NNN_....feature#scenarios)
```

### Requirements Section

Organize statements by type with clear headers:

```markdown
## Requirements

### Event-driven
- WHEN [condition] THE [system] SHALL [action] WITHIN [constraint].
- WHEN [another condition] THE [system] SHALL [different action].

### Unwanted Behavior
- IF [problem] THE [system] SHALL [prevention] WITHIN [timeframe].
- IF [another problem] THE [system] SHALL [fallback].

### State-driven
- WHILE [state] THE [system] SHALL [behavior] WITHIN [limit].
- WHILE [another state] THE [system] SHALL [alternative behavior].

### Ubiquitous
- THE [system] SHALL [system-wide requirement].
- THE [system] SHALL [quality attribute] WITHIN [threshold].
```

### Traceability Section

Document upstream sources and downstream artifacts:

```markdown
## Traceability
- Upstream Sources: [PRD-NNN](../prd/PRD-NNN_...md), [SYS-NNN](../sys/SYS-NNN_...md)
- Downstream Artifacts: [REQ-NNN](../reqs/.../REQ-NNN_...md#REQ-NNN), [SPEC-NNN](../specs/.../SPEC-NNN_...yaml)
- Anchors/IDs: `# EARS-NNN`
- Code Path(s): `option_strategy/component/module.py`
```

## File Naming Convention

```
EARS-NNN_descriptive_title.md
```

Where:
- `EARS` is the constant prefix
- `NNN` is the three-digit sequence number (001, 002, 003, etc.)
- `descriptive_title` uses snake_case for clarity

**Examples:**
- `EARS-001_alpha_vantage_integration.md`
- `EARS-035_position_limit_enforcement.md`
- `EARS-042_ml_model_serving.md`

## Guidelines for Writing EARS Statements

### 1. Use Precise, Measurable Language
- Replace vague terms with specific criteria
- Include quantitative constraints wherever possible
- Define exact timeframes, thresholds, and boundaries

### 2. One Concept Per Statement
- Each WHEN-THE-SHALL-WITHIN statement represents one atomic requirement
- Avoid combining multiple behaviors into single statements
- Split complex requirements into multiple clear statements

### 3. Maintain Consistent Context
- Use consistent terminology within a file
- Define acronyms and domain-specific terms clearly
- Reference the same system component consistently

### 4. Include Performance and Quality Attributes
- Specify response times, throughput, availability, and other NFRs
- Define error conditions and failure modes explicitly
- Include security and audit requirements where applicable

### 5. Enable Testability
- Write statements that can be directly translated to BDD scenarios
- Include specific input conditions that trigger behavior
- Define measurable outputs and side effects

## Integration with Development Workflow

### Pre-Writing Steps
1. Read the source PRD thoroughly
2. Identify functional requirements in the PRD
3. Prepare traceability links to related artifacts
4. Understand system context and constraints

### Writing Process
1. Use the template structure for consistency
2. Categorize each requirement by behavioral type
3. Write clear, unambiguous WHEN-THE-SHALL-WITHIN statements
4. Include performance constraints and edge cases
5. Add comprehensive traceability information

### Post-Writing Validation
1. Cross-reference all linked artifacts exist and are accessible
2. Ensure each statement is independently testable
3. Verify consistency with PRD functional requirements
4. Check for complete coverage of all PRD requirements

## Quality Gates

**Each EARS statement must:**
- Use proper WHEN-THE-SHALL-WITHIN format
- Be atomic (one concept per statement)
- Include measurable criteria
- Be verifiable through testing
- Include appropriate time/space constraints
- Maintain traceability links
- Use consistent terminology

**Each EARS file must:**
- Follow naming conventions
- Include complete traceability header
- Categorize statements appropriately
- Cover all source PRD requirements
- Reference valid downstream artifacts
- Include code path information

## Example Template

See `EARS-001_alpha_vantage_integration.md` for a complete example of a well-structured EARS file.

## Benefits

1. **Precision**: Eliminates ambiguity in requirements interpretation
2. **Traceability**: Maintains clear links throughout the development pipeline
3. **Testability**: Enables direct translation to BDD scenarios and unit tests
4. **Consistency**: Standardizes requirements documentation across teams
5. **AI-Readiness**: Provides structured input for AI-assisted specification generation

## Common Pitfalls

1. **Vague Language**: Avoid terms like "fast," "reliable," "secure" without quantification
2. **Overloading**: Don't combine multiple behaviors into single statements
3. **Missing Context**: Always specify the subject system and triggering conditions
4. **Orphaned Statements**: Ensure each statement can be traced to a PRD source
5. **Incomplete Coverage**: Review PRDs to capture all functional requirements

## Version Control and Collaboration

- Commits should include the EARS ID in commit messages
- Reviews should verify completeness of PRD coverage
- Regular updates may be needed as PRDs evolve
- Changes should maintain backward traceability links
