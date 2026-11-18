"""Run the bundled vibe-server engine for benchmark measurements."""

from __future__ import annotations

import json
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

from .metrics import parse_word_timestamps


@dataclass
class ModelSpec:
    """A model under test, as configured in models.local.json."""

    id: str
    path: str
    language: str
    family: str = "whisper"
    args: list[str] = field(default_factory=list)
    size_bytes: int | None = None
    prompt: str | None = None

    @property
    def size_mb(self) -> float | None:
        return round(self.size_bytes / 1e6, 1) if self.size_bytes else None


def load_models(path: Path, engine: str) -> dict:
    """Load and validate a models definition file."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    models: dict[str, ModelSpec] = {}
    for model_id, item in payload.get("models", {}).items():
        prompt = item.get("prompt")
        prompt_file = item.get("prompt_file")
        if prompt_file:
            prompt_path = Path(prompt_file)
            if not prompt_path.is_absolute():
                prompt_path = path.parent / prompt_path
            prompt = prompt_path.read_text(encoding="utf-8").strip()
        args = list(item.get("args", []))
        if prompt:
            # clap accepts --prompt=value, so a multi-word prompt stays one argv entry.
            args.append(f"--prompt={prompt}")
        model = ModelSpec(
            id=model_id,
            path=item["path"],
            language=item["language"],
            family=item.get("family", "whisper"),
            args=args,
            size_bytes=item.get("size_bytes"),
            prompt=prompt,
        )
        if not Path(model.path).exists():
            raise FileNotFoundError(f"{model_id}: model file not found at {model.path}")
        models[model_id] = model
    if not models:
        raise ValueError("models file defines no models")
    payload["_models"] = models
    payload["_engine"] = engine
    return payload


def run_clip(
    engine: str,
    model: ModelSpec,
    audio: Path,
    use_word_timestamps: bool,
    timeout: float = 600.0,
) -> dict:
    """Transcribe one clip and return text, timing and timestamp status.

    When word timestamps are requested the engine prints one timed word per
    line; the transcript is rebuilt from those words. If the timestamped run
    fails, the clip is retried without timestamps and reported as not covered.
    """
    started = time.perf_counter()
    result = _invoke(engine, model, audio, word_timestamps=use_word_timestamps, timeout=timeout)
    latency = time.perf_counter() - started
    if use_word_timestamps:
        parsed = parse_word_timestamps(result["stdout"])
        if parsed["ok"]:
            return {
                "ok": True,
                "text": " ".join(parsed["words"]),
                "latency_sec": round(latency, 3),
                "timestamps": True,
                "timed_words": parsed["timed_words"],
                "returncode": result["returncode"],
                "stderr": result["stderr"][-500:],
            }
        # Retry plain so a missing timestamp parser does not lose the transcript.
        started = time.perf_counter()
        result = _invoke(engine, model, audio, word_timestamps=False, timeout=timeout)
        latency = time.perf_counter() - started
    text = " ".join(result["stdout"].split())
    return {
        "ok": result["returncode"] == 0 and bool(text),
        "text": text,
        "latency_sec": round(latency, 3),
        "timestamps": False,
        "timed_words": 0,
        "returncode": result["returncode"],
        "stderr": result["stderr"][-500:],
    }


def _decode(raw: bytes) -> str:
    """Decode engine output as UTF-8.

    The engine always writes UTF-8, but Python's text mode on Windows decodes
    with the console codepage (cp1252), which turns Arabic into mojibake and
    silently corrupts every measurement. Decode explicitly instead.
    """
    return raw.decode("utf-8", errors="replace")


def _invoke(engine: str, model: ModelSpec, audio: Path, word_timestamps: bool, timeout: float) -> dict:
    command = [engine, "transcribe", model.path, str(audio)]
    command.extend(model.args)
    command.extend(["--language", model.language])
    if word_timestamps:
        command.append("--word-timestamps")
    completed = subprocess.run(command, capture_output=True, timeout=timeout)
    return {
        "returncode": completed.returncode,
        "stdout": _decode(completed.stdout),
        "stderr": _decode(completed.stderr),
    }


def preflight(engine: str, models: dict) -> list[str]:
    """Return a list of human-readable problems before running the suite."""
    problems: list[str] = []
    if not Path(engine).exists():
        problems.append(f"engine not found: {engine}")
    for model in models.values():
        if not Path(model.path).exists():
            problems.append(f"{model.id}: model not found: {model.path}")
        for arg in model.args:
            if arg.startswith("--vad-model="):
                vad_path = Path(arg.split("=", 1)[1])
                if not vad_path.exists():
                    problems.append(f"{model.id}: VAD model not found: {vad_path}")
    return problems
