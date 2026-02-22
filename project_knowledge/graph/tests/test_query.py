"""Unit tests for graph/query.py."""

from unittest.mock import MagicMock, patch

import pytest

from graph.query import (
    QUERIES,
    get_query,
    list_queries,
    run_preset_query,
)


class TestQueryCatalog:
    """Tests for query catalog functions."""

    def test_get_query_exists(self):
        query = get_query("biases_for_ticker")
        assert query is not None
        assert "Bias" in query
        assert "$symbol" in query

    def test_get_query_not_found(self):
        query = get_query("nonexistent_query")
        assert query is None

    def test_list_queries(self):
        queries = list_queries()
        assert isinstance(queries, list)
        assert len(queries) > 0
        assert "biases_for_ticker" in queries
        assert "sector_peers" in queries


class TestQueryContent:
    """Tests for query correctness."""

    def test_biases_for_ticker_query(self):
        query = QUERIES["biases_for_ticker"]
        assert "MATCH" in query
        assert "Bias" in query
        assert "Trade" in query
        assert "Ticker" in query
        assert "$symbol" in query

    def test_strategies_for_earnings_query(self):
        query = QUERIES["strategies_for_earnings"]
        assert "Strategy" in query
        assert "Catalyst" in query
        assert "earnings" in query

    def test_competitive_landscape_query(self):
        query = QUERIES["competitive_landscape"]
        assert "COMPETES_WITH" in query
        assert "Company" in query

    def test_risks_open_positions_query(self):
        query = QUERIES["risks_open_positions"]
        assert "Risk" in query
        assert "THREATENS" in query
        assert "status = 'open'" in query

    def test_learning_loop_query(self):
        query = QUERIES["learning_loop"]
        assert "Bias" in query
        assert "Trade" in query
        assert "Learning" in query
        assert "DERIVED_FROM" in query

    def test_supply_chain_query(self):
        query = QUERIES["supply_chain"]
        assert "SUPPLIES_TO" in query
        assert "CUSTOMER_OF" in query

    def test_node_counts_query(self):
        query = QUERIES["node_counts"]
        assert "labels(n)" in query
        assert "count(n)" in query

    def test_edge_counts_query(self):
        query = QUERIES["edge_counts"]
        assert "type(r)" in query
        assert "count(r)" in query


class TestRunPresetQuery:
    """Tests for preset query execution."""

    @patch("graph.layer.TradingGraph")
    def test_run_preset_query(self, mock_graph_class):
        mock_graph = MagicMock()
        mock_graph.run_cypher.return_value = [
            {"bias": "loss-aversion", "occurrences": 3},
        ]
        mock_graph_class.return_value.__enter__ = MagicMock(return_value=mock_graph)
        mock_graph_class.return_value.__exit__ = MagicMock(return_value=False)

        results = run_preset_query("biases_for_ticker", {"symbol": "NVDA"})

        assert len(results) == 1
        assert results[0]["bias"] == "loss-aversion"
        mock_graph.run_cypher.assert_called_once()

    def test_run_preset_query_invalid(self):
        with pytest.raises(ValueError, match="Unknown query"):
            run_preset_query("nonexistent_query")

    @patch("graph.layer.TradingGraph")
    def test_run_preset_query_no_params(self, mock_graph_class):
        mock_graph = MagicMock()
        mock_graph.run_cypher.return_value = [
            {"label": "Ticker", "count": 10},
        ]
        mock_graph_class.return_value.__enter__ = MagicMock(return_value=mock_graph)
        mock_graph_class.return_value.__exit__ = MagicMock(return_value=False)

        results = run_preset_query("node_counts")

        assert len(results) == 1
        mock_graph.run_cypher.assert_called_with(QUERIES["node_counts"], {})


class TestQueryParameters:
    """Tests for query parameterization."""

    def test_ticker_queries_use_symbol_param(self):
        ticker_queries = [
            "biases_for_ticker",
            "competitive_landscape",
            "supply_chain",
            "sector_peers",
            "pattern_by_ticker",
        ]
        for name in ticker_queries:
            query = QUERIES[name]
            assert "$symbol" in query, f"Query {name} should use $symbol parameter"

    def test_bias_queries_use_bias_param(self):
        query = QUERIES["learnings_for_bias"]
        assert "$bias_name" in query
