import { m } from '~/paraglide/messages.js'
import { ModifyState, NamedPath } from './types'
import { pathToNamedPath } from './fs'
import { ask } from '@tauri-apps/plugin-dialog'
import { useEffect } from 'react'
import { listen } from '@tauri-apps/api/event'
import { useNavigate } from 'react-router-dom'
import * as config from '~/lib/config'
import { parseDeepLinkDownloadUrl, parseModelDownloadUrl } from './model-download-url'
import * as os from '@tauri-apps/plugin-os'

interface UseSingleInstanceProps {
	setFiles: ModifyState<NamedPath[]>
}

export function useSingleInstance({ setFiles }: UseSingleInstanceProps) {
	const navigate = useNavigate()

	async function handleSingleInstance() {
		const platform = await os.platform()
		await listen<string[]>('single-instance', async (event) => {
			const argv = event.payload
			const action = argv?.[1]

			// sada://download/?url=... — macOS gets the same link through useDeepLinks instead.
			const requestedDownload = action ? parseDeepLinkDownloadUrl(action) : null
			if (requestedDownload !== null && platform !== 'macos') {
				const link = parseModelDownloadUrl(requestedDownload)
				if (!link) {
					console.error('refusing a model download deep link from an untrusted source', action)
				} else {
					const confirm = await ask(`${m.askForDownloadModel()} ${link.url}؟`, { title: m.downloadModel(), kind: 'info' })
					if (confirm) {
						// A catalog URL keeps its published size and SHA-256; a user URL has neither.
						navigate('/setup', { state: { downloadURL: link.url, downloadIntegrity: link.catalog } })
					}
				}
			}
			// if not action, probably it's open with action
			const newFiles: NamedPath[] = []
			for (const arg of argv) {
				if (config.audioExtensions.some((e) => arg.endsWith(e)) || config.videoExtensions.some((e) => arg.endsWith(e))) {
					newFiles.push(await pathToNamedPath(arg))
				}
			}
			if (newFiles.length > 0) {
				setFiles([...newFiles])
			}
		})
	}

	useEffect(() => {
		handleSingleInstance()
	}, [])
}
