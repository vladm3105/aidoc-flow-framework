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

This document provides centralized definitions for common business, technical, regulatory, and domain-specific terminology used across all Business Requirements Documents (BRDs) in the AI Dev Flow framework. Individual BRDs reference this glossary and define project-specific terms only in their local section 17 (Glossary).

## Usage Guidelines

### For BRD Authors

1. **Check this glossary first** before defining any term in individual BRD section 17
2. **Reference entries** from this glossary instead of duplicating definitions
3. **Add project-specific terms** to individual BRD section 17 when they don't belong here
4. **Propose additions** to this master glossary when terms are used across 3+ BRDs

### When to Define Terms Here vs. Individual BRD

| Define in BRD-00_GLOSSARY.md | Define in Individual BRD section 17 |
|-------------------------------|-------------------------------------|
| ✅ Terms used across 3+ BRDs | ✅ Project-specific terminology |
| ✅ Standard BRD framework terms (FR, QA, BO) | ✅ Unique partner names |
| ✅ Common business terms (KPI, ROI, stakeholder) | ✅ Project-specific acronyms |
| ✅ Standard abbreviations | ✅ Domain concepts unique to ONE project |
| ✅ Industry-standard regulatory terms | ✅ Custom workflow terminology |

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
| Acceptance Criteria | Conditions that must be met for deliverables to be accepted by stakeholders | section 9 of BRDs, validation checkpoints |
| Business Objective | Specific, measurable goal aligned with organizational strategic priorities | section 2.4 of BRDs, strategic alignment |
| Business Process | Sequence of activities performed to achieve a business outcome | Process scope, section 5 |
| Deliverable | Tangible or intangible output produced as part of project execution | Project scope, milestones |
| KPI | Key Performance Indicator - measurable value demonstrating effectiveness toward achieving objectives | Success metrics, section 9.7 |
| Milestone | Significant point in project timeline marking completion of major phase | Project timeline, section 15 |
| ROI | Return on Investment - measure of profitability relative to cost | Cost-benefit analysis, section 14 |
| Stakeholder | Person or group with interest in or influence over project outcome | Stakeholder analysis, section 4 |
| Success Metric | Quantifiable measure used to evaluate achievement of objectives | Acceptance criteria, section 9 |
| Transaction | Single business operation or exchange of value | Core business model, process flows |
| Workflow | Sequence of steps to complete a business process | Process scope definition, section 5 |

---

## 2. Technical Terms

Common technical terminology explained for business stakeholders.

| Term | Definition | Common Usage Context |
|------|------------|---------------------|
| API | Application Programming Interface - method for systems to communicate and exchange data | Partner integrations, section 6 FRs |
| Integration | Connection between two or more systems to share data and functionality | Partner ecosystems, external systems |
| MCP | Model Context Protocol - standard protocol enabling AI assistants to connect with external data sources and tools | AI agent integrations, tool connectivity FRs |
| RAG | Retrieval-Augmented Generation - technique combining information retrieval with LLM generation for contextual responses | AI/ML features, knowledge base FRs |
| SLA | Service Level Agreement - commitment between service provider and client defining service expectations | Quality Attributes section 7.5, performance requirements |
| Webhook | Automated notification sent from one system to another when specific events occur | Status updates, real-time integrations |

---

## 3. Domain-Specific Terms

Industry/domain terminology requiring definition for cross-domain understanding.

| Term | Definition | Domain | Common Usage Context |
|------|------------|--------|---------------------|
| AML | Anti-Money Laundering - regulations and procedures preventing illicit financial activity | FinTech/Compliance | Transaction monitoring FRs, section 6 |
| Identity Verification | Verification of user or business identity required by regulations | Compliance | User onboarding, section 6 FRs |
| NAV | Net Asset Value - total value of assets minus liabilities, typically per share/unit | Financial Services | Portfolio valuation, fund accounting BRDs |
| Remittance | Transfer of money by foreign worker to individual in home country | Financial Services | Cross-border payment BRDs |

---

## 4. Acronyms

Standard abbreviations used across BRD framework.

| Acronym | Full Form | Category |
|---------|-----------|----------|
| AC | Acceptance Criteria | BRD Framework |
| ADR | Architecture Decision Record | SDD Framework |
| AML | Anti-Money Laundering | Compliance |
| API | Application Programming Interface | Technical |
| BA | Business Analyst | Role |
| BDD | Behavior-Driven Development | SDD Framework |
| BO | Business Objective | BRD Framework |
| BRD | Business Requirements Document | SDD Framework |
| EARS | Event-Action-Response-State (Engineering Requirements) | SDD Framework |
| FR | Functional Requirement | BRD Framework |
| KPI | Key Performance Indicator | Business |
| Verification | Identity verification (individual or business) | Compliance |
| MCP | Model Context Protocol | Technical |
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
| UAT | User Acceptance Testing | Testing |

---

## 5. Cross-References

References to related BRDs and framework documents.

| Term/Concept | Referenced Document | section | Relationship |
|--------------|---------------------|---------|--------------|
| BRD Template | ai_dev_flow/01_BRD/BRD-MVP-TEMPLATE.md | All | Reference template for creating BRDs (full template archived) |
| BRD Creation Rules | ai_dev_flow/01_BRD/BRD_CREATION_RULES.md | N/A | Authoring guidelines and best practices |
| BRD Validation Rules | ai_dev_flow/01_BRD/BRD_VALIDATION_RULES.md | N/A | Quality assurance and validation checks |
| FR Examples Guide | ai_dev_flow/01_BRD/FR_EXAMPLES_GUIDE.md | N/A | Functional requirement writing examples |
| SDD Guide | ai_dev_flow/SPEC_DRIVEN_DEVELOPMENT_GUIDE.md | N/A | Overall framework methodology |

---

## 6. External Standards

Regulatory, industry, and technical standards referenced in BRDs.

| Standard | Organization | Relevance | Common Application |
|----------|--------------|-----------|-------------------|
| PCI-DSS | Payment Card Industry security Standards Council | Payment security compliance | Payment processing BRDs, Quality Attributes section 7.3 |
| GDPR | European Union | Data privacy regulation | Data handling, QA section 7.3 |
| CCPA | State of California | Consumer privacy rights | Data handling, QA section 7.3 |
| SOC 2 | AICPA | security and availability controls | security QAs, audit requirements |
| ISO 27001 | International Organization for Standardization | Information security management | security QAs, section 7.3 |
| WCAG 2.1 | W3C | Web accessibility standards | Accessibility QAs, section 7.8 |
| FinCEN | US Department of Treasury | AML/CFT compliance | Financial services BRDs, regulatory requirements |
| OFAC | US Department of Treasury Office of Foreign Assets Control | Sanctions screening | Cross-border transactions, compliance FRs |

---

## Document Control

| Item | Details |
|------|---------|
| **Document ID** | BRD-00_GLOSSARY |
| **Document Version** | 1.1 |
| **Creation Date** | 2025-11-26 |
| **Document Owner** | SDD Framework Team |
| **Maintained By** | Business Analyst Team |
| **Review Frequency** | Quarterly or with framework updates |
| **Last Reviewed** | 2025-12-30 |

### Revision History

| Version | Date | Author | Changes Made | Approver |
|---------|------|--------|--------------|----------|
| 1.1 | 2025-12-30 | Claude | Added MCP, NAV, RAG terms per audit recommendation | Framework Lead |
| 1.0 | 2025-11-26 | Claude | Initial master glossary creation | Framework Lead |

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

1. **Identify candidate term** in individual BRD section 17
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
