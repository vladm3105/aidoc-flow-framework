# Contributing to AI Cost Monitoring

Thank you for contributing to AI Cost Monitoring! This document provides guidelines for contributing to the project.

## Table of Contents

- [Maintainers & Reviewers](#maintainers--reviewers)
- [Code of Conduct](#code-of-conduct)
- [Development Setup](#development-setup)
- [Code Standards](#code-standards)
- [Git Workflow](#git-workflow)
- [Testing](#testing)
- [Documentation](#documentation)
- [Documentation Validation](#documentation-validation)
- [Pull Request Process](#pull-request-process)

---

## Maintainers & Reviewers

### Auto-Assignment (CODEOWNERS)

PR reviewers are **automatically assigned** based on file paths via [`.github/CODEOWNERS`](.github/CODEOWNERS). When a PR touches files matching a CODEOWNERS pattern, the listed owners are requested as reviewers without manual intervention.

### Reviewer Roster

Reviewers who can be assigned to PRs. CODEOWNERS auto-assigns reviewers marked **Auto**; reviewers marked **Manual** are assigned by AI agents or humans when their expertise is needed.

| GitHub Username | Role | Review Scope | Assignment |
|:----------------|:-----|:-------------|:-----------|
| `{CODEOWNER_1}` | Project Lead | All components, governance | Auto (CODEOWNERS) |
| `{CODEOWNER_2}` | Maintainer | All components | Auto (CODEOWNERS) |
| `{CODEOWNER_1}` | Infra Lead | Terraform, CI/CD, Cloud Run | Manual |
| `{CODEOWNER_1}` | Security | Workflows, auth, secrets | Manual |
| `{CODEOWNER_1}` | Architecture | ADRs, specs, design decisions | Manual |

### Assignment Rules

1. **Automatic**: CODEOWNERS handles most cases. No manual action needed when it matches.
2. **Manual override**: When CODEOWNERS does not match or additional expertise is needed, AI agents select from the roster above based on the PR's component scope.
3. **Self-review prohibition**: If the PR author is on the roster, assign a **different** reviewer.
4. **Minimum**: At least one reviewer per PR (enforced by branch protection).

**For AI agents**: Use `--reviewer <username>` on `gh pr create`, or `gh pr edit --add-reviewer <username>` after creation. See [GOVERNANCE_RULES.md §3](governance/GOVERNANCE_RULES.md#3-ai-workflow) for the full rule.

**Updating this list**: Add new reviewers when they are expected to review PRs. If the reviewer should be auto-assigned, also add them to [`.github/CODEOWNERS`](.github/CODEOWNERS) for the relevant file paths.

---

## Code of Conduct

This project is for professional use. Please be respectful and constructive in all interactions.

---

## Development Setup

See **[DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md)** for complete setup instructions.

**Quick Start:**

```bash
git clone https://{GITHUB_HOST}/{GITHUB_ORG}/{REPO_NAME}.git
cd {REPO_NAME}
# Follow DEVELOPER_GUIDE.md for detailed setup
```

**Pre-commit setup (required for BRD naming checks):**

```bash
python3 -m pip install pre-commit
pre-commit install
pre-commit run --all-files
```

---

## Code Standards

### Python (Backend, Agents, MCP Servers)

**Style Guide:** PEP 8

**Requirements:**

- [PASS] Type hints required for all functions
- [PASS] Docstrings for all public functions/classes (Google style)
- [PASS] Maximum line length: 100 characters
- [PASS] Use `black` for formatting
- [PASS] Use `ruff` for linting

**Example:**

```python
from typing import List, Optional

def calculate_cost(
    usage_amount: float,
    rate_per_unit: float,
    currency: str = "USD"
) -> dict:
    \"\"\"Calculate cost for a given usage amount.

    Args:
        usage_amount: Amount of resource used
        rate_per_unit: Cost per unit of resource
        currency: Currency code (default: USD)

    Returns:
        Dictionary with cost breakdown
    \"\"\"
    total_cost = usage_amount * rate_per_unit
    return {
        "amount": total_cost,
        "currency": currency,
        "breakdown": {...}
    }
```

### TypeScript/JavaScript (Frontend, AG-UI)

**Style Guide:** Airbnb + Prettier

**Requirements:**

- [PASS] TypeScript for all new code
- [PASS] ESLint + Prettier configured
- [PASS] React functional components with hooks
- [PASS] Interfaces for all props

**Example:**

```typescript
interface CostMetric {
  date: string;
  cloudProvider: string;
  cost: number;
  currency: string;
}

export function calculateTotalCost(metrics: CostMetric[]): number {
  return metrics.reduce((sum, metric) => sum + metric.cost, 0);
}
```

### SQL

**Style Guide:** sqlfluff

**Requirements:**

- [PASS] Keywords in UPPERCASE
- [PASS] Table/column names in snake_case
- [PASS] Indentation: 2 spaces
- [PASS] Comments for complex queries

**Example:**

```sql
SELECT
  date,
  cloud_provider,
  SUM(cost_usd) AS total_cost
FROM cost_metrics
WHERE date >= CURRENT_DATE - INTERVAL '30 days'
  AND tenant_id = :tenant_id
GROUP BY date, cloud_provider
ORDER BY date DESC;
```

### Infrastructure as Code (Terraform)

**Style Guide:** HashiCorp style

**Requirements:**

- [PASS] Use modules for reusable components
- [PASS] Variables with descriptions
- [PASS] Outputs documented
- [PASS] Run `terraform fmt` before commit

---

## Git Workflow

### Branch Naming

See [GOVERNANCE_RULES.md §4](governance/GOVERNANCE_RULES.md#4-naming-conventions) for the canonical branch naming rules.

| Type | Pattern | Example |
|:-----|:--------|:--------|
| Feature | `feature/{short-name}` | `feature/budget-alerts` |
| Bugfix | `bugfix/{short-name}` | `bugfix/threshold-calc` |
| Hotfix | `hotfix/{short-name}` | `hotfix/pubsub-retry` |
| AI | `ai/{issue-number}-{short-name}` | `ai/24-costguarded-llm` |

### Commit Messages

Follow **[Conventional Commits](https://www.conventionalcommits.org/)**:

```
<type>(<scope>): <short summary>

<body> (optional)

<footer> (optional)
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (formatting, no logic change)
- `refactor`: Code restructuring
- `test`: Test additions/fixes
- `chore`: Build, CI, dependencies

**Examples:**

```
feat(mcp): add AWS Cost Explorer integration

Implements MCP server for AWS cost data retrieval.
- Queries Cost Explorer API
- Maps to unified cost schema
- Caches results for 5 minutes

Closes #42
```

```
fix(api): resolve BigQuery timeout on large date ranges

Reduced query complexity by pre-aggregating at table level
instead of query-time aggregation.
```

### Workflow

1. **Create branch** from `main`:

   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make changes** with frequent commits

3. **Push** to remote:

   ```bash
   git push origin feature/my-feature
   ```

4. **Create Pull Request** on GitHub

5. **Address review** feedback

6. **Merge** after approval

---

## Testing

### Requirements

- [PASS] Unit tests for all new features
- [PASS] Integration tests for APIs
- [PASS] Minimum 80% code coverage
- [PASS] All tests must pass before merge

### Running Tests

**Python:**

```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Specific file
pytest tests/test_mcp_gcp.py
```

**TypeScript:**

```bash
# All tests
npm test

# Watch mode
npm test -- --watch

# Coverage
npm test -- --coverage
```

### Writing Tests

**Python (pytest):**

```python
def test_calculate_cost():
    result = calculate_cost(usage_amount=100, rate_per_unit=0.05)
    assert result["amount"] == 5.0
    assert result["currency"] == "USD"
```

**TypeScript (Jest):**

```typescript
describe('calculateTotalCost', () => {
  it('sums costs correctly', () => {
    const metrics = [
      { date: '2024-01-01', cloudProvider: 'GCP', cost: 100, currency: 'USD' },
      { date: '2024-01-02', cloudProvider: 'AWS', cost: 150, currency: 'USD' }
    ];
    expect(calculateTotalCost(metrics)).toBe(250);
  });
});
```

---

## Documentation

### When to Update Documentation

- [PASS] Adding new features → Update relevant `/core` spec
- [PASS] Changing APIs → Update `docs/core/05-api-endpoint-spec.md`
- [PASS] Infrastructure changes → Update deployment guides
- [PASS] Breaking changes → Document in PR + CHANGELOG

### Documentation Files

| File | Update When |
|------|-------------|
| `README.md` | Adding major features |
| `docs/core/*.md` | Changing architecture/specs |
| `docs/adr/*.md` | Making architectural decisions |
| `*-DEPLOYMENT.md` | Changing deployment process |

### Documentation Validation

Run this before opening a PR when markdown files changed:

```bash
scripts/validate_changed_links.sh
```

Validation behavior:

- Checks changed non-template markdown files with `sdd_validate_links`.
- Skips `governance/templates/` files in framework-repo context.
- Template links are validated after scaffold in target-project context.

### Adding ADRs

For significant architectural decisions:

1. Create `docs/adr/NNN-title.md`
2. Use template from existing ADRs
3. Include: Context, Decision, Rationale, Consequences

---

## Pull Request Process

### Before Creating PR

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Commits follow Conventional Commits
- [ ] Branch is up-to-date with `main`

### PR Description Template

```markdown
## What
Brief description of changes

## Why
Problem this solves or feature this adds

## How
Technical approach taken

## Testing
How you tested these changes

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Follows code style
- [ ] Breaking changes documented
```

### Review Process

1. **Automated checks** must pass (tests, linting)
2. **Code review** by at least 1 maintainer
3. **Address feedback** through additional commits
4. **Squash and merge** once approved

### After Merge

- Delete feature branch
- Update local `main`:

  ```bash
  git checkout main
  git pull origin main
  ```

---

## Questions?

- Open an issue for bugs or feature requests
- Discuss in pull requests for code-related questions
- Contact team lead for architectural questions

---

**Thank you for contributing!**
