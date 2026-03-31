---
title: "UXSPEC MVP Creation Rules"
tags:
  - creation-rules
  - layer-9-artifact
  - uxspec-subtype
custom_fields:
  document_type: rules
  artifact_type: UXSPEC
  layer: 9
  subtype_code: 52
---

# UXSPEC MVP Creation Rules

## Purpose

Guidelines for creating UX/Design Specification (UXSPEC) documents - specifications for wireframes, mockups, workflows, and user journeys.

## When to Create UXSPEC

Create a UXSPEC when:
- REQ document has `deliverable_type: ux`
- Requirement results in UI/UX design output
- Feature requires wireframes, mockups, or prototypes
- User flows need documentation

## Prerequisites

Before creating UXSPEC:

1. **REQ Document**: Atomic requirement with `deliverable_type: ux`
2. **BRD/PRD**: Business and product requirements with user stories
3. **ADR Document**: Architecture decisions for frontend framework (if applicable)
4. **BDD Scenarios**: Test scenarios for user interactions

## File Naming

```
UXSPEC-NN_feature_name.yaml
```

- `NN`: Sequential number (01, 02, 03...)
- `feature_name`: Snake_case, descriptive name

## Required Sections

| Section | Required | Description |
|---------|----------|-------------|
| metadata | Yes | Document control with `deliverable_type: ux` |
| traceability | Yes | Must include REQ reference |
| ux_specification | Yes | Flows, screens, components, interactions |
| accessibility | Yes | WCAG level, ARIA requirements |
| visual_requirements | Yes | Style guide, typography, colors |
| responsive | Yes | Breakpoints, adaptive behavior |
| verification | Yes | BDD scenarios, usability testing |

## Element ID Format

```
UXSPEC.{DOC}.{TYPE}.{SEQ}
```

| Code | Type | Example |
|------|------|---------|
| 60 | flow | UXSPEC.01.c890 |
| 61 | screen | UXSPEC.01.f2ae |
| 62 | component | UXSPEC.01.bf46 |
| 63 | interaction | UXSPEC.01.fb37 |

## CTR Requirement

UXSPEC **does not require** CTR (Contract) reference:
- CTR is optional for UX specifications
- Include CTR only if UI consumes API contracts
- Reference CTR in traceability section if applicable

## UX Specification Content

### User Flows

Each flow must include:
- **ID**: Unique identifier (UXSPEC.NN.60.SS)
- **Name**: Descriptive flow name
- **Entry Point**: Where user starts the flow
- **Exit Point**: Where user ends the flow
- **Steps**: Sequential actions with system responses

### Screens

Each screen must include:
- **ID**: Unique identifier (UXSPEC.NN.61.SS)
- **Name**: Screen name
- **Purpose**: What the screen accomplishes
- **Components**: List of UI components
- **Layout**: Structure and regions

### Components

Each component should include:
- **ID**: Unique identifier (UXSPEC.NN.62.SS)
- **Name**: Component name
- **Type**: button, input, card, modal, list, etc.
- **States**: default, hover, active, disabled, error, loading
- **Variants**: Different visual variants

### Interactions

Each interaction should include:
- **ID**: Unique identifier (UXSPEC.NN.63.SS)
- **Trigger**: click, hover, focus, scroll, gesture
- **Action**: What happens
- **Response**: Visual feedback
- **Animation**: Type, duration, easing

## Accessibility Requirements

### WCAG Compliance

Specify target WCAG level:
- **A**: Basic accessibility
- **AA**: Standard compliance (recommended)
- **AAA**: Enhanced accessibility

### Required Checklist Items

- Color contrast ratio (4.5:1 for normal text)
- Keyboard accessibility
- Focus indicators
- Screen reader compatibility
- Touch targets (44x44px minimum)
- Form labels
- Error message association

## Visual Requirements

Include references to:
- Design system or style guide
- Typography specifications
- Color palette
- Spacing tokens
- Theme support (light/dark)

## Quality Gate

**DESIGN-Ready Score Target**: >= 85%

| Criterion | Weight |
|-----------|--------|
| User Flow Completeness | 25% |
| Interaction Patterns | 20% |
| Accessibility Requirements | 20% |
| Visual Requirements | 15% |
| Traceability | 20% |

## Validation Checklist

- [ ] `deliverable_type: ux` in metadata
- [ ] REQ reference in traceability
- [ ] At least one user flow defined
- [ ] At least one screen defined
- [ ] Each flow has entry/exit points
- [ ] WCAG level specified
- [ ] Accessibility checklist completed
- [ ] Style guide referenced
- [ ] Responsive breakpoints defined
- [ ] BDD scenarios referenced

## Artifact Types

| Type | Description | Fidelity |
|------|-------------|----------|
| wireframe | Basic layout structure | low |
| mockup | Visual design representation | medium/high |
| prototype | Interactive clickable design | high |
| workflow | Process flow diagram | low/medium |
| user_journey | End-to-end user experience | medium |

## Design Tools

Supported tools for documentation:
- **Figma**: Preferred for wireframes, mockups, prototypes
- **Sketch**: Alternative design tool
- **Miro**: Workflows and user journeys
- **Lucidchart**: Flow diagrams

---

**Rules Version**: 1.0
**Last Updated**: 2026-03-01

---

## DEPRECATED: Template+Schema migration (2026-03-24)

This file is deprecated and retained for backward compatibility only.

Active references for MCP and framework tooling must use:
- `*-MVP-TEMPLATE.*`
- `*_MVP_SCHEMA.yaml`

Do not add new dependencies on this file.
