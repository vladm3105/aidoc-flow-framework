"""Query expansion for improved retrieval recall.

Generates semantic variations of queries using LLM to broaden search coverage.
Inspired by Haystack's QueryExpander component.

Example:
    Original: "NVDA competitive position"
    Variations:
    - "NVIDIA market share vs competitors"
    - "NVDA AMD Intel competitive landscape"
    - "NVIDIA data center GPU dominance"
"""

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path

import yaml

log = logging.getLogger(__name__)


@dataclass
class ExpandedQuery:
    """Result of query expansion."""

    original: str
    variations: list[str]
    all_queries: list[str]  # original + variations (if include_original=True)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "original": self.original,
            "variations": self.variations,
            "all_queries": self.all_queries,
        }


class QueryExpander:
    """
    Expand queries with semantic variations using LLM.

    Uses a small, fast model (gpt-4o-mini) to generate alternative
    phrasings that preserve the original intent but use different keywords.
    """

    EXPANSION_PROMPT = """Generate {n} semantically similar variations of this financial search query.

Requirements:
- Preserve the same search intent
- Use different keywords and phrasings
- Include relevant financial terminology
- Maintain the same language as the original
- Each variation should find different but related documents

Query: {query}

Return ONLY a JSON object with this exact structure (no markdown, no explanation):
{{"queries": ["variation 1", "variation 2", "variation 3"]}}"""

    def __init__(
        self,
        n_expansions: int = 3,
        include_original: bool = True,
        provider: str = "openai",
        model: str | None = None,
    ):
        """
        Initialize query expander.

        Args:
            n_expansions: Number of variations to generate
            include_original: Include original query in output
            provider: LLM provider ("openai", "openrouter")
            model: Model name (default: gpt-4o-mini)
        """
        self.n_expansions = n_expansions
        self.include_original = include_original
        self.provider = provider
        self.model = model or self._get_default_model()
        self._client = None

    def _get_default_model(self) -> str:
        """Get default model from config or use fallback."""
        try:
            config_path = Path(__file__).parent / "config.yaml"
            if config_path.exists():
                with open(config_path) as f:
                    config = yaml.safe_load(f) or {}
                return config.get("query_expansion", {}).get("model", "gpt-4o-mini")
        except Exception:
            pass
        return "gpt-4o-mini"

    @property
    def client(self):
        """Lazy-load LLM client."""
        if self._client is None:
            if self.provider == "openai":
                try:
                    from openai import OpenAI

                    api_key = os.getenv("OPENAI_API_KEY")
                    if not api_key:
                        log.warning("OPENAI_API_KEY not set, query expansion disabled")
                        return None
                    self._client = OpenAI(api_key=api_key)
                except ImportError:
                    log.warning("openai package not installed")
                    return None
            elif self.provider == "openrouter":
                try:
                    from openai import OpenAI

                    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENROUTER_API_KEY")
                    if not api_key:
                        log.warning("LLM_API_KEY not set, query expansion disabled")
                        return None
                    self._client = OpenAI(
                        api_key=api_key,
                        base_url="https://openrouter.ai/api/v1",
                    )
                except ImportError:
                    log.warning("openai package not installed")
                    return None
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        return self._client

    def expand(self, query: str) -> ExpandedQuery:
        """
        Expand query with semantic variations.

        Args:
            query: Original search query

        Returns:
            ExpandedQuery with original and variations
        """
        # Return original only if client unavailable
        if self.client is None:
            return ExpandedQuery(
                original=query,
                variations=[],
                all_queries=[query],
            )

        try:
            prompt = self.EXPANSION_PROMPT.format(n=self.n_expansions, query=query)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300,
            )

            content = response.choices[0].message.content.strip()

            # Parse JSON response
            # Handle potential markdown code blocks
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]

            data = json.loads(content)
            variations = data.get("queries", [])[:self.n_expansions]

            # Build all_queries list
            all_queries = []
            if self.include_original:
                all_queries.append(query)
            all_queries.extend(variations)

            log.debug(f"Expanded '{query}' into {len(variations)} variations")

            return ExpandedQuery(
                original=query,
                variations=variations,
                all_queries=all_queries,
            )

        except json.JSONDecodeError as e:
            log.warning(f"Failed to parse expansion response: {e}")
            return ExpandedQuery(
                original=query,
                variations=[],
                all_queries=[query],
            )
        except Exception as e:
            log.warning(f"Query expansion failed: {e}")
            return ExpandedQuery(
                original=query,
                variations=[],
                all_queries=[query],
            )


# =============================================================================
# Singleton Management
# =============================================================================

_expander: QueryExpander | None = None


def get_expander(n_expansions: int | None = None) -> QueryExpander:
    """
    Get singleton expander instance.

    Args:
        n_expansions: Override number of expansions

    Returns:
        QueryExpander instance
    """
    global _expander

    if _expander is None:
        # Load config
        config_n = 3
        try:
            config_path = Path(__file__).parent / "config.yaml"
            if config_path.exists():
                with open(config_path) as f:
                    config = yaml.safe_load(f) or {}
                config_n = config.get("query_expansion", {}).get("n_expansions", 3)
        except Exception:
            pass

        _expander = QueryExpander(n_expansions=config_n)

    # Allow runtime override of n_expansions
    if n_expansions is not None:
        _expander.n_expansions = n_expansions

    return _expander


def expand_query(query: str, n: int = 3) -> ExpandedQuery:
    """
    Convenience function to expand a query.

    Args:
        query: Original search query
        n: Number of variations to generate

    Returns:
        ExpandedQuery with original and variations
    """
    expander = get_expander(n_expansions=n)
    return expander.expand(query)


def reset_expander() -> None:
    """Reset singleton (for testing)."""
    global _expander
    _expander = None
