# Google ADK Code Examples

Production-ready code examples for Google Agent Development Kit (ADK).

## Files

### google_adk_agent_implementation.py
Agent creation patterns for different use cases:
- `create_weather_assistant()` - Basic LlmAgent with custom tools
- `create_data_pipeline()` - Sequential Workflow Agent (ordered execution)
- `create_market_researcher()` - Parallel Workflow Agent (concurrent execution)
- `create_content_generator()` - Loop Workflow Agent (iterative refinement)
- `create_stateful_session()` - Session management with conversation history

**Complexity:** 2-3

### google_adk_tools_example.py
Custom tool development patterns:
- `calculate_tax()` - Basic function tool with type hints
- `fetch_user_data()` - Async tool for API calls
- `send_email()`, `delete_user_account()` - HITL confirmation tools
- `send_email_tool()` - Input validation and sanitization
- `fetch_external_data()` - Retry logic with exponential backoff
- `call_external_api()` - Rate limiting decorator
- `fetch_stock_price()` - Graceful error handling
- `create_api_agent()` - OpenAPI tool integration
- `create_mcp_agent()` - MCP server integration
- `create_portfolio_analyzer()` - Async parallel execution

**Tool Design Best Practices:**
- Single responsibility pattern (GOOD vs BAD examples)
- Descriptive naming conventions (GOOD vs BAD examples)
- Complete type annotations (GOOD examples)

**Complexity:** 2-3

### google_adk_multi_agent.py
Multi-agent orchestration patterns:
- **Pattern 1:** `create_coordinator_system()` - Coordinator/Dispatcher (Complexity: 4)
- **Pattern 2:** `create_content_pipeline()` - Sequential Pipeline (Complexity: 3)
- **Pattern 3:** `create_market_analysis_system()` - Parallel Fan-Out/Gather (Complexity: 4)
- **Pattern 4:** `create_project_management_system()` - Hierarchical Decomposition (Complexity: 5)
- **Pattern 5:** `create_quality_content_system()` - Generator-Critic Loop (Complexity: 4)
- **Pattern 6:** `create_account_management_agent()` - Human-in-the-Loop (Complexity: 3)
- **Pattern 7:** `StatefulAgent` class - In-memory state management
- **Pattern 8:** `save_state()`, `load_state()` - Database persistence (PostgreSQL/SQLAlchemy)

**Complexity:** 3-5

### google_adk_deployment.py
Deployment configuration and patterns:
- `create_production_agent()` - Production agent configuration
- FastAPI server with agent endpoints (`/invoke`, `/health`)
- `invoke_agent_safe()` - Error handling and validation
- Session-based API endpoints (`/session/create`, `/session/invoke`, `/session/delete`)
- `evaluate_agent_endpoint()` - Criteria-based evaluation API
- `Config` class - Environment configuration
- Startup/shutdown event handlers
- Logging and monitoring setup

**Deployment Examples (Reference):**
- Dockerfile configuration
- docker-compose.yml with Redis
- Resource requirements table
- Deployment commands for Agent Engine, Cloud Run, Docker

**Complexity:** 2-3

## Usage

All examples are production-ready patterns with proper error handling, type hints, and documentation. Copy/modify for your specific use case.

**Reference format in SKILL.md:**
```markdown
[See Code Examples: examples/google_adk_agent_implementation.py]
[See: `create_weather_assistant()` in examples/google_adk_agent_implementation.py]
```

---

**Last Updated:** 2025-11-14
**Purpose:** Compliance with CLAUDE.md documentation standards (no inline code blocks >50 lines)
