"""Command line entry point for the Sada Arabic ASR benchmark.

Commands:
    build-manifest  select clips from the pinned datasets and write manifest.json
    fetch           download clip audio and convert it to 16 kHz mono WAV
    run             transcribe every clip with every configured model
    report          aggregate results into JSON + Markdown tables
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from . import datasets, engine, report


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sadabench", description="Sada Arabic ASR benchmark harness")
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build-manifest", help="select clips and write the manifest")
    build.add_argument("--out", type=Path, default=Path("manifest.json"))
    build.add_argument("--msa", type=int, default=30, help="number of MSA clips")
    build.add_argument("--egyptian", type=int, default=20, help="number of Egyptian clips")
    build.add_argument("--latin", type=int, default=10, help="number of Latin-mixed clips")
    build.add_argument("--technical", type=int, default=10, help="number of technical clips")

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
    run.add_argument("--limit", type=int, default=0, help="run the first N clips only")

    render = sub.add_parser("report", help="aggregate results into tables")
    render.add_argument("--results", type=Path, required=True)
    render.add_argument("--md", type=Path, default=None, help="write Markdown next to the JSON")
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
    manifest = datasets.build_manifest(
        msa_count=args.msa,
        egyptian_count=args.egyptian,
        latin_count=args.latin,
        technical_count=args.technical,
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
    markdown = report.render_markdown(report_data)
    md_path = args.md or args.results.with_suffix(".md")
    md_path.write_text(markdown, encoding="utf-8")
    print(markdown)
    print(f"wrote {md_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    handlers = {
        "build-manifest": cmd_build_manifest,
        "fetch": cmd_fetch,
        "run": cmd_run,
        "report": cmd_report,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
