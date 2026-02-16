#!/bin/bash

CTR_FILE="/opt/data/trading_nexus_v4.2/Nexus_Platform_v4.2/docs/08_CTR/CTR-01_iam.md"
filename=$(basename "$CTR_FILE")

echo "CHECK 10: YAML Companion File"
echo "-----------------------------------------"

if [[ "$filename" == *.md ]]; then
  yaml_file="${CTR_FILE%.md}.yaml"
  echo "Looking for: $yaml_file"
  
  if [ -f "$yaml_file" ]; then
    echo "Found YAML file"
    
    if command -v python3 &> /dev/null; then
      if python3 -c "import yaml; yaml.safe_load(open('$yaml_file'))" 2>/dev/null; then
        echo "✅ YAML syntax valid"
      else
        echo "❌ YAML syntax invalid"
      fi
    fi
  else
    echo "❌ No YAML file found"
  fi
fi

echo "Done"
