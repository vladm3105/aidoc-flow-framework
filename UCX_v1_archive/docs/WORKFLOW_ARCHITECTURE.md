# UCX Workflow Architecture

## Overview

This document explains how UCX orchestrates AI-powered document reviews. Understanding this architecture helps clarify what "personas" and "skills" actually are, and how UCX interacts with AI backends.

**Key Insight**: UCX does NOT create subagents inside the LLM. It orchestrates multiple LLM calls with different prompts.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         UCX Python CLI                          │
│                    (Orchestration Layer)                        │
└─────────────────────────┬───────────────────────────────────────┘
                          │
         ┌────────────────┼────────────────┐
         │                │                │
         ▼                ▼                ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│  Prompt 1   │   │  Prompt 2   │   │  Prompt 3   │
│ + Architect │   │ + Auditor   │   │ + Tech Lead │
│   Skill     │   │   Skill     │   │   Skill     │
└──────┬──────┘   └──────┬──────┘   └──────┬──────┘
       │                 │                 │
       ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AI Backend (One at a time)                   │
│         Claude Code CLI  /  Gemini CLI  /  LiteLLM API          │
└─────────────────────────────────────────────────────────────────┘
       │                 │                 │
       ▼                 ▼                 ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│  Response 1 │   │  Response 2 │   │  Response 3 │
│  (Architect │   │  (Auditor   │   │  (Tech Lead │
│   findings) │   │   findings) │   │   findings) │
└──────┬──────┘   └──────┬──────┘   └──────┬──────┘
       │                 │                 │
       └─────────────────┼─────────────────┘
                         ▼
              ┌─────────────────────┐
              │  UCX Assembles      │
              │  Final Report       │
              └─────────────────────┘
```

---

## Step-by-Step Workflow

### 1. User Runs UCX Command

```bash
ucx review brd docs/01_BRD/BRD-01/
```

### 2. UCX Loads Document Content

```python
# UCX reads the document files
content = document.read_content()  # ~50-150KB of markdown
```

### 3. UCX Builds Prompts with Injected Skills

For each persona, UCX constructs a complete prompt:

```python
prompt = f"""
{architect_skill}        # ← Skill content (domain knowledge)

## Document to Review
{document_content}       # ← The actual BRD content

## Your Task
Review this document as an Architect. Identify issues...
"""
```

### 4. UCX Calls External AI (One Call Per Persona)

**CLI Mode** - runs Claude Code as subprocess:
```python
subprocess.run(
    ["claude", "-p", "--dangerously-skip-permissions", "--model", "opus"],
    input=prompt,
    capture_output=True
)
```

**API Mode** - HTTP call via LiteLLM:
```python
response = litellm.completion(
    model="anthropic/claude-opus-4-5-20251101",
    messages=[{"role": "user", "content": prompt}]
)
```

### 5. UCX Collects Responses and Assembles Report

```python
# UCX parses each response and combines them
final_report = assemble_report([
    architect_response,
    auditor_response,
    tech_lead_response,
    # ... more personas
    chairperson_synthesis  # Final synthesis
])
```

---

## What Skills Actually Are

Skills are **NOT** loaded into the LLM. They are **text injected into prompts**:

```
┌─────────────────────────────────────────────┐
│              PROMPT SENT TO LLM             │
├─────────────────────────────────────────────┤
│ # Platform Architect Domain Knowledge       │  ← SKILL
│                                             │     (injected text)
│ ## Role                                     │
│ Software Architect responsible for...       │
│                                             │
│ ## Review Focus                             │
│ - System structure and modularity           │
│ - Integration patterns                      │
├─────────────────────────────────────────────┤
│ # Document to Review                        │  ← DOCUMENT
│                                             │     (content)
│ [Full BRD content here - 50-150KB]          │
│                                             │
├─────────────────────────────────────────────┤
│ # Instructions                              │  ← TASK
│                                             │     (what to do)
│ Review this BRD as an Architect.            │
│ Output findings in format: [P0-001] ...     │
└─────────────────────────────────────────────┘
```

**The LLM receives plain text** - it has no concept of "skills" or "personas". These are abstractions that UCX uses to organize prompts.

---

## Terminology Clarification

| UCX Concept | What It Actually Is |
|-------------|---------------------|
| **Persona** | A prompt template + skill content + specific instructions |
| **Skill** | Markdown text injected into prompts (domain knowledge) |
| **Subagent** | There are none - UCX makes sequential/parallel LLM API calls |
| **Chairperson** | Final LLM call that receives summary of all prior findings |
| **Review Session** | Series of LLM calls with responses saved to disk |

---

## Two Review Modes

### Unified Prompt Mode (Default)

Single LLM call with all personas in one prompt:

```
User Command
    │
    ▼
┌─────────────────────────────────────┐
│ UCX builds ONE large prompt:        │
│                                     │
│ [Architect Skill]                   │
│ [Auditor Skill]                     │
│ [Tech Lead Skill]                   │
│ ... (all 9-12 skills)               │
│                                     │
│ [Document Content]                  │
│                                     │
│ [Review Instructions]               │
└──────────────┬──────────────────────┘
               │
               ▼
        ┌──────────────┐
        │  1 LLM Call  │
        └──────┬───────┘
               │
               ▼
        ┌──────────────┐
        │   Response   │
        │  (all finds) │
        └──────────────┘
```

**Characteristics:**
- 1 API call
- Lower cost
- Faster execution
- Risk of truncation on large documents
- All personas see full document

### Persona Prompts Mode (`--persona`)

Multiple LLM calls, one per persona:

```
User Command
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                    UCX Orchestration                        │
└─────────────────────────────────────────────────────────────┘
    │           │           │                       │
    ▼           ▼           ▼                       ▼
┌────────┐ ┌────────┐ ┌────────┐             ┌────────────┐
│Prompt 1│ │Prompt 2│ │Prompt 3│    ...      │Prompt N    │
│Architect│ │Auditor │ │Tech Ld │             │Chairperson │
└───┬────┘ └───┬────┘ └───┬────┘             └─────┬──────┘
    │          │          │                        │
    ▼          ▼          ▼                        ▼
┌────────┐ ┌────────┐ ┌────────┐             ┌────────────┐
│LLM Call│ │LLM Call│ │LLM Call│    ...      │LLM Call    │
│   #1   │ │   #2   │ │   #3   │             │   #N       │
└───┬────┘ └───┬────┘ └───┬────┘             └─────┬──────┘
    │          │          │                        │
    ▼          ▼          ▼                        ▼
┌────────┐ ┌────────┐ ┌────────┐             ┌────────────┐
│Response│ │Response│ │Response│             │ Synthesis  │
│   #1   │ │   #2   │ │   #3   │             │  Report    │
└───┬────┘ └───┬────┘ └───┬────┘             └─────┬──────┘
    │          │          │                        │
    └──────────┴──────────┴────────────────────────┘
                          │
                          ▼
               ┌─────────────────────┐
               │  UCX Assembles      │
               │  Final Report       │
               └─────────────────────┘
```

**Characteristics:**
- 8-12 API calls
- Higher cost
- Slower execution
- Resume capability (if interrupted)
- Each persona gets full attention
- Anti-repetition (later personas see prior findings summary)

---

## How Chairperson Sees Prior Findings

The Chairperson persona receives a special prompt that includes summaries of all prior persona findings:

```
┌─────────────────────────────────────────────┐
│         CHAIRPERSON PROMPT                  │
├─────────────────────────────────────────────┤
│ # Chairperson Domain Knowledge              │
│ [Chairperson skill content]                 │
│                                             │
├─────────────────────────────────────────────┤
│ # Prior Findings Summary                    │  ← INJECTED BY UCX
│                                             │
│ ## Architect Findings                       │
│ - [P0-001] Missing state machine            │
│ - [P1-002] No retry policy                  │
│                                             │
│ ## Auditor Findings                         │
│ - [P0-001] GDPR compliance gap              │
│ - [P1-003] Audit logging incomplete         │
│                                             │
│ ## Tech Lead Findings                       │
│ - [P1-001] No error handling spec           │
│ ...                                         │
├─────────────────────────────────────────────┤
│ # Your Task                                 │
│ Synthesize findings, remove duplicates,     │
│ calculate final score, produce manifest.    │
└─────────────────────────────────────────────┘
```

The Chairperson does NOT have special access to prior responses - UCX extracts findings and injects them into the prompt.

---

## Actual Code Flow

```python
# ucx/api/review.py (simplified)
class UCRPhase:
    def review_multi_turn(self, doc_type, doc_path):
        # 1. Load document
        content = self._load_document(doc_path)

        # 2. Get persona list for this doc type
        personas = ["architect", "auditor", "tech_lead", ...]

        # 3. For each persona, make separate LLM call
        responses = []
        prior_findings = []

        for persona in personas:
            # Load skill for this persona
            skill = self._skill_loader.load(persona)

            # Build prompt with skill + document + instructions
            # Later personas also get prior_findings summary
            prompt = self._build_prompt(
                skill=skill,
                content=content,
                persona=persona,
                prior_findings=prior_findings  # Anti-repetition
            )

            # Call external AI (Claude CLI or API)
            response = self._ai_client.generate(prompt)

            # Extract findings for anti-repetition
            findings = self._extract_findings(response)
            prior_findings.extend(findings)

            responses.append(response)

        # 4. Assemble final report from all responses
        return self._assemble_report(responses)
```

---

## AI Backend Interaction

### CLI Mode (Default)

UCX spawns a subprocess to run the AI CLI tool:

```python
# ucx/ai/cli_client.py (simplified)
class CLIClient:
    def generate(self, prompt: str) -> str:
        # Build command
        cmd = [
            "claude",                        # CLI executable
            "-p",                            # Print mode
            "--dangerously-skip-permissions", # Non-interactive
            "--model", "opus"                # Model selection
        ]

        # Run as subprocess with prompt as stdin
        result = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            timeout=600
        )

        return result.stdout
```

### API Mode

UCX makes HTTP API calls via LiteLLM:

```python
# ucx/ai/litellm_client.py (simplified)
class LiteLLMClient:
    def generate(self, prompt: str) -> str:
        response = litellm.completion(
            model=self._model,  # e.g., "anthropic/claude-opus-4-5-20251101"
            messages=[{"role": "user", "content": prompt}],
            max_tokens=8000
        )

        return response.choices[0].message.content
```

---

## Session Memory (Persona Mode)

In persona prompts mode, UCX saves intermediate state to disk:

```
docs/01_BRD/BRD-01/.ucx_review_session/
├── session.json              # Session metadata (hash, completed personas)
├── shared_context.txt        # Document content
├── prompt_architect.txt      # Prompt sent to architect
├── response_architect.txt    # Response from architect
├── prompt_auditor.txt        # Prompt sent to auditor
├── response_auditor.txt      # Response from auditor
├── ...                       # More persona prompts/responses
└── assembled_report.md       # Final assembled report
```

This enables:
- **Resume capability**: If interrupted, UCX skips completed personas
- **Debugging**: Inspect exactly what was sent to/received from LLM
- **Auditing**: Full trace of the review process

---

## Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "UCX creates AI agents" | UCX makes standard LLM API calls with different prompts |
| "Skills are loaded into the LLM" | Skills are text injected into prompts |
| "Personas are subagents" | Personas are prompt templates with specific instructions |
| "The LLM knows about personas" | The LLM only sees the prompt text - no special mode |
| "Chairperson has special access" | UCX extracts findings and includes them in the prompt |
| "Skills give the LLM new abilities" | Skills provide context/instructions in the prompt |

---

## Sequence Diagram: Full Review

```
User                UCX CLI              SkillLoader          AI Backend
 │                    │                      │                    │
 │  ucx review brd    │                      │                    │
 │───────────────────>│                      │                    │
 │                    │                      │                    │
 │                    │  load("architect")   │                    │
 │                    │─────────────────────>│                    │
 │                    │      skill_text      │                    │
 │                    │<─────────────────────│                    │
 │                    │                      │                    │
 │                    │  build_prompt(skill, doc, instructions)   │
 │                    │─────────────────────────────────────────> │
 │                    │                      │                    │
 │                    │                      │   generate(prompt) │
 │                    │──────────────────────────────────────────>│
 │                    │                      │                    │
 │                    │                      │      response_1    │
 │                    │<──────────────────────────────────────────│
 │                    │                      │                    │
 │                    │  (repeat for each persona...)             │
 │                    │                      │                    │
 │                    │  assemble_report()   │                    │
 │                    │───────────────────>  │                    │
 │                    │                      │                    │
 │   final_report.md  │                      │                    │
 │<───────────────────│                      │                    │
```

---

## Summary

| Question | Answer |
|----------|--------|
| Does UCX create subagents inside LLM? | **No** - UCX makes multiple separate LLM calls |
| How are skills used? | Injected as text into prompts before sending to LLM |
| What is a "persona"? | A prompt template + skill content + specific instructions |
| Does the LLM know about personas? | Only what's in the prompt - no special agent mode |
| How does Chairperson see prior findings? | UCX includes summary of prior responses in its prompt |
| What does UCX orchestrate? | Document loading, prompt building, LLM calls, report assembly |

**UCX is a prompt orchestration tool** - it manages the complexity of building effective prompts and assembling results, while the actual AI reasoning happens in standard LLM API calls.
