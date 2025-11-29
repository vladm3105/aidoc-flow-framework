# Implementation Plan - Make Framework Project-Independent

**Created**: 2025-11-29 15:08:46 EST
**Status**: Ready for Implementation

## Objective

Make the AI Dev Flow Framework at `/opt/data/docs_flow_framework` generic and reusable for any project by removing IB API MCP Server-specific references and replacing them with project-independent placeholders and generic service names.

## Context

### Approach Selected: Mixed
- Use `[PROJECT_NAME]`, `[PROJECT_A]`, `[PROJECT_B]` for project name references
- Keep realistic code examples with generic service names (`ServiceConnector`, `ExternalAPI`)
- Replace domain-specific agent with generic `requirements-analyst.md`
- Preserve `work_plans/` directory as framework evolution history

### Key Decisions
- **Example Style**: Mixed approach - placeholders for project names, realistic code examples with generic service names
- **Agent File**: Replace `option-analyst.md` with generic `requirements-analyst.md`
- **Work Plans**: Keep as-is for framework development history

## Task List

### Pending
- [ ] Priority 1: Update root README.md (GitHub URLs)
- [ ] Priority 1: Update MULTI_PROJECT_SETUP_GUIDE.md (project names, skill examples)
- [ ] Priority 1: Update MULTI_PROJECT_QUICK_REFERENCE.md (batch examples)
- [ ] Priority 2: Rewrite ai_dev_flow/IPLAN/README.md (50+ IB-specific refs)
- [ ] Priority 3: Replace .claude/agents/option-analyst.md with requirements-analyst.md
- [ ] Priority 4: Update .claude/skills/project-mngt/examples/README.md
- [ ] Priority 4: Update .claude/skills/trace-check/examples/example_validation_report.md
- [ ] Priority 4: Update .claude/skills/project-init/SKILL.md
- [ ] Priority 5: Batch update template files (6 files)
- [ ] Run verification grep commands
- [ ] Commit changes

## Implementation Guide

### Generic Replacement Reference Table

| Original | Replacement |
|----------|-------------|
| `ibmcp` | `[PROJECT_NAME]` |
| `b_local` | `[PROJECT_A]` |
| `trading` | `[PROJECT_B]` |
| `techtrend` | `[PROJECT_C]` |
| `cara_framework` | `[PROJECT_D]` |
| `IBGatewayConnectionService` | `ServiceConnector` |
| `IBGatewayConnector` | `ExternalConnector` |
| `IB Gateway` | `External Service` |
| `IB API` | `External API` |
| `ib_async` | `async_client` |
| `src/ibmcp/gateway/` | `src/[project]/services/` |
| `connection_service.py` | `connector.py` |
| `IB_CONN_001` - `IB_CONN_006` | `SVC_ERR_001` - `SVC_ERR_006` |
| `IB_CIRCUIT_BREAKER_TIMEOUT` | `SERVICE_TIMEOUT` |
| `GatewayError` | `ServiceError` |
| `vladm3105/aidoc-flow-framework` | `[YOUR_ORG]/ai-dev-flow-framework` |

### Execution Steps

#### Phase 1: Core Documentation (30 min)

1. **README.md** - Update GitHub URLs:
   ```
   BEFORE: git clone https://github.com/vladm3105/aidoc-flow-framework.git
   AFTER:  git clone https://github.com/[YOUR_ORG]/ai-dev-flow-framework.git
   ```

2. **MULTI_PROJECT_SETUP_GUIDE.md** - Update for-loops and examples:
   ```
   BEFORE: for PROJECT in ibmcp b_local trading techtrend cara_framework; do
   AFTER:  for PROJECT in [PROJECT_A] [PROJECT_B] [PROJECT_C]; do
   ```
   Also replace IB-specific skill/command examples with generic templates.

3. **MULTI_PROJECT_QUICK_REFERENCE.md** - Update batch example (line ~34)

#### Phase 2: IPLAN Documentation (2 hrs)

4. **ai_dev_flow/IPLAN/README.md** - Major rewrite:
   - Replace all IB-specific class names with generic service names
   - Update file paths from `src/ibmcp/gateway/` to `src/[project]/services/`
   - Replace error codes from `IB_CONN_*` to `SVC_ERR_*`
   - Keep realistic code structure, just make domain generic

#### Phase 3: Agent Replacement (30 min)

5. **Replace .claude/agents/option-analyst.md** with new `requirements-analyst.md`:
   - Purpose: Requirements decomposition and validation
   - Coverage analysis across SDD layers
   - Traceability mapping expertise
   - Quality validation for SMART requirements

#### Phase 4: Skills Examples (1 hr)

6. **.claude/skills/project-mngt/examples/README.md** - Replace trading system with generic software project

7. **.claude/skills/trace-check/examples/example_validation_report.md** - Simple find/replace:
   - "IB API MCP Server" → "[PROJECT_NAME]"
   - "market_data_service" → "data_service"

8. **.claude/skills/project-init/SKILL.md** - Update Example 1:
   - "algorithmic trading platform" → "software application"
   - Financial Services → Software/SaaS domain

#### Phase 5: Template Files (1 hr)

9. Batch update these files using replacement table:
   - `ai_dev_flow/IPLAN/IPLAN_CREATION_RULES.md`
   - `ai_dev_flow/TASKS/TASKS_CREATION_RULES.md`
   - `ai_dev_flow/ICON/README.md`
   - `ai_dev_flow/ICON/ICON_INTEGRATION_WORKFLOW.md`
   - `ai_dev_flow/TASKS/IMPLEMENTATION_CONTRACTS_GUIDE.md`
   - `ai_dev_flow/AI_ASSISTANT_RULES.md`

### Verification

Run these commands to verify no project-specific references remain:

```bash
# Check for remaining project-specific references
grep -rn "ibmcp\|b_local\|trading\|techtrend\|cara_framework" \
  /opt/data/docs_flow_framework --include="*.md" | grep -v work_plans

grep -rn "IBGateway\|ib_async\|IB_CONN\|IB API" \
  /opt/data/docs_flow_framework --include="*.md" | grep -v work_plans

grep -rn "vladm3105" \
  /opt/data/docs_flow_framework --include="*.md"

# Verify agent replacement
ls -la /opt/data/docs_flow_framework/.claude/agents/
```

## References

### Critical Files
1. `ai_dev_flow/IPLAN/README.md` - Largest rewrite (50+ replacements)
2. `MULTI_PROJECT_SETUP_GUIDE.md` - Primary setup documentation
3. `.claude/agents/option-analyst.md` - Full replacement needed
4. `README.md` - Framework entry point
5. `.claude/skills/project-mngt/examples/README.md` - Example rewrite

### Files to Keep Unchanged
- `work_plans/` - Framework development history
- `ai_dev_flow/FINANCIAL_DOMAIN_CONFIG.md` - Domain-specific by design
- `ai_dev_flow/SOFTWARE_DOMAIN_CONFIG.md` - Already generic
- `ai_dev_flow/GENERIC_DOMAIN_CONFIG.md` - Already generic
- Template files with `[PLACEHOLDER]` format - Already generic

### Estimated Effort
- Total: 5-6 hours
- Phase 1: 30 min
- Phase 2: 2 hrs
- Phase 3: 30 min
- Phase 4: 1 hr
- Phase 5: 1 hr
- Verification: 30 min
