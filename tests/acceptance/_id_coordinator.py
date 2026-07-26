"""Compute deterministic element IDs for fixture artifacts.

Element ID format: TYPE.NN.SS.xxxx where xxxx is the first 4 hex chars of the
canonical element hash — ``sdd_doc_lint.compute_element_hash()``, which applies
the normative ID_NAMING_STANDARDS transform to ``title`` and ``description``
before hashing. This module MUST NOT re-derive that hash; it delegates, and
``deterministic/test_id_coordinator.py`` asserts the delegation holds
(IDCOORD-SECOND-HASH-IMPL, #351).
"""

import re
import sys
from pathlib import Path

import yaml

# Module scope, not inside extract_elements(): element_hash() is called on its
# own by the parity test, which would ImportError if the path insert only ran
# on the extract_elements() code path. (This makes tools/ *available* on the
# path; it does not by itself decide which copy wins — a combined run that
# already imported a vendored platforms/*/sdd_doc_lint keeps that one in
# sys.modules. Harmless: test_doc_lint_vendoring.py holds all three copies
# byte-identical.)
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from sdd_doc_lint import _normalise_heading, compute_element_hash


def element_hash(doc_id: str, section_id: str, title: str, description: str) -> str:
    """Return the canonical element hash, truncated to the 4-char standard form.

    ``compute_element_hash()`` returns the full 64-char digest and leaves the
    slice to its caller by design — 4 chars for the standard form, 8 for the
    collision form. This helper is hard-wired to 4: fixture IDs have no
    collision-escape path, which is acceptable only because the module has no
    product consumer.
    """
    return compute_element_hash(doc_id, section_id, title, description)[:4]


def element_id(doc_type: str, doc_num: int, section_id: str, title: str, description: str) -> str:
    """Return a fixture-local element identifier — NOT a spec-conformant element ID.

    ``section_id`` is a normalised heading string (``"project_scope"``), because
    that is all ``extract_elements()`` can derive from an artifact's headings.
    The spec's element form is ``{TYPE}.{doc_id}.{section_id}.{hash}`` with a
    two-digit NUMERIC section, and the registry pattern
    ``^[A-Z]+\\.\\d{2,}\\.\\d{2,}\\.[a-f0-9]{4,8}$``
    (``framework/registry/LAYER_REGISTRY.yaml``) therefore rejects what this
    returns. Deliberate: mapping heading → section ordinal would require a
    per-layer table that does not exist anywhere in the repo, and inventing one
    is a new contract, not a fixture helper's job (plan D3 option c; the
    numeric form is tracked as a deferred TODO).

    The **hash** is canonical regardless — only the ``section_id`` segment is
    fixture-local.
    """
    doc_id = f"{doc_type}-{doc_num:02d}"
    return f"{doc_type}.{doc_num:02d}.{section_id}.{element_hash(doc_id, section_id, title, description)}"


def extract_elements(artifact: Path) -> list[dict]:
    """Walk an artifact and return [{section_id, title, description, element_id}, ...]."""
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
        # safe_load_all, not safe_load: YAML goldens may carry a `---`-fenced
        # frontmatter block ahead of the body, i.e. two YAML documents, which
        # safe_load rejects with ComposerError. Take the LAST dict document —
        # the body — rather than merging the two key sets. A key-union would
        # promote frontmatter keys into the section namespace, diverging from
        # _harness.headings(), which strips frontmatter outright. No frontmatter
        # in the corpus today would actually mint an element either way (`doc_id`
        # is scalar, `metadata` is filtered by name, and `reuse:` is a flat dict
        # of scalars) — a frontmatter key mapping to a mapping-of-mappings would,
        # and test_frontmatter_keys_are_not_walked_as_sections pins that.
        data: dict = {}
        for document in yaml.safe_load_all(text):
            if isinstance(document, dict):
                data = document
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
