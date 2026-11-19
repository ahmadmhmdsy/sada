import { openUrl } from '@tauri-apps/plugin-opener'
import { useLocation, useNavigate } from 'react-router-dom'
import { ChevronDown, Copy, ExternalLink, RotateCcw } from 'lucide-react'
import { toast } from 'sonner'
import * as clipboard from '@tauri-apps/plugin-clipboard-manager'
import { m } from '~/paraglide/messages.js'
import { ModifyState } from '~/lib/types'
import { getIssueUrl, resetApp } from '~/lib/app'
import { classifyError, type ErrorKind } from '~/lib/error-kind'
import { collectLogs } from '~/lib/logs'
import { ErrorModalState } from '~/providers/error-modal'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '~/components/ui/dialog'
import { Button } from '~/components/ui/button'
import { Textarea } from '~/components/ui/textarea'

interface ErrorModalProps {
	state: ErrorModalState
	setState: ModifyState<ErrorModalState>
}

interface ErrorCopy {
	title: () => string
	body: () => string
	/** The one action worth leading with; everything else is secondary. */
	primary: 'settings' | 'retry' | 'close'
}

/**
 * Each kind gets its own sentence and its own action. The old dialog said "a bug happened" and
 * offered a destructive reset first, which told the user nothing about what to do next.
 */
const ERROR_COPY: Record<ErrorKind, ErrorCopy> = {
	model: { title: m.errorModelTitle, body: m.errorModelBody, primary: 'settings' },
	network: { title: m.errorNetworkTitle, body: m.errorNetworkBody, primary: 'retry' },
	audio: { title: m.errorAudioTitle, body: m.errorAudioBody, primary: 'close' },
	file: { title: m.errorFileTitle, body: m.errorFileBody, primary: 'close' },
	disk: { title: m.errorDiskTitle, body: m.errorDiskBody, primary: 'close' },
	memory: { title: m.errorMemoryTitle, body: m.errorMemoryBody, primary: 'close' },
	managed: { title: m.errorManagedTitle, body: m.errorManagedBody, primary: 'settings' },
	unknown: { title: m.errorTitle, body: m.modalErrorBody, primary: 'close' },
}

export default function ErrorModal({ state, setState }: ErrorModalProps) {
	const navigate = useNavigate()
	const location = useLocation()
	const kind: ErrorKind = state.kind ?? classifyError(state.log)
	const copy = ERROR_COPY[kind]
	const log = state.log ?? ''

	async function clearLogAndReset() {
		setState({ open: false, log: '' })
		resetApp()
	}

	async function reportIssue() {
		let info = ''
		try {
			info = await collectLogs()
		} catch (error) {
			console.error(error)
			info = `Couldn't get info: ${error}`
		}

		const url = await getIssueUrl(state?.log + '\n' + info)
		openUrl(url)
	}

	async function copyDetails() {
		try {
			await clipboard.writeText(log)
			toast.success(m.errorDetailsCopied(), { position: 'bottom-center' })
		} catch (error) {
			console.error('copy error details failed', error)
		}
	}

	/** Close first, then go where the fix lives; setup has no Layout listening for the event. */
	function recover() {
		setState({ open: false, log: '' })
		if (copy.primary === 'settings') {
			if (location.pathname === '/setup') {
				navigate('/#settings', { replace: true, state: { disableBack: true } })
				return
			}
			window.dispatchEvent(new CustomEvent('vibe:open-settings', { detail: { scrollTo: 'models' } }))
			return
		}
		if (copy.primary === 'retry') {
			// Setup re-runs its online check and download on mount, so a reload is a real retry.
			if (location.pathname === '/setup') {
				window.location.reload()
				return
			}
			window.dispatchEvent(new CustomEvent('vibe:open-settings', { detail: { scrollTo: 'models' } }))
		}
	}

	return (
		<Dialog open={state?.open} onOpenChange={(open) => setState({ ...state, open })}>
			<DialogContent className="max-w-md">
				<DialogHeader>
					<DialogTitle>{copy.title()}</DialogTitle>
					<DialogDescription>{copy.body()}</DialogDescription>
				</DialogHeader>

				{/* The raw message is evidence, not the headline: keep it behind a disclosure. */}
				<details className="group rounded-lg border border-border/60 bg-muted/25 px-3 py-2">
					<summary className="flex cursor-pointer list-none items-center gap-1.5 text-xs font-medium text-muted-foreground transition-colors hover:text-foreground">
						<ChevronDown aria-hidden="true" className="h-3.5 w-3.5 transition-transform group-open:rotate-180" />
						{m.errorRawDetails()}
					</summary>
					<Textarea
						readOnly
						dir="ltr"
						value={log}
						aria-label={m.errorRawDetails()}
						className="mt-2 max-h-28 w-full font-mono text-[11px]"
					/>
				</details>

				<div className="flex flex-col gap-2 sm:flex-row">
					{copy.primary === 'close' ? (
						<Button onClick={() => setState({ open: false, log: '' })} className="flex-1">
							{m.modalClose()}
						</Button>
					) : (
						<Button onClick={recover} className="flex-1">
							{copy.primary === 'settings' ? m.errorOpenSettings() : m.tryAgain()}
						</Button>
					)}
					<Button variant="outline" onClick={() => void copyDetails()} className="flex-1">
						<Copy aria-hidden="true" />
						{m.errorCopyDetails()}
					</Button>
				</div>

				<div className="flex justify-end">
					<button
						type="button"
						onClick={() => void reportIssue()}
						className="flex cursor-pointer items-center gap-1 text-xs font-medium text-muted-foreground transition-colors hover:text-foreground">
						<ExternalLink aria-hidden="true" className="h-3 w-3" />
						{m.reportIssue()}
					</button>
				</div>

				<DialogFooter className="flex-col items-stretch gap-2 sm:flex-col">
					{/* Reset was the primary action before; it is a last resort, so it lives here. */}
					<details className="rounded-lg border border-border/50 px-3 py-2">
						<summary className="cursor-pointer text-xs font-medium text-muted-foreground transition-colors hover:text-foreground">
							{m.errorAdvanced()}
						</summary>
						<p className="mt-2 text-xs leading-relaxed text-muted-foreground">{m.errorResetHint()}</p>
						<Button variant="outline" size="sm" onClick={() => void clearLogAndReset()} className="mt-2 w-fit text-destructive">
							<RotateCcw aria-hidden="true" />
							{m.resetApp()}
						</Button>
					</details>
				</DialogFooter>
			</DialogContent>
		</Dialog>
	)
}
