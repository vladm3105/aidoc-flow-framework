#!/bin/bash
# .aidev/plugins/tech-lead/workflow.sh

# CONFIG
SOURCE_REQ="docs/REQ/REQ-001.md"
TARGET_SPEC="docs/SPEC/SPEC-Draft.yaml"
PROMPT_DIR=".aidev/plugins/tech-lead/prompts"

echo "🤖 Tech Lead (Claude Code) starting..."

# 1. Execute (Claude)
# SPEC requires deep reasoning to prevent bugs
claude --prompt "$(cat $PROMPT_DIR/writer.md)
Atomic Reqs:
$(cat $SOURCE_REQ)" > $TARGET_SPEC

# 2. Review (Gemini)
gemini generate -t "$(cat $PROMPT_DIR/reviewer.md)
Draft Spec:
$(cat $TARGET_SPEC)" > docs/SPEC/SPEC-Review.md
