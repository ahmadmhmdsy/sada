# Privacy

Sada runs entirely on this computer.

- No analytics, no telemetry, no crash reporting and no account. The upstream Aptabase client
  and the updater are removed from the code, not merely switched off at runtime.
- Audio, video and transcripts never leave the machine. The model runs locally through the
  bundled `vibe-server` sidecar.
- The application only uses the network when you ask it to: downloading a Whisper model,
  fetching audio from a link you paste, or calling a summary provider (Claude / Ollama) that
  you configure yourself with your own key.
- Recordings, projects and settings stay under your Windows user profile:
  `%APPDATA%\app.sada.desktop\` and the projects folder you choose.
- The Android/iOS phone handoff server is hidden in this build (v1). It is not started and no
  relay is used.

If you build Sada from source with the analytics/updater code re-enabled, those are your
changes, not this project's.
