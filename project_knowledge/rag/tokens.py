"""Token estimation using tiktoken."""

import tiktoken

# Use cl100k_base (GPT-4/Claude tokenizer approximation)
_encoder = None


def _get_encoder():
    """Lazy-load encoder to avoid import overhead."""
    global _encoder
    if _encoder is None:
        _encoder = tiktoken.get_encoding("cl100k_base")
    return _encoder


def estimate_tokens(text: str) -> int:
    """
    Estimate token count for text.

    Uses cl100k_base encoding which is a good approximation
    for both GPT-4 and Claude tokenizers.

    Args:
        text: Input text

    Returns:
        Estimated token count
    """
    if not text:
        return 0
    encoder = _get_encoder()
    return len(encoder.encode(text))


def truncate_to_tokens(text: str, max_tokens: int) -> str:
    """
    Truncate text to fit within token limit.

    Args:
        text: Input text
        max_tokens: Maximum allowed tokens

    Returns:
        Truncated text (or original if within limit)
    """
    if not text:
        return ""

    encoder = _get_encoder()
    tokens = encoder.encode(text)

    if len(tokens) <= max_tokens:
        return text

    return encoder.decode(tokens[:max_tokens])


def split_by_tokens(text: str, max_tokens: int, overlap: int = 50) -> list[str]:
    """
    Split text into chunks with token limit and overlap.

    Args:
        text: Input text
        max_tokens: Maximum tokens per chunk
        overlap: Token overlap between chunks

    Returns:
        List of text chunks
    """
    if not text:
        return []

    encoder = _get_encoder()
    tokens = encoder.encode(text)

    if len(tokens) <= max_tokens:
        return [text]

    chunks = []
    start = 0

    while start < len(tokens):
        end = min(start + max_tokens, len(tokens))
        chunk_tokens = tokens[start:end]
        chunks.append(encoder.decode(chunk_tokens))

        # Move start with overlap
        start = end - overlap if end < len(tokens) else end

    return chunks
