# Security Testing

**Project**: AI Cloud Cost Monitoring
**Version**: 1.0
**Last Updated**: {DATE}

---

## Security Testing Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Security Testing Pipeline                    │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────┤
│    SAST     │  Dependency │  Container  │   Secret    │  DAST   │
│   (Code)    │    Scan     │    Scan     │  Detection  │  (API)  │
├─────────────┼─────────────┼─────────────┼─────────────┼─────────┤
│   bandit    │  pip-audit  │   trivy     │  gitleaks   │ (TBD)   │
│   semgrep   │  npm audit  │             │             │         │
└─────────────┴─────────────┴─────────────┴─────────────┴─────────┘
```

---

## Static Application Security Testing (SAST)

### Python: Bandit

**Purpose**: Detect common security issues in Python code

| Issue Type | Severity | Example |
|:-----------|:---------|:--------|
| Hardcoded passwords | HIGH | `password = "secret123"` |
| SQL injection | HIGH | `f"SELECT * FROM {table}"` |
| Command injection | HIGH | `os.system(user_input)` |
| Insecure deserialization | HIGH | `pickle.loads(data)` |
| Weak cryptography | MEDIUM | `hashlib.md5()` |

**Configuration** (`pyproject.toml`):

```toml
[tool.bandit]
exclude_dirs = ["tests", "venv", ".venv"]
skips = ["B101"]  # Skip assert_used (acceptable in tests)
```

**CI Integration**:

```yaml
- run: |
    pip install bandit
    bandit -r src/ -ll -f json -o bandit-report.json
    # Fail on HIGH severity
    bandit -r src/ -ll --severity-level high
```

### Python: Semgrep (Optional)

**Purpose**: Advanced pattern-based security scanning

```yaml
- run: |
    pip install semgrep
    semgrep --config=p/python --config=p/security-audit src/
```

---

## Dependency Scanning

### Python: pip-audit

**Purpose**: Detect known vulnerabilities in Python dependencies

```yaml
- run: |
    pip install pip-audit
    pip-audit --requirement requirements.txt --format json > audit-report.json
    pip-audit --requirement requirements.txt --strict  # Fail on any vulnerability
```

### JavaScript/TypeScript: npm audit

**Purpose**: Detect vulnerabilities in npm packages

```yaml
- run: |
    npm audit --json > npm-audit.json
    npm audit --audit-level=high  # Fail on high severity
```

---

## Container Scanning

### Trivy

**Purpose**: Scan container images for vulnerabilities and misconfigurations

```yaml
- run: |
    curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
    trivy image gcr.io/${PROJECT}/${IMAGE}:${TAG} \
      --severity HIGH,CRITICAL \
      --exit-code 1 \
      --format json \
      --output trivy-report.json
```

### Scan Policies

| Severity | Action | SLA |
|:---------|:-------|:----|
| CRITICAL | Block deployment | Fix within 24 hours |
| HIGH | Block deployment | Fix within 7 days |
| MEDIUM | Warning | Fix within 30 days |
| LOW | Informational | Fix within 90 days |

---

## Secret Detection

### Gitleaks

**Purpose**: Detect secrets and credentials in code

**Pre-commit Hook** (`.pre-commit-config.yaml`):

```yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
```

**CI Integration**:

```yaml
- run: |
    curl -sSfL https://github.com/gitleaks/gitleaks/releases/download/v8.18.0/gitleaks_8.18.0_linux_x64.tar.gz | tar xz
    ./gitleaks detect --source . --no-git --report-format json --report-path gitleaks-report.json
    ./gitleaks detect --source . --no-git  # Exit code 1 if secrets found
```

### Common Secret Patterns

| Pattern | Example | Detection |
|:--------|:--------|:----------|
| API keys | `ANTHROPIC_API_KEY=sk-...` | Gitleaks |
| AWS credentials | `aws_secret_access_key` | Gitleaks |
| GCP service account | `"private_key":` | Gitleaks |
| Database passwords | `DATABASE_PASSWORD=` | Gitleaks |
| JWT tokens | `eyJ...` | Gitleaks |

### False Positive Handling

Create `.gitleaks.toml` to exclude known false positives:

```toml
[allowlist]
paths = [
    '''tests/fixtures/.*''',
    '''docs/examples/.*''',
]

[[rules]]
id = "test-api-key"
description = "Test API key (not real)"
regex = '''test[-_]?api[-_]?key'''
allowlist = true
```

---

## OWASP Top 10 Coverage

| # | Risk | Testing Approach |
|:--|:-----|:-----------------|
| A01 | Broken Access Control | Integration tests for auth/authz |
| A02 | Cryptographic Failures | Bandit + manual review |
| A03 | Injection | Bandit + parameterized queries |
| A04 | Insecure Design | Architecture review |
| A05 | Security Misconfiguration | Terraform scanning, trivy |
| A06 | Vulnerable Components | pip-audit, npm audit |
| A07 | Auth Failures | Integration tests |
| A08 | Data Integrity Failures | Input validation tests |
| A09 | Logging Failures | Log review, no sensitive data |
| A10 | SSRF | Input validation, URL allowlists |

---

## Vulnerability Management

### Severity Levels

| Level | CVSS Score | Response Time | Notification |
|:------|:-----------|:--------------|:-------------|
| Critical | 9.0-10.0 | 24 hours | Immediate page |
| High | 7.0-8.9 | 7 days | Team email |
| Medium | 4.0-6.9 | 30 days | Weekly report |
| Low | 0.1-3.9 | 90 days | Monthly report |

### Vulnerability Workflow

```
Discovery → Triage → Assign → Fix → Verify → Close
    │          │        │       │       │
    └──────────┴────────┴───────┴───────┴── Track in issue
```

### Exception Process

For vulnerabilities that cannot be fixed immediately:

1. Create security exception ticket
2. Document risk assessment
3. Implement compensating controls
4. Set review date (max 90 days)
5. Get security team approval

---

## Security Testing in CI

### Pipeline Placement

```yaml
jobs:
  lint:
    # ... linting

  security:
    runs-on: self-hosted
    steps:
      - name: SAST - Bandit
        run: bandit -r src/ -ll --severity-level high

      - name: Dependency Scan
        run: pip-audit --strict

      - name: Secret Detection
        run: ./gitleaks detect --source . --no-git

  test:
    needs: [lint, security]
    # ... testing

  build:
    needs: [test]
    steps:
      - name: Build image
        run: docker build -t ${IMAGE} .

      - name: Container Scan
        run: trivy image ${IMAGE} --severity HIGH,CRITICAL --exit-code 1
```

---

## Security Test Data

### Test Credentials

Never use real credentials in tests. Use dedicated test values:

```python
# conftest.py
@pytest.fixture
def test_api_key():
    """Fake API key for testing - not a real credential."""
    return "test-api-key-not-real-abc123"

@pytest.fixture
def mock_gcp_credentials():
    """Mock GCP credentials for testing."""
    return MagicMock(spec=Credentials)
```

### Test Data Isolation

- Use separate test databases/collections
- Clear test data after each test run
- Never copy production data to test environments

---

## References

- [01-testing-strategy.md](01-testing-strategy.md) — Overall testing approach
- [03-ci-pipeline-spec.md](03-ci-pipeline-spec.md) — CI pipeline integration
- [GOVERNANCE_RULES.md §2](../../governance/GOVERNANCE_RULES.md) — Security posture
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
