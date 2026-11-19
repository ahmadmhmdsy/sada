import { createContext, useContext, type ReactNode } from 'react'

/**
 * Settings rows own their visible label; a bare control inside the row (a switch, a select
 * trigger) has no accessible name of its own. The row publishes its label id here and those
 * controls consume it, so assistive technology announces the row label with the control.
 */
const RowLabelContext = createContext<string | undefined>(undefined)

export function RowLabelProvider({ labelId, children }: { labelId: string; children: ReactNode }) {
	return <RowLabelContext.Provider value={labelId}>{children}</RowLabelContext.Provider>
}

export function useRowLabelId() {
	return useContext(RowLabelContext)
}
