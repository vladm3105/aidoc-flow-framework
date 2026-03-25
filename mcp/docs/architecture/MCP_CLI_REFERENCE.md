# MCP CLI Reference

| Field | Value |
| --- | --- |
| Status | Active |
| Version | 1.0 |
| Date | 2026-03-24 |
| Scope | CLI command contracts implemented in mcp/src/mcp_server/cli/main.py |

---

## 1. Commands

| Command | Required Arguments | Optional Arguments | Output |
| --- | --- | --- | --- |
| init | --project | none | scaffold summary lines |
| create-build | --project --persona --doc-type --layer --template | --sections-json --out | creation prompt path and layer asset names |
| review-build | --project --persona --doc-type --template --sections-json | --layer --out | review prompt path, sidecar path, inspection path, layer asset names |

---

## 2. Command Contracts

### 2.1 init

Required:
- --project path to project root where docs/UCX assets are created

Behavior:
- Creates project UCX scaffold if missing
- Skips existing files
- Returns created and skipped counts

### 2.2 create-build

Required:
- --project project root containing docs/UCX
- --persona persona file base name
- --doc-type document type label
- --layer SSD layer directory name
- --template template file under docs/UCX/prompt templates creation path

Optional:
- --sections-json path to JSON array with section_id, title, content, included
- --out explicit output directory

Behavior:
- If sections-json is provided, command loads provided sections as SourceSection list.
- If sections-json is omitted, command runs with default internal section fallback behavior.
- If out is omitted, command writes artifacts to `<document_dir>/.ucx_create/creation` when sections-json is provided, otherwise to `<project>/docs/.ucx_create/creation`.
- If out points to a `.ucx_create` folder, command appends `/creation` automatically.
- Command writes creation_prompt.txt, creation_prompt_sidecar.json, and creation_prompt_inspection.json.

Constraint:
- Direct markdown source ingestion as a dedicated create-build mode is not implemented.

### 2.3 review-build

Required:
- --project project root containing docs/UCX
- --persona persona file base name
- --doc-type document type label
- --template review template file
- --sections-json required sections payload path

Optional:
- --layer SSD layer directory name
- --out explicit output directory

Behavior:
- Command requires sections-json input.
- If out is omitted, command writes artifacts to `<document_dir>/.ucx_create/review`.
- If out points to a `.ucx_create` folder, command appends `/review` automatically.
- Command writes review_prompt.txt, review_prompt_sidecar.json, and review_prompt_inspection.json.

---

## 3. Sections JSON Payload Contract

Expected element fields:
- section_id
- title
- content
- included (optional, defaults true)

Required top-level structure:
- JSON array of section objects

Failure modes:
- Missing required field in any section object
- Invalid JSON syntax
- Unreadable file path

---

## 4. Exit Behavior

| Condition | Exit Outcome |
| --- | --- |
| Successful command | return code 0 |
| Unknown or missing command | parser help, return code 2 |
| Runtime error | non-zero process failure |

---

## 5. Examples

### 5.1 Initialize project UCX scaffold

mcp init --project /path/to/project

### 5.2 Build creation prompt with default stage output folder

mcp create-build --project /path/to/project --persona architect --doc-type brd --layer 01_BRD --template BRD-MVP-TEMPLATE.md --sections-json /path/to/sections.json

### 5.3 Build creation prompt with explicit output directory

mcp create-build --project /path/to/project --persona architect --doc-type brd --layer 01_BRD --template BRD-MVP-TEMPLATE.md --sections-json /path/to/sections.json --out /path/to/out

### 5.4 Build review prompt

mcp review-build --project /path/to/project --persona auditor --doc-type brd --template BRD-MVP-TEMPLATE.md --sections-json /path/to/sections.json --out /path/to/out
