"""Conformance: ``framework/VERSION`` is present and a valid SemVer string."""

import re
import unittest

from _spec import FRAMEWORK

VERSION_PATH = FRAMEWORK / "VERSION"
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


class FrameworkVersion(unittest.TestCase):
    def test_version_file_exists(self):
        self.assertTrue(VERSION_PATH.is_file(), "framework/VERSION is missing")

    def test_version_is_a_single_semver_line(self):
        lines = VERSION_PATH.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 1, "VERSION must hold exactly one line")
        self.assertRegex(
            lines[0], SEMVER, "VERSION must be a bare X.Y.Z SemVer string"
        )


if __name__ == "__main__":
    unittest.main()
