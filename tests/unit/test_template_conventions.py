"""Unit: SDD-chain templates carry uniform, placeholder-only metadata.

Regression cover for CHG-24 #805: EVAL-TEMPLATE shipped schema_version 2.0
against nine 1.0 siblings, a future-dated last_updated, and CHG-TEMPLATE
hardcoded a framework_version literal that rots on every VERSION bump.
"""

import sys
import unittest
from datetime import date
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
LAYERS = REPO_ROOT / "framework" / "layers"
CHG_TWINS = [
    REPO_ROOT / "framework" / "layers" / "09_CHG" / "CHG-TEMPLATE.yaml",
    REPO_ROOT / "framework" / "governance" / "chg" / "CHG-TEMPLATE.yaml",
]


def template_files():
    # The SDD document chain only: governance families (e.g. PROFILE-TEMPLATE
    # with its own 1.0.0 profile-schema line) version independently and are
    # out of scope (CHG-24 #805).
    layer_templates = sorted(LAYERS.rglob("*TEMPLATE*.yaml"))
    return layer_templates + [p for p in CHG_TWINS if p not in layer_templates]


def load(path):
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def walk(node, path=()):
    if isinstance(node, dict):
        for key, value in node.items():
            yield from walk(value, path + (key,))
    elif isinstance(node, list):
        for value in node:
            yield from walk(value, path)
    else:
        yield path, node


class TemplateConventionTests(unittest.TestCase):
    def test_schema_version_uniform_1_0(self):
        seen = {}
        for path in template_files():
            data = load(path) or {}
            meta = data.get("metadata", {}) if isinstance(data, dict) else {}
            if isinstance(meta, dict) and "schema_version" in meta:
                seen.setdefault(str(meta["schema_version"]), []).append(
                    path.relative_to(REPO_ROOT).as_posix()
                )
        self.assertTrue(seen, "no template declares schema_version")
        self.assertEqual(
            set(seen),
            {"1.0"},
            f"schema_version drift (want uniform 1.0): {seen}",
        )

    def test_framework_version_is_placeholder(self):
        offenders = []
        for path in template_files():
            for keys, value in walk(load(path)):
                if keys and keys[-1] == "framework_version" and isinstance(value, str):
                    if value.strip() != "[X.Y.Z]":
                        offenders.append(
                            f"{path.relative_to(REPO_ROOT)}: {value!r}"
                        )
        self.assertFalse(
            offenders,
            f"hardcoded framework_version literals (want [X.Y.Z]): {offenders}",
        )

    def test_no_future_dates(self):
        today = date.today().isoformat()
        offenders = []
        for path in template_files():
            for keys, value in walk(load(path)):
                if (
                    keys
                    and keys[-1] in ("last_updated", "date_created", "date")
                    and isinstance(value, str)
                ):
                    day = value.strip()[:10]
                    if len(day) == 10 and day[0].isdigit():
                        try:
                            is_future = day > today
                        except TypeError:
                            continue
                        if is_future:
                            offenders.append(
                                f"{path.relative_to(REPO_ROOT)}:{keys[-1]}={value!r}"
                            )
        self.assertFalse(offenders, f"future dates in templates: {offenders}")


if __name__ == "__main__":
    unittest.main()
