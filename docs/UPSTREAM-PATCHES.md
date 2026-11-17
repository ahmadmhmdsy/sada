# What this fork changes compared with upstream Vibe v3.2.2

Base: `thewh1teagle/vibe` tag **v3.2.2**, commit `23eae78b864088202e4e3b9987d269fe4da5ebb3`.

> **v3.3.0 update:** section 6 lists the MCP agent interface and the other changes shipped after
> the v3.2.2 release. The file counts in sections 1–5 describe the v3.2.2 fork delta.
Everything below is a deliberate delta. The upstream tree stays untouched in
`upstream/vibe-3.2.2/` for reference; this document is generated from a file-by-file hash
comparison between that snapshot and the fork.

```
106 upstream files differ (54 text/code + 52 generated icon files), 51 new files, 9 upstream files removed
```

## 1. Arabic locale and first-run Arabic

| File | Change |
| --- | --- |
| `i18n/desktop/ar-IQ.json` | **new** — complete Arabic catalogue, 704/704 keys in en-US order, Western digits, MSA with Iraqi date formats |
| `i18n/locales.json` | new locale `ar-IQ` (name `arabic`), desktop only |
| `desktop/project.inlang/settings.json` | `ar-IQ` added; paraglide base locale intentionally stays `en-US` |
| `desktop/index.html` | `<html lang="ar" dir="rtl">`, title `صدى`, new favicon |
| `desktop/src/bootstrap.tsx` | `DEFAULT_DISPLAY_LANGUAGE = 'ar-IQ'`; boot locale applied after config load, before first paint |
| `desktop/src/app.tsx` | `<html lang/dir>` and `<body dir>` kept in sync with the display language |
| `desktop/src/providers/preference.tsx` | first-run defaults: `ar-IQ`, language `ar`, `translate: false`, `temperature: 0`, `beam_size: 5`, `best_of: 5`, `n_threads: 6`, empty `init_prompt`, RTL text area, analytics off |
| `desktop/src/globals.css` | IBM Plex Sans Arabic `@font-face` (400/500/600/700), Arabic-first font stack, Arabic typography rules (tracking, line-height, bidi isolation for numbers and monospace) |
| `desktop/src/assets/fonts/IBMPlexSansArabic-*.ttf` | **new** — four OFL font files |
| `desktop/src/lib/arabic-text.ts` | **new** — Arabic transcript post-processing: ASCII `,`/`?`/`;` → `،`/`؟`/`؛`, space cleanup, Latin acronym restoration (GPU/CPU/PDF/SRT/VTT/JSON/API/FFmpeg/Whisper); idempotent, English text untouched |
| `desktop/src/lib/arabic-text.test.ts` | **new** — 10 unit tests (pass) |
| `desktop/src/pages/main/hooks/use-transcribe-queue.ts` | post-processes live segments, final segments and saved projects |
| `desktop/src/providers/hotkey.tsx` | post-processes dictation output; notification titles use `m.appTitle()` (صدى) |
| `desktop/src/components/handoff-transcript-saver.tsx` | post-processes phone-handoff transcripts (code path kept, UI hidden) |
| `desktop/src/lib/pdf/transcript-pdf.ts`, `pdf/transcript-document.tsx` | IBM Plex Sans Arabic registered for PDF and selected automatically when the document contains Arabic; pure Hebrew/English right-to-left documents keep Rubik (which covers Hebrew, unlike the Arabic face) |
| `i18n/desktop/en-US.json` | two new keys (`privacyLocalOnly`, `aboutUpstream`), `projectLink` reworded; other upstream locales fall back to English for those two keys |

## 2. Rebranding and identity

| File | Change |
| --- | --- |
| `desktop/src-tauri/tauri.conf.json` | `productName: "Sada"`, `mainBinaryName: "Sada"`, `identifier: "app.sada.desktop"`, only NSIS target, no updater artifacts, only the deep-link plugin with scheme `sada` |
| `desktop/src-tauri/Cargo.toml` | crate version `0.0.6` → `3.2.2` so the Windows file version matches the product version; description names the Sada fork |
| `desktop/src-tauri/icons/*` | **new icon set** generated from `desktop/src-tauri/sada-icon.svg` (all Windows/macOS/iOS/Android sizes) |
| `desktop/src-tauri/sada-icon.svg`, `assets/sada-icon.svg` | **new** — Sada artwork (sound-wave mark, not derived from the Vibe logo) |
| `desktop/src-tauri/src/setup.rs` | window title `صدى`; Arabic-first crash dialog (no upstream issue URL); log line `Sada App Running` |
| `desktop/src-tauri/src/tray.rs` | tray tooltip `صدى` |
| `desktop/src-tauri/src/config.rs` | documents subfolder `Vibe` → `Sada` |
| `desktop/src-tauri/src/keepawake.rs` | power-assertion name/reason → Sada |
| `desktop/package.json` | package name `sada`, description updated; updater dependency removed |
| `desktop/src/lib/docx.ts` | DOCX description no longer says "Vibe" |
| `desktop/src/lib/skill.ts` (+ test) | generated agent-skill text rebranded to Sada |
| `desktop/src/lib/transcripts-store.ts` (+ test) | default transcripts folder `Vibe` → `Sada` |
| `desktop/src/lib/config.ts` | help/About/update links point at the upstream GitHub repository/releases instead of Vibe's website, Discord and support pages |
| `desktop/src/pages/settings/sections/general.tsx` | help section reduced to one "original project" link (no Discord/support/upstream update buttons) |
| `desktop/src/components/ui/dialog.tsx` | hard-coded English "Close" now uses the locale catalogue |

## 3. Removing telemetry, updater and phone relay

| File | Change |
| --- | --- |
| `desktop/src-tauri/src/analytics.rs` | replaced with a no-op module: same public functions, always disabled, no Aptabase client at all |
| `desktop/src-tauri/src/main.rs` | Aptabase plugin and updater plugin no longer registered |
| `desktop/src-tauri/Cargo.toml` | `tauri-plugin-updater` and the Aptabase git dependency removed |
| `desktop/src-tauri/capabilities/main.json` | `updater:default` and `aptabase:allow-track-event` permissions removed |
| `desktop/src/providers/updater.tsx` | replaced with a no-op provider (`availableUpdate` always false); update UI cannot appear |
| `desktop/src/pages/settings/sections/privacy.tsx` | rewritten: local-only statement plus the "keep projects" switch; analytics and policy links removed |
| `desktop/src/pages/settings/page.tsx` | phone pairing section removed from settings navigation and routing (handoff code remains compiled but unreachable) |
| `desktop/src/pages/main/components/recents-sidebar.tsx` | the phone-handoff button is removed from the sidebar footer (it opened a settings section that no longer exists); the remaining footer is Settings + optional update badge |
| `Cargo.lock`, `desktop/pnpm-lock.yaml` | regenerated after the dependency removals |

## 4. Documentation, licence and attribution

New: `README.ar.md` (main Arabic README), `NOTICE`, `PRIVACY.md`,
`THIRD-PARTY-NOTICES.md`, `docs/UPSTREAM-PATCHES.md` (this file),
`docs/upstream-README.md` (upstream README snapshot), `docs/licenses/` (GPL-3.0,
Apache-2.0, OFL for IBM Plex Sans Arabic, Rubik and Inter), sidecar README.
`README.md` and `LICENSE` were repurposed: MIT kept with the original copyright notice plus
the fork copyright.

## 5. Packaging, CI, release and discovery (added by Sada)

| File | Change |
| --- | --- |
| `.github/workflows/ci.yml` | **new** — CI: frozen install, frontend build (`pnpm build`), unit tests (`pnpm test`) |
| `.github/workflows/release.yml` | **rewritten** — tag `v*` → Windows build (`chore setup`, Rust, Tauri NSIS) → GitHub Release with installer, `SHA256SUMS.txt`, `LICENSE`, `NOTICE` and `THIRD-PARTY-NOTICES.md`; requires `docs/releases/v<version>.md` |
| `.github/workflows/pages.yml` | **new** — deploys `site/` to GitHub Pages |
| `.github/workflows/{lint_rust,server-libs,server-release,server-test,test-release,website}.yml` | **removed** — upstream workflows that do not apply to this fork (and one of which would run on our release) |
| `.github/FUNDING.yml` | **removed** — upstream author's funding accounts; a fork must not redirect them |
| `.github/ISSUE_TEMPLATE/*`, `.github/pull_request_template.md` | rewritten/added for Sada (Arabic + English) |
| `docs/releases/v3.2.2.md` | **new** — bilingual release notes used by the release workflow |
| `docs/VERIFICATION.md` | **new** — public verification report (build, hashes, ASR evidence, limitations) |
| `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md` | **new/rewritten** — Sada-specific contributing, security and changelog |
| `CITATION.cff`, `llms.txt` | **new** — citation metadata and an agent/research index (llms.txt format) |
| `AGENTS.md` | **rewritten** — Sada repository guide for humans/AI agents, upstream dev notes retained |
| `README.md`, `README.ar.md` | rewritten — badges, screenshots, install, FAQ, verification, attribution and discovery keywords |
| `docs/media/` | **new** — screenshots used by the README and the website |
| `site/` | **new** — bilingual static landing page (Arabic first, English under `/en/`) with JSON-LD (WebSite, SoftwareApplication, FAQPage), Open Graph/Twitter metadata, `robots.txt`, `sitemap.xml`, local OFL fonts and `llms.txt` |

The upstream engine, model handling and audio pipeline remain untouched by this section.

## 6. MCP agent interface and v3.3.0 delta (added by Sada)

| File | Change |
| --- | --- |
| `desktop/src-tauri/src/mcp/mod.rs` | **new** — stdio MCP server: protocol negotiation (2025-06-18 / 2025-03-26 / 2024-11-05), `initialize`, `ping`, `tools/list`, `tools/call`, empty `resources/list`/`prompts/list`, JSON-RPC errors, Arabic-first server instructions |
| `desktop/src-tauri/src/mcp/tools.rs` | **new** — `sada_transcribe`, `sada_transcripts`, `sada_transcript`, `sada_info`; config/model/engine/FFmpeg/transcripts resolution; actionable errors; unit tests |
| `desktop/src-tauri/src/mcp/transcripts.rs` | **new** — project-folder and legacy flat transcript scanning, rendering with `HH:MM:SS.mmm` timecodes, previews, tests |
| `desktop/src-tauri/src/arabic.rs` | **new** — Rust twin of `desktop/src/lib/arabic-text.ts` (same punctuation, whitespace and acronym rules; parity tests) |
| `desktop/src-tauri/src/main.rs` | `mod arabic;` / `mod mcp;` and an early `mcp::run_if_requested()` hook before any Tauri setup; `--config` override |
| `desktop/src-tauri/src/cmd/skill.rs` | installed skill folder and metadata renamed to **sada** (`.claude|.codex/skills/sada/SKILL.md`); tests updated |
| `desktop/src/lib/skill.ts` (+ `skill.test.ts`) | MCP section added before the CLI section: `--mcp`, Claude Code command, Codex TOML and generic JSON registration, four tools, `--config`; `AgentPaths.sada`, `sadaBinary`; frontmatter `name: sada` |
| `desktop/src/lib/config.ts` | branding URLs point at the Sada repository/releases/issues/privacy instead of upstream Vibe |
| `desktop/src/mock-tauri/handlers/media-misc.ts` | mock agent paths, skill path and Documents folder renamed for Sada |
| `docs/AGENT-MCP.md`, `docs/AGENT-MCP.ar.md` | **new** — English and Arabic agent guide (quick start, registration, tool reference, resolution order, protocol, security, troubleshooting) |
| `docs/VOICEBOX-REVIEW.md`, `docs/VOICEBOX-REVIEW.ar.md` | **new** — Qiyas Council review of Voicebox, verdict table and the criteria for any future TTS work |
| `docs/releases/v3.3.0.md` | **new** — bilingual release notes |
| `desktop/src-tauri/tauri.conf.json`, `desktop/src-tauri/Cargo.toml`, `Cargo.lock`, `CITATION.cff` | version `3.2.2` → `3.3.0` |
| `README.md`, `README.ar.md`, `CHANGELOG.md`, `AGENTS.md`, `llms.txt`, `site/` | MCP feature, agent FAQ, 3.3.0 installer names, version and release-note links |

No dependency was added: the MCP server uses the existing Rust std, `serde`/`serde_json` and the
existing engine binary. The transport is stdio only — no port, no listener, no network endpoint.

## 7. Model and feature research (added by Sada, docs only)

| File | Change |
| --- | --- |
| `docs/MODELS-COUNCIL.md`, `docs/MODELS-COUNCIL.ar.md` | **new** — Qiyas Council Mode C review of models/features/tools worth adopting (GPU/Vulkan support, verified model catalog, engine v0.6.16 bump, Nemotron 3.5, Arabic Whisper fine-tunes, Qwen3-ASR/Cohere/transcribe.cpp, read-aloud, local LLM), with the licence gate, measured evidence on this host, falsification tests and a phased plan |

No code changes accompany this review: it is a decision record for the next releases. It also
records the verified sizes and SHA-256 values that were filled into `desktop/src/lib/config.ts`
in the same round.

## 8. Engine v0.6.16, diarization migration and GPU documentation (added by Sada, v3.3.1)

| File | Change |
| --- | --- |
| `.server-version` | `server-v0.6.10` → `server-v0.6.16` (upstream `master`; prebuilt Windows x64 sidecar with the Vulkan backend, FFmpeg 9.0.2 alongside) |
| `desktop/src/lib/config.ts` | diarization moves from the retired Sortformer ONNX file to `nemotron-3-diarization-Q8_0.gguf` (size + SHA-256 pinned from upstream's v3.3.3 config); `legacyDiarizeModelFilenames` keeps the old file out of the model list |
| `desktop/src/lib/model.ts`, `model.test.ts` | auxiliary-model filter covers the new GGUF diarization file and the legacy filename, with tests |
| `README.md`, `README.ar.md` | new **GPU acceleration (optional)** section: device picker, CPU fallback, Vulkan runtime, out-of-memory retry, measured speed |
| `docs/BUILDING.md` | **GPU acceleration (runtime)** section: Vulkan is baked into the pinned sidecar, no CUDA/ROCm build step, `devices` diagnostics, `no_gpu` behaviour |
| `docs/DEBUG.md` | `vulkan-1.dll` entry now says Vulkan is optional and how to list devices |
| `THIRD-PARTY-NOTICES.md` | bundled FFmpeg 9.0.1 → 9.0.2 (GPLv3 source offer updated) |
| `docs/releases/v3.3.1.md`, `docs/VERIFICATION.md` | bilingual release notes and verification report for the engine bump |
| `desktop/src-tauri/tauri.conf.json`, `Cargo.toml`, `Cargo.lock`, `CITATION.cff` | version `3.3.0` → `3.3.1` |

The bump was accepted after the E1 smoke test in [MODELS-COUNCIL.md](MODELS-COUNCIL.md): the four
Arabic clips produced the same text as v0.6.10, SRT/VTT keeps timed segments, the new Nemotron-3
diarization GGUF labels transcript segments (12/12 on the combined clip), Nemotron 3.5 ASR still
loads behind the Silero VAD, and the CPU-only path still transcribes. The engine source in
`server/` was not modified for v3.3.1 (the loopback guard landed in v3.4.0, see section 9).

## 9. Verified model catalog, engine capability gating and the loopback guard (added by Sada, v3.4.0)

| File | Change |
| --- | --- |
| `desktop/src/lib/model-catalog.ts`, `version.ts`, `model-catalog-source.ts` (+ test) | **new** — bundled-only catalog manifest: strict entry validation (licence allowlist MIT/Apache-2.0/CC-BY-4.0/OpenMDW-1.1, size, SHA-256, languages), upstream-version gate, no network source |
| `desktop/src/assets/model-catalog.json` | **new** — three curated entries (Whisper large-v3-turbo, Parakeet v3, Nemotron 3.5) with pinned hashes; no model is bundled or committed |
| `desktop/src/lib/model-install.ts`, `desktop/src/pages/settings/use-model-catalog.ts`, `desktop/src/pages/settings/sections/model-catalog.tsx` | **new** — catalog install flow in Settings → Models replaces the plain model list (`sections/models.tsx` removed) |
| `docs/MODELS.md`, `docs/MODELS.ar.md` | **new** — model guide: sizes, licenses, hardware, VAD requirement, catalog policy |
| `desktop/src-tauri/src/mcp/model_caps.rs` | **new** — GGUF metadata probe without the engine: engine kind (Whisper / Parakeet v3 / Nemotron), VAD requirement, language list, detection, translation and prompt support, VAD model resolution, tests |
| `desktop/src-tauri/src/mcp/tools.rs` | `sada_transcribe` probes the model, maps the language to the model (`ar` → `ar-AR`, `auto` only with detection), passes `--vad-model` for VAD engines, and only sends `--translate`/`--prompt` when supported; `sada_info` reports capabilities and the models folder |
| `desktop/src/lib/model-capabilities.ts` (+ test) | **new** — pure language reconciliation (nearest advertised code, exact/base match, `auto` only with detection) and VAD gate decision |
| `desktop/src/lib/vad-gate.ts` | **new** — single-flight Silero VAD download/validation used by every model-selection and run path |
| `desktop/src/lib/model.ts` | `readModelMetadata` shared wrapper over the `get_model_metadata` command |
| `desktop/src/providers/preference.tsx`, `pages/settings/view-model.ts`, `pages/setup/view-model.ts`, `pages/main/hooks/use-transcribe-queue.ts`, `providers/hotkey.tsx` | language reconciliation on metadata change; VAD gate before model selection, queue start, retries and dictation; removes the hard-coded English prompts |
| `i18n/desktop/en-US.json`, `ar-IQ.json` | five VAD keys (`vadRequiredTitle`, `vadRequiredMessage`, `vadDownloading`, `vadDownloadFailed`, `vadRequiredToTranscribe`) |
| `server/crates/vibe-server/src/server/guard.rs` | **new** — loopback request guard for the engine: `Host` must be a loopback name for the bound port, an `Origin` header must be a loopback (or Tauri webview) origin; unit tests for rebinding hosts and cross-origin pages |
| `server/crates/vibe-server/src/server/mod.rs` | applies the guard to loopback listeners only; the guard state carries the listener port |
| `server/crates/vibe-server/Cargo.toml` | dev-dependencies for the guard tests (`tower`, `http-body-util`) |
| `desktop/src-tauri/src/server/process.rs` | engine is started with an explicit `--host 127.0.0.1` and an ephemeral port |
| `.github/workflows/release.yml` | builds the engine from `server/` after fetching the pinned sidecars (version `v0.6.16-sada.1`), runs the guard tests, and caches the engine workspace; the installer therefore ships the guarded engine, not the upstream binary |
| `SECURITY.md` | new **Local engine boundary** section: threat, guard rules, residual local-process risk |

This is the first release that changes `server/`. The engine tree is otherwise upstream v0.6.16
code; the guard is the only behavioural delta and is upstreamable as-is.
## Deliberately not changed

- The Whisper engine, model handling and audio pipeline are upstream code apart from the loopback request guard in section 9; no model is bundled.
- The transcription defaults changed only at the application default-config layer
  (`preference.tsx`), not in the engine, so a user can still pick any language/values.
- Upstream i18n catalogues for the other 21 locales are untouched and still selectable.
- No telemetry code was added back; no network endpoint of this fork exists.
