---
title: "UXSPEC MVP Validation Rules"
tags:
  - validation-rules
  - layer-9-artifact
  - uxspec-subtype
custom_fields:
  document_type: rules
  artifact_type: UXSPEC
  layer: 9
  subtype_code: 52
---

# UXSPEC MVP Validation Rules

## Purpose

Validation checklist for UX/Design Specification (UXSPEC) documents after creation.

## Validation Checklist

### Structure Validation

- [ ] File is valid YAML
- [ ] File name matches `UXSPEC-NN_name.yaml` format
- [ ] All required sections present
- [ ] `instance_document_type: uxspec-document`
- [ ] `deliverable_type: ux`

### Metadata Validation

- [ ] Version is semantic version format (X.Y.Z)
- [ ] Status is valid (draft, review, approved, implemented)
- [ ] Dates are YYYY-MM-DD format
- [ ] At least one author specified
- [ ] `ctr_required: false` (or true if CTR used)

### Traceability Validation

- [ ] REQ reference present (required)
- [ ] CTR reference present (optional, document if used)
- [ ] All cumulative tags complete (BRD through REQ)
- [ ] Downstream artifacts defined (wireframes, mockups, prototypes)
- [ ] Element IDs use UXSPEC.NN.TT.SS format

### UX Specification Validation

- [ ] artifact_type specified (wireframe/mockup/prototype/workflow/user_journey)
- [ ] fidelity specified (low/medium/high)
- [ ] tool specified (figma/sketch/miro/lucidchart)

### User Flow Validation

- [ ] At least one user flow defined
- [ ] Each flow has unique ID (UXSPEC.NN.60.SS format)
- [ ] Each flow has name
- [ ] Each flow has entry_point
- [ ] Each flow has exit_point
- [ ] Each flow has at least one step
- [ ] Steps include action and system_response

### Screen Validation

- [ ] At least one screen defined
- [ ] Each screen has unique ID (UXSPEC.NN.61.SS format)
- [ ] Each screen has name
- [ ] Each screen has purpose
- [ ] Components listed (if applicable)

### Component Validation

- [ ] Component IDs use UXSPEC.NN.62.SS format
- [ ] Component type specified
- [ ] Component states defined (default, hover, active, disabled)
- [ ] Variants documented if applicable

### Interaction Validation

- [ ] Interaction IDs use UXSPEC.NN.63.SS format
- [ ] Trigger specified (click/hover/focus/scroll/gesture)
- [ ] Animation type specified if animated
- [ ] Duration specified for animations
- [ ] Easing function specified for animations

### Accessibility Validation

- [ ] WCAG level specified (A/AA/AAA)
- [ ] Color contrast requirements documented
- [ ] Keyboard accessibility addressed
- [ ] Focus indicators specified
- [ ] Screen reader compatibility documented
- [ ] Touch target sizes specified (44x44px minimum)
- [ ] Form labels documented
- [ ] Error association documented

### Visual Requirements Validation

- [ ] Style guide reference provided
- [ ] Typography specifications included
- [ ] Color palette documented
- [ ] Spacing tokens defined
- [ ] Theme support documented

### Responsive Validation

- [ ] Breakpoints defined
- [ ] Mobile layout documented
- [ ] Tablet layout documented (if applicable)
- [ ] Desktop layout documented
- [ ] Adaptive component behavior specified

### Error States Validation

- [ ] Error messages documented
- [ ] Empty states defined
- [ ] Loading states specified
- [ ] Recovery actions provided

### Verification Validation

- [ ] At least one BDD scenario referenced
- [ ] Usability testing criteria specified
- [ ] Accessibility testing tools listed

## DESIGN-Ready Score Calculation

| Criterion | Weight | Check |
|-----------|--------|-------|
| User Flow Completeness | 25% | All flows with entry/exit points and steps |
| Interaction Patterns | 20% | All interactions, animations, transitions |
| Accessibility Requirements | 20% | WCAG compliance, ARIA patterns |
| Visual Requirements | 15% | Style guide, typography, colors |
| Traceability | 20% | All upstream/downstream links |

**Target**: >= 85%

## Score Calculation Method

```
Score = (user_flow_score * 0.25) +
        (interaction_score * 0.20) +
        (accessibility_score * 0.20) +
        (visual_score * 0.15) +
        (traceability_score * 0.20)
```

### Scoring Each Criterion

| Score | Description |
|-------|-------------|
| 100% | All items complete and detailed |
| 75% | Most items complete, minor gaps |
| 50% | Core items complete, significant gaps |
| 25% | Partial completion, major gaps |
| 0% | Section missing or empty |

## Error Codes

| Code | Severity | Message |
|------|----------|---------|
| UXSPEC-E001 | Error | File is not valid YAML |
| UXSPEC-E002 | Error | Missing required field |
| UXSPEC-E003 | Error | deliverable_type must be 'ux' |
| UXSPEC-E004 | Error | Missing REQ reference |
| UXSPEC-E005 | Error | No user flows defined |
| UXSPEC-E006 | Error | No screens defined |
| UXSPEC-E007 | Error | Flow missing entry_point or exit_point |
| UXSPEC-E008 | Error | WCAG level not specified |
| UXSPEC-W001 | Warning | Missing style guide reference |
| UXSPEC-W002 | Warning | Missing typography specifications |
| UXSPEC-W003 | Warning | Missing BDD references |
| UXSPEC-W004 | Warning | CTR reference not provided (optional) |
| UXSPEC-W005 | Warning | Missing responsive breakpoints |
| UXSPEC-W006 | Warning | Missing error states documentation |
| UXSPEC-W007 | Warning | Missing loading states documentation |

## Common Validation Failures

### User Flow Issues

| Issue | Resolution |
|-------|------------|
| Missing entry_point | Add where user starts the flow |
| Missing exit_point | Add where user completes the flow |
| No steps defined | Add sequential steps with actions |
| Steps without system_response | Add how system responds to each action |

### Accessibility Issues

| Issue | Resolution |
|-------|------------|
| WCAG level missing | Add wcag_level: "AA" (or A/AAA) |
| Checklist incomplete | Complete all checklist items with true/false |
| ARIA patterns missing | Document required ARIA patterns |

### Visual Issues

| Issue | Resolution |
|-------|------------|
| No style guide | Add reference to design system |
| Typography missing | Define h1, body, caption at minimum |
| Color palette missing | Document primary, secondary, error, success |

---

**Rules Version**: 1.0
**Last Updated**: 2026-03-01
