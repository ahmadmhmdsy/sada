import { ReactNode, createContext, useState } from 'react'
import type { ErrorKind } from '~/lib/error-kind'
import { ModifyState } from '~/lib/types'

export interface ErrorModalState {
	open: boolean
	log?: string
	/** A source that already knows what failed can skip the text classifier. */
	kind?: ErrorKind
}
interface ErrorModalContext {
	state: ErrorModalState
	setState: ModifyState<ErrorModalState>
}

export const ErrorModalContext = createContext<ErrorModalContext>({} as ErrorModalContext)

export function ErrorModalProvider({ children }: { children: ReactNode }) {
	const [state, setState] = useState<ErrorModalState>({ open: false, log: '' })
	return <ErrorModalContext.Provider value={{ setState, state }}>{children}</ErrorModalContext.Provider>
}
