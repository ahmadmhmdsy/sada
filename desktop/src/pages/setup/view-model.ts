import { invoke } from '@tauri-apps/api/core'
import { emit, listen } from '@tauri-apps/api/event'
import { useContext, useEffect, useRef, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { ErrorModalContext } from '~/providers/error-modal'
import { usePreferenceProvider } from '~/providers/preference'
import * as utils from '~/lib/model'
import { readModelMetadata } from '~/lib/model'
import { ensureVadModel } from '~/lib/vad-gate'
import * as osExt from '@tauri-apps/plugin-os'
import * as config from '~/lib/config'
import { loadManagedPolicy, modelDownloadsDisabled } from '~/lib/policy'
import { m } from '~/paraglide/messages.js'

export function viewModel() {
	const location = useLocation()
	const [downloadProgress, setDownloadProgress] = useState(0)
	const [isOnline, setIsOnline] = useState<boolean | null>(null)
	const downloadProgressRef = useRef(0)
	const { setState: setErrorModal } = useContext(ErrorModalContext)
	const navigate = useNavigate()
	const preference = usePreferenceProvider()

	function handleProgressEvenets() {
		listen('download_progress', (event) => {
			// event.event is the event name (useful if you want to use a single callback fn for multiple event types)
			// event.payload is the payload object
			const [current, total] = event.payload as [number, number]
			const newDownloadProgress = Number(current / total) * 100

			if (newDownloadProgress > downloadProgressRef.current) {
				// for some reason it jumps if not
				setDownloadProgress(newDownloadProgress)
				downloadProgressRef.current = newDownloadProgress
			}
		})
	}

	async function selectDownloadedModel(modelPath: string) {
		const metadata = await readModelMetadata(modelPath)
		// Selecting the model is what starts using it, so the VAD gate belongs here: the setup
		// flow must not leave a model active that cannot run. Language reconciliation happens in
		// the preference provider once the capabilities arrive.
		if (!(await ensureVadModel(metadata))) return false
		preference.setModelMetadata(metadata)
		preference.setModelPath(modelPath)
		return true
	}

	async function downloadModel() {
		// A managed machine can forbid downloads; setup then sends the user to Settings to pick a
		// model an administrator already installed instead of retrying a refused download.
		if (modelDownloadsDisabled(await loadManagedPolicy())) {
			preference.setSkippedSetup(true)
			setErrorModal?.({ open: true, log: m.managedPolicyModelDownloads() })
			navigate('/#settings', { replace: true, state: { disableBack: true } })
			return
		}
		handleProgressEvenets()

		let lastError = null

		try {
			let urls: config.ModelDownload[] = []

			// Determine model URLs
			if (location?.state?.downloadURL) {
				// A deep link that matches the catalog keeps the published size and SHA-256; a URL
				// the user supplied carries neither, so the backend falls back to the size and
				// magic-byte checks it runs on every download.
				const integrity = (location.state.downloadIntegrity ?? {}) as config.ModelIntegrity
				urls = [{ url: location.state.downloadURL, ...integrity }]
				console.log(`[model] Using provided model URL: ${urls[0].url}`)
			} else {
				urls = [...config.modelUrls.default]
				const locale = await osExt.locale()
				console.log(`[locale] Detected locale: ${locale}`)

				if (locale?.endsWith('-IL')) {
					console.log(`[model] Prioritizing Hebrew models`)
					urls.unshift(...config.modelUrls.hebrew)
				}
			}

			// Try downloading from each URL
			for (const source of urls) {
				try {
					console.log(`[model] Attempting to download from: ${source.url}`)
					// Re-downloading a corrupt model overwrites it in place instead of dropping a
					// second, randomly named copy next to the broken one.
					const path = await utils.downloadModel(source, { replacePath: location?.state?.replacePath })
					if (!path) {
						console.log('[model] Download cancelled')
						return
					}
					console.log(`[model] Download succeeded: ${path}`)
					if (!(await selectDownloadedModel(path))) {
						navigate('/#settings', { replace: true })
						return
					}
					navigate('/', { replace: true, state: { disableBack: true } })
					return
				} catch (err) {
					console.error(`[model] Failed to download from ${source.url}:`, err)
					lastError = err
				}
			}

			throw new Error(`All model downloads failed. Last error: ${lastError}`)
		} catch (err) {
			console.error(`[model] Unhandled error:`, err)
			setErrorModal?.({ open: true, log: String(err) })
		}
	}

	async function downloadIfOnline() {
		if (modelDownloadsDisabled(await loadManagedPolicy())) {
			preference.setSkippedSetup(true)
			setErrorModal?.({ open: true, log: m.managedPolicyModelDownloads() })
			navigate('/#settings', { replace: true, state: { disableBack: true } })
			return
		}
		// Check if online
		const isOnlineResponse = await invoke<boolean>('is_online')
		// If online download model
		if (isOnlineResponse) {
			downloadModel()
		}
		// Update UI
		setIsOnline(isOnlineResponse)
	}

	async function cancelSetup() {
		// Cancel and go to settings
		preference.setSkippedSetup(true)
		emit('abort_download')
		navigate('/#settings', { replace: true, state: { disableBack: true } })
	}

	useEffect(() => {
		downloadIfOnline()
	}, [])

	return {
		navigate,
		cancelSetup,
		setErrorModal,
		downloadProgress,
		downloadIfOnline,
		setDownloadProgress,
		downloadProgressRef,
		isOnline,
		location,
	}
}
