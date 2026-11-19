import { invoke } from '@tauri-apps/api/core'
import type { AiConnection, AiSettings } from './config'

/**
 * API keys are stored with DPAPI (Windows Data Protection API) as opaque hex blobs, so a copied
 * app_config.json or a roaming backup cannot unlock them on another account or machine. The
 * plaintext fields on AiSettings only ever exist in memory; every write goes through
 * `sealAiSecrets`, every boot through `openAiSecrets`.
 */
const SECRET_FIELDS = [
	{ plain: 'claudeApiKey', encrypted: 'claudeApiKeyEnc' },
	{ plain: 'openaiApiKey', encrypted: 'openaiApiKeyEnc' },
] as const

type SecretField = (typeof SECRET_FIELDS)[number]

function read(connection: AiConnection, field: string): string {
	const value = (connection as unknown as Record<string, unknown>)[field]
	return typeof value === 'string' ? value : ''
}

function write(connection: AiConnection, field: string, value: string) {
	;(connection as unknown as Record<string, unknown>)[field] = value
}

async function protect(value: string): Promise<string> {
	if (!value) return ''
	try {
		return await invoke<string>('protect_secret', { value })
	} catch (error) {
		// Failing closed would erase the user's key on the next save; keep the old behaviour on a
		// platform without DPAPI and report it instead.
		console.error('could not encrypt an API key at rest', error)
		return ''
	}
}

async function unprotect(value: string): Promise<string> {
	if (!value) return ''
	try {
		return await invoke<string>('unprotect_secret', { value })
	} catch (error) {
		// A profile copied from another Windows account cannot decrypt its keys; start empty rather
		// than show a bogus key or crash.
		console.warn('could not decrypt a saved API key', error)
		return ''
	}
}

/** True when at least one encrypted key is stored. */
export function hasStoredAiSecrets(settings: AiSettings): boolean {
	return SECRET_FIELDS.some((field: SecretField) => read(settings.connection, field.encrypted) !== '')
}

/** True when a plaintext key is waiting to be sealed (pre-DPAPI config or a fresh install). */
export function hasPlaintextAiSecrets(settings: AiSettings): boolean {
	return SECRET_FIELDS.some((field: SecretField) => read(settings.connection, field.plain) !== '')
}

/**
 * Move plaintext keys into DPAPI blobs before anything is persisted. Returns a copy: the caller's
 * in-memory settings (the ones the AI client uses) keep their plaintext keys.
 */
export async function sealAiSecrets(settings: AiSettings): Promise<AiSettings> {
	const connection: AiConnection = { ...settings.connection }
	for (const field of SECRET_FIELDS) {
		const plaintext = read(connection, field.plain)
		write(connection, field.encrypted, plaintext ? await protect(plaintext) : '')
		// The plaintext copy never reaches the config file.
		write(connection, field.plain, '')
	}
	return { ...settings, connection }
}

/** Decrypt stored keys for this boot. A missing blob or a failed decrypt leaves the field empty. */
export async function openAiSecrets(stored: AiSettings): Promise<AiSettings> {
	const connection: AiConnection = { ...stored.connection }
	for (const field of SECRET_FIELDS) {
		if (read(connection, field.plain)) continue
		const encrypted = read(connection, field.encrypted)
		if (encrypted) write(connection, field.plain, await unprotect(encrypted))
	}
	return { ...stored, connection }
}
