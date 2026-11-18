"""App-level Arabic post-processing: the Python mirror of desktop/src/lib/arabic-text.ts.

The benchmark scores raw engine output, but the app applies these rules before showing or exporting
text, so this module lets the harness report what users actually see. The canonical cases live in
fixtures/arabic-postprocess-cases.json and are asserted by both test suites; keep the rule order in
sync with the TypeScript implementation.
"""

from __future__ import annotations

import re

_ARABIC_CHAR = "[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]"
_HAS_ARABIC = re.compile(_ARABIC_CHAR)
_NO_ARABIC_BEFORE = "(?<!" + _ARABIC_CHAR + ")"
_NO_ARABIC_AFTER = "(?!" + _ARABIC_CHAR + ")"


def _term(latin: str, *segments: tuple[str, ...]) -> tuple[re.Pattern[str], str]:
    """One rule for a term whisper writes out in Arabic letters (spaces optional, article swallowed)."""
    body = "[ \\t]*".join("(?:" + "|".join(alternatives) + ")" for alternatives in segments)
    return (re.compile(_NO_ARABIC_BEFORE + "(?:ال)?" + body + _NO_ARABIC_AFTER), latin)


def _joined(latin: str, *spellings: str) -> tuple[re.Pattern[str], str]:
    """One rule for a joined spelling whose syllables overlap when split."""
    return (
        re.compile(_NO_ARABIC_BEFORE + "(?:ال)?(?:" + "|".join(spellings) + ")" + _NO_ARABIC_AFTER),
        latin,
    )


# Spellings whisper.cpp produces for terms that are normally written in Latin in Arabic text.
# Order matters, in the same way as in the TypeScript list: longer terms before their prefixes.
_TERMS: list[tuple[re.Pattern[str], str]] = [
    _term("HTTPS", ("إتش", "اتش"), ("تي", "تى"), ("تي", "تى"), ("بي", "بى"), ("إس", "اس", "أس")),
    _term("HTTP", ("إتش", "اتش"), ("تي", "تى"), ("تي", "تى"), ("بي", "بى")),
    _term("HTML", ("إتش", "اتش"), ("تي", "تى"), ("إم", "ام", "أم"), ("إل", "ال", "أل")),
    # Joined spellings overlap ("جيبيو" is جي + بيو), so they need their own rules first.
    _joined("GPU", "جيبيو", "جيبْيو"),
    _joined("CPU", "سيبيو", "سيبْيو"),
    _term("GPU", ("جي", "جى"), ("بي", "بى"), ("يو", "يوا")),
    _term("CPU", ("سي", "سى"), ("بي", "بى"), ("يو", "يوا")),
    _term("PDF", ("بي", "بى"), ("دي", "دى"), ("إف", "اف", "أف", "ف")),
    _joined("SRT", "سورتي", "سورتى"),
    _term("SRT", ("إس", "اس", "أس"), ("آر", "ار", "أر"), ("تي", "تى")),
    _term("VTT", ("في", "فى"), ("تي", "تى"), ("تي", "تى")),
    _joined("JSON", "جيسون", "جسون", "جيسُن"),
    _term("API", ("إيه", "ايه", "إي"), ("بي", "بى"), ("آي", "اي", "أي")),
    _term("FFmpeg", ("إف", "اف", "أف"), ("إف", "اف", "أف"), ("إم", "ام", "أم"), ("بيغ", "بيج", "بغ")),
    _joined("Whisper", "ويسبر", "ويسپر", "ويسْبر"),
    _term("URL", ("يو", "يوا"), ("آر", "ار", "أر"), ("إل", "ال", "أل")),
    _term("SQL", ("إس", "اس", "أس"), ("كيو",), ("إل", "ال", "أل")),
    _term("CSS", ("سي", "سى"), ("إس", "اس", "أس"), ("إس", "اس", "أس")),
    _term("USB", ("يو", "يوا"), ("إس", "اس", "أس"), ("بي", "بى")),
    _term("VPN", ("في", "فى"), ("بي", "بى"), ("إن", "ان", "أن")),
    _term("Wi-Fi", ("واي", "واى"), ("فاي", "فاى")),
    _term("GitHub", ("غيت", "جيت"), ("هاب", "هب")),
]

# ASCII punctuation that Arabic typography replaces with its own codepoint.
_PUNCTUATION: list[tuple[re.Pattern[str], str]] = [
    (re.compile("(" + _ARABIC_CHAR + ")[ \\t]*,[ \\t]*"), r"\1، "),
    (re.compile("(" + _ARABIC_CHAR + ")[ \\t]*\\?[ \\t]*"), r"\1؟ "),
    (re.compile("(" + _ARABIC_CHAR + ")[ \\t]*;[ \\t]*"), r"\1؛ "),
]

_SPACE_BEFORE_PUNCTUATION = re.compile("[ \\t]+([،؛؟])")
_DOUBLE_SPACES = re.compile("[ \\t]{2,}")
_TRAILING_SPACES = re.compile("[ \\t]+$", re.MULTILINE)


def postprocess(text: str) -> str:
    """Apply the app's Arabic clean-up to one transcript text.

    Returns the input untouched when there is no Arabic in it, exactly like the TypeScript module.
    """
    if not text or not _HAS_ARABIC.search(text):
        return text
    result = text
    for pattern, replacement in _TERMS:
        result = pattern.sub(replacement, result)
    for pattern, replacement in _PUNCTUATION:
        result = pattern.sub(replacement, result)
    result = _SPACE_BEFORE_PUNCTUATION.sub(r"\1", result)
    result = _DOUBLE_SPACES.sub(" ", result)
    result = _TRAILING_SPACES.sub("", result)
    return result


def find_terms(text: str) -> list[dict]:
    """Return glossary matches in text without rewriting it (used by the corpus safety test)."""
    found: list[dict] = []
    for pattern, replacement in _TERMS:
        for match in pattern.finditer(text or ""):
            found.append({"term": replacement, "match": match.group(0), "start": match.start()})
    return found
