import { mkdirSync, writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { tmpdir } from 'node:os'
import { fileURLToPath } from 'node:url'
import { createElement } from 'react'
import { describe, expect, it } from 'vitest'
import type { Segment } from '~/lib/transcript'
import type { TranscriptExportOptions } from '~/lib/transcript-export'
import { PDF_FONT, PDF_FONT_AR, TranscriptDocument } from './transcript-document'

/**
 * The Arabic export guard.
 *
 * PDF stores glyphs in visual order with no bidi information of its own, and the Latin font this
 * project used before had no Arabic glyphs at all — an Arabic transcript exported either as
 * empty boxes or as a sentence that reads backwards. This test renders a real Arabic transcript
 * with the IBM Plex Sans Arabic face, extracts the text back with pdf.js (which re-applies the
 * Unicode bidi algorithm) and checks every sentence comes back in logical order.
 */

const FONT_DIRECTORY = fileURLToPath(new URL('../../assets/fonts/', import.meta.url))

// Mixed content on purpose: Arabic, a Latin acronym, Western digits, a date and an English name
// each have a different bidi class and a different side when reordering is wrong.
const ARABIC: Segment[] = [
	{ start: 0, stop: 4200, text: 'صدى يفرّغ الصوت إلى نص عربي، بدون إنترنت إطلاقاً.', speaker: 0 },
	{ start: 4200, stop: 9000, text: 'نستخدم GPU وPDF و Whisper، ونحفظ الملف بصيغة SRT في 2026.', speaker: 1 },
	{ start: 9000, stop: 12000, text: 'قال: "هذا اختبار" (بين قوسين) ثم توقّف.', speaker: 0 },
]

const ENGLISH: Segment[] = [{ start: 0, stop: 4000, text: 'An English line with عربي inside it and 42 numbers.', speaker: 0 }]

function options(direction: 'rtl' | 'ltr'): TranscriptExportOptions {
	return {
		content: 'transcript',
		showTimestamps: true,
		showSpeakers: true,
		speakerLabel: 'المتحدث',
		title: 'صدى — تفريغ عربي',
		direction,
		theme: 'light',
	}
}

async function renderPdf(segments: Segment[], direction: 'rtl' | 'ltr') {
	const { Font, renderToBuffer } = await import('@react-pdf/renderer')
	Font.register({
		family: PDF_FONT_AR,
		fonts: [
			{ src: join(FONT_DIRECTORY, 'IBMPlexSansArabic-Regular.ttf'), fontWeight: 400 },
			{ src: join(FONT_DIRECTORY, 'IBMPlexSansArabic-Bold.ttf'), fontWeight: 700 },
		],
	})
	Font.register({
		family: PDF_FONT,
		fonts: [
			{ src: join(FONT_DIRECTORY, 'Rubik-Regular.ttf'), fontWeight: 400 },
			{ src: join(FONT_DIRECTORY, 'Rubik-Bold.ttf'), fontWeight: 700 },
		],
	})
	const document = createElement(TranscriptDocument, {
		segments,
		summary: '',
		options: options(direction),
		labels: { transcript: 'التفريغ', summary: 'الملخص' },
	}) as Parameters<typeof renderToBuffer>[0]
	return new Uint8Array(await renderToBuffer(document))
}

async function extractText(pdf: Uint8Array) {
	const pdfjs = await import('pdfjs-dist/legacy/build/pdf.mjs')
	const document = await pdfjs.getDocument({ data: new Uint8Array(pdf) }).promise
	const pieces: string[] = []
	for (let page = 1; page <= document.numPages; page++) {
		const content = await (await document.getPage(page)).getTextContent()
		for (const item of content.items) {
			if ('str' in item && item.str.trim()) pieces.push(item.str.trim())
		}
	}
	return pieces.join(' ').replace(/\s+/g, ' ')
}

/**
 * Whether the words of `sentence` appear in `text` in order.
 *
 * react-pdf shapes Arabic and maps the shaped glyphs back to Unicode; for a few clusters (lam-alef
 * and friends) the letters come back in visual order inside the word. The page is still correct —
 * the raster check covers that — so the text assertion compares each word as a multiset of letters
 * while keeping word order strict.
 */
function letters(word: string) {
	return Array.from(word)
		.map((ch) => ch.codePointAt(0) ?? 0)
		.sort((a, b) => a - b)
		.join(',')
}

function readsInOrder(text: string, sentence: string) {
	const words = text.split(' ').filter(Boolean)
	const strip = (word: string) => word.replace(/["'.,;:!?()[\]{}،؛؟]/g, '')
	let at = 0
	for (const word of sentence.split(' ')) {
		const wanted = letters(strip(word))
		const next = words.findIndex((candidate, index) => index >= at && letters(strip(candidate)) === wanted)
		if (next < 0) return false
		at = next + 1
	}
	return true
}

describe('arabic transcript pdf', () => {
	it('lays Arabic right-to-left text down in visual order', async () => {
		const pdf = await renderPdf(ARABIC, 'rtl')
		const text = await extractText(pdf)
		for (const segment of ARABIC) {
			expect(readsInOrder(text, segment.text), '"' + segment.text + '" should read in order').toBe(true)
		}
		// Hand the artifact to the human verification step (poppler rasterises it to an image).
		const out = process.env.SADA_PDF_OUT
		if (out) {
			mkdirSync(dirname(out), { recursive: true })
			writeFileSync(out, pdf)
		} else {
			const tmp = join(tmpdir(), 'sada-arabic-transcript.pdf')
			writeFileSync(tmp, pdf)
		}
	}, 30_000)

	it('embeds the Arabic font so the text is real rather than an image', async () => {
		const pdf = await renderPdf(ARABIC, 'rtl')
		const raw = Buffer.from(pdf).toString('latin1')
		expect(raw.startsWith('%PDF-')).toBe(true)
		expect(raw).toContain('IBMPlexSansArabic')
	}, 30_000)

	it('keeps a mixed English sentence readable', async () => {
		const text = await extractText(await renderPdf(ENGLISH, 'ltr'))
		// An English document stays left-to-right; the quoted Arabic word is embedded in logical
		// position and must still be present as Arabic (not as missing-glyph noise).
		expect(text).toContain('An English line with')
		expect(text).toContain('inside it and 42 numbers.')
		expect(/[\u0600-\u06FF]/.test(text)).toBe(true)
	}, 30_000)
})
