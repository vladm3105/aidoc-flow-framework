"""Unit tests for rag/tokens.py."""

from rag.tokens import estimate_tokens, split_by_tokens, truncate_to_tokens


class TestEstimateTokens:
    """Tests for token estimation."""

    def test_empty_string(self):
        assert estimate_tokens("") == 0

    def test_single_word(self):
        tokens = estimate_tokens("hello")
        assert tokens == 1

    def test_sentence(self):
        tokens = estimate_tokens("The quick brown fox jumps over the lazy dog.")
        assert 8 <= tokens <= 12  # Approximate range

    def test_longer_text(self):
        text = "This is a longer text that should have more tokens. " * 10
        tokens = estimate_tokens(text)
        assert tokens > 50


class TestTruncateToTokens:
    """Tests for token truncation."""

    def test_empty_string(self):
        assert truncate_to_tokens("", 100) == ""

    def test_short_text_unchanged(self):
        text = "Short text"
        result = truncate_to_tokens(text, 100)
        assert result == text

    def test_truncation(self):
        text = "This is a longer text that needs to be truncated because it exceeds the limit. " * 5
        result = truncate_to_tokens(text, 20)
        result_tokens = estimate_tokens(result)
        assert result_tokens <= 20


class TestSplitByTokens:
    """Tests for splitting text by tokens."""

    def test_empty_string(self):
        assert split_by_tokens("", 100) == []

    def test_short_text_single_chunk(self):
        text = "Short text"
        result = split_by_tokens(text, 100)
        assert len(result) == 1
        assert result[0] == text

    def test_splitting(self):
        text = "This is a longer text that should be split. " * 10
        result = split_by_tokens(text, 50, overlap=10)
        assert len(result) >= 2

    def test_overlap(self):
        text = "Word " * 100
        result = split_by_tokens(text, 50, overlap=10)
        # With overlap, chunks should share some content
        assert len(result) >= 2
