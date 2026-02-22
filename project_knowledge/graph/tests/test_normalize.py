"""Unit tests for graph/normalize.py."""

from graph.normalize import (
    dedupe_entities,
    normalize_bias,
    normalize_entity,
    normalize_pattern,
    normalize_strategy,
    normalize_ticker,
    normalize_type,
    resolve_ticker,
    standardize_separators,
)


class TestNormalizeTicker:
    """Tests for ticker normalization."""

    def test_uppercase(self):
        assert normalize_ticker("nvda") == "NVDA"
        assert normalize_ticker("Nvda") == "NVDA"

    def test_alias_resolution(self):
        assert normalize_ticker("GOOG") == "GOOGL"
        assert normalize_ticker("FB") == "META"

    def test_strip_whitespace(self):
        assert normalize_ticker("  NVDA  ") == "NVDA"


class TestNormalizeBias:
    """Tests for bias name normalization."""

    def test_alias_resolution(self):
        assert normalize_bias("loss aversion") == "loss-aversion"
        assert normalize_bias("FOMO") == "fear-of-missing-out"
        assert normalize_bias("confirmation bias") == "confirmation-bias"

    def test_hyphenation(self):
        assert normalize_bias("some_new_bias") == "some-new-bias"


class TestNormalizePattern:
    """Tests for pattern name normalization."""

    def test_alias_resolution(self):
        assert normalize_pattern("gap up") == "gap-and-go"
        assert normalize_pattern("PEAD") == "earnings-drift"

    def test_hyphenation(self):
        assert normalize_pattern("mean reversion") == "mean-reversion"


class TestNormalizeStrategy:
    """Tests for strategy name normalization."""

    def test_alias_resolution(self):
        assert normalize_strategy("earnings play") == "earnings-momentum"
        assert normalize_strategy("breakout trade") == "breakout"


class TestResolveTicker:
    """Tests for company name to ticker resolution."""

    def test_exact_match(self):
        assert resolve_ticker("NVIDIA") == "NVDA"
        assert resolve_ticker("Apple") == "AAPL"
        assert resolve_ticker("Microsoft") == "MSFT"

    def test_case_insensitive(self):
        assert resolve_ticker("nvidia") == "NVDA"
        assert resolve_ticker("APPLE") == "AAPL"

    def test_not_found(self):
        assert resolve_ticker("Unknown Company") is None


class TestStandardizeSeparators:
    """Tests for separator standardization."""

    def test_underscores_to_hyphens(self):
        assert standardize_separators("loss_aversion") == "loss-aversion"

    def test_spaces_to_hyphens(self):
        assert standardize_separators("loss aversion") == "loss-aversion"


class TestNormalizeType:
    """Tests for entity type normalization."""

    def test_pascal_case(self):
        assert normalize_type("ticker") == "Ticker"
        assert normalize_type("earnings_event") == "EarningsEvent"
        assert normalize_type("COMPANY") == "Company"


class TestNormalizeEntity:
    """Tests for full entity normalization."""

    def test_ticker_entity(self):
        entity = {"type": "ticker", "value": "nvda", "confidence": 0.9}
        result = normalize_entity(entity)
        assert result["type"] == "Ticker"
        assert result["value"] == "NVDA"

    def test_bias_entity(self):
        entity = {"type": "bias", "value": "loss aversion", "confidence": 0.8}
        result = normalize_entity(entity)
        assert result["type"] == "Bias"
        assert result["value"] == "loss-aversion"

    def test_company_with_ticker_resolution(self):
        entity = {"type": "company", "value": "NVIDIA", "confidence": 0.85}
        result = normalize_entity(entity)
        assert result["type"] == "Company"
        assert result.get("resolved_ticker") == "NVDA"


class TestDedupeEntities:
    """Tests for entity deduplication."""

    def test_dedupe_by_type_and_value(self):
        entities = [
            {"type": "Ticker", "value": "NVDA", "confidence": 0.9},
            {"type": "Ticker", "value": "nvda", "confidence": 0.8},  # Duplicate, lower confidence
            {"type": "Company", "value": "NVIDIA", "confidence": 0.85},
        ]
        result = dedupe_entities(entities)
        assert len(result) == 2  # One ticker, one company

    def test_keep_highest_confidence(self):
        entities = [
            {"type": "Ticker", "value": "NVDA", "confidence": 0.7},
            {"type": "Ticker", "value": "NVDA", "confidence": 0.9},
        ]
        result = dedupe_entities(entities)
        assert len(result) == 1
        assert result[0]["confidence"] == 0.9
