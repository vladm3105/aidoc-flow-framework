# {PROJECT_NAME} — Project Definition

**Document:** PROJECT_DEFINITION.md
**Version:** 1.0.0
**Date:** {DATE}
**Status:** Draft

---

## Strategic Context

This project definition describes {PROJECT_DESCRIPTION_SHORT}. Replace this section with your project's strategic context, including:

- Parent initiative or program (if applicable)
- Strategic decision gates
- Links to related strategy documents

---

## Executive Summary

**{PROJECT_NAME}** is {PROJECT_DESCRIPTION}.

**Core Differentiator:** {PROJECT_DIFFERENTIATOR}

---

## Project Purpose

### Problem Statement

{PROBLEM_STATEMENT}

| Challenge | Impact |
|-----------|--------|
| {CHALLENGE_1} | {IMPACT_1} |
| {CHALLENGE_2} | {IMPACT_2} |
| {CHALLENGE_3} | {IMPACT_3} |

### Solution

{SOLUTION_OVERVIEW}

1. **{CAPABILITY_1}** — {CAPABILITY_1_DESCRIPTION}
2. **{CAPABILITY_2}** — {CAPABILITY_2_DESCRIPTION}
3. **{CAPABILITY_3}** — {CAPABILITY_3_DESCRIPTION}

---

## Architecture Overview

> Replace this section with your project's architecture diagram and description.
> Use Mermaid or ASCII diagrams for version-controlled illustrations.

```

                              USER INTERFACE
                          {UI_TECHNOLOGY_STACK}




                         APPLICATION LAYER
                      {APP_TECHNOLOGY_STACK}




                           DATA LAYER
                      {DATA_TECHNOLOGY_STACK}

```

### Key Architecture Decisions

| Decision | Choice | Rationale | ADR |
|----------|--------|-----------|-----|
| {DECISION_1} | {CHOICE_1} | {RATIONALE_1} | ADR-001 |
| {DECISION_2} | {CHOICE_2} | {RATIONALE_2} | ADR-002 |
| {DECISION_3} | {CHOICE_3} | {RATIONALE_3} | ADR-003 |

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **UI** | {UI_TECH} | {UI_PURPOSE} |
| **Backend** | {BACKEND_TECH} | {BACKEND_PURPOSE} |
| **Database** | {DB_TECH} | {DB_PURPOSE} |
| **Infrastructure** | {INFRA_TECH} | {INFRA_PURPOSE} |
| **CI/CD** | {CICD_TECH} | {CICD_PURPOSE} |

---

## Scope Clarification

### What This Project IS

| Category | Description |
|----------|-------------|
| **{SCOPE_IN_1}** | {SCOPE_IN_1_DESC} |
| **{SCOPE_IN_2}** | {SCOPE_IN_2_DESC} |
| **{SCOPE_IN_3}** | {SCOPE_IN_3_DESC} |

### What This Project is NOT

| Category | Clarification |
|----------|---------------|
| **{SCOPE_OUT_1}** | {SCOPE_OUT_1_DESC} |
| **{SCOPE_OUT_2}** | {SCOPE_OUT_2_DESC} |
| **{SCOPE_OUT_3}** | {SCOPE_OUT_3_DESC} |

---

## MVP Scope

| Aspect | Decision |
|--------|----------|
| {MVP_ASPECT_1} | {MVP_DECISION_1} |
| {MVP_ASPECT_2} | {MVP_DECISION_2} |
| {MVP_ASPECT_3} | {MVP_DECISION_3} |

### MVP Success Criteria

| Criterion | Metric |
|-----------|--------|
| **{SUCCESS_1}** | {METRIC_1} |
| **{SUCCESS_2}** | {METRIC_2} |
| **{SUCCESS_3}** | {METRIC_3} |

---

## Open Questions

| Question | Options | Status |
|----------|---------|--------|
| {QUESTION_1} | {OPTIONS_1} | To be decided |
| {QUESTION_2} | {OPTIONS_2} | To be decided |

---

## Terminology

| Term | Definition |
|------|------------|
| **{TERM_1}** | {DEFINITION_1} |
| **{TERM_2}** | {DEFINITION_2} |
| **{TERM_3}** | {DEFINITION_3} |

---

## Related Documents

- [docs/adr/](adr/) — Architecture Decision Records
- [docs/qa/](qa/) — QA Documentation
- [governance/PROJECT_PLAN.md](../governance/PROJECT_PLAN.md) — Project timeline and milestones

---

## Template Usage

This document uses placeholder variables. Replace all `{PLACEHOLDER}` values with your project-specific content. See [CONFIG.md](../CONFIG.md) for the complete placeholder reference.

**Required placeholders to replace:**

- `{PROJECT_NAME}` — Your project name
- `{PROJECT_DESCRIPTION}` — One-sentence project description
- `{PROJECT_DIFFERENTIATOR}` — What makes this project unique
- `{PROBLEM_STATEMENT}` — The problem being solved
- All `{CHALLENGE_N}`, `{CAPABILITY_N}`, `{SCOPE_*}` placeholders
