# Changelog

Sada is an Arabic-first fork of [Vibe](https://github.com/thewh1teagle/vibe) (MIT). The upstream
project keeps its own detailed release history; this file records Sada releases and the fork's
delta from upstream v3.2.2.

## v3.5.0 — 2026-11-18

Measured Arabic model evaluation. No engine change (still `vibe-server v0.6.16-sada.1`); the
release adds the benchmark harness, the written decisions, one optional verified catalogue entry,
and the read-aloud and second-engine verdicts.

### Added

- **Arabic ASR benchmark harness** (`benchmarks/arabic-asr/`, stdlib Python, offline after the
  one-time fetch): pinned 60-clip manifest (30 MSA Common Voice 18 CC0, 10 Latin-mixed Common Voice,
  20 Egyptian FLEURS `ar_eg` CC BY 4.0), Arabic normalisation, corpus-level WER/CER, acronym and
  Latin-name preservation, word-timestamp coverage, RTF, per-slice curation verdicts, 38 `unittest`
  tests and a CI job. Audio and weights stay out of git.
- **NVIDIA Nemotron 3.5 ASR Streaming 0.6B** as an optional catalogue entry
  (`nemotron-3.5-asr-streaming-0.6b`, OpenMDW-1.1, 495,831,520 B, SHA-256
  `41c99fa5…b8fd`, Silero VAD supplied automatically). It wins the measured read MSA/Egyptian
  slices, adds punctuation, is faster and 3.3× smaller than Turbo; its description states that it
  transliterates Latin technical terms and that it is not the default.
- **Decision record** `docs/MODELS-DECISIONS.md` (measured numbers, rulings, reproduction commands,
  reopen conditions) and **read-aloud evidence** `docs/READ-ALOUD.md` (no-go for Windows voices).
- Evidence log §8 in `docs/MODELS-COUNCIL.md` and its Arabic mirror; ROADMAP P2 completed.

### Changed

- `docs/MODELS.md` / `docs/MODELS.ar.md`: the optional Nemotron entry, the rejected fine-tune and
  the unmeasured Iraqi/Gulf/Levantine/technical slices are documented honestly.
- Catalogue is now four curated entries (three Whisper models + Nemotron); no weight is bundled.

### Rejected (recorded, not shipped)

- Arabic Whisper fine-tune `whisper-large-v3-turbo-arabic-dialectal-v2-q5_0`: 23.09% overall WER vs
  19.46% for Turbo, no ≥1.0 pp slice win → not curated.
- Read-aloud via Windows voices: no Arabic voice in a normal install, rubric not runnable → no TTS code.
- Second engine (transcribe.cpp + Qwen3-ASR 0.6B, CPU): 24.38% overall WER (MSA 20.54%, Egyptian
  21.10%), no timestamps and no VAD → not integrated; keep-learning conditions recorded.

## v3.4.0 — 2026-11-17

Verified model catalog, model-capability gating and local endpoint hardening. The installer still
ships no model; the engine sidecar is now built from this repository with the loopback guard.

### Added

- **Verified model catalog** (`desktop/src/assets/model-catalog.json`) with a Get models experience
  in Settings → Models. Three commercially reusable entries — large-v3-turbo and tiny Whisper
  (MIT) and the Hebrew large-v3-turbo (Apache-2.0) — and compact engine models for users who choose
  them; each entry is validated for licence (MIT / Apache-2.0 / CC-BY-4.0 / OpenMDW-1.1), byte size,
  SHA-256 and language coverage before it can appear. Guides: `docs/MODELS.md`, `docs/MODELS.ar.md`.
- **Model capabilities everywhere.** `sada_info` reports the configured model's engine class,
  language list, Silero VAD requirement, and whether it supports translation and text prompts.
  `sada_transcribe` probes the model locally (no port), maps language codes to the model's list,
  finds the required VAD model automatically, and passes `--translate` / `--prompt` only when the
  model declares support. Documented in `docs/AGENT-MCP.md` and `docs/AGENT-MCP.ar.md`.
- **Language and VAD gating in the app.** Choosing a model reconciles the transcription language to
  the nearest supported one, and Settings, Setup, the transcription queue and the global hotkey all
  ensure the Silero VAD model is present before loading an engine that requires it. Five new
  strings in `en-US` and `ar-IQ`.

### Security

- **Loopback request guard in the bundled engine** (`server/crates/vibe-server/src/server/guard.rs`):
  only loopback `Host` values are accepted (DNS-rebinding defence) and browser `Origin` values must be
  loopback or the Tauri scheme, so a web page or a rebound hostname cannot drive the local API.
  Requests without `Host` are rejected. The guard applies only when the listener binds loopback; an
  explicit `--host` elsewhere remains opt-in network serving. Residual risk: a same-user local process
  can still reach the API (a per-run token is the next step). See `SECURITY.md`.
- The app now starts the engine with an explicit `--host 127.0.0.1 --port 0` instead of relying on the
  engine default, and the Release workflow rebuilds the engine from `server/` (`chore server-build`)
  and runs `cargo test -p vibe-server guard::` before packaging. `docs/UPSTREAM-PATCHES.md` §9 and
  `docs/ARCHITECTURE.md`, `docs/BUILDING.md` record the new delta.
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
