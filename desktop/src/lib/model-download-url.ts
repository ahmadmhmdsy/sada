import { modelUrls, type ModelDownload } from './config'

/** The only hosts a model link may point at: the bundled catalog downloads from these two. */
const trustedDownloadHosts = ['huggingface.co', 'github.com']

/** Whether a host is one of the trusted download hosts, or a subdomain of one. */
export function isTrustedDownloadHost(hostname: string): boolean {
	const host = hostname.toLowerCase()
	return trustedDownloadHosts.some((trusted) => host === trusted || host.endsWith('.' + trusted))
}

/** The catalog entry for a URL, so its size and SHA-256 are enforced. Undefined for user URLs. */
export function catalogModelFor(url: string): ModelDownload | undefined {
	return Object.values(modelUrls)
		.flat()
		.find((entry) => {
			try {
				return new URL(entry.url).toString() === url
			} catch {
				return false
			}
		})
}

export interface ModelDownloadLink {
	/** Normalized URL. */
	url: string
	host: string
	/** The catalog entry when the URL is one the app ships, so the download is hash-checked. */
	catalog?: ModelDownload
}

/**
 * A model URL from the settings field or a deep link: https on a trusted host, nothing else.
 * Anything rejected here never reaches the download command, which re-checks https and the
 * models folder on its own.
 */
export function parseModelDownloadUrl(raw: string | null | undefined): ModelDownloadLink | null {
	if (!raw) return null
	try {
		const parsed = new URL(raw)
		if (parsed.protocol !== 'https:') return null
		if (!isTrustedDownloadHost(parsed.hostname)) return null
		const url = parsed.toString()
		return { url, host: parsed.hostname, catalog: catalogModelFor(url) }
	} catch {
		return null
	}
}

/**
 * The model URL inside a sada://download/?url=... deep link, or null for any other URL.
 * The caller still runs it through parseModelDownloadUrl before showing it.
 */
export function parseDeepLinkDownloadUrl(raw: string): string | null {
	try {
		const parsed = new URL(raw)
		if (parsed.protocol !== 'sada:' || parsed.hostname !== 'download') return null
		return parsed.searchParams.get('url')
	} catch {
		return null
	}
}
