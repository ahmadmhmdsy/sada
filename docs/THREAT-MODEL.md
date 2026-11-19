# Threat model — Sada 3.9.0

Method: asset inventory, trust boundaries, then a STRIDE pass over the entry points that exist in
this build. This is a software-engineering threat model maintained with the code, not a formal
audit. It is reviewed whenever a release changes the network surface, packaging or secrets
handling.

Last updated: 2026-11-19 (v3.9.0). Related: `NETWORK.md`, `SECURITY-WHITEPAPER.md`,
`DATA-HANDLING.md`.

## Assets

| Asset | Why it matters |
|-------|----------------|
| Recordings and transcripts | Personal, business, legal or medical speech content; the most sensitive data the app handles |
| Exported documents | Copies of transcripts outside the app's store |
| AI provider API keys | Billable credentials; leakage enables abuse at the user's expense |
| Model files | Integrity matters (a tampered model could alter output); no secrets |
| Update/release artifacts | A tampered installer is the classic supply-chain attack |
| Settings / managed policy | Determines whether the app may use the network |

## Adversaries

1. **Opportunistic local attacker** — another user on the machine, or malware running as the user.
2. **Network attacker** — on-path observer/attacker between the machine and a download/AI provider.
3. **Malicious or compromised upstream** — a hijacked download host, GitHub account, dependency or
   release asset.
4. **Curious/abusive insider with user rights** — can read the user profile and use the app.
5. **Administrator** — intentionally out of scope as an attacker: admin can do anything on Windows.

## Trust boundaries

WebView2 ↔ Rust IPC; app ↔ filesystem; app ↔ network; app ↔ child processes (sidecar/FFmpeg/
yt-dlp); release pipeline ↔ source repository. The Rust command layer is the enforcement point for
every boundary except filesystem ACLs, which Windows owns.

## STRIDE analysis (entry points that exist in this build)

| Threat | Scenario | Mitigation | Residual risk |
|--------|----------|------------|---------------|
| Spoofing | Fake "update" or model page tricks a user into installing something | No updater; version link opens the real GitHub releases page in the browser; model downloads are HTTPS only and verified when the catalog has a hash | User can still run any file they choose; unsigned builds mean SmartScreen cannot vouch for Sada |
| Tampering | Modified model file or installer | SHA-256/size/magic checks for models; yt-dlp checked against release sums; release sums + Sigstore provenance attestations for installers | Unsigned installers: integrity depends on verifying hashes/attestations out of band |
| Repudiation | Dispute over what was transcribed or deleted | Local-only logs of app actions; retention purge logs counts (not content) | No tamper-evident audit log by design (privacy) |
| Information disclosure | Transcript or key leaks | No telemetry/upload; AI calls only when configured; keys DPAPI-sealed; logs exclude transcript text and keys; files inherit Windows ACLs | No at-rest encryption of transcripts; a user-level attacker can read the profile; AI prompts necessarily contain transcript text when AI is enabled |
| Denial of service | Corrupt config/model, full disk, hostile media file | Config failures fall back to defaults; model checks reject truncated files; FFmpeg/yt-dlp run as separate processes; download cancellations | A malicious media file can still crash a decoder process; engine is restarted rather than trusted |
| Elevation of privilege | WebView compromise reaching the OS | Rust-owned commands validate inputs; no shell execution of user strings; IPC handler list is fixed; CSP restricts the webview; plugin capability scopes are declared | Tauri/WebView2 vulnerabilities are inherited from upstream; keep them patched |
| Policy bypass | User disables offline policy via UI | Policy is re-read in Rust per guarded action; UI gating is cosmetic only | Local admin can edit HKLM; documented as admin responsibility |

## Specific attack paths considered

- **URL import / yt-dlp:** the URL is user-supplied; yt-dlp is a third-party binary downloaded from
  its own release and hash-checked. A malicious site is handled by yt-dlp/FFmpeg as untrusted input.
  Under managed policy this path can be disabled entirely.
- **AI providers:** prompts contain transcript text by definition. Keys are secrets in transit
  (TLS) and at rest (DPAPI). There is no project-operated proxy; the user's chosen provider sees
  the prompt. `disableAi` removes the path.
- **Phone handoff:** upstream iroh endpoint is not exposed in Sada and its start command refuses.
  This removes the only relay-like path rather than relying on a setting.
- **MCP server:** stdio only; the agent already has the user's file access, so MCP adds no new
  privilege. It can read transcripts the user can read.
- **Local API server (agents):** binds loopback with a per-run token; documented in
  `AGENT-MCP.md`; under offline policy it remains loopback-only.
- **DPAPI profile copy:** copied config cannot be decrypted on another account/machine; key loss is
  a usability cost, documented in `DATA-HANDLING.md`.
- **Silent install / MSI:** MSI requires administrator and installs per-machine; the policy file and
  model folder are the admin's responsibility. Detection rules are documented in
  `ENTERPRISE-DEPLOYMENT.md`.

## Out of scope

- An administrator intentionally weakening the machine.
- Physical access to an unlocked machine without disk encryption.
- Vulnerabilities in Windows, WebView2, the GPU driver or the model files themselves.
- The accuracy of transcriptions (an ASR quality property, not a security one).
- Third-party AI providers' handling of data they receive.

## Review triggers

Any change to: network commands, the IPC handler list, capability files, secrets handling,
installer packaging, update/attestation workflow, or the managed-policy schema.
