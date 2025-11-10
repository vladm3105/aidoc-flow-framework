# AI Coding Tools Comparison: File Size & Context Window Guidelines

## Comprehensive Comparison Table

| Feature | Claude Code | Gemini CLI | OpenAI Codex CLI | GitHub Copilot |
|---------|------------|------------|-----------------|----------------|
| **Context Window** | 200K tokens | 1M tokens (conversation)<br/>⚠️ ~13K per file (@) | 200K tokens (codex-mini-latest) | 64K-128K tokens |
| **Optimal File Size** | 20-40KB | 10-13KB per file ⚠️ | 30-60KB | 10-30KB |
| **Max Practical File** | 100KB | 15KB (via @)<br/>Chunks for larger | 100KB | 50KB |
| **Multiple Files** | Up to 50 files | Many files, each <15KB | 20-30 files | 10-20 files (often restricted) |
| **Total Project Context** | ~150K tokens usable | 1M tokens total<br/>(conversation history) | ~150K tokens usable | ~50K tokens usable |
| **Cost** | $3/hour usage (paid) | Free tier: 60 req/min, 1K req/day | Included with ChatGPT Plus/Pro ($20-$200/mo) | $10-$19/mo (Individual/Pro) |
| **Model** | Claude Sonnet 4 | Gemini 2.5 Pro | GPT-5-Codex / o4-mini | GPT-4, o4, Claude, Gemini (multi-model) |
| **Platform Support** | macOS, Linux, Windows | macOS, Linux, Windows (native) | macOS, Linux, Windows (WSL) | All platforms (IDE extension) |
| **Best For** | Complex refactoring | Large codebases | Quick prototyping | Inline completions |
| **Response Format** | Streaming with approval | Interactive TUI | Streaming with diffs | Inline suggestions |
| **Auto-completion** | ❌ No | ❌ No | ❌ No | ✅ Yes |
| **Agentic Actions** | ✅ Yes (file edits, commands) | ✅ Yes (MCP support) | ✅ Yes (sandboxed) | ⚠️ Limited (Chat mode only) |
| **MCP Support** | ✅ Yes | ✅ Yes (extensive) | ✅ Yes | ❌ No |
| **IDE Integration** | CLI only | CLI + VS Code companion | CLI + IDE extension | Native IDE integration |
| **Rate Limits** | Time-based (hourly) | 60 req/min (free), higher (paid) | Plan-dependent | Model-dependent |
| **Caching** | ✅ Prompt caching | ✅ Token caching | ⚠️ Limited | ⚠️ Limited |
| **Memory/Personalization** | ❌ No persistent memory | ✅ GEMINI.md file support | ✅ AGENTS.md / codex.md | ⚠️ Copilot Memory (separate) |
| **Network Access** | Internet access | ✅ Google Search built-in | ⚠️ Sandboxed (API only) | ❌ No direct access |

---

## Detailed File Size Recommendations by Tool

### 1. Claude Code

**Context Window:** 200,000 tokens (~150,000 words or ~600KB text)

#### Optimal File Sizes:
- **Single Document/BRD:** 20-40KB (5,000-10,000 words) ✅ **IDEAL**
- **Code File:** Up to 50KB (1,000-2,000 lines)
- **Multiple Files:** Can handle 30-50 files simultaneously
- **Total Context:** Aim for <150KB total across all files

#### Best Practices:
```
✅ GOOD: 60KB BRD (your current file) - Perfect size
✅ GOOD: 10 files × 10KB each = 100KB total
⚠️ ACCEPTABLE: 100KB single document (still manageable)
❌ AVOID: 200KB+ single file (will truncate or degrade)
```

#### When to Split:
- Files >100KB: Consider splitting into modules
- Complex projects: Use project structure with multiple smaller files
- Documentation: Split large docs into sections with table of contents

---

### 2. Gemini CLI

**Context Window:** 1,000,000 tokens (theoretical), BUT with **important practical limits**

#### ⚠️ CRITICAL: Actual File Reference Limits:
- **Single File via @ reference:** ~13,000 tokens (~10KB-15KB text) ⚠️ **MUCH SMALLER**
- **Total Conversation Context:** Up to 1M tokens (includes conversation history)
- **File read tool limit:** ~2,000 lines by default per file

#### Optimal File Sizes:
- **Single Document/BRD via @:** 10-13KB MAX ⚠️ **YOUR 60KB FILE IS TOO LARGE**
- **Code File via @:** Up to 15KB (500-800 lines max)
- **Multiple Files:** Can reference multiple small files, but each hits same limit
- **Total Context:** 1M tokens for entire conversation, not per file

#### Best Practices:
```
❌ YOUR 60KB BRD: TOO LARGE for @ reference (will hit 13K token limit)
✅ GOOD: Split into 5-6 files × 10KB each
✅ GOOD: Use file read tool with offset/limit parameters for large files
⚠️ WORKAROUND: Let Gemini CLI use file read tool instead of @ reference
```

#### Special Features:
- **Automatic Context Loading:** Can read project directories, but individual files limited
- **@reference syntax:** `@./src` loads directory structure, but large files truncated
- **/compress command:** Summarize long conversations to free context
- **Respects .gitignore:** Won't load node_modules, etc.
- **file read tool:** Use instead of @ for large files (reads in chunks)

#### The Reality:
While Gemini 2.5 Pro has 1M token context window:
1. **@ reference** is limited to ~13K tokens per file
2. **Conversation history** uses the bulk of the 1M tokens
3. **Multiple tool calls** to read large files in chunks
4. **Often hits limit** before reaching 1M with multiple file references

#### When to Split:
- Files >13KB: **MUST SPLIT** for @ reference
- Files >50KB: Even file read tool will struggle
- Use `/compress` frequently with large codebases
- Let Gemini use file tools rather than @ for large files

#### Recommendations:
- **Your 60KB BRD:** ❌ TOO LARGE - Split into 5-6 smaller files
- **Best for:** Iterative development with conversation memory
- **Cost:** Free tier (60 requests/min), but may burn through quickly
- **Reality:** Less generous than advertised for single file access

---

### 3. OpenAI Codex CLI

**Context Window:** 200,000 tokens (codex-mini-latest model)

#### Optimal File Sizes:
- **Single Document/BRD:** 30-60KB (7,500-15,000 words) ✅ **GOOD**
- **Code File:** Up to 60KB (1,500-3,000 lines)
- **Multiple Files:** Can handle 20-30 files
- **Total Context:** Aim for <150KB total

#### Best Practices:
```
✅ GOOD: 60KB BRD - Well within limits
✅ GOOD: 20 files × 10KB each = 200KB (context window match)
⚠️ ACCEPTABLE: 100KB single file
❌ AVOID: 150KB+ (approaching limit)
```

#### Context Management:
- **Standard Mode:** Only loads files explicitly requested (via `cat` or tool calls)
- **Full Context Mode** (`--full-context`): Pre-loads entire project (experimental)
- **Instructions:** `~/.codex/instructions.md` (global) or `codex.md` (project)
- **Conversation History:** Tracked in context window

#### When to Split:
- Files >80KB: Consider splitting
- Use AGENTS.md for project-specific instructions (doesn't count against context)
- Leverage file read tools instead of pasting content

#### Recommendations:
- **Best for:** Quick prototyping, iterative development
- **Your 60KB BRD:** Perfect fit
- **UX Note:** Some users report context handling issues; explicit file loading recommended

---

### 4. GitHub Copilot

**Context Window:** 64,000-128,000 tokens (varies by model)

#### Standard (GPT-4o): 64K tokens
#### Extended (GPT-4o in VS Code Insiders): 128K tokens
#### Gemini 2.5 Pro (when available): Reported as reduced to ~64K in Copilot

#### Optimal File Sizes:
- **Single File:** 10-30KB (2,500-7,500 words) ⚠️ **MORE RESTRICTIVE**
- **Code File:** Up to 40KB (800-1,500 lines)
- **Multiple Files:** 10-20 files maximum
- **Total Context:** Aim for <50KB total

#### Best Practices:
```
⚠️ YOUR 60KB BRD IS TOO LARGE for comfortable Copilot use
✅ BETTER: Split into 3× 20KB files
✅ GOOD: 10 files × 5KB each = 50KB total
❌ AVOID: 60KB+ single file (will truncate)
```

#### Context Limitations:
- **Working Set Limit:** Max 10 files in Copilot Edits
- **Inline Completion:** Only ~60 lines from current file + 20 nearby files
- **Chat Mode:** Can reference more files but still limited
- **#codebase:** Often doesn't include all necessary files (poor retrieval)

#### When to Split:
- Documents >30KB: **MUST SPLIT** for Copilot
- Code files >1,000 lines: Consider refactoring
- Use multiple chat sessions for different contexts

#### Context Strategy for Large Files:
1. **Break into modules:** Core (20KB) + Technical (20KB) + Compliance (20KB)
2. **Use external reference:** Link to full doc, use summaries in Copilot
3. **Chunk interactions:** Ask about one section at a time
4. **Export summaries:** Generate TL;DR versions for Copilot context

#### Recommendations:
- **Your 60KB BRD:** Too large - recommend creating a 20-30KB executive summary
- **Best for:** Inline code completion, quick fixes, small refactors
- **Limitation:** Not ideal for comprehensive document analysis

---

## Specific Recommendations for Your 60KB BRD

### ✅ Claude Code (RECOMMENDED)
- **Status:** Perfect fit - 60KB is in the sweet spot
- **Usage:** Load entire document, ask questions, generate code
- **No modifications needed**

### ✅ Gemini CLI (HIGHLY RECOMMENDED)
- **Status:** Excellent - uses only 6% of context window
- **Usage:** Can load BRD + entire codebase simultaneously
- **Advantage:** Best for comprehensive project understanding
- **No modifications needed**

### ✅ OpenAI Codex CLI (GOOD)
- **Status:** Good fit - within comfortable range
- **Usage:** Load document with `@BRD.md` reference
- **Minor concern:** May need to be selective with additional files
- **No modifications needed**

### ⚠️ GitHub Copilot (NEEDS MODIFICATION)
- **Status:** Too large for optimal use
- **Recommendation:** Create versions:
  - **Executive Summary:** 15-20KB (high-level overview)
  - **Core Requirements:** 20-25KB (functional requirements)
  - **Technical Specs:** 20-25KB (architecture, tools, tech details)
  
**Example Split Structure:**
```
IB_MCP_BRD_Executive.md       (20KB) - Sections 1-4, 13
IB_MCP_BRD_Requirements.md    (25KB) - Sections 5-6, 9
IB_MCP_BRD_Technical.md       (20KB) - Sections 7-8, 10-12
```

---

## Practical Guidelines by Use Case

### Use Case 1: Initial Document Review
**Best Tool:** Gemini CLI or Claude Code

```bash
# Gemini CLI
gemini @IB_MCP_Server_BRD.md "Review this BRD and identify any gaps"

# Claude Code  
claude "Review this BRD comprehensively" < IB_MCP_Server_BRD.md
```

### Use Case 2: Generate Code from Requirements
**Best Tool:** Claude Code or OpenAI Codex

```bash
# Claude Code - Best for complex implementations
claude "Implement the get_market_data tool based on section 5.2.1"

# Codex - Good for quick prototypes
codex "Create MCP tools from the BRD functional requirements"
```

### Use Case 3: Incremental Development with Context
**Best Tool:** Gemini CLI (largest context) or Claude Code

```bash
# Gemini CLI - Can maintain entire project in context
gemini @./src @IB_MCP_Server_BRD.md "Implement next tool maintaining consistency"

# Claude Code - Good context management
claude --files src/ "Continue implementation based on BRD section 5.3"
```

### Use Case 4: Quick Reference & Inline Coding
**Best Tool:** GitHub Copilot

```bash
# Split BRD into smaller files first
# Then reference specific sections in Copilot Chat
# Use for inline completions while implementing
```

---

## Token-to-Size Conversion Reference

| Tokens | Words (approx) | Characters | File Size | Lines of Code |
|--------|---------------|------------|-----------|---------------|
| 1K | 750 | 3,000 | ~3KB | ~60 lines |
| 10K | 7,500 | 30,000 | ~30KB | ~600 lines |
| 50K | 37,500 | 150,000 | ~150KB | ~3,000 lines |
| 100K | 75,000 | 300,000 | ~300KB | ~6,000 lines |
| 200K | 150,000 | 600,000 | ~600KB | ~12,000 lines |
| 1M | 750,000 | 3,000,000 | ~3MB | ~60,000 lines |

**Note:** Token counts vary by language and format:
- English text: ~0.75 words per token
- Code: ~0.5-0.7 tokens per character (language dependent)
- JSON: ~1.2 tokens per key-value pair
- Markdown: ~0.8 words per token (formatting overhead)

---

## Best Practices Summary

### Do's ✅

1. **Size Management:**
   - Keep individual files <40KB for universal compatibility
   - Use 20-30KB as the "safe zone" for all tools
   - Your 60KB BRD is excellent for Claude Code and Gemini CLI

2. **File Organization:**
   - Split large documents logically by section
   - Use clear naming conventions
   - Maintain a table of contents/index file

3. **Tool Selection:**
   - Large codebases → Gemini CLI (1M context)
   - Complex refactoring → Claude Code (quality)
   - Quick prototypes → OpenAI Codex (speed)
   - Inline completions → GitHub Copilot (integration)

4. **Context Optimization:**
   - Use prompt caching (Claude Code, Gemini CLI)
   - Reference files explicitly rather than pasting
   - Compress conversations when they get long (Gemini CLI)
   - Use project-specific instructions files (all tools)

### Don'ts ❌

1. **Avoid:**
   - Single files >100KB (except Gemini CLI)
   - Pasting entire codebases into prompts
   - Assuming all tools handle context equally
   - Ignoring .gitignore patterns

2. **Don't:**
   - Use GitHub Copilot for 60KB+ documents without splitting
   - Exceed rate limits by loading too much at once
   - Mix sensitive and non-sensitive content without checking policies
   - Forget to version control your project before using agentic tools

---

## Cost Considerations

### Claude Code
- **Pricing:** ~$3/hour of active usage
- **Best Value:** Complex tasks requiring deep understanding
- **60KB BRD Cost:** ~$0.50-$1 per comprehensive review session

### Gemini CLI
- **Pricing:** FREE (60 req/min, 1K req/day on personal account)
- **Paid Tier:** Google AI Ultra for higher limits
- **Best Value:** Highest free tier offering
- **60KB BRD Cost:** FREE

### OpenAI Codex CLI
- **Pricing:** Included with ChatGPT Plus ($20/mo), Pro ($200/mo)
- **Token Cost:** ~$0.15-$0.30 per million input tokens (codex-mini)
- **Best Value:** Good if already have ChatGPT subscription
- **60KB BRD Cost:** ~$0.05 per review (if using API directly)

### GitHub Copilot
- **Pricing:** $10/mo (Individual), $19/mo (Pro), $39/user/mo (Business)
- **Best Value:** Continuous inline assistance
- **60KB BRD Cost:** N/A (subscription-based, but would need to split file)

---

## Recommendations by Project Size

### Small Projects (<50 files, <500KB total)
- **Primary:** Claude Code or Gemini CLI (free)
- **Secondary:** OpenAI Codex for quick iterations
- **Your 60KB BRD:** Use as-is with any tool

### Medium Projects (50-200 files, 500KB-2MB)
- **Primary:** Gemini CLI (best context window)
- **Secondary:** Claude Code for specific complex tasks
- **Your 60KB BRD:** Perfect reference document

### Large Projects (200+ files, >2MB)
- **Primary:** Gemini CLI with /compress as needed
- **Strategy:** Use in phases, compress between major milestones
- **Your 60KB BRD:** Keep as anchor document

### Enterprise/Production
- **Primary:** Claude Code or OpenAI Codex (better security/compliance)
- **Backup:** GitHub Copilot for day-to-day development
- **Strategy:** Split BRD into role-specific documents

---

## Final Recommendation for Your 60KB BRD

### ✅ Keep As-Is For:
1. **Claude Code** - Perfect fit (30% of context window)
2. **OpenAI Codex** - Good fit (30% of context window)

### ⚠️ Too Large For:
1. **Gemini CLI** - Exceeds ~13K token @ reference limit ⚠️ **SPLIT REQUIRED**
2. **GitHub Copilot** - Exceeds 30KB comfortable limit

### Suggested Action Plan:

```markdown
# Document Strategy

## Primary Use (No Changes Needed):
- IB_MCP_Server_BRD.md (60KB) → Claude Code, OpenAI Codex

## Split Required For:
### Gemini CLI (Split into 5-6 files ~10KB each):
- IB_MCP_BRD_01_Overview.md (10KB) - Sections 1-3
- IB_MCP_BRD_02_Requirements.md (12KB) - Section 5 (partial)
- IB_MCP_BRD_03_OrderMgmt.md (10KB) - Section 5 (partial)  
- IB_MCP_BRD_04_Technical.md (12KB) - Sections 7-8
- IB_MCP_BRD_05_Security.md (10KB) - Sections 11-12
- IB_MCP_BRD_06_Appendix.md (6KB) - Sections 13-17

### GitHub Copilot (Create summary):
- IB_MCP_Server_BRD_Summary.md (20KB) → GitHub Copilot
  - Include: Sections 1-2, 5 (condensed), 9, 13
  - Omit: Detailed examples, appendices, verbose tables
```

---

## Conclusion

Your 60KB BRD has **different compatibility** across AI coding tools than initially thought:

- ✅ **Claude Code:** Perfect - uses 30% of context
- ❌ **Gemini CLI:** TOO LARGE - @ reference limited to ~13K tokens per file ⚠️
- ✅ **OpenAI Codex:** Good - uses 30% of context
- ❌ **GitHub Copilot:** TOO LARGE - exceeds 30KB comfortable limit

### The Truth About Gemini CLI:

While Gemini 2.5 Pro has a **1M token context window**, the practical reality is:

1. **@ file reference:** Limited to ~13,000 tokens (~10-13KB) per file
2. **1M context:** Used for conversation history, NOT single file loading
3. **File read tool:** Can read larger files in chunks (2000 line default)
4. **Your 60KB file:** Will hit error messages about token limits

### Updated Recommendations:

**✅ Best Tools for Your 60KB BRD As-Is:**
1. **Claude Code** - Excellent choice
2. **OpenAI Codex** - Good choice

**⚠️ Requires Splitting:**
1. **Gemini CLI** - Split into 5-6 files (~10KB each)
2. **GitHub Copilot** - Create 20-30KB summary

**Bottom Line:** Your 60KB BRD is perfect for **Claude Code and OpenAI Codex only**. Both Gemini CLI and GitHub Copilot require you to split or condense the file. The "1M token" Gemini CLI marketing is misleading for single file operations - it's really about total conversation context, not individual file loading.
