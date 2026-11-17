export const aboutURL = 'https://github.com/alshahia/sada'
export const repoURL = 'https://github.com/alshahia/sada'
export const updateVersionURL = 'https://github.com/alshahia/sada/releases/latest'
export const modelsDocURL = 'https://github.com/alshahia/sada#first-run-and-models'
/**
 * Release notes. With a version it opens that release, otherwise the whole list —
 * the page falls back to English for a release this locale has not translated.
 */
/** Upstream release notes, for the version this fork is based on. */
export const changelogURL = (_version?: string) => 'https://github.com/alshahia/sada/releases'
export const discordURL = 'https://github.com/alshahia/sada/issues'
export const supportVibeURL = 'https://github.com/alshahia/sada/issues'
export const privacyPolicyURL = 'https://github.com/alshahia/sada/blob/master/PRIVACY.md'
export const storeFilename = 'app_config.json'

/** What the catalog knows about a finished download, beyond the bytes themselves. */
export interface ModelIntegrity {
	/** Exact size in bytes of the published artifact. */
	size?: number
	/** Lowercase hex SHA-256 of the published artifact. */
	sha256?: string
}

/** One downloadable model. Only catalog entries carry integrity metadata — a URL the user pastes
 * into settings or opens with `vibe://download/?url=` never does, and falls back to the size and
 * magic-byte checks the backend runs on every download. */
export interface ModelDownload extends ModelIntegrity {
	url: string
}

// Integrity is checked when the bytes are downloaded: a size or hash mismatch rejects the file
// and the next mirror is tried. The primary Hugging Face entries are verified against the published
// artifacts (the values match upstream Vibe's model catalog); the GitHub fallback asset is left
// unset because its own published hash has not been verified here — an unset field falls back to the
// backend's size and magic-byte checks rather than rejecting a good download.
export const modelUrls: Record<'default' | 'hebrew', ModelDownload[]> = {
	default: [
		{
			url: 'https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo.bin',
			size: 1624555275,
			sha256: '1fc70f774d38eb169993ac391eea357ef47c88757ef72ee5943879b7e8e2bc69',
		},
		{
			url: 'https://huggingface.co/vibe-app/whisper-large-v3-turbo-gguf/resolve/main/ggml-large-v3-turbo.bin', // Hugging Face fallback
			size: 1624555275,
			sha256: '1fc70f774d38eb169993ac391eea357ef47c88757ef72ee5943879b7e8e2bc69',
		},
		{ url: 'https://github.com/thewh1teagle/vibe/releases/download/model-files-v1.0/ggml-large-v3-turbo.bin' }, // GitHub fallback
	],
	hebrew: [
		{
			url: 'https://huggingface.co/ivrit-ai/whisper-large-v3-turbo-ggml/resolve/main/ggml-model.bin',
			size: 1624555275,
			sha256: 'c8090411113357097bfafc2b8e228ec1639fa7f5fe4ecb5d054ac0ccef8641b1',
		},
	],
}

export const embeddingModelFilename = 'wespeaker_en_voxceleb_CAM++.onnx'
export const segmentModelFilename = 'segmentation-3.0.onnx'
export const embeddingModelUrl = 'https://github.com/thewh1teagle/vibe/releases/download/v0.0.1/wespeaker_en_voxceleb_CAM++.onnx'
export const segmentModelUrl = 'https://github.com/thewh1teagle/vibe/releases/download/v0.0.1/segmentation-3.0.onnx'

/**
 * Diarization runs NVIDIA Nemotron-3-Diarization (up to 8 speakers) on ggml, a GGUF exported from
 * the HF safetensors by `server/crates/nemotron-diarize-rs/scripts/export.py --dtype q8_0`.
 * Q8_0 matches F32 segments on upstream checks at a quarter of the size.
 *
 * Mirrored into the vibe-app org from `nvidia/Nemotron-3-Diarization` (OpenMDW 1.1).
 *
 * Anyone upgrading has speaker recognition on with this file missing: the transcription queue
 * runs the same download gate as the switch before the run. The models they had before stay
 * untouched — see `legacyDiarizeModelFilenames`.
 */
export const diarizeModelFilename = 'nemotron-3-diarization-Q8_0.gguf'
export const diarizeModelUrl = 'https://huggingface.co/vibe-app/nemotron-3-diarization-gguf/resolve/main/nemotron-3-diarization-Q8_0.gguf'
export const diarizeModelIntegrity: ModelIntegrity = {
	size: 108541632,
	sha256: 'a25f026847d765c8661fd5095c73a0e5f20d310dcb8249c654e3828592a2fc73',
}
/**
 * Diarization models earlier releases downloaded. Nothing reads them; they are listed only so the
 * Sortformer GGUF never shows up as a transcription model. The older 492 MB `.onnx` needs no entry:
 * it is not a `.gguf`/`.bin`, so the model listing never sees it. Deleting them is left to users.
 */
export const legacyDiarizeModelFilenames = ['diar_streaming_sortformer_4spk-v2.q8_0.gguf']
export const vadModelFilename = 'ggml-silero-v6.2.0.bin'
export const vadModelUrl = 'https://huggingface.co/ggml-org/whisper-vad/resolve/main/ggml-silero-v6.2.0.bin'

export const llmApiKeyUrl = 'https://console.anthropic.com/settings/keys'
export const llmDefaultMaxTokens = 8192 // https://docs.anthropic.com/en/docs/about-claude/models
export const llmLimitsUrl = 'https://console.anthropic.com/settings/limits'
export const llmCostUrl = 'https://console.anthropic.com/settings/cost'

export const ytDlpAssetNames: Record<string, string> = {
	'windows-x86_64': 'yt-dlp.exe',
	'windows-aarch64': 'yt-dlp_arm64.exe',
	'linux-x86_64': 'yt-dlp_linux',
	'linux-aarch64': 'yt-dlp_linux_aarch64',
	'macos-x86_64': 'yt-dlp_macos',
	'macos-aarch64': 'yt-dlp_macos',
}

export function ytDlpDownloadUrl(version: string, key: string): string {
	return `https://github.com/yt-dlp/yt-dlp/releases/download/${version}/${ytDlpAssetNames[key]}`
}

export const videoExtensions = ['mp4', 'mkv', 'avi', 'mov', 'wmv', 'webm', 'mxf']
export const audioExtensions = ['mp3', 'wav', 'aac', 'flac', 'oga', 'ogg', 'opic', 'opus', 'm4a', 'm4b', 'wma']
export const themes = ['light', 'dark']
export const defaultAutoSummarizeOnFinish = false

/**
 * Default dictation shortcut: Option+Space on macOS, Ctrl+Space elsewhere. Resolved on call rather
 * than at module scope: reading the platform at import time makes this file unimportable outside a
 * webview (and untestable).
 */
export function getDefaultHotkeyShortcut() {
	const isMac = navigator.platform.toUpperCase().includes('MAC')
	return isMac ? 'Alt+Space' : 'Ctrl+Space'
}

/** Global recording uses one portable accelerator on every desktop platform. */
export function getDefaultRecordingShortcut() {
	return 'CmdOrCtrl+Shift+R'
}
