# Documentation Repository Best Practices

Treating documentation with the same rigor as software ("Docs as Code") ensures high quality, maintainability, and trust.

## 1. Docs as Code Philosophy
-   **Version Control**: All specs and guides live in Git. History is preserved, and changes are traceable.
-   **Pull Requests**: No direct commits to `main`. All changes require peer review to ensure clarity and accuracy.
-   **Linters**: Use tools like `markdownlint` to enforce formatting consistency (headers, lists, code blocks).

## 2. Structural Integrity
-   **Immutable ADRs**: Architecture Decision Records (`docs/adr/`) should never be modified after approval. If a decision changes, create a new ADR that supersedes the old one.
-   **Single Source of Truth**: Avoid duplicating information. If one document defines the standard, other docs should link to it, not copy it.

## 3. Automated Validation (CI/CD for Docs)
Even without code, you should run checks:
-   **Link Checking**: Use `markdown-link-check` to prevent broken relative and absolute links.
-   **Spell Checking**: Use `cspell` to catch typos in technical terms.
-   **Prose Linting**: Tools like `vale` can enforce style guides (e.g., "Google Developer Documentation Style Guide").

## 4. Versioning & Releasing
-   **Tagging**: Tag the repo (e.g., `v1.0-specs`) when a major milestone is reached. Implementation teams can then build against a specific version of the specs.
-   **Changelog**: Maintain a `CHANGELOG.md` strictly for specification changes. Example: "Added field `{field_name}` to schema in v1.1".

## 5. Traceability
-   **Spec-to-Code Linking**: In implementation repos, comments should reference spec sections.
    ```python
    # See docs/core/{spec-file}.md Section 4.1
    def example_function(context): ...
    ```
-   **Issue Linking**: Every PR in this repo should link to a "Documentation" or "Planning" issue.

## 6. Publishing
-   **Static Site Generator**: Consider using MkDocs, Hugo, or Docusaurus to render these Markdown files into a searchable website.
-   **Mermaid Diagrams**: Keep diagrams as code (`mermaid`) inside markdown files for easy updates, rather than binary images.

## 7. Organizing Docs with Code Repos ("Twin Repos")

When specifications live in a separate repo from code, you need a strategy to keep them synced.

### Structure A: Side-by-Side (Recommended)
Keep repos independent but linked via **IDs** and **Process**.
-   **Docs Repo**: `{PROJECT_PREFIX}-specs` (The "Why" and "What")
-   **Code Repo**: `{PROJECT_PREFIX}-impl` (The "How")

### Traceability Links
1.  **In Requirements**: Give every spec a stable ID.
    -   *Spec*: `## [{PREFIX}-001] {Feature Name}`
2.  **In Code**: Reference the ID in docstrings.
    ```python
    def feature_function():
        """
        Implementation of [{PREFIX}-001]
        See: https://{GITHUB_HOST}/{GITHUB_ORG}/{REPO_NAME}/blob/main/docs/core/{spec}.md#{id}
        """
    ```

### Synchronization Workflow
1.  **Spec First**: Draft and approve changes in `Docs Repo` (PR #10).
2.  **Implementation**: Open PR in `Code Repo` referencing the Spec PR or merged ID.
    -   *PR Description*: "Implements Spec #10 from docs repo".
3.  **CI/CD Verification**: (Advanced) Use a script to scan code for Spec IDs and warn if code references a deprecated spec ID.

### Version Alignment
-   **Lock Step**: Release `v1.2.0` of specs, then build `v1.2.0` of code.
-   **Schema Sharing**: If you have machine-readable specs (OpenAPI, JSON Schema), publish them as a package (npm/pip) from the `Docs Repo` so the `Code Repo` can consume them as a dependency.
