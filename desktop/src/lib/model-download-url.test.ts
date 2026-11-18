import { describe, expect, it } from 'vitest'
import { modelUrls } from './config'
import { catalogModelFor, isTrustedDownloadHost, parseDeepLinkDownloadUrl, parseModelDownloadUrl } from './model-download-url'

const catalogUrl = modelUrls.default[0].url

describe('parseModelDownloadUrl', () => {
	it('accepts https links on the catalog hosts', () => {
		const link = parseModelDownloadUrl('https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.bin')
		expect(link?.host).toBe('huggingface.co')
		expect(link?.url).toBe('https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.bin')
		expect(link?.catalog).toBeUndefined()
	})

	it('recognizes a catalog URL and hands back its integrity metadata', () => {
		const link = parseModelDownloadUrl(catalogUrl)
		expect(link?.catalog?.sha256).toBe(modelUrls.default[0].sha256)
		expect(catalogModelFor(catalogUrl)?.size).toBe(modelUrls.default[0].size)
	})

	it('rejects plain http, other schemes and untrusted hosts', () => {
		for (const bad of [
			'http://huggingface.co/ggml-tiny.bin',
			'file:///C:/Windows/win.ini',
			'javascript:alert(1)',
			'https://evil.example/model.bin',
			'https://huggingface.co.evil.example/model.bin',
			'https://nothuggingface.co/model.bin',
			'https://github.com.evil.example/x.bin',
			'',
			'not a url',
		]) {
			expect(parseModelDownloadUrl(bad)).toBeNull()
		}
	})

	it('accepts github.com and its subdomains', () => {
		expect(parseModelDownloadUrl('https://github.com/alshahia/sada/releases/download/v1/model.bin')?.host).toBe('github.com')
		expect(parseModelDownloadUrl('https://objects.github.com/x.bin')).not.toBeNull()
	})
})

describe('isTrustedDownloadHost', () => {
	it('matches only the trusted hosts and their subdomains', () => {
		expect(isTrustedDownloadHost('huggingface.co')).toBe(true)
		expect(isTrustedDownloadHost('HUGGINGFACE.CO')).toBe(true)
		expect(isTrustedDownloadHost('cdn.huggingface.co')).toBe(true)
		expect(isTrustedDownloadHost('github.com')).toBe(true)
		expect(isTrustedDownloadHost('evil.com')).toBe(false)
		expect(isTrustedDownloadHost('huggingface.co.evil.com')).toBe(false)
	})
})

describe('parseDeepLinkDownloadUrl', () => {
	it('reads the url parameter of a download deep link', () => {
		expect(parseDeepLinkDownloadUrl('sada://download/?url=https%3A%2F%2Fhuggingface.co%2Fggml-tiny.bin')).toBe(
			'https://huggingface.co/ggml-tiny.bin'
		)
	})

	it('ignores unrelated URLs and schemes', () => {
		for (const other of ['sada://open/?url=https%3A%2F%2Fhuggingface.co%2Fx', 'vibe://download/?url=x', 'https://example.com', 'C:/audio.mp3', 'not a url']) {
			expect(parseDeepLinkDownloadUrl(other)).toBeNull()
		}
	})
})
