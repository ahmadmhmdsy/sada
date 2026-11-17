//
// The one VAD gate every transcription path runs before it starts a model that needs Silero.
//
// Settings and setup used to gate only the model picker, so a queued run, a retry or a
// dictation with a Nemotron model could start without the VAD file and fail deep inside the
// engine. This module locates the file, downloads it once when the user agrees, and reports a
// plain boolean so callers only have to decide what to do when it is false.

import { invoke } from '@tauri-apps/api/core'
import { ask } from '@tauri-apps/plugin-dialog'
import { join } from '@tauri-apps/api/path'
import { toast } from 'sonner'
import { m } from '~/paraglide/messages.js'
import * as config from '~/lib/config'
import { downloadModel, isModelFileUsable, type ModelMetadata } from '~/lib/model'
import { vadGate } from '~/lib/model-capabilities'

export interface EnsureVadOptions {
	/**
	 * Ask before downloading. Settings and setup ask; a run that already started downloads
	 * quietly, because a modal in the middle of a queue would block every following file.
	 */
	confirm?: boolean
}

let inFlight: Promise<boolean> | null = null

/**
 * True when the model needs no VAD, or its Silero file is usable after this call.
 *
 * Concurrent callers share one download: a queue with ten files and a dictation hotkey
 * pressed twice must not race two writes into the same file.
 */
export async function ensureVadModel(metadata: ModelMetadata | null, options: EnsureVadOptions = {}): Promise<boolean> {
	if (inFlight) return inFlight
	inFlight = resolveVadModel(metadata, options).finally(() => {
		inFlight = null
	})
	return inFlight
}

async function resolveVadModel(metadata: ModelMetadata | null, options: EnsureVadOptions): Promise<boolean> {
	const requiresVad = metadata?.capabilities?.requires_vad ?? false
	if (vadGate(requiresVad, true) === 'skip') return true

	let modelsFolder: string
	try {
		modelsFolder = await invoke<string>('get_models_folder')
	} catch (error) {
		console.error('could not resolve the models folder for the VAD model:', error)
		toast.error(m.vadDownloadFailed())
		return false
	}
	const vadPath = await join(modelsFolder, config.vadModelFilename)
	if (vadGate(requiresVad, await isModelFileUsable(vadPath)) === 'satisfied') return true

	if (options.confirm !== false) {
		const confirmed = await ask(m.vadRequiredMessage(), { title: m.vadRequiredTitle(), kind: 'info' })
		if (!confirmed) return false
	}

	try {
		toast.loading(m.vadDownloading(), { id: 'vad-download' })
		const path = await downloadModel({ url: config.vadModelUrl }, { replacePath: vadPath })
		if (!path) {
			toast.error(m.vadDownloadFailed(), { id: 'vad-download' })
			return false
		}
		toast.success(m.downloadComplete(), { id: 'vad-download' })
		return true
	} catch (error) {
		console.error('failed to download the Silero VAD model:', error)
		toast.error(m.vadDownloadFailed(), { id: 'vad-download' })
		return false
	}
}
