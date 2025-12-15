#!/bin/bash
# .aidev/plugins/product-manager/workflow.sh

# CONFIG
SOURCE_BRD="docs/BRD/BRD-001.md"
TARGET_PRD="docs/PRD/PRD-Draft.md"
PROMPT_DIR=".aidev/plugins/product-manager/prompts"

echo "🤖 PRD Manager (Claude Code) starting..."

# 1. Execute (Claude)
# Claude is best for structured reasoning
claude --prompt "$(cat $PROMPT_DIR/writer.md) 
Context: 
$(cat $SOURCE_BRD)" > $TARGET_PRD

echo "✅ Draft Generate. Starting Review..."

# 2. Review (Gemini)
# Gemini checks against the huge BRD context
gemini generate -t "$(cat $PROMPT_DIR/reviewer.md)
Original BRD:
$(cat $SOURCE_BRD)
Draft PRD:
$(cat $TARGET_PRD)" > docs/PRD/PRD-Review.md
