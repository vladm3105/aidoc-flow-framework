#!/usr/bin/env python3
import os
import re
from pathlib import Path
from datetime import datetime
import sys

# Configuration
# Run from project root. Assumes docs/TASKS and docs/IPLAN structure.
PROJECT_ROOT = os.getcwd()
TASKS_DIR = os.path.join(PROJECT_ROOT, "docs", "TASKS")
IPLAN_DIR = os.path.join(PROJECT_ROOT, "docs", "IPLAN")

# Template is relative to this script in the framework
# Script: /opt/data/docs_flow_framework/ai_dev_flow/scripts/generate_iplan.py
# Template: /opt/data/docs_flow_framework/ai_dev_flow/IPLAN/IPLAN-TEMPLATE.md
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FRAMEWORK_ROOT = os.path.dirname(SCRIPT_DIR)
TEMPLATE_PATH = os.path.join(FRAMEWORK_ROOT, "IPLAN", "IPLAN-TEMPLATE.md")

def load_file(path):
    try:
        with open(path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {path}")
        return None

def parse_tasks(content):
    """
    Extracts metadata from TASKS file.
    """
    data = {}
    
    # ID
    id_match = re.search(r'TASKS-([0-9]+)', content)
    data['id_num'] = id_match.group(1) if id_match else "00"
    data['tasks_id'] = f"TASKS-{data['id_num']}"
    
    # Title
    title_match = re.search(r'title: "TASKS-[0-9]+: (.+)"', content)
    if title_match:
        data['title'] = title_match.group(1)
    else:
        # Fallback to H1
        h1_match = re.search(r'# TASKS-[0-9]+: (.+)', content)
        data['title'] = h1_match.group(1) if h1_match else "Untitled"

    # Parent SPEC
    spec_match = re.search(r'parent_spec: (SPEC-[0-9]+)', content)
    data['spec_id'] = spec_match.group(1) if spec_match else "SPEC-00"

    # Traceability Tags
    tags = []
    tag_matches = re.findall(r'(@[a-z]+): (.*)', content)
    for tag, val in tag_matches:
        if tag not in ['@tasks', '@impl']:
            tags.append(f"- `{tag}: {val.strip()}`")
    
    data['tags_list'] = "\n".join(tags)
    
    return data

def generate_iplan_content(tasks_data, template, filename):
    content = template
    
    iplan_id = f"IPLAN-{tasks_data['id_num']}"
    
    # Replace Metadata
    content = content.replace("IPLAN-NN", iplan_id)
    content = content.replace("TASKS-NN", tasks_data['tasks_id'])
    content = content.replace("[Descriptive Task/Feature Name]", tasks_data['title'])
    
    # Context
    content = content.replace("SPEC-NN", tasks_data['spec_id'])
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S EST")
    content = content.replace("YYYY-MM-DD HH:MM:SS TZ", timestamp)
    
    # Context filler
    content = content.replace("[TASKS-NN - code generation plan being implemented]", f"{tasks_data['tasks_id']} - {tasks_data['title']}")
    
    return content

def main():
    print(f"IPLAN Generator")
    print(f"--------------")
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"TASKS Dir:    {TASKS_DIR}")
    print(f"IPLAN Dir:    {IPLAN_DIR}")
    print(f"Template:     {TEMPLATE_PATH}")
    print(f"--------------")

    if not os.path.exists(TASKS_DIR):
        print(f"Error: {TASKS_DIR} does not exist. Run this from your project root.")
        sys.exit(1)

    if not os.path.exists(IPLAN_DIR):
        os.makedirs(IPLAN_DIR)
        
    template = load_file(TEMPLATE_PATH)
    if not template:
        sys.exit(1)
        
    tasks_files = sorted([f for f in os.listdir(TASKS_DIR) if f.startswith("TASKS-") and f.endswith(".md")])
    
    if not tasks_files:
        print("No TASKS files found.")
        sys.exit(0)
        
    print(f"Found {len(tasks_files)} TASKS files. Generating IPLANs...")
    
    for filename in tasks_files:
        if "TEMPLATE" in filename:
            continue
            
        tasks_path = os.path.join(TASKS_DIR, filename)
        tasks_content = load_file(tasks_path)
        
        if not tasks_content:
            continue
            
        tasks_data = parse_tasks(tasks_content)
        
        iplan_filename = filename.replace("TASKS-", "IPLAN-")
        iplan_path = os.path.join(IPLAN_DIR, iplan_filename)
        
        iplan_content = generate_iplan_content(tasks_data, template, iplan_filename)
        
        # Write file
        with open(iplan_path, 'w') as f:
            f.write(iplan_content)
            
        print(f"[GENERATED] {iplan_filename}")

if __name__ == "__main__":
    main()
