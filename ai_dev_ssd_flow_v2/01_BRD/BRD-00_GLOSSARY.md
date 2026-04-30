---
title: "BRD-000 GLOSSARY: Master Business Requirements Terminology"
tags:
  - brd-glossary
  - layer-1-artifact
  - shared-architecture
  - reference-document
custom_fields:
  document_type: reference-glossary
  artifact_type: BRD
  layer: 1
  architecture_approaches: [ai-agent-based, traditional-8layer]
  priority: shared
  development_status: active
  scope: framework-wide
  applies_to: all-brds
---

# BRD-000 GLOSSARY: Master Business Requirements Terminology

## Purpose

This document provides centralized definitions for common business, technical, regulatory, and domain-specific terminology used across all Business Requirements Documents (BRDs) in the AI Dev Flow framework. Individual BRDs reference this glossary and define project-specific terms only in their local Section 15 (Glossary).

## Usage Guidelines

### For BRD Authors

1. **Check this glossary first** before defining any term in individual BRD Section 15
2. **Reference entries** from this glossary instead of duplicating definitions
3. **Add project-specific terms** to individual BRD Section 15 when they don't belong here
4. **Propose additions** to this master glossary when terms are used across 3+ BRDs

### When to Define Terms Here vs. Individual BRD

| Define in BRD-00_GLOSSARY.md | Define in Individual BRD section 17 |
|-------------------------------|-------------------------------------|
| [PASS] Terms used across 3+ BRDs | [PASS] Project-specific terminology |
| [PASS] Standard BRD framework terms (FR, QA, BO) | [PASS] Unique partner names |
| [PASS] Common business terms (KPI, ROI, stakeholder) | [PASS] Project-specific acronyms |
| [PASS] Standard abbreviations | [PASS] Domain concepts unique to ONE project |
| [PASS] Industry-standard regulatory terms | [PASS] Custom workflow terminology |

### Maintenance

- **Document Owner**: SDD Framework Team
- **Maintained By**: Business Analyst Team
- **Review Frequency**: Quarterly or with framework updates
- **Addition Threshold**: Term appears in 3+ BRDs or expected to

---

## 1. Business Terms

Common business terminology used across multiple BRDs.

| Term | Definition | Common Usage Context |
|------|------------|---------------------|
| Acceptance Criteria | Conditions that must be met for deliverables to be accepted by stakeholders | Section 11 of BRDs, validation checkpoints |
| Business Objective | Specific, measurable goal aligned with organizational strategic priorities | Section 4 of BRDs, strategic alignment |
| Business Process | Sequence of activities performed to achieve a business outcome | Project scope, Section 5 |
| Deliverable | Tangible or intangible output produced as part of project execution | Project scope, milestones |
| KPI | Key Performance Indicator - measurable value demonstrating effectiveness toward achieving objectives | Success metrics, Section 4 |
| Milestone | Significant point in project timeline marking completion of major phase | Project timeline, appendix |
| ROI | Return on Investment - measure of profitability relative to cost | Cost-benefit, Section 4 |
| Stakeholder | Person or group with interest in or influence over project outcome | Stakeholder analysis, Section 6 |
| Success Metric | Quantifiable measure used to evaluate achievement of objectives | Acceptance criteria, Section 11 |
| Transaction | Single business operation or exchange of value | Core business model, process flows |
| Workflow | Sequence of steps to complete a business process | Project scope, Section 5 |

---

## 2. Technical Terms

Common technical terminology explained for business stakeholders.

| Term | Definition | Common Usage Context |
|------|------------|---------------------|
| API | Application Programming Interface - method for systems to communicate and exchange data | Partner integrations, Section 7 FRs |
| Integration | Connection between two or more systems to share data and functionality | Partner ecosystems, external systems |
| MCP | Model Context Protocol - standard protocol enabling AI assistants to connect with external data sources and tools | AI agent integrations, tool connectivity FRs |
| RAG | Retrieval-Augmented Generation - technique combining information retrieval with LLM generation for contextual responses | AI/ML features, knowledge base FRs |
| SLA | Service Level Agreement - commitment between service provider and client defining service expectations | Quality expectations, Section 9 |
| Webhook | Automated notification sent from one system to another when specific events occur | Status updates, real-time integrations |

---

## 3. Domain-Specific Terms

Industry/domain terminology requiring definition for cross-domain understanding.

| Term | Definition | Domain | Common Usage Context |
|------|------------|--------|---------------------|
| AML | Anti-Money Laundering - regulations and procedures preventing illicit financial activity | FinTech/Compliance | Transaction monitoring FRs, Section 7 |
| Identity Verification | Verification of user or business identity required by regulations | Compliance | User onboarding, Section 7 FRs |
| NAV | Net Asset Value - total value of assets minus liabilities, typically per share/unit | Financial Services | Portfolio valuation, fund accounting BRDs |
| Remittance | Transfer of money by foreign worker to individual in home country | Financial Services | Cross-border payment BRDs |

---

## 4. Acronyms

Standard abbreviations used across BRD framework.

| Acronym | Full Form | Category |
|---------|-----------|----------|
| AC | Acceptance Criteria | BRD Framework |
| ADR | Architecture Decision Record | SDD Framework |
| ATDD | Acceptance Test-Driven Development | Testing |
| AML | Anti-Money Laundering | Compliance |
| API | Application Programming Interface | Technical |
| BA | Business Analyst | Role |
| BDD | Behavior-Driven Development | SDD Framework |
| BO | Business Objective | BRD Framework |
| BRD | Business Requirements Document | SDD Framework |
| EARS | Easy Approach to Requirements Syntax | SDD Framework |
| FR | Functional Requirement | BRD Framework |
| KPI | Key Performance Indicator | Business |
| KYC | Know Your Customer (identity verification) | Compliance |
| IPLAN | Implementation Plan (deprecated) | SDD Framework |
| MCP | Model Context Protocol | Technical |
| MVP | Minimum Viable Product | Business |
| NAV | Net Asset Value | Financial |
| QA | Quality Attribute | BRD Framework |
| PRD | Product Requirements Document | SDD Framework |
| RAG | Retrieval-Augmented Generation | Technical |
| REQ | Atomic Requirement | SDD Framework |
| ROI | Return on Investment | Business |
| SLA | Service Level Agreement | Technical |
| SME | Subject Matter Expert | Role |
| SPEC | Technical Specification | SDD Framework |
| SYS | System Requirements | SDD Framework |
| TASKS | AI Implementation Guide (code-generation bridge) | SDD Framework |
| TDD | Test-Driven Development | Testing |
| TSPEC | Test Specification | SDD Framework |
| UAT | User Acceptance Testing | Testing |

### 4.1 Requirement Type Clarification (FR vs EARS vs REQ)

These three requirement types serve different purposes in the SDD workflow. Understanding when to use each prevents confusion during documentation:

| Type | Layer | Full Name | Purpose | Format Example |
|------|-------|-----------|---------|----------------|
| **FR** | L1 (BRD) | Functional Requirement | Business-level capability statement from stakeholder perspective | "The system shall allow users to reset their password via email." |
| **EARS** | L3 | Engineering Requirement (WHEN-THE-SHALL-WITHIN format) | Structured technical requirement with conditions and constraints | "WHEN a user requests password reset, THE system SHALL send a reset link WITHIN 30 seconds." |
| **REQ** | L7 | Atomic Requirement | Implementation-ready requirement decomposed for development | "REQ.07.01.xxxx: Implement password reset endpoint with rate limiting (max 3 attempts/hour)." |

**Workflow Progression**:
1. **FR** (BRD): Capture stakeholder intent in business language
2. **EARS** (Layer 3): Add engineering precision with conditions and time constraints
3. **REQ** (Layer 7): Decompose into atomic, testable, implementable units

**Common Confusion**:
- FRs are NOT the same as REQs - FRs are higher-level business statements
- EARS is NOT a synonym for requirements - EARS is a specific format for engineering requirements
- REQs always trace back to EARS which trace back to FRs, forming the traceability chain

---

## 5. Cross-References

References to related BRDs and framework documents.

| Term/Concept | Referenced Document | Relationship |
|--------------|---------------------|--------------|
| BRD Template | ai_dev_ssd_flow/01_BRD/BRD-TEMPLATE.yaml | Single source of truth for BRD structure, authoring guidance, and ID standards |
| SDD Guide | ai_dev_ssd_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md | Overall framework methodology |

---

## 6. External Standards

Regulatory, industry, and technical standards referenced in BRDs.

| Standard | Organization | Relevance | Common Application |
|----------|--------------|-----------|-------------------|
| PCI-DSS | Payment Card Industry Security Standards Council | Payment security compliance | Quality expectations (Section 9), security |
| GDPR | European Union | Data privacy regulation | Quality expectations (Section 9), security |
| CCPA | State of California | Consumer privacy rights | Quality expectations (Section 9), security |
| SOC 2 | AICPA | Security and availability controls | Quality expectations (Section 9), audit |
| ISO 27001 | International Organization for Standardization | Information security management | Quality expectations (Section 9), security |
| WCAG 2.1 | W3C | Web accessibility standards | Quality expectations (Section 9) |
| FinCEN | US Department of Treasury | AML/CFT compliance | Functional requirements (Section 7) |
| OFAC | US Department of Treasury Office of Foreign Assets Control | Sanctions screening | Functional requirements (Section 7) |

---

## Document Control

| Item | Details |
|------|---------|
| **Document ID** | BRD-00_GLOSSARY |
| **Document Version** | 1.2 |
| **Creation Date** | 2025-11-26T00:00:00 |
| **Document Owner** | SDD Framework Team |
| **Maintained By** | Business Analyst Team |
| **Review Frequency** | Quarterly or with framework updates |
| **Last Reviewed** | 2026-02-06T00:00:00 |

### Revision History

| Version | Date | Author | Changes Made | Approver |
|---------|------|--------|--------------|----------|
| 1.2 | 2026-02-06T00:00:00 | Claude | Added FR vs EARS vs REQ clarification subsection 4.1 | Framework Lead |
| 1.1 | 2025-12-30T00:00:00 | Claude | Added MCP, NAV, RAG terms per audit recommendation | Framework Lead |
| 1.0 | 2025-11-26T00:00:00 | Claude | Initial master glossary creation | Framework Lead |

---

## Contributing to This Glossary

### Addition Criteria

Add terms to this glossary when they meet ANY of these criteria:

1. **Frequency**: Term appears in 3+ existing BRDs
2. **Framework Standard**: Term is part of BRD framework methodology
3. **Industry Standard**: Term is widely recognized in relevant industry
4. **Cross-Domain**: Term bridges multiple business domains
5. **Regulatory**: Term is defined by regulatory or compliance standards

### Proposal Process

1. **Identify candidate term** in individual BRD Section 15
2. **Check usage frequency** across existing BRDs
3. **Submit proposal** to Business Analyst Team with:
   - Term definition
   - Usage context
   - BRDs where term appears
   - Justification for inclusion
4. **Review and approval** by Framework Lead
5. **Add to glossary** and update individual BRDs to reference master

### Update Process

- **Minor updates** (corrections, clarifications): Business Analyst Team approval
- **Major updates** (new subsections, structural changes): Framework Lead approval
- **Version increment**: Minor (0.1) for corrections, Major (1.0) for structural changes
