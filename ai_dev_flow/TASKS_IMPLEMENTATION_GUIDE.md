# TASKS Implementation Guide

This guide describes the standard workflow for implementing a feature defined in a `TASKS` artifact.

## 1. Initial Assessment
Before starting code:
1.  **Check Status**: Review `DEVELOPMENT_PLAN.md` (created from `TASKS/DEVELOPMENT_PLAN_TEMPLATE.md`) to confirm the task is next in the queue and prerequisites are met.
2.  **Review TASKS Artifact**: Read the `TASKS-XX.md` file to understand the scope, requirements, and design constraints.

## 2. Create Implementation Plan (IPLAN)
Translation of `TASKS` into concrete work steps.
1.  **Create File**: `docs/12_IPLAN/IPLAN-XX_[slug].md`.
2.  **Structure (Standard Pattern)**:
    *   **Phase 1: Domain & Protocols**: 
        *   Define Pydantic Models (`domain.py`)
        *   Define Interfaces/Protocols (`protocol.py`)
    *   **Phase 2: Logic & Engines**: 
        *   Implement pure logic components (`engine.py`, `calculator.py`)
        *   Focus on testability (no I/O if possible).
    *   **Phase 3: Service Assembly**: 
        *   Implement the facade/service (`service.py`) that wires components together.
        *   Implement Adapters (`adapter.py`).
    *   **Phase 4: Testing**: 
        *   Unit Tests (`tests/unit/...`)
        *   Integration Tests (`tests/integration/...`)
3.  **Cross-Reference**: Ensure mapped Tasks in IPLAN correspond to TASKS requirements.

## 3. Implementation Loop
Execute the plan phase by phase.
1.  **Update `task.md`**: Update your active agent task list to reflect the current granular steps.
    *   *Example*: `[ ] Implement DeduplicationEngine`
2.  **Code**: Implement the code in `src/`.
3.  **Test**: Write corresponding tests in `tests/`.
    *   *Tip*: Use `pytest` for automated testing.
    *   *Tip*: Use manual verification scripts if environment isolation is complex.
4.  **Mark Progress**: Check off items in `IPLAN` and `task.md` as you go.

## 4. Verification & Validation
1.  **Run Tests**: Ensure all new tests pass and no regressions in related modules.
2.  **Manual Check**: If applicable, run a usage script to verify end-to-end behavior.

## 5. Documentation & Completion
1.  **Update IPLAN**: Mark all tasks as `[x]`.
2.  **Update Development Plan**:
    *   Change status icon to ✅ in the Phase Table.
    *   Add an entry to the **Session Log** summarizing the work.
3.  **Update Walkthrough**: Add a section to `walkthrough.md` describing the design and verification results.
4.  **Notify User**: Report completion with key deliverables.
