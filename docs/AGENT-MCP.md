# Sada as an MCP server

Started in **3.3.0**. Sada is an Arabic-first, fully offline speech-to-text app, and this document
covers the MCP server that ships inside the app executable: agents get local transcription and the
user's saved transcripts through tools, without a server toggle, a port, or a running window.

Why it exists: Voicebox gives agents a voice (text to speech); Sada gives agents ears (Arabic-first
speech to text), on the user's own machine, with the same Arabic cleanup the app applies.

- **Transport:** stdio only. Nothing listens on a port, no network call is made.
- **GUI:** not required. The process starts, serves JSON-RPC, and exits when stdin closes.
- **Privacy:** media never leaves the machine; no account, telemetry or API key is involved.
- **Availability:** since 3.3.0, on the Windows x64 build.

## Quick start

The MCP server is the installed app executable with the **--mcp** argument:

~~~text
%LOCALAPPDATA%\Sada\Sada.exe --mcp
~~~

Smoke test without any client — send one JSON-RPC frame per line and read one frame per line:

~~~json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26"}}
{"jsonrpc":"2.0","id":2,"method":"tools/list"}
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"sada_info","arguments":{}}}
~~~

The server prints one line per response on stdout and logs to stderr. Close stdin to stop it.

## Registering the server

### Claude Code

~~~text
claude mcp add sada -- "C:/Users/you/AppData/Local/Sada/Sada.exe" --mcp
~~~

### Codex

In **~/.codex/config.toml**:

~~~toml
[mcp_servers.sada]
command = "C:/Users/you/AppData/Local/Sada/Sada.exe"
args = ["--mcp"]
~~~

### Any MCP client that takes JSON configuration

Claude Desktop, Cursor, Windsurf, Cline and most others accept the same shape:

~~~json
{
  "mcpServers": {
    "sada": {
      "command": "C:/Users/you/AppData/Local/Sada/Sada.exe",
      "args": ["--mcp"]
    }
  }
}
~~~

Restart the client after editing its configuration. On Windows the installed executable is under
**%LOCALAPPDATA%\Sada\** (per-user install, no administrator rights needed); a build from source writes **desktop/src-tauri/target/release/vibe.exe** (a Tauri bundle copies it in
as **Sada.exe**).

## Tools

| Tool | What it does |
| --- | --- |
| **sada_transcribe** | Transcribe one local audio or video file with the configured model. Returns plain text, Arabic-normalised by default. |
| **sada_transcripts** | List saved transcripts, newest first, with folder, record path and preview. |
| **sada_transcript** | Read one saved transcript as text; newest by default; optional timecodes and speaker labels. |
| **sada_info** | Report version, model, engine, transcript folder, config path and whether each file resolves. |

### sada_transcribe

| Argument | Type | Notes |
| --- | --- | --- |
| path | string, required | Absolute path to a local file (mp3, wav, m4a, mp4, mkv, ...). URLs are rejected. |
| language | string | Language code: two-letter (**ar**) or BCP-47 (**ar-AR**), mapped to the nearest language the configured model supports; **auto** asks the model to detect. Defaults to the app's language setting (Arabic). |
| translate | boolean | Translate speech to English instead of transcribing in the source language. Off by default; ignored by models that cannot translate (Nemotron, Parakeet). |
| timestamps | boolean | Prefix segments with [start --> end] timecodes. Off by default. |
| normalize | boolean | Apply Sada's Arabic cleanup. Default **true**. |
| model | string | Absolute path of a ggml model, overriding the configured one (advanced). |
| prompt | string | Initial prompt for engines that accept one — Whisper only for now (advanced; the configured prompt is used when omitted). |
| threads | integer | Engine CPU threads; 0 or omitted uses the configured/default value. |
| enhance_audio | boolean | Normalise loudness with the bundled FFmpeg first. Off by default. |
| vad_model | string | Silero VAD model path. Resolved automatically next to the configured model for engines that require VAD (Nemotron, Parakeet); pass this only to override (advanced). |

Example call:

~~~json
{"jsonrpc":"2.0","id":10,"method":"tools/call","params":{"name":"sada_transcribe","arguments":{"path":"C:/Users/you/Desktop/meeting.mp3","timestamps":true}}}
~~~

Before running, **sada_transcribe** asks the engine for the model's metadata and adapts the request:
language codes are mapped to the model's list, **--translate** and **--prompt** are passed only when the
model declares those capabilities, and a Silero VAD model is located automatically when the engine
requires one. The configured decoding settings (beam size, temperature, threads, prompt) are reused, so
MCP output matches what the same file produces in the app rather than the engine's bare defaults.

### sada_transcripts

| Argument | Type | Notes |
| --- | --- | --- |
| limit | integer | 1-50; default 10. |
| folder | string | Read a different transcripts folder (advanced). |

Returns JSON with **folder**, **total**, **shown** and a **transcripts** array; each entry has
**name**, **created_at**, **language**, **path**, optional **audio**, and a **preview**. Newest first,
sorted on the timestamp suffix the app writes into folder and file names.

### sada_transcript

| Argument | Type | Notes |
| --- | --- | --- |
| path | string | A **transcript.vibe.json** file or its project folder. Omit for the newest transcript. |
| timestamps | boolean | Prefix lines with [start --> end]. Off by default. |
| speakers | boolean | Label diarised lines as [speaker 1], [speaker 2], ... Off by default. |
| include_summary | boolean | Append the transcript's last saved AI summary. Off by default. |

Returns a small header (name, saved date, language, record path, audio) followed by the transcript
text. Segment timestamps in the stored record are centiseconds; the rendered timecodes are
HH:MM:SS.mmm.

### sada_info

No arguments. Returns JSON about this install:

~~~json
{
  "app": "Sada",
  "version": "3.8.0",
  "platform": "windows",
  "arabic_first": true,
  "engine": { "path": "...", "present": true },
  "ffmpeg": { "path": "...", "present": true },
  "model": {
    "path": "...",
    "present": true,
    "capabilities": {
      "engine": "nemotron",
      "languages": ["en-US", "ar-AR", "..."],
      "requires_vad": true,
      "translation": false,
      "text_prompts": false
    }
  },
  "transcription": { "default_language": "ar", "normalizes_arabic": true, "media_stays_local": true },
  "config_path": "...",
  "config_present": true,
  "transcripts_dir": "...",
  "tools": ["sada_transcribe", "sada_transcripts", "sada_transcript", "sada_info"],
  "notes": ["..."]
}
~~~

Start here when any tool reports a missing model or engine: it shows what Sada resolved and what is
missing.

## Arabic-first behaviour

- **Default language** comes from **transcription.modelOptions.lang** in the app config. A fresh
  profile sets **ar**; the UI can change it. Pass **language: "auto"** for detection.
- **Translation is off** unless asked for, because translating Arabic to English is not the common
  case for this app's users.
- **Arabic cleanup** is the same Rust implementation the UI uses: Arabic punctuation instead of
  ASCII commas/question marks/semicolons, hugging spaces removed, and common acronyms restored
  (GPU, CPU, PDF, SRT, VTT, JSON, API, FFmpeg, Whisper) when whisper.cpp wrote them as Arabic
  transliterations. It is lossless and idempotent; pass **normalize: false** to see the raw engine
  output.
- **RTL text** is returned as-is. Clients that display it should respect the text direction of the
  document they produce; Sada wraps nothing and adds no bidi control characters.

## How paths are resolved

Config file, in order:

1. **--config <path>** after **--mcp** (used by tests and non-standard installs);
2. **SADA_CONFIG_PATH** environment variable;
3. **%APPDATA%/app.sada.desktop/app_config.json**;
4. **%LOCALAPPDATA%/app.sada.desktop/app_config.json**;
5. the legacy upstream folders (**github.com.thewh1teagle.vibe**, **com.vibe.desktop**) for a
   profile that once ran Vibe.

Model: the **model** argument, else **model.path** in the config.

Engine: **SADA_ENGINE** environment variable, else **vibe-server.exe** next to the app executable
(that is where the installer puts it); development builds also find the repository's
**desktop/src-tauri/binaries/** engine, and a PATH lookup is the last resort.

FFmpeg: **VIBE_SERVER_FFMPEG_PATH**, else next to the engine/app; it is only needed for formats
the engine cannot decode on its own or for **enhance_audio**.

Transcripts folder: **transcription.projectsPath** in the config, else **SADA_TRANSCRIPTS_DIR**,
else **Documents/Sada** (OneDrive-redirected Documents is honoured). The same folder the app's
Projects page shows.

## Protocol

- Revisions: **2025-06-18**, **2025-03-26**, **2024-11-05** (negotiated from the client request;
  an unknown one falls back to the oldest).
- Methods: **initialize**, **notifications/initialized**, **ping**, **tools/list**, **tools/call**;
  **resources/list** and **prompts/list** answer with empty lists for clients that probe them.
- Capabilities: tools only, no list-changed notifications.
- Requests are handled one at a time. A transcription can take minutes; a client that pipelines
  several calls would otherwise race two engine processes over the same model file.
- stdout carries protocol frames only. Engine output is captured; diagnostics go to stderr.
- Exit code 0 when stdin closes; the process does not install anything, open windows or write logs
  outside Sada's usual folders.

## Security and privacy

- **No port, no network.** The transport is stdin/stdout of a process the MCP client starts.
- **Local files only.** Media paths are resolved on disk; http(s)/www links are rejected with an
  explanation rather than downloaded.
- **No secrets in results.** Only transcription settings (model path, language, transcript folder)
  are read from the config; summary-provider keys and other values are never copied into a tool
  result.
- **No elevation, no installs.** The MCP process uses the same per-user folders as the app.
- **Trust:** an agent with this server can read any local file the user's account can read and
  writes only through the app's normal paths. Register it only in clients the user trusts.

## Troubleshooting

| Symptom | What to do |
| --- | --- |
| "No model is configured for Sada" or "The configured model does not exist" | Open Sada → Settings → Models, download or select a ggml model (large-v3-turbo recommended), then retry. Or pass an absolute **model** path. |
| "engine (vibe-server.exe) was not found" | Reinstall Sada, or set **SADA_ENGINE** to the engine binary. Bundled installs keep it next to Sada.exe. |
| Empty result or "returned no text" | The clip may be silent or undecodable. Check it plays; try **enhance_audio: true**; confirm the bundled FFmpeg resolved in **sada_info**. |
| Wrong language | Pass **language: "ar"** (or the right code) explicitly; **auto** can misdetect short clips. Check **transcription.modelOptions.lang** in the config. |
| Tool returns **isError: true** | The error text explains the fix; **sada_info** shows which expected path is missing. |
| Client cannot start the server | Use the full path to **Sada.exe** in the client config; quote it if it contains spaces; restart the client after editing config. |

## Verifying a build

Built-in tests (from **desktop/src-tauri**):

~~~text
cargo test --release
# filters, one at a time (cargo accepts a single TESTNAME):
cargo test --release mcp::
cargo test --release arabic::
~~~

That covers the protocol frames, the four tool definitions, transcript scanning and rendering, the
Arabic normaliser, and config resolution. An end-to-end check with a real model is one manual
round trip: download ggml-tiny.bin, set **model.path** in a scratch config, call
**sada_transcribe** through **--config** and confirm Arabic output on a known clip.

## Licence

The MCP server is part of Sada, MIT-licensed, built on the upstream Vibe fork (MIT). See
[docs/releases/v3.3.0.md](releases/v3.3.0.md) for the release notes and
[docs/VOICEBOX-REVIEW.md](VOICEBOX-REVIEW.md) for why MCP was chosen over adding a speech engine.
