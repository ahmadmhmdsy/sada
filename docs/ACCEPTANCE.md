# Clean-machine acceptance

This page is the release acceptance procedure for a Windows build that must work **offline, on a
clean machine, without developer tooling**. It is the checklist issue #16 asks for: every build is
tested twice, once on the development machine (automated suites, see the bottom of this page) and
once by installing the published installer on a machine that has never had Rust, Node, Python,
FFmpeg or the app itself.

The procedure is the script for an acceptance run (last attempted for v3.6.0; the next target is
v3.9.0, where all three deployment assets exist — per-user NSIS, offline-WebView2 NSIS and the
per-machine MSI). Record the evidence in the table at the end; the
published results for each release live in docs/VERIFICATION.md.

The engine reports its build through the `-sada.N` suffix: 3.4.0 through 3.10.0 shipped
`vibe-server v0.6.16-sada.1`, and from 3.11.0 the release builds `v0.6.16-sada.2` — check the version
the installer actually ships instead of assuming it. From 3.11.0 the provenance attestations also
cover `SHA256SUMS.txt`, so the hash list itself is attested.

## Machine matrix

| Slot | Machine | Purpose |
| --- | --- | --- |
| A | Windows 11 x64, SSD, WebView2 preinstalled, no developer tools | default path: online install, GPU transcription |
| B | Windows 10 22H2 x64, no developer tools, **network disconnected** | offline install and offline transcription |
| C | Same as B, CPU only (no Vulkan device) | CPU fallback, baseline build |
| D | VM limited to AVX-only CPU (Sandy Bridge model) — or any pre-2013 x64 CPU | baseline CPU build |
| E | VM with SSE4.2 but no AVX | expected graceful failure, not a crash |

Windows 11 ships the WebView2 Evergreen Runtime; many Windows 10 images do not. The default
installer (about 45 MB) uses Tauri's `downloadBootstrapper` mode, which needs a network connection
to fetch WebView2. From v3.8.0 the release also publishes
**`Sada_<version>_x64-setup-offline.exe`** (about 250 MB), whose bundle embeds the WebView2
Evergreen installer; use that file for slot B, and verify both hashes against `SHA256SUMS.txt`.
From v3.9.0 there is also a per-machine MSI (`Sada_<version>_x64_en-US.msi`) for managed
environments; the acceptance rows below use the NSIS installers because they match the consumer
download paths (the MSI has its own silent-install checks in [ENTERPRISE-DEPLOYMENT.md](ENTERPRISE-DEPLOYMENT.md)).
Caveat: neither variant embeds the VC++ 2015-2022 runtime — the NSIS hook downloads it from
Microsoft when missing or older than 14.40, so on a fully offline machine pre-install
`vc_redist.x64.exe` (or let WebView2 setup pull it) before running the acceptance steps.

## Models on an offline machine

No model is bundled. On the connected machine, download the model(s) and the Silero VAD model from
Settings -> Models, then copy the models folder to the offline machine before the run. The folder is
reported by the app (Settings -> Models -> Models folder) and defaults to
%LOCALAPPDATA%\Sada\models. The sidecar binaries (vibe-server, ffmpeg) are inside the installer.

## Acceptance steps

### A. Install and first run (machines A and B)

1. Verify the installer against the SHA256SUMS.txt attached to the release:
   Get-FileHash .\Sada_<version>x64-setup.exe -Algorithm SHA256
2. Install per-user (default). Confirm the install path is under %LOCALAPPDATA%\Sada.
3. Launch. The window is Arabic (RTL), first-run language ar-IQ, transcription language ar,
   translation off.
4. No DevTools console errors. In particular no Content-Security-Policy violations on the first
   paint, while loading models, or while playing a recording (the 3.6.0 CSP is new).

Pass: first paint Arabic, no error dialog, no console CSP violation.

### B. Offline transcription (machine B, network adapter disabled)

1. Disable every network adapter (Settings -> Network -> Change adapter options -> Disable), or
   block Sada outbound in Windows Defender Firewall with advanced security.
2. Launch, load a sideloaded model, transcribe a 30-second Arabic clip and export the transcript.
3. Repeat with a dictation via the global shortcut: record, stop, confirm the text is typed into
   Notepad.

Pass: both transcriptions succeed with no network adapter enabled; Windows firewall shows no
outbound rule hit; text typed exactly once per recording.

### C. CPU fallback (machine C)

1. Settings -> Advanced -> CPU build: "baseline" (this maps to VIBE_SERVER_CPU_VARIANT=baseline).
2. Load the model and transcribe the same clip.
3. Repeat once with the GPU device removed/disabled.

Pass: transcription succeeds on CPU; the engine log shows no illegal-instruction exit; the UI does
not show the "CPU without AVX" hint.

### D. Baseline CPU (machine D, or a VM with AVX but not AVX2/FMA/BMI2)

1. Leave the CPU build on "auto" first: the server detects AVX2/FMA/BMI2 and picks the Haswell
   build only if the CPU has all three; otherwise it must fall back to the x64 baseline build.
2. Transcribe.
3. Force the wrong build (Settings -> Advanced -> "AVX2") and confirm the app reports the
   illegal-instruction hint instead of crashing silently.

Pass: auto picks baseline, transcription works, the forced-wrong build gets the explanatory error.

### E. SSE4.2 without AVX (machine E)

Both bundled x64 backends require AVX (baseline is AVX + SSE4.2). A CPU with SSE4.2 but no AVX
therefore cannot run the engine. Expected behaviour: the app shows the illegal-instruction hint
("This looks like a CPU without AVX support...") naming Settings -> Advanced, and the UI stays
usable.

Pass: readable error, no silent crash loop, no corrupted config.

### F. Nemotron VAD path (machine A or B)

1. Install the Nemotron model from the catalog (machine A) or copy it to the offline machine (B).
2. Ensure the Silero VAD model is present (Settings -> Models shows it; the app downloads it once
   when a VAD model is selected).
3. Transcribe with timestamps enabled, offline on machine B.
4. Confirm the timestamps checkbox is honoured and the transcript is not empty for silence-only
   audio.

Pass: Nemotron transcription with request timestamps; VAD resolved from the offline copy; no
different failure between online and offline.

### G. Deep link and URL hardening (machine A, online)

1. In a browser, open
   sada://download/?url=https%3A%2F%2Fhuggingface.co%2Fggerganov%2Fwhisper.cpp%2Fresolve%2Fmain%2Fggml-tiny.bin
   The dialog must show the **whole URL**, and accepting must prefill the setup download.
2. Repeat with a non-catalog host:
   sada://download/?url=https%3A%2F%2Fexample.com%2Fmodel.bin
   The app must refuse it (no download, console message only).
3. Repeat with a plain http URL: also refused.

Pass: only https on huggingface.co / github.com is offered, and the full URL is visible before
accepting.

### H. Engine confinement and typing permit

1. While a transcription runs, check the server process working directory is the sidecar folder and
   its TEMP points at the app temp folder (Process Explorer -> Environment).
2. From an unrelated program, call the app's type_text command path (DevTools console in the app
   window): it must be rejected because no recording finished recently.
3. Record a dictation and confirm type_text works exactly once.

Pass: both checks behave as described; the Rust unit tests cover the same paths.

## Evidence table

| Slot | Windows | WebView2 | CPU / GPU | Offline | Result | Date |
| --- | --- | --- | --- | --- | --- | --- |
| A |  |  |  |  |  |  |
| B |  |  |  |  |  |  |
| C |  |  |  |  |  |  |
| D |  |  |  |  |  |  |
| E |  |  |  |  |  |  |

## Automated evidence recorded during development

| Check | Command | Result |
| --- | --- | --- |
| Frontend tests | cd desktop; pnpm test | 33 files / 204 tests passed |
| Frontend build | cd desktop; pnpm build | exit 0, final vite bundle 1m 5s |
| Rust tests | cd desktop/src-tauri; cargo test --release | 120 tests passed, exit 0 |
| Engine guard tests | cargo test --release -p vibe-server guard:: | 8 tests passed, exit 0 |
| Arabic benchmark tests | cd benchmarks/arabic-asr; python -m unittest discover -s tests | 62 tests passed (including regression-gate tests) |
| i18n audit | python scripts/check_i18n.py | passed |
| Rust type check | cd app; cargo check --tests | exit 0 |
| Installers | release workflow artifacts, 3.9.0 | default 44,939,266 bytes · SHA-256 `560b76c2…6133`; offline-WebView2 262,848,006 bytes · SHA-256 `674d58c2…b979`; MSI 70,934,528 bytes · SHA-256 `751e74f3…6bad`; all three hash-matched `SHA256SUMS.txt`, NSIS silent-install verified (Sada.exe 3.9.0, sidecar v0.6.16-sada.1, MCP sada-mcp 3.9.0), MSI database verified as per-machine en-US (`ALLUSERS=1`, ProductVersion 3.9.0) |
| Build provenance | `gh attestation verify` on all three installers + `sbom-cyclonedx.json` | passed (keyless Sigstore) |
| SBOM | `sbom-cyclonedx.json` from the release | CycloneDX 1.6, 1,939 components, bundled FFmpeg/WebView2/vibe-server/yt-dlp listed |
| Release verification script | `scripts/verify-release.ps1 -Version 3.9.0 -Download` | hashes and attestations passed, exit 0 |
| Benchmark regression gate | cd benchmarks/arabic-asr; python -m sadabench compare --baseline results/results-2026-11-18-v2.json --candidate results/results-2026-11-18-v2.json | passed, all deltas 0.00 pp; CI runs the same self-comparison |

The recorded values are for the v3.9.0 release (19 November 2026); the same commands were run for v3.8.0 in the previous cycle (193 frontend tests, 101 Rust tests, two installers). The clean-machine runs above (slots B-E) need physical/VM machines the maintainer controls; until
they are recorded this page is the procedure plus the automated evidence, and docs/VERIFICATION.md
says exactly which rows were actually run for the release. P6 (v3.9.0) adds a ready-to-run script
for those rows — `scripts/acceptance/run-row-b-e.ps1` (invoked as `-Slot B`, `-Slot C`, `-Slot D`
or `-Slot E`, with `-AssetDir`, optional `-Install` and `-EvidenceOut`) — plus the step list in
[VALIDATION-RUNBOOK.md](VALIDATION-RUNBOOK.md). Rows B–E remain **blocked on hardware**, not on code.
