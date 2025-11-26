# Functional Requirements (FR) Examples Guide

**Purpose**: Concrete examples of properly structured business-level Functional Requirements, demonstrating what achieves PRD-Ready Score ≥90/100.

**Last Updated**: 2025-11-26
**Status**: Reference Guide
**Audience**: BRD Authors, Business Analysts, Product Managers

---

## Table of Contents

1. [Example 1: Simple FR (Complexity 2/5)](#example-1-simple-fr-complexity-25)
2. [Example 2: Complex FR (Complexity 4/5)](#example-2-complex-fr-complexity-45)
3. [Example 3: AI/ML FR (Complexity 3/5)](#example-3-aiml-fr-complexity-35)
4. [Example 4: Before/After Refactoring](#example-4-beforeafter-refactoring)
5. [FR 4-Subsection Detailed Guidance](#fr-4-subsection-detailed-guidance)
   - [Subsection 1: Business Capability](#subsection-1-business-capability-required)
   - [Subsection 2: Business Requirements](#subsection-2-business-requirements-required)
   - [Subsection 3: Business Rules](#subsection-3-business-rules-required)
   - [Subsection 4: Business Acceptance Criteria](#subsection-4-business-acceptance-criteria-required)
   - [Subsection 5: Related Requirements](#subsection-5-related-requirements-required)
   - [Subsection 6: Complexity Rating](#subsection-6-complexity-rating-required)
   - [Subsection 7: Customer-Facing Language](#subsection-7-customer-facing-language-optional)

---

## Example 1: Simple FR (Complexity 2/5)

**FR-001: Recipient Selection and Management**

**Business Capability**: System must enable customers to select existing recipients or add new recipients for remittance transactions.

**Business Requirements**:
- Support recipient reuse from saved recipient list (managed per BRD-011 Recipient Management)
- Enable first-time recipient creation during transaction initiation
- Validate recipient information meets Paynet delivery network requirements
- Support multiple payout methods (bank accounts, mobile wallets, Paynet cards)
- Accept recipient names in both Cyrillic and Latin scripts (Uzbek naming conventions)
- Enforce Uzbekistan phone number format (+998 country code)

**Business Rules**:
- Recipients validated successfully in first transaction become saved for future reuse
- Recipient information must match Paynet network requirements for successful delivery
- Invalid recipient data must be rejected before transaction initiation to prevent delivery failures

**Business Acceptance Criteria**:
- Recipient selection process completes within business-acceptable timeframe (<1 second for list retrieval)
- New recipient creation completes efficiently (median ≤30 seconds)
- Validation errors communicated immediately to prevent failed transactions
- First-time recipients automatically saved after successful delivery (reduces friction for repeat sends)

**Related Requirements**:
- Partner Integration: BRD-011 (Recipient Management)
- Delivery Network: BRD-002 (Paynet Partner Integration)

**Complexity**: 2/5 (Standard customer data management; requires recipient validation API integration from BRD-011)

---

## Example 2: Complex FR (Complexity 4/5)

**FR-002A: Multi-Region Wallet Funding Support**

**Business Capability**: System must support remittances funded from multiple wallet funding sources across US and EU markets.

**Business Requirements**:
- Accept wallet funds from Bridge custody provider (US ACH, card, EU SEPA deposits per BRD-008)
- Support USD-denominated wallet balance from multiple funding sources
- Enable remittances from either US-sourced (ACH/card) or EU-sourced (SEPA) wallet funding
- Present unified wallet balance regardless of original funding source
- Maintain fee transparency across all funding paths

**Multi-Region Funding Sources**:
| Region | Funding Methods | Settlement Time to Remittance-Ready | Managed By |
|--------|----------------|-------------------------------------|------------|
| US | ACH bank transfer | 1-3 business days | BRD-008 (Bridge custody) |
| US | Debit/credit card | Instant | BRD-008 (Bridge custody) |
| EU | EUR SEPA transfer | <10 minutes after EUR receipt | BRD-008 (Bridge custody) |

**Fee Structure - EU Customer Example**:
For €200 EUR deposit → $200 USD remittance to Uzbekistan:
- EUR→USD conversion: Included in Bridge custody fee (waived initially per BRD-008)
- BeeLocal service fee: $3.00 flat (per FR-002)
- FX spread (USDC→UZS): 1.5-2.0% (per FR-003)
- Total effective cost: ~$6.50 on $200 send (~3.25% all-in cost)

**Business Rules**:
- All remittances execute from single USD wallet balance (Bridge custody)
- EU customers use Bridge SEPA path for EUR deposits with automatic EUR→USD conversion
- US customers use Bridge ACH or card path for direct USD deposits
- Wallet balance displays in USD regardless of original deposit currency
- Remittance execution process identical for US and EU customers

**Business Acceptance Criteria**:
- EU customers can initiate remittance within <10 minutes of EUR clearing (95% of transactions)
- Unified wallet balance displayed across all funding sources (100% consistency)
- Fee transparency maintained for all funding paths (no hidden conversion fees)
- Cross-border funding enables EU market expansion without separate infrastructure

**Related Requirements**:
- Platform: BRD-001 (Platform Architecture), BRD-002 (Partner Ecosystem)
- Partner Integration: BRD-008 (Wallet Funding via Bridge)
- Compliance: BRD-003 (Multi-jurisdiction KYC/AML)

**Complexity**: 4/5 (Dual-region funding architecture; requires custody provider integration with ACH and SEPA paths; unified wallet balance across currency sources; multi-jurisdiction compliance)

---

## Example 3: AI/ML FR (Complexity 3/5)

**FR-004: Pre-Transaction Risk and Compliance Screening**

**Business Capability**: System must perform comprehensive fraud detection and regulatory compliance screening before authorizing remittance transactions.

**Business Requirements**:
- Execute OFAC/PEP sanctions screening for 100% of transactions (sender and recipient)
- Assess fraud risk using ML-based scoring model with automated decision thresholds
- Enforce velocity limits (transaction count and amount per day/week/month) for structuring prevention
- Validate sender geolocation (US-based) and recipient geolocation (Uzbekistan-based)
- Apply Travel Rule compliance for transactions ≥$3,000 (identity disclosure requirements)
- Flag structured transactions (multiple small transactions to evade reporting thresholds)

**Business Rules**:
- **Sanctions Screening**: Auto-decline on OFAC/PEP exact match; queue for manual review on fuzzy match (≥85% similarity)
- **Fraud Risk Scoring** (ML-based):
  - Risk score 0-59: Auto-approve transaction
  - Risk score 60-79: Queue for manual compliance review (target <5% of volume)
  - Risk score 80-100: Auto-decline with SAR consideration
- **Velocity Limits** (Anti-Structuring):
  - L1 KYC: Max 3 transactions/day, $500 daily limit
  - L2 KYC: Max 5 transactions/day, $2,000 daily limit
  - L3 KYC: Max 10 transactions/day, $10,000 daily limit
- **Geolocation Validation**: Sender IP must resolve to US; recipient phone must be Uzbekistan (+998)

**Business Acceptance Criteria**:
- Screening completion time: ≤3 seconds for 95% of transactions (customer experience requirement)
- False positive rate: ≤3% (minimize blocking legitimate customers unnecessarily)
- True positive rate: ≥95% (catch actual fraudulent/sanctioned transactions)
- Manual review queue processing: ≤2 hours during business hours for 90% of cases
- Sanctions list updates: Applied within 24 hours of OFAC publication (regulatory requirement)

**Related Requirements**:
- Platform: BRD-003 (Security & Compliance Framework)
- AI Agent: BRD-022 (Fraud Detection Agent - ML implementation details)
- Compliance: BRD-017 (Compliance Monitoring & SAR Generation)
- KYC: BRD-006 (B2C KYC Onboarding - tiering logic)

**Complexity**: 3/5 (Multiple screening systems integration; ML model inference with business rule thresholds; regulatory compliance across sanctions, AML, and Travel Rule; manual review workflow coordination)

---

## Example 4: Before/After Refactoring

### BEFORE (PRD-Level - Score 65/100)

```markdown
**FR-004: Risk Screening API Integration**

- Call POST /screening/ofac with sender/recipient data
- Receive JSON response with match_score (0-100)
- If match_score >= 85, display warning modal to user
- Store screening result in PostgreSQL screening_results table
- Trigger webhook to compliance team if match detected
- Implement retry logic with exponential backoff (500ms, 1000ms, 2000ms)
```

**Problems**:
- ❌ API endpoint specification (POST /screening/ofac)
- ❌ JSON response format details
- ❌ UI interaction (display warning modal)
- ❌ Database table name (PostgreSQL screening_results)
- ❌ Webhook implementation details
- ❌ Code-level retry logic (exponential backoff values)

### AFTER (Business-Level - Score 100/100)

**FR-004: Pre-Transaction Sanctions Screening**

**Business Capability**: System must screen all transactions against OFAC/PEP sanctions lists before authorization.

**Business Requirements**:
- Execute OFAC/PEP screening for 100% of transactions (sender and recipient)
- Validate against current sanctions lists updated within 24 hours of OFAC publication
- Support fuzzy matching to catch name variations and misspellings
- Provide screening results to compliance team for manual review queue
- Maintain screening audit trail for regulatory examination

**Business Rules**:
- Exact match (100% similarity): Auto-decline transaction immediately
- Fuzzy match (≥85% similarity): Queue for manual compliance review within 2 hours
- Low match (<85% similarity): Auto-approve with screening result logged
- Screening must complete before transaction authorization (blocking operation)

**Business Acceptance Criteria**:
- Screening completion time: ≤3 seconds for 95% of transactions
- False positive rate: ≤3% (minimize blocking legitimate customers)
- Sanctions list staleness: ≤24 hours from OFAC publication
- Audit trail retention: 7 years per FinCEN recordkeeping requirements

**Related Requirements**:
- Platform: BRD-003 (Security & Compliance Framework)
- Compliance: BRD-017 (Compliance Monitoring & SAR Generation)

**Complexity**: 2/5 (Standard sanctions screening integration; requires compliance workflow for manual review queue)

**What Changed**:
- ✅ Removed API specifications → Kept business capability ("screen all transactions")
- ✅ Removed JSON format → Kept business rules (auto-decline, queue for review)
- ✅ Removed UI details → Kept business acceptance criteria (completion time ≤3 seconds)
- ✅ Removed database/webhook → Kept business requirement (audit trail for regulatory examination)
- ✅ Removed retry logic → Kept business SLA (completion time target)
- ✅ Added complexity rating with business rationale
- ✅ Added cross-references to related Platform and Compliance BRDs

---

## FR 4-Subsection Detailed Guidance

This section provides detailed patterns for each FR subsection to achieve PRD-Ready Score ≥90/100.

---

### Subsection 1: Business Capability (Required)

**Purpose**: One-sentence statement defining WHAT the system must enable from a business perspective.

**Pattern**: `System must [enable/support/provide] [business actor] to [business action] [business outcome/context].`

**Format Rules**:
- Single sentence (maximum 30 words)
- Starts with "System must"
- Uses business verbs: enable, support, provide, ensure, maintain
- Excludes technical terms: API, endpoint, database, webhook, payload
- Focuses on business outcome, not implementation mechanism

**Examples by Complexity**:

| Complexity | Business Capability Example |
|------------|----------------------------|
| 1/5 | System must enable customers to view their transaction history for all completed remittances. |
| 2/5 | System must support recipient management including creation, validation, and reuse for future transactions. |
| 3/5 | System must perform comprehensive fraud detection and regulatory compliance screening before authorizing remittance transactions. |
| 4/5 | System must support remittances funded from multiple wallet funding sources across US and EU markets with unified balance presentation. |
| 5/5 | System must orchestrate end-to-end remittance lifecycle across multiple partners with automated failure recovery and regulatory compliance across jurisdictions. |

**Anti-Patterns (Avoid)**:
- ❌ "System must call the fraud detection API endpoint"
- ❌ "System must store transaction data in PostgreSQL"
- ❌ "System must display a modal dialog for confirmation"
- ❌ "System must implement webhook handlers for partner callbacks"

---

### Subsection 2: Business Requirements (Required)

**Purpose**: Bulleted list of 6-8 specific business needs that elaborate the Business Capability.

**Pattern**: Each bullet follows `[Action verb] [business object] [business context/constraint]`

**Format Rules**:
- 6-8 bullets per FR (minimum 4, maximum 10)
- Each bullet is 1-2 sentences maximum
- Uses business action verbs: Accept, Support, Validate, Enable, Enforce, Maintain, Provide
- Includes cross-references to related BRDs using format: `(per BRD-XXX)` or `(managed per BRD-XXX)`
- Excludes implementation details: field names, data types, API parameters

**Example Structure**:
```markdown
**Business Requirements**:
- [Primary capability requirement with BRD cross-reference]
- [Secondary capability requirement]
- [Validation/quality requirement]
- [Support for variations/edge cases]
- [Compliance/regulatory requirement if applicable]
- [Integration requirement with partner BRD reference]
- [Performance/availability business need]
- [Audit/reporting business need]
```

**Example (FR-002: Fee Calculation)**:
```markdown
**Business Requirements**:
- Calculate flat service fee based on transaction amount tiers (per Fee Schedule in Section 10)
- Apply corridor-specific FX spread for USD→UZS conversion (per FR-003)
- Present total cost breakdown before customer confirmation (fee transparency requirement)
- Support fee waiver promotions during initial launch period (per Marketing campaign requirements)
- Maintain fee audit trail for regulatory examination and customer dispute resolution
- Calculate delivery partner fees based on payout method (bank vs mobile wallet vs Paynet card)
```

**Cross-Reference Pattern**:
| Reference Type | Format | Example |
|---------------|--------|---------|
| Platform BRD | `(per BRD-XXX)` | `(per BRD-008)` |
| Feature BRD | `(managed per BRD-XXX)` | `(managed per BRD-011)` |
| Internal Section | `(per Section X)` | `(per Fee Schedule in Section 10)` |
| Related FR | `(per FR-XXX)` | `(per FR-003)` |

---

### Subsection 3: Business Rules (Required)

**Purpose**: Decision logic, thresholds, and conditional behaviors expressed in business terms.

**When to Use Tables vs Bullets**:

| Use Tables When | Use Bullets When |
|-----------------|------------------|
| ≥3 decision variables | Simple if/then rules |
| Tiered thresholds (KYC levels, fee tiers) | Sequential business rules |
| Multi-column decision matrix | Rules with single condition |
| Comparing options (funding methods, payout types) | Rules requiring narrative explanation |

**Table Pattern (Tiered Thresholds)**:
```markdown
**Business Rules**:

| KYC Level | Daily Limit | Per-Transaction Limit | Velocity Limit |
|-----------|-------------|----------------------|----------------|
| L1 (Basic) | $500 | $200 | 3 transactions/day |
| L2 (Enhanced) | $2,000 | $500 | 5 transactions/day |
| L3 (Full) | $10,000 | $2,500 | 10 transactions/day |
```

**Table Pattern (Decision Matrix)**:
```markdown
**Business Rules**:

| Risk Score | Action | SLA | Escalation |
|------------|--------|-----|------------|
| 0-59 | Auto-approve | Immediate | None |
| 60-79 | Manual review | ≤2 hours | Compliance team |
| 80-100 | Auto-decline | Immediate | SAR consideration |
```

**Bullet Pattern (Sequential Rules)**:
```markdown
**Business Rules**:
- Recipients validated successfully in first transaction become saved for future reuse
- Recipient information must match Paynet network requirements for successful delivery
- Invalid recipient data must be rejected before transaction initiation to prevent delivery failures
- Duplicate recipient detection within same customer profile (name + phone number match)
```

**Examples by Business Rule Type**:

| Rule Type | Example |
|-----------|---------|
| Threshold | "Transactions ≥$3,000 require Travel Rule compliance (identity disclosure)" |
| Conditional | "EU customers use SEPA path; US customers use ACH or card path" |
| Validation | "Sender IP must resolve to US; recipient phone must be Uzbekistan (+998)" |
| Sequencing | "Sanctions screening must complete before transaction authorization (blocking operation)" |
| Default | "Wallet balance displays in USD regardless of original deposit currency" |

---

### Subsection 4: Business Acceptance Criteria (Required)

**Purpose**: Measurable success criteria with quantitative thresholds and business justification.

**Pattern**: `[Metric]: [Threshold] ([Percentile/Target]) ([Business Justification])`

**Format Rules**:
- Each criterion has quantitative threshold (number, percentage, time)
- Include percentile or target qualifier (95%, median, 100%)
- Include business justification in parentheses
- 4-6 acceptance criteria per FR
- Focus on business outcomes, not technical metrics

**Quantitative Patterns**:

| Metric Type | Pattern | Example |
|-------------|---------|---------|
| Response Time | `≤[time] for [percentile]% of [operations]` | `≤3 seconds for 95% of transactions` |
| Accuracy | `≤[rate]% [error type] rate` | `≤3% false positive rate` |
| Availability | `[percentage]% [consistency/uptime]` | `100% balance consistency across funding sources` |
| Compliance | `≤[time] from [trigger event]` | `≤24 hours from OFAC publication` |
| Throughput | `[count] [unit] per [time period]` | `10,000 transactions per day capacity` |
| Quality | `≥[percentage]% [quality metric]` | `≥95% true positive rate for fraud detection` |

**Example (FR-004: Risk Screening)**:
```markdown
**Business Acceptance Criteria**:
- Screening completion time: ≤3 seconds for 95% of transactions (customer experience requirement)
- False positive rate: ≤3% (minimize blocking legitimate customers unnecessarily)
- True positive rate: ≥95% (catch actual fraudulent/sanctioned transactions)
- Manual review queue processing: ≤2 hours during business hours for 90% of cases
- Sanctions list updates: Applied within 24 hours of OFAC publication (regulatory requirement)
```

**Justification Phrases**:
| Justification Type | Phrase Pattern |
|-------------------|----------------|
| Customer Experience | `(customer experience requirement)` |
| Regulatory | `(regulatory requirement)`, `(per FinCEN/OFAC mandate)` |
| Operational | `(operational efficiency)`, `(reduce manual processing)` |
| Business | `(reduces friction for repeat sends)`, `(enables market expansion)` |
| Risk | `(minimize false blocks)`, `(prevent delivery failures)` |

---

### Subsection 5: Related Requirements (Required)

**Purpose**: Cross-references to Platform BRDs, Partner Integration BRDs, and other Feature BRDs.

**Format**:
```markdown
**Related Requirements**:
- Platform: BRD-001 (Platform Architecture), BRD-002 (Partner Ecosystem)
- Partner Integration: BRD-008 (Wallet Funding via Bridge), BRD-011 (Recipient Management)
- Compliance: BRD-003 (Security & Compliance Framework), BRD-017 (Compliance Monitoring)
- AI Agent: BRD-022 (Fraud Detection Agent - ML implementation details)
```

**Category Definitions**:
| Category | BRD Range | Purpose |
|----------|-----------|---------|
| Platform | BRD-001 through BRD-005 | Core platform capabilities |
| Partner Integration | BRD-006 through BRD-015 | External partner integrations |
| Compliance | BRD-016 through BRD-020 | Regulatory and compliance |
| AI Agent | BRD-021 through BRD-030 | AI/ML agent capabilities |
| Feature | BRD-031+ | Specific business features |

---

### Subsection 6: Complexity Rating (Required)

**Purpose**: 1-5 scale rating with business-level justification.

**Pattern**: `[Rating]/5 ([Partner chain]; [Regulatory scope]; [Business constraint count])`

**Complexity Factors**:
| Factor | Low (1-2) | Medium (3) | High (4-5) |
|--------|-----------|------------|------------|
| Partner Count | 0-1 partners | 2 partners | 3+ partners |
| Regulatory Scope | Single jurisdiction | Dual jurisdiction | Multi-jurisdiction |
| Business Constraints | 1-2 constraints | 3-4 constraints | 5+ constraints |
| Integration Complexity | Single integration | Chain (A→B) | Multi-chain (A→B→C) |
| Business Rule Count | 1-3 rules | 4-6 rules | 7+ rules |

**Multi-Partner Chain Notation**: Use arrow notation to show partner dependencies.
- Simple: `(BeeLocal→Bridge→Paynet)`
- Complex: `(BeeLocal→Bridge→Paynet; BeeLocal→Compliance→OFAC)`

**Examples**:
```markdown
**Complexity**: 2/5 (Standard customer data management; requires recipient validation API integration from BRD-011)

**Complexity**: 3/5 (Multiple screening systems integration; ML model inference with business rule thresholds; regulatory compliance across sanctions, AML, and Travel Rule; manual review workflow coordination)

**Complexity**: 4/5 (Dual-region funding architecture; requires custody provider integration with ACH and SEPA paths; unified wallet balance across currency sources; multi-jurisdiction compliance)

**Complexity**: 5/5 (End-to-end orchestration: BeeLocal→Bridge→Paynet partner chain; 7 business constraints including regulatory hold periods; multi-jurisdiction compliance US+Uzbekistan; automated retry with business escalation; 12 business rules across 4 decision categories)
```

---

### Subsection 7: Customer-Facing Language [Optional]

**Purpose**: Document customer-visible text, notifications, error messages, and communication templates for customer-facing BRDs. This subsection ensures consistent messaging across all customer touchpoints.

**When Required**: Include this subsection when the FR involves:
- Customer-visible UI text or messages
- Email/SMS/push notifications triggered by the FR
- Error messages displayed to customers
- Terms and conditions language
- Customer support scripts or FAQs

**Cross-Reference**: Full communication templates are documented in **Appendix N: Customer Communication Templates**. This subsection provides FR-specific excerpts.

**Content Categories**:

| Category | Purpose | Example |
|----------|---------|---------|
| **Success Messages** | Confirmation text shown after successful actions | "Your transfer of $[amount] to [recipient] is being processed" |
| **Error Messages** | Customer-friendly explanations of failures | "We couldn't complete your transfer. Your payment method was declined." |
| **Notification Text** | Push/SMS/email notification content | "Your transfer to [recipient] has been delivered successfully" |
| **Help/FAQ Text** | Self-service support content | "Transfers typically arrive within 1-3 business days" |
| **Legal/Disclosure** | Required regulatory or compliance text | "Transfer fees and exchange rates are locked at time of confirmation" |

**Format Pattern**:
```markdown
**Customer-Facing Language**:

**Success Messages**:
| Trigger Event | Message | Channel |
|---------------|---------|---------|
| Transaction initiated | "Your transfer of $[amount] to [recipient] is being processed. Estimated delivery: [date]" | In-app, Email |
| Transaction delivered | "Great news! [recipient] has received your transfer of $[amount] ([local_amount] UZS)" | Push, SMS |

**Error Messages**:
| Error Condition | Customer Message | Support Code |
|-----------------|------------------|--------------|
| Insufficient funds | "Your payment couldn't be completed. Please check your balance and try again." | ERR-001 |
| Recipient validation failed | "We couldn't verify the recipient's information. Please check the details and try again." | ERR-002 |

**Regulatory Disclosures**:
- Pre-transfer disclosure: "You will be charged $[fee]. Exchange rate: 1 USD = [rate] UZS. [recipient] will receive [local_amount] UZS."
- Transfer Rights disclosure: "For questions or complaints about this transfer, contact us at [support] or visit [URL]"
```

**Example (FR-001: Transaction Initiation)**:
```markdown
**Customer-Facing Language**:

**Success Messages**:
| Trigger | Message | Channel |
|---------|---------|---------|
| Quote generated | "Send $[amount] to [recipient]. Fee: $[fee]. [recipient] receives [local_amount] UZS." | In-app |
| Transaction submitted | "Your transfer is on its way! We'll notify you when [recipient] receives the funds." | In-app, Email |

**Error Messages**:
| Condition | Customer Message | Support Code |
|-----------|------------------|--------------|
| Daily limit exceeded | "You've reached your daily transfer limit of $[limit]. Try again tomorrow or contact support to increase your limit." | TXN-LIMIT |
| Recipient country blocked | "We're unable to send transfers to this destination at this time." | TXN-DEST |

**Notification Text**:
- Push (initiation): "Transfer started: $[amount] to [recipient_name]"
- Push (delivered): "✓ Delivered: [recipient_name] received [local_amount] UZS"
- SMS (delivered): "BeeLocal: Your transfer of [local_amount] UZS to [recipient_name] has been delivered."
```

**Language Guidelines**:
| Guideline | Do | Don't |
|-----------|-----|-------|
| Tone | Friendly, clear, helpful | Technical, formal, jargon-heavy |
| Specificity | Include amounts, names, dates | Use vague placeholders |
| Action | Tell customer what to do next | Leave customer uncertain |
| Blame | "We couldn't complete" | "You failed to" |
| Technical terms | "Your bank declined" | "ACH return code R01" |

**Placeholder Standards**:
| Placeholder | Description | Example Rendering |
|-------------|-------------|-------------------|
| `[amount]` | USD amount with currency symbol | "$150.00" |
| `[local_amount]` | Destination currency amount | "1,875,000 UZS" |
| `[recipient]` | Recipient display name | "Dilshod A." |
| `[recipient_name]` | Recipient full name | "Dilshod Alimov" |
| `[fee]` | Fee amount | "$4.99" |
| `[date]` | Expected delivery date | "December 15, 2024" |
| `[rate]` | Exchange rate | "12,500" |
| `[limit]` | Applicable limit | "$2,000" |
| `[support]` | Support contact | "1-800-XXX-XXXX" |

---

## Reference: Gold Standard BRDs

See the following BRDs for examples of business-level FRs that achieved perfect PRD-Ready Score:

- `/opt/data/blocal_n8n/docs/BRD/BRD-009_remittance_transaction_us_to_uzbekistan.md` (100/100 Score)

**Key Success Factors from BRD-009**:
- Zero code blocks in entire document
- FRs structured with Business Capability → Business Requirements → Business Rules → Business Acceptance Criteria
- All technical implementation details deferred to PRD references
- Complexity ratings include business-level rationale (partner count, regulatory scope)
- Cross-references to Platform BRDs (BRD-001 through BRD-005) for traceability

---

**Document Control**:
- **Version**: 1.0
- **Created**: 2025-11-26
- **Source**: Extracted from BRD-TEMPLATE.md Appendix C
- **Maintenance**: Update when BRD template FR structure changes
