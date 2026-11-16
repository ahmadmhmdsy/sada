import { describe, expect, it } from 'vitest'
import { normalizeArabicText, normalizeSegment, normalizeSegments } from './arabic-text'

const asciiComma = ' , '
const arabicComma = '،'

describe('normalizeArabicText', () => {
	it('leaves English text untouched', () => {
		const text = 'Hello, world? Yes; fine.'
		expect(normalizeArabicText(text)).toBe(text)
	})

	it('rewrites ASCII punctuation that follows Arabic', () => {
		const text = 'مرحبا' + asciiComma + 'كيف حالك? بخير; شكرا'
		expect(normalizeArabicText(text)).toBe('مرحبا' + arabicComma + ' كيف حالك؟ بخير؛ شكرا')
	})

	it('removes the space whisper leaves before Arabic punctuation', () => {
		expect(normalizeArabicText('نص عربي ، ثم سؤال ؟')).toBe('نص عربي، ثم سؤال؟')
	})

	it('restores common Latin acronyms', () => {
		expect(normalizeArabicText('استخدم جي بي يو لتسريع تحسين الصوت')).toBe('استخدم GPU لتسريع تحسين الصوت')
		expect(normalizeArabicText('ملف بي دي إف جاهز')).toBe('ملف PDF جاهز')
		expect(normalizeArabicText('حفظ بصيغة إس آر تي')).toBe('حفظ بصيغة SRT')
	})

	it('does not touch the inside of Latin words or URLs', () => {
		const text = 'افتح https://example.com/a,b ثم اقرأ الملف'
		expect(normalizeArabicText(text)).toBe(text)
	})

	it('is idempotent', () => {
		const once = normalizeArabicText('مرحبا ، هذا جي بي يو ؟')
		expect(normalizeArabicText(once)).toBe(once)
	})

	it('keeps empty and whitespace-only text', () => {
		expect(normalizeArabicText('')).toBe('')
		expect(normalizeArabicText('   ')).toBe('   ')
	})
})

describe('normalizeSegment(s)', () => {
	it('normalizes text and keeps the rest of the segment', () => {
		const segment = { start: 0, end: 1, text: 'مرحبا , بالعالم', speaker: 'A' }
		const out = normalizeSegment(segment)
		expect(out).toEqual({ start: 0, end: 1, text: 'مرحبا، بالعالم', speaker: 'A' })
	})

	it('returns the same object when nothing changes', () => {
		const segment = { start: 0, end: 1, text: 'English only.' }
		expect(normalizeSegment(segment)).toBe(segment)
	})

	it('maps a whole list', () => {
		const out = normalizeSegments([
			{ start: 0, end: 1, text: 'مرحبا ,' },
			{ start: 1, end: 2, text: 'English, stays.' },
		])
		expect(out.map((s) => s.text)).toEqual(['مرحبا،', 'English, stays.'])
	})
})
