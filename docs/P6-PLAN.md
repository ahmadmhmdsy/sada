# P6 — trust and enterprise readiness (v3.9.0 Wave 1)

Status: in progress (opened 2026-11-19). Milestone: P6 Wave 1 — trust and enterprise readiness (#7).
Issues: #27–#35. This plan covers exactly what can be done without the owner: no purchases, no
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

A machine-wide JSON file, `%ProgramData%\Sada\policy.json` (override with
`SADA_POLICY_PATH` for tests), is read by the Rust shell at startup and exposed to the UI via a
Tauri command. Administrators deploy it with Intune/GPO/SCCM (file or script); no registry writes
are needed by the app. Schema (all fields optional, missing = false/default):

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
- The file is read at startup and re-read when the config changes; malformed JSON is ignored with a
  warning (fail-open for availability, documented as an admin responsibility).
- Limit: policy is a management control inside the local-user trust boundary. A user who can edit
  files as themselves could bypass UI gating; guarded commands in Rust refuse regardless of UI state.
  Strong enforcement is a Windows policy/user-rights task (documented).

### DPAPI secrets

Claude/OpenAI API keys are encrypted per Windows user with `CryptProtectData` (DPAPI, current
user scope) in the Rust layer, stored as base64 blobs in `app_config.json`
(`claudeApiKeyEnc`/`openaiApiKeyEnc`), and never written back as plaintext. On load, legacy
plaintext keys are encrypted and redacted. Loss of the Windows profile means the key must be
re-entered (documented). Ollama has no key; base URLs stay non-secret.

### Retention

`transcription.retentionDays` (0 = off, default 0) plus a Settings action runs a Rust purge that
deletes only files under the configured transcripts directory older than the cutoff, and reports how
many were removed. No deletion runs outside that directory; symlink/junction resolution stays inside
the root. Automatic purge (if enabled) runs once per launch in the background. Logs never include
transcript text or media paths in release builds (audited under #32).

### Supply chain

- GitHub Artifact Attestations (keyless, Sigstore) for every release asset via
  `actions/attest-build-provenance`; consumers run `gh attestation verify <asset> --repo
  alshahia/sada`.
- CycloneDX SBOM (application + Rust workspace + npm production dependencies) published as a release
  asset; FFmpeg/WebView2 external components listed explicitly.
- `SHA256SUMS.txt` stays as the offline verification path; `scripts/verify-release.ps1` checks
  hashes and attestation in one step.
- Code signing remains dormant (#18); the attestation flow is the interim trust signal.

### MSI / enterprise deployment

Keep NSIS per-user as the consumer default; add a per-machine MSI (WiX) third asset for managed
deployment with public properties (INSTALLDIR, ALLUSERS=1), silent install `msiexec /i ... /qn`,
detection rules for Intune/SCCM and a documented uninstall. Policy file and model pre-provisioning
are deployed alongside. MSI requires administrator rights; the docs say so.

### Rows B–E

Deliver `scripts/acceptance/run-row-b-e.ps1` (or equivalent) that performs the smoke steps,
captures versions/hashes/GPU/CPU flags and writes an evidence block matching the ACCEPTANCE template.
Rows that need hardware stay unchecked with explicit "blocked: no hardware" notes.

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
