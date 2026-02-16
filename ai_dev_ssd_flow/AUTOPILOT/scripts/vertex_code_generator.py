#!/usr/bin/env python3
"""
Vertex AI Code Generator
Generates source code from high-level SPEC files using Google Vertex AI.

Usage:
  python3 vertex_code_generator.py \
    --spec ai_dev_flow/09_SPEC/SPEC-01_service.yaml \
    --output src/ \
    --project my-gcp-project \
    --location us-central1 \
    --model claude-3-5-sonnet@20240620

Prerequisites:
  - google-cloud-aiplatform
  - vertexai
  - PyYAML
"""

import argparse
import os
import sys
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
import json

# Try importing Vertex AI SDK
try:
    import vertexai
    from vertexai.generative_models import GenerativeModel, Part, HarmCategory, HarmBlockThreshold
    VERTEX_AVAILABLE = True
except ImportError:
    VERTEX_AVAILABLE = False


def load_spec(spec_path: Path) -> Dict[str, Any]:
    """Load and parse the SPEC YAML file."""
    if not spec_path.exists():
        print(f"❌ Error: SPEC file not found: {spec_path}")
        sys.exit(1)
    
    with open(spec_path, 'r', encoding='utf-8') as f:
        try:
            return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            print(f"❌ Error parsing SPEC file: {e}")
            sys.exit(1)

def load_contracts(contracts_path: Path) -> str:
    """Load all referenced API contracts (OpenAPI/Protobuf)."""
    if not contracts_path.exists():
        return ""
    
    context = []
    if contracts_path.is_file():
        files = [contracts_path]
    else:
        files = list(contracts_path.glob("*.yaml")) + list(contracts_path.glob("*.json"))
    
    for f in files:
        context.append(f"--- Contract: {f.name} ---")
        context.append(f.read_text(encoding='utf-8'))
    
    return "\n".join(context)

def construct_prompt(spec: Dict[str, Any], contracts_context: str) -> str:
    """Build the prompt for the LLM."""
    
    spec_yaml = yaml.dump(spec, sort_keys=False)
    
    prompt = f"""
You are a Senior Software Engineer acting as an automated code generator.
Your task is to generate production-ready Python code based strictly on the provided Technical Specification (SPEC).

CONTEXT:
- Framework: AI Dev Flow (Layer 11: Implementation)
- Input: SPEC YAML + API Contracts
- Output: Complete Python source files

RULES:
1. Follow the SPEC exactly. Do not invent requirements.
2. Use the technology stack defined in the SPEC (e.g., FastAPI, Pydantic).
3. Implement 100% type hints (mypy strict).
4. Include Google-style docstrings for all functions and classes.
5. Add traceability tags (e.g. `@spec: SPEC-01`, `@req: REQ-05`) in docstrings.
6. Generate comprehensive unit tests (pytest) for the code.
7. Return ONLY JSON output with the following structure:
{{
  "files": [
    {{
      "path": "src/service/main.py",
      "content": "..."
    }},
    {{
      "path": "tests/test_main.py",
      "content": "..."
    }}
  ]
}}

INPUT SPECIFICATION:
{spec_yaml}

API CONTRACTS:
{contracts_context}

Generate the implementation now.
"""
    return prompt

def generate_code_mock(prompt: str) -> str:
    """Mock generation for testing without API keys."""
    print("⚠️  Vertex AI SDK not found or API call disabled. Returning mock response.")
    
    mock_response = {
        "files": [
            {
                "path": "src/generated_service/main.py",
                "content": "# Generated from SPEC (Mock)\n\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/')\ndef read_root():\n    return {'Hello': 'World'}\n"
            }
        ]
    }
    return json.dumps(mock_response)

def generate_code_vertex(prompt: str, project: str, location: str, model_name: str) -> str:
    """Call Vertex AI to generate code."""
    if not VERTEX_AVAILABLE:
        print("❌ Error: google-cloud-aiplatform not installed. Run: pip install google-cloud-aiplatform")
        return generate_code_mock(prompt)

    print(f"🤖 Initializing Vertex AI (Project: {project}, Location: {location})...")
    vertexai.init(project=project, location=location)
    
    print(f"🧠 Loading Model: {model_name}...")
    model = GenerativeModel(model_name)
    
    config = {
        "max_output_tokens": 8192,
        "temperature": 0.2, # Low temperature for code
        "top_p": 0.95,
    }
    
    print("🚀 Sending request to Vertex AI...")
    try:
        response = model.generate_content(
            prompt,
            generation_config=config,
            stream=False
        )
        return response.text
    except Exception as e:
        print(f"❌ Vertex AI Error: {e}")
        return generate_code_mock(prompt)

def save_files(json_content: str, output_root: Path):
    """Parse JSON response and save files to disk."""
    try:
        # Clean up markdown code blocks if present
        clean_json = json_content.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json[7:]
        if clean_json.endswith("```"):
            clean_json = clean_json[:-3]
        
        data = json.loads(clean_json)
        
        if "files" not in data:
            print("❌ Error: Invalid response format (missing 'files' key)")
            return

        for file_entry in data["files"]:
            rel_path = file_entry.get("path")
            content = file_entry.get("content")
            
            if not rel_path or not content:
                continue
                
            full_path = output_root / rel_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Wrote: {full_path}")
            
    except json.JSONDecodeError as e:
        print(f"❌ Error decoding JSON response: {e}")
        print(f"Raw response start: {json_content[:500]}...")

def main():
    parser = argparse.ArgumentParser(description="Generate code from SPEC using Vertex AI")
    parser.add_argument("--spec", required=True, help="Path to SPEC YAML file")
    parser.add_argument("--contracts", default="", help="Path to CTR directory or file")
    parser.add_argument("--output", default=".", help="Output directory root")
    parser.add_argument("--project", default=os.environ.get("GCP_PROJECT_ID"), help="GCP Project ID")
    parser.add_argument("--location", default="us-central1", help="GCP Region")
    parser.add_argument("--model", default="gemini-1.5-pro-001", help="Model name (e.g. gemini-1.5-pro, claude-3-5-sonnet)")
    parser.add_argument("--dry-run", action="store_true", help="Print prompt without calling AI")
    
    args = parser.parse_args()
    
    spec_path = Path(args.spec)
    output_root = Path(args.output)
    contracts_path = Path(args.contracts) if args.contracts else None
    
    # 1. Load context
    print(f"📖 Loading SPEC: {spec_path}")
    spec_data = load_spec(spec_path)
    
    contracts_context = ""
    if contracts_path:
        print(f"📜 Loading Contracts from: {contracts_path}")
        contracts_context = load_contracts(contracts_path)

    # 2. Construct Prompt
    prompt = construct_prompt(spec_data, contracts_context)
    
    if args.dry_run:
        print("\n--- PROMPT PREVIEW ---")
        print(prompt)
        print("----------------------")
        return

    # 3. Generate
    if not args.project:
        print("⚠️  No GCP Project ID provided. Using mock generation.")
        response_text = generate_code_mock(prompt)
    else:
        response_text = generate_code_vertex(prompt, args.project, args.location, args.model)
        
    # 4. Save
    print("\n💾 Saving Generated Files...")
    save_files(response_text, output_root)
    print("\n✨ Generation Complete!")

if __name__ == "__main__":
    main()
