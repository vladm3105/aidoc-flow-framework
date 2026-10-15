"""Tests for compute_reviewed_sha256 and review_log cryptographic verification."""

import unittest
from sdd_doc_lint import compute_reviewed_sha256, lint_text
import re

class TestReviewedSha256(unittest.TestCase):
    def test_compute_reviewed_sha256_strips_frontmatter_and_normalizes(self):
        doc1 = """---
id: SPEC-01
review_log: []
---
# Title

This is the specification body.
"""
        doc2 = """---
id: SPEC-01
other_meta: value
---
# Title\r\n\r\nThis is the specification body.\r\n
"""
        sha1 = compute_reviewed_sha256(doc1)
        sha2 = compute_reviewed_sha256(doc2)
        self.assertEqual(sha1, sha2, "Different line endings and frontmatters must produce identical SHA-256 for identical bodies")
        self.assertTrue(re.match(r"^[0-9a-f]{64}$", sha1), "SHA-256 must be a 64-character lowercase hex string")

    def test_stale_review_detected(self):
        body = "# Title\n\nOriginal text."
        valid_sha = compute_reviewed_sha256(f"---\nid: SPEC-01\n---\n{body}")
        
        # Tampered body after review
        doc_tampered = f"""---
id: SPEC-01
review_log:
  - pass: 1
    reviewed_sha256: "{valid_sha}"
    verdict: "PASS"
    blocking_remaining: 0
---
# Title

Tampered text.
"""
        doc_re = re.compile(r"^[A-Z]+-[0-9]+$")
        elem_re = re.compile(r"^[A-Z]+\.[0-9]+$")
        layers = {"SPEC": {}}
        findings = lint_text(doc_tampered, "SPEC", "docs/sdd/06_SPEC/SPEC-01.md", layers, doc_re, elem_re)
        stale_findings = [f for f in findings if f.code == "REV01"]
        self.assertEqual(len(stale_findings), 1, "Must detect STALE_REVIEW_DETECTED when body differs from reviewed_sha256")

    def test_valid_review_log_passes(self):
        body = "# Title\n\nVerified text."
        valid_sha = compute_reviewed_sha256(f"---\nid: SPEC-01\n---\n{body}")
        doc_valid = f"""---
id: SPEC-01
review_log:
  - pass: 1
    reviewed_sha256: "{valid_sha}"
    verdict: "PASS"
    blocking_remaining: 0
---
# Title

Verified text.
"""
        doc_re = re.compile(r"^[A-Z]+-[0-9]+$")
        elem_re = re.compile(r"^[A-Z]+\.[0-9]+$")
        layers = {"SPEC": {}}
        findings = lint_text(doc_valid, "SPEC", "docs/sdd/06_SPEC/SPEC-01.md", layers, doc_re, elem_re)
        rev_findings = [f for f in findings if f.code.startswith("REV")]
        self.assertEqual(len(rev_findings), 0, "Valid review_log with matching hash must produce 0 REV findings")


if __name__ == "__main__":
    unittest.main()
