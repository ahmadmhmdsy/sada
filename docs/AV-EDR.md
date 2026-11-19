# Antivirus, EDR and SmartScreen guidance — Sada 3.9.0

Sada is an unsigned, self-contained Windows desktop app that bundles an FFmpeg executable and a
local AI inference sidecar. That combination triggers heuristics on some AV/EDR products, and being
unsigned means SmartScreen shows a warning. This document tells administrators what to whitelist,
what behaviour is normal, and how to report a false positive.

Last updated: 2026-11-19.

## Why it may be flagged

- **Unsigned binaries.** The installer and `Sada.exe` have no Authenticode signature (code
  signing is deferred; see `SIGNING.md`). SmartScreen shows "Windows protected your PC" until
  the user chooses **More info → Run anyway**, or an administrator allow-lists the hash.
- **Bundled FFmpeg.** FFmpeg is a commonly abused tool; some products flag any copy. Sada's copy is
  the official gyan.dev build, version-pinned, shipped as a separate executable, GPLv3.
- **Local inference engine.** `vibe-server.exe` opens local sockets/loopback and runs CPU/GPU
  inference; behaviour-based engines may see that as unusual for an installer payload.
- **yt-dlp.** Fetched at runtime for URL import only; it is a Python-based downloader that some
  products classify as a PUA unless allow-listed.

## Normal runtime behaviour (allow-list rationale)

| Process | Behaviour | Notes |
|---------|-----------|-------|
| `Sada.exe` | Tauri shell; WebView2; local file IO | No service, no drivers, no auto-start unless the user enabled a global shortcut |
| `vibe-server.exe` | Child process; reads model + media; loopback only; exits with the app | Bundled sidecar, version `0.6.16-sada.1` |
| `ffmpeg.exe` | Child process; decodes local media to WAV | Only on transcribe/import; exits when done |
| `yt-dlp.exe` | Child process; only when the user imports a URL; downloads media | Absent until first URL import unless provisioned |
| Installer | Per-user NSIS to `%LOCALAPPDATA%\Sada` (or per-machine MSI) | No kernel components, no services |
| Network | Only user/administrator-triggered HTTPS paths | Complete list: `NETWORK.md` |

There are no Windows services, no drivers, no scheduled tasks, no browser extensions and no
auto-start entries created by the installer. A global hotkey can be registered by the app while it
runs if the user enables it.

## Recommended allow-listing

1. Allow-list by hash for the current release (preferred): hashes are in `SHA256SUMS.txt` and
   in `docs/VERIFICATION.md`; verify with
   `Get-FileHash <file> -Algorithm SHA256`.
2. If a management product supports publisher rules, an unsigned app cannot use them; use path +
   hash rules for:
   - `%LOCALAPPDATA%\Sada\Sada.exe` (per-user) or the MSI install path (per-machine)
   - `%LOCALAPPDATA%\Sada\vibe-server.exe`, `ffmpeg.exe`, `yt-dlp.exe`
   - the models folder if the AV scans large model files (optional; they are inert data)
3. Allow the app's outbound HTTPS destinations from `NETWORK.md` if a firewall prompts, or
   block them all and set the managed `OfflineMode` policy — local transcription still works.
4. Do not exclude the transcripts folder from backup/scanning unless policy requires it; transcripts
   are user data and should be protected like documents.

## What Sada does not do (and an EDR should not see)

- No process injection into other apps, no credential dumping, no persistence outside the install
  and the optional global hotkey, no hidden network beacon, no updater, no remote shell.
- The MCP server runs only when an agent starts `Sada.exe --mcp`; it speaks stdio, not a
  port.
- The local agent API server binds `127.0.0.1` with a per-run token and is documented in
  `AGENT-MCP.md`.

## False positives

If a scanner removes or quarantines a file:

1. Confirm the hash matches `SHA256SUMS.txt` (and, when present,
   `gh attestation verify <asset> --repo alshahia/sada`).
2. Submit the file to the vendor as a false positive with the hash and this document as context.
3. Open an issue at https://github.com/alshahia/sada/issues with the product, version, detection
   name and hash so the project can track it.
4. Until resolved, install from a verified hash with an allow-list rule, or use the portable layout
   (offline installer without runtime downloads).

## SmartScreen specifically

Because there is no reputation and no signature, the warning appears for the first users of each
build. Options for administrators:

- Deploy via Intune/SCCM, which often bypasses browser-based SmartScreen reputation prompts.
- Allow the installer hash in Windows Defender Application Control (WDAC) or AppLocker policies.
- Accept the warning once per build and document it; never disable SmartScreen machine-wide.

Code signing would remove the warning for end users. The signing route is prepared but deliberately
dormant (`SIGNING.md` appendix); until then, hash + provenance verification is the
compensating control.
