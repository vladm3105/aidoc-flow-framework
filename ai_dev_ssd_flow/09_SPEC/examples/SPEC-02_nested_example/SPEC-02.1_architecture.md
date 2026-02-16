---
doc_id: SPEC-02
section: 1
title: "Architecture"
parent_doc: "SPEC-02.0_index.md"
tags:
  - section-file
  - spec-section
  - layer-10-artifact
custom_fields:
  section_type: content
  artifact_type: SPEC
  layer: 10
  split_type: section
---

# SPEC-02.1: Architecture

## Overview

This section provides the narrative context and rationale for the `nested_example` component defined in `SPEC-02_nested_example.yaml`.

## Diagram (optional)

```mermaid
flowchart LR
  Client -->|ping| ExampleService
  ExampleService -->|responds| Client
```

## Notes

- YAML remains monolithic for deterministic code generation.
- Narrative and diagrams live in Markdown to aid review.

