#!/usr/bin/env python3
"""
MVP Autopilot: Generate and validate the MVP workflow from BRD to TASKS.

This tool scaffolds single-file MVP artifacts using existing templates,
runs layer validators, and optionally attempts simple auto-fixes.

Usage:
  python3 ai_dev_flow/scripts/mvp_autopilot.py \
    --root ai_dev_flow \
    --intent "My MVP idea" \
    --up-to TASKS \
    --auto-fix

Notes:
  - Generation uses the repository's MVP/full templates under `ai_dev_flow/*`.
  - No network calls or LLMs are used; content is copied from templates with
    light substitutions from `--intent` and IDs.
  - Validators are invoked via the existing validate_all.py registry.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Allow importing validator registry/utilities
SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

try:
    # Use the existing orchestrator to avoid duplicating validator logic
    from validate_all import VALIDATOR_REGISTRY, run_validator, ValidatorConfig
except Exception:
    VALIDATOR_REGISTRY = {}
    run_validator = None  # type: ignore
    ValidatorConfig = object  # type: ignore


@dataclass
class Layer:
    name: str
    layer_no: int
    # template filename relative to `ai_dev_flow/<NAME>/`
    template: str
    # expected file extension for generated artifact
    ext: str = ".md"
    # upstream tag list to apply for basic auto-fixes
    upstream_tags: List[str] = field(default_factory=list)

    def dir(self, root: Path) -> Path:
        return root / self.name

    def template_path(self, root: Path) -> Path:
        return self.dir(root) / self.template


def slugify(text: str, fallback: str) -> str:
    if not text:
        return fallback
    # lowercase, alnum and underscores only
    s = re.sub(r"[^a-z0-9]+", "_", text.lower())
    s = s.strip("_")
    return s or fallback


def substitute_ids(content: str, layer_name: str, nn: str = "01") -> str:
    # 1. Handle complex/nested placeholders first (specific to templates)
    # BRD.NN.TT.SS -> BRD.01.01.01
    content = re.sub(fr"BRD\.NN\.TT\.SS", f"BRD.{nn}.01.01", content)
    # PRD.NN.EE.SS -> PRD.01.01.01
    content = re.sub(fr"PRD\.NN\.EE\.SS", f"PRD.{nn}.01.01", content)
    # BRD.NN.32.SS -> BRD.01.32.01 (Architecture reference)
    content = re.sub(fr"BRD\.NN\.32\.SS", f"BRD.{nn}.32.01", content)
    # EARS.NN.24.SS -> EARS.01.24.01
    content = re.sub(fr"EARS\.NN\.24\.SS", f"EARS.{nn}.24.01", content)
    
    # 2. Handle standard NN tokens for ALL layers with separator preservation
    prefixes = ["BRD", "PRD", "EARS", "BDD", "ADR", "SYS", "REQ", "SPEC"]
    for prefix in prefixes:
        # Match Prefix + Separator + NN (e.g. BRD-NN or BRD.NN)
        # Capture separator to preserve style (dot vs hyphen)
        # Use \g<N> syntax to avoid octal/group ambiguity with subsequent digits
        content = re.sub(fr"({prefix})([-._])NN", fr"\g<1>\g<2>{nn}", content)
    
    # 3. Fallback for current layer generic reference
    if layer_name not in prefixes:
         content = re.sub(fr"({layer_name})([-._])NN", fr"\g<1>\g<2>{nn}", content)
    
    return content


def ensure_planning_docs(layer_dir: Path, name: str, id_nn: str, target_filename: str) -> None:
    # Create X-00_required_documents_list.md if missing; list the intended file
    req = layer_dir / f"{name}-00_required_documents_list.md"
    if not req.exists():
        req.write_text(
            f"# {name} Required Documents List\n\n- {target_filename}\n",
            encoding="utf-8",
        )


def generate_from_template(
    layer: Layer,
    root: Path,
    nn: str,
    intent: str,
    slug_hint: str,
) -> Path:
    layer_dir = layer.dir(root)
    layer_dir.mkdir(parents=True, exist_ok=True)

    slug = slugify(slug_hint or intent, f"{layer.name.lower()}_{nn}")
    target = layer_dir / f"{layer.name}-{nn}_{slug}{layer.ext}"
    if target.exists():
        return target

    # Fix: use SCRIPT_DIR to find templates in the framework directory
    # layer.template_path(root) was incorrectly looking in the output directory
    tpl = SCRIPT_DIR.parent / layer.name / layer.template
    
    if not tpl.exists():
        # fallback: create minimal file if template missing
        target.write_text(
            f"---\n" f"title: \"{layer.name}-{nn}: {slug.replace('_',' ').title()}\"\n" f"---\n\n",
            encoding="utf-8",
        )
        ensure_planning_docs(layer_dir, layer.name, nn, target.name)
        return target

    content = tpl.read_text(encoding="utf-8")
    content = substitute_ids(content, layer.name, nn)
    
    # Fix: update document_type from template to artifact type
    content = content.replace("document_type: template", f"document_type: {layer.name.lower()}")
    
    # Fix: update tags (remove template tag, ensure artifact tag exists)
    # Replace 'layer-template' with 'layer' (e.g. 'prd-template' -> 'prd')
    content = content.replace(f"{layer.name.lower()}-template", layer.name.lower())
    # Ensure mandatory tag exists if replacement didn't just add it
    # (Since we replaced prd-template with prd, prd is now there. If prd was duplicate, YAML handles it or we don't care)

    # Shallow injection of intent where obvious placeholders exist
    human_slug = slug.replace("_", " ").title()
    content = content.replace("[MVP Product/Feature Name]", human_slug)
    content = content.replace("[MVP idea]", intent)
    content = content.replace("[Idea/Project Name]", human_slug)

    # Normalize frontmatter title to concrete ID when possible
    try:
        display_title = f"{layer.name}-{nn}: {human_slug}"
        content = re.sub(r'(?m)^title:\s*".*"$', f'title: "{display_title}"', content)
    except Exception:
        pass

    # Best-effort heading normalization for markdown/templates
    try:
        if layer.ext == ".md":
            # Replace first H1 that looks like a template header
            content = re.sub(
                r'(?m)^(#)\s+.*TEMPLATE.*$',
                f"# {layer.name}-{nn}: {human_slug}",
                content,
                count=1,
            )
        elif layer.ext == ".feature":
            # Replace Feature line if it's a template marker
            content = re.sub(
                r'(?m)^Feature:\s*.*TEMPLATE.*$',
                f"Feature: {layer.name}-{nn} — {human_slug}",
                content,
                count=1,
            )
    except Exception:
        pass

    # Ensure frontmatter is at the top (fix for templates with leading comments)
    try:
        content = _move_frontmatter_to_top(content)
    except Exception:
        pass

    target.write_text(content, encoding="utf-8")
    ensure_planning_docs(layer_dir, layer.name, nn, target.name)
    return target


def basic_upstream_tag_block(layer: Layer, upstream_ids: Dict[str, str]) -> str:
    if not layer.upstream_tags:
        return ""
    lines = ["\n<!-- Autopilot traceability tags -->\n"]
    for tag in layer.upstream_tags:
        if tag.lower() in upstream_ids:
            lines.append(f"@{tag.lower()}: {upstream_ids[tag.lower()]}\n")
    return ("\n" + "".join(lines) + "\n") if len(lines) > 1 else ""


def _move_frontmatter_to_top(content: str) -> str:
    """Ensure a YAML frontmatter block is at the top if one exists elsewhere."""
    if content.startswith("---\n"):
        return content
    # find any frontmatter block

    m = re.search(r"\n---\n(.*?)\n---\n", content, re.DOTALL)
    if not m:
        return content
    block = m.group(0).strip("\n") + "\n\n"
    before = content[: m.start()] if m else ""
    after = content[m.end():] if m else content
    # remove block from original position and prepend
    return block + before + after


def _ensure_frontmatter_keys(content: str, required_tags: List[str], required_cf: Dict[str, str | int | list]) -> str:
    """Best-effort frontmatter patcher: inject tags and custom_fields keys if missing in the first block."""

    if not content.startswith("---\n"):
        # create a minimal frontmatter
        tags_yaml = "\n".join([f"  - {t}" for t in required_tags])
        cf_lines = []
        for k, v in required_cf.items():
            if isinstance(v, list):
                vv = ", ".join(str(x) for x in v)
                cf_lines.append(f"  {k}: [{vv}]")
            else:
                cf_lines.append(f"  {k}: {v}")
        cf_yaml = "\n".join(cf_lines)
        header = f"---\n" f"title: \"\"\n" f"tags:\n{tags_yaml}\n" f"custom_fields:\n{cf_yaml}\n" f"---\n\n"
        return header + content

    # patch inside existing first frontmatter
    # capture first block only
    m = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if not m:
        return content
    yaml_block = m.group(1)
    body = content[m.end():]

    # ensure tags list exists and contains required tags
    if "\ntags:" not in "\n" + yaml_block:
        yaml_block = yaml_block + "\n" + "tags:\n" + "\n".join([f"  - {t}" for t in required_tags])
    else:
        for t in required_tags:
            if re.search(rf"^\s*-\s*{re.escape(t)}\s*$", yaml_block, re.MULTILINE) is None:
                # append to tags list
                yaml_block = re.sub(r"\ntags:\n", "\ntags:\n  - " + t + "\n", yaml_block, count=1)

    # ensure custom_fields exists and keys are present
    if "\ncustom_fields:" not in "\n" + yaml_block:
        cf_lines = []
        for k, v in required_cf.items():
            if isinstance(v, list):
                vv = ", ".join(str(x) for x in v)
                cf_lines.append(f"  {k}: [{vv}]")
            else:
                cf_lines.append(f"  {k}: {v}")
        yaml_block = yaml_block + "\ncustom_fields:\n" + "\n".join(cf_lines)
    else:
        for k, v in required_cf.items():
            pat = rf"\n\s*{re.escape(k)}:\s*"
            if re.search(pat, yaml_block) is None:
                insert_point = yaml_block.find("custom_fields:") + len("custom_fields:")
                yaml_block = yaml_block[:insert_point] + f"\n  {k}: {v if not isinstance(v, list) else '[' + ', '.join(str(x) for x in v) + ']'}" + yaml_block[insert_point:]

    return f"---\n{yaml_block}\n---\n" + body


def _ensure_h1(content: str, layer_name: str, nn: str, human_slug: str) -> str:

    # Remove any first H1 and replace with standardized one
    lines = content.splitlines()
    idx = None
    for i, line in enumerate(lines):
        if line.startswith("# ") and not line.startswith("## "):
            idx = i
            break
    new_h1 = f"# {layer_name}-{nn}: {human_slug}"
    if idx is not None:
        lines[idx] = new_h1
    else:
        # Insert after frontmatter if present
        if content.startswith("---\n"):
            # find end of frontmatter
            m = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
            pos = m.end() if m else 0
            return content[:pos] + "\n" + new_h1 + "\n" + content[pos:]
        else:
            return new_h1 + "\n\n" + content
    return "\n".join(lines)


def _ensure_section(content: str, header: str, stub: str) -> str:

    if re.search(rf"^\s*{re.escape(header)}\s*$", content, re.MULTILINE):
        return content
    return content.rstrip() + "\n\n" + header + "\n" + stub.strip() + "\n"


def _fix_brd(content: str, nn: str, human_slug: str) -> str:
    # Frontmatter at top with tags and custom_fields
    content = _move_frontmatter_to_top(content)
    content = _ensure_frontmatter_keys(
        content,
        required_tags=["brd", "layer-1-artifact"],
        required_cf={
            "document_type": "brd",
            "artifact_type": "BRD",
            "layer": 1,
            "architecture_approaches": ["ai-agent-based"],
            "priority": "shared",
            "development_status": "active",
        },
    )
    # H1
    content = _ensure_h1(content, "BRD", nn, human_slug)
    # Required sections minimal stubs or rename existing numbered sections to expected labels
    dc_stub = "| Item | Details |\n|------|---------|\n| Related PRD | PRD-" + nn + " |\n| Status | Draft |"
    content = _ensure_section(content, "## 0. Document Control", dc_stub)


    def _ensure_or_rename(num: int, expected: str, stub: str) -> str:
        nonlocal content
        # If exact header exists, do nothing
        if re.search(rf"^##\s+{num}\.\s+{re.escape(expected)}\s*$", content, re.MULTILINE):
            return content
        # Find first header with this number and rename it
        m = re.search(rf"^##\s+{num}\.\s+.+$", content, re.MULTILINE)
        if m:
            start, end = m.span()
            line = content[start:end]
            content = content[:start] + f"## {num}. {expected}" + content[end:]
            return content
        # Otherwise append a new section stub
        content = _ensure_section(content, f"## {num}. {expected}", stub)
        return content

    content = _ensure_or_rename(1, "Executive Summary", "[One-paragraph summary]")
    content = _ensure_or_rename(2, "Business Context", "[Context]")
    content = _ensure_or_rename(3, "Business Requirements", "- [ ] MVP Requirement 1")
    # Demote duplicate top-level section numbers 1-3 to avoid duplicates
    lines = content.splitlines()
    seen_nums = set()
    for i, line in enumerate(lines):
        m = re.match(r"^##\s+(\d+)\.\s+", line)
        if m:
            num = int(m.group(1))
            if num in (1, 2, 3):
                if num in seen_nums:
                    lines[i] = line.replace("## ", "### ", 1)
                else:
                    seen_nums.add(num)
    content = "\n".join(lines)
    return content


def _fix_prd(content: str, nn: str, upstream_ids: Dict[str, str], human_slug: str) -> str:
    content = _move_frontmatter_to_top(content)
    content = _ensure_frontmatter_keys(
        content,
        required_tags=["prd", "layer-2-artifact"],
        required_cf={
            "document_type": "prd",
            "artifact_type": "PRD",
            "layer": 2,
            "architecture_approaches": ["ai-agent-based"],
            "priority": "shared",
            "development_status": "active",
        },
    )
    content = _ensure_h1(content, "PRD", nn, human_slug)
    # Ensure Document Control with @brd in dotted format
    brd_dot = upstream_ids.get("brd", f"BRD-{nn}").replace("-", ".") + ".01.01"
    dc_stub = (
        "| Item | Details |\n|------|---------|\n" +
        f"| Related BRD | @brd: {brd_dot} |\n| Status | Draft |"
    )
    content = _ensure_section(content, "## 0. Document Control", dc_stub)
    content = _ensure_section(content, "## 1. Executive Summary", "[Summary]")
    content = _ensure_section(content, "## 2. Product Vision", "[Vision]")
    content = _ensure_section(content, "## 3. Functional Requirements", "- [ ] Core capability")
    return content


def _fix_ears(content: str, nn: str, upstream_ids: Dict[str, str], human_slug: str) -> str:
    content = _move_frontmatter_to_top(content)
    content = _ensure_frontmatter_keys(
        content,
        required_tags=["ears", "layer-3-artifact"],
        required_cf={
            "document_type": "ears",
            "artifact_type": "EARS",
            "layer": 3,
            "priority": "shared",
            "development_status": "active",
        },
    )
    content = _ensure_h1(content, "EARS", nn, human_slug)
    # EARS preferred Document Control (no '0.' in header per validator)
    dc_stub = "| Item | Details |\n|------|---------|\n| Source PRD | @prd: PRD." + nn + ".01.01 |\n| Status | Draft |"
    content = _ensure_section(content, "## Document Control", dc_stub)
    content = _ensure_section(content, "## Purpose", "[Purpose of EARS mapping]")
    # Traceability section with tags
    tags_block = (
        "- `@brd: " + upstream_ids.get("brd", f"BRD.{nn}.01.01").replace("-", ".") + "`\n" +
        "- `@prd: PRD." + nn + ".01.01`\n"
    )
    content = _ensure_section(content, "## Traceability", tags_block)
    # Ensure at least one EARS requirement ID (use project NN for cosmetic alignment)
    if "EARS." not in content:
        content += (
            f"\n\n#### EARS.{nn}.01.01: MVP shall provide basic capability\n\n"
            "WHEN a user triggers action THE system SHALL execute core flow.\n"
        )
    return content


def _fix_bdd(content: str, nn: str, upstream_ids: Dict[str, str], human_slug: str) -> str:
    lines = content.splitlines()
    # Ensure tag lines for cumulative traceability
    header_tags = [
        f"@brd: {upstream_ids.get('brd', f'BRD.{nn}.01.01').replace('-', '.')} ",
        f"@prd: PRD.{nn}.01.01 ",
        f"@ears: EARS.{nn}.01.01 ",
    ]
    if not any(line.strip().startswith("@brd") for line in lines[:5]):
        lines.insert(0, "".join(header_tags).strip())
    # Ensure Feature line
    if not any(l.startswith("Feature:") for l in lines):
        lines.insert(1, f"Feature: BDD-{nn} — {human_slug}")
    # Ensure at least one scenario with GWT
    if not any(l.strip().startswith("Scenario:") for l in lines):
        lines += [
            "",
            f"Scenario: Primary path",
            "  Given a precondition",
            "  When the user performs an action",
            "  Then the system responds",
        ]
    return "\n".join(lines)


def try_minimal_autofix(file: Path, layer: Layer, upstream_ids: Dict[str, str]) -> None:
    """Deterministic auto-fixes per layer: frontmatter, headings, sections, tags."""
    try:
        content = file.read_text(encoding="utf-8")
    except Exception:
        return

    human_slug = re.sub(r"[^a-z0-9]+", " ", file.stem.split("_", 1)[1]).title() if "_" in file.stem else file.stem
    nn = re.search(r"-(\d{2,})", file.stem)
    nn = nn.group(1) if nn else "01"

    if layer.name == "BRD":
        newc = _fix_brd(content, nn, human_slug)
    elif layer.name == "PRD":
        newc = _fix_prd(content, nn, upstream_ids, human_slug)
    elif layer.name == "EARS":
        newc = _fix_ears(content, nn, upstream_ids, human_slug)
    elif layer.name == "BDD":
        newc = _fix_bdd(content, nn, upstream_ids, human_slug)
    elif layer.name == "SYS":
        # Build minimal if heavy gaps; simple fixer first
        def _fix_sys(c: str) -> str:
            cc = _move_frontmatter_to_top(c)
            cc = _ensure_frontmatter_keys(
                cc,
                required_tags=["sys", "layer-6-artifact"],
                required_cf={
                    "document_type": "sys",
                    "artifact_type": "SYS",
                    "layer": 6,
                    "architecture_approaches": ["ai-agent-based"],
                    "priority": "shared",
                    "development_status": "draft",
                },
            )
            cc = _ensure_h1(cc, "SYS", nn, human_slug)
            # Required sections 1..15 minimal stubs
            stubs = {
                1: ("Document Control", "| Item | Details |\n|------|---------|\n| Status | Draft |"),
                2: ("Executive Summary", "[Summary]"),
                3: ("Scope", "[Scope]"),
                4: ("Functional Requirements", "- FR-001: Describe function"),
                5: ("Quality Attributes", "Performance: target latency 200ms\nSecurity: baseline"),
                6: ("Interface Specifications", "External Interfaces: ..."),
                7: ("Data Management", "[Data]"),
                8: ("Testing Requirements", "Coverage: 80%"),
                9: ("Deployment Requirements", "[Deploy]"),
                10: ("Compliance Requirements", "[Compliance]"),
                11: ("Acceptance Criteria", "[Criteria]"),
                12: ("Risk Assessment", "[Risks]"),
                13: ("Traceability", "@brd: {brd}\n@prd: {prd}\n@ears: {ears}\n@bdd: {bdd}\n@adr: {adr}".format(
                    brd=upstream_ids.get('brd','BRD.'+nn+'.01.01').replace('-', '.'),
                    prd=upstream_ids.get('prd','PRD.'+nn+'.01.01').replace('-', '.'),
                    ears=upstream_ids.get('ears','EARS.'+nn+'.01.01').replace('-', '.'),
                    bdd=upstream_ids.get('bdd','BDD.'+nn+'.01.01').replace('-', '.'),
                    adr=upstream_ids.get('adr','ADR.'+nn+'.01.01').replace('-', '.'),
                )),
                14: ("Implementation Notes", "[Notes]"),
                15: ("Change History", "| Date | Version | Notes |\n|------|---------|-------|\n| 2025-01-04 | 0.1.0 | Initial |"),
            }
            for num, (title, stub) in stubs.items():
                cc = _ensure_section(cc, f"## {num}. {title}", stub)
            return cc
        newc = _fix_sys(content)
    elif layer.name == "REQ":
        content = _move_frontmatter_to_top(content)
        content = _ensure_frontmatter_keys(
            content,
            required_tags=["req", "layer-7-artifact"],
            required_cf={
                "document_type": "req",
                "artifact_type": "REQ",
                "layer": 7,
                "architecture_approaches": ["ai-agent-based"],
                "priority": "shared",
                "development_status": "draft",
            },
        )
        content = _ensure_h1(content, "REQ", nn, human_slug)
        # 1. Document Control
        dc_stub = "| Item | Details |\n|------|---------|\n| Source | SYS." + nn + ".01.01 |\n| Status | Draft |"
        content = _ensure_section(content, "## 1. Document Control", dc_stub)
        # 2. Requirement Description
        content = _ensure_section(content, "## 2. Requirement Description", "### 2.1 Statement\n\nThe system SHALL...")
        # 3. Traceability
        trace = "@brd: {brd}\n@prd: {prd}\n@sys: {sys}\n@ears: {ears}\n@adr: {adr}".format(
             brd=upstream_ids.get('brd','BRD.'+nn+'.01.01').replace('-', '.'),
             prd=upstream_ids.get('prd','PRD.'+nn+'.01.01').replace('-', '.'),
             sys=upstream_ids.get('sys','SYS.'+nn+'.01.01').replace('-', '.'),
             ears=upstream_ids.get('ears','EARS.'+nn+'.01.01').replace('-', '.'),
             adr=upstream_ids.get('adr','ADR.'+nn+'.01.01').replace('-', '.'),
        )
        content = _ensure_section(content, "## 10. Traceability", f"### 10.3 Traceability Tags\n\n{trace}")
        newc = content
    elif layer.name == "SPEC":
        # Ensure YAML has required top-level keys; fallback if not
        try:
            y = content
            required = ["id","summary","metadata","traceability","architecture","interfaces","behavior","performance","security","observability","verification","implementation"]
            if not all(k+":" in y for k in required):
                raise ValueError("missing keys")
            newc = content
        except Exception:
            newc = content
    else:
        # Fallback: ensure traceability block
        newc = content
        block = basic_upstream_tag_block(layer, upstream_ids)
        if block and any((f"@{t.lower():s}:" not in content.lower()) for t in (layer.upstream_tags or [])):
            newc = content.rstrip() + block

    if newc != content:
        file.write_text(newc, encoding="utf-8")


    # All skeleton-related helpers removed; no minimal templates are generated


def run_layer_validation(root_or_file: Path, layer_name: str, strict: bool = False, mvp_validators: bool = False) -> Tuple[bool, str]:
    """Run a single validator. Success when exit code is 0 (strict) or 0/1 (warnings-only)."""

    if not VALIDATOR_REGISTRY:
        return False, "Validator registry unavailable"
    # MVP-friendly overrides
    if mvp_validators and layer_name == "BRD":
        # Prefer the Python BRD validator on a single file
        script_path = SCRIPT_DIR / "validate_brd.py"
        cmd = [sys.executable, str(script_path), str(root_or_file)]
    else:
        vcfg: ValidatorConfig = VALIDATOR_REGISTRY.get(layer_name)
        if not vcfg:
            return True, f"No validator registered for {layer_name} (skipping)"

        script_path = SCRIPT_DIR / vcfg.script
        if not script_path.exists():
            return False, f"Script not found: {script_path}"

        if vcfg.script_type == "python":
            if layer_name == "EARS":
                cmd = [sys.executable, str(script_path), "--path", str(root_or_file)]
            else:
                cmd = [sys.executable, str(script_path), str(root_or_file)]
        else:
            cmd = ["bash", str(script_path), str(root_or_file)]

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        # Treat warnings-only (exit code 1) as pass unless strict
        ok = (res.returncode == 0) if strict else (res.returncode in (0, 1))
        out = (res.stdout or "") + ("\n" + res.stderr if res.stderr else "")
        return ok, out.strip()
    except subprocess.TimeoutExpired:
        return False, "Validator timed out"
    except Exception as e:
        return False, f"Validator failed: {e}"


def main():
    parser = argparse.ArgumentParser(description="MVP Autopilot (BRD → TASKS)")
    parser.add_argument("--root", default="ai_dev_flow", help="Docs root (default: ai_dev_flow)")
    parser.add_argument("--intent", default="", help="Seed idea to name the MVP")
    parser.add_argument("--nn", default="01", help="Numeric ID to assign (default: 01)")
    parser.add_argument(
        "--up-to",
        default="TASKS",
        choices=["BRD","PRD","EARS","BDD","ADR","SYS","REQ","SPEC","TASKS"],
        help="Last layer to generate/validate (default: TASKS)",
    )
    parser.add_argument("--from-layer", default="", help="Start from this layer (e.g., BDD) instead of BRD")
    parser.add_argument("--auto-fix", action="store_true", help="Attempt simple auto-fixes on failures")
    parser.add_argument("--skip-validate", action="store_true", help="Skip validations (generate only)")
    parser.add_argument("--no-precheck", action="store_true", help="Skip pre-checks (path validator and upstream existence checks)")
    parser.add_argument("--precheck-strict", action="store_true", help="Treat pre-check failures as fatal (block generation)")
    parser.add_argument("--slug", default="", help="Slug hint for filenames")
    # Skeletons are not supported; no related flags
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors during validation")
    parser.add_argument("--report", choices=["none","markdown","json","text"], default="none", help="Write a run summary report")
    parser.add_argument("--report-path", default="", help="Custom report file path (defaults to work_plans/)")
    parser.add_argument("--mvp-validators", action="store_true", help="Use lighter MVP validators when available (e.g., BRD python validator)")
    parser.add_argument("--config", default="", help="Path to autopilot config YAML (defaults to ai_dev_flow/.autopilot.yaml if present)")
    parser.add_argument("--profile", default="", help="Named profile from config to load (e.g., mvp, strict)")
    # Resume/Fork & planning controls
    parser.add_argument("--resume", action="store_true", help="Resume existing project; reuse and validate existing artifacts, generate only missing ones")
    parser.add_argument("--no-overwrite", action="store_true", help="Do not overwrite existing files (skip generation if target exists)")
    parser.add_argument("--include-layers", nargs='*', default=[], help="Limit operation to specific layers (e.g., BRD PRD EARS)")
    parser.add_argument("--exclude-layers", nargs='*', default=[], help="Exclude specific layers")
    parser.add_argument("--plan-only", action="store_true", help="Analyze and report plan without writing files")
    parser.add_argument("--dry-run", action="store_true", help="Show intended actions without writing files")
    # Fork controls
    parser.add_argument("--fork-from-nn", default="", help="Source NN to fork from (e.g., 01)")
    parser.add_argument("--new-nn", default="", help="New NN for forked project (e.g., 02)")
    parser.add_argument("--new-slug", default="", help="New slug for forked project (e.g., new_product)")
    parser.add_argument("--id-map", default="", help="Path to YAML mapping of IDs to rewrite during fork (from->to)")
    parser.add_argument("--supersede", action="store_true", help="Insert Supersedes/Derived-from notes in forked docs")
    parser.add_argument("--copy-assets", action="store_true", help="Copy relative assets when forking documents")
    args = parser.parse_args()

    # Load config (before using args), merge profile/defaults into args where CLI kept defaults
    def _load_config(cfg_path: Optional[str]) -> dict:
        try:
            import yaml  # type: ignore
        except Exception:
            return {}
        config_file = None
        if cfg_path:
            p = Path(cfg_path)
            if p.exists():
                config_file = p
        else:
            p = Path(args.root or "ai_dev_flow") / ".autopilot.yaml"
            if p.exists():
                config_file = p
        if not config_file:
            return {}
        try:
            return yaml.safe_load(config_file.read_text(encoding="utf-8")) or {}
        except Exception:
            return {}

    cfg = _load_config(args.config)

    def _apply_cfg_flag(current_val, cfg_val):
        # Only apply when current equals parser default (False/"none").
        return cfg_val if current_val in (False, "none", "") else current_val

    if cfg:
        defaults = cfg.get("defaults", {})
        profile_name = args.profile or cfg.get("default_profile", "")
        profile = {}
        if profile_name and cfg.get("profiles"):
            profile = cfg["profiles"].get(profile_name, {})
        # Merge order: defaults -> profile -> CLI (CLI already parsed; we only set if still default)
        for key, val in {**defaults, **profile}.items():
            if key == "auto_fix":
                args.auto_fix = _apply_cfg_flag(args.auto_fix, bool(val))
            elif key == "strict":
                args.strict = _apply_cfg_flag(args.strict, bool(val))
            # no_skeleton removed; skeletons are not supported
            elif key == "mvp_validators":
                args.mvp_validators = _apply_cfg_flag(args.mvp_validators, bool(val))
            elif key == "report":
                if args.report == "none" and val in ("markdown", "json", "text"):
                    args.report = val
            elif key == "report_path":
                if not args.report_path and isinstance(val, str):
                    args.report_path = val

    root = Path(args.root).resolve()
    root.mkdir(parents=True, exist_ok=True)

    # Define layers and their upstream tag expectations
    LAYERS: List[Layer] = [
        Layer("BRD", 1, "BRD-MVP-TEMPLATE.md", ".md", upstream_tags=[]),
        Layer("PRD", 2, "PRD-MVP-TEMPLATE.md", ".md", upstream_tags=["brd"]),
        Layer("EARS", 3, "EARS-MVP-TEMPLATE.md", ".md", upstream_tags=["brd","prd"]),
        Layer("BDD", 4, "BDD-MVP-TEMPLATE.feature", ".feature", upstream_tags=["brd","prd","ears"]),
        Layer("ADR", 5, "ADR-MVP-TEMPLATE.md", ".md", upstream_tags=["brd","prd","ears","bdd"]),
        Layer("SYS", 6, "SYS-MVP-TEMPLATE.md", ".md", upstream_tags=["brd","prd","ears","bdd","adr"]),
        Layer("REQ", 7, "REQ-MVP-TEMPLATE.md", ".md", upstream_tags=["brd","prd","ears","bdd","adr","sys"]),
        Layer("SPEC",10, "SPEC-TEMPLATE.yaml", ".yaml", upstream_tags=["req"]),
        Layer("TASKS",11, "TASKS-TEMPLATE.md", ".md", upstream_tags=["spec","req"]),
    ]

    # Apply template overrides from config (optional)
    try:
        tmpl_over = (cfg or {}).get("templates", {})
        if tmpl_over:
            for layer in LAYERS:
                if layer.name in tmpl_over and isinstance(tmpl_over[layer.name], str):
                    layer.template = tmpl_over[layer.name]
    except Exception:
        pass

    # Resolve layers with include/exclude and up-to
    def _filter_layers(layers: List[Layer]) -> List[Layer]:
        # determine start index
        start_idx = 0
        if getattr(args, 'from_layer', ''):
            fl = args.from_layer.upper()
            for i, l in enumerate(layers):
                if l.name == fl:
                    start_idx = i
                    break
        up_to_idx = next((i for i, l in enumerate(layers) if l.name == args.up_to), len(layers)-1)
        selected = layers[start_idx: up_to_idx + 1]
        inc = set(x.upper() for x in (args.include_layers or []))
        exc = set(x.upper() for x in (args.exclude_layers or []))
        if inc:
            selected = [l for l in selected if l.name in inc]
        if exc:
            selected = [l for l in selected if l.name not in exc]
        return selected

    to_run = _filter_layers(LAYERS)

    # Pre-check helpers
    def _run_path_precheck() -> Tuple[bool, str]:
        """Run path validator; return (ok, output)."""
        try:

            script_path = SCRIPT_DIR / "validate_documentation_paths.py"
            cmd = [sys.executable, str(script_path), "--root", str(root)]
            if args.precheck_strict:
                cmd.append("--strict")
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            ok = (res.returncode == 0) or (not args.precheck_strict)
            out = (res.stdout or "") + ("\n" + res.stderr if res.stderr else "")
            return ok, out.strip()
        except Exception as e:
            return False, f"precheck failed: {e}"

    # map layer name -> expected extension for existence checks
    ext_map: Dict[str, str] = {l.name: l.ext for l in LAYERS}

    def _find_upstream_file(up_name: str, nn: str) -> Optional[Path]:
        up_dir = root / up_name
        if not up_dir.exists():
            return None
        ext = ext_map.get(up_name, ".md")
        # Try monolithic pattern first
        for p in up_dir.glob(f"{up_name}-{nn}_*{ext}"):
            return p
        # Fallback to any matching NN (including sectional names)
        for p in up_dir.glob(f"{up_name}-{nn}*"):
            return p
        return None

    created_ids: Dict[str, str] = {}
    last_success = True

    # Collect per-layer results for reporting
    results: List[Dict[str, str]] = []
    plan_actions: List[Dict[str, str]] = []

    def _record(action: str, layer_name: str, file_path: Path, note: str = ""):
        plan_actions.append({"action": action, "layer": layer_name, "file": str(file_path), "note": note})

    # Helper: low-friction yaml loader
    def _load_yaml(path: Path) -> dict:
        try:
            import yaml
            return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except Exception:
            return {}

    # Fork mode pre-processing
    def _apply_id_map(text: str, idmap: Dict[str, str]) -> str:
        for k, v in idmap.items():
            text = text.replace(k, v)
        return text

    def _rewrite_for_new_ids(content: str, layer_name: str, old_nn: str, new_nn: str, new_human_slug: str, supersede_note: Optional[str]) -> str:
        content = re.sub(r'(?m)^title:\s*".*"$', f'title: "{layer_name}-{new_nn}: {new_human_slug}"', content)
        if layer_name == "BDD":
            content = re.sub(r'(?m)^Feature:\s*.*$', f'Feature: {layer_name}-{new_nn} — {new_human_slug}', content, count=1)
        else:
            content = re.sub(r'(?m)^#\s+.*$', f'# {layer_name}-{new_nn}: {new_human_slug}', content, count=1)
        for prefix in ["BRD","PRD","EARS","BDD","ADR","SYS","REQ","SPEC","TASKS"]:
            content = content.replace(f"{prefix}-{old_nn}", f"{prefix}-{new_nn}")
        content = content.replace(f".{old_nn}.", f".{new_nn}.")
        if supersede_note:
            insert_at = 0
            if content.startswith("---\n"):
                m = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
                insert_at = m.end() if m else 0
            content = content[:insert_at] + f"\n> Derived from: {supersede_note}\n\n" + content[insert_at:]
        return content

    def _copy_assets_if_needed(src_file: Path, dst_file: Path):
        if not args.copy_assets:
            return
        try:
            txt = src_file.read_text(encoding="utf-8")
        except Exception:
            return
        import re as _re
        rels = _re.findall(r"\(([^)]+)\)", txt)
        for rel in rels:
            if rel.startswith("http") or rel.startswith("/") or rel.startswith("#"):
                continue
            s = (src_file.parent / rel).resolve()
            d = (dst_file.parent / rel).resolve()
            if s.exists():
                d.parent.mkdir(parents=True, exist_ok=True)
                if not args.plan_only and not args.dry_run:
                    try:
                        shutil.copy2(s, d)
                    except Exception:
                        pass

    # If fork specified, create new copies up-front (supports monolithic and sectional files)
    if args.fork_from_nn and args.new_nn and args.new_slug:
        old_nn = args.fork_from_nn
        new_nn = args.new_nn
        new_slug = args.new_slug
        idmap = _load_yaml(Path(args.id_map)) if args.id_map else {}
        human_slug = new_slug.replace("_", " ").title()
        for layer in to_run:
            layer_dir = root / layer.name
            # Find all matching files (monolithic or sectional) recursively
            matches = list(layer_dir.rglob(f"{layer.name}-{old_nn}*{layer.ext}"))
            if not matches:
                continue
            for src in matches:
                rel = src.relative_to(layer_dir)
                # Build destination filename
                src_name = src.name
                # Monolithic pattern: LAYER-OLDNN_{oldslug}.ext
                if src_name.startswith(f"{layer.name}-{old_nn}_"):
                    dst_name = f"{layer.name}-{new_nn}_{new_slug}{layer.ext}"
                else:
                    # Sectional: replace the NN only, keep the rest (e.g., BRD-01.0_index.md -> BRD-02.0_index.md)
                    dst_name = src_name.replace(f"{layer.name}-{old_nn}", f"{layer.name}-{new_nn}")
                dst = (layer_dir / rel.parent / dst_name).resolve()
                if dst.exists() and args.no_overwrite:
                    _record("skip-exists", layer.name, dst, "no-overwrite fork")
                    continue
                try:
                    raw = src.read_text(encoding="utf-8")
                except Exception:
                    _record("error", layer.name, src, "read failed")
                    continue
                newc = _rewrite_for_new_ids(raw, layer.name, old_nn, new_nn, human_slug, supersede_note=f"{layer.name}-{old_nn}" if args.supersede else None)
                if idmap:
                    newc = _apply_id_map(newc, idmap)
                _record("fork", layer.name, dst, f"from {src.name}")
                _copy_assets_if_needed(src, dst)
                if not args.plan_only and not args.dry_run:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    dst.write_text(newc, encoding="utf-8")
            # track new id for this layer
            created_ids[layer.name.lower()] = f"{layer.name}-{new_nn}"

    effective_nn = args.new_nn if (args.fork_from_nn and args.new_nn and args.new_slug) else args.nn
    effective_slug = args.new_slug if (args.fork_from_nn and args.new_nn and args.new_slug) else args.slug

    # Skeleton templates removed; no external or inline skeleton support

    for layer in to_run:
        # Optional pre-checks (paths + upstream presence) before generation
        if not args.no_precheck:
            ok_paths, out_paths = _run_path_precheck()
            if not ok_paths:
                print("⚠️  Pre-Check (paths) reported issues")
                if out_paths:
                    print(out_paths)
                if args.precheck_strict:
                    print("❌ Pre-Check failed in strict mode; aborting")
                    last_success = False
                    break

            # Verify required upstream artifacts exist when not already created in-session
            missing_up: List[str] = []
            for up in (layer.upstream_tags or []):
                if up in created_ids:
                    continue
                up_name = up.upper()
                if not _find_upstream_file(up_name, effective_nn):
                    missing_up.append(up_name)
            if missing_up:
                print(f"⚠️  Pre-Check: missing upstream artifacts for {layer.name}: {', '.join(missing_up)}")
                if args.precheck_strict:
                    print("❌ Pre-Check missing upstream (strict); aborting")
                    last_success = False
                    break

        # Decide target path and whether to generate
        layer_dir = root / layer.name
        slug_eff = effective_slug or (args.intent or layer.name).lower().replace(' ', '_')
        want_filename = f"{layer.name}-{effective_nn}_{slug_eff}{layer.ext}"
        target = layer_dir / want_filename
        must_generate = True

        if args.resume:
            if target.exists():
                must_generate = False
                _record("reuse", layer.name, target, "resume exact")
            else:
                existing = None
                for p in layer_dir.glob(f"{layer.name}-{effective_nn}_*{layer.ext}"):
                    existing = p
                    break
                if existing:
                    target = existing
                    must_generate = False
                    _record("reuse", layer.name, target, "resume any")
        else:
            if target.exists() and args.no_overwrite:
                must_generate = False
                _record("skip-exists", layer.name, target, "no-overwrite")

        if must_generate:
            _record("generate", layer.name, target, "from template")
            if not args.plan_only and not args.dry_run:
                target = generate_from_template(layer, root, effective_nn, args.intent, slug_eff)

        # Track canonical IDs for tags (e.g., brd: BRD-01)
        created_ids.setdefault(layer.name.lower(), f"{layer.name}-{effective_nn}")

        print(f"Generated: {target.relative_to(root.parent) if root.parent in target.parents else target}")

        if args.skip_validate or args.plan_only or args.dry_run:
            results.append({"layer": layer.name, "file": str(target), "status": "planned" if args.plan_only else "generated", "notes": "validation skipped"})
            continue

        # Validate
        ok, msg = run_layer_validation(target, layer.name, strict=args.strict, mvp_validators=args.mvp_validators)
        if ok:
            print(f"✅ {layer.name} validation passed")
            results.append({"layer": layer.name, "file": str(target), "status": "pass", "notes": ""})
        else:
            print(f"❌ {layer.name} validation failed")
            if msg:
                print(msg)

            if args.auto_fix and not args.dry_run:
                # Minimal fix attempt: ensure upstream tags are present
                try_minimal_autofix(target, layer, created_ids)
                # Re-run validation once after fix
                ok2, msg2 = run_layer_validation(target, layer.name, strict=args.strict, mvp_validators=args.mvp_validators)
                if ok2:
                    print(f"🩹 {layer.name} auto-fix succeeded")
                    results.append({"layer": layer.name, "file": str(target), "status": "fixed", "notes": "auto-fix"})
                else:
                    # Auto-fix did not resolve issues; no skeleton fallback
                    print(f"🩹 {layer.name} auto-fix did not resolve all issues")
                    if msg2:
                        print(msg2)
                    last_success = False
                    results.append({"layer": layer.name, "file": str(target), "status": "fail", "notes": "fix failed"})
            else:
                last_success = False
                results.append({"layer": layer.name, "file": str(target), "status": "fail", "notes": "no auto-fix"})

        if not last_success:
            print(f"Halting at {layer.name} due to validation errors. Use --auto-fix to attempt repairs.")
            break

    # Final cross-link validation when all preceding layers succeeded
    links_result = None
    if (not args.skip_validate) and (not args.plan_only) and last_success:
        # Prefer link validator to ensure cross-doc integrity
        try:
            from validate_all import CROSS_VALIDATORS
            vcfg = CROSS_VALIDATORS.get("LINKS")
            if vcfg is not None:
                result = run_validator(vcfg, root)
                if result.success and result.error_count == 0:
                    print("🔗 Link integrity check passed")
                    links_result = True
                else:
                    print("🔗 Link integrity issues detected")
                    if hasattr(result, 'output') and result.output:
                         print(result.output)
                    elif hasattr(result, 'messages') and result.messages:
                         for m in result.messages:
                              print(f"  - {m}")
                    links_result = False
        except Exception:
            pass

    # Reporting
    if args.report and args.report != "none":
        from datetime import datetime
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = Path(args.report_path).parent if args.report_path else Path("work_plans")
        report_dir.mkdir(parents=True, exist_ok=True)
        if args.report_path:
            out_path = Path(args.report_path)
        else:
            ext = "md" if args.report == "markdown" else ("json" if args.report == "json" else "txt")
            out_path = report_dir / f"mvp_autopilot_report_{ts}.{ext}"

        summary_status = "PASS" if last_success else "FAIL"
        try:
            if args.report == "json":
                import json
                payload = {
                    "summary": {
                        "status": summary_status,
                        "up_to": args.up_to,
                        "strict": args.strict,
                        "links_ok": bool(links_result) if links_result is not None else None,
                    },
                    "results": results,
                    "plan": plan_actions,
                }
                out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            elif args.report == "markdown":
                lines = [
                    f"# MVP Autopilot Report ({summary_status})",
                    "",
                    f"- Up to: `{args.up_to}`",
                    f"- Strict: `{args.strict}`",
                    (f"- Links OK: `{links_result}`" if links_result is not None else "- Links OK: `N/A`"),
                    "",
                    "## Results",
                    "| Layer | Status | File | Notes |",
                    "|-------|--------|------|-------|",
                ]
                for r in results:
                    lines.append(f"| {r['layer']} | {r['status']} | `{r['file']}` | {r['notes']} |")
                if plan_actions:
                    lines.append("")
                    lines.append("## Plan Actions")
                    lines.append("| Action | Layer | File | Note |")
                    lines.append("|--------|-------|------|------|")
                    for a in plan_actions:
                        lines.append(f"| {a['action']} | {a['layer']} | `{a['file']}` | {a['note']} |")
                out_path.write_text("\n".join(lines), encoding="utf-8")
            else:
                lines = [f"MVP Autopilot Report: {summary_status}"]
                for r in results:
                    lines.append(f"- {r['layer']}: {r['status']} -> {r['file']} ({r['notes']})")
                if links_result is not None:
                    lines.append(f"- Links OK: {links_result}")
                out_path.write_text("\n".join(lines), encoding="utf-8")
            print(f"📝 Report written to {out_path}")
        except Exception as e:
            print(f"⚠️  Failed to write report: {e}")

    # Plan-only output file
    if args.plan_only:
        try:
            from datetime import datetime
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            plan_path = Path("work_plans") / f"mvp_plan_{ts}.md"
            plan_lines = [
                f"# MVP Autopilot Plan ({ts})",
                "",
                f"- Resume: `{args.resume}`",
                f"- Fork: `{bool(args.fork_from_nn and args.new_nn and args.new_slug)}`",
                f"- Include layers: `{args.include_layers}`",
                f"- Exclude layers: `{args.exclude_layers}`",
                "",
                "## Actions",
                "| Action | Layer | File | Note |",
                "|--------|-------|------|------|",
            ]
            for a in plan_actions:
                plan_lines.append(f"| {a['action']} | {a['layer']} | `{a['file']}` | {a['note']} |")
            plan_path.write_text("\n".join(plan_lines), encoding="utf-8")
            print(f"📝 Plan written to {plan_path}")
        except Exception as e:
            print(f"⚠️  Failed to write plan: {e}")


if __name__ == "__main__":
    main()
