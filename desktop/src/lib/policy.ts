import { invoke } from '@tauri-apps/api/core'

/**
 * Machine-wide restrictions written by an administrator (HKLM\\SOFTWARE\\Sada\\Policy, or a
 * policy.json the installer manages). The Rust side enforces every flag independently; this
 * module exists so the UI never offers a control whose backing action would be refused.
 */
export interface ManagedPolicy {
	/** No feature may contact the network. Implies every disable flag below. */
	offlineMode: boolean
	/** Hide AI providers (Claude, OpenAI, Ollama) and the AI settings pages. */
	disableAi: boolean
	/** Hide URL import (yt-dlp downloads and the media link tab). */
	disableUrlImport: boolean
	/** Hide model catalog downloads. */
	disableModelDownloads: boolean
	/** Fixed transcripts folder; hides the folder picker when set. */
	transcriptsDir: string | null
}

/** A machine with no policy behaves exactly like an unmanaged install. */
export const UNMANAGED_POLICY: ManagedPolicy = {
	offlineMode: false,
	disableAi: false,
	disableUrlImport: false,
	disableModelDownloads: false,
	transcriptsDir: null,
}

let pending: Promise<ManagedPolicy> | null = null

/** Read the policy once per launch. A failure means "unmanaged", matching the Rust default. */
export function loadManagedPolicy(): Promise<ManagedPolicy> {
	if (!pending) {
		pending = invoke<ManagedPolicy>('get_managed_policy')
			.then((policy) => ({ ...UNMANAGED_POLICY, ...policy, transcriptsDir: policy.transcriptsDir || null }))
			.catch((error) => {
				console.warn('managed policy unavailable; treating this machine as unmanaged', error)
				return UNMANAGED_POLICY
			})
	}
	return pending
}

/** Test-only: forget the cached policy so the next call re-reads the backend. */
export function resetManagedPolicyCache() {
	pending = null
}

export function aiDisabled(policy: ManagedPolicy): boolean {
	return policy.offlineMode || policy.disableAi
}

export function urlImportDisabled(policy: ManagedPolicy): boolean {
	return policy.offlineMode || policy.disableUrlImport
}

export function modelDownloadsDisabled(policy: ManagedPolicy): boolean {
	return policy.offlineMode || policy.disableModelDownloads
}

/** Phone handoff is not exposed in Sada at all; no policy value can turn it on. */
export function handoffDisabled(): boolean {
	return true
}

/** True when an administrator manages anything on this machine. */
export function hasManagedPolicy(policy: ManagedPolicy): boolean {
	return (
		policy.offlineMode ||
		policy.disableAi ||
		policy.disableUrlImport ||
		policy.disableModelDownloads ||
		Boolean(policy.transcriptsDir)
	)
}
