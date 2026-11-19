import { beforeEach, describe, expect, it, vi } from 'vitest'

const mocks = vi.hoisted(() => ({ invoke: vi.fn() }))
vi.mock('@tauri-apps/api/core', () => ({ invoke: mocks.invoke }))

import {
	UNMANAGED_POLICY,
	aiDisabled,
	hasManagedPolicy,
	loadManagedPolicy,
	modelDownloadsDisabled,
	resetManagedPolicyCache,
	urlImportDisabled,
} from './policy'

beforeEach(() => {
	mocks.invoke.mockReset()
	resetManagedPolicyCache()
})

describe('managed policy', () => {
	it('reads the backend policy once and caches it', async () => {
		mocks.invoke.mockResolvedValue({ offlineMode: true, disableAi: false, disableUrlImport: false, disableModelDownloads: false, transcriptsDir: 'D:\\Sada' })
		const first = await loadManagedPolicy()
		const second = await loadManagedPolicy()
		expect(first.offlineMode).toBe(true)
		expect(second).toBe(first)
		expect(mocks.invoke).toHaveBeenCalledTimes(1)
		expect(mocks.invoke).toHaveBeenCalledWith('get_managed_policy')
	})

	it('treats a failed read as unmanaged instead of breaking the UI', async () => {
		mocks.invoke.mockRejectedValue(new Error('command missing'))
		const policy = await loadManagedPolicy()
		expect(policy).toEqual(UNMANAGED_POLICY)
		expect(hasManagedPolicy(policy)).toBe(false)
	})

	it('fills missing fields and normalizes an empty transcripts dir', async () => {
		mocks.invoke.mockResolvedValue({ disableAi: true, transcriptsDir: '' })
		const policy = await loadManagedPolicy()
		expect(policy.offlineMode).toBe(false)
		expect(policy.disableAi).toBe(true)
		expect(policy.transcriptsDir).toBeNull()
	})

	it('offline mode implies every network guard', () => {
		const policy = { ...UNMANAGED_POLICY, offlineMode: true }
		expect(aiDisabled(policy)).toBe(true)
		expect(urlImportDisabled(policy)).toBe(true)
		expect(modelDownloadsDisabled(policy)).toBe(true)
	})

	it('individual flags stay independent', () => {
		const policy = { ...UNMANAGED_POLICY, disableModelDownloads: true }
		expect(modelDownloadsDisabled(policy)).toBe(true)
		expect(aiDisabled(policy)).toBe(false)
		expect(urlImportDisabled(policy)).toBe(false)
	})

	it('reports a managed machine when a policy pins the transcripts folder', () => {
		expect(hasManagedPolicy({ ...UNMANAGED_POLICY, transcriptsDir: 'D:\\Sada' })).toBe(true)
		expect(hasManagedPolicy(UNMANAGED_POLICY)).toBe(false)
	})
})
