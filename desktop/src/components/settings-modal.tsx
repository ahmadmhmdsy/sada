import { useRef } from 'react'
import { m } from '~/paraglide/messages.js'
import { ModifyState } from '~/lib/types'
import { Dialog, DialogContent, DialogTitle } from '~/components/ui/dialog'
import SettingsPage from '~/pages/settings/page'

interface SettingsModalProps {
	visible: boolean
	setVisible: ModifyState<boolean>
	scrollTo?: string
}

/**
 * Radix owns the dialog contract — role, aria-modal, focus trap, Escape and outside click — so
 * the settings window behaves like every other dialog instead of a div that imitates one.
 */
export default function SettingsModal({ visible, setVisible, scrollTo }: SettingsModalProps) {
	const previousFocusRef = useRef<HTMLElement | null>(null)

	return (
		<Dialog
			open={visible}
			onOpenChange={(open) => !open && setVisible(false)}>
			<DialogContent
				hideClose
				aria-describedby={undefined}
				onOpenAutoFocus={() => {
					previousFocusRef.current = document.activeElement as HTMLElement | null
				}}
				onCloseAutoFocus={(event) => {
					// Return focus to the control that opened settings, not to the document body.
					event.preventDefault()
					previousFocusRef.current?.focus?.()
				}}
				className="w-auto max-w-none gap-0 overflow-visible border-0 bg-transparent p-0 shadow-none">
				<DialogTitle className="sr-only">{m.settings()}</DialogTitle>
				<SettingsPage setVisible={setVisible} scrollTo={scrollTo} />
			</DialogContent>
		</Dialog>
	)
}
