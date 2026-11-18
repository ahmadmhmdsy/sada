// @vitest-environment jsdom

import { readFileSync } from 'node:fs'
import { join } from 'node:path'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { waitFor } from '@testing-library/react'

const mocks = vi.hoisted(() => ({
	windowLabel: 'main',
	loadConfigStore: vi.fn(),
	readConfig: vi.fn(() => undefined),
	runMigrations: vi.fn(),
	unregisterAll: vi.fn(),
	render: vi.fn(),
	releaseCleanup: null as null | (() => void),
}))

vi.mock('@tauri-apps/api/window', () => ({ getCurrentWindow: () => ({ label: mocks.windowLabel }) }))
vi.mock('@tauri-apps/plugin-global-shortcut', () => ({ unregisterAll: mocks.unregisterAll }))
vi.mock('./lib/config-store', () => ({ loadConfigStore: mocks.loadConfigStore, readConfig: mocks.readConfig }))
vi.mock('./lib/migrations', () => ({ runMigrations: mocks.runMigrations }))
vi.mock('./root', () => ({ default: () => null }))
vi.mock('react-dom/client', () => ({ default: { createRoot: () => ({ render: mocks.render }) } }))

beforeEach(async () => {
	// A test that timed out can leave `start()` waiting on native cleanup. Release and flush it
	// before the module registry and mock call history are reset, otherwise its render lands in the
	// next test and makes it look like bootstrap rendered twice.
	mocks.releaseCleanup?.()
	mocks.releaseCleanup = null
	await new Promise((resolve) => setTimeout(resolve, 0))
	vi.resetModules()
	vi.resetAllMocks()
	mocks.windowLabel = 'main'
	document.body.innerHTML = '<div id="root"></div>'
})

afterEach(() => vi.restoreAllMocks())

describe('shortcut recovery after a webview reload', () => {
	it('finishes clearing stale native shortcuts before either provider can register again', { timeout: 15000 }, async () => {
		let finishCleanup!: () => void
		mocks.unregisterAll.mockImplementation(
			() =>
				new Promise<void>((resolve) => {
					finishCleanup = resolve
					mocks.releaseCleanup = resolve
				})
		)
		await import('./bootstrap')
		await waitFor(() => expect(mocks.unregisterAll).toHaveBeenCalledOnce())
		expect(mocks.render).not.toHaveBeenCalled()
		finishCleanup()
		await waitFor(() => expect(mocks.render).toHaveBeenCalledOnce())
	})

	it.each(['dictation-indicator', 'meeting-prompt'])('does not release live shortcuts when %s opens', { timeout: 15000 }, async (label) => {
		mocks.windowLabel = label
		await import('./bootstrap')
		await waitFor(() => expect(mocks.render).toHaveBeenCalledOnce())
		expect(mocks.unregisterAll).not.toHaveBeenCalled()
	})

	it('keeps Settings accessible if native cleanup fails', async () => {
		const error = new Error('Native cleanup failed')
		const log = vi.spyOn(console, 'error').mockImplementation(() => {})
		mocks.unregisterAll.mockRejectedValue(error)
		await import('./bootstrap')
		await waitFor(() => expect(mocks.render).toHaveBeenCalledOnce())
		expect(log).toHaveBeenCalledWith('Failed to clear shortcuts from the previous webview:', error)
	})

	it('boots Arabic-first when no language has been chosen yet', async () => {
		await import('./bootstrap')
		await waitFor(() => expect(mocks.render).toHaveBeenCalledOnce())
		expect(document.documentElement.lang).toBe('ar-IQ')
		expect(document.documentElement.dir).toBe('rtl')
	})

	it('grants the native cleanup command used during startup', () => {
		const capabilities = JSON.parse(readFileSync(join(__dirname, '../src-tauri/capabilities/main.json'), 'utf8'))
		expect(capabilities.permissions).toContain('global-shortcut:allow-unregister-all')
	})
})
