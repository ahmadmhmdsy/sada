# Security whitepaper — Sada 3.9.0

Audience: security reviewers, procurement teams, IT administrators and auditors evaluating Sada
for offline Arabic transcription. This document states what the software does and does not
protect, with pointers to the code and the reproducible evidence. It is written to be useful to a
reviewer, not to advertise.

Last updated: 2026-11-19. Applies to v3.9.0 (Windows desktop, Tauri 2 + Rust + React).

## 1. What Sada is

Sada (صدى, "echo") is an Arabic-first desktop transcription app for Windows. It is an independent
MIT-licensed fork of Vibe (built on upstream tag v3.2.2) with a complete Arabic localization,
Arabic ASR defaults, and a deliberately reduced feature surface: telemetry and the auto-updater
are removed, and the upstream phone-handoff endpoint is disabled.

The transcription engine (whisper.cpp / GGML models) runs as a bundled local sidecar
(`vibe-server`, v0.6.16-sada.1). Audio decoding uses a bundled FFmpeg. Export writes local
PDF/DOCX/SRT/VTT/TXT files. A local MCP server over stdio lets agents transcribe and read
transcripts with no port. There is no server component, account, licence check or cloud service.

## 2. Architecture and trust boundaries

```
+----------------------- Windows user session ------------------------+
|  WebView2 (React UI)  <--IPC-->  Rust shell (Tauri commands)        |
|                                  |  - managed policy (read-only)   |
|                                  |  - DPAPI for API keys           |
|                                  |  - transcript retention purge   |
|                                  +--> local sidecar process(es)      |
|                                       vibe-server, ffmpeg, yt-dlp    |
|  Files: app_config.json, logs, models, transcripts, exports         |
+-------------+-------------------------------------------------------+
              | explicit, user-triggered HTTPS only (see NETWORK.md)
              v  model downloads, URL import, AI provider calls
```

Trust boundaries:

1. **WebView2 ↔ Rust.** The UI is not trusted to enforce security. Every guarded action (model
   download, media import, AI call, handoff) is enforced in Rust. The IPC surface is the
   `tauri::generate_handler!` list in `desktop/src-tauri/src/main.rs`.
2. **Process ↔ network.** All egress goes through a small number of Rust commands or the WebView's
   plugin-http fetch for AI providers; `NETWORK.md` is the complete inventory.
3. **Local user ↔ administrator.** The managed policy is a machine-wide control (HKLM); a local
   user cannot bypass enforced commands, but an administrator can change the policy. This is the
   documented boundary (see `NETWORK.md` and `ENTERPRISE-DEPLOYMENT.md`).
4. **Machine ↔ model/provider.** Models are content-addressed and verified; AI providers are
   configured by the user with their own keys; no project-operated service is involved.

## 3. Data at rest

| Data | Location | Protection |
|------|----------|------------|
| Settings (including AI provider config) | `%APPDATA%\app.sada.desktop\app_config.json` | Windows user profile ACLs; API keys stored as DPAPI blobs (current-user scope), never plaintext after migration |
| Logs | same folder, dated `sada_*.log` | User profile ACLs; logs are diagnostic only (see §9) |
| Models | `%LOCALAPPDATA%\app.sada.desktop\models` (or a chosen folder) | User profile/ACL; verified against catalog sizes and SHA-256 where published |
| Transcripts + media copies | chosen transcripts folder (default `Documents\Sada`) | User profile/disk; optional retention window (Settings → Privacy); no app-level encryption |
| Exports | wherever the user saves them | User's own file handling; Sada never copies exports elsewhere |

Sada does **not** encrypt transcripts, media or exports at rest. Full-disk encryption (BitLocker)
is the expected control for sensitive deployments, and the app is compatible with it. This is
stated plainly rather than implied: `DATA-HANDLING.md` has the deletion and backup details.

## 4. Cryptography

- **API keys at rest:** Windows DPAPI `CryptProtectData`, current-user scope, no optional
  entropy, `CRYPTPROTECT_UI_FORBIDDEN`, called directly through `crypt32` exports
  (`desktop/src-tauri/src/secrets.rs`). Blobs are hex-encoded into
  `claudeApiKeyEnc`/`openaiApiKeyEnc`. A copied config cannot be decrypted on
  another account or machine; losing the profile means re-entering the key. Legacy plaintext keys
  are sealed once at boot.
- **Downloads:** HTTPS only (the model command rejects non-HTTPS URLs); the yt-dlp binary is
  checked against the release's own `SHA2-256SUMS`; models are checked against size and
  SHA-256 when the catalog provides them, plus GGML/GGUF magic bytes.
- **Release integrity:** SHA-256 sums published with every release, GitHub build provenance
  attestations (Sigstore, keyless) and a CycloneDX SBOM. No release signing yet — see §8.
- **No custom cryptography** is used anywhere; no random number generation for security purposes,
  no home-grown crypto, no embedded secrets (telemetry keys are compiled out).

## 5. Network behaviour

Offline by default. The complete egress list — destination, trigger, payload and the policy switch
that removes it — is `NETWORK.md`. In summary: model downloads, yt-dlp download/version
check, URL import media downloads, optional AI provider calls (Claude/OpenAI/Ollama), and a
connectivity probe used only during setup/model installation. No telemetry, no updater, no relay,
no remote config. `offlineMode` policy turns all of it off, including the probe.

## 6. Supply chain

- Lockfiles committed (`Cargo.lock`; pnpm lockfile) and CI builds from them.
- Release builds run on GitHub-hosted Windows runners from a tagged commit; the workflow is
  source-visible in `.github/workflows/release.yml`.
- CycloneDX SBOM (Rust + npm production dependencies + external components FFmpeg/WebView2) is
  attached to each release.
- GitHub Artifact Attestations bind each asset to the workflow, commit and repository; verify with
  `gh attestation verify <asset> --repo alshahia/sada` or `scripts/verify-release.ps1`.
- `SHA256SUMS.txt` remains the offline verification path.
- Third-party licences and attribution are in `NOTICE` and `THIRD-PARTY-NOTICES.md`;
  FFmpeg is GPLv3 and ships as a separate executable, never linked into Sada.

## 7. Logging and privacy

Logs are local, dated, in the app config folder. They record process start/stop, engine command
lines and errors. Release builds do not log transcript text or API keys; media and transcript
paths may appear in diagnostic errors. Logs are not shipped anywhere automatically; the user (or an
administrator) can read, delete or collect them. `docs/AGENT-MCP.md` documents the MCP
surface, which reads transcripts only when an agent asks.

## 8. Known limitations (read before a regulated deployment)

1. **Unsigned binaries.** v3.9.0 installers and executables are not code-signed. Windows SmartScreen
   will warn on first run. Code signing is deferred by the project owner (see `SIGNING.md`);
   the interim trust signal is hashes + provenance attestations.
2. **No MDM-grade tamper resistance.** Managed policy is enforced in the app but a local
   administrator can change it; use Windows user rights/AppLocker to constrain that.
3. **No at-rest encryption of transcripts.** BitLocker (or similar) is required for sensitive data.
4. **No formal certification.** No ISO 27001, SOC 2, Common Criteria or pen-test report. The
   evidence here is engineering evidence, not an audit.
5. **Single-maintainer project, no SLA.** Support is best-effort via GitHub issues
   (`SECURITY.md` has response targets for vulnerabilities).
6. **Benchmark coverage.** The Arabic evaluation set has 90 clips across MSA, Iraqi, Gulf, Egyptian,
   Latin-mixed and technical speech; Levantine and Iraqi dialect coverage is thinner than MSA. Do
   not generalize word-error numbers beyond the published set.

## 9. Verification and evidence

- Automated: 120 Rust tests, 204 frontend/unit tests, 62 Python benchmark tests, engine guard tests,
  i18n parity, typecheck. CI workflow: `.github/workflows/ci.yml`.
- Release evidence: `docs/VERIFICATION.md` lists every asset, SHA-256, silent-install and
  version check for the current release; `docs/ACCEPTANCE.md` maps requirements to evidence.
- Reproduce a hash: `Get-FileHash .\Sada_3.9.0_x64-setup.exe -Algorithm SHA256`.
- Verify provenance: `gh attestation verify .\Sada_3.9.0_x64-setup.exe --repo alshahia/sada`.

## 10. Reporting a vulnerability

See `SECURITY.md`. Do not open a public issue for an unfixed vulnerability. The project
aims to acknowledge within 3 business days and to ship a fix for high-severity issues within 30
days of confirmation, best-effort given the single-maintainer model.
