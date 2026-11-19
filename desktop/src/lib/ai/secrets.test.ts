import { beforeEach, describe, expect, it, vi } from 'vitest'

const mocks = vi.hoisted(() => ({ invoke: vi.fn() }))
vi.mock('@tauri-apps/api/core', () => ({ invoke: mocks.invoke }))

import { DEFAULT_AI, type AiSettings } from './config'
import { hasPlaintextAiSecrets, hasStoredAiSecrets, openAiSecrets, sealAiSecrets } from './secrets'

function settings(overrides: Partial<AiSettings['connection']> = {}): AiSettings {
	return {
		...DEFAULT_AI,
		connection: { ...DEFAULT_AI.connection, claudeApiKey: 'sk-claude', openaiApiKey: 'sk-openai', ...overrides },
	}
}

beforeEach(() => {
	mocks.invoke.mockReset()
	// Stand-in for DPAPI: `seal:<hex>` and `open:<hex>` map to the original value.
	const sealed = new Map<string, string>()
	mocks.invoke.mockImplementation(async (command: string, args: { value: string }) => {
		if (command === 'protect_secret') {
			const token = 'sealed-' + args.value
			sealed.set(token, args.value)
			return token
		}
		if (command === 'unprotect_secret') {
			const value = sealed.get(args.value)
			if (value === undefined) throw new Error('cannot decrypt')
			return value
		}
		throw new Error('unknown command ' + command)
	})
})

describe('AI key sealing', () => {
	it('never leaves a plaintext key in the sealed settings', async () => {
		const sealed = await sealAiSecrets(settings())
		expect(sealed.connection.claudeApiKey).toBe('')
		expect(sealed.connection.openaiApiKey).toBe('')
		expect(sealed.connection.claudeApiKeyEnc).toMatch(/^sealed-/)
		expect(sealed.connection.openaiApiKeyEnc).toMatch(/^sealed-/)
		expect(hasStoredAiSecrets(sealed)).toBe(true)
		expect(hasPlaintextAiSecrets(sealed)).toBe(false)
	})

	it('unseals keys for this boot', async () => {
		const sealed = await sealAiSecrets(settings())
		const opened = await openAiSecrets(sealed)
		expect(opened.connection.claudeApiKey).toBe('sk-claude')
		expect(opened.connection.openaiApiKey).toBe('sk-openai')
	})

	it('keeps empty keys empty without calling the backend', async () => {
		const sealed = await sealAiSecrets(settings({ claudeApiKey: '', openaiApiKey: '' }))
		expect(sealed.connection.claudeApiKeyEnc).toBe('')
		expect(sealed.connection.openaiApiKeyEnc).toBe('')
		expect(hasStoredAiSecrets(sealed)).toBe(false)
	})

	it('starts empty when a stored blob cannot be decrypted', async () => {
		const sealed = settings({ claudeApiKey: '', openaiApiKey: '', claudeApiKeyEnc: 'from-another-account' })
		const opened = await openAiSecrets(sealed)
		expect(opened.connection.claudeApiKey).toBe('')
	})

	it('detects a legacy plaintext config that still needs migration', () => {
		expect(hasPlaintextAiSecrets(settings())).toBe(true)
	})
})
