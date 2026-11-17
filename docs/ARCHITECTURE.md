# Sada Architecture

## Overview

Sada is a desktop transcription app built with **Tauri** (Rust + TypeScript frontend). It is a fork
of Vibe v3.2.2; the sections below describe the upstream architecture first, then the Sada-specific
additions (Arabic first-run/normalisation and the MCP agent interface).

## Components

### Desktop App (`desktop/`)

- **Frontend**: TypeScript + React (UI)
- **Backend**: Rust/Tauri (`desktop/src-tauri/`)
- Handles UI, file management, settings, analytics
- Spawns and communicates with the server via local HTTP

### Server (`server/`)

- **Language**: Rust on ggml (`whisper-rs`, `parakeet-rs`, `nemotron-rs`, `vad-rs`, `diarize-rs`)
- **Location**: `server/` in this repository, its own Cargo workspace; crate and binary `vibe-server`
- **Purpose**: single local process for audio transcription, model loading, streaming, and diarization, behind an OpenAI-compatible HTTP API
- Bundled as the `vibe-server` sidecar with the desktop app
- Diarization is in-process via `diarize-rs`; Vibe does not bundle or spawn a separate binary
- **Build**: `server-libs.yml` publishes the prebuilt ggml libraries (`libraries-ggml-<version>-r<revision>`, inputs under `server/libs/`); `server-release.yml` publishes `server-v*` prereleases; `server-test.yml` runs a release across platforms
- **Request guard (Sada)**: loopback listeners reject requests whose `Host` is not `127.0.0.1`/`localhost`/`[::1]` for the bound port, and requests whose `Origin` is not a loopback/Tauri origin. This blocks DNS rebinding and cross-origin pages from driving the engine; see [SECURITY.md](../SECURITY.md)
- **Distribution**: the app downloads the release named by `.server-version` at build time (`setup` task in the root `chorefile`) for FFmpeg and dev use; since Sada 3.4.0 the **Release** workflow also runs `chore server-build` so the installer ships the guarded engine built from this tree

### FFmpeg Helper

- macOS and Windows builds also bundle `ffmpeg` from the server release archives
- Vibe passes its path to the server with `VIBE_SERVER_FFMPEG_PATH`

### Build Flow

1. Vibe CI runs `chore setup <target-triple>`
2. It downloads the prebuilt `vibe-server` from the `server-v*` release in `.server-version`
3. Binaries placed in `desktop/src-tauri/binaries/`
4. Sada 3.4.0+: `chore server-build <triple>` rebuilds the engine from `server/` (with the request guard) over the downloaded sidecar, and its guard tests run before packaging
5. Tauri bundles `vibe-server` and, where configured, `ffmpeg` into the final app

## Agent interface — MCP (Sada 3.3.0)

`Sada.exe --mcp` starts a local MCP server before any Tauri builder or window is created, so it
works headlessly with no GUI, no port and no network.

- `desktop/src-tauri/src/mcp/mod.rs` — stdio JSON-RPC loop: `initialize` (protocol revisions
  2025-06-18 / 2025-03-26 / 2024-11-05), `ping`, `tools/list`, `tools/call`, empty
  `resources/list`/`prompts/list`, parse and method errors. One flushed JSON line per frame on
  stdout; diagnostics on stderr.
- `desktop/src-tauri/src/mcp/tools.rs` — four tools (`sada_transcribe`, `sada_transcripts`,
  `sada_transcript`, `sada_info`) and install resolution.
- `desktop/src-tauri/src/mcp/transcripts.rs` — scans saved project folders and legacy flat
  records, renders them with `HH:MM:SS.mmm` timecodes.
- `desktop/src-tauri/src/arabic.rs` — Rust twin of `desktop/src/lib/arabic-text.ts`; same
  normalisation rules so live UI text and MCP output cannot drift.
- Resolution order: config file (`--config`, `SADA_CONFIG_PATH`, `%APPDATA%|%LOCALAPPDATA%` +
  legacy Vibe folders, flat dotted keys such as `model.path`), model (`model.path` or the tool
  argument), engine (`SADA_ENGINE`, exe-relative `vibe-server*.exe`, `binaries/` ancestors, PATH),
  FFmpeg (`VIBE_SERVER_FFMPEG_PATH` or next to the engine) and transcripts folder
  (`transcription.projectsPath`, `SADA_TRANSCRIPTS_DIR`, Documents/Sada).
- Language defaults to the app language (`transcription.modelOptions.lang`), which is `ar` on a
  fresh profile; the tool schema offers `language: "auto"` and optional translation.
- Tests: `cargo test --release` covers `mcp::` and `arabic::`.

## Key Point for Agents

Native runtime compatibility issues for transcription usually come from the server or its linked ggml libraries, not the UI code. MCP/transcription integration issues almost always come from install resolution (config path, model path, sidecar location) — check that first, and keep the transport stdio-only: no HTTP server, port or listener may be added to MCP.

To fix one, change `server/` (a ggml fix goes in `server/libs/patches/` with a revision bump), tag a `server-v*` release, then bump `.server-version` here.
