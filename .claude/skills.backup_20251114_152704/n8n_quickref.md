# n8n Workflow Automation - Quick Reference

**Skill ID:** n8n
**Version:** 1.0.0
**Purpose:** Rapid guidance for n8n workflow development, custom nodes, and integrations

## Quick Start

```bash
# Invoke skill
/skill n8n

# Common requests
- "Design a workflow to sync Stripe customers to PostgreSQL"
- "Write a Code node to transform API response data"
- "Build a custom node for our internal API"
- "Create an AI agent workflow with approval gates"
```

## What This Skill Does

1. Analyze automation requirements
2. Select appropriate node types (native vs Code vs custom)
3. Design workflow structure with error handling
4. Provide code examples for transformations
5. Guide custom node development
6. Implement integration patterns
7. Configure deployment and scaling

## Core Concepts at a Glance

### Node Types

| Type | Purpose | When to Use | Complexity |
|------|---------|-------------|------------|
| **Native nodes** | Pre-built integrations | Available for your service | 1 |
| **HTTP Request** | REST API calls | No native node exists | 1 |
| **Code (JS/Python)** | Custom logic | <50 lines, one-off use | 2 |
| **Custom node** | Reusable logic | >100 lines, multiple workflows | 4 |
| **AI Agent** | LLM automation | Decision-making workflows | 3 |
| **Execute Workflow** | Sub-workflows | Modular design | 2 |

### Execution Models

| Trigger | Use Case | Example |
|---------|----------|---------|
| **Manual** | User-initiated | Testing, on-demand tasks |
| **Webhook** | External events | API callbacks, form submissions |
| **Schedule** | Time-based | Hourly sync, daily reports |
| **Database** | Data changes | New record processing |
| **Error Trigger** | Failure handling | Alert on workflow errors |

### Data Access Patterns

```javascript
// Current node output
{{ $json.fieldName }}

// Specific node output
{{ $('Node Name').item.json.fieldName }}

// All items from input
{{ $input.all() }}

// First item only
{{ $input.first() }}

// Current item index
{{ $itemIndex }}

// Previous node (positional)
{{ $input.item.json.fieldName }}
```

## Workflow Design Decision Tree

```
START: What's the automation goal?
  │
  ├─> Simple API integration?
  │   ├─> Native node available? ─Yes─> Use native node ★
  │   └─> No native node?
  │       ├─> RESTful API? ─Yes─> HTTP Request node ★
  │       └─> Complex auth? ─Yes─> Custom node ★
  │
  ├─> Data transformation?
  │   ├─> Simple mapping? ─Yes─> Set node ★
  │   ├─> <50 lines logic? ─Yes─> Code node ★
  │   └─> Reusable across workflows? ─Yes─> Custom node ★
  │
  ├─> Conditional logic?
  │   ├─> Two branches? ─Yes─> If node ★
  │   └─> Multiple branches? ─Yes─> Switch node ★
  │
  ├─> AI automation?
  │   ├─> Simple LLM call? ─Yes─> AI Agent (no tools) ★
  │   ├─> Need external data? ─Yes─> AI Agent + Tools ★
  │   └─> Human approval needed? ─Yes─> Gatekeeper pattern ★
  │
  └─> Large dataset processing?
      ├─> <1000 items? ─Yes─> Process all ★
      └─> >1000 items? ─Yes─> Split In Batches ★
```

## Common Workflow Patterns

### Pattern 1: API Integration

```
Manual/Schedule Trigger
    ↓
HTTP Request (GET/POST)
    ↓
Code (transform response)
    ↓
If (validate data)
    ├─> Valid ─> Database Insert
    └─> Invalid ─> Error notification
```

**Code example (transform):**
```javascript
const items = $input.all();
return items.map(item => ({
  json: {
    id: item.json.id,
    name: item.json.full_name,
    email: item.json.email_address.toLowerCase(),
    created: new Date().toISOString()
  }
}));
```

### Pattern 2: Data Sync

```
Schedule Trigger (hourly)
    ↓
PostgreSQL (fetch updated records)
    ↓
Split In Batches (100 items)
    ↓
HTTP Request (send to external API)
    ↓
Code (log results)
```

**Batch processing:**
```javascript
// Processes 100 items at a time
// Configured in Split In Batches node
const batch = $input.all();
console.log(`Processing batch of ${batch.length} items`);
return batch;
```

### Pattern 3: Error Handling

```
Main Workflow
    ↓
[Error Output] ──> Error Trigger Workflow
                        ↓
                   If (critical error?)
                      ├─> Yes ─> Slack Alert
                      └─> No ─> Log to Database
```

**Error trigger setup:**
1. Create new workflow with Error Trigger node
2. Configure: "Listen to all workflows" or specific workflows
3. Access error data: `{{ $json.error }}`, `{{ $json.execution }}`

### Pattern 4: AI Agent with Gatekeeper

```
Webhook (user request)
    ↓
AI Agent (plan action)
    ↓
If (confidence > 0.8)
    ├─> High ─> Execute Action
    └─> Low ─> Send Email (approval) ─> Webhook (response) ─> If (approved) ─> Execute
```

**AI Agent configuration:**
- **Prompt:** "You are an assistant that helps with {{$json.task}}"
- **Tools:** HTTP Request, Database Query, Calculator
- **Memory:** Conversation Buffer (maintains context)
- **Output:** Action plan with confidence score

### Pattern 5: RAG (Retrieval Augmented Generation)

```
User Query
    ↓
Vector Store Search (top 5 results)
    ↓
Code (format context)
    ↓
AI Agent (generate answer with context)
    ↓
Response
```

**Context formatting:**
```javascript
const results = $input.all();
const context = results.map(r => r.json.text).join('\n\n');

return [{
  json: {
    context,
    query: $('Manual Trigger').item.json.query
  }
}];
```

## Code Node Quick Reference

### JavaScript Essentials

**Access input:**
```javascript
const items = $input.all();           // All items
const firstItem = $input.first();     // Single item
const currentItem = $json;            // Current iteration
```

**Transform data:**
```javascript
// Map
return items.map(item => ({
  json: { transformed: item.json.field.toUpperCase() }
}));

// Filter
return items.filter(item => item.json.status === 'active');

// Aggregate
const total = items.reduce((sum, item) => sum + item.json.amount, 0);
return [{ json: { total } }];

// Group by
const grouped = _.groupBy(items, item => item.json.category);
```

**API calls:**
```javascript
const results = [];
for (const item of items) {
  const response = await fetch(`https://api.example.com/data/${item.json.id}`);
  const data = await response.json();
  results.push({ json: data });
}
return results;
```

**Error handling:**
```javascript
return items.map(item => {
  try {
    return { json: { result: processItem(item.json) } };
  } catch (error) {
    return { json: { error: error.message, item: item.json } };
  }
});
```

### Python Essentials

**Access input:**
```python
items = _input.all()                  # All items
first_item = _input.first()           # Single item
current_item = _input.item.json       # Current iteration
```

**Transform data:**
```python
# Map
processed = []
for item in items:
    processed.append({
        'json': {'transformed': item['json']['field'].upper()}
    })
return processed

# Filter
return [item for item in items if item['json']['status'] == 'active']

# Aggregate
total = sum(item['json']['amount'] for item in items)
return [{'json': {'total': total}}]
```

## Custom Node Quick Start

### Create Node

```bash
# Initialize from template
npm create @n8n/node my-custom-node
cd my-custom-node

# Install dependencies
npm install

# Build
npm run build
```

### Basic Structure (Programmatic)

```typescript
import { INodeType, INodeTypeDescription, IExecuteFunctions } from 'n8n-workflow';

export class MyNode implements INodeType {
  description: INodeTypeDescription = {
    displayName: 'My Node',
    name: 'myNode',
    group: ['transform'],
    version: 1,
    description: 'Custom functionality',
    defaults: { name: 'My Node' },
    inputs: ['main'],
    outputs: ['main'],
    properties: [
      {
        displayName: 'Operation',
        name: 'operation',
        type: 'options',
        options: [
          { name: 'Get', value: 'get' },
          { name: 'Create', value: 'create' },
        ],
        default: 'get',
      },
    ],
  };

  async execute(this: IExecuteFunctions) {
    const items = this.getInputData();
    const returnData = [];

    for (let i = 0; i < items.length; i++) {
      const operation = this.getNodeParameter('operation', i);

      // Your logic here
      const result = await this.helpers.request({
        method: 'GET',
        url: 'https://api.example.com/data',
      });

      returnData.push({ json: result });
    }

    return [returnData];
  }
}
```

### Test Locally

```bash
# Link for local testing
npm link

# In n8n custom nodes directory
cd ~/.n8n/custom
npm link my-custom-node

# Restart n8n
```

### Publish

```bash
# Update package.json version
npm version patch

# Publish to npm
npm publish

# Install in n8n
# Settings → Community Nodes → Install → my-custom-node
```

## Integration Quick Reference

### Popular Connectors by Category

**Communication:**
- Email (IMAP/SMTP), Slack, Discord, Telegram, Twilio (SMS), SendGrid

**Databases:**
- PostgreSQL, MySQL, MongoDB, Redis, Supabase, Firebase

**Cloud Storage:**
- AWS S3, Google Drive, Dropbox, OneDrive, Cloudflare R2

**Cloud Platforms:**
- AWS (Lambda, SQS, SNS), GCP (Cloud Functions, Pub/Sub), Azure (Functions, Service Bus)

**AI/ML:**
- OpenAI, Anthropic, Hugging Face, Cohere, Pinecone (vectors), LangChain

**Business:**
- Stripe, Shopify, QuickBooks, HubSpot, Salesforce, Airtable

**Development:**
- GitHub, GitLab, Jira, Linear, Notion, Confluence

### Authentication Patterns

| Method | Use Case | Configuration |
|--------|----------|---------------|
| **API Key** | Simple auth | Header: `Authorization: Bearer {key}` |
| **OAuth2** | User authorization | Automatic flow, needs redirect URI |
| **Basic Auth** | Legacy APIs | Username + Password |
| **Header Auth** | Custom headers | Custom header name + value |
| **JWT** | Token-based | Generate/refresh token in workflow |

### Webhook Setup

```
1. Add Webhook Trigger node
2. Set HTTP Method (POST/GET)
3. Configure Authentication:
   - None: Public webhook
   - Header Auth: Require custom header
   - Basic Auth: Username/password
4. Get webhook URL from node
5. Register URL with external service
6. Test with curl:
   curl -X POST https://your-n8n.com/webhook/test \
     -H "Content-Type: application/json" \
     -d '{"test": "data"}'
```

## Deployment Quick Guide

### Docker Setup (Recommended)

```yaml
# docker-compose.yml
version: '3.8'
services:
  n8n:
    image: n8nio/n8n:latest
    ports:
      - "5678:5678"
    environment:
      - N8N_HOST=https://n8n.yourdomain.com
      - WEBHOOK_URL=https://n8n.yourdomain.com/
      - N8N_ENCRYPTION_KEY=your-secure-key
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - GENERIC_TIMEZONE=America/New_York
    volumes:
      - n8n_data:/home/node/.n8n
```

### Essential Environment Variables

```bash
N8N_HOST                    # Public URL for webhooks
WEBHOOK_URL                 # Webhook endpoint base
N8N_ENCRYPTION_KEY          # Credential encryption (persist!)
DB_TYPE                     # sqlite/postgresdb/mysqldb
EXECUTIONS_DATA_SAVE_ON_ERROR=all
EXECUTIONS_DATA_SAVE_ON_SUCCESS=all
N8N_PAYLOAD_SIZE_MAX=16     # MB
EXECUTIONS_TIMEOUT=3600     # Seconds
```

### Scaling Strategy

| Volume | Setup | Resources |
|--------|-------|-----------|
| <100 exec/day | Single instance, SQLite | 1 CPU, 512MB RAM |
| 100-1000/day | Single instance, PostgreSQL | 2 CPU, 2GB RAM |
| 1000-10000/day | Single instance, PostgreSQL | 4 CPU, 4GB RAM |
| >10000/day | Queue mode (main + workers) | 8+ CPU, 8GB+ RAM |

**Queue Mode:**
```bash
# Main process (UI + queue)
N8N_QUEUE_MODE=main n8n start

# Worker processes (execution)
N8N_QUEUE_MODE=worker n8n worker
```

## Complexity Ratings

| Task | Rating | Description |
|------|--------|-------------|
| Use native node | 1 | Direct configuration |
| HTTP Request integration | 1 | Simple API calls |
| Code node transformation | 2 | Custom JS/Python logic |
| Error handling pattern | 2 | Error outputs + triggers |
| Declarative custom node | 2 | RESTful API wrapper |
| AI agent basic | 3 | LLM with tools |
| Programmatic custom node | 3 | Complex authentication |
| Gatekeeper pattern | 4 | Human-in-the-loop workflow |
| Multi-agent orchestration | 5 | Complex AI workflows |

## When NOT to Use n8n

**Avoid n8n when:**
- Real-time processing required (<100ms latency)
- Complex business logic better suited to application code
- Extensive custom UI needed (n8n has minimal UI customization)
- Workflow requires advanced debugging tools
- Team lacks workflow automation experience
- Use case is single-purpose script (Python/Node.js script simpler)

**Alternative approaches:**
- Real-time: Event-driven architecture (Kafka, AWS Lambda)
- Complex logic: Application code (Python, Node.js, Go)
- Custom UI: Full-stack framework (React, Vue, Angular)
- Advanced debugging: IDE-based development

## Troubleshooting Quick Guide

| Issue | Cause | Resolution |
|-------|-------|------------|
| Invalid JSON error | Wrong return format | `return [{ json: {...} }]` |
| Property undefined | Missing data | `$json.field?.subfield ?? 'default'` |
| Webhook not receiving | URL/auth mismatch | Verify URL, test with curl |
| High memory usage | Large dataset, no batching | Use Split In Batches (100-1000) |
| Custom node not showing | Not installed/linked | `npm install -g`, restart n8n |
| Credentials not working | Expired token | Re-authenticate OAuth2 |
| Slow workflow execution | Too many API calls in loop | Batch requests, use pagination |

## Best Practices Checklist

**Before deploying workflow:**
- [ ] Tested with realistic data volume
- [ ] Error outputs configured on critical nodes
- [ ] Error Trigger workflow created for alerts
- [ ] Credentials used (no hardcoded secrets)
- [ ] Workflow description documented
- [ ] Complex logic has notes
- [ ] Webhook authentication enabled (if applicable)
- [ ] Retry logic configured where needed
- [ ] Large datasets use Split In Batches
- [ ] Execution logging configured appropriately

**Code node quality:**
- [ ] Input data validated
- [ ] Error handling with context
- [ ] No hardcoded values (use parameters)
- [ ] Idempotent operations where possible
- [ ] Console.log for debugging (remove in production)

## References

**Official Docs:**
- Main: https://docs.n8n.io
- Nodes: https://docs.n8n.io/integrations/builtin/
- Custom nodes: https://docs.n8n.io/integrations/creating-nodes/
- Expressions: https://docs.n8n.io/code/expressions/

**Repositories:**
- Platform: https://github.com/n8n-io/n8n
- Docs: https://github.com/n8n-io/n8n-docs

**Community:**
- Forum: https://community.n8n.io
- Templates: https://n8n.io/workflows
- npm: https://www.npmjs.com/search?q=n8n-nodes

**Related Skills:**
- Cloud integrations → `cloud-devops-expert`
- Database design → `database-specialist`
- API design → `api-design-architect`
- TypeScript → Language-specific skills

---

**Quick Reference Version:** 1.0.0
**Full Skill:** `.claude/skills/n8n/SKILL.md`
**Last Updated:** 2025-11-13
