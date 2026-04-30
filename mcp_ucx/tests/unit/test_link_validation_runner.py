"""Tests for link validation runner."""

import json
import tempfile
from pathlib import Path

import pytest

from mcp_server.link_validation import run_link_validation


class TestLinkValidation:
    def test_empty_directory(self, tmp_path):
        result = run_link_validation(target_path=tmp_path)
        assert result.passed is True
        assert result.payload["files_scanned"] == 0
        assert result.payload["broken_count"] == 0

    def test_valid_links(self, tmp_path):
        a = tmp_path / "a.md"
        b = tmp_path / "b.md"
        a.write_text("# Hello\n\n[link to b](b.md)\n")
        b.write_text("# World\n\nContent here.\n")

        result = run_link_validation(target_path=tmp_path)
        assert result.passed is True
        assert result.payload["total_links_checked"] == 1
        assert result.payload["broken_count"] == 0

    def test_broken_file_link(self, tmp_path):
        a = tmp_path / "a.md"
        a.write_text("# Doc\n\n[missing](nonexistent.md)\n")

        result = run_link_validation(target_path=tmp_path)
        assert result.passed is False
        assert result.payload["broken_count"] == 1
        broken = result.payload["broken_links"]
        assert broken[0]["reason"] == "file_not_found"
        assert broken[0]["line_number"] == 3

    def test_broken_anchor_link(self, tmp_path):
        a = tmp_path / "a.md"
        b = tmp_path / "b.md"
        a.write_text("# Doc\n\n[link](b.md#bad-anchor)\n")
        b.write_text("# Real Heading\n\nContent.\n")

        result = run_link_validation(target_path=tmp_path)
        assert result.passed is False
        assert result.payload["broken_count"] == 1
        assert result.payload["broken_links"][0]["reason"] == "anchor_not_found"

    def test_same_file_anchor_broken(self, tmp_path):
        a = tmp_path / "a.md"
        a.write_text("# Title\n\n[jump](#nonexistent)\n")

        result = run_link_validation(target_path=tmp_path)
        assert result.passed is False
        assert result.payload["broken_links"][0]["reason"] == "anchor_not_found"

    def test_same_file_anchor_valid(self, tmp_path):
        a = tmp_path / "a.md"
        a.write_text("# Title\n\n[jump](#title)\n\nMore content.\n")

        result = run_link_validation(target_path=tmp_path)
        assert result.passed is True

    def test_external_links_skipped(self, tmp_path):
        a = tmp_path / "a.md"
        a.write_text("# Doc\n\n[ext](https://example.com)\n[mail](mailto:a@b.com)\n")

        result = run_link_validation(target_path=tmp_path)
        assert result.passed is True
        assert result.payload["total_links_checked"] == 0

    def test_media_links_skipped(self, tmp_path):
        a = tmp_path / "a.md"
        a.write_text("# Doc\n\n![img](photo.png)\n[pdf](doc.pdf)\n")

        result = run_link_validation(target_path=tmp_path)
        assert result.passed is True

    def test_single_file_mode(self, tmp_path):
        a = tmp_path / "a.md"
        b = tmp_path / "b.md"
        a.write_text("# A\n\n[link](b.md)\n")
        b.write_text("# B\n\n[broken](missing.md)\n")

        result = run_link_validation(target_path=a, workspace_root=tmp_path)
        assert result.payload["files_scanned"] == 1
        assert result.passed is True  # only scanned a.md, which has a valid link

    def test_output_dir_writes_artifacts(self, tmp_path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "a.md").write_text("# Doc\n\n[missing](gone.md)\n")

        out = tmp_path / "output"
        result = run_link_validation(target_path=docs, output_dir=out)

        assert result.report_path is not None
        assert result.report_path.exists()
        assert result.summary_path is not None
        assert result.summary_path.exists()

        report = json.loads(result.report_path.read_text())
        assert report["broken_count"] == 1

    def test_line_number_accuracy(self, tmp_path):
        a = tmp_path / "a.md"
        a.write_text("# Title\n\nLine 3 text\n\n[broken](missing.md)\n\nLine 7\n")

        result = run_link_validation(target_path=tmp_path)
        assert result.payload["broken_links"][0]["line_number"] == 5

    def test_valid_cross_file_anchor(self, tmp_path):
        a = tmp_path / "a.md"
        b = tmp_path / "b.md"
        a.write_text("# Doc\n\n[link](b.md#section-one)\n")
        b.write_text("# Section One\n\nContent.\n")

        result = run_link_validation(target_path=tmp_path)
        assert result.passed is True

    def test_report_text_format(self, tmp_path):
        a = tmp_path / "a.md"
        a.write_text("# Doc\n\n[broken](missing.md)\n")

        result = run_link_validation(target_path=tmp_path)
        assert "Link Validation Report" in result.report_text
        assert "Broken links:" in result.report_text
        assert "file_not_found" in result.report_text

    def test_nonexistent_target_raises(self, tmp_path):
        missing = tmp_path / "nonexistent"
        with pytest.raises(FileNotFoundError):
            run_link_validation(target_path=missing)

    def test_skip_dirs_filtered(self, tmp_path):
        node_modules = tmp_path / "node_modules"
        node_modules.mkdir()
        (node_modules / "bad.md").write_text("# Bad\n\n[broken](missing.md)\n")
        (tmp_path / "good.md").write_text("# Good\n\nNo links here.\n")

        result = run_link_validation(target_path=tmp_path)
        assert result.passed is True
        assert result.payload["files_scanned"] == 1

    def test_url_encoded_link(self, tmp_path):
        target = tmp_path / "my file.md"
        target.write_text("# Target\n\nContent.\n")
        source = tmp_path / "source.md"
        source.write_text("# Source\n\n[link](my%20file.md)\n")

        result = run_link_validation(target_path=tmp_path)
        assert result.passed is True

    def test_md_extension_fallback(self, tmp_path):
        target = tmp_path / "readme.md"
        target.write_text("# Readme\n\nContent.\n")
        source = tmp_path / "source.md"
        source.write_text("# Source\n\n[link](readme)\n")

        result = run_link_validation(target_path=tmp_path)
        assert result.passed is True

    def test_absolute_link_resolution(self, tmp_path):
        sub = tmp_path / "docs"
        sub.mkdir()
        target = tmp_path / "root.md"
        target.write_text("# Root\n\nContent.\n")
        source = sub / "source.md"
        source.write_text("# Source\n\n[link](/root.md)\n")

        result = run_link_validation(target_path=sub, workspace_root=tmp_path)
        assert result.passed is True
