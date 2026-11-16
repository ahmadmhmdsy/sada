import { m } from '~/paraglide/messages.js'
import { Switch } from '~/components/ui/switch'
import { SettingsGroup, SettingsRow, type SettingsViewModel } from './shared'

/**
 * This build has no analytics to toggle and no remote policy page to open, so the section states
 * what is actually true of it instead of offering switches whose other side is compiled out.
 */
export function PrivacySection({ vm }: { vm: SettingsViewModel }) {
	return (
		<div className="space-y-6">
			<p className="text-sm leading-relaxed text-muted-foreground">{m.privacyLocalOnly()}</p>
			<SettingsGroup>
				<SettingsRow label={m.saveProjects()} description={m.saveProjectsInfo()}>
					<Switch checked={vm.preference.saveTranscripts} onCheckedChange={vm.preference.setSaveTranscripts} />
				</SettingsRow>
			</SettingsGroup>
		</div>
	)
}
