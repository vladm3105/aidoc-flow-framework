#!/usr/bin/env python3
"""
Generate persona prompts without running the actual LLM review.

Usage:
    cd /opt/data/docs_flow_framework/UCX
    PYTHONPATH=. python scripts/generate_prompts.py \
        --doc-path /opt/data/b-local/b-local-docs/docs/01_BRD/BRD-01_platform_architecture/ \
        --doc-type brd \
        --project-dir /opt/data/b-local/b-local-docs \
        --output-dir tmp/prompts \
        --personas architect auditor

Options:
    --doc-path: Path to document directory or file
    --doc-type: Document type (brd, prd, etc.)
    --project-dir: Project directory for project-specific prompts/skills
    --output-dir: Where to save generated prompts (default: tmp/prompts)
    --personas: Space-separated list of personas (default: all 11)
    --show-stats: Show token statistics for each prompt
"""

import argparse
import sys
from pathlib import Path

# Add UCX to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ucx.core.persona_prompts import build_persona_prompt


# Default personas for BRD review
DEFAULT_PERSONAS = [
    "architect",
    "auditor",
    "tech_lead",
    "strategist",
    "chaos_engineer",
    "operator",
    "integration_lead",
    "product_owner",
    "business_analyst",
    "fact_checker",
    "chairperson",
]


def estimate_tokens(text: str) -> int:
    """Rough estimate: ~4 chars per token."""
    return len(text) // 4


def load_document_content(doc_path: Path) -> str:
    """Load document content from path (file or directory)."""
    if doc_path.is_file():
        return doc_path.read_text(encoding="utf-8")

    # Directory: concatenate all markdown files
    content_parts = []
    for md_file in sorted(doc_path.glob("*.md")):
        # Skip review reports and memory files
        if any(x in md_file.name for x in [".UCR_", ".V_", ".ucx_review_session"]):
            continue
        content_parts.append(f"# File: {md_file.name}\n\n")
        content_parts.append(md_file.read_text(encoding="utf-8"))
        content_parts.append("\n\n---\n\n")

    return "".join(content_parts)


def main():
    parser = argparse.ArgumentParser(
        description="Generate persona prompts without running LLM review"
    )
    parser.add_argument(
        "--doc-path", "-d",
        type=Path,
        required=True,
        help="Path to document directory or file"
    )
    parser.add_argument(
        "--doc-type", "-t",
        type=str,
        default="brd",
        help="Document type (brd, prd, etc.)"
    )
    parser.add_argument(
        "--project-dir", "-p",
        type=Path,
        default=None,
        help="Project directory for project-specific prompts/skills"
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=Path,
        default=Path("tmp/prompts"),
        help="Output directory for generated prompts"
    )
    parser.add_argument(
        "--personas",
        nargs="+",
        default=None,
        help="Personas to generate (default: all)"
    )
    parser.add_argument(
        "--show-stats",
        action="store_true",
        help="Show token statistics"
    )
    parser.add_argument(
        "--use-context-engineering",
        action="store_true",
        default=True,
        help="Use context engineering (v1.13.0+)"
    )

    args = parser.parse_args()

    # Validate paths
    if not args.doc_path.exists():
        print(f"Error: Document path not found: {args.doc_path}")
        sys.exit(1)

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Load document content
    print(f"Loading document from: {args.doc_path}")
    shared_context = load_document_content(args.doc_path)
    print(f"  Document size: {len(shared_context):,} chars (~{estimate_tokens(shared_context):,} tokens)")

    # Determine personas
    personas = args.personas or DEFAULT_PERSONAS
    print(f"\nGenerating prompts for {len(personas)} personas...")

    # Generate prompts
    previous_responses = {}
    stats = []

    for i, persona in enumerate(personas, 1):
        print(f"\n[{i}/{len(personas)}] {persona}...")

        try:
            # Build prompt using context engineering
            prompt = build_persona_prompt(
                persona=persona,
                shared_context=shared_context,
                previous_responses=previous_responses if i > 1 else None,
                doc_type=args.doc_type,
                skill_dir=None,
                project_dir=args.project_dir,
                use_context_engineering=args.use_context_engineering,
            )

            # Save prompt
            output_file = args.output_dir / f"prompt_{persona}.txt"
            output_file.write_text(prompt, encoding="utf-8")

            # Calculate stats
            char_count = len(prompt)
            token_estimate = estimate_tokens(prompt)
            stats.append({
                "persona": persona,
                "chars": char_count,
                "tokens": token_estimate,
                "file": output_file,
            })

            print(f"  Saved: {output_file}")
            print(f"  Size: {char_count:,} chars (~{token_estimate:,} tokens)")

            # Simulate a response for next persona's "previous_responses"
            # (In real review, this would be the LLM response)
            previous_responses[persona] = f"[Simulated response for {persona}]"

        except Exception as e:
            print(f"  Error: {e}")
            import traceback
            traceback.print_exc()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    total_chars = sum(s["chars"] for s in stats)
    total_tokens = sum(s["tokens"] for s in stats)

    print(f"\nTotal prompts: {len(stats)}")
    print(f"Total size: {total_chars:,} chars (~{total_tokens:,} tokens)")
    print(f"Average per persona: {total_chars // len(stats):,} chars (~{total_tokens // len(stats):,} tokens)")

    if args.show_stats:
        print("\nPer-Persona Breakdown:")
        print("-" * 50)
        for s in stats:
            print(f"  {s['persona']:20} {s['chars']:>10,} chars ({s['tokens']:>8,} tokens)")

    print(f"\nPrompts saved to: {args.output_dir.absolute()}")
    print("\nTo inspect a prompt:")
    print(f"  less {args.output_dir}/prompt_architect.txt")


if __name__ == "__main__":
    main()
