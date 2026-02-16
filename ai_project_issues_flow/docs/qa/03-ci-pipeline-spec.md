# CI Pipeline Specification

**Project**: {PROJECT_NAME}
**Version**: 1.0
**Last Updated**: {DATE}

---

## Pipeline Overview

```
┌─────────┐    ┌──────────┐    ┌─────────────┐    ┌──────────┐    ┌───────┐
│  Lint   │───►│  Unit    │───►│ Integration │───►│ Security │───►│ Build │
│         │    │  Tests   │    │    Tests    │    │   Scan   │    │       │
└─────────┘    └──────────┘    └─────────────┘    └──────────┘    └───────┘
     │              │                 │                 │              │
     ▼              ▼                 ▼                 ▼              ▼
   ~1min          ~3min             ~5min            ~2min          ~3min
```

**Total target time**: <15 minutes for full pipeline

---

## Triggers

| Event | Pipeline Stages | Blocking |
|:------|:----------------|:---------|
| PR opened | Lint, Unit, Integration, Security | Yes |
| PR synchronized | Lint, Unit, Integration, Security | Yes |
| PR ready for review | Full pipeline | Yes |
| Push to `main` | Full pipeline + Build | N/A |
| Release tag | Full pipeline + Build + Publish | N/A |
| Scheduled (nightly) | Full pipeline + Slow tests | No |

---

## Stage Specifications

### Stage 1: Lint

**Purpose**: Catch style and formatting issues early

| Check | Tool | Failure Action |
|:------|:-----|:---------------|
| Python linting | `ruff check` | Block |
| Python formatting | `ruff format --check` | Block |
| Type checking | `mypy --strict` | Block |
| YAML validation | `yamllint` | Warn |

**Configuration**:
```yaml
jobs:
  lint:
    runs-on: self-hosted
    steps:
      - run: |
          git clone "https://${GITHUB_SERVER_URL#https://}/${GITHUB_REPOSITORY}.git" . --depth 1 --branch ${{ github.head_ref || github.ref_name }}
      - run: pip install ruff mypy
      - run: ruff check . --output-format=github
      - run: ruff format --check .
      - run: mypy src/ --strict
```

### Stage 2: Unit Tests

**Purpose**: Validate core business logic

| Metric | Target | Enforcement |
|:-------|:-------|:------------|
| Coverage | ≥80% | Fail build |
| Duration | <3 min | Alert if exceeded |
| Failures | 0 | Fail build |

**Configuration**:
```yaml
jobs:
  test-unit:
    runs-on: self-hosted
    steps:
      - run: |
          git clone "https://${GITHUB_SERVER_URL#https://}/${GITHUB_REPOSITORY}.git" . --depth 1 --branch ${{ github.head_ref || github.ref_name }}
      - run: pip install -e ".[dev]"
      - run: pytest tests/unit/ -v --cov=src --cov-report=xml --cov-fail-under=80 --junitxml=test-results.xml
      - run: |
          # Upload coverage artifact
          mkdir -p artifacts
          cp coverage.xml artifacts/
          cp test-results.xml artifacts/
```

### Stage 3: Integration Tests

**Purpose**: Validate component interactions

| Metric | Target | Enforcement |
|:-------|:-------|:------------|
| Coverage | ≥60% | Warn |
| Duration | <5 min | Alert if exceeded |
| Failures | 0 | Fail build |

**Configuration**:
```yaml
jobs:
  test-integration:
    runs-on: self-hosted
    needs: [lint, test-unit]
    services:
      firestore-emulator:
        image: gcr.io/google.com/cloudsdktool/google-cloud-cli:emulators
    steps:
      - run: |
          git clone "https://${GITHUB_SERVER_URL#https://}/${GITHUB_REPOSITORY}.git" . --depth 1 --branch ${{ github.head_ref || github.ref_name }}
      - run: pip install -e ".[dev]"
      - run: pytest tests/integration/ -v --timeout=300
        env:
          FIRESTORE_EMULATOR_HOST: localhost:8080
```

### Stage 4: Security Scan

**Purpose**: Detect vulnerabilities before merge

| Check | Tool | Severity Threshold |
|:------|:-----|:-------------------|
| Python SAST | `bandit` | HIGH = fail |
| Dependency audit | `pip-audit` | HIGH = fail |
| Secret detection | `gitleaks` | Any = fail |

**Configuration**:
```yaml
jobs:
  security:
    runs-on: self-hosted
    steps:
      - run: |
          git clone "https://${GITHUB_SERVER_URL#https://}/${GITHUB_REPOSITORY}.git" . --depth 1 --branch ${{ github.head_ref || github.ref_name }}
      - run: pip install bandit pip-audit
      - run: bandit -r src/ -ll -f json -o bandit-report.json
      - run: pip-audit --requirement requirements.txt --strict
      - run: |
          # Check for secrets
          curl -sSfL https://github.com/gitleaks/gitleaks/releases/download/v8.18.0/gitleaks_8.18.0_linux_x64.tar.gz | tar xz
          ./gitleaks detect --source . --no-git
```

### Stage 5: Build

**Purpose**: Create deployable artifacts

| Output | Format | Destination |
|:-------|:-------|:------------|
| Container image | Docker | gcr.io/{project}/{service}:{sha} |
| Python wheel | `.whl` | Artifacts |

**Configuration**:
```yaml
jobs:
  build:
    runs-on: self-hosted
    needs: [test-unit, test-integration, security]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - run: |
          git clone "https://${GITHUB_SERVER_URL#https://}/${GITHUB_REPOSITORY}.git" . --depth 1
      - run: |
          docker build -t gcr.io/${{ secrets.GCP_PROJECT }}/${SERVICE_NAME}:${GITHUB_SHA} .
      - run: |
          # Scan image for vulnerabilities
          trivy image gcr.io/${{ secrets.GCP_PROJECT }}/${SERVICE_NAME}:${GITHUB_SHA} \
            --severity HIGH,CRITICAL --exit-code 1
      - run: |
          docker push gcr.io/${{ secrets.GCP_PROJECT }}/${SERVICE_NAME}:${GITHUB_SHA}
```

---

## Parallelization

### Matrix Builds

For libraries supporting multiple Python versions:

```yaml
jobs:
  test:
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    steps:
      - run: |
          pyenv install ${{ matrix.python-version }}
          pyenv local ${{ matrix.python-version }}
      - run: pytest
```

### Parallel Test Execution

```yaml
jobs:
  test-unit:
    steps:
      - run: pytest tests/unit/ -n auto  # Use pytest-xdist
```

---

## Caching

### pip Cache

```yaml
jobs:
  test:
    steps:
      - run: |
          # Cache pip packages in runner-local directory
          export PIP_CACHE_DIR=/opt/cache/pip
          pip install -e ".[dev]"
```

### Test Result Cache

```yaml
jobs:
  test:
    steps:
      - run: pytest --cache-dir=/opt/cache/pytest
```

---

## Artifacts

| Artifact | Retention | Purpose |
|:---------|:----------|:--------|
| `coverage.xml` | 30 days | Coverage tracking |
| `test-results.xml` | 30 days | Test result history |
| `bandit-report.json` | 30 days | Security audit trail |
| Container image | Until next deploy | Deployment artifact |

---

## Failure Handling

### Fail Fast Strategy

```yaml
jobs:
  test-unit:
    steps:
      - run: pytest --exitfirst  # Stop on first failure
```

### Continue on Non-Critical

```yaml
jobs:
  lint:
    steps:
      - run: yamllint . || true  # Don't fail on YAML lint
```

### Retry Flaky Tests

```yaml
jobs:
  test-integration:
    steps:
      - run: pytest --reruns 2 --reruns-delay 5
```

---

## Notifications

| Event | Channel | Recipients |
|:------|:--------|:-----------|
| PR checks failed | GitHub PR comment | PR author |
| Main build failed | Teams channel | Team |
| Security vulnerability | Teams + Email | Security team |
| Nightly tests failed | Teams channel | Team |

---

## Workflow Files

| File | Purpose |
|:-----|:--------|
| `.github/workflows/ci.yml` | Main CI pipeline |
| `.github/workflows/ci-reusable.yml` | Reusable workflow for components |
| `.github/workflows/security-scan.yml` | Dedicated security scanning |
| `.github/workflows/nightly.yml` | Nightly slow tests |

---

## References

- [01-testing-strategy.md](01-testing-strategy.md) — Test types and coverage targets
- [06-security-testing.md](06-security-testing.md) — Security scan details
- [GOVERNANCE_RULES.md §2a](../../governance/GOVERNANCE_RULES.md) — No marketplace actions policy
- [GITHUB_WORKFLOWS.md](../../governance/GITHUB_WORKFLOWS.md) — Existing workflow documentation
