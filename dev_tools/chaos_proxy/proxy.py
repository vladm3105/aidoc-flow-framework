import argparse
import asyncio
import random
import logging
from typing import Optional

from fastapi import FastAPI, Request, Response, HTTPException
import httpx
import uvicorn

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - FAULT - %(message)s')
logger = logging.getLogger("chaos-proxy")

app = FastAPI(title="Chaos Proxy")

# Global Config
TARGET_URL = ""
FAILURE_RATE = 0.0
LATENCY_MS = 0

@app.on_event("startup")
async def startup():
    logger.info(f"Proxy started. Target: {TARGET_URL}, Failure Rate: {FAILURE_RATE}, Latency: {LATENCY_MS}ms")

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(path: str, request: Request):
    # 1. Fault Injection: Latency
    if LATENCY_MS > 0:
        # Add some jitter (+/- 20%)
        jitter = random.uniform(0.8, 1.2)
        delay = (LATENCY_MS * jitter) / 1000.0
        await asyncio.sleep(delay)

    # 2. Fault Injection: Error
    if random.random() < FAILURE_RATE:
        logger.warning(f"Injecting failure for {path}")
        return Response(content="Chaos Injection: 500 Internal Server Error", status_code=500)

    # 3. Forward Request
    url = f"{TARGET_URL}/{path}"
    
    async with httpx.AsyncClient() as client:
        try:
            # Read body
            body = await request.body()
            
            # Forward headers (excluding host)
            headers = dict(request.headers)
            headers.pop("host", None)
            
            # Send
            resp = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                data=body,
                params=request.query_params
            )
            
            return Response(
                content=resp.content,
                status_code=resp.status_code,
                headers=dict(resp.headers)
            )
        except Exception as e:
            logger.error(f"Upstream error: {e}")
            raise HTTPException(status_code=502, detail="Upstream unreachable")

def main():
    parser = argparse.ArgumentParser(description="Chaos Proxy")
    parser.add_argument("--target", required=True, help="Upstream URL (e.g. http://localhost:8002)")
    parser.add_argument("--port", type=int, default=9002, help="Proxy port")
    parser.add_argument("--failure-rate", type=float, default=0.0, help="0.0 to 1.0")
    parser.add_argument("--latency", type=int, default=0, help="Latency in ms")
    
    args = parser.parse_args()
    
    global TARGET_URL, FAILURE_RATE, LATENCY_MS
    TARGET_URL = args.target.rstrip("/")
    FAILURE_RATE = args.failure_rate
    LATENCY_MS = args.latency
    
    uvicorn.run(app, host="0.0.0.0", port=args.port)

if __name__ == "__main__":
    main()
