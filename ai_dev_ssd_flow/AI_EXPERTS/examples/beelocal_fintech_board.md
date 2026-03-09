# Example: BeeLocal (Fintech & AI) UCR Configuration

When adapting the AI Expert Board to the BeeLocal platform, we tailor the UCR personas to focus on **Cross-Border Remittance (Fintech)** and **Multi-Agent Orchestration (AI)** domains.

## UCR Usage for BeeLocal

### Quick Start

```bash
# BRD Review (9 personas)
cat AI_EXPERTS/UCR_PROMPT_BRD.md docs/01_BRD/BRD-01_platform_architecture/*.md | claude -p > BRD-01_PERSONA_REVIEW.md

# PRD Review (9 personas)
cat AI_EXPERTS/UCR_PROMPT_PRD.md docs/02_PRD/PRD-*.md | claude -p > PRD_PERSONA_REVIEW.md

# ADR Review (7 personas)
cat AI_EXPERTS/UCR_PROMPT_ADR.md docs/05_ADR/ADR-*.md | claude -p > ADR_PERSONA_REVIEW.md
```

---

## Domain-Specific Persona Focus

### 🏛️ Architect (Integration & Scalability)
- **Focus**: Multi-cloud failover (GCP primary), gRPC/REST boundary efficiency, event-bus payload limits, database sharding for high-TPS transaction ledgers
- **BeeLocal Specifics**: Bridge/Noah custody integration, Asterium FX rate caching, multi-AZ deployment

### ⚖️ Auditor (Compliance & Risk)
- **Focus**: KYC/KYB bounds, AML velocity limits, SOC2/PCI-DSS, immutable audit trails
- **BeeLocal Specifics**: OFAC screening, SAR workflow automation, PCI-DSS for Nuvei card integration

### 🧠 Tech Lead (AI Multi-Agent Systems)
- **Focus**: Claude SDK orchestration, prompt injection vulnerabilities, agent state loops, parallel tool calling, inference cost optimization
- **BeeLocal Specifics**: Claude Opus 4.5 orchestration for compliance agents, agent failure recovery

### 👔 Strategist (Value & Economics)
- **Focus**: B2C/B2B onboarding friction, API partner costs (Nuvei vs Bridge), treasury float management, UX conversion
- **BeeLocal Specifics**: 2-3% fee target, $20k float requirement, 50k MAU projections

### 🕵️ Devil's Advocate (Edge-Cases)
- **Focus**: FX rate change mid-flight, gateway timeout after balance deduction but before credit
- **BeeLocal Specifics**: Transaction saga compensation, double-spend prevention, quote TTL expiration

### 🔧 Operator (SRE)
- **Focus**: Distributed tracing across agent network, CI/CD deployment safety, database migration rollback
- **BeeLocal Specifics**: Cloud Run auto-scaling, Pub/Sub retry policies, DLQ monitoring

### 🔗 Integration Lead (Dependencies & Contracts)
- **Focus**: Cross-module dependencies, API contract versioning, data entity ownership
- **BeeLocal Specifics**: Bridge API version pinning, Asterium webhook validation, schema registry for events

### 📈 Product Owner (Business Value)
- **Focus**: MVP scope boundaries, feature-to-goal mapping, scope creep prevention
- **BeeLocal Specifics**: US-to-Uzbekistan corridor focus, diaspora worker persona prioritization

### 📋 Business Analyst (Requirements)
- **Focus**: Requirements completeness, stakeholder coverage, acceptance criteria precision
- **BeeLocal Specifics**: Regulatory stakeholder requirements, partner contract constraints

---

## Verification Protocol for BeeLocal BRD

When reviewing BeeLocal BRD documents, the verification protocol must include:

1. **Section 18 (Appendices)** - Technology conditions, retry patterns (RETRY-TX, RETRY-WEBHOOK, RETRY-TREASURY)
2. **Section 7 (Quality Attributes)** - Auth0 security, HashiCorp Vault secrets, observability
3. **Section 10 (Risk Analysis)** - Partner backup strategies (UZNEX for Asterium)
4. **Section 5.6** - Comprehensive retry patterns with DLQ

---

## Sample UCR Output

After running UCR on BRD-01:

| Finding | Priority | Verified Location |
|---------|----------|-------------------|
| Circuit breaker pattern | ✓ Present | Section 10.2.1, Section 5.6 |
| Retry patterns | ✓ Present | Section 5.6 (RETRY-TX, RETRY-WEBHOOK) |
| SAR human review | P0 Missing | Section 6 - needs explicit mandate |
| PCI-DSS scope | P0 Missing | Section 7.6 - needs SAQ-A specification |
| Auth0 session controls | P0 Missing | Section 7.2 - needs timeout/concurrent limits |

---

## Running Full Board Review

For comprehensive BeeLocal review:

```bash
# Create combined input
cat AI_EXPERTS/UCR_PROMPT_BRD.md > /tmp/beelocal_review.md
echo "" >> /tmp/beelocal_review.md
cat docs/01_BRD/BRD-01_platform_architecture/*.md >> /tmp/beelocal_review.md

# Run UCR
claude -p < /tmp/beelocal_review.md > docs/01_BRD/BRD-01_platform_architecture/BRD-01_UCR_REVIEW.md
```
