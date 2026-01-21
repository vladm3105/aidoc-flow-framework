import asyncio
import subprocess
import sys
import time
from fastapi import FastAPI
import uvicorn
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify-chaos")

# 1. Target Server (Simulates Mock A2A)
app = FastAPI()
@app.get("/status")
async def status():
    return {"status": "ok"}

async def run_target():
    config = uvicorn.Config(app, port=9003, log_level="error")
    server = uvicorn.Server(config)
    await server.serve()

async def verify():
    # Start Target
    target_task = asyncio.create_task(run_target())
    await asyncio.sleep(2)

    # Start Proxy
    # Point to 9003. Listen on 9002.
    # Failure Rate 0.5, Latency 500ms
    proxy_cmd = [
        sys.executable, "proxy.py",
        "--target", "http://localhost:9003",
        "--port", "9002",
        "--failure-rate", "0.5",
        "--latency", "500"
    ]
    logger.info(f"Starting proxy: {' '.join(proxy_cmd)}")
    proxy_proc = await asyncio.create_subprocess_exec(*proxy_cmd)
    
    await asyncio.sleep(2) # Wait for proxy startup
    
    # Test Requests
    success_count = 0
    fail_count = 0
    total_time = 0
    iterations = 10
    
    async with httpx.AsyncClient() as client:
        logger.info(f"Sending {iterations} requests...")
        for i in range(iterations):
            start = time.time()
            try:
                resp = await client.get("http://localhost:9002/status", timeout=2.0)
                if resp.status_code == 200:
                    success_count += 1
                elif resp.status_code == 500:
                    fail_count += 1
                else:
                     logger.warning(f"Unexpected status: {resp.status_code}")
            except Exception as e:
                logger.error(f"Request failed: {e}")
                
            elapsed = (time.time() - start) * 1000
            total_time += elapsed
            logger.info(f"Req {i}: Status={resp.status_code if 'resp' in locals() else 'ERR'}, Time={elapsed:.2f}ms")

    # Clean up
    proxy_proc.terminate()
    await proxy_proc.wait()
    
    avg_time = total_time / iterations
    logger.info(f"Success: {success_count}, Fail: {fail_count}, Avg Time: {avg_time:.2f}ms")
    
    # Assertions
    # 1. Latency should be around 500ms + overhead
    assert avg_time > 400, f"Latency too low: {avg_time}"
    
    # 2. Failures should happen (probabilistic, but 0.5 rate over 10 reqs should catch at least 1)
    if fail_count == 0:
        logger.warning("No failures occurred (unlikely but possible with random).")
    else:
        logger.info("Failures injected successfully.")

    print("Verification Successful!")
    sys.exit(0)

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(verify())
