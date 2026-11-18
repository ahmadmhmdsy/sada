"""Unit tests for result aggregation and the curation rule."""

import unittest

from sadabench import report


def _results() -> dict:
    return {
        "created": "2026-11-18 10:00:00",
        "engine": "vibe-server v0.6.16-sada.1",
        "baseline": "turbo",
        "models": {
            "turbo": {"family": "whisper", "size_mb": 1624.6, "language": "ar"},
            "nemotron": {"family": "nemotron", "size_mb": 495.8, "language": "ar-AR"},
        },
        "clips": [
            {"id": "msa-1", "slice": "msa", "reference": "اجتمع الفريق صباح اليوم", "duration_sec": 3.0},
            {"id": "msa-2", "slice": "msa", "reference": "اتفقنا على تأجيل المشروع", "duration_sec": 3.0},
            {"id": "tech-1", "slice": "technical", "reference": "صدّر الملف بصيغة SRT", "duration_sec": 2.0},
        ],
        "runs": {
            "turbo": {
                "msa-1": {"ok": True, "text": "اجتمع الفريق صباح اليوم", "latency_sec": 1.0, "timestamps": True},
                "msa-2": {"ok": True, "text": "اتفقنا على تأجيل المشروع", "latency_sec": 1.0, "timestamps": True},
                "tech-1": {"ok": True, "text": "صدّر الملف بصيغة SRT", "latency_sec": 1.0, "timestamps": True},
            },
            "nemotron": {
                "msa-1": {"ok": True, "text": "اجتمع الفريق صباح اليوم", "latency_sec": 2.0, "timestamps": False},
                "msa-2": {"ok": True, "text": "اتفقنا على تأجيل المشروع", "latency_sec": 2.0, "timestamps": False},
                "tech-1": {"ok": True, "text": "صدّر الملف بصيغة السورتي", "latency_sec": 2.0, "timestamps": False},
            },
        },
    }


class AggregateTest(unittest.TestCase):
    def test_scores_per_slice_and_overall(self) -> None:
        payload = report.aggregate(_results())
        self.assertEqual(payload["clips"], 3)
        self.assertEqual(payload["models"]["turbo"]["overall"]["wer_pct"], 0.0)
        self.assertEqual(payload["models"]["turbo"]["overall"]["acronym_preserved_pct"], 100.0)
        self.assertEqual(payload["models"]["nemotron"]["slices"]["technical"]["acronym_preserved_pct"], 0.0)
        self.assertEqual(payload["models"]["nemotron"]["overall"]["timestamps_ok_pct"], 0.0)

    def test_curation_rule_requires_timestamps_and_acronyms(self) -> None:
        payload = report.aggregate(_results())
        notes = report.decisions(payload)
        self.assertIn("nemotron", notes)
        self.assertEqual(notes["nemotron"]["curate_on"], [])

    def test_render_markdown_contains_tables_and_rule(self) -> None:
        payload = report.aggregate(_results())
        markdown = report.render_markdown(payload)
        self.assertIn("| Model | Size MB | WER % |", markdown)
        self.assertIn("nemotron", markdown)
        self.assertIn("Curation rule", markdown)
        self.assertIn("technical", markdown)


if __name__ == "__main__":
    unittest.main()
