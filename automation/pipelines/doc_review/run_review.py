#!/usr/bin/env python3
"""
run_review.py — Doc Review Pipeline Review Orchestrator (Python)

AI Expert Board Automation Script.
Generates a PERSONA_REVIEW_REPORT acting as a formal framework audit gate.

Usage:
    python run_review.py <target_document.md> [options]

Options:
    --dry-run       Preview actions, don't execute AI logic
    --env-file      Path to .env file (default: auto-detect)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any

import yaml

# Try to import httpx for API calls
try:
    import httpx
except ImportError:
    httpx = None


# =============================================================================
# Logging Helpers
# =============================================================================

BLUE = "\033[0;34m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
CYAN = "\033[0;36m"
RED = "\033[0;31m"
RESET = "\033[0m"


def log_info(msg: str) -> None:
    print(f"{BLUE}[INFO]{RESET}    {msg}")


def log_ok(msg: str) -> None:
    print(f"{GREEN}[OK]{RESET}      {msg}")


def log_warn(msg: str) -> None:
    print(f"{YELLOW}[WARN]{RESET}    {msg}")


def log_error(msg: str) -> None:
    print(f"{RED}[ERROR]{RESET}   {msg}", file=sys.stderr)


def log_step(msg: str) -> None:
    print(f"{CYAN}{msg}{RESET}")


def log_dry(msg: str) -> None:
    print(f"{YELLOW}[DRY-RUN]{RESET} {msg}")


# =============================================================================
# Environment Loading
# =============================================================================

def load_env_file(env_file: Path | None = None) -> None:
    """Load environment variables from .env file."""
    if env_file and env_file.exists():
        _parse_env_file(env_file)
        return

    # Auto-detect .env file
    cwd = Path.cwd()
    for path in [cwd / ".env", cwd.parent / ".env"]:
        if path.exists():
            _parse_env_file(path)
            log_info(f"Loaded environment from {path}")
            return


def _parse_env_file(path: Path) -> None:
    """Parse .env file and set environment variables."""
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ[key] = value


# =============================================================================
# AI Execution
# =============================================================================

def run_ai_agent(
    prompt_file: Path,
    engine: str,
    cmd: str | None = None,
    model: str = "gpt-4o",
    temperature: float = 0.3,
    max_tokens: int | None = None,
    api_base: str = "https://api.openai.com/v1",
    api_key_env: str = "OPENAI_API_KEY",
    timeout: int = 300,
    system_prompt_file: Path | None = None,
) -> str:
    """Execute AI agent with given configuration."""
    if engine == "cmd":
        return _run_cmd_engine(prompt_file, cmd, timeout, system_prompt_file)
    else:
        return _run_litellm_engine(
            prompt_file, model, api_base, api_key_env,
            temperature, max_tokens, timeout, system_prompt_file
        )


def _run_cmd_engine(
    prompt_file: Path,
    cmd: str | None,
    timeout: int,
    system_prompt_file: Path | None = None,
) -> str:
    """Execute CLI command with prompt piped to stdin."""
    if not cmd:
        raise ValueError("engine=cmd requires cmd parameter")

    # Build full prompt
    prompt_parts = []
    if system_prompt_file and system_prompt_file.exists():
        prompt_parts.append(system_prompt_file.read_text(encoding="utf-8"))
        prompt_parts.append("\n\n--- PERSONA INSTRUCTIONS ---\n\n")
    prompt_parts.append(prompt_file.read_text(encoding="utf-8"))
    prompt_content = "".join(prompt_parts)

    # Execute command
    result = subprocess.run(
        cmd,
        shell=True,
        input=prompt_content,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=os.environ,
    )

    if result.returncode != 0:
        log_error(f"Command failed: {result.stderr}")
        raise RuntimeError(f"Command failed with exit code {result.returncode}")

    return result.stdout


def _run_litellm_engine(
    prompt_file: Path,
    model: str,
    api_base: str,
    api_key_env: str,
    temperature: float,
    max_tokens: int | None,
    timeout: int,
    system_prompt_file: Path | None = None,
) -> str:
    """Call OpenAI-compatible API directly."""
    api_key = os.environ.get(api_key_env, "")
    if not api_key:
        raise ValueError(f"Environment variable '{api_key_env}' is not set")

    # Build messages
    messages = []
    if system_prompt_file and system_prompt_file.exists():
        messages.append({
            "role": "system",
            "content": system_prompt_file.read_text(encoding="utf-8")
        })
    messages.append({
        "role": "user",
        "content": prompt_file.read_text(encoding="utf-8")
    })

    # Build payload
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    if max_tokens:
        payload["max_tokens"] = max_tokens

    # Make request
    url = f"{api_base.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    if httpx:
        with httpx.Client(timeout=timeout) as client:
            response = client.post(url, headers=headers, json=payload)
            if response.status_code != 200:
                raise RuntimeError(f"API returned HTTP {response.status_code}: {response.text}")
            return response.json()["choices"][0]["message"]["content"]
    else:
        import urllib.request
        import urllib.error

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"API returned HTTP {e.code}: {e.read().decode()}")


# =============================================================================
# Document Processing
# =============================================================================

def extract_frontmatter(file_path: Path) -> dict[str, str]:
    """Extract YAML frontmatter metadata from markdown file."""
    content = file_path.read_text(encoding="utf-8")
    result = {"doc_id": "", "version": "UNKNOWN", "artifact_type": ""}

    for key in result:
        match = re.search(rf"^{key}:\s*(.+)$", content, re.MULTILINE)
        if match:
            result[key] = match.group(1).strip()

    return result


def find_experts_yaml(target_dir: Path, artifact_type: str, git_root: Path | None) -> Path:
    """Locate review.yaml configuration file."""
    # Search order
    candidates = []

    if artifact_type:
        candidates.append(target_dir / f"review.{artifact_type.lower()}.yaml")
        if git_root:
            candidates.append(git_root / "docs" / "AI_EXPERTS" / f"review.{artifact_type.lower()}.yaml")

    candidates.append(target_dir / "review.yaml")
    if git_root:
        candidates.append(git_root / "docs" / "AI_EXPERTS" / "review.yaml")

    # Framework fallback
    candidates.append(Path("/opt/data/docs_flow_framework/ai_dev_ssd_flow/AI_EXPERTS/review.template.yaml"))

    for candidate in candidates:
        if candidate.exists():
            return candidate

    raise FileNotFoundError("No review.yaml found")


def get_git_root() -> Path | None:
    """Get git repository root directory."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except Exception:
        pass
    return None


def build_shared_context(target_file: Path, target_dir: Path) -> str:
    """Build shared document context for all personas."""
    parts = ["=== SHARED DOCUMENT CONTEXT ===\n"]

    # Find creation rules/templates
    parent_dir = target_dir.parent
    for pattern in ["*_CREATION_RULES.md", "*_TEMPLATE.md"]:
        for f in parent_dir.glob(pattern):
            parts.append("=== DOCUMENT CREATION RULES / TEMPLATE START ===\n")
            parts.append(f.read_text(encoding="utf-8"))
            parts.append("\n=== DOCUMENT CREATION RULES / TEMPLATE END ===\n\n")
            break

    parts.append("=== TARGET DOCUMENT START ===\n")

    # Extract linked files
    content = target_file.read_text(encoding="utf-8")
    linked_files = set(re.findall(r'\]\(([^)]+\.md)\)', content))
    linked_files = {f for f in linked_files if not f.startswith("http") and "/" not in f}

    if linked_files:
        # Sectioned layout - add index first
        parts.append(f"--- FILE: {target_file.name} ---\n")
        parts.append(content)
        parts.append("\n")

        # Add linked files
        for linked_file in sorted(linked_files):
            local_path = target_dir / linked_file
            if local_path.exists() and local_path != target_file:
                parts.append(f"--- FILE: {linked_file} ---\n")
                parts.append(local_path.read_text(encoding="utf-8"))
                parts.append("\n")
    else:
        # Monolithic layout
        parts.append(f"--- FILE: {target_file.name} ---\n")
        parts.append(content)
        parts.append("\n")

    parts.append("=== TARGET DOCUMENT END ===\n")
    return "".join(parts)


def find_skill_file(persona: str, git_root: Path | None) -> Path | None:
    """Find domain knowledge skill file for persona."""
    candidates = []
    if git_root:
        candidates.append(git_root / "docs" / "AI_EXPERTS" / "skills" / f"{persona}.md")
    candidates.append(Path(f"/opt/data/docs_flow_framework/ai_dev_ssd_flow/AI_EXPERTS/skills/{persona}.md"))

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


# =============================================================================
# Agent Extraction
# =============================================================================

def extract_agent_config(config: dict, key: str) -> dict[str, Any]:
    """Extract agent configuration from YAML."""
    if key == "chairperson":
        data = config.get("chairperson", {})
    elif key == "judge":
        data = config.get("judge", {})
    elif key == "editor":
        data = config.get("editor", {})
    else:
        data = config.get("personas", {}).get(key, {})

    agent = data.get("agent", {})
    return {
        "name": data.get("name", ""),
        "prompt": data.get("prompt", ""),
        "skill_file": data.get("skill_file"),
        "engine": agent.get("engine", "litellm"),
        "cmd": agent.get("cmd"),
        "model": agent.get("model", "gpt-4o"),
        "temperature": float(agent.get("temperature", 0.3)),
        "max_tokens": agent.get("max_tokens"),
        "api_base": agent.get("api_base", "https://api.openai.com/v1"),
        "api_key_env": agent.get("api_key_env", "OPENAI_API_KEY"),
    }


# =============================================================================
# Main Pipeline
# =============================================================================

def run_pipeline(target_file: Path, dry_run: bool = False) -> None:
    """Run the document review pipeline."""
    target_dir = target_file.parent
    target_basename = target_file.stem
    current_date_str = date.today().isoformat()

    # Extract metadata
    metadata = extract_frontmatter(target_file)
    doc_id = metadata["doc_id"] or target_basename
    version = metadata["version"]
    artifact_type = metadata["artifact_type"]

    # Find git root
    git_root = get_git_root()

    # Find experts YAML
    experts_yaml = find_experts_yaml(target_dir, artifact_type, git_root)
    log_info(f"Using experts config: {experts_yaml}")

    # Load config
    with open(experts_yaml, "r") as f:
        config = yaml.safe_load(f)

    # Get personas
    personas = list(config.get("personas", {}).keys())
    log_info(f"Loaded {len(personas)} personas: {', '.join(personas)}")

    # Setup workspace
    run_dir = target_dir / ".doc_review_memory"
    run_dir.mkdir(exist_ok=True)

    # Clear previous artifacts
    for pattern in ["prompt_*.txt", "response_*.txt", "shared_context.txt", "final_body.md"]:
        for f in run_dir.glob(pattern):
            f.unlink()

    # Header
    print()
    print("=" * 60)
    print("  DOC REVIEW PIPELINE — AI Board Review")
    print("=" * 60)
    print(f"  Target:     {target_file}")
    print(f"  Document:   {doc_id}")
    print(f"  Dry run:    {dry_run}")
    print("=" * 60)
    print()

    # Build shared context
    shared_context_file = run_dir / "shared_context.txt"
    shared_context = build_shared_context(target_file, target_dir)
    shared_context_file.write_text(shared_context, encoding="utf-8")

    # Template file
    template_file = Path("/opt/data/docs_flow_framework/ai_dev_ssd_flow/AI_EXPERTS/PERSONA_REVIEW-MVP-TEMPLATE.md")

    # ==========================================================================
    # Step 1: Persona Reviews
    # ==========================================================================
    log_step("Step 1 / 5 — Phase 2 Blind Audits")

    for persona in personas:
        log_info(f"Summoning {persona}...")

        agent_cfg = extract_agent_config(config, persona)
        prompt_file = run_dir / f"prompt_{persona}.txt"
        response_file = run_dir / f"response_{persona}.txt"

        # Build prompt
        prompt_parts = []

        # Domain knowledge
        skill_file = find_skill_file(persona, git_root)
        if skill_file:
            prompt_parts.append("=== YOUR DOMAIN KNOWLEDGE ===\n")
            prompt_parts.append(skill_file.read_text(encoding="utf-8"))
            prompt_parts.append("\n=== END DOMAIN KNOWLEDGE ===\n\n")

        # Previous findings
        prev_responses = list(run_dir.glob("response_*.txt"))
        if prev_responses:
            prompt_parts.append("=== PREVIOUS EXPERT FINDINGS ===\n")
            prompt_parts.append("The following are findings from other experts:\n")
            for prev in sorted(prev_responses):
                prev_name = prev.stem.replace("response_", "")
                prompt_parts.append(f"--- Report from {prev_name} ---\n")
                prompt_parts.append(prev.read_text(encoding="utf-8"))
                prompt_parts.append("\n")
            prompt_parts.append("=== END PREVIOUS EXPERT FINDINGS ===\n\n")

        # Expert instructions
        prompt_parts.append("==============\nEXPERT INSTRUCTIONS:\n")
        prompt_parts.append(f"You are {agent_cfg['name']}.\n")
        prompt_parts.append(agent_cfg['prompt'])

        prompt_file.write_text("".join(prompt_parts), encoding="utf-8")

        if dry_run:
            log_dry(f"Would call {persona} with engine={agent_cfg['engine']}")
            response_file.write_text(f"Dry run output for {persona}: [Mocked response]")
        else:
            # Expand environment variables in cmd
            cmd = agent_cfg.get("cmd")
            if cmd:
                cmd = os.path.expandvars(cmd.replace("$P_MODEL", agent_cfg["model"]))

            response = run_ai_agent(
                prompt_file=prompt_file,
                engine=agent_cfg["engine"],
                cmd=cmd,
                model=agent_cfg["model"],
                temperature=agent_cfg["temperature"],
                max_tokens=agent_cfg.get("max_tokens"),
                api_base=agent_cfg["api_base"],
                api_key_env=agent_cfg["api_key_env"],
                timeout=300,
                system_prompt_file=shared_context_file,
            )
            response_file.write_text(response, encoding="utf-8")
            log_ok(f"{persona} completed review.")

    # ==========================================================================
    # Step 2: Chairperson Synthesis
    # ==========================================================================
    log_step("Step 2 / 5 — Summarizing via Chairperson")

    chair_cfg = extract_agent_config(config, "chairperson")
    chair_prompt_file = run_dir / "prompt_chairperson.txt"
    chair_response_file = run_dir / "final_body.md"

    # Build chairperson prompt
    chair_parts = []
    chair_parts.append(f"{chair_cfg['prompt']}\n\n")
    chair_parts.append(f"Read the following {len(personas)} expert reports regarding document {doc_id}.\n\n")

    chair_parts.append("=== EXPERT REPORTS ===\n")
    for persona in personas:
        resp_file = run_dir / f"response_{persona}.txt"
        chair_parts.append(f"--- Report from {persona} ---\n")
        if resp_file.exists():
            chair_parts.append(resp_file.read_text(encoding="utf-8"))
        else:
            chair_parts.append("[No response]")
        chair_parts.append("\n")
    chair_parts.append("=== END EXPERT REPORTS ===\n\n")

    if template_file.exists():
        chair_parts.append("=== TEMPLATE FORMAT TO FOLLOW ===\n")
        chair_parts.append(template_file.read_text(encoding="utf-8"))
        chair_parts.append("\n=== END TEMPLATE FORMAT ===\n\n")

    chair_parts.append(f"""=== REQUIRED OUTPUT STRUCTURE (Follow exactly) ===
# Expert Board Audit Report: {doc_id}

> **Target Document**: {doc_id} (Version {version})
> **Audit Date**: {current_date_str}
> **Board Configuration**: review.yaml

## 1. Executive Summary
*   **Consensus Recommendation**: (Proceed / Remediation Required / Fundamental Redesign)
*   *Chairperson's Synthesis*: [Your synthesized paragraph]

[... Fill out Sections 2 through 6 based on the template requirements]
""")

    chair_prompt_file.write_text("".join(chair_parts), encoding="utf-8")

    if dry_run:
        log_dry("Would call Chairperson")
        chair_response_file.write_text(f"# Expert Board Audit Report: {doc_id}\nDry run output")
    else:
        log_info("Summoning chairperson...")
        cmd = chair_cfg.get("cmd")
        if cmd:
            cmd = os.path.expandvars(cmd.replace("$P_MODEL", chair_cfg["model"]))

        response = run_ai_agent(
            prompt_file=chair_prompt_file,
            engine=chair_cfg["engine"],
            cmd=cmd,
            model=chair_cfg["model"],
            temperature=chair_cfg["temperature"],
            max_tokens=chair_cfg.get("max_tokens"),
            api_base=chair_cfg["api_base"],
            api_key_env=chair_cfg["api_key_env"],
            timeout=300,
            system_prompt_file=shared_context_file,
        )
        chair_response_file.write_text(response, encoding="utf-8")
        log_ok("Chairperson synthesis complete.")

    # ==========================================================================
    # Step 3: Judge Validation
    # ==========================================================================
    log_step("Step 3 / 5 — Judge validation of synthesis")

    judge_cfg = extract_agent_config(config, "judge")

    if judge_cfg["name"]:
        judge_prompt_file = run_dir / "prompt_judge.txt"
        judge_response_file = run_dir / "response_judge.txt"

        # Build judge prompt
        judge_parts = []
        judge_parts.append(f"{judge_cfg['prompt']}\n\n")

        judge_parts.append("=== RAW EXPERT REPORTS ===\n")
        for persona in personas:
            resp_file = run_dir / f"response_{persona}.txt"
            judge_parts.append(f"--- Report from {persona} ---\n")
            if resp_file.exists():
                judge_parts.append(resp_file.read_text(encoding="utf-8"))
            else:
                judge_parts.append("[No response]")
            judge_parts.append("\n")
        judge_parts.append("=== END RAW EXPERT REPORTS ===\n\n")

        judge_parts.append("=== CHAIRPERSON'S SYNTHESIS ===\n")
        judge_parts.append(chair_response_file.read_text(encoding="utf-8"))
        judge_parts.append("\n=== END CHAIRPERSON'S SYNTHESIS ===\n\n")

        judge_parts.append("Validate the synthesis against the raw expert reports and provide your verdict.")

        judge_prompt_file.write_text("".join(judge_parts), encoding="utf-8")

        if dry_run:
            log_dry("Would call Judge")
            judge_response_file.write_text("Verdict: PASS (dry run)")
        else:
            log_info("Summoning judge...")
            cmd = judge_cfg.get("cmd")
            if cmd:
                cmd = os.path.expandvars(cmd.replace("$P_MODEL", judge_cfg["model"]))

            response = run_ai_agent(
                prompt_file=judge_prompt_file,
                engine=judge_cfg["engine"],
                cmd=cmd,
                model=judge_cfg["model"],
                temperature=judge_cfg["temperature"],
                max_tokens=judge_cfg.get("max_tokens"),
                api_base=judge_cfg["api_base"],
                api_key_env=judge_cfg["api_key_env"],
                timeout=300,
                system_prompt_file=shared_context_file,
            )
            judge_response_file.write_text(response, encoding="utf-8")
            log_ok("Judge validation complete.")

        # Check if revision needed
        judge_content = judge_response_file.read_text(encoding="utf-8")
        if "REVISION_REQUIRED" in judge_content.upper():
            # ==========================================================================
            # Step 4: Editor Fixes
            # ==========================================================================
            log_step("Step 4 / 5 — Editor applying fixes from Judge")

            editor_cfg = extract_agent_config(config, "editor")
            editor_prompt_file = run_dir / "prompt_editor.txt"
            editor_response_file = run_dir / "response_editor.txt"

            editor_parts = []
            editor_parts.append(f"{editor_cfg['prompt']}\n\n")

            editor_parts.append("=== ORIGINAL CHAIRPERSON SYNTHESIS ===\n")
            editor_parts.append(chair_response_file.read_text(encoding="utf-8"))
            editor_parts.append("\n=== END ORIGINAL SYNTHESIS ===\n\n")

            editor_parts.append("=== JUDGE'S CRITIQUE ===\n")
            editor_parts.append(judge_content)
            editor_parts.append("\n=== END JUDGE'S CRITIQUE ===\n\n")

            editor_parts.append("=== RAW EXPERT REPORTS (for reference) ===\n")
            for persona in personas:
                resp_file = run_dir / f"response_{persona}.txt"
                editor_parts.append(f"--- Report from {persona} ---\n")
                if resp_file.exists():
                    editor_parts.append(resp_file.read_text(encoding="utf-8"))
                editor_parts.append("\n")
            editor_parts.append("=== END RAW EXPERT REPORTS ===\n\n")

            editor_parts.append("Apply all fixes and output the COMPLETE corrected PERSONA_REVIEW_REPORT.")

            editor_prompt_file.write_text("".join(editor_parts), encoding="utf-8")

            if dry_run:
                log_dry("Would call Editor")
                editor_response_file.write_text(chair_response_file.read_text(encoding="utf-8"))
            else:
                log_info("Summoning editor...")
                cmd = editor_cfg.get("cmd")
                if cmd:
                    cmd = os.path.expandvars(cmd.replace("$P_MODEL", editor_cfg["model"]))

                response = run_ai_agent(
                    prompt_file=editor_prompt_file,
                    engine=editor_cfg["engine"],
                    cmd=cmd,
                    model=editor_cfg["model"],
                    temperature=editor_cfg["temperature"],
                    max_tokens=editor_cfg.get("max_tokens"),
                    api_base=editor_cfg["api_base"],
                    api_key_env=editor_cfg["api_key_env"],
                    timeout=300,
                    system_prompt_file=None,  # Editor doesn't need doc context
                )
                editor_response_file.write_text(response, encoding="utf-8")
                log_ok("Editor fixes applied.")

            # Use editor output as final
            chair_response_file = editor_response_file
        else:
            log_ok("Judge verdict: PASS — no revision needed.")
    else:
        log_warn("No judge configured in YAML — skipping validation step.")

    # ==========================================================================
    # Step 5: Assemble Final Report
    # ==========================================================================
    log_step("Step 5 / 5 — Assembling final audit report")

    output_file = target_dir / f"{doc_id}_PERSONA_REVIEW_REPORT.md"

    if dry_run:
        log_dry(f"Would assemble {output_file}")
    else:
        # Build frontmatter from template
        if template_file.exists():
            template_content = template_file.read_text(encoding="utf-8")
            # Extract frontmatter
            fm_match = re.match(r'^---\n(.*?)\n---', template_content, re.DOTALL)
            if fm_match:
                frontmatter = fm_match.group(0)
                frontmatter = frontmatter.replace("{NN}", re.sub(r'[^0-9]', '', doc_id))
                frontmatter = frontmatter.replace("{TARGET_DOC_ID}", doc_id)
                frontmatter = frontmatter.replace("{TARGET_DOC_VERSION}", version)
                frontmatter = frontmatter.replace("{PASS_OR_FAIL}", "PENDING_REVIEW")
                frontmatter = frontmatter.replace("{CURRENT_DATE}", current_date_str)
            else:
                frontmatter = f"---\ndoc_id: EXPERTS-{doc_id}\nversion: 1.0.0\n---\n"
        else:
            frontmatter = f"---\ndoc_id: EXPERTS-{doc_id}\nversion: 1.0.0\n---\n"

        # Combine frontmatter + body
        final_content = frontmatter + "\n" + chair_response_file.read_text(encoding="utf-8")
        output_file.write_text(final_content, encoding="utf-8")

        print()
        log_ok("EXPERTS Audit Report generated at:")
        print(f"  {output_file}")
        print()
        log_info("Next steps: To apply remediation or create tasks, run:")
        print(f"  python run_remediate.py {output_file} --target-doc {target_file}")

    print()
    print("=" * 60)
    print("  DOC REVIEW PIPELINE REVIEW — Complete")
    print("=" * 60)


# =============================================================================
# Entry Point
# =============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(description="Doc Review Pipeline")
    parser.add_argument("target_file", type=Path, help="Target document to review")
    parser.add_argument("--dry-run", action="store_true", help="Preview without executing")
    parser.add_argument("--env-file", type=Path, help="Path to .env file")

    args = parser.parse_args()

    if not args.target_file.exists():
        log_error(f"Target file not found: {args.target_file}")
        sys.exit(1)

    # Load environment
    load_env_file(args.env_file)

    # Run pipeline
    try:
        run_pipeline(args.target_file, args.dry_run)
    except Exception as e:
        log_error(f"Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
