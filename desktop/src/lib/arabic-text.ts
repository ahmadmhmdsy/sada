/**
 * Arabic post-processing for transcripts.
 *
 * Whisper's Arabic output is usable but typographically raw: it emits ASCII punctuation, keeps
 * spaces before commas, and transliterates acronyms it has rarely seen written (GPU becomes
 * "جي بي يو"). This module fixes those in one place so every surface — live segments, saved
 * projects, dictation, phone handoff and every export — shows the same polished text.
 *
 * The rules are deliberately lossless: no words are added, removed or reordered, and Latin text,
 * numbers and file names are left alone. Everything here is idempotent, so applying it twice is
 * the same as applying it once.
 */

const ARABIC_CHAR = '[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]'
const HAS_ARABIC = new RegExp(ARABIC_CHAR)
const NO_ARABIC_BEFORE = '(?<!' + ARABIC_CHAR + ')'
const NO_ARABIC_AFTER = '(?!' + ARABIC_CHAR + ')'

/**
 * Build one rule for a term whisper writes out in Arabic letters. Segments may be written with or
 * without spaces, and the Arabic definite article is swallowed with the term, so "الجيبيو" and
 * "جي بي يو" both become "GPU". Rules only fire on whole words.
 */
function term(latin: string, ...segments: string[][]): [RegExp, string] {
	const body = segments.map((alternatives) => '(?:' + alternatives.join('|') + ')').join('[ \t]*')
	return [new RegExp(NO_ARABIC_BEFORE + '(?:ال)?' + body + NO_ARABIC_AFTER, 'g'), latin]
}

/**
 * Spellings whisper.cpp produces for terms that are normally written in Latin in Arabic text.
 *
 * This list is mirrored by benchmarks/arabic-asr/sadabench/postprocess.py (so the harness can score
 * what the app actually shows); both implementations assert
 * benchmarks/arabic-asr/fixtures/arabic-postprocess-cases.json, which keeps them in sync.
 */
const ACRONYMS: [RegExp, string][] = [
	// Longest terms first: HTTPS contains HTTP, so the shorter rule must not run first.
	term('HTTPS', ['إتش', 'اتش'], ['تي', 'تى'], ['تي', 'تى'], ['بي', 'بى'], ['إس', 'اس', 'أس']),
	term('HTTP', ['إتش', 'اتش'], ['تي', 'تى'], ['تي', 'تى'], ['بي', 'بى']),
	term('HTML', ['إتش', 'اتش'], ['تي', 'تى'], ['إم', 'ام', 'أم'], ['إل', 'ال', 'أل']),
	// Joined spellings overlap ("جيبيو" is جي + بيو), so they need their own rules before the split ones.
	[new RegExp(NO_ARABIC_BEFORE + '(?:ال)?(?:جيبيو|جيبْيو)' + NO_ARABIC_AFTER, 'g'), 'GPU'],
	[new RegExp(NO_ARABIC_BEFORE + '(?:ال)?(?:سيبيو|سيبْيو)' + NO_ARABIC_AFTER, 'g'), 'CPU'],
	term('GPU', ['جي', 'جى'], ['بي', 'بى'], ['يو', 'يوا']),
	term('CPU', ['سي', 'سى'], ['بي', 'بى'], ['يو', 'يوا']),
	term('PDF', ['بي', 'بى'], ['دي', 'دى'], ['إف', 'اف', 'أف', 'ف']),
	// SRT is often written as one joined word ("السورتي") rather than read as three letters.
	[new RegExp(NO_ARABIC_BEFORE + '(?:ال)?(?:سورتي|سورتى)' + NO_ARABIC_AFTER, 'g'), 'SRT'],
	term('SRT', ['إس', 'اس', 'أس'], ['آر', 'ار', 'أر'], ['تي', 'تى']),
	term('VTT', ['في', 'فى'], ['تي', 'تى'], ['تي', 'تى']),
	[new RegExp(NO_ARABIC_BEFORE + '(?:ال)?(?:جيسون|جسون|جيسُن)' + NO_ARABIC_AFTER, 'g'), 'JSON'],
	term('API', ['إيه', 'ايه', 'إي'], ['بي', 'بى'], ['آي', 'اي', 'أي']),
	term('FFmpeg', ['إف', 'اف', 'أف'], ['إف', 'اف', 'أف'], ['إم', 'ام', 'أم'], ['بيغ', 'بيج', 'بغ']),
	[new RegExp(NO_ARABIC_BEFORE + '(?:ال)?(?:ويسبر|ويسپر|ويسْبر)' + NO_ARABIC_AFTER, 'g'), 'Whisper'],
	term('URL', ['يو', 'يوا'], ['آر', 'ار', 'أر'], ['إل', 'ال', 'أل']),
	term('SQL', ['إس', 'اس', 'أس'], ['كيو'], ['إل', 'ال', 'أل']),
	term('CSS', ['سي', 'سى'], ['إس', 'اس', 'أس'], ['إس', 'اس', 'أس']),
	term('USB', ['يو', 'يوا'], ['إس', 'اس', 'أس'], ['بي', 'بى']),
	term('VPN', ['في', 'فى'], ['بي', 'بى'], ['إن', 'ان', 'أن']),
	term('Wi-Fi', ['واي', 'واى'], ['فاي', 'فاى']),
	term('GitHub', ['غيت', 'جيت'], ['هاب', 'هب']),
]

/** ASCII punctuation that Arabic typography replaces with its own codepoint. */
const PUNCTUATION: [RegExp, string][] = [
	[new RegExp('(' + ARABIC_CHAR + ')[ \\t]*,[ \\t]*', 'g'), '$1، '],
	[new RegExp('(' + ARABIC_CHAR + ')[ \\t]*\\?[ \\t]*', 'g'), '$1؟ '],
	[new RegExp('(' + ARABIC_CHAR + ')[ \\t]*;[ \\t]*', 'g'), '$1؛ '],
]

/**
 * Normalise one segment's text. Returns the input untouched when there is no Arabic in it, so
 * English transcripts and SRT/VTT files keep their ASCII punctuation exactly as before.
 */
export function normalizeArabicText(text: string): string {
	if (!text || !HAS_ARABIC.test(text)) return text
	let result = text
	for (const [pattern, replacement] of ACRONYMS) result = result.replace(pattern, replacement)
	for (const [pattern, replacement] of PUNCTUATION) result = result.replace(pattern, replacement)
	// Arabic punctuation hugs the preceding word; whisper often leaves a space before it.
	result = result.replace(/[ \t]+([،؛؟])/g, '$1')
	// The substitutions above can leave a doubled or trailing space.
	result = result.replace(/[ \t]{2,}/g, ' ')
	result = result.replace(/[ \t]+$/gm, '')
	return result
}

/** Same, for anything shaped like a transcript segment. */
export function normalizeSegment<T extends { text: string }>(segment: T): T {
	const text = normalizeArabicText(segment.text)
	return text === segment.text ? segment : { ...segment, text }
}

export function normalizeSegments<T extends { text: string }>(segments: T[]): T[] {
	return segments.map(normalizeSegment)
}
