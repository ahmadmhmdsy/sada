import { describe, expect, it } from 'vitest'
import type { ModelCapabilities } from '~/lib/model'
import { nearestLanguage, reconcileLanguage, vadGate } from './model-capabilities'

function caps(overrides: Partial<ModelCapabilities> = {}): ModelCapabilities {
	return {
		engine: 'whisper',
		requires_vad: false,
		languages: [],
		language_detection: true,
		streaming: true,
		translation: true,
		timestamps: true,
		text_prompts: true,
		...overrides,
	}
}

const WHISPER_LANGUAGES = ['en', 'ar', 'de', 'fr', 'he']
const NEMOTRON_LANGUAGES = ['ar-AR', 'en-US', 'de-DE', 'fr-FR', 'he-IL']

describe('nearestLanguage', () => {
	it('returns the advertised spelling of an exact match', () => {
		expect(nearestLanguage('ar-AR', NEMOTRON_LANGUAGES)).toBe('ar-AR')
		expect(nearestLanguage('AR-ar', NEMOTRON_LANGUAGES)).toBe('ar-AR')
	})

	it('maps a base code onto the full advertised code and back', () => {
		expect(nearestLanguage('ar', NEMOTRON_LANGUAGES)).toBe('ar-AR')
		expect(nearestLanguage('ar-AR', WHISPER_LANGUAGES)).toBe('ar')
		expect(nearestLanguage('ar-IQ', WHISPER_LANGUAGES)).toBe('ar')
	})

	it('returns null when the language is not advertised', () => {
		expect(nearestLanguage('ja', NEMOTRON_LANGUAGES)).toBeNull()
		expect(nearestLanguage('', WHISPER_LANGUAGES)).toBeNull()
	})
})

describe('reconcileLanguage', () => {
	it('leaves alone a code the model already advertises', () => {
		expect(reconcileLanguage('ar', caps({ language_detection: false, languages: WHISPER_LANGUAGES }))).toEqual({ lang: 'ar', changed: false })
		expect(reconcileLanguage('ar-AR', caps({ language_detection: false, languages: NEMOTRON_LANGUAGES }))).toEqual({
			lang: 'ar-AR',
			changed: false,
		})
	})

	it('switching Whisper -> Nemotron upgrades the base code', () => {
		expect(reconcileLanguage('ar', caps({ engine: 'nemotron', language_detection: false, languages: NEMOTRON_LANGUAGES }))).toEqual({
			lang: 'ar-AR',
			changed: true,
		})
	})

	it('switching Nemotron -> Whisper drops the region', () => {
		expect(reconcileLanguage('ar-AR', caps({ language_detection: false, languages: WHISPER_LANGUAGES }))).toEqual({ lang: 'ar', changed: true })
	})

	it('keeps auto only when the model can detect the language', () => {
		expect(reconcileLanguage('auto', caps())).toEqual({ lang: 'auto', changed: false })
		expect(reconcileLanguage('auto', caps({ language_detection: false, languages: NEMOTRON_LANGUAGES }))).toEqual({
			lang: 'ar-AR',
			changed: true,
		})
	})

	it('falls back to detection, else the first language, for an unsupported code', () => {
		expect(reconcileLanguage('ja', caps({ languages: NEMOTRON_LANGUAGES }))).toEqual({ lang: 'auto', changed: true })
		expect(reconcileLanguage('ja', caps({ language_detection: false, languages: NEMOTRON_LANGUAGES }))).toEqual({
			lang: 'ar-AR',
			changed: true,
		})
	})

	it('keeps the stored language when the capabilities are unknown', () => {
		expect(reconcileLanguage('ar-IQ', null)).toEqual({ lang: 'ar-IQ', changed: false })
		expect(reconcileLanguage('ar-IQ', caps({ languages: [] }))).toEqual({ lang: 'ar-IQ', changed: false })
	})
})

describe('vadGate', () => {
	it('skips models that do not need a VAD', () => {
		expect(vadGate(false, false)).toBe('skip')
		expect(vadGate(undefined, false)).toBe('skip')
	})

	it('runs when the VAD file is already usable', () => {
		expect(vadGate(true, true)).toBe('satisfied')
	})

	it('asks for a download only when a required VAD file is missing', () => {
		expect(vadGate(true, false)).toBe('download')
	})
})
