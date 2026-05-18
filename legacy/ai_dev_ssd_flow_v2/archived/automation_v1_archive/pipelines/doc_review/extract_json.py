#!/usr/bin/env python3
"""
extract_json.py — Extract a JSON array from AI agent response text.
Strips markdown code fences and validates the output is a JSON array.

Usage: python3 extract_json.py <input_file> <output_file>
Exit: 0=success, 1=error
"""
import json
import re
import sys

if len(sys.argv) != 3:
    print("Usage: extract_json.py <input_file> <output_file>", file=sys.stderr)
    sys.exit(1)

input_file  = sys.argv[1]
output_file = sys.argv[2]

try:
    with open(input_file) as f:
        text = f.read().strip()
except FileNotFoundError:
    print(f"[extract_json] ERROR: input file not found: {input_file}", file=sys.stderr)
    sys.exit(1)

# Strip markdown code fences if present
text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.MULTILINE)
text = re.sub(r'\s*```\s*$', '', text, flags=re.MULTILINE)
text = text.strip()

try:
    data = json.loads(text)
    if not isinstance(data, list):
        raise ValueError("Expected a JSON array, got: " + type(data).__name__)
except Exception as e:
    print(f"[extract_json] ERROR: AI response is not valid JSON: {e}", file=sys.stderr)
    print(f"[extract_json] Raw response (first 500 chars):\n{text[:500]}", file=sys.stderr)
    sys.exit(1)

with open(output_file, "w") as f:
    json.dump(data, f, indent=2)

p0 = sum(1 for i in data if i.get("priority") == "P0")
p1 = sum(1 for i in data if i.get("priority") == "P1")
p2 = sum(1 for i in data if i.get("priority") == "P2")
p3 = sum(1 for i in data if i.get("priority") == "P3")

print(f"[extract_json] Extracted {len(data)} actions: P0={p0}, P1={p1}, P2={p2}, P3={p3}")
