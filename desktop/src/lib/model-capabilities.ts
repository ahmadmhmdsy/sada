//!
// Language reconciliation and the VAD gate, shared by every model path.
//
// A model switch changes what the engine accepts: Whisper uses two-letter codes and needs
// no VAD, while Parakeet and Nemotron advertise full codes such as `ar-AR` and refuse to
// run without Silero VAD. Both rules were previously re-implemented (or missing) in each
// caller; these pure functions are the single decision point, unit tested once.

import type { ModelCapabilities } from '~/lib/model'

/** The selected language, after it was checked against the model that will run. */
export interface LanguageReconciliation {
	lang: string
	changed: boolean
}

/**
 * The advertised code closest to `current`: an exact (case-insensitive) match first, then the
 * same base language either way (`ar` -> `ar-AR`, `ar-AR` -> `ar`). Returns null when the model
 * does not advertise that language at all.
 */
export function nearestLanguage(current: string, languages: readonly string[]): string | null {
	const requested = current.trim().toLowerCase()
	if (!requested) return null
	const exact = languages.find((code) => code.toLowerCase() === requested)
	if (exact) return exact
	const requestedBase = requested.split(/[-_]/)[0]
	const byBase = languages.find((code) => {
		const base = code.toLowerCase().split(/[-_]/)[0]
		return base === requestedBase
	})
	return byBase ?? null
}

/**
 * Map the stored language onto the model's advertised list.
 *
 * Order: keep a supported code exactly as it is; otherwise pick the nearest advertised code;
 * otherwise language detection when the model supports it; otherwise the first advertised
 * language. An empty or unknown capability list keeps the user's choice untouched, because
 * guessing there would silently change a language the next model might accept.
 */
export function reconcileLanguage(current: string, capabilities: ModelCapabilities | null | undefined): LanguageReconciliation {
	if (!capabilities) return { lang: current, changed: false }
	const languages = capabilities.languages ?? []
	if (languages.length === 0) return { lang: current, changed: false }

	const stored = current.trim()
	if (stored === 'auto') {
		return capabilities.language_detection ? { lang: stored, changed: false } : { lang: languages[0], changed: languages[0] !== stored }
	}

	const nearest = nearestLanguage(stored, languages)
	if (nearest) return { lang: nearest, changed: nearest !== stored }

	const fallback = capabilities.language_detection ? 'auto' : languages[0]
	return { lang: fallback, changed: fallback !== stored }
}

/** What a caller has to do before a run: nothing, run, or download the VAD model first. */
export type VadGate = 'skip' | 'satisfied' | 'download'

/** One decision shared by settings, setup, the queue and dictation. */
export function vadGate(requiresVad: boolean | undefined, vadUsable: boolean): VadGate {
	if (!requiresVad) return 'skip'
	return vadUsable ? 'satisfied' : 'download'
}
