# P6 — trust and enterprise readiness (v3.9.0 Wave 1)

Status: in progress (opened 2026-11-19, implementation landed for v3.9.0). Milestone: P6 Wave 1 —
trust and enterprise readiness (#7). Issues: #27–#35. See "Delivered" below for the map from
workstream to code/docs. This plan covers exactly what can be done without the owner: no purchases, no
certificate application, no external audit and no hardware acquisition. Items that need the owner
are listed at the end and are **not** activated by this plan.

## Why

v3.8.0 shipped an honest readiness statement ([PRODUCTION-READINESS.md](PRODUCTION-READINESS.md)):
ready for individual and small-team offline Windows use, but not yet for sensitive-data or
managed-enterprise deployment. The remaining gaps are not engine problems; they are trust signal,
packaging/policy and assurance evidence:

1. **Sensitive data** — unsigned binaries (signing deferred by the owner), no verifiable supply
   chain, optional egress paths not documented or administratively controllable, API keys stored in
   plaintext config, no retention controls, no security whitepaper/DPIA material for buyers.
2. **Managed enterprise / regulated** — no MSI/per-machine deployment path, no admin policy to
   enforce offline behaviour, no AV/EDR guidance, no dependency-scanning/SBOM/provenance practice,
   no response targets in SECURITY.md, clean-machine rows B–E still unexecuted.

## Goal

Close every gap that software and documentation can close without the owner, and leave only
owner-level items: code-signing application/budget, paid support/SLA, external audit, and physical
hardware for rows B–E.

## Non-goals (owner decisions, deliberately not activated)

- Applying for SignPath Foundation or buying an OV/EV certificate, and enabling signing.
- Committing to paid support, SLA credits or a commercial entity.
- Ordering an external penetration test or audit.
- Buying/building hardware for clean-machine rows B–E (the runbook and scripts are delivered so
  anyone with the hardware can execute them).
- Any change to the Arabic-first, fully-local design: no telemetry, no auto-updater, no relay.

## Workstreams

| # | Issue | Deliverable | Acceptance |
| --- | --- | --- | --- |
| 1 | #27 | Assurance pack: `SECURITY-WHITEPAPER.md`, `THREAT-MODEL.md`, `DATA-HANDLING.md`, `AV-EDR.md` | Accurate against code (egress inventory verified), linked from docs index and README, link check clean |
| 2 | #28 | Keyless supply chain: GitHub build provenance attestations, CycloneDX SBOM asset, `scripts/verify-release.ps1`, `SUPPLY-CHAIN.md` | v3.9.0 release has attestations + SBOM; verification script passes on published assets |
| 3 | #29 | Security operations: rustsec audit-check + pnpm audit workflow, Dependabot (cargo/npm/actions), SECURITY.md response targets | Workflow green, configs validated, SECURITY.md reviewed |
| 4 | #30 | Egress inventory (`NETWORK.md`) + machine-wide managed policy (offline mode) read by Rust and enforced in commands/UI | Policy set ⇒ no network features offered, guarded commands refuse, tests |
| 5 | #31 | DPAPI protection of Claude/OpenAI API keys + plaintext migration | Roundtrip and migration tests, AI still works, docs |
| 6 | #32 | Transcript retention (days, default off), purge command limited to transcripts dir, Settings action, log-redaction review | Cutoff/safety tests, AR/EN strings, docs |
| 7 | #33 | Per-machine MSI third asset + Intune/SCCM/GPO deployment kit, detection/uninstall scripts | MSI in CI/release, install/uninstall evidence (or documented admin requirement), `ENTERPRISE-DEPLOYMENT.md` |
| 8 | #34 | Rows B–E acceptance runbook + scripts + evidence template; execute any row the host supports | Scripts syntax/exit checks, runbook complete, templates added |
| 9 | #35 | v3.9.0 docs, version bump, AR/EN notes, full tests, release, verification evidence | Release published and verified; P6 Wave 1 issues closed |

## Design decisions

### Managed policy (admin controls)

**Implemented.** The Rust shell reads machine-wide values from
`HKLM\SOFTWARE\Sada\Policy` (DWORD values; `TranscriptsDir` as SZ) and merges a JSON file
at `%ProgramData%\Sada\policy.json` (override with `SADA_POLICY_PATH` for tests); registry
values win and restrictions are OR-ed, so no source can loosen another. The policy is exposed to the
UI through the `get_managed_policy` command and re-read by the Rust command layer on every
guarded action. Administrators deploy it with Intune/GPO/SCCM (registry preference or script);
`scripts/enterprise/set-sada-policy.ps1` and `clear-sada-policy.ps1` implement it. Schema
(all fields optional, missing = false/default):

    {
      "offlineMode": true,
      "disableAi": true,
      "disableUrlImport": true,
      "disableModelDownloads": true,
      "transcriptsDir": "D:\\Sada\\transcripts"
    }

Semantics:

- `offlineMode` implies all other disable flags; the app hides/disables the AI section, URL
  import and model catalogue downloads, and guarded Rust commands refuse with a clear error.
- `transcriptsDir` pins the transcript output directory; the Setting becomes read-only.
- The policy is re-read on every guarded operation; malformed JSON is ignored with a warning, and a
  registry failure never disables file-based restrictions (fail-open for availability, documented as
  an admin responsibility). The connectivity probe returns "offline" without opening a socket when
  `OfflineMode` is set. URL import/download guards are covered by Rust tests.
- Limit: policy is a management control inside the local-user trust boundary. A user who can edit
  files as themselves could bypass UI gating; guarded commands in Rust refuse regardless of UI state.
  Strong enforcement is a Windows policy/user-rights task (documented).

### DPAPI secrets

**Implemented.** Claude/OpenAI API keys are encrypted per Windows user with `CryptProtectData`
(caller-supplied FFI, current-user scope, `CRYPTPROTECT_UI_FORBIDDEN`), stored as hex blobs in
`app_config.json` (`claudeApiKeyEnc`/`openaiApiKeyEnc`), and never written back as
plaintext. On boot the frontend decrypts the blobs into memory and migrates legacy plaintext keys
once, clearing them. Decryption failure (copied profile, tampered blob) yields an empty provider key
so the user re-enters it. Loss of the Windows profile means re-entering the key (documented). Ollama
has no key; base URLs stay non-secret.

**Implemented.** `transcription.retentionDays` (0 = off, default 0) plus a Settings action runs
`purge_old_transcripts`, which deletes only project folders containing `transcript.vibe.json`
and legacy `*.vibe.json` files under the configured transcripts directory that are older than the
cutoff, and reports deleted count and freed bytes. No deletion runs outside that directory; symlinks
and junctions are skipped; foreign files are left alone (covered by Rust tests). Automatic purge runs
once per launch (2 s after boot) when a window is set. Logs never include transcript text or API keys
in release builds (audited under #32).

### Supply chain

- **Implemented:** GitHub Artifact Attestations (keyless, Sigstore) for every release asset via
  `actions/attest-build-provenance`; consumers run `gh attestation verify <asset> --repo
  alshahia/sada` or the new `scripts/verify-release.ps1` (hash + attestation in one step).
- CycloneDX SBOM (application + Rust workspace + npm production dependencies) published as a release
  asset; FFmpeg/WebView2 external components listed explicitly.
- `SHA256SUMS.txt` stays as the offline verification path; `scripts/verify-release.ps1` checks
  hashes and attestation in one step.
- Code signing remains dormant (#18); the attestation flow is the interim trust signal.

### MSI / enterprise deployment

**Implemented:** NSIS per-user stays the consumer default; a per-machine MSI (WiX) is built from
`desktop/src-tauri/tauri.enterprise.conf.json` and published as the third asset. Silent install
`msiexec /i ... /qn`, detection/uninstall, policy deployment and model pre-provisioning are
documented in [ENTERPRISE-DEPLOYMENT.md](ENTERPRISE-DEPLOYMENT.md) with helper scripts under
`scripts/enterprise/`. MSI requires administrator rights; the docs say so.

### Rows B–E

**Implemented:** `scripts/acceptance/run-row-b-e.ps1` collects machine facts (OS/CPU/AVX/WebView2),
verifies a local installer against `SHA256SUMS.txt`, optionally silent-installs it, records the
installed version/sidecar hash, prints the manual checklist and writes an evidence block matching
the template in [VALIDATION-RUNBOOK.md](VALIDATION-RUNBOOK.md). The rows themselves need hardware this
host does not have, so they stay unchecked with explicit "blocked: no hardware" notes in
VERIFICATION.md — the runbook and script let anyone with the hardware execute them.

## Release plan (v3.9.0)

1. Land workstreams in order, each with tests and docs.
2. Full local matrix: pnpm test, pnpm build, cargo test --release, engine guard, cargo check, i18n,
   Python tests.
3. Version bump 3.9.0; release notes AR/EN; CHANGELOG; README/BUILDING/SIGNING/ACCEPTANCE/ROADMAP/
   llms/site updates.
4. Tag `v3.9.0`; Release workflow builds default NSIS + offline NSIS + MSI, generates SBOM,
   publishes provenance attestations, verifies both installers; CI runs the gate.
5. Re-download every asset, verify SHA-256 + attestation, silent-install NSIS variants and MSI, record
   VERIFICATION.md evidence, close #27–#35, comment on #17/#18.

## Delivered in v3.9.0 (map)

| Workstream | Code / artifacts | Docs |
| --- | --- | --- |
| #27 Assurance pack | — (documentation) | SECURITY-WHITEPAPER.md, THREAT-MODEL.md, DATA-HANDLING.md, AV-EDR.md |
| #28 Supply chain | release workflow attestations + SBOM, scripts/verify-release.ps1 | SUPPLY-CHAIN.md |
| #29 Security ops | CI dependency scan workflow, .github/dependabot.yml, response targets | SECURITY.md |
| #30 Egress + managed policy | src-tauri/src/policy.rs, src/lib/policy.ts, guards in download/ytdlp/handoff/is_online, UI gating | NETWORK.md (+ar), ENTERPRISE-DEPLOYMENT.md |
| #31 DPAPI keys | src-tauri/src/secrets.rs, src/lib/ai/secrets.ts, boot migration | whitepaper §4, DATA-HANDLING.md |
| #32 Retention | src-tauri/src/retention.rs, purge command + Settings/Privacy action, boot purge | DATA-HANDLING.md |
| #33 MSI + deployment kit | tauri.enterprise.conf.json, scripts/enterprise/*.ps1 | ENTERPRISE-DEPLOYMENT.md |
| #34 Rows B–E | scripts/acceptance/run-row-b-e.ps1 + evidence template | VALIDATION-RUNBOOK.md (rows stay blocked: no hardware) |
| #35 Release | version bump, release notes, CHANGELOG/VERIFICATION/roadmap, full suites | docs/releases/v3.9.0.md |

Test counts at delivery: 120 Rust tests (19 new), 204 frontend tests (11 new), 62 Python benchmark
tests. Residual owner-level gaps are unchanged: signing (#18), rows B–E execution, external
audit, SLA.

## Risks and residuals

- New Rust code (policy, DPAPI via P/Invoke, retention) touches the security surface: keep it small,
  testable, no new network behaviour, no new telemetry.
- MSI/WiX bundling adds CI time and may need tool download; if CI cannot build it reliably, the MSI
  becomes a local/optional asset and the gap is documented (still better than no path).
- Without signing, SmartScreen stays; assurance docs say so explicitly.
- Single maintainer and no SLA remain business risks, not engineering gaps.

## Owner decisions still open

- Code signing route (#18): SignPath Foundation (free OSS) vs Azure Artifact Signing vs OV cert;
  application packet prepared in `SIGNING.md` appendix when the owner is ready.
- Paid support/SLA tier for managed-enterprise buyers.
- External penetration test / audit budget when a regulated buyer appears.
- Hardware/VM access for rows B–E (offline Windows 10, CPU-only, AVX-only, AVX-less SSE4.2).
