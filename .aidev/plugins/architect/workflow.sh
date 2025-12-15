#!/bin/bash
# .aidev/plugins/architect/workflow.sh

# CONFIG
SOURCE_BDD="docs/BDD/BDD-001.feature"
TARGET_ADR="docs/ADR/ADR-Draft.md"
PROMPT_DIR=".aidev/plugins/architect/prompts"

echo "🤖 Architect (Gemini) starting..."

# 1. Execute (Gemini)
# Gemini has context window for all upstream docs
gemini generate -t "$(cat $PROMPT_DIR/writer.md)
Context BDD:
$(cat $SOURCE_BDD)" > $TARGET_ADR

# 2. Review (Claude)
# Claude critiques the logic
claude --prompt "$(cat $PROMPT_DIR/reviewer.md)
Draft ADR:
$(cat $TARGET_ADR)" > docs/ADR/ADR-Review.md
