import { describe, expect, it } from 'vitest'
import { isAuxiliaryModelFile, withoutUnsupportedOptions, type ModelCapabilities } from './model'

const whisper: ModelCapabilities = {
	engine: 'whisper',
	requires_vad: false,
	languages: ['en'],
	language_detection: true,
	streaming: true,
	translation: true,
	timestamps: true,
	text_prompts: true,
}

const options = { lang: 'en', init_prompt: 'Punctuate. Use full sentences.', translate: true, n_threads: 4 }

describe('withoutUnsupportedOptions', () => {
	it('sends everything to a model that takes prompts and translation', () => {
		expect(withoutUnsupportedOptions(options, whisper)).toEqual(options)
	})

	it('drops the prompt and translation for engines that reject them, keeping the rest', () => {
		expect(withoutUnsupportedOptions(options, { ...whisper, engine: 'parakeet', text_prompts: false, translation: false })).toEqual({
			lang: 'en',
			n_threads: 4,
		})
	})

	it('leaves the options alone when no capabilities are known yet', () => {
		expect(withoutUnsupportedOptions(options, null)).toEqual(options)
		expect(withoutUnsupportedOptions(options, undefined)).toBe(options)
	})
})

describe('isAuxiliaryModelFile', () => {
	it('keeps helper models and the retired Sortformer file out of the model list', () => {
		expect(isAuxiliaryModelFile('ggml-silero-v6.2.0.bin')).toBe(true)
		expect(isAuxiliaryModelFile('nemotron-3-diarization-Q8_0.gguf')).toBe(true)
		expect(isAuxiliaryModelFile('diar_streaming_sortformer_4spk-v2.q8_0.gguf')).toBe(true)
		expect(isAuxiliaryModelFile('DIAR_STREAMING_SORTFORMER_4SPK-V2.Q8_0.GGUF')).toBe(true)
	})

	it('keeps real transcription models listed', () => {
		expect(isAuxiliaryModelFile('ggml-large-v3-turbo.bin')).toBe(false)
		expect(isAuxiliaryModelFile('ggml-tiny.bin')).toBe(false)
		expect(isAuxiliaryModelFile('nemotron-3.5-asr-streaming-0.6b-Q4_K_M.gguf')).toBe(false)
	})
})
