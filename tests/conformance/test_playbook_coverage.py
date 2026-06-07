"""Every (layer, lens) in REVIEW_CREWS.yaml has a playbook file."""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CREWS = REPO_ROOT / "framework" / "governance" / "REVIEW_CREWS.yaml"
PLAYBOOKS = REPO_ROOT / "framework" / "playbooks"

# Layer numbering matches framework/layers/ directory convention.
LAYER_PREFIX = {
    "BRD": "01_BRD",
    "PRD": "02_PRD",
    "EARS": "03_EARS",
    "BDD": "04_BDD",
    "ADR": "05_ADR",
    "SPEC": "06_SPEC",
    "TDD": "07_TDD",
    "IPLAN": "08_IPLAN",
}


class PlaybookCoverageTests(unittest.TestCase):
    def setUp(self):
        with CREWS.open() as f:
            self.crews = yaml.safe_load(f)

    # SKIP: Phase E will author the 45 playbook files.
    # Remove this decorator (and the skip) once Phase E lands all playbooks
    # under framework/playbooks/{prefix}/{lens}.md.
    @unittest.skip("Phase E will land 45 playbooks — skip until then")
    def test_every_crew_lens_has_a_playbook_file(self):
        missing = []
        for layer_name, crew in self.crews["crews"].items():
            prefix = LAYER_PREFIX[layer_name]
            for lens in crew["review"]:
                expected = PLAYBOOKS / prefix / f"{lens}.md"
                if not expected.is_file():
                    missing.append(str(expected.relative_to(REPO_ROOT)))
        self.assertEqual(
            missing,
            [],
            f"Playbook coverage gap: {len(missing)} missing files.\n"
            + "\n".join(f"  - {p}" for p in missing),
        )


if __name__ == "__main__":
    unittest.main()
