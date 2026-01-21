import asyncio
import httpx
import sys
import subprocess
import time

SERVER_SCRIPT = "/opt/data/docs_flow_framework/dev_tools/a2a/server.py"
BASE_URL = "http://localhost:8002"

async def verify():
    print("Starting A2A V2 Verification...")
    
    process = subprocess.Popen(
        [sys.executable, SERVER_SCRIPT],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd="/opt/data/docs_flow_framework/dev_tools/a2a" 
    )
    
    # Wait for startup
    time.sleep(5)
    
    try:
        async with httpx.AsyncClient() as client:
            # 1. Test Static Match
            print("Testing Static Match...")
            resp = await client.get(f"{BASE_URL}/api/v1/market/status")
            assert resp.status_code == 200
            assert resp.json()["is_open"] == True
            print("OK.")

            # 2. Test Dynamic Match + Templating + Latency
            print("Testing Dynamic Match & Latency (Expect ~500ms)...")
            start = time.time()
            resp = await client.get(f"{BASE_URL}/api/v1/users/888")
            elapsed = (time.time() - start) * 1000
            
            print(f"Elapsed: {elapsed:.2f}ms")
            print(f"Response: {resp.json()}")

            assert resp.status_code == 200
            assert resp.json()["id"] == "888" # Template worked
            assert resp.json()["name"] == "Dynamic User 888" # Template worked
            assert elapsed >= 400 # Latency worked (allow some jitter)
            print("OK.")
            
        print("Verification Successful!")
        
    finally:
        process.terminate()
        stdout, stderr = process.communicate()
        if verify.failed: # Pseudo-code check
             print("--- SERVER STDOUT ---")
             print(stdout.decode())
             print("--- SERVER STDERR ---")
             print(stderr.decode())

if __name__ == "__main__":
    # monkey patch for better debugging output
    verify.failed = False
    try:
        asyncio.run(verify())
    except Exception as e:
        verify.failed = True
        raise e
