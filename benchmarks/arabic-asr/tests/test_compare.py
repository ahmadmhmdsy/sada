"""Unit tests for the benchmark regression gate (sadabench.compare)."""

import json
import tempfile
import unittest
from pathlib import Path

from sadabench import compare
from sadabench.__main__ import main

_WORDS = ["واحد", "اثنان", "ثلاثة", "أربعة", "خمسة", "ستة", "سبعة", "ثمانية", "تسعة", "عشرة"]


def _results(
    models: tuple[str, ...] = ("turbo",),
    clips: int = 10,
    errors: dict | None = None,
    engine: str = "vibe-server v0.6.16-sada.1",
) -> dict:
    """Build a results payload: every clip is the same ten-word reference, errors are word swaps.

    WER is corpus-level, so with 10 clips x 10 words one wrong word is exactly 1.00 pp.
    """
    errors = errors or {}
    payload = {
        "version": 1,
        "created": "2026-11-18 12:00:00",
        "engine": engine,
        "baseline": models[0],
        "models": {
            model: {"family": "whisper", "language": "ar", "size_mb": 1624.6} for model in models
        },
        "clips": [],
        "runs": {model: {} for model in models},
    }
    for index in range(clips):
        clip_id = f"clip-{index:02d}"
        payload["clips"].append(
            {
                "id": clip_id,
                "slice": "msa" if index < clips // 2 else "technical",
                "reference": " ".join(_WORDS),
                "duration_sec": 2.0,
            }
        )
        for model in models:
            hypothesis = list(_WORDS)
            for position in range(errors.get((model, clip_id), 0)):
                hypothesis[position] = "نطق"
            payload["runs"][model][clip_id] = {
                "ok": True,
                "text": " ".join(hypothesis),
                "latency_sec": 2.0,
                "timestamps": True,
            }
    return payload


def _write(directory: Path, name: str, payload: dict) -> Path:
    path = directory / name
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path


class CompareResultsTest(unittest.TestCase):
    def test_identical_runs_pass(self) -> None:
        payload = _results()
        comparison = compare.compare_results(payload, payload)
        self.assertTrue(comparison["ok"])
        self.assertEqual(comparison["regressions"], [])
        self.assertEqual(comparison["models"]["turbo"]["overall"]["wer_delta_pp"], 0.0)

    def test_regression_over_tolerance_fails(self) -> None:
        baseline = _results()
        candidate = _results(errors={("turbo", "clip-00"): 2})
        comparison = compare.compare_results(baseline, candidate, tolerance_pp=1.0)
        self.assertFalse(comparison["ok"])
        overall = comparison["models"]["turbo"]["overall"]
        self.assertEqual(overall["wer_delta_pp"], 2.0)
        self.assertTrue(overall["regression"])
        # The msa slice loses 2 of its 50 reference words, so it regresses too.
        self.assertTrue(comparison["models"]["turbo"]["slices"]["msa"]["regression"])
        scopes = {(item["model"], item["scope"]) for item in comparison["regressions"]}
        self.assertIn(("turbo", "overall"), scopes)
        self.assertIn(("turbo", "msa"), scopes)

    def test_tolerance_boundary_passes_at_exactly_tolerance(self) -> None:
        # 20 clips x 10 words: one wrong word in each slice is exactly 1.00 pp overall and
        # exactly 1.00 pp on each slice, so it sits on the tolerance boundary everywhere.
        baseline = _results(clips=20)
        candidate = _results(clips=20, errors={("turbo", "clip-00"): 1, ("turbo", "clip-10"): 1})
        at_tolerance = compare.compare_results(baseline, candidate, tolerance_pp=1.0)
        self.assertTrue(at_tolerance["ok"])
        overall = at_tolerance["models"]["turbo"]["overall"]
        self.assertEqual(overall["wer_delta_pp"], 1.0)
        self.assertFalse(overall["regression"])
        stricter = compare.compare_results(baseline, candidate, tolerance_pp=0.5)
        self.assertFalse(stricter["ok"])

    def test_candidate_missing_clip_is_a_usage_error(self) -> None:
        baseline = _results()
        candidate = _results()
        candidate["clips"] = candidate["clips"][1:]
        for runs in candidate["runs"].values():
            runs.pop("clip-00", None)
        with self.assertRaises(compare.ComparisonError) as caught:
            compare.compare_results(baseline, candidate)
        self.assertIn("missing 1 baseline clip", str(caught.exception))

    def test_changed_slice_or_reference_is_a_usage_error(self) -> None:
        baseline = _results()
        changed_slice = _results()
        changed_slice["clips"][0]["slice"] = "gulf"
        with self.assertRaises(compare.ComparisonError) as caught:
            compare.compare_results(baseline, changed_slice)
        self.assertIn("changed slice label", str(caught.exception))

        changed_reference = _results()
        changed_reference["clips"][0]["reference"] += " زائد"
        with self.assertRaises(compare.ComparisonError) as caught:
            compare.compare_results(baseline, changed_reference)
        self.assertIn("reference transcript", str(caught.exception))

    def test_missing_model_is_a_usage_error_and_extra_model_is_a_warning(self) -> None:
        baseline = _results(models=("turbo", "nemotron"))
        candidate = _results(models=("turbo",))
        with self.assertRaises(compare.ComparisonError) as caught:
            compare.compare_results(baseline, candidate)
        self.assertIn("missing baseline model", str(caught.exception))

        extra = _results(models=("turbo", "extra"))
        comparison = compare.compare_results(_results(), extra)
        self.assertTrue(comparison["ok"])
        self.assertTrue(any("no baseline" in warning for warning in comparison["warnings"]))

    def test_engine_change_is_a_warning_not_a_blocker(self) -> None:
        baseline = _results()
        candidate = _results(engine="vibe-server v0.7.0-sada.1")
        comparison = compare.compare_results(baseline, candidate)
        self.assertTrue(comparison["ok"])
        self.assertTrue(any("engine differs" in warning for warning in comparison["warnings"]))

    def test_negative_tolerance_is_rejected(self) -> None:
        report = compare.report.aggregate(_results())
        with self.assertRaises(compare.ComparisonError):
            compare.compare_reports(report, report, tolerance_pp=-1.0)

    def test_render_markdown_reports_verdict_and_tables(self) -> None:
        baseline = _results()
        passed = compare.render_markdown(compare.compare_results(baseline, baseline))
        self.assertIn("PASS", passed)
        self.assertIn("| Model | Baseline WER % |", passed)
        self.assertIn("WER delta pp by slice", passed)

        regressed = compare.render_markdown(
            compare.compare_results(baseline, _results(errors={("turbo", "clip-00"): 2}))
        )
        self.assertIn("REGRESSION", regressed)
        self.assertIn("Gated regressions", regressed)


class CompareCliTest(unittest.TestCase):
    def test_exit_codes(self) -> None:
        baseline_payload = _results()
        regressed_payload = _results(errors={("turbo", "clip-00"): 2})
        incompatible_payload = _results()
        incompatible_payload["clips"] = incompatible_payload["clips"][1:]
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            baseline = _write(directory, "baseline.json", baseline_payload)
            candidate = _write(directory, "candidate.json", baseline_payload)
            regressed = _write(directory, "regressed.json", regressed_payload)
            incompatible = _write(directory, "incompatible.json", incompatible_payload)
            out = directory / "comparison.json"

            self.assertEqual(
                main(["compare", "--baseline", str(baseline), "--candidate", str(candidate)]), 0
            )
            self.assertEqual(
                main(
                    [
                        "compare",
                        "--baseline",
                        str(baseline),
                        "--candidate",
                        str(regressed),
                    ]
                ),
                1,
            )
            self.assertEqual(
                main(
                    [
                        "compare",
                        "--baseline",
                        str(baseline),
                        "--candidate",
                        str(incompatible),
                    ]
                ),
                2,
            )
            self.assertEqual(
                main(
                    [
                        "compare",
                        "--baseline",
                        str(baseline),
                        "--candidate",
                        str(candidate),
                        "--json",
                        "--out",
                        str(out),
                    ]
                ),
                0,
            )
            written = json.loads(out.read_text(encoding="utf-8"))
            self.assertTrue(written["ok"])


if __name__ == "__main__":
    unittest.main()
