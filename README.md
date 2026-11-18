<div align="center">

# صدى · Sada

**Arabic-first speech-to-text for Windows — fully offline.**

[![CI](https://github.com/alshahia/sada/actions/workflows/ci.yml/badge.svg)](https://github.com/alshahia/sada/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/alshahia/sada?label=release&color=2ea043)](https://github.com/alshahia/sada/releases/latest)
[![License: MIT](https://img.shields.io/github/license/alshahia/sada?color=blue)](LICENSE)
![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11%20x64-0078D4)
![Arabic-first](https://img.shields.io/badge/Arabic--first-ar--IQ-1f6feb)

[العربية (Arabic)](README.ar.md) · [Download](https://github.com/alshahia/sada/releases/latest) · [Website](https://alshahia.github.io/sada/) · [Docs](docs/)

</div>

![Sada main window, Arabic RTL](docs/media/sada-main.png)

Sada (صدى, "echo") turns audio and video into text **on your own computer**, and it is
**Arabic-first**: the app opens in Arabic, right-to-left, with Arabic transcription defaults,
Arabic typography (IBM Plex Sans Arabic) and Arabic-aware transcript cleanup. English and the
other upstream languages are still one click away in Settings.

It is an independent fork of [Vibe](https://github.com/thewh1teagle/vibe) (MIT), built on upstream
tag **v3.2.2**, with the telemetry, auto-updater and phone relay removed and a complete Arabic
localization added. Nothing is uploaded: the Whisper engine runs locally through the bundled
`vibe-server` sidecar, and the installer bundles its own FFmpeg for audio decoding.

Since 3.3.0 Sada is also **agent-ready**: `Sada.exe --mcp` runs a local MCP server over stdio,
so Claude Code, Codex and other agents can transcribe Arabic audio and read saved transcripts
directly — no server port, no account, no network. See [docs/AGENT-MCP.md](docs/AGENT-MCP.md).

- **Keywords:** offline speech-to-text, Arabic ASR, whisper.cpp, Whisper large-v3-turbo, RTL UI,
  MSA and Iraqi Arabic, Windows transcription app, private voice-to-text, SRT/VTT/PDF/DOCX export,
  MCP server for AI agents, local agent tools.

## Why Sada

Most transcription apps treat Arabic as a translation target, not a first language. Sada inverts
that:

- **Arabic-first defaults** — display language `ar-IQ`, transcription language `ar`, translation
  off, temperature 0, beam size 5, 6 threads, empty initial prompt.
- **Right-to-left interface** — the shell, settings, dialogs, PDF export and errors are Arabic and
  RTL; Latin acronyms and file paths stay isolated and readable.
- **Arabic-aware text cleanup** — normalizes ASCII punctuation to Arabic (`,` → `،`, `?` → `؟`,
  `;` → `؛`), collapses stray spaces, and restores common Latin acronyms (GPU, CPU, PDF, SRT, VTT,
  JSON, API, FFmpeg, Whisper) inside Arabic transcripts.
- **Arabic PDF** — transcripts export to PDF with an embedded Arabic font and proper shaping.
- **Truly offline and private** — no account, no analytics, no crash reporting, no auto-update, no
  phone relay. The only network calls happen when *you* ask for them (model download, a URL you
  paste, or a summary provider you configure with your own key).
- **Agent-ready (MCP)** — `Sada.exe --mcp` gives agents Arabic ears over stdio: transcribe a
  file, list or read saved transcripts, inspect the install. No port, no toggle, no window.

## Features

| | |
| --- | --- |
| **Transcribe files** | Drop audio or video files; batch transcription with per-file progress and cancellation. |
| **Live preview** | Watch the transcript fill in as the file is processed. |
| **Whisper models** | Any `ggml-*.bin` Whisper model; download from Settings or point at a local file. Recommended for Arabic: `large-v3-turbo`. |
| **Export** | SRT, VTT, TXT, HTML, PDF (Arabic font embedded), DOCX, JSON. |
| **Dictation** | Global shortcut: hold to record, release to transcribe into the active app. |
| **Recording** | Microphone and system-audio capture. |
| **Projects** | Saved transcripts with search, reopen and re-export. |
| **Optional summaries** | Claude or local Ollama, with your own key — off by default. |
| **Agents (MCP)** | `Sada.exe --mcp` — four stdio tools for Claude Code, Codex and other MCP clients; Arabic defaults, local only. |
| **Languages** | Arabic (`ar-IQ`) plus 20+ inherited locales. |

## Install

1. Download **`Sada_3.8.0_x64-setup.exe`** (about 45 MB) from the [latest release](https://github.com/alshahia/sada/releases/latest)
   and verify its SHA-256 against the attached `SHA256SUMS.txt`.
2. Run the installer. It installs per-user into `%LOCALAPPDATA%\Sada\`; no administrator rights
   are required.
3. Launch **صدى / Sada** from the Start Menu.

**Fully offline machine?** Windows 10 machines that have never run a modern app do not have the
WebView2 Runtime, and the default installer asks Windows to download it. If the target machine
cannot go online, download **`Sada_3.8.0_x64-setup-offline.exe`** instead (about 250 MB): it
embeds the WebView2 installer, so one file covers the app and the runtime. Both files are the same
app and both hashes are listed in `SHA256SUMS.txt`. One caveat: neither file embeds the VC++
2015-2022 runtime — Sada's installer fetches it from Microsoft when missing or outdated, so a fully
offline machine should have `vc_redist.x64.exe` pre-installed (installing WebView2 first also pulls
its dependencies).

> **SmartScreen:** the installer is not code-signed (owner decision while the project is
> open-source-only), so Windows may show "Windows protected your PC". Choose *More info → Run
> anyway* only for the official release after verifying the checksum. Signing is staged and will be
> switched on when the project applies for it — see [docs/SIGNING.md](docs/SIGNING.md).

Requirements: 64-bit Windows 10 or 11, the WebView2 Runtime (bundled with current Windows; the
offline installer includes it), the VC++ 2015-2022 runtime (installed automatically when online),
and disk space for a Whisper model.

## First run and models

On first launch Sada opens with an Arabic setup screen. Open **Settings → Models → Get models**. The catalogue ships inside the app, so it works on a
fresh offline install, and every download is checked against the SHA-256 in the catalogue:

- **Whisper Large v3 Turbo** (~1.6 GB, MIT) — the default: best Arabic quality/speed balance, with
  word timestamps;
- **Whisper Tiny** (78 MB, MIT) — for slow machines, lower accuracy;
- **Whisper Large v3 Turbo Hebrew** (Apache-2.0) — for Hebrew audio;
- or **Add a model… / choose a file** if you already have a `ggml-*.bin` on disk.

Models are **not bundled** with the installer; they are distributed by their own publishers under
their own terms and downloaded once by you. The model is loaded locally and never leaves your
machine. Sizes, licences, hashes, GPU notes and how to verify a download: **[docs/MODELS.md](docs/MODELS.md)**.
The measured Arabic comparison behind the catalogue — including why Turbo stays the default and
Nemotron is only optional — is in **[docs/MODELS-DECISIONS.md](docs/MODELS-DECISIONS.md)**.

## GPU acceleration (optional)

Sada ships the Vulkan build of its whisper.cpp engine, so a Vulkan-capable GPU can speed up
transcription without CUDA, ROCm or any extra download. GPU is an **optional accelerator, never a
requirement**: every model still runs on the CPU.

- **Device picker:** **Settings → Models → Hardware**. **Auto** (the default) lets the engine pick
  its default Vulkan device; choose a specific one if you have more than one GPU. **Transcribe on
  CPU** forces the CPU path.
- **What you need:** a GPU driver that provides Vulkan 1.1+ (current NVIDIA/AMD/Intel drivers do;
  on a machine without the Vulkan loader, install the
  [Vulkan Runtime](https://sdk.lunarg.com/sdk/download/1.3.290.0/windows/VulkanRT-1.3.290.0-Installer.exe)).
  When Vulkan is unavailable the engine quietly uses the CPU — the app does not refuse to run.
- **Out of memory:** if a model fails to load on the GPU, Sada retries it on the CPU, tells you it
  did, and remembers that model so later runs start on the CPU instead of failing again.
- **Speed:** on the reference machine (NVIDIA Quadro RTX 4000 with Vulkan), 38 s of Arabic audio
  transcribed in ~4.9 s including model load (~12.5× realtime). CPU-only is a compatibility path,
  not a speed path.
- **Diagnostics:** the engine lists the devices it sees with
  `vibe-server-x86_64-pc-windows-msvc.exe devices`; see [docs/DEBUG.md](docs/DEBUG.md) for
  `vulkan-1.dll` errors and [docs/BUILDING.md](docs/BUILDING.md) for build details.

## Privacy

- No analytics, telemetry, crash reporting or account.
- Audio, video and transcripts never leave the computer.
- The bundled FFmpeg is used only as a local subprocess for decoding.
- Settings and projects live under `%APPDATA%\app.sada.desktop\`; the model and WebView profile
  live under `%LOCALAPPDATA%\app.sada.desktop\`.

See [PRIVACY.md](PRIVACY.md). The upstream updater and Aptabase client are removed from the
source, not switched off at runtime.

## Verified build

This release was built from the source in this repository and checked end-to-end:

- 26 test files / 134 unit tests passing (`pnpm test`, exit 0), including Arabic text
  normalization, Arabic PDF export, boot-locale and RTL tests.
- Engine v0.6.16 smoke test: the four Arabic clips produced exactly the same text as on v0.6.10,
  SRT/VTT timings were correct, Nemotron-3 diarization labelled 12/12 segments, and the CPU-only
  path still transcribed.
- Rust: 83 tests passing (`cargo test --release`), including 19 MCP protocol/tools tests and 9
  Arabic normaliser tests.
- MCP verified end-to-end: `Sada.exe --mcp` answered initialize, tools/list, sada_info,
  sada_transcripts, sada_transcript and sada_transcribe over pipes with a real model and Arabic
  audio.
- Fresh-profile launch verified Arabic/RTL (`lang=ar-IQ`, `dir=rtl`) by inspecting the running
  WebView, not just the source.
- Arabic transcription verified with the app's own engine on Modern Standard Arabic and Iraqi
  Arabic clips; CLI transcription exits 0.
- Idle network check on the installed app: only loopback sockets, no external endpoint.
- Known limitations are listed in [docs/VERIFICATION.md](docs/VERIFICATION.md).

## Build from source

Prerequisites: [Rust](https://rustup.rs), Node.js 22+, pnpm 10.4.1 (corepack), [chore](https://getchore.github.io/chore/).

```powershell
git clone https://github.com/alshahia/sada.git
cd sada
chore setup x86_64-pc-windows-msvc   # downloads the pinned vibe-server + ffmpeg sidecars
cd desktop
pnpm install
pnpm test
pnpm exec tauri build                # writes the NSIS installer under target/release/bundle/nsis/
```

Sidecar binaries are not committed to git (they are ~175MB combined); `chore setup` fetches the
pinned release from the upstream server tag in [.server-version](.server-version). See
[docs/BUILDING.md](docs/BUILDING.md) for details and non-Windows instructions.

## Repository layout

```text
desktop/          React 19 + Tauri 2 desktop app (frontend, Rust shell, icons, fonts)
i18n/desktop/     Translation catalogues, including ar-IQ.json (704 keys)
server/           vibe-server: Rust sidecar around whisper.cpp (upstream engine)
docs/             Architecture, building, verification, licences, release notes, MCP guide, Voicebox review
site/             Bilingual static landing page (GitHub Pages, with llms.txt for agents)
.github/workflows CI (build + tests), Release (tag → Windows installer + GitHub release), Deploy site
```

## FAQ

<details>
<summary><strong>Is Sada free?</strong></summary>
Yes. MIT-licensed source; the Windows installer is free. No account, no subscription.
</details>

<details>
<summary><strong>Does it work without internet?</strong></summary>
Yes, after the one-time model download. Transcription is fully local; network is used only for
what you explicitly request.
</details>

<details>
<summary><strong>Can AI agents use Sada?</strong></summary>
Yes. `Sada.exe --mcp` is a local MCP server over stdio with four tools: transcribe a file, list
saved transcripts, read one transcript and report install info. Register it in Claude Code with
`claude mcp add sada -- ".../Sada.exe" --mcp`, or in any MCP client JSON config. It is local
only: no port, no account, no network. See [docs/AGENT-MCP.md](docs/AGENT-MCP.md).
</details>

<details>
<summary><strong>Does it support Iraqi Arabic?</strong></summary>
Whisper handles Iraqi Arabic as part of Arabic. Arabic-first cleanup normalizes punctuation;
dialect accuracy depends on the model and audio quality. `large-v3-turbo` is the recommended
starting point.
</details>

<details>
<summary><strong>How is it different from Vibe?</strong></summary>
Sada is a fork: full Arabic localization and RTL, Arabic defaults and transcript cleanup, Arabic
PDF export, a new name/icon, and removal of telemetry, auto-update and the phone relay. The
transcription engine is upstream code. See [docs/UPSTREAM-PATCHES.md](docs/UPSTREAM-PATCHES.md).
</details>

<details>
<summary><strong>Why does Windows warn about the installer?</strong></summary>
The installer is not code-signed (code-signing certificates cost money). Verify the SHA-256
checksum and build from source if you prefer.
</details>

<details>
<summary><strong>Where are my files?</strong></summary>
Settings, logs and projects: `%APPDATA%\app.sada.desktop\`. Model and WebView data:
`%LOCALAPPDATA%\app.sada.desktop\`. Nothing is copied elsewhere.
</details>

## Contributing

Issues and pull requests are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). For security
reports use GitHub Security Advisories, see [SECURITY.md](SECURITY.md).

## Licence and attribution

MIT — see [LICENSE](LICENSE). The original Vibe copyright notice is preserved. Sada is an
independent fork, **not affiliated with or endorsed by** the Vibe author; "Vibe" remains that
author's property, while the Sada name and artwork are this fork's own.

The installer bundles an **FFmpeg 9.0.1 GPLv3** build; read [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md)
before redistributing a build. IBM Plex Sans Arabic is SIL OFL 1.1. Full notices and licence
texts: [NOTICE](NOTICE), [docs/licenses/](docs/licenses/).

---

<sub>صدى — تفريغ صوتي عربي على جهازك، بلا إنترنت. Arabic-first offline transcription for Windows.</sub>
