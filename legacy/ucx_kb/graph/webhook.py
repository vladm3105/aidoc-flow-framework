"""FastAPI HTTP endpoints for graph operations."""

import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .exceptions import ExtractionError, GraphUnavailableError
from .extract import extract_document, extract_text
from .layer import TradingGraph

log = logging.getLogger(__name__)

app = FastAPI(title="Trading Graph API", version="1.0.0")


# --- Request Models ---


class ExtractRequest(BaseModel):
    file_path: str
    extractor: str = "ollama"
    commit: bool = True


class ExtractTextRequest(BaseModel):
    text: str
    doc_type: str
    doc_id: str
    source_url: str | None = None
    extractor: str = "ollama"


class QueryRequest(BaseModel):
    cypher: str
    params: dict = {}


# --- Endpoints ---


@app.post("/api/graph/extract")
async def api_extract_document(req: ExtractRequest) -> dict:
    """Extract entities from a YAML file."""
    try:
        result = extract_document(
            file_path=req.file_path,
            extractor=req.extractor,
            commit=req.commit,
        )
        return result.to_dict()
    except ExtractionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except GraphUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.post("/api/graph/extract-text")
async def api_extract_text(req: ExtractTextRequest) -> dict:
    """Extract entities from raw text."""
    try:
        result = extract_text(
            text=req.text,
            doc_type=req.doc_type,
            doc_id=req.doc_id,
            source_url=req.source_url,
            extractor=req.extractor,
        )
        return result.to_dict()
    except ExtractionError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/graph/status")
async def api_get_status() -> dict:
    """Get graph statistics."""
    try:
        with TradingGraph() as graph:
            stats = graph.get_stats()
            return stats.to_dict()
    except GraphUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.post("/api/graph/query")
async def api_run_query(req: QueryRequest) -> dict:
    """Execute Cypher query."""
    try:
        with TradingGraph() as graph:
            results = graph.run_cypher(req.cypher, req.params)
            return {"results": results}
    except GraphUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/graph/ticker/{symbol}")
async def api_get_ticker_context(symbol: str) -> dict:
    """Get comprehensive context for a ticker."""
    try:
        with TradingGraph() as graph:
            return graph.get_ticker_context(symbol.upper())
    except GraphUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/api/graph/ticker/{symbol}/peers")
async def api_get_peers(symbol: str) -> dict:
    """Get sector peers for a ticker."""
    try:
        with TradingGraph() as graph:
            return {"peers": graph.get_sector_peers(symbol.upper())}
    except GraphUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/api/graph/ticker/{symbol}/risks")
async def api_get_risks(symbol: str) -> dict:
    """Get known risks for a ticker."""
    try:
        with TradingGraph() as graph:
            return {"risks": graph.get_risks(symbol.upper())}
    except GraphUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/api/graph/ticker/{symbol}/competitors")
async def api_get_competitors(symbol: str) -> dict:
    """Get competitors for a ticker."""
    try:
        with TradingGraph() as graph:
            return {"competitors": graph.get_competitors(symbol.upper())}
    except GraphUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/api/graph/biases")
async def api_get_biases(name: str | None = None) -> dict:
    """Get bias history across trades."""
    try:
        with TradingGraph() as graph:
            return {"biases": graph.get_bias_history(name)}
    except GraphUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/api/graph/strategies")
async def api_get_strategies(name: str | None = None) -> dict:
    """Get strategy performance."""
    try:
        with TradingGraph() as graph:
            return {"strategies": graph.get_strategy_performance(name)}
    except GraphUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/api/graph/health")
async def api_health_check() -> dict:
    """Health check endpoint."""
    try:
        with TradingGraph() as graph:
            if graph.health_check():
                return {"status": "healthy", "neo4j": "connected"}
            return {"status": "unhealthy", "neo4j": "disconnected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@app.get("/api/graph/ready")
async def api_readiness_check() -> dict:
    """Readiness check - can accept traffic."""
    try:
        with TradingGraph() as graph:
            stats = graph.get_stats()
            return {
                "status": "ready",
                "schema_initialized": True,
                "node_count": stats.total_nodes,
                "edge_count": stats.total_edges,
            }
    except Exception as e:
        raise HTTPException(status_code=503, detail={"status": "not_ready", "error": str(e)})
