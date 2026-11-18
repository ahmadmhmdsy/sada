import { describe, expect, it } from 'vitest'
import fixture from '../../../benchmarks/arabic-asr/fixtures/arabic-postprocess-cases.json'
import { normalizeArabicText } from './arabic-text'

/**
 * The Post-processing rules are duplicated in benchmarks/arabic-asr/sadabench/postprocess.py so the
 * harness scores what the app actually shows. Both implementations assert this same fixture file,
 * so a rule that is added to one side without the other fails a test instead of drifting silently.
 */
describe('arabic-text shared fixtures', () => {
	it('rewrites every replacement case', () => {
		for (const item of fixture.replacements) {
			expect(normalizeArabicText(item.input), item.name).toBe(item.expected)
		}
	})

	it('leaves every unchanged case untouched', () => {
		for (const item of fixture.unchanged) {
			expect(normalizeArabicText(item.input), item.name).toBe(item.input)
		}
	})

	it('is idempotent on the fixture', () => {
		const inputs = [
			...fixture.replacements.map((item) => item.input),
			...fixture.unchanged.map((item) => item.input),
		]
		for (const input of inputs) {
			const once = normalizeArabicText(input)
			expect(normalizeArabicText(once), input).toBe(once)
		}
	})
})
