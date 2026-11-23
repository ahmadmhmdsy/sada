import ReactDOM from 'react-dom/client'
import { getCurrentWindow } from '@tauri-apps/api/window'
import { unregisterAll } from '@tauri-apps/plugin-global-shortcut'
import './globals.css'
import { CONFIG_KEYS } from './lib/config-keys'
import { loadConfigStore, readConfig } from './lib/config-store'
import { runMigrations } from './lib/migrations'
import { DEFAULT_DISPLAY_LANGUAGE, supportedLanguages } from './lib/i18n'
import { getLocale, getTextDirection, setLocale } from './paraglide/runtime.js'
import Root from './root'


/**
 * Paraglide resolves the locale through its strategies (localStorage, then the base locale), so
 * the stored language has to be applied before the first render — otherwise the window paints in
 * English and corrects itself, and every direction-dependent style flashes LTR.
 */
function applyBootLocale() {
	const stored = readConfig<string>(CONFIG_KEYS.displayLanguage, DEFAULT_DISPLAY_LANGUAGE)
	const locale = supportedLanguages[stored] ? stored : DEFAULT_DISPLAY_LANGUAGE
	if (locale !== getLocale()) setLocale(locale as never, { reload: false })
	document.documentElement.lang = locale
	document.documentElement.dir = getTextDirection(locale)
}

async function start() {
	await loadConfigStore()
	runMigrations()
	applyBootLocale()
	// Echo 4.0 preview: opt-in paper-and-ink token layer, off in every shipped build.
	// See docs/design/ui-decisions/ECHO-PREVIEW.md and echo-identity-4.0.md §3.
	if (import.meta.env.VITE_ECHO_PREVIEW === 'true') {
		document.documentElement.dataset.echoPreview = 'true'
	}
	// Native registrations outlive a webview reload, including their dead JS callbacks.
	// Clear them before either shortcut provider mounts. Auxiliary windows must never
	// clear the main window's live shortcuts when their own webviews start.
	if (getCurrentWindow().label === 'main') {
		try {
			await unregisterAll()
		} catch (error) {
			console.error('Failed to clear shortcuts from the previous webview:', error)
		}
	}
	ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(<Root />)
}

void start()
