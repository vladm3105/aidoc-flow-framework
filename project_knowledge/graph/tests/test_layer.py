"""Unit tests for graph/layer.py with mocked Neo4j."""

from unittest.mock import MagicMock, patch

import pytest

from graph.exceptions import GraphUnavailableError
from graph.layer import TradingGraph
from graph.models import GraphStats


class TestTradingGraphConnection:
    """Tests for Neo4j connection handling."""

    @patch("graph.layer.GraphDatabase")
    def test_context_manager_connects(self, mock_db):
        mock_driver = MagicMock()
        mock_db.driver.return_value = mock_driver

        with TradingGraph() as graph:
            mock_driver.verify_connectivity.assert_called_once()

    @patch("graph.layer.GraphDatabase")
    def test_context_manager_closes(self, mock_db):
        mock_driver = MagicMock()
        mock_db.driver.return_value = mock_driver

        with TradingGraph() as graph:
            pass

        mock_driver.close.assert_called_once()

    @patch("graph.layer.GraphDatabase")
    def test_connection_failure_raises(self, mock_db):
        from neo4j.exceptions import ServiceUnavailable

        mock_db.driver.side_effect = ServiceUnavailable("Connection refused")

        with pytest.raises(GraphUnavailableError):
            with TradingGraph() as graph:
                pass

    @patch("graph.layer.GraphDatabase")
    def test_health_check_success(self, mock_db):
        mock_driver = MagicMock()
        mock_db.driver.return_value = mock_driver

        with TradingGraph() as graph:
            assert graph.health_check() is True

    @patch("graph.layer.GraphDatabase")
    def test_health_check_failure(self, mock_db):
        mock_driver = MagicMock()
        mock_driver.verify_connectivity.side_effect = [None, Exception("Down")]
        mock_db.driver.return_value = mock_driver

        with TradingGraph() as graph:
            assert graph.health_check() is False


class TestMergeNode:
    """Tests for node creation/update operations."""

    @patch("graph.layer.GraphDatabase")
    def test_merge_node_returns_id(self, mock_db):
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_record = {"id": "4:abc:123"}

        mock_result.single.return_value = mock_record
        mock_session.run.return_value = mock_result
        mock_driver.session.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_driver.session.return_value.__exit__ = MagicMock(return_value=False)
        mock_db.driver.return_value = mock_driver

        with TradingGraph() as graph:
            node_id = graph.merge_node("Ticker", "symbol", {"symbol": "NVDA"})

        assert node_id == "4:abc:123"

    @patch("graph.layer.GraphDatabase")
    def test_merge_node_missing_key_returns_none(self, mock_db):
        mock_driver = MagicMock()
        mock_db.driver.return_value = mock_driver

        with TradingGraph() as graph:
            node_id = graph.merge_node("Ticker", "symbol", {"name": "NVIDIA"})

        assert node_id is None


class TestMergeRelation:
    """Tests for relationship operations."""

    @patch("graph.layer.GraphDatabase")
    def test_merge_relation_executes(self, mock_db):
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_driver.session.return_value.__exit__ = MagicMock(return_value=False)
        mock_db.driver.return_value = mock_driver

        with TradingGraph() as graph:
            graph.merge_relation(
                ("Company", "name", "NVIDIA"),
                "ISSUED",
                ("Ticker", "symbol", "NVDA"),
            )

        # Verify run was called with relationship query
        call_args = mock_session.run.call_args
        assert "MERGE (a)-[r:ISSUED]->(b)" in call_args[0][0]

    @patch("graph.layer.GraphDatabase")
    def test_merge_relation_with_props(self, mock_db):
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_driver.session.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_driver.session.return_value.__exit__ = MagicMock(return_value=False)
        mock_db.driver.return_value = mock_driver

        with TradingGraph() as graph:
            graph.merge_relation(
                ("Company", "name", "NVIDIA"),
                "ISSUED",
                ("Ticker", "symbol", "NVDA"),
                {"date": "2025-01-01"},
            )

        call_args = mock_session.run.call_args
        assert "SET r += $props" in call_args[0][0]


class TestQueries:
    """Tests for query operations."""

    @patch("graph.layer.GraphDatabase")
    def test_find_related(self, mock_db):
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.__iter__ = lambda self: iter(
            [
                {"labels": ["Company"], "props": {"name": "NVIDIA"}},
                {"labels": ["Sector"], "props": {"name": "Semiconductors"}},
            ]
        )
        mock_session.run.return_value = mock_result
        mock_driver.session.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_driver.session.return_value.__exit__ = MagicMock(return_value=False)
        mock_db.driver.return_value = mock_driver

        with TradingGraph() as graph:
            related = graph.find_related("NVDA", depth=2)

        assert len(related) == 2
        assert related[0]["labels"] == ["Company"]

    @patch("graph.layer.GraphDatabase")
    def test_get_sector_peers(self, mock_db):
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.__iter__ = lambda self: iter(
            [
                {"peer": "AMD", "company": "AMD Inc", "sector": "Semiconductors"},
                {"peer": "INTC", "company": "Intel", "sector": "Semiconductors"},
            ]
        )
        mock_session.run.return_value = mock_result
        mock_driver.session.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_driver.session.return_value.__exit__ = MagicMock(return_value=False)
        mock_db.driver.return_value = mock_driver

        with TradingGraph() as graph:
            peers = graph.get_sector_peers("NVDA")

        assert len(peers) == 2
        assert peers[0]["peer"] == "AMD"

    @patch("graph.layer.GraphDatabase")
    def test_get_risks(self, mock_db):
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.__iter__ = lambda self: iter(
            [
                {"risk": "Export controls", "description": "China restrictions"},
            ]
        )
        mock_session.run.return_value = mock_result
        mock_driver.session.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_driver.session.return_value.__exit__ = MagicMock(return_value=False)
        mock_db.driver.return_value = mock_driver

        with TradingGraph() as graph:
            risks = graph.get_risks("NVDA")

        assert len(risks) == 1
        assert risks[0]["risk"] == "Export controls"


class TestStats:
    """Tests for statistics operations."""

    @patch("graph.layer.GraphDatabase")
    def test_get_stats(self, mock_db):
        mock_driver = MagicMock()
        mock_session = MagicMock()

        # Mock node counts
        node_result = MagicMock()
        node_result.__iter__ = lambda self: iter(
            [
                {"label": "Ticker", "count": 10},
                {"label": "Company", "count": 8},
            ]
        )

        # Mock edge counts
        edge_result = MagicMock()
        edge_result.__iter__ = lambda self: iter(
            [
                {"relationship": "ISSUED", "count": 8},
                {"relationship": "ANALYZES", "count": 15},
            ]
        )

        # Mock last extraction
        extract_result = MagicMock()
        extract_result.single.return_value = {"last_extraction": "2025-01-01"}

        mock_session.run.side_effect = [node_result, edge_result, extract_result]
        mock_driver.session.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_driver.session.return_value.__exit__ = MagicMock(return_value=False)
        mock_db.driver.return_value = mock_driver

        with TradingGraph() as graph:
            stats = graph.get_stats()

        assert isinstance(stats, GraphStats)
        assert stats.total_nodes == 18
        assert stats.total_edges == 23
        assert stats.node_counts["Ticker"] == 10


class TestRunCypher:
    """Tests for raw Cypher execution."""

    @patch("graph.layer.GraphDatabase")
    def test_run_cypher(self, mock_db):
        mock_driver = MagicMock()
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.__iter__ = lambda self: iter(
            [
                {"symbol": "NVDA", "name": "NVIDIA"},
            ]
        )
        mock_session.run.return_value = mock_result
        mock_driver.session.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_driver.session.return_value.__exit__ = MagicMock(return_value=False)
        mock_db.driver.return_value = mock_driver

        with TradingGraph() as graph:
            results = graph.run_cypher(
                "MATCH (t:Ticker {symbol: $symbol}) RETURN t.symbol AS symbol, t.name AS name",
                {"symbol": "NVDA"},
            )

        assert len(results) == 1
        assert results[0]["symbol"] == "NVDA"
