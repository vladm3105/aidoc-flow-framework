# Project Management Skill Examples

This directory contains reference examples showing how to apply the project-mgnt skill to real projects.

## Trading System Example

The trading system example demonstrates the complete MVP/MMP/MMR planning methodology applied to a multi-strategy options trading system.

### Context

**Project**: Multi-strategy options trading system
**Requirements**: 11 BRD documents with 317 total requirements
- BRD-000: Implementation Plan (metadata)
- BRD-001: Foundation & Overview (15 FR, 8 NFR)
- BRD-002: Core Strategy Logic (18 FR, 12 NFR)
- BRD-003: Market Analysis & Entry (20 FR, 10 NFR)
- BRD-004: Risk Management & Controls (26 FR, 15 NFR)
- BRD-005: Position Management (23 FR, 12 NFR)
- BRD-007: Technical Infrastructure (26 FR, 10 NFR)
- BRD-008: Strategy Playbooks (27 FR, 9 NFR)
- BRD-009: Broker Integration (26 FR, 25 NFR) - **CRITICAL PREREQUISITE**
- BRD-010: Foundational Monitoring (8 FR, 4 NFR)
- BRD-011: Comprehensive Observability (18 FR, 9 NFR)

**Team**: 5-6 FTE (2 backend, 1 frontend, 1 QA, 1 DevOps, 1 PM)
**Constraints**: Must start with paper trading before live trading
**Timeline**: Target 27 weeks total

### Analysis Results

**Atomic Groups Identified**: 13 groups across 3 stages

**Stage Assignment**:
- **MVP** (4 groups, 8 weeks): Paper trading validation
  - Priority 1: Broker Integration (BRD-009) - 4 weeks
  - Priority 2: Basic Monitoring (BRD-010 partial) - 1 week (parallel with P1)
  - Priority 3: Greeks Calculator (BRD-007 subset) - 2 weeks
  - Priority 4: Simple State Machine (BRD-002 simplified) - 1 week

- **MMP** (4 groups, 10 weeks): Single strategy live trading
  - Priority 5: Risk Validation Framework (BRD-004) - 3 weeks
  - Priority 6: ML Regime Classification (BRD-003 partial) - 3 weeks (parallel with P5)
  - Priority 7: Strike Selection + Enforcement (BRD-003 + BRD-004) - 2 weeks
  - Priority 8: Iron Condor Playbook (BRD-008 IC only) - 2 weeks

- **MMR** (5 groups, 9 weeks): Multi-strategy + advanced features
  - MMR-1 (4 weeks): Additional Strategies
    - Priority 9: CSP + Covered Calls (BRD-008) - 2 weeks
    - Priority 10: Position Management & Recovery (BRD-005) - 2 weeks
  - MMR-2 (3 weeks): Advanced Observability
    - Priority 11: Portfolio Delta Hedging (BRD-004 hedging) - 1 week
    - Priority 12: Comprehensive Dashboards (BRD-011) - 2 weeks
  - MMR-3 (2 weeks): Advanced Features
    - Priority 13: Volatility Skew Optimization (BRD-005 skew) - 2 weeks

### Key Decisions

**MVP Scope Rationale**:
- Minimal: Only broker connection, basic monitoring, core calculations, simple workflow
- Goal: Validate paper trading works end-to-end
- Deferred: Risk enforcement, ML models, multiple strategies (all MMP+)
- Critical Path: BRD-009 (Broker Integration) blocks everything

**MMP Scope Rationale**:
- Risk-complete: Full risk validation and enforcement before live trading
- Single strategy: Iron Condor only (most common, well-understood)
- Production-ready: All quality gates, automated testing, monitoring

**MMR Progression**:
- MMR-1: Expand strategy types (CSP, CC) for diversification
- MMR-2: Enhanced observability for scale management
- MMR-3: Optimization features for alpha generation

**Parallelization Strategy**:
- MVP: Groups 1-2 parallel (broker + monitoring, different subsystems)
- MMP: Groups 5-6 parallel (risk validation + ML models, different teams)
- MMR-1: Groups 9-10 parallel (independent strategies)
- MMR-2: Groups 11-12 parallel (hedging + dashboards, different focus)

### Version History

**Version 1.0** (Initial Plan):
- Created from 11 BRD documents
- 13 atomic groups defined
- All groups marked PLANNED
- Timeline: 27 weeks from project start
- File: `trading_system_v1.md` (example placeholder)

**Version 2.0** (Updated after BRD-004 changes):
- Context: MVP completed (4 weeks), MMP Group 5 in progress
- BRD Change: BRD-004 added 5 new risk requirements (REQ-041 to REQ-045)
- Impact:
  - Groups 1-4 (MVP): COMPLETED, preserved unchanged
  - Group 5 (Risk Validation): IN_PROGRESS, absorbed REQ-041, REQ-042
  - Groups 6-8: PLANNED, unchanged
  - NEW Group 14: Created in MMR-3 for REQ-043, REQ-044, REQ-045
- Timeline Impact: +2 weeks for new Group 14
- File: `trading_system_v2.md` (example placeholder)

### Lessons from This Example

1. **Critical Path Identification**: BRD-009 was correctly identified as blocking prerequisite
2. **MVP Minimalism**: Resisted temptation to include risk enforcement in MVP
3. **Stage-Appropriate Quality**: MVP focused on validation, MMP on production-readiness
4. **Preserving Progress**: Version 2.0 kept MVP work immutable despite BRD changes
5. **Flexible MMR**: New requirements fit into MMR-3 without disrupting MMP timeline

### How to Use This Example

1. **Study the analysis**: See how 11 BRDs were grouped into 13 atomic units
2. **Understand the rationale**: Note why certain features went to MVP vs MMP vs MMR
3. **Learn from parallelization**: Observe which groups could run simultaneously
4. **Review the update process**: See how v2.0 preserved completed work
5. **Adapt to your project**: Apply same methodology to your requirements

### Creating Your Own Plan

To create a plan for your project:

```
"Use the project-mgnt skill to create an implementation plan for [your project].

Inputs:
- Requirement documents: [your BRD/PRD files]
- Project context: [your domain, team size, constraints]
- Timeline constraint: [if any]

Create PLAN-XXX_[your_project_name].md"
```

The skill will analyze your requirements and create a customized plan following the same methodology demonstrated in this trading system example.

---

## Other Examples (Future)

This directory can be expanded with examples from other domains:
- Web application (e-commerce site)
- API service (REST API development)
- Infrastructure project (cloud migration)
- ML/AI system (recommendation engine)

Each example would demonstrate domain-specific adaptations of the core methodology.
