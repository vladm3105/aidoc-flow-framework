# ADR-009: AI PR Review via Custom GitHub Actions Workflow

**Status**: Amended (v1.1)
**Date**: {DATE} (amended {DATE})
**Deciders**: {CODEOWNER_1}, {CODEOWNER_2}

## Context

The project needs automated AI code review on pull requests to supplement human reviewers. Four approaches were evaluated for the GHES environment at `{GITHUB_HOST}`:

1. **Custom GitHub Actions Workflow** — Python script triggered by `pull_request` event
2. **Bot Account + Cloud Run Webhook** — Dedicated GHES bot user with webhook handler
3. **{AI_TOOL_NAME} Code Action** — `anthropics/claude-code-action` in CI
4. **PR-Agent (Qodo open source)** — `qodo-ai/pr-agent` in GitHub Actions mode

## Decision

**Use a Custom GitHub Actions Workflow with Gemini 2.5 Flash via Vertex AI.**

## Rationale

### Scorecard (Custom Workflow vs PR-Agent finalist)

| Dimension | Custom Workflow | PR-Agent | Winner |
|:----------|:-:|:-:|:-------|
| Implementation (lines of code) | 280 (3 files) | 85 (2 files) | PR-Agent |
| GHES Compatibility | Full (no Docker) | Needs image mirror + `BASE_URL` | Custom |
| Review Quality | Inline comments + APPROVE/REQUEST_CHANGES | Single markdown comment | Custom |
| LLM Provider Options | Manual per provider | 15+ via litellm | PR-Agent |
| Cost (25 PRs/mo) | $0.15-$1.20/mo | $0.30-$2.44/mo | Tie |
| Customization | Full prompt control + ruff/mypy integration | `extra_instructions` only | Custom |
| Security | 2 deps, controlled payload | ~50+ deps in 1.2GB Docker image | Custom |
| Failure Modes | Your error messages, no Docker pull risk | Opaque errors, Docker pull risk | Custom |
| Maintenance | 2-4 hrs/mo | 0.5-1 hr/mo | PR-Agent |
| Extensibility | Review gating via branch protection | Comments only (cannot block merge) | Custom |

**Custom Workflow wins 6-3** on dimensions that matter for this GHES + GCP environment.

### Key Differentiators

1. **Inline line-level comments** in the "Files changed" tab (same UX as human reviewers). PR-Agent posts a single markdown summary.
2. **APPROVE / REQUEST_CHANGES** events integrate with branch protection. PR-Agent's comments cannot block merging.
3. **ruff/mypy integration** — pipe static analysis output into the AI prompt so reviews are additive, not redundant.
4. **Minimal attack surface** — 2 Python dependencies (`google-auth`, `requests`) vs PR-Agent's 1.2GB Docker image with 50+ transitive deps.
5. **Full GHES control** — no Docker image to mirror, no undocumented calls to `api.github.com`.

### Why Gemini 2.5 Flash via Vertex AI

| Factor | Decision |
|:-------|:---------|
| WIF compliance | Vertex AI uses the same WIF auth as all GCP services — no third-party API keys |
| Cost | $0.15/month at 25 PRs (functionally free) |
| Latency | 3-8 seconds per review call |
| Quality | Sufficient for Python code review at this volume |
| Upgrade path | Swap to Claude Sonnet 4.5 on Vertex AI for security-labeled PRs |

### Monthly Cost by Model (25 PRs/month)

| Model | Custom Workflow | PR-Agent |
|:------|:---------------:|:--------:|
| Gemini 2.5 Flash | **$0.15** | $0.30 |
| Claude Haiku 4.5 | $0.40 | $0.82 |
| Gemini 2.5 Pro | $0.65 | $1.24 |
| Claude Sonnet 4.5 | $1.20 | $2.44 |

### Rejected Alternatives

**PR-Agent**: Well-built but posts comments instead of formal reviews (no merge gating), requires Docker image mirroring on GHES, and has a larger supply chain surface.

**Bot Account + Cloud Run**: Only approach that provides a named reviewer identity, but highest complexity (4/5). Reserved for future if branch protection requires a named AI reviewer.

**{AI_TOOL_NAME} Code Action**: Not officially supported on GHES. Vendor-locked to Anthropic. Data residency concerns with sending all code to Anthropic servers.

## Consequences

### Positive
- AI reviews supplement human reviewers on every PR
- Review gating enforces quality via branch protection
- Static analysis (ruff/mypy) output enriches AI review context
- WIF-compliant, no additional API keys
- Negligible cost ($1.80/year with Gemini Flash)

### Negative
- ~280 lines of custom code to maintain
- Reviews appear as `github-actions` bot, not a named reviewer
- Cannot satisfy "required reviewer" branch protection rules (for that, would need Bot approach)
- Prompt tuning required to achieve good review quality

### Neutral
- AI review is advisory by default; human review still required per GOVERNANCE_RULES.md
- Can be disabled per-PR via `skip-ai-review` label

## Implementation

Operational documentation: [AI_PR_Review/](../../governance/AI_PR_Review/) (overview, GCP setup, onboarding).
Original implementation plan: [IPLAN-003](../../governance/plans/IPLAN-003_ai-pr-review-workflow.md) (Complete).

### Files Created

| File | Purpose |
|:-----|:--------|
| `.github/workflows/ai-review.yml` | Workflow trigger (~55 lines) |

> **Note**: Original `scripts/ai_review.py` and `scripts/requirements-review.txt` were removed after switch to {AI_TOOL_NAME} Code CLI (see Amendment below).

### GCP Prerequisites (Human Task)

| Prerequisite | Detail |
|:-------------|:-------|
| Vertex AI API enabled | `aiplatform.googleapis.com` in GCP project |
| WIF configured | `WIF_PROVIDER` and `WIF_SA_EMAIL` in GitHub Secrets |
| IAM role | Service account needs `aiplatform.endpoints.predict` |

---

## Amendment: Switch to {AI_TOOL_NAME} Code CLI ({DATE})

### Context

The original Gemini 2.5 Flash implementation via `ai_review.py` required:
- 3 marketplace actions (`actions/checkout`, `actions/setup-python`, `google-github-actions/auth`) — unreliable on GHES v3.12.4 due to GitHub Connect issues
- Python runtime + pip dependency installation on the runner
- GCP WIF authentication to Vertex AI
- A 350-line custom Python script for diff parsing, AI API calls, and review posting

The self-hosted runner (`local-{PROJECT_PREFIX}-01`) already has {AI_TOOL_NAME} Code CLI installed. {AI_TOOL_NAME} Code's `-p` (print) mode supports non-interactive execution with tool use, cost caps, and structured output — eliminating the need for custom code.

### Amended Decision

**Replace Gemini 2.5 Flash + Python script with {AI_TOOL_NAME} Code CLI on the self-hosted runner.**

The custom workflow pattern (ADR-009 original decision) is retained. Only the AI backend changes: from a Python script calling Vertex AI to {AI_TOOL_NAME} Code CLI calling the Anthropic API.

### Comparison

| Dimension | Gemini + Python (v1.0) | {AI_TOOL_NAME} Code CLI (v1.1) |
|:----------|:----------------------:|:----------------------:|
| Marketplace actions | 3 required | 0 |
| Custom code | 350 lines Python | 0 (prompt-driven) |
| Dependencies | google-auth, requests | {AI_TOOL_NAME} Code CLI (pre-installed) |
| Auth | GCP WIF + Vertex AI | `ANTHROPIC_API_KEY` secret |
| Runner label | `ubuntu-latest` | `self-hosted` |
| Review depth | Single-prompt, diff-only | Agent: reads files, multi-turn |
| Inline comments | Via custom REST API code | Via `gh api` (Claude posts directly) |
| Cost (25 PRs/mo, Sonnet) | $1.20 | ~$2-5 (with $0.50/review cap) |
| Cost (25 PRs/mo, Haiku) | $0.40 | ~$0.50-1.50 |
| Execution time | 3-8 seconds | 30-90 seconds |
| Fix loop capability | None | Available (not enabled in CI) |

### Trade-offs

**Gained**:
- Zero marketplace action dependency — fully GHES-compatible
- Zero custom code to maintain — review logic is in the prompt
- Deeper review quality — Claude reads source files for context, not just the diff
- Configurable model per-repo (`sonnet` default, `haiku` for cost, `opus` for security PRs)
- Built-in cost cap (`--max-budget-usd`)

**Lost**:
- WIF-only auth (now requires `ANTHROPIC_API_KEY` external secret)
- Sub-10-second review latency (Claude agent loop is slower)
- ruff/mypy output integration (Claude reads source directly instead)

**Data residency**: Code diffs and source files are sent to the Anthropic API during review. This was a concern in v1.0 (rejected "{AI_TOOL_NAME} Code Action") but is now accepted given:
1. The self-hosted runner approach avoids the unsupported `claude-code-action` on GHES
2. {AI_TOOL_NAME} Code CLI is already authorized for manual reviews per [MANUAL_REVIEW_GUIDE.md](../../governance/AI_PR_Review/MANUAL_REVIEW_GUIDE.md)
3. The same code is already visible to the Anthropic API during manual review sessions

### Amended Files

| File | Change |
|:-----|:-------|
| `.github/workflows/ai-review-reusable.yml` | Rewritten — {AI_TOOL_NAME} Code CLI replaces Python + Vertex AI |
| `.github/workflows/ai-review.yml` | Re-enabled (was `.disabled`) |
| `scripts/ai_review.py` | Removed (was deprecated Gemini script) |
| `scripts/requirements-review.txt` | Removed (was dependencies for deprecated script) |

### Amended Secrets (per-repo)

| Secret | Source |
|:-------|:-------|
| `ANTHROPIC_API_KEY` | Anthropic API key (or org-level secret) |

GCP secrets (`WIF_PROVIDER`, `WIF_SA_EMAIL`, `GCP_PROJECT_ID`) are no longer required for AI review but remain in use by other workflows (deploy, terraform).

---

## Version History

| Version | Date | Changes |
|:--------|:-----|:--------|
| 1.1 | {DATE} | Amendment — replaced Gemini 2.5 Flash + Python script with {AI_TOOL_NAME} Code CLI on self-hosted runner |
| 1.0 | {DATE} | Initial ADR — selected Custom Workflow over PR-Agent, Bot, and {AI_TOOL_NAME} Code Action |
