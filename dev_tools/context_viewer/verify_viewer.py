import asyncio
import subprocess
import sys
import time
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify-viewer")

async def verify():
    # Start Viewer
    cmd = [sys.executable, "viewer.py", "--port", "9004"]
    logger.info(f"Starting viewer: {' '.join(cmd)}")
    proc = await asyncio.create_subprocess_exec(*cmd)
    
    try:
        await asyncio.sleep(2) # Wait for startup
        
        async with httpx.AsyncClient() as client:
            # 1. Test Index
            resp = await client.get("http://localhost:9004/")
            assert resp.status_code == 200
            assert "sample_run.json" in resp.text
            logger.info("Index page loaded.")

            # 2. Test Viewer
            resp = await client.get("http://localhost:9004/view/sample_run.json")
            assert resp.status_code == 200
            assert "Hello, world!" in resp.text
            logger.info("Viewer page loaded.")
            
        print("Verification Successful!")
    finally:
        proc.terminate()
        await proc.wait()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(verify())
