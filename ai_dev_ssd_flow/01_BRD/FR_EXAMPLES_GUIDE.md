---
title: "Business-Level Functional Requirements Examples Guide (Layer 1 BRD)"
tags:
  - framework-guide
  - layer-1-artifact
  - shared-architecture
  - examples
custom_fields:
  document_type: examples-guide
  artifact_type: BRD
  layer: 1
  priority: shared
  development_status: active
---

# Business-Level Functional Requirements Examples Guide (Layer 1 BRD)

**Purpose**: Show concise, business-level Functional Requirements that achieve PRD-Ready Score ≥90/100 with clear patterns and minimal examples.

**Status**: Reference Guide  |  **Audience**: BRD Authors, BAs, PMs  |  **Format**: `BRD.NN.EE.SS`

---

## Example 1: Simple Functional Requirement (Complexity 2/5)

### BRD.NNN.001: Recipient Selection and Management

- Business Capability: Enable customers to select existing recipients or add new recipients.
- Business Requirements:
  - Reuse saved recipients; create new during initiation; validate per delivery network.
  - Support multiple payout methods and localized names; enforce phone format.
- Business Rules:
  - Save first-time recipients after successful delivery; reject invalid data pre-initiation.
- Acceptance Criteria:
  - List retrieval <1s; creation median ≤30s; clear validation errors.
- Related: BRD-NN (Recipient Management), BRD-NN (Delivery Integration)
- Complexity: 2/5

---

## Example 2: Complex Functional Requirement (Complexity 4/5)

### BRD.NNN.002: Multi-Region Wallet Funding Support

- Business Capability: Support transactions funded from multiple regional sources with unified balance.
- Business Requirements: Accept multiple rails; unify balance; consistent execution; fee transparency.
- Business Rules: Execute from unified balance; region-appropriate rails; present primary currency.
- Acceptance Criteria: Funds usable <10 minutes (95%); 100% balance consistency; clear fees.
- Related: BRD-NN (Platform Architecture), BRD-NN (Custody Provider), BRD-NN (Compliance)
- Complexity: 4/5

---

## Example 3: AI/ML Functional Requirement (Complexity 3/5)

### BRD.NNN.004: Pre-Request Risk and Compliance Screening

- Business Capability: Screen requests for policy and risk compliance before authorization.
- Business Requirements: 100% sanctions/PEP screening; ML risk scoring; velocity limits; geolocation checks.
- Business Rules (Decision Matrix):
  - 0–59 Approve; 60–79 Manual review (target <5%); 80–100 Decline (consider escalation).
- Acceptance Criteria: ≤3s completion p95; ≤3% false positive; ≥95% true positive; updates ≤24h.
- Related: BRD-NN (Security & Compliance), BRD-NN (Monitoring), BRD-NN (Onboarding)
- Complexity: 3/5

---

## Before/After (Refactoring Illustration)

- Before (anti-pattern): Technical API steps, DB tables, retries, webhooks in BRD.
- After (good): Business capability, business rules, acceptance criteria, cross-references.

---

## Patterns (Copy/Paste)

- Business Capability: “System must [enable/support/provide] [actor] to [action] [outcome/context].”
- Business Requirements (6–8 bullets): Action verb + object + context/constraint; no technical details.
- Business Rules:
  - Threshold table (tiers) or decision matrix (score → action → SLA) or sequential bullets.
- Acceptance Criteria (4–6): Metric + threshold + percentile/target + business justification.
- Cross-References: `(per BRD-NN)`, `(managed per BRD-NN)`, `(per section X)`, `(per BRD.NN.EE.SS)`.

---

## Quality Gates (Checklist)

- Capability: One sentence, business language, starts with “System must”.
- Requirements: 6–8 bullets, business verbs, constraints clear, cross-references present.
- Rules: Express thresholds/logic; tables for tiers; bullets for sequence.
- Acceptance: Quantitative, justified, 4–6 items.
- Tone: Customer-facing clarity; no API/DB/implementation details.

**Problems**:

- ❌ API endpoint specification (POST /screening/ofac)
- ❌ JSON response format details
- ❌ UI interaction (display warning modal)
- ❌ Database table name (PostgreSQL screening_results)
- ❌ Webhook implementation details
- ❌ Code-level retry logic (exponential backoff values)
- ❌ Uses deprecated `FR-XXX` heading format

### AFTER (Business-Level - Score 100/100)

### BRD.NNN.004: Pre-Transaction Sanctions Screening

**Business Capability**: System must screen all transactions against sanctions/PEP lists before authorization.

**Business Requirements**:
- Execute sanctions/PEP screening for 100% of transactions (sender and recipient)
- Validate against current sanctions lists updated within 24 hours of official publication
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
- Sanctions list staleness: ≤24 hours from official publication
- Audit trail retention: 7 years per FinCEN recordkeeping requirements

**Related Requirements**:
- Platform: BRD-03 (security & Compliance Framework)
- Compliance: BRD-17 (Compliance Monitoring & SAR Generation)

**Complexity**: 2/5 (Standard sanctions screening integration; requires compliance workflow for manual review queue)

**What Changed**:

- ✅ Removed API specifications → Kept business capability ("screen all transactions")
- ✅ Removed JSON format → Kept business rules (auto-decline, queue for review)
- ✅ Removed UI details → Kept business acceptance criteria (completion time ≤3 seconds)
- ✅ Removed database/webhook → Kept business requirement (audit trail for regulatory examination)
- ✅ Removed retry logic → Kept business SLA (completion time target)
- ✅ Added complexity rating with business rationale
- ✅ Added cross-references to related Platform and Compliance BRDs
- ✅ Updated heading format from `FR-XXX` to `BRD.NN.EE.SS`

---

## Functional Requirement 4-Subsection Detailed Guidance

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
| 1/5 | System must enable customers to view their transaction history for all completed transactions. |
| 2/5 | System must support recipient management including creation, validation, and reuse for future transactions. |
| 3/5 | System must perform comprehensive fraud detection and regulatory compliance screening before authorizing transactions. |
| 4/5 | System must support transactions funded from multiple wallet funding sources across regions with unified balance presentation. |
| 5/5 | System must orchestrate end-to-end transaction lifecycle across multiple partners with automated failure recovery and regulatory compliance across jurisdictions. |

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
- 6-8 bullets per functional requirement (minimum 4, maximum 10)
- Each bullet is 1-2 sentences maximum
- Uses business action verbs: Accept, Support, Validate, Enable, Enforce, Maintain, Provide
- Includes cross-references to related BRDs using format: `(per BRD-XXX)` or `(managed per BRD-XXX)`
- Excludes implementation details: field names, data types, API parameters

**Example Structure**:

```markdown
**Business Requirements**:
- [Primary capability requirement with BRD cross-reference]
- [secondary capability requirement]
- [Validation/quality requirement]
- [Support for variations/edge cases]
- [Compliance/regulatory requirement if applicable]
- [Integration requirement with partner BRD reference]
- [Performance/availability business need]
- [Audit/reporting business need]
```

**Example (BRD.NNN.002: Fee Calculation)**:

```markdown
**Business Requirements**:
- Calculate flat service fee based on transaction amount tiers (per Fee Schedule in section 10)
- Apply region-specific conversion margin for currency conversion (per BRD.NNN.003)
- Present total cost breakdown before customer confirmation (fee transparency requirement)
- Support fee waiver promotions during initial launch period (per Marketing campaign requirements)
- Maintain fee audit trail for regulatory examination and customer dispute resolution
- Calculate delivery partner fees based on payout method (bank vs mobile wallet vs prepaid card)
```

**Cross-Reference Pattern** (with Section Context):

| Reference Type | Format | Example |
|---------------|--------|---------|
| Platform BRD | `(per BRD-NN, Section X)` | `(per BRD-01, Section 6)` |
| Feature BRD | `(managed per BRD-XXX, Section X)` | `(managed per BRD-11, Section 6)` |
| Internal section | `(per BRD-XX.Y_filename.md)` | `(per BRD-09.7_quality_attributes.md)` |
| Related Functional Requirement | `BRD.NN.EE.SS (Section X)` | `BRD.09.01.05 (Section 6)` |
| Business Objective | `BRD.NN.23.SS (Section 2)` | `BRD.09.23.01 (Section 2)` |

**Note**: Always include section context in parentheses after element IDs to improve navigability. For file-based references, use explicit markdown filenames instead of vague "Section X" references.

---

### Subsection 3: Business Rules (Required)

**Purpose**: Decision logic, thresholds, and conditional behaviors expressed in business terms.

**When to Use Tables vs Bullets**:

| Use Tables When | Use Bullets When |
|-----------------|------------------|
| ≥3 decision variables | Simple if/then rules |
| Tiered thresholds (verification tiers, fee tiers) | Sequential business rules |
| Multi-column decision matrix | Rules with single condition |
| Comparing options (funding methods, payout types) | Rules requiring narrative explanation |

**Table Pattern (Tiered Thresholds)**:
```markdown
**Business Rules**:

| Verification Tier | Daily Limit | Per-Transaction Limit | Velocity Limit |
|-----------|-------------|----------------------|----------------|
| L1 (Basic) | @threshold: PRD.NN.quota.l1.daily | @threshold: PRD.NN.quota.l1.per_txn | @threshold: PRD.NN.quota.l1.velocity |
| L2 (Enhanced) | @threshold: PRD.NN.quota.l2.daily | @threshold: PRD.NN.quota.l2.per_txn | @threshold: PRD.NN.quota.l2.velocity |
| L3 (Full) | @threshold: PRD.NN.quota.l3.daily | @threshold: PRD.NN.quota.l3.per_txn | @threshold: PRD.NN.quota.l3.velocity |
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
- Recipient information must match delivery network requirements for successful delivery
- Invalid recipient data must be rejected before transaction initiation to prevent delivery failures
- Duplicate recipient detection within same customer profile (name + phone number match)
```

**Examples by Business Rule Type**:

| Rule Type | Example |
|-----------|---------|
| Threshold | "Transactions ≥$3,000 require Travel Rule compliance (identity disclosure)" |
| Conditional | "Region B customers use regional bank transfer path; Region A customers use bank transfer or card path" |
| Validation | "Validate sender/recipient region and phone country code format (e.g., +[country code])" |
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
| Compliance | `≤[time] from [trigger event]` | `≤24 hours from official publication` |
| Throughput | `[count] [unit] per [time period]` | `10,000 transactions per day capacity` |
| Quality | `≥[percentage]% [quality metric]` | `≥95% true positive rate for fraud detection` |

**Example (BRD.NNN.004: Risk Screening)**:

```markdown
**Business Acceptance Criteria**:
- Screening completion time: ≤3 seconds for 95% of transactions (customer experience requirement)
- False positive rate: ≤3% (minimize blocking legitimate customers unnecessarily)
- True positive rate: ≥95% (catch actual fraudulent/sanctioned transactions)
- Manual review queue processing: ≤2 hours during business hours for 90% of cases
- Sanctions list updates: Applied within 24 hours of official publication (regulatory requirement)
```

**Justification Phrases**:
| Justification Type | Phrase Pattern |
|-------------------|----------------|
| Customer Experience | `(customer experience requirement)` |
| Regulatory | `(regulatory requirement)`, `(per applicable regulatory mandate)` |
| Operational | `(operational efficiency)`, `(reduce manual processing)` |
| Business | `(reduces friction for repeat sends)`, `(enables market expansion)` |
| Risk | `(minimize false blocks)`, `(prevent delivery failures)` |

---

### Subsection 5: Related Requirements (Required)

**Purpose**: Cross-references to Platform BRDs, Partner Integration BRDs, and other Feature BRDs with section context for navigability.

**Format** (with Section Context):
```markdown
**Related Requirements**:
- Platform: BRD-01 (Platform Architecture, Section 6), BRD-02 (Partner Ecosystem, Section 6)
- Partner Integration: BRD-08 (Wallet Funding via Custody Provider, Section 6), BRD-11 (Recipient Management, Section 6)
- Compliance: BRD-03 (Security & Compliance Framework, Section 6), BRD-17 (Compliance Monitoring, Section 6)
- AI Agent: BRD-22 (Fraud Detection Agent - ML implementation details, Section 6)
- Business Objectives: BRD.09.23.01 (Section 2), BRD.09.23.02 (Section 2)
```

**Explicit File Path Format** (preferred for split BRDs):
```markdown
**Related Requirements**:
- Platform: [BRD-01.6_functional_requirements.md](../BRD-01_platform_architecture/BRD-01.6_functional_requirements.md)
- Quality: [BRD-09.7_quality_attributes.md](BRD-09.7_quality_attributes.md)
- Business Objectives: BRD.09.23.01 (Section 2 - [BRD-09.2_business_objectives.md](BRD-09.2_business_objectives.md))
```

**Category Definitions**:
| Category | BRD Range | Purpose |
|----------|-----------|---------|
| Platform | BRD-01 through BRD-05 | Core platform capabilities |
| Partner Integration | BRD-06 through BRD-15 | External partner integrations |
| Compliance | BRD-16 through BRD-20 | Regulatory and compliance |
| AI Agent | BRD-21 through BRD-30 | AI/ML agent capabilities |
| Feature | BRD-31+ | Specific business features |

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
- Simple: `([Your App]→[Provider A]→[Provider B])`
- Complex: `([Your App]→[Provider A]→[Provider B]; [Your App]→Compliance→[Sanctions Provider])`

**Examples**:
```markdown
**Complexity**: 2/5 (Standard customer data management; requires recipient validation API integration from BRD-11)

**Complexity**: 3/5 (Multiple screening systems integration; ML model inference with business rule thresholds; regulatory compliance across sanctions, AML, and Travel Rule; manual review workflow coordination)

**Complexity**: 4/5 (Dual-region funding architecture; requires custody provider integration with bank transfer and regional transfer rails; unified wallet balance across funding sources; multi-jurisdiction compliance)

**Complexity**: 5/5 (End-to-end orchestration: [Your App]→[Provider A]→[Provider B] partner chain; 7 business constraints including regulatory hold periods; multi-jurisdiction compliance across regions; automated retry with business escalation; 12 business rules across 4 decision categories)
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

**Cross-Reference**: Full communication templates are documented in **Appendix N: Customer Communication Templates**. This subsection provides functional requirement-specific excerpts.

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
| Transaction delivered | "Great news! [recipient] has received your transfer of $[amount] ([localized_amount] [CURRENCY])" | Push, SMS |

**Error Messages**:
| Error Condition | Customer Message | Support Code |
|-----------------|------------------|--------------|
| Insufficient funds | "Your payment couldn't be completed. Please check your balance and try again." | ERR-001 |
| Recipient validation failed | "We couldn't verify the recipient's information. Please check the details and try again." | ERR-002 |

**Regulatory Disclosures**:
- Pre-transfer disclosure: "You will be charged $[fee]. Conversion rate: 1 [CURRENCY_A] = [rate] [CURRENCY_B]. [recipient] will receive [localized_amount] [CURRENCY_B]."
- Transfer Rights disclosure: "For questions or complaints about this transfer, contact us at [support] or visit [URL]"
```

**Example (BRD.NNN.001: Transaction Initiation)**:

```markdown
**Customer-Facing Language**:

**Success Messages**:
| Trigger | Message | Channel |
|---------|---------|---------|
| Quote generated | "Send $[amount] to [recipient]. Fee: $[fee]. [recipient] receives [localized_amount] [CURRENCY]." | In-app |
| Transaction submitted | "Your transfer is on its way! We'll notify you when [recipient] receives the funds." | In-app, Email |

**Error Messages**:
| Condition | Customer Message | Support Code |
|-----------|------------------|--------------|
| Daily limit exceeded | "You've reached your daily transfer limit of $[limit]. Try again tomorrow or contact support to increase your limit." | TXN-LIMIT |
| Recipient country blocked | "We're unable to send transfers to this destination at this time." | TXN-DEST |

**Notification Text**:
- Push (initiation): "Transfer started: $[amount] to [recipient_name]"
- Push (delivered): "✓ Delivered: [recipient_name] received [localized_amount] [CURRENCY]"
- SMS (delivered): "[Your App]: Your transfer of [local_amount] [CURRENCY] to [recipient_name] has been delivered."
```

**Language Guidelines**:
| Guideline | Do | Don't |
|-----------|-----|-------|
| Tone | Friendly, clear, helpful | Technical, formal, jargon-heavy |
| Specificity | Include amounts, names, dates | Use vague placeholders |
| Action | Tell customer what to do next | Leave customer uncertain |
| Blame | "We couldn't complete" | "You failed to" |
| Technical terms | "Payment declined" | "Bank return code R01" |

**Placeholder Standards**:
| Placeholder | Description | Example Rendering |
|-------------|-------------|-------------------|
| `[amount]` | USD amount with currency symbol | "$150.00" |
| `[localized_amount]` | Destination currency amount | "1,875,000 [CURRENCY]" |
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

- `[example path to a high-scoring BRD file in your repo]` (100/100 Score)

**Key Success Factors from BRD-09**:
- Zero code blocks in entire document
- FRs structured with Business Capability → Business Requirements → Business Rules → Business Acceptance Criteria
- All technical implementation details deferred to PRD references
- Complexity ratings include business-level rationale (partner count, regulatory scope)
- Cross-references to Platform BRDs (BRD-01 through BRD-05) for traceability

---

**Document Control**:

- **Version**: 2.0
- **Created**: 2025-11-26T00:00:00
- **Updated**: 2025-12-10T00:00:00 (migrated to unified `BRD.NN.EE.SS` heading format)
- **Source**: Extracted from BRD-MVP-TEMPLATE.md Appendix C
- **Maintenance**: Update when BRD template functional requirement structure changes
