---
title: "EARS (Event-Action-Response-State) — Engineering Requirements"
tags:
  - index-document
  - layer-3-artifact
  - shared-architecture
custom_fields:
  document_type: readme
  artifact_type: EARS
  layer: 3
  priority: shared
---

# EARS (Event-Action-Response-State) — Engineering Requirements

## Generation Rules

- Index-only: maintain `EARS-00_index.md` as the authoritative plan and registry (mark planned items with Status: Planned).
- Templates: default to the MVP template; use the full (sectioned) template only when explicitly set in project settings or clearly requested in the prompt.
- Inputs used for generation: `EARS-00_index.md` + selected template profile; no skeletons are used.
- Example index: `ai_dev_flow/tmp/SYS-00_index.md`.

Note: `EARS-TEMPLATE.md` is a reference template. For real EARS documents, prefer sectioned docs using `EARS-SECTION-0-TEMPLATE.md` and `EARS-SECTION-TEMPLATE.md` per `../DOCUMENT_SPLITTING_RULES.md`.

## Overview

EARS files capture engineering requirements in a structured, precise format that transforms high-level product requirements into clear, testable statements. EARS uses the **WHEN-THE-SHALL-WITHIN** syntax to ensure every requirement is measurable and implementation-ready.

## Purpose

EARS serves as the crucial translation layer between:
- **Upstream**: Product Requirements Documents (PRDs) 
- **Downstream**: Atomic Requirements (REQs), Architecture Decisions (ADRs), and Technical Specifications

## Position in Document Workflow

**⚠️ See [../index.md](../index.md#traceability-flow) for the authoritative workflow visualization.**

**⚠️ See for the full document flow: [SPEC_DRIVEN_DEVELOPMENT_GUIDE.md](../SPEC_DRIVEN_DEVELOPMENT_GUIDE.md)**

## Statement Types

### Event-Driven Requirements
Define system behavior in response to specific events:

```markdown
WHEN [triggering condition] THE [system] SHALL [response action] WITHIN [timeframe]
```

**Example:**
```markdown
WHEN the [DATA_ANALYSIS - e.g., user behavior analysis, trend detection] Agent requests historical data, the client SHALL retrieve data from [EXTERNAL_DATA_PROVIDER - e.g., Weather API, item Data API] and cache the response with endpoint-appropriate TTL.
```

### State-Driven Requirements
Define behavior based on system states:

```markdown
WHILE [state condition] THE [system] SHALL [behavior] WITHIN [constraint]
```

**Example:**
```markdown
WHILE [EXTERNAL_DATA_PROVIDER - e.g., Weather API, item Data API] is degraded, the client SHALL use the last valid cached response if freshness SLA is met.
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
@requirement:[REQ-NN](../07_REQ/.../REQ-NN_...md#REQ-NN)
@adr:[ADR-NN](../05_ADR/ADR-NN_...md#ADR-NN)
@PRD:[PRD-NN](../02_PRD/PRD-NN_...md)
@SYS:[SYS-NN](../06_SYS/SYS-NN_...md)
@spec:[SPEC-NN](../10_SPEC/.../SPEC-NN_...yaml)
@bdd:[BDD-NN.SS:scenarios](../04_BDD/BDD-NN_{suite}/BDD-NN.SS_{slug}.feature#scenarios)
```

### Requirements section

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

### Traceability section

Document upstream sources and downstream artifacts:

```markdown
## Traceability
- Upstream Sources: [PRD-NN](../02_PRD/PRD-NN_...md), [SYS-NN](../06_SYS/SYS-NN_...md)
- Downstream Artifacts: [REQ-NN](../07_REQ/.../REQ-NN_...md#REQ-NN), [SPEC-NN](../10_SPEC/.../SPEC-NN_...yaml)
- Anchors/IDs: `# EARS-NN`
- Code Path(s): `src/domain/component/module.py`
```

## File Naming Convention

```
EARS-NN_descriptive_title.md
```

Where:
- `EARS` is the constant prefix
- `NNN` is the 2+ digit sequence number (01, 02, 003, etc.)
- `descriptive_title` uses snake_case for clarity

**Examples:**
- `EARS-01_external_api_integration.md`
- `EARS-035_resource_limit_enforcement.md`
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
- Specify response times, throughput, availability, and other quality attributes
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

See `EARS-01_external_api_integration.md` for a complete example of a well-structured EARS file.

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
## File Size Limits

- Target: 300–500 lines per file
- Maximum: 600 lines per file (absolute)
- If a file approaches/exceeds limits, split into section files using `EARS-SECTION-TEMPLATE.md` and update the suite index. See `../DOCUMENT_SPLITTING_RULES.md` for core splitting standards.

## Document Splitting Standard

When EARS documents grow large or span disparate requirement groups:
- Ensure `EARS-{NN}.0_index.md` exists and contains a section map
- Create `EARS-{NN}.{S}_{section_slug}.md` from `EARS-SECTION-TEMPLATE.md` (see `../DOCUMENT_SPLITTING_RULES.md` for numbering and required front‑matter)
- Keep Prev/Next navigation and update traceability entries
- Validate with link and size lints; keep YAML frontmatter consistent across sections
