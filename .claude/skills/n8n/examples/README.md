# n8n Workflow Automation Code Examples

Production-ready code examples for n8n workflow automation platform.

## Files

### n8n_custom_node.ts
TypeScript custom node development patterns:
- `CustomNode` class - Programmatic style with full control (Complexity: 3-4)
- `operations` and `router` - Declarative style for CRUD operations (Complexity: 2)
- `customApiCredentials` - Credential configuration
- `validateCredentials()` - Credential testing
- `PollingTrigger` class - Polling trigger with state management (Complexity: 4-5)
- Development workflow commands reference

**Complexity:** 2-5 depending on pattern

### n8n_workflow_examples.js
JavaScript Code node patterns for workflows:
- `basicTransformation()` - Simple data mapping (Complexity: 1)
- `filterData()` - Item filtering (Complexity: 1)
- `aggregateData()` - Grouping with Lodash (Complexity: 2)
- `enrichWithAPI()` - Async API enrichment (Complexity: 2)
- `transformWithErrorHandling()` - Try/catch patterns (Complexity: 2)
- `handlePagination()` - API pagination handler (Complexity: 3)
- `processWebhook()` - Webhook response formatting (Complexity: 2)
- `prepareBatchInsert()` - Database batch operations (Complexity: 2)
- `validateInputData()` - Input validation (Complexity: 2)
- `apiCallWithContext()` - Error context logging (Complexity: 3)
- `checkBeforeCreate()` - Idempotency patterns (Complexity: 2)
- `initializeAgentState()`, `updateAgentState()` - AI agent state management (Complexity: 3)
- Data access pattern examples (expressions reference)

**Complexity:** 1-3

### n8n_deployment.yaml
Deployment and configuration examples:
- docker-compose.yaml - Standard deployment with PostgreSQL
- docker-compose.queue.yaml - Queue mode for high-volume workloads
- Environment variable reference (essential and performance tuning)
- Resource requirements by volume
- Nginx reverse proxy configuration
- Monitoring and backup strategies
- Development vs Production setup

**Complexity:** 2-3

## Usage

All examples are production-ready patterns with proper error handling and best practices. Copy/modify for your specific workflow needs.

**Reference format in SKILL.md:**
```markdown
[See Code Examples: examples/n8n_custom_node.ts]
[See: `CustomNode` class in examples/n8n_custom_node.ts]
```

## Available Libraries

**JavaScript Code Node:**
- Node.js built-ins: fs, path, crypto, https
- Lodash: _.groupBy(), _.sortBy(), _.uniq(), etc.
- Luxon: DateTime manipulation
- n8n helpers: $input, $json, $binary, this.helpers

**Python Code Node:**
- Standard library: json, datetime, re, requests
- NumPy: Array operations
- Pandas: Data analysis (if installed)
- _input: Access to input items

---

**Last Updated:** 2025-11-14
**Purpose:** Compliance with CLAUDE.md documentation standards (no inline code blocks >50 lines)
