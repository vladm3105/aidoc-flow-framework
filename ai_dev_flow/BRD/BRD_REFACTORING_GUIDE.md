# BRD Refactoring Guide

**Purpose**: Step-by-step guide for transforming PRD-level contaminated BRDs into business-level documents achieving ≥90/100 PRD-Ready Score

**Target Audience**: Business Analysts, Product Managers, Technical Writers performing BRD refactoring

**Gold Standard Reference**: BRD-009 (US-to-Uzbekistan Remittance) - 100/100 PRD-Ready Score

---

## Table of Contents

1. [When to Refactor](#when-to-refactor)
2. [Refactoring Workflow](#refactoring-workflow)
3. [FR Transformation Process](#fr-transformation-process)
4. [Common Mistakes and Fixes](#common-mistakes-and-fixes)
5. [Self-Review Checklist](#self-review-checklist)
6. [Before/After Examples](#beforeafter-examples)
7. [Lessons Learned](#lessons-learned)

---

## When to Refactor

### Refactoring Triggers

**Immediate Refactoring Required**:
- PRD-Ready Score <70/100 (heavy PRD-level contamination)
- Code blocks present in Functional Requirements (Section 4)
- API endpoints or database schemas documented in FRs
- UI mockups or screen flows embedded in business requirements

**Recommended Refactoring**:
- PRD-Ready Score 70-89/100 (moderate contamination)
- Technical terminology prevalent in FR descriptions
- Missing Complexity ratings or Related Requirements cross-references
- Tabular FR format instead of 4-subsection business-level structure

**Optional Refactoring**:
- PRD-Ready Score ≥90/100 but want to achieve gold standard (100/100)
- Minor UI term usage or occasional technical language
- Improving traceability with better Platform BRD cross-references

---

## Refactoring Workflow

### 10-Step Refactoring Process

**Step 1: Baseline Assessment**
1. Run validation script: `./scripts/validate_brd.py docs/BRD/BRD-XXX.md`
2. Document current PRD-Ready Score (should be <90/100)
3. Review detailed deduction report
4. Identify top 3 categories causing deductions

**Step 2: Create Backup**
```bash
cp docs/BRD/BRD-XXX_feature_name.md docs/BRD/BRD-XXX_feature_name.md.backup_v1.0
```

**Step 3: Update Version Control**
1. Increment Document Version from 1.0 → 2.0 (major version for structural refactoring)
2. Add Revision History entry (see BRD_CREATION_RULES.md Section 3.5 for template)
3. Label entry as "**Major Refactoring**"

**Step 4: Remove PRD-Level Content** (Category 1 Violations)
- Remove ALL code blocks (Python, JSON, SQL, YAML) from Section 4
- Remove API endpoint specifications (POST /api/v1/*, GET /api/*)
- Remove database schemas and table structures
- Remove UI mockups and screen flow descriptions
- See BRD-TEMPLATE.md Appendix B for comprehensive REMOVE/KEEP rules

**Step 5: Replace with Business-Level Descriptions**
- Convert API specs → business capabilities ("Customer initiates transaction")
- Convert database queries → business rules ("Customer must have completed KYC")
- Convert UI flows → business actions ("Customer selects recipient from saved list")
- Convert code logic → business acceptance criteria ("95% of transactions complete in <5 seconds")

**Step 6: Transform FR Structure** (Category 2 Violations)
1. For each FR in Section 4:
   - Add **Business Capability** subsection (one sentence high-level description)
   - Convert existing content into **Business Requirements** (bullet list)
   - Extract policies/constraints into **Business Rules**
   - Define measurable outcomes in **Business Acceptance Criteria**
   - Add **Related Requirements** cross-references to Platform/Feature BRDs
   - Add **Complexity** rating (X/5 with business-level rationale)

2. Use BRD-TEMPLATE.md Section 5.2 as structure reference
3. Follow BRD_CREATION_RULES.md Section 5.5 for Complexity methodology

**Step 7: Add Cross-References**
1. Identify Platform BRD dependencies (BRD-001 through BRD-005)
2. Identify Feature BRD dependencies (related BRDs in same domain)
3. Add Related Requirements subsection to each FR
4. Verify all BRD references exist (CHECK 18 validation)

**Step 8: Validate Transformation**
```bash
./scripts/validate_brd.py docs/BRD/BRD-XXX_feature_name.md
```
1. Review new PRD-Ready Score
2. Target: ≥90/100 (should improve by 20-40 points from baseline)
3. Address any remaining violations

**Step 9: Document Changes**
1. Create CHANGELOG entry (or update work plan)
2. Document before/after score improvement
3. List structural changes and content removals
4. Reference deferred PRD content location

**Step 10: Submit for Review**
1. Update Document Control Status to "In Review"
2. Submit to business stakeholders for approval
3. Address feedback and re-validate
4. Update Status to "Approved" when finalized

---

## FR Transformation Process

### Converting Tabular Format → 4-Subsection Business-Level Structure

#### BEFORE: Tabular PRD-Level Format (Score: 65/100)

```markdown
### FR-005: Transaction Initiation API

| Field | Requirement |
|-------|-------------|
| **Endpoint** | POST /api/v1/transactions |
| **Authentication** | Bearer token in Authorization header |
| **Request Body** | JSON with fields: amount (decimal), recipient_id (UUID), funding_source_id (UUID) |
| **Validation** | Amount >$1.00, recipient exists in database, funding source belongs to customer |
| **Response** | 201 Created with transaction_id (UUID) and status (INITIATED) |
| **Error Codes** | 400 (invalid input), 404 (recipient not found), 500 (server error) |
| **Database** | INSERT into transactions table with customer_id, amount, recipient_id, funding_source_id, status='INITIATED', created_at=NOW() |
| **Performance** | API latency <200ms for 95th percentile |
```

**Deductions**:
- Code blocks: 0 (no triple backticks, but table is PRD-level)
- API/technical terms: 14 instances (POST, JSON, UUID, database, INSERT, Bearer token, Authorization header, etc.) → -28 points (capped at -20)
- UI terms: 0
- Missing subsections: 6 (all required subsections missing) → -5 points
- Invalid cross-references: N/A (no Related Requirements section)
- **Total Deductions**: 45 points
- **PRD-Ready Score**: 55/100 ❌

---

#### AFTER: 4-Subsection Business-Level Structure (Score: 100/100)

```markdown
#### FR-005: Customer-Initiated Cross-Border Transaction

**Business Capability**: Enable customers to initiate remittance transactions to Uzbekistan recipients with selected funding source

**Business Requirements**:
- Customer selects transaction amount (minimum $1.00), recipient from saved list, and funding source (ACH/debit card/wallet)
- System validates customer KYC status (must be completed per BRD-006), transaction limits (daily/monthly per FinCEN MSB regulations), and recipient active status
- System validates funding source belongs to customer and has sufficient balance (or credit limit for cards)
- Customer receives immediate transaction confirmation with tracking ID and estimated delivery time

**Business Rules**:
- **Minimum Transaction**: $1.00 USD
- **Maximum Transaction**: $10,000 per transaction, $50,000 per rolling 30-day period (FinCEN Money Services Business limits)
- **KYC Requirement**: Customer must have completed KYC identity verification (BRD-006 B2C Progressive KYC)
- **Recipient Requirement**: Recipient must be pre-validated and active status (BRD-011 Recipient Management)
- **Funding Source Requirement**: Funding source must be verified and belong to customer (BRD-008 Wallet Funding)
- **Compliance Screening**: All transactions subject to OFAC sanctions screening before processing (BRD-003 Compliance Framework)

**Business Acceptance Criteria**:
- 95% of valid transaction initiations complete within 5 seconds (from customer submission to confirmation display)
- Customer receives transaction receipt with tracking ID immediately upon successful initiation
- Invalid transactions rejected with clear business reason (insufficient balance, limit exceeded, recipient inactive, KYC incomplete)
- Transaction tracking ID format: TXN-{YYYYMMDD}-{UUID} for customer reference and support lookup

**Related Requirements**:
- Platform BRDs: BRD-001 (Platform Architecture), BRD-002 (Partner Ecosystem - Bridge/Plaid/Stripe), BRD-003 (Security & Compliance - OFAC screening)
- Feature BRDs: BRD-006 (B2C KYC Onboarding), BRD-008 (Wallet Funding), BRD-009 (Remittance Processing), BRD-011 (Recipient Management), BRD-016 (Fraud Detection - risk screening)

**Complexity**: 4/5 (Five partner integrations (Bridge USDC custody, Plaid ACH, Stripe card processing, Sardine fraud detection, Unit21 AML monitoring); FinCEN MSB compliance requirements; OFAC sanctions screening; references BRD-001, BRD-002, BRD-003, BRD-006, BRD-008, BRD-009, BRD-011, BRD-016)
```

**Deductions**:
- Code blocks: 0 → -0 points
- API/technical terms: 0 → -0 points
- UI terms: 0 → -0 points
- Missing subsections: 0 → -0 points
- Invalid cross-references: 0 → -0 points
- **Total Deductions**: 0 points
- **PRD-Ready Score**: 100/100 ✅

---

### Transformation Changes Applied

**Removed (PRD-Level Content)**:
1. API endpoint specification: `POST /api/v1/transactions`
2. Authentication mechanism: Bearer token, Authorization header
3. Request/Response JSON structure: `amount (decimal), recipient_id (UUID)`
4. HTTP status codes: 201 Created, 400, 404, 500
5. Database implementation: `INSERT into transactions table`
6. Technical performance metric: API latency <200ms

**Replaced With (Business-Level Content)**:
1. **Business Capability**: One-sentence description of what business function this enables
2. **Business Requirements**: Customer actions and system validations at business level
3. **Business Rules**: Policies, regulatory constraints (FinCEN, OFAC), business limits ($1 min, $10K max)
4. **Business Acceptance Criteria**: Customer-facing SLAs (95% complete in <5 seconds) and outcomes
5. **Related Requirements**: Platform BRD dependencies (architecture, partners, compliance) and Feature BRD dependencies
6. **Complexity Rating**: 4/5 with business-level rationale (partner count, regulatory scope, dependencies)

**Content Deferred to PRD**:
- API endpoint design → PRD-009 Section 4 (API Specifications)
- Request/Response JSON schemas → PRD-009 Section 5 (Data Models)
- Database schema and queries → PRD-009 Section 6 (Data Layer)
- Error handling and HTTP codes → PRD-009 Section 7 (Error Handling)
- Technical performance metrics → PRD-009 Section 8 (Performance Requirements)

---

## Common Mistakes and Fixes

### Mistake 1: "Technology Prescriptions" (Edge Case 1)

❌ **WRONG (PRD-Level)**:
```markdown
**Business Requirements**:
- Platform MUST use Bridge custody provider for USDC wallet operations
- MUST use PostgreSQL database with replication
- MUST use Auth0 for OAuth 2.0 authentication
```

✅ **CORRECT (Business-Level)**:
```markdown
**Business Requirements**:
- Platform requires segregated USDC custody with MTL sponsorship (BRD-002 partner selection defines Bridge as custody provider)
- Platform requires scalable relational data storage with ACID compliance and disaster recovery (BRD-001 technology stack)
- Platform requires OAuth 2.0/OIDC authentication with multi-factor authentication support (BRD-003 authentication requirements)
```

**Fix Strategy**:
1. Replace vendor/technology name with business capability description
2. Add Platform BRD reference in parentheses
3. Keep regulatory/business requirement (MTL sponsorship, ACID compliance, MFA)

---

### Mistake 2: "Quantitative Thresholds - Technical vs Business SLAs" (Edge Case 2)

❌ **WRONG (Technical Metrics)**:
```markdown
**Business Acceptance Criteria**:
- API endpoint response time <200ms (95th percentile)
- Database query execution time <50ms
- Cache hit rate ≥90%
- WebSocket connection establishment <500ms
```

✅ **CORRECT (Business-Level SLAs)**:
```markdown
**Business Acceptance Criteria**:
- 95% of transactions complete end-to-end in <15 minutes (customer-facing SLA)
- Email notifications delivered within 60 seconds for 95% of events (customer notification SLA)
- Compliance screening completes in ≤3 seconds for 95% of transactions (regulatory requirement)
- Refund processing completes within 1 hour of delivery failure for 95% of cases (customer service SLA)
```

**Fix Strategy**:
1. Ask: "Does this metric affect customer experience or regulatory compliance?"
2. If YES → Keep as business acceptance criterion
3. If NO → Remove and defer to PRD technical requirements
4. Rewrite technical metrics as customer-facing outcomes

---

### Mistake 3: "State Machines - Business States vs Technical Implementation" (Edge Case 3)

❌ **WRONG (Technical State Management)**:
```markdown
**Business Requirements**:
- StateMachine.transition(from: INITIATED, to: FUNDED, on: wallet_debited event)
- Update transaction_state column in PostgreSQL transactions table
- Publish state_changed event to Kafka topic for downstream consumers
- Implement idempotent state transitions with optimistic locking
```

✅ **CORRECT (Business State Names)**:
```markdown
**Business Requirements**:
- Transaction progresses through business states: INITIATED → FUNDED → COMPLETED
- Customer receives status update notifications at each state transition
- System records state transition timestamp for audit trail and customer support reference

**Business Rules**:
- Transaction state transitions are irreversible (cannot return from COMPLETED to FUNDED)
- Failed transactions transition to FAILED state with business reason code (insufficient funds, recipient inactive, compliance decline)
```

**Fix Strategy**:
1. Keep state NAMES (INITIATED, FUNDED, COMPLETED) as business process states
2. Remove technical event handlers, database updates, message queue publishing
3. Focus on customer-visible outcomes and business reasons for state changes

---

### Mistake 4: "Code Blocks in Business Requirements" (Edge Case 4)

❌ **WRONG (Code Blocks)**:
```markdown
**Business Requirements**:
- Calculate transaction fee using the following algorithm:

\`\`\`python
def calculate_fee(amount, recipient_country, funding_source):
    base_fee = 2.99
    if amount > 1000:
        percentage_fee = amount * 0.01
    else:
        percentage_fee = amount * 0.02

    if funding_source == "card":
        percentage_fee += amount * 0.029

    return base_fee + percentage_fee
\`\`\`
```

✅ **CORRECT (Business-Level Fee Structure)**:
```markdown
**Business Requirements**:
- System calculates transaction fee based on amount, recipient country, and funding source per fee schedule (BRD-REF-007 Business Model Economics)

**Business Rules** (Fee Structure):
| Transaction Amount | Base Fee | Percentage Fee | Card Surcharge |
|--------------------|----------|----------------|----------------|
| $1.00 - $999.99 | $2.99 | 2.0% of amount | +2.9% of amount |
| $1,000.00 - $10,000.00 | $2.99 | 1.0% of amount | +2.9% of amount |

- **Total Fee** = Base Fee + Percentage Fee + Card Surcharge (if applicable)
- Fee calculation algorithm implementation detailed in PRD-009 Section 4.3 (Fee Processing)
```

**Fix Strategy**:
1. Remove ALL code blocks (Python, JSON, SQL, pseudocode)
2. Replace with business-level fee structure using markdown table
3. State business rules as tier structure with percentages
4. Reference PRD for implementation algorithm

---

### Mistake 5: "Business Economics Tables vs Calculation Code" (Edge Case 5)

✅ **KEEP (Business-Level Fee Table)**:
```markdown
**Business Rules** (FX Markup Tiers):
| Monthly Volume (USD) | FX Markup | Example (USD → UZS) |
|---------------------|-----------|---------------------|
| $0 - $10,000 | 1.5% | 1 USD = 12,450 UZS |
| $10,001 - $50,000 | 1.2% | 1 USD = 12,475 UZS |
| $50,001+ | 0.9% | 1 USD = 12,500 UZS |

- Base rate sourced from partner FX provider (BRD-002 partner ecosystem)
- Markup applied to customer exchange rate, not partner settlement rate
```

❌ **REMOVE (Calculation Implementation)**:
```markdown
\`\`\`python
def get_fx_rate(base_rate, monthly_volume):
    if monthly_volume <= 10000:
        markup = 0.015
    elif monthly_volume <= 50000:
        markup = 0.012
    else:
        markup = 0.009
    return base_rate * (1 + markup)
\`\`\`
```

**Fix Strategy**:
1. KEEP fee/pricing tables showing tier structure and percentages
2. KEEP examples showing customer-facing rates
3. REMOVE calculation code and formulas
4. State business rules (when markup applies, who sees which rate)

---

### Mistake 6: "ML Model Specifications - Business Rules vs Model Architecture" (Edge Case 6)

✅ **KEEP (Business-Level Risk Rules)**:
```markdown
**Business Rules** (Risk Scoring Tiers):
| Risk Score Range | Business Outcome | Rationale |
|------------------|------------------|-----------|
| 0-59 (Low Risk) | Auto-Approve | Clean transaction history, verified customer, low-risk recipient country |
| 60-79 (Medium Risk) | Manual Review | First-time recipient, high transaction amount, recent account changes |
| 80-100 (High Risk) | Auto-Decline | Sanctions list match, suspicious activity patterns, compliance red flags |

- Risk scoring algorithm provided by Sardine risk partner (BRD-002 partner ecosystem)
- Manual review cases routed to compliance team queue (BRD-020 admin console case management)
```

❌ **REMOVE (ML Model Architecture)**:
```markdown
\`\`\`python
# Feature engineering
features = [
    'transaction_amount_normalized',
    'recipient_country_risk_score',
    'customer_age_days',
    'historical_transaction_count',
    'time_since_last_transaction_hours'
]

# Model hyperparameters
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    min_samples_split=50
)
\`\`\`
```

**Fix Strategy**:
1. KEEP business risk tiers and decision outcomes (auto-approve, manual review, auto-decline)
2. KEEP business rationale for each tier (transaction history, recipient country risk)
3. REMOVE feature engineering code and model hyperparameters
4. Reference ML model implementation in PRD-022 Fraud Detection Agent

---

## Self-Review Checklist

### Pre-Validation Checklist (Use Before Running Validation Script)

**Category 1: PRD-Level Content Removal** ☐ Complete
- [ ] Zero code blocks (```) in Section 4 Functional Requirements
- [ ] No API endpoint specifications (POST, GET, PUT, DELETE, /api/v1/*)
- [ ] No JSON/XML/YAML schema examples
- [ ] No database schemas or SQL queries (INSERT, UPDATE, SELECT, CREATE TABLE)
- [ ] No UI mockups or screen flow descriptions (modals, buttons, forms, clicks)
- [ ] No technical performance metrics (API latency, database query time, cache hit rate)

**Category 2: Business-Level Content Present** ☐ Complete
- [ ] All FRs use 4-subsection structure (Business Capability, Business Requirements, Business Rules, Business Acceptance Criteria, Related Requirements, Complexity)
- [ ] Business Capability is one-sentence high-level description
- [ ] Business Requirements focus on what customer/system accomplishes (not how technically)
- [ ] Business Rules include regulatory constraints (FinCEN, OFAC), policies, business limits
- [ ] Business Acceptance Criteria are customer-facing SLAs with measurable targets (95% in <X seconds)

**Category 3: Cross-References and Traceability** ☐ Complete
- [ ] Every FR has Related Requirements subsection
- [ ] Platform BRD references present (BRD-001 through BRD-005 as applicable)
- [ ] Feature BRD references present (related BRDs in same domain)
- [ ] All BRD-NNN references use correct 3-digit format (BRD-002, not BRD-2)
- [ ] All referenced BRD files exist in docs/BRD/ directory

**Category 4: Complexity Ratings** ☐ Complete
- [ ] Every FR has Complexity subsection
- [ ] Complexity rating uses X/5 scale (1/5 through 5/5)
- [ ] Rationale includes partner count with names
- [ ] Rationale includes regulatory scope (specific regulations: FinCEN, OFAC, etc.)
- [ ] Rationale includes business constraints (SLAs, settlement timing)
- [ ] Rationale includes cross-BRD dependencies (lists specific BRD references)

**Category 5: Document Structure** ☐ Complete
- [ ] Document Control table includes PRD-Ready Score field
- [ ] All 17 required sections present (see BRD-TEMPLATE.md)
- [ ] Document Revision History table has at least one entry
- [ ] Major refactoring labeled as "**Major Refactoring**" in Revision History
- [ ] Before/after score documented in Revision History or CHANGELOG

---

## Before/After Examples

### Example 1: Simple FR Refactoring (Complexity 2/5)

**BEFORE: Recipient Selection UI (Score: 60/100)**
```markdown
### FR-002: Recipient Selection

**UI Components**:
- Dropdown menu displays saved recipients
- Click recipient name to select
- Search box filters recipient list
- "Add New Recipient" button opens modal form

**API Calls**:
- GET /api/v1/recipients returns JSON array
- POST /api/v1/recipients/select with recipient_id

**Validation**:
- Recipient must exist in database
- Recipient status = 'ACTIVE'
```

**Deductions**:
- API terms: 6 instances (GET, POST, JSON, database, etc.) → -12 points
- UI terms: 8 instances (dropdown, click, button, modal, search box) → -16 points
- Missing subsections: 6 → -5 points
- **Total**: -33 points
- **Score**: 67/100 ❌

---

**AFTER: Recipient Selection (Score: 100/100)**
```markdown
#### FR-002: Recipient Selection from Saved List

**Business Capability**: Enable customers to select delivery recipient from their pre-validated saved recipient list

**Business Requirements**:
- Customer views list of saved recipients with name, country, and account details
- Customer searches saved recipients by name or account number
- Customer selects recipient to receive remittance funds
- Customer can add new recipient to saved list (navigates to BRD-011 recipient validation workflow)

**Business Rules**:
- Only ACTIVE status recipients appear in selection list
- Recipient must have completed validation (BRD-011 recipient management requirements)
- Customer cannot select INACTIVE or PENDING_VALIDATION recipients
- Maximum 50 saved recipients per customer account

**Business Acceptance Criteria**:
- Recipient list loads within 2 seconds for 95% of customer sessions
- Search results filter list in real-time (<500ms response for 95% of searches)
- Customer receives clear message if attempting to select inactive recipient: "Recipient unavailable. Please verify recipient details."

**Related Requirements**:
- Platform BRDs: BRD-001 (Platform Architecture), BRD-004 (Data Model - recipient storage)
- Feature BRDs: BRD-011 (Recipient Management and Validation), BRD-009 (Remittance Transaction Processing)

**Complexity**: 2/5 (Two partner integrations (internal recipient database, Uzbekistan recipient validation via partner API); basic business rules; references BRD-001, BRD-004, BRD-009, BRD-011)
```

**Deductions**:
- API terms: 0 → -0 points
- UI terms: 0 → -0 points
- Missing subsections: 0 → -0 points
- **Total**: 0 points
- **Score**: 100/100 ✅

---

### Example 2: Complex FR Refactoring (Complexity 5/5)

**BEFORE: Cross-Border Payment Processing (Score: 55/100)**
```markdown
### FR-009: Payment Processing Engine

**Technical Architecture**:
\`\`\`json
{
  "transaction": {
    "id": "uuid",
    "amount_usd": "decimal",
    "amount_uzs": "decimal",
    "fx_rate": "decimal",
    "status": "string"
  }
}
\`\`\`

**API Endpoints**:
- POST /api/v1/transactions/initiate - Start transaction
- POST /api/v1/transactions/{id}/fund - Debit customer wallet
- POST /api/v1/transactions/{id}/convert - Execute FX conversion
- POST /api/v1/transactions/{id}/deliver - Send to Uzbekistan partner

**Database Transactions**:
\`\`\`sql
BEGIN TRANSACTION;
UPDATE wallets SET balance = balance - amount WHERE customer_id = ?;
INSERT INTO transactions (customer_id, amount, status) VALUES (?, ?, 'INITIATED');
COMMIT;
\`\`\`

**State Machine**:
- INITIATED → wallet_debited → FUNDED
- FUNDED → fx_converted → CONVERTED
- CONVERTED → delivered_to_partner → COMPLETED

**Performance**:
- API latency <200ms per endpoint
- Database transaction time <100ms
- End-to-end processing <30 seconds
```

**Deductions**:
- Code blocks: 3 (JSON, SQL, state machine) → -30 points
- API terms: 15+ instances → -20 points (capped)
- UI terms: 0 → -0 points
- Missing subsections: 6 → -5 points
- **Total**: -55 points
- **Score**: 45/100 ❌

---

**AFTER: Cross-Border Payment Processing (Score: 100/100)**
```markdown
#### FR-009: US-to-Uzbekistan Cross-Border Payment Delivery

**Business Capability**: Execute end-to-end cross-border payment from US customer wallet debit through Uzbekistan recipient delivery via local partner network

**Business Requirements**:
- System debits customer USDC wallet upon transaction initiation (BRD-008 wallet funding provides USDC balance)
- System executes USD-to-UZS foreign exchange conversion using partner FX provider rate with tiered markup (see Business Rules)
- System routes UZS funds to Uzbekistan delivery partner (BRD-002 partner ecosystem defines Paynet/Humo delivery network)
- System confirms delivery to recipient bank account or mobile wallet (Uzbekistan partner provides delivery confirmation)
- Customer receives delivery confirmation notification via email/SMS (BRD-018 multi-channel notifications)

**Business Rules**:
- **FX Conversion Timing**: Conversion executed immediately after wallet debit to lock exchange rate for customer
- **FX Markup Tiers** (per BRD-REF-007 Business Model Economics):
  - $0-$10K monthly volume: 1.5% markup
  - $10K-$50K monthly volume: 1.2% markup
  - $50K+ monthly volume: 0.9% markup
- **Delivery Partner Selection**: System selects Uzbekistan partner based on recipient account type (bank account → Paynet, mobile wallet → Humo)
- **Settlement Timing**: T+1 settlement with Uzbekistan partners (funds delivered within 24 hours of conversion)
- **OFAC Compliance**: All transactions screened against OFAC sanctions list before FX conversion (BRD-003 compliance framework)

**Business Acceptance Criteria**:
- 95% of transactions complete full cycle (wallet debit → FX conversion → delivery) within 15 minutes
- Customer receives delivery confirmation within 5 minutes of Uzbekistan partner confirmation
- FX rate locked within 3 seconds of wallet debit to prevent customer exchange rate risk
- Failed deliveries trigger automatic refund to customer wallet within 1 hour (BRD-015 error handling and refund processing)

**Related Requirements**:
- Platform BRDs: BRD-001 (Platform Architecture - payment orchestration), BRD-002 (Partner Ecosystem - Bridge custody, FX provider, Uzbekistan delivery partners), BRD-003 (Compliance Framework - OFAC screening), BRD-004 (Ledger Architecture - double-entry accounting)
- Feature BRDs: BRD-008 (Wallet Funding - USDC balance source), BRD-010 (Bill Payment - Paynet integration), BRD-013 (Settlement Reconciliation - T+1 partner settlement), BRD-015 (Error Handling and Refund Processing), BRD-016 (Fraud Detection - transaction screening), BRD-018 (Multi-Channel Notifications)

**Complexity**: 5/5 (Seven partner integrations across two countries (Bridge USDC custody, FX provider, Sardine/Unit21 compliance screening, Paynet/Humo Uzbekistan delivery, email/SMS notification); FinCEN MSB licensing, OFAC sanctions compliance, Uzbekistan Central Bank regulations; T+1 settlement SLA; multi-currency reconciliation; references BRD-001, BRD-002, BRD-003, BRD-004, BRD-008, BRD-010, BRD-013, BRD-015, BRD-016, BRD-018)
```

**Deductions**:
- Code blocks: 0 → -0 points
- API terms: 0 → -0 points
- UI terms: 0 → -0 points
- Missing subsections: 0 → -0 points
- **Total**: 0 points
- **Score**: 100/100 ✅

---

## Lessons Learned

### From BRD-009 Pilot Refactoring (65/100 → 100/100)

**Key Insights**:

1. **Fee Structures Belong in BRD, Calculation Code Belongs in PRD**
   - KEEP: Markdown tables showing fee tiers, percentages, examples
   - REMOVE: Python functions calculating fees, JSON fee configuration

2. **State Names Are Business-Level, State Transitions Are Technical**
   - KEEP: INITIATED → FUNDED → COMPLETED (state names and flow)
   - REMOVE: Event handlers, database updates, state machine implementation code

3. **Customer-Facing SLAs Are Business Requirements**
   - KEEP: "95% of transactions complete in <15 minutes" (customer experience)
   - REMOVE: "API latency <200ms" (internal technical metric)

4. **Regulatory Requirements Are Business Rules**
   - KEEP: "OFAC sanctions screening required before processing" (compliance requirement)
   - KEEP: "$10,000 transaction limit per FinCEN MSB regulations" (regulatory constraint)
   - REMOVE: Technical implementation of OFAC API integration

5. **Platform BRD References Provide Technology Context Without Prescribing**
   - CORRECT: "Platform requires segregated USDC custody with MTL sponsorship (BRD-002 partner selection)"
   - WRONG: "Platform MUST use Bridge custody provider"
   - Rationale: Platform BRD makes technology selection; Feature BRD references the decision

6. **Complexity Ratings Should Be Comprehensive**
   - Include partner count WITH partner names/categories
   - Include specific regulations (FinCEN, OFAC, Uzbekistan Central Bank)
   - Include business constraints (T+1 settlement, 95% SLA)
   - Include ALL Platform/Feature BRD dependencies

7. **Cross-References Enable Traceability**
   - Every FR should reference 2-5 Platform BRDs (architecture foundation)
   - Every FR should reference 2-8 related Feature BRDs (domain dependencies)
   - Use descriptive parenthetical after BRD-NNN: "BRD-008 (Wallet Funding - USDC balance source)"

8. **Business Acceptance Criteria Need Measurable Targets**
   - Always include percentage: "95% of transactions..."
   - Always include time bound: "...within 15 minutes"
   - Always include business outcome: "...receive delivery confirmation"
   - Format: "[Percentage] of [business entity] [achieve outcome] within [time] for [percentage] of [cases]"

9. **Major Refactoring = Major Version Increment**
   - 1.0 → 2.0 when changing FR structure (tabular → 4-subsection)
   - 1.0 → 1.1 when adding minor content or fixing typos
   - Document "Major Refactoring" in Revision History with before/after scores

10. **Validation Script Catches What Manual Review Misses**
    - Automated scanning finds ALL technical terms (manual review misses ~30%)
    - Code block detection is 100% reliable with regex
    - Cross-reference validation prevents broken links
    - PRD-Ready Score calculation provides objective quality metric

---

### Refactoring Effort Estimation

**Based on BRD-009 and 11 subsequent BRD refactorings**:

| PRD-Ready Score Range | Estimated Refactoring Effort | Typical Issues |
|----------------------|------------------------------|----------------|
| **90-100/100** | 30 minutes - 1 hour | Minor UI term cleanup, add missing Complexity ratings |
| **70-89/100** | 2-4 hours | Convert tabular FRs to 4-subsection structure, remove technical terminology, add cross-references |
| **50-69/100** | 4-8 hours | Heavy PRD-level contamination; remove code blocks, API specs, database schemas; complete FR restructuring |
| **<50/100** | 8-16 hours | Essentially rewrite FRs from scratch; extensive Platform BRD dependency analysis required |

**Efficiency Tip**: Use BRD-TEMPLATE.md Appendix C examples as copy-paste starting points for similar FRs (payment processing, KYC verification, notification delivery, etc.)

---

## Validation Workflow

### Running Validation Script

**Command**:
```bash
./scripts/validate_brd.py docs/BRD/BRD-XXX_feature_name.md
```

**Expected Output**:
```
=== BRD VALIDATION REPORT ===
File: docs/BRD/BRD-XXX_feature_name.md

CHECK 14 (Code Blocks): ✅ PASS - No code blocks found in Section 4
CHECK 15 (API/Technical Terms): ⚠️  WARNING - 3 instances found (lines 245, 312, 389)
CHECK 16 (UI Terms): ✅ PASS - No UI-specific terms found
CHECK 17 (FR Structure): ✅ PASS - All FRs have 6 required subsections
CHECK 18 (Cross-References): ✅ PASS - All BRD references valid

=== PRD-READY SCORE ===
Category 1 (PRD Contamination): -6 points (3 technical terms)
Category 2 (FR Structure): -0 points
Category 3 (Document Structure): -0 points

Total Deductions: -6 points
PRD-Ready Score: 94/100 ✅

Validation Result: PASS (Target: ≥90/100)

Recommendations:
- Line 245: Replace "database query" with "system validates"
- Line 312: Replace "JSON payload" with "transaction details"
- Line 389: Replace "API call" with "system request"
```

**Iterative Validation**:
1. Run validation → Review deduction report
2. Fix violations → Run validation again
3. Repeat until score ≥90/100
4. Update Document Control with final score

---

## Quick Reference

### Top 10 Refactoring Rules

1. **Remove ALL code blocks** - No exceptions (Python, JSON, SQL, YAML)
2. **Replace API specs with business capabilities** - "Customer initiates transaction" not "POST /api/v1/transactions"
3. **Replace database terms with business language** - "System validates customer status" not "Query users table"
4. **Replace UI terms with business actions** - "Customer selects recipient" not "Customer clicks dropdown"
5. **Keep fee structure tables, remove calculation code** - Markdown tables OK, Python functions NO
6. **Keep state names, remove state transitions** - INITIATED → COMPLETED OK, StateMachine.transition() NO
7. **Keep customer SLAs, remove technical metrics** - "95% in <15 min" OK, "API <200ms" NO
8. **Add 6 subsections to every FR** - Business Capability, Business Requirements, Business Rules, Business Acceptance Criteria, Related Requirements, Complexity
9. **Add Platform BRD cross-references** - Every FR should reference BRD-001 through BRD-005
10. **Add Complexity ratings with business rationale** - Partner count, regulatory scope, business constraints, dependencies

---

## Success Metrics

**Target Outcome**: PRD-Ready Score ≥90/100 on first validation after refactoring

**Achieved Results** (12 BRD refactorings completed):
- Average score improvement: +35 points (from 62/100 baseline to 97/100 post-refactor)
- BRD-009 pilot: 65/100 → 100/100 (+35 points)
- Average refactoring time: 4.5 hours per BRD
- First-pass validation success rate: 83% (10 of 12 BRDs passed ≥90/100 threshold on first validation)

**Gold Standard Reference**: BRD-009 (US-to-Uzbekistan Remittance) - 100/100 PRD-Ready Score

---

**Document Version**: 1.0
**Created**: 2024-11-24
**Purpose**: Consolidate lessons learned from BRD-009 pilot refactoring and provide step-by-step guide for transforming PRD-level BRDs into business-level documents
