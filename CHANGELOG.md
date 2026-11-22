# Changelog

Sada is an Arabic-first fork of [Vibe](https://github.com/thewh1teagle/vibe) (MIT). The upstream
project keeps its own detailed release history; this file records Sada releases and the fork's
delta from upstream v3.2.2.

## v3.11.0 — 2026-11-22

Maintenance and release-engineering release. No UI, engine (code), model, identity or feature
change; installers remain unsigned and there is no auto-updater, telemetry or account. The
five-user Arabic gate is still the next UX step and this release makes no Wave-2 or 4.0 claim.
The bundled engine now reports `v0.6.16-sada.2` so each installer’s engine build is identifiable,
and the build-provenance attestations cover `SHA256SUMS.txt` as well as the installers and SBOM.

### Changed

- **Dependency refresh:** twenty Dependabot updates merged on 20–21 November 2026 (Rust crates,
  npm packages and GitHub Actions: checkout 7, setup-node 7, cache 4,
  attest-build-provenance 4, configure-pages 6, codeql-action 4 and others), plus the server’s
  OpenAPI stack moved to utoipa 6 (`utoipa-axum` 0.3, `utoipa-swagger-ui` 10). No product
  behaviour change; lockfiles updated.
- **Tauri 2.12 stack:** the desktop runtime moved from tauri 2.10 to **2.12.7** (wry 0.57.3,
  tao 0.37.3) with the aligned plugin and CLI packages (`tauri-plugin-notification` 2.8.1,
  `tauri-plugin-opener` 2.7.3, `@tauri-apps/api` 2.12.5, `@tauri-apps/cli` 2.12.6). Upstream fixes
  only; no intended UI or transcription change.
- **CI builds and tests the engine:** a `server` job in `ci.yml` runs `cargo check --all-targets`
  and `cargo test --release -p vibe-server` on every change after fetching the pinned native
  libraries. It closes the CI gap that let the engine breakage in #44 pass CI and fail only at
  release time.
- **Release supply chain:** the patched engine is built as `v0.6.16-sada.2` (release workflow, SBOM,
  AV/EDR and security docs) because 3.4.0–3.10.0 shipped three distinct engines that all reported
  `v0.6.16-sada.1`; `SHA256SUMS.txt` is now in the keyless build-provenance attestation subjects
  alongside the three installers and the CycloneDX SBOM.
- **Version bump to 3.11.0** across the app, Cargo manifests/lockfile and site/README/llms/CITATION
  metadata.

### Fixed

- Nothing user-facing in this release; it is a maintenance cut.

## v3.10.0 — 2026-11-19

UI/UX repair release (Wave 1, pre-gate). Implements the owner's 19 November 2026 decisions after
the 3.9.0 UI/UX critique: all four repair families (A–D) plus the V3 scoped truth-only copy. No
engine, model, identity or layout change; installers remain unsigned; no auto-updater, telemetry
or account. The five-user gate is the next step and blocks Wave 2 (3.11) and the 4.0 "Echo"
identity.

### Added

- **Error taxonomy and recovery** (`desktop/src/lib/error-kind.ts` + tests;
  `desktop/src/components/error-modal.tsx`): fixed-precedence classification (disk → memory →
  network → audio → file → model → managed → unknown), a kind-specific title/body and a contextual
  primary action (open model settings, retry a network step, reload); the raw log is behind a
  disclosure with an accessible **Copy details**, **Report issue** is secondary and **Reset** moved
  under **Advanced**. Recording failures report as `audio`.
- **Copy all** (`desktop/src/pages/main/components/transcript-toolbar.tsx`): filled-primary button
  next to Export, `Ctrl+Shift+C`, full transcript as plain text, toast confirmation and tooltip
  hint.
- **Grouped export** (`transcript-export-dialog.tsx`): the nine formats stay, grouped under four
  headings — Text (TXT, Markdown), Captions & timing (SRT, WebVTT), Document (HTML, DOCX, PDF),
  Data (JSON, CSV); batch mode opens a menu.
- **Settings dialog** (`desktop/src/components/settings-modal.tsx`,
  `desktop/src/pages/settings/page.tsx`, `components/layout.tsx`, `components/ui/dialog.tsx`):
  rebuilt on Radix `Dialog` with focus trap/restore, `Escape` and a labelled close button; header
  gear, `Ctrl+,`, `vibe:open-settings` event and `#settings` deep link; four labelled navigation
  groups instead of a flat list.
- **Accessible row labels** (`desktop/src/components/ui/row-label-context.tsx`,
  `settings/sections/shared.tsx`, `ui/switch.tsx`, `ui/select.tsx`): switches and Radix select
  triggers inherit the visible row label as their accessible name.
- **V3 truth-only trust copy** on the drop point (`idle-hero.tsx`), first-run
  (`setup/page.tsx`) and Settings → Privacy, plus a bidi-safe download progress component with
  aria values, live percent, "x of y" size and a calibrated ETA.
- **Five-user gate kit** (`docs/design/ui-decisions/GATE-KIT.md`): materials, moderator rules,
  five Arabic task cards, printable observation sheet, scoring table and pass/partial/fail path.
- **Runtime accessibility evidence**: 35 UI states audited with axe-core 4.14.1 (WCAG 2.2 A/AA) in
  English, Arabic and dark mode — 0 violations; Settings dialog focus trap (5/5) and `Escape`
  verified.

### Changed

- Windows `setTheme` rejection is caught and `core:window:allow-set-theme` is granted, so a theme
  change can no longer surface an unhandled promise error (`providers/preference.tsx`,
  `src-tauri/capabilities/main.json`).
- Arabic inverse tracking rule (`html[lang^='ar'] * { letter-spacing: 0 }` with mono/tabular and
  uppercase-Latin exceptions) and bidi isolates around download sizes.
- Contrast and naming fixes: selected Settings nav row (`bg-primary/10 text-foreground`), version
  footer, selected export-format badge (`bg-primary text-primary-foreground`), display-language
  and transcript-language trigger names that contain their visible labels.
- Mock seed data moved from `Vibe/` to `Sada/` under the Documents folder; decision records,
  boards and 11 screenshots under `docs/design/ui-decisions/` (05, 06 and 09 recaptured after
the fixes).
- Version bump to 3.10.0 across the app, Cargo manifests/lockfile and site/README/llms/CITATION
  metadata.

### Verified

- `pnpm build` exit 0 (paraglide → tsc → Vite, 1m 19s); `pnpm test` 34 files / 207 tests.
- i18n parity 786/786 keys; `node scripts/seo/check-seo.mjs` passed.
- Runtime axe audit 35 states / 0 violations; Settings dialog focus trap and `Escape`.

### Known limitations

- Installers remain unsigned (owner decision) → SmartScreen warning; verify SHA-256/provenance.
- The five-user gate has not been run; no measured usability claim until it completes.
- Windows screen-reader behaviour and the installed (Tauri) build are not covered by the automated
  audit; focus restoration after dialog close was not confirmed; acceptance rows B–E are still
  unexecuted (no hardware/VM); ETA needs real-download calibration.

## v3.9.0 — 2026-11-19

Trust and enterprise-control release (P6 Wave 1). The engine, models, catalogue and transcription
behaviour are unchanged; the release adds the controls, evidence and packaging needed for sensitive
and managed deployments: machine-wide managed policy, DPAPI-protected API keys, transcript
retention, a network egress inventory, an assurance pack, a keyless supply chain (provenance
attestations + SBOM) and a per-machine MSI. Installers remain unsigned by owner decision; no
auto-updater, telemetry or account.

### Added

- **Managed machine policy** (`desktop/src-tauri/src/policy.rs`, `desktop/src/lib/policy.ts`):
  `OfflineMode`, `DisableAi`, `DisableUrlImport`, `DisableModelDownloads` and `TranscriptsDir`
  read from `HKLM\\SOFTWARE\\Sada\\Policy` with a `%ProgramData%\\Sada\\policy.json` fallback
  (`SADA_POLICY_PATH` for tests); restrictions OR-ed, enforced in the Rust command layer on every
  guarded action, and reflected in the UI (AI settings hidden, media-link tab hidden, download
  controls hidden, transcripts folder pinned). The connectivity probe returns "offline" without
  opening a socket under offline mode. Helper scripts under `scripts/enterprise/`.
- **DPAPI-protected AI keys** (`desktop/src-tauri/src/secrets.rs`, `desktop/src/lib/ai/secrets.ts`):
  Claude/OpenAI keys sealed with `CryptProtectData` (current-user scope) as
  `claudeApiKeyEnc`/`openaiApiKeyEnc`; legacy plaintext keys migrate once at boot; decryption
  failure yields an empty key instead of a crash.
- **Transcript retention** (`desktop/src-tauri/src/retention.rs`): `transcription.retentionDays`
  (0 = forever, default), automatic purge at launch and a "delete old transcripts now" action that
  only touches transcript files under the transcripts folder (symlinks skipped, counts/bytes
  reported, content never logged).
- **Network egress inventory** `docs/NETWORK.md` (+ `NETWORK.ar.md`): every outbound path,
  trigger, payload and policy switch; phone handoff is disabled unconditionally
  (`handoff_start` always refuses), and the setup connectivity probe is policy-gated.
- **Assurance pack**: `docs/SECURITY-WHITEPAPER.md`, `docs/THREAT-MODEL.md`,
  `docs/DATA-HANDLING.md`, `docs/AV-EDR.md`.
- **Supply-chain evidence**: GitHub build provenance attestations
  (`actions/attest-build-provenance`) for every release asset, a CycloneDX SBOM
  (`sbom-cyclonedx.json`, enriched with FFmpeg/WebView2/sidecar/yt-dlp by
  `scripts/generate-sbom.ps1`), and `scripts/verify-release.ps1` for hash + attestation checks.
  `docs/SUPPLY-CHAIN.md` documents the chain.
- **Per-machine MSI** (`desktop/src-tauri/tauri.enterprise.conf.json`) published as a third asset,
  plus `docs/ENTERPRISE-DEPLOYMENT.md` and `scripts/enterprise/` for silent install, detection,
  policy, uninstall and user-data cleanup.
- **Security operations**: `.github/workflows/security.yml` (RustSec audit of every cargo
  lockfile, production npm audit failing only on critical advisories, CodeQL for the frontend),
  `.github/dependabot.yml` (Cargo/npm/actions/Python), and response targets in `SECURITY.md`.
- **Validation runbook**: `docs/VALIDATION-RUNBOOK.md` and
  `scripts/acceptance/run-row-b-e.ps1` for clean-machine rows B–E (still unexecuted: no hardware).

### Changed

- Privacy/README/SECURITY/production-readiness documentation corrected and extended for the new
  controls (managed-policy banner, retention setting, DPAPI keys, egress list, supply chain, MSI).
  `docs/P6-PLAN.md` design sections now describe the implemented design (registry policy, hex
  DPAPI blobs, retention semantics, MSI).
- Release workflow: permissions for attestations, MSI build/staging, SBOM generation/enrichment,
  provenance attestation, and SHA256SUMS now covers all three installers. Release is still signed
  only when `SIGNING_ENABLED` is set.
- Version bump to 3.9.0 across the app, Cargo manifests/lockfile and site metadata.

### Verified

- pnpm test: 33 files / 204 tests; pnpm build; pnpm exec tsc --noEmit; i18n audit.
- cargo test --release: 120 tests (19 new: policy, DPAPI, retention); engine guard: 8 tests;
  cargo check --tests.
- python -m unittest discover -s tests (benchmarks/arabic-asr): 62 tests.
- Three installers built from the same source; sizes and SHA-256 recorded in
  `docs/VERIFICATION.md` after the release, with silent-install verification of each.

### Known limitations

- Installers remain unsigned (owner decision while open-source-only) → SmartScreen warning; verify
  SHA-256/provenance. No external audit or certification.
- Clean-machine rows B–E are unexecuted (no hardware); runbook/script provided.
- Managed policy is enforced inside the app; a local administrator can change HKLM (documented).
- No at-rest encryption of transcripts (BitLocker expected for sensitive data); only API keys are
  DPAPI-encrypted.
- MSI needs administrator rights and a WebView2 runtime; fully offline clean installs should use
  the offline NSIS installer.
- Iraqi/Levantine remain unmeasured; no accuracy claims beyond the published 90-clip suite.
- No auto-update (by design).

## v3.8.0 — 2026-11-18

Distribution and trust release. **No app runtime change**: the engine, models, catalogue and UI
behaviour are identical to v3.7.0 (the version bump is what produces a new installer). The release
adds a fully offline WebView2 installer as a second asset, stages (but keeps dormant) the code
signing pipeline, adds a benchmark regression gate that fails a re-run on WER regression, and
records an honest production-readiness statement. Releases stay unsigned while the project is
open-source-only, by owner decision.

### Added

- **Offline WebView2 installer variant** (`desktop/src-tauri/tauri.offline.conf.json`,
  `webviewInstallMode = offlineInstaller`). The release workflow builds it first and stages it as
  `Sada_<version>_x64-setup-offline.exe`, then builds the default `Sada_<version>_x64-setup.exe`;
  `SHA256SUMS.txt` gets one line per asset. Download docs explain which file to pick.
- **Benchmark regression gate**: `sadabench compare` (`benchmarks/arabic-asr/sadabench/compare.py`,
  CLI `python -m sadabench compare --baseline ... --candidate ...`) re-scores both result files and
  fails when overall or per-slice WER regresses by more than 1.0 pp (`--tolerance-pp`), exits 2 on
  incompatible runs, and renders Markdown/JSON. 10 new tests (62 Python tests total); CI runs it on
  the committed baseline so the gate is exercised on every push.
- **Dormant signing steps** in the release workflow: `SIGNING_ENABLED=true` merges the signing
  overlay, sets up `uv`, runs `scripts/sign.py`, and verifies Authenticode on both installers before
  publishing; with the variable unset no signing step runs. Procedure and alternatives:
  `docs/SIGNING.md`; issue #18 remains open for the actual signing application.
- **Production readiness statement** `docs/PRODUCTION-READINESS.md`: per-audience verdict
  (individual and small team ready with conditions; managed enterprise deployment not yet), eight
  evidence categories, go/no-go checklist, gap-closing steps, evidence index, Arabic summary.
- **Docs**: `docs/P5-PLAN.md` (v3.8.0 plan and acceptance criteria); BUILDING.md installer-variants
  and fork release steps; SIGNING.md decision/status and switch-on steps; README/README.ar file
  choice, SmartScreen, WebView2 and VC++ notes.

### Changed

- Release workflow now publishes two NSIS assets from the same source and verifies the tag matches
  `tauri.conf.json` before building; release notes for this version document both hashes.
- ROADMAP milestone/backlog: v3.8.0 row (#22–#26), P5 section, stale 60-clip figures replaced with
  the 90-clip measurements.

### Verified

- pnpm test: 31 files / 193 tests; pnpm build; i18n audit.
- cargo test --release: 101 tests; engine guard: 8 tests; cargo check --tests.
- python -m unittest discover -s tests (benchmarks/arabic-asr): 62 tests.
- Both installer variants built from the same source; published sizes and SHA-256 are recorded in
  `docs/VERIFICATION.md`, with silent-install verification of both assets.

### Known limitations

- Installers remain unsigned (owner decision, open-source-only period) → possible SmartScreen
  warning; verify SHA-256.
- The offline WebView2 installer embeds WebView2 but not the VC++ 2015-2022 runtime; the NSIS hook
  downloads it when missing, so fully offline machines must pre-install `vc_redist.x64.exe`.
- Iraqi/Levantine remain unmeasured; Gulf/technical slices are scripted code-switch speech.
- No auto-update (by design); updates are deliberate manual downloads.

## v3.7.0 — 2026-11-18

Benchmark coverage and prompt-biasing evidence release. **No app runtime change**: the engine,
models, catalogue and UI behaviour are identical to v3.6.0 (the version bump is what produces a new
installer). The release extends the Arabic benchmark to 90 clips with measured Gulf and technical
code-switch slices from a commercial-use corpus, records the corpus licence matrix and the still-missing
Iraqi/Levantine coverage, and reports a **negative** prompt-biasing result instead of shipping it.

### Added

- **Gulf and technical slices** in `benchmarks/arabic-asr/manifest.json` (v1 format, 90 clips):
  15 Saudi Arabic (Najdi/Hijazi)–English and 15 Egyptian Arabic–English code-switch clips from
  [Perle-ai/ASR_Code_Switch](https://huggingface.co/datasets/Perle-ai/ASR_Code_Switch) (MIT; audio
  recorded by native voice actors, human reference transcripts, pinned revision,
  `prompt`/`transcript` reference support). Audio is still fetched, never committed.
- **Prompt-biasing experiment support** in the harness: `prompt_file`/`prompt` per model,
  `--slices` filter, `prompt_sha256` in result metadata, committed prompt variants under
  `benchmarks/arabic-asr/prompts/`, and `build-manifest --reuse` so extending one slice does not
  re-walk the Common Voice test split (110 pages) under a rate-limited viewer. Retries on the
  dataset viewer now tolerate 429/5xx bursts (12 attempts, jitter, Retry-After).
- **Licence matrix and plan** `docs/P4-PLAN.md`: accepted corpora and every examined/rejected
  corpus with its licence reason (QASR CC BY-NC, ArSyra CC BY-NC-SA, SADA licence contradiction,
  MADIS5 ambiguous metadata, MASC YouTube provenance and missing dialect labels, Lahgtna synthetic
  TTS audio, LDC/ELRA paid research licences).

### Measured

- Initial-prompt biasing on `latin-mixed` + `msa` (40 clips, same weights): raw WER
  turbo 29.38% vs Arabic+Latin glossary 31.92% vs English-only glossary 38.42% vs Arabic-only
  instruction 31.36%. Every prompt variant is **worse** on latin-mixed (glossary 55.21% vs
  48.96%) and MSA is flat-to-worse, and Latin-name preservation does not improve (25% in every
  variant). Decision: no prompt preset is shipped; the existing user-editable prompt field stays
  as-is. Numbers: `benchmarks/arabic-asr/results/prompt-spike-v1.md`.
- Full 90-clip corpus rerun on five models (four previous models + the prompt variant) is recorded
  in `benchmarks/arabic-asr/results/results-2026-11-18-v2.md`; Iraqi and Levantine remain pending
  because no free commercial-use corpus with human transcripts was found.

### Verification

`pnpm test` 31 files / 193 tests, `pnpm build` (paraglide + tsc + vite), `cargo test --release`
101 tests, `cargo test --release -p vibe-server guard::` 8 tests, `cargo check --tests`, the i18n
audit and the Python benchmark suite (52 tests) all pass on 2026-11-18. The installer is built by CI
from the same source; its hash is recorded in `docs/VERIFICATION.md` after the release.

## v3.6.0 — 2026-11-18

Transcript quality and security hardening. No engine or model change (still
`vibe-server v0.6.16-sada.1`, same four catalogue entries); the release adds the Arabic
post-processing pass and its shared fixtures, ports the relevant upstream v3.3.6 security fixes,
and records the clean-machine acceptance procedure and the code-signing decision.

### Added

- **Arabic term restoration** in `desktop/src/lib/arabic-text.ts`: 21 common Latin technical
  terms (GPU, CPU, HTTP, HTTPS, HTML, PDF, SRT, VTT, JSON, API, FFmpeg, Whisper, URL, SQL, CSS,
  USB, VPN, Wi-Fi, GitHub, …) that whisper.cpp wrote in Arabic letters are restored to their Latin
  spelling, with the Arabic definite article and split/joined spellings handled and whole-word
  matching only. Arabic punctuation (، ؟ ؛) and spacing are normalised in the same pass. Rules are
  lossless and idempotent and already run on every transcript surface (live text, saved projects,
  dictation, phone handoff, exports).
- **Shared post-processing fixtures** `benchmarks/arabic-asr/fixtures/arabic-postprocess-cases.json`
  asserted by both the TypeScript app rules and the new `sadabench/postprocess.py`, plus an
  **App-level** table in the benchmark report so scoring runs the same rules users see.
  Measured result on the current clips: app-level WER equals raw (Turbo 19.46%, Nemotron 17.12%),
  i.e. the pass is presentation-only and does not claim an accuracy gain.
- **Clean-machine acceptance procedure** `docs/ACCEPTANCE.md`: install/offline/CPU/VAD/deep-link/
  dictation checklist with an evidence table, plus the WebView2 prerequisite finding for offline
  Windows 10.
- **Code-signing decision record** `docs/SIGNING.md`: SignPath Foundation (free OSS), Azure
  Artifact Signing (~US$10/month), OV/EV certificate options, costs, existing `scripts/sign.py`
  state and the recommendation not to buy before the owner decides.
- New tests: Rust 101 (was 91) covering yt-dlp release validation, download destination
  confinement and the dictation typing permit/control-character scrubbing; TypeScript 31 files /
  193 tests (was 28/179) including safe Markdown and sada: deep-link parsing; Python 44 (was 38)
  including the postprocess fixtures.

### Security

Ported the applicable parts of upstream Vibe v3.3.6 (see `docs/UPSTREAM-PATCHES.md` §10):

- Content-Security-Policy in `tauri.conf.json` (dev and production).
- `SafeMarkdown`: images dropped, http(s) links opened in the system browser, other schemes inert.
- `sada://download/?url=…` accepts https on huggingface.co / github.com only, shows the full URL
  for confirmation and takes size/SHA-256 from the bundled catalogue.
- Model download destinations confined to `.bin`/`.gguf` inside the models folder (no relative
  paths, `..`, symlinked destinations or `.part` symlinks); https-only redirects, max 10.
- yt-dlp update: version-tag validation, app-built GitHub release URL, required SHA2-256SUMS.
- Engine child process: canonical working directory, app TEMP/TMP, `GGML_BACKEND_PATH` removed.
- Dictation typing permit (30-minute window after a recording) and 50,000-character cap with
  control characters stripped.
- Deleted the unvalidated generic `download_file` command; the webview cannot pass a download URL
  or path any more.

### Changed

- `SECURITY.md`: supported version is 3.6.x and a new "Defences in depth added in 3.6.0" section
  records the boundary and the signing status.
- `AGENTS.md`: docs index (acceptance, signing) and current test counts.

### Verification

`pnpm test` 31 files / 193 tests, `pnpm build` (paraglide + tsc + vite), `cargo test --release`
101 tests, `cargo test --release -p vibe-server guard::` 8 tests, Python benchmark suite 44 tests
and the i18n audit all pass on 2026-11-18. The installer is built by CI from the same source; its
hash is recorded in `docs/VERIFICATION.md` after the release. The installer remains unsigned
(SmartScreen warning) until a signing programme is adopted.

## v3.5.0 — 2026-11-18

Measured Arabic model evaluation. No engine change (still `vibe-server v0.6.16-sada.1`); the
release adds the benchmark harness, the written decisions, one optional verified catalogue entry,
and the read-aloud and second-engine verdicts.

### Added

- **Arabic ASR benchmark harness** (`benchmarks/arabic-asr/`, stdlib Python, offline after the
  one-time fetch): pinned 60-clip manifest (30 MSA Common Voice 18 CC0, 10 Latin-mixed Common Voice,
  20 Egyptian FLEURS `ar_eg` CC BY 4.0), Arabic normalisation, corpus-level WER/CER, acronym and
  Latin-name preservation, word-timestamp coverage, RTF, per-slice curation verdicts, 38 `unittest`
  tests and a CI job. Audio and weights stay out of git.
- **NVIDIA Nemotron 3.5 ASR Streaming 0.6B** as an optional catalogue entry
  (`nemotron-3.5-asr-streaming-0.6b`, OpenMDW-1.1, 495,831,520 B, SHA-256
  `41c99fa5…b8fd`, Silero VAD supplied automatically). It wins the measured read MSA/Egyptian
  slices, adds punctuation, is faster and 3.3× smaller than Turbo; its description states that it
  transliterates Latin technical terms and that it is not the default.
- **Decision record** `docs/MODELS-DECISIONS.md` (measured numbers, rulings, reproduction commands,
  reopen conditions) and **read-aloud evidence** `docs/READ-ALOUD.md` (no-go for Windows voices).
- Evidence log §8 in `docs/MODELS-COUNCIL.md` and its Arabic mirror; ROADMAP P2 completed.

### Changed

- `docs/MODELS.md` / `docs/MODELS.ar.md`: the optional Nemotron entry, the rejected fine-tune and
  the unmeasured Iraqi/Gulf/Levantine/technical slices are documented honestly.
- Catalogue is now four curated entries (three Whisper models + Nemotron); no weight is bundled.

### Rejected (recorded, not shipped)

- Arabic Whisper fine-tune `whisper-large-v3-turbo-arabic-dialectal-v2-q5_0`: 23.09% overall WER vs
  19.46% for Turbo, no ≥1.0 pp slice win → not curated.
- Read-aloud via Windows voices: no Arabic voice in a normal install, rubric not runnable → no TTS code.
- Second engine (transcribe.cpp + Qwen3-ASR 0.6B, CPU): 24.38% overall WER (MSA 20.54%, Egyptian
  21.10%), no timestamps and no VAD → not integrated; keep-learning conditions recorded.

## v3.4.0 — 2026-11-17

Verified model catalog, model-capability gating and local endpoint hardening. The installer still
ships no model; the engine sidecar is now built from this repository with the loopback guard.

### Added

- **Verified model catalog** (`desktop/src/assets/model-catalog.json`) with a Get models experience
  in Settings → Models. Three commercially reusable entries — large-v3-turbo and tiny Whisper
  (MIT) and the Hebrew large-v3-turbo (Apache-2.0) — and compact engine models for users who choose
  them; each entry is validated for licence (MIT / Apache-2.0 / CC-BY-4.0 / OpenMDW-1.1), byte size,
  SHA-256 and language coverage before it can appear. Guides: `docs/MODELS.md`, `docs/MODELS.ar.md`.
- **Model capabilities everywhere.** `sada_info` reports the configured model's engine class,
  language list, Silero VAD requirement, and whether it supports translation and text prompts.
  `sada_transcribe` probes the model locally (no port), maps language codes to the model's list,
  finds the required VAD model automatically, and passes `--translate` / `--prompt` only when the
  model declares support. Documented in `docs/AGENT-MCP.md` and `docs/AGENT-MCP.ar.md`.
- **Language and VAD gating in the app.** Choosing a model reconciles the transcription language to
  the nearest supported one, and Settings, Setup, the transcription queue and the global hotkey all
  ensure the Silero VAD model is present before loading an engine that requires it. Five new
  strings in `en-US` and `ar-IQ`.

### Security

- **Loopback request guard in the bundled engine** (`server/crates/vibe-server/src/server/guard.rs`):
  only loopback `Host` values are accepted (DNS-rebinding defence) and browser `Origin` values must be
  loopback or the Tauri scheme, so a web page or a rebound hostname cannot drive the local API.
  Requests without `Host` are rejected. The guard applies only when the listener binds loopback; an
  explicit `--host` elsewhere remains opt-in network serving. Residual risk: a same-user local process
  can still reach the API (a per-run token is the next step). See `SECURITY.md`.
- The app now starts the engine with an explicit `--host 127.0.0.1 --port 0` instead of relying on the
  engine default, and the Release workflow rebuilds the engine from `server/` (`chore server-build`)
  and runs `cargo test -p vibe-server guard::` before packaging. `docs/UPSTREAM-PATCHES.md` §9 and
  `docs/ARCHITECTURE.md`, `docs/BUILDING.md` record the new delta.
## v3.3.1 — 2026-11-17

Engine and GPU foundation release: the bundled engine moves to upstream vibe-server v0.6.16, the
diarization model is replaced, and the GPU/Vulkan support that was already in the engine is
finally documented with a user-facing device story.

### Changed

- Engine sidecar `.server-version` v0.6.10 → v0.6.16: Vulkan and large-file crash fixes, non-AVX
  (SSE4.2) CPU support, sentence/paragraph reconstruction, repeated-line retries.
- Diarization model: the retired Sortformer ONNX file is replaced by `nemotron-3-diarization-Q8_0.gguf`
  (108,541,632 bytes, SHA-256 pinned); the old filename is filtered out of the model list so it no
  longer looks like a transcription model. Users who had it keep the file on disk — nothing is deleted.
- Bundled FFmpeg 9.0.1 → 9.0.2 (GPLv3; notices and source offer updated).

### Added

- GPU/Vulkan documentation: README.md, README.ar.md, docs/BUILDING.md and docs/DEBUG.md now explain
  the Settings → Models → Hardware device picker, what Auto means, CPU fallback when Vulkan is
  missing, the out-of-memory retry-and-remember behaviour, and the Vulkan runtime requirement.
- `docs/VERIFICATION.md` section for 3.3.1 and bilingual `docs/releases/v3.3.1.md`.
## v3.3.0 — 2026-11-16

Agent interface release: Sada can now act as an MCP server for AI agents, with Arabic-first defaults.

### Added

- **MCP server** (`Sada.exe --mcp`): JSON-RPC over stdio — initialize, ping, tools/list,
  tools/call, empty resources/prompts; protocol revisions 2025-06-18 / 2025-03-26 / 2024-11-05.
  No port, no network, no GUI.
- **Four tools**: `sada_transcribe` (local audio/video to Arabic transcript, optional
  timestamps, language auto, normalization on by default), `sada_transcripts` (list saved
  transcripts), `sada_transcript` (read one, optional timecodes and speakers), `sada_info`
  (install diagnostics).
- **Rust twin of the Arabic normaliser** (`desktop/src-tauri/src/arabic.rs`) shared by MCP
  output, with parity tests against the TypeScript rules.
- **Documentation**: [docs/AGENT-MCP.md](docs/AGENT-MCP.md),
  [docs/AGENT-MCP.ar.md](docs/AGENT-MCP.ar.md), [docs/VOICEBOX-REVIEW.md](docs/VOICEBOX-REVIEW.md)
  and [docs/VOICEBOX-REVIEW.ar.md](docs/VOICEBOX-REVIEW.ar.md).

### Changed

- The installed agent skill is now **sada** (`.claude|.codex/skills/sada/SKILL.md`) and leads
  with MCP registration, keeping the transcript-folder, local-API and engine-CLI routes as
  fallbacks.
- Settings About/repository/privacy links point at the Sada repository instead of upstream Vibe.
- Version bumped to 3.3.0.

### Removed

- Nothing. No new dependencies, no extra binaries, no extra models.

## v3.2.2 — 2026-11-16

First public release of Sada, built from Vibe v3.2.2 (commit `23eae78`).

### Added

- **Arabic-first fork**: full Arabic UI catalogue `ar-IQ` (704 keys), RTL shell and settings,
  Arabic-first defaults (display `ar-IQ`, transcription `ar`, no translation, temperature 0,
  beam 5), IBM Plex Sans Arabic typography, Western digits and Iraqi date formats.
- **Arabic transcript normalization**: Arabic punctuation (`، ؟ ؛`), whitespace cleanup and
  restoration of common Latin acronyms in Arabic text.
- **Arabic PDF export** with an embedded Arabic font and correct shaping.
- **New identity**: product name Sada (صدى), `Sada.exe`, identifier `app.sada.desktop`, scheme
  `sada`, new icon set and artwork.
- **Documentation and attestation**: Arabic and English README, PRIVACY, NOTICE,
  THIRD-PARTY-NOTICES, upstream delta list, verification report, licences.
- **Delivery automation**: CI workflow for build/tests, release workflow (tag → Windows installer +
  GitHub Release with checksums), and a bilingual GitHub Pages site with `llms.txt`.

### Changed

- Installation name/paths and Windows version metadata are Sada 3.2.2.
- The hidden meeting-prompt window now shares the same Arabic default, fixing an English-first-paint
  race on a fresh profile.

### Removed

- Telemetry/Aptabase client, auto-updater plugin, and the phone handoff entry point (code path
  remains compiled but unreachable).
- Vibe branding in shipped UI strings; upstream attribution remains in Settings → About and NOTICE.

### Known issues

- Unsigned installer (SmartScreen warning), no bundled model, occasional silence hallucinations
  and acronym/number normalization gaps. See [docs/VERIFICATION.md](docs/VERIFICATION.md).

### Upstream

Based on Vibe v3.2.2 (MIT). See [docs/UPSTREAM-PATCHES.md](docs/UPSTREAM-PATCHES.md) for the full
file-by-file delta.
