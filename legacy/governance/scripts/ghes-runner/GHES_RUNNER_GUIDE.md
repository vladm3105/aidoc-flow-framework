# GHES Self-Hosted Runner Guide

**Project**: {PROJECT_NAME} (`{PROJECT_PREFIX}`)
**GHES**: `{GITHUB_HOST}` (v3.12.4)
**Runner Version**: 2.311.0

---

## 1. Problem

GHES does not provide hosted runners. Unlike github.com, `runs-on: ubuntu-latest` does not match any GitHub-managed runner. Without a self-hosted runner registered, all workflow jobs queue indefinitely.

**Impact**: All 8 workflows in `.github/workflows/` are blocked — CI, AI PR review, board automation, and releases cannot execute.

---

## 2. Architecture

```

  GHES ({GITHUB_HOST})                     
      
    8 Workflows     Project Board #{PROJECT_BOARD_NUMBER}         
    (queued)        (status sync blocked)     
      
          job dispatch                           
                                                 
                              
    Runner Registry    registration token   
                              

           long-poll (HTTPS)
          

  Self-Hosted Runner                  
  (host process or Docker container)  
                                      
  Labels: ubuntu-latest               
  Mode:   persistent (long-running)   
  Auth:   registration token via PAT  

```

The runner long-polls GHES for queued jobs matching its labels. When a job arrives, the runner executes it locally, reports results back to GHES, then resumes polling.

---

## 3. Runner Options

### Option A: Host-Based Runner (Current — Recommended)

Runs directly on the development workstation. Uses existing system tools (Python, Node.js, gh CLI).

| Aspect | Detail |
|:-------|:-------|
| **Script** | `governance/scripts/ghes-runner/setup-local-runner.sh` |
| **Location** | `governance/scripts/ghes-runner/runner-local/` (gitignored) |
| **Process** | Background `nohup` process with PID file |
| **Auth** | Uses `gh auth token` from host (OAuth `gho_*` token) |
| **Label** | `ubuntu-latest` (matches all existing workflows) |
| **Dependencies** | git, Python 3.10+, Node.js, gh CLI, jq, curl, {AI_TOOL_NAME} Code CLI |

**When to use**: Development, testing, immediate unblock of queued workflows.

### Option B: Docker Runner

Runs inside a Docker container for isolation. Requires GHES CA certificate to be injected.

| Aspect | Detail |
|:-------|:-------|
| **Files** | `Dockerfile`, `docker-compose.yml`, `start.sh` |
| **Image** | Ubuntu 22.04 + Python 3.10/3.11/3.12 + Node 20 + gh CLI |
| **Auth** | `GHES_PAT` env var (classic PAT with `repo` scope) |
| **Known Issue** | GHES TLS — requires `ghes-ca.crt` in image (see §8) |

**When to use**: CI environments, shared servers, production-like isolation.

### Option C: Cloud Run Worker Pool (Future)

Serverless runners on GCP with scale-to-zero autoscaling. See implementation plans in [plans/](../plans/) directory.

**When to use**: Production, multi-repo, cost-optimized long-term solution.

---

## 4. Quick Start (Host-Based)

### Prerequisites

1. `gh` CLI authenticated to GHES with `repo` scope:
   ```bash
   GH_HOST={GITHUB_HOST} gh auth status
   ```
   Required scopes: `repo`, `workflow`

2. Host tools: Python 3.10+, Node.js, git, jq, curl, {AI_TOOL_NAME} Code CLI (`claude --version`)

### Commands

```bash
# Make script executable (first time only)
chmod +x governance/scripts/ghes-runner/setup-local-runner.sh

# Start runner (downloads binary on first run)
governance/scripts/ghes-runner/setup-local-runner.sh start

# Check status and GHES registration
governance/scripts/ghes-runner/setup-local-runner.sh status

# Stop runner (keeps registration)
governance/scripts/ghes-runner/setup-local-runner.sh stop

# Fully deregister and stop
governance/scripts/ghes-runner/setup-local-runner.sh remove
```

### Verification

After starting, verify the runner appears on GHES:

```bash
GH_HOST={GITHUB_HOST} gh api \
  /repos/{GITHUB_ORG}/{REPO_NAME}/actions/runners \
  --jq '.runners[] | {name, status, labels: [.labels[].name]}'
```

Expected output:
```json
{
  "name": "local-{PROJECT_PREFIX}-01",
  "status": "online",
  "labels": ["self-hosted", "Linux", "X64", "ubuntu-latest"]
}
```

---

## 5. Label Mapping

**All workflows use `runs-on: self-hosted`** as the project standard. The `ubuntu-latest` custom label is retained on the runner for backward compatibility but should not be used in new workflows.

| Workflow Label | Runner Label | Match |
|:---------------|:-------------|:------|
| `self-hosted` | `self-hosted` (auto) | Yes (standard) |
| `ubuntu-latest` | `ubuntu-latest` (custom) | Yes (legacy, not recommended) |
| `linux` | `Linux` (auto) | Yes |

---

## 6. Security Considerations

### Token Scope

| Token Type | Prefix | Scope | Use Case |
|:-----------|:-------|:------|:---------|
| OAuth (gh auth) | `gho_*` | `repo`, `workflow` | Host-based runner (auto from `gh auth`) |
| Classic PAT | `ghp_*` | `repo` | Docker runner (`GHES_PAT` env var) |

**Do NOT** use tokens with `admin:org` scope unless registering an organization-level runner.

### Runner Isolation

| Risk | Host Runner | Docker Runner |
|:-----|:------------|:--------------|
| Workflow reads host files | Yes — runs as current user | No — isolated filesystem |
| Workflow installs packages | Yes — affects host | Yes — but ephemeral if `--rm` |
| Workflow accesses network | Yes — host network | Yes — Docker bridge network |
| Secret exposure | Via env vars and `gh auth` | Limited to passed env vars |

**Mitigation**: The runner executes workflow steps as the runner user. Sensitive files outside the repo directory are not accessible unless explicitly mounted or referenced.

### Credential Rotation

- Rotate the `gh` OAuth token periodically (`gh auth refresh`)
- If using a classic PAT, set an expiration date and rotate before expiry
- The registration token is single-use and expires in 1 hour — `setup-local-runner.sh` fetches a fresh one each time

---

## 7. Workflow Compatibility

All 8 workflows are compatible with the self-hosted runner. **Zero marketplace actions** — all workflows use inline shell commands per GOVERNANCE_RULES.md §2a (GitHub Connect unreliable on GHES v3.12.4).

| Workflow | Required Tools | Status |
|:---------|:---------------|:-------|
| `ci.yml` (lint) | Python 3, pip, ruff | Host has Python 3.11/3.12 |
| `ci.yml` (type-check) | Python 3, pip, mypy | Host has Python 3.11/3.12 |
| `ci.yml` (test) | Python 3.11/3.12, pytest | Host has both (matrix) |
| `ci.yml` (security) | Python 3, pip, bandit, safety | Host has Python 3.11/3.12 |
| `ai-review.yml` | {AI_TOOL_NAME} Code CLI, gh CLI | Requires `ANTHROPIC_API_KEY` secret |
| `issue-label-sync.yml` | gh CLI, jq | Host has both |
| `pr-merge-cleanup.yml` | gh CLI, jq | Host has both |
| `auto-add-to-project.yml` | gh CLI, jq | Host has both |
| `release.yml` | gh CLI | Host has gh |
| `phase-transition.yml` | gh CLI, jq | Host has both |

### {AI_TOOL_NAME} Code CLI Requirement

The `ai-review-reusable.yml` workflow requires {AI_TOOL_NAME} Code CLI installed on the runner. The workflow verifies this in the first step and fails with install instructions if missing.

```bash
# Verify
claude --version

# Install if needed
npm install -g @anthropic-ai/claude-code
```

---

## 8. Docker Runner — TLS Fix

The Docker runner fails to register because the GHES TLS certificate is not trusted inside the container. The runner binary (.NET runtime) rejects the connection as a 404.

### Diagnosis

The `gh` CLI and `curl` inside the container can reach GHES (they obtained the registration token), but the runner's .NET HTTP client cannot complete TLS verification against GHES.

### Fix

1. Extract the GHES CA certificate on the host:
   ```bash
   openssl s_client -connect {GITHUB_HOST}:443 -showcerts </dev/null 2>/dev/null \
     | openssl x509 -outform PEM > governance/scripts/ghes-runner/ghes-ca.crt
   ```

2. Add to `Dockerfile` before the runner binary download:
   ```dockerfile
   COPY ghes-ca.crt /usr/local/share/ca-certificates/ghes-ca.crt
   RUN update-ca-certificates
   ```

3. For .NET specifically, set the environment variable:
   ```yaml
   # In docker-compose.yml, under environment:
   SSL_CERT_FILE: /etc/ssl/certs/ca-certificates.crt
   ```

4. Rebuild and restart:
   ```bash
   GHES_PAT=$(GH_HOST={GITHUB_HOST} gh auth token) docker compose up -d --build
   ```

---

## 9. Operations

### Log Location

| Runner Type | Log Path |
|:------------|:---------|
| Host-based | `governance/scripts/ghes-runner/runner-local/runner.log` |
| Docker | `docker logs ghes-runner-{PROJECT_PREFIX}` |

### Process Management

```bash
# Check if runner process is alive
governance/scripts/ghes-runner/setup-local-runner.sh status

# View live logs (host runner)
tail -f governance/scripts/ghes-runner/runner-local/runner.log

# View workflow execution logs on GHES
GH_HOST={GITHUB_HOST} gh run list --repo {GITHUB_ORG}/{REPO_NAME}
```

### Handling Stuck Workflow Runs

Before starting the runner, cancel stale queued runs that accumulated while no runner was available:

```bash
# List all queued runs
GH_HOST={GITHUB_HOST} gh run list \
  --repo {GITHUB_ORG}/{REPO_NAME} \
  --status queued --limit 50

# Cancel a specific run
GH_HOST={GITHUB_HOST} gh run cancel <RUN_ID> \
  --repo {GITHUB_ORG}/{REPO_NAME}

# Cancel all queued runs (batch)
GH_HOST={GITHUB_HOST} gh run list \
  --repo {GITHUB_ORG}/{REPO_NAME} \
  --status queued --json databaseId --jq '.[].databaseId' \
  | xargs -I{} GH_HOST={GITHUB_HOST} gh run cancel {} \
    --repo {GITHUB_ORG}/{REPO_NAME}
```

### Runner Lifecycle on Reboot

The host-based runner does not auto-start on reboot. Options:

1. **Manual**: Run `setup-local-runner.sh start` after login
2. **systemd service** (persistent):
   ```bash
   # From the runner-local directory:
   sudo ./svc.sh install
   sudo ./svc.sh start
   ```
   The `svc.sh` script is included in the runner binary distribution and creates a proper systemd unit.

---

## 10. File Inventory

```
governance/scripts/ghes-runner/
 setup-local-runner.sh     # Host runner: start/stop/status/remove
 Dockerfile                # Docker runner image (Ubuntu 22.04)
 docker-compose.yml        # Docker runner compose config
 start.sh                  # Docker entrypoint (register + run)
 .env.example              # PAT template for Docker runner
 runner-local/             # (gitignored) Runner binary + work dir
    config.sh             # Runner configuration script
    run.sh                # Runner execution script
    .runner               # Registration state
    _work/                # Workflow job workspaces
    runner.log            # Runner output log
    runner.pid            # PID file for process management
 ghes-ca.crt               # (optional) GHES TLS CA certificate
```

---

## 11. Upgrade Path

| Current | Target | Trigger |
|:--------|:-------|:--------|
| Host runner | Docker runner | Need isolation; add `ghes-ca.crt` |
| Host runner | Cloud Run | Multi-repo; see plans/ |
| Docker runner | Cloud Run | Production deployment |

When upgrading, deregister the old runner first:
```bash
governance/scripts/ghes-runner/setup-local-runner.sh remove
```

---

## Related Documents

- [Implementation Plans](../plans/) — Production runner and other plans
- [GITHUB_WORKFLOWS.md](../GITHUB_WORKFLOWS.md) — All workflow documentation
- [GOVERNANCE_RULES.md](../../GOVERNANCE_RULES.md) — Project operational rules

---

## Version History

| Version | Date | Changes |
|:--------|:-----|:--------|
| 1.2 | {DATE} | Removed 4 unused workflows (12→8), eliminated all marketplace actions from ci.yml and release.yml |
| 1.1 | {DATE} | Updated for {AI_TOOL_NAME} Code CLI requirement (AI review workflow) — dependencies, label mapping, workflow compatibility |
| 1.0 | {DATE} | Initial guide — host runner, Docker runner, operations |
