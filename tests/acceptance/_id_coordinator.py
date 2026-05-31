"""Compute deterministic element IDs for fixture artifacts.

Element ID format: TYPE.NN.SS.xxxx where xxxx = first 4 hex of
SHA256("{doc_id}:{section_id}:{title}:{description}").
"""

import hashlib
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "conformance"))


def element_hash(doc_id: str, section_id: str, title: str, description: str) -> str:
    key = f"{doc_id}:{section_id}:{title}:{description}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:4]


def element_id(doc_type: str, doc_num: int, section_id: str, title: str, description: str) -> str:
    doc_id = f"{doc_type}-{doc_num:02d}"
    return f"{doc_type}.{doc_num:02d}.{section_id}.{element_hash(doc_id, section_id, title, description)}"


def extract_elements(artifact: Path) -> list[dict]:
    """Walk an artifact and return [{section_id, title, description, element_id}, ...]."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
    from sdd_doc_lint import _normalise_heading

    text = artifact.read_text(encoding="utf-8")
    artifact_id_match = re.search(r"^\s*artifact_id:\s*([A-Z]+-\d+)", text, re.MULTILINE)
    if not artifact_id_match:
        return []
    doc_type, doc_num_str = artifact_id_match.group(1).split("-", 1)
    doc_num = int(doc_num_str)

    out: list[dict] = []
    if artifact.suffix == ".md":
        lines = text.splitlines()
        current_section: str | None = None
        for i, line in enumerate(lines):
            if line.startswith("## "):
                current_section = _normalise_heading(line.lstrip("# ").strip())
            elif line.startswith("### ") and current_section:
                title = line.lstrip("# ").strip()
                description = ""
                for follow in lines[i + 1 :]:
                    s = follow.strip()
                    if not s:
                        continue
                    if s.startswith("#"):
                        break
                    description = s
                    break
                out.append(
                    {
                        "section_id": current_section,
                        "title": title,
                        "description": description,
                        "element_id": element_id(
                            doc_type, doc_num, current_section, title, description
                        ),
                    }
                )
    elif artifact.suffix == ".yaml":
        data = yaml.safe_load(text) or {}
        for section_key, section in data.items():
            if section_key.startswith("_") or section_key == "metadata":
                continue
            if isinstance(section, dict):
                for elem_key, elem in section.items():
                    if not isinstance(elem, dict):
                        continue
                    title = str(elem.get("title") or elem.get("name") or elem_key)
                    description = str(elem.get("description") or elem.get("desc") or "")
                    out.append(
                        {
                            "section_id": section_key,
                            "title": title,
                            "description": description,
                            "element_id": element_id(
                                doc_type, doc_num, section_key, title, description
                            ),
                        }
                    )
            elif isinstance(section, list):
                for item in section:
                    if not isinstance(item, dict):
                        continue
                    title = str(item.get("title") or item.get("name") or "")
                    description = str(item.get("description") or item.get("desc") or "")
                    if not title:
                        continue
                    out.append(
                        {
                            "section_id": section_key,
                            "title": title,
                            "description": description,
                            "element_id": element_id(
                                doc_type, doc_num, section_key, title, description
                            ),
                        }
                    )
    return out


def write_registry(registry_path: Path, layer_key: str, elements: list[dict]) -> None:
    data: dict = {}
    if registry_path.exists():
        loaded = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            data = loaded
    data[layer_key] = elements
    registry_path.write_text(yaml.safe_dump(data, sort_keys=True), encoding="utf-8")
