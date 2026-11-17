import bundled from '~/assets/model-catalog.json'
import { normalizeCatalog, type CatalogModel, type ModelCatalog } from './model-catalog'

/**
 * The licence column the council sealed: a model we may ship an entry for must allow commercial
 * use, carry no gate and no non-commercial clause. Anything else is dropped before it is shown.
 */
export const CURATED_LICENSES = ['MIT', 'Apache-2.0', 'CC-BY-4.0', 'OpenMDW-1.1'] as const

/**
 * A model the app may install unattended, per the evidence rule in ROADMAP.md: a licence from the
 * sealed list, a size, a SHA-256 and at least one language. Entries without that evidence never
 * reach the UI, even if they are syntactically valid.
 */
export function isCurated(model: CatalogModel): boolean {
	return (
		(CURATED_LICENSES as readonly (string | undefined)[]).includes(model.license) &&
		typeof model.size === 'number' &&
		model.size > 0 &&
		/^[0-9a-f]{64}$/.test(model.sha256 ?? '') &&
		model.languages.length > 0
	)
}

export function curateCatalog(value: unknown): ModelCatalog {
	const parsed = normalizeCatalog(value)
	if (!parsed) return { models: [] }
	const models = parsed.models.filter(isCurated)
	const dropped = parsed.models.length - models.length
	if (dropped > 0) console.warn(`[models] the catalog dropped ${dropped} entries without licence, size, hash or language`)
	return { models }
}

/**
 * The catalog as it was when this app was built: what an offline or blocked machine gets.
 * Sada never asks a server for it — the list is curated and shipped with the installer, so
 * "Get models" works on a fresh offline install. A catalogue change therefore ships with an app
 * release, the same way the verified hashes do.
 */
export const bundledCatalog: ModelCatalog = curateCatalog(bundled)
