import asyncio
import argparse
import sys
import json
import logging
import time
from typing import List, Dict, Any
import httpx
import pandas as pd
from dateutil import parser as date_parser

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("event-replay")

class Replayer:
    def __init__(self, source: str, target: str, speed: float, timestamp_col: str, sort: bool):
        self.source = source
        self.target = target
        self.speed = speed
        self.timestamp_col = timestamp_col
        self.sort = sort
        self.client = httpx.AsyncClient()

    def load_data(self) -> List[Dict[str, Any]]:
        logger.info(f"Loading data from {self.source}...")
        try:
            if self.source.endswith('.csv'):
                df = pd.read_csv(self.source)
            elif self.source.endswith('.jsonl') or self.source.endswith('.json'):
                df = pd.read_json(self.source, lines=self.source.endswith('.jsonl'))
            else:
                raise ValueError("Unsupported file format. Use .csv or .jsonl")
            
            # Normalize timestamp
            if self.timestamp_col not in df.columns:
                 # Try common names if not specified
                 common = ['timestamp', 'ts', 'time', 'date', 'datetime']
                 for c in common:
                     if c in df.columns:
                         self.timestamp_col = c
                         logger.info(f"Auto-detected timestamp column: {c}")
                         break
                 else:
                     raise ValueError(f"Timestamp column '{self.timestamp_col}' not found.")

            # Convert to datetime
            df[self.timestamp_col] = pd.to_datetime(df[self.timestamp_col])
            
            if self.sort:
                df = df.sort_values(by=self.timestamp_col)
            
            records = df.to_dict(orient='records')
            logger.info(f"Loaded {len(records)} events.")
            return records
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            sys.exit(1)

    async def run(self):
        events = self.load_data()
        if not events:
            return

        start_real_time = time.time()
        start_event_time = events[0][self.timestamp_col].timestamp()

        logger.info(f"Starting replay of {len(events)} events at {self.speed}x speed.")
        
        for i, event in enumerate(events):
            # Calculate target delay
            event_ts = event[self.timestamp_col].timestamp()
            time_offset = event_ts - start_event_time
            
            # Where we should be in real time
            target_real_time = start_real_time + (time_offset / self.speed)
            
            # Wait if needed
            now = time.time()
            if target_real_time > now:
                delay = target_real_time - now
                if delay > 0.001: # Don't sleep shorter than 1ms
                    await asyncio.sleep(delay)
            
            await self.send_event(event)

        logger.info("Replay complete.")

    async def send_event(self, event: Dict[str, Any]):
        # JSON serializer fallback for datetime
        data = json.loads(json.dumps(event, default=str)) 
        try:
            resp = await self.client.post(self.target, json=data)
            status = resp.status_code
            if status >= 400:
                logger.warning(f"Target returned status {status}")
        except Exception as e:
            logger.error(f"Failed to send event: {e}")

async def main():
    parser = argparse.ArgumentParser(description="Generic Event Replay Tool")
    parser.add_argument("--source", required=True, help="Input file (CSV/JSONL)")
    parser.add_argument("--target", required=True, help="Target URL (HTTP POST)")
    parser.add_argument("--speed", type=float, default=1.0, help="Replay speed multiplier")
    parser.add_argument("--ts-col", default="timestamp", help="Timestamp column name")
    parser.add_argument("--no-sort", action="store_true", help="Skip sorting by timestamp")

    args = parser.parse_args()

    replayer = Replayer(
        source=args.source,
        target=args.target,
        speed=args.speed,
        timestamp_col=args.ts_col,
        sort=not args.no_sort
    )
    
    await replayer.run()

if __name__ == "__main__":
    asyncio.run(main())
