# Data handling and retention — Sada 3.9.0

This is the plain-language data inventory a privacy officer or DPO can check against the code. It
describes what Sada stores, where, for how long, who can reach it, and how it is deleted. It
complements `PRIVACY.md` (the user-facing statement), `NETWORK.md` (network egress)
and `SECURITY-WHITEPAPER.md` (controls).

Last updated: 2026-11-19, verified against the v3.9.0 source tree.

## Data inventory

| Category | What it is | Where it lives | Default retention |
|----------|------------|----------------|-------------------|
| Transcripts | Project folders containing `transcript.vibe.json`, plus media copies the user chose to keep | Chosen transcripts folder; default `%USERPROFILE%\Documents\Sada` | Until the user deletes them; optional retention window |
| Media | Audio/video files the user transcribed, if "save media" is on, or imported copies | Chosen projects folder | Until deleted; optionally copied from source |
| Exports | PDF/DOCX/SRT/VTT/TXT written by the user | User-chosen destination | User's responsibility |
| Settings | Display language, transcription defaults, model choice, AI provider config, retention days | `%APPDATA%\app.sada.desktop\app_config.json` | Kept until reset/uninstall |
| AI API keys | Claude/OpenAI keys | Same file, DPAPI-sealed as hex blobs (`claudeApiKeyEnc`/`openaiApiKeyEnc`) | Kept until replaced/cleared |
| Logs | Diagnostic app log, dated files | `%APPDATA%\app.sada.desktop\sada_*.log` | Rotated by size/age by the logging setup |
| Models | Verified GGML/GGUF model files | `%LOCALAPPDATA%\app.sada.desktop\models` or user-chosen folder | Kept until removed in Settings |
| Temporary files | Engine temp dirs, media conversion, yt-dlp downloads | `%TEMP%\vibe_temp_*` | Removed when the operation ends; crash leftovers are safe to delete |
| MCP / agent access | Not stored; reads existing transcripts on request | n/a | n/a |

No data category is transmitted anywhere unless a user (or administrator) runs a network feature;
`NETWORK.md` is the exhaustive list. Sada has no telemetry database, no cloud project
store, no account and no remote backup.

## Who can access the data

- The Windows user running Sada, through the app and normal file permissions.
- Any process running as that same user (by design of Windows; use AppLocker/EDR and full-disk
  encryption if that matters).
- Administrators of the machine.
- A chosen AI provider only for the text of a prompt the user explicitly runs; nothing else.

## Retention controls

1. **Per-run retention** — Settings → Privacy → "Keep transcripts for" offers forever (default),
   7, 30, 90 or 365 days (`0` means forever).
2. **Automatic purge** — at every launch, if a finite window is set, the app deletes project folders
   and legacy `*.vibe.json` transcripts older than the cutoff, and logs a count (never
   content).
3. **Manual purge** — "Delete old transcripts now" in the same settings page runs the same
   operation immediately and reports deleted count and freed bytes.
4. **Safety limits** — the purge only touches the configured transcripts folder: project folders
   that contain `transcript.vibe.json` and legacy transcript files. Foreign files, symlinks
   and junctions are skipped. Nothing outside the folder is deleted; the models and settings are
   never touched.
5. **Deletion on uninstall** — the uninstaller removes the app; user data under
   `%APPDATA%\app.sada.desktop`, the models folder and the transcripts folder are
   intentionally left so nothing is destroyed by accident. Administrators should deploy an
   uninstall script that clears them if needed (see `ENTERPRISE-DEPLOYMENT.md`).

## Encryption and backup

- **At rest:** API keys via DPAPI (current-user). Transcripts, media, logs and settings rely on
  Windows ACLs and the disk. Sada does not provide file-level encryption; BitLocker/device
  encryption is the expected control for sensitive data.
- **In transit:** only the user-triggered network paths, all HTTPS. See `NETWORK.md`.
- **Backup:** nothing is backed up by Sada. The transcripts folder is plain files, so normal
  enterprise backup tools can protect it; `app_config.json` contains DPAPI blobs that only
  decrypt for the same Windows user on the same machine, which is intentional.
- **Credential loss:** if the Windows profile is lost or reset, the sealed API key cannot be
  recovered; the user re-enters it. Transcripts are unaffected.

## Data subject / deletion requests

Because all data is local, the user (or the administrator holding the machine) can satisfy deletion
requests directly: delete the transcript folder contents, use the retention purge, or remove the
app config folder. There is no server-side copy to chase. Document the machine-level steps in the
organization's own runbook; Sada supports them but does not contact any remote processor.

## Logging hygiene

Release builds never write transcript text or API keys to the log. Media/transcript file paths can
appear in diagnostic error messages, and the engine command line (model path, media path) is
logged. Logs stay local. An organization that treats paths as sensitive should collect logs
deliberately and delete them on a schedule.

## What to include in a DPIA / vendor questionnaire

- Data leaves the device only when the user runs a network feature; list from `NETWORK.md`.
- AI prompts contain transcript text if AI tasks are enabled; disable or leave unconfigured for
  sensitive environments (`disableAi` policy).
- No sub-processor operated by the project; the user's own AI provider credentials apply.
- Encryption at rest: BitLocker required for sensitive data; API keys DPAPI-sealed.
- Retention: configurable purge, default forever (nothing deleted without the user asking).
- Audit: no server logs; Windows event logs/EDR see process and file activity.
