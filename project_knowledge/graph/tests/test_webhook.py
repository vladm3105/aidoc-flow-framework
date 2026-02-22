"""Tests for FastAPI webhook endpoints."""

from unittest.mock import MagicMock, patch

from graph.exceptions import ExtractionError, GraphUnavailableError
from graph.models import ExtractionResult, GraphStats


class TestExtractDocumentEndpoint:
    """Tests for POST /api/graph/extract."""

    def test_extract_document_success(self, test_client, mock_extract_document):
        """Extract document returns 200 on success."""
        mock_result = MagicMock(spec=ExtractionResult)
        mock_result.to_dict.return_value = {
            "entities": [{"type": "Ticker", "name": "NVDA"}],
            "relations": [],
            "doc_id": "test_doc",
        }
        mock_extract_document.return_value = mock_result

        response = test_client.post(
            "/api/graph/extract",
            json={"file_path": "/path/to/doc.yaml", "extractor": "ollama", "commit": True},
        )

        assert response.status_code == 200
        assert response.json()["doc_id"] == "test_doc"
        mock_extract_document.assert_called_once_with(
            file_path="/path/to/doc.yaml",
            extractor="ollama",
            commit=True,
        )

    def test_extract_document_extraction_error(self, test_client, mock_extract_document):
        """Extract document returns 400 on ExtractionError."""
        mock_extract_document.side_effect = ExtractionError("Invalid YAML")

        response = test_client.post(
            "/api/graph/extract",
            json={"file_path": "/invalid.yaml"},
        )

        assert response.status_code == 400
        assert "Invalid YAML" in response.json()["detail"]

    def test_extract_document_graph_unavailable(self, test_client, mock_extract_document):
        """Extract document returns 503 when graph unavailable."""
        mock_extract_document.side_effect = GraphUnavailableError("Neo4j down")

        response = test_client.post(
            "/api/graph/extract",
            json={"file_path": "/path/to/doc.yaml"},
        )

        assert response.status_code == 503
        assert "Neo4j down" in response.json()["detail"]


class TestExtractTextEndpoint:
    """Tests for POST /api/graph/extract-text."""

    def test_extract_text_success(self, test_client, mock_extract_text):
        """Extract text returns 200 on success."""
        mock_result = MagicMock(spec=ExtractionResult)
        mock_result.to_dict.return_value = {
            "entities": [{"type": "Risk", "name": "Interest rate risk"}],
            "relations": [],
            "doc_id": "text_doc",
        }
        mock_extract_text.return_value = mock_result

        response = test_client.post(
            "/api/graph/extract-text",
            json={
                "text": "NVDA has interest rate risk",
                "doc_type": "research",
                "doc_id": "text_doc",
            },
        )

        assert response.status_code == 200
        assert response.json()["doc_id"] == "text_doc"

    def test_extract_text_extraction_error(self, test_client, mock_extract_text):
        """Extract text returns 400 on ExtractionError."""
        mock_extract_text.side_effect = ExtractionError("Parse failed")

        response = test_client.post(
            "/api/graph/extract-text",
            json={"text": "bad", "doc_type": "research", "doc_id": "x"},
        )

        assert response.status_code == 400


class TestQueryEndpoint:
    """Tests for POST /api/graph/query."""

    def test_query_success(self, test_client, mock_trading_graph):
        """Query returns 200 with results."""
        mock_trading_graph.run_cypher.return_value = [{"n": {"name": "NVDA"}}]

        response = test_client.post(
            "/api/graph/query",
            json={"cypher": "MATCH (n:Ticker) RETURN n LIMIT 1"},
        )

        assert response.status_code == 200
        assert "results" in response.json()

    def test_query_graph_unavailable(self, test_client):
        """Query returns 503 when graph unavailable."""
        with patch("graph.webhook.TradingGraph") as mock_class:
            mock_class.return_value.__enter__ = MagicMock(
                side_effect=GraphUnavailableError("Connection refused")
            )

            response = test_client.post(
                "/api/graph/query",
                json={"cypher": "MATCH (n) RETURN n"},
            )

            assert response.status_code == 503

    def test_query_invalid_cypher(self, test_client, mock_trading_graph):
        """Query returns 400 on invalid Cypher."""
        mock_trading_graph.run_cypher.side_effect = Exception("Syntax error")

        response = test_client.post(
            "/api/graph/query",
            json={"cypher": "INVALID QUERY"},
        )

        assert response.status_code == 400


class TestStatusEndpoint:
    """Tests for GET /api/graph/status."""

    def test_status_success(self, test_client, mock_trading_graph):
        """Status returns 200 with stats."""
        mock_stats = MagicMock(spec=GraphStats)
        mock_stats.to_dict.return_value = {
            "total_nodes": 100,
            "total_edges": 50,
            "node_counts": {"Ticker": 10, "Risk": 20},
        }
        mock_trading_graph.get_stats.return_value = mock_stats

        response = test_client.get("/api/graph/status")

        assert response.status_code == 200
        assert response.json()["total_nodes"] == 100

    def test_status_graph_unavailable(self, test_client):
        """Status returns 503 when graph unavailable."""
        with patch("graph.webhook.TradingGraph") as mock_class:
            mock_class.return_value.__enter__ = MagicMock(
                side_effect=GraphUnavailableError("Neo4j timeout")
            )

            response = test_client.get("/api/graph/status")

            assert response.status_code == 503


class TestTickerContextEndpoint:
    """Tests for GET /api/graph/ticker/{symbol}."""

    def test_ticker_context_success(self, test_client, mock_trading_graph):
        """Ticker context returns 200."""
        mock_trading_graph.get_ticker_context.return_value = {
            "ticker": "NVDA",
            "peers": ["AMD", "INTC"],
            "risks": ["Supply chain"],
        }

        response = test_client.get("/api/graph/ticker/nvda")

        assert response.status_code == 200
        mock_trading_graph.get_ticker_context.assert_called_once_with("NVDA")

    def test_ticker_context_uppercase(self, test_client, mock_trading_graph):
        """Ticker symbol is uppercased."""
        mock_trading_graph.get_ticker_context.return_value = {"ticker": "AAPL"}

        response = test_client.get("/api/graph/ticker/aapl")

        mock_trading_graph.get_ticker_context.assert_called_with("AAPL")


class TestPeersEndpoint:
    """Tests for GET /api/graph/ticker/{symbol}/peers."""

    def test_peers_success(self, test_client, mock_trading_graph):
        """Peers returns 200 with list."""
        mock_trading_graph.get_sector_peers.return_value = ["AMD", "INTC", "QCOM"]

        response = test_client.get("/api/graph/ticker/NVDA/peers")

        assert response.status_code == 200
        assert response.json()["peers"] == ["AMD", "INTC", "QCOM"]


class TestRisksEndpoint:
    """Tests for GET /api/graph/ticker/{symbol}/risks."""

    def test_risks_success(self, test_client, mock_trading_graph):
        """Risks returns 200 with list."""
        mock_trading_graph.get_risks.return_value = ["Supply chain", "Regulatory"]

        response = test_client.get("/api/graph/ticker/NVDA/risks")

        assert response.status_code == 200
        assert "Supply chain" in response.json()["risks"]


class TestCompetitorsEndpoint:
    """Tests for GET /api/graph/ticker/{symbol}/competitors."""

    def test_competitors_success(self, test_client, mock_trading_graph):
        """Competitors returns 200 with list."""
        mock_trading_graph.get_competitors.return_value = ["AMD", "INTC"]

        response = test_client.get("/api/graph/ticker/NVDA/competitors")

        assert response.status_code == 200
        assert response.json()["competitors"] == ["AMD", "INTC"]


class TestBiasesEndpoint:
    """Tests for GET /api/graph/biases."""

    def test_biases_all(self, test_client, mock_trading_graph):
        """Biases returns all biases without filter."""
        mock_trading_graph.get_bias_history.return_value = [
            {"name": "confirmation-bias", "count": 5},
            {"name": "loss-aversion", "count": 3},
        ]

        response = test_client.get("/api/graph/biases")

        assert response.status_code == 200
        mock_trading_graph.get_bias_history.assert_called_once_with(None)

    def test_biases_filtered(self, test_client, mock_trading_graph):
        """Biases returns filtered by name."""
        mock_trading_graph.get_bias_history.return_value = [
            {"name": "confirmation-bias", "count": 5}
        ]

        response = test_client.get("/api/graph/biases?name=confirmation-bias")

        mock_trading_graph.get_bias_history.assert_called_once_with("confirmation-bias")


class TestStrategiesEndpoint:
    """Tests for GET /api/graph/strategies."""

    def test_strategies_all(self, test_client, mock_trading_graph):
        """Strategies returns all without filter."""
        mock_trading_graph.get_strategy_performance.return_value = [
            {"name": "momentum", "win_rate": 0.65}
        ]

        response = test_client.get("/api/graph/strategies")

        assert response.status_code == 200
        mock_trading_graph.get_strategy_performance.assert_called_once_with(None)

    def test_strategies_filtered(self, test_client, mock_trading_graph):
        """Strategies returns filtered by name."""
        mock_trading_graph.get_strategy_performance.return_value = []

        response = test_client.get("/api/graph/strategies?name=momentum")

        mock_trading_graph.get_strategy_performance.assert_called_once_with("momentum")


class TestHealthEndpoint:
    """Tests for GET /api/graph/health."""

    def test_health_healthy(self, test_client, mock_trading_graph):
        """Health returns healthy status."""
        mock_trading_graph.health_check.return_value = True

        response = test_client.get("/api/graph/health")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_health_unhealthy(self, test_client, mock_trading_graph):
        """Health returns unhealthy when check fails."""
        mock_trading_graph.health_check.return_value = False

        response = test_client.get("/api/graph/health")

        assert response.status_code == 200
        assert response.json()["status"] == "unhealthy"

    def test_health_exception(self, test_client):
        """Health returns unhealthy on exception."""
        with patch("graph.webhook.TradingGraph") as mock_class:
            mock_class.return_value.__enter__ = MagicMock(
                side_effect=Exception("Connection failed")
            )

            response = test_client.get("/api/graph/health")

            assert response.status_code == 200
            assert response.json()["status"] == "unhealthy"


class TestReadinessEndpoint:
    """Tests for GET /api/graph/ready."""

    def test_ready_success(self, test_client, mock_trading_graph):
        """Ready returns 200 when graph is ready."""
        mock_stats = MagicMock(spec=GraphStats)
        mock_stats.total_nodes = 100
        mock_stats.total_edges = 50
        mock_trading_graph.get_stats.return_value = mock_stats

        response = test_client.get("/api/graph/ready")

        assert response.status_code == 200
        assert response.json()["status"] == "ready"
        assert response.json()["node_count"] == 100

    def test_ready_not_ready(self, test_client):
        """Ready returns 503 when graph not ready."""
        with patch("graph.webhook.TradingGraph") as mock_class:
            mock_class.return_value.__enter__ = MagicMock(
                side_effect=Exception("Schema not initialized")
            )

            response = test_client.get("/api/graph/ready")

            assert response.status_code == 503
