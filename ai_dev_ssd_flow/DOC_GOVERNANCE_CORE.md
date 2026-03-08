---
title: "Documentation Governance Core — Documentation as Code"
tags:
  - framework-guide
  - shared-architecture
  - governance
custom_fields:
  document_type: guide
  priority: shared
  status: production
---

# Documentation Governance Core — Documentation as Code

**Version**: 1.0 | **Status**: Production | **Last Updated**: 2026-03-06

> **Core Principle**: Every document in this framework is treated exactly like source code.
> It lives in Git, is reviewed via Pull Requests, is gated by automated AI-Expert review pipelines,
> and is merged into a living Knowledge Base only after approval.

---

## The Fundamental Principle: Documentation as Code

Documentation is not a side-effect of development — it **is** the development in SDD.
This means it inherits all best practices from modern software engineering:

| Code Practice | Documentation Equivalent |
|--------------|--------------------------|
| Feature branches | `feature/BRD-01-update` branch per document change |
| Pull Requests | Every document submitted as a PR for review |
| CI/CD pipelines | AI Expert Board review triggered on PR open |
| Merge gates | PR blocked until persona review returns `Proceed` |
| Automated tests | Quality gate scripts + AI validation pipelines |
| Semantic versioning | Document versions tracked via Git tags |
| Single source of truth | `main` branch = approved, production-ready corpus |
| Dependency management | `@depends:` tags enforce upstream document references |

---

## Repository Architecture

Each project has a **dedicated documentation repository** separate from its code repository:

```
{project_name}               ← code repository
{project_name}_documentation ← documentation repository (this pattern)
```

This separation ensures:
- Documentation has its own review lifecycle, independent of code releases
- The documentation repo can be shared across multiple code repos (platform docs)
- Knowledge Base ingestion targets only the `docs` repo, not the code repo

---

## Document Lifecycle: The Git-Native Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                    DOCUMENT CREATION                             │
│                                                                  │
│  Human / AI Agent / Pipeline writes or updates a document       │
│  Creates a feature branch: feature/{DOC_ID}-{description}       │
└─────────────────────────────┬────────────────────────────────────┘
                              │ git push + open Pull Request
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                    AUTOMATED REVIEW (CI on PR)                   │
│                                                                  │
│  1. Quality gate scripts (schema, YAML frontmatter, IDs)        │
│  2. AI Expert Board audit (7-persona board)                   │
│     → P0 blockers: PR is blocked, comments posted               │
│     → P1/P2: Comments posted as non-blocking suggestions        │
│  3. Integration Expert cross-references KB for dep conflicts     │
│  4. Results posted as PR review comments                        │
└─────────────────────────────┬────────────────────────────────────┘
                              │ Author resolves comments
                              │ Multiple rounds as needed
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                    HUMAN APPROVAL                                │
│                                                                  │
│  Reviewer (human or designated AI agent) approves the PR        │
│  Required approvals: 1 (configurable per layer)                 │
└─────────────────────────────┬────────────────────────────────────┘
                              │ merge to main
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE BASE INGESTION                      │
│   Triggered automatically on merge to main                       │
│                                                                  │
│  1. rag_embed  → index document chunks in pgvector (RAG)        │
│  2. graph_extract → upsert Document + Dependency nodes (Neo4j)  │
│  3. Old chunks deleted before re-indexing (idempotent)          │
│  4. KB reflects only approved, merged documents                 │
└──────────────────────────────────────────────────────────────────┘
```

---

## AI Expert Board Review (PR-Integrated)

The 7-persona AI Expert Board runs as a **GitHub Actions workflow** triggered on every documentation PR:

```yaml
# .github/workflows/doc-expert-review.yml
on:
  pull_request:
    paths: ['docs/**/*.md', 'docs/**/*.yaml']
```

### How PR Comments Work

- Each expert's finding is posted as a **PR review comment** on the specific line/section
- P0 blockers request changes (PR cannot merge)
- P1/P2 findings are informational comments
- The Chairperson summary is posted as the main PR review body

### Chicken-and-Egg: New Documents

When reviewing a **brand new** document not yet in the KB, the Integration Expert uses:

1. **PR diff** as the primary context for the new document
2. **KB query** for all existing upstream dependencies
3. **Open PRs scan** to detect concurrent conflicting changes

---

## Knowledge Base Architecture

The KB solves the critical context-window scaling problem:

> **74 BRDs × 18 sections + all downstream layers = 4,000+ documents.**
> No AI agent can hold even 10% of this in context simultaneously.

Instead of injecting full documents, every AI Expert receives **targeted context** fetched from the KB:

```
Before each persona prompt:
  rag_search(doc_summary)       → top-5 semantically related chunks
  graph_query(DEPENDS_ON path)  → upstream document nodes
  → Compact 300-500 token context injected
  (vs. 40,000+ tokens for full corpus)
```

### KB Operating Mode

| Branch | KB Indexed? | Purpose |
|--------|------------|---------|
| `main` | ✅ Yes | Approved, production-ready corpus |
| `feature/*` | ❌ No | Work in progress — not canonical |
| `release/*` | ❌ No | Only `main` is the KB source of truth |

### KB Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **RAG** | PostgreSQL + pgvector | Semantic similarity search |
| **Graph** | Neo4j | Dependency traversal, entity ownership, event topics |
| **MCP Server** | `project_knowledge/mcp/` | Unified `kb_*` tool interface for all agents |

---

## Ingestion on Merge: GitHub Actions

```yaml
# .github/workflows/kb-ingest.yml
on:
  push:
    branches: [main]
    paths: ['docs/**/*.md', 'docs/**/*.yaml']

jobs:
  ingest:
    steps:
      - name: RAG Embed
        run: python project_knowledge/orchestrator.py rag_embed $CHANGED_FILE

      - name: Graph Extract
        run: python project_knowledge/orchestrator.py graph_extract $CHANGED_FILE

      - name: Verify Ingestion
        run: python project_knowledge/orchestrator.py verify $CHANGED_FILE
```

Ingestion is **idempotent**: if a document is updated, its old vector chunks and graph nodes
are deleted before re-indexing.

---

## Branch Strategy for Documentation

```
main
  └── feature/BRD-01-add-payment-flows          ← one branch per doc change
  └── feature/PRD-45-update-user-stories
  └── feature/INTEGRATION-MATRIX-add-brd-47
  └── hotfix/BRD-22-fix-circular-dependency       ← urgent fixes
```

**Rules:**
- `main` = approved, KB-indexed documents only
- Never commit directly to `main` (branch protection required)
- PRs require green expert review before merge
- Feature branches are short-lived (days, not weeks)

---

## Automation Pipeline Integration

The full automation stack works together:

```
automation/pipelines/doc_review/run_review.sh
        │
        ├─ Reads PERSONA_REVIEW_REPORT.md (generated by GitHub Actions review)
        ├─ Parses P0/P1/P2 remediation actions
        ├─ Auto-applies structural P0 fixes (commits to feature branch)
        ├─ Creates GitHub Issues for content P0 + all P1/P2 (enters governance loop)
        └─ Updates KB via graph_extract after merge

project_knowledge/
        │
        ├─ rag/    → Semantic search for Integration Expert context
        └─ graph/  → Dependency graph traversal
```

---

## Summary: Core Governance Rules

1. **No document exists outside Git** — every doc is version-controlled
2. **No merge without review** — all changes go through PR + AI Expert Board
3. **KB reflects `main` only** — only approved documents are searchable by AI agents
4. **Context over corpus** — AI agents query the KB, never read full file trees
5. **Remediation is automated** — expert findings become GitHub Issues automatically
6. **Agent-agnostic** — all pipelines use `ai_exec.sh` adapter; not tied to Claude CLI
