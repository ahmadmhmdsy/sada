"""Text normalisation for Arabic ASR scoring.

The goal is to remove differences that are not meaningful for recognition quality,
following the rules in the models council evidence plan (docs/MODELS-COUNCIL.md
section 6, step zero E2):

* drop diacritics (tashkeel) and tatweel;
* unify hamza forms and alef maqsura;
* normalise Arabic-Indic digits to ASCII digits;
* replace punctuation with spaces, collapse whitespace and lowercase Latin text.

Ta marbuta is intentionally kept as-is: mapping it to haa would hide real spelling
mistakes that matter for dictation.
"""

from __future__ import annotations

import re
import unicodedata

# Arabic combining marks: harakat, tanween, shadda, sukun, superscript alef and
# Quranic annotation signs.
_DIACRITICS = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]")
_TATWEEL = "\u0640"

_ALEF_VARIANTS = {
    "\u0622": "\u0627",  # alef with madda
    "\u0623": "\u0627",  # alef with hamza above
    "\u0625": "\u0627",  # alef with hamza below
    "\u0671": "\u0627",  # alef wasla
    "\u0672": "\u0627",
    "\u0673": "\u0627",
}
_HAMZA_CARRIERS = {
    "\u0624": "\u0648",  # waw with hamza -> waw
    "\u0626": "\u064A",  # yeh with hamza -> yeh
}
_ALEF_MAQSURA = "\u0649"  # -> yeh
_YEH = "\u064A"

_DIGITS = str.maketrans(
    "\u0660\u0661\u0662\u0663\u0664\u0665\u0666\u0667\u0668\u0669"
    "\u06F0\u06F1\u06F2\u06F3\u06F4\u06F5\u06F6\u06F7\u06F8\u06F9",
    "01234567890123456789",
)

# Latin acronyms tracked by the benchmark; extend together with clip selection.
ACRONYMS = (
    "GPU",
    "CPU",
    "RAM",
    "SSD",
    "USB",
    "PDF",
    "SRT",
    "VTT",
    "MCP",
    "API",
    "HTML",
    "JSON",
    "WAV",
    "ASR",
    "LLM",
    "AI",
    "BDF",
    "FFMPEG",
    "GGUF",
)


def strip_diacritics(text: str) -> str:
    """Remove Arabic diacritics and tatweel."""
    return _DIACRITICS.sub("", text).replace(_TATWEEL, "")


def normalize(text: str) -> str:
    """Return the normalised text used for word/character error rates."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = strip_diacritics(text)
    text = "".join(_ALEF_VARIANTS.get(ch, ch) for ch in text)
    text = "".join(_HAMZA_CARRIERS.get(ch, ch) for ch in text)
    text = text.replace(_ALEF_MAQSURA, _YEH)
    text = text.translate(_DIGITS)
    text = text.lower()

    out = []
    for ch in text:
        if ch.isalnum():
            out.append(ch)
        else:
            out.append(" ")
    return re.sub(r"\s+", " ", "".join(out)).strip()


def words(text: str) -> list[str]:
    """Normalised word tokens."""
    normalised = normalize(text)
    return normalised.split(" ") if normalised else []


def characters(text: str) -> list[str]:
    """Normalised characters without spaces (for CER)."""
    return [ch for ch in normalize(text) if not ch.isspace()]


def strip_latin_separators(text: str) -> str:
    """Lowercase and remove punctuation/spaces, used for acronym matching.

    'B.D.F' and 'B D F' both become 'bdf', so an engine that spells an acronym
    with dots still counts as preserving it.
    """
    return "".join(ch for ch in text.lower() if ch.isalnum())
