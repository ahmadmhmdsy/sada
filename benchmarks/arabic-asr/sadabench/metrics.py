"""Word/character error rates and the auxiliary Arabic ASR metrics."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .normalize import ACRONYMS, characters, strip_latin_separators, words

_TIMESTAMP_LINE = re.compile(
    r"^\[(\d{2}):(\d{2}):(\d{2})\.(\d{3}) --> (\d{2}):(\d{2}):(\d{2})\.(\d{3})\]\s*(.*)$"
)

_LATIN_TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:[-'][A-Za-z0-9]+)*")


@dataclass
class EditStats:
    """Edit operations between a reference and a hypothesis."""

    substitutions: int = 0
    deletions: int = 0
    insertions: int = 0
    reference_length: int = 0
    hits: int = 0
    hypothesis_empty: bool = False

    @property
    def errors(self) -> int:
        return self.substitutions + self.deletions + self.insertions

    def accumulate(self, other: "EditStats") -> None:
        self.substitutions += other.substitutions
        self.deletions += other.deletions
        self.insertions += other.insertions
        self.reference_length += other.reference_length
        self.hits += other.hits
        self.hypothesis_empty = self.hypothesis_empty or other.hypothesis_empty


def _edit_stats(reference: list[str], hypothesis: list[str]) -> EditStats:
    """Levenshtein distance with operation counts (O(n*m) time, O(m) memory)."""
    ref_n, hyp_n = len(reference), len(hypothesis)
    stats = EditStats(reference_length=ref_n, hypothesis_empty=hyp_n == 0 and ref_n > 0)
    if ref_n == 0:
        stats.insertions = hyp_n
        return stats

    prev_cost = list(range(hyp_n + 1))
    prev_sub = [0] * (hyp_n + 1)
    prev_del = [0] * (hyp_n + 1)
    prev_ins = list(range(hyp_n + 1))
    for i in range(1, ref_n + 1):
        cost = [i] + [0] * hyp_n
        sub = [0] * (hyp_n + 1)
        dele = [i] + [0] * hyp_n
        ins = [0] * (hyp_n + 1)
        for j in range(1, hyp_n + 1):
            same = reference[i - 1] == hypothesis[j - 1]
            diag = prev_cost[j - 1] + (0 if same else 1)
            up = prev_cost[j] + 1
            left = cost[j - 1] + 1
            best = min(diag, up, left)
            cost[j] = best
            if best == diag:
                sub[j] = prev_sub[j - 1] + (0 if same else 1)
                dele[j] = prev_del[j - 1]
                ins[j] = prev_ins[j - 1]
            elif best == up:
                sub[j] = prev_sub[j]
                dele[j] = prev_del[j] + 1
                ins[j] = prev_ins[j]
            else:
                sub[j] = sub[j - 1]
                dele[j] = dele[j - 1]
                ins[j] = ins[j - 1] + 1
        prev_cost, prev_sub, prev_del, prev_ins = cost, sub, dele, ins

    stats.substitutions = prev_sub[hyp_n]
    stats.deletions = prev_del[hyp_n]
    stats.insertions = prev_ins[hyp_n]
    stats.hits = ref_n - stats.substitutions - stats.deletions
    return stats


def word_stats(reference: str, hypothesis: str) -> EditStats:
    """WER edit statistics for one clip."""
    return _edit_stats(words(reference), words(hypothesis))


def char_stats(reference: str, hypothesis: str) -> EditStats:
    """CER edit statistics for one clip (spaces are not scored)."""
    return _edit_stats(characters(reference), characters(hypothesis))


def rate(stats: EditStats) -> float:
    """Percentage error rate for a stats record."""
    if stats.reference_length == 0:
        return 100.0 if stats.hypothesis_empty else 0.0
    return 100.0 * stats.errors / stats.reference_length


def acronym_report(reference: str, hypothesis: str) -> tuple[int, int]:
    """Return (occurrences, preserved) of Latin acronyms for one clip.

    An acronym counts as preserved when it appears in the hypothesis after
    lowercasing and removing separators, so 'B.D.F' satisfies 'BDF' but a
    transliteration such as 'بي ديف' does not.
    """
    if not reference:
        return 0, 0
    occurrences = 0
    preserved = 0
    compact_hyp = strip_latin_separators(hypothesis)
    for acronym in ACRONYMS:
        pattern = r"(?<![A-Za-z])" + r"\.?".join(re.escape(ch) for ch in acronym) + r"(?![A-Za-z])"
        for _ in re.finditer(pattern, reference, flags=re.IGNORECASE):
            occurrences += 1
            if acronym.lower() in compact_hyp:
                preserved += 1
    return occurrences, preserved


def latin_report(reference: str, hypothesis: str) -> tuple[int, int]:
    """Return (occurrences, preserved) of Latin-script words in the reference.

    This measures how an Arabic engine handles code-switched names and terms
    (proper nouns, brand names, acronyms) without requiring the technical
    code-switching slice that no permissive corpus currently provides.
    """
    if not reference:
        return 0, 0
    compact_hyp = strip_latin_separators(hypothesis)
    occurrences = preserved = 0
    for match in _LATIN_TOKEN.finditer(reference):
        token = match.group(0)
        # A lone capital letter or roman numeral is not meaningful here.
        if len(token) < 2:
            continue
        occurrences += 1
        if strip_latin_separators(token) in compact_hyp:
            preserved += 1
    return occurrences, preserved


def parse_word_timestamps(text: str) -> dict:
    """Parse engine word-timestamp output.

    Returns words, the number of timed words, the fraction of non-empty lines
    that carried a timestamp, monotonicity and an overall ok flag.
    """
    parsed: list[dict] = []
    other_lines = 0
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        match = _TIMESTAMP_LINE.match(line)
        if not match:
            other_lines += 1
            continue
        start = _seconds(match.group(1), match.group(2), match.group(3), match.group(4))
        end = _seconds(match.group(5), match.group(6), match.group(7), match.group(8))
        parsed.append({"word": match.group(9).strip(), "start": start, "end": end})

    total_lines = len(parsed) + other_lines
    coverage = (len(parsed) / total_lines) if total_lines else 0.0
    monotonic = all(
        parsed[i]["start"] >= parsed[i - 1]["start"] - 1e-6
        and parsed[i]["end"] >= parsed[i]["start"]
        for i in range(1, len(parsed))
    ) and all(p["end"] >= p["start"] for p in parsed)
    return {
        "words": [p["word"] for p in parsed if p["word"]],
        "timed_words": len(parsed),
        "coverage": coverage,
        "monotonic": monotonic,
        "ok": bool(parsed) and monotonic and coverage >= 0.99,
    }


def _seconds(hours: str, minutes: str, seconds: str, millis: str) -> float:
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(millis) / 1000.0


@dataclass
class Score:
    """Aggregated scores for a set of clips (one model, one slice or overall)."""

    clips: int = 0
    wer: EditStats = field(default_factory=EditStats)
    cer: EditStats = field(default_factory=EditStats)
    acronym_occurrences: int = 0
    acronym_preserved: int = 0
    latin_occurrences: int = 0
    latin_preserved: int = 0
    timestamps_ok: int = 0
    timestamps_clips: int = 0
    audio_seconds: float = 0.0
    latency_seconds: float = 0.0

    def add(
        self,
        reference: str,
        hypothesis: str,
        audio_seconds: float,
        latency_seconds: float,
        timestamps_ok: bool,
    ) -> None:
        self.clips += 1
        self.wer.accumulate(word_stats(reference, hypothesis))
        self.cer.accumulate(char_stats(reference, hypothesis))
        occurrences, preserved = acronym_report(reference, hypothesis)
        self.acronym_occurrences += occurrences
        self.acronym_preserved += preserved
        latin_occurrences, latin_preserved = latin_report(reference, hypothesis)
        self.latin_occurrences += latin_occurrences
        self.latin_preserved += latin_preserved
        self.timestamps_clips += 1
        self.timestamps_ok += 1 if timestamps_ok else 0
        self.audio_seconds += audio_seconds
        self.latency_seconds += latency_seconds

    def as_dict(self) -> dict:
        return {
            "clips": self.clips,
            "wer_pct": round(rate(self.wer), 2),
            "cer_pct": round(rate(self.cer), 2),
            "substitutions": self.wer.substitutions,
            "deletions": self.wer.deletions,
            "insertions": self.wer.insertions,
            "reference_words": self.wer.reference_length,
            "acronym_occurrences": self.acronym_occurrences,
            "acronym_preserved_pct": (
                round(100.0 * self.acronym_preserved / self.acronym_occurrences, 1)
                if self.acronym_occurrences
                else None
            ),
            "latin_occurrences": self.latin_occurrences,
            "latin_preserved_pct": (
                round(100.0 * self.latin_preserved / self.latin_occurrences, 1)
                if self.latin_occurrences
                else None
            ),
            "timestamps_ok_pct": (
                round(100.0 * self.timestamps_ok / self.timestamps_clips, 1)
                if self.timestamps_clips
                else None
            ),
            "audio_seconds": round(self.audio_seconds, 2),
            "latency_seconds": round(self.latency_seconds, 2),
            "rtf": (
                round(self.latency_seconds / self.audio_seconds, 3)
                if self.audio_seconds
                else None
            ),
        }
