"""Shared fixtures for the app-level Arabic post-processing rules.

The canonical case list lives in fixtures/arabic-postprocess-cases.json and is also asserted by
desktop/src/lib/arabic-text-fixtures.test.ts, so the TypeScript app and this Python mirror cannot
drift apart without a failing test on one side.
"""

import json
import unittest
from pathlib import Path

from sadabench import postprocess

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = json.loads((ROOT / "fixtures" / "arabic-postprocess-cases.json").read_text(encoding="utf-8"))
RESULTS = ROOT / "results" / "results-2026-11-18.json"


class PostprocessFixtureTest(unittest.TestCase):
    def test_rewrites_every_replacement_case(self) -> None:
        for item in FIXTURE["replacements"]:
            with self.subTest(case=item["name"]):
                self.assertEqual(postprocess.postprocess(item["input"]), item["expected"])

    def test_leaves_every_unchanged_case_untouched(self) -> None:
        for item in FIXTURE["unchanged"]:
            with self.subTest(case=item["name"]):
                self.assertEqual(postprocess.postprocess(item["input"]), item["input"])

    def test_is_idempotent_on_the_fixture(self) -> None:
        inputs = [item["input"] for item in FIXTURE["replacements"] + FIXTURE["unchanged"]]
        for text in inputs:
            once = postprocess.postprocess(text)
            self.assertEqual(postprocess.postprocess(once), once)

    def test_corpus_references_never_trigger_a_rule(self) -> None:
        """The glossary must not rewrite ordinary Arabic: no reference sentence may match it."""
        if not RESULTS.exists():
            self.skipTest("committed results file is not present")
        results = json.loads(RESULTS.read_text(encoding="utf-8"))
        for clip in results["clips"]:
            with self.subTest(clip=clip["id"]):
                self.assertEqual(postprocess.find_terms(clip["reference"]), [])


if __name__ == "__main__":
    unittest.main()
