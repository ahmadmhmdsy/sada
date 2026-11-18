"""Compare a benchmark run against a committed baseline (the regression gate).

The gate answers one question: did the candidate run get **worse** than the committed baseline
beyond a tolerance we are willing to accept as noise? It validates that the two runs cover the same
suite (same clips, slice labels and reference text) and the same models, then reports overall and
per-slice deltas for WER, CER, Latin-name preservation and timestamp coverage.

A run that fails validation is a *usage* error (exit code 2), not a regression: comparing an
incompatible run would hide the problem behind numbers.
"""

from __future__ import annotations

import json
from pathlib import Path

from . import report

DEFAULT_TOLERANCE_PP = 1.0

# WER is the gate. CER, Latin preservation and timestamp coverage are reported as context only:
# they can move for harmless reasons (punctuation, a single clip) and are not release blockers.
GATED_METRIC = "wer_pct"

_METRICS = (
    ("wer_pct", "wer_delta_pp"),
    ("cer_pct", "cer_delta_pp"),
    ("latin_preserved_pct", "latin_delta_pp"),
    ("timestamps_ok_pct", "timestamps_delta_pp"),
)


class ComparisonError(ValueError):
    """The two runs cannot be compared (different suite, models or reference text)."""


def load_results(path: Path | str) -> dict:
    """Read a results JSON file, raising ComparisonError for unreadable input."""
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise ComparisonError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ComparisonError(f"{path} is not valid JSON: {exc}") from exc


def validate(baseline: dict, candidate: dict) -> list[str]:
    """Check the two runs are comparable; return warnings, raise ComparisonError on blockers."""
    errors: list[str] = []
    warnings: list[str] = []

    baseline_clips = {clip["id"]: clip for clip in baseline.get("clips", [])}
    candidate_clips = {clip["id"]: clip for clip in candidate.get("clips", [])}
    if not baseline_clips:
        raise ComparisonError("baseline has no clips")
    if not candidate_clips:
        raise ComparisonError("candidate has no clips")

    missing = sorted(set(baseline_clips) - set(candidate_clips))
    extra = sorted(set(candidate_clips) - set(baseline_clips))
    if missing:
        errors.append(
            f"candidate is missing {len(missing)} baseline clip(s), for example: "
            + ", ".join(missing[:5])
        )
    if extra:
        warnings.append(
            f"candidate adds {len(extra)} clip(s) not in the baseline, ignored by the gate: "
            + ", ".join(extra[:5])
        )

    shared = sorted(set(baseline_clips) & set(candidate_clips))
    re_sliced = [clip_id for clip_id in shared if baseline_clips[clip_id].get("slice") != candidate_clips[clip_id].get("slice")]
    if re_sliced:
        errors.append(
            f"{len(re_sliced)} clip(s) changed slice label, for example: " + ", ".join(re_sliced[:5])
        )
    changed_reference = [
        clip_id
        for clip_id in shared
        if baseline_clips[clip_id].get("reference") != candidate_clips[clip_id].get("reference")
    ]
    if changed_reference:
        errors.append(
            f"{len(changed_reference)} reference transcript(s) changed between runs, for example: "
            + ", ".join(changed_reference[:5])
            + " — regenerate the baseline instead of comparing across corpus edits"
        )

    baseline_models = set(baseline.get("runs", {}))
    candidate_models = set(candidate.get("runs", {}))
    if not baseline_models:
        errors.append("baseline has no model runs")
    missing_models = sorted(baseline_models - candidate_models)
    if missing_models:
        errors.append(
            "candidate is missing baseline model(s): " + ", ".join(missing_models)
        )
    extra_models = sorted(candidate_models - baseline_models)
    if extra_models:
        warnings.append(
            "candidate has model(s) with no baseline, not gated: " + ", ".join(extra_models)
        )

    if baseline.get("engine") and candidate.get("engine") and baseline["engine"] != candidate["engine"]:
        warnings.append(
            f"engine differs: baseline {baseline['engine']} vs candidate {candidate['engine']} — "
            "a regression may be an engine change, inspect it before accepting"
        )

    if errors:
        raise ComparisonError("\n".join(errors))
    return warnings


def _delta(baseline_value, candidate_value) -> float | None:
    if baseline_value is None or candidate_value is None:
        return None
    return round(candidate_value - baseline_value, 2)


def _cell(baseline_score: dict, candidate_score: dict, tolerance_pp: float) -> dict:
    cell = {
        "baseline_clips": baseline_score.get("clips", 0),
        "candidate_clips": candidate_score.get("clips", 0),
    }
    for metric, delta_key in _METRICS:
        cell[f"baseline_{metric}"] = baseline_score.get(metric)
        cell[f"candidate_{metric}"] = candidate_score.get(metric)
        cell[delta_key] = _delta(baseline_score.get(metric), candidate_score.get(metric))
    wer_delta = cell["wer_delta_pp"]
    cell["regression"] = wer_delta is not None and wer_delta > tolerance_pp + 1e-9
    return cell


def compare_reports(
    baseline_report: dict,
    candidate_report: dict,
    tolerance_pp: float = DEFAULT_TOLERANCE_PP,
) -> dict:
    """Diff two aggregated reports (see report.aggregate)."""
    if tolerance_pp < 0:
        raise ComparisonError("tolerance must be >= 0")
    warnings: list[str] = []
    models: dict[str, dict] = {}
    regressions: list[dict] = []

    baseline_models = baseline_report.get("models", {})
    candidate_models = candidate_report.get("models", {})
    for model_id, baseline_model in baseline_models.items():
        candidate_model = candidate_models.get(model_id)
        if candidate_model is None:
            warnings.append(f"model {model_id} has no candidate report, not compared")
            continue
        overall = _cell(baseline_model.get("overall", {}), candidate_model.get("overall", {}), tolerance_pp)
        slices: dict[str, dict] = {}
        for slice_name, baseline_slice in baseline_model.get("slices", {}).items():
            candidate_slice = candidate_model.get("slices", {}).get(slice_name, {})
            if not candidate_slice.get("clips"):
                warnings.append(
                    f"model {model_id}: slice {slice_name} has no candidate clips, not compared"
                )
                continue
            slices[slice_name] = _cell(baseline_slice, candidate_slice, tolerance_pp)
        model_regressions = []
        if overall["regression"]:
            model_regressions.append("overall")
            regressions.append({"model": model_id, "scope": "overall", "wer_delta_pp": overall["wer_delta_pp"]})
        for slice_name, cell in slices.items():
            if cell["regression"]:
                model_regressions.append(slice_name)
                regressions.append(
                    {"model": model_id, "scope": slice_name, "wer_delta_pp": cell["wer_delta_pp"]}
                )
        models[model_id] = {"overall": overall, "slices": slices, "regressions": model_regressions}

    return {
        "baseline": {
            "created": baseline_report.get("created", ""),
            "engine": baseline_report.get("engine", ""),
            "clips": baseline_report.get("clips", 0),
        },
        "candidate": {
            "created": candidate_report.get("created", ""),
            "engine": candidate_report.get("engine", ""),
            "clips": candidate_report.get("clips", 0),
        },
        "tolerance_pp": tolerance_pp,
        "warnings": warnings,
        "models": models,
        "regressions": regressions,
        "ok": not regressions,
    }


def compare_results(
    baseline: dict,
    candidate: dict,
    tolerance_pp: float = DEFAULT_TOLERANCE_PP,
) -> dict:
    """Validate two raw results files and compare them as a regression gate."""
    warnings = validate(baseline, candidate)
    comparison = compare_reports(
        report.aggregate(baseline), report.aggregate(candidate), tolerance_pp=tolerance_pp
    )
    comparison["warnings"] = warnings + comparison["warnings"]
    return comparison


def _fmt(value) -> str:
    return "n/a" if value is None else f"{value:.2f}"


def _fmt_delta(value) -> str:
    if value is None:
        return "n/a"
    return f"{value:+.2f}"


def render_markdown(comparison: dict) -> str:
    """Render a human-readable comparison, suitable for a release checklist."""
    verdict = "PASS — no gated regression" if comparison["ok"] else "REGRESSION"
    lines: list[str] = []
    lines.append("# Arabic ASR benchmark regression check")
    lines.append("")
    lines.append(f"**Verdict: {verdict}** (gate: WER delta > +{comparison['tolerance_pp']:.1f} pp)")
    lines.append("")
    lines.append(
        f"- Baseline: {comparison['baseline']['created'] or 'unknown'} · "
        f"{comparison['baseline']['engine'] or 'unknown engine'} · {comparison['baseline']['clips']} clips"
    )
    lines.append(
        f"- Candidate: {comparison['candidate']['created'] or 'unknown'} · "
        f"{comparison['candidate']['engine'] or 'unknown engine'} · {comparison['candidate']['clips']} clips"
    )
    lines.append("")
    lines.append("## Overall")
    lines.append("")
    lines.append("| Model | Baseline WER % | Candidate WER % | Delta pp | CER delta pp | Latin delta pp | Verdict |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for model_id, model in comparison["models"].items():
        overall = model["overall"]
        lines.append(
            "| "
            + " | ".join(
                [
                    model_id,
                    _fmt(overall["baseline_wer_pct"]),
                    _fmt(overall["candidate_wer_pct"]),
                    _fmt_delta(overall["wer_delta_pp"]),
                    _fmt_delta(overall["cer_delta_pp"]),
                    _fmt_delta(overall["latin_delta_pp"]),
                    "REGRESSION" if overall["regression"] else "ok",
                ]
            )
            + " |"
        )
    lines.append("")
    slices = sorted({name for model in comparison["models"].values() for name in model["slices"]})
    if slices:
        lines.append("## WER delta pp by slice (positive = worse)")
        lines.append("")
        lines.append("| Model | " + " | ".join(slices) + " |")
        lines.append("| --- | " + " | ".join("---" for _ in slices) + " |")
        for model_id, model in comparison["models"].items():
            row = [model_id]
            for slice_name in slices:
                cell = model["slices"].get(slice_name)
                row.append("n/a" if cell is None else _fmt_delta(cell["wer_delta_pp"]))
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")
    if comparison["regressions"]:
        lines.append("## Gated regressions")
        lines.append("")
        for item in comparison["regressions"]:
            lines.append(
                f"- {item['model']} / {item['scope']}: WER {item['wer_delta_pp']:+.2f} pp "
                f"vs the baseline (tolerance {comparison['tolerance_pp']:.1f} pp)"
            )
        lines.append("")
    if comparison["warnings"]:
        lines.append("## Warnings")
        lines.append("")
        for warning in comparison["warnings"]:
            lines.append(f"- {warning}")
        lines.append("")
    lines.append("## Method")
    lines.append("")
    lines.append(
        "Both runs are aggregated with the same scorer (sadabench.report). The gate fails when the "
        "candidate WER is worse than the committed baseline by more than the tolerance on the overall "
        "run or on any single slice; CER, Latin-name preservation and timestamp coverage are shown "
        "for context but do not gate. The tolerance absorbs scorer-noise-sized movement; it is not a "
        "license to accept a real regression — inspect the warnings and the per-slice table before "
        "releasing."
    )
    lines.append("")
    return "\n".join(lines)
