# IPLAN Creation Prompt

# Document Type: IPLAN (Implementation Plan)

# Layer: 8

# Template: IPLAN-TEMPLATE.yaml

You are an expert in software implementation and execution planning.
Your task is to create an IPLAN that bridges SPEC component definitions
to actual source code with test-first development order.

## Context

- Upstream: SPEC (Layer 6), TDD (Layer 7)
- Downstream: Code (source files)
- Layer 8: IPLAN - Execution bridge from SPEC to source code

## Instructions

Follow the IPLAN-TEMPLATE.yaml structure exactly. Create:

1. **Document Control**: Generate IPLAN ID, link to SPEC component,
   set status, estimate file count and session count

2. **File Manifest**: Declare file creation order with test-first priority.
   Each file needs: path, order, status (default NOT_STARTED), session (null),
   verified (false)

3. **Execution Commands**: Provide setup, implementation, and validation
   bash commands. Test files must come before implementation files.

4. **Implementation Contracts**: Optional section. Required if 3+ files
   depend on shared interfaces. State "No implementation contracts"
   if not applicable.

5. **Session Handoff**: Initialize with empty sessions array (`sessions: []`).
   Never write a session entry while authoring — the trail is retrospective and
   is populated during implementation sessions via markers (NOT_STARTED,
   IN_PROGRESS, DONE, PARTIAL)

6. **Traceability**: Link to SPEC references and TDD references

## Output Requirements

- Use YAML format
- Include all 6 required sections from template
- Use @spec: SPEC-NN and @tdd: TDD.NN tags for traceability
- File manifest order must enforce tests-first (order numbers)
- Do NOT generate code - only describe what will be created

## Success Criteria

- All 6 sections present and populated (a Draft's `session_handoff` is `sessions: []`)
- File manifest declares all files with proper order
- Execution commands include setup, implementation, validation
- Session handoff section initialized (empty sessions array)
- Traceability links SPEC and TDD upstream artifacts
- File manifest includes test files BEFORE implementation files
