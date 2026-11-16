import { describe, expect, it } from 'vitest'
import { CONFIG_KEYS } from './config-keys'
import { composeSkill, withFrontmatter, type SkillContext } from './skill'

const context: SkillContext = {
	baseUrl: 'http://127.0.0.1:51234',
	serverSkill: '# Server Local Transcription API\n\nBase URL: http://127.0.0.1:51234\n',
	transcriptsFolder: '/Users/me/Documents/Sada',
	configPath: '/Users/me/Library/Application Support/vibe/app_config.json',
	dictationShortcut: 'Alt+Space',
	serverBinary: '/Applications/vibe.app/Contents/MacOS/server',
	sadaBinary: '/Applications/vibe.app/Contents/MacOS/vibe',
}

describe('composeSkill', () => {
	// A refactor that drops a section is invisible until an agent is missing half its instructions.
	it('keeps every part an agent needs', () => {
		const skill = composeSkill(context)
		expect(skill).toContain('# Server Local Transcription API')
		expect(skill).toContain(context.baseUrl)
		expect(skill).toContain(context.transcriptsFolder!)
		expect(skill).toContain(context.configPath!)
		expect(skill).toContain('transcript.vibe.json')
		expect(skill).toContain('"dictation.shortcut": "Alt+Space"')
		expect(skill).toContain('# When invoked without a task')
	})

	// The port is per-run: an agent that cannot find the live one, or the offline route, is stuck.
	it('routes around the dynamic port', () => {
		const skill = composeSkill(context)
		expect(skill).toContain(CONFIG_KEYS.apiBaseUrl)
		expect(skill).toContain('/health')
		expect(skill).toContain(context.serverBinary!)
		expect(skill).toContain(context.sadaBinary!)
	})

	// MCP is the route that works without a port or a running GUI: it must stay documented.
	it('documents the stdio MCP server and how to register it', () => {
		const skill = composeSkill(context)
		expect(skill).toContain('--mcp')
		expect(skill).toContain('claude mcp add sada')
		expect(skill).toContain('[mcp_servers.sada]')
		expect(skill).toContain('sada_transcribe')
		expect(skill).toContain('sada_info')
		expect(skill).toContain(context.sadaBinary!)
	})

	it('falls back to the executable name when the app path cannot be resolved', () => {
		const skill = composeSkill({ ...context, sadaBinary: null })
		expect(skill).toContain('Sada.exe --mcp')
	})

	it('still names both transcript layouts when the folder cannot be resolved', () => {
		const skill = composeSkill({ ...context, transcriptsFolder: null, configPath: null, serverBinary: null, sadaBinary: null })
		expect(skill).toContain('$HOME/Documents/Sada')
		expect(skill).toContain('Settings → API & Agents → Config file')
		expect(skill).toContain('bundles the `server` engine')
	})
})

describe('withFrontmatter', () => {
	it('opens with the frontmatter the agent runtimes index by', () => {
		expect(withFrontmatter(composeSkill(context)).split('\n').slice(0, 4)).toEqual(['---', 'name: sada', expect.stringContaining('description:'), '---'])
	})
})
