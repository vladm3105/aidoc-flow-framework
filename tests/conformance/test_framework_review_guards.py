"""Conformance guards from the FRWK-REVIEW pre-production audit.

These lock in fixes the rest of the suite doesn't otherwise catch:
  - layer-template trace-tag examples are well-formed (document OR element ID
    form, never the malformed hybrid) — guards #1;
  - no stale "5-gate" naming survives now that GATE-SPEC is the 6th gate (#2);
  - the emergency post-mortem SLA is a single value (48h) across the CHG docs (#3).
"""

import re
import unittest

from _spec import FRAMEWORK

LAYER_TAGS = ("brd", "prd", "ears", "bdd", "adr", "spec", "tdd", "iplan")
_TAG = re.compile(r"@(" + "|".join(LAYER_TAGS) + r"):\s*([A-Za-z][A-Za-z0-9.\-]*)")
# Placeholder-tolerant: tokens may be NN / SS / xxxx etc., so segments are
# [A-Za-z0-9]+ rather than the literal registry regex's \d / [a-f0-9].
_DOC_FORM = re.compile(r"^[A-Z]+-[A-Za-z0-9]+$")  # e.g. SPEC-NN
_ELEM_FORM = re.compile(r"^[A-Z]+(?:\.[A-Za-z0-9]+){3}$")  # e.g. ADR.NN.SS.xxxx
CHG = FRAMEWORK / "governance" / "chg"


class TraceTagForms(unittest.TestCase):
    def test_layer_template_trace_tags_well_formed(self):
        bad = []
        for tmpl in sorted(FRAMEWORK.glob("layers/*/*-TEMPLATE.yaml")):
            for i, line in enumerate(tmpl.read_text(encoding="utf-8").splitlines(), 1):
                if "FAIL:" in line:
                    continue  # _antipatterns deliberately show malformed examples
                for m in _TAG.finditer(line):
                    tok = m.group(2)
                    if not (_DOC_FORM.match(tok) or _ELEM_FORM.match(tok)):
                        rel = tmpl.relative_to(FRAMEWORK).as_posix()
                        bad.append(f"{rel}:{i}: @{m.group(1)}: {tok}")
        self.assertEqual(
            bad,
            [],
            "trace-tag ids must be document form (DOC-NN) or element form "
            f"(DOC.NN.SS.xxxx), never a hybrid/truncated form: {bad}",
        )


class GateNaming(unittest.TestCase):
    def test_no_stale_five_gate(self):
        bad = []
        for f in CHG.rglob("*.md"):
            for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
                if re.search(r"5-gate|five[- ]gate", line, re.I) and not re.search(
                    r"original|artifact", line, re.I
                ):
                    bad.append(f"{f.relative_to(FRAMEWORK).as_posix()}:{i}")
        self.assertEqual(bad, [], f"stale '5-gate' refs (GATE-SPEC makes it six): {bad}")


class EmergencySLA(unittest.TestCase):
    def test_post_mortem_sla_is_48h(self):
        catalog = (CHG / "gates" / "GATE_ERROR_CATALOG.md").read_text(encoding="utf-8")
        emg = [ln for ln in catalog.splitlines() if "EMG-E004" in ln]
        self.assertTrue(emg, "EMG-E004 (post-mortem timeline) missing from the catalog")
        self.assertIn("48 hours", emg[0])
        self.assertNotIn("72 hours", emg[0])
        for f in (CHG / "gates").glob("*.md"):
            self.assertNotIn(
                "24-72",
                f.read_text(encoding="utf-8"),
                f"stale 24-72h emergency window in {f.name}",
            )


if __name__ == "__main__":
    unittest.main()
