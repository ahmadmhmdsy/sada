import { useState } from 'react'
import { invoke } from '@tauri-apps/api/core'
import { toast } from 'sonner'
import { m } from '~/paraglide/messages.js'
import { Button } from '~/components/ui/button'
import { Switch } from '~/components/ui/switch'
import { hasManagedPolicy, modelDownloadsDisabled } from '~/lib/policy'
import { SettingsGroup, SettingsNote, SettingsRow, rowControlClass, type SettingsViewModel } from './shared'

/** Retention windows offered in the picker. 0 means "keep until the user deletes them". */
const RETENTION_CHOICES = [0, 7, 30, 90, 365]

interface PurgeResult {
	deleted: number
	freedBytes: number
}

/**
 * What this build actually does with personal data, stated plainly: no analytics, no telemetry,
 * no account. The only automatic deletion is the app's own transcript retention window, and it
 * never touches exported files.
 */
export function PrivacySection({ vm }: { vm: SettingsViewModel }) {
	const policy = vm.preference.managedPolicy
	const days = vm.preference.retentionDays
	const [purging, setPurging] = useState(false)
	const transcriptsDir = vm.preference.projectsPath ?? vm.defaultProjectsPath
	const downloadsDisabled = modelDownloadsDisabled(policy)

	async function purgeNow() {
		if (!transcriptsDir) return
		setPurging(true)
		try {
			// An ad-hoc purge uses the chosen window; "keep forever" still lets the user purge now,
			// so ask the backend for the smallest window rather than zero (which deletes nothing).
			const result = await invoke<PurgeResult>('purge_old_transcripts', { dir: transcriptsDir, days: days || 1 })
			toast.success(m.privacyRetentionDone({ count: String(result.deleted) }))
		} catch (error) {
			console.error('transcript purge failed', error)
			toast.error(m.privacyRetentionFailed())
		} finally {
			setPurging(false)
		}
	}

	return (
		<div className="space-y-6">
			<p className="text-sm leading-relaxed text-muted-foreground">{m.privacyLocalOnly()}</p>

			{hasManagedPolicy(policy) && (
				<SettingsGroup title={m.managedPolicyTitle()}>
					<SettingsNote>{m.managedPolicyInfo()}</SettingsNote>
					{policy.offlineMode && <SettingsNote>{m.managedPolicyOffline()}</SettingsNote>}
					{policy.disableAi && !policy.offlineMode && <SettingsNote>{m.managedPolicyAi()}</SettingsNote>}
					{policy.disableUrlImport && !policy.offlineMode && <SettingsNote>{m.managedPolicyUrlImport()}</SettingsNote>}
					{downloadsDisabled && <SettingsNote>{m.managedPolicyModelDownloads()}</SettingsNote>}
					{policy.transcriptsDir && <SettingsNote>{m.managedPolicyTranscriptsDir({ path: policy.transcriptsDir })}</SettingsNote>}
				</SettingsGroup>
			)}

			<SettingsGroup>
				<SettingsRow label={m.saveProjects()} description={m.saveProjectsInfo()}>
					<Switch checked={vm.preference.saveTranscripts} onCheckedChange={vm.preference.setSaveTranscripts} />
				</SettingsRow>
			</SettingsGroup>

			<SettingsGroup title={m.privacyRetentionTitle()} description={m.privacyRetentionInfo()}>
				<SettingsRow label={m.privacyRetentionTitle()} description={m.privacyRetentionNote()}>
					<select
						aria-label={m.privacyRetentionTitle()}
						value={String(days)}
						onChange={(event) => vm.preference.setRetentionDays(Number(event.target.value))}
						className={`${rowControlClass} min-w-32 border border-border bg-background px-3 text-sm`}>
						{RETENTION_CHOICES.map((choice) => (
							<option key={choice} value={String(choice)}>
								{choice === 0 ? m.privacyRetentionKeepForever() : m.privacyRetentionDaysOption({ days: String(choice) })}
							</option>
						))}
					</select>
				</SettingsRow>
				<SettingsRow label={m.privacyRetentionRun()}>
					<Button variant="outline" size="sm" className="rounded-lg" disabled={purging || days <= 0} onClick={() => void purgeNow()}>
						{m.privacyRetentionRun()}
					</Button>
				</SettingsRow>
			</SettingsGroup>
		</div>
	)
}
