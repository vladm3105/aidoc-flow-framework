#!/bin/bash
# =============================================================================
# Add schema validation to all TSPEC validators
# Applies the same pattern used in validate_utest.py to other validators
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================="
echo "Adding Schema Validation to Validators"
echo "========================================="
echo ""

# Array of validator types (excluding UTEST which is already done)
TYPES=("itest" "stest" "ftest" "ptest" "sectest")

for type in "${TYPES[@]}"; do
    TYPE_UPPER=$(echo "$type" | tr '[:lower:]' '[:upper:]')
    validator_file="$SCRIPT_DIR/validate_${type}.py"

    echo "Processing: validate_${type}.py"

    # Check if file exists
    if [ ! -f "$validator_file" ]; then
        echo "  ❌ File not found: $validator_file"
        continue
    fi

    # Check if schema validation already added
    if grep -q "_validate_against_schema" "$validator_file"; then
        echo "  ✅ Schema validation already present - skipping"
        continue
    fi

    # Create a Python script to add schema validation
    python3 << EOF
import re

# Read the file
with open('$validator_file', 'r') as f:
    content = f.read()

# 1. Add imports after existing imports
import_pattern = r'(import argparse\nimport re\nimport sys\nfrom dataclasses import dataclass, field\nfrom pathlib import Path\nfrom typing import Optional)'
import_replacement = r'''\1
import yaml

try:
    from jsonschema import validate as jsonschema_validate, ValidationError, SchemaError
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False'''

if re.search(import_pattern, content):
    content = re.sub(import_pattern, import_replacement, content)
else:
    print("  ⚠️  Could not find import section - manual edit required")

# 2. Add schema validation method after __init__
# Find the __init__ method and add schema validation after it
init_end_pattern = r'(    def __init__\(self, verbose: bool = False\):.*?self\.spec_ref: Optional\[str\] = None)\n\n(    def validate_file)'
schema_method = r'''

    def _validate_against_schema(self, file_path: Path, content: str) -> list:
        """Validate TSPEC document against MVP schema with flexible path resolution.

        Args:
            file_path: Path to TSPEC file
            content: File content string

        Returns:
            List of schema validation errors
        """
        errors = []

        if not HAS_JSONSCHEMA:
            # jsonschema not available - skip schema validation
            return errors

        # Extract type from filename
        filename = file_path.name
        type_match = re.match(r'^(UTEST|ITEST|STEST|FTEST|PTEST|SECTEST)-', filename)

        if not type_match:
            errors.append(f"Cannot determine test type from filename: {filename}")
            return errors

        type_name = type_match.group(1)

        # Try multiple schema locations
        schema_candidates = [
            # Nested structure: /TYPE/TYPE-NN_slug/TYPE-NN_slug.md -> /TYPE/TYPE_MVP_SCHEMA.yaml
            file_path.parents[1] / f"{type_name}_MVP_SCHEMA.yaml",

            # Flat structure: /TYPE/TYPE-NN_slug.md -> /TYPE/TYPE_MVP_SCHEMA.yaml
            file_path.parent / f"{type_name}_MVP_SCHEMA.yaml",

            # Type subdirectory: /10_TSPEC/TYPE/... -> /10_TSPEC/TYPE/TYPE_MVP_SCHEMA.yaml
            file_path.parents[2] / type_name / f"{type_name}_MVP_SCHEMA.yaml" if len(file_path.parents) > 2 else None,
        ]

        # Dynamic search strategy
        current = file_path.parent
        search_depth = 0
        while current.name and current.name not in ['TSPEC', '10_TSPEC', '/'] and search_depth < 5:
            schema_candidates.append(current / type_name / f"{type_name}_MVP_SCHEMA.yaml")
            current = current.parent
            search_depth += 1
            if current == current.parent:  # Reached root
                break

        # Find first existing schema
        schema_file = None
        for candidate in schema_candidates:
            if candidate and candidate.exists():
                schema_file = candidate
                break

        if not schema_file:
            # No schema found - return warning but don't block
            if self.verbose:
                print(f"  Note: Schema file not found for {type_name}")
            return errors

        try:
            # Load schema
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema = yaml.safe_load(f)

            # Parse frontmatter (YAML between --- markers)
            frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if not frontmatter_match:
                errors.append("No YAML frontmatter found")
                return errors

            frontmatter = yaml.safe_load(frontmatter_match.group(1))

            # Validate against schema
            jsonschema_validate(instance=frontmatter, schema=schema)

        except yaml.YAMLError as e:
            errors.append(f"YAML parsing error: {e}")
        except ValidationError as e:
            errors.append(f"Schema validation failed: {e.message} at {'.'.join(str(p) for p in e.path)}")
        except SchemaError as e:
            errors.append(f"Invalid schema: {e}")
        except Exception as e:
            errors.append(f"Unexpected error during schema validation: {e}")

        return errors

\2'''

if re.search(init_end_pattern, content, re.DOTALL):
    content = re.sub(init_end_pattern, r'\1' + schema_method, content, flags=re.DOTALL)
else:
    print("  ⚠️  Could not find __init__ method - manual edit required")

# 3. Add schema validation call in validate_file method
validate_pattern = r'(        content = file_path\.read_text\(encoding="utf-8"\))\n(\s+)(self\.test_cases = \[\])'
validate_replacement = r'''\1

        # NEW (v2.0): Schema validation (before other checks)
        schema_errors = self._validate_against_schema(file_path, content)
        if schema_errors:
            return ValidationResult(
                file_path=str(file_path),
                passed=False,
                overall_score=0,
                issues=schema_errors,
            )

\2\3'''

if re.search(validate_pattern, content):
    content = re.sub(validate_pattern, validate_replacement, content)
else:
    print("  ⚠️  Could not find validate_file content section - manual edit required")

# Write back
with open('$validator_file', 'w') as f:
    f.write(content)

print("  ✅ Schema validation added")
EOF

done

echo ""
echo "========================================="
echo "Schema Validation Added to All Validators"
echo "========================================="
