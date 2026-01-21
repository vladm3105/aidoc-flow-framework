# Generic Event Replay Tool

A project-agnostic utility to replay historical events (from CSV/JSONL) to a target system (HTTP) with accurate time simulation.

## Usage

```bash
python replay.py --source data.csv --target http://localhost:8000/api/ingest --speed 10
```

## Arguments

- `--source`: Path to input file. Supported formats:
    - `.csv`: Comma-separated values.
    - `.jsonl`: JSON Lines (one JSON object per line).
- `--target`: HTTP endpoint to POST events to.
- `--speed`: Speed multiplier.
    - `1.0`: Real-time (1 second in data = 1 second wait).
    - `10.0`: 10x speed.
    - `0.0`: No wait (send execution speed).
- `--ts-col`: Name of the column containing timestamps (default: auto-detects `timestamp`, `time`, `ts`).
- `--no-sort`: Disable auto-sorting by timestamp.

## Example Data

`market_data_sample.csv`:
```csv
timestamp,symbol,price,volume
2023-10-01T09:30:00,AAPL,170.00,100
2023-10-01T09:30:05,AAPL,170.10,50
2023-10-01T09:30:10,AAPL,170.05,200
```

Running this at `--speed 5` will send 3 requests with ~1 second interval between them.
