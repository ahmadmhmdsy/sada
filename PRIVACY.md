# Privacy

Sada runs entirely on this computer.

- No analytics, no telemetry, no crash reporting and no account. The upstream telemetry client is
  compiled out (no ingest key, all calls are no-ops) and the updater is not included in the build.
- Audio, video and transcripts never leave the machine during transcription. The model runs locally
  through the bundled `vibe-server` sidecar.
- Outbound traffic happens only for actions you start: downloading a Whisper model, importing media
  from a link you paste (yt-dlp), or calling a summary/dictation provider (Claude, OpenAI or a local
  Ollama) that you configure with your own key. A connectivity probe during setup only opens TCP
  sockets to public DNS addresses and sends no data. The complete list is in
  [docs/NETWORK.md](docs/NETWORK.md).
- An administrator can enforce an offline machine policy that turns every one of those paths off
  (including the probe) and pins the transcripts folder; Sada then makes no outbound connections at
  all. See [docs/ENTERPRISE-DEPLOYMENT.md](docs/ENTERPRISE-DEPLOYMENT.md).
- Recordings, projects and settings stay under your Windows user profile:
  `%APPDATA%\app.sada.desktop\` and the projects folder you choose. Transcripts can be kept for a
  retention window you set (7/30/90/365 days or forever); purging deletes only transcript files
  under that folder. See [docs/DATA-HANDLING.md](docs/DATA-HANDLING.md).
- Claude/OpenAI API keys are encrypted with Windows DPAPI for your user before being written to the
  config file; they are never stored in plaintext after the first migration. They cannot be
  decrypted on another Windows account or machine.
- The upstream phone-handoff server is not exposed in this build: no settings page starts it and
  the backend refuses to start it. No relay is used.
- Logs are local diagnostic logs only; release builds do not write transcript text or API keys to
  them.

If you build Sada from source with the telemetry/updater code re-enabled, those are your changes,
not this project's.
