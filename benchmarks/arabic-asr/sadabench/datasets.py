"""Dataset access and clip manifest handling for the Arabic ASR benchmark.

Clips are never committed to the repository. The committed manifest records the
dataset, split and row offset plus the reference transcript and licence; the
fetch step downloads the audio at run time and verifies the reference text again
so a changed dataset row cannot silently corrupt a measurement.

Sources currently used (commercial-use-permissive only):

* Common Voice 18 Arabic (CC0) -- read MSA sentences plus technical sentences.
* FLEURS ar_eg (CC BY 4.0) -- Egyptian Arabic read speech.

Iraqi, Gulf and Levantine corpora are not included while no corpus with a
commercial-use licence is available; research-only corpora (for example MADAR)
are excluded by the fork's licence policy.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import wave
from dataclasses import dataclass
from pathlib import Path

from .normalize import ACRONYMS, normalize

DATASETS_SERVER = "https://datasets-server.huggingface.co"
HF_API = "https://huggingface.co/api/datasets"
USER_AGENT = "sada-arabic-asr-benchmark/1.0 (+https://github.com/alshahia/sada)"

COMMERCIAL_LICENCES = {"cc0-1.0", "cc-by-4.0", "cc-by-sa-4.0", "mit", "apache-2.0"}

DATASET_LICENCES = {
    "MohamedRashad/common-voice-18-arabic": {
        "license": "CC0-1.0",
        "attribution": "Common Voice 18.0 Arabic (Mozilla), CC0 1.0",
        "url": "https://commonvoice.mozilla.org/",
    },
    "google/fleurs": {
        "license": "CC-BY-4.0",
        "attribution": "FLEURS ar_eg (Google), CC BY 4.0; Conneau et al. 2022",
        "url": "https://huggingface.co/datasets/google/fleurs",
    },
}

# Slices of the benchmark. 'pending' slices have no clip yet because no
# commercial-use-permissive corpus was found; they are kept visible so the gap
# is not mistaken for a measurement.
SLICES = {
    "msa": "Modern Standard Arabic read speech (Common Voice ar)",
    "egyptian": "Egyptian Arabic read speech (FLEURS ar_eg)",
    "latin-mixed": "Arabic read speech whose reference contains Latin proper nouns (Common Voice ar)",
    "technical": "pending: no commercial-use-permissive Arabic/English technical speech corpus found",
    "iraqi": "pending: no commercial-use-permissive Iraqi corpus found",
    "gulf": "pending: no commercial-use-permissive Gulf corpus found",
    "levantine": "pending: no commercial-use-permissive Levantine corpus found",
}

_LATIN_TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:[-'][A-Za-z0-9]+)*")

_ACRONYM_RE = re.compile(
    r"(?<![A-Za-z])(?:" + "|".join(ACRONYMS) + r")(?![A-Za-z])", re.IGNORECASE
)
_LATIN_RE = re.compile(r"[A-Za-z]")
_DIGITS_RE = re.compile(r"[0-9\u0660-\u0669\u06F0-\u06F9]")


def _open(url: str, timeout: float) -> bytes:
    """Open a URL with retries for transient rate limiting and server errors."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    delay = 2.0
    for attempt in range(1, 7):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - https only
                return response.read()
        except urllib.error.HTTPError as error:
            if error.code != 429 and error.code < 500:
                raise
            if attempt == 6:
                raise
            retry_after = error.headers.get("Retry-After")
            wait = float(retry_after) if retry_after and retry_after.isdigit() else delay
            print(f"  rate limited ({error.code}); retrying in {wait:.0f}s", file=sys.stderr)
            time.sleep(wait)
            delay = min(delay * 2, 60.0)
    raise RuntimeError("unreachable")


def http_json(url: str, timeout: float = 90.0) -> dict:
    return json.loads(_open(url, timeout).decode("utf-8"))


def http_download(url: str, destination: Path, timeout: float = 120.0) -> None:
    destination.write_bytes(_open(url, timeout))


def _quote(value: str) -> str:
    return urllib.parse.quote(value, safe="")


def dataset_revision(dataset: str) -> str:
    """Current Hub revision (commit sha) of a dataset."""
    info = http_json(f"{HF_API}/{dataset}")
    return info.get("sha", "unknown")


def dataset_rows(dataset: str, config: str, split: str, offset: int, length: int) -> list[tuple[int, dict]]:
    """Rows from the datasets-server viewer, as (row index, row) tuples."""
    url = (
        f"{DATASETS_SERVER}/rows?dataset={_quote(dataset)}&config={_quote(config)}"
        f"&split={_quote(split)}&offset={offset}&length={length}"
    )
    payload = http_json(url)
    return [(item["row_idx"], item["row"]) for item in payload.get("rows", [])]


def dataset_size(dataset: str, config: str) -> dict:
    """Split sizes for a dataset config."""
    payload = http_json(f"{DATASETS_SERVER}/size?dataset={_quote(dataset)}&config={_quote(config)}")
    return {split["split"]: split.get("num_rows", 0) for split in payload["size"]["splits"]}


def qualifies_msa(sentence: str) -> bool:
    """Read MSA sentence suitable for the MSA slice (no Latin, no digits)."""
    if not sentence:
        return False
    stripped = sentence.strip()
    if not (40 <= len(stripped) <= 140):
        return False
    if _LATIN_RE.search(stripped) or _DIGITS_RE.search(stripped):
        return False
    return len(normalize(stripped)) >= 30


def acronym_hits(sentence: str) -> int:
    """Number of tracked Latin acronyms in a sentence."""
    if not sentence:
        return 0
    return len(_ACRONYM_RE.findall(sentence))


def _row_audio_url(row: dict) -> str:
    audio = row.get("audio")
    if isinstance(audio, list) and audio:
        return audio[0]["src"]
    if isinstance(audio, dict):
        return audio["src"]
    raise ValueError("row has no audio")


def _row_reference(row: dict, kind: str) -> str:
    field = "sentence" if kind == "common_voice" else "transcription"
    value = row.get(field) or ""
    return " ".join(str(value).split())


@dataclass
class ClipSpec:
    """One selected clip before download."""

    id: str
    slice: str
    reference: str
    dataset: str
    config: str
    split: str
    offset: int
    revision: str

    def to_manifest(self) -> dict:
        meta = DATASET_LICENCES.get(self.dataset, {"license": "unknown", "attribution": "unknown", "url": ""})
        return {
            "id": self.id,
            "slice": self.slice,
            "reference": self.reference,
            "source": {
                "dataset": self.dataset,
                "config": self.config,
                "split": self.split,
                "offset": self.offset,
                "revision": self.revision,
                "license": meta["license"],
                "attribution": meta["attribution"],
                "url": meta["url"],
            },
        }


def _common_voice_clips(count: int, kind: str) -> list[ClipSpec]:
    dataset = "MohamedRashad/common-voice-18-arabic"
    config = "default"
    revision = dataset_revision(dataset)
    # Technical acronyms are rare in read speech, so that slice scans more splits.
    splits = ["validation"] if kind == "msa" else ["validation", "test", "other"]
    clips: list[ClipSpec] = []
    page = 100
    for split in splits:
        if len(clips) >= count:
            break
        offset = 0
        pages = 0
        while len(clips) < count and pages < 80:
            rows = dataset_rows(dataset, config, split, offset, page)
            if not rows:
                break
            for row_idx, row in rows:
                if len(clips) >= count:
                    break
                reference = _row_reference(row, "common_voice")
                if row.get("up_votes", 0) < 2 or row.get("down_votes", 0) != 0:
                    continue
                if kind == "technical":
                    if acronym_hits(reference) == 0 or len(reference) > 180:
                        continue
                    slice_name = "technical"
                else:
                    if not qualifies_msa(reference) or acronym_hits(reference) > 0:
                        continue
                    slice_name = "msa"
                number = len([c for c in clips if c.slice == slice_name]) + 1
                clip_id = f"{slice_name}-cv-{number:03d}"
                clips.append(
                    ClipSpec(clip_id, slice_name, reference, dataset, config, split, row_idx, revision)
                )
            offset += page
            pages += 1
            time.sleep(0.8)
    return clips


def _latin_clips(count: int) -> list[ClipSpec]:
    """Select Common Voice rows whose reference contains Latin proper nouns."""
    dataset = "MohamedRashad/common-voice-18-arabic"
    config, split = "default", "test"
    revision = dataset_revision(dataset)
    clips: list[ClipSpec] = []
    offset = 0
    page = 100
    pages = 0
    while len(clips) < count and pages < 110:
        rows = dataset_rows(dataset, config, split, offset, page)
        if not rows:
            break
        for row_idx, row in rows:
            if len(clips) >= count:
                break
            reference = _row_reference(row, "common_voice")
            if row.get("up_votes", 0) < 2 or row.get("down_votes", 0) != 0:
                continue
            tokens = [token for token in _LATIN_TOKEN.findall(reference) if len(token) >= 2]
            if not tokens:
                continue
            clips.append(
                ClipSpec(
                    f"latin-cv-{len(clips) + 1:03d}",
                    "latin-mixed",
                    reference,
                    dataset,
                    config,
                    split,
                    row_idx,
                    revision,
                )
            )
        offset += page
        pages += 1
        time.sleep(0.8)
    return clips


def _fleurs_clips(count: int) -> list[ClipSpec]:
    dataset = "google/fleurs"
    config, split = "ar_eg", "test"
    revision = dataset_revision(dataset)
    total = dataset_size(dataset, config).get(split, 0)
    if total == 0:
        raise RuntimeError("FLEURS ar_eg test split has no rows")
    wanted = sorted({round(i * (total - 1) / max(count - 1, 1)) for i in range(count)})
    clips: list[ClipSpec] = []
    # Fetch in pages of 100 rows.
    for page_start in range(0, total, 100):
        needed = [o for o in wanted if page_start <= o < page_start + 100]
        if not needed:
            continue
        rows = dataset_rows(dataset, config, split, page_start, 100)
        by_offset = dict(rows)
        for offset in needed:
            row = by_offset.get(offset)
            if row is None:
                continue
            reference = _row_reference(row, "fleurs")
            if len(normalize(reference)) < 10:
                continue
            clips.append(
                ClipSpec(
                    f"egyptian-fleurs-{len(clips) + 1:03d}",
                    "egyptian",
                    reference,
                    dataset,
                    config,
                    split,
                    offset,
                    revision,
                )
            )
        time.sleep(0.8)
    return clips


def build_manifest(
    msa_count: int = 30,
    egyptian_count: int = 20,
    latin_count: int = 10,
    technical_count: int = 10,
) -> dict:
    """Build a new clip manifest by selecting rows from the pinned datasets.

    The technical slice is only populated when a permissive code-switching
    corpus is available; by default it selects nothing and stays pending.
    """
    clips = _common_voice_clips(msa_count, "msa")
    clips += _latin_clips(latin_count)
    clips += _fleurs_clips(egyptian_count)
    if technical_count:
        clips += _common_voice_clips(technical_count, "technical")
    if not clips:
        raise RuntimeError("no clips selected; check dataset availability")
    return {
        "version": 1,
        "created": time.strftime("%Y-%m-%d"),
        "policy": "commercial-use-permissive corpora only; audio is fetched, never committed",
        "slices": SLICES,
        "clips": [clip.to_manifest() for clip in clips],
    }


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as handle:
        return handle.getnframes() / float(handle.getframerate())


@dataclass
class FetchResult:
    fetched: int
    skipped: int
    failed: list[str]


def fetch_clips(
    manifest: dict,
    audio_dir: Path,
    ffmpeg: str,
    force: bool = False,
) -> FetchResult:
    """Download and convert every clip in the manifest to 16 kHz mono WAV."""
    audio_dir.mkdir(parents=True, exist_ok=True)
    lock_path = audio_dir / "manifest.lock.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8")) if lock_path.exists() else {}
    fetched = skipped = 0
    failed: list[str] = []
    for clip in manifest["clips"]:
        clip_id = clip["id"]
        destination = audio_dir / f"{clip_id}.wav"
        if destination.exists() and not force:
            skipped += 1
            continue
        source = clip["source"]
        try:
            rows = dataset_rows(source["dataset"], source["config"], source["split"], source["offset"], 1)
            row = next((row for offset, row in rows if offset == source["offset"]), None)
            if row is None:
                raise ValueError("row not found at stored offset")
            reference = " ".join(str(row.get("sentence") or row.get("transcription") or "").split())
            if reference != clip["reference"]:
                raise ValueError("dataset row text no longer matches the manifest reference")
            audio_url = _row_audio_url(row)
            with tempfile.TemporaryDirectory() as temp_dir:
                raw = Path(temp_dir) / "audio.src"
                http_download(audio_url, raw)
                command = [
                    ffmpeg, "-y", "-v", "error", "-i", str(raw),
                    "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(destination),
                ]
                completed = subprocess.run(command, capture_output=True, text=True, timeout=180)
                if completed.returncode != 0:
                    raise RuntimeError(f"ffmpeg failed: {completed.stderr.strip()[:200]}")
            duration = _wav_duration(destination)
            digest = hashlib.sha256(destination.read_bytes()).hexdigest()
            lock[clip_id] = {
                "sha256": digest,
                "duration_sec": round(duration, 3),
                "reference": clip["reference"],
            }
            lock_path.write_text(json.dumps(lock, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            fetched += 1
            print(f"  {clip_id}: {duration:.1f}s {clip['slice']}")
        except Exception as error:  # noqa: BLE001 - report per clip and continue
            failed.append(f"{clip_id}: {error}")
            print(f"  {clip_id}: FAILED {error}")
        time.sleep(0.15)
    return FetchResult(fetched=fetched, skipped=skipped, failed=failed)
