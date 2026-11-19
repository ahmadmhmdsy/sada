import { describe, expect, it } from 'vitest'
import { classifyError } from './error-kind'

describe('classifyError', () => {
	it('reads a failed model download as a network problem', () => {
		expect(classifyError('All model downloads failed. Last error: download timed out')).toBe('network')
	})

	it('recognises disk, memory, audio, file and model failures', () => {
		expect(classifyError('OS error 112: not enough disk space')).toBe('disk')
		expect(classifyError('CUDA out of memory')).toBe('memory')
		expect(classifyError('ffmpeg exited with code 1')).toBe('audio')
		expect(classifyError('No such file or directory (os error 2)')).toBe('file')
		expect(classifyError('ggml model could not be loaded')).toBe('model')
	})

	it('falls back to unknown without a message', () => {
		expect(classifyError(undefined)).toBe('unknown')
		expect(classifyError('something odd happened')).toBe('unknown')
	})
})
