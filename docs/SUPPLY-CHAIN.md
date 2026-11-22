# Supply chain — Sada 3.11.0

How a Sada release is built, what proves where it came from, and how a consumer verifies it
without trusting this repository's account. This is the practical evidence pack; the security
rationale is in `SECURITY-WHITEPAPER.md`.

Last updated: 2026-11-22 (v3.11.0).

## Build path

1. Source: tagged commit on `alshahia/sada`, branch `master`.
2. Runner: GitHub-hosted `windows-latest`, workflow `.github/workflows/release.yml`,
   triggered by pushing a `v<version>` tag (the tag must equal `desktop/src-tauri/tauri.conf.json`'s
   version and match `docs/releases/v<version>.md`, or the run fails before building).
3. Dependencies are installed from committed lockfiles: `pnpm install --frozen-lockfile` and
   Cargo lockfiles; the engine workspace under `server/` is built from source in the same job.
4. The bundled sidecars come from the pinned `.server-version` via `chore`; the engine is built
   from `server/` and reports `<.server-version>-sada.2` since 3.11.0 (the suffix makes each
   installer’s engine build unique), and the request guard tests must pass before packaging.
5. Tests run before packaging: frontend unit tests, Rust tests in release mode, engine guard tests.
6. Bundles: NSIS default, NSIS offline-WebView2, and a WiX per-machine MSI. No signing (dormant,
   see `SIGNING.md`) — hashes and attestations are the interim trust signal.
7. Assets are collected, hashed into `SHA256SUMS.txt`, SBOM generated, and a keyless provenance
   attestation is created for the three installers, `SHA256SUMS.txt` and the CycloneDX SBOM — so
   the hash list itself is attested. All assets are uploaded in one release step.

## What is published

| Asset | Purpose |
|-------|---------|
| `Sada_<version>_x64-setup.exe` | Default per-user NSIS installer |
| `Sada_<version>_x64-setup-offline.exe` | NSIS installer with embedded WebView2 runtime |
| `Sada_<version>_x64_en-US.msi` | Per-machine WiX installer for managed deployment |
| `SHA256SUMS.txt` | SHA-256 of every installer (offline verification path) |
| `sbom-cyclonedx.json` | CycloneDX SBOM: Rust + npm dependencies, external components |
| `LICENSE`, `NOTICE`, `THIRD-PARTY-NOTICES.md` | Licensing and attribution |

Attestations are stored by GitHub (not as downloadable assets) and prove that a given file was
built by this repository's workflow from a specific commit. The attested subjects are the three
installers, `SHA256SUMS.txt` (since 3.11.0) and `sbom-cyclonedx.json`.

## Verification (consumer side)

Fast path, no build:

```powershell
# 1. Download the release assets and SHA256SUMS.txt from the GitHub release page.
# 2. Verify hashes and provenance in one step (GitHub CLI required for attestations):
.\scripts\verify-release.ps1 -Version 3.11.0 -Download

# Or verify a local directory without re-downloading:
.\scripts\verify-release.ps1 -Path .\Sada_3.11.0_x64-setup.exe
```

Manual equivalents:

```powershell
Get-FileHash .\Sada_3.11.0_x64-setup.exe -Algorithm SHA256
gh attestation verify .\Sada_3.11.0_x64-setup.exe --repo alshahia/sada
# and, since 3.11.0, the checksum list itself:
gh attestation verify .\SHA256SUMS.txt --repo alshahia/sada
```

The script exits non-zero on any hash mismatch or missing attestation, and never installs anything.
Missing `gh` produces a warning for attestations (the hash check still runs); use the CLI for
the full check.

## SBOM

- CycloneDX JSON produced on the release runner from the Rust and npm lockfiles.
- Includes direct and transitive dependencies with versions, plus explicitly listed external
  components: FFmpeg (GPLv3, separate executable), WebView2 runtime (Microsoft), the pinned
  `vibe-server` sidecar (version `v0.6.16-sada.2` since 3.11.0) and yt-dlp (fetched at runtime,
  not bundled).
- Model files are not software dependencies; their hashes are documented in `docs/MODELS.md`.
- The SBOM is a starting point for an inventory, not a vulnerability report; pair it with the
  dependency scanning in CI (`cargo audit` / `pnpm audit`, see `SECURITY.md`).

## Dependency and vulnerability practice

- Dependabot is configured for Cargo, npm and GitHub Actions (see `.github/dependabot.yml`).
- CI runs a scheduled and push-time dependency scan (RustSec advisory database and npm audit).
- Security fixes are handled under the response targets in `SECURITY.md`.
- No model weights are stored in the repository; no secrets are committed. Telemetry keys are
  compiled out rather than configured.

## Signing status

Not signed. The signing configuration overlay exists and the Release workflow has a dormant
`SIGNING_ENABLED` gate; when the owner enables it, a valid Authenticode signature is required
on every installer before the release step. Until then:

- SmartScreen shows a warning (see `AV-EDR.md` for allow-listing guidance).
- Integrity relies on published hashes plus Sigstore attestations.
- The signing application packet is prepared in the appendix of `SIGNING.md`; it is not
  activated by this plan.

## Reproducibility

The build is not bit-for-bit reproducible across machines (Windows toolchain, WiX/NSIS timestamps,
WebView2 payloads vary). What is verifiable: the exact commit, the workflow run, the input
lockfiles, the published SHA-256 and the attestation binding them. Treat that as the evidence
chain rather than a binary-equality claim.
