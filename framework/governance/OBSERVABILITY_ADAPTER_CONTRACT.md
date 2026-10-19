# Observability Adapter Contract & Projection Standard

## Document Control

| Field | Value |
|---|---|
| Version | 1.0.0 |
| Status | Ratified |
| Last Updated | 2026-10-16 |
| Author | Framework Maintainer |
| Framework Version | 0.96.5 |
| Authority | Decision DEC-CHG-108 / GD-95, [`DOC_GOVERNANCE_CORE.md`](DOC_GOVERNANCE_CORE.md) Principle 2 |

---

## 1. Purpose & Architectural Context

The Observability Adapter (`sdd-render`) implements the **Read Plane** of the framework's Dual-Plane CQRS Architecture. 

While autonomous AI agents operate on the **Write Plane** (reading, mutating, and reviewing the Native SDD Graph), human stakeholders, auditors, and engineering leaders require high-level, human-friendly representations (spec sheets, visual architecture maps, and pull request summaries).

### 1.1 Non-Authoritative Invariant (Principle 2)
Per [DOC_GOVERNANCE_CORE.md Principle 2](DOC_GOVERNANCE_CORE.md#L16):
> *"Markdown is optional and descriptive: a rendering of the underlying data... generated, not authored — hand-editing it is destroyed by the next generation run, and a stale rendering is a drift defect."*

The Observability Adapter is strictly **non-authoritative and deterministic**:
- The Graph (`.graph.yaml`) is the Single Source of Truth.
- All human documents are compiled projections.
- Hand-editing rendered markdown is prohibited and blocked by CI.

---

## 2. Engine Neutrality & Pure-Python Mandate (Decision D-0013)

To ensure zero-friction portability across Linux, macOS, Windows, and air-gapped CI environments:
1. **Zero External Browser/Node.js Dependencies**: The adapter must NOT depend on Node.js, `@mermaid-js/mermaid-cli`, Puppeteer, or headless Chromium.
2. **Pure Text Emission**:
   - `sdd-render diagram` emits **pure Mermaid text** (`.mmd` files or fenced markdown blocks).
   - Visual SVG/PNG rasterization is delegated to GitHub's native Mermaid markdown renderer or optional static site generators (VitePress/MkDocs).
3. **Pure-Python Standard Library**: The adapter implementation lives in `sdd_doc_lint/observability_adapter.py` and requires only Python standard libraries and `pyyaml`.

---

## 3. Projection Subcommands & Formats

The adapter CLI (`python3 -m sdd_doc_lint --render-*`) provides four canonical projection targets:

### 3.1 Spec Sheet Projection (`--render-spec`)
Compiles a graph slice into structured Markdown replicating traditional SDD document sections:
- Groups `business_objective` nodes into Executive Summary.
- Groups `formal_requirement` nodes into Requirements Specification.
- Formats `acceptance_scenario` nodes into Given/When/Then scenario tables.
- Formats `architectural_decision` nodes into Context/Decision/Consequences summaries.
- Auto-dispatches to `render_module_spec` when processing a Tier 2 module graph slice (`MODULE-NN_[slug].graph.yaml`), generating a canonical spec sheet matching `MODULE-TEMPLATE.md` with line 1 YAML frontmatter.

Command:
```bash
python3 -m sdd_doc_lint --render-spec docs/sdd/graph/initiatives/INIT-01.graph.yaml --out docs/specs/INIT-01.md
python3 -m sdd_doc_lint --render-spec docs/modules/MODULE-01_auth/MODULE-01_auth.graph.yaml --out docs/modules/MODULE-01_auth/MODULE-01_auth.md
```

### 3.2 Architectural Diagram Projection (`--render-diagram`)
Generates native Mermaid diagrams derived from node properties and relational edges:
- **`--type c4-context`**: Emits `graph TB` from `seed_intent` and `system_container` boundaries.
- **`--type c4-container`**: Emits subsystem container maps from `system_container` and `component_contract` nodes.
- **`--type dfd`**: Emits Data Flow Diagrams with trust boundary subgraphs and classified data paths.
- **`--type sequence`**: Emits inter-module interaction flows and failure recovery branches from `system_container.choreography`.
- **`--type lineage`**: Emits the end-to-end Traceability DAG (`Requirement` $\longrightarrow$ `Scenario` $\longrightarrow$ `Test` $\longrightarrow$ `Code`).

Command:
```bash
python3 -m sdd_doc_lint --render-diagram docs/sdd/graph/ --type c4-container --out docs/specs/diagrams/c4_containers.mmd
python3 -m sdd_doc_lint --render-diagram docs/modules/MODULE-01_auth/MODULE-01_auth.graph.yaml --type sequence --out docs/modules/MODULE-01_auth/sequence.mmd
```

### 3.3 Verification & Traceability Matrix (`--render-matrix`)
Emits an exhaustive compliance verification table proving 100% oracle realization:

| Requirement ID | Statement | BDD Scenario Oracle | Test Fixture Proof | Implementation Task | Status |
|---|---|---|---|---|---|
| `EARS.01.01.a8b9` | The system shall... | `BDD.01.01.c3d4` | `tests/unit/test_auth.py` | `TASK.01.01.e5f6` | ✅ Verified |

Command:
```bash
python3 -m sdd_doc_lint --render-matrix docs/sdd/graph/ --out docs/specs/TRACEABILITY_MATRIX.md
```

### 3.4 CI Pull Request Impact Summary (`--render-pr-impact`)
Compares the PR branch graph ($G_{head}$) against the base branch graph ($G_{base}$):
- Evaluates added, modified, and deleted nodes.
- Computes the exact downstream blast radius ($\text{nx.descendants}$).
- Materializes $G_{base}$ in-memory via `git show origin/main:<path>` streams without requiring a secondary physical checkout.
- Emits a concise GitHub markdown comment block with an embedded Mermaid delta visual.

Command:
```bash
python3 -m sdd_doc_lint --render-pr-impact --base origin/main --head HEAD
```

---

## 4. The Read-Only Invariant & Cryptographic Banner

Every file emitted by `sdd-render` prepends a non-negotiable generated banner:

```markdown
<!-- ===================================================================== -->
<!-- GENERATED BY SDD-RENDER. DO NOT EDIT DIRECTLY. MUTATE THE GRAPH SOURCE. -->
<!-- Source Graph SHA: a1b2c3d4e5f6... | Engine: sdd-render v1.0.0           -->
<!-- ===================================================================== -->
```

### 4.1 CI Mutation Guard (`GATE-DOC-READONLY`)
The CI pipeline checks all generated spec files:
1. Recomputes $\text{SHA-256}(\text{source graph slice})$.
2. If the commit modifies a rendered markdown file without modifying the corresponding graph slice, or if the rendered output does not match `sdd-render(graph)`, CI fails immediately with `ERR-STALE-PROJECTION`.

### 4.2 Frontmatter Sequencing Invariant
For document specifications requiring YAML frontmatter (such as `MODULE-NN_slug.md`), the opening fence `---` must appear at line 1, column 1 to guarantee standard frontmatter parser compatibility across all tools and test harnesses. The SDD-RENDER generated notice is embedded as YAML comment lines within the frontmatter block, and cryptographic metadata is recorded within the `document_control` mapping.

---

## 5. Workstation Integration (`.aidoc/Taskfile.yml`)

Developers and AI agents invoke the adapter through standardized Taskfile commands:

```bash
# Render all project specs into docs/specs/
task sdd:render

# Check graph verification and delta impact
task sdd:delta
```
