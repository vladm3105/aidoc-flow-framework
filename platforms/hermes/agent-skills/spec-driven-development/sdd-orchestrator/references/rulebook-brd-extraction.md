# Rulebook-to-BRD Extraction Workflow

Proven pattern for decomposing a large strategy rulebook (~2,000 lines, 16 sections) into 7–9 feature BRDs with one pass through the validator per BRD.

## Phase 0: Coverage Audit (BEFORE any BRD generation)

1. Extract all section headers: `grep -n '^# ' rulebook.md`
2. Build a coverage matrix: each source section → proposed BRD number + rationale
3. Verify 100% coverage — every section has an explicit BRD home or deliberate exclusion with rationale
4. Identify orphan content — content blocks between section boundaries not captured by any header
5. Get human approval on the matrix before extracting

## Phase 1: Bulk Generation Strategy

Generate all BRDs in Python via `execute_code` using `yaml.dump()` — NOT iterative write_file → validate → patch cycles.

### Reusable structure

Build a base dict template with all 18 standard BRD sections (metadata → appendix). Clone it per BRD, changing only the content sections. This ensures structural consistency across all BRDs — same metadata keys, same section ordering, same format.

Key sections that vary per BRD:

- `id`, `title`
- `executive_summary.overview`
- `introduction` (business_context, purpose, document_scope)
- `business_objectives` (hypothesis, goals, metrics)
- `functional_requirements.requirements[]`
- `diagrams.items[]`
- `traceability` (cross_links, upstream, cross_brd_dependencies)

Key sections that remain structurally identical:

- `metadata` (all keys, only changing `last_updated`)
- `document_control` (only changing date/version)
- `adr_topics` (7 standard topics, only changing business_driver text)
- `quality_expectations`, `constraints_and_assumptions`, `risk_management`
- `approval`, `glossary`, `appendix`

### Element ID generation

Use a deterministic `make_id(doc_id, section_id, label)` function:

- Input: `f"{doc_id}:{section_id}:{label}"[:200].lower()` with special chars stripped
- Hash: `hashlib.sha256(input.encode()).hexdigest()[:4]`
- Output: `BRD.{doc_id:02d}.{section_id:02d}.{hash}`

### Post-processing

After `yaml.dump()`, quote any values starting with `>=`, `<=`, `>`, `<` to prevent YAML chomping-indicator errors. Pattern:

```python
if re.match(r'^[><]=?\s*\d', val) and not val.startswith("'"):
    line = f"{pre}: '{val}'"
```

### Validation step

After file write, validate immediately with `mcp_sdd_lifecycle_sdd_validate`. The two most common issues and their fixes:

1. **metadata.tags has N tags; max 1 for brd** — Reduce tags list to `["brd-document"]` only
2. **diagrams.items is missing or empty** — Populate with at least one diagram item (user journey + integration points for feature BRDs)

## Phase 2: Thin Section Expansion

Some rulebook sections are short (50–60 lines) and produce thin BRDs. Expand these by:

- Adding explicit validation rules derived from the source (not fabricated)
- Cross-referencing related BRDs for interface contracts
- Including acceptance criteria that test the boundaries of the rules
- Pulling in governance context from the umbrella BRD (BRD-01)

Example: §8 + §9 (56 lines) → BRD-05 at 589 lines. The expansion comes from formalizing 5 hard stop conditions with re-entry criteria, 6 position sizing limits with acceptance thresholds, and a pre-entry qualification protocol.

## Validator Quirk: YAML Treated as Markdown

The UCX validator (`sdd_validate`) may fail on structurally valid YAML files, reporting:

- "Missing or invalid YAML frontmatter"
- "Missing required section: Title (H1)"
- Passes show: "Requires YAML data (skipped for MD)"

This happens when the validator's file-type detection heuristic misclassifies a valid `.yaml` file as Markdown. The file parses correctly with `yaml.safe_load()` and is structurally identical to passing BRDs.

**Workaround**: If the UCX validator generates a `*_validated.yaml` file, that file is the validator's own re-serialization of the document. It may differ from the original in whitespace/encoding. Use the validated version as canonical:

```python
if os.path.exists(validated_path):
    with open(validated_path) as f:
        fixed = f.read()
    with open(original_path, 'w') as f:
        f.write(fixed)
```

If the re-validated file still fails with the same error, the issue is in the validator's type detection — acknowledge the gap explicitly. The document is content-complete and YAML-valid; the heuristic false-negative does not indicate a content problem.

## Session Pattern: Sequential Extraction

When extracting multiple BRDs from a single source:

1. Generate all BRDs in order (BRD-03 → BRD-09)
2. Validate each immediately after generation before proceeding to next
3. Fix validation errors inline (tags, diagrams) before moving on
4. Final gate: run `sdd_next_action` to confirm all BRDs visible

Time efficiency: 7 BRDs generated and validated in one session using bulk Python generation with reusable structure.
