import asyncio
import subprocess
import sys
import time
from fastapi import FastAPI
import uvicorn
import httpx

# Helper Server to receive events
app = FastAPI()
received_events = []

@app.post("/ingest")
async def ingest(data: dict):
    received_events.append({"ts": time.time(), "data": data})
    return {"status": "ok"}

async def run_server():
    config = uvicorn.Config(app, port=9001, log_level="error")
    server = uvicorn.Server(config)
    await server.serve()

async def verify():
    print("Starting Replay Verification...")
    
    # Start receiver in background task
    server_task = asyncio.create_task(run_server())
    await asyncio.sleep(2) # Wait for startup

    # Run Replayer
    # Speed 0.5 means SLOWER (wait * 2)? No, wait / speed. 
    # Speed 1.0 = real time.
    # Data is 1s apart.
    # We want to test speed control. Speed = 2.0 -> 0.5s apart.
    
    cmd = [
        sys.executable, "replay.py",
        "--source", "test.csv",
        "--target", "http://localhost:9001/ingest",
        "--speed", "2.0" 
    ]
    
    print(f"Running: {' '.join(cmd)}")
    proc = await asyncio.create_subprocess_exec(*cmd)
    await proc.wait()
    
    print(f"Received {len(received_events)} events.")
    assert len(received_events) == 3
    
    # Check Timing
    t0 = received_events[0]["ts"]
    t1 = received_events[1]["ts"]
    t2 = received_events[2]["ts"]
    
    diff1 = t1 - t0
    diff2 = t2 - t1
    
    print(f"Diffs: {diff1:.4f}s, {diff2:.4f}s")
    
    # Expected: 1s gap / 2.0 speed = 0.5s gap.
    # Allow some jitter
    assert 0.4 < diff1 < 0.6
    assert 0.4 < diff2 < 0.6
    
    print("Verification Successful!")
    sys.exit(0)

if __name__ == "__main__":
    # We need to run client and server in same loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(verify())
