# Working with Large Files in Gemini CLI: Practical Solutions

## Your Situation
- **File:** 60KB BRD (IB_MCP_Server_BRD.md)
- **Problem:** Gemini CLI's @ reference limited to ~13K tokens
- **Goal:** Keep single file, still use Gemini CLI when needed

---

## Solution Options (Best to Worst)

### ✅ Option 1: Let Gemini Use File Read Tool (RECOMMENDED)

Instead of using `@filename`, let Gemini's built-in file read tool handle it automatically.

**How it works:**
```bash
gemini

# Then in the conversation:
> "Read the file IB_MCP_Server_BRD.md and summarize the key requirements"
```

**What happens:**
- Gemini CLI will use its `read_file` tool automatically
- The tool reads files in chunks (2000 lines default)
- Gemini processes it intelligently, focusing on relevant parts
- No token limit error!

**Advantages:**
- ✅ No file modification needed
- ✅ Works with any file size
- ✅ Gemini decides what to read
- ✅ Can request specific sections

**Example Usage:**
```bash
gemini

# General queries
> "What are the main functional requirements in IB_MCP_Server_BRD.md?"

# Specific sections
> "Read section 5 of IB_MCP_Server_BRD.md about functional requirements"

# Targeted analysis
> "Analyze the security requirements in IB_MCP_Server_BRD.md"

# Implementation
> "Based on IB_MCP_Server_BRD.md, implement the get_market_data tool"
```

**Best for:** 
- General queries about the document
- Letting AI decide what's relevant
- Quick questions without setup

---

### ✅ Option 2: Use Offset/Limit Parameters

Manually control which parts of the file Gemini reads.

**How it works:**
```bash
gemini

# Read first 500 lines
> "Read IB_MCP_Server_BRD.md with limit 500"

# Read lines 500-1000
> "Read IB_MCP_Server_BRD.md with offset 500 and limit 500"

# Read last 500 lines (after finding total)
> "Read IB_MCP_Server_BRD.md from line 1200 to end"
```

**Advantages:**
- ✅ No file modification needed
- ✅ Full control over what's loaded
- ✅ Can progressively read entire file
- ✅ Good for sequential reading

**Disadvantages:**
- ⚠️ More manual work
- ⚠️ Need to know file structure
- ⚠️ Multiple queries needed for large docs

**Best for:**
- Working through document section by section
- When you know exactly what part you need
- Systematic review of entire document

---

### ✅ Option 3: Create Companion Summary File

Keep original 60KB file + create small 10KB summary for quick Gemini access.

**Structure:**
```
/project
  ├── IB_MCP_Server_BRD.md           (60KB - full version)
  └── IB_MCP_Server_BRD_Summary.md   (10KB - for Gemini @)
```

**Summary file contents (10KB):**
```markdown
# IB MCP Server BRD - Quick Reference

> Full document: IB_MCP_Server_BRD.md (60KB)

## Executive Summary
[2KB - key objectives, scope, timeline]

## Quick Reference: Tools & Requirements
[4KB - tool names, main parameters, priority requirements]

## Technical Stack
[2KB - architecture, APIs, dependencies]

## Critical Requirements
[2KB - must-haves, security, compliance]

---
For full details, see: IB_MCP_Server_BRD.md
```

**Usage:**
```bash
# Quick questions - use summary
gemini @IB_MCP_Server_BRD_Summary.md "What tools are we building?"

# Deep dive - use read tool on full doc
gemini "Read section 5.2 of IB_MCP_Server_BRD.md for market data specs"
```

**Advantages:**
- ✅ Fast @ reference for quick questions
- ✅ Full document preserved for detailed work
- ✅ Best of both worlds
- ✅ Summary useful for other tools too

**Disadvantages:**
- ⚠️ Need to maintain summary file
- ⚠️ Two files to keep in sync

**Best for:**
- Frequent Gemini CLI usage
- Quick reference needs
- When you need both speed and depth

---

### ⚠️ Option 4: Use /compress Command

Load document in conversation, then compress to free context.

**How it works:**
```bash
gemini

# Load document naturally (Gemini will read it)
> "Analyze the IB_MCP_Server_BRD.md document"
[Gemini reads and responds]

# If conversation gets long, compress
> /compress

# Continue working with compressed context
> "Now implement the place_order tool based on the BRD"
```

**Advantages:**
- ✅ No file modification
- ✅ Full document context initially
- ✅ Can extend long conversations

**Disadvantages:**
- ⚠️ Loses detail after compression
- ⚠️ Need to repeat for new conversations
- ⚠️ May lose important specifics

**Best for:**
- One-time deep analysis
- Long implementation sessions
- When you need full context initially

---

### ⚠️ Option 5: Use GEMINI.md Project Instructions

Put key parts of BRD into GEMINI.md for persistent context.

**How it works:**
```bash
# Create .gemini/GEMINI.md in your project
cat > .gemini/GEMINI.md << 'EOF'
# IB MCP Server Project Context

## Project Overview
- Building MCP server for Interactive Brokers
- Full BRD: IB_MCP_Server_BRD.md (60KB)

## Key Requirements (High Level)
[Copy 2-3KB of most important requirements]

## Implementation Guidelines
[Copy key technical decisions]

## For full details:
Always refer to IB_MCP_Server_BRD.md using file read tools
EOF

# Now use Gemini
gemini
> "Implement get_market_data based on the BRD"
```

**Advantages:**
- ✅ Context available in every session
- ✅ No need to re-load
- ✅ Original file preserved

**Disadvantages:**
- ⚠️ Limited to ~10KB in GEMINI.md
- ⚠️ Manual extraction/maintenance
- ⚠️ Not full document context

**Best for:**
- Ongoing project work
- Consistent reference needs
- Working with same project frequently

---

## Recommended Workflow (Best Approach)

**Combine Option 1 + Option 3 for maximum flexibility:**

### Setup:
```bash
# Keep your files
IB_MCP_Server_BRD.md           # 60KB full version
IB_MCP_Server_BRD_Quick.md     # 10KB quick reference
```

### Usage Pattern:

**For Quick Questions:**
```bash
gemini @IB_MCP_Server_BRD_Quick.md "What's the timeline?"
```

**For Detailed Implementation:**
```bash
gemini

> "Read the functional requirements section from IB_MCP_Server_BRD.md 
   and help me implement the get_market_data tool"
```

**For Comprehensive Analysis:**
```bash
gemini

> "I need to analyze security requirements. 
   Please read sections 6.3 and 11 from IB_MCP_Server_BRD.md"
```

---

## Quick Reference Commands

### Direct File Reading (No @ needed)
```bash
# Let Gemini read automatically
gemini
> "Summarize IB_MCP_Server_BRD.md"

# Request specific sections
> "What does section 5.2 in IB_MCP_Server_BRD.md say about market data?"

# Targeted questions
> "Find all security requirements in IB_MCP_Server_BRD.md"
```

### Chunked Reading
```bash
gemini
> "Read first 1000 lines of IB_MCP_Server_BRD.md"
> "Read lines 1000-2000 of IB_MCP_Server_BRD.md"
> "Read from line 2000 to end of IB_MCP_Server_BRD.md"
```

### With Compression
```bash
gemini
> "Read and analyze IB_MCP_Server_BRD.md completely"
[After long conversation]
> /compress
> "Continue implementation based on what we discussed"
```

---

## Creating a Quick Reference File (10KB)

If you choose Option 3, here's a template:

```markdown
# IB MCP Server BRD - Quick Reference (v1.0)

**Full Document:** IB_MCP_Server_BRD.md (60KB)  
**Last Updated:** 2025-11-07

---

## 🎯 Project Overview (500 words)

**Goal:** Build Interactive Brokers MCP Server enabling LLM integration

**Scope:**
- Phase 1 (MVP): Market data, account info, order management
- Timeline: 13 weeks to production launch
- Tech Stack: Python 3.11+, FastMCP, ib-async 2.0.1

**Key Stakeholders:** Product Owner, Engineering, Compliance, Security

---

## 🛠️ MCP Tools Summary (2KB)

### Market Data Tools (Read-Only)
1. `get_market_data` - Real-time quotes
2. `get_historical_data` - Historical prices  
3. `search_contracts` - Find instruments

### Account Tools (Read-Only)
1. `get_account_summary` - Balance, buying power
2. `get_positions` - Current holdings
3. `get_transactions` - Transaction history

### Order Management Tools (Write)
1. `place_order` - Submit orders (CRITICAL: dry_run parameter)
2. `cancel_order` - Cancel orders
3. `get_order_status` - Check order status

### Analysis Tools (Read-Only)
1. `calculate_portfolio_metrics` - Performance metrics
2. `analyze_position` - Deep position analysis

---

## ⚙️ Technical Architecture (1KB)

**API Integration:**
- Primary: IB Client Portal Web API (REST + WebSocket)
- Secondary: TWS API (TCP socket)

**Authentication:**
- OAuth 2.0 with token refresh
- Session timeout: 30 minutes

**Key Dependencies:**
```python
mcp >= 1.0.0
pydantic >= 2.0
async_client == 1.0.0
aeventkit >= 2.1.0
nest_asyncio
httpx >= 0.24.0
```

**Python Version:** >=3.10 (required for ib-async 2.0.1)
**IB Gateway Version:** >=1023

---

## 🔒 Critical Requirements (1KB)

**Security:**
- TLS 1.3 for all connections
- Pre-trade risk checks
- Rate limiting: 100 req/sec

**Compliance:**
- SEC/FINRA regulations
- Pattern Day Trader rules
- Audit logging for all trades

**Performance:**
- 90% of calls <2 seconds
- 99.5% uptime during market hours

---

## 📋 Must-Have Features (MVP)

**Phase 1 Requirements:**
1. Real-time market data (quotes, depth)
2. Account summary and positions
3. Place/cancel market and limit orders
4. Order status tracking
5. Basic portfolio metrics

**Non-Negotiable:**
- OAuth 2.0 authentication
- Pre-trade validation
- Error recovery
- Comprehensive logging

---

## 🚀 Timeline

- Week 1-2: Planning & Design
- Week 3-8: MVP Development  
- Week 9-10: Security & Compliance
- Week 11-12: Beta Testing
- Week 13: Production Launch

---

## 💡 Usage Notes

**For Implementation Details:**
- Tool specifications: See section 5 in full BRD
- Error handling: See section 6 in full BRD  
- Security specs: See section 11 in full BRD

**For Questions:**
Ask Gemini to read specific sections from IB_MCP_Server_BRD.md

---

**Document Status:** Quick Reference Only  
**Source:** IB_MCP_Server_BRD.md (complete 60KB version)
```

---

## When to Use Which Approach

### Use Option 1 (File Read Tool) When:
- ✅ First time working with the document
- ✅ Need specific sections
- ✅ Exploring the document
- ✅ Implementation questions

### Use Option 2 (Offset/Limit) When:
- ✅ Systematic review needed
- ✅ You know exact line numbers
- ✅ Working through document sequentially

### Use Option 3 (Summary File) When:
- ✅ Frequent Gemini usage
- ✅ Quick reference needs
- ✅ Want best of both worlds
- ✅ Team collaboration (others benefit too)

### Use Option 4 (Compress) When:
- ✅ Long implementation sessions
- ✅ Need full context initially
- ✅ Single deep-dive analysis

### Use Option 5 (GEMINI.md) When:
- ✅ Ongoing project development
- ✅ Consistent context needed
- ✅ Same team working on project

---

## My Recommendation

**Best Solution: Option 1 + Option 3 Combined**

1. **Keep:** IB_MCP_Server_BRD.md (60KB original)
2. **Create:** IB_MCP_Server_BRD_Quick.md (10KB quick reference)
3. **Primary use:** Let Gemini read the full file with file read tool
4. **Quick reference:** Use @ with summary file when needed

**Why this works:**
- ✅ No modification to original file
- ✅ Quick @ reference available (10KB summary)
- ✅ Full document accessible via read tool
- ✅ Minimal maintenance overhead
- ✅ Works with all query types

**Example workflow:**
```bash
# Quick check
gemini @IB_MCP_Server_BRD_Quick.md "Timeline?"

# Implementation  
gemini "Read section 5.2 from IB_MCP_Server_BRD.md and implement get_market_data"

# Deep analysis
gemini "Analyze all security requirements in IB_MCP_Server_BRD.md"
```

---

## Bonus: Creating the 10KB Summary Automatically

You can have Claude Code or another tool create the summary for you:

```bash
# Using Claude Code
claude "Read IB_MCP_Server_BRD.md and create a 10KB quick reference 
        version called IB_MCP_Server_BRD_Quick.md with:
        - Executive summary (500 words)
        - Tool list with parameters (2KB)
        - Technical architecture (1KB)
        - Critical requirements (1KB)
        - Timeline
        Keep it under 10KB total"
```

---

## Summary

**Your Goal:** Keep single 60KB file + use Gemini CLI when needed

**Best Solution:**
1. Keep original file unchanged
2. Let Gemini use file read tool (no @ needed)
3. Optionally create 10KB quick reference for @ usage

**Commands to remember:**
```bash
# Just ask naturally - Gemini reads automatically
gemini
> "Read IB_MCP_Server_BRD.md and summarize key points"

# No @ needed for large files!
# No splitting needed!
# No modifications needed!
```

**Bottom line:** The @ reference limit is real, but the file read tool has no such limit. Just don't use @ for large files, and you're good to go!
