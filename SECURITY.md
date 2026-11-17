# Security policy

## Reporting a vulnerability

Please report security issues privately through GitHub's
[Security Advisories](https://github.com/alshahia/sada/security/advisories/new) ("Report a
vulnerability"). Do **not** open a public issue for a security report.

Include: affected version, Windows version, steps to reproduce, impact, and any relevant logs
(remove personal audio paths and transcripts first). You will get an acknowledgement as soon as
possible and credit in the advisory once a fix ships, unless you prefer to stay anonymous.

## Supported versions

Security fixes target the latest released `3.3.x` build. Older builds are not maintained.

## Scope

Sada runs entirely locally: audio, transcripts and settings stay on the machine, and there is no
telemetry, account or updater. In-scope issues include the Tauri shell, IPC between the app and the
bundled `vibe-server` sidecar, local file handling, and the Windows installer.

Since 3.3.0 the app executable can also run as a local MCP server (`Sada.exe --mcp`). Its transport
is stdin/stdout only: it opens no port, starts no listener and makes no network requests. The
process is started by the user's MCP client under the same user account and reads only the config,
model and transcript paths needed for transcription; provider API keys and other settings are never
returned by a tool. A report that MCP opens a network endpoint, returns secrets or writes outside
the paths `sada_info` reports would be in scope.

Reports about the upstream Vibe project or its engine code should also be raised upstream
(thewh1teagle/vibe) where appropriate; this fork will pick up upstream fixes when it rebases.

## Local engine boundary

The app talks to its transcription engine (`vibe-server`, the `serve` subcommand) over loopback
HTTP on an ephemeral port. That port is reachable by anything on the machine, including a web
page: a DNS-rebinding page can resolve its own domain to `127.0.0.1` and POST to the port without
the user noticing. The fork ships an engine built from `server/` with a request guard (see
`server/crates/vibe-server/src/server/guard.rs`) and reports version `v0.6.16-sada.1`:

- The app starts the engine with an explicit `--host 127.0.0.1` and port `0` (an ephemeral port),
  so the listener is loopback-only.
- For loopback listeners the engine requires the `Host` header to be `127.0.0.1:<port>`,
  `localhost:<port>` or `[::1]:<port>`. A browser sends the header of the page URL, so a rebinding
  page is rejected before it reaches a route.
- Requests that carry an `Origin` header are only accepted from loopback origins (plus the Tauri
  webview origin). Native clients send no `Origin`; a cross-origin fetch/form POST from an
  internet page does, so writes from a page are rejected even if the page guesses the port.
- Binding the engine to another host with the CLI is an explicit opt-in to network serving; the
  guard does not apply there, and that mode is outside the app's supported configuration.

Residual risk: a process running as the same user can still call the engine, like any local
software. The guard closes the browser path, not the local trust boundary; a per-run bearer token
between the app and the engine is the next step if that boundary is ever considered too wide.
## Third-party dependencies

If the issue is in a third-party dependency (Tauri, React, whisper.cpp/ggml, FFmpeg, Rust/Node
crates), please report it to that project's maintainers as well.
