"""Conformance: every platform declares ``FRAMEWORK_SPEC_VERSION``
matching ``framework/VERSION`` (PC1) and uses the bare-SemVer file
shape (D-0009)."""

import re
import unittest

from _spec import (
    framework_version,
    platform_dirs,
    platform_framework_spec_version_file,
    platform_version_file,
)

BARE_SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


class PlatformVersionDeclarationTests(unittest.TestCase):
    def test_every_platform_has_VERSION_file(self):
        for platform in platform_dirs():
            with self.subTest(platform=platform.name):
                f = platform_version_file(platform)
                self.assertTrue(f.is_file(), f"{f} missing")

    def test_every_platform_has_FRAMEWORK_SPEC_VERSION_file(self):
        for platform in platform_dirs():
            with self.subTest(platform=platform.name):
                f = platform_framework_spec_version_file(platform)
                self.assertTrue(f.is_file(), f"{f} missing")

    def test_version_files_are_bare_semver(self):
        for platform in platform_dirs():
            for getter in (platform_version_file, platform_framework_spec_version_file):
                f = getter(platform)
                with self.subTest(platform=platform.name, file=f.name):
                    self.assertTrue(f.is_file(), f"{f} missing")
                    body = f.read_text(encoding="utf-8").strip()
                    self.assertRegex(body, BARE_SEMVER, f"{f}: not bare SemVer")

    def test_FRAMEWORK_SPEC_VERSION_matches_framework_VERSION(self):
        fwk = framework_version()
        for platform in platform_dirs():
            with self.subTest(platform=platform.name):
                f = platform_framework_spec_version_file(platform)
                declared = f.read_text(encoding="utf-8").strip()
                self.assertEqual(
                    declared, fwk,
                    f"{platform.name} declares spec {declared!r}; "
                    f"framework/VERSION is {fwk!r}",
                )
