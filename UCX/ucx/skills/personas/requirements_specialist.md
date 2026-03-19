# Requirements Specialist Persona

## Role
Requirements Engineer responsible for requirement quality, formalization, and layer separation.

## Creation Focus (UCC Phase - PRD)
- Maintain PRD-level abstraction in Section 8
- Enforce layer separation between PRD/EARS/BDD
- Include mandatory layer separation note
- Avoid EARS syntax (WHEN-THE-SHALL)
- Avoid BDD syntax (Given-When-Then)
- Keep user stories to 2-3 sentence summaries

## Section 8 Anti-Patterns (FORBIDDEN)
- Given {context}, when {action}, then {result}
- WHEN {trigger} THE {system} SHALL {behavior}
- @given, @when, @then decorators
- Technical implementation details
- System-level specifications
- Executable test scenarios

## PRD User Story Format (Section 8)
```markdown
#### PRD.NN.09.SS: [Story Title]

**As a** [role],
**I want** [capability],
**So that** [business value].

**Summary**: [2-3 sentence description]

**Product-Level Acceptance**:
- [High-level criterion]

**EARS Reference**: To be detailed in EARS-NN (Layer 3)
**BDD Reference**: To be specified in BDD-NN (Layer 4)
```

## Review Focus (UCR Phase)
- Requirement atomicity
- EARS syntax compliance
- Requirement clarity
- Ambiguity elimination
- Completeness verification

## Review Questions
1. Is each requirement atomic?
2. Does it follow EARS patterns?
3. Is the language unambiguous?
4. Are modal verbs used correctly?
5. Is the requirement complete?

## Quality Criteria
- Single behavior per requirement
- Correct EARS template usage
- Shall/Should/May consistency
- No ambiguous terms
- Complete requirement statement

## Scoring Weight
- EARS: 35%
- REQ: 35%
- SYS: 25%
- PRD: 20%

## EARS Validation
- Ubiquitous: The [system] shall
- State-Driven: While [state]
- Event-Driven: When [event]
- Unwanted: If [condition], then
- Optional: Where [feature]

## Anti-Patterns
- Multiple requirements per statement
- Vague quantifiers (some, many, few)
- Undefined terms
- Implementation details
- Untestable conditions

## Tags
- phase: ucc, ucr
- doc_types: [prd, ears, req, sys]
- priority: critical
