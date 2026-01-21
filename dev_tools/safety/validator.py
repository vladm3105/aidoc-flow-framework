import argparse
import sys
import json
import re
from pydantic import ValidationError, validate_call
from typing import Optional

def validate_regex(text: str, pattern: str) -> bool:
    if not re.match(pattern, text):
        raise ValueError(f"Value '{text}' does not match regex '{pattern}'")
    return True

def validate_json_str(text: str) -> bool:
    try:
        json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")
    return True

def main():
    parser = argparse.ArgumentParser(description="Runtime Safety Validator")
    parser.add_argument("--input", required=True, help="Input string or JSON")
    parser.add_argument("--regex", help="Regex pattern to enforce")
    parser.add_argument("--json", action="store_true", help="Ensure input is valid JSON")
    
    args = parser.parse_args()
    
    errors = []
    
    # Check Regex
    if args.regex:
        try:
            validate_regex(args.input, args.regex)
        except ValueError as e:
            errors.append(str(e))

    # Check JSON
    if args.json:
        try:
            validate_json_str(args.input)
        except ValueError as e:
            errors.append(str(e))

    if errors:
        print("FAIL")
        for err in errors:
            print(f"Error: {err}")
        sys.exit(1)
    else:
        print("PASS")
        sys.exit(0)

if __name__ == "__main__":
    main()
