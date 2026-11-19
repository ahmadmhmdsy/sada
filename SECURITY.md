# Security policy

## Reporting a vulnerability

Please report security issues privately through GitHub's
[Security Advisories](https://github.com/alshahia/sada/security/advisories/new) ("Report a
vulnerability"). Do **not** open a public issue for a security report.

Include: affected version, Windows version, steps to reproduce, impact, and any relevant logs
(remove personal audio paths and transcripts first). Do not include API keys, transcripts or audio
you are not able to share.

## Response targets

Best-effort targets for a single-maintainer project, not a contractual SLA:

| Stage | Target |
| --- | --- |
| Acknowledge a private report | 3 business days |
| Triage + severity assessment | 10 business days |
| Fix or documented mitigation for high severity (RCE, data disclosure, key theft, installer tampering) | 30 days from confirmation |
| Fix for medium/low severity | next release where practical |
| Public advisory + credit | after the fix ships, coordinated with the reporter |

If a report is about a third-party dependency (Tauri, WebView2, whisper.cpp/ggml, FFmpeg, Rust/Node
crates), the project will coordinate with upstream; the fix may land in an upstream release first.

## Supported versions

Security fixes target the latest released `3.9.x` build. Older builds are not maintained.
(3.7.0 and 3.8.0 were measurement/distribution releases with no runtime change; 3.9.0 adds the
managed policy, DPAPI key storage, transcript retention and supply-chain evidence described below.
The 3.6.0 defence-in-depth work is unchanged and still applies.)

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

## Trust and enterprise controls added in 3.9.0

These are hardening features, not a claim that the app is certified. Details and the exact
semantics are in [NETWORK.md](docs/NETWORK.md), [DATA-HANDLING.md](docs/DATA-HANDLING.md),
[SECURITY-WHITEPAPER.md](docs/SECURITY-WHITEPAPER.md) and
[ENTERPRISE-DEPLOYMENT.md](docs/ENTERPRISE-DEPLOYMENT.md).

- **Managed policy**: an administrator can enforce offline mode and disable AI, URL import and
  model downloads machine-wide (HKLM `SOFTWARE\Sada\Policy`, with a ProgramData JSON fallback).
  The Rust command layer re-checks the policy on every guarded action, so UI hiding is never the
  only enforcement; the connectivity probe returns "offline" without opening a socket when
  offline mode is set. A local administrator can change the policy — that boundary is documented.
- **DPAPI key storage**: Claude/OpenAI API keys are sealed with `CryptProtectData` (current-user
  scope) and stored as `claudeApiKeyEnc`/`openaiApiKeyEnc`; legacy plaintext keys migrate once at
  boot and are never written back in plaintext. Blobs do not decrypt on another account or machine.
- **Retention**: an optional per-user transcript retention window (0 = forever, default) with a
  purge that only deletes project folders/legacy transcript files under the transcripts folder,
  never following symlinks; a manual "delete old transcripts now" action reports counts and bytes.
- **Egress inventory**: every outbound path is documented in [NETWORK.md](docs/NETWORK.md), and the
  phone-handoff endpoint is disabled unconditionally (the start command always refuses) rather than
  left to a setting.
- **Supply chain**: keyless GitHub build provenance attestations, a CycloneDX SBOM and
  `scripts/verify-release.ps1` are published with each release; SHA-256 sums remain the offline
  verification path. Releases are still unsigned (see below).

## Defences in depth added in 3.6.0

Upstream v3.3.6 shipped a security audit; the parts that fit this fork were ported and are listed
in [UPSTREAM-PATCHES.md](docs/UPSTREAM-PATCHES.md). The behaviour they enforce:

- **Webview content**: the window has a Content-Security-Policy (`default-src 'self'`, no
  `object-src`, no remote script/connect origin except the Tauri asset protocol). Markdown is
  rendered through a wrapper that drops images and opens http(s) links in the system browser
  instead of navigating the app window; other schemes are inert.
- **Deep links**: the `sada:` handler only accepts `https` model URLs on `huggingface.co` or
  `github.com` (plus their subdomains), shows the whole URL and asks for confirmation, and takes
  the expected size and SHA-256 from the bundled catalogue. A `sada:` link cannot point the app
  at an arbitrary host, path or plain-http URL.
- **Model downloads**: the destination must be a `.bin`/`.gguf` file directly inside the
  models folder (parents canonicalised, `..` rejected, symlinked destinations and `.part`
  files rejected). The download client follows only https redirects, at most ten, and writes the
  file only after the checksum and size in the catalogue match.
- **yt-dlp update**: the release version is validated against the date tag format, the download
  URL is built by the app from the validated version (never from the webview), and the release
  `SHA2-256SUMS` file is required.
- **Engine process**: the sidecar starts in its own canonical directory with
  `GGML_BACKEND_PATH` removed and `TEMP`/`TMP` pointing at the app temp folder, so a hostile
  profile or a stray backend library cannot redirect the engine load path.
- **Dictation**: `type_text` accepts input only within 30 minutes of a finished recording, and
  the text is capped (50,000 characters) and stripped of control characters before typing. Other
  local processes cannot use the app as an arbitrary keystroke injector.
- **No update channel**: the app still has no updater and never downloads and executes new code;
  yt-dlp is only updated by explicit user action and is verified against the published checksums.

## Release artifacts and code signing

Every release publishes the installers together with `SHA256SUMS.txt`, a CycloneDX SBOM and
GitHub build provenance attestations; `docs/VERIFICATION.md` records the size and SHA-256 of each
asset. From 3.9.0 the release also contains a per-machine MSI for managed deployment. The Windows
binaries are **unsigned** up to 3.9.0, so SmartScreen shows an "unknown publisher" warning. Verify
the hash (and, when available, `gh attestation verify`) before running an installer. The signing
options, costs and the recommended (free, OSS) path are recorded in [SIGNING.md](docs/SIGNING.md);
nothing is signed until the owner funds or is accepted for one of those programmes.

## Third-party dependencies

If the issue is in a third-party dependency (Tauri, React, whisper.cpp/ggml, FFmpeg, Rust/Node
crates), please report it to that project's maintainers as well.
