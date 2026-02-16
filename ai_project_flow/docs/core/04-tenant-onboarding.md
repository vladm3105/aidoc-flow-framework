# AI Cost Monitoring — Tenant Onboarding Workflow

## Document Info

| Field | Value |
|-------|-------|
| **Document** | 04 — Tenant Onboarding Workflow |
| **Version** | 1.0 |
| **Date** | February 2026 |
| **Status** | Architecture |
| **Audience** | Architects, Product, Frontend Developers |

---

## 1. Onboarding Overview

Onboarding is the most critical user journey — it's the first experience a customer has with the platform. A new tenant goes from "just signed up" to "seeing their first cost dashboard" in this flow.

### 1.1 Onboarding Stages

```
Sign Up → Create Organization → Connect Cloud Accounts → First Data Sync → Dashboard Ready
   │              │                      │                      │               │
   ▼              ▼                      ▼                      ▼               ▼
 Auth0        PostgreSQL            Secret Manager +       Cloud Tasks       Interactive
 User +       tenant +              Cloud Account          → MCP Servers     Mode Ready
 Org          admin user            verification           → BigQuery
```

### 1.2 Time Targets

| Stage | Target Duration | Notes |
|-------|-----------------|-------|
| Sign up + org creation | < 2 minutes | Auth0 Universal Login + form |
| Connect first cloud account | < 5 minutes | Guided wizard, copy-paste credentials |
| First data sync | 5-15 minutes | Depends on account size |
| **Total: Sign up to dashboard** | **< 20 minutes** | For a single-cloud, small account |

---

## 2. Stage 1: Sign Up & Organization Creation

### 2.1 Flow

```
User clicks "Get Started"
  → Auth0 Universal Login (sign up with email or SSO)
    → Auth0 creates User
      → Platform creates Auth0 Organization
        → Platform creates tenant record in PostgreSQL
          → Platform assigns user as org_admin of new tenant
            → Redirect to onboarding wizard
```

### 2.2 What Gets Created

| System | Entity | Details |
|--------|--------|---------|
| Auth0 | User | Email, password (or SSO link) |
| Auth0 | Organization | `org_{slug}`, display name |
| Auth0 | Membership | User → Organization with `org_admin` role |
| PostgreSQL | tenant | id, name, slug, auth0_org_id, plan=free, status=onboarding |
| PostgreSQL | user | Synced from Auth0, role=org_admin |
| Secret Manager | Tenant path | `tenant-{tenant_id}-{provider}` naming pattern (empty, ready for credentials) |
| Redis (optional) | Session | User session initialized (or in-memory for MVP) |

### 2.3 Business Rules

- Default plan is `free` — can be upgraded later
- The first user is always `org_admin`
- Tenant `status` is `onboarding` until first cloud account is connected and synced
- Organization slug is derived from company name (URL-safe, unique)

---

## 3. Stage 2: Connect Cloud Accounts

### 3.1 Cloud Account Connection Wizard

The wizard guides the user through connecting their first cloud account. Each provider has a different credential mechanism:

#### AWS Connection

```
Step 1: User selects "Connect AWS Account"
Step 2: Platform displays a CloudFormation template URL
        (creates IAM Role with specific permissions + External ID)
Step 3: User deploys the template in their AWS console
Step 4: User copies the Role ARN back into the wizard
Step 5: Platform stores Role ARN + External ID in **Secret Manager**
Step 6: Platform tests: AssumeRole → GetCallerIdentity
Step 7: Success → cloud_account created with status=active
```

**What the IAM Role allows (read-only + limited write for remediation):**
- Cost Explorer: GetCostAndUsage, GetCostForecast, GetAnomalies
- Compute Optimizer: Get* (read-only)
- CloudWatch: GetMetricData, GetMetricStatistics
- EC2: Describe* (read), StopInstances, ModifyInstanceAttribute (remediation)
- Trusted Advisor: Describe* (read-only)
- Resource Groups: GetResources, SearchResources

#### Azure Connection

```
Step 1: User selects "Connect Azure Subscription"
Step 2: Platform displays instructions to create a Service Principal
        (App Registration with Reader + Cost Management Reader roles)
Step 3: User provides: Client ID, Client Secret, Azure Tenant ID, Subscription ID
Step 4: Platform stores credentials in **Secret Manager**
Step 5: Platform tests: authenticate → list subscriptions
Step 6: Success → cloud_account created
```

#### GCP Connection

```
Step 1: User selects "Connect GCP Project"
Step 2: Platform displays instructions to create a Service Account
        (with Viewer + Billing Account Viewer roles)
Step 3: User uploads Service Account JSON key file
Step 4: Platform stores JSON key in **Secret Manager**
Step 5: Platform tests: authenticate → list projects
Step 6: Success → cloud_account created
```

#### Kubernetes Connection

```
Step 1: User selects "Connect Kubernetes Cluster"
Step 2: User provides: Cluster API endpoint + kubeconfig or service account token
Step 3: Platform verifies OpenCost is installed (required)
Step 4: Platform stores credentials in **Secret Manager**
Step 5: Platform tests: list namespaces → check OpenCost endpoint
Step 6: Success → cloud_account created
```

### 3.2 Credential Storage

All credentials go directly to **Secret Manager** — never to PostgreSQL.

| Provider | Secret Manager Path | Stored Data |
|----------|---------------------|-------------|
| AWS | `tenant-{id}-aws-{account_id}` | role_arn, external_id |
| Azure | `tenant-{id}-azure-{subscription_id}` | client_id, client_secret, azure_tenant_id |
| GCP | `tenant-{id}-gcp-{project_id}` | service_account_json |
| K8s | `tenant-{id}-k8s-{cluster_name}` | kubeconfig or token |

### 3.3 Validation & Error Handling

| Validation | Check | On Failure |
|------------|-------|------------|
| Credential format | Regex/schema validation | Inline form error |
| Connectivity test | Attempt API call with provided credentials | "Unable to connect — check permissions" |
| Permission test | Call specific APIs needed by the platform | "Missing permission: ce:GetCostAndUsage" with fix instructions |
| Duplicate check | Same account_identifier already connected | "This account is already connected to your organization" |

---

## 4. Stage 3: First Data Sync

### 4.1 Triggered Immediately After Account Connection

```
Cloud account created (status=active)
  → Cloud Tasks triggered: initial_sync_{provider}
    → Phase 1: Resource Inventory (discover all resources)
    → Phase 2: Cost Data (pull last 30 days of cost data)
    → Phase 3: Anomaly Detection (baseline establishment)
    → Phase 4: Recommendations (initial optimization scan)
      → On completion: tenant status → active
        → Notification to user: "Your dashboard is ready!"
```

### 4.2 Sync Progress Tracking

The onboarding UI shows real-time progress:

| Phase | Description | Estimated Time |
|-------|-------------|----------------|
| Connecting | Verifying credentials | < 30 sec |
| Discovering resources | Scanning cloud inventory | 1-3 min |
| Loading cost data | Pulling 30-day history | 3-10 min |
| Analyzing patterns | Anomaly baseline + recommendations | 1-3 min |
| Ready | Dashboard populated | — |

Progress is pushed via SSE to the frontend. Each phase updates a `sync_progress` key in Redis.

### 4.3 First Sync Data Scope

| Data | Lookback Period | Purpose |
|------|----------------|---------|
| Cost metrics | 30 days | Enough for trend analysis |
| Resource inventory | Current state | Snapshot of all resources |
| Anomaly baseline | 30 days | Establish normal patterns |
| Recommendations | Current | Initial optimization opportunities |

**After onboarding:** Regular Mode 2 scheduled jobs take over with full lookback periods.

---

## 5. Stage 4: Dashboard Ready

### 5.1 First-Run Experience

When the user lands on the dashboard for the first time:

```
1. Welcome message: "Your {provider} account is connected. Here's what we found."

2. Key metrics displayed:
   → Total monthly spend (current month)
   → Month-over-month trend
   → Number of resources discovered
   → Initial savings opportunities (if any)

3. Guided suggestions:
   → "Ask me anything about your cloud costs"
   → Example queries shown as clickable chips:
     - "What are my top 5 most expensive services?"
     - "Show me idle resources"
     - "How does this month compare to last month?"

4. Next steps card:
   → "Connect more cloud accounts" (if only one connected)
   → "Invite your team" (user management)
   → "Set up budget alerts" (policy configuration)
```

### 5.2 Tenant Status Transition

| Status | Meaning | Transitions To |
|--------|---------|---------------|
| onboarding | Tenant created, no cloud accounts connected yet | active (after first sync) |
| active | At least one cloud account connected and synced | suspended (admin action or billing) |
| suspended | Access restricted, data retained | active (reactivation) |

---

## 6. Post-Onboarding: Adding More Accounts

After initial onboarding, users can add additional cloud accounts through:

```
Settings → Cloud Accounts → "Add Account"
  → Same wizard as onboarding, but:
     - No Auth0/tenant creation (already exists)
     - Sync runs in background (user can continue using dashboard)
     - Existing data not affected
     - New account data merges into unified view
```

---

## 7. Invite Team Members

```
Settings → Team → "Invite Member"
  → Enter email + select role (analyst, operator, org_admin)
    → Auth0 invitation sent (email with signup link)
      → Invitee creates account → automatically added to Auth0 Organization
        → User record created in PostgreSQL with assigned role
          → Invitee has immediate access per their role
```

**Role assignment during invite:**

| Inviter Role | Can Invite As |
|-------------|---------------|
| org_admin | org_admin, operator, analyst, viewer |
| operator | analyst, viewer |
| analyst | viewer |
| viewer | (cannot invite) |

---

## Developer Notes

> **DEV-ONB-001:** The CloudFormation template for AWS should be hosted on our Cloud Storage bucket and versioned. Users click a "Launch Stack" button that opens AWS CloudFormation with the template pre-loaded. The External ID must be unique per tenant to prevent confused deputy attacks.

> **DEV-ONB-002:** Credential validation must happen server-side only. Never send cloud credentials to the frontend or store them in browser storage. The wizard submits credentials directly to the backend, which stores them in **Secret Manager** and returns only a success/failure status.

> **DEV-ONB-003:** First sync should be a dedicated **Cloud Tasks** job (not the regular scheduled sync) with different timeout and retry settings. It should prioritize speed over completeness — pull the most important data first, backfill details in subsequent scheduled syncs.

> **DEV-ONB-004:** Track onboarding funnel metrics: sign-up → org created → account connected → first sync complete → first query. Identify where users drop off.

> **DEV-ONB-005:** The "disconnect account" flow must: revoke Secret Manager credentials, mark resources as terminated, stop scheduled syncs for that account, and archive (not delete) historical cost data. Data deletion requires a separate "delete data" action per compliance requirements.

> **DEV-ONB-006:** Consider a "demo mode" or "sandbox tenant" with pre-loaded sample data for users who want to explore the platform before connecting real cloud accounts. This reduces friction in the evaluation phase.
