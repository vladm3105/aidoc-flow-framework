"""Cleanup module for pruning obsolete stage artifacts."""

from .runner import CleanResult, run_clean

__all__ = ["CleanResult", "run_clean"]
