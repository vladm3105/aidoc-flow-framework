"""Conformance: the ``framework/`` root holds exactly the expected docs."""

import unittest

from _spec import FRAMEWORK

EXPECTED_ROOT_FILES = {
    "README.md",
    "VERSION",
    "SPEC_DRIVEN_DEVELOPMENT_GUIDE.md",
    "QUICK_REFERENCE.md",
    "AI_ASSISTANT_RULES.md",
    "TESTING_STRATEGY_TDD.md",
}


class FrameworkRoot(unittest.TestCase):
    def test_root_files_match_expected(self):
        found = {p.name for p in FRAMEWORK.iterdir() if p.is_file()}
        self.assertEqual(found, EXPECTED_ROOT_FILES)


if __name__ == "__main__":
    unittest.main()
