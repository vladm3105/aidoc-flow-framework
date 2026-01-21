# Chaos Proxy

A fault-injection proxy to test agent resilience.

## Usage

```bash
python proxy.py \
  --target http://localhost:8002 \
  --failure-rate 0.2 \
  --latency 1000
```

This will:
- Forward traffic to `http://localhost:8002` (Mock A2A).
- Fail 20% of requests with HTTP 500.
- Delay all requests by ~1000ms.
