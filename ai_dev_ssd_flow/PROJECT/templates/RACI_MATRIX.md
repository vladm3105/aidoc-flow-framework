# RACI Matrix

**Project**: {PROJECT_NAME}
**Version**: 1.0
**Last Updated**: {DATE}

---

## Legend

- **R** = Responsible (does the work)
- **A** = Accountable (final decision maker, only one per row)
- **C** = Consulted (provides input)
- **I** = Informed (kept up to date)

## Roles

| Role | Description |
|------|-------------|
| Project Lead | Overall project accountability |
| Product Manager | Product requirements and priorities |
| Architect | Technical design and architecture |
| Developer | Implementation and coding |
| QA Lead | Quality assurance and testing |
| DevOps | Infrastructure and CI/CD |

## Activity Matrix

### Tier 1: Business Requirements (L1-L4)

| Activity | Project Lead | Product Manager | Architect | Developer | QA Lead | DevOps |
|----------|:------------:|:---------------:|:---------:|:---------:|:-------:|:------:|
| BRD creation | A | R | C | I | I | I |
| PRD creation | A | R | C | I | C | I |
| EARS creation | A | C | R | I | C | I |
| BDD creation | A | C | C | I | R | I |
| GATE-01 approval | A | R | C | I | C | I |

### Tier 2: Architecture (L5-L8)

| Activity | Project Lead | Product Manager | Architect | Developer | QA Lead | DevOps |
|----------|:------------:|:---------------:|:---------:|:---------:|:-------:|:------:|
| ADR creation | A | I | R | C | I | C |
| SYS creation | A | I | R | C | C | I |
| REQ creation | A | I | R | C | C | I |
| CTR creation | A | I | R | C | I | C |
| GATE-05 approval | A | I | R | C | C | I |

### Tier 3: Implementation Specification (L9-L11)

| Activity | Project Lead | Product Manager | Architect | Developer | QA Lead | DevOps |
|----------|:------------:|:---------------:|:---------:|:---------:|:-------:|:------:|
| SPEC creation | A | I | C | R | I | I |
| TSPEC creation | A | I | I | C | R | I |
| TASKS creation | A | I | C | R | C | I |
| GATE-09 approval | A | I | C | R | C | I |

### Tier 4: Implementation (L12-L14)

| Activity | Project Lead | Product Manager | Architect | Developer | QA Lead | DevOps |
|----------|:------------:|:---------------:|:---------:|:---------:|:-------:|:------:|
| Code implementation | A | I | C | R | I | I |
| Unit testing | A | I | I | R | C | I |
| Integration testing | A | I | I | C | R | I |
| GATE-12 approval | A | I | C | R | R | I |

### Cross-Cutting Activities

| Activity | Project Lead | Product Manager | Architect | Developer | QA Lead | DevOps |
|----------|:------------:|:---------------:|:---------:|:---------:|:-------:|:------:|
| GitHub Issue sync | A | I | I | R | I | C |
| Validator CI setup | A | I | I | C | I | R |
| CHG management | R | C | A | C | C | I |
| Drift monitoring | A | I | I | I | C | R |
| Sprint planning | A | R | C | I | I | I |

## Validation Rules

1. Each row has exactly one **A** (Accountable)
2. Each row has at least one **R** (Responsible)
3. No row is empty
4. **A** and **R** cannot be the same person for approval activities

---

## Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {DATE} | | Initial matrix |
