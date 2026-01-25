#!/bin/bash

CTR_FILE="/opt/data/trading_nexus_v4.2/Nexus_Platform_v4.2/docs/08_CTR/CTR-01_iam.md"

echo "Testing tag detection loop..."

for tag in "@brd" "@prd" "@ears" "@bdd" "@adr" "@sys" "@req"; do
  echo "Checking tag: $tag"
  if grep -qE "^${tag}:|^\- \`${tag}:" "$CTR_FILE"; then
    echo "  ✅ Found"
  else
    echo "  ❌ MISSING"
  fi
done

echo "Loop completed successfully"
