"""Unit tests for rag/flatten.py."""

from rag.flatten import (
    flatten_dict_list,
    flatten_list,
    humanize_key,
    section_to_text,
    yaml_to_text,
)


class TestHumanizeKey:
    """Tests for YAML key humanization."""

    def test_simple_key(self):
        assert humanize_key("ticker") == "Ticker"

    def test_underscored_key(self):
        assert humanize_key("customer_demand") == "Customer Demand"

    def test_abbreviations(self):
        assert humanize_key("yoy_pct") == "YoY %"
        assert humanize_key("eps") == "EPS"

    def test_numbered_suffix(self):
        result = humanize_key("revenue_trend_8q")
        assert "8Q" in result or "(8Q)" in result

    def test_phase_prefix(self):
        assert "Phase 2" in humanize_key("phase2_fundamentals")


class TestFlattenList:
    """Tests for list flattening."""

    def test_empty_list(self):
        assert flatten_list([]) == ""

    def test_short_list(self):
        result = flatten_list(["a", "b", "c"])
        assert result == "a, b, c"

    def test_long_list(self):
        result = flatten_list(["a", "b", "c", "d", "e"])
        assert result.startswith("- ")

    def test_with_formatter(self):
        result = flatten_list([1, 2, 3], item_formatter=lambda x: f"item_{x}")
        assert "item_1" in result


class TestFlattenDictList:
    """Tests for dict list flattening."""

    def test_empty_list(self):
        assert flatten_dict_list([]) == ""

    def test_single_dict(self):
        result = flatten_dict_list([{"name": "Test", "value": "123"}])
        assert "Test" in result
        assert "123" in result

    def test_multiple_dicts(self):
        dicts = [
            {"name": "First", "value": "1"},
            {"name": "Second", "value": "2"},
        ]
        result = flatten_dict_list(dicts)
        assert "First" in result
        assert "Second" in result


class TestYamlToText:
    """Tests for YAML-to-text conversion."""

    def test_string_value(self):
        result = yaml_to_text("ticker", "NVDA")
        assert "Ticker: NVDA" in result

    def test_number_value(self):
        result = yaml_to_text("price", 145.50)
        assert "Price" in result
        # Formatted as currency: $146 (rounded)
        assert "$" in result

    def test_list_value(self):
        result = yaml_to_text("tags", ["tech", "ai", "growth"])
        assert "Tags" in result
        assert "tech" in result

    def test_dict_value(self):
        result = yaml_to_text("customer", {"name": "Microsoft", "spend": "50B"})
        assert "Customer" in result
        assert "Microsoft" in result

    def test_null_value(self):
        result = yaml_to_text("empty", None)
        assert result == ""


class TestSectionToText:
    """Tests for section conversion."""

    def test_dict_section(self):
        section = {"key1": "value1", "key2": "value2"}
        result = section_to_text(section, "Test Section")
        assert "value1" in result
        assert "value2" in result

    def test_list_section(self):
        section = ["item1", "item2", "item3"]
        result = section_to_text(section, "Test Section")
        assert "item1" in result

    def test_string_section(self):
        section = "Simple text content"
        result = section_to_text(section, "Test Section")
        assert result == "Simple text content"

    def test_none_section(self):
        result = section_to_text(None, "Test Section")
        assert result == ""
