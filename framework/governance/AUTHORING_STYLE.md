# Authoring Style — token-efficient SDD documents

Authority for **how** SDD documents are written. Templates define structure;
this defines voice, density, and form. Apply to every layer (BRD/PRD/EARS/BDD/
ADR/SPEC/TDD/IPLAN) and to CHG records. Audit skills enforce it as part of the
structural checklist.

**Rationale.** A large corpus is read into LLM context every cycle (authoring,
audit, review, traceability). Every superfluous word multiplies token cost
across all downstream operations. Documents must be **precise and complete**,
not **detailed and exhaustive** — completeness comes from covering every
required template section, not from prose volume.

## Eliminate

Banned in document prose. Audit-blocking when present in a published artifact.

| Class | Examples |
|-------|----------|
| Benefit statements | "This will help you…", "Users benefit from…" |
| Efficiency claims | "Faster than…", "More efficient than…", "Improves performance" (without a measurable comparison) |
| Ease-of-use claims | "Simply…", "Just…", "Easily…", "Straightforwardly…" |
| Future-oriented promises | "You'll be able to…", "Soon supports…", "Will allow…" |
| Superlatives | best, optimal, superior, amazing, powerful, robust, seamless, comprehensive (when used as praise), cutting-edge, state-of-the-art |
| Filler phrases | "in order to" → "to"; "the fact that" → omit; "it should be noted" → omit; "please note" → omit; "as a matter of fact" → omit |
| Verbose introductions | restating section purpose before the content; paragraph-long preambles before the first concrete sentence |
| Redundant restatement | repeating upstream content instead of referencing it via `@brd`/`@prd`/etc. |

## Enforce

| Form | Rule |
|------|------|
| Procedures | Imperative verbs ("Open X", "Set Y") — never "you should open X" |
| Error handling | Conditional statements ("If X, then Y") — never "you might want to consider…" |
| Parameter specifications | Tabular form — column per attribute (name, type, default, constraint) |
| Configuration options | Bullet list — one bullet per option |
| Element/function descriptions | One sentence maximum |
| Rationale | ≤3 sentences per decision/topic |
| Quantitative claims | Use `@threshold:` keys; never magic numbers in prose |
| Data types | Precise (`int`, `string`, `ISO-8601 date`) — never "a value" / "an identifier" |
| Scope statements | Explicit in-scope and out-of-scope bullets; no "etc." or "and so on" |
| Complexity ratings | 1–5 scale where applicable (1 = minimal, 5 = architectural change) |
| Impact metrics | Measurable where possible (latency p95, error rate, cost delta) |

## Form preferences (descending order)

1. Tables — for any homogeneous list (≥3 items with the same attributes).
2. Bullets — for short heterogeneous lists.
3. Diagrams (`@diagram:` per `DIAGRAM_STANDARDS.md`) — for relationships.
4. Prose — only when none of the above fits.

When in doubt, **collapse paragraphs into a table or bullet list** and check
that no information is lost. If information is lost, prose is justified;
otherwise it is wasted tokens.

## Size targets

These are **defaults**; a template may relax a target via per-section
`_guidance`. They are not hard caps — but exceeding by ≥50% is an audit
finding ("style-bloat").

| Element | Target |
|---------|--------|
| Section body | ≤ 200 words, or one table, or one diagram + caption |
| Element description (FR/AC/decision/etc.) | 1 sentence |
| Rationale (per decision/risk/constraint) | ≤ 3 sentences |
| Glossary entry | ≤ 1 sentence + ≤ 1 cross-reference |
| Inline code block | ≤ 50 lines; reference an external file otherwise |
| Whole document (markdown body, no front-matter) | ≤ 3 000 words for BRD/PRD; ≤ 1 500 for EARS/BDD/ADR/SPEC/TDD/IPLAN/CHG |

## Abbreviations and references

- Use canonical abbreviations where defined (HTTP status codes, RFC numbers,
  ISO standards).
- Reference upstream elements by element ID (`@brd: BRD.NN.SS.xxxx`) — do not
  restate their content.
- Reference governance via filename (`see ID_NAMING_STANDARDS.md §…`) — do not
  inline quote.

## Audit hook

Audit skills (`doc-<layer>-audit`) include this rule in the Structural
Checklist:

- [ ] Authoring style complies with `AUTHORING_STYLE.md` — no banned phrases,
      form preferences observed, size targets met within +50%.

Violations are **Tier 2 — advisory** by default, **Tier 1 — blocking** when
they push the document above the size-target threshold or when ≥3 banned
phrases appear in one section.

## What this is NOT

- **Not a content reviewer.** Substantive review (correctness, traceability,
  completeness) stays with the per-layer audit content checks.
- **Not a hard cap.** Templates may explicitly grant a section more room via
  `_guidance` or `_size_target` keys (template is the canonical authority).
- **Not retroactive.** Existing approved artifacts are not automatically
  invalidated; they update on next CHG edit.
