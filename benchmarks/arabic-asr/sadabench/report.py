"""Aggregate benchmark runs into comparable tables and decision notes."""

from __future__ import annotations

from typing import Callable

from .metrics import Score

MIN_WER_GAIN_PP = 1.0
MIN_ACRONYM_PRESERVED_PCT = 90.0

HypothesisFilter = Callable[[str], str]


def aggregate(results: dict, hypothesis_filter: HypothesisFilter | None = None) -> dict:
    """Compute overall and per-slice scores for every model in a results file.

    When hypothesis_filter is given (normally postprocess.postprocess), the filter is applied to
    every hypothesis before scoring, so the report describes what the app actually shows.
    """
    clips = results["clips"]
    slices = sorted({clip["slice"] for clip in clips})
    models: dict[str, dict] = {}
    for model_id, runs in results["runs"].items():
        overall = Score()
        per_slice = {name: Score() for name in slices}
        for clip in clips:
            run = runs.get(clip["id"])
            if not run:
                continue
            reference = clip["reference"]
            hypothesis = run.get("text", "")
            if hypothesis_filter is not None:
                hypothesis = hypothesis_filter(hypothesis)
            duration = clip.get("duration_sec", 0.0)
            latency = run.get("latency_sec", 0.0)
            timestamps_ok = bool(run.get("timestamps"))
            overall.add(reference, hypothesis, duration, latency, timestamps_ok)
            per_slice[clip["slice"]].add(reference, hypothesis, duration, latency, timestamps_ok)
        meta = results.get("models", {}).get(model_id, {})
        models[model_id] = {
            "family": meta.get("family", ""),
            "size_mb": meta.get("size_mb"),
            "language": meta.get("language", ""),
            "overall": overall.as_dict(),
            "slices": {name: score.as_dict() for name, score in per_slice.items()},
        }
    return {
        "created": results.get("created", ""),
        "engine": results.get("engine", ""),
        "baseline": results.get("baseline", ""),
        "clips": len(clips),
        "slices": slices,
        "models": models,
    }


def decisions(report: dict) -> dict:
    """Apply the council curation rule to every challenger.

    Rule (docs/MODELS-COUNCIL.md section 6): a challenger is curated only when it
    beats the baseline by at least 1.0 pp WER on its target slice, keeps word
    timestamps, and preserves at least 90% of Latin acronyms.
    """
    baseline_id = report.get("baseline")
    baseline = report["models"].get(baseline_id or "")
    notes: dict[str, dict] = {}
    if not baseline:
        return notes
    for model_id, model in report["models"].items():
        if model_id == baseline_id:
            continue
        per_slice: dict[str, dict] = {}
        for slice_name, slice_score in model["slices"].items():
            baseline_slice = baseline["slices"].get(slice_name, {})
            if not slice_score.get("clips"):
                continue
            base_wer = baseline_slice.get("wer_pct")
            challenger_wer = slice_score.get("wer_pct")
            gain = None if base_wer is None or challenger_wer is None else round(base_wer - challenger_wer, 2)
            acronym = slice_score.get("acronym_preserved_pct")
            latin = slice_score.get("latin_preserved_pct")
            timestamps = slice_score.get("timestamps_ok_pct")
            passes = (
                gain is not None
                and gain >= MIN_WER_GAIN_PP
                and timestamps == 100.0
                and (acronym is None or acronym >= MIN_ACRONYM_PRESERVED_PCT)
            )
            per_slice[slice_name] = {
                "baseline_wer_pct": base_wer,
                "challenger_wer_pct": challenger_wer,
                "wer_gain_pp": gain,
                "timestamps_ok_pct": timestamps,
                "acronym_preserved_pct": acronym,
                "latin_preserved_pct": latin,
                "passes_rule": passes,
            }
        wins = [name for name, item in per_slice.items() if item["passes_rule"]]
        notes[model_id] = {"slices": per_slice, "curate_on": wins}
    return notes


def _fmt(value) -> str:
    return "n/a" if value is None else str(value)


def render_markdown(report: dict, app_report: dict | None = None) -> str:
    """Render a human-readable Markdown report.

    app_report, when given, is the same aggregation with the app's post-processing applied to the
    hypotheses; its scores are rendered as a separate section.
    """
    lines: list[str] = []
    lines.append("# Arabic ASR benchmark results")
    lines.append("")
    lines.append(f"- Created: {report['created'] or 'unknown'}")
    lines.append(f"- Engine: {report['engine'] or 'unknown'}")
    lines.append(f"- Clips: {report['clips']}")
    lines.append(f"- Slices: {', '.join(report['slices'])}")
    lines.append(f"- Baseline: {report['baseline']}")
    lines.append("")
    lines.append("## Overall")
    lines.append("")
    lines.append(
        "| Model | Size MB | WER % | CER % | Acronyms preserved % | Latin names preserved % | Timestamps ok % | RTF |"
    )
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for model_id, model in report["models"].items():
        overall = model["overall"]
        lines.append(
            "| "
            + " | ".join(
                [
                    model_id,
                    _fmt(model.get("size_mb")),
                    _fmt(overall.get("wer_pct")),
                    _fmt(overall.get("cer_pct")),
                    _fmt(overall.get("acronym_preserved_pct")),
                    _fmt(overall.get("latin_preserved_pct")),
                    _fmt(overall.get("timestamps_ok_pct")),
                    _fmt(overall.get("rtf")),
                ]
            )
            + " |"
        )
    lines.append("")
    lines.append("## WER % by slice")
    lines.append("")
    header = "| Model | " + " | ".join(report["slices"]) + " |"
    lines.append(header)
    lines.append("| --- | " + " | ".join("---" for _ in report["slices"]) + " |")
    for model_id, model in report["models"].items():
        row = [model_id]
        for slice_name in report["slices"]:
            row.append(_fmt(model["slices"].get(slice_name, {}).get("wer_pct")))
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    notes = decisions(report)
    if notes:
        lines.append("## Curation rule")
        lines.append("")
        lines.append(
            f"A challenger is curated only if it beats the baseline by at least {MIN_WER_GAIN_PP} pp WER "
            f"on a slice, keeps word timestamps (100%) and preserves at least {MIN_ACRONYM_PRESERVED_PCT}% "
            "of Latin acronyms on that slice."
        )
        lines.append("")
        for model_id, note in notes.items():
            lines.append(f"### {model_id}")
            lines.append("")
            if not note["curate_on"]:
                lines.append("- Does not clear the rule on any measured slice.")
            else:
                lines.append(f"- Clears the rule on: {', '.join(note['curate_on'])}")
            for slice_name, item in note["slices"].items():
                lines.append(
                    f"- {slice_name}: WER {_fmt(item['challenger_wer_pct'])}% vs baseline "
                    f"{_fmt(item['baseline_wer_pct'])}% (gain {_fmt(item['wer_gain_pp'])} pp), "
                    f"timestamps {_fmt(item['timestamps_ok_pct'])}%, acronyms "
                    f"{_fmt(item['acronym_preserved_pct'])}%, latin names "
                    f"{_fmt(item['latin_preserved_pct'])}% -> "
                    f"{'PASS' if item['passes_rule'] else 'no'}"
                )
            lines.append("")
    if app_report:
        lines.append("## App-level (after the app's Arabic post-processing)")
        lines.append("")
        lines.append(
            "The app normalises Arabic punctuation and restores transliterated technical terms "
            "(desktop/src/lib/arabic-text.ts, mirrored by sadabench/postprocess.py) before showing "
            "or exporting text. These scores apply the same rules to every hypothesis."
        )
        lines.append("")
        lines.append(
            "| Model | Raw WER % | App WER % | App CER % | App acronyms preserved % | "
            "App Latin names preserved % |"
        )
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for model_id, model in app_report["models"].items():
            raw_overall = report["models"].get(model_id, {}).get("overall", {})
            overall = model["overall"]
            lines.append(
                "| "
                + " | ".join(
                    [
                        model_id,
                        _fmt(raw_overall.get("wer_pct")),
                        _fmt(overall.get("wer_pct")),
                        _fmt(overall.get("cer_pct")),
                        _fmt(overall.get("acronym_preserved_pct")),
                        _fmt(overall.get("latin_preserved_pct")),
                    ]
                )
                + " |"
            )
        lines.append("")
        lines.append(
            "On the committed clips this changes punctuation only: no permissive Arabic technical "
            "corpus exists yet, so the reference transcripts carry no Latin acronyms to restore. "
            "The section exists so the next technical slice is scored against what users see."
        )
        lines.append("")
    lines.append("## Method")
    lines.append("")
    lines.append(
        "Reference transcripts are normalised (diacritics, tatweel, hamza forms, alef maqsura, "
        "digits, punctuation) before word/character Levenshtein scoring; WER and CER are "
        "corpus-level sums. Latency includes one process start and model load per clip. "
        "See README.md for sources, licences and the decision rule."
    )
    lines.append("")
    return "\n".join(lines)
