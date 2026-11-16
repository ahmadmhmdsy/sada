# Security policy

## Reporting a vulnerability

Please report security issues privately through GitHub's
[Security Advisories](https://github.com/alshahia/sada/security/advisories/new) ("Report a
vulnerability"). Do **not** open a public issue for a security report.

Include: affected version, Windows version, steps to reproduce, impact, and any relevant logs
(remove personal audio paths and transcripts first). You will get an acknowledgement as soon as
possible and credit in the advisory once a fix ships, unless you prefer to stay anonymous.

## Supported versions

Security fixes target the latest released `3.2.x` build. Older builds are not maintained.

## Scope

Sada runs entirely locally: audio, transcripts and settings stay on the machine, and there is no
telemetry, account or updater. In-scope issues include the Tauri shell, IPC between the app and the
bundled `vibe-server` sidecar, local file handling, and the Windows installer.

Reports about the upstream Vibe project or its engine code should also be raised upstream
(thewh1teagle/vibe) where appropriate; this fork will pick up upstream fixes when it rebases.

## Third-party dependencies

If the issue is in a third-party dependency (Tauri, React, whisper.cpp/ggml, FFmpeg, Rust/Node
crates), please report it to that project's maintainers as well.
