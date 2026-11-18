"""Command line entry point for the Sada Arabic ASR benchmark.

Commands:
    build-manifest  select clips from the pinned datasets and write manifest.json
    fetch           download clip audio and convert it to 16 kHz mono WAV
    run             transcribe every clip with every configured model
    report          aggregate results into JSON + Markdown tables
    compare         diff a run against a committed baseline (regression gate)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

from . import compare as compare_mod
from . import datasets, engine, postprocess, report


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sadabench", description="Sada Arabic ASR benchmark harness")
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build-manifest", help="select clips and write the manifest")
    build.add_argument("--out", type=Path, default=Path("manifest.json"))
    build.add_argument("--msa", type=int, default=30, help="number of MSA clips")
    build.add_argument("--egyptian", type=int, default=20, help="number of Egyptian clips")
    build.add_argument("--latin", type=int, default=10, help="number of Latin-mixed clips")
    build.add_argument("--gulf", type=int, default=15, help="number of Gulf (Saudi, Perle) clips")
    build.add_argument("--technical", type=int, default=15, help="number of Arabic/English technical clips")
    build.add_argument(
        "--reuse",
        type=Path,
        default=None,
        help="existing manifest whose unchanged slices are reused instead of re-scanned",
    )

    fetch = sub.add_parser("fetch", help="download and convert clip audio")
    fetch.add_argument("--manifest", type=Path, default=Path("manifest.json"))
    fetch.add_argument("--audio-dir", type=Path, default=Path("audio"))
    fetch.add_argument("--ffmpeg", default="ffmpeg")
    fetch.add_argument("--force", action="store_true", help="re-download existing clips")

    run = sub.add_parser("run", help="transcribe all clips with all models")
    run.add_argument("--manifest", type=Path, default=Path("manifest.json"))
    run.add_argument("--audio-dir", type=Path, default=Path("audio"))
    run.add_argument("--models", type=Path, default=Path("models.local.json"))
    run.add_argument("--engine", required=True, help="path to vibe-server.exe")
    run.add_argument("--out", type=Path, required=True)
    run.add_argument("--baseline", default="whisper-large-v3-turbo")
    run.add_argument("--only", default="", help="comma separated model ids to run")
    run.add_argument("--slices", default="", help="comma separated slice names to run")
    run.add_argument("--limit", type=int, default=0, help="run the first N clips only")

    render = sub.add_parser("report", help="aggregate results into tables")
    render.add_argument("--results", type=Path, required=True)
    render.add_argument("--md", type=Path, default=None, help="write Markdown next to the JSON")

    compare = sub.add_parser(
        "compare",
        help="diff a run against a committed baseline and fail on a WER regression",
    )
    compare.add_argument("--baseline", type=Path, required=True)
    compare.add_argument("--candidate", type=Path, required=True)
    compare.add_argument(
        "--tolerance-pp",
        type=float,
        default=compare_mod.DEFAULT_TOLERANCE_PP,
        help=f"allowed WER regression in percentage points (default {compare_mod.DEFAULT_TOLERANCE_PP:g})",
    )
    compare.add_argument("--json", action="store_true", help="print the comparison as JSON")
    compare.add_argument(
        "--out",
        type=Path,
        default=None,
        help="also write the JSON comparison to this path",
    )
    return parser


def _engine_version(engine_path: str) -> str:
    try:
        completed = subprocess.run([engine_path, "--version"], capture_output=True, timeout=60)
        text = completed.stdout.decode("utf-8", errors="replace") or completed.stderr.decode(
            "utf-8", errors="replace"
        )
        return text.strip()
    except Exception:  # noqa: BLE001 - version is informational only
        return "unknown"


def cmd_build_manifest(args: argparse.Namespace) -> int:
    reuse = datasets.load_manifest(args.reuse) if args.reuse else None
    manifest = datasets.build_manifest(
        msa_count=args.msa,
        egyptian_count=args.egyptian,
        latin_count=args.latin,
        gulf_count=args.gulf,
        technical_count=args.technical,
        reuse_manifest=reuse,
    )
    datasets.write_json(args.out, manifest)
    counts: dict[str, int] = {}
    for clip in manifest["clips"]:
        counts[clip["slice"]] = counts.get(clip["slice"], 0) + 1
    print(f"wrote {args.out} with {len(manifest['clips'])} clips: {json.dumps(counts)}")
    return 0


def cmd_fetch(args: argparse.Namespace) -> int:
    manifest = datasets.load_manifest(args.manifest)
    result = datasets.fetch_clips(manifest, args.audio_dir, args.ffmpeg, force=args.force)
    print(f"fetched {result.fetched}, skipped {result.skipped}, failed {len(result.failed)}")
    for message in result.failed:
        print(f"FAILED {message}", file=sys.stderr)
    return 1 if result.failed else 0


def cmd_run(args: argparse.Namespace) -> int:
    manifest = datasets.load_manifest(args.manifest)
    models_path = Path(args.models)
    loaded = engine.load_models(models_path, args.engine)
    models = loaded["_models"]
    if args.only:
        wanted = {item.strip() for item in args.only.split(",") if item.strip()}
        models = {model_id: model for model_id, model in models.items() if model_id in wanted}
    problems = engine.preflight(args.engine, models)
    if problems:
        for problem in problems:
            print(f"preflight: {problem}", file=sys.stderr)
        return 2

    clips = manifest["clips"][: args.limit] if args.limit else manifest["clips"]
    if args.slices:
        wanted_slices = {item.strip() for item in args.slices.split(",") if item.strip()}
        clips = [clip for clip in clips if clip["slice"] in wanted_slices]
    lock = {}
    lock_path = Path(args.audio_dir) / "manifest.lock.json"
    if lock_path.exists():
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
    missing = [clip["id"] for clip in clips if not (Path(args.audio_dir) / f"{clip['id']}.wav").exists()]
    if missing:
        print(f"missing audio for {len(missing)} clips; run the fetch command first", file=sys.stderr)
        return 2

    results = {
        "version": 1,
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
        "engine": _engine_version(args.engine),
        "baseline": args.baseline,
        "models": {
            model_id: {
                "file": Path(model.path).name,
                "family": model.family,
                "language": model.language,
                "size_mb": model.size_mb,
            }
            for model_id, model in models.items()
        },
        "clips": [],
        "runs": {model_id: {} for model_id in models},
    }
    for clip in clips:
        audio = Path(args.audio_dir) / f"{clip['id']}.wav"
        duration = lock.get(clip["id"], {}).get("duration_sec", 0.0)
        results["clips"].append(
            {
                "id": clip["id"],
                "slice": clip["slice"],
                "reference": clip["reference"],
                "duration_sec": duration,
            }
        )

    total = len(clips) * len(models)
    done = 0
    for model_id, model in models.items():
        print(f"== {model_id} ({model.family}, {model.size_mb} MB) ==")
        for clip in clips:
            audio = Path(args.audio_dir) / f"{clip['id']}.wav"
            run = engine.run_clip(args.engine, model, audio, use_word_timestamps=True)
            results["runs"][model_id][clip["id"]] = run
            done += 1
            status = "ok" if run["ok"] else "FAIL"
            print(
                f"  [{done}/{total}] {clip['id']} {status} "
                f"{run['latency_sec']}s ts={run['timestamps']}"
            )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    datasets.write_json(args.out, results)
    print(f"wrote {args.out}")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    results = json.loads(args.results.read_text(encoding="utf-8"))
    report_data = report.aggregate(results)
    app_report = report.aggregate(results, hypothesis_filter=postprocess.postprocess)
    markdown = report.render_markdown(report_data, app_report=app_report)
    md_path = args.md or args.results.with_suffix(".md")
    md_path.write_text(markdown, encoding="utf-8")
    print(markdown)
    print(f"wrote {md_path}")
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    try:
        baseline = compare_mod.load_results(args.baseline)
        candidate = compare_mod.load_results(args.candidate)
        comparison = compare_mod.compare_results(
            baseline, candidate, tolerance_pp=args.tolerance_pp
        )
    except compare_mod.ComparisonError as exc:
        print(f"compare: {exc}", file=sys.stderr)
        return 2
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        datasets.write_json(args.out, comparison)
        print(f"wrote {args.out}")
    if args.json:
        print(json.dumps(comparison, ensure_ascii=False, indent=2))
    else:
        markdown = compare_mod.render_markdown(comparison)
        print(markdown)
        if not comparison["ok"]:
            for item in comparison["regressions"]:
                print(
                    f"REGRESSION {item['model']} / {item['scope']}: "
                    f"{item['wer_delta_pp']:+.2f} pp vs baseline",
                    file=sys.stderr,
                )
    return 0 if comparison["ok"] else 1


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    handlers = {
        "build-manifest": cmd_build_manifest,
        "fetch": cmd_fetch,
        "run": cmd_run,
        "report": cmd_report,
        "compare": cmd_compare,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
