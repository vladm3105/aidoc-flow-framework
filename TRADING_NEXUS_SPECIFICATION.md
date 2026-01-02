# Trading Nexus - Technical Specification

## Document Control

| Field | Value |
|-------|-------|
| Version | 2.0 |
| Created | 2026-01-01 |
| Updated | 2026-01-02 |
| Status | **Final** |
| Codename | **Trading Nexus** |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture](#2-system-architecture)
3. [Agent Hierarchy](#3-agent-hierarchy)
4. [Data Architecture](#4-data-architecture)
5. [Agent Ensemble Engine](#5-agent-ensemble-engine)
6. [Implementation Framework: Google ADK](#6-implementation-framework-google-adk)
7. [MCP-First Tool Architecture](#7-mcp-first-tool-architecture)
8. [Infrastructure Design](#8-infrastructure-design)
9. [Implementation Roadmap](#9-implementation-roadmap)
10. [Success Metrics](#10-success-metrics)

---

## 1. Executive Summary

### 1.1 Vision

**Trading Nexus** is an AI-powered options trading intelligence platform that combines:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    TRADING NEXUS                                             │
│                       "The Complete AI Trading Intelligence Platform"                        │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│   CORE CAPABILITIES                          TECHNICAL FOUNDATION                           │
│   ═════════════════                          ════════════════════                           │
│   ✓ Earnings-Driven Directional Trading      ✓ Google ADK Framework                        │
│   ✓ Income Strategies (CC, CSP, IC)          ✓ MCP-First Tool Architecture                 │
│   ✓ Multi-LLM Ensemble (200+ models)         ✓ 6-Level Agent Hierarchy (22+ agents)        │
│   ✓ AI Gateway with Cost Optimization        ✓ GCP Cloud-Native Infrastructure            │
│   ✓ Graph RAG Knowledge System               ✓ Interactive Brokers Integration             │
│   ✓ Continuous Learning & Bias Detection     ✓ Full Observability Stack                   │
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Key Technology Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Agent Framework** | Google ADK | Native GCP, multi-agent design, Dev UI, MCP support |
| **Tool Protocol** | MCP (Model Context Protocol) | Industry standard, 2000+ servers, unified interface |
| **AI Gateway** | LiteLLM / OpenRouter | 200+ models, cost optimization, single interface |
| **Infrastructure** | GCP Cloud-Native | Managed services, scale-to-zero, low ops |
| **Broker** | Interactive Brokers | Professional API, options support, low costs |
| **Knowledge Base** | Neo4j + ChromaDB | Graph relationships + vector embeddings |

### 1.3 Platform Capabilities

| Capability | Description |
|------------|-------------|
| **Earnings Trading** | Directional plays around earnings catalysts with systematic analysis |
| **Income Generation** | Covered calls, cash-secured puts, iron condors |
| **Multi-LLM Analysis** | Ensemble of 5 voting agents with consensus mechanism |
| **Continuous Learning** | Graph RAG with bias detection and framework evolution |
| **Risk Management** | 7 circuit breaker types, position limits, Greeks constraints |

### 1.4 Cost Summary

| Category | Development | Active Trading | Production |
|----------|-------------|----------------|------------|
| LLM APIs | $50 | $100 | $150 |
| Cloud Run | $85 | $100 | $120 |
| Databases | $10 | $75 | $80 |
| Data Services | $20 | $60 | $100 |
| Other GCP | $10 | $25 | $35 |
| IB Data | $0 | $15 | $40 |
| **Total** | **$175** | **$375** | **$525** |

See [COST_ANALYSIS.md](COST_ANALYSIS.md) for detailed breakdown.

---

## 2. System Architecture

### 2.1 High-Level Design

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    TRADING NEXUS                                             │
│                              GCP Cloud-Native Platform                                       │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│   ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│   │                              GOOGLE ADK AGENT LAYER                                    │ │
│   │                                                                                        │ │
│   │   Level 0: System Agents (Health, Circuit Breaker, Scheduler)                         │ │
│   │   Level 1: Portfolio Orchestrator (Capital Allocator, Risk Governor)                  │ │
│   │   Level 2: Strategy Coordinators (Earnings, Income, Hedging)                          │ │
│   │   Level 3: Execution Agents (Order Manager, Position Monitor)                         │ │
│   │   Level 4: Analytical Agents (Stock Selection, Market Intel, Calendar)                │ │
│   │   Level 5: Data Agents (IB Connector, Content Processor)                              │ │
│   │                                                                                        │ │
│   │   Implementation: LlmAgent, SequentialAgent, ParallelAgent, LoopAgent                 │ │
│   │                                                                                        │ │
│   └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                           │                                                  │
│   ┌───────────────────────────────────────┼───────────────────────────────────────────────┐ │
│   │                              MCP TOOL LAYER                                            │ │
│   │                                       │                                                │ │
│   │   LOCAL MCP SERVERS                   │       REMOTE MCP SERVERS                      │ │
│   │   ══════════════════                  │       ════════════════════                    │ │
│   │   ┌─────────────────┐                 │       ┌─────────────────┐                     │ │
│   │   │  IB Trading MCP │                 │       │  Polygon.io MCP │                     │ │
│   │   │  (Our Server)   │                 │       │  (Market Data)  │                     │ │
│   │   └─────────────────┘                 │       └─────────────────┘                     │ │
│   │   ┌─────────────────┐                 │       ┌─────────────────┐                     │ │
│   │   │  Browser MCP    │                 │       │ Financial Data  │                     │ │
│   │   │  (Puppeteer)    │                 │       │ (SEC, Earnings) │                     │ │
│   │   └─────────────────┘                 │       └─────────────────┘                     │ │
│   │   ┌─────────────────┐                 │       ┌─────────────────┐                     │ │
│   │   │ DB Toolbox MCP  │                 │       │   Octagon MCP   │                     │ │
│   │   │ (BigQuery, SQL) │                 │       │  (Transcripts)  │                     │ │
│   │   └─────────────────┘                 │       └─────────────────┘                     │ │
│   │                                                                                        │ │
│   └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                           │                                                  │
│   ┌───────────────────────────────────────┼───────────────────────────────────────────────┐ │
│   │                         AI GATEWAY LAYER (LiteLLM/OpenRouter)                          │ │
│   │                                       │                                                │ │
│   │   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐                   │ │
│   │   │ Anthropic│ │  OpenAI  │ │  Google  │ │   Meta   │ │ DeepSeek │                   │ │
│   │   │  Claude  │ │  GPT-4   │ │  Gemini  │ │  Llama   │ │  V3/R1   │                   │ │
│   │   │ $3/1M in │ │ $2.5/1M  │ │ $1.25/1M │ │  Free    │ │ $0.27/1M │                   │ │
│   │   └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘                   │ │
│   │                                                                                        │ │
│   │   Task-Based Routing: Complex→Claude, Fast→Gemini, Cheap→DeepSeek                    │ │
│   │                                                                                        │ │
│   └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                           │                                                  │
│   ┌───────────────────────────────────────┼───────────────────────────────────────────────┐ │
│   │                              GCP INFRASTRUCTURE                                        │ │
│   │                                                                                        │ │
│   │   Cloud Run (Agents) │ Firestore (State) │ BigQuery (Analytics) │ Cloud Scheduler    │ │
│   │   Vertex AI (Vectors)│ Neo4j (Graph RAG) │ Cloud Logging        │ Secret Manager     │ │
│   │                                                                                        │ │
│   └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Agent Framework** | Google ADK | Agent orchestration, workflows, evaluation |
| **Tool Protocol** | MCP | Unified tool interface for all agents |
| **AI Gateway** | LiteLLM | Multi-provider LLM routing and cost optimization |
| **Compute** | Cloud Run | Serverless containers, scale-to-zero |
| **Database** | Firestore | Real-time state, positions, configuration |
| **Analytics** | BigQuery | Historical analysis, performance tracking |
| **Knowledge** | Neo4j + ChromaDB | Graph relationships + vector search |
| **Broker** | Interactive Brokers | Trading execution, market data |
| **Observability** | Cloud Logging/Monitoring | Metrics, logs, traces |

---

## 3. Agent Hierarchy

### 3.1 Six-Level Agent Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                              TRADING NEXUS AGENT HIERARCHY                                   │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  LEVEL 0: SYSTEM AGENTS (Infrastructure)                                                    │
│  ═══════════════════════════════════════                                                    │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                           │
│  │   Health    │ │   Circuit   │ │Reconciliation│ │  Scheduler  │                           │
│  │   Monitor   │ │   Breaker   │ │    Agent    │ │   Agent     │                           │
│  │             │ │   Manager   │ │             │ │             │                           │
│  │ ADK: Loop   │ │ ADK: LLM    │ │ ADK: Seq    │ │ ADK: Loop   │                           │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘                           │
│                                                                                              │
│  LEVEL 1: PORTFOLIO ORCHESTRATOR (Command)                                                  │
│  ═════════════════════════════════════════                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐              │
│  │                         PORTFOLIO ORCHESTRATOR                            │              │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                        │              │
│  │  │   Capital   │ │    Risk     │ │Authorization│  ADK: SequentialAgent  │              │
│  │  │  Allocator  │ │  Governor   │ │    Gate     │                        │              │
│  │  └─────────────┘ └─────────────┘ └─────────────┘                        │              │
│  └──────────────────────────────────────────────────────────────────────────┘              │
│                                                                                              │
│  LEVEL 2: STRATEGY COORDINATORS (Planning)                                                  │
│  ═════════════════════════════════════════                                                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                                           │
│  │  Earnings   │ │   Income    │ │   Hedging   │                                           │
│  │ Coordinator │ │ Coordinator │ │ Coordinator │  ADK: LlmAgent                            │
│  │             │ │ (CC/CSP/IC) │ │             │                                           │
│  └─────────────┘ └─────────────┘ └─────────────┘                                           │
│                                                                                              │
│  LEVEL 3: EXECUTION AGENTS (Action)                                                         │
│  ══════════════════════════════════                                                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                                           │
│  │    Order    │ │  Position   │ │    P&L      │                                           │
│  │   Manager   │ │   Monitor   │ │   Tracker   │  ADK: LlmAgent + LoopAgent               │
│  │             │ │             │ │             │                                           │
│  └─────────────┘ └─────────────┘ └─────────────┘                                           │
│                                                                                              │
│  LEVEL 4: ANALYTICAL AGENTS (Intelligence)                                                  │
│  ═════════════════════════════════════════                                                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                           │
│  │   Stock     │ │   Market    │ │  Earnings   │ │  Technical  │                           │
│  │  Selection  │ │   Intel     │ │  Calendar   │ │  Analysis   │  ADK: ParallelAgent      │
│  │   Agent     │ │   Agent     │ │   Agent     │ │   Agent     │                           │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘                           │
│                                                                                              │
│  LEVEL 5: DATA AGENTS (Foundation)                                                          │
│  ═════════════════════════════════                                                          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                           │
│  │     IB      │ │   Content   │ │   Graph     │ │   Vector    │                           │
│  │  Connector  │ │  Processor  │ │    RAG      │ │   Search    │  MCP Tools               │
│  │             │ │             │ │             │ │             │                           │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘                           │
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Agent Inventory (22+ Agents)

| Level | Agent | ADK Type | Purpose |
|-------|-------|----------|---------|
| 0 | Health Monitor | LoopAgent | System health checks |
| 0 | Circuit Breaker Manager | LlmAgent | Risk circuit breakers |
| 0 | Reconciliation Agent | SequentialAgent | State synchronization |
| 0 | Scheduler Agent | LoopAgent | Cron jobs and triggers |
| 1 | Portfolio Orchestrator | SequentialAgent | Capital allocation |
| 1 | Risk Governor | LlmAgent | Portfolio risk limits |
| 1 | Authorization Gate | LlmAgent | Final trade approval |
| 2 | Earnings Coordinator | LlmAgent | Earnings trade strategy |
| 2 | Income Coordinator | LlmAgent | CC/CSP/IC strategies |
| 2 | Hedging Coordinator | LlmAgent | Portfolio protection |
| 3 | Order Manager | LlmAgent | Order execution |
| 3 | Position Monitor | LoopAgent | Position tracking |
| 3 | P&L Tracker | LoopAgent | Profit/loss monitoring |
| 4 | Stock Selection Agent | LlmAgent | Ticker screening |
| 4 | Market Intel Agent | LlmAgent | Market conditions |
| 4 | Earnings Calendar Agent | LlmAgent | Earnings schedule |
| 4 | Technical Analysis Agent | LlmAgent | Chart patterns |
| 4 | Sentiment Agent | LlmAgent | News/social sentiment |
| 5 | IB Connector | MCP Tools | Broker integration |
| 5 | Content Processor | MCP Tools | Document processing |
| 5 | Graph RAG Agent | MCP Tools | Knowledge retrieval |
| 5 | Vector Search Agent | MCP Tools | Semantic search |

---

## 4. Data Architecture

### 4.1 Database Strategy

| Store | Technology | Purpose |
|-------|------------|---------|
| **Operational** | Firestore | Real-time state, positions, config |
| **Analytical** | BigQuery | Historical data, performance analysis |
| **Knowledge Graph** | Neo4j | Entity relationships, pattern learning |
| **Vector Store** | ChromaDB / Vertex AI | Semantic search, embeddings |

### 4.2 Firestore Collections

```
trading_nexus/
├── positions/              # Active positions
│   └── {position_id}
│       ├── symbol, quantity, entry_price
│       ├── state (10-state machine)
│       ├── greeks, pnl
│       └── timestamps
│
├── trades/                 # Trade history
│   └── {trade_id}
│       ├── order details
│       ├── fills, commissions
│       └── analysis metadata
│
├── analyses/               # Agent analyses
│   └── {analysis_id}
│       ├── agent outputs
│       ├── ensemble votes
│       └── consensus result
│
├── llm_logs/              # LLM call tracking
│   └── {log_id}
│       ├── provider, model, tokens
│       ├── cost, latency
│       └── quality_score
│
└── system/                # Configuration
    ├── agent_configs
    ├── circuit_breakers
    └── risk_limits
```

### 4.3 Knowledge Graph Schema (Neo4j)

```
NODES:
├── Stock (ticker, sector, market_cap)
├── EarningsEvent (date, quarter, surprise)
├── Trade (entry, exit, pnl, strategy)
├── Analysis (agent, prediction, confidence)
├── Pattern (type, success_rate)
└── Bias (type, frequency, impact)

RELATIONSHIPS:
├── Stock -[HAD_EARNINGS]-> EarningsEvent
├── Trade -[BASED_ON]-> Analysis
├── Trade -[FOLLOWED]-> Pattern
├── Analysis -[SHOWED]-> Bias
└── Pattern -[SIMILAR_TO]-> Pattern
```

---

## 5. Agent Ensemble Engine

### 5.1 Multi-LLM Voting Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                              AGENT ENSEMBLE ENGINE                                           │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│   ┌───────────────────────────────────────────────────────────────────────────────────────┐ │
│   │                         VOTING AGENTS (ParallelAgent)                                  │ │
│   │                                                                                        │ │
│   │   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │ │
│   │   │  Reasoning  │ │  Technical  │ │  Sentiment  │ │ Contrarian  │ │    Risk     │    │ │
│   │   │   Agent     │ │   Agent     │ │   Agent     │ │   Agent     │ │   Agent     │    │ │
│   │   │             │ │             │ │             │ │             │ │             │    │ │
│   │   │ Claude 3.5  │ │ Gemini 2.0  │ │ GPT-4o-mini │ │ DeepSeek V3 │ │ Llama 3.1   │    │ │
│   │   │   Sonnet    │ │    Flash    │ │             │ │             │ │    70B      │    │ │
│   │   │             │ │             │ │             │ │             │ │             │    │ │
│   │   │ Weight: 30% │ │ Weight: 20% │ │ Weight: 20% │ │ Weight: 15% │ │ Weight: 15% │    │ │
│   │   └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘    │ │
│   │          │               │               │               │               │            │ │
│   │          └───────────────┴───────────────┴───────────────┴───────────────┘            │ │
│   │                                          │                                             │ │
│   │                                          ▼                                             │ │
│   │   ┌──────────────────────────────────────────────────────────────────────────────┐   │ │
│   │   │                         CONSENSUS AGENT (LlmAgent)                            │   │ │
│   │   │                                                                               │   │ │
│   │   │   Model: Claude 3.5 Sonnet                                                   │   │ │
│   │   │   Function: Synthesize votes, detect conflicts, produce final recommendation │   │ │
│   │   │                                                                               │   │ │
│   │   │   Output:                                                                     │   │ │
│   │   │   ├── Direction: BULLISH | BEARISH | NEUTRAL                                 │   │ │
│   │   │   ├── Conviction: 1-10                                                       │   │ │
│   │   │   ├── Consensus Level: STRONG | MODERATE | WEAK | SPLIT                     │   │ │
│   │   │   ├── Key Factors: [list]                                                    │   │ │
│   │   │   └── Dissenting Views: [list]                                               │   │ │
│   │   │                                                                               │   │ │
│   │   └──────────────────────────────────────────────────────────────────────────────┘   │ │
│   │                                                                                        │ │
│   └───────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 AI Gateway Integration (LiteLLM)

```python
# Agent configuration with LiteLLM models
AGENT_CONFIGS = {
    "reasoning_agent": {
        "model": "anthropic/claude-3.5-sonnet",
        "weight": 0.30,
        "max_tokens": 4096,
        "temperature": 0.3
    },
    "technical_agent": {
        "model": "google/gemini-2.0-flash",
        "weight": 0.20,
        "max_tokens": 2048,
        "temperature": 0.2
    },
    "sentiment_agent": {
        "model": "openai/gpt-4o-mini",
        "weight": 0.20,
        "max_tokens": 2048,
        "temperature": 0.3
    },
    "contrarian_agent": {
        "model": "deepseek/deepseek-chat",
        "weight": 0.15,
        "max_tokens": 2048,
        "temperature": 0.5
    },
    "risk_agent": {
        "model": "together_ai/meta-llama/Llama-3.1-70B",
        "weight": 0.15,
        "max_tokens": 2048,
        "temperature": 0.2
    }
}
```

### 5.3 Cost Optimization by Task

| Task Type | Model Choice | Cost/1M tokens | Rationale |
|-----------|--------------|----------------|-----------|
| **Complex Analysis** | Claude 3.5 Sonnet | $3.00 | Best reasoning |
| **Fast Queries** | Gemini 2.0 Flash | $0.075 | Speed + quality |
| **Simple Tasks** | DeepSeek V3 | $0.27 | 95% quality, 10% cost |
| **Bulk Processing** | Llama 3.1 70B | $0.88 | Good balance |
| **Code Generation** | Claude 3.5 Sonnet | $3.00 | Best for code |

**Monthly LLM Cost Estimate**: $12-15 (down from $33 with single-provider approach)

---

## 6. Implementation Framework: Google ADK

### 6.1 Why Google ADK

| Requirement | ADK Capability |
|-------------|----------------|
| **22+ Agent Hierarchy** | Multi-agent by design, hierarchical composition |
| **GCP Infrastructure** | Native Vertex AI Agent Engine deployment |
| **Developer Experience** | Built-in Web UI for debugging, state inspection |
| **Model Flexibility** | LiteLLM integration for 200+ models |
| **Evaluation** | Built-in AgentEvaluator framework |
| **Workflows** | SequentialAgent, ParallelAgent, LoopAgent |

### 6.2 ADK Agent Types Mapping

| ADK Type | Trading Nexus Use |
|----------|-------------------|
| **LlmAgent** | Strategy agents, analytical agents |
| **SequentialAgent** | Analysis pipelines, trade lifecycle |
| **ParallelAgent** | Voting ensemble (5 agents parallel) |
| **LoopAgent** | Position monitor, health checks |
| **MCPToolset** | All tool integrations |

### 6.3 Example: Earnings Analysis Pipeline

```python
from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent
from google.adk.tools.mcp_tool import MCPToolset

# Connect to MCP tools
ib_tools = MCPToolset.from_server(
    connection_params=StdioServerParameters(
        command="python", args=["-m", "ib_mcp_server"]
    )
)

financial_tools = MCPToolset.from_server(
    connection_params=StreamableHTTPParameters(
        url="https://mcp.financialdatasets.ai/mcp"
    )
)

# Define voting agents (parallel execution)
voting_agents = ParallelAgent(
    name="VotingEnsemble",
    sub_agents=[
        LlmAgent(name="ReasoningAgent", model="anthropic/claude-3.5-sonnet", 
                 tools=[ib_tools, financial_tools]),
        LlmAgent(name="TechnicalAgent", model="google/gemini-2.0-flash",
                 tools=[ib_tools]),
        LlmAgent(name="SentimentAgent", model="openai/gpt-4o-mini"),
        LlmAgent(name="ContrarianAgent", model="deepseek/deepseek-chat"),
        LlmAgent(name="RiskAgent", model="together_ai/meta-llama/Llama-3.1-70B"),
    ]
)

# Consensus agent
consensus_agent = LlmAgent(
    name="ConsensusAgent",
    model="anthropic/claude-3.5-sonnet",
    instruction="Synthesize votes and produce unified recommendation"
)

# Full pipeline
earnings_pipeline = SequentialAgent(
    name="EarningsAnalysisPipeline",
    sub_agents=[voting_agents, consensus_agent]
)
```

---

## 7. MCP-First Tool Architecture

### 7.1 MCP Strategy

All agents access tools through MCP (Model Context Protocol) for:
- **Unified Interface**: Same protocol for all 22+ agents
- **Ecosystem Leverage**: Reuse ~2,000 existing MCP servers
- **Future-Proof**: Industry standard (OpenAI, Google, Microsoft adopted)

### 7.2 MCP Server Inventory

#### Local MCP Servers (Build/Maintain)

| Server | Purpose | Status |
|--------|---------|--------|
| **IB Trading MCP** | Trading execution, portfolio, market data | ✅ Built |
| **Browser MCP** | Web scraping, protected articles | ✅ Built |
| **Files MCP** | Analysis storage, markdown | ✅ Available |

#### Remote MCP Servers (Reuse)

| Server | Provider | Purpose |
|--------|----------|---------|
| **Polygon.io** | Official | Market data, 35+ tools |
| **Financial Datasets** | Official | SEC filings, financials |
| **SEC EDGAR** | Community | 10-K, 10-Q, 8-K filings |
| **Octagon AI** | Official | Earnings transcripts |
| **Alpha Vantage** | Official | Technical indicators |
| **MCP Toolbox** | Google | Database access (BigQuery) |

### 7.3 Build vs. Reuse

| Category | Strategy | Servers |
|----------|----------|---------|
| Trading Execution | BUILD | Our IB MCP |
| Market Data | REUSE | Polygon, Alpha Vantage |
| SEC Filings | REUSE | SEC EDGAR, Financial Datasets |
| Earnings Data | REUSE | Octagon AI |
| Database | REUSE | MCP Toolbox |
| Browser | BUILD | Our Puppeteer MCP |

**Estimated Savings**: ~8-10 weeks of development time

---

## 8. Infrastructure Design

### 8.1 GCP Services

| Service | Purpose | Cost/Month |
|---------|---------|------------|
| **Cloud Run** | Agent containers | $20-40 |
| **Firestore** | Real-time state | $10-20 |
| **BigQuery** | Analytics | $5-15 |
| **Cloud Scheduler** | Cron jobs | $1 |
| **Secret Manager** | API keys | $1 |
| **Cloud Logging** | Observability | $5-10 |
| **Vertex AI** | Vector search | $20-35 |
| **Neo4j (Aura Pro)** | Graph RAG | $0-65 |

**Note**: Cloud Run costs assume IB MCP server runs ~always-on during market hours (~$65-70/month alone).

**GCP Subtotal**: $95-165/month

### 8.2 External Services

| Service | Purpose | Cost/Month |
|---------|---------|------------|
| **LLM APIs** | AI Gateway (mixed models) | $50-150 |
| **IB Market Data** | Real-time quotes | $0-40 |
| **Polygon.io** | Market data | $0-29 |
| **Financial Data APIs** | SEC, earnings | $10-30 |

**External Subtotal**: $60-250/month

**See [COST_ANALYSIS.md](COST_ANALYSIS.md) for detailed breakdown.**

### 8.3 Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                              GCP DEPLOYMENT                                                  │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│   Cloud Run Services:                                                                        │
│   ├── trading-nexus-agents (ADK agents)                                                     │
│   ├── ib-mcp-server (IB integration)                                                        │
│   └── browser-mcp-server (web scraping)                                                     │
│                                                                                              │
│   Firestore:                                                                                 │
│   └── trading_nexus (database)                                                              │
│       ├── positions, trades, analyses                                                       │
│       └── llm_logs, system                                                                  │
│                                                                                              │
│   BigQuery:                                                                                  │
│   └── trading_analytics (dataset)                                                           │
│       ├── trade_history, agent_performance                                                  │
│       └── llm_metrics, market_data                                                          │
│                                                                                              │
│   Cloud Scheduler:                                                                           │
│   ├── daily-prep (6:00 AM ET)                                                               │
│   ├── market-open (9:30 AM ET)                                                              │
│   ├── position-monitor (every 15 min)                                                       │
│   └── market-close (4:00 PM ET)                                                             │
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. Implementation Roadmap

### 9.1 16-Week Phased Approach

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                              IMPLEMENTATION ROADMAP                                          │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  PHASE 1: FOUNDATION (Weeks 1-4)                                                            │
│  ═══════════════════════════════                                                            │
│  Week 1-2: Google ADK Setup                                                                 │
│  ├── Install ADK, configure dev environment                                                │
│  ├── Create first LlmAgent with IB MCP tools                                               │
│  └── Test with ADK Dev UI                                                                  │
│                                                                                              │
│  Week 3-4: Core Infrastructure                                                              │
│  ├── Firestore schema deployment                                                            │
│  ├── BigQuery tables creation                                                               │
│  └── Cloud Run initial deployment                                                           │
│                                                                                              │
│  PHASE 2: AGENT ENSEMBLE (Weeks 5-8)                                                        │
│  ═══════════════════════════════════                                                        │
│  Week 5-6: Voting Agents                                                                    │
│  ├── Implement 5 voting agents with ParallelAgent                                          │
│  ├── Configure LiteLLM with multiple providers                                             │
│  └── Test parallel execution                                                                │
│                                                                                              │
│  Week 7-8: Consensus & Pipeline                                                             │
│  ├── Implement ConsensusAgent                                                               │
│  ├── Create SequentialAgent pipeline                                                        │
│  └── Add logging for evaluation                                                             │
│                                                                                              │
│  PHASE 3: MCP INTEGRATION (Weeks 9-12)                                                      │
│  ═════════════════════════════════════                                                      │
│  Week 9-10: Third-Party MCP Servers                                                         │
│  ├── Integrate Polygon.io MCP                                                               │
│  ├── Integrate Financial Datasets MCP                                                       │
│  └── Integrate SEC EDGAR MCP                                                                │
│                                                                                              │
│  Week 11-12: Graph RAG                                                                      │
│  ├── Neo4j schema deployment                                                                │
│  ├── ChromaDB vector store                                                                  │
│  └── Knowledge retrieval pipeline                                                           │
│                                                                                              │
│  PHASE 4: PRODUCTION (Weeks 13-16)                                                          │
│  ══════════════════════════════════                                                         │
│  Week 13-14: Strategy Agents                                                                │
│  ├── Earnings Coordinator                                                                   │
│  ├── Income Coordinator (CC/CSP)                                                            │
│  └── Risk Governor                                                                          │
│                                                                                              │
│  Week 15-16: Production Hardening                                                           │
│  ├── Circuit breakers                                                                       │
│  ├── Monitoring dashboards                                                                  │
│  └── Documentation                                                                          │
│                                                                                              │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 9.2 Phase Deliverables

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| **Foundation** | Weeks 1-4 | ADK setup, Firestore, Cloud Run, basic agent |
| **Ensemble** | Weeks 5-8 | 5 voting agents, consensus, LiteLLM integration |
| **MCP** | Weeks 9-12 | Third-party MCPs, Graph RAG, knowledge base |
| **Production** | Weeks 13-16 | Strategy agents, circuit breakers, monitoring |

---

## 10. Success Metrics

### 10.1 Realistic Win Rate Expectations

**Professional Benchmarks** (not 75%+ hype):

| Strategy Type | Realistic Win Rate | Key Metric |
|---------------|-------------------|------------|
| Earnings Directional | 45-55% | 2:1+ risk/reward |
| Income Strategies | 65-75% | Premium capture |
| Overall Portfolio | 50-60% | Profit factor > 1.5 |

### 10.2 Primary Metrics (Priority Order)

| Rank | Metric | Target | Why |
|------|--------|--------|-----|
| 1 | **Profit Factor** | > 1.5 | Gross profit / gross loss |
| 2 | **Risk-Adjusted Return** | > 1.0 Sharpe | Return per unit risk |
| 3 | **Max Drawdown** | < 15% | Capital preservation |
| 4 | **Win Rate** | > 50% | Secondary to above |

### 10.3 System Metrics

| Category | Metric | Target |
|----------|--------|--------|
| **Uptime** | System availability | > 99.5% |
| **Latency** | Agent response time | < 5s average |
| **LLM Cost** | Monthly spend | < $20 |
| **Accuracy** | Analysis quality | Tracked per agent |

### 10.4 Learning Metrics

| Metric | Purpose |
|--------|---------|
| **Bias Detection Rate** | Identify systematic errors |
| **Framework Evolution** | Track methodology improvements |
| **Pattern Recognition** | Measure predictive accuracy |
| **Agent Accuracy** | Compare provider performance |

---

## Appendix A: Quick Reference

### A.1 Key Commands

```bash
# Start ADK Dev UI
adk web

# Run agent locally
adk run earnings_agent

# Deploy to Cloud Run
gcloud run deploy trading-nexus-agents --source .

# View logs
gcloud logging read "resource.type=cloud_run_revision"
```

### A.2 Key Files

| File | Purpose |
|------|---------|
| `agents/earnings_agent.py` | Earnings analysis agent |
| `agents/ensemble.py` | Voting ensemble |
| `tools/ib_mcp_server.py` | IB integration |
| `config/agent_configs.yaml` | Agent configurations |

### A.3 Key URLs

| Resource | URL |
|----------|-----|
| ADK Documentation | https://google.github.io/adk-docs/ |
| MCP Registry | https://modelcontextprotocol.io |
| LiteLLM Docs | https://docs.litellm.ai |
| Project Repository | (internal) |

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-01 | Initial platform proposal |
| 1.3 | 2026-01-02 | Added AI Gateway architecture |
| 2.0 | 2026-01-02 | Consolidated spec with ADK + MCP decisions |

---

**End of Specification**
