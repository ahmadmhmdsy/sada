import { motion } from 'framer-motion'
import { m } from '~/paraglide/messages.js'
import { viewModel } from './view-model'
import { Progress } from '~/components/ui/progress'
import { Spinner } from '~/components/ui/spinner'
import { Button } from '~/components/ui/button'
import { Dialog, DialogContent } from '~/components/ui/dialog'
import { Tooltip, TooltipContent, TooltipTrigger } from '~/components/ui/tooltip'

/**
 * Bytes travel between Rust and the UI as a number; one decimal is enough for a progress line.
 * The isolate marks keep "25 MB" one left-to-right run: inside an Arabic sentence the bidi
 * algorithm would otherwise draw the unit before the number.
 */
function formatBytes(bytes: number) {
	const size =
		bytes >= 1_000_000_000
			? `${(bytes / 1_000_000_000).toFixed(1)} GB`
			: bytes >= 10_000_000
				? `${Math.round(bytes / 1_000_000)} MB`
				: `${(bytes / 1_000_000).toFixed(1)} MB`
	return `\u2066${size}\u2069`
}

function App() {
	const vm = viewModel()
	const percent = Math.round(vm.downloadProgress)
	const sizeProgress = vm.downloadBytes
		? m.downloadSizeProgress({ done: formatBytes(vm.downloadBytes.done), total: formatBytes(vm.downloadBytes.total) })
		: null
	const timeLeft =
		vm.estimatedMinutesLeft === null
			? null
			: vm.estimatedMinutesLeft <= 1
				? m.downloadAlmostDone()
				: m.downloadTimeLeft({ minutes: String(vm.estimatedMinutesLeft) })
	// The progressbar carries one readable value text; a live region per tick would spam a screen reader.
	const progressText = [`${percent}%`, sizeProgress, timeLeft].filter(Boolean).join(' · ')

	return (
		<div className="flex min-h-screen items-center justify-center px-5 py-10">
			<motion.div
				initial={{ opacity: 0, y: 8 }}
				animate={{ opacity: 1, y: 0 }}
				transition={{ duration: 0.22, ease: 'easeOut' }}
				className="w-full max-w-lg text-center">
				<p className="eyebrow">{m.setup({ defaultValue: 'Setup' })}</p>
				<h1 className="mt-4 text-balance text-[28px] font-semibold leading-[1.1] tracking-[-0.03em] md:text-[36px]">{m.downloadingModel()}</h1>
				{/* First run is the one moment the download exception matters most; say it before the bytes. */}
				<p className="mx-auto mt-3 max-w-md text-balance text-[13px] leading-relaxed text-muted-foreground">{m.setupTrust()}</p>

				<div className="mt-9 flex flex-col items-center gap-4">
					{vm.downloadProgress > 0 && (
						<>
							<div
								role="progressbar"
								aria-label={m.downloadingModel()}
								aria-valuemin={0}
								aria-valuemax={100}
								aria-valuenow={percent}
								aria-valuetext={progressText}
								className="w-full max-w-sm">
								<Progress className="progress-aurora h-1.5 w-full bg-muted" value={vm.downloadProgress} />
							</div>
							<div className="flex flex-wrap items-center justify-center gap-x-3 gap-y-1 text-[13px] text-muted-foreground">
								<span className="font-medium tabular-nums text-foreground">{percent}%</span>
								{sizeProgress && <span>{sizeProgress}</span>}
								{timeLeft && <span>{timeLeft}</span>}
							</div>
							{!vm.location?.state?.downloadURL && <p className="text-[12px] text-muted-foreground/80">{m.thisHappensOnce()}</p>}
						</>
					)}
					{(vm.downloadProgress === 0 || vm.isOnline === null) && <Spinner className="h-6 w-6 text-muted-foreground" />}
				</div>

				<Tooltip>
					<TooltipTrigger asChild>
						<Button
							variant="ghost"
							size="sm"
							className="mt-8 rounded-full px-4 text-[13px] font-medium text-muted-foreground hover:text-foreground"
							onClick={vm.cancelSetup}>
							{m.cancel()}
						</Button>
					</TooltipTrigger>
					<TooltipContent>{m.infoCancelDownload()}</TooltipContent>
				</Tooltip>
			</motion.div>

			<Dialog open={vm.isOnline === false}>
				<DialogContent className="rounded-2xl">
					<h2 className="text-center text-[22px] font-semibold tracking-[-0.03em]">{m.noConnection()}</h2>
					<p className="mt-2 text-center text-[13px] leading-relaxed text-muted-foreground">{m.infoManualDownload()}</p>
					<div className="mt-6 flex flex-col justify-center gap-2">
						<Button className="rounded-full" onClick={vm.downloadIfOnline}>
							{m.tryAgain()}
						</Button>
						<Button variant="ghost" size="sm" className="rounded-full text-muted-foreground hover:text-foreground" onClick={vm.cancelSetup}>
							{m.iPreferManualSetup()}
						</Button>
					</div>
				</DialogContent>
			</Dialog>
		</div>
	)
}

export default App
