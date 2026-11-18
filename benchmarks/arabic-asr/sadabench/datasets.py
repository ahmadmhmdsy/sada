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
import random
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
    "Perle-ai/ASR_Code_Switch": {
        "license": "MIT",
        "attribution": "ASR Code-Switching Benchmark (Perle AI), MIT; Abdoli et al. 2026, arXiv:2605.19069",
        "url": "https://huggingface.co/datasets/Perle-ai/ASR_Code_Switch",
    },
}

# Slices of the benchmark. 'pending' slices have no clip yet because no
# commercial-use-permissive corpus was found; they are kept visible so the gap
# is not mistaken for a measurement.
SLICES = {
    "msa": "Modern Standard Arabic read speech (Common Voice ar)",
    "egyptian": "Egyptian Arabic read speech (FLEURS ar_eg)",
    "latin-mixed": "Arabic read speech whose reference contains Latin proper nouns (Common Voice ar)",
    "technical": "Arabic/English code-switched technical speech (Perle AI Benchmark, MIT; scripted by native speakers)",
    "gulf": "Gulf Arabic (Saudi Najdi/Hijazi) conversational code-switched speech (Perle AI Benchmark, MIT)",
    "iraqi": "pending: no commercial-use-permissive Iraqi corpus with transcripts found",
    "levantine": "pending: no commercial-use-permissive Levantine corpus with transcripts found",
}

_LATIN_TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:[-'][A-Za-z0-9]+)*")

_ACRONYM_RE = re.compile(
    r"(?<![A-Za-z])(?:" + "|".join(ACRONYMS) + r")(?![A-Za-z])", re.IGNORECASE
)
_LATIN_RE = re.compile(r"[A-Za-z]")
_DIGITS_RE = re.compile(r"[0-9\u0660-\u0669\u06F0-\u06F9]")


def _open(url: str, timeout: float) -> bytes:
    """Open a URL with retries for transient rate limiting and server errors.

    The Hugging Face dataset viewer returns 429/5xx in bursts while its parquet
    conversion queues work; a build scans many pages, so give it a dozen tries
    with backoff, jitter and Retry-After support before failing.
    """
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    delay = 2.0
    for attempt in range(1, 13):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - https only
                return response.read()
        except urllib.error.HTTPError as error:
            if error.code != 429 and error.code < 500:
                raise
            if attempt == 12:
                raise
            retry_after = error.headers.get("Retry-After")
            base = float(retry_after) if retry_after and retry_after.isdigit() else delay
            wait = base + random.uniform(0.0, 1.0)
            print(f"  rate limited ({error.code}); retrying in {wait:.1f}s", file=sys.stderr)
            time.sleep(wait)
            delay = min(delay * 2, 60.0)
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            if attempt == 12:
                raise
            wait = delay + random.uniform(0.0, 1.0)
            print(f"  network error ({error}); retrying in {wait:.1f}s", file=sys.stderr)
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
    value = row.get(field) or row.get("transcript") or ""
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


def _perle_clips(counts: dict[str, int]) -> list[ClipSpec]:
    """Select Perle AI code-switch clips for the gulf and technical slices.

    The benchmark records which language pair each row belongs to; rows are
    picked evenly across the pair so the slice is not biased to the first page
    of the file. Saudi rows fill the gulf slice first, then the technical
    remainder; Egyptian rows fill the technical remainder. Every clip is a
    single utterance with a human reference transcript, recorded by native
    speakers (the audio is not scraped from other corpora).
    """
    dataset = "Perle-ai/ASR_Code_Switch"
    config, split = "default", "train"
    revision = dataset_revision(dataset)
    pair_for_slice = {
        "gulf": "Saudi Arabic (Najdi/Hijazi)–English",
        "egyptian": "Egyptian Arabic–English",
    }
    remaining = dict(counts)
    rows_by_pair: dict[str, list[tuple[int, dict]]] = {pair: [] for pair in pair_for_slice.values()}
    offset = 0
    page = 100
    while True:
        rows = dataset_rows(dataset, config, split, offset, page)
        if not rows:
            break
        for row_idx, row in rows:
            pair = str(row.get("language_pair", ""))
            if pair in rows_by_pair:
                rows_by_pair[pair].append((row_idx, row))
        offset += page
        time.sleep(0.5)
    clips: list[ClipSpec] = []
    # Gulf first: Saudi code-switched speech.
    saudi = rows_by_pair[pair_for_slice["gulf"]]
    need = remaining.get("gulf", 0)
    for position, (row_idx, row) in enumerate(_evenly_spaced(saudi, need)):
        reference = _row_reference(row, "perle")
        clips.append(
            ClipSpec(
                f"gulf-perle-{position + 1:03d}",
                "gulf",
                reference,
                dataset,
                config,
                split,
                row_idx,
                revision,
            )
        )
    # Technical remainder: Egyptian first, then any Saudi rows not used above.
    used_saudi = {row_idx for row_idx, _ in _evenly_spaced(saudi, need)}
    technical: list[tuple[int, dict, str]] = []
    egyptian = rows_by_pair[pair_for_slice["egyptian"]]
    technical_need = remaining.get("technical", 0)
    egyptian_need = min(len(egyptian), technical_need)
    for row_idx, row in _evenly_spaced(egyptian, egyptian_need):
        technical.append((row_idx, row, "egyptian"))
    extra_saudi = [item for item in saudi if item[0] not in used_saudi]
    for row_idx, row in _evenly_spaced(extra_saudi, technical_need - len(technical)):
        technical.append((row_idx, row, "saudi"))
    for position, (row_idx, row, origin) in enumerate(technical):
        reference = _row_reference(row, "perle")
        clips.append(
            ClipSpec(
                f"technical-perle-{position + 1:03d}",
                "technical",
                reference,
                dataset,
                config,
                split,
                row_idx,
                revision,
            )
        )
    return clips


def _evenly_spaced(rows: list[tuple[int, dict]], count: int) -> list[tuple[int, dict]]:
    """Pick count rows spread evenly across a list."""
    if count <= 0 or not rows:
        return []
    count = min(count, len(rows))
    if count == 1:
        return [rows[0]]
    step = (len(rows) - 1) / (count - 1)
    return [rows[round(index * step)] for index in range(count)]


SLICE_COUNTS = {"msa": "msa_count", "latin-mixed": "latin_count", "egyptian": "egyptian_count"}


def reused_clips(reuse_manifest: dict, counts: dict[str, int]) -> dict[str, list[dict]]:
    """Clip entries an existing manifest already pins for the given slice counts.

    Rebuilding the manifest re-scans the Common Voice test split for Latin-mixed
    rows (up to 110 pages on a rate-limited viewer) only to find the same rows
    again. When an existing manifest already selected exactly the requested
    number of clips for a slice, those entries are reproducible and are reused;
    only slices whose count changed are rebuilt.
    """
    by_slice: dict[str, list[dict]] = {}
    for clip in reuse_manifest.get("clips", []):
        slice_name = clip.get("slice")
        if slice_name in SLICE_COUNTS:
            by_slice.setdefault(slice_name, []).append(clip)
    reused: dict[str, list[dict]] = {}
    for slice_name, attribute in SLICE_COUNTS.items():
        wanted = counts[attribute]
        if wanted > 0 and len(by_slice.get(slice_name, [])) == wanted:
            reused[slice_name] = by_slice[slice_name]
    return reused


def build_manifest(
    msa_count: int = 30,
    egyptian_count: int = 20,
    latin_count: int = 10,
    gulf_count: int = 15,
    technical_count: int = 15,
    reuse_manifest: dict | None = None,
) -> dict:
    """Build a new clip manifest by selecting rows from the pinned datasets."""
    counts = {
        "msa_count": msa_count,
        "egyptian_count": egyptian_count,
        "latin_count": latin_count,
    }
    reused = reused_clips(reuse_manifest, counts) if reuse_manifest else {}
    fresh: dict[str, list[ClipSpec]] = {}
    if "msa" not in reused:
        fresh["msa"] = _common_voice_clips(msa_count, "msa")
    if "latin-mixed" not in reused:
        fresh["latin-mixed"] = _latin_clips(latin_count)
    if "egyptian" not in reused:
        fresh["egyptian"] = _fleurs_clips(egyptian_count)
    if gulf_count or technical_count:
        perle = _perle_clips({"gulf": gulf_count, "technical": technical_count})
        fresh["gulf"] = [clip for clip in perle if clip.slice == "gulf"]
        fresh["technical"] = [clip for clip in perle if clip.slice == "technical"]
    entries: list[dict] = []
    for slice_name in ("msa", "latin-mixed", "egyptian", "gulf", "technical"):
        entries.extend(reused.get(slice_name, []))
        entries.extend(clip.to_manifest() for clip in fresh.get(slice_name, []))
    if not entries:
        raise RuntimeError("no clips selected; check dataset availability")
    return {
        "version": 1,
        "created": time.strftime("%Y-%m-%d"),
        "policy": "commercial-use-permissive corpora only; audio is fetched, never committed",
        "slices": SLICES,
        "clips": entries,
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
            reference = " ".join(
                str(row.get("sentence") or row.get("transcription") or row.get("transcript") or "").split()
            )
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
