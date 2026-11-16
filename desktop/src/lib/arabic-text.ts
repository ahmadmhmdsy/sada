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

/** Spellings whisper.cpp produces for terms that are normally written in Latin in Arabic text. */
const ACRONYMS: [RegExp, string][] = [
	[/(?<![\u0600-\u06FF])(?:جي|جى)[ \t]*(?:بي|بى)[ \t]*(?:يو|يوا)(?![\u0600-\u06FF])/g, 'GPU'],
	[/(?<![\u0600-\u06FF])(?:سي|سى)[ \t]*(?:بي|بى)[ \t]*(?:يو|يوا)(?![\u0600-\u06FF])/g, 'CPU'],
	[/(?<![\u0600-\u06FF])(?:بي|بى)[ \t]*(?:دي|دى)[ \t]*(?:إف|اف|أف)(?![\u0600-\u06FF])/g, 'PDF'],
	[/(?<![\u0600-\u06FF])(?:إس|اس|أس)[ \t]*(?:آر|ار|أر)[ \t]*(?:تي|تى)(?![\u0600-\u06FF])/g, 'SRT'],
	[/(?<![\u0600-\u06FF])(?:في|فى)[ \t]*(?:تي|تى)[ \t]*(?:تي|تى)(?![\u0600-\u06FF])/g, 'VTT'],
	[/(?<![\u0600-\u06FF])(?:جيسون|جسون|جيسُن|جيسون)(?![\u0600-\u06FF])/g, 'JSON'],
	[/(?<![\u0600-\u06FF])(?:إيه|ايه|إي)[ \t]*(?:بي|بى)[ \t]*(?:آي|اي|أي)(?![\u0600-\u06FF])/g, 'API'],
	[/(?<![\u0600-\u06FF])(?:إف|اف|أف)[ \t]*(?:إف|اف|أف)[ \t]*(?:إم|ام|أم)[ \t]*(?:بيغ|بيج|بغ)(?![\u0600-\u06FF])/g, 'FFmpeg'],
	[/(?<![\u0600-\u06FF])(?:ويسبر|ويسپر|ويسْبر)(?![\u0600-\u06FF])/g, 'Whisper'],
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
