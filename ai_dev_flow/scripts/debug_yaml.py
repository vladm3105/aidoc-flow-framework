import yaml
from pathlib import Path

def check_schema(path):
    print(f"Checking {path}...")
    try:
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        print(f"Parsing successful. Type: {type(data)}")
        if isinstance(data, dict):
            print(f"schema_version keys: {[k for k in data.keys() if 'schema_version' in k]}")
            val = data.get('schema_version')
            print(f"schema_version value: {val!r}")
        else:
            print("Not a dict!")
    except Exception as e:
        print(f"Error: {e}")

check_schema('/opt/data/docs_flow_framework/ai_dev_flow/01_BRD/BRD_MVP_SCHEMA.yaml')
check_schema('/opt/data/docs_flow_framework/ai_dev_flow/02_PRD/PRD_MVP_SCHEMA.yaml')
