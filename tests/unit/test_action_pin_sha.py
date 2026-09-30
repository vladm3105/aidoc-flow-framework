"""Unit: first-party action pins are SHAs with version comments.

Regression cover for CHG-25 #811: five workflows pinned
``actions/checkout`` / ``actions/setup-python`` to mutable major tags
(``@v7``) while ``pre-commit.yml`` pins the same actions by SHA, so a
moved or compromised major tag would silently change what CI executes.
Every ``checkout`` / ``setup-python`` pin must be a 40-hex SHA carrying a
version comment in the ``pre-commit.yml`` form
(``uses: actions/checkout@<sha> # vX.Y.Z``).
"""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"

# In scope for #811: the two first-party actions the issue names. Reusable
# canon callers (@ci/vX.Y.Z) and third-party scanners are out of scope.
PINNED_ACTIONS = ("actions/checkout@", "actions/setup-python@")
SHA_PIN = re.compile(r"^actions/(checkout|setup-python)@[0-9a-f]{40}\s+#\s+v\d+\.\d+\.\d+\s*$")


def uses_lines():
    hits = []
    for path in sorted(WORKFLOWS.glob("*.yml")):
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if not stripped.startswith("uses:"):
                continue
            ref = stripped.removeprefix("uses:").strip()
            if ref.startswith(PINNED_ACTIONS):
                hits.append((path.name, lineno, ref))
    return hits


class ActionPinShaTests(unittest.TestCase):
    def test_checkout_and_setup_python_pins_are_sha(self):
        hits = uses_lines()
        self.assertTrue(hits, "no checkout/setup-python pins found at all")
        mutable = [
            f"{name}:{lineno}: {ref}" for name, lineno, ref in hits if not SHA_PIN.match(ref)
        ]
        self.assertFalse(
            mutable,
            "mutable major-tag pins (want SHA pins with version comments "
            "in the pre-commit.yml form):\n" + "\n".join(mutable),
        )


if __name__ == "__main__":
    unittest.main()
