---
title: "AI Assistant Playbook"
tags:
  - framework-guide
  - shared-architecture
  - active
custom_fields:
  document_type: playbook
  priority: shared
  development_status: active
  applies_to: [ai-assistants]
  version: "1.0"
---

# AI Assistant Playbook

Purpose: A concise index that routes AI assistants and developers to the right guidance for executing the framework and using tools effectively.

## Quick Start

- Read this Playbook to choose the right path.
- Follow Execution Rules to bootstrap projects quickly: AI_ASSISTANT_RULES.md.
- Use the Tool Optimization Guide for sizes, validation commands, and tone: AI_TOOL_OPTIMIZATION_GUIDE.md.

## Choose Your Path

- Project Execution Flow (what to do, in what order):
  - AI_ASSISTANT_RULES.md
- Tool Usage, Limits, and Validation (how to use assistants well):
  - AI_TOOL_OPTIMIZATION_GUIDE.md
  - Includes:
    - Quick Start (assistant‑agnostic)
    - Style and Tone Guidelines (All tools; stricter rules for Claude Code)
    - Traceability and Validation (local scripts + assistant tips)
    - Token limits and file splitting guidelines
    - Decision tree and decision matrix by assistant
- Validation Decision-Making (fix doc vs validator vs accept):
  - VALIDATION_DECISION_FRAMEWORK.md (core, all artifacts)
  - 07_REQ/AI_VALIDATION_DECISION_GUIDE.md (REQ-specific addendum)

## Suggested Flow

1) Initialize using Execution Rules: domain → folders → config → templates → CTR decision → indexes → docs.
2) Use Tool Optimization Guide to pick sizes and run validation commands.
3) Create artifacts using templates; keep content token‑efficient and actionable.
4) Validate links, metadata, and traceability; fix findings before commit/PR.
5) Repeat per layer (BRD → … → TASKS → Code) maintaining complete cumulative tags.

## Style & Tone (All Tools)

- Professional engineering tone; no marketing/emotional language.
- Token‑efficient: concise bullets, short paragraphs, concrete commands.
- Actionable outputs: commands, file paths, code identifiers, checklists.
- Emoji: informational only, minimal (0–1 typical).
- See AI_TOOL_OPTIMIZATION_GUIDE.md for detailed guidance and Claude‑specific stricter rules.
