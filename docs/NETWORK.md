# Network egress inventory

This document lists every outbound network path in Sada 3.9.0, what triggers it, what leaves the
machine, and which managed-policy switch removes it. It is the reference for firewall rules,
procurement questionnaires and the assurance pack
([SECURITY-WHITEPAPER.md](SECURITY-WHITEPAPER.md)).

Sada is offline by design. There is no telemetry, no crash reporting, no account system, no
auto-updater and no remote relay. The paths below exist only because a **user (or an
administrator) explicitly asks for a download, a URL import or an AI provider call**.

## Inventory

| # | Feature | Destination | Trigger | Data sent | Managed switch |
|---|---------|-------------|---------|-----------|----------------|
| 1 | Model download | `huggingface.co`, `github.com` (catalog URLs); any `https` URL from the model-URL field or a `sada://download?url=` deep link | User clicks **Download** in the model catalog, setup, model prompt, VAD/diarization auto-install, or follows a download deep link | HTTPS GET for the model file; host + path + standard TLS/HTTP request headers. No account, cookie, transcript or device ID | `offlineMode` or `disableModelDownloads` |
| 2 | yt-dlp binary download + version check | `api.github.com` (latest release), `github.com/yt-dlp/yt-dlp/releases` (asset + `SHA2-256SUMS`) | First URL import, manual "update yt-dlp", or a weekly version check | HTTPS GET of the release metadata / binary; standard request headers | `offlineMode` or `disableUrlImport` |
| 3 | URL import (media download) | The site in the pasted URL and the CDN hosts yt-dlp follows for it (e.g. `youtube.com`, `googlevideo.com`) | User pastes a media link and starts a transcription | The URL itself plus yt-dlp's standard HTTP requests to fetch the media | `offlineMode` or `disableUrlImport` |
| 4 | AI summary / dictation cleanup — Claude | `api.anthropic.com` | A task the user enabled runs (summary on finish, resummarize, or dictation cleanup) | Prompt text — which contains the transcript or dictated text — plus the user's API key in a request header, model name, token limits | `offlineMode` or `disableAi` |
| 5 | AI summary / dictation cleanup — OpenAI | `api.openai.com` or a user-configured OpenAI-compatible base URL | Same as #4 with the OpenAI platform selected | Same as #4 | `offlineMode` or `disableAi` |
| 6 | AI summary / dictation cleanup — Ollama | `http://localhost:11434` (loopback) or a user-configured base URL | Same as #4 with Ollama selected | Prompt text to the local server; **no egress** when the default loopback URL is used | `offlineMode` or `disableAi` |
| 7 | Connectivity probe | TCP connect to `1.1.1.1:80`, `1.1.1.1:53`, `8.8.8.8:53`, `8.8.8.8:80` | First-run setup and model installation check whether a download is possible | A TCP handshake only; no HTTP request, no payload, no identifier | `offlineMode` (probe returns "offline" without connecting) |
| 8 | Phone handoff (iroh) | iroh relay/discovery infrastructure | **Never in Sada.** The upstream feature is present in the tree but no settings page mounts it and `handoff_start` is refused by the backend | Nothing is sent; no endpoint is created | Always disabled; `offlineMode` also covers it |
| 9 | External links (About, docs, issues, release page) | `github.com` | User clicks a link; the URL is opened in the default browser, not fetched by the app | Only what the browser sends normally | Not applicable (user action, outside the app) |
| 10 | MCP server | None — stdio | `Sada.exe --mcp` is started by an agent | Local stdin/stdout only | No network path exists |

Everything else runs on the local machine: Whisper inference through the bundled `vibe-server`
sidecar, FFmpeg decoding, PDF/DOCX/SRT export, the MCP server, and the local API server used by
agents (`127.0.0.1` loopback only).

## Managed-policy enforcement

An administrator writes `HKLM\\SOFTWARE\\Sada\\Policy` values (DWORD `1` to disable):

| Value | Effect |
|-------|--------|
| `OfflineMode` | All of the below, and the connectivity probe no longer opens sockets. |
| `DisableAi` | AI settings pages hidden; no AI provider calls are possible from the UI. |
| `DisableUrlImport` | Media-link tab hidden; yt-dlp version check, binary download and media download commands refuse. |
| `DisableModelDownloads` | Model catalog/manual download UI hidden; `download_model` refuses with a clear error; installed models stay usable. |
| `TranscriptsDir` (SZ) | Pins the transcripts folder. |

A JSON file at `%ProgramData%\Sada\policy.json` (or the path in `SADA_POLICY_PATH`) is also read;
registry values win and restrictions are OR-ed together. See
[ENTERPRISE-DEPLOYMENT.md](ENTERPRISE-DEPLOYMENT.md) for GPO/Intune/SCCM examples.

The Rust command layer re-reads the policy on every guarded action, so hiding a control in the UI
is never the only protection. Enforcement is still **within the local-user trust boundary**: a user
who can edit the machine registry as administrator can change the policy; a user who cannot cannot
bypass it. Strong separation requires Windows user rights, which is an administrator responsibility.

## Verification

- Inspect the policy in effect: Settings → Privacy shows a "Managed by your organization" block
  when any restriction is active.
- Watch connections while the app is idle: `Get-NetTCPConnection -OwningProcess (Get-Process Sada).Id`
  in an elevated PowerShell should show no ESTABLISHED remote connections when no download or AI
  task is running. The probe in #7 is a short TCP connect during setup/model installation only.
- A firewall that blocks all outbound traffic still leaves the app fully usable for local
  transcription, export, MCP and dictation; only downloads, URL import and AI calls fail.

## What Sada does not do

- No analytics, telemetry, crash reporting or "phone home".
- No automatic update check at runtime (the updater is not compiled in; the release page link is
  opened in a browser only when clicked).
- No account, licence server, activation or remote configuration.
- No relay, cloud transcription or upload of audio/video/transcripts.
- No third-party SDKs with network behaviour in the release build.

Last verified: 2026-11-19 against the v3.9.0 source tree.
