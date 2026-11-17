# Changelog

Sada is an Arabic-first fork of [Vibe](https://github.com/thewh1teagle/vibe) (MIT). The upstream
project keeps its own detailed release history; this file records Sada releases and the fork's
delta from upstream v3.2.2.

## v3.3.1 — 2026-11-17

Engine and GPU foundation release: the bundled engine moves to upstream vibe-server v0.6.16, the
diarization model is replaced, and the GPU/Vulkan support that was already in the engine is
finally documented with a user-facing device story.

### Changed

- Engine sidecar `.server-version` v0.6.10 → v0.6.16: Vulkan and large-file crash fixes, non-AVX
  (SSE4.2) CPU support, sentence/paragraph reconstruction, repeated-line retries.
- Diarization model: the retired Sortformer ONNX file is replaced by `nemotron-3-diarization-Q8_0.gguf`
  (108,541,632 bytes, SHA-256 pinned); the old filename is filtered out of the model list so it no
  longer looks like a transcription model. Users who had it keep the file on disk — nothing is deleted.
- Bundled FFmpeg 9.0.1 → 9.0.2 (GPLv3; notices and source offer updated).

### Added

- GPU/Vulkan documentation: README.md, README.ar.md, docs/BUILDING.md and docs/DEBUG.md now explain
  the Settings → Models → Hardware device picker, what Auto means, CPU fallback when Vulkan is
  missing, the out-of-memory retry-and-remember behaviour, and the Vulkan runtime requirement.
- `docs/VERIFICATION.md` section for 3.3.1 and bilingual `docs/releases/v3.3.1.md`.
## v3.3.0 — 2026-11-16

Agent interface release: Sada can now act as an MCP server for AI agents, with Arabic-first defaults.

### Added

- **MCP server** (`Sada.exe --mcp`): JSON-RPC over stdio — initialize, ping, tools/list,
  tools/call, empty resources/prompts; protocol revisions 2025-06-18 / 2025-03-26 / 2024-11-05.
  No port, no network, no GUI.
- **Four tools**: `sada_transcribe` (local audio/video to Arabic transcript, optional
  timestamps, language auto, normalization on by default), `sada_transcripts` (list saved
  transcripts), `sada_transcript` (read one, optional timecodes and speakers), `sada_info`
  (install diagnostics).
- **Rust twin of the Arabic normaliser** (`desktop/src-tauri/src/arabic.rs`) shared by MCP
  output, with parity tests against the TypeScript rules.
- **Documentation**: [docs/AGENT-MCP.md](docs/AGENT-MCP.md),
  [docs/AGENT-MCP.ar.md](docs/AGENT-MCP.ar.md), [docs/VOICEBOX-REVIEW.md](docs/VOICEBOX-REVIEW.md)
  and [docs/VOICEBOX-REVIEW.ar.md](docs/VOICEBOX-REVIEW.ar.md).

### Changed

- The installed agent skill is now **sada** (`.claude|.codex/skills/sada/SKILL.md`) and leads
  with MCP registration, keeping the transcript-folder, local-API and engine-CLI routes as
  fallbacks.
- Settings About/repository/privacy links point at the Sada repository instead of upstream Vibe.
- Version bumped to 3.3.0.

### Removed

- Nothing. No new dependencies, no extra binaries, no extra models.

## v3.2.2 — 2026-11-16

First public release of Sada, built from Vibe v3.2.2 (commit `23eae78`).

### Added

- **Arabic-first fork**: full Arabic UI catalogue `ar-IQ` (704 keys), RTL shell and settings,
  Arabic-first defaults (display `ar-IQ`, transcription `ar`, no translation, temperature 0,
  beam 5), IBM Plex Sans Arabic typography, Western digits and Iraqi date formats.
- **Arabic transcript normalization**: Arabic punctuation (`، ؟ ؛`), whitespace cleanup and
  restoration of common Latin acronyms in Arabic text.
- **Arabic PDF export** with an embedded Arabic font and correct shaping.
- **New identity**: product name Sada (صدى), `Sada.exe`, identifier `app.sada.desktop`, scheme
  `sada`, new icon set and artwork.
- **Documentation and attestation**: Arabic and English README, PRIVACY, NOTICE,
  THIRD-PARTY-NOTICES, upstream delta list, verification report, licences.
- **Delivery automation**: CI workflow for build/tests, release workflow (tag → Windows installer +
  GitHub Release with checksums), and a bilingual GitHub Pages site with `llms.txt`.

### Changed

- Installation name/paths and Windows version metadata are Sada 3.2.2.
- The hidden meeting-prompt window now shares the same Arabic default, fixing an English-first-paint
  race on a fresh profile.

### Removed

- Telemetry/Aptabase client, auto-updater plugin, and the phone handoff entry point (code path
  remains compiled but unreachable).
- Vibe branding in shipped UI strings; upstream attribution remains in Settings → About and NOTICE.

### Known issues

- Unsigned installer (SmartScreen warning), no bundled model, occasional silence hallucinations
  and acronym/number normalization gaps. See [docs/VERIFICATION.md](docs/VERIFICATION.md).

### Upstream

Based on Vibe v3.2.2 (MIT). See [docs/UPSTREAM-PATCHES.md](docs/UPSTREAM-PATCHES.md) for the full
file-by-file delta.
