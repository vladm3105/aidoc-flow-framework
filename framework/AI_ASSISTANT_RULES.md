# AI Assistant Rules

## Template Usage

- Use templates from `layers/0X_TYPE/TYPE-TEMPLATE.yaml`.
- Fill placeholder fields (`[text]`, `xxxx`) with actual values.
- Do not remove `_guidance`, `_note`, `_example`, or `_antipatterns` fields — they are ignored by validators but provide context.

## Traceability Rules

- Every element must be traceable to an upstream artifact.
- Use the cumulative tag hierarchy: `@brd` → `@prd` → `@ears` → `@bdd` → `@adr` → `@spec` → `@tdd` → `@iplan`.
- Downstream references are declared as placeholders until artifacts exist.
- Never create circular references.

## Layer Generation Order

```
1. BRD — business requirements, objectives, scope
2. PRD — product features, user stories (from BRD)
3. EARS — formal WHEN-THE-SHALL-WITHIN requirements (from PRD)
4. BDD — Given-When-Then scenarios with spec_trace to SPEC (from EARS)
5. ADR — architecture decisions (from BDD + PRD topics)
6. SPEC — component interfaces, data models, behavior contracts (from ADR + BDD)
7. TDD — test case definitions with inputs/outputs/edge cases (from SPEC + BDD)
8. IPLAN — file manifest, bash commands, session handoff (from TDD)
9. Code — implementation from IPLAN
```

## TDD Enforcement

When generating code from IPLAN:

1. Generate test files FIRST (from TDD Sections 3-4 test mappings and cases)
2. Run tests — they MUST fail (no implementation exists)
3. Generate implementation files
4. Run tests — they MUST pass
5. Refactor — keep tests green

## Development Completion Rule

A development IPLAN is **Completed** when:

- Source code is authored, committed, and tests pass
- Terraform modules, Helm charts, CI/CD workflow files, schema DDL, and deployment scripts are authored and committed
- `pre-commit run --all-files` passes with no errors

A development IPLAN is **NOT** blocked by:

- `terraform apply` not yet executed
- `atlas migrate apply` not yet run against the target environment
- Acceptance/soak testing not yet performed
- Image not yet built or deployed to a registry

These operator-only execution steps belong to a separate deployment plan. When closing a development IPLAN, register any deployment-handoff obligations in the IPLAN registry's `deferred_items` before flipping `Completed`.

## IPLAN Session Handoff

Each AI agent session follows this protocol:

1. Read `session_handoff.sessions` — identify the last session's state
2. Check `file_manifest.files` — find next NOT_STARTED or PARTIAL file
3. Read `partial_work` description if resuming a PARTIAL step
4. Continue from that point — do NOT regenerate completed work
5. Update file status after completion or session end
6. Append to `session_handoff.sessions` with next_session_directive

## What NOT to Reference

- Non-active layer artifacts in current authoring workflows
- Legacy subtype taxonomies when generating active artifacts
- CHG gates — a governance overlay, outside layer authoring
