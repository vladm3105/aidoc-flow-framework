# UCX v1.14.2 - Enhanced Skill Extraction

**Release Date**: 2026-03-14

## Overview

This release enhances the skill extraction logic to capture more domain-specific context from skill manifests, significantly improving instruction quality for persona-based reviews. Added **27 extraction patterns** covering all 11 personas.

## Problem Statement

Skill files contain rich domain knowledge, but only a subset was being extracted:

| Category | Section Types | Personas |
|----------|---------------|----------|
| Core | Role, Review Focus, Anti-Patterns | All |
| Business | Business Processes, Stakeholders, Domain Requirements | business_analyst |
| Quality | Review Questions, Analysis Checklist, Quality Framework (5 C's) | business_analyst, auditor |
| Leadership | Core Mission, Prioritization Weights, Score Calculation, Synthesis Process | chairperson |
| Adversarial | Failure Scenarios, Edge Case Framework, Critical Rule | devils_advocate |
| Verification | Verification Areas, Verification Process | fact_checker |
| Integration | Partner Ecosystem, Integration Requirements, Assessment Template | integration_lead |
| Operations | Operational Requirements, Operational Checklist | operator |
| Product | MVP Definition, Acceptance Criteria Format | product_owner |
| Strategy | Business Model, Competitive Landscape, Financial Projections, Scoring Weight | strategist |
| Technical | Technology Stack, Technical Assessment | tech_lead |

**Impact**: ~60% of skill content was not being used in generated prompts.

## Solution

Enhanced `_load_system_instructions()` in `ucx/prompts/api.py` with 27 extraction patterns:

```python
# Extraction patterns by category
# Core (existing)
- ^## Role\n
- ^## Review Focus\n
- ^##\s+.*Anti-Patterns.*?\n

# Business Domain
- ^##\s+.*Business Process.*?\n
- ^##\s+.*Stakeholders.*?\n
- ^##\s+.*(?:Corridor|Domain).*?Requirements.*?\n

# Quality Framework
- ^##\s+Review Questions.*?\n
- ^##\s+Analysis Checklist.*?\n
- ^##\s+The 5\s*['"]?C['"]?s.*?\n

# Chairperson (Synthesis)
- ^##\s+Core Mission.*?\n
- ^##\s+.*Prioritization.*?Weights.*?\n
- ^##\s+Score Calculation.*?\n
- ^##\s+Synthesis Process.*?\n
- ^##\s+Output Requirements.*?\n
- ^##\s+.*CRITICAL.*?\n

# Devil's Advocate
- ^##\s+.*Failure.*?Scenarios.*?\n
- ^##\s+.*Edge Case.*?\n
- ^##\s+Critical Rule.*?\n

# Fact Checker
- ^##\s+.*Verification.*?Areas.*?\n
- ^##\s+Verification Process.*?\n

# Integration Lead
- ^##\s+Partner Ecosystem.*?\n
- ^##\s+Integration.*?(?:Requirements|Checklist).*?\n
- ^##\s+.*Assessment.*?Template.*?\n

# Operator
- ^##\s+Operational Requirements.*?\n
- ^##\s+Operational Checklist.*?\n

# Product Owner
- ^##\s+.*MVP.*?Definition.*?\n
- ^##\s+Acceptance Criteria.*?\n

# Strategist
- ^##\s+.*Business Model.*?\n
- ^##\s+Competitive Landscape.*?\n
- ^##\s+Financial Projections.*?\n
- ^##\s+Scoring Weight.*?\n

# Tech Lead
- ^##\s+Technology Stack.*?\n
- ^##\s+Technical Assessment.*?\n
```

## Before/After Comparison

### All Personas - Instruction Token Improvements

| Persona | Before | After | Improvement | Final Ratio |
|---------|--------|-------|-------------|-------------|
| business_analyst | 372 | 906 | +143% | 4.9% |
| chairperson | 318 | 1,945 | +512% | 5.6% |
| devils_advocate | 398 | 1,133 | +185% | 7.8% |
| fact_checker | 423 | 855 | +102% | 2.6% |
| integration_lead | 436 | 991 | +127% | 8.0% |
| operator | 436 | 812 | +86% | 8.2% |
| product_owner | 324 | 631 | +95% | 3.4% |
| strategist | 316 | 745 | +136% | 5.4% |
| tech_lead | 538 | 851 | +58% | 6.9% |

**Target ratio**: 5-10% instruction tokens

### Example: Business Analyst

**Before (v1.14.1)**:
```
**Role**: Business Analyst responsible for BeeLocal...
**Review Focus**: (5 bullet points)
**Anti-Patterns to Flag**: (3 patterns)
```

**After (v1.14.2)**:
```
**Role**: Business Analyst responsible for BeeLocal...
**Review Focus**: (5 bullet points)
**Anti-Patterns to Flag**: (3 patterns)
**Business Processes**: (6-step remittance flow + stakeholder table)
**Review Questions**: (5 questions)
**Analysis Checklist**: (7 checklist items)
**Quality Framework (5 C's)**: (Clear, Complete, Consistent, Correct, Confirmable)
```

### Example: Chairperson (Largest Improvement)

**Before**: 318 tokens (1.0% ratio)
**After**: 1,945 tokens (5.6% ratio) - **+512% improvement**

Extracted sections:
- Core Mission (synthesis goal)
- Prioritization Weights (severity/priority rules)
- Score Calculation (formula and rules)
- Synthesis Process (step-by-step)
- Output Requirements (format specifications)
- CRITICAL REQUIREMENTS (manifest requirements)

## Files Changed

| File | Changes |
|------|---------|
| `ucx/prompts/api.py` | Added 27 section extraction patterns in `_load_system_instructions()` (~lines 833-976) |

## Skill File Conventions

To maximize extraction, skill files should use these section headers:

| Category | Header Pattern | Example Content |
|----------|----------------|-----------------|
| **Core** | | |
| Role | `## Role` | Persona responsibility statement |
| Review Focus | `## Review Focus` | Key areas to evaluate |
| Anti-Patterns | `## ... Anti-Patterns...` | Patterns to flag |
| **Business Domain** | | |
| Business Processes | `## ... Business Process...` | Domain workflows |
| Stakeholders | `## ... Stakeholders...` | Key actors |
| Domain Requirements | `## ... Corridor/Domain ... Requirements...` | Domain constraints |
| **Quality Framework** | | |
| Review Questions | `## Review Questions` | Actionable prompts |
| Analysis Checklist | `## Analysis Checklist` | Verification items |
| Quality Framework | `## The 5 'C's...` | Quality criteria |
| **Chairperson** | | |
| Core Mission | `## Core Mission` | Synthesis goal |
| Prioritization Weights | `## ... Prioritization ... Weights...` | Severity rules |
| Score Calculation | `## Score Calculation` | Scoring formula |
| Synthesis Process | `## Synthesis Process` | Step-by-step process |
| Output Requirements | `## Output Requirements` | Format specs |
| CRITICAL | `## ... CRITICAL...` | Manifest requirements |
| **Devil's Advocate** | | |
| Failure Scenarios | `## ... Failure ... Scenarios...` | Domain failures |
| Edge Case Framework | `## ... Edge Case...` | Boundary conditions |
| Critical Rule | `## Critical Rule` | Essential constraints |
| **Fact Checker** | | |
| Verification Areas | `## ... Verification ... Areas...` | Domain areas |
| Verification Process | `## Verification Process` | Step-by-step process |
| **Integration Lead** | | |
| Partner Ecosystem | `## Partner Ecosystem` | Partner details |
| Integration Requirements | `## Integration ... Requirements/Checklist...` | Integration checklist |
| Assessment Template | `## ... Assessment ... Template...` | Assessment format |
| **Operator** | | |
| Operational Requirements | `## Operational Requirements` | SLIs, DR targets |
| Operational Checklist | `## Operational Checklist` | Deployment checklist |
| **Product Owner** | | |
| MVP Definition | `## ... MVP ... Definition...` | Scope, features |
| Acceptance Criteria | `## Acceptance Criteria...` | Story format |
| **Strategist** | | |
| Business Model | `## ... Business Model...` | Unit economics |
| Competitive Landscape | `## Competitive Landscape` | Competitors |
| Financial Projections | `## Financial Projections` | Key assumptions |
| Scoring Weight | `## Scoring Weight` | Weight per doc type |
| **Tech Lead** | | |
| Technology Stack | `## Technology Stack` | Core technologies |
| Technical Assessment | `## Technical Assessment` | Technical checklist |

## Verification

```bash
# Generate all prompts for BRD-01
cd /opt/data/b-local/b-local-docs
source .envrc
ucx prompt generate brd docs/01_BRD/BRD-01_platform_architecture/

# Check instruction ratios for all personas
for persona in business_analyst chairperson devils_advocate fact_checker integration_lead operator product_owner strategist tech_lead; do
  ratio=$(jq -r '"'"'.tokens | "\(.instructions)/\(.total) = \((.instructions/.total*100)|floor)%"'"'" \
    docs/01_BRD/BRD-01_platform_architecture/.doc_review_memory/prompt_${persona}.meta.json 2>/dev/null)
  echo "$persona: $ratio"
done

# Expected output (all in 3-8% range):
# business_analyst: 906/18633 = 4%
# chairperson: 1945/34551 = 5%
# devils_advocate: 1133/14529 = 7%
# ...
```

## Backward Compatibility

- No breaking changes
- Existing skill files work without modification
- New sections are extracted only if present in skill files
- Prompts with minimal skill files continue to work
- Framework skill files serve as fallback when project-specific skills not found

## References

- [PLAN-005: Prompt Engineering Toolset](plans/PLAN-005_prompt_engineering_toolset.md)
- [CHANGELOG_v1.14.1](CHANGELOG_v1.14.1.md) - Content preprocessing
- [CHANGELOG_v1.14.0](CHANGELOG_v1.14.0.md) - Prompt inspection toolset

---

*UCX v1.14.2 - 2026-03-14*
