import { onOpenUrl } from '@tauri-apps/plugin-deep-link'
import { m } from '~/paraglide/messages.js'
import { ModifyState, NamedPath } from './types'
import { pathToNamedPath } from './fs'
import { ask } from '@tauri-apps/plugin-dialog'
import * as config from '~/lib/config'
import { parseDeepLinkDownloadUrl, parseModelDownloadUrl } from './model-download-url'
import { useNavigate } from 'react-router-dom'
import { useEffect } from 'react'
import * as os from '@tauri-apps/plugin-os'
import { invoke } from '@tauri-apps/api/core'

interface UseDeepLinksProps {
	setFiles: ModifyState<NamedPath[]>
}

export function useDeepLinks({ setFiles }: UseDeepLinksProps) {
	const navigate = useNavigate()

	async function processURLs(urls: string[]): Promise<void> {
		const newFiles: NamedPath[] = []
		for (let url of urls) {
			const requestedDownload = parseDeepLinkDownloadUrl(url)
			if (requestedDownload !== null) {
				// Only a model URL the backend may fetch: https on a catalog host. The dialog
				// shows the whole URL, not just the host, so a lookalike path cannot hide.
				const link = parseModelDownloadUrl(requestedDownload)
				if (!link) {
					console.error('refusing a model download deep link from an untrusted source', url)
					break
				}
				const confirm = await ask(`${m.askForDownloadModel()} ${link.url}؟`, { kind: 'info', title: m.downloadModel() })
				if (confirm) {
					// A catalog URL keeps its published size and SHA-256; a user URL has neither.
					navigate('/setup', { state: { downloadURL: link.url, downloadIntegrity: link.catalog } })
				}
				break
			} else if (config.videoExtensions.some((e) => url.endsWith(e)) || config.audioExtensions.some((e) => url.endsWith(e))) {
				url = url.replace('file://', '')
				url = decodeURIComponent(url)
				const newFile = await pathToNamedPath(url)
				newFiles.push(newFile)
			}
		}
		setFiles(newFiles)
	}

	async function handleArgv() {
		const argv = await invoke<string[]>('get_argv')
		await processURLs(argv)
	}

	async function handleDeepLinks() {
		const platform = await os.platform()
		if (['windows', 'linux'].includes(platform)) {
			return
		}
		onOpenUrl(async (urls) => {
			await processURLs(urls)
		})
	}

	useEffect(() => {
		handleArgv()
		handleDeepLinks()
	}, [])
}
