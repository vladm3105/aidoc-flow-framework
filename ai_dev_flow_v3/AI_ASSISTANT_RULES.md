# AI Assistant Rules — SDD v3

## Template Usage

- Use templates from `ai_dev_flow_v3/0X_TYPE/TYPE-TEMPLATE.yaml`.
- Fill placeholder fields (`[text]`, `xxxx`) with actual values.
- Do not remove `_guidance`, `_note`, `_example`, or `_antipatterns` fields — they are ignored by validators but provide context.

## Traceability Rules

- Every element must be traceable to an upstream artifact.
- Use the cumulative tag hierarchy: `@brd` → `@prd` → `@ears` → `@bdd` → `@adr` → `@tdd` → `@spec`.
- Downstream references are declared as placeholders until artifacts exist.
- Never create circular references.

## Layer Generation Order

```
1. BRD — business requirements, objectives, scope
2. PRD — product features, user stories (from BRD)
3. EARS — formal WHEN-THE-SHALL-WITHIN requirements (from PRD)
4. BDD — Given-When-Then scenarios (from EARS)
5. ADR — architecture decisions (from BDD + PRD topics)
6. TDD — test pyramid, BDD-to-test mapping (from BDD + ADR)
7. SPEC — component interfaces, data models, behavior (from TDD + ADR)
8. Code — implementation from SPEC
```

## TDD Enforcement

When generating code from SPEC:
1. Generate test files FIRST (from TDD Section 3 mappings)
2. Run tests — they MUST fail (no implementation exists)
3. Generate implementation files
4. Run tests — they MUST pass
5. Refactor — keep tests green

## What NOT to Reference

- `ai_dev_ssd_flow/` — SDD v2 (superseded)
- SYS, REQ, CTR layers — cut from v3
- TSPEC subtypes (UTEST, ITEST, STEST, FTEST, PTEST, SECTEST) — replaced by TDD
- TASKS — AI generates tasks from SPEC on-the-fly
- CHG/ gates — not a v3 concern
