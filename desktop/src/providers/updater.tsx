import React, { createContext, useState } from 'react'
import { ModifyState } from '~/lib/types'

/**
 * This fork does not update itself.
 *
 * There is no release server to ask, no signing key to trust and no updater plugin in the build,
 * so an update banner would be theatre at best and a remote-code path at worst. The context stays
 * because several affordances read it; with no manifest ever set they render nothing.
 */
export const FAKE_UPDATE_KEY = 'sada_fake_update'
export const devToolsEnabled = import.meta.env.DEV

export interface UpdateManifest {
	version: string
	date?: string
	body?: string
}

type UpdaterContextType = {
	availableUpdate: boolean
	setAvailableUpdate: ModifyState<boolean>
	updating: boolean
	setUpdating: ModifyState<boolean>
	manifest?: UpdateManifest
	setManifest: ModifyState<UpdateManifest | undefined>
	updateApp: () => Promise<void>
	progress: number | null
	fakeUpdate: boolean
	setFakeUpdate: (value: boolean) => void
}

export const UpdaterContext = createContext<UpdaterContextType>({
	availableUpdate: false,
	setAvailableUpdate: () => {},
	updating: false,
	setUpdating: () => {},
	setManifest: () => {},
	updateApp: async () => {},
	progress: null,
	fakeUpdate: false,
	setFakeUpdate: () => {},
})

export function UpdaterProvider({ children }: { children: React.ReactNode }) {
	const [manifest, setManifest] = useState<UpdateManifest | undefined>()
	return (
		<UpdaterContext.Provider
			value={{
				availableUpdate: false,
				setAvailableUpdate: () => {},
				updating: false,
				setUpdating: () => {},
				manifest,
				setManifest,
				updateApp: async () => {},
				progress: null,
				fakeUpdate: false,
				setFakeUpdate: () => {},
			}}>
			{children}
		</UpdaterContext.Provider>
	)
}
